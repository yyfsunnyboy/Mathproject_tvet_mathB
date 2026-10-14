from __future__ import annotations

import importlib

import pytest

from core.domain.absolute_value_domain import build_absolute_value_matrix
from core.gencode.absolute_value_latex import (
    format_abs_inequality_op,
    format_linear_abs_expr,
    format_x_minus_center,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

SKILL_MODULE = "skills.vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning"
PT_INTERVAL = "absolute_value_inequality_linear_expression_basic"


def _interval_payload(center: int) -> dict:
    matrix = build_absolute_value_matrix(
        seed=0,
        line_type=PT_INTERVAL,
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={"a": 1, "b": -center, "c": 2, "op": "<="},
    )
    return convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="expression",
        problem_type_id=PT_INTERVAL,
        domain_operation=PT_INTERVAL,
    )


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
    payload = _interval_payload(-2)
    qt = str(payload.get("question_text", ""))
    assert r"\left|x+2\right|" in qt.replace(" ", "")
    assert r"\le" in qt
    assert "-(-" not in qt
    assert "<=" not in qt
    assert payload.get("answer") == "[-4,0]"
    assert payload.get("correct_answer") == "[-4,0]"
    assert "-(-" not in str(payload.get("explanation", ""))


def test_interval_problem_center_3() -> None:
    payload = _interval_payload(3)
    qt = str(payload.get("question_text", ""))
    assert r"\left|x-3\right|" in qt.replace(" ", "")
    assert r"\le" in qt
    assert payload.get("answer") == "[1,5]"


def test_interval_problem_center_0() -> None:
    payload = _interval_payload(0)
    qt = str(payload.get("question_text", ""))
    assert r"\left|x\right|" in qt.replace(" ", "")
    assert "x-0" not in qt
    assert "x+0" not in qt
    assert payload.get("answer") == "[-2,2]"


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
