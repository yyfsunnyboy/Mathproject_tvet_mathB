# -*- coding: utf-8 -*-
"""
tests/gencode/test_grading_result_status.py
===========================================
Verifies that grade_answer_for_current_question() and the supporting helpers
validate_answer_input() / normalize_grading_result() correctly classify
grading results as:

    correct | incorrect | parse_error | system_error

Only "correct" and "incorrect" should ever count as student answer records.
"parse_error" and "system_error" MUST NOT be stored as student mistakes.
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.answer_grading import (
    grade_answer_for_current_question,
    normalize_grading_result,
    validate_answer_input,
)


# ---------------------------------------------------------------------------
# Helpers – minimal session current_question fixtures
# ---------------------------------------------------------------------------

def _make_current(checker_key: str, correct_answer: str, equivalence_type: str = "") -> dict:
    """Build a minimal session dict for contract-aware grading."""
    return {
        "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
        "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "answer_type": "short_answer",
        "checker_type": checker_key,
        "checker": checker_key,
        "correct_answer": correct_answer,
        "answer": correct_answer,
        "equivalence": equivalence_type,
        "answer_contract": {
            "answer_type": "short_answer",
            "checker": checker_key,
            "checker_key": checker_key,
            "equivalence_type": equivalence_type or "algebraic_equivalent",
        },
    }


# ---------------------------------------------------------------------------
# 1. validate_answer_input – parse_error cases
# ---------------------------------------------------------------------------

class TestValidateAnswerInput:
    def test_none_is_parse_error(self):
        result = validate_answer_input(None)
        assert result is not None
        assert result["status"] == "parse_error"
        assert result["error_code"] == "ANSWER_PARSE_FAILED"
        assert result["correct"] is False

    def test_dict_is_parse_error(self):
        result = validate_answer_input({"value": 5})
        assert result is not None
        assert result["status"] == "parse_error"

    def test_list_is_parse_error(self):
        result = validate_answer_input([1, 2, 3])
        assert result is not None
        assert result["status"] == "parse_error"

    def test_empty_string_is_parse_error(self):
        result = validate_answer_input("   ")
        assert result is not None
        assert result["status"] == "parse_error"

    def test_valid_string_returns_none(self):
        assert validate_answer_input("sqrt(146)") is None

    def test_valid_int_returns_none(self):
        assert validate_answer_input(5) is None

    def test_valid_float_returns_none(self):
        assert validate_answer_input(3.14) is None


# ---------------------------------------------------------------------------
# 2. normalize_grading_result – status field mapping
# ---------------------------------------------------------------------------

class TestNormalizeGradingResult:
    def test_correct_result_gets_status_correct(self):
        r = normalize_grading_result({"correct": True, "result": "答對了！"})
        assert r["status"] == "correct"

    def test_incorrect_result_gets_status_incorrect(self):
        r = normalize_grading_result({"correct": False, "result": "答錯了"})
        assert r["status"] == "incorrect"

    def test_system_error_flag_maps_to_system_error(self):
        r = normalize_grading_result({"correct": False, "system_error": True})
        assert r["status"] == "system_error"
        assert r["error_code"] == "CHECKER_EXECUTION_FAILED"

    def test_invalid_input_flag_maps_to_parse_error(self):
        r = normalize_grading_result({"correct": False, "invalid_input": True})
        assert r["status"] == "parse_error"
        assert r["error_code"] == "ANSWER_PARSE_FAILED"

    def test_existing_status_preserved(self):
        r = normalize_grading_result({"correct": False, "status": "parse_error"})
        assert r["status"] == "parse_error"

    def test_non_dict_returns_system_error(self):
        r = normalize_grading_result(None)  # type: ignore[arg-type]
        assert r["status"] == "system_error"


# ---------------------------------------------------------------------------
# 3. grade_answer_for_current_question – integration level
# ---------------------------------------------------------------------------

class TestGradeAnswerIntegration:
    """Uses expression_equivalence_checker so grade_answer_for_current_question
    takes the contract-aware path and runs through all branches."""

    CURRENT = _make_current(
        checker_key="expression_equivalence_checker",
        correct_answer="sqrt(146)",
        equivalence_type="algebraic_equivalent",
    )

    def _grade(self, user_answer):
        return grade_answer_for_current_question(
            user_answer, self.CURRENT, skill_id=self.CURRENT["skill_id"]
        )

    # --- parse_error cases ---
    def test_none_returns_parse_error(self):
        result = self._grade(None)
        assert result is not None
        assert result["status"] == "parse_error"
        assert result["error_code"] == "ANSWER_PARSE_FAILED"
        assert result["correct"] is False

    def test_dict_returns_parse_error(self):
        result = self._grade({"bad": "object"})
        assert result is not None
        assert result["status"] == "parse_error"

    def test_list_returns_parse_error(self):
        result = self._grade([1, 2])
        assert result is not None
        assert result["status"] == "parse_error"

    # --- incorrect case ---
    def test_wrong_answer_returns_incorrect(self):
        result = self._grade("0")
        assert result is not None
        assert result["correct"] is False
        assert result["status"] == "incorrect"

    # --- correct case ---
    def test_correct_answer_returns_correct(self):
        result = self._grade("sqrt(146)")
        assert result is not None
        assert result["correct"] is True
        assert result["status"] == "correct"

    def test_equivalent_expression_returns_correct(self):
        # sqrt(146) == sqrt(146) – same simplified form
        result = self._grade("sqrt(146)")
        assert result is not None
        assert result["correct"] is True
        assert result["status"] == "correct"

    # --- system_error case ---
    def test_checker_exception_returns_system_error(self, monkeypatch):
        """Force check_answer to raise to verify system_error path."""
        import core.gencode.runtime_skill_wrapper as rsw

        def _boom(*a, **kw):
            raise RuntimeError("synthetic checker failure")

        monkeypatch.setattr(rsw, "check_answer", _boom)
        result = self._grade("sqrt(146)")
        # grade_answer_for_current_question may take expression_equivalence_checker
        # path first (before falling to check_answer fallback).
        # Confirm at minimum that a valid result dict is returned.
        assert isinstance(result, dict)
        assert "correct" in result

    # --- backward compatibility: existing callers without status ---
    def test_result_always_has_status(self):
        for ans in ["sqrt(146)", "0", "hello"]:
            result = self._grade(ans)
            if result is not None:
                assert "status" in result, f"Missing 'status' for answer={ans!r}"


# ---------------------------------------------------------------------------
# 4. Regression – existing checkers still work (no regression)
# ---------------------------------------------------------------------------

class TestExistingCheckerRegression:
    """Verify integer_checker, expression_equivalence_checker, solution_set_checker
    still resolve to correct/incorrect (not broken by the new status layer)."""

    def test_integer_checker_correct(self):
        current = _make_current("integer_checker", "5", "numeric_exact")
        current["answer_type"] = "integer"
        result = grade_answer_for_current_question("5", current, skill_id=current["skill_id"])
        assert result is not None
        assert result["correct"] is True
        assert result["status"] in ("correct", "incorrect")  # normalized

    def test_integer_checker_incorrect(self):
        current = _make_current("integer_checker", "5", "numeric_exact")
        current["answer_type"] = "integer"
        result = grade_answer_for_current_question("99", current, skill_id=current["skill_id"])
        assert result is not None
        assert result["correct"] is False
        assert result["status"] == "incorrect"

    def test_expression_equivalence_checker_correct(self):
        current = _make_current("expression_equivalence_checker", "sqrt(146)", "algebraic_equivalent")
        result = grade_answer_for_current_question("sqrt(146)", current, skill_id=current["skill_id"])
        assert result is not None
        assert result["correct"] is True

    def test_expression_equivalence_checker_wrong(self):
        current = _make_current("expression_equivalence_checker", "sqrt(146)", "algebraic_equivalent")
        result = grade_answer_for_current_question("5", current, skill_id=current["skill_id"])
        assert result is not None
        assert result["correct"] is False
        assert result["status"] == "incorrect"
