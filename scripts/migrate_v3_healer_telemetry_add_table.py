# -*- coding: utf-8 -*-
"""Add gencode_v3_healer_telemetry_events to an existing SQLite DB (add-only, idempotent).

The migration only runs CREATE TABLE / INDEX / TRIGGER ... IF NOT EXISTS for the
telemetry table. It never drops, alters, deletes or rewrites existing tables or rows
(legacy healer_events is kept as-is).

Subcommands (read-only / dry-run by default):
  audit    Read-only inventory (tables, schema objects, row counts, content SHA-256, sqlite_sequence).
  backup   SQLite Backup API snapshot (source opened mode=ro) + before audit + SHA-256 manifest.
  migrate  Apply the add-only DDL; requires --apply. The formal DB is refused unless
           --approved-formal-apply is given (human approval required).
  compare  Before/after: only the telemetry table and its own objects may be added.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.gencode.schema.gencode_v3_healer_telemetry_inspection import (  # noqa: E402
    TABLE_NAME as TELEMETRY_TABLE,
    inspect_gencode_v3_healer_telemetry_schema,
    load_healer_telemetry_ddl,
)

MIGRATION_ID = "20261101_v3_healer_telemetry_add_table"
FORMAL_DB = (ROOT / "instance" / "kumon_math.db").resolve()
DEFAULT_ARCHIVE_ROOT = Path.home() / "MathProject_DB_Archives"
EXPECTED_TELEMETRY_INDEXES = (
    "idx_gencode_v3_healer_tel_type_created",
    "idx_gencode_v3_healer_tel_attempt",
)
EXPECTED_TELEMETRY_TRIGGER = "trg_gencode_v3_healer_tel_no_update"
_ALLOWED_STATEMENT = re.compile(
    r"^CREATE\s+(TABLE|INDEX|TRIGGER)\s+IF\s+NOT\s+EXISTS\s+\w+\s*"
    rf"(\(|ON\s+{TELEMETRY_TABLE}\s*\(|BEFORE\s+UPDATE\s+ON\s+{TELEMETRY_TABLE}\b)",
    re.IGNORECASE,
)
_FORBIDDEN_TOKENS = re.compile(r"\b(DROP|ALTER|DELETE|UPDATE\s+\w+\s+SET|INSERT|REPLACE|VACUUM)\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _is_formal_db(path: Path) -> bool:
    return path.resolve() == FORMAL_DB


def _connect_ro(path: Path) -> sqlite3.Connection:
    if not path.exists():
        raise FileNotFoundError(path)
    return sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"__bytes_b64__": base64.b64encode(value).decode("ascii")}
    return value


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _ordered_rows(conn: sqlite3.Connection, table: str) -> tuple[list[str], list[tuple]]:
    columns = [str(r[1]) for r in conn.execute(f"PRAGMA table_info({_quote(table)})").fetchall()]
    try:
        rows = conn.execute(f"SELECT * FROM {_quote(table)} ORDER BY rowid").fetchall()
    except sqlite3.OperationalError:
        order = ", ".join(str(i + 1) for i in range(len(columns))) or "1"
        rows = conn.execute(f"SELECT * FROM {_quote(table)} ORDER BY {order}").fetchall()
    return columns, rows


def _content_sha256(columns: list[str], rows: list[tuple]) -> str:
    digest = hashlib.sha256()
    digest.update(json.dumps(columns, ensure_ascii=False).encode("utf-8"))
    for row in rows:
        digest.update(b"\n")
        digest.update(json.dumps([_json_value(v) for v in row], ensure_ascii=False).encode("utf-8"))
    return digest.hexdigest()


def _table_names(conn: sqlite3.Connection) -> list[str]:
    return [
        str(r[0])
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    ]


def _split_statements(script: str) -> list[str]:
    statements: list[str] = []
    buffer = ""
    for line in script.splitlines(keepends=True):
        if not buffer and line.lstrip().startswith("--"):
            continue
        buffer += line
        if sqlite3.complete_statement(buffer):
            stmt = buffer.strip()
            if stmt:
                statements.append(stmt)
            buffer = ""
    if buffer.strip():
        statements.append(buffer.strip())
    return statements


def migration_statements() -> list[str]:
    """Add-only statements; raises if the canonical DDL contains anything else."""
    statements = _split_statements(load_healer_telemetry_ddl())
    for stmt in statements:
        head = stmt.split("BEGIN", 1)[0]
        if not _ALLOWED_STATEMENT.match(stmt) or _FORBIDDEN_TOKENS.search(head):
            raise RuntimeError(f"non add-only statement in telemetry DDL: {stmt[:120]!r}")
    return statements


def migration_sql() -> str:
    return (
        f"-- {MIGRATION_ID}\n"
        f"-- Add-only: creates {TELEMETRY_TABLE} with its indexes and append-only trigger.\n"
        "-- Idempotent (IF NOT EXISTS). No DROP / ALTER / DELETE / UPDATE / INSERT on existing tables.\n\n"
        + "\n\n".join(migration_statements())
        + "\n"
    )


# ---------------------------------------------------------------------------
# audit
# ---------------------------------------------------------------------------

def audit_connection(conn: sqlite3.Connection) -> dict[str, Any]:
    tables: dict[str, Any] = {}
    for table in _table_names(conn):
        columns, rows = _ordered_rows(conn, table)
        tables[table] = {
            "row_count": len(rows),
            "columns": columns,
            "content_sha256": _content_sha256(columns, rows),
        }
    objects = [
        {"type": r[0], "name": r[1], "tbl_name": r[2], "sql": r[3]}
        for r in conn.execute("SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY type, name").fetchall()
    ]
    sequence = (
        [list(r) for r in conn.execute("SELECT name, seq FROM sqlite_sequence ORDER BY name").fetchall()]
        if "sqlite_sequence" in tables
        else []
    )
    return {
        "table_count": len(tables),
        "tables": tables,
        "schema_objects": objects,
        "sqlite_sequence": sequence,
        "telemetry_table_present": TELEMETRY_TABLE in tables,
        "journal_mode": conn.execute("PRAGMA journal_mode").fetchone()[0],
    }


def audit_db(path: Path) -> dict[str, Any]:
    conn = _connect_ro(path)
    try:
        report = audit_connection(conn)
        report["integrity_check"] = conn.execute("PRAGMA integrity_check").fetchone()[0]
        report["foreign_key_check_violations"] = len(conn.execute("PRAGMA foreign_key_check").fetchall())
    finally:
        conn.close()
    report["db_path"] = str(path.resolve())
    return report


# ---------------------------------------------------------------------------
# backup
# ---------------------------------------------------------------------------

def backup_db(source: Path, archive_root: Path) -> dict[str, Any]:
    archive_root = archive_root.resolve()
    if ROOT in (archive_root, *archive_root.parents):
        raise SystemExit(f"archive dir must be outside the project: {archive_root}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = archive_root / f"healer_telemetry_add_table_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=False)

    backup_path = out_dir / f"{source.stem}.backup_{stamp}.db"
    src = _connect_ro(source)
    dst = sqlite3.connect(str(backup_path))
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()

    backup_audit = audit_db(backup_path)
    source_audit = audit_db(source)
    snapshot_matches = set(source_audit["tables"]) == set(backup_audit["tables"]) and all(
        source_audit["tables"][n]["content_sha256"] == info["content_sha256"]
        for n, info in backup_audit["tables"].items()
    )

    audit_path = out_dir / "before_audit.json"
    audit_path.write_text(json.dumps(backup_audit, ensure_ascii=False, indent=2), encoding="utf-8")
    sql_path = out_dir / f"{MIGRATION_ID}.sql"
    sql_path.write_text(migration_sql(), encoding="utf-8")
    files = [backup_path, audit_path, sql_path]
    manifest = {
        "migration_id": MIGRATION_ID,
        "created_at_utc": stamp,
        "source_db": str(source.resolve()),
        "backup_method": "sqlite3.Connection.backup (source opened mode=ro)",
        "backup_integrity_check": backup_audit["integrity_check"],
        "snapshot_matches_source_content": snapshot_matches,
        "table_count": backup_audit["table_count"],
        "files": {p.name: {"path": str(p), "bytes": p.stat().st_size, "sha256": _sha256_file(p)} for p in files},
    }
    manifest_path = out_dir / "backup_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    manifest["manifest_sha256"] = _sha256_file(manifest_path)
    return manifest


# ---------------------------------------------------------------------------
# migrate
# ---------------------------------------------------------------------------

def verify_telemetry_schema(conn: sqlite3.Connection) -> dict[str, Any]:
    info = inspect_gencode_v3_healer_telemetry_schema(conn)
    index_rows = conn.execute(f"PRAGMA index_list({_quote(TELEMETRY_TABLE)})").fetchall()
    indexes = {str(r[1]): {"unique": bool(r[2]), "origin": r[3]} for r in index_rows}
    unique_event_key = any(
        meta["unique"]
        and [str(r[2]) for r in conn.execute(f"PRAGMA index_info({_quote(name)})").fetchall()] == ["event_key"]
        for name, meta in indexes.items()
    )
    table_sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (TELEMETRY_TABLE,)
    ).fetchone()[0]
    check_columns = [
        c for c in ("event_type", "mode", "environment", "data_origin")
        if re.search(rf"CHECK\s*\(\s*{c}\s+IN", table_sql)
    ]
    triggers = [
        str(r[0])
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name=?", (TELEMETRY_TABLE,)
        ).fetchall()
    ]
    missing_indexes = [n for n in EXPECTED_TELEMETRY_INDEXES if n not in indexes]
    ok = (
        info["ok"] and unique_event_key and not missing_indexes
        and len(check_columns) == 4 and EXPECTED_TELEMETRY_TRIGGER in triggers
    )
    return {
        "missing_required_columns": info["missing_required_columns"],
        "indexes": indexes,
        "missing_indexes": missing_indexes,
        "unique_event_key": unique_event_key,
        "check_constraints": check_columns,
        "triggers": triggers,
        "ok": ok,
    }


def migrate_db(
    target: Path,
    *,
    apply: bool,
    approved_formal_apply: bool = False,
    evidence_dir: Path | None = None,
) -> dict[str, Any]:
    if _is_formal_db(target) and not approved_formal_apply:
        raise SystemExit(
            "refusing to migrate the formal DB without --approved-formal-apply (human approval required)"
        )
    statements = migration_statements()
    if not apply:
        conn = _connect_ro(target)
        try:
            present = TELEMETRY_TABLE in _table_names(conn)
        finally:
            conn.close()
        return {"target": str(target.resolve()), "mode": "dry-run", "telemetry_table_present": present, "statements": statements}

    conn = sqlite3.connect(str(target), isolation_level=None)
    try:
        conn.execute("PRAGMA busy_timeout = 30000")
        # Before/after audits share the write lock, so concurrent app writes cannot
        # interleave; anything beyond the telemetry objects rolls the DDL back.
        conn.execute("BEGIN IMMEDIATE")
        try:
            before = audit_connection(conn)
            existed = before["telemetry_table_present"]
            for stmt in statements:
                conn.execute(stmt)
            after = audit_connection(conn)
            comparison = compare_audits(before, after)
            if evidence_dir is not None:
                evidence_dir.mkdir(parents=True, exist_ok=True)
                for name, payload in (("migration_before.json", before), ("migration_after.json", after),
                                      ("migration_compare.json", comparison)):
                    (evidence_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
            if not comparison["only_expected_changes"]:
                conn.execute("ROLLBACK")
                return {
                    "target": str(target.resolve()),
                    "mode": "apply",
                    "applied": False,
                    "reason": "unexpected_difference_rolled_back",
                    "comparison": {k: v for k, v in comparison.items() if k != "retained"},
                }
            conn.execute("COMMIT")
        except Exception:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        fk_violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        telemetry = verify_telemetry_schema(conn)
    finally:
        conn.close()
    return {
        "target": str(target.resolve()),
        "mode": "apply",
        "applied": True,
        "telemetry_table_existed_before": existed,
        "comparison": {k: v for k, v in comparison.items() if k != "retained"},
        "retained_identical": sum(r["identical"] for r in comparison["retained"]),
        "retained_total": len(comparison["retained"]),
        "integrity_check": integrity,
        "foreign_key_check_violations": len(fk_violations),
        "telemetry_schema": telemetry,
    }


# ---------------------------------------------------------------------------
# compare
# ---------------------------------------------------------------------------

def compare_audits(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    b_tables, a_tables = before["tables"], after["tables"]
    b_objs = {(o["type"], o["name"]): o for o in before["schema_objects"]}
    a_objs = {(o["type"], o["name"]): o for o in after["schema_objects"]}
    added = sorted(set(a_tables) - set(b_tables))
    removed = sorted(set(b_tables) - set(a_tables))
    retained = []
    changed = []
    for name in sorted(set(b_tables) & set(a_tables)):
        b, a = b_tables[name], a_tables[name]
        same = (
            b["row_count"] == a["row_count"]
            and b["content_sha256"] == a["content_sha256"]
            and b_objs.get(("table", name), {}).get("sql") == a_objs.get(("table", name), {}).get("sql")
        )
        retained.append({"table": name, "row_count": a["row_count"], "content_sha256": a["content_sha256"], "identical": same})
        if not same:
            changed.append(name)
    objs_added = sorted(set(a_objs) - set(b_objs))
    objs_removed = sorted(set(b_objs) - set(a_objs))
    objs_changed = sorted(k for k in set(a_objs) & set(b_objs) if a_objs[k]["sql"] != b_objs[k]["sql"])
    sequence_same = before.get("sqlite_sequence") == after.get("sqlite_sequence")
    only_expected = (
        added in ([TELEMETRY_TABLE], [])
        and not removed
        and not changed
        and not objs_removed
        and not objs_changed
        and all(a_objs[k]["tbl_name"] == TELEMETRY_TABLE for k in objs_added)
        and sequence_same
    )
    return {
        "tables_before": len(b_tables),
        "tables_after": len(a_tables),
        "added_tables": added,
        "removed_tables": removed,
        "changed_retained_tables": changed,
        "schema_objects_added": [f"{t}:{n}" for t, n in objs_added],
        "schema_objects_removed": [f"{t}:{n}" for t, n in objs_removed],
        "schema_objects_changed": [f"{t}:{n}" for t, n in objs_changed],
        "sqlite_sequence_identical": sequence_same,
        "retained": retained,
        "only_expected_changes": only_expected,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_audit = sub.add_parser("audit")
    p_audit.add_argument("--db", type=Path, default=FORMAL_DB)
    p_audit.add_argument("--out", type=Path)

    p_backup = sub.add_parser("backup")
    p_backup.add_argument("--db", type=Path, default=FORMAL_DB)
    p_backup.add_argument("--archive-root", type=Path, default=DEFAULT_ARCHIVE_ROOT)

    p_migrate = sub.add_parser("migrate")
    p_migrate.add_argument("--db", type=Path, required=True)
    p_migrate.add_argument("--apply", action="store_true")
    p_migrate.add_argument("--approved-formal-apply", action="store_true")
    p_migrate.add_argument("--evidence-dir", type=Path)

    p_compare = sub.add_parser("compare")
    p_compare.add_argument("--before", type=Path, required=True)
    p_compare.add_argument("--after", type=Path, required=True)
    p_compare.add_argument("--out", type=Path)

    sub.add_parser("print-sql")

    args = parser.parse_args(argv)
    if args.cmd == "audit":
        result: Any = audit_db(args.db)
        if args.out:
            args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            result = {"out": str(args.out), "table_count": result["table_count"]}
    elif args.cmd == "backup":
        result = backup_db(args.db, args.archive_root)
    elif args.cmd == "migrate":
        result = migrate_db(
            args.db,
            apply=args.apply,
            approved_formal_apply=args.approved_formal_apply,
            evidence_dir=args.evidence_dir,
        )
    elif args.cmd == "compare":
        def _load(p: Path) -> dict[str, Any]:
            return json.loads(p.read_text(encoding="utf-8")) if p.suffix == ".json" else audit_db(p)
        result = compare_audits(_load(args.before), _load(args.after))
        if args.out:
            args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(migration_sql())
        return 0
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
