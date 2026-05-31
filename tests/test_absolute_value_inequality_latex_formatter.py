from __future__ import annotations

import importlib
from unittest.mock import patch

import pytest

from core.gencode.absolute_value_latex import (
    format_abs_inequality_op,
    format_linear_abs_expr,
    format_x_minus_center,
)

SKILL_MODULE = "skills.vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning"
PT_INTERVAL = "absolute_value_inequality_linear_expression_basic"


@pytest.mark.parametrize(
    ("center", "expected_inner", "expected_abs"),
    [
        (-2, "x+2", "|x+2|"),
        (3, "x-3", "|x-3|"),
        (0, "x", "|x|"),
    ],
)
def test_format_linear_abs_expr(center: int, expected_inner: str, expected_abs: str) -> None:
    assert format_x_minus_center(center) == expected_inner
    assert format_linear_abs_expr(center) == expected_abs


def test_format_abs_inequality_op_uses_latex_symbols() -> None:
    assert format_abs_inequality_op("<=") == r"\le"
    assert format_abs_inequality_op(">=") == r"\ge"
    assert format_abs_inequality_op("<") == "<"
    assert format_abs_inequality_op(">") == ">"


def test_interval_problem_center_minus_2() -> None:
    mod = importlib.import_module(SKILL_MODULE)
    with patch.object(mod.random, "randint", side_effect=[-2, 2]), patch.object(
        mod.random, "choice", return_value="<="
    ):
        payload = mod._gen_interval_problem(PT_INTERVAL)
    qt = str(payload.get("question_text", ""))
    assert "|x+2|" in qt
    assert r"\le" in qt
    assert "-(-" not in qt
    assert "<=" not in qt
    assert payload.get("answer") == "[-4, 0]"
    assert payload.get("correct_answer") == "[-4, 0]"
    assert "-(-" not in str(payload.get("explanation", ""))


def test_interval_problem_center_3() -> None:
    mod = importlib.import_module(SKILL_MODULE)
    with patch.object(mod.random, "randint", side_effect=[3, 2]), patch.object(
        mod.random, "choice", return_value="<="
    ):
        payload = mod._gen_interval_problem(PT_INTERVAL)
    qt = str(payload.get("question_text", ""))
    assert "|x-3|" in qt
    assert r"\le" in qt
    assert payload.get("answer") == "[1, 5]"


def test_interval_problem_center_0() -> None:
    mod = importlib.import_module(SKILL_MODULE)
    with patch.object(mod.random, "randint", side_effect=[0, 2]), patch.object(
        mod.random, "choice", return_value="<="
    ):
        payload = mod._gen_interval_problem(PT_INTERVAL)
    qt = str(payload.get("question_text", ""))
    assert "|x|" in qt
    assert "x-0" not in qt
    assert "x+0" not in qt
    assert payload.get("answer") == "[-2, 2]"


def test_generate_30_items_avoid_unnatural_latex() -> None:
    mod = importlib.import_module(SKILL_MODULE)
    for seed in range(30):
        payload = mod.generate(level=1, seed=seed)
        text = " ".join(
            str(payload.get(key, ""))
            for key in ("question_text", "question", "explanation")
        )
        assert "-(-" not in text
        assert "+-" not in text
        assert "<=" not in text
        assert ">=" not in text
        if "inequality" in str(payload.get("problem_type_id", "")):
            assert r"\le" in text or r"\ge" in text or "<" in text or ">" in text


def test_interval_checker_regression() -> None:
    mod = importlib.import_module(SKILL_MODULE)
    assert mod.check("[-4,0]", "[-4, 0]") is True
    assert mod.check("[-4, 0]", "[1, 5]") is False
