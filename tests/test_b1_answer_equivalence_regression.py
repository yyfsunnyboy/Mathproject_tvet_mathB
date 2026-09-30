"""Regression: B1 answer equivalence through the shared checker / normalization layer.

Covers the real reported case (|x|>=4 answered as `x<=-4,x>=4`) plus positive and
negative representations per checker family, so semantic equivalence is accepted
while the deterministic correctness boundary is kept.
"""
from __future__ import annotations

import copy
import importlib
from fractions import Fraction

import pytest

from core.checkers.coordinate_pair_checker import check_coordinate_pair_answer
from core.checkers.expression_equivalence_checker import (
    check_equation_equivalence_answer,
    check_expression_equivalence_answer,
)
from core.checkers.inequality_solution_checker import (
    check_inequality_solution_answer,
    parse_numeric_endpoint,
)
from core.checkers.interval_checker import check_interval_answer, parse_interval_answer
from core.checkers.line_label_checker import check_line_label_answer
from core.checkers.math_input_normalization import latex_to_plain, parse_exact_number
from core.checkers.multi_part_answer_checker import _check_numeric_equivalent
from core.checkers.solution_set_checker import check_solution_set_answer
from core.gencode.answer_payload import grade_numeric_contract_answer, parse_single_numeric

ABS_CANONICAL = "(-∞,-4] ∪ [4,∞)"


# --------------------------------------------------------------------------- shared layer


@pytest.mark.parametrize(
    ("raw", "plain"),
    [
        (r"(-\infty, -4] \cup [4, \infty)", "(-∞, -4] ∪ [4, ∞)"),
        (r"x \le -4 \text{ 或 } x \geq 4", "x ≤ -4 或 x ≥ 4"),
        (r"\frac{22}{7}", "((22)/(7))"),
        (r"-\dfrac{5}{3}", "-((5)/(3))"),
        ("x²-3x+2", "x^(2)-3x+2"),
        (r"x^{2}-3x+2", "x^(2)-3x+2"),
        ("L₁", "L_1"),
        (r"\left(6,-2\right)", "(6,-2)"),
        (r"x \in \mathbb{R}", "x ∈ ℝ"),
        ("（２，３）", "(2,3)"),
    ],
)
def test_latex_to_plain(raw: str, plain: str) -> None:
    assert latex_to_plain(raw) == plain


def test_latex_in_does_not_eat_infty() -> None:
    assert "∈fty" not in latex_to_plain(r"x \in (-\infty, 3)")
    assert latex_to_plain(r"x \in (-\infty, 3)") == "x ∈ (-∞, 3)"


@pytest.mark.parametrize(
    ("raw", "value"),
    [
        ("22/7", Fraction(22, 7)),
        (r"\frac{22}{7}", Fraction(22, 7)),
        ("3.5", Fraction(7, 2)),
        ("7/2", Fraction(7, 2)),
        ("2/-3", Fraction(-2, 3)),
        (r"-\frac{2}{3}", Fraction(-2, 3)),
        (r"\frac{-2}{3}", Fraction(-2, 3)),
        ("((−5)/(3))", Fraction(-5, 3)),
    ],
)
def test_parse_exact_number_accepts_rational_forms(raw: str, value: Fraction) -> None:
    assert parse_exact_number(raw) == value


@pytest.mark.parametrize("raw", ["1+2", "x", "1/0", "", "2x", "sqrt(2)"])
def test_parse_exact_number_rejects_non_literals(raw: str) -> None:
    assert parse_exact_number(raw) is None


@pytest.mark.parametrize("token", [r"-\infty", r"\infty", "+∞", "-∞", r"\frac{22}{7}", r"-\frac{5}{3}"])
def test_numeric_endpoint_parser_handles_latex_tokens(token: str) -> None:
    assert parse_numeric_endpoint(token) is not None


def test_numeric_endpoint_parser_never_accepts_variables() -> None:
    assert parse_numeric_endpoint("x") is None
    assert parse_numeric_endpoint("2x") is None


# --------------------------------------------------------------------------- interval / inequality


