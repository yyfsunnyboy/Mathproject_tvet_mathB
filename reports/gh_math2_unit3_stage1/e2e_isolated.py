"""Isolated end-to-end run of the real general-high importer on Unit 3 (DB copy + private asset root).

No mocks for DOCX/PDF parsing, MathType conversion, save_to_database, skill map, PDF visuals, review,
Gate or commit/rollback. Gemini is the project's own wrapper; --no-ai makes the AI step NOT TESTED.

usage: python -m reports.gh_math2_unit3_stage1.e2e_isolated <scenario> [--keep]
scenarios: replace | rerun | unauthorized | update_mode
"""
import hashlib, json, os, queue as queue_mod, shutil, sqlite3, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

SRC = ROOT / "textbook_import/uploaded_sources/general/數學2"
DOCX, PDF = SRC / "cd38c1890caf_單元03-計數原理.docx", SRC / "fe5ce0b620d3_單元03-計數原理.pdf"
FORMAL = ROOT / "instance/kumon_math.db"
CHAPTER, VOLUME = "單元3 計數原理", "數學2"
CASE = HERE / "production_change_set.json"
BOX = HERE / "e2e"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree_digest(*dirs):
    """path -> content hash for every guarded formal file (sqlite -shm/-wal sidecars excluded: reading changes them)."""
    out = {}
    for d in dirs:
        for p in sorted(Path(d).rglob("*")) if Path(d).exists() else []:
            if p.is_file() and not p.name.endswith(("-shm", "-wal")):
                out[str(p)] = (p.stat().st_size, sha(p))
    return out


