#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Repair math B4 chapter-2 self-assessment quality issues."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_db_path() -> Path:
    sys.path.insert(0, str(project_root()))
    from config import Config  # pylint: disable=import-outside-toplevel

    return Path(Config.db_path)


def load_helpers():
    sys.path.insert(0, str(project_root()))
    from core.textbook_processor import (  # pylint: disable=import-outside-toplevel
        infer_mathb4_ch2_self_assessment_skill,
        normalize_probability_event_notation,
    )

    return infer_mathb4_ch2_self_assessment_skill, normalize_probability_event_notation


def preview(text: str, n: int = 100) -> str:
    s = str(text or "").replace("\n", "\\n")
    return s[:n] + ("..." if len(s) > n else "")


def clear_needs_review_flag(source_description: str, problem_text: str) -> str:
    sd = str(source_description or "")
    if "needs_review=true" not in sd:
        return sd
    risk = any(k in str(problem_text or "") for k in ("[FORMULA_MISSING]", "[FORMULA_IMAGE_", "[WORD_EQUATION_UNPARSED]", "[BLOCK_IMAGE]"))
    if risk:
        return sd
    return sd.replace(" | needs_review=true", "").replace("needs_review=true | ", "").replace("needs_review=true", "").replace("[]", "").replace("  ", " ").strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(default_db_path()))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    do_apply = bool(args.apply)
    if not args.apply and not args.dry_run:
        args.dry_run = True

    db_path = Path(args.db).resolve()
    if not db_path.exists():
        print(f"DB not found: {db_path}")
        return 1

    infer_ch2, normalize_prob = load_helpers()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = cur.execute(
        """
        SELECT id, skill_id, source_chapter, source_section, source_description, problem_text
        FROM textbook_examples
        WHERE source_description LIKE '%source_type=self_assessment%'
          AND (source_chapter LIKE '%2%' OR source_chapter LIKE '%機率%' OR source_description LIKE '%自我評量%')
        """
    ).fetchall()

    changed = 0
    for row in rows:
        before_skill = str(row["skill_id"] or "")
        before_desc = str(row["source_description"] or "")
        before_text = str(row["problem_text"] or "")

        new_skill = before_skill
        if new_skill == "vh_數學B4_ProbabilityOperations":
            new_skill = "vh_數學B4_ProbabilityProperties"

        mapped = infer_ch2(str(row["source_chapter"] or ""), str(row["source_section"] or ""), before_desc, before_text)
        if mapped.get("skill_id"):
            mapped_skill = str(mapped["skill_id"])
            if mapped_skill == "vh_數學B4_ProbabilityOperations":
                mapped_skill = "vh_數學B4_ProbabilityProperties"
            new_skill = mapped_skill

        new_text, _ = normalize_prob(before_text)
        new_desc = clear_needs_review_flag(before_desc, new_text)

        if (new_skill, new_desc, new_text) == (before_skill, before_desc, before_text):
            continue
        changed += 1
        print(f"[CHANGE] id={row['id']}")
        print(f"  skill: {before_skill} -> {new_skill}")
        print(f"  desc : {preview(before_desc)}")
        print(f"        -> {preview(new_desc)}")
        print(f"  text : {preview(before_text)}")
        print(f"        -> {preview(new_text)}")

        if do_apply:
            cur.execute(
                "UPDATE textbook_examples SET skill_id=?, source_description=?, problem_text=? WHERE id=?",
                (new_skill, new_desc, new_text, row["id"]),
            )

    if do_apply:
        conn.commit()
        print(f"\nApplied changes: {changed}")
    else:
        print(f"\nDry-run changes: {changed}")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

