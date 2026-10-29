"""Isolated Stage 1 rehearsal of Unit 5 with the STAGED (pending) visual region for 進階題12.

Same import path as reports/gh_math2_unit5_stage1_repair/replay_isolated.py (copied sources, copied SQLite, no external AI); the only
difference is that the existing human-review hook ``verified_visual_regions`` returns the staged region with a placeholder reviewer
marked as an isolated rehearsal.  The live configs/stage1_verified_visual_regions.json is never read for writing and must not change.

    python reports/gh_math2_unit5_fixed/rehearse_unit5_fixed.py
"""
import contextlib
import hashlib
import io
import json
import os
import queue
import shutil
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = HERE / "sandbox"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "reports/gh_math2_unit5_stage1_repair"))
import replay_isolated as R  # noqa: E402  (helpers only: sha, copy_formal, reconstructed_metadata, snapshot)

LIVE_FILES = [ROOT / "configs/stage1_verified_visual_regions.json", ROOT / "configs/fixed_textbook_practice.json"]
BASELINE = ROOT / "reports/gh_math2_unit5_stage1_repair/dry_run_raw.json"
TARGET = "general_2_section_advanced_exercise_012_037"
VISUAL_KEYS = ("image_assets", "has_image", "needs_image_review", "visual_status", "visual_review_reasons", "pdf_visual_status",
               "pdf_visual_enrichment", "visual_required_missing", "needs_review", "image_warning", "image_warning_resolved_by")


