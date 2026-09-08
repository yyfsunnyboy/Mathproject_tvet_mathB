# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.runtime_skill_wrapper import check_answer
from core.checkers.multi_part_answer_checker import check_multi_part_answer

print("=== textbook FactorTheorem ===")
conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
conn.row_factory = sqlite3.Row
rows = conn.execute(
    """
    SELECT id, source_section, problem_type, substr(problem_text,1,400) AS q,
           substr(correct_answer,1,200) AS ans, substr(detailed_solution,1,200) AS sol
    FROM textbook_examples
    WHERE skill_id = 'vh_數學B1_FactorTheorem'
    ORDER BY id
    """
).fetchall()
print("COUNT", len(rows))
for r in rows:
    q = (r["q"] or "").replace("\n", " ")
    print("-" * 40)
    print("id", r["id"], "sec", r["source_section"], "type", r["problem_type"])
    print("Q", q[:300])
    print("A", (r["ans"] or "")[:180])
conn.close()

print("\n=== convert seed 677 ===")
matrix = build_polynomial_matrix(seed=677, domain_operation="factor_theorem_root_factor", constraints={})
payload = convert_domain_matrix_to_question_payload(
    matrix,
    presentation_mode="short_answer",
    answer_type="expression",
    problem_type_id="factor_theorem_root_factor",
    domain_operation="factor_theorem_root_factor",
    seed=677,
)
keep = [
    "answer_type", "checker", "checker_key", "equivalence", "equivalence_type",
    "answer", "correct_answer", "display_answer", "semantic_answer",
    "presentation_mode", "interaction_type", "question_text",
]
slim = {k: payload.get(k) for k in keep}
slim["answer_contract"] = payload.get("answer_contract")
slim["subquestions"] = payload.get("subquestions")
print(json.dumps(slim, ensure_ascii=False, indent=2, default=str)[:4000])

print("\n=== checker tests seed 677 ===")
user_ok = {"part_1": "x-3", "part_2": "x-3"}
user_w1 = {"part_1": "x+3", "part_2": "x-3"}
user_w2 = {"part_1": "x-3", "part_2": "x+3"}
for name, ua in [("correct", user_ok), ("wrong1", user_w1), ("wrong2", user_w2)]:
    mp = check_multi_part_answer(
        ua, payload.get("answer"),
        answer_contract=payload.get("answer_contract"),
        payload=payload,
    )
    wrapped = check_answer(ua, payload.get("answer"), payload=payload)
    print(name, "mp.overall", mp.get("overall_correct"), "reason", mp.get("failed_parts"), "per", mp.get("per_part_results"), "check_answer", wrapped)

print("\n=== wrapper generate seed 677 no component ===")
spec = importlib.util.spec_from_file_location("ft", ROOT / "skills" / "vh_數學B1_FactorTheorem.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
# try many seeds via wrapper looking for the stem
for seed in range(0, 400):
    pl = mod.generate(seed=seed)
    q = str(pl.get("question_text") or "")
    if "一次因式" in q and "整除" in q:
        print("WRAPPER HIT", "seed", seed, "cid", pl.get("component_id"), "AT", pl.get("answer_type"))
        print("Q", q[:180])
        print("A", pl.get("answer"))
        print("CK", pl.get("checker"), pl.get("checker_key"))
        print("AC.parts", (pl.get("answer_contract") or {}).get("parts"))
        print("AC.type", (pl.get("answer_contract") or {}).get("answer_type"))
        break
else:
    print("NO WRAPPER HIT in 400 seeds")

print("\n=== src_4650 contract sample ===")
path = ROOT / "agent_skills_v3" / "vh_數學B1_FactorTheorem" / "components" / "src_4650" / "generate.py"
spec2 = importlib.util.spec_from_file_location("g4650", path)
m2 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(m2)
pl = m2.generate(seed=0, component_id="src_4650")
print("AT", pl.get("answer_type"), "CK", pl.get("checker"))
print("A", pl.get("answer"))
print("AC", json.dumps(pl.get("answer_contract"), ensure_ascii=False, default=str)[:1200])
print("subq", pl.get("subquestions"))
ok = check_answer(pl.get("answer"), pl.get("answer"), payload=pl)
print("self-check", ok)
