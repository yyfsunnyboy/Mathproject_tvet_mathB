# -*- coding: utf-8 -*-
"""Phase A–E: HIGH-confidence B1 3-2 self-assessment Q8–Q15 textbook repair.

DB-only. No gencode / component / publish / domain / commit.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "scratch" / f"_b1_3_2_db_repair_backup_{STAMP}.json"
MAPPING = ROOT / "scratch" / "_b1_3_2_mapping_table.json"
REPORT = ROOT / "scratch" / "_b1_3_2_db_repair_report.json"

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

# HIGH only. problem_text keeps existing LaTeX; only complete missing stem/choices.
REPAIRS = {
    4721: {
        "textbook_no": 8,
        "correct_answer": "C",
        "semantic_answer": "3",
        "problem_text": (
            r"設$f\left( x \right)={{x}^{101}}+98{{x}^{99}}+3{{x}^{2}}+99$，"
            r"則以x + 1除$f\left( x \right)$之餘式為 (A) −3 (B) −4 (C) 3 (D) −5。"
        ),
    },
    4722: {
        "textbook_no": 9,
        "correct_answer": "D",
        "semantic_answer": "2",
        "problem_text": (
            r"設$f\left( x \right)=2{{x}^{3}}+2{{x}^{2}}-4x+a$除以x − 1的餘式為2，"
            r"則a之值為 (A) 5 (B) 4 (C) 3 (D) 2。"
        ),
    },
    4707: {
        "textbook_no": 10,
        "correct_answer": "C",
        "semantic_answer": "7",
        "problem_text": (
            r"設$f\left( x \right)={{x}^{5}}-6{{x}^{4}}-4{{x}^{3}}-25{{x}^{2}}+30x-7$，"
            r"則$f\left( 7 \right)=$ (A) 9 (B) 8 (C) 7 (D) 6。"
        ),
    },
    4708: {
        "textbook_no": 11,
        "correct_answer": "B",
        "semantic_answer": "4",
        "problem_text": (
            r"設a、b為實數，已知多項式$f\left( x \right)=2{{x}^{3}}-{{x}^{2}}-ax+b$"
            r"除以x − 1之餘式為−3，且除以x + 1之餘式為3，則a − b之值為 "
            r"(A) 3 (B) 4 (C) 5 (D) 6。"
        ),
    },
    4709: {
        "textbook_no": 12,
        "correct_answer": "A",
        "semantic_answer": "-4",
        "problem_text": (
            r"設兩多項式$f\left( x \right)$和$g\left( x \right)$除以x + 5所得的餘式分別為2和−2，"
            r"則$f\left( x \right)\times g\left( x \right)$除以x + 5所得的餘式為 "
            r"(A) −4 (B) −2 (C) −1 (D) 0。"
        ),
    },
    4710: {
        "textbook_no": 13,
        "correct_answer": "D",
        "semantic_answer": "4",
        "problem_text": (
            r"設x − 1為$f\left( x \right)=2{{x}^{3}}-k{{x}^{2}}+7x-5$之因式，"
            r"則k = (A) 1 (B) 2 (C) 3 (D) 4。"
        ),
    },
    4711: {
        "textbook_no": 14,
        "correct_answer": "D",
        "semantic_answer": "2",
        "problem_text": (
            r"若多項式$f\left( x \right)=a{{x}^{2}}\left( x+3 \right)+5x\left( x+3 \right)+2\left( x+3 \right)$"
            r"被x + 2除盡，則a = (A) −2 (B) −1 (C) 1 (D) 2。"
        ),
    },
    4712: {
        "textbook_no": 15,
        "correct_answer": "B",
        "semantic_answer": "-1",
        "problem_text": (
            r"若${{x}^{2}}-3x+2$是$a{{x}^{3}}+3{{x}^{2}}+bx-2$的因式，"
            r"則a + b之值為 (A)$-\frac{4}{3}$ (B) −1 (C)$-\frac{1}{3}$ (D) 0。"
        ),
    },
}

EXPECTED_SKILL = {
    4721: "vh_數學B1_RemainderTheorem",
    4722: "vh_數學B1_RemainderTheorem",
    4707: "vh_數學B1_RemainderTheorem",
    4708: "vh_數學B1_RemainderTheorem",
    4709: "vh_數學B1_RemainderTheorem",
    4710: "vh_數學B1_FactorTheorem",
    4711: "vh_數學B1_FactorTheorem",
    4712: "vh_數學B1_FactorTheorem",
}


def _has_abcd(text: str) -> bool:
    t = (text or "").replace("（", "(").replace("）", ")")
    return all(f"({lab})" in t for lab in "ABCD")


def _summarize(row: dict) -> dict:
    return {
        "example_id": row.get("id"),
        "skill_id": row.get("skill_id"),
        "source_description": row.get("source_description"),
        "problem_type": row.get("problem_type"),
        "problem_text": row.get("problem_text"),
        "correct_answer": row.get("correct_answer"),
        "source_section": row.get("source_section"),
        "source_paragraph": row.get("source_paragraph"),
    }


def main() -> None:
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row

    scope_rows = conn.execute(
        """
        SELECT id, skill_id, source_description, problem_type, source_paragraph
        FROM textbook_examples
        WHERE source_volume LIKE '%B1%' AND source_section LIKE '3-2%'
        ORDER BY id
        """
    ).fetchall()
    scope = [dict(r) for r in scope_rows]

    mapping = []
    for eid, spec in REPAIRS.items():
        row = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone()
        if row is None:
            mapping.append(
                {
                    "textbook_question": spec["textbook_no"],
                    "example_id": eid,
                    "skill_id": None,
                    "current_db_summary": "MISSING_ROW",
                    "match_confidence": "NONE",
                    "reason": "row not in textbook_examples",
                    "allowed": False,
                }
            )
            continue
        d = dict(row)
        expected_skill = EXPECTED_SKILL[eid]
        conflict = []
        if d["skill_id"] != expected_skill:
            conflict.append(f"skill_id={d['skill_id']} expected={expected_skill}")
        if str(d.get("source_section") or "").find("3-2") < 0:
            conflict.append(f"section={d.get('source_section')}")
        desc = str(d.get("source_description") or "")
        qno = spec["textbook_no"]
        if f"題{qno}" not in desc and f"題 {qno}" not in desc:
            conflict.append(f"source_description={desc} not 題{qno}")
        confidence = "HIGH" if not conflict else "CONFLICT"
        mapping.append(
            {
                "textbook_question": qno,
                "example_id": eid,
                "skill_id": d["skill_id"],
                "current_db_summary": _summarize(d),
                "match_confidence": confidence,
                "reason": (
                    f"source_description={desc}; stem/source aligns with 自我評量第{qno}題"
                    if not conflict
                    else "; ".join(conflict)
                ),
                "allowed": not conflict,
            }
        )

    MAPPING.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    print("MAPPING_WRITTEN", MAPPING)
    for m in mapping:
        print(
            f"Q{m['textbook_question']} id={m['example_id']} {m['match_confidence']} allowed={m['allowed']}"
        )

    allowed_ids = [m["example_id"] for m in mapping if m["allowed"]]
    blocked = [m for m in mapping if not m["allowed"]]
    if blocked:
        print("BLOCKED", [(m["textbook_question"], m["reason"]) for m in blocked])

    backup_rows = []
    for eid in allowed_ids:
        row = dict(conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone())
        backup_rows.append(
            {
                "example_id": row["id"],
                "problem_text": row.get("problem_text"),
                "choices": None,
                "correct_answer": row.get("correct_answer"),
                "source_description": row.get("source_description"),
                "skill_id": row.get("skill_id"),
                "problem_type_id": None,
                "problem_type": row.get("problem_type"),
                "source_section": row.get("source_section"),
                "source_paragraph": row.get("source_paragraph"),
            }
        )
    BACKUP.write_text(json.dumps(backup_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print("BACKUP", BACKUP, "n=", len(backup_rows))

    repairs = []
    for eid in allowed_ids:
        spec = REPAIRS[eid]
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
            raise SystemExit(f"locked_fields_changed:{eid}:{locked_changed}")
        changed = [
            k
            for k in ("problem_text", "correct_answer")
            if before.get(k) != after.get(k)
        ]
        q = after["problem_text"] or ""
        repairs.append(
            {
                "example_id": eid,
                "textbook_no": spec["textbook_no"],
                "fields_changed": changed,
                "before": {
                    "problem_text": before.get("problem_text"),
                    "correct_answer": before.get("correct_answer"),
                },
                "after": {
                    "problem_text": after.get("problem_text"),
                    "correct_answer": after.get("correct_answer"),
                },
                "question_complete": "YES" if ("則" in q or "若" in q or "設" in q) else "NO",
                "choices_complete": "YES" if _has_abcd(q) else "NO",
                "answer_confirmed": "YES" if after.get("correct_answer") in {"A", "B", "C", "D"} else "NO",
                "stored_label": after.get("correct_answer"),
                "semantic_answer": spec["semantic_answer"],
                "skill_id_unchanged": before["skill_id"] == after["skill_id"],
                "problem_type_unchanged": before["problem_type"] == after["problem_type"],
                "status": "REPAIRED",
            }
        )
    conn.commit()

    verify = []
    for eid in allowed_ids:
        after = dict(conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone())
        spec = REPAIRS[eid]
        q = after["problem_text"] or ""
        ok = (
            _has_abcd(q)
            and after.get("correct_answer") == spec["correct_answer"]
            and after.get("skill_id") == EXPECTED_SKILL[eid]
            and after.get("problem_type") == "self_assessment"
        )
        verify.append(
            {
                "example_id": eid,
                "stored_label": after.get("correct_answer"),
                "semantic_answer": spec["semantic_answer"],
                "verified": "YES" if ok else "NO",
                "choices_complete": "YES" if _has_abcd(q) else "NO",
                "skill_id": after.get("skill_id"),
                "source_description": after.get("source_description"),
            }
        )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope_count": len(scope),
        "scope": scope,
        "mapping": mapping,
        "backup_path": str(BACKUP.relative_to(ROOT)),
        "repairs": repairs,
        "verify": verify,
        "not_found": [],
        "blocked": blocked,
        "safety": {
            "skill_id_changed": "NO",
            "problem_type_changed": "NO",
            "classification_changed": "NO",
            "taxonomy_changed": "NO",
            "gencode_executed": "NO",
            "publish_executed": "NO",
        },
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("REPORT", REPORT)
    for r in repairs:
        print(r["example_id"], "Q", r["textbook_no"], r["fields_changed"], r["stored_label"], r["semantic_answer"])


if __name__ == "__main__":
    main()
