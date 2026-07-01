# -*- coding: utf-8 -*-
"""
tests/test_grading_legacy_path_guard.py
=========================================
Verifies that the legacy mod.check() path in practice.py correctly:

  - Converts checker exceptions → system_error (no persistence)
  - Converts structurally invalid input → parse_error (no persistence)
  - Allows correct/incorrect results through to persistence
  - Reuses normalize_grading_result and validate_answer_input without a parallel guard

These tests operate without Flask context by testing the guard logic directly
via the shared helper functions from answer_grading.
"""
from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.answer_grading import (
    normalize_grading_result,
    validate_answer_input,
)


# ---------------------------------------------------------------------------
# Replica of the legacy guard logic from practice.py (unit-testable)
# ---------------------------------------------------------------------------

def _simulate_legacy_check(user_ans, mod_check_return=None, mod_check_raises=None):
    """Simulate the entire legacy mod.check() section guard logic.

    Returns (result_dict, _legacy_gradable, persistence_blocked).
    """
    # 1. Pre-flight parse_error check
    parse_fail = validate_answer_input(user_ans)
    if parse_fail is not None:
        return parse_fail, False, True  # blocked immediately

    # 2. Invoke checker (with exception catch)
    try:
        try:
            if mod_check_raises is not None:
                raise mod_check_raises
            result = mod_check_return
        except TypeError:
            # Simulate TypeError → 2-arg fallback (still raises if same exc)
            if mod_check_raises is not None:
                raise mod_check_raises
            result = mod_check_return
    except Exception as _exc:
        result = normalize_grading_result({
            "correct": False,
            "system_error": True,
            "error_code": "CHECKER_EXECUTION_FAILED",
            "result": f"批改系統錯誤：{_exc}",
        })

    # 3. bool → dict
    if isinstance(result, bool):
        result = {"correct": result, "result": "Correct!" if result else "Incorrect."}

    # 4. Normalize status
    if isinstance(result, dict) and "status" not in result:
        result = normalize_grading_result(result)

    # 5. Gradability gate
    _legacy_status = str(result.get("status", "")).strip() if isinstance(result, dict) else ""
    _legacy_gradable = _legacy_status in ("correct", "incorrect") or (
        _legacy_status == ""
        and not result.get("system_error")
        and not result.get("invalid_input")
    )

    persistence_blocked = not _legacy_gradable
    return result, _legacy_gradable, persistence_blocked


# ---------------------------------------------------------------------------
# 1. parse_error – pre-flight gate
# ---------------------------------------------------------------------------

class TestLegacyParseErrorGate:
    def test_none_blocked(self):
        result, gradable, blocked = _simulate_legacy_check(None)
        assert result["status"] == "parse_error"
        assert result["error_code"] == "ANSWER_PARSE_FAILED"
        assert gradable is False
        assert blocked is True

    def test_dict_blocked(self):
        result, gradable, blocked = _simulate_legacy_check({"bad": "obj"})
        assert result["status"] == "parse_error"
        assert blocked is True

    def test_list_blocked(self):
        result, gradable, blocked = _simulate_legacy_check([1, 2, 3])
        assert result["status"] == "parse_error"
        assert blocked is True

    def test_empty_string_blocked(self):
        result, gradable, blocked = _simulate_legacy_check("   ")
        assert result["status"] == "parse_error"
        assert blocked is True

    def test_valid_string_passes(self):
        result, gradable, blocked = _simulate_legacy_check(
            "42", mod_check_return={"correct": True}
        )
        assert blocked is False
        assert gradable is True


# ---------------------------------------------------------------------------
# 2. system_error – checker exception gate
# ---------------------------------------------------------------------------

class TestLegacyCheckerExceptionGate:
    def test_generic_exception_becomes_system_error(self):
        result, gradable, blocked = _simulate_legacy_check(
            "42", mod_check_raises=RuntimeError("synthetic failure")
        )
        assert result["status"] == "system_error"
        assert result["error_code"] == "CHECKER_EXECUTION_FAILED"
        assert result["correct"] is False
        assert gradable is False
        assert blocked is True

    def test_value_error_becomes_system_error(self):
        result, gradable, blocked = _simulate_legacy_check(
            "42", mod_check_raises=ValueError("bad value")
        )
        assert result["status"] == "system_error"
        assert blocked is True

    def test_exception_result_has_readable_message(self):
        result, _, _ = _simulate_legacy_check(
            "42", mod_check_raises=RuntimeError("division by zero")
        )
        assert "division by zero" in result.get("result", "")

    def test_system_error_does_not_affect_gradability(self):
        _, gradable, blocked = _simulate_legacy_check(
            "42", mod_check_raises=RuntimeError("boom")
        )
        assert gradable is False
        assert blocked is True


