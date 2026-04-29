#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Read-only checker for imported textbook LaTeX.

Usage:
    python scripts/check_imported_latex.py
    python scripts/check_imported_latex.py --db instance/kumon_math.db
"""

from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TARGET_TERMS = ("1-5", "二項式定理")
LATEX_KEYWORDS = (r"\(", r"\)", r"\binom", r"\frac", r"\times", r"\sum")
SUSPICIOUS_LITERALS = (r"\\(", r"\\binom", r"\\frac")
CONTROL_CHARS = {
    "\x08": r"\b / BACKSPACE",
    "\x0c": r"\f / FORM FEED",
    "\t": r"\t / TAB",
}
TEXT_TYPE_TOKENS = ("CHAR", "CLOB", "TEXT", "VARCHAR", "STRING")
TARGET_CONTEXT_COLUMN_HINTS = (
    "chapter",
    "section",
    "title",
    "category",
    "paragraph",
    "skill_ch_name",
    "family_name",
)
DEFAULT_LIMIT = 200


@dataclass(frozen=True)
class ColumnInfo:
    name: str
    type_name: str
    is_pk: bool


@dataclass(frozen=True)
class Finding:
    table: str
    row_id: object
    column: str
    label: str
    preview: str


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_db_path() -> Path:
    try:
        sys.path.insert(0, str(project_root()))
        from config import Config  # pylint: disable=import-outside-toplevel

        return Path(Config.db_path)
    except Exception:
        return project_root() / "instance" / "kumon_math.db"


def open_readonly(db_path: Path) -> sqlite3.Connection:
    resolved = db_path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"SQLite database not found: {resolved}")
    conn = sqlite3.connect(f"file:{resolved.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def quote_ident(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def user_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()
    return [str(row["name"]) for row in rows]


def table_columns(conn: sqlite3.Connection, table: str) -> list[ColumnInfo]:
    rows = conn.execute(f"PRAGMA table_info({quote_ident(table)})").fetchall()
    return [
        ColumnInfo(str(row["name"]), str(row["type"] or ""), bool(row["pk"]))
        for row in rows
    ]


def text_columns(columns: Iterable[ColumnInfo]) -> list[str]:
    result = []
    for col in columns:
        type_name = col.type_name.upper()
        if not type_name or any(token in type_name for token in TEXT_TYPE_TOKENS):
            result.append(col.name)
    return result


def row_identifier(row: sqlite3.Row, columns: list[ColumnInfo]) -> object:
    for col in columns:
        if col.is_pk and col.name in row.keys():
            return row[col.name]
    if "rowid" in row.keys():
        return row["rowid"]
    if "id" in row.keys():
        return row["id"]
    if "skill_id" in row.keys():
        return row["skill_id"]
    return "?"


def contains_target(row: sqlite3.Row, cols: Iterable[str]) -> bool:
    for col in cols:
        val = row[col]
        if val is None:
            continue
        text = str(val)
        if any(term in text for term in TARGET_TERMS):
            return True
    return False


def target_context_columns(cols: Iterable[str]) -> list[str]:
    result = []
    for col in cols:
        lower = col.lower()
        if any(hint in lower for hint in TARGET_CONTEXT_COLUMN_HINTS):
            result.append(col)
    return result


def contains_latex_keyword(text: str) -> bool:
    return any(keyword in text for keyword in LATEX_KEYWORDS)


def preview_around(text: str, needle: str | None = None, width: int = 90) -> str:
    cleaned = text.replace("\n", "\\n").replace("\r", "\\r")
    if needle and needle in cleaned:
        idx = cleaned.find(needle)
    else:
        idx = 0
    start = max(0, idx - width // 2)
    end = min(len(cleaned), idx + len(needle or "") + width // 2)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(cleaned) else ""
    return prefix + cleaned[start:end] + suffix


def find_suspicious(text: str) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for literal in SUSPICIOUS_LITERALS:
        if literal in text:
            findings.append((f"literal {literal}", literal))

    for char, label in CONTROL_CHARS.items():
        if char in text:
            findings.append((f"control char {label}", char))

    return findings


def fetch_all_rows(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    return conn.execute(f"SELECT rowid AS rowid, * FROM {quote_ident(table)}").fetchall()


def collect_target_rows(conn: sqlite3.Connection) -> tuple[dict[str, list[sqlite3.Row]], set[str]]:
    targets: dict[str, list[sqlite3.Row]] = {}
    target_skill_ids: set[str] = set()

    for table in user_tables(conn):
        columns = table_columns(conn, table)
        cols = text_columns(columns)
        context_cols = target_context_columns(cols)
        if not context_cols:
            continue

        matched = []
        for row in fetch_all_rows(conn, table):
            if contains_target(row, context_cols):
                matched.append(row)
                if "skill_id" in row.keys() and row["skill_id"]:
                    target_skill_ids.add(str(row["skill_id"]))

        if matched:
            targets[table] = matched

    if target_skill_ids and "textbook_examples" in user_tables(conn):
        placeholders = ",".join("?" for _ in target_skill_ids)
        rows = conn.execute(
            f"""
            SELECT rowid AS rowid, *
            FROM textbook_examples
            WHERE skill_id IN ({placeholders})
            """,
            sorted(target_skill_ids),
        ).fetchall()
        existing_ids = {row["rowid"] for row in targets.get("textbook_examples", [])}
        extra = [row for row in rows if row["rowid"] not in existing_ids]
        if extra:
            targets.setdefault("textbook_examples", []).extend(extra)

    return targets, target_skill_ids


def scan_targets(
    conn: sqlite3.Connection,
    targets: dict[str, list[sqlite3.Row]],
    limit: int,
) -> tuple[list[Finding], list[Finding], int]:
    latex_hits: list[Finding] = []
    suspicious_hits: list[Finding] = []
    scanned_fields = 0

    for table, rows in sorted(targets.items()):
        columns = table_columns(conn, table)
        cols = text_columns(columns)
        for row in rows:
            rid = row_identifier(row, columns)
            for col in cols:
                val = row[col]
                if val is None:
                    continue
                text = str(val)
                scanned_fields += 1

                for label, needle in find_suspicious(text):
                    suspicious_hits.append(
                        Finding(table, rid, col, label, preview_around(text, needle))
                    )

                if contains_latex_keyword(text):
                    first_keyword = next(k for k in LATEX_KEYWORDS if k in text)
                    latex_hits.append(
                        Finding(table, rid, col, first_keyword, preview_around(text, first_keyword))
                    )

    return latex_hits[:limit], suspicious_hits[:limit], scanned_fields


def print_findings(title: str, findings: list[Finding]) -> None:
    if not findings:
        print(f"{title}: none")
        return

    print(f"{title}: {len(findings)}")
    for item in findings:
        print(
            f"- table={item.table} row_id={item.row_id} "
            f"column={item.column} match={item.label}"
        )
        print(f"  preview={item.preview}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check imported 1-5 binomial theorem LaTeX text in SQLite."
    )
    parser.add_argument(
        "--db",
        default=str(default_db_path()),
        help="SQLite database path. Defaults to config.Config.db_path.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Maximum normal/suspicious findings to print per category.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db_path = Path(args.db)

    print(f"[LATEX CHECK] DB: {db_path.resolve()}")
    print(f"[LATEX CHECK] Target terms: {', '.join(TARGET_TERMS)}")

    conn = open_readonly(db_path)
    try:
        targets, target_skill_ids = collect_target_rows(conn)
        target_count = sum(len(rows) for rows in targets.values())
        print(f"[LATEX CHECK] Target rows: {target_count}")
        if target_skill_ids:
            print(f"[LATEX CHECK] Target skill_id count: {len(target_skill_ids)}")

        if not targets:
            print("[LATEX CHECK] WARN: no rows matched section/chapter terms 1-5 or 二項式定理.")
            return 1

        latex_hits, suspicious_hits, scanned_fields = scan_targets(conn, targets, args.limit)
        print(f"[LATEX CHECK] Scanned text fields: {scanned_fields}")
        print_findings("[LATEX CHECK] LaTeX keyword hits", latex_hits)
        print_findings("[LATEX CHECK] Suspicious hits", suspicious_hits)

        if suspicious_hits:
            print("[LATEX CHECK] FAIL: suspicious imported LaTeX text found.")
            return 2

        print("[LATEX CHECK] OK: imported LaTeX appears valid for MathJax.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
