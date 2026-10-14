# -*- coding: utf-8 -*-
"""B1 Chapter 3 published-skill smoke: import / generate / check without V2."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = ROOT / "skills"

# Published B1 Chapter 3 polynomial / rational skills (V3 thin facades).
B1_CH3_SKILLS = [
    "vh_數學B1_PolynomialBasicConcepts",
    "vh_數學B1_PolynomialArithmeticOperations",
    "vh_數學B1_PolynomialEquality",
    "vh_數學B1_PolynomialFactoring",
    "vh_數學B1_RemainderTheorem",
    "vh_數學B1_FactorTheorem",
    "vh_數學B1_RationalExpressionArithmeticOperations",
    "vh_數學B1_RationalEquation",
]


def _load_skill_module(skill_id: str):
    path = SKILLS_DIR / f"{skill_id}.py"
    assert path.is_file(), f"missing published skill facade: {path}"
    spec = importlib.util.spec_from_file_location(f"b1_smoke_{skill_id}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("skill_id", B1_CH3_SKILLS)
def test_b1_ch3_published_skill_runtime_smoke(skill_id: str):
    import core.code_generator as cg

    assert not hasattr(cg, "auto_generate_skill_code")

    module = _load_skill_module(skill_id)
    assert callable(getattr(module, "generate", None)), skill_id
    assert callable(getattr(module, "check", None)), skill_id

    payload = module.generate(level=1, seed=42)
    assert isinstance(payload, dict), skill_id
    assert payload.get("question") or payload.get("question_text") or payload.get("problem_text"), payload

    correct = (
        payload.get("correct_answer")
        or payload.get("answer")
        or (payload.get("metadata") or {}).get("correct_answer")
    )
    # Checker must accept the generated correct answer (or bool/dict contract).
    result = module.check(correct, correct, payload)
    if isinstance(result, dict):
        assert result.get("correct") is True or result.get("is_correct") is True or result.get("ok") is True, result
    else:
        assert result is True or result == correct
