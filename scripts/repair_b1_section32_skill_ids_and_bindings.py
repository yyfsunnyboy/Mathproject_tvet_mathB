# -*- coding: utf-8 -*-
import argparse
from collections import defaultdict

from app import app
from models import db, SkillInfo, SkillCurriculum, TextbookExample

OLD_SKILL_ID = "vh_數學B1_SubSection322"
TARGET_SKILL_ID = "vh_數學B1_RemainderTheorem"
DIV_SKILL_ID = "vh_數學B1_DivisionAlgorithm"
FAC_SKILL_ID = "vh_數學B1_FactorTheorem"
OUTLINE_SKILL_ID = "outline_vocational_數學B1_32"
SECTION_NAME = "3-2 除法原理與餘式定理"


def _b1_32_curriculum_q():
    return SkillCurriculum.query.filter(
        SkillCurriculum.curriculum == "vocational",
        SkillCurriculum.volume == "數學B1",
        SkillCurriculum.section.like("3-2%"),
    )


def _b1_32_examples_q():
    return TextbookExample.query.filter(
        TextbookExample.source_volume == "數學B1",
        TextbookExample.source_section.like("3-2%"),
    )


def _mainline_example_order_map():
    rows = (
        _b1_32_examples_q()
        .filter(
            TextbookExample.title.like("例%")
        )
        .order_by(TextbookExample.id.asc())
        .all()
    )
    first = {}
    for r in rows:
        sid = str(getattr(r, "skill_id", "") or "").strip()
        if sid and sid not in first:
            first[sid] = int(getattr(r, "id", 0) or 0)
    return first


def _print_b1_32_skill_listing():
    rows = (
        db.session.query(SkillInfo, SkillCurriculum)
        .join(SkillCurriculum, SkillCurriculum.skill_id == SkillInfo.skill_id)
        .filter(
            SkillCurriculum.curriculum == "vocational",
            SkillCurriculum.volume == "數學B1",
            SkillCurriculum.section.like("3-2%"),
        )
        .order_by(SkillInfo.skill_id.asc(), SkillCurriculum.id.asc())
        .all()
    )
    print("[B1_3_2_CURRENT_SKILLS]")
    for si, sc in rows:
        print(
            f"skill_id={si.skill_id}\tskill_ch_name={si.skill_ch_name}\tskill_en_name={si.skill_en_name}\t"
            f"category={si.category}\torder_index={si.order_index}\tsection={sc.section}\tparagraph={sc.paragraph}"
        )


def _ensure_target_skill_row_from_old(old_si, old_sc):
    if old_si is not None:
        desc = str(getattr(old_si, "description", "") or "").strip() or "當多項式 $f(x)$ 除以 $x-a$ 時，餘式等於 $f(a)$，可快速求餘式。"
        prompt = (
            "目前學生正在學習技術型高中數學B「3-2 除法原理與餘式定理」中的「餘式定理」。"
            f"技能重點：{desc}"
            "回答時請聚焦在這個技能範圍，用繁體中文分步提示；數學式請使用 LaTeX。"
        )
        return {
            "skill_id": TARGET_SKILL_ID,
            "skill_en_name": "RemainderTheorem",
            "skill_ch_name": "餘式定理",
            "category": SECTION_NAME,
            "description": desc,
            "gemini_prompt": prompt,
            "input_type": str(getattr(old_si, "input_type", "") or "text") or "text",
            "consecutive_correct_required": int(getattr(old_si, "consecutive_correct_required", 3) or 3),
            "is_active": 1,
            "order_index": 2,
            "importance": int(getattr(old_si, "importance", 1) or 1),
        }
    desc = "當多項式 $f(x)$ 除以 $x-a$ 時，餘式等於 $f(a)$，可快速求餘式。"
    prompt = (
        "目前學生正在學習技術型高中數學B「3-2 除法原理與餘式定理」中的「餘式定理」。"
        f"技能重點：{desc}"
        "回答時請聚焦在這個技能範圍，用繁體中文分步提示；數學式請使用 LaTeX。"
    )
    return {
        "skill_id": TARGET_SKILL_ID,
        "skill_en_name": "RemainderTheorem",
        "skill_ch_name": "餘式定理",
        "category": SECTION_NAME,
        "description": desc,
        "gemini_prompt": prompt,
        "input_type": "text",
        "consecutive_correct_required": 3,
        "is_active": 1,
        "order_index": 2,
        "importance": 1,
    }


