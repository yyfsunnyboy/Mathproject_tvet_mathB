# -*- coding: utf-8 -*-
"""
tests/gencode/test_answer_contract_canonicalization_generic.py
==============================================================
Generic answer-contract canonicalization regression tests (updated for
answer_format_hint-driven architecture).

Architecture summary:
  - answer_format_hint is the HIGHEST priority for contract derivation.
  - source_has_choices=True → infer hint "A/B/C/D" → choice_label_checker.
  - Properties slots (vertex_form_properties, standard_to_vertex_properties)
    are NOT hard-locked to single_choice; their format is hint-driven.
  - SLOT_PRESENTATION_MODE is a FALLBACK used only when hint is absent.
  - Phase 2 mismatch gate detects when live payload contradicts spec.
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.answer_format_hint import (
    HINT_CHOICE,
    HINT_COORDINATE,
    HINT_INTEGER,
    HINT_RATIONAL,
    HINT_TEXT_SHORT,
    HINT_TRANSLATION_TEXT,
    answer_contract_from_hint,
    infer_answer_format_hint,
    infer_answer_format_hint_from_answers,
    naming_warning_if_prefix_contract_mismatch,
)
from core.gencode.problem_type_canonicalizer import (
    enrich_spec_with_canonicalization,
    infer_presentation_mode,
)
from core.gencode.template_slot_resolver import (
    SLOT_PRESENTATION_MODE,
    get_slot_primary_presentation_mode,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_raw_spec(pt_id: str, target_task: str = "", *, source_has_choices: bool = False,
                   answer_format_hint: str | None = None) -> dict:
    """Build a minimal pre-canonicalization spec with configurable hint."""
    spec: dict = {
        "problem_type_id": pt_id,
        "target_task": target_task or pt_id,
        "answer_contract": {
            "answer_type": pt_id.split("_")[0] if "_" in pt_id else "integer",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "source_has_choices": source_has_choices,
        },
    }
    if answer_format_hint is not None:
        spec["answer_format_hint"] = answer_format_hint
    return spec


# ── 1. answer_format_hint module ─────────────────────────────────────────────

class TestAnswerFormatHintModule:
    def test_answer_contract_from_hint_choice(self) -> None:
        ac = answer_contract_from_hint(HINT_CHOICE)
        assert ac["checker_key"] == "choice_label_checker"
        assert ac["answer_type"] == "single_choice"
        assert ac["equivalence_type"] == "choice_label"

    def test_answer_contract_from_hint_integer(self) -> None:
        ac = answer_contract_from_hint(HINT_INTEGER)
        assert ac["checker_key"] == "integer_checker"
        assert ac["answer_type"] == "integer"

    def test_answer_contract_from_hint_coordinate(self) -> None:
        ac = answer_contract_from_hint(HINT_COORDINATE)
        assert ac["checker_key"] == "coordinate_pair_checker"
        assert ac["answer_type"] == "coordinate_pair"

    def test_answer_contract_from_hint_translation(self) -> None:
        ac = answer_contract_from_hint(HINT_TRANSLATION_TEXT)
        assert ac["checker_key"] == "structured_text_checker"
        assert ac["answer_type"] == "text_short"
        assert "horizontal_shift" in ac.get("answer_fields", [])

    def test_infer_hint_from_source_has_choices(self) -> None:
        spec = {"answer_contract": {"source_has_choices": True}}
        assert infer_answer_format_hint(spec) == HINT_CHOICE

    def test_infer_hint_from_choices_required(self) -> None:
        spec = {"answer_contract": {"choices_required": True}}
        assert infer_answer_format_hint(spec) == HINT_CHOICE

    def test_infer_hint_from_answer_type_integer(self) -> None:
        # integer answer_type alone is NOT a reliable hint (could be typed-prefix artifact).
        # Explicit answer_format_hint or answer_fields are required for integer.
        spec = {"answer_contract": {"answer_type": "integer"}}
        # Should return HINT_UNKNOWN (not HINT_INTEGER from raw answer_type)
        from core.gencode.answer_format_hint import HINT_UNKNOWN
        assert infer_answer_format_hint(spec) == HINT_UNKNOWN

    def test_explicit_hint_integer_is_respected(self) -> None:
        # When answer_format_hint is set explicitly, it IS trusted
        spec = {"answer_format_hint": HINT_INTEGER, "answer_contract": {"answer_type": "integer"}}
        assert infer_answer_format_hint(spec) == HINT_INTEGER

    def test_infer_hint_from_answer_samples_choice(self) -> None:
        hint = infer_answer_format_hint_from_answers(["A", "B", "C", "D", "A"])
        assert hint == HINT_CHOICE

    def test_infer_hint_from_answer_samples_coordinate(self) -> None:
        hint = infer_answer_format_hint_from_answers(["(1,2)", "(-3,4)", "(0,-1)"])
        assert hint == HINT_COORDINATE

    def test_infer_hint_from_answer_samples_integer(self) -> None:
        hint = infer_answer_format_hint_from_answers(["3", "-2", "7", "0"])
        assert hint == HINT_INTEGER

    def test_naming_warning_when_prefix_contradicts_hint(self) -> None:
        warning = naming_warning_if_prefix_contract_mismatch(
            "integer_quadratic_standard_to_vertex_properties", HINT_CHOICE
        )
        assert warning is not None
        assert "naming_warning" in warning

    def test_no_naming_warning_when_consistent(self) -> None:
        warning = naming_warning_if_prefix_contract_mismatch(
            "integer_compute_vertex_x", HINT_INTEGER
        )
        assert warning is None


# ── 2. SLOT_PRESENTATION_MODE: properties slots are NOT hard-locked ──────────

class TestSlotPresentationModeMap:
    """Properties slots are multi-format; SLOT_PRESENTATION_MODE is fallback-only."""

    def test_properties_slots_not_in_slot_presentation_mode(self) -> None:
        # Properties slots should NOT be in SLOT_PRESENTATION_MODE because they
        # support multiple formats (choice, coordinate, text).
        assert "quadratic_vertex_form_properties" not in SLOT_PRESENTATION_MODE
        assert "quadratic_standard_to_vertex_properties" not in SLOT_PRESENTATION_MODE

    def test_explicit_choice_slots_are_in_map(self) -> None:
        assert SLOT_PRESENTATION_MODE.get("quadratic_graph_vertex_axis_choice") == "single_choice"
        assert SLOT_PRESENTATION_MODE.get("linear_function_two_point_choice") == "single_choice"

    def test_fill_blank_slots_are_short_answer(self) -> None:
        assert SLOT_PRESENTATION_MODE.get("quadratic_graph_translation_fill_blank") == "short_answer"

    def test_get_slot_primary_presentation_mode_returns_empty_for_properties(self) -> None:
        assert get_slot_primary_presentation_mode("quadratic_standard_to_vertex_properties") == ""
        assert get_slot_primary_presentation_mode("quadratic_vertex_form_properties") == ""


# ── 3. enrich_spec: answer_format_hint drives the contract ──────────────────

class TestEnrichSpecWithHint:
    def test_explicit_hint_choice_overrides_integer_prefix(self) -> None:
        spec = _make_raw_spec(
            "integer_quadratic_standard_to_vertex_properties",
            "quadratic_standard_to_vertex_properties",
            answer_format_hint=HINT_CHOICE,
        )
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "choice_label_checker"
        assert ac.get("answer_type") == "single_choice"

    def test_source_has_choices_true_gives_choice_label_checker(self) -> None:
        spec = _make_raw_spec(
            "integer_quadratic_standard_to_vertex_properties",
            "quadratic_standard_to_vertex_properties",
            source_has_choices=True,
        )
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "choice_label_checker"

    def test_source_has_choices_true_fills_blank_slot(self) -> None:
        # Even fill_blank slot: if source has choices, hint = A/B/C/D
        spec = _make_raw_spec(
            "integer_quadratic_graph_translation_fill_blank",
            "quadratic_graph_translation_fill_blank",
            source_has_choices=True,
        )
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "choice_label_checker"

    def test_no_hint_no_choices_uses_slot_fallback_for_fill_blank(self) -> None:
        # Without hint and without choices, fill_blank slot → short_answer fallback
        spec = {
            "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
            "target_task": "quadratic_graph_translation_fill_blank",
            "answer_contract": {
                "answer_type": "integer",
                "checker_key": "integer_checker",
                "source_has_choices": False,
            },
        }
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        # fill_blank slot → short_answer via SLOT_PRESENTATION_MODE fallback
        checker = ac.get("checker_key") or ac.get("checker")
        assert checker == "text_short_checker", f"Expected text_short_checker, got {checker}"

    def test_hint_coordinate_gives_coordinate_pair_checker(self) -> None:
        spec = _make_raw_spec(
            "integer_quadratic_standard_to_vertex_properties",
            answer_format_hint=HINT_COORDINATE,
        )
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "coordinate_pair_checker"

    def test_hint_translation_gives_structured_text_checker(self) -> None:
        spec = _make_raw_spec(
            "integer_quadratic_standard_to_vertex_properties",
            answer_format_hint=HINT_TRANSLATION_TEXT,
        )
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "structured_text_checker"

    def test_hint_integer_gives_integer_checker(self) -> None:
        spec = _make_raw_spec("integer_compute_vertex_x", "compute_x_value",
                              answer_format_hint=HINT_INTEGER)
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "integer_checker"


# ── 4. Properties tasks with choices evidence ─────────────────────────────────

class TestEnrichSpecPropertiesWithChoicesEvidence:
    def test_integer_standard_to_vertex_with_choices_gets_choice_label_checker(self) -> None:
        spec = _make_raw_spec(
            "integer_quadratic_standard_to_vertex_properties",
            "quadratic_standard_to_vertex_properties",
            source_has_choices=True,
        )
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "choice_label_checker"

    def test_rational_standard_to_vertex_with_choices_gets_choice_label_checker(self) -> None:
        spec = _make_raw_spec(
            "rational_quadratic_standard_to_vertex_properties",
            "quadratic_standard_to_vertex_properties",
            source_has_choices=True,
        )
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "choice_label_checker"

    def test_integer_vertex_form_with_choices_gets_choice_label_checker(self) -> None:
        spec = _make_raw_spec(
            "integer_quadratic_vertex_form_properties",
            "quadratic_vertex_form_properties",
            source_has_choices=True,
        )
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "choice_label_checker"

    def test_properties_without_choices_can_use_coordinate_hint(self) -> None:
        """Properties problem asking for vertex coordinate → coordinate hint."""
        spec = _make_raw_spec(
            "quadratic_vertex_form_properties",
            "quadratic_vertex_form_properties",
            answer_format_hint=HINT_COORDINATE,
        )
        enriched = enrich_spec_with_canonicalization(spec)
        ac = enriched["answer_contract"]
        assert (ac.get("checker_key") or ac.get("checker")) == "coordinate_pair_checker"


# ── 5. structured_text_checker normalization ──────────────────────────────────

class TestStructuredTextCheckerNormalization:
    def test_chinese_comma_normalizes(self) -> None:
        from core.checkers.structured_text_checker import normalize_separators
        assert normalize_separators("向右 1，向上 2") == "向右 1, 向上 2"

    def test_dun_hao_normalizes(self) -> None:
        from core.checkers.structured_text_checker import normalize_separators
        result = normalize_separators("向右 1、向上 2")
        assert "," in result

    def test_fullwidth_digits_normalize(self) -> None:
        from core.checkers.structured_text_checker import normalize_fullwidth
        assert normalize_fullwidth("（１，２）") == "(1,2)"

    def test_coordinate_normalization(self) -> None:
        from core.checkers.structured_text_checker import normalize_structured_text
        assert normalize_structured_text("（1，2）") == "(1,2)"
        assert normalize_structured_text("（1, 2）") == "(1,2)"

    def test_axis_normalization(self) -> None:
        from core.checkers.structured_text_checker import normalize_structured_text
        assert normalize_structured_text("x = 1") == "x=1"
        assert normalize_structured_text("x = -3") == "x=-3"

    def test_translation_comparison_success(self) -> None:
        from core.checkers.structured_text_checker import compare_structured_text
        result = compare_structured_text("向右 1, 向上 2", "向右 1，向上 2",
                                         answer_fields=["horizontal_shift", "vertical_shift"])
        assert result["is_correct"]

    def test_coordinate_comparison_fullwidth_vs_halfwidth(self) -> None:
        from core.checkers.structured_text_checker import compare_structured_text
        result = compare_structured_text("(1,2)", "（1，2）")
        assert result["is_correct"]

    def test_vertex_axis_field_comparison(self) -> None:
        from core.checkers.structured_text_checker import compare_structured_text
        result = compare_structured_text(
            "頂點=(1,-2), 對稱軸=x=1",
            "頂點=（1，-2）, 對稱軸=x = 1",
            answer_fields=["vertex", "axis"],
        )
        # After normalization both should be equivalent
        assert result["is_correct"]

    def test_mismatch_detected(self) -> None:
        from core.checkers.structured_text_checker import compare_structured_text
        result = compare_structured_text("向右 1, 向上 2", "向右 3, 向上 4")
        assert not result["is_correct"]


# ── 6. Phase 2 mismatch detection ─────────────────────────────────────────────

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

    def test_no_mismatch_when_contracts_agree_choice(self) -> None:
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


# ── 7. Phase 3 integrity gate ─────────────────────────────────────────────────

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

    def test_canonicalized_properties_spec_with_choice_contract_passes(self) -> None:
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
