import sys
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / '.env')

from app import create_app
from models import db, TextbookExample, SkillInfo, SkillCurriculum
import core.textbook_importer_v3_pipeline as pipeline
from core.textbook_importer_v3_orchestrate import find_b2_11_source_pair

app = create_app()

with app.app_context():
    # 1. Inspect existing B2 1-1 rows before deletion
    existing_b2_11 = TextbookExample.query.filter_by(
        source_curriculum="vocational",
        source_volume="數學B2",
        source_section="1-1 角度的基本性質",
    ).all()
    deleted_count = len(existing_b2_11)
    print(f"[PRE-IMPORT] Found {deleted_count} existing B2 1-1 rows to clear.")
    
    # Delete the test/broken rows
    for r in existing_b2_11:
        db.session.delete(r)
    db.session.commit()
    print(f"[PRE-IMPORT] Cleared {deleted_count} rows from production DB.")
    
    # Verify deletion
    remaining = TextbookExample.query.filter_by(
        source_curriculum="vocational",
        source_volume="數學B2",
        source_section="1-1 角度的基本性質",
    ).count()
    assert remaining == 0, f"Expected 0 remaining, got {remaining}"

    # 2. Run official ingestion pipeline with allow_phase4=True
    pair = find_b2_11_source_pair(ROOT)
    print(f"[IMPORT] Running v3 pair pipeline on:\n  DOCX: {pair.original_docx}\n  PDF:  {pair.pdf}")
    
    report = pipeline.run_v3_pair_pipeline(
        project_root=ROOT,
        docx_path=pair.original_docx,
        pdf_path=pair.pdf,
        curriculum="vocational",
        volume="數學B2",
        allow_phase4=True,
        app=app,
    )
    print(f"[IMPORT] Pipeline result ok={report.get('ok')} error={report.get('error')}")
    
    # 3. Post-import verification directly from production DB
    imported_rows = TextbookExample.query.filter_by(
        source_curriculum="vocational",
        source_volume="數學B2",
        source_section="1-1 角度的基本性質",
    ).order_by(TextbookExample.id.asc()).all()
    
    print(f"[VERIFY] Total imported B2 1-1 rows in DB: {len(imported_rows)}")
    
    # MATH_PARSE_FAILED check
    mpf_count = sum(
        (r.problem_text or "").count("MATH_PARSE_FAILED") +
        (r.detailed_solution or "").count("MATH_PARSE_FAILED")
        for r in imported_rows
    )
    print(f"[VERIFY] MATH_PARSE_FAILED count: {mpf_count}")
    
    # Skill ID distribution
    skill_dist = {}
    invalid_skills = []
    for r in imported_rows:
        skill_dist[r.skill_id] = skill_dist.get(r.skill_id, 0) + 1
        if not db.session.get(SkillInfo, r.skill_id):
            invalid_skills.append((r.id, r.skill_id))
    print(f"[VERIFY] Skill distribution: {skill_dist}")
    print(f"[VERIFY] Invalid skills count: {len(invalid_skills)}")
    
    # Chapter and section check
    ch_sec_invalid = [
        (r.id, r.source_chapter, r.source_section)
        for r in imported_rows
        if r.source_chapter != "第1章 三角函數" or r.source_section != "1-1 角度的基本性質"
    ]
    print(f"[VERIFY] Invalid chapter/section count: {len(ch_sec_invalid)}")
    
    # Visual references in notes
    mounted_visuals = []
    invalid_visual_refs = []
    for r in imported_rows:
        notes = {}
        if r.notes:
            try:
                notes = json.loads(r.notes)
            except Exception:
                pass
        va = notes.get("visual_assets") or []
        if va:
            mounted_visuals.append((r.id, r.source_description, len(va)))
            for asset in va:
                fp = asset.get("file_path") or asset.get("relative_path") or asset.get("url")
                if fp:
                    # check if file exists
                    full_p = ROOT / fp if not Path(fp).is_absolute() else Path(fp)
                    if not full_p.is_file():
                        invalid_visual_refs.append((r.id, fp))
    
    print(f"[VERIFY] Mounted visuals count: {len(mounted_visuals)} questions")
    for mv in mounted_visuals:
        print(f"   {mv[1]} (id={mv[0]}): {mv[2]} asset(s)")
    print(f"[VERIFY] Invalid visual references: {len(invalid_visual_refs)}")
    
    # Check old broken rows remaining
    old_ids = set(range(11587, 11606))
    old_remaining = [r.id for r in imported_rows if r.id in old_ids]
    print(f"[VERIFY] Old broken row IDs remaining: {old_remaining}")
    
    # Output summary json
    summary = {
        "deleted_count": deleted_count,
        "inserted_count": len(imported_rows),
        "final_total": len(imported_rows),
        "mpf_count": mpf_count,
        "invalid_skills_count": len(invalid_skills),
        "invalid_ch_sec_count": len(ch_sec_invalid),
        "mounted_visuals_count": len(mounted_visuals),
        "invalid_visual_refs_count": len(invalid_visual_refs),
        "old_broken_remaining": len(old_remaining),
        "pipeline_ok": report.get("ok"),
    }
    (ROOT / "reports/b2_1_1_audit/production_import_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("[DONE] Summary written to reports/b2_1_1_audit/production_import_summary.json")