def build_db(path, mode):
    """Pre-repair Unit 3. mode old20: only the old printing; both50: old 20 + newly imported 30."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    with sqlite3.connect(f"file:{FORMAL.as_posix()}?mode=ro", uri=True) as src, sqlite3.connect(path) as dst:
        src.backup(dst)
    changes = json.loads(CASE.read_text(encoding="utf-8"))
    con = sqlite3.connect(path)
    for op in changes["updates"]:
        b = op["before"]
        con.execute("update textbook_examples set problem_text=?,detailed_solution=?,skill_id=?,notes=? where id=?",
                    (b["problem_text"], b["detailed_solution"], b["skill_id"], b["notes"], op["id"]))
    for row in changes["old_rows"]:
        cols = list(row)
        con.execute(f"insert into textbook_examples ({','.join(cols)}) values ({','.join('?' for _ in cols)})",
                    [row[k] for k in cols])
    if mode == "old20":
        con.execute("delete from textbook_examples where source_chapter=? and source_volume=? and id>=12744",
                    (CHAPTER, VOLUME))
    con.commit()
    con.close()


def chapter_state(path):
    con = sqlite3.connect(f"file:{Path(path).as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "select * from textbook_examples where source_curriculum='general' and source_volume=? and source_chapter=? "
        "order by id", (VOLUME, CHAPTER))]
    other = hashlib.sha256(repr([tuple(r) for r in con.execute(
        "select * from textbook_examples where not (source_curriculum='general' and source_volume=? and "
        "source_chapter=?) order by id", (VOLUME, CHAPTER))]).encode()).hexdigest()
    bindings = con.execute("select skill_id from skill_curriculum where curriculum='general' and volume=? and chapter=? "
                           "order by skill_id", (VOLUME, CHAPTER)).fetchall()
    con.close()
    notes = [json.loads(r["notes"] or "{}") for r in rows]
    anchors = [(n.get("question_anchor") or {}).get("anchor_id") for n in notes]
    new = [r for r in rows if r["id"] >= 12744]
    return {
        "rows": len(rows), "old_rows(<12744)": sum(r["id"] < 12744 for r in rows),
        "labels_unique": len({r["source_description"].split(" [", 1)[0] for r in new}) == len(new),
        "anchors_non_null": sum(a is not None for a in anchors), "anchors_unique": len({a for a in anchors if a}),
        "skills": {s: sum(r["skill_id"] == s for r in rows if r["id"] >= 12744) for s in sorted({r["skill_id"] for r in new})},
        "binding_rows": len(bindings), "math_parse_failed": sum("MATH_PARSE_FAILED" in (r["problem_text"] or "") + (r["detailed_solution"] or "") for r in rows),
        "asset_rows": [r["id"] for r, n in zip(rows, notes) if n.get("image_assets")],
        "visual_missing_flags": sum(n.get("pdf_visual_status") == "VISUAL_REQUIRED_MISSING" for n in notes),
        "ids": [rows[0]["id"], rows[-1]["id"]] if rows else None,
        "chapter_content_digest": hashlib.sha256(repr([sorted(r.items()) for r in rows]).encode()).hexdigest()[:16],
        "id_skill_map_digest": hashlib.sha256(repr([(r["id"], r["skill_id"]) for r in rows]).encode()).hexdigest()[:16], "other_tables_textbook_digest": other,
    }


def main():
    scenario = sys.argv[1]
    box = BOX / scenario
    db_path = box / "work.db"
    state_file = box / "state.json"
    shutil.rmtree(box, ignore_errors=True)
    if scenario == "rerun":  # continue from the DB + asset root left by a successful 'replace' run
        shutil.copytree(BOX / "replace", box, ignore=shutil.ignore_patterns("result.json", "logs.txt"))
    else:
        build_db(db_path, "both50" if scenario == "update_mode" else "old20")
    root = box / "project_root"
    root.mkdir(parents=True, exist_ok=True)
    guarded = (ROOT / "uploads", ROOT / "textbook_import", ROOT / "instance")
    guard_before, formal_before = tree_digest(*guarded), sha(FORMAL)
    before = chapter_state(db_path)

    import config as _cfg
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + db_path.as_posix()
    from app import create_app
    from models import TextbookExample, db
    app = create_app()
    app.root_path = str(root)
    os.chdir(box)  # private reports/import_debug output
    import core.textbook_processor as tp

    with app.app_context():
        assert Path(db.engine.url.database).resolve() == db_path.resolve(), "must use the isolated DB"
        policy = {"docx_primary": True, "pdf_optional_enrich": True, "docx_formula_source_mode": "converted_docx_latex",
                  "formula_postprocess_mode": "convert_only", "general_replacement": None, "auto_stage1_review": True}
        if scenario == "replace":
            from core.general_textbook_replacement import scope_fingerprint
            old = TextbookExample.query.filter_by(source_curriculum="general", source_volume=VOLUME,
                                                  source_chapter=CHAPTER).order_by(TextbookExample.id).all()
            backup = box / "pre_replace.db"
            with sqlite3.connect(db_path) as s, sqlite3.connect(backup) as d:
                s.backup(d)
            policy["general_replacement"] = {
                "preview": {"volume": VOLUME, "chapter": CHAPTER, "question_count": 30, "docx_sha256": sha(DOCX)},
                "old_ids": [r.id for r in old], "old_rows_fingerprint": scope_fingerprint(old),
                "backup_path": str(backup)}
        q = queue_mod.Queue()
        result = tp.process_textbook_file(
            str(DOCX), {"curriculum": "general", "publisher": "longteng", "grade": "高中", "volume": VOLUME}, q,
            skip_code_gen=True, import_policy=policy, optional_enrich_pdf_path=str(PDF))
        logs = [str(m) for m in list(q.queue)]
        db.session.remove()

    after = chapter_state(db_path)
    out = {
        "scenario": scenario, "result_status": result.get("status"),
        "result_message": str(result.get("message"))[:200],
        "gate_line": next((m for m in reversed(logs) if "[STAGE1 GATE]" in m), None),
        "review_issues": (result.get("stage1_auto_review") or {}).get("issues"),
        "gemini_requests": [m for m in logs if "Gemini" in m or "AI" in m][:6],
        "before": before, "after": after,
        "published_assets": sorted(str(p.relative_to(root)) for p in (root / "uploads").rglob("*") if p.is_file())
        if (root / "uploads").exists() else [],
        "formal_db_unchanged": sha(FORMAL) == formal_before,
        "formal_uploads_textbook_import_instance_untouched": tree_digest(*guarded) == guard_before,
        "formal_files_changed": sorted(k for k, v in tree_digest(*guarded).items() if guard_before.get(k) != v),
        "sources_present": DOCX.is_file() and PDF.is_file(),
    }
    (box / "result.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (box / "logs.txt").write_text("\n".join(logs), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
