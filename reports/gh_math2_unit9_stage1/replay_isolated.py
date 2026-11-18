"""Isolated replay of Unit 9 Stage 1: formal DB copied read-only into OUT, Gemini stubbed, formal DB SHA checked."""
import contextlib, hashlib, io, json, os, queue, re, shutil, sqlite3, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(tempfile.gettempdir()) / "u9_replay" / "fixed"
PRIVATE = OUT / "sandbox"
RECORD = ROOT / "textbook_import/uploaded_sources/general/數學2/9c9b32ac81f815083df42fbe492ec3188f22ab16ba0ef272099b7dee5e3f79ec.json"
FORMAL = ROOT / "instance/kumon_math.db"
CHAPTER = "單元9 二維數據分析"
sys.path.insert(0, str(ROOT))
TITLES = ["例題1", "隨堂練習1", "例題2", "隨堂練習2", "例題3", "隨堂練習3", "隨堂練習4", "例題4", "隨堂練習5",
          "例題5", "隨堂練習6", "例題6", "隨堂練習7", "例題7"] + \
         [f"9習題 觀念澄清{i}" for i in range(1, 6)] + [f"9習題 基礎題{i}" for i in range(1, 6)] + \
         ["9習題 進階題6", "9習題 進階題7"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def copy_formal(dst):
    with sqlite3.connect(f"file:{FORMAL.as_posix()}?mode=ro", uri=True) as s, sqlite3.connect(dst) as t:
        s.backup(t)


def metadata():
    concepts = [
        {"concept_name": "散布圖", "concept_en_id": "ScatterPlot", "concept_paragraph": "甲 散布圖", "examples": [], "practice_questions": []},
        {"concept_name": "相關係數", "concept_en_id": "CorrelationCoefficient", "concept_paragraph": "乙 相關係數", "examples": [], "practice_questions": []},
        {"concept_name": "最小平方法與迴歸直線", "concept_en_id": "LeastSquaresMethodAndRegressionLine", "concept_paragraph": "丙 最小平方法與迴歸直線", "examples": [], "practice_questions": []},
    ]
    for t in TITLES:
        n = int(re.search(r"(\d+)$", t).group(1))
        ex = t.startswith("例題")
        if ex:
            c = 0 if n == 1 else 1 if n <= 3 else 2
        elif t.startswith("隨堂練習"):
            c = 0 if n == 1 else 1 if n <= 4 else 2
        else:
            c = 2
        st = ("textbook_example" if ex else "in_class_practice" if t.startswith("隨堂練習")
              else "basic_exercise" if "基礎題" in t else "advanced_exercise" if "進階題" in t else "concept_check")
        concepts[c]["examples" if ex else "practice_questions"].append(
            {"title": t, "source_description": t, "source_type": st, "problem_text": t, "correct_answer": "", "detailed_solution": ""})
    return {"chapters": [{"chapter_title": CHAPTER, "sections": [{"section_title": "9.二維數據分析", "concepts": concepts}]}]}


def snap(rows):
    return [{"id": r.id, "label": r.source_description.split(" [", 1)[0], "skill_id": r.skill_id,
             "problem_text": r.problem_text, "detailed_solution": r.detailed_solution,
             "notes": json.loads(r.notes or "{}")} for r in rows]


def main():
    OUT.mkdir(parents=True, exist_ok=True); PRIVATE.mkdir(parents=True, exist_ok=True)
    temp = PRIVATE / "temp"; temp.mkdir(exist_ok=True)
    os.environ.update({"TMP": str(temp), "TEMP": str(temp), "TMPDIR": str(temp), "SEED_DB_ONLY": "1"})
    tempfile.tempdir = str(temp)
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    sources = {}
    for k in ("docx", "pdf"):
        src = ROOT / record["sources"][k]["stored_path"]
        assert sha(src) == record["sources"][k]["sha256"]
        dst = PRIVATE / f"09-.{k}"; shutil.copy2(src, dst); sources[k] = dst
    formal_before = sha(FORMAL)
    sandbox_db = PRIVATE / "unit9.db"
    copy_formal(sandbox_db)

    import config
    config.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + sandbox_db.as_posix()
    config.Config.UPLOAD_FOLDER = str(PRIVATE / "uploads")
    from app import create_app
    from models import TextbookExample, db
    from core.general_textbook_replacement import scope_fingerprint
    import core.textbook_processor as processor
    import core.textbook_stage1_auto_review as review

    app = create_app(production=False)
    app.root_path = str(PRIVATE)
    app.config["UPLOAD_FOLDER"] = str(PRIVATE / "uploads")
    cap = {"pre": [], "post": [], "visual": None, "scan": None, "skill_map": None}
    orig = (processor.call_gemini_for_analysis, processor.enrich_general_high_pdf_visuals,
            review.review_and_heal_rows, review._default_ai_review, processor.attach_general_high_source_evidence)
    processor.call_gemini_for_analysis = lambda *a, **kw: json.dumps(metadata(), ensure_ascii=False)
    review._default_ai_review = lambda items, skills: []

    def visual(*a, **kw):
        cap["visual"] = orig[1](*a, **kw); return cap["visual"]

    orig_map = processor.apply_general_high_source_skill_map
    def skill_map(*a, **kw):
        cap["skill_map"] = orig_map(*a, **kw); return cap["skill_map"]
    processor.apply_general_high_source_skill_map = skill_map

    def evidence(*a, **kw):
        cap["scan"] = {"items": kw["scan"].get("items"), "chapter": kw["scan"].get("chapter")}
        return orig[4](*a, **kw)

    def auto(rows, **kw):
        cap["pre"] = snap(rows); v = orig[2](rows, **kw); cap["post"] = snap(rows); return v

    processor.enrich_general_high_pdf_visuals = visual
    processor.attach_general_high_source_evidence = evidence
    review.review_and_heal_rows = auto
    q = queue.Queue(); out, err = io.StringIO(), io.StringIO(); result = None
    try:
        with app.app_context():
            assert Path(db.engine.url.database).resolve() == sandbox_db.resolve()
            old = TextbookExample.query.filter_by(source_curriculum="general", source_volume="數學2",
                                                  source_chapter=CHAPTER).order_by(TextbookExample.id).all()
            repl = {"preview": {"volume": "數學2", "chapter": CHAPTER, "question_count": 26, "docx_sha256": sha(sources["docx"])},
                    "old_ids": [r.id for r in old], "old_rows_fingerprint": scope_fingerprint(old), "backup_path": str(sandbox_db)}
            policy = {"docx_primary": True, "pdf_optional_enrich": True, "docx_formula_source_mode": "converted_docx_latex",
                      "formula_postprocess_mode": "convert_only", "auto_stage1_review": True, "general_replacement": repl,
                      "retained_source_provenance": {str(sources[k]): record["sources"][k] for k in sources},
                      "source_original_filenames": {str(sources[k]): record["sources"][k]["original_filename"] for k in sources}}
            (PRIVATE / "reports/import_debug").mkdir(parents=True, exist_ok=True)
            cwd = Path.cwd(); os.chdir(PRIVATE)
            try:
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    result = processor.process_textbook_file(
                        str(sources["docx"]), {"curriculum": "general", "publisher": "longteng", "grade": 11, "volume": "數學2"},
                        q, skip_code_gen=True, import_policy=policy, optional_enrich_pdf_path=str(sources["pdf"]))
            finally:
                os.chdir(cwd)
            db.session.remove()
    finally:
        (processor.call_gemini_for_analysis, processor.enrich_general_high_pdf_visuals,
         review.review_and_heal_rows, review._default_ai_review, processor.attach_general_high_source_evidence) = orig; processor.apply_general_high_source_skill_map = orig_map
    logs = [str(m) for m in list(q.queue)]
    (OUT / "log.txt").write_text("\n".join(logs) + "\nSTDOUT\n" + out.getvalue() + "\nSTDERR\n" + err.getvalue(), encoding="utf-8")
    (OUT / "raw.json").write_text(json.dumps({"result": result, "cap": cap}, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    g = (result or {}).get("stage1_gate") or {}
    print(json.dumps({"status": (result or {}).get("status"), "gate": g.get("status"), "reasons": g.get("reasons"),
                      "blocked": g.get("blocked"), "needs_review": g.get("needs_review"),
                      "issues": ((result or {}).get("stage1_auto_review") or {}).get("issues"),
                      "formal_db_unchanged": sha(FORMAL) == formal_before}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

