# -*- coding: utf-8 -*-
"""tests/gencode/test_phase2_typed_prefix_readiness.py — Phase 2 readiness after canonicalization."""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.problem_type_canonicalizer import (
    READINESS_CONTRACT_SLOT_MISMATCH,
    READINESS_GENERATOR_NOT_READY,
    READINESS_PENDING_TEMPLATE,
    READINESS_RUNTIME_READY,
    READINESS_RUNTIME_READY_WITH_WARNING,
    evaluate_typed_prefix_readiness,
    is_phase3_packaging_allowed,
)
from core.gencode.spec_phase1_merge import slot_generator_readiness


def _spec(pt_id: str, target_task: str = "", ac: dict | None = None) -> dict:
    tt = target_task or pt_id.split("_", 1)[-1] if "_" in pt_id else pt_id
    return {
        "problem_type_id": pt_id,
        "target_task": target_task or tt,
        "answer_contract": ac or {},
        "generator_contract": {},
    }


class TestTypedPrefixReadiness:
    def test_integer_fill_blank_is_runtime_ready(self):
        r, usable, blockers = evaluate_typed_prefix_readiness(
            _spec("integer_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        )
        assert r == READINESS_RUNTIME_READY
        assert usable is True
        assert not blockers

    def test_rational_fill_blank_is_runtime_ready(self):
        r, usable, _ = evaluate_typed_prefix_readiness(
            _spec("rational_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        )
        assert r == READINESS_RUNTIME_READY
        assert usable is True

    def test_integer_properties_choice_is_runtime_ready(self):
        r, usable, _ = evaluate_typed_prefix_readiness(
            _spec("integer_quadratic_graph_properties_choice", "quadratic_graph_properties_choice")
        )
        assert r == READINESS_RUNTIME_READY
        assert usable is True

    def test_missing_slot_is_pending_template(self):
        r, usable, blockers = evaluate_typed_prefix_readiness(
            _spec("integer_totally_unknown_slot_xyz_abc", "totally_unknown_slot_xyz_abc")
        )
        assert r in {READINESS_GENERATOR_NOT_READY, READINESS_PENDING_TEMPLATE, "slot_generator_not_registered"}
        assert usable is False

    def test_choice_task_does_not_get_integer_checker(self):
        from core.gencode.problem_type_canonicalizer import enrich_spec_with_canonicalization
        spec = enrich_spec_with_canonicalization(
            _spec(
                "integer_quadratic_graph_properties_choice",
                "quadratic_graph_properties_choice",
                {"answer_type": "integer", "checker_key": "integer_checker", "equivalence_type": "numeric_exact"},
            )
        )
        ac = spec["answer_contract"]
        assert ac["checker_key"] != "integer_checker"
        assert ac["checker_key"] == "choice_label_checker"
        assert ac["equivalence_type"] == "choice_label"

    def test_fill_blank_maps_to_fill_blank_slot(self):
        from core.gencode.problem_type_canonicalizer import enrich_spec_with_canonicalization
        spec = enrich_spec_with_canonicalization(
            _spec("integer_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        )
        assert spec.get("_resolved_template_slot") == "quadratic_graph_translation_fill_blank"

    def test_contract_slot_mismatch_blocks_usable(self):
        """Forced numeric checker on choice slot → contract_slot_mismatch."""
        from core.gencode.problem_type_canonicalizer import check_contract_slot_mismatch
        spec = {
            "problem_type_id": "integer_quadratic_graph_properties_choice",
            "answer_contract": {
                "answer_type": "integer",
                "checker_key": "integer_checker",
                "equivalence_type": "numeric_exact",
                "presentation_mode": "single_choice",
            },
        }
        blockers = check_contract_slot_mismatch(spec, "quadratic_vertex_form_properties")
        assert blockers, "Expected contract_slot_mismatch blockers"


class TestSlotGeneratorReadinessIntegration:
    def test_slot_generator_readiness_integer_fill_blank(self):
        r = slot_generator_readiness(
            _spec("integer_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        )
        assert r in {READINESS_RUNTIME_READY, READINESS_RUNTIME_READY_WITH_WARNING}
        assert r != READINESS_GENERATOR_NOT_READY

    def test_slot_generator_readiness_rational_fill_blank(self):
        r = slot_generator_readiness(
            _spec("rational_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank")
        )
        assert r in {READINESS_RUNTIME_READY, READINESS_RUNTIME_READY_WITH_WARNING}


class TestPhase3PackagingGate:
    def test_generator_not_ready_not_packaging_allowed(self):
        assert is_phase3_packaging_allowed("generator_not_ready", True) is False

    def test_contract_slot_mismatch_not_packaging_allowed(self):
        assert is_phase3_packaging_allowed(READINESS_CONTRACT_SLOT_MISMATCH, True) is False

    def test_runtime_ready_packaging_allowed(self):
        assert is_phase3_packaging_allowed(READINESS_RUNTIME_READY, True) is True

    def test_usable_false_blocks_even_if_ready(self):
        assert is_phase3_packaging_allowed(READINESS_RUNTIME_READY, False) is False
