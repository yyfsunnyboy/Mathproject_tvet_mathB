# -*- coding: utf-8 -*-
import argparse
import re
from collections import defaultdict

from app import app
from models import db, SkillInfo, SkillCurriculum, TextbookExample
from core.ai_analyzer import get_model
from core.textbook_processor import _call_gemini_with_retry


def is_path_like_description(desc, volume, chapter, section):
    d = str(desc or "").strip()
    if not d:
        return True
    flat = re.sub(r"\s+", " ", d)
    pat = rf"^{re.escape(str(volume or '').strip())}\s+{re.escape(str(chapter or '').strip())}\s+{re.escape(str(section or '').strip())}\s*-\s*.+$"
    return bool(re.match(pat, flat))


def fallback_description(skill_ch_name, section):
    return f"理解「{skill_ch_name}」的基本概念與常見題型，並能應用於「{section}」相關問題。"


def _example_num(title):
    t = str(title or "")
    m = re.search(r"例\s*([0-9０-９]+)", t)
    if not m:
        return None
    return int(str(m.group(1)).translate(str.maketrans("０１２３４５６７８９", "0123456789")))


def _summarize_skill_examples(skill_id, section):
    rows = (
        TextbookExample.query.filter_by(skill_id=skill_id)
        .filter(TextbookExample.source_section.like("%" + str(section or "")[:3] + "%"))
        .order_by(TextbookExample.id.asc())
        .limit(5)
        .all()
    )
    parts = []
    for r in rows:
        title = str(getattr(r, "title", "") or "").strip()
        problem = str(getattr(r, "problem", "") or getattr(r, "problem_text", "") or "").strip()
        parts.append((title + " " + problem)[:80])
    return "\n".join(parts)


def generate_ai_description(skill_ch_name, section, chapter, volume, examples_hint):
    try:
        model = get_model("architect")
        prompt = (
            "請為技術型高中數學B技能產生學生看得懂的簡短概念說明。"
            "限制：1到2句、繁體中文、可含LaTeX、避免章節路徑字串。"
            f"\n技能：{skill_ch_name}\n小節：{section}\n章：{chapter}\n冊別：{volume}\n"
            f"例題摘要：\n{examples_hint or '（無）'}\n"
            "只輸出說明文字。"
        )
        raw = _call_gemini_with_retry(model, prompt, queue=None, context_message="repair description", parse_json=False)
        text = str(raw or "").strip()
        text = re.sub(r"^```(?:text)?|```$", "", text, flags=re.MULTILINE).strip()
        if text and len(text) <= 180:
            return text
    except Exception:
        pass
    return ""


def build_tutor_prompt(skill_ch_name, section, description):
    d = str(description or "").strip()
    base = f"目前學生正在學習技術型高中數學B「{section}」中的「{skill_ch_name}」。\n"
    if d:
        base += f"技能重點：{d}\n"
    base += "回答時請聚焦在這個技能範圍，用繁體中文分步提示；數學式請使用 LaTeX。"
    return base


def needs_prompt_repair(prompt):
    p = str(prompt or "").strip()
    if not p:
        return True
    if p.lower().startswith("generate math problems about"):
        return True
    if "目前學生正在學習技術型高中數學B" not in p:
        return True
    return False


