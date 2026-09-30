"""Audit and repair high-confidence LaTeX escape corruption in SQLite.

Usage:
  python scripts/recover_illegal_xml_chars.py --dry-run
  python scripts/recover_illegal_xml_chars.py --apply
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.backup.excel_sanitizer import (  # noqa: E402
    XML_ILLEGAL_CONTROL_CHARS,
    repair_known_latex_escape_corruption,
)


DEFAULT_DB = PROJECT_ROOT / "instance" / "kumon_math.db"


def _quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _text_columns(conn: sqlite3.Connection, table: str) -> tuple[list[str], list[str]]:
    info = conn.execute(f"PRAGMA table_info({_quote(table)})").fetchall()
    text_columns = [row[1] for row in info if any(kind in (row[2] or "").upper() for kind in ("CHAR", "TEXT", "CLOB", "JSON"))]
    primary_key = [row[1] for row in info if row[5]]
    return text_columns, primary_key


def scan_database(db_path: Path) -> list[dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    findings: list[dict[str, Any]] = []
    try:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
        for (table,) in tables:
            columns, primary_key = _text_columns(conn, table)
            if not columns:
                continue
            for row in conn.execute(f"SELECT rowid AS __rowid__, * FROM {_quote(table)}"):
                for column in columns:
                    value = row[column]
                    if not isinstance(value, str):
                        continue
                    for position, char in enumerate(value):
                        if ord(char) not in XML_ILLEGAL_CONTROL_CHARS:
                            continue
                        before, repairs = repair_known_latex_escape_corruption(value)
                        identity = {key: row[key] for key in primary_key} or {"rowid": row["__rowid__"]}
                        findings.append({
                            "table": table,
                            "primary_key": identity,
                            "column": column,
                            "char_code": f"U+{ord(char):04X}",
                            "context": repr(value[max(0, position - 35):position + 45]),
                            "before_repr": repr(value),
                            "after_repr": repr(before) if repairs else None,
                            "semantic_repairs": repairs,
                            "repairable": bool(repairs),
                        })
    finally:
        conn.close()
    return findings


def apply_repairs(db_path: Path, findings: list[dict[str, Any]]) -> Path | None:
    changes: dict[tuple[str, tuple[tuple[str, Any], ...], str], tuple[str, str]] = {}
    for finding in findings:
        if not finding["repairable"]:
            continue
        key = (finding["table"], tuple(finding["primary_key"].items()), finding["column"])
        changes[key] = (finding["before_repr"], finding["after_repr"])
    if not changes:
        return None

    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{db_path.stem}_before_illegal_xml_repair_{datetime.now():%Y%m%d_%H%M%S}{db_path.suffix}"
    source = sqlite3.connect(db_path)
    target = sqlite3.connect(backup_path)
    try:
        source.backup(target)
        if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("native SQLite backup integrity check failed")
    finally:
        target.close()
        source.close()

    conn = sqlite3.connect(db_path)
    try:
        with conn:
            for (table, primary_key_items, column), (_, after_repr) in changes.items():
                primary_key = dict(primary_key_items)
                where = " AND ".join(f"{_quote(key)} = ?" for key in primary_key)
                before_row = conn.execute(
                    f"SELECT {_quote(column)} FROM {_quote(table)} WHERE {where}", tuple(primary_key.values())
                ).fetchone()
                if before_row is None:
                    raise RuntimeError(f"row disappeared during repair: {table} {primary_key}")
                before, repairs = repair_known_latex_escape_corruption(before_row[0])
                if not repairs:
                    continue
                conn.execute(
                    f"UPDATE {_quote(table)} SET {_quote(column)} = ? WHERE {where}",
                    (before, *primary_key.values()),
                )
    finally:
        conn.close()
    return backup_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.apply and args.dry_run:
        parser.error("choose either --dry-run or --apply")
    findings = scan_database(args.db)
    backup_path = apply_repairs(args.db, findings) if args.apply else None
    report = {
        "mode": "apply" if args.apply else "dry-run",
        "database": str(args.db),
        "finding_count": len(findings),
        "repairable_finding_count": sum(1 for item in findings if item["repairable"]),
        "native_backup": str(backup_path) if backup_path else None,
        "findings": findings,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
