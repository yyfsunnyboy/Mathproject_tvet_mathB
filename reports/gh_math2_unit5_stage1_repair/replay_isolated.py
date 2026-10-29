"""Rebuild Unit 5 Stage 1 evidence on copied sources and an isolated SQLite DB."""

import contextlib
import hashlib
import io
import json
import os
import queue
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PRIVATE = OUT / "sandbox"
RECORD = ROOT / "textbook_import/uploaded_sources/general/數學2/12f0850f70a4f4bb1fe149c078a1b9d5f3f9927285122d4c70c09c13eb5a89d6.json"
FORMAL = ROOT / "instance/kumon_math.db"
CHAPTER = "單元5 組合"
sys.path.insert(0, str(ROOT))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def copy_formal(destination):
    with sqlite3.connect(f"file:{FORMAL.as_posix()}?mode=ro", uri=True) as source:
        with sqlite3.connect(destination) as target:
            source.backup(target)
            assert target.execute("pragma integrity_check").fetchone()[0] == "ok"


def reconstructed_metadata():
    basis = json.loads((ROOT / "reports/gh_math2_unit5_stage1_diagnostic/reconstructed_metadata_basis.json").read_text(encoding="utf-8"))
    labels = basis["labels"]
    assert len(labels) == len(set(labels)) == 37
    concepts = [
        {"concept_name": "組合", "concept_en_id": "Combination", "concept_paragraph": "甲.組合",
         "examples": [], "practice_questions": []},
        {"concept_name": "二項式定理", "concept_en_id": "BinomialTheorem", "concept_paragraph": "乙.二項式定理",
         "examples": [], "practice_questions": []},
    ]
    import re
    for title in labels:
        number = int(re.search(r"(\d+)$", title).group(1))
        binomial = ((title.startswith("例題") and number >= 6)
                    or (title.startswith("隨堂練習") and number >= 7)
                    or ("觀念澄清" in title and number == 4)
                    or ("基礎題" in title and number >= 6)
                    or ("進階題" in title and number == 11))
        example = title.startswith("例題")
        source_type = ("textbook_example" if example else "in_class_practice" if title.startswith("隨堂練習")
                       else "basic_exercise" if "基礎題" in title else "advanced_exercise" if "進階題" in title
                       else "concept_check")
        item = {"title": title, "source_description": title, "source_type": source_type,
                "problem_text": title, "correct_answer": "", "detailed_solution": ""}
        concepts[int(binomial)]["examples" if example else "practice_questions"].append(item)
    return {"chapters": [{"chapter_title": CHAPTER, "sections": [{"section_title": "5.組合", "concepts": concepts}]}]}


def snapshot(rows):
    return [{"id": row.id, "label": row.source_description.split(" [", 1)[0],
             "skill_id": row.skill_id, "problem_text": row.problem_text,
             "detailed_solution": row.detailed_solution, "notes": json.loads(row.notes or "{}")}
            for row in rows]


