# -*- coding: utf-8 -*-
"""B2 Ch4 post-import inventory & capability preflight (read-only)."""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
OUT_DIR = ROOT / "reports"


def connect():
    conn = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def rows(conn, sql, params=()):
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def is_ch4_skill(skill_id: str, chapter: str | None = None, section: str | None = None) -> bool:
    sid = str(skill_id or "")
    if not sid.startswith("vh_"):
        return False
    if re.search(r"B2_SubSection_4_", sid) or re.search(r"B2.*_4_\d", sid):
        return True
    ch = str(chapter or "")
    sec = str(section or "")
    if "第4章" in ch or ch.strip().startswith("4-") or "圓與直線" in ch:
        if "B2" in sid or "數學B2" in sid:
            return True
    if re.match(r"^4-\d", sec) and ("B2" in sid or "數學B2" in sid):
        return True
    return False


def classify_source_group(title: str, source_kind: str | None = None) -> str:
    t = str(title or "")
    sk = str(source_kind or "").lower()
    if "自我評量" in t or "self" in sk:
        return "self_assessment"
    if "統測" in t or "學測" in t or "exam" in sk:
        return "past_exam"
    if "進階" in t or "advanced" in sk:
        return "advanced_exercise"
    if "基礎" in t or "basic" in sk:
        return "basic_exercise"
    if "習題" in t and "進階" not in t and "基礎" not in t:
        return "textbook_exercise"
    if "隨堂" in t or "practice" in sk:
        return "in_class_practice"
    if t.startswith("例") or "example" in sk or "例題" in t:
        return "example"
    if "練習" in t:
        return "in_class_practice"
    return "other_formal"


def has_visual(row: dict) -> bool:
    for key in (
        "image_path",
        "image_base64",
        "visual_asset",
        "figure_path",
        "question_image_path",
        "asset_path",
    ):
        val = row.get(key)
        if val and str(val).strip() and str(val).strip() not in {"None", "null", "{}"}:
            return True
    notes = str(row.get("notes") or "")
    if "image" in notes.lower() or "visual" in notes.lower() or "圖" in notes:
        # weak signal only if explicit
        if re.search(r"image|visual_asset|figure|圖\d", notes, re.I):
            return True
    text = str(row.get("problem_text") or row.get("question_text") or "")
    if re.search(r"(如圖|下圖|見圖|▲圖|圖\s*\d)", text):
        return True
    return False


def search_repo_capabilities():
    """Lightweight filesystem keyword search for circle/line capabilities."""
    hits = {
        "domain_modules": [],
        "adapters": [],
        "taxonomy": [],
        "phase1": [],
        "skills_v3": [],
        "ops_keywords": [],
    }
    patterns = {
        "circle": re.compile(r"circle|圓方程式|圓與直線|切線|tangent_segment|unit_circle|circle_line", re.I),
        "ops": re.compile(
            r"compute_.*circle|circle_.*equation|tangent_line|point_circle|circle_line_relation|tangent_length",
            re.I,
        ),
    }
    # domains
    dom = ROOT / "core" / "domain"
    if dom.is_dir():
        for p in dom.rglob("*.py"):
            name = p.name.lower()
            if any(k in name for k in ("circle", "圓", "tangent", "line_equation", "coordinate")):
                hits["domain_modules"].append(str(p.relative_to(ROOT)))
            else:
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")[:8000]
                except Exception:
                    continue
                if patterns["circle"].search(text) and (
                    "OPS" in text or "build_" in text or "domain_operation" in text
                ):
                    hits["domain_modules"].append(str(p.relative_to(ROOT)))
    # adapters / taxonomy
    for rel in [
        "core/gencode",
        "core/registry",
        "configs",
        "agent_skills_v3",
        "skills",
    ]:
        base = ROOT / rel
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in {".py", ".json", ".yaml", ".yml", ".md"}:
                continue
            low = p.name.lower()
            path_s = str(p.relative_to(ROOT)).replace("\\", "/")
            if "4_1" in low or "4_2" in low or "circle" in low or "圓" in path_s:
                if "agent_skills_v3" in path_s or path_s.startswith("skills/"):
                    hits["skills_v3"].append(path_s)
                elif "taxonomy" in path_s or "domain_binding" in path_s or "registry" in path_s:
                    hits["taxonomy"].append(path_s)
                elif "phase1" in path_s or "rule_pack" in path_s:
                    hits["phase1"].append(path_s)
                elif "adapter" in path_s or "domain_matrix" in path_s:
                    hits["adapters"].append(path_s)
    # dedupe
    for k, v in hits.items():
        hits[k] = sorted(set(v))[:80]
    return hits


