#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Restore high-quality textbook_examples text from an xlsx backup for one section."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

import pandas as pd


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_db_path() -> Path:
    sys.path.insert(0, str(project_root()))
    from config import Config  # pylint: disable=import-outside-toplevel

    return Path(Config.db_path)


def normalize_cell(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    return str(value).strip()


def extract_dedupe(source_description: str) -> str:
    m = re.search(r"dedupe=([0-9a-fA-F]+)", str(source_description or ""))
    return str(m.group(1)).lower() if m else ""


def normalize_title(source_description: str) -> str:
    text = str(source_description or "").split(" [", 1)[0].strip()
    text = re.sub(r"\s+", "", text)
    text = text.replace("例題", "例")
    text = re.sub(r"^例(\d+)$", lambda m: f"例{int(m.group(1))}", text)
    text = re.sub(r"^隨堂練習(\d+)$", lambda m: f"隨堂練習{int(m.group(1))}", text)
    text = re.sub(r"^1-1習題基礎題(\d+)$", lambda m: f"1-1習題基礎題{int(m.group(1))}", text)
    text = re.sub(r"^(\d{2,3})統測([A-Za-z])$", lambda m: f"{m.group(1)}統測{m.group(2).upper()}", text)
    return text


def is_better_optional_text(backup_value: str, current_value: str) -> bool:
    sys.path.insert(0, str(project_root()))
    from core.textbook_processor import _is_low_value_import_field

    backup = normalize_cell(backup_value)
    current = normalize_cell(current_value)
    if _is_low_value_import_field(backup):
        return False
    if _is_low_value_import_field(current):
        return True
    return len(backup) > len(current) + 8


def load_backup_rows(xlsx_path: Path, volume: str, section: str) -> list[dict[str, Any]]:
    if not xlsx_path.exists():
        raise FileNotFoundError(f"xlsx not found: {xlsx_path}")
    sheets = pd.read_excel(xlsx_path, sheet_name=None, dtype=str)
    chosen = None
    for name, df in sheets.items():
        cols = {str(c) for c in df.columns}
        if {"source_volume", "source_section", "source_description", "problem_text"}.issubset(cols):
            chosen = df
            break
        if str(name).lower() == "textbook_examples":
            chosen = df
            break
    if chosen is None:
        raise ValueError("No textbook_examples-like sheet found in xlsx.")

    rows: list[dict[str, Any]] = []
    for _, row in chosen.iterrows():
        item = {str(k): normalize_cell(v) for k, v in row.to_dict().items()}
        if item.get("source_volume") != volume:
            continue
        if item.get("source_section") != section:
            continue
        rows.append(item)
    return rows


def fetch_current_rows(conn: sqlite3.Connection, volume: str, section: str) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    return conn.execute(
        """
        SELECT id, source_description, problem_text, correct_answer, detailed_solution, notes
        FROM textbook_examples
        WHERE source_volume=? AND source_section=?
        ORDER BY id ASC
        """,
        (volume, section),
    ).fetchall()


def build_match_indexes(rows: list[sqlite3.Row]) -> tuple[dict[str, sqlite3.Row], dict[str, sqlite3.Row]]:
    by_dedupe: dict[str, sqlite3.Row] = {}
    by_title: dict[str, sqlite3.Row] = {}
    for row in rows:
        sd = str(row["source_description"] or "")
        dedupe = extract_dedupe(sd)
        title = normalize_title(sd)
        if dedupe and dedupe not in by_dedupe:
            by_dedupe[dedupe] = row
        if title and title not in by_title:
            by_title[title] = row
    return by_dedupe, by_title


def match_current_row(backup_row: dict[str, Any], by_dedupe: dict[str, sqlite3.Row], by_title: dict[str, sqlite3.Row]) -> sqlite3.Row | None:
    dedupe = extract_dedupe(backup_row.get("source_description", ""))
    if dedupe and dedupe in by_dedupe:
        return by_dedupe[dedupe]
    title = normalize_title(backup_row.get("source_description", ""))
    return by_title.get(title)


def restore_section(*, xlsx: Path, db_path: Path, volume: str, section: str, write: bool, report: Path) -> dict[str, Any]:
    sys.path.insert(0, str(project_root()))
    from core.textbook_processor import score_problem_text_quality

    backup_rows = load_backup_rows(xlsx, volume, section)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    current_rows = fetch_current_rows(conn, volume, section)
    by_dedupe, by_title = build_match_indexes(current_rows)

    stats = {
        "matched_records": 0,
        "backup_better_records": 0,
        "current_kept_records": 0,
        "updated_records": 0,
        "skipped_records": 0,
        "restored": [],
        "records": [],
    }

    for backup in backup_rows:
        current = match_current_row(backup, by_dedupe, by_title)
        if current is None:
            stats["skipped_records"] += 1
            stats["records"].append({"backup_title": backup.get("source_description", ""), "decision": "skipped_no_match"})
            continue

        stats["matched_records"] += 1
        backup_text = backup.get("problem_text", "")
        current_text = str(current["problem_text"] or "")
        backup_q = score_problem_text_quality(backup_text)
        current_q = score_problem_text_quality(current_text)
        backup_better = int(backup_q["score"]) > int(current_q["score"])
        answer_better = is_better_optional_text(backup.get("correct_answer", ""), str(current["correct_answer"] or ""))
        solution_better = is_better_optional_text(backup.get("detailed_solution", ""), str(current["detailed_solution"] or ""))
        decision = "proposed_restore" if backup_better else "keep_current"

        if backup_better:
            stats["backup_better_records"] += 1
        else:
            stats["current_kept_records"] += 1

        updated_fields = []
        if write and (backup_better or answer_better or solution_better):
            sets = []
            params: list[Any] = []
            if backup_better:
                sets.append("problem_text=?")
                params.append(backup_text)
                updated_fields.append("problem_text")
            if answer_better:
                sets.append("correct_answer=?")
                params.append(backup.get("correct_answer", ""))
                updated_fields.append("correct_answer")
            if solution_better:
                sets.append("detailed_solution=?")
                params.append(backup.get("detailed_solution", ""))
                updated_fields.append("detailed_solution")
            params.append(int(current["id"]))
            conn.execute(f"UPDATE textbook_examples SET {', '.join(sets)} WHERE id=?", params)
            stats["updated_records"] += 1
            stats["restored"].append({"id": int(current["id"]), "title": str(current["source_description"] or ""), "fields": updated_fields})

        stats["records"].append(
            {
                "id": int(current["id"]),
                "title": str(current["source_description"] or ""),
                "backup_title": backup.get("source_description", ""),
                "decision": decision,
                "backup_quality_score": int(backup_q["score"]),
                "current_quality_score": int(current_q["score"]),
                "formula_placeholder_count": int(current_q["placeholder_count"]),
                "latex_signal_count": int(current_q["latex_signal_count"]),
                "answer_restore": bool(answer_better),
                "solution_restore": bool(solution_better),
            }
        )

    if write:
        conn.commit()
    conn.close()

    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Textbook Examples Restore From Backup Report",
        f"- xlsx: `{xlsx.as_posix()}`",
        f"- volume: `{volume}`",
        f"- section: `{section}`",
        f"- dry_run: `{not write}`",
        "",
        "## Summary",
        f"- matched_records: `{stats['matched_records']}`",
        f"- backup_better_records: `{stats['backup_better_records']}`",
        f"- current_kept_records: `{stats['current_kept_records']}`",
        f"- updated_records: `{stats['updated_records']}`",
        f"- skipped_records: `{stats['skipped_records']}`",
        f"- restored: `{stats['restored']}`",
        "",
        "## Records",
    ]
    for row in stats["records"]:
        lines.append(
            "- id={id} | title=`{title}` | backup_title=`{backup_title}` | decision=`{decision}` | "
            "current_score=`{current_quality_score}` | backup_score=`{backup_quality_score}` | "
            "formula_placeholder_count=`{formula_placeholder_count}` | latex_signal_count=`{latex_signal_count}` | "
            "answer_restore=`{answer_restore}` | solution_restore=`{solution_restore}`".format(
                id=row.get("id", ""),
                title=row.get("title", ""),
                backup_title=row.get("backup_title", ""),
                decision=row.get("decision", ""),
                current_quality_score=row.get("current_quality_score", ""),
                backup_quality_score=row.get("backup_quality_score", ""),
                formula_placeholder_count=row.get("formula_placeholder_count", ""),
                latex_signal_count=row.get("latex_signal_count", ""),
                answer_restore=row.get("answer_restore", ""),
                solution_restore=row.get("solution_restore", ""),
            )
        )
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return stats


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", required=True)
    parser.add_argument("--volume", required=True)
    parser.add_argument("--section", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--report", required=True)
    parser.add_argument("--db", default="")
    args = parser.parse_args()

    if args.write and args.dry_run:
        raise SystemExit("Use either --dry-run or --write, not both.")
    write = bool(args.write)
    root = project_root()
    xlsx = Path(args.xlsx)
    if not xlsx.is_absolute():
        xlsx = root / xlsx
    report = Path(args.report)
    if not report.is_absolute():
        report = root / report
    db_path = Path(args.db) if args.db else default_db_path()

    stats = restore_section(
        xlsx=xlsx,
        db_path=db_path,
        volume=args.volume,
        section=args.section,
        write=write,
        report=report,
    )
    print(report.as_posix())
    print(json.dumps({k: stats[k] for k in ("matched_records", "backup_better_records", "updated_records", "skipped_records")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