def file_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    live_before = {str(p): file_sha(p) for p in LIVE_FILES}
    if PRIVATE.exists():
        shutil.rmtree(PRIVATE)
    PRIVATE.mkdir(parents=True)
    temp = PRIVATE / "temp"
    temp.mkdir()
    os.environ.update({"TMP": str(temp), "TEMP": str(temp), "TMPDIR": str(temp), "SEED_DB_ONLY": "1"})
    tempfile.tempdir = str(temp)
    record = json.loads(R.RECORD.read_text(encoding="utf-8"))
    sources = {}
    for kind in ("docx", "pdf"):
        src = ROOT / record["sources"][kind]["stored_path"]
        assert R.sha(src) == record["sources"][kind]["sha256"]
        dst = PRIVATE / f"05-.{kind}"
        shutil.copy2(src, dst)
        sources[kind] = dst
    staged = json.loads((HERE / "staged_visual_region.json").read_text(encoding="utf-8"))["source"]
    assert staged["pdf_sha256"] == R.sha(sources["pdf"])
    rehearsal_region = {**staged, "verified_by": "ISOLATED_REHEARSAL_pending_teacher_confirmation", "verified_on": "rehearsal"}

    before, after, sandbox_db = PRIVATE / "formal_before.db", PRIVATE / "formal_after.db", PRIVATE / "unit5.db"
    R.copy_formal(before)
    shutil.copy2(before, sandbox_db)

    import config
    prior = config.Config.SQLALCHEMY_DATABASE_URI, config.Config.UPLOAD_FOLDER
    config.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + sandbox_db.as_posix()
    config.Config.UPLOAD_FOLDER = str(PRIVATE / "uploads")
    from app import create_app
    from models import TextbookExample, db
    from core.general_textbook_replacement import scope_fingerprint, validate_replacement_scope
    import core.textbook_processor as processor
    import core.textbook_stage1_auto_review as review

    app = create_app(production=False)
    app.root_path = str(PRIVATE)
    app.config["UPLOAD_FOLDER"] = str(PRIVATE / "uploads")
    cap = {"visual_summary": None, "rows": []}
    original = (processor.call_gemini_for_analysis, processor.enrich_general_high_pdf_visuals, review._default_ai_review,
                review.verified_visual_regions)
    processor.call_gemini_for_analysis = lambda *a, **kw: json.dumps(R.reconstructed_metadata(), ensure_ascii=False)
    review._default_ai_review = lambda items, skills: []

    def regions(pdf_path, *, curriculum, volume, chapter):
        hit = (R.sha(Path(pdf_path)), curriculum, volume, chapter) == (staged["pdf_sha256"], staged["curriculum"], staged["volume"], staged["chapter"])
        cap["region_hook_called"] = {"curriculum": curriculum, "volume": volume, "chapter": chapter, "matched": hit}
        return rehearsal_region if hit else None

    def visual(*a, **kw):
        cap["visual_summary"] = original[1](*a, **kw)
        return cap["visual_summary"]

    review.verified_visual_regions = regions
    processor.enrich_general_high_pdf_visuals = visual
    q, out, err, result = queue.Queue(), io.StringIO(), io.StringIO(), None
    try:
        with app.app_context():
            assert Path(db.engine.url.database).resolve() == sandbox_db.resolve()
            old = TextbookExample.query.filter_by(source_curriculum="general", source_volume="數學2", source_chapter=R.CHAPTER).order_by(TextbookExample.id).all()
            assert len(old) == 28
            validate_replacement_scope(old, expected_ids=[r.id for r in old], incoming_sha256=R.sha(sources["docx"]))
            policy = {"docx_primary": True, "pdf_optional_enrich": True, "docx_formula_source_mode": "converted_docx_latex",
                      "formula_postprocess_mode": "convert_only", "auto_stage1_review": True,
                      "general_replacement": {"preview": {"volume": "數學2", "chapter": R.CHAPTER, "question_count": 37, "docx_sha256": R.sha(sources["docx"])},
                                              "old_ids": [r.id for r in old], "old_rows_fingerprint": scope_fingerprint(old), "backup_path": str(before)},
                      "retained_source_provenance": {str(sources[k]): record["sources"][k] for k in sources},
                      "source_original_filenames": {str(sources[k]): record["sources"][k]["original_filename"] for k in sources}}
            (PRIVATE / "reports/import_debug").mkdir(parents=True, exist_ok=True)
            cwd = Path.cwd()
            os.chdir(PRIVATE)
            try:
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    result = processor.process_textbook_file(
                        str(sources["docx"]), {"curriculum": "general", "publisher": "longteng", "grade": 10, "volume": "數學2"}, q,
                        skip_code_gen=True, import_policy=policy, optional_enrich_pdf_path=str(sources["pdf"]))
            finally:
                os.chdir(cwd)
            rows = TextbookExample.query.filter_by(source_curriculum="general", source_volume="數學2", source_chapter=R.CHAPTER).order_by(TextbookExample.id).all()
            cap["rows"] = R.snapshot(rows)
            from core.textbook_stage1_gate import evaluate_stage1_gate
            cap["gate_recomputed"] = evaluate_stage1_gate(rows)
            db.session.remove()
    finally:
        (processor.call_gemini_for_analysis, processor.enrich_general_high_pdf_visuals, review._default_ai_review,
         review.verified_visual_regions) = original
        config.Config.SQLALCHEMY_DATABASE_URI, config.Config.UPLOAD_FOLDER = prior
        R.copy_formal(after)

    gate = (result or {}).get("stage1_gate") or {}
    rows = cap["rows"]
    by_anchor = {(r["notes"].get("question_anchor") or {}).get("anchor_id"): r for r in rows}
    target = by_anchor[TARGET]
    assets = target["notes"].get("image_assets") or []
    asset_files = [{"path": a.get("path"), "exists": (PRIVATE / a["path"]).is_file(), "sha256": a.get("sha256"),
                    "bbox": a.get("bbox"), "visual_status": a.get("visual_status"), "question_anchor": a.get("question_anchor"),
                    "source_page": a.get("source_page"), "reason": a.get("reason")} for a in assets]

    # Other 36 rows vs the previous isolated replay (same sources, no region): content, skill and anchor must be identical.
    base = {(r["notes"].get("question_anchor") or {}).get("anchor_id"): r
            for r in json.loads(BASELINE.read_text(encoding="utf-8"))["capture"]["post_review_rows"]}

    sandbox_paths = [str(ROOT / "reports/gh_math2_unit5_stage1_repair/sandbox"), str(PRIVATE)]

    def unpath(value):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
        for p in sandbox_paths:  # the copied sources live in a per-run sandbox; only that directory differs
            text = text.replace(json.dumps(p)[1:-1], "<SANDBOX>").replace(json.dumps(json.dumps(p)[1:-1])[1:-1], "<SANDBOX>")
        return text

    def strip(r):
        n = {k: v for k, v in r["notes"].items() if k not in VISUAL_KEYS}
        # Auto-review entries hash a notes snapshot that embeds the sandbox path; the snapshot itself is compared via before/after.
        n["stage1_auto_review"] = [{k: v for k, v in e.items() if k not in ("before_sha256", "after_sha256")} if isinstance(e, dict) else e
                                   for e in (n.get("stage1_auto_review") or [])]
        return {"label": r["label"], "skill_id": r["skill_id"], "problem_text": r["problem_text"], "detailed_solution": r["detailed_solution"], "notes": unpath(n)}

    diffs = [a for a in base if a != TARGET and strip(base[a]) != strip(by_anchor.get(a, {"label": None, "skill_id": None, "problem_text": None, "detailed_solution": None, "notes": {}}))]
    visual_diffs = [a for a in base if a != TARGET and {k: base[a]["notes"].get(k) for k in VISUAL_KEYS if k != "pdf_visual_enrichment"}
                    != {k: by_anchor[a]["notes"].get(k) for k in VISUAL_KEYS if k != "pdf_visual_enrichment"}]
    target_core_same = {k: v for k, v in strip(base[TARGET]).items() if k != "notes"} == {k: v for k, v in strip(target).items() if k != "notes"}
    live_after = {str(p): file_sha(p) for p in LIVE_FILES}
    report = {
        "evidence_type": "new_isolated_rehearsal_with_staged_region",
        "original_evidence_status": "original_evidence_unavailable",
        "metadata_basis": "reconstructed_title_inventory; original_Gemini_response_unavailable",
        "staged_region_status": "pending_teacher_confirmation (placeholder reviewer used only inside this rehearsal)",
        "region_hook": cap.get("region_hook_called"),
        "manual_region_overrides_applied": ((cap["visual_summary"] or {}).get("enrichment") or {}).get("manual_region_overrides_applied"),
        "gate_returned_by_import": {k: gate.get(k) for k in ("status", "stage1_ready", "rows", "blocked", "needs_review", "reasons")},
        "gate_log_line": next((str(m) for m in list(q.queue) if "[STAGE1 GATE]" in str(m)), None),
        "gate": {k: (cap.get("gate_recomputed") or {}).get(k) for k in ("status", "stage1_ready", "rows", "blocked", "needs_review", "reasons")},
        "import_result_type": type(result).__name__,
        "import_result_keys": sorted(result) if isinstance(result, dict) else None,
        "import_result_status": (result or {}).get("status") if isinstance(result, dict) else None,
        "auto_review_issues": ((result or {}).get("stage1_auto_review") or {}).get("issues"),
        "rows": len(rows), "unique_anchors": len(by_anchor),
        "target": {"id": target["id"], "label": target["label"], "skill_id": target["skill_id"],
                   "pdf_visual_status": target["notes"].get("pdf_visual_status"), "visual_required_missing": target["notes"].get("visual_required_missing"),
                   "question_anchor": target["notes"].get("question_anchor"), "image_assets": asset_files,
                   "stem_skill_solution_identical_to_previous_replay": target_core_same},
        "other_36_rows": {"content_skill_anchor_diffs": diffs, "visual_state_diffs": visual_diffs},
        "live_config_unchanged": live_before == live_after,
        "formal_db_zero_change": R.sha(before) == R.sha(after),
        "formal_db_sha256": {"before": R.sha(before), "after": R.sha(after)},
    }
    (HERE / "rehearsal_result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "rehearsal_log.txt").write_text("\n".join(str(m) for m in list(q.queue)) + "\nSTDOUT\n" + out.getvalue() + "\nSTDERR\n" + err.getvalue(), encoding="utf-8")
    for p in (before, after):
        p.unlink()
    print(json.dumps({k: report[k] for k in ("gate", "auto_review_issues", "rows", "unique_anchors", "other_36_rows", "live_config_unchanged", "formal_db_zero_change")}, ensure_ascii=False))
    print(json.dumps(report["target"]["image_assets"], ensure_ascii=False))


if __name__ == "__main__":
    main()
