# -*- coding: utf-8 -*-
"""B1 3-3 source completeness audit. No classification changes."""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"

CHOICE_PARSE = re.compile(r"\(([A-D])\)\s*")
IMG = re.compile(r"如下圖|如右圖|左圖|右圖|根據下圖|根據右圖|依下圖|觀察圖形|見圖|附圖|如圖")
TABLE = re.compile(r"完成下表|依下表|根據下表|根據表格|如下表|下表")

OP_BY_SKILL = {
    "vh_數學B1_PolynomialFactoring": "polynomial_factoring",
    "vh_數學B1_RationalExpressionArithmeticOperations": "rational_expression_arithmetic",
    "vh_數學B1_RationalEquation": "rational_equation_solve",
}


def parse_choices(text: str) -> list[tuple[str, str]]:
    t = text.replace("（", "(").replace("）", ")")
    out = []
    matches = list(CHOICE_PARSE.finditer(t))
    for i, m in enumerate(matches):
        lab = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(t)
        body = t[start:end].strip().rstrip("。．.;；,，〔〕【】 ")
        body = re.sub(r"〔[^〕]*〕\s*$", "", body).strip()
        out.append((lab, body))
    seen = set()
    uniq = []
    for lab, body in out:
        if lab in seen:
            continue
        seen.add(lab)
        uniq.append((lab, body))
    return uniq


def main() -> None:
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT id, skill_id, source_description, problem_text, correct_answer,
               problem_type, source_paragraph, source_section
        FROM textbook_examples
        WHERE source_volume LIKE '%B1%' AND source_section LIKE '3-3%'
        ORDER BY id
        """
    ).fetchall()
    results = []
    for row in rows:
        eid = int(row["id"])
        text = str(row["problem_text"] or "")
        stripped = text.strip()
        choices = parse_choices(text)
        needs_choices = bool(choices) or "(A)" in text.replace("（", "(")
        choice_n = len(choices)
        labels = {a for a, _ in choices}
        bodies_ok = all(b.strip() for _, b in choices)
        choices_complete = choice_n >= 4 and bodies_ok and {"A", "B", "C", "D"} <= labels
        needs_image = bool(IMG.search(text))
        needs_table = bool(TABLE.search(text))
        has_tabular = bool(re.search(r"\\begin\{tabular\}|\\begin\{array\}|<table", text, re.I))
        dollar_n = text.count("$")
        image_data_present = needs_image and dollar_n >= 4

        if needs_choices:
            topo = "choice" if choices_complete else "choice_incomplete"
        elif re.search(r"（\s*[1-9]\s*）|\([1-9]\)|（[1-9]）", text):
            topo = "multi_part"
        else:
            topo = "short_answer_or_expression"

        op = OP_BY_SKILL.get(str(row["skill_id"]) or "", "")
        if not stripped or len(stripped) < 16 or "$" not in stripped:
            status = "SOURCE_INCOMPLETE"
            reason = "stem missing usable math"
        elif re.search(r"(周長為|之值為|為)$", stripped):
            status = "SOURCE_INCOMPLETE"
            reason = "truncated stem; missing ask/choices"
        elif needs_image and not image_data_present:
            status = "IMAGE_REQUIRED_BUT_MISSING"
            reason = "stem image cue but no usable quantitative data"
        elif needs_table and not has_tabular:
            status = "TABLE_REQUIRED_BUT_MISSING"
            reason = "table required but missing"
        elif needs_choices and not choices_complete:
            status = "CHOICES_INCOMPLETE"
            reason = f"choice markers incomplete (parsed={choice_n})"
        else:
            status = "READY_FOR_COMPONENT"
            reason = f"source stem complete; topology_obs={topo}"
            if needs_image and image_data_present:
                reason += "; figure cue ignored because polynomials are in text"

        decision = "INCLUDE" if status == "READY_FOR_COMPONENT" else "EXCLUDE"
        results.append(
            {
                "example_id": eid,
                "skill_id": row["skill_id"],
                "problem_type": row["problem_type"],
                "source_description": row["source_description"],
                "correct_answer": row["correct_answer"],
                "needs_choices": needs_choices,
                "choices_complete": choices_complete,
                "source_complete": status == "READY_FOR_COMPONENT",
                "feasibility_status": status,
                "rebuild_decision": decision,
                "reason": reason,
                "topology_observation": topo,
                "problem_type_id": op,
                "required_operation": op,
            }
        )

    out = {
        "total": len(results),
        "skills": dict(Counter(r["skill_id"] for r in results)),
        "status_counts": dict(Counter(r["feasibility_status"] for r in results)),
        "decision_counts": dict(Counter(r["rebuild_decision"] for r in results)),
        "rows": results,
    }
    path = ROOT / "scratch" / "_b1_3_3_source_feasibility.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("TOTAL", out["total"], "SKILLS", out["skills"])
    print("STATUS", out["status_counts"])
    print("DECISION", out["decision_counts"])
    for r in results:
        print(
            r["example_id"],
            r["skill_id"].split("_")[-1],
            r["feasibility_status"],
            r["rebuild_decision"],
            r["reason"][:90],
        )
    print("wrote", path)


if __name__ == "__main__":
    main()
