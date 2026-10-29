"""Replay the Unit 5 V1 import on a fresh copy of the formal DB with the LIVE verified-region catalog (teacher approved 2026-10-29).

Same path as reports/gh_math2_unit5_fixed/rehearse_unit5_fixed.py, but the region hook is not replaced and the authoritative
uploaded sources are used in place (as in reports/gh_math2_unit4_stage1/replay_isolated.py).  Only the Gemini title grouping is
reconstructed (original response not persisted).  The formal DB is read through the SQLite backup API only.

    python reports/gh_math2_unit5_stage1_formal/replay_formal.py
"""
import contextlib, hashlib, io, json, os, queue, shutil, sys, tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = HERE / "tmp" / "replay"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "reports/gh_math2_unit5_stage1_repair"))
import replay_isolated as R  # noqa: E402  (sha, copy_formal, reconstructed_metadata, snapshot, RECORD, CHAPTER)

TARGET = "general_2_section_advanced_exercise_012_037"


def main():
    if PRIVATE.exists():
        shutil.rmtree(PRIVATE)
    (PRIVATE / "temp").mkdir(parents=True)
    (PRIVATE / "reports/import_debug").mkdir(parents=True)
    os.environ.update({"TMP": str(PRIVATE / "temp"), "TEMP": str(PRIVATE / "temp"), "TMPDIR": str(PRIVATE / "temp"), "SEED_DB_ONLY": "1"})
    tempfile.tempdir = str(PRIVATE / "temp")
    record = json.loads(R.RECORD.read_text(encoding="utf-8"))
    sources = {k: ROOT / record["sources"][k]["stored_path"] for k in ("docx", "pdf")}
    for k, p in sources.items():
        assert R.sha(p) == record["sources"][k]["sha256"], k
    sandbox_db = PRIVATE / "unit5.db"
    R.copy_formal(sandbox_db)
    formal_sha_before = R.sha(R.FORMAL)

    import config
    config.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + sandbox_db.as_posix()
    config.Config.UPLOAD_FOLDER = str(PRIVATE / "uploads")
    from app import create_app
    from models import TextbookExample, db
    from core.general_textbook_replacement import scope_fingerprint, validate_replacement_scope
    from core.textbook_stage1_gate import evaluate_stage1_gate
    import core.textbook_processor as processor
    import core.textbook_stage1_auto_review as review

    app = create_app(production=False)
    app.root_path = str(PRIVATE)
    app.config["UPLOAD_FOLDER"] = str(PRIVATE / "uploads")
    processor.call_gemini_for_analysis = lambda *a, **kw: json.dumps(R.reconstructed_metadata(), ensure_ascii=False)
    review._default_ai_review = lambda items, skills: []
    q, out, err = queue.Queue(), io.StringIO(), io.StringIO()
    with app.app_context():
        assert Path(db.engine.url.database).resolve() == sandbox_db.resolve()
        old = TextbookExample.query.filter_by(source_curriculum="general", source_volume="數學2", source_chapter=R.CHAPTER).order_by(TextbookExample.id).all()
        assert len(old) == 28
        validate_replacement_scope(old, expected_ids=[r.id for r in old], incoming_sha256=R.sha(sources["docx"]))
        policy = {"docx_primary": True, "pdf_optional_enrich": True, "docx_formula_source_mode": "converted_docx_latex",
                  "formula_postprocess_mode": "convert_only", "auto_stage1_review": True,
                  "general_replacement": {"preview": {"volume": "數學2", "chapter": R.CHAPTER, "question_count": 37, "docx_sha256": R.sha(sources["docx"])},
                                          "old_ids": [r.id for r in old], "old_rows_fingerprint": scope_fingerprint(old), "backup_path": str(sandbox_db)},
                  "retained_source_provenance": {str(sources[k]): record["sources"][k] for k in sources},
                  "source_original_filenames": {str(sources[k]): record["sources"][k]["original_filename"] for k in sources}}
        cwd = Path.cwd()
        os.chdir(PRIVATE)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                result = processor.process_textbook_file(
                    str(sources["docx"]), {"curriculum": "general", "publisher": "longteng", "grade": 10, "volume": "數學2"}, q,
                    skip_code_gen=True, import_policy=policy, optional_enrich_pdf_path=str(sources["pdf"]))
        finally:
            os.chdir(cwd)
        db.session.expire_all()
        rows = TextbookExample.query.filter_by(source_curriculum="general", source_volume="數學2", source_chapter=R.CHAPTER).order_by(TextbookExample.id).all()
        gate = evaluate_stage1_gate(rows)
        snap = R.snapshot(rows)
        db.session.remove()

    by_anchor = {(r["notes"].get("question_anchor") or {}).get("anchor_id"): r for r in snap}
    with_assets = {r["id"]: r["notes"].get("image_assets") for r in snap if r["notes"].get("image_assets")}
    target = by_anchor[TARGET]
    assets = [{"path": a["path"], "sha256": a.get("sha256"), "exists": (PRIVATE / a["path"]).is_file(),
               "file_sha256": R.sha(PRIVATE / a["path"]) if (PRIVATE / a["path"]).is_file() else None,
               "visual_status": a.get("visual_status"), "bbox": a.get("bbox"), "source_page": a.get("source_page")}
              for a in target["notes"].get("image_assets") or []]
    rehearsal = {(r["notes"].get("question_anchor") or {}).get("anchor_id"): r
                 for r in json.loads((ROOT / "reports/gh_math2_unit5_stage1_repair/dry_run_raw.json").read_text(encoding="utf-8"))["capture"]["post_review_rows"]}
    content_diffs = [a for a in rehearsal if (rehearsal[a]["label"], rehearsal[a]["skill_id"], rehearsal[a]["problem_text"], rehearsal[a]["detailed_solution"])
                     != (by_anchor[a]["label"], by_anchor[a]["skill_id"], by_anchor[a]["problem_text"], by_anchor[a]["detailed_solution"])]
    report = {
        "metadata_basis": "reconstructed_title_inventory; original_Gemini_response_unavailable",
        "region_source": "configs/stage1_verified_visual_regions.json (live, verified_by=teacher, 2026-10-29)",
        "import_status": (result or {}).get("status"),
        "gate_from_import": {k: ((result or {}).get("stage1_gate") or {}).get(k) for k in ("status", "stage1_ready", "reasons")},
        "gate": {"status": gate.get("status"), "stage1_ready": gate.get("stage1_ready"), "blocked": len(gate.get("blocked") or []),
                 "needs_review": len(gate.get("needs_review") or []), "reasons": gate.get("reasons")},
        "rows": len(snap), "ids": [snap[0]["id"], snap[-1]["id"]], "unique_anchors": len(by_anchor),
        "skills": {s: sum(1 for r in snap if r["skill_id"] == s) for s in sorted({r["skill_id"] for r in snap})},
        "rows_with_assets": sorted(with_assets), "target_id": target["id"], "target_pdf_visual_status": target["notes"].get("pdf_visual_status"),
        "target_assets": assets,
        "content_diffs_vs_stage1_dry_run": content_diffs,
        "formal_db_unchanged": R.sha(R.FORMAL) == formal_sha_before,
    }
    (HERE / "replay_formal_result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "replay_formal_log.txt").write_text("\n".join(str(m) for m in list(q.queue)) + "\nSTDOUT\n" + out.getvalue() + "\nSTDERR\n" + err.getvalue(), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
