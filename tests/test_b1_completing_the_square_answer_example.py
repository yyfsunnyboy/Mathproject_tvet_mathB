# -*- coding: utf-8 -*-
"""CompletingTheSquare answer example must be vertex form, not factorization."""
from __future__ import annotations

import importlib

from core.gencode.answer_format_hint import (
    VERTEX_FORM_HINT_EXAMPLE,
    answer_format_example_for_contract,
    build_answer_format_suffix,
)
from core.gencode.problem_type_spec import get_answer_contract, load_problem_type_spec

SKILL = "vh_數學B1_CompletingTheSquare"
PT = "expression_complete_square_to_vertex"
FACTOR_EXAMPLE = "(x-2)(x+3)"


def test_vertex_form_contract_uses_vertex_example_not_factorization() -> None:
    ac = get_answer_contract(
        load_problem_type_spec(SKILL, PT, prefer="auto")
    )
    assert ac.get("answer_shape") == "vertex_form_expression"
    example = answer_format_example_for_contract(ac)
    assert example == VERTEX_FORM_HINT_EXAMPLE
    assert FACTOR_EXAMPLE not in example
    suffix = build_answer_format_suffix(ac)
    assert suffix == f"（答案範例：{VERTEX_FORM_HINT_EXAMPLE}）"
    assert FACTOR_EXAMPLE not in suffix


def test_generic_expression_contract_keeps_factorization_example() -> None:
    """Factorization-style expression contracts must remain unchanged."""
    ac = {
        "answer_type": "expression",
        "answer_shape": "expression",
        "checker": "expression_checker",
        "checker_key": "expression_checker",
    }
    assert answer_format_example_for_contract(ac) == FACTOR_EXAMPLE
    assert build_answer_format_suffix(ac) == f"（答案範例：{FACTOR_EXAMPLE}）"


def test_completing_the_square_runtime_suffix_is_vertex_form() -> None:
    mod = importlib.import_module(f"skills.{SKILL}")
    seen = 0
    for seed in range(40):
        q = mod.generate(level=1, seed=seed)
        if q.get("problem_type_id") != PT:
            continue
        seen += 1
        qt = str(q.get("question_text") or "")
        assert "頂點式" in qt or "配方" in qt or "a(x" in qt
        assert FACTOR_EXAMPLE not in qt
        assert VERTEX_FORM_HINT_EXAMPLE in qt or "2(x-2)^2+3" in qt
        assert "（答案範例：" in qt
        # Checker accepts the canonical vertex-form answer.
        ans = q.get("correct_answer") or q.get("answer")
        assert bool(mod.check(ans, ans, question_payload=q)) is True
    assert seen >= 3