@pytest.mark.parametrize(
    "answer",
    [
        "x<=-4,x>=4",
        "x <= -4 or x >= 4",
        "x≤-4 或 x≥4",
        "(-∞,-4]∪[4,∞)",
        "(-inf,-4] U [4,inf)",
        r"(-\infty,-4]\cup[4,\infty)",
        r"(-\infty, -4] \cup [4, +\infty)",
        r"x \le -4 \text{ 或 } x \ge 4",
        "(-∞,-4],[4,∞)",
        r"\{x \mid x\le -4 \text{ or } x\ge 4\}",
        "x ∈ (-∞,-4] ∪ [4,∞)",
    ],
)
def test_case_a_union_answers_accepted(answer: str) -> None:
    assert check_inequality_solution_answer(answer, ABS_CANONICAL) is True
    assert check_interval_answer(answer, ABS_CANONICAL) is True


@pytest.mark.parametrize(
    "answer",
    [
        "x<-4,x>4",  # open endpoints
        "(-∞,-4)∪(4,∞)",
        "-4<=x<=4",  # AND instead of OR
        "x<=-4 且 x>=4",  # empty intersection
        "x<=-4",  # missing branch
        "x>=4",
        "x<=4 或 x>=-4",
    ],
)
def test_case_a_wrong_answers_rejected(answer: str) -> None:
    assert check_inequality_solution_answer(answer, ABS_CANONICAL) is False
    assert check_interval_answer(answer, ABS_CANONICAL) is False


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("-1<x<=5", True),
        ("x>-1 且 x<=5", True),
        ("x>-1, x<=5", True),
        ("5>=x>-1", True),
        (r"-1 < x \le 5", True),
        ("-1<=x<=5", False),
        ("(-1,5)", False),
        ("x>-1 或 x<=5", False),
        ("-1<x<5", False),
    ],
)
def test_bounded_interval_and_vs_or(answer: str, expected: bool) -> None:
    assert check_inequality_solution_answer(answer, "(-1,5]") is expected


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        (r"x<-\frac{5}{3} 或 x>-\frac{11}{9}", True),
        (r"(-\infty,\frac{-5}{3})\cup(\frac{-11}{9},\infty)", True),
        (r"x<-\dfrac{5}{3}, x>-\dfrac{11}{9}", True),
        ("x<-5/3 或 x>-11/9", True),
        (r"x\le-\frac{5}{3} 或 x>-\frac{11}{9}", False),
        (r"-\frac{5}{3}<x<-\frac{11}{9}", False),
    ],
)
def test_latex_fraction_endpoints(answer: str, expected: bool) -> None:
    assert check_inequality_solution_answer(answer, "(-∞,-5/3) ∪ (-11/9,∞)") is expected


def test_ambiguous_overlapping_comma_list_is_not_guessed_as_union() -> None:
    # Overlapping bracket intervals separated by a comma have no safe reading.
    assert check_inequality_solution_answer("(-∞,3],[1,∞)", "(-∞,∞)") is None


def test_interval_checker_never_raises_on_latex() -> None:
    assert isinstance(parse_interval_answer(r"(-\infty, \frac{22}{7}] \cup \{"), list)
    assert check_interval_answer(r"(-\infty, \frac{22}{7}]", "(-∞,22/7]") is True
    assert check_interval_answer("garbage \\frac{", "(-∞,22/7]") is False


# --------------------------------------------------------------------------- numeric / rational


@pytest.mark.parametrize("answer", ["22/7", r"\frac{22}{7}", r"\dfrac{22}{7}", "44/14"])
def test_rational_contract_accepts_latex_fraction(answer: str) -> None:
    res = grade_numeric_contract_answer(answer, "22/7", {"answer_type": "rational"}, checker="rational_checker")
    assert res.get("correct") is True


@pytest.mark.parametrize("answer", ["7/22", "3.14", r"\frac{22}{8}"])
def test_rational_contract_rejects_other_values(answer: str) -> None:
    res = grade_numeric_contract_answer(answer, "22/7", {"answer_type": "rational"}, checker="rational_checker")
    assert res.get("correct") is not True


def test_numeric_equivalence_decimal_and_fraction() -> None:
    assert parse_single_numeric("3.5") == (3.5, None)
    assert parse_single_numeric(r"\frac{7}{2}") == (3.5, None)
    assert parse_single_numeric(r"\frac{38}{2}", require_integer=True) == (19.0, None)
    assert parse_single_numeric(r"\frac{7}{2}", require_integer=True) == (None, "invalid")


