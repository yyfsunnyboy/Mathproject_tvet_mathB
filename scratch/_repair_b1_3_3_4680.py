# -*- coding: utf-8 -*-
"""DB-only repair for B1 3-3 112統測B (example_id 4680).

Appends the pre-repair row to the round 3-3 backup.
No gencode / component / publish / domain / commit / push.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
BACKUP = ROOT / "scratch" / "_b1_3_3_rational_equation_db_backup_20260908_120805.json"
EID = 4680
EXPECTED_SKILL = "vh_數學B1_RationalEquation"
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
    r"已知多項式$Q\left( x \right)=ax+b$，"
    r"$f\left( x \right)=\left( 2a-b \right){{x}^{2}}+ax-1$，"
    r"$g\left( x \right)=3{{x}^{2}}+x-1$，"
    r"且$f\left( x \right)=g\left( x \right)$。"
    r"若分式方程式$\frac{x}{Q\left( x \right)}+\frac{5}{x-2}"
    r"=\frac{-1}{\left( x-2 \right)Q\left( x \right)}$的解為$x=c$，"
    r"則${{a}^{2}}+{{b}^{2}}+{{c}^{2}}=$？ "
    r"(A) 4 (B) 10 (C) 18 (D) 27 〔112統測B〕"
)


def _has_abcd(text: str) -> bool:
    t = (text or "").replace("（", "(").replace("）", ")")
    return all(f"({lab})" in t for lab in "ABCD")


def _dump_row(d: dict) -> dict:
    return {
        "example_id": d.get("id"),
        "skill_id": d.get("skill_id"),
        "source_description": d.get("source_description"),
        "problem_text": d.get("problem_text"),
        "choices": None,
        "correct_answer": d.get("correct_answer"),
        "problem_type_id": None,
        "problem_type": d.get("problem_type"),
        "classification": None,
        "chapter": d.get("source_chapter"),
        "section": d.get("source_section"),
        "source_paragraph": d.get("source_paragraph"),
        "detailed_solution": d.get("detailed_solution"),
        "notes": d.get("notes"),
    }


def main() -> None:
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (EID,)).fetchone()
    if row is None:
        raise SystemExit("STOP missing example_id=4680")
    before = dict(row)
    rec = _dump_row(before)
    print("STEP1_SELECT")
    for k, v in rec.items():
        print(f"  {k}={v}")

    text = before.get("problem_text") or ""
    compact = text.replace(" ", "")
    markers = {
        "source_112": "112統測B" in str(before.get("source_description") or ""),
        "skill": before.get("skill_id") == EXPECTED_SKILL,
        "section_3_3": "3-3" in str(before.get("source_section") or ""),
        "q_ax_b": "ax+b" in compact,
        "f_poly": "2a-b" in compact and "ax-1" in compact,
        "g_poly": "3x^2+x-1" in compact.replace("{", "").replace("}", "").replace("^", "")
        or r"3{{x}^{2}}+x-1" in text,
        "f_eq_g": r"f\left( x \right)=g\left( x \right)" in text,
        "rational_eq": r"\frac{x}{Q" in text and r"\frac{5}{x-2}" in text,
        "ask_abc": r"{{a}^{2}}+{{b}^{2}}+{{c}^{2}}" in text,
        "has_18_27": "(C)18" in compact or "(C) 18" in text,
    }
    print("MARKERS", markers)
    if not all(markers.values()):
        raise SystemExit(f"STOP not HIGH confidence: {markers}")

    backup = json.loads(BACKUP.read_text(encoding="utf-8"))
    if any(item.get("example_id") == EID for item in backup):
        raise SystemExit("STOP 4680 already in backup; refuse double-append")
    backup.append(rec)
    BACKUP.write_text(json.dumps(backup, ensure_ascii=False, indent=2), encoding="utf-8")
    print("BACKUP_APPENDED", BACKUP.name, "n=", len(backup))

    conn.execute(
        "UPDATE textbook_examples SET problem_text = ?, correct_answer = ? WHERE id = ?",
        (NEW_TEXT, "C", EID),
    )
    after = dict(conn.execute("SELECT * FROM textbook_examples WHERE id=?", (EID,)).fetchone())
    locked_changed = {
        k: (before.get(k), after.get(k)) for k in LOCKED if before.get(k) != after.get(k)
    }
    if locked_changed:
        conn.rollback()
        raise SystemExit(f"locked_fields_changed:{locked_changed}")
    q = after["problem_text"] or ""
    if not _has_abcd(q):
        conn.rollback()
        raise SystemExit("missing_choices")
    if after["correct_answer"] != "C":
        conn.rollback()
        raise SystemExit("answer_must_be_C")
    stored = str(after["correct_answer"] or "")
    if stored in {"-4", "c=-4", "x=-4"} or "x=1" in stored:
        conn.rollback()
        raise SystemExit("must not store extraneous root as answer")
    if "(A) 4" not in q or "(B) 10" not in q or "(C) 18" not in q or "(D) 27" not in q:
        conn.rollback()
        raise SystemExit("choices_mismatch")
    if "(A) 3" in q or "(A)3" in q.replace(" ", ""):
        conn.rollback()
        raise SystemExit("choice_A_must_be_4_not_3")
    conn.commit()

    print("STEP4_VERIFY")
    print("  question complete = YES")
    print("  choices = 4")
    print("  stored answer =", after["correct_answer"])
    print("  semantic answer = 18")
    print("  skill_id unchanged =", before["skill_id"] == after["skill_id"])
    print("  problem_type unchanged =", before["problem_type"] == after["problem_type"])
    print("  source_description =", after["source_description"])
    print("  problem_text =", after["problem_text"])
    print("DONE")


if __name__ == "__main__":
    main()
