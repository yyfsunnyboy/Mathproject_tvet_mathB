"""Reconstruct Unit 4 metadata from the original title inventory, then replay the V1 import on DB copies.

The original Gemini JSON was not persisted. This substitutes only its recorded
title-to-concept grouping; DOCX extraction, DB write, visual enrichment, review,
Gate, replacement, publish and rollback use production functions.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import queue
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "textbook_import/uploaded_sources/general/數學2"
DOCX = SOURCE / "327f295a06d7_單元04-排列.docx"
PDF = SOURCE / "bf39d447345e_單元04-排列.pdf"
MANIFEST = SOURCE / "abe2e7906ec604d8dccdc5c8b1bbcf4df1beb162230faa454bd0e0fa810f3160.json"
FORMAL = ROOT / "instance/kumon_math.db"
CHAPTER = "單元4 排列"
VOLUME = "數學2"


def digest_rows(db_path: Path, sql: str) -> str:
    with sqlite3.connect(db_path) as con:
        return hashlib.sha256(repr(con.execute(sql).fetchall()).encode()).hexdigest()


def protected_state(db_path: Path) -> dict:
    result = {}
    result["other_textbook"] = digest_rows(
        db_path,
        "select * from textbook_examples where not "
        "(source_curriculum='general' and source_volume='數學2' and source_chapter='單元4 排列') order by id",
    )
    for table in ("users", "practice_attempts", "quiz_attempts", "progress", "mistake_notebook_entries", "mistake_logs"):
        result[table] = digest_rows(db_path, f"select * from {table} order by rowid")
    return result


def reconstructed_metadata() -> dict:
    lines = (ROOT / "reports/import_debug/數學2_unknown_title_inventory_report.md").read_text(encoding="utf8").splitlines()
    start = lines.index("## Returned Title Mapping") + 3
    labels = []
    for line in lines[start:]:
        if not line.startswith("| "):
            break
        labels.append(line.split("|")[1].strip())
    assert len(labels) == 38
    concepts = []
    groups = (
        ("LinearPermutation", "直線排列", "甲.直線排列", labels[:19]),
        ("PermutationWithIdenticalItems", "有相同物的排列", "乙.有相同物的排列", labels[19:30]),
        ("RepeatedPermutation", "重複排列", "丙.重複排列", labels[30:]),
    )
    for en, name, paragraph, group in groups:
        concept = {"concept_name": name, "concept_en_id": en, "concept_paragraph": paragraph,
                   "examples": [], "practice_questions": []}
        for label in group:
            is_example = label.startswith("例題")
            source_type = ("textbook_example" if is_example else "in_class_practice" if label.startswith("隨堂")
                           else "basic_exercise" if "基礎題" in label else "advanced_exercise" if "進階題" in label
                           else "concept_check")
            item = {"title": label, "source_description": label, "source_type": source_type,
                    "problem_text": label, "correct_answer": "", "detailed_solution": ""}
            concept["examples" if is_example else "practice_questions"].append(item)
        concepts.append(concept)
    return {"chapters": [{"chapter_title": CHAPTER,
                          "sections": [{"section_title": "4.排列", "concepts": concepts}]}]}


def run(mode: str, *, retry: bool = False) -> dict:
    import config
    from app import create_app
    from models import TextbookExample, db
    from core.general_textbook_replacement import scope_fingerprint
    import core.textbook_processor as tp
    import core.textbook_stage1_auto_review as review

    private = OUT / "tmp" / f"replay_{mode}"
    private.mkdir(parents=True, exist_ok=True)
    (private / "reports/import_debug").mkdir(parents=True, exist_ok=True)
    sandbox = private / "unit4.db"
    with sqlite3.connect(f"file:{FORMAL.as_posix()}?mode=ro", uri=True) as src, sqlite3.connect(sandbox) as dst:
        src.backup(dst)
    prior_uri = config.Config.SQLALCHEMY_DATABASE_URI
    config.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + sandbox.as_posix()
    app = create_app()
    app.config.update(TESTING=True)
    app.root_path = str(private)
    original_ai = tp.call_gemini_for_analysis
    original_regions = review.verified_visual_regions
    original_review = review.review_and_heal_rows
    tp.call_gemini_for_analysis = lambda *a, **k: json.dumps(reconstructed_metadata(), ensure_ascii=False)
    def capture_review_rows(rows, **kwargs):
        (OUT / f"pre_review_{mode}.json").write_text(json.dumps([
            {"id": r.id, "label": r.source_description, "problem_text": r.problem_text,
             "notes": json.loads(r.notes or "{}")}
            for r in rows
        ], ensure_ascii=False, indent=2), encoding="utf8")
        return original_review(rows, **kwargs)
    review.review_and_heal_rows = capture_review_rows
    if mode == "without_regions":
        review.verified_visual_regions = lambda *a, **k: None
    manifest = json.loads(MANIFEST.read_text(encoding="utf8"))["sources"]
    import_policy = {
        "docx_primary": True, "pdf_optional_enrich": True,
        "docx_formula_source_mode": "converted_docx_latex",
        "formula_postprocess_mode": "convert_only", "auto_stage1_review": True,
        "retained_source_provenance": {str(DOCX): manifest["docx"], str(PDF): manifest["pdf"]},
        "source_original_filenames": {str(DOCX): "單元04-排列.docx", str(PDF): "單元04-排列.pdf"},
    }
    results = []
    try:
        with app.app_context():
            baseline = protected_state(sandbox)
            for attempt in range(2 if retry else 1):
                old = TextbookExample.query.filter_by(source_curriculum="general", source_volume=VOLUME,
                                                       source_chapter=CHAPTER).order_by(TextbookExample.id).all()
                policy = {"preview": {"volume": VOLUME, "chapter": CHAPTER, "question_count": 38,
                                      "docx_sha256": hashlib.sha256(DOCX.read_bytes()).hexdigest()},
                          "old_ids": [r.id for r in old], "old_rows_fingerprint": scope_fingerprint(old),
                          "backup_path": str(sandbox)}
                q = queue.Queue()
                cwd = Path.cwd()
                os.chdir(private)
                try:
                    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                        result = tp.process_textbook_file(
                            str(DOCX), {"curriculum": "general", "publisher": "longteng", "grade": 10,
                                        "volume": VOLUME}, q, skip_code_gen=True,
                            import_policy={**import_policy, "general_replacement": policy},
                            optional_enrich_pdf_path=str(PDF),
                        )
                finally:
                    os.chdir(cwd)
                db.session.expire_all()
                current = TextbookExample.query.filter_by(source_curriculum="general", source_volume=VOLUME,
                                                           source_chapter=CHAPTER).order_by(TextbookExample.id).all()
                rows = []
                for row in current:
                    notes = json.loads(row.notes or "{}")
                    rows.append({"id": row.id, "label": row.source_description.split(" [", 1)[0],
                                 "skill_id": row.skill_id, "problem_text": row.problem_text,
                                 "anchor": notes.get("question_anchor"), "notes": notes})
                results.append({"attempt": attempt + 1, "status": result.get("status"),
                                "stage1_gate": result.get("stage1_gate"),
                                "stage1_auto_review": result.get("stage1_auto_review"),
                                "row_count": len(rows), "rows": rows,
                                "logs": [str(x) for x in list(q.queue) if any(tag in str(x) for tag in
                                         ("[PDF VISUAL]", "[STAGE1 GATE]", "[AUTO REVIEW]"))]})
            protected_equal = protected_state(sandbox) == baseline
            db.session.remove()
    finally:
        tp.call_gemini_for_analysis = original_ai
        review.verified_visual_regions = original_regions
        review.review_and_heal_rows = original_review
        config.Config.SQLALCHEMY_DATABASE_URI = prior_uri
    return {"mode": mode, "source": {"docx_sha256": hashlib.sha256(DOCX.read_bytes()).hexdigest(),
                                      "pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest()},
            "gemini_response": "reconstructed_from_original_title_inventory_report",
            "publisher_assumption": "longteng", "grade_assumption": 10,
            "protected_state_unchanged": protected_equal, "attempts": results}


if __name__ == "__main__":
    import sys
    mode = sys.argv[1]
    data = run(mode, retry=mode == "with_regions")
    (OUT / f"formal_replay_{mode}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")
    for item in data["attempts"]:
        gate = item["stage1_gate"] or {}
        print(mode, item["attempt"], item["status"], gate.get("status"), gate.get("reasons"),
              "blocked", [x["label"] for x in gate.get("blocked") or []], "rows", item["row_count"])
    print("protected_state_unchanged", data["protected_state_unchanged"])