@pytest.mark.parametrize("answer", ["-2/3", r"-\frac{2}{3}", r"\frac{-2}{3}", "-4/6", "2/-3"])
def test_multi_part_numeric_part_accepts_signed_fraction_forms(answer: str) -> None:
    assert _check_numeric_equivalent(answer, "-2/3") is True


@pytest.mark.parametrize("answer", ["2/3", "-3/2"])
def test_multi_part_numeric_part_rejects_wrong_values(answer: str) -> None:
    assert _check_numeric_equivalent(answer, "-2/3") is False


# --------------------------------------------------------------------------- expression / equation


@pytest.mark.parametrize("answer", ["(x-1)(x-2)", "(x-2)(x-1)", "x^2-3x+2", "x²-3x+2", r"x^{2}-3x+2"])
def test_expression_equivalence_forms(answer: str) -> None:
    assert check_expression_equivalence_answer(answer, "x^2-3x+2") is True


@pytest.mark.parametrize("answer", ["(x+1)(x+2)", "x^2+3x+2", "(x-1)(x+2)"])
def test_expression_equivalence_rejects_wrong(answer: str) -> None:
    assert check_expression_equivalence_answer(answer, "x^2-3x+2") is False


@pytest.mark.parametrize("answer", ["y=2x+3", "2x-y+3=0", "y-3=2x", "-2x+y-3=0"])
def test_equation_equivalence_forms(answer: str) -> None:
    assert check_equation_equivalence_answer(answer, "2x - y + 3 = 0") is True


@pytest.mark.parametrize("answer", ["y=2x-3", "y=3x+2", "y=-2x+3"])
def test_equation_equivalence_rejects_wrong(answer: str) -> None:
    assert check_equation_equivalence_answer(answer, "2x - y + 3 = 0") is False


@pytest.mark.parametrize("answer", ["1 或 21", "21 或 1", "a=1 或 a=21", "1,21"])
def test_multi_value_answer_is_unordered(answer: str) -> None:
    assert check_expression_equivalence_answer(answer, "1 或 21") is True


@pytest.mark.parametrize("answer", ["1", "1 或 20", "-1 或 -21", "1 或 21 或 5"])
def test_multi_value_answer_rejects_incomplete_or_wrong(answer: str) -> None:
    assert check_expression_equivalence_answer(answer, "1 或 21") is False


def test_assignment_list_accepts_chinese_and_joiner() -> None:
    assert check_expression_equivalence_answer("a=2 且 b=0", "a=2,b=0") is True
    assert check_expression_equivalence_answer("a=0 且 b=2", "a=2,b=0") is False


def test_assignment_list_duplicate_variable_is_not_collapsed() -> None:
    assert check_expression_equivalence_answer("x=7, x=21", "x=1, x=21") is False


# --------------------------------------------------------------------------- coordinates / sets / labels


@pytest.mark.parametrize("answer", ["(2,3)", "( 2 , 3 )", "（2，3）", r"\left(2,3\right)", r"(\frac{4}{2}, 3)"])
def test_coordinate_pair_forms(answer: str) -> None:
    assert check_coordinate_pair_answer(answer, "(2,3)") is True


def test_coordinate_pair_order_matters() -> None:
    assert check_coordinate_pair_answer("(3,2)", "(2,3)") is False


@pytest.mark.parametrize("answer", ["-13, 13", "x=±13", r"\pm 13", "13 或 -13"])
def test_solution_set_pm_forms(answer: str) -> None:
    assert check_solution_set_answer(answer, "-13, 13") is True


def test_solution_set_rejects_partial() -> None:
    assert check_solution_set_answer("13", "-13, 13") is False


@pytest.mark.parametrize("answer", ["L_1", "L1", "L₁", "$L_1$"])
def test_line_label_forms(answer: str) -> None:
    assert check_line_label_answer(answer, "L_1") is True
    assert check_line_label_answer("L_2", "L_1") is False


# --------------------------------------------------------------------------- production path


