"""Apply (or roll back) the reviewed 數學2 單元2 Stage 1 change set.  NOT RUN against production in this phase.

    # rehearsal on a copy (default behaviour: nothing is written without --apply)
    python apply_unit2.py --db <copy.db> --uploads-root <dir> --backup-dir <dir> [--apply]
    python apply_unit2.py --db <copy.db> --uploads-root <dir> --rollback <manifest.json>

Production needs BOTH ``--production`` and ``--user-authorized "<who/when>"``; without them the script refuses to
open instance/kumon_math.db for writing.  Safety order: preflight (every op's current values must still match the
fingerprint taken when the change set was built, source PNG hashes must match, no destination file may differ) ->
backup (sqlite backup API + integrity_check) -> one transaction -> post-verify -> manifest with the exact before-values.
Rollback is row-level and file-level (only files this run created, hash-checked), so unrelated later changes survive;
the backup file is the last resort.
"""
import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD_DB = (ROOT / "instance" / "kumon_math.db").resolve()
CHANGE_SET = HERE / "production_change_set.json"
SOURCE_ROOT = HERE / "sandbox" / "crops"
COLS = ("problem_text", "detailed_solution", "source_description", "notes", "skill_id")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fp(row, cols) -> str:
    return sha(json.dumps({c: row[c] for c in cols}, ensure_ascii=False, sort_keys=True).encode("utf-8"))


def preflight(con, cs, uploads_root: Path) -> list[str]:
    problems = []
    for op in cs["db_ops"]:
        row = con.execute("select * from textbook_examples where id=?", (op["id"],)).fetchone()
        if row is None:
            problems.append(f"id {op['id']}: row missing")
            continue
        cols = op.get("columns") or list(COLS)
        if fp(row, cols) != op["expected_before_sha256"]:
            problems.append(f"id {op['id']}: current values differ from the reviewed baseline (drift)")
    for f in cs["asset_files"]:
        src = SOURCE_ROOT / f["copy_to"]
        if not src.is_file() or sha(src.read_bytes()) != f["sha256"]:
            problems.append(f"source asset missing or altered: {f['copy_to'][-60:]}")
        dst = uploads_root / f["copy_to"]
        if dst.exists() and sha(dst.read_bytes()) != f["sha256"]:
            problems.append(f"destination exists with different content: {f['copy_to'][-60:]}")
    return problems


def apply(con, db_path: Path, cs, uploads_root: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"kumon_math_before_math2_unit2_stage1_{stamp}.db"
    dst = sqlite3.connect(backup)
    con.backup(dst)
    ok = dst.execute("pragma integrity_check").fetchone()[0]
    n = dst.execute("select count(*) from textbook_examples").fetchone()[0]
    dst.close()
    assert ok == "ok", ok
    manifest = {"db": str(db_path), "backup": str(backup), "backup_sha256": sha(backup.read_bytes()), "backup_textbook_examples": n,
                "created_files": [], "before_rows": {}, "ops": [{"op": o["op"], "id": o["id"]} for o in cs["db_ops"]]}
    for f in cs["asset_files"]:
        dst_file = uploads_root / f["copy_to"]
        if dst_file.exists():
            continue  # identical content (checked in preflight): nothing to undo
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE_ROOT / f["copy_to"], dst_file)
        assert sha(dst_file.read_bytes()) == f["sha256"]
        manifest["created_files"].append({"path": f["copy_to"], "sha256": f["sha256"]})
    con.execute("begin immediate")
    try:
        for op in cs["db_ops"]:
            row = con.execute("select * from textbook_examples where id=?", (op["id"],)).fetchone()
            manifest["before_rows"][str(op["id"])] = dict(row)
            if op["op"] == "delete":
                con.execute("delete from textbook_examples where id=?", (op["id"],))
            else:
                sets = ", ".join(f"{c}=?" for c in op["columns"])
                con.execute(f"update textbook_examples set {sets} where id=?", (*[op["new"][c] for c in op["columns"]], op["id"]))
        for op in cs["db_ops"]:  # post-verify inside the transaction; any mismatch rolls everything back
            row = con.execute("select * from textbook_examples where id=?", (op["id"],)).fetchone()
            if op["op"] == "delete":
                assert row is None
            else:
                assert all(row[c] == op["new"][c] for c in op["columns"]), op["id"]
        left = con.execute("select count(*) from textbook_examples where source_curriculum='general' and source_volume='數學2' and source_chapter='單元2 級數'").fetchone()[0]
        assert left == cs["expected_unit_rows_after"], left
        total = con.execute("select count(*) from textbook_examples").fetchone()[0]
        assert total == n - 28, (total, n)
        con.execute("commit")
    except Exception:
        con.execute("rollback")
        for c in manifest["created_files"]:
            (uploads_root / c["path"]).unlink(missing_ok=True)
        raise
    out = backup_dir / f"apply_manifest_{stamp}.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out


def rollback(con, manifest_path: Path, uploads_root: Path) -> None:
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    con.execute("begin immediate")
    try:
        for rid, row in m["before_rows"].items():
            cols = list(row)
            exists = con.execute("select 1 from textbook_examples where id=?", (int(rid),)).fetchone()
            if exists:
                con.execute("update textbook_examples set " + ", ".join(f"{c}=?" for c in cols if c != "id") + " where id=?",
                            (*[row[c] for c in cols if c != "id"], int(rid)))
            else:
                con.execute(f"insert into textbook_examples ({','.join(cols)}) values ({','.join('?' * len(cols))})", [row[c] for c in cols])
        con.execute("commit")
    except Exception:
        con.execute("rollback")
        raise
    for c in m["created_files"]:
        f = uploads_root / c["path"]
        if f.is_file() and sha(f.read_bytes()) == c["sha256"]:
            f.unlink()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--uploads-root", required=True, help="directory that contains uploads/")
    ap.add_argument("--backup-dir")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--rollback")
    ap.add_argument("--production", action="store_true")
    ap.add_argument("--user-authorized", default="")
    a = ap.parse_args()
    db = Path(a.db).resolve()
    is_prod = db == PROD_DB or Path(a.uploads_root).resolve() == ROOT
    if is_prod and not (a.production and a.user_authorized.strip()):
        sys.exit("REFUSED: production DB/uploads need --production and --user-authorized (explicit user authorisation).")
    if not is_prod and a.production:
        sys.exit("REFUSED: --production given for a non-production target.")
    cs = json.loads(CHANGE_SET.read_text(encoding="utf-8"))
    uploads_root = Path(a.uploads_root)
    if not (a.apply or a.rollback):
        con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        problems = preflight(con, cs, uploads_root)
        print("PREFLIGHT", "OK" if not problems else problems, f"| ops={len(cs['db_ops'])} assets={len(cs['asset_files'])} (dry run, nothing written)")
        sys.exit(1 if problems else 0)
    con = sqlite3.connect(db, isolation_level=None)
    con.row_factory = sqlite3.Row
    if a.rollback:
        rollback(con, Path(a.rollback), uploads_root)
        print("rolled back from", a.rollback)
        return
    problems = preflight(con, cs, uploads_root)
    if problems:
        sys.exit("PREFLIGHT FAILED, nothing written: " + "; ".join(problems))
    print("applied; manifest:", apply(con, db, cs, uploads_root, Path(a.backup_dir or HERE / "backups")))


if __name__ == "__main__":
    main()
