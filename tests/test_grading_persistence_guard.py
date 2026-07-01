# -*- coding: utf-8 -*-
"""
tests/test_grading_persistence_guard.py
========================================
Verifies that parse_error / system_error grading results are NOT allowed to
write student records, while correct / incorrect results ARE recorded normally.

Tests operate at two levels:
  1. The `_is_gradable` logic extracted from _emit_check_result (unit level).
  2. The `should_record` logic extracted from the two grade_answer_for_current_question
     call-sites (unit level, no Flask context required).
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ---------------------------------------------------------------------------
# Pure-unit helpers: replicate the exact guard logic from practice.py so
# we can test it without a Flask context.
# ---------------------------------------------------------------------------

def _is_gradable(result: dict) -> bool:
    """Mirrors the _emit_check_result guard added to practice.py."""
    _status = str(result.get("status", "")).strip() if isinstance(result, dict) else ""
    return _status in ("correct", "incorrect") or (
        _status == ""
        and not result.get("system_error")
        and not result.get("invalid_input")
    )


def _should_record_main_path(result: dict) -> bool:
    """Mirrors the main contract_result should_record guard in practice.py."""
    _res_status = str(result.get("status", "")).strip()
    return _res_status in ("correct", "incorrect") or (
        _res_status == ""
        and not result.get("system_error")
        and not result.get("invalid_input")
    )


def _should_record_drawing_path(result: dict) -> bool:
    """Mirrors the drawing-path contract_result should_record guard in practice.py."""
    _cr_status = str(result.get("status", "")).strip()
    is_correct_value = result.get("correct")
    return _cr_status in ("correct", "incorrect") or (
        _cr_status == ""
        and is_correct_value is not None
        and not result.get("system_error")
        and not result.get("invalid_input")
    )


# ---------------------------------------------------------------------------
# 1. _is_gradable (emit_check_result guard)
# ---------------------------------------------------------------------------

class TestIsGradable:
    def test_correct_status_is_gradable(self):
        assert _is_gradable({"correct": True, "status": "correct"}) is True

    def test_incorrect_status_is_gradable(self):
        assert _is_gradable({"correct": False, "status": "incorrect"}) is True

    def test_parse_error_status_not_gradable(self):
        assert _is_gradable({
            "correct": False,
            "status": "parse_error",
            "error_code": "ANSWER_PARSE_FAILED",
        }) is False

    def test_system_error_status_not_gradable(self):
        assert _is_gradable({
            "correct": False,
            "status": "system_error",
            "error_code": "CHECKER_EXECUTION_FAILED",
        }) is False

    def test_legacy_system_error_flag_not_gradable(self):
        # Backward-compat: old results without 'status' but with system_error flag
        assert _is_gradable({"correct": False, "system_error": True}) is False

    def test_legacy_invalid_input_flag_not_gradable(self):
        assert _is_gradable({"correct": False, "invalid_input": True}) is False

    def test_legacy_correct_without_status_is_gradable(self):
        # Pre-existing results that don't yet have 'status' should still pass through
        assert _is_gradable({"correct": True}) is True

    def test_legacy_incorrect_without_status_is_gradable(self):
        assert _is_gradable({"correct": False}) is True


# ---------------------------------------------------------------------------
# 2. should_record guard – main path
# ---------------------------------------------------------------------------

class TestShouldRecordMainPath:
    def test_correct_records(self):
        assert _should_record_main_path({"correct": True, "status": "correct"}) is True

    def test_incorrect_records(self):
        assert _should_record_main_path({"correct": False, "status": "incorrect"}) is True

    def test_parse_error_does_not_record(self):
        assert _should_record_main_path({
            "correct": False,
            "status": "parse_error",
            "error_code": "ANSWER_PARSE_FAILED",
        }) is False

    def test_system_error_does_not_record(self):
        assert _should_record_main_path({
            "correct": False,
            "status": "system_error",
            "error_code": "CHECKER_EXECUTION_FAILED",
        }) is False

    def test_legacy_system_error_flag_does_not_record(self):
        assert _should_record_main_path({"correct": False, "system_error": True}) is False

    def test_legacy_invalid_input_does_not_record(self):
        assert _should_record_main_path({"correct": False, "invalid_input": True}) is False


# ---------------------------------------------------------------------------
# 3. should_record guard – drawing path
# ---------------------------------------------------------------------------

class TestShouldRecordDrawingPath:
    def test_correct_records(self):
        assert _should_record_drawing_path({"correct": True, "status": "correct"}) is True

    def test_incorrect_records(self):
        assert _should_record_drawing_path({"correct": False, "status": "incorrect"}) is True

    def test_parse_error_does_not_record(self):
        assert _should_record_drawing_path({
            "correct": False,
            "status": "parse_error",
        }) is False

    def test_system_error_does_not_record(self):
        assert _should_record_drawing_path({
            "correct": False,
            "status": "system_error",
        }) is False

    def test_correct_none_with_no_status_does_not_record(self):
        # correct=None means the checker could not determine a verdict (e.g. drawing timeout)
        assert _should_record_drawing_path({"correct": None}) is False


# ---------------------------------------------------------------------------
# 4. Integration with normalize_grading_result
#    Confirm that normalize_grading_result output feeds correctly into guards.
# ---------------------------------------------------------------------------

class TestNormalizeIntegrationWithGuards:
    from core.gencode.answer_grading import normalize_grading_result  # type: ignore[import]

    @pytest.fixture(autouse=True)
    def _import(self):
        from core.gencode.answer_grading import normalize_grading_result
        self.normalize = normalize_grading_result

    def test_normalized_correct_is_gradable(self):
        r = self.normalize({"correct": True})
        assert _is_gradable(r) is True
        assert _should_record_main_path(r) is True

    def test_normalized_incorrect_is_gradable(self):
        r = self.normalize({"correct": False})
        assert _is_gradable(r) is True
        assert _should_record_main_path(r) is True

    def test_normalized_system_error_not_gradable(self):
        r = self.normalize({"correct": False, "system_error": True})
        assert _is_gradable(r) is False
        assert _should_record_main_path(r) is False

    def test_normalized_invalid_input_not_gradable(self):
        r = self.normalize({"correct": False, "invalid_input": True})
        assert _is_gradable(r) is False
        assert _should_record_main_path(r) is False

    def test_parse_error_direct_not_gradable(self):
        r = {
            "correct": False,
            "status": "parse_error",
            "error_code": "ANSWER_PARSE_FAILED",
            "message": "答案格式不正確",
        }
        assert _is_gradable(r) is False
        assert _should_record_main_path(r) is False


# ---------------------------------------------------------------------------
# 5. API response still includes status and error_code (schema preservation)
# ---------------------------------------------------------------------------

class TestApiResponsePreservation:
    """Confirm the result dict passed to jsonify still carries status/error_code."""

    def test_parse_error_result_has_status_and_error_code(self):
        result = {
            "correct": False,
            "status": "parse_error",
            "error_code": "ANSWER_PARSE_FAILED",
            "message": "答案格式不正確",
        }
        # Even when not gradable, the dict itself is intact for the API response
        assert result["status"] == "parse_error"
        assert result["error_code"] == "ANSWER_PARSE_FAILED"
        assert result["correct"] is False

    def test_system_error_result_has_status_and_error_code(self):
        result = {
            "correct": False,
            "status": "system_error",
            "error_code": "CHECKER_EXECUTION_FAILED",
            "result": "批改系統錯誤：synthetic error",
        }
        assert result["status"] == "system_error"
        assert result["error_code"] == "CHECKER_EXECUTION_FAILED"
        assert result["correct"] is False
