from fractions import Fraction

import pytest

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.checkers.rational_between_bounds_checker import check_rational_between_bounds_answer
from core.checkers.simplest_fraction_checker import check_simplest_fraction_answer, parse_fraction_form
from core.gencode.answer_payload import grade_numeric_contract_answer
from core.gencode.checker_registry import (
    CHECKER_CAPABILITIES,
    select_checker_from_answer_contract,
    validate_answer_contract_capability,
)
from core.gencode.runtime_skill_wrapper import check_answer


def _frac(student, expected):
    return check_simplest_fraction_answer(student, expected)


# --- simplest fraction ------------------------------------------------------

@pytest.mark.parametrize(
    "student, expected",
    [
        ("7/25", "7/25"),
        ("\\frac{7}{25}", "7/25"),
        ("\\dfrac{7}{25}", "7/25"),
        ("$\\frac{7}{25}$", "7/25"),
        (" 7 / 25 ", "7/25"),
        ("32/99", "32/99"),
        ("\\frac{32}{99}", "32/99"),
        ("131/90", "131/90"),
        ("-7/25", "-7/25"),
        ("\\frac{-7}{25}", "-7/25"),
        ("-\\frac{7}{25}", "-7/25"),
        ("\u22127/25", "-7/25"),
        ("0", "0"),
        ("3", "3"),
        ("3/1", "3"),
    ],
)
def test_simplest_fraction_accepted(student, expected):
    assert _frac(student, expected)["correct"] is True


@pytest.mark.parametrize(
    "student, expected, reason",
    [
        ("28/100", "7/25", "not_simplest"),
        ("14/50", "7/25", "not_simplest"),
        ("\\frac{14}{50}", "7/25", "not_simplest"),
        ("64/198", "32/99", "not_simplest"),
        ("0/5", "0", "not_simplest"),
        ("-7/-25", "7/25", "denominator_not_positive"),
        ("7/-25", "-7/25", "denominator_not_positive"),
        ("0.28", "7/25", "fraction_form_required"),
        ("0.280", "7/25", "fraction_form_required"),
        ("0.(32)", "32/99", "fraction_form_required"),
        ("0.\\overline{32}", "32/99", "fraction_form_required"),
        ("1.4(5)", "131/90", "fraction_form_required"),
        ("-0.28", "-7/25", "fraction_form_required"),
        ("7/26", "7/25", "value_mismatch"),
        ("7/25", "-7/25", "value_mismatch"),
        ("-\\frac{-7}{25}", "7/25", "fraction_form_required"),
        ("1", "7/25", "value_mismatch"),
        ("7/0", "7/25", "unparseable_fraction"),
        ("1 31/90", "131/90", "fraction_form_required"),
        ("x/25", "7/25", "unparseable_fraction"),
        ("", "7/25", "unparseable_fraction"),
    ],
)
def test_simplest_fraction_rejected(student, expected, reason):
    result = _frac(student, expected)
    assert result["correct"] is False
    assert result["reason"] == reason


def test_fraction_form_parser_is_exact():
    form = parse_fraction_form("-\\frac{7}{25}")
    assert (form.numerator, form.denominator) == (-7, 25)
    assert isinstance(form.value, Fraction)
    assert parse_fraction_form("0.28") is None
    assert parse_fraction_form(True) is None


def test_unparseable_expected_is_system_error():
    assert _frac("7/25", "0.(32)")["system_error"] is True


def test_multi_part_dispatches_simplest_fraction_parts():
    contract = {
        "answer_type": "multi_part",
        "checker": "multi_part_answer_checker",
        "parts": [
            {"key": "part_1", "checker": "simplest_fraction_checker", "equivalence_type": "simplest_fraction_exact", "expected_answer": "7/25"},
            {"key": "part_2", "checker": "simplest_fraction_checker", "equivalence_type": "simplest_fraction_exact", "expected_answer": "32/99"},
            {"key": "part_3", "checker": "simplest_fraction_checker", "equivalence_type": "simplest_fraction_exact", "expected_answer": "131/90"},
        ],
    }
    good = {"part_1": "\\frac{7}{25}", "part_2": "32/99", "part_3": "131/90"}
    assert check_multi_part_answer(good, None, answer_contract=contract)["overall_correct"] is True
    reducible = dict(good, part_1="28/100")
    assert check_multi_part_answer(reducible, None, answer_contract=contract)["failed_parts"] == ["part_1"]
    decimal = dict(good, part_2="0.(32)")
    assert check_multi_part_answer(decimal, None, answer_contract=contract)["failed_parts"] == ["part_2"]