def infer_family_from_text(skill_id: str, title: str, text: str) -> str:
    blob = f"{title}\n{text}"
    sid = skill_id
    # 4-1
    if "4_1_1" in sid or "標準式" in sid:
        if re.search(r"圓心|半徑|標準式", blob):
            return "rewrite_or_read_standard_circle"
        if re.search(r"寫出|方程式", blob):
            return "write_standard_circle_equation"
        return "standard_circle_misc"
    if "4_1_2" in sid or "一般式" in sid:
        if re.search(r"一般式|化成標準|完成平方", blob):
            return "general_to_standard_circle"
        if re.search(r"圓心|半徑", blob):
            return "read_center_radius_from_general"
        return "general_circle_misc"
    # 4-2 concepts by paragraph hints in text
    if re.search(r"點.*(圓上|圓內|圓外)|圓上、圓外或圓內|在圓", blob):
        return "point_circle_position"
    if re.search(r"弦.?長|交於.*兩點.*弦", blob):
        return "chord_length_from_center_distance"
    if re.search(r"相切|相割|相離|不相交|幾個交點|判斷.*直線.*關係", blob):
        if re.search(r"求.*k|範圍|實數", blob):
            return "circle_line_parameter_relation"
        return "circle_line_position_relation"
    if re.search(r"切線方程式|過圓上.*切線|平行於.*相切|垂直於.*相切", blob):
        if re.search(r"平行", blob):
            return "tangent_parallel_to_line"
        if re.search(r"垂直", blob):
            return "tangent_perpendicular_to_line"
        return "tangent_at_point_on_circle"
    if re.search(r"切線段長", blob):
        return "tangent_segment_length"
    if re.search(r"颱風|暴風|觸礁|航線", blob):
        return "applied_circle_line_geometry"
    if re.search(r"統測", blob):
        return "exam_circle_line_composite"
    return "unclassified_circle_topic"


def skill_classification(
    skill_id: str,
    families: list[str],
    repo_hits: dict,
    has_v3: bool,
) -> tuple[str, str, str]:
    """Return (capability_class, route, why)."""
    circleish = any(
        "circle" in x.lower() or "圓" in x or "line_equation" in x.lower() or "coordinate" in x.lower()
        for x in repo_hits.get("domain_modules", [])
    )
    # Known: line equation domain exists; no dedicated circle domain module found typically
    has_circle_domain = any(
        re.search(r"circle", x, re.I) and "circum" not in x.lower()
        for x in repo_hits.get("domain_modules", [])
    )
    has_line_domain = any("line_equation" in x or "coordinate" in x for x in repo_hits.get("domain_modules", []))
    missing = [f for f in families if f.startswith("unclassified") or True]
    unique_fams = sorted(set(families))
    covered_existing = []  # none mapped yet for ch4
    missing_fams = unique_fams  # all missing until domain exists

    if has_v3 and not missing_fams:
        return (
            "EXISTING_DOMAIN_EXISTING_FAMILY",
            "DIRECT_V3",
            "Published V3 wrappers already cover families",
        )
    if has_circle_domain and missing_fams:
        return (
            "EXISTING_DOMAIN_NEW_FAMILY",
            "AGENT_EXTEND_FAMILY_THEN_V3",
            "Circle domain exists but Ch4 families not covered",
        )
    if has_line_domain and not has_circle_domain:
        # circle+line may partially reuse line distance / equation
        if any(
            f in unique_fams
            for f in (
                "circle_line_position_relation",
                "tangent_parallel_to_line",
                "tangent_perpendicular_to_line",
                "chord_length_from_center_distance",
            )
        ):
            return (
                "COMPOSITE_EXISTING_CAPABILITIES",
                "AGENT_NEW_DOMAIN_ONBOARDING",
                "Line/coordinate domains reusable for distance-to-line pieces, but circle equation/tangent families need new circle domain",
            )
        return (
            "NEW_DOMAIN",
            "AGENT_NEW_DOMAIN_ONBOARDING",
            "No dedicated circle domain; Ch4 skills require circle equation + tangent families",
        )
    if not has_circle_domain:
        return (
            "NEW_DOMAIN",
            "AGENT_NEW_DOMAIN_ONBOARDING",
            "Repo search found no dedicated circle/plane-circle domain module for B2 Ch4",
        )
    return ("UNKNOWN", "VISUAL_REVIEW_REQUIRED", "Insufficient signal")


