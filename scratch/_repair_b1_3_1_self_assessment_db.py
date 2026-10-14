# -*- coding: utf-8 -*-
"""Phase A: match + backup + repair HIGH-confidence 3-1 self-assessment rows."""
from __future__ import annotations

import json
import sqlite3
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
BACKUP = ROOT / "scratch" / f"_b1_3_1_db_repair_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
REPORT = ROOT / "scratch" / "_b1_3_1_db_repair_report.json"

# Matching (HIGH only repairs):
# 4706 -> Q3, 4716 -> Q2, 4717 -> Q4, 4718 -> Q5, 4719 -> Q6, 4720 -> Q7
# 4618/4629 table SKIP; 4628 統測 NOT matched; Q1 missing in DB

REPAIRS = {
    4706: {
        "textbook_no": 3,
        "confidence": "HIGH",
        "reason": "source_description=CH1自我評量 題3; stem matches product (3x^3-...)(2x^2-...); partial choice A=−7",
        "problem_text": (
            r"$\left( 3{{x}^{3}}-2{{x}^{2}}+2x-5 \right)\left( 2{{x}^{2}}-5x-7 \right)$"
            r"乘積中，${{x}^{3}}$項的係數為 (A) −7 (B) −11 (C) −21 (D) 18。"
        ),
        "correct_answer": "A",
        "detailed_solution": "展開求 x^3 係數：3·(−7)+ (−2)·(−5)+2·2 = −21+10+4 = −7。故選 (A)。",
    },
    4716: {
        "textbook_no": 2,
        "confidence": "HIGH",
        "reason": "source_description=CH1自我評量 題2; stem matches deg f=4,g=5,h=fg,k=f+g truncated at 則",
        "problem_text": (
            r"設$f\left( x \right)$為四次多項式，$g\left( x \right)$為五次多項式，"
            r"$h\left( x \right)=f\left( x \right)\times g\left( x \right)$，"
            r"$k\left( x \right)=f\left( x \right)+g\left( x \right)$且"
            r"$h\left( x \right)$為a次多項式，$k\left( x \right)$為b次多項式，則a − b = ？"
            r" (A) 4 (B) 14 (C) 9 (D) 6。"
        ),
        "correct_answer": "A",
        "detailed_solution": "deg h=4+5=9，deg k=5（首項不消去），a−b=9−5=4。故選 (A)。",
    },
    4717: {
        "textbook_no": 4,
        "confidence": "HIGH",
        "reason": "source_description=CH1自我評量 題4; stem matches (ax^2+bx+c)^3 identity truncated at 則",
        "problem_text": (
            r"設${{x}^{6}}-3{{x}^{5}}+12{{x}^{4}}-19{{x}^{3}}+36{{x}^{2}}-27x+27="
            r"{{\left( a{{x}^{2}}+bx+c \right)}^{3}}$，則a + b + c = ？"
            r" (A) 2 (B) 3 (C) 4 (D) 5。"
        ),
        "correct_answer": "B",
        "detailed_solution": "由 $(x^2-x+3)^3$ 得 a=1,b=−1,c=3，a+b+c=3。故選 (B)。",
    },
    4718: {
        "textbook_no": 5,
        "confidence": "HIGH",
        "reason": "source_description=CH1自我評量 題5; stem+4 choices already match textbook Q5; missing correct_answer",
        "problem_text": (
            r"多項式${{x}^{4}}-3{{x}^{3}}+{{x}^{2}}+x+1$除以${{x}^{2}}+x-2$，"
            r"餘式為ax + b，則a + b = (A) 1 (B) 2 (C) 3 (D) 4。"
        ),
        "correct_answer": "A",
        "detailed_solution": "餘式為 −14x+15，a+b=1。故選 (A)。",
    },
    4719: {
        "textbook_no": 6,
        "confidence": "HIGH",
        "reason": "source_description=CH1自我評量 題6; stem+choices match textbook Q6; missing correct_answer",
        "problem_text": (
            r"已知a、b為實數，若${{x}^{3}}+a{{x}^{2}}+bx-6$可被${{x}^{2}}-x+3$整除，"
            r"則a + b = (A) −2 (B) 0 (C) 2 (D) 4。"
        ),
        "correct_answer": "C",
        "detailed_solution": "整除條件解得 a+b=2。故選 (C)。",
    },
    4720: {
        "textbook_no": 7,
        "confidence": "HIGH",
        "reason": "source_description=CH1自我評量 題7; stem+choices match textbook Q7; missing correct_answer",
        "problem_text": (
            r"設$f\left( x \right)$為多項式，且$4{{x}^{3}}+x+1="
            r"f\left( x \right)\left( 2{{x}^{2}}-x+3 \right)-4x-2$，"
            r"則$f\left( x \right)=$ (A) 10x − 2 (B) 6x + 2 (C) 4x − 1 (D) 2x + 1。"
        ),
        "correct_answer": "D",
        "detailed_solution": "移項得 f(x)(2x^2-x+3)=4x^3+5x+3，長除得 f(x)=2x+1。故選 (D)。",
    },
}

