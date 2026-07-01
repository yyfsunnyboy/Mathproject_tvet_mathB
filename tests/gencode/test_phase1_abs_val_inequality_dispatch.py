# -*- coding: utf-8 -*-
"""Phase 1 classifier dispatch for vh_數學B1_AbsoluteValueInequality.

Verifies that run_v3_no_llm_phase1_for_example correctly delegates to
VocationalMathB1AbsoluteValueInequalityClassifier and returns a definite
problem_type_id for all 10 textbook examples instead of
PHASE1_CLASSIFICATION_UNRESOLVED.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pytest

from core.gencode.pipeline_orchestrator import (
    PHASE1_CLASSIFICATION_UNRESOLVED,
    _skill_has_python_classifier,
    run_v3_no_llm_phase1_for_example,
)

SKILL = "vh_數學B1_AbsoluteValueInequality"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_row(
    example_id: int,
    problem_text: str,
    answer: str = "",
    runtime_category: str | None = None,
) -> dict[str, Any]:
    return {
        "id": example_id,
        "skill_id": SKILL,
        "problem_text": problem_text,
        "correct_answer": answer,
        "detailed_solution": "",
        "problem_type_id": "",
        "problem_type": "",
        "runtime_category": runtime_category or "",
    }


def _phase1(row: dict[str, Any]) -> dict[str, Any]:
    return run_v3_no_llm_phase1_for_example(SKILL, row)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def production_examples() -> list[dict[str, Any]]:
    """Load all 10 textbook examples from production DB."""
    if not DB_PATH.exists():
        pytest.skip(f"Production DB not found: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM textbook_examples WHERE skill_id=? ORDER BY id",
        (SKILL,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# _skill_has_python_classifier
# ---------------------------------------------------------------------------

class TestSkillHasPythonClassifier:
    def test_absolute_value_inequality_has_classifier(self) -> None:
        assert _skill_has_python_classifier(SKILL) is True

    def test_unknown_skill_has_no_classifier(self) -> None:
        assert _skill_has_python_classifier("vh_Unknown_Skill_9999") is False


# ---------------------------------------------------------------------------
# Synthetic unit tests (no DB required)
# ---------------------------------------------------------------------------

class TestSyntheticDispatch:
    """Verify correct problem_type_id for representative synthetic rows."""

    _CASES = [
        # (description, problem_text, expected_problem_type_id, expected_mode)
        (
            "zero_center_less_than",
            "解不等式 |x| < 5",
            "absolute_value_inequality_zero_center_basic",
            "short_answer",
        ),
        (
            "zero_center_greater_than",
            "解不等式 |x| > 3",
            "absolute_value_inequality_zero_center_basic",
            "short_answer",
        ),
        (
            "shifted_le",
            "解不等式 |x - 2| <= 4",
            "absolute_value_inequality_shifted_basic",
            "short_answer",
        ),
        (
            "shifted_ge",
            "解不等式 |x + 5| >= 1",
            "absolute_value_inequality_shifted_basic",
            "short_answer",
        ),
        (
            "linear_expression_strict",
            "解不等式 |3x + 1| < 7",
            "absolute_value_inequality_linear_expression_basic",
            "short_answer",
        ),
        (
            "linear_expression_ge",
            "解不等式 |4x - 2| >= 6",
            "absolute_value_inequality_linear_expression_basic",
            "short_answer",
        ),
        (
            "integer_count_choice",
            "整數x共有多少個滿足|x|<=3的整數？(A)3 (B)5 (C)7 (D)9",
            "absolute_value_inequality_integer_solution_count_choice",
            "single_choice",
        ),
    ]

    @pytest.mark.parametrize("desc,text,expected_pt,expected_mode", _CASES, ids=[c[0] for c in _CASES])
    def test_synthetic_classification(
        self, desc: str, text: str, expected_pt: str, expected_mode: str
    ) -> None:
        row = _make_row(99901, text)
        result = _phase1(row)
        assert result.get("classification_status_code") != PHASE1_CLASSIFICATION_UNRESOLVED, (
            f"[{desc}] Got unresolved: {result.get('reason')}"
        )
        assert result.get("problem_type_id") == expected_pt, (
            f"[{desc}] Expected {expected_pt}, got {result.get('problem_type_id')}"
        )
        assert result.get("presentation_mode") == expected_mode, (
            f"[{desc}] Expected mode {expected_mode}, got {result.get('presentation_mode')}"
        )
        assert result.get("classification_source") == "python_skill_classifier"

    def test_choice_answer_contract_keys(self) -> None:
        """Integer solution count choice sets answer_type=choice and checker=choice_label_checker."""
        row = _make_row(99902, "整數x共有多少個滿足|x|<=3？(A)3 (B)5 (C)7 (D)9")
        result = _phase1(row)
        ac = result.get("answer_contract") or {}
        assert ac.get("answer_type") == "choice"
        assert ac.get("checker_key") == "choice_label_checker"

    def test_no_yaml_rulepack_bypassed(self) -> None:
        """Dispatch reaches python_skill_classifier (not phase1_rule_pack)."""
        row = _make_row(99903, "解不等式 |x| < 8")
        result = _phase1(row)
        assert result.get("classification_source") == "python_skill_classifier"

    def test_unregistered_skill_reports_not_registered_reason(self) -> None:
        """Unregistered skill (no yaml, no python) sets reason=phase1_classifier_not_registered."""
        unknown_skill = "vh_Unknown_Test_Skill_9999"
        row = {
            "id": 99999,
            "skill_id": unknown_skill,
            "problem_text": "solve something",
            "correct_answer": "42",
            "detailed_solution": "",
            "problem_type_id": "",
        }
        result = run_v3_no_llm_phase1_for_example(unknown_skill, row)
        # The result should be unresolved for an unknown skill
        assert result.get("classification_status_code") == PHASE1_CLASSIFICATION_UNRESOLVED
        assert result.get("reason") == "phase1_classifier_not_registered"

    def test_malformed_source_gives_valid_classification(self) -> None:
        """Classifier identifies malformed source text as a valid (review-flagged) classification."""
        # Simulate 4409-style source: missing operator between |x| and number
        row = _make_row(99904, "試求下列不等式之解：(1)|x|3 (2) |x| >= 4")
        result = _phase1(row)
        # Should be resolved (ok=True), not unresolved
        assert result.get("classification_status_code") != PHASE1_CLASSIFICATION_UNRESOLVED
        assert result.get("problem_type_id") == "absolute_value_inequality_malformed_source_review"
        assert result.get("classification_source") == "python_skill_classifier"


# ---------------------------------------------------------------------------
# Production DB integration tests (10 real textbook examples)
# ---------------------------------------------------------------------------

# Expected classifications derived from running the verified classifier on
# the production DB rows.
_EXPECTED_PT: dict[int, str] = {
    4400: "absolute_value_inequality_zero_center_basic",
    4402: "absolute_value_inequality_shifted_basic",
    4403: "absolute_value_inequality_shifted_basic",
    4404: "absolute_value_inequality_linear_expression_basic",
    4405: "absolute_value_inequality_linear_expression_basic",
    4406: "absolute_value_inequality_linear_expression_basic",
    4407: "absolute_value_inequality_linear_expression_basic",
    4409: "absolute_value_inequality_zero_center_basic",
    4413: "absolute_value_inequality_zero_center_basic",
    4499: "absolute_value_inequality_integer_solution_count_choice",
}

_EXPECTED_MODE: dict[int, str] = {
    **{k: "short_answer" for k in (4400, 4402, 4403, 4404, 4405, 4406, 4407, 4409, 4413)},
    4499: "single_choice",
}


class TestProductionExamples:
    def test_all_10_examples_loaded(self, production_examples: list[dict]) -> None:
        assert len(production_examples) == 10, (
            f"Expected 10 examples, got {len(production_examples)}"
        )

    def test_zero_unresolved(self, production_examples: list[dict]) -> None:
        """None of the 10 examples should return PHASE1_CLASSIFICATION_UNRESOLVED."""
        unresolved = []
        for row in production_examples:
            result = _phase1(row)
            if result.get("classification_status_code") == PHASE1_CLASSIFICATION_UNRESOLVED:
                unresolved.append((row["id"], result.get("reason")))
        assert unresolved == [], f"Unresolved examples: {unresolved}"

    def test_all_use_python_skill_classifier(self, production_examples: list[dict]) -> None:
        for row in production_examples:
            result = _phase1(row)
            assert result.get("classification_source") == "python_skill_classifier", (
                f"Example {row['id']} used {result.get('classification_source')}"
            )

    @pytest.mark.parametrize("ex_id,expected_pt", list(_EXPECTED_PT.items()))
    def test_problem_type_id(
        self,
        ex_id: int,
        expected_pt: str,
        production_examples: list[dict],
    ) -> None:
        row = next((r for r in production_examples if r["id"] == ex_id), None)
        if row is None:
            pytest.skip(f"Example {ex_id} not in production DB")
        result = _phase1(row)
        assert result.get("problem_type_id") == expected_pt, (
            f"Example {ex_id}: expected {expected_pt}, got {result.get('problem_type_id')}"
        )

    @pytest.mark.parametrize("ex_id,expected_mode", list(_EXPECTED_MODE.items()))
    def test_presentation_mode(
        self,
        ex_id: int,
        expected_mode: str,
        production_examples: list[dict],
    ) -> None:
        row = next((r for r in production_examples if r["id"] == ex_id), None)
        if row is None:
            pytest.skip(f"Example {ex_id} not in production DB")
        result = _phase1(row)
        assert result.get("presentation_mode") == expected_mode, (
            f"Example {ex_id}: expected mode {expected_mode}, got {result.get('presentation_mode')}"
        )

    def test_choice_example_answer_contract(self, production_examples: list[dict]) -> None:
        """Example 4499 (integer solution count choice) should have choice answer_type."""
        row = next((r for r in production_examples if r["id"] == 4499), None)
        if row is None:
            pytest.skip("Example 4499 not in production DB")
        result = _phase1(row)
        ac = result.get("answer_contract") or {}
        assert ac.get("answer_type") == "choice"
        assert ac.get("checker_key") == "choice_label_checker"

    def test_capabilities_populated(self, production_examples: list[dict]) -> None:
        """required_capabilities should be a non-empty list for all resolved examples."""
        for row in production_examples:
            result = _phase1(row)
            caps = result.get("required_capabilities") or []
            assert isinstance(caps, list) and len(caps) > 0, (
                f"Example {row['id']} has empty required_capabilities"
            )


# ---------------------------------------------------------------------------
# Test for vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning
# ---------------------------------------------------------------------------

class TestExpansionSkillProductionExamples:
    EXP_SKILL = "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning"

    @pytest.fixture(scope="class")
    def exp_examples(self) -> list[dict[str, Any]]:
        """Load all examples from production DB for the expansion skill."""
        if not DB_PATH.exists():
            pytest.skip(f"Production DB not found: {DB_PATH}")
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM textbook_examples WHERE skill_id=? ORDER BY id",
            (self.EXP_SKILL,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def test_load_all_examples(self, exp_examples: list[dict[str, Any]]) -> None:
        # Expected total_examples=3 (4411, 4415, 4416)
        assert len(exp_examples) == 3, f"Expected 3 examples, got {len(exp_examples)}"

    def test_examples_classification(self, exp_examples: list[dict[str, Any]]) -> None:
        for row in exp_examples:
            result = run_v3_no_llm_phase1_for_example(self.EXP_SKILL, row)
            assert result.get("classification_status_code") != PHASE1_CLASSIFICATION_UNRESOLVED, (
                f"Example {row['id']} got unresolved classification: {result.get('reason')}"
            )
            assert result.get("classification_source") == "python_skill_classifier"

            ex_id = row["id"]
            pt_id = result.get("problem_type_id")
            mode = result.get("presentation_mode")
            ac = result.get("answer_contract") or {}

            if ex_id in (4411, 4415):
                assert pt_id == "absolute_value_inequality_linear_expression_basic"
                assert mode == "short_answer"
                assert "absolute_value_inequality_linear_expression_basic" in result.get("required_capabilities", [])
            elif ex_id == 4416:
                assert pt_id == "absolute_value_inequality_interval_interpretation"
                assert mode == "single_choice"
                assert ac.get("answer_type") == "choice"
                assert ac.get("checker_key") == "choice_label_checker"
                assert "absolute_value_inequality_interval_interpretation" in result.get("required_capabilities", [])