def visual_class(row: dict, family: str) -> str:
    text = str(row.get("problem_text") or row.get("question_text") or "")
    needs = bool(re.search(r"(如圖|下圖|見圖|▲圖|圖\s*\d)", text)) or has_visual(row)
    if not needs:
        return "D"
    if family in {
        "point_circle_position",
        "circle_line_position_relation",
        "tangent_at_point_on_circle",
        "tangent_parallel_to_line",
        "chord_length_from_center_distance",
    }:
        return "C"  # parametric coordinate diagram
    if "applied" in family or "颱風" in text or "渡輪" in text:
        return "B"  # textbook figure / PDF crop
    if family == "exam_circle_line_composite":
        return "E"
    return "E"


def main():
    conn = connect()
    # --- chapter structure ---
    skills = rows(
        conn,
        """
        SELECT sc.skill_id, sc.curriculum, sc.grade, sc.volume, sc.chapter, sc.section,
               sc.paragraph, sc.display_order, si.skill_ch_name, si.skill_en_name, si.is_active
        FROM skill_curriculum sc
        LEFT JOIN skills_info si ON si.skill_id = sc.skill_id
        WHERE sc.skill_id LIKE '%數學B2_SubSection_4_%'
           OR sc.skill_id LIKE '%B2_SubSection_4_%'
           OR (sc.chapter LIKE '%第4章%' AND sc.skill_id LIKE 'vh_%' AND sc.skill_id LIKE '%B2%')
           OR (sc.chapter LIKE '%圓與直線%' AND sc.skill_id LIKE 'vh_%B2%')
        ORDER BY COALESCE(sc.display_order, 9999), sc.section, sc.paragraph, sc.skill_id
        """,
    )
    # Prefer formal vh subsection skills only for inventory matrix
    formal_skills = [
        s
        for s in skills
        if str(s["skill_id"]).startswith("vh_") and "SubSection_4_" in str(s["skill_id"])
    ]
    outline_skills = [
        s for s in skills if str(s["skill_id"]).startswith("outline_vocational") and "B2_4" in str(s["skill_id"]).replace("數學", "")
    ]

    # textbook_examples columns dynamically
    te_cols = [r[1] for r in conn.execute("PRAGMA table_info(textbook_examples)").fetchall()]
    # pull all rows for Ch4 skills
    skill_ids = [s["skill_id"] for s in formal_skills]
    if not skill_ids:
        # fallback broader
        skill_ids = [s["skill_id"] for s in skills if str(s["skill_id"]).startswith("vh_")]

    placeholders = ",".join("?" * len(skill_ids)) if skill_ids else "''"
    examples = []
    if skill_ids:
        examples = rows(
            conn,
            f"SELECT * FROM textbook_examples WHERE skill_id IN ({placeholders}) ORDER BY skill_id, id",
            skill_ids,
        )
    # also catch by chapter field if present
    if "chapter" in te_cols:
        extra = rows(
            conn,
            """
            SELECT * FROM textbook_examples
            WHERE (chapter LIKE '%第4章%' OR chapter LIKE '%圓與直線%' OR section LIKE '4-%')
              AND skill_id LIKE 'vh_%B2%'
            ORDER BY skill_id, id
            """,
        )
        seen_ids = {e.get("id") for e in examples}
        for e in extra:
            if e.get("id") not in seen_ids:
                examples.append(e)

    # Integrity
    dup_keys = Counter()
    empty_text = []
    binding_issues = []
    contamination = []
    for e in examples:
        title = str(e.get("title") or e.get("source_description") or "")
        text = str(e.get("problem_text") or e.get("question_text") or e.get("content") or "")
        sid = str(e.get("skill_id") or "")
        key = (
            sid,
            title.strip(),
            hashlib.sha1(text.strip().encode("utf-8", errors="ignore")).hexdigest()[:12],
        )
        dup_keys[key] += 1
        if not text.strip():
            empty_text.append({"id": e.get("id"), "skill_id": sid, "title": title})
        if not is_ch4_skill(sid, e.get("chapter"), e.get("section")):
            # still in query by skill list — check section string
            sec = str(e.get("section") or "")
            if sec and not sec.startswith("4-") and "第4" not in str(e.get("chapter") or ""):
                binding_issues.append({"id": e.get("id"), "skill_id": sid, "section": sec})
        # contamination: skill id chapter number
        m = re.search(r"SubSection_(\d+)_", sid)
        if m and int(m.group(1)) != 4:
            contamination.append({"id": e.get("id"), "skill_id": sid, "title": title})

    duplicates = [
        {"skill_id": k[0], "title": k[1], "text_hash": k[2], "count": c}
        for k, c in dup_keys.items()
        if c > 1
    ]

    repo_hits = search_repo_capabilities()
    # detect published v3 for ch4
    v3_skills = set()
    skills_dir = ROOT / "skills"
    asv3 = ROOT / "agent_skills_v3"
    for base in (skills_dir, asv3):
        if not base.exists():
            continue
        for p in base.iterdir():
            name = p.name
            if "B2_SubSection_4_" in name or re.search(r"數學B2_SubSection_4_", name):
                v3_skills.add(name)

    # Per skill inventory
    by_skill = defaultdict(list)
    for e in examples:
        by_skill[str(e.get("skill_id"))].append(e)

    inventory_skills = []
    capability_rows = []
    visual_rows = []
    family_rows = []

    for s in formal_skills:
        sid = s["skill_id"]
        name = s.get("skill_ch_name") or s.get("paragraph") or sid
        items = by_skill.get(sid, [])
        groups = Counter()
        visual_n = 0
        fams = []
        existing_covered = 0
        for e in items:
            title = str(e.get("title") or e.get("source_description") or "")
            text = str(e.get("problem_text") or e.get("question_text") or e.get("content") or "")
            g = classify_source_group(title, e.get("source_kind") or e.get("source_type"))
            groups[g] += 1
            fam = infer_family_from_text(sid, title, text)
            fams.append(fam)
            vis = has_visual(e)
            if vis:
                visual_n += 1
            vclass = visual_class(e, fam)
            visual_rows.append(
                {
                    "id": e.get("id"),
                    "skill_id": sid,
                    "title": title[:120],
                    "family": fam,
                    "visual_class": vclass,
                    "has_asset_signal": vis,
                }
            )
            family_rows.append(
                {
                    "id": e.get("id"),
                    "skill_id": sid,
                    "title": title[:120],
                    "family": fam,
                    "group": g,
                }
            )

        uniq_fams = sorted(set(fams))
        # none of ch4 families are existing-covered yet unless v3 present
        has_v3 = any(sid in x or x.endswith(sid) for x in v3_skills) or sid in v3_skills
        # also check directory name match
        has_v3 = has_v3 or (skills_dir / sid).exists() or (asv3 / sid).exists()

        cap_class, route, why = skill_classification(sid, uniq_fams, repo_hits, has_v3)
        # refine: if NEW_DOMAIN and only visual applied families
        if all(f.startswith("unclassified") for f in uniq_fams) and not items:
            route = "DATA_REPAIR_REQUIRED"
            why = "No imported formal exercises bound to this skill"
            cap_class = "UNKNOWN"

        inventory_skills.append(
            {
                "skill_id": sid,
                "skill_name": name,
                "section": s.get("section"),
                "paragraph": s.get("paragraph"),
                "display_order": s.get("display_order"),
                "source_count": len(items),
                "group_breakdown": dict(groups),
                "visual_count": visual_n,
                "recognized_families": uniq_fams,
                "recognized_family_count": len(uniq_fams),
                "existing_covered_count": existing_covered,
                "missing_family_count": len(uniq_fams),
            }
        )
        capability_rows.append(
            {
                "skill_id": sid,
                "skill_name": name,
                "source_count": len(items),
                "existing_domain": (
                    "none_dedicated_circle"
                    if not any(re.search(r"(?<!circum)circle", x, re.I) for x in repo_hits["domain_modules"])
                    else "circle_related"
                ),
                "related_existing_modules": [
                    x
                    for x in repo_hits["domain_modules"]
                    if re.search(r"line_equation|coordinate|circle", x, re.I)
                ],
                "existing_families": [],
                "missing_families": uniq_fams,
                "classification": cap_class,
                "recommended_route": route,
                "why": why,
                "has_v3_assets": has_v3,
            }
        )

    # Chapter structure summary
    sections = {}
    for s in formal_skills:
        sec = str(s.get("section") or "")
        sections.setdefault(sec, {"section": sec, "skills": []})
        sections[sec]["skills"].append(
            {
                "skill_id": s["skill_id"],
                "skill_name": s.get("skill_ch_name") or s.get("paragraph"),
                "paragraph": s.get("paragraph"),
                "display_order": s.get("display_order"),
            }
        )

    chapter_title = None
    for s in formal_skills:
        if s.get("chapter"):
            chapter_title = s["chapter"]
            break
    if not chapter_title:
        chapter_title = "第4章 圓與直線"

    group_totals = Counter()
    for s in inventory_skills:
        for g, n in (s.get("group_breakdown") or {}).items():
            group_totals[g] += n

    visual_counts = Counter(v["visual_class"] for v in visual_rows)
    route_counts = Counter(c["recommended_route"] for c in capability_rows)

    inventory = {
        "chapter": chapter_title,
        "volume": "B2",
        "curriculum": "vocational",
        "sections": list(sections.values()),
        "skills": inventory_skills,
        "outline_skills": outline_skills,
        "totals": {
            "formal_skills": len(formal_skills),
            "formal_exercises": len(examples),
            "group_breakdown": dict(group_totals),
            "visual_count": sum(s["visual_count"] for s in inventory_skills),
        },
        "examples_sample_columns": te_cols,
    }

    integrity = {
        "duplicates": duplicates,
        "duplicate_count": len(duplicates),
        "empty_problem_text": empty_text,
        "empty_problem_text_count": len(empty_text),
        "binding_issues": binding_issues,
        "binding_issue_count": len(binding_issues),
        "cross_chapter_contamination": contamination,
        "contamination_count": len(contamination),
        "notes": [
            "intentional_skip not treated as coverage",
            "Read-only verification against imported DB",
        ],
    }

    capability = {
        "repo_search": repo_hits,
        "v3_skill_dirs_found": sorted(v3_skills),
        "skills": capability_rows,
        "families_by_source": family_rows,
        "route_counts": dict(route_counts),
    }

    visual = {
        "items": visual_rows,
        "counts": {
            "A_dynamic_existing": visual_counts.get("A", 0),
            "B_pdf_crop": visual_counts.get("B", 0),
            "C_parametric": visual_counts.get("C", 0),
            "D_no_visual": visual_counts.get("D", 0),
            "E_human_review": visual_counts.get("E", 0),
        },
        "legend": {
            "A": "existing reusable dynamic visual",
            "B": "paired-PDF crop appropriate",
            "C": "parametric/generated visual appropriate",
            "D": "no visual needed",
            "E": "human review needed",
        },
    }

    # also attach integrity into inventory report for convenience
    inventory["integrity"] = integrity

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = {
        "inventory": OUT_DIR / "b2_ch4_inventory.json",
        "capability": OUT_DIR / "b2_ch4_capability_preflight.json",
        "visual": OUT_DIR / "b2_ch4_visual_inventory.json",
    }
    paths["inventory"].write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["capability"].write_text(json.dumps(capability, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["visual"].write_text(json.dumps(visual, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "chapter": chapter_title,
        "formal_skills": len(formal_skills),
        "formal_exercises": len(examples),
        "group_breakdown": dict(group_totals),
        "integrity": {
            "duplicates": len(duplicates),
            "empty_text": len(empty_text),
            "binding": len(binding_issues),
            "contamination": len(contamination),
        },
        "routes": dict(route_counts),
        "visual_counts": visual["counts"],
        "skills": [
            {
                "skill_id": c["skill_id"],
                "name": c["skill_name"],
                "n": c["source_count"],
                "class": c["classification"],
                "route": c["recommended_route"],
                "missing_families": c["missing_families"],
            }
            for c in capability_rows
        ],
        "report_paths": {k: str(v) for k, v in paths.items()},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
