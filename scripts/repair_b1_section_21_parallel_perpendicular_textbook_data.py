#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Apply computed textbook data for B1 section 2-1 parallel/perpendicular examples.

Scope: skills ``vh_數學B1_PropertiesOfParallelLines`` and
``vh_數學B1_PropertiesOfPerpendicularLines``, example ids
4526, 4527, 4530, 4531, 4532, 4535, 4536, 4537, 4538, 4539, 4600, 4602.

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

TARGET_SKILL_IDS: tuple[str, ...] = (
    "vh_數學B1_PropertiesOfParallelLines",
    "vh_數學B1_PropertiesOfPerpendicularLines",
)
TARGET_IDS: tuple[int, ...] = (
    4526, 4527, 4530, 4531, 4532, 4535, 4536, 4537, 4538, 4539, 4600, 4602,
)

AUTHORITATIVE_PATCHES: dict[int, dict[str, str]] = {
    4530: {
        "correct_answer": "-6",
        "detailed_solution": (
            "m_AB=(5-0)/(-3-2)=-1；m_CD=(x+1)/5；平行得 -1=(x+1)/5，故 x=-6。"
        ),
    },
    4535: {
        "correct_answer": "3",
        "detailed_solution": (
            "m_AB=(1-(-5))/(4-1)=2；m_CD=(-3-x)/(-3)= (x+3)/3；"
            "平行得 2=(x+3)/3，故 x=3。"
        ),
    },
    4600: {
        "correct_answer": "C",
        "detailed_solution": (
            "m_AB=(5-3)/(2-1)=2；m_CD=(x-1)/2；平行得 x=5，選(C)。"
        ),
    },
    4602: {
        "correct_answer": "A",
        "detailed_solution": (
            "第一直線斜率 m=(5-3)/(3-1)=1；第二直線斜率 a；平行得 a=1，選(A)。"
        ),
    },
    4526: {
        "correct_answer": "-2/3；3/2",
        "detailed_solution": (
            "L1 斜率 m1=-2/3；(1) L2平行L1得 m2=-2/3；"
            "(2) L3垂直L1得 m3=-1/m1=3/2。"
        ),
    },
    4527: {
        "correct_answer": "是",
        "detailed_solution": (
            "m_AB=(3-1)/(1-2)=-2；m_AC=(2-1)/(4-2)=1/2；"
            "m_AB·m_AC=-1，故 △ABC 為直角三角形（直角在 A）。"
        ),
    },
    4531: {
        "correct_answer": "1",
        "detailed_solution": (
            "m_AB=(4-a)/5；m_CD=-5/3；垂直得 (4-a)/5·(-5/3)=-1，故 a=1。"
        ),
    },
    4532: {
        "correct_answer": "3/2；-2/3",
        "detailed_solution": (
            "m1=3/2；(1) L2平行L1得 m2=3/2；(2) L3垂直L1得 m3=-2/3。"
        ),
    },
    4536: {
        "correct_answer": "2",
        "detailed_solution": (
            "m_AB=(1-4)/(a+3)=-3/(a+3)；m_CD=10/6=5/3；"
            "垂直得 (-3/(a+3))·(5/3)=-1，故 a=2。"
        ),
    },
    4537: {
        "correct_answer": "-17",
        "detailed_solution": (
            "m1=(4-k)/(-k-3)；m2=(1-(-3))/(-2-4)=-2/3；"
            "垂直得 m1·m2=-1，解得 k=-17。"
        ),
    },
    4538: {
        "correct_answer": "D",
        "detailed_solution": (
            "L1 過第一、三象限得 m1>0；L2垂直L1得 m2=-1/m1<0；"
            "點 (m1,m2) 的 x>0、y<0，落在第四象限，選(D)。"
        ),
    },
    4539: {
        "correct_answer": "-1/2；2",
        "detailed_solution": (
            "m1=-1/2；(1) L2平行L1得 m2=-1/2；(2) L3垂直L1得 m3=2。"
        ),
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
        str(row["correct_answer"] or "") == patch["correct_answer"]
        and str(row["detailed_solution"] or "") == patch["detailed_solution"]
    )


def run(*, db_path: Path, apply: bool) -> dict[str, Any]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    report: dict[str, Any] = {
        "db_path": str(db_path),
        "apply": apply,
        "stamp": _utc_stamp(),
        "rows": [],
    }
    for example_id in TARGET_IDS:
        row = conn.execute(
            "SELECT id, skill_id, correct_answer, detailed_solution, notes FROM textbook_examples WHERE id=?",
            (example_id,),
        ).fetchone()
        patch = AUTHORITATIVE_PATCHES[example_id]
        item: dict[str, Any] = {"example_id": example_id, "patch": patch}
        if row is None:
            item["status"] = "missing_row"
            report["rows"].append(item)
            continue
        item["skill_id"] = str(row["skill_id"] or "")
        if item["skill_id"] not in TARGET_SKILL_IDS:
            item["status"] = "skill_mismatch"
            report["rows"].append(item)
            continue
        if _row_is_canonical(row, patch):
            item["status"] = "already_canonical"
            report["rows"].append(item)
            continue
        notes = _load_notes(row["notes"])
        notes["b1_section_21_parallel_perpendicular_data_fix"] = {
            "stamp": report["stamp"],
            "script": "repair_b1_section_21_parallel_perpendicular_textbook_data.py",
        }
        if apply:
            conn.execute(
                """
                UPDATE textbook_examples
                SET correct_answer = ?, detailed_solution = ?, notes = ?
                WHERE id = ?
                """,
                (
                    patch["correct_answer"],
                    patch["detailed_solution"],
                    _dump_notes(notes),
                    example_id,
                ),
            )
        item["status"] = "updated" if apply else "would_update"
        report["rows"].append(item)
    if apply:
        conn.commit()
    conn.close()
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--db", default=str(default_db_path()))
    args = parser.parse_args()
    report = run(db_path=Path(args.db), apply=bool(args.apply))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