# --- strictly between bounds --------------------------------------------------

BOUNDS = {"checker": "rational_between_bounds_checker", "equivalence_type": "strict_between_bounds",
          "answer_type": "short_answer", "lower": "3/2", "upper": "5/3"}


@pytest.mark.parametrize("student", ["19/12", "8/5", "\\frac{8}{5}", "1.6", "1.55", "31/20", "1.5(9)", "1.\\overline{54}"])
def test_strictly_inside_accepted(student):
    assert check_rational_between_bounds_answer(student, answer_contract=BOUNDS)["correct"] is True


@pytest.mark.parametrize(
    "student, reason",
    [
        ("3/2", "outside_bounds"),
        ("1.5", "outside_bounds"),
        ("5/3", "outside_bounds"),
        ("1.(6)", "outside_bounds"),
        ("10/6", "outside_bounds"),
        ("7/5", "outside_bounds"),
        ("2", "outside_bounds"),
        ("-8/5", "outside_bounds"),
        ("sqrt(2)", "unparseable_rational"),
        ("1.6...", "unparseable_rational"),
        ("8/5+0", "unparseable_rational"),
        ("", "unparseable_rational"),
        ("abc", "unparseable_rational"),
    ],
)
def test_boundary_outside_and_malformed_rejected(student, reason):
    result = check_rational_between_bounds_answer(student, answer_contract=BOUNDS)
    assert result["correct"] is False
    assert result["reason"] == reason


def test_fraction_required_form_rejects_decimal():
    contract = dict(BOUNDS, required_form="fraction")
    assert check_rational_between_bounds_answer("8/5", answer_contract=contract)["correct"] is True
    assert check_rational_between_bounds_answer("16/10", answer_contract=contract)["correct"] is True
    assert check_rational_between_bounds_answer("1.6", answer_contract=contract)["correct"] is False


def test_exact_near_boundary_without_float():
    # 1.6666666666666667 is 5/3 as a float but strictly below 5/3 exactly.
    assert float(Fraction("1.6666666666666667")) == float(Fraction(5, 3))
    assert check_rational_between_bounds_answer("1.6666666666666667", answer_contract=BOUNDS)["correct"] is False
    assert check_rational_between_bounds_answer("1.6666666666666666", answer_contract=BOUNDS)["correct"] is True


def test_invalid_bounds_contract_is_system_error():
    assert check_rational_between_bounds_answer("8/5", answer_contract={"lower": "5/3", "upper": "3/2"})["system_error"]
    assert check_rational_between_bounds_answer("8/5", answer_contract={})["system_error"]


def test_runtime_check_answer_uses_predicate_not_canonical_example():
    payload = {"answer_contract": dict(BOUNDS), "correct_answer": "19/12", "answer_type": "short_answer"}
    assert check_answer("8/5", "19/12", payload=payload) is True
    assert check_answer("1.6", "19/12", payload=payload) is True
    assert check_answer("19/12", "19/12", payload=payload) is True
    assert check_answer("5/3", "19/12", payload=payload) is False


# --- registry / existing behaviour -------------------------------------------

def test_new_checkers_registered_without_changing_fallback_selection():
    for key in ("simplest_fraction_checker", "rational_between_bounds_checker"):
        assert CHECKER_CAPABILITIES[key]["runtime_available"] is True
    assert validate_answer_contract_capability(BOUNDS)["checker_capability_status"] == "ok"
    assert validate_answer_contract_capability(
        {"checker": "simplest_fraction_checker", "answer_type": "fraction", "equivalence_type": "simplest_fraction_exact"}
    )["checker_capability_status"] == "ok"
    assert select_checker_from_answer_contract({"answer_type": "fraction"})[0] == "rational_checker"
    assert select_checker_from_answer_contract({"answer_type": "rational"})[0] == "rational_checker"
    assert select_checker_from_answer_contract({"answer_type": "short_answer"})[0] == "expression_equivalence_checker"


def test_existing_fraction_checker_still_accepts_equivalent_fractions():
    assert grade_numeric_contract_answer("28/100", "7/25", {"answer_type": "fraction"}, checker="fraction_checker")["correct"]
    assert check_multi_part_answer(
        {"a": "28/100"}, None,
        answer_contract={"parts": [{"key": "a", "checker": "fraction_checker", "expected_answer": "7/25"}]},
    )["overall_correct"] is True
