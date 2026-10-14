from fractions import Fraction

import pytest

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.checkers.repeating_decimal_checker import (
    canonical_form,
    check_decimal_expansion_answer,
    format_decimal_expansion,
    parse_decimal_expansion,
)
from core.gencode.checker_registry import CHECKER_CAPABILITIES, validate_answer_contract_capability


def _ok(student, expected, **contract):
    return check_decimal_expansion_answer(student, expected, answer_contract=contract)


@pytest.mark.parametrize(
    "fraction, expected",
    [
        (Fraction(1, 2), "0.5"),
        (Fraction(3, 8), "0.375"),
        (Fraction(1, 3), "0.(3)"),
        (Fraction(1, 6), "0.1(6)"),
        (Fraction(9, 22), "0.4(09)"),
        (Fraction(1, 37), "0.(027)"),
        (Fraction(-1, 6), "-0.1(6)"),
    ],
)
def test_expected_notation_parses_to_exact_fraction(fraction, expected):
    parsed = parse_decimal_expansion(expected)
    assert parsed is not None
    assert parsed.value == fraction
    assert isinstance(parsed.value, Fraction)
    assert format_decimal_expansion(canonical_form(parsed)) == expected


@pytest.mark.parametrize(
    "student, expected",
    [
        ("0.5", "0.5"),
        ("0.50", "0.5"),
        ("0.375", "0.375"),
        ("0.(3)", "0.(3)"),
        ("0.\\overline{3}", "0.(3)"),
        ("0.1(6)", "0.1(6)"),
        ("0.1\\overline{6}", "0.1(6)"),
        ("0.4(09)", "0.4(09)"),
        ("0.4\\overline{09}", "0.4(09)"),
        ("$0.4\\overline{09}$", "0.4(09)"),
        ("0. {\\overline{ 09 }}", "0.(09)"),
        ("0.(027)", "0.(027)"),
        ("0.\\overline{027}", "0.(027)"),
        ("-0.1(6)", "-0.1(6)"),
        ("\u22120.1\\overline{6}", "-0.1(6)"),
        ("0.(142857)", "0.(142857)"),
    ],
)
def test_correct_decimal_expansions_accepted(student, expected):
    assert _ok(student, expected)["correct"] is True


def test_parenthesis_and_overline_are_equivalent_both_directions():
    assert _ok("0.\\overline{3}", "0.(3)")["correct"]
    assert _ok("0.(3)", "0.\\overline{3}")["correct"]
    assert _ok("0.4\\overline{09}", "0.4(09)")["correct"]
    assert _ok("0.4(09)", "0.4\\overline{09}")["correct"]


@pytest.mark.parametrize(
    "student, expected, reason",
    [
        ("0.(4)", "0.4(09)", "value_mismatch"),
        ("0.4(90)", "0.4(09)", "value_mismatch"),
        ("0.(16)", "0.1(6)", "value_mismatch"),
        ("0.(6)", "0.1(6)", "value_mismatch"),
        ("0.(27)", "0.(027)", "value_mismatch"),
        ("0.1(6)", "-0.1(6)", "value_mismatch"),
        ("0.3", "0.(3)", "value_mismatch"),
        ("0.1818", "0.(18)", "value_mismatch"),
        ("0.1667", "0.1(6)", "value_mismatch"),
        ("0.333333", "0.(3)", "value_mismatch"),
        ("0.1818...", "0.(18)", "unparseable_decimal_expansion"),
        ("0.1818\u2026", "0.(18)", "unparseable_decimal_expansion"),
        ("1/3", "0.(3)", "decimal_expansion_required"),
        ("\\frac{1}{6}", "0.1(6)", "decimal_expansion_required"),
        ("9/22", "0.4(09)", "decimal_expansion_required"),
        ("1/2", "0.5", "decimal_expansion_required"),
        ("", "0.5", "unparseable_decimal_expansion"),
    ],
)
def test_wrong_answers_rejected(student, expected, reason):
    result = _ok(student, expected)
    assert result["correct"] is False
    assert result["reason"] == reason


@pytest.mark.parametrize(
    "student, expected",
    [
        ("0.(33)", "0.(3)"),
        ("0.3(3)", "0.(3)"),
        ("0.1(66)", "0.1(6)"),
        ("0.40(90)", "0.4(09)"),
        ("0.4(9)", "0.5"),
        ("0.5(0)", "0.5"),
    ],
)
def test_noncanonical_repetend_rejected_by_default(student, expected):
    result = _ok(student, expected)
    assert result["correct"] is False
    assert result["reason"] == "noncanonical_repetend"
    assert _ok(student, expected, allow_noncanonical_repetend=True)["correct"] is True


def test_no_float_equality_for_near_values():
    # 0.3333333333333333 == 1/3 as a float; exact arithmetic must still reject it.
    assert float(Fraction(3333333333333333, 10**16)) == 1 / 3
    assert _ok("0.3333333333333333", "0.(3)")["correct"] is False


def test_unparseable_expected_answer_is_system_error():
    result = _ok("0.5", "1/2")
    assert result["correct"] is False
    assert result["system_error"] is True


def test_multi_part_dispatches_repeating_decimal_parts():
    contract = {
        "answer_type": "multi_part",
        "checker": "multi_part_answer_checker",
        "equivalence_type": "multi_part_answer",
        "parts": [
            {"key": "part_1", "checker": "repeating_decimal_checker", "equivalence_type": "decimal_expansion_exact", "expected_answer": "0.275"},
            {"key": "part_2", "checker": "repeating_decimal_checker", "equivalence_type": "decimal_expansion_exact", "expected_answer": "0.(18)"},
        ],
    }
    good = check_multi_part_answer({"part_1": "0.275", "part_2": "0.\\overline{18}"}, None, answer_contract=contract)
    assert good["overall_correct"] is True
    fraction = check_multi_part_answer({"part_1": "11/40", "part_2": "0.(18)"}, None, answer_contract=contract)
    assert fraction["overall_correct"] is False
    assert fraction["failed_parts"] == ["part_1"]
    wrong_cycle = check_multi_part_answer({"part_1": "0.275", "part_2": "0.(81)"}, None, answer_contract=contract)
    assert wrong_cycle["failed_parts"] == ["part_2"]


def test_checker_registered():
    cap = CHECKER_CAPABILITIES["repeating_decimal_checker"]
    assert cap["runtime_available"] is True
    assert cap["module"] == "core.checkers.repeating_decimal_checker"
    status = validate_answer_contract_capability(
        {"checker": "repeating_decimal_checker", "answer_type": "decimal_expansion", "equivalence_type": "decimal_expansion_exact"}
    )
    assert status["checker_capability_status"] == "ok"
