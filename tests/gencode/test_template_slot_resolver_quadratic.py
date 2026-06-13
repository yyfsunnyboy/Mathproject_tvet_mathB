# -*- coding: utf-8 -*-
"""
tests/gencode/test_template_slot_resolver_quadratic.py
=======================================================
Template Slot Resolver 二次函數精確映射測試

驗收條件：
C1. 5 個 formal quadratic problem_type_id 精確映射到對應 slot。
C2. quadratic_graph_translation 不再落到 generic choice default。
C3. quadratic_graph_properties_choice 映射到 choice properties slot。
C4. text_short_compute_vertex_and_axis (bridge primary) 不得映射到 choice slot。
C5. SLOT_REGISTRY 中 5 個 quadratic slot 均 callable。
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.template_slot_resolver import (
    TASK_FAMILY_TO_SLOT,
    resolve_template_slot,
)
from core.gencode.slot_generators import SLOT_REGISTRY


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _spec(pt_id: str, answer_type: str = "single_choice", target_task: str = "") -> dict:
    tt = target_task or pt_id
    return {
        "problem_type_id": pt_id,
        "target_task": tt,
        "answer_contract": {
            "answer_type": answer_type,
            "presentation_mode": "single_choice" if answer_type == "single_choice" else "short_answer",
        },
    }


def _spec_text_short(pt_id: str, target_task: str = "") -> dict:
    return _spec(pt_id, answer_type="text_short", target_task=target_task or pt_id)


def _resolve(spec: dict) -> str:
    return resolve_template_slot(spec)


# ─── C1: 5 formal quadratic problem_type_id → correct slots ──────────────────

class TestFormalQuadraticSlotMapping:
    """5 個 formal quadratic problem_type_id 精確映射到對應 slot（TASK_FAMILY_TO_SLOT 直接命中）。"""

    @pytest.mark.parametrize("pt_id,expected_slot", [
        ("quadratic_graph_vertex_axis_choice",      "quadratic_graph_vertex_axis_choice"),
        ("quadratic_graph_translation_fill_blank",  "quadratic_graph_translation_fill_blank"),
        ("quadratic_graph_translation_short_answer","quadratic_graph_translation_short_answer"),
        ("quadratic_vertex_form_properties",        "quadratic_vertex_form_properties"),
        ("quadratic_standard_to_vertex_properties", "quadratic_standard_to_vertex_properties"),
    ])
    def test_direct_mapping_in_task_family_to_slot(self, pt_id: str, expected_slot: str) -> None:
        assert TASK_FAMILY_TO_SLOT.get(pt_id) == expected_slot, (
            f"TASK_FAMILY_TO_SLOT[{pt_id!r}] = "
            f"{TASK_FAMILY_TO_SLOT.get(pt_id)!r}, expected {expected_slot!r}"
        )

    @pytest.mark.parametrize("pt_id,expected_slot", [
        ("quadratic_graph_vertex_axis_choice",      "quadratic_graph_vertex_axis_choice"),
        ("quadratic_graph_translation_fill_blank",  "quadratic_graph_translation_fill_blank"),
        ("quadratic_graph_translation_short_answer","quadratic_graph_translation_short_answer"),
        ("quadratic_vertex_form_properties",        "quadratic_vertex_form_properties"),
        ("quadratic_standard_to_vertex_properties", "quadratic_standard_to_vertex_properties"),
    ])
    def test_resolve_template_slot_returns_correct_slot(self, pt_id: str, expected_slot: str) -> None:
        spec = _spec(pt_id)
        resolved = _resolve(spec)
        assert resolved == expected_slot, (
            f"resolve_template_slot({pt_id!r}) = {resolved!r}, expected {expected_slot!r}"
        )


# ─── C2: quadratic_graph_translation → fill_blank (not generic choice) ───────

class TestTaxonomyTargetTaskMapping:
    """Taxonomy target_tasks 精確映射到正確 presentation slot。"""

    def test_quadratic_graph_translation_maps_to_fill_blank(self) -> None:
        slot = TASK_FAMILY_TO_SLOT.get("quadratic_graph_translation")
        assert slot == "quadratic_graph_translation_fill_blank", (
            f"Expected fill_blank, got {slot!r}"
        )

    def test_quadratic_vertex_axis_identification_maps_to_fill_blank(self) -> None:
        slot = TASK_FAMILY_TO_SLOT.get("quadratic_vertex_axis_identification")
        assert slot == "quadratic_graph_translation_fill_blank", (
            f"Expected fill_blank, got {slot!r}"
        )

    def test_quadratic_graph_translation_resolve_via_target_task(self) -> None:
        spec = {
            "problem_type_id": "text_short_compute_vertex_and_axis",
            "target_task": "quadratic_graph_translation",
            "answer_contract": {
                "answer_type": "text_short",
                "presentation_mode": "short_answer",
            },
        }
        resolved = _resolve(spec)
        assert resolved != "quadratic_graph_vertex_axis_choice", (
            f"quadratic_graph_translation resolved to choice slot: {resolved!r}"
        )
        assert "fill_blank" in resolved or "short_answer" in resolved, (
            f"Expected a short_answer slot, got {resolved!r}"
        )


# ─── C3: quadratic_graph_properties_choice → vertex_form_properties ──────────

class TestPropertiesChoiceSlotMapping:
    def test_quadratic_graph_properties_choice_maps_to_vertex_form(self) -> None:
        slot = TASK_FAMILY_TO_SLOT.get("quadratic_graph_properties_choice")
        assert slot == "quadratic_vertex_form_properties", (
            f"Expected quadratic_vertex_form_properties, got {slot!r}"
        )

    def test_resolve_properties_choice_target_task(self) -> None:
        spec = {
            "problem_type_id": "some_pt",
            "target_task": "quadratic_graph_properties_choice",
            "answer_contract": {"answer_type": "single_choice"},
        }
        resolved = _resolve(spec)
        assert resolved == "quadratic_vertex_form_properties", (
            f"resolve({spec['target_task']!r}) = {resolved!r}"
        )


# ─── C4: text_short_compute_vertex_and_axis (bridge primary) → NOT choice slot ─

class TestBridgePrimaryNotMappedToChoiceSlot:
    """Bridge primary pt_id should not directly resolve to a choice slot
    without answer_contract guidance."""

    def test_text_short_primary_with_text_short_ac_avoids_choice_slot(self) -> None:
        spec = _spec_text_short(
            "text_short_compute_vertex_and_axis",
            target_task="text_short_compute_vertex_and_axis",
        )
        resolved = _resolve(spec)
        assert resolved != "quadratic_graph_vertex_axis_choice", (
            f"text_short bridge primary resolved to choice slot: {resolved!r}"
        )

    def test_text_short_primary_with_no_ac_uses_fill_blank_not_choice(self) -> None:
        """Bridge primary without AC should not resolve to the choice slot.
        (Bridge primaries should have been expanded by Phase 2 before reaching the resolver;
        returning empty string or a non-choice slot is both acceptable.)"""
        spec = {
            "problem_type_id": "text_short_compute_vertex_and_axis",
            "target_task": "text_short_compute_vertex_and_axis",
            "answer_contract": {},
        }
        resolved = _resolve(spec)
        # Must NOT resolve to choice slot; empty string is acceptable (expansion not done yet)
        assert resolved != "quadratic_graph_vertex_axis_choice", (
            f"Bridge primary with no AC resolved to choice slot: {resolved!r}"
        )


# ─── C5: SLOT_REGISTRY 中 5 個 quadratic slot 均 callable ────────────────────

EXPECTED_QUADRATIC_SLOTS = [
    "quadratic_graph_vertex_axis_choice",
    "quadratic_graph_translation_fill_blank",
    "quadratic_graph_translation_short_answer",
    "quadratic_vertex_form_properties",
    "quadratic_standard_to_vertex_properties",
]


class TestQuadraticSlotsRegistered:
    def test_all_5_slots_in_registry(self) -> None:
        for slot_key in EXPECTED_QUADRATIC_SLOTS:
            assert slot_key in SLOT_REGISTRY, (
                f"Slot {slot_key!r} not in SLOT_REGISTRY"
            )

    def test_all_5_slots_callable(self) -> None:
        for slot_key in EXPECTED_QUADRATIC_SLOTS:
            fn = SLOT_REGISTRY.get(slot_key)
            assert callable(fn), (
                f"Slot {slot_key!r} is not callable: {fn!r}"
            )

    @pytest.mark.parametrize("slot_key", EXPECTED_QUADRATIC_SLOTS)
    def test_slot_generates_valid_payload(self, slot_key: str) -> None:
        fn = SLOT_REGISTRY[slot_key]
        is_choice = "choice" in slot_key or "properties" in slot_key
        spec = {
            "problem_type_id": slot_key,
            "answer_contract": {
                "answer_type": "single_choice" if is_choice else "text_short",
            },
            "generator_contract": {},
        }
        payload = fn("skill_id", slot_key, spec, 0)
        assert isinstance(payload, dict), f"Slot {slot_key!r} did not return dict"
        assert "question_text" in payload, f"Slot {slot_key!r} payload missing question_text"
        assert "$" in payload.get("question_text", ""), (
            f"Slot {slot_key!r} question_text has no formula: {payload['question_text']!r}"
        )


# ─── Typed-prefix canonical resolution ─────────────────────────────────────────

class TestTypedPrefixQuadraticSlotMapping:
    """Typed-prefix problem_type_id resolves to same slot as base."""

    def test_integer_translation_fill_blank_resolves_to_fill_blank_slot(self) -> None:
        from core.gencode.problem_type_canonicalizer import enrich_spec_with_canonicalization
        spec = enrich_spec_with_canonicalization({
            "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
            "target_task": "quadratic_graph_translation_fill_blank",
            "answer_contract": {},
            "generator_contract": {},
        })
        resolved = spec.get("_resolved_template_slot") or _resolve(spec)
        assert resolved == "quadratic_graph_translation_fill_blank"

    def test_rational_translation_fill_blank_resolves_to_fill_blank_slot(self) -> None:
        from core.gencode.problem_type_canonicalizer import enrich_spec_with_canonicalization
        spec = enrich_spec_with_canonicalization({
            "problem_type_id": "rational_quadratic_graph_translation_fill_blank",
            "target_task": "quadratic_graph_translation_fill_blank",
            "answer_contract": {},
            "generator_contract": {},
        })
        resolved = spec.get("_resolved_template_slot") or _resolve(spec)
        assert resolved == "quadratic_graph_translation_fill_blank"

    def test_integer_properties_choice_resolves_and_is_choice_contract(self) -> None:
        from core.gencode.problem_type_canonicalizer import enrich_spec_with_canonicalization
        spec = enrich_spec_with_canonicalization({
            "problem_type_id": "integer_quadratic_graph_properties_choice",
            "target_task": "quadratic_graph_properties_choice",
            "answer_contract": {"answer_type": "integer", "checker_key": "integer_checker"},
            "generator_contract": {},
        })
        resolved = spec.get("_resolved_template_slot") or _resolve(spec)
        assert resolved == "quadratic_vertex_form_properties"
        ac = spec["answer_contract"]
        assert ac["answer_type"] == "single_choice"
        assert ac["checker_key"] == "choice_label_checker"
        assert ac["checker_key"] != "integer_checker"


# ─── 額外：確認 contextual_application 不被映射到 quadratic slot ──────────────

class TestContextualApplicationNotMappedToQuadratic:
    def test_contextual_application_does_not_map_to_quadratic_slot(self) -> None:
        slot = _resolve(
            {
                "problem_type_id": "text_short_contextual_application",
                "target_task": "contextual_application",
                "answer_contract": {"answer_type": "text_short"},
            }
        )
        for qs in EXPECTED_QUADRATIC_SLOTS:
            assert slot != qs, (
                f"contextual_application resolved to quadratic slot {qs!r}"
            )