def main():
    PRIVATE.mkdir(parents=True, exist_ok=True)
    temp = PRIVATE / "temp"
    temp.mkdir(exist_ok=True)
    os.environ.update({"TMP": str(temp), "TEMP": str(temp), "TMPDIR": str(temp), "SEED_DB_ONLY": "1"})
    tempfile.tempdir = str(temp)
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    assert (record["curriculum"], record["volume"]) == ("general", "數學2")
    sources = {}
    for kind in ("docx", "pdf"):
        source = ROOT / record["sources"][kind]["stored_path"]
        assert source.stat().st_size == record["sources"][kind]["size_bytes"]
        assert sha(source) == record["sources"][kind]["sha256"]
        target = PRIVATE / f"05-.{kind}"
        shutil.copy2(source, target)
        assert sha(target) == sha(source)
        sources[kind] = target
    before = PRIVATE / "formal_before.db"
    after = PRIVATE / "formal_after.db"
    sandbox_db = PRIVATE / "unit5.db"
    copy_formal(before)
    shutil.copy2(before, sandbox_db)

    import config
    prior_uri, prior_upload = config.Config.SQLALCHEMY_DATABASE_URI, config.Config.UPLOAD_FOLDER
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
    captures = {"pre_review_rows": [], "post_review_rows": [], "visual_summary": None, "source_skill_map": None}
    original = (processor.call_gemini_for_analysis, processor.enrich_general_high_pdf_visuals,
                processor.apply_general_high_source_skill_map, review.review_and_heal_rows,
                review._default_ai_review)
    processor.call_gemini_for_analysis = lambda *a, **kw: json.dumps(reconstructed_metadata(), ensure_ascii=False)
    review._default_ai_review = lambda items, skills: []

    def visual(*a, **kw):
        value = original[1](*a, **kw)
        captures["visual_summary"] = value
        return value

    def source_map(*a, **kw):
        value = original[2](*a, **kw)
        captures["source_skill_map"] = value
        return value

    def auto_review(rows, **kw):
        captures["pre_review_rows"] = snapshot(rows)
        value = original[3](rows, **kw)
        captures["post_review_rows"] = snapshot(rows)
        return value

    processor.enrich_general_high_pdf_visuals = visual
    processor.apply_general_high_source_skill_map = source_map
    review.review_and_heal_rows = auto_review
    q = queue.Queue()
    stdout, stderr = io.StringIO(), io.StringIO()
    result = None
    try:
        with app.app_context():
            assert Path(db.engine.url.database).resolve() == sandbox_db.resolve()
            old_rows = TextbookExample.query.filter_by(source_curriculum="general", source_volume="數學2",
                                                       source_chapter=CHAPTER).order_by(TextbookExample.id).all()
            assert len(old_rows) == 28
            validate_replacement_scope(old_rows, expected_ids=[row.id for row in old_rows],
                                       incoming_sha256=sha(sources["docx"]))
            replacement = {"preview": {"volume": "數學2", "chapter": CHAPTER, "question_count": 37,
                                       "docx_sha256": sha(sources["docx"])},
                           "old_ids": [row.id for row in old_rows], "old_rows_fingerprint": scope_fingerprint(old_rows),
                           "backup_path": str(before)}
            policy = {"docx_primary": True, "pdf_optional_enrich": True,
                      "docx_formula_source_mode": "converted_docx_latex", "formula_postprocess_mode": "convert_only",
                      "auto_stage1_review": True, "general_replacement": replacement,
                      "retained_source_provenance": {str(sources[k]): record["sources"][k] for k in sources},
                      "source_original_filenames": {str(sources[k]): record["sources"][k]["original_filename"] for k in sources}}
            (PRIVATE / "reports/import_debug").mkdir(parents=True, exist_ok=True)
            cwd = Path.cwd()
            os.chdir(PRIVATE)
            try:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    result = processor.process_textbook_file(
                        str(sources["docx"]), {"curriculum": "general", "publisher": "longteng",
                                                    "grade": 10, "volume": "數學2"}, q, skip_code_gen=True,
                        import_policy=policy, optional_enrich_pdf_path=str(sources["pdf"]))
            finally:
                os.chdir(cwd)
            db.session.remove()
    finally:
        (processor.call_gemini_for_analysis, processor.enrich_general_high_pdf_visuals,
         processor.apply_general_high_source_skill_map, review.review_and_heal_rows,
         review._default_ai_review) = original
        config.Config.SQLALCHEMY_DATABASE_URI, config.Config.UPLOAD_FOLDER = prior_uri, prior_upload
        copy_formal(after)
    logs = [str(message) for message in list(q.queue)]
    (OUT / "dry_run_log.txt").write_text("\n".join(logs) + "\nSTDOUT\n" + stdout.getvalue() +
                                         "\nSTDERR\n" + stderr.getvalue(), encoding="utf-8")
    comparison = {"formal_before_sha256": sha(before), "formal_after_sha256": sha(after),
                  "formal_db_zero_change_confirmed": sha(before) == sha(after)}
    (OUT / "formal_db_unchanged.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    evidence = {"evidence_type": "new_isolated_dry_run_after_repair",
                "original_evidence_status": "original_evidence_unavailable", "result": result,
                "capture": captures, "source_sha256": {k: sha(v) for k, v in sources.items()},
                "metadata_basis": "reconstructed_title_inventory; original_Gemini_response_unavailable",
                "external_ai_requests": 0}
    (OUT / "dry_run_raw.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    gate = (result or {}).get("stage1_gate") or {}
    print(json.dumps({"status": (result or {}).get("status"), "gate": gate.get("status"),
                      "reasons": gate.get("reasons"), "blocked": gate.get("blocked"),
                      "needs_review": gate.get("needs_review"),
                      "auto_review_issues": ((result or {}).get("stage1_auto_review") or {}).get("issues"),
                      "rows": len(captures["post_review_rows"]), "db_unchanged": comparison["formal_db_zero_change_confirmed"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
