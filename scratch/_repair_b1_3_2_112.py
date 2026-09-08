# -*- coding: utf-8 -*-
"""Repair B1 3-2 112統測B row only. No gencode / commit."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "scratch" / f"_b1_3_2_112_db_repair_backup_{STAMP}.json"
REPORT = ROOT / "scratch" / "_b1_3_2_112_db_repair_report.json"
EID = 4655
LOCKED = (
    "skill_id",
    "problem_type",
    "source_curriculum",
    "source_volume",
    "source_chapter",
    "source_section",
    "source_paragraph",
    "source_description",
    "difficulty_level",
    "difficulty_h",
    "notes",
)
NEW_TEXT = (
    r"已知多項式$f\left( x \right)$除以$\left( x+2 \right)\left( x-7 \right)$的餘式為$ax+3$。"
    r"若$\left( x-7 \right)$為$f\left( x \right)$的因式，則$f\left( -2 \right)=$？ "
    r"(A) $\frac{27}{7}$ (B) $\frac{29}{7}$ (C) $\frac{31}{7}$ (D) $\frac{33}{7}$。"
)


def _has_abcd(text: str) -> bool:
    t = (text or "").replace("（", "(").replace("）", ")")
    return all(f"({lab})" in t for lab in "ABCD")


def main() -> None:
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (EID,)).fetchone()
    if row is None:
        raise SystemExit("NOT_FOUND:4655")
    before = dict(row)
    markers = {
        "source_112": "112統測" in str(before.get("source_description") or ""),
        "divisor": "(x+2)" in (before.get("problem_text") or "").replace(" ", "")
        or "x+2" in (before.get("problem_text") or ""),
        "remainder_ax3": "ax+3" in (before.get("problem_text") or "").replace(" ", ""),
        "factor_x7": "x-7" in (before.get("problem_text") or "").replace(" ", ""),
        "ask_f_minus_2": "f\\left( -2 \\right)" in (before.get("problem_text") or ""),
        "choices_27_33": all(
            tok in (before.get("problem_text") or "")
            for tok in (r"\frac{27}{7}", r"\frac{29}{7}", r"\frac{31}{7}", r"\frac{33}{7}")
        ),
    }
    if not all(markers.values()):
        raise SystemExit(f"NOT_HIGH_CONFIDENCE:{markers}")
    if before["skill_id"] != "vh_數學B1_FactorTheorem":
        raise SystemExit(f"skill_conflict:{before['skill_id']}")

    BACKUP.write_text(
        json.dumps(
            [
                {
                    "example_id": before["id"],
                    "problem_text": before.get("problem_text"),
                    "choices": None,
                    "correct_answer": before.get("correct_answer"),
                    "source_description": before.get("source_description"),
                    "skill_id": before.get("skill_id"),
                    "problem_type_id": None,
                    "problem_type": before.get("problem_type"),
                }
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    conn.execute(
        "UPDATE textbook_examples SET problem_text = ?, correct_answer = ? WHERE id = ?",
        (NEW_TEXT, "A", EID),
    )
    after = dict(conn.execute("SELECT * FROM textbook_examples WHERE id=?", (EID,)).fetchone())
    locked_changed = {
        k: (before.get(k), after.get(k)) for k in LOCKED if before.get(k) != after.get(k)
    }
    if locked_changed:
        raise SystemExit(f"locked_fields_changed:{locked_changed}")
    conn.commit()
    q = after["problem_text"] or ""
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mapping": {
            "source": "112統測B",
            "example_id": EID,
            "skill_id": after["skill_id"],
            "match_confidence": "HIGH",
            "reason": "source_description=112統測B; stem has (x+2)(x-7), ax+3, factor x-7, ask f(-2), choices 27/7..33/7",
            "rejected_near_miss": {
                "example_id": 4649,
                "reason": "3-2習題 進階題 10; different stem x^2+ax+3",
            },
        },
        "backup_path": str(BACKUP.relative_to(ROOT)),
        "fields_changed": [
            k
            for k in ("problem_text", "correct_answer")
            if before.get(k) != after.get(k)
        ],
        "before": {
            "problem_text": before.get("problem_text"),
            "correct_answer": before.get("correct_answer"),
            "source_description": before.get("source_description"),
        },
        "after": {
            "problem_text": after.get("problem_text"),
            "correct_answer": after.get("correct_answer"),
            "source_description": after.get("source_description"),
            "skill_id": after.get("skill_id"),
            "problem_type": after.get("problem_type"),
        },
        "verify": {
            "choices_complete": "YES" if _has_abcd(q) else "NO",
            "stored_label": after.get("correct_answer"),
            "semantic_answer": "27/7",
            "source_description": after.get("source_description"),
            "skill_id_unchanged": before["skill_id"] == after["skill_id"],
            "problem_type_unchanged": before["problem_type"] == after["problem_type"],
        },
        "status": "REPAIRED",
        "safety": {
            "skill_id_changed": "NO",
            "problem_type_changed": "NO",
            "classification_changed": "NO",
            "gencode_executed": "NO",
        },
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("REPAIRED", EID, report["fields_changed"], after["correct_answer"])


if __name__ == "__main__":
    main()
