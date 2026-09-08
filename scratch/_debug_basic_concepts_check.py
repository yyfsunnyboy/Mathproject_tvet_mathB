# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.gencode.runtime_skill_wrapper import check_answer

import importlib.util
p = Path("skills/vh_數學B1_PolynomialBasicConcepts.py")
spec = importlib.util.spec_from_file_location("bc", p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

for seed in (3000, 3002, 3003, 3006):
    pl = mod.generate(seed=seed)
    ans = pl.get("answer")
    ok = check_answer(ans, ans, payload=pl)
    ac = pl.get("answer_contract") or {}
    print("=" * 40, seed, "ok", ok)
    print("answer_type", pl.get("answer_type"), "checker", pl.get("checker"), ac.get("checker"))
    print("answer", ans)
    print("contract", {k: ac.get(k) for k in ("answer_type", "checker", "equivalence_type", "parts", "required_form", "problem_type_id")})
    print("q", str(pl.get("question_text") or "")[:120])
