#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Diagnose textbook import merge quality decisions for one volume/section."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_db_path() -> Path:
    sys.path.insert(0, str(project_root()))
    from config import Config  # pylint: disable=import-outside-toplevel

    return Path(Config.db_path)


def load_incoming_map(path: str) -> dict[str, str]:
    if not path:
        return {}
    p = Path(path)
    if not p.is_absolute():
        p = project_root() / p
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items()}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser()
    parser.add_argument("--volume", required=True)
    parser.add_argument("--section", required=True)
    parser.add_argument("--incoming-json", default="", help="Optional id/title -> incoming_problem_text map.")
    parser.add_argument("--db", default="")
    args = parser.parse_args()

    sys.path.insert(0, str(project_root()))
    from core.textbook_processor import score_problem_text_quality, should_replace_problem_text

    db_path = Path(args.db) if args.db else default_db_path()
    incoming_map = load_incoming_map(args.incoming_json)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT id, source_description, problem_text
        FROM textbook_examples
        WHERE source_volume=? AND source_section=?
        ORDER BY id ASC
        """,
        (args.volume, args.section),
    ).fetchall()
    conn.close()

    print("# Text Quality Merge Diagnosis")
    print(f"- volume: `{args.volume}`")
    print(f"- section: `{args.section}`")
    print(f"- rows: `{len(rows)}`")
    print("")
    for row in rows:
        rid = int(row["id"])
        title = str(row["source_description"] or "")
        existing = str(row["problem_text"] or "")
        incoming = incoming_map.get(str(rid), incoming_map.get(title, ""))
        existing_q = score_problem_text_quality(existing)
        incoming_q = score_problem_text_quality(incoming) if incoming else {}
        if incoming:
            replace, _, _ = should_replace_problem_text(existing, incoming)
            decision = "update_incoming" if replace else "keep_existing"
        else:
            decision = "no_incoming"
        print(f"## id={rid} {title}")
        print(f"- existing_problem_text: `{existing}`")
        print(f"- incoming_problem_text: `{incoming}`")
        print(f"- existing_quality_score: `{existing_q.get('score')}`")
        print(f"- incoming_quality_score: `{incoming_q.get('score', '')}`")
        print(f"- merge_decision: `{decision}`")
        print(f"- formula_placeholder_count: `{existing_q.get('placeholder_count')}`")
        print(f"- latex_signal_count: `{existing_q.get('latex_signal_count')}`")
        print("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
