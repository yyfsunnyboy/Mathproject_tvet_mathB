#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Apply authoritative textbook data for blocked SlopeOfALine examples.

Scope: skill ``vh_數學B1_SlopeOfALine``, textbook example ids 4519, 4520,
4533, 4534, 4601 only.

Default mode is dry-run. Use ``--apply`` to persist changes.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TARGET_SKILL_ID = "vh_數學B1_SlopeOfALine"
TARGET_IDS: tuple[int, ...] = (4519, 4520, 4533, 4534, 4601)

AUTHORITATIVE_PATCHES: dict[int, dict[str, str]] = {
    4519: {
        "problem_text": (
            "設$A\\left( -2,2 \\right)$、$B\\left( 3,-2 \\right)$、$C\\left( 5,2 \\right)$、$D\\left( 3,4 \\right)$，"
            "試求下列直線的斜率並在坐標平面上畫出圖形。"
            "(1)直線AB (2)直線BC(3)直線AC (4)直線BD。"
        ),
        "correct_answer": "-4/5；2；0；不存在",
        "detailed_solution": (
            "AB：m=(-2-2)/(3-(-2))=-4/5；"
            "BC：m=(2-(-2))/(5-3)=2；"
            "AC：m=(2-2)/(5-(-2))=0；"
            "BD：x相同，斜率不存在。"
        ),
    },
    4520: {
        "problem_text": (
            "(1) 請將m = 0、m不存在、m > 0、m < 0，填入下列各圖形的斜率。①②③④"
            "(2) 設${{m}_{1}}$、${{m}_{2}}$分別為直線${{L}_{1}}$、${{L}_{2}}$的斜率，"
            "試比較圖①、圖②中${{m}_{1}}$與${{m}_{2}}$的大小。① ②"
        ),
        "correct_answer": "m>0；m=0；m不存在；m<0；m1>m2；m1<m2",
        "detailed_solution": (
            "(1)四圖依序為正斜率、水平、鉛直、負斜率；"
            "(2)兩比較圖依序為m1>m2、m1<m2。"
        ),
    },
    4533: {
        "problem_text": (
            "如圖所示$A\\left( -1,4 \\right)$、$B\\left( 2,-1 \\right)$、$C\\left( -2,2 \\right)$、"
            "$D\\left( -3,-1 \\right)$、$P\\left( 2,2 \\right)$，試求下列直線的斜率。"
            "(1)直線AP (2)直線BP(3)直線CP (4)直線DP。"
        ),
        "correct_answer": "-2/3；不存在；0；3/5",
        "detailed_solution": (
            "AP：m=(2-4)/(2-(-1))=-2/3；"
            "BP：x相同，斜率不存在；"
            "CP：m=(2-2)/(2-(-2))=0；"
            "DP：m=(2-(-1))/(2-(-3))=3/5。"
        ),
    },
    4534: {
        "problem_text": (
            "若$A\\left( -3,k \\right)$、$B\\left( -1,0 \\right)$、$C\\left( 3,-2 \\right)$"
            "三點無法連結成一個三角形，試求k之值。"
        ),
        "correct_answer": "1",
        "detailed_solution": "三點共線時無法構成三角形；由斜率相等得k=1。",
    },
    4601: {
        "problem_text": (
            "設$P\\left( 4,2 \\right)$、$Q\\left( 0,a \\right)$、$R\\left( 8,-2 \\right)$為共線之三點，"
            "則a = (A) 5 (B) 6 (C) 7 (D) 8。"
        ),
        "correct_answer": "B",
        "detailed_solution": "共線得(a-2)/(0-4)=(-2-2)/(8-4)⇒(a-2)/(-4)=(-4)/4⇒a-2=-(-4)⇒a=6，選(B)。",
    },
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_db_path() -> Path:
    sys.path.insert(0, str(project_root()))
    from config import Config  # pylint: disable=import-outside-toplevel

    return Path(Config.db_path)


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


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _row_is_canonical(row: sqlite3.Row, patch: dict[str, str]) -> bool:
    return (
        str(row["problem_text"] or "") == patch["problem_text"]
        and str(row["correct_answer"] or "") == patch["correct_answer"]
        and str(row["detailed_solution"] or "") == patch["detailed_solution"]
    )


def apply_patch(
    conn: sqlite3.Connection,
    *,
    write: bool = False,
    repaired_at: str | None = None,
) -> dict[str, Any]:
    """Apply authoritative patches for scoped SlopeOfALine examples."""
    stamp = repaired_at or _utc_stamp()
    placeholders = ",".join("?" for _ in TARGET_IDS)
    rows = conn.execute(
        f"""
        SELECT id, skill_id, source_description, problem_text, correct_answer, detailed_solution, notes
        FROM textbook_examples
        WHERE id IN ({placeholders})
        ORDER BY id ASC
        """,
        TARGET_IDS,
    ).fetchall()

    found_ids = {int(row["id"]) for row in rows}
    missing_ids = [eid for eid in TARGET_IDS if eid not in found_ids]

    updated_records = 0
    skipped_records = 0
    rejected_records = 0
    updated_ids: list[int] = []
    per_record: list[dict[str, Any]] = []

    for row in rows:
        eid = int(row["id"])
        patch = AUTHORITATIVE_PATCHES[eid]
        skill_id = str(row["skill_id"] or "").strip()
        if skill_id != TARGET_SKILL_ID:
            rejected_records += 1
            per_record.append(
                {
                    "id": eid,
                    "action": "reject_skill_mismatch",
                    "expected_skill_id": TARGET_SKILL_ID,
                    "actual_skill_id": skill_id,
                }
            )
            continue

        if _row_is_canonical(row, patch):
            skipped_records += 1
            per_record.append({"id": eid, "action": "skip_already_canonical"})
            continue

        notes_obj = _load_notes(row["notes"])
        notes_obj["formal_data_repair"] = {
            "skill_id": TARGET_SKILL_ID,
            "repaired_at": stamp,
            "reason": "authoritative_source_completion",
            "fields": sorted(patch.keys()),
        }
        new_notes = _dump_notes(notes_obj)

        updated_records += 1
        updated_ids.append(eid)
        if write:
            conn.execute(
                """
                UPDATE textbook_examples
                SET problem_text = ?, correct_answer = ?, detailed_solution = ?, notes = ?
                WHERE id = ? AND skill_id = ?
                """,
                (
                    patch["problem_text"],
                    patch["correct_answer"],
                    patch["detailed_solution"],
                    new_notes,
                    eid,
                    TARGET_SKILL_ID,
                ),
            )
        per_record.append(
            {
                "id": eid,
                "action": "update",
                "fields": sorted(patch.keys()),
            }
        )

    if write:
        conn.commit()

    return {
        "mode": "write" if write else "dry-run",
        "scope": {
            "skill_id": TARGET_SKILL_ID,
            "target_ids": list(TARGET_IDS),
        },
        "found_ids": sorted(found_ids),
        "missing_ids": missing_ids,
        "updated_records": updated_records,
        "skipped_records": skipped_records,
        "rejected_records": rejected_records,
        "updated_ids": updated_ids,
        "per_record": per_record,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Repair authoritative SlopeOfALine textbook data (4519/4520/4533/4534/4601)."
    )
    parser.add_argument("--db", default=str(default_db_path()), help="Path to sqlite DB.")
    parser.add_argument("--apply", action="store_true", help="Persist updates.")
    parser.add_argument("--dry-run", action="store_true", help="Preview updates without writing.")
    args = parser.parse_args()

    if not args.apply and not args.dry_run:
        args.dry_run = True

    db_path = Path(args.db).expanduser().resolve()
    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        report = apply_patch(conn, write=bool(args.apply))
    finally:
        conn.close()

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report.get("missing_ids"):
        return 1
    if report.get("rejected_records"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