def _stored_question(skill_id: str, component_id: str, seed: int) -> dict:
    from core.gencode.answer_payload import refresh_runtime_question_session
    from core.legacy_generator_adapter import normalize_runtime_value
    from core.practice_question_store import slim_payload_for_store

    wrapper = importlib.import_module(f"skills.{skill_id}")
    data = normalize_runtime_value(wrapper.generate(level=1, seed=seed, component_id=component_id))
    if "answer" in data and "correct_answer" not in data:
        data["correct_answer"] = data["answer"]
    session = refresh_runtime_question_session(dict(data), skill_id=skill_id)
    return slim_payload_for_store(session, skill_id=skill_id, question_uid="regression")


def _with_canonical(stored: dict, canonical: str) -> dict:
    stored = copy.deepcopy(stored)
    stored["correct_answer"] = canonical
    stored["answer"] = canonical
    ac = stored.get("answer_contract") or {}
    ac["semantic_answer"] = canonical
    if "canonical_answer" in ac:
        ac["canonical_answer"] = canonical
    stored["answer_contract"] = ac
    return stored


def _grade(stored: dict, skill_id: str, answer: str) -> dict:
    from core.gencode.answer_grading import grade_answer_for_current_question
    from core.gencode.answer_payload import refresh_runtime_question_session

    current = refresh_runtime_question_session(dict(stored), skill_id=skill_id)
    return grade_answer_for_current_question(answer, current, skill_id)


ABS_SKILL = "vh_數學B1_AbsoluteValueInequality"


@pytest.fixture(scope="module")
def abs_question() -> dict:
    return _with_canonical(_stored_question(ABS_SKILL, "src_4409", 4409), ABS_CANONICAL)


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("x<=-4,x>=4", True),
        (r"(-\infty,-4]\cup[4,\infty)", True),
        ("x≤-4 或 x≥4", True),
        ("-4<=x<=4", False),
        ("x<-4,x>4", False),
    ],
)
def test_case_a_production_grading_path(abs_question: dict, answer: str, expected: bool) -> None:
    result = _grade(abs_question, ABS_SKILL, answer)
    assert result.get("correct") is expected
    assert not result.get("system_error")


def test_case_a_handwriting_path_does_not_crash(abs_question: dict) -> None:
    from core.handwriting_ai_check import HandwritingCheckContext, build_handwriting_check_response

    ac = abs_question.get("answer_contract") or {}
    ctx = HandwritingCheckContext(
        question_uid="regression",
        skill_id=ABS_SKILL,
        question_text=str(abs_question.get("question_text") or ""),
        problem_type_id=str(abs_question.get("problem_type_id") or ""),
        presentation_mode=str(abs_question.get("presentation_mode") or ""),
        answer_type=str(abs_question.get("answer_type") or ac.get("answer_type") or ""),
        correct_answer=abs_question.get("correct_answer"),
        semantic_answer=ac.get("semantic_answer"),
        answer_contract=ac,
        checker=str(abs_question.get("checker") or ac.get("checker") or ""),
        equivalence=str(abs_question.get("equivalence") or ac.get("answer_equivalence") or ""),
        choices=list(abs_question.get("choices") or []),
        rubric="",
    )
    ink = "data:image/png;base64," + "iVBORw0KGgo" + "A" * 64
    for recognized, expected in [
        ("x<=-4,x>=4", True),
        (r"(-\infty,-4] \cup [4,\infty)", True),
        (r"x \le -4 \text{ 或 } x \ge 4", True),
        ("-4<=x<=4", False),
    ]:
        resp = build_handwriting_check_response(
            image_base64=ink,
            ctx=ctx,
            ai_result={"mode": "final_answer_only", "recognized_answer": recognized, "confidence": 0.95},
        )
        assert resp.get("final_answer_correct") is expected, recognized


def test_closed_bracket_value_list_is_not_hijacked_as_interval() -> None:
    skill = "vh_數學B1_DistanceBetweenTwoPointsInPlane"
    stored = _with_canonical(_stored_question(skill, "src_4419", 4419), "[-9, 3]")
    for answer in ["-9, 3", "3, -9", "k=-9 或 k=3"]:
        assert _grade(stored, skill, answer).get("correct") is True, answer
    for answer in ["-9≤k≤3", "-9<=x<=3", "-9<k<3", "-9", "(-9,3)"]:
        assert _grade(stored, skill, answer).get("correct") is not True, answer
