# -*- coding: utf-8 -*-
"""DB-only repair for B1 3-3 self-assessment Q19/Q20 (example_id 4723, 4724).

No gencode / component / publish / domain / commit / push.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "scratch" / f"_b1_3_3_rational_equation_db_backup_{STAMP}.json"

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

REPAIRS = {
    4723: {
        "qno": 19,
        "problem_text": (
            r"試求方程式$\frac{x}{1-x}=\frac{1}{x}$之解為 "
            r"(A)$x=\frac{-1\pm \sqrt{5}}{2}$ "
            r"(B)$x=\frac{-2\pm \sqrt{5}}{2}$ "
            r"(C)$x=\frac{-1\pm \sqrt{3}}{2}$ "
            r"(D)$x=\frac{-2\pm \sqrt{3}}{2}$。"
        ),
        "correct_answer": "A",
        "semantic_answer": "x = (-1 ± √5) / 2",
    },
    4724: {
        "qno": 20,
        "problem_text": (
            r"試求方程式$\frac{3}{\left( x-2 \right)\left( x+1 \right)}"
            r"+\frac{x+2}{x+1}=\frac{2}{x-2}$之解為 "
            r"(A) $x=1$ (B) $x=2$ (C) $x=3$ (D) $x=-2$。"
        ),
        "correct_answer": "C",
        "semantic_answer": "x = 3",
    },
}


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

    print("STEP1_SELECT")
    rows = {}
    for eid, spec in REPAIRS.items():
        row = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone()
        if row is None:
            raise SystemExit(f"STOP missing example_id={eid}")
        d = dict(row)
        rows[eid] = d
        rec = _dump_row(d)
        print(f"example_id={rec['example_id']}")
        print(f"  skill_id={rec['skill_id']}")
        print(f"  source_description={rec['source_description']}")
        print(f"  problem_text={rec['problem_text']}")
        print(f"  choices={rec['choices']}")
        print(f"  correct_answer={rec['correct_answer']}")
        print(f"  problem_type_id={rec['problem_type_id']}")
        print(f"  problem_type={rec['problem_type']}")
        print(f"  classification={rec['classification']}")
        print(f"  chapter={rec['chapter']}")
        print(f"  section={rec['section']}")

        conflicts = []
        if d["skill_id"] != EXPECTED_SKILL:
            conflicts.append(f"skill_id={d['skill_id']}")
        desc = str(d.get("source_description") or "")
        qno = spec["qno"]
        if f"題{qno}" not in desc and f"題 {qno}" not in desc:
            conflicts.append(f"source_description={desc} not 題{qno}")
        if "3-3" not in str(d.get("source_section") or ""):
            conflicts.append(f"section={d.get('source_section')}")
        if conflicts:
            raise SystemExit(f"STOP conflict id={eid}: {conflicts}")
        print(f"  MATCH Q{qno} {EXPECTED_SKILL}")

    backup = [_dump_row(rows[eid]) for eid in REPAIRS]
    BACKUP.write_text(json.dumps(backup, ensure_ascii=False, indent=2), encoding="utf-8")
    print("BACKUP", BACKUP)

    for eid, spec in REPAIRS.items():
        before = dict(conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone())
        conn.execute(
            "UPDATE textbook_examples SET problem_text = ?, correct_answer = ? WHERE id = ?",
            (spec["problem_text"], spec["correct_answer"], eid),
        )
        after = dict(conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone())
        locked_changed = {
            k: (before.get(k), after.get(k)) for k in LOCKED if before.get(k) != after.get(k)
        }
        if locked_changed:
            conn.rollback()
            raise SystemExit(f"locked_fields_changed:{eid}:{locked_changed}")
        if not _has_abcd(after["problem_text"]):
            conn.rollback()
            raise SystemExit(f"missing_choices:{eid}")
        if after["correct_answer"] != spec["correct_answer"]:
            conn.rollback()
            raise SystemExit(f"answer_mismatch:{eid}")
        stored = str(after["correct_answer"] or "")
        if eid == 4724 and ("x=-1" in stored.replace(" ", "") or stored in {"-1", "B"}):
            conn.rollback()
            raise SystemExit("4724 must not store x=-1 as answer")

    conn.commit()

    print("STEP4_VERIFY")
    for eid, spec in REPAIRS.items():
        d = dict(conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone())
        text = d["problem_text"]
        print(f"AFTER id={eid}")
        print(f"  skill_id={d['skill_id']}")
        print(f"  source_description={d['source_description']}")
        print(f"  problem_type={d['problem_type']}")
        print(f"  correct_answer={d['correct_answer']}")
        print(f"  semantic_answer={spec['semantic_answer']}")
        print(f"  has_abcd={_has_abcd(text)}")
        print(f"  problem_text={text}")
        if eid == 4723:
            assert r"\frac{x}{1-x}=\frac{1}{x}" in text
            assert r"\frac{-1\pm \sqrt{5}}{2}" in text
            assert r"\frac{-2\pm \sqrt{5}}{2}" in text
            assert r"\frac{-1\pm \sqrt{3}}{2}" in text
            assert r"\frac{-2\pm \sqrt{3}}{2}" in text
            assert d["correct_answer"] == "A"
        if eid == 4724:
            assert r"\frac{3}{\left( x-2 \right)\left( x+1 \right)}" in text
            assert r"\frac{x+2}{x+1}" in text
            assert r"\frac{2}{x-2}" in text
            assert "$x=1$" in text and "$x=2$" in text and "$x=3$" in text and "$x=-2$" in text
            assert d["correct_answer"] == "C"
            assert "x=-1" not in str(d["correct_answer"] or "")
            assert d["correct_answer"] != "-1"
        assert d["skill_id"] == EXPECTED_SKILL
        assert d["problem_type"] == rows[eid]["problem_type"]
        assert d["source_description"] == rows[eid]["source_description"]
        assert d["source_chapter"] == rows[eid]["source_chapter"]
        assert d["source_section"] == rows[eid]["source_section"]

    print("DONE")


if __name__ == "__main__":
    main()
