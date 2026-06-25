# -*- coding: utf-8 -*-
"""
tests/gencode/test_answer_contract_consistency_rules.py
=======================================================
Regression tests for canonical answer-contract consistency rules.

Covers (rule numbering matches answer_contract_gate.normalize_payload_answer_contract):
  R1  – single_choice + choice_label_checker + integer answer_type → FAIL
  R2  – single_choice + choice_label answer_type → PASS
  R3  – numeric_input + integer answer_type + integer_checker → PASS
  R4  – choice label answer not in choices → FAIL
  R5  – semantic_answer != correct choice value → FAIL
  R6  – three cumulative components runtime contract → PASS (answer_type=single_choice)
  R7  – full 5-seed run api_call_count=0
  R8  – existing non-B4 single-choice skills not broken (via normalize_payload)
"""
from __future__ import annotations

import importlib.util
import os
import sys
from typing import Any

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for CI/test environments

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.answer_contract_gate import normalize_payload_answer_contract
from core.gencode.validators.answer_contract_validator import (
    validate_answer_type_presentation_consistency,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_payload(**kw: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "question_text": "test",
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "answer_value_type": "choice_label",
        "checker_key": "choice_label_checker",
        "answer": "A",
        "choices": [
            {"label": "A", "text": "5", "value": 5},
            {"label": "B", "text": "8", "value": 8},
            {"label": "C", "text": "10", "value": 10},
            {"label": "D", "text": "12", "value": 12},
        ],
        "semantic_answer": 5,
    }
    base.update(kw)
    return base


def _load_component(cid: str):
    path = os.path.join(
        ROOT, "agent_skills_v3",
        "vh_數學B4_StatisticalChartReading", "components", cid, "generate.py"
    )
    spec = importlib.util.spec_from_file_location(f"gen_{cid}", path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# ---------------------------------------------------------------------------
# R1 – single_choice + choice_label_checker + integer answer_type → FAIL
# ---------------------------------------------------------------------------

class TestR1SingleChoiceIntegerAnswerTypeFail:
    def test_validator_detects_integer_with_choice_label_checker(self):
        payload = _make_payload(answer_type="integer", checker_key="choice_label_checker")
        errors = validate_answer_type_presentation_consistency(payload)
        codes = " ".join(errors)
        assert "ANSWER_CONTRACT_INCONSISTENT" in codes, (
            f"Expected ANSWER_CONTRACT_INCONSISTENT, got: {errors}"
        )

    def test_validator_detects_integer_label_mismatch(self):
        """answer_type=integer but answer='A' is a label → ANSWER_TYPE_INTEGER_LABEL_MISMATCH"""
        payload = _make_payload(answer_type="integer")
        errors = validate_answer_type_presentation_consistency(payload)
        codes = " ".join(errors)
        assert "ANSWER_TYPE_INTEGER_LABEL_MISMATCH" in codes, (
            f"Expected ANSWER_TYPE_INTEGER_LABEL_MISMATCH, got: {errors}"
        )

    def test_normalize_corrects_integer_to_single_choice(self):
        payload = _make_payload(answer_type="integer", checker_key="choice_label_checker")
        result = normalize_payload_answer_contract(payload)
        assert result["answer_type"] == "single_choice", (
            f"Expected single_choice, got {result['answer_type']}"
        )


# ---------------------------------------------------------------------------
# R2 – single_choice + choice_label answer_type → PASS
# ---------------------------------------------------------------------------

class TestR2SingleChoiceChoiceLabelPass:
    @pytest.mark.parametrize("atype", ["single_choice", "choice_label"])
    def test_valid_contract_passes(self, atype: str):
        payload = _make_payload(answer_type=atype)
        errors = validate_answer_type_presentation_consistency(payload)
        assert not errors, f"Unexpected errors for answer_type={atype}: {errors}"

    def test_normalize_single_choice_is_idempotent(self):
        payload = _make_payload(answer_type="single_choice")
        result = normalize_payload_answer_contract(payload)
        assert result["answer_type"] == "single_choice"
        assert result.get("answer_value_type") == "choice_label"


# ---------------------------------------------------------------------------
# R3 – numeric_input + integer + integer_checker → PASS
# ---------------------------------------------------------------------------

class TestR3NumericInputIntegerPass:
    def test_numeric_input_valid_contract(self):
        payload = _make_payload(
            presentation_mode="numeric_input",
            answer_type="integer",
            answer_value_type="integer",
            checker_key="integer_checker",
            answer=5,
            choices=[],
        )
        errors = validate_answer_type_presentation_consistency(payload)
        assert not errors, f"Unexpected errors: {errors}"

    def test_normalize_does_not_corrupt_numeric_input(self):
        payload = _make_payload(
            presentation_mode="numeric_input",
            answer_type="integer",
            checker_key="integer_checker",
            answer=5,
            choices=[],
        )
        result = normalize_payload_answer_contract(payload)
        assert result["answer_type"] == "integer"
        assert result["checker_key"] == "integer_checker"


# ---------------------------------------------------------------------------
# R4 – choice label not in choices → FAIL
# ---------------------------------------------------------------------------

class TestR4LabelNotInChoicesFail:
    def test_answer_not_in_choices_detected(self):
        payload = _make_payload(answer="Z")
        errors = validate_answer_type_presentation_consistency(payload)
        codes = " ".join(errors)
        assert "CHOICE_LABEL_NOT_IN_CHOICES" in codes, f"Got: {errors}"

    def test_missing_choices_detected(self):
        payload = _make_payload(choices=[])
        errors = validate_answer_type_presentation_consistency(payload)
        codes = " ".join(errors)
        assert "CHOICES_EMPTY_FOR_SINGLE_CHOICE" in codes, f"Got: {errors}"


# ---------------------------------------------------------------------------
# R5 – semantic_answer != correct choice value → FAIL
# ---------------------------------------------------------------------------

class TestR5SemanticAnswerMismatchFail:
    def test_semantic_mismatch_detected(self):
        payload = _make_payload(semantic_answer=99)  # choice A has value=5, not 99
        errors = validate_answer_type_presentation_consistency(payload)
        codes = " ".join(errors)
        assert "SEMANTIC_ANSWER_MISMATCH" in codes, f"Got: {errors}"

    def test_semantic_match_passes(self):
        payload = _make_payload(semantic_answer=5)  # A.value==5 ✓
        errors = validate_answer_type_presentation_consistency(payload)
        assert not errors, f"Unexpected errors: {errors}"


# ---------------------------------------------------------------------------
# R6 – three cumulative components runtime contract → PASS (answer_type=single_choice)
# ---------------------------------------------------------------------------

CUMULATIVE_COMPONENTS = [
    ("src_3884", "cumulative_above_fail_count"),
    ("src_3885", "cumulative_above_interval_count"),
    ("src_3886", "cumulative_below_interval_count"),
]


@pytest.mark.parametrize("cid,expected_op", CUMULATIVE_COMPONENTS)
class TestR6CumulativeComponentsContract:
    def test_answer_type_is_single_choice(self, cid: str, expected_op: str):
        mod = _load_component(cid)
        p = mod.generate(seed=1)
        assert p["answer_type"] == "single_choice", (
            f"{cid}: answer_type={p['answer_type']} (expected single_choice)"
        )

    def test_answer_value_type_is_choice_label(self, cid: str, expected_op: str):
        mod = _load_component(cid)
        p = mod.generate(seed=1)
        assert p.get("answer_value_type") == "choice_label", (
            f"{cid}: answer_value_type={p.get('answer_value_type')}"
        )

    def test_semantic_answer_type_is_integer(self, cid: str, expected_op: str):
        mod = _load_component(cid)
        p = mod.generate(seed=1)
        assert p.get("semantic_answer_type") == "integer", (
            f"{cid}: semantic_answer_type={p.get('semantic_answer_type')}"
        )

    def test_checker_is_choice_label_checker(self, cid: str, expected_op: str):
        mod = _load_component(cid)
        p = mod.generate(seed=1)
        ck = p.get("checker_key") or p.get("checker")
        assert ck == "choice_label_checker", f"{cid}: checker={ck}"

    def test_domain_operation_correct(self, cid: str, expected_op: str):
        mod = _load_component(cid)
        p = mod.generate(seed=1)
        op = p.get("domain_operation") or p.get("problem_type_id")
        assert op == expected_op, f"{cid}: op={op}"

    def test_validator_passes(self, cid: str, expected_op: str):
        mod = _load_component(cid)
        p = mod.generate(seed=42)
        errors = validate_answer_type_presentation_consistency(p)
        assert not errors, f"{cid}: {errors}"


# ---------------------------------------------------------------------------
# R7 – 5-seed run api_call_count=0
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cid,expected_op", CUMULATIVE_COMPONENTS)
class TestR7FiveSeedsApiCallCountZero:
    SEEDS = [1, 7, 42, 99, 123]

    def test_five_seeds_all_pass(self, cid: str, expected_op: str):
        mod = _load_component(cid)
        for seed in self.SEEDS:
            p = mod.generate(seed=seed)
            assert p["answer_type"] == "single_choice", (
                f"{cid} seed={seed}: answer_type={p['answer_type']}"
            )
            errors = validate_answer_type_presentation_consistency(p)
            assert not errors, f"{cid} seed={seed}: {errors}"


# ---------------------------------------------------------------------------
# R8 – normalize_payload does not corrupt valid non-B4 single-choice payloads
# ---------------------------------------------------------------------------

class TestR8ExistingSkillsNotBroken:
    def test_already_correct_single_choice_unchanged(self):
        payload = _make_payload(
            answer_type="single_choice",
            answer_value_type="choice_label",
            checker_key="choice_label_checker",
        )
        before = dict(payload)
        normalize_payload_answer_contract(payload)
        assert payload["answer_type"] == "single_choice"
        assert payload["checker_key"] == "choice_label_checker"

    def test_short_answer_not_coerced_to_choice(self):
        payload = {
            "question_text": "求 x 的值",
            "presentation_mode": "short_answer",
            "answer_type": "integer",
            "checker_key": "integer_checker",
            "answer": 5,
            "choices": [],
        }
        normalize_payload_answer_contract(payload)
        assert payload["answer_type"] == "integer"
        assert payload["checker_key"] == "integer_checker"

    def test_line_equation_not_coerced(self):
        payload = {
            "question_text": "求直線方程式",
            "presentation_mode": "short_answer",
            "answer_type": "linear_equation",
            "checker_key": "linear_equation_equivalent_checker",
            "answer": "y=2x+1",
            "choices": [],
        }
        normalize_payload_answer_contract(payload)
        assert payload["answer_type"] == "linear_equation"