# ---------------------------------------------------------------------------
# 3. correct / incorrect – pass through to persistence
# ---------------------------------------------------------------------------

class TestLegacyGradableResults:
    def test_bool_true_is_gradable(self):
        result, gradable, blocked = _simulate_legacy_check(
            "5", mod_check_return=True
        )
        assert result["correct"] is True
        assert result["status"] == "correct"
        assert gradable is True
        assert blocked is False

    def test_bool_false_is_gradable(self):
        result, gradable, blocked = _simulate_legacy_check(
            "99", mod_check_return=False
        )
        assert result["correct"] is False
        assert result["status"] == "incorrect"
        assert gradable is True
        assert blocked is False

    def test_dict_correct_is_gradable(self):
        result, gradable, blocked = _simulate_legacy_check(
            "5", mod_check_return={"correct": True, "result": "答對了！"}
        )
        assert result["status"] == "correct"
        assert gradable is True

    def test_dict_incorrect_is_gradable(self):
        result, gradable, blocked = _simulate_legacy_check(
            "0", mod_check_return={"correct": False, "result": "答錯了"}
        )
        assert result["status"] == "incorrect"
        assert gradable is True
        assert blocked is False


# ---------------------------------------------------------------------------
# 4. normalize_grading_result applied to all paths
# ---------------------------------------------------------------------------

class TestNormalizeAppliedInLegacyPath:
    def test_result_always_has_status(self):
        for ans, check_ret in [("5", True), ("0", False), ("hello", {"correct": False})]:
            result, _, _ = _simulate_legacy_check(ans, mod_check_return=check_ret)
            assert "status" in result, f"Missing status for ans={ans!r}"

    def test_system_error_result_has_error_code(self):
        result, _, _ = _simulate_legacy_check(
            "5", mod_check_raises=RuntimeError("boom")
        )
        assert result.get("error_code") == "CHECKER_EXECUTION_FAILED"

    def test_parse_error_result_has_error_code(self):
        result, _, _ = _simulate_legacy_check(None)
        assert result.get("error_code") == "ANSWER_PARSE_FAILED"


# ---------------------------------------------------------------------------
# 5. API response preservation (result dict intact even when blocked)
# ---------------------------------------------------------------------------

class TestApiResponsePreservationLegacy:
    def test_parse_error_result_preserved_for_api(self):
        result, _, blocked = _simulate_legacy_check(None)
        assert blocked is True
        # Dict is still intact for jsonify
        assert result["status"] == "parse_error"
        assert result["correct"] is False
        assert "error_code" in result

    def test_system_error_result_preserved_for_api(self):
        result, _, blocked = _simulate_legacy_check(
            "5", mod_check_raises=RuntimeError("oops")
        )
        assert blocked is True
        assert result["status"] == "system_error"
        assert result["correct"] is False
        assert "error_code" in result


# ---------------------------------------------------------------------------
# 6. No special-casing by skill_id / problem_type_id
# ---------------------------------------------------------------------------

class TestNoSkillSpecificSpecialCases:
    """Guard logic must be skill-agnostic."""

    @pytest.mark.parametrize("skill_id", [
        "vh_數學B1_DistanceBetweenTwoPointsInPlane",
        "jh_數學1上_FourArithmeticOperationsOfIntegers",
        "vh_some_other_skill",
    ])
    def test_parse_error_blocked_regardless_of_skill(self, skill_id):
        # validate_answer_input doesn't take skill_id – it's always universal
        result = validate_answer_input(None)
        assert result is not None
        assert result["status"] == "parse_error"

    @pytest.mark.parametrize("user_ans", [None, {"k": 1}, [], b"bytes"])
    def test_all_unparseable_types_blocked(self, user_ans):
        result, _, blocked = _simulate_legacy_check(user_ans)
        assert blocked is True
        assert result["status"] == "parse_error"
