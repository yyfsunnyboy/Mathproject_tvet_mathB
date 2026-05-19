#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Apply canonical problem_text patch for Math B1 section 1-1 only.

Default mode is dry-run. Use --write to persist changes.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

TARGET_VOLUME = "數學B1"
TARGET_SECTION = "1-1 數線與絕對值"

CANONICAL_TEXTS: dict[str, str] = {
    "例題1": "數線上，若$\\left| x \\right|=7$，試求$x$之值。",
    "隨堂練習1": "數線上，若$\\left| x \\right|=4$，試求$x$之值。",
    "1-1習題 基礎題1": "數線上，若$\\left| x \\right|=8$，試求$x$之值。",
    "1-1習題 基礎題2": "已知數線上兩點$A\\left( -3 \\right)$、$B\\left( 7 \\right)$，試求A、B兩點的距離。",
    "例題2": "試求下列不等式之解：\n(1)$\\left| x \\right|<3$\n(2)$\\left| x \\right|\\ge 4$",
    "隨堂練習2": "試求下列不等式之解：\n(1)$\\left| x \\right|\\le 6$\n(2)$\\left| x \\right|>5$",
    "1-1習題 基礎題3": "試求下列不等式之解：\n(1)$\\left| x \\right|\\le 8$　(2)$\\left| x \\right|>10$　(3)$\\left| x \\right|<7$　(4)$\\left| x \\right|\\ge 12$",
    "例題4": "解下列不等式：\n(1)$\\left| x-2 \\right|<3$\n(2)$\\left| 4x-1 \\right|\\ge 7$",
    "隨堂練習4": "解下列不等式：\n(1)$\\left| x-5 \\right|>3$\n(2)$\\left| 2x-5 \\right|\\le 3$",
    "111統測B": "若不等式$\\left| 7x-a \\right|<28$之解為$b<x<5$，則點$\\left( b,a \\right)$屬於哪一象限？\n(A)第一象限\n(B)第二象限\n(C)第三象限\n(D)第四象限\n〔111統測B〕",
    "1-1習題 基礎題5": "解下列不等式：\n(1)$\\left| x-2 \\right|\\le 4$　(2)$\\left| x+5 \\right|>1$",
    "1-1習題 基礎題6": "解下列不等式：\n(1)$\\left| x-3 \\right|<2$　(2)$\\left| x+5 \\right|\\ge 4$",
    "1-1習題 基礎題7": "解不等式$\\left| 4x+1 \\right|\\le 6$。",
    "1-1習題 基礎題8": "解不等式$\\left| 2x-3 \\right|>1$。",
    "1-1習題 基礎題9": "解不等式$\\left| 3x-1 \\right|\\ge 7$。",
    "1-1習題 基礎題10": "解不等式$\\left| 5x+3 \\right|<7$。",
}


def default_db_path() -> Path:
    return Path(__file__).resolve().parents[1] / "instance" / "math_system.db"


def _extract_title(source_description: str) -> str:
    return str(source_description or "").split(" [", 1)[0].strip()


def normalize_title(title: str) -> str:
    t = re.sub(r"\s+", "", str(title or ""))
    t = t.replace("例", "例題") if re.fullmatch(r"例\d+", t) else t
    t = re.sub(r"^隨堂練習(\d+)$", r"隨堂練習\1", t)
    return t


def canonical_map_normalized() -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for k, v in CANONICAL_TEXTS.items():
        out[normalize_title(k)] = (k, v)
    return out


def _load_notes(raw: Any) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(str(raw))
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _dump_notes(meta: dict[str, Any]) -> str:
    return json.dumps(meta, ensure_ascii=False)


def apply_patch(conn: sqlite3.Connection, *, write: bool = False) -> dict[str, Any]:
    cmap = canonical_map_normalized()
    rows = conn.execute(
        """
        SELECT id, source_description, problem_text, notes
        FROM textbook_examples
        WHERE source_volume = ? AND source_section = ?
        ORDER BY id ASC
        """,
        (TARGET_VOLUME, TARGET_SECTION),
    ).fetchall()

    matched_records = 0
    updated_records = 0
    skipped_records = 0
    updated_ids: list[int] = []
    per_record: list[dict[str, Any]] = []

    for row in rows:
        rid, source_description, old_problem_text, old_notes = row
        raw_title = _extract_title(source_description)
        ntitle = normalize_title(raw_title)
        canonical = cmap.get(ntitle)
        if not canonical:
            skipped_records += 1
            per_record.append({"id": rid, "title": raw_title, "action": "skip_not_in_canonical"})
            continue

        matched_records += 1
        canonical_title, new_problem_text = canonical
        notes_obj = _load_notes(old_notes)
        old_text = str(old_problem_text or "")
        changed = old_text != new_problem_text

        clean_formula = ("[FORMULA_IMAGE_" not in new_problem_text) and ("[FORMULA_MISSING]" not in new_problem_text)
        if clean_formula:
            notes_obj["needs_formula_review"] = False
            notes_obj["formula_missing"] = False
            notes_obj["review_required"] = False
        new_notes = _dump_notes(notes_obj)
        notes_changed = str(old_notes or "") != new_notes

        if changed or notes_changed:
            updated_records += 1
            updated_ids.append(int(rid))
            if write:
                conn.execute(
                    "UPDATE textbook_examples SET problem_text = ?, notes = ? WHERE id = ?",
                    (new_problem_text, new_notes, rid),
                )
            per_record.append(
                {
                    "id": rid,
                    "title": raw_title,
                    "canonical_title": canonical_title,
                    "action": "update",
                    "problem_text_before": old_text[:80],
                    "problem_text_after": new_problem_text[:80],
                    "notes_flags_after": {
                        "needs_formula_review": notes_obj.get("needs_formula_review"),
                        "formula_missing": notes_obj.get("formula_missing"),
                        "review_required": notes_obj.get("review_required"),
                    },
                }
            )
        else:
            skipped_records += 1
            per_record.append({"id": rid, "title": raw_title, "canonical_title": canonical_title, "action": "skip_no_change"})

    if write:
        conn.commit()

    return {
        "mode": "write" if write else "dry-run",
        "scope": {"source_volume": TARGET_VOLUME, "source_section": TARGET_SECTION},
        "matched_records": matched_records,
        "updated_records": updated_records,
        "skipped_records": skipped_records,
        "updated_ids": updated_ids,
        "per_record": per_record,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply canonical problem_text patch for B1 1-1 only.")
    parser.add_argument("--db", default=str(default_db_path()), help="Path to sqlite DB.")
    parser.add_argument("--write", action="store_true", help="Persist updates.")
    args = parser.parse_args()

    db_path = Path(args.db).expanduser().resolve()
    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}")

    conn = sqlite3.connect(str(db_path))
    try:
        report = apply_patch(conn, write=bool(args.write))
    finally:
        conn.close()

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