def run(apply=False):
    with app.app_context():
        _print_b1_32_skill_listing()

        old_si = db.session.get(SkillInfo, OLD_SKILL_ID)
        target_si = db.session.get(SkillInfo, TARGET_SKILL_ID)
        old_sc = (
            _b1_32_curriculum_q().filter(SkillCurriculum.skill_id == OLD_SKILL_ID).order_by(SkillCurriculum.id.asc()).first()
        )

        print("[SKILL_ID_PRESENCE]")
        print(f"old_skill_exists={bool(old_si)} old_skill_id={OLD_SKILL_ID}")
        print(f"target_skill_exists={bool(target_si)} target_skill_id={TARGET_SKILL_ID}")

        target_payload = _ensure_target_skill_row_from_old(old_si, old_sc)
        if not target_si:
            print("[TARGET_CREATE_OR_RENAME_PREVIEW]")
            for k, v in target_payload.items():
                print(f"{k}={v}")

        # count references in constrained scope
        ex_old_refs = _b1_32_examples_q().filter(TextbookExample.skill_id == OLD_SKILL_ID).count()
        sc_old_refs = _b1_32_curriculum_q().filter(SkillCurriculum.skill_id == OLD_SKILL_ID).count()
        ex_4733 = _b1_32_examples_q().filter(TextbookExample.id == 4733).first()
        ex_4743 = _b1_32_examples_q().filter(TextbookExample.id == 4743).first()
        ex_4724 = _b1_32_examples_q().filter(TextbookExample.id == 4724).first()

        print("[REFERENCE_UPDATE_PLAN]")
        print(f"textbook_examples {OLD_SKILL_ID} -> {TARGET_SKILL_ID}: {ex_old_refs}")
        print(f"skill_curriculum {OLD_SKILL_ID} -> {TARGET_SKILL_ID}: {sc_old_refs}")
        print(f"skills_info normalize old->target: {1 if old_si else 0}")

        # other tables with skill_id column (report only)
        unknown_refs = []
        for tbl in db.metadata.tables.values():
            if tbl.name in {"skills_info", "skill_curriculum", "textbook_examples"}:
                continue
            if "skill_id" not in tbl.c:
                continue
            try:
                cnt = db.session.execute(
                    db.text(f"SELECT COUNT(*) FROM {tbl.name} WHERE skill_id = :sid"),
                    {"sid": OLD_SKILL_ID},
                ).scalar()
                if int(cnt or 0) > 0:
                    unknown_refs.append((tbl.name, int(cnt)))
            except Exception:
                pass
        if unknown_refs:
            print("[OTHER_TABLE_REFERENCES_REPORT_ONLY]")
            for n, c in unknown_refs:
                print(f"table={n} refs={c}")

        print("[REBINDS_PREVIEW]")
        print(f"id=4733 old={getattr(ex_4733, 'skill_id', None)} -> {TARGET_SKILL_ID}")
        print(f"id=4743 old={getattr(ex_4743, 'skill_id', None)} -> {TARGET_SKILL_ID}")
        print(f"id=4724 keep={getattr(ex_4724, 'skill_id', None)}")

        print("[ORDER_INDEX_PREVIEW]")
        div = db.session.get(SkillInfo, DIV_SKILL_ID)
        fac = db.session.get(SkillInfo, FAC_SKILL_ID)
        tar = target_si
        print(f"DivisionAlgorithm {getattr(div,'order_index',None)} -> 1")
        print(f"RemainderTheorem {getattr(tar,'order_index',None) if tar else None} -> 2")
        print(f"FactorTheorem {getattr(fac,'order_index',None)} -> 3")

        if not apply:
            return

        # --- apply (raw SQL only; avoid ORM relationship lazy-load issues) ---
        updates = defaultdict(int)
        tx = db.session
        try:
            # create target if missing
            if target_si is None:
                tx.execute(
                    db.text(
                        """
                        INSERT INTO skills_info
                        (skill_id, skill_en_name, skill_ch_name, category, description, input_type,
                         gemini_prompt, consecutive_correct_required, is_active, order_index, importance)
                        VALUES
                        (:skill_id, :skill_en_name, :skill_ch_name, :category, :description, :input_type,
                         :gemini_prompt, :consecutive_correct_required, :is_active, :order_index, :importance)
                        """
                    ),
                    target_payload,
                )
                updates["skills_info_created"] += 1
            else:
                tx.execute(
                    db.text(
                        """
                        UPDATE skills_info
                        SET skill_en_name='RemainderTheorem',
                            skill_ch_name='餘式定理',
                            category=:cat,
                            description=CASE WHEN description IS NULL OR description='' THEN :desc ELSE description END,
                            gemini_prompt=:gp,
                            input_type=COALESCE(NULLIF(input_type,''), 'text'),
                            consecutive_correct_required=COALESCE(NULLIF(consecutive_correct_required,0),3),
                            is_active=1,
                            importance=COALESCE(NULLIF(importance,0),1)
                        WHERE skill_id=:sid
                        """
                    ),
                    {
                        "cat": SECTION_NAME,
                        "desc": target_payload["description"],
                        "gp": target_payload["gemini_prompt"],
                        "sid": TARGET_SKILL_ID,
                    },
                )
                updates["skills_info_target_updated"] += 1

            r = tx.execute(
                db.text(
                    """
                    UPDATE textbook_examples
                    SET skill_id=:target
                    WHERE source_volume='數學B1'
                      AND source_section LIKE '3-2%'
                      AND skill_id=:old
                    """
                ),
                {"target": TARGET_SKILL_ID, "old": OLD_SKILL_ID},
            )
            updates["textbook_examples_old_to_target"] += int(r.rowcount or 0)

            for ex_id in (4733, 4743):
                rr = tx.execute(
                    db.text(
                        """
                        UPDATE textbook_examples
                        SET skill_id=:target
                        WHERE id=:id
                          AND source_volume='數學B1'
                          AND source_section LIKE '3-2%'
                        """
                    ),
                    {"target": TARGET_SKILL_ID, "id": ex_id},
                )
                updates[f"textbook_examples_force_{ex_id}"] += int(rr.rowcount or 0)

            rr4724 = tx.execute(
                db.text(
                    """
                    UPDATE textbook_examples
                    SET skill_id=:factor
                    WHERE id=4724
                      AND source_volume='數學B1'
                      AND source_section LIKE '3-2%'
                    """
                ),
                {"factor": FAC_SKILL_ID},
            )
            updates["textbook_examples_keep_4724_factor"] += int(rr4724.rowcount or 0)

            rsc = tx.execute(
                db.text(
                    """
                    UPDATE skill_curriculum
                    SET skill_id=:target
                    WHERE curriculum='vocational'
                      AND volume='數學B1'
                      AND section LIKE '3-2%'
                      AND skill_id=:old
                    """
                ),
                {"target": TARGET_SKILL_ID, "old": OLD_SKILL_ID},
            )
            updates["skill_curriculum_old_to_target"] += int(rsc.rowcount or 0)

            # order index fixes in this section only
            tx.execute(db.text("UPDATE skills_info SET order_index=1 WHERE skill_id=:sid"), {"sid": DIV_SKILL_ID})
            tx.execute(db.text("UPDATE skills_info SET order_index=2 WHERE skill_id=:sid"), {"sid": TARGET_SKILL_ID})
            tx.execute(db.text("UPDATE skills_info SET order_index=3 WHERE skill_id=:sid"), {"sid": FAC_SKILL_ID})
            tx.execute(db.text("UPDATE skills_info SET order_index=9999 WHERE skill_id=:sid"), {"sid": OUTLINE_SKILL_ID})
            updates["skills_info_order_updates"] += 4

            # remove legacy fallback skill if unreferenced in key tables
            old_after_ex = tx.execute(
                db.text("SELECT COUNT(*) FROM textbook_examples WHERE skill_id=:old"),
                {"old": OLD_SKILL_ID},
            ).scalar()
            old_after_sc = tx.execute(
                db.text("SELECT COUNT(*) FROM skill_curriculum WHERE skill_id=:old"),
                {"old": OLD_SKILL_ID},
            ).scalar()
            if int(old_after_ex or 0) == 0 and int(old_after_sc or 0) == 0:
                rd = tx.execute(
                    db.text("DELETE FROM skills_info WHERE skill_id=:old"),
                    {"old": OLD_SKILL_ID},
                )
                updates["skills_info_old_deleted"] += int(rd.rowcount or 0)

            tx.commit()
        except Exception:
            tx.rollback()
            raise

        print("[APPLY_UPDATES]")
        for k, v in sorted(updates.items()):
            print(f"{k}={v}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Repair B1 section 3-2 skill IDs and bindings")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    run(apply=args.apply)
