# -*- coding: utf-8 -*-
"""
tests/gencode/test_phase2_phase3_canonicalized_spec_handoff.py
==============================================================
Verifies that the canonicalized answer_contract set in Phase 2 survives intact
all the way to the Phase 3 GENERATOR_SPECS — specifically that
_reinforce_canonical_answer_contract() does NOT overwrite text_short_checker
with integer_checker for typed-prefix quadratic problem_types.
"""
from __future__ import annotations

import copy
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.problem_type_canonicalizer import enrich_spec_with_canonicalization
from core.gencode.phase3_skill_codegen import build_generator_specs_for_phase3


SKILL_ID = "vh_數學B1_QuadraticFunctionGraph"

_TYPED_PREFIXES = [
    ("integer_quadratic_graph_translation_fill_blank",  "quadratic_graph_translation_fill_blank"),
    ("rational_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank"),
    ("integer_quadratic_graph_properties_choice",       "quadratic_graph_properties_choice"),
]


def _make_spec(pt_id: str, target_task: str) -> dict:
    """Minimal Phase 1 induced spec draft after enrich_spec_with_canonicalization.

    Sets source_has_choices appropriately for choice-type problem_types.
    """
    # Determine if this is a choice-type task
    is_choice_task = any(
        marker in target_task
        for marker in ("_choice", "properties_choice", "properties")
    ) and "fill_blank" not in target_task and "short_answer" not in target_task

    # For fill_blank tasks, the answer hint should be "text_short"
    is_fill_blank = "fill_blank" in target_task or "short_answer" in target_task

    spec = {
        "problem_type_id": pt_id,
        "target_task": target_task,
        "answer_contract": {
            # Simulate the raw Phase 1 induction answer_contract (prefix-derived, not yet canonical)
            "answer_type": pt_id.split("_")[0],  # "integer" or "rational"
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "source_has_choices": is_choice_task,
        },
        "generator_contract": {},
    }
    # For fill_blank types, set the answer_format_hint explicitly
    if is_fill_blank:
        spec["answer_format_hint"] = "text_short"
    return enrich_spec_with_canonicalization(spec)


def _make_phase2_usable(pt_id: str, target_task: str) -> dict:
    spec = _make_spec(pt_id, target_task)
    return {
        "problem_type_id": pt_id,
        "generator_key": f"{SKILL_ID}:{pt_id}:draft_v1",
        "generator_status": "runtime_ready_with_warning",
        "generator_readiness": "runtime_ready_with_warning",
        "usable_for_phase3": True,
        "checker_smoke_status": "passed",
        "dynamic_sampling_status": "passed",
        "blockers": [],
        "answer_contract_proposal": spec.get("answer_contract", {}),
        "problem_type_spec_draft": spec,
    }


class TestCanonicalizedSpecSurvivesReinforce:
    """_reinforce_canonical_answer_contract must NOT overwrite canonical specs."""

    @pytest.mark.parametrize("pt_id,target_task", _TYPED_PREFIXES)
    def test_enrich_then_reinforce_keeps_canonical_checker(self, pt_id: str, target_task: str) -> None:
        from core.gencode.pipeline_orchestrator import _reinforce_canonical_answer_contract
        spec = _make_spec(pt_id, target_task)
        _reinforce_canonical_answer_contract(spec, pt_id)
        ac = spec["answer_contract"]
        checker = ac.get("checker_key") or ac.get("checker")
        assert checker != "integer_checker", (
            f"[{pt_id}] _reinforce_canonical_answer_contract overwrote canonical checker with integer_checker"
        )

    def test_integer_fill_blank_checker_is_text_short(self) -> None:
        from core.gencode.pipeline_orchestrator import _reinforce_canonical_answer_contract
        spec = _make_spec("integer_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        _reinforce_canonical_answer_contract(spec, "integer_quadratic_graph_translation_fill_blank")
        ac = spec["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "text_short_checker", (
            f"Expected text_short_checker, got {ac.get('checker_key')!r}"
        )
        assert ac.get("answer_type") in {"text_short", "short_answer"}

    def test_rational_fill_blank_checker_is_text_short(self) -> None:
        from core.gencode.pipeline_orchestrator import _reinforce_canonical_answer_contract
        spec = _make_spec("rational_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        _reinforce_canonical_answer_contract(spec, "rational_quadratic_graph_translation_fill_blank")
        ac = spec["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "text_short_checker"

    def test_integer_properties_choice_checker_is_choice_label(self) -> None:
        from core.gencode.pipeline_orchestrator import _reinforce_canonical_answer_contract
        spec = _make_spec("integer_quadratic_graph_properties_choice", "quadratic_graph_properties_choice")
        _reinforce_canonical_answer_contract(spec, "integer_quadratic_graph_properties_choice")
        ac = spec["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "choice_label_checker", (
            f"Expected choice_label_checker, got {ac.get('checker_key')!r}"
        )
        assert ac.get("answer_type") == "single_choice"
        assert ac.get("equivalence_type") == "choice_label"


class TestBuildGeneratorSpecsForPhase3:
    """build_generator_specs_for_phase3 output must carry canonical contract."""

    def _run(self, pt_id: str, target_task: str) -> dict:
        usable = [_make_phase2_usable(pt_id, target_task)]
        specs_out, _ = build_generator_specs_for_phase3(SKILL_ID, usable)
        match = next((s for s in specs_out if s.get("problem_type_id") == pt_id), None)
        return match or {}

    def test_integer_fill_blank_output_has_text_short_checker(self) -> None:
        row = self._run("integer_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        assert row, "Spec row not found in output"
        assert row.get("checker_key") == "text_short_checker", (
            f"Expected text_short_checker, got {row.get('checker_key')!r}"
        )
        assert row.get("equivalence_type") == "exact_string"
        assert row.get("answer_type") in {"text_short", "short_answer", None, ""}  # may not be set

    def test_rational_fill_blank_output_has_text_short_checker(self) -> None:
        row = self._run("rational_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        assert row, "Spec row not found in output"
        assert row.get("checker_key") == "text_short_checker"

    def test_integer_properties_choice_output_has_choice_label_checker(self) -> None:
        row = self._run("integer_quadratic_graph_properties_choice", "quadratic_graph_properties_choice")
        assert row, "Spec row not found in output"
        assert row.get("checker_key") == "choice_label_checker", (
            f"Expected choice_label_checker, got {row.get('checker_key')!r}"
        )
        assert row.get("equivalence_type") == "choice_label"

    def test_integer_fill_blank_no_regression_to_integer_checker(self) -> None:
        row = self._run("integer_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        assert row.get("checker_key") != "integer_checker", (
            "integer_checker must not appear for fill_blank typed-prefix spec"
        )

    def test_output_includes_template_slot(self) -> None:
        row = self._run("integer_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        assert row.get("template_slot") == "quadratic_graph_translation_fill_blank"

    def test_output_includes_base_problem_type_id(self) -> None:
        row = self._run("integer_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        assert row.get("base_problem_type_id") == "quadratic_graph_translation_fill_blank"

    def test_generator_readiness_not_generator_not_ready(self) -> None:
        for pt_id, target_task in _TYPED_PREFIXES:
            row = self._run(pt_id, target_task)
            assert row.get("generator_readiness") != "generator_not_ready", (
                f"{pt_id}: generator_readiness must not be generator_not_ready"
            )
