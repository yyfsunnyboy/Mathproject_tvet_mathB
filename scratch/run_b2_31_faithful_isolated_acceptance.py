"""One-off isolated B2 3-1 acceptance verification; never opens production DB writable."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
import argparse
from pathlib import Path

from flask import Flask


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SOURCE_DB = ROOT / "instance" / "kumon_math.db"
WORK = ROOT / "scratch" / "b2_31_faithful_isolated"
ISOLATED_DB = WORK / "kumon_math.db"
DOCX = ROOT / "textbook_import" / "source" / "vocational" / "math_B2" / "第三章 3-1 向量的作圖-課本.docx"
LATEX_DOCX = DOCX.with_name("第三章 3-1 向量的作圖-課本_Latex.docx")
SKILLS = [f"vh_數學B2_SubSection_3_1_{n}" for n in range(1, 5)]
MANUAL = {
    "3-1習題基礎題1": SKILLS[3], "3-1習題基礎題2": SKILLS[1],
    "3-1習題基礎題3": SKILLS[2], "3-1習題基礎題4": SKILLS[2],
    "3-1習題基礎題5": SKILLS[3], "3-1習題基礎題6": SKILLS[3],
    "3-1習題基礎題7": SKILLS[3], "3-1習題基礎題8": SKILLS[3],
    "3-1習題進階題9": SKILLS[3], "3-1習題進階題10": SKILLS[3],
}


def compact(value: object) -> str:
    return "".join(str(value or "").split())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(db_path: Path, sql: str, params: tuple = ()) -> list[dict]:
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql, params)]
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply-production",
        action="store_true",
        help="Explicitly run the verified missing-only Phase 4 backfill on production.",
    )
    args = parser.parse_args()
    target_db = SOURCE_DB if args.apply_production else ISOLATED_DB
    WORK.mkdir(parents=True, exist_ok=True)
    production_hash_before = sha256(SOURCE_DB)
    if not args.apply_production:
        # The live SQLite database uses WAL.  Copying only the main .db file omits
        # committed WAL pages (including the UI-visible skills), so use SQLite's
        # read-only backup API to make one transactionally consistent isolated copy.
        source_conn = sqlite3.connect(f"file:{SOURCE_DB.as_posix()}?mode=ro", uri=True)
        target_conn = sqlite3.connect(ISOLATED_DB)
        try:
            source_conn.backup(target_conn)
        finally:
            target_conn.close()
            source_conn.close()

    skill_sql = """
        select si.skill_id, si.skill_ch_name, si.is_active, sc.curriculum, sc.grade,
               sc.volume, sc.chapter, sc.section, sc.paragraph, sc.display_order
          from skills_info si join skill_curriculum sc on sc.skill_id = si.skill_id
         where si.skill_id in (?,?,?,?) order by si.skill_id, sc.id
    """
    candidate_before = rows(target_db, skill_sql, tuple(SKILLS))
    assert len(candidate_before) == 4, candidate_before
    coords = tuple(candidate_before[0][k] for k in ("curriculum", "volume", "chapter", "section"))
    example_sql = """
        select id, skill_id, source_description, problem_type, problem_text
          from textbook_examples
         where source_curriculum=? and source_volume=? and source_chapter=? and source_section=?
         order by id
    """
    before = rows(target_db, example_sql, coords)
    assert len(before) == 13, len(before)
    formal_before = rows(target_db, "select count(*) as count from skills_info where skill_id like 'vh_%'")[0]["count"]

    # No create_app(): that path bootstraps database content.  Bind models directly
    # to the byte-for-byte copy so this process has no authority to initialize skills.
    app = Flask("b2_31_faithful_isolated")
    app.config.update(SQLALCHEMY_DATABASE_URI=f"sqlite:///{target_db.as_posix()}", SQLALCHEMY_TRACK_MODIFICATIONS=False)
    from models import db
    db.init_app(app)
    with app.app_context():
        import core.textbook_processor_v2 as tpv2
        from core.textbook_importer_v3_orchestrate import build_curriculum_info_for_v3_import
        from core.textbook_importer_v3_pipeline import audit_v3_skill_extraction, _fill_chapter_section_from_outline_or_lines
        from core.textbook_structural_metadata import align_structural_metadata

        info = build_curriculum_info_for_v3_import(
            latex_docx_path=LATEX_DOCX, original_docx_filename=DOCX.name,
            curriculum="vocational", publisher="longteng", grade=10, volume="數學B2",
        )
        lines = tpv2.phase1_extract_docx_lines(str(LATEX_DOCX), curriculum_info=info)
        scope = tpv2._resolve_import_source_metadata(
            parse_filename=str(info.get("parse_filename") or DOCX.name), lines=lines, curriculum_info=info,
        )
        assert scope["source_scope"] == "section_textbook", scope
        info = scope["curriculum_info"]
        audit = audit_v3_skill_extraction(DOCX, info, lines)
        assert audit["curriculum_binding"] == "PASS", audit
        info = _fill_chapter_section_from_outline_or_lines(audit["curriculum_info"], lines)
        blocks = tpv2.phase2_deterministic_block_slice(lines, source_scope="section_textbook", curriculum_info=info)
        meta = dict(tpv2._DOCX_BLOCK_META)
        for key in meta:
            meta[key]["problem_text"] = str(blocks.get(key) or "")
        assert len(blocks) == 23 == len(meta), (len(blocks), len(meta))
        parsed = align_structural_metadata(sorted(blocks), meta, info)

        all_items = [item for chapter in parsed["chapters"] for section in chapter["sections"]
                     for concept in section["concepts"] for bucket in ("examples", "practice_questions")
                     for item in concept.get(bucket, [])]
        assert len(all_items) == 23, len(all_items)
        applied = []
        for item in all_items:
            label = compact(item.get("title"))
            if label in MANUAL:
                item["skill_id"] = MANUAL[label]
                item["mapping_status"] = "manual_backfill"
                item["needs_skill_resolution"] = False
                applied.append(label)
        assert sorted(applied) == sorted(MANUAL), applied

        stats = tpv2.phase4_absolute_hydrate_and_save(
            parsed, blocks, info, queue=None, commit=True,
            insert_missing_only=args.apply_production,
        )

    after = rows(target_db, example_sql, coords)
    formal_after = rows(target_db, "select count(*) as count from skills_info where skill_id like 'vh_%'")[0]["count"]
    original_before = {r["source_description"]: r["skill_id"] for r in before}
    original_after = {r["source_description"]: r["skill_id"] for r in after if r["source_description"] in original_before}
    inserted = [r for r in after if compact(r["source_description"]) in MANUAL]
    duplicate_count = rows(target_db, """
        select count(*) as count from (
          select source_description, problem_type, count(*) n from textbook_examples
           where source_curriculum=? and source_volume=? and source_chapter=? and source_section=?
           group by source_description, problem_type having n > 1
        )
    """, coords)[0]["count"]
    production_hash_after = sha256(SOURCE_DB)
    report = {
        "source_db": str(SOURCE_DB), "target_db": str(target_db),
        "apply_production": args.apply_production,
        "production_hash_unchanged": (production_hash_before == production_hash_after) if not args.apply_production else None,
        "candidate_skills": candidate_before, "before_count": len(before), "after_count": len(after),
        "formal_skills_before": formal_before, "formal_skills_after": formal_after,
        "formal_skill_created": formal_after - formal_before,
        "phase4": stats, "original_13_unchanged": original_before == original_after,
        "manual_rows": [{k: r[k] for k in ("source_description", "skill_id", "problem_type", "problem_text")} for r in inserted],
        "manual_count": len(inserted), "duplicate_count": duplicate_count,
        "all_manual_in_candidate_set": all(r["skill_id"] in SKILLS for r in inserted),
        "all_23_have_skill": all(bool(r["skill_id"]) for r in after),
    }
    report_name = "production_backfill_report.json" if args.apply_production else "report.json"
    (WORK / report_name).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