def compute_order_targets(rows):
    by_group = defaultdict(list)
    for r in rows:
        by_group[(r["curriculum"], r["volume"], r["chapter"], r["section"])].append(r)

    targets = {}
    sources = {}
    for key, items in by_group.items():
        # 1) textbook_examples first-occurrence order
        ex_sorted = sorted(
            items,
            key=lambda x: (
                0 if x["first_example_num"] is not None else 1,
                x["first_example_num"] if x["first_example_num"] is not None else 10**9,
                x["first_example_id"] if x["first_example_id"] is not None else 10**9,
                x["sc_id"] if x["sc_id"] is not None else 10**9,
                x["skill_id"],
            ),
        )
        have_example = any(x["first_example_id"] is not None for x in items)
        if have_example:
            for idx, x in enumerate(ex_sorted, 1):
                targets[x["skill_id"]] = idx
                sources[x["skill_id"]] = "textbook_examples"
            continue

        # 2) fallback skill_curriculum order
        sc_sorted = sorted(
            items,
            key=lambda x: (
                x["sc_id"] if x["sc_id"] is not None else 10**9,
                str(x["paragraph"] or ""),
                x["skill_id"],
            ),
        )
        for idx, x in enumerate(sc_sorted, 1):
            targets[x["skill_id"]] = idx
            sources[x["skill_id"]] = "skill_curriculum"

    return targets, sources


