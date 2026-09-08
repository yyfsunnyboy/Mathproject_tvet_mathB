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

SKILL = ROOT / "agent_skills_v3" / "vh_數學B1_FactorTheorem"
KEYS = [
    "src_4646", "src_4647", "src_4648", "src_4649", "src_4650", "src_4651",
    "src_4652", "src_4653", "src_4654", "src_4655", "src_4660", "src_4661",
    "src_4662", "src_4663", "src_4710", "src_4711", "src_4712",
]


def _load(key: str):
    path = SKILL / "components" / key / "generate.py"
    spec = importlib.util.spec_from_file_location(f"gen_{key}", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


print("=== published component sweep ===")
hits = []
for key in KEYS:
    mod = _load(key)
    for seed in range(200):
        pl = mod.generate(level=1, seed=seed, component_id=key)
        q = str(pl.get("question_text") or "")
        compact = q.replace(" ", "").replace("{", "").replace("}", "")
        if "一次因式" in q and "整除" in q:
            rec = {
                "component_id": key,
                "seed": seed,
                "question": q,
                "answer_type": pl.get("answer_type"),
                "checker": pl.get("checker") or pl.get("checker_key"),
                "answer": pl.get("answer"),
                "semantic_answer": pl.get("semantic_answer"),
                "display_answer": pl.get("display_answer"),
                "answer_contract": pl.get("answer_contract"),
                "metadata_keys": list((pl.get("metadata") or {}).keys()) if isinstance(pl.get("metadata"), dict) else [],
            }
            hits.append(rec)
            print("HIT", key, "seed", seed)
            print(" Q", q[:180])
            print(" AT", rec["answer_type"], "CK", rec["checker"])
            print(" A", rec["answer"])
            print(" SA", rec["semantic_answer"])
            print(" DA", rec["display_answer"])
            print(" AC", json.dumps(rec["answer_contract"], ensure_ascii=False)[:500])
            break
        if "x^2-9" in compact or "x^{2}-9" in compact:
            print("POLY_HIT", key, seed, q[:160], "AT", pl.get("answer_type"), "A", pl.get("answer"))
print("STEM_HITS", len(hits))

print("=== domain empty-source root_to_factor locate x^2-9 ===")
exact = None
for seed in range(0, 1500):
    matrix = build_polynomial_matrix(
        seed=seed,
        domain_operation="factor_theorem_root_factor",
        constraints={},
    )
    q = str(matrix.get("question_text") or "")
    compact = q.replace(" ", "").replace("{", "").replace("}", "")
    if "一次因式" in q and ("x^2-9" in compact or "x^{2}-9" in compact) and "x=3" in compact:
        exact = {"seed": seed, "matrix": matrix, "q": q}
        print("EXACT_SEED", seed)
        print("Q", q)
        print("ANSWER", matrix.get("answer"))
        print("DIST", matrix.get("distractors"))
        break

print("=== textbook examples 3-2 FactorTheorem ===")
db = ROOT / "instance" / "kumon_math.db"
if db.is_file():
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT id, skill_id, source_kind, substr(question_text,1,240) AS q, answer_text, source_section
        FROM textbook_examples
        WHERE skill_id = 'vh_數學B1_FactorTheorem'
        ORDER BY id
        """
    ).fetchall()
    print("COUNT", len(rows))
    for r in rows:
        q = str(r["q"] or "")
        flag = ""
        if "一次因式" in q or "x^2-9" in q.replace(" ", "") or "整除" in q:
            flag = " <--- MATCH?"
        print(r["id"], r["source_kind"], r["source_section"], q[:140].replace("\n", " "), flag)
    conn.close()
else:
    print("NO_DB")