MATCHING = [
    {
        "example_id": 4618,
        "textbook_no": None,
        "confidence": "N/A",
        "matched": False,
        "reason": "例1 完成下表；非自我評量選擇題；表缺",
    },
    {
        "example_id": 4628,
        "textbook_no": None,
        "confidence": "HIGH_NOT_MATCH",
        "matched": False,
        "reason": "source=110統測B；題幹為二次多項式餘式條件求 c，與自我評量第1～7題皆不符",
    },
    {
        "example_id": 4629,
        "textbook_no": None,
        "confidence": "N/A",
        "matched": False,
        "reason": "隨堂練習1 完成下表；非自我評量選擇題；表缺",
    },
    {
        "example_id": 4706,
        "textbook_no": 3,
        "confidence": "HIGH",
        "matched": True,
        "reason": REPAIRS[4706]["reason"],
    },
    {
        "example_id": 4716,
        "textbook_no": 2,
        "confidence": "HIGH",
        "matched": True,
        "reason": REPAIRS[4716]["reason"],
    },
    {
        "example_id": 4717,
        "textbook_no": 4,
        "confidence": "HIGH",
        "matched": True,
        "reason": REPAIRS[4717]["reason"],
    },
    {
        "example_id": 4718,
        "textbook_no": 5,
        "confidence": "HIGH",
        "matched": True,
        "reason": REPAIRS[4718]["reason"],
    },
    {
        "example_id": 4719,
        "textbook_no": 6,
        "confidence": "HIGH",
        "matched": True,
        "reason": REPAIRS[4719]["reason"],
    },
    {
        "example_id": 4720,
        "textbook_no": 7,
        "confidence": "HIGH",
        "matched": True,
        "reason": REPAIRS[4720]["reason"],
    },
]


def _has_abcd(text: str) -> bool:
    t = text or ""
    return all(f"({lab})" in t or f"（{lab}）" in t for lab in "ABCD")


def main() -> None:
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row

    backup_rows = []
    for eid in REPAIRS:
        row = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone()
        if not row:
            raise SystemExit(f"missing row {eid}")
        backup_rows.append(dict(row))
    BACKUP.write_text(json.dumps(backup_rows, ensure_ascii=False, indent=2), encoding="utf-8")

    repair_results = []
    for eid, spec in REPAIRS.items():
        before = dict(conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone())
        conn.execute(
            """
            UPDATE textbook_examples
            SET problem_text = ?, correct_answer = ?, detailed_solution = ?
            WHERE id = ?
            """,
            (spec["problem_text"], spec["correct_answer"], spec["detailed_solution"], eid),
        )
        after = dict(conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone())
        q = after["problem_text"] or ""
        repair_results.append(
            {
                "example_id": eid,
                "matched_textbook_no": spec["textbook_no"],
                "fields_changed": ["problem_text", "correct_answer", "detailed_solution"],
                "question_complete": "YES" if "則" in q or "係數" in q or "f\\left" in q or "乘積" in q else "NO",
                "choices_complete": "YES" if _has_abcd(q) else "NO",
                "answer_confirmed": "YES" if after.get("correct_answer") in {"A", "B", "C", "D"} else "NO",
                "before": {
                    "problem_text": before.get("problem_text"),
                    "correct_answer": before.get("correct_answer"),
                    "detailed_solution": before.get("detailed_solution"),
                },
                "after": {
                    "problem_text": after.get("problem_text"),
                    "correct_answer": after.get("correct_answer"),
                    "detailed_solution": after.get("detailed_solution"),
                },
                "status": "REPAIRED",
            }
        )
    conn.commit()

    recovered = [
        r["example_id"]
        for r in repair_results
        if r["choices_complete"] == "YES" and r["answer_confirmed"] == "YES"
    ]

    report = {
        "matching": MATCHING,
        "q1_note": "自我評量第1題在 production DB 的 3-1 Polynomial skill 中找不到對應 example（incomplete 9 筆亦無）；未新增列。",
        "backup_path": str(BACKUP.relative_to(ROOT)),
        "repairs": repair_results,
        "RECOVERED_SOURCE_IDS": recovered,
        "still_incomplete": [4618, 4629, 4628],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("BACKUP", BACKUP)
    print("RECOVERED", recovered)
    for r in repair_results:
        print(
            r["example_id"],
            "Q",
            r["matched_textbook_no"],
            r["choices_complete"],
            r["answer_confirmed"],
        )


if __name__ == "__main__":
    main()
