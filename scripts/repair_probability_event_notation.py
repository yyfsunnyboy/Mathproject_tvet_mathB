#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Repair probability event notation in textbook_examples.problem_text.

Usage:
    python scripts/repair_probability_event_notation.py --dry-run
    python scripts/repair_probability_event_notation.py --apply
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


TARGET_SKILLS = {
    "vh_數學B4_ProbabilityDefinition",
    "vh_數學B4_ProbabilityProperties",
    "vh_數學B4_ConditionalProbability",
    "vh_數學B4_IndependentEvents",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_db_path() -> Path:
    sys.path.insert(0, str(project_root()))
    from config import Config  # pylint: disable=import-outside-toplevel

    return Path(Config.db_path)


def load_normalizer():
    sys.path.insert(0, str(project_root()))
    from core.textbook_processor import normalize_probability_event_notation  # pylint: disable=import-outside-toplevel

    return normalize_probability_event_notation


def preview(text: str, width: int = 120) -> str:
    t = (text or "").replace("\n", "\\n")
    return t[:width] + ("..." if len(t) > width else "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(default_db_path()))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    do_apply = bool(args.apply)
    if not args.apply and not args.dry_run:
        args.dry_run = True

    db_path = Path(args.db).resolve()
    if not db_path.exists():
        print(f"DB not found: {db_path}")
        return 1

    normalize_fn = load_normalizer()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    placeholders = ",".join("?" for _ in TARGET_SKILLS)
    rows = cur.execute(
        f"""
        SELECT id, skill_id, source_description, problem_text
        FROM textbook_examples
        WHERE skill_id IN ({placeholders})
        """,
        sorted(TARGET_SKILLS),
    ).fetchall()

    changed = 0
    for row in rows:
        before = str(row["problem_text"] or "")
        after, meta = normalize_fn(before)
        if not meta.get("changed"):
            continue
        changed += 1
        print(f"[CHANGE] id={row['id']} skill={row['skill_id']}")
        print(f"  title: {preview(str(row['source_description'] or ''))}")
        print(f"  before: {preview(before)}")
        print(f"  after : {preview(after)}")
        if do_apply:
            cur.execute("UPDATE textbook_examples SET problem_text=? WHERE id=?", (after, row["id"]))

    if do_apply:
        conn.commit()
        print(f"\nApplied changes: {changed}")
    else:
        print(f"\nDry-run changes: {changed}")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

