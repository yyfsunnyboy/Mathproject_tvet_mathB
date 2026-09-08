# -*- coding: utf-8 -*-
"""Focused recheck: src_4628 20 seeds + ArithmeticOperations 40 smoke."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.gencode.runtime_skill_wrapper import check_answer


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def verify_src_4628(n: int = 20) -> dict:
    gen = _load(
        ROOT
        / "agent_skills_v3"
        / "vh_數學B1_PolynomialArithmeticOperations"
        / "components"
        / "src_4628"
        / "generate.py",
        "gen_src_4628",
    )
    passed = failed = 0
    errors = []
    for i in range(n):
        seed = 9000 + i
        try:
            pl = gen.generate(seed=seed)
            q = str(pl.get("question_text") or "")
            choices = pl.get("choices") or []
            ans = pl.get("answer")
            if not q or "餘式" not in q or len(choices) != 4:
                failed += 1
                errors.append(f"{seed}:bad_payload")
                continue
            if not check_answer(ans, ans, payload=pl):
                failed += 1
                errors.append(f"{seed}:checker")
                continue
            pl2 = gen.generate(seed=seed)
            if pl2.get("question_text") != pl.get("question_text") or pl2.get("answer") != ans:
                failed += 1
                errors.append(f"{seed}:repro")
                continue
            passed += 1
        except Exception as exc:
            failed += 1
            errors.append(f"{seed}:exc:{exc}")
    return {"n": n, "passed": passed, "failed": failed, "errors": errors}


def smoke_arith(n: int = 40) -> dict:
    mod = _load(
        ROOT / "skills" / "vh_數學B1_PolynomialArithmeticOperations.py",
        "skill_arith",
    )
    passed = failed = 0
    hit = 0
    errors = []
    for i in range(n):
        try:
            pl = mod.generate(seed=7000 + i)
            cid = str(pl.get("component_id") or "")
            if cid == "src_4628":
                hit += 1
            if not pl.get("question_text") or pl.get("answer") is None:
                failed += 1
                errors.append(f"{i}:empty:{cid}")
                continue
            if not check_answer(pl.get("answer"), pl.get("answer"), payload=pl):
                failed += 1
                errors.append(f"{i}:checker:{cid}")
                continue
            passed += 1
        except Exception as exc:
            failed += 1
            errors.append(f"{i}:exc:{exc}")
    return {"n": n, "passed": passed, "failed": failed, "src_4628_hit": hit, "errors": errors}


if __name__ == "__main__":
    a = verify_src_4628()
    b = smoke_arith()
    print("SRC_4628", a)
    print("SMOKE", b)
    raise SystemExit(0 if a["failed"] == 0 and b["failed"] == 0 else 1)