def main():
    parser = argparse.ArgumentParser(description="Repair B1 skills_info metadata only")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--use-ai-description", action="store_true")
    args = parser.parse_args()

    with app.app_context():
        joined = (
            db.session.query(SkillInfo, SkillCurriculum)
            .outerjoin(SkillCurriculum, SkillCurriculum.skill_id == SkillInfo.skill_id)
            .filter(SkillInfo.skill_id.like("vh_數學B1_%"))
            .order_by(SkillCurriculum.volume.asc(), SkillCurriculum.chapter.asc(), SkillCurriculum.section.asc(), SkillCurriculum.id.asc())
            .all()
        )

        total_checked = 0
        needs_description = 0
        path_like_description_count = 0
        needs_gemini_prompt = 0
        wrong_generator_prompt_count = 0
        needs_order_index = 0
        will_update_count = 0
        order_source_counts = {"textbook_examples": 0, "skill_curriculum": 0, "unchanged": 0}
        preview = []

        rows = []
        by_skill = {}
        for si, sc in joined:
            if si is None:
                continue
            sid = str(si.skill_id)
            section = str(getattr(sc, "section", "") or getattr(si, "category", "") or "").strip()
            ex_rows = (
                TextbookExample.query.filter_by(skill_id=sid)
                .order_by(TextbookExample.id.asc())
                .all()
            )
            first_ex_id = None
            first_ex_num = None
            for te in ex_rows:
                # B1 scoped using source_volume/source_section when possible
                sv = str(getattr(te, "source_volume", "") or "")
                if sv and "B1" not in sv:
                    continue
                if section:
                    ss = str(getattr(te, "source_section", "") or "")
                    if ss and ss != section:
                        continue
                first_ex_id = int(getattr(te, "id", 0) or 0)
                first_ex_num = _example_num(getattr(te, "title", ""))
                break

            rows.append({
                "skill_id": sid,
                "curriculum": getattr(sc, "curriculum", None),
                "volume": getattr(sc, "volume", None),
                "chapter": getattr(sc, "chapter", None),
                "section": section,
                "paragraph": getattr(sc, "paragraph", None),
                "sc_id": int(getattr(sc, "id", 0) or 0) if sc is not None else None,
                "first_example_id": first_ex_id,
                "first_example_num": first_ex_num,
            })
            by_skill[sid] = (si, sc)
            total_checked += 1

        target_order, order_source = compute_order_targets(rows)

        for sid, (si, sc) in by_skill.items():
            section = str(getattr(sc, "section", "") or getattr(si, "category", "") or "").strip()
            chapter = str(getattr(sc, "chapter", "") or "").strip()
            volume = str(getattr(sc, "volume", "") or "數學B1").strip()
            skill_ch = str(getattr(si, "skill_ch_name", "") or "").strip() or sid

            old_desc = str(getattr(si, "description", "") or "").strip()
            desc_bad = (not old_desc) or is_path_like_description(old_desc, volume, chapter, section)
            if desc_bad:
                needs_description += 1
                if is_path_like_description(old_desc, volume, chapter, section):
                    path_like_description_count += 1

            if desc_bad:
                desc_source = "fallback"
                if args.use_ai_description:
                    hint = _summarize_skill_examples(sid, section)
                    ai_desc = generate_ai_description(skill_ch, section, chapter, volume, hint)
                    if ai_desc and not is_path_like_description(ai_desc, volume, chapter, section):
                        new_desc = ai_desc
                        desc_source = "ai"
                    else:
                        new_desc = fallback_description(skill_ch, section)
                else:
                    new_desc = fallback_description(skill_ch, section)
            else:
                new_desc = old_desc
                desc_source = "unchanged"

            old_prompt = str(getattr(si, "gemini_prompt", "") or "").strip()
            prompt_bad = needs_prompt_repair(old_prompt)
            if prompt_bad:
                needs_gemini_prompt += 1
                if old_prompt.lower().startswith("generate math problems about"):
                    wrong_generator_prompt_count += 1
            new_prompt = build_tutor_prompt(skill_ch, section, new_desc) if prompt_bad else old_prompt

            old_order = int(getattr(si, "order_index", 0) or 0)
            new_order = int(target_order.get(sid, old_order if old_order > 0 else 1))
            source = order_source.get(sid, "unchanged")
            order_bad = old_order != new_order
            if order_bad:
                needs_order_index += 1
                order_source_counts[source] += 1
            else:
                order_source_counts["unchanged"] += 1

            need_update = any([
                desc_bad,
                prompt_bad,
                order_bad,
                not str(getattr(si, "category", "") or "").strip() and bool(section),
                not str(getattr(si, "input_type", "") or "").strip(),
                int(getattr(si, "consecutive_correct_required", 0) or 0) == 0,
                getattr(si, "is_active", None) is None,
                getattr(si, "importance", None) in (None, 0),
            ])
            if need_update:
                will_update_count += 1

            if len(preview) < 30 and need_update:
                preview.append({
                    "skill_id": sid,
                    "skill_ch_name": skill_ch,
                    "section": section,
                    "old_description": old_desc,
                    "new_description": new_desc,
                    "old_gemini_prompt": old_prompt,
                    "new_gemini_prompt": new_prompt,
                    "old_order_index": old_order,
                    "new_order_index": new_order,
                    "order_source": source,
                    "description_source": desc_source,
                })

            if args.apply and need_update:
                if desc_bad:
                    si.description = new_desc
                if prompt_bad:
                    si.gemini_prompt = new_prompt
                if order_bad:
                    si.order_index = new_order
                if not str(getattr(si, "category", "") or "").strip() and section:
                    si.category = section
                if not str(getattr(si, "input_type", "") or "").strip():
                    si.input_type = "text"
                if int(getattr(si, "consecutive_correct_required", 0) or 0) == 0:
                    si.consecutive_correct_required = 3
                if getattr(si, "is_active", None) is None:
                    si.is_active = 1
                if getattr(si, "importance", None) in (None, 0):
                    si.importance = 1
                if getattr(si, "description", None) is None:
                    si.description = new_desc
                if getattr(si, "gemini_prompt", None) is None:
                    si.gemini_prompt = new_prompt

        print(f"total_checked={total_checked}")
        print(f"needs_description={needs_description}")
        print(f"path_like_description_count={path_like_description_count}")
        print(f"needs_gemini_prompt={needs_gemini_prompt}")
        print(f"wrong_generator_prompt_count={wrong_generator_prompt_count}")
        print(f"needs_order_index={needs_order_index}")
        print(f"will_update_count={will_update_count}")
        print("order_source_counts:")
        print(f"- textbook_examples={order_source_counts['textbook_examples']}")
        print(f"- skill_curriculum={order_source_counts['skill_curriculum']}")
        print(f"- unchanged={order_source_counts['unchanged']}")
        print("preview(top30):")
        for p in preview:
            print(p)

        if args.apply:
            db.session.commit()
            print(f"applied_updates={will_update_count}")


if __name__ == "__main__":
    main()
