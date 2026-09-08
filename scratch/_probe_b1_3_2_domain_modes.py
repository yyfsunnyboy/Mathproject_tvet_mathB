# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.domain.polynomial_domain import build_polynomial_matrix

rows = json.loads((ROOT / "scratch/_b1_3_2_source_feasibility.json").read_text(encoding="utf-8"))["rows"]
dump = {r["example_id"]: r for r in json.loads((ROOT / "scratch/_b1_3_2_scope_dump.json").read_text(encoding="utf-8"))}

for row in rows:
    if row["rebuild_decision"] != "INCLUDE":
        continue
    eid = row["example_id"]
    src = dump[eid]["problem_text"]
    op = row["required_operation"]
    choice = row["topology_observation"] == "choice"
    try:
        matrix = build_polynomial_matrix(
            seed=7,
            domain_operation=op,
            constraints={
                "presentation_mode": "single_choice" if choice else "short_answer",
                "source_problem_text": src,
            },
        )
        q = str(matrix.get("question_text") or "")[:80]
        ans = matrix.get("answer", {})
        val = ans.get("value") if isinstance(ans, dict) else ans
        dist = matrix.get("distractors") or []
        print("OK", eid, op, "choice" if choice else "sa", "dist", len(dist), "ans", val, q)
    except Exception as exc:
        print("FAIL", eid, exc)
