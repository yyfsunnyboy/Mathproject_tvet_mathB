# -*- coding: utf-8 -*-
"""
tests/gencode/test_answer_contract_canonicalization_generic.py
==============================================================
Generic answer-contract canonicalization regression tests.

Covers:
  1. Properties tasks (vertex_form_properties, standard_to_vertex_properties)
     must NOT get integer_checker regardless of value-type prefix.
  2. Translation tasks with text answers must not get integer_checker.
  3. standard_to_vertex_properties that produces A/B/C/D must use choice_label_checker.
  4. Slot-based presentation inference overrides name-based heuristics.
  5. Phase 2 diversity sampling detects payload/spec contract mismatch.
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.problem_type_canonicalizer import (
    enrich_spec_with_canonicalization,
    infer_presentation_mode,
)
from core.gencode.template_slot_resolver import (
    SLOT_PRESENTATION_MODE,
    get_slot_primary_presentation_mode,
)


# ── Helper ────────────────────────────────────────────────────────────────────

def _make_raw_spec(pt_id: str, target_task: str = "", integer_prefix_contract: bool = True) -> dict:
    """Build a minimal pre-canonicalization spec (what Phase 1 induction produces)."""
    spec: dict = {
        "problem_type_id": pt_id,
        "target_task": target_task or pt_id,
        "answer_contract": {},
    }
    if integer_prefix_contract:
        spec["answer_contract"] = {
            "answer_type": "integer",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
        }
    return spec


# ── 1. SLOT_PRESENTATION_MODE contains correct entries ───────────────────────

class TestSlotPresentationModeMap:
    def test_properties_slots_are_single_choice(self) -> None:
        assert SLOT_PRESENTATION_MODE.get("quadratic_vertex_form_properties") == "single_choice"
        assert SLOT_PRESENTATION_MODE.get("quadratic_standard_to_vertex_properties") == "single_choice"

    def test_translation_slots_are_short_answer(self) -> None:
        assert SLOT_PRESENTATION_MODE.get("quadratic_graph_translation_fill_blank") == "short_answer"
        assert SLOT_PRESENTATION_MODE.get("quadratic_graph_translation_short_answer") == "short_answer"

    def test_choice_slots_are_single_choice(self) -> None:
        assert SLOT_PRESENTATION_MODE.get("quadratic_graph_vertex_axis_choice") == "single_choice"
        assert SLOT_PRESENTATION_MODE.get("linear_function_two_point_choice") == "single_choice"

    def test_get_slot_primary_presentation_mode_helper(self) -> None:
        assert get_slot_primary_presentation_mode("quadratic_standard_to_vertex_properties") == "single_choice"
        assert get_slot_primary_presentation_mode("quadratic_graph_translation_fill_blank") == "short_answer"
        assert get_slot_primary_presentation_mode("unknown_slot_xyz") == ""


# ── 2. infer_presentation_mode slot argument overrides name markers ───────────

class TestInferPresentationModeWithSlot:
    def test_properties_slot_gives_single_choice(self) -> None:
        mode = infer_presentation_mode(
            "quadratic_standard_to_vertex_properties",
            slot="quadratic_standard_to_vertex_properties",
        )
        assert mode == "single_choice"

    def test_vertex_form_properties_slot_gives_single_choice(self) -> None:
        mode = infer_presentation_mode(
            "quadratic_vertex_form_properties",
            slot="quadratic_vertex_form_properties",
        )
        assert mode == "single_choice"

    def test_fill_blank_slot_gives_short_answer(self) -> None:
        mode = infer_presentation_mode(
            "quadratic_graph_translation_fill_blank",
            slot="quadratic_graph_translation_fill_blank",
        )
        assert mode == "short_answer"

    def test_no_slot_falls_back_to_name_markers(self) -> None:
        # Without slot, choice marker in name wins
        mode = infer_presentation_mode("quadratic_graph_vertex_axis_choice")
        assert mode == "single_choice"


# ── 3. enrich_spec_with_canonicalization — properties tasks ──────────────────

class TestEnrichSpecPropertiesTasks:
    def test_integer_standard_to_vertex_gets_choice_label_checker(self) -> None:
        spec = _make_raw_spec("integer_quadratic_standard_to_vertex_properties", "quadratic_standard_to_vertex_properties")
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "choice_label_checker", (
            f"Expected choice_label_checker, got {ac!r}"
        )
        assert ac.get("answer_type") == "single_choice"
        assert ac.get("equivalence_type") == "choice_label"

    def test_integer_vertex_form_properties_gets_choice_label_checker(self) -> None:
        spec = _make_raw_spec("integer_quadratic_vertex_form_properties", "quadratic_vertex_form_properties")
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "choice_label_checker", (
            f"Expected choice_label_checker, got {ac!r}"
        )

    def test_rational_standard_to_vertex_gets_choice_label_checker(self) -> None:
        spec = {
            "problem_type_id": "rational_quadratic_standard_to_vertex_properties",
            "target_task": "quadratic_standard_to_vertex_properties",
            "answer_contract": {"answer_type": "rational", "checker_key": "rational_checker"},
        }
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "choice_label_checker"

    def test_properties_checker_is_never_integer_checker(self) -> None:
        """Core invariant: properties slots never use integer_checker."""
        for pt_prefix in ("integer", "rational", "numeric"):
            for base in ("quadratic_standard_to_vertex_properties", "quadratic_vertex_form_properties"):
                spec = _make_raw_spec(f"{pt_prefix}_{base}", base)
                enriched = enrich_spec_with_canonicalization(spec)
                ac = enriched["answer_contract"]
                checker = ac.get("checker_key") or ac.get("checker")
                assert checker != "integer_checker", (
                    f"{pt_prefix}_{base}: Must not get integer_checker, got {checker!r}"
                )
                assert checker != "rational_checker", (
                    f"{pt_prefix}_{base}: Must not get rational_checker for choice slot, got {checker!r}"
                )


# ── 4. enrich_spec — translation tasks still get text_short_checker ──────────

class TestEnrichSpecTranslationTasks:
    def test_integer_translation_fill_blank_gets_text_short_checker(self) -> None:
        spec = _make_raw_spec("integer_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "text_short_checker"

    def test_translation_checker_is_never_integer_checker(self) -> None:
        spec = _make_raw_spec("integer_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) != "integer_checker"


# ── 5. _reinforce_canonical_answer_contract respects properties slots ────────

class TestReinforceCanonicalAnswerContractProperties:
    def test_integer_standard_to_vertex_not_overwritten_to_integer_checker(self) -> None:
        from core.gencode.pipeline_orchestrator import _reinforce_canonical_answer_contract
        spec = _make_raw_spec("integer_quadratic_standard_to_vertex_properties", "quadratic_standard_to_vertex_properties")
        enriched = enrich_spec_with_canonicalization(spec)  # Mark as canonicalized
        _reinforce_canonical_answer_contract(enriched, "integer_quadratic_standard_to_vertex_properties")
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "choice_label_checker", (
            f"_reinforce_canonical_answer_contract overwrote to: {ac.get('checker_key')!r}"
        )


# ── 6. Phase 2 mismatch detection ────────────────────────────────────────────

class TestPayloadSpecContractMismatch:
    def test_numeric_spec_with_choice_payloads_is_blocker(self) -> None:
        from core.gencode.generator_diversity_sampling import _detect_payload_spec_contract_mismatch
        spec = {
            "problem_type_id": "integer_quadratic_standard_to_vertex_properties",
            "answer_contract": {
                "answer_type": "integer",
                "checker_key": "integer_checker",
                "equivalence_type": "numeric_exact",
            },
        }
        payloads = [
            {"answer_type": "single_choice", "answer": "A", "choices": ["A", "B", "C", "D"]},
            {"answer_type": "single_choice", "answer": "B", "choices": ["A", "B", "C", "D"]},
            {"answer_type": "single_choice", "answer": "C", "choices": ["A", "B", "C", "D"]},
            {"answer_type": "single_choice", "answer": "D", "choices": ["A", "B", "C", "D"]},
        ]
        blockers = _detect_payload_spec_contract_mismatch(spec, payloads)
        assert blockers, "Expected mismatch blocker when numeric spec but choice payloads"
        assert any("numeric" in b and "choice" in b for b in blockers)

    def test_no_mismatch_when_contracts_agree(self) -> None:
        from core.gencode.generator_diversity_sampling import _detect_payload_spec_contract_mismatch
        spec = {
            "problem_type_id": "quadratic_standard_to_vertex_properties",
            "answer_contract": {
                "answer_type": "single_choice",
                "checker_key": "choice_label_checker",
                "equivalence_type": "choice_label",
            },
        }
        payloads = [
            {"answer_type": "single_choice", "answer": "A", "choices": ["A", "B", "C", "D"]},
            {"answer_type": "single_choice", "answer": "B", "choices": ["A", "B", "C", "D"]},
            {"answer_type": "single_choice", "answer": "C", "choices": ["A", "B", "C", "D"]},
        ]
        blockers = _detect_payload_spec_contract_mismatch(spec, payloads)
        assert not blockers, f"Expected no blockers, got {blockers}"

    def test_text_short_spec_with_numeric_payloads_is_blocker(self) -> None:
        from core.gencode.generator_diversity_sampling import _detect_payload_spec_contract_mismatch
        spec = {
            "problem_type_id": "quadratic_graph_translation_fill_blank",
            "answer_contract": {
                "answer_type": "text_short",
                "checker_key": "text_short_checker",
            },
        }
        payloads = [
            {"answer_type": "integer", "answer": "3"},
            {"answer_type": "integer", "answer": "5"},
            {"answer_type": "integer", "answer": "7"},
            {"answer_type": "integer", "answer": "2"},
        ]
        blockers = _detect_payload_spec_contract_mismatch(spec, payloads)
        assert blockers, "Expected mismatch when text_short spec but integer payloads"


# ── 7. Phase 3 integrity gate for properties specs ───────────────────────────

class TestPhase3IntegrityForPropertiesSpecs:
    def test_properties_slot_with_integer_checker_is_blocked(self) -> None:
        from core.gencode.packaging_policy import validate_phase3_generator_spec_integrity
        row = {
            "problem_type_id": "integer_quadratic_standard_to_vertex_properties",
            "base_problem_type_id": "quadratic_standard_to_vertex_properties",
            "template_slot": "quadratic_standard_to_vertex_properties",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "answer_type": "integer",
            "generator_readiness": "runtime_ready_with_warning",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert any("choice_slot" in b for b in blockers), f"Expected choice_slot mismatch, got {blockers}"

    def test_canonicalized_properties_spec_passes(self) -> None:
        from core.gencode.packaging_policy import validate_phase3_generator_spec_integrity
        row = {
            "problem_type_id": "integer_quadratic_standard_to_vertex_properties",
            "base_problem_type_id": "quadratic_standard_to_vertex_properties",
            "template_slot": "quadratic_standard_to_vertex_properties",
            "checker_key": "choice_label_checker",
            "equivalence_type": "choice_label",
            "answer_type": "single_choice",
            "answer_shape": "single_choice",
            "generator_readiness": "runtime_ready_with_warning",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert not blockers, f"Expected no blockers, got {blockers}"
