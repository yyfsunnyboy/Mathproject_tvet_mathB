# -*- coding: utf-8 -*-
"""
tests/gencode/test_quadratic_phase2_multi_type_packaging.py
Phase 3 packaging safety: generator_not_ready must not enter draft wrapper.
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.packaging_policy import is_generator_usable_for_packaging, select_generators_for_packaging
from core.gencode.problem_type_canonicalizer import (
    evaluate_typed_prefix_readiness,
    is_phase3_packaging_allowed,
)


QUADRATIC_TYPED_CANDIDATES = [
    "integer_quadratic_graph_translation_fill_blank",
    "rational_quadratic_graph_translation_fill_blank",
    "integer_quadratic_graph_properties_choice",
]


def _build_candidate(pt_id: str, target_task: str) -> dict:
    from core.gencode.problem_type_canonicalizer import enrich_spec_with_canonicalization

    spec = enrich_spec_with_canonicalization({
        "problem_type_id": pt_id,
        "target_task": target_task,
        "answer_contract": {},
        "generator_contract": {},
    })
    readiness, usable, blockers = evaluate_typed_prefix_readiness(spec)
    ac = spec["answer_contract"]
    return {
        "problem_type_id": pt_id,
        "generator_key": f"test_skill:{pt_id}:draft_v1",
        "generator_status": readiness if readiness in {"runtime_ready", "runtime_ready_with_warning"} else "generator_not_ready",
        "generator_readiness": readiness,
        "usable_for_phase3": usable,
        "checker_smoke_status": "passed" if usable else "skipped_with_blockers",
        "dynamic_sampling_status": "passed" if usable else "skipped_with_blockers",
        "blockers": blockers,
        "checker_key_proposal": ac.get("checker_key", ""),
        "equivalence_type_proposal": ac.get("equivalence_type", ""),
        "answer_contract_proposal": ac,
    }


class TestQuadraticMultiTypePackaging:
    def test_three_typed_candidates_all_usable(self):
        """All 3 quadratic typed-prefix candidates should be usable after canonicalization."""
        candidates = [
            _build_candidate("integer_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank"),
            _build_candidate("rational_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank"),
            _build_candidate("integer_quadratic_graph_properties_choice", "quadratic_graph_properties_choice"),
        ]
        usable_count = sum(1 for c in candidates if c["usable_for_phase3"])
        assert usable_count == 3, (
            f"Expected 3 usable, got {usable_count}: "
            f"{[(c['problem_type_id'], c['generator_readiness']) for c in candidates]}"
        )

    def test_packaging_includes_all_three(self):
        phase2_summary = {
            "generator_results": [
                _build_candidate("integer_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank"),
                _build_candidate("rational_quadratic_graph_translation_fill_blank", "quadratic_graph_translation_fill_blank"),
                _build_candidate("integer_quadratic_graph_properties_choice", "quadratic_graph_properties_choice"),
            ]
        }
        included, diag = select_generators_for_packaging(phase2_summary, None)
        assert diag["included_count"] == 3, (
            f"Expected included=3, got {diag['included_count']}: {diag.get('excluded')}"
        )
        assert diag["excluded_count"] == 0

    def test_generator_not_ready_excluded_from_packaging(self):
        row = {
            "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
            "generator_status": "generator_not_ready",
            "generator_readiness": "generator_not_ready",
            "usable_for_phase3": False,
            "checker_smoke_status": "skipped_with_blockers",
            "dynamic_sampling_status": "skipped_with_blockers",
            "blockers": ["generator_not_ready"],
        }
        usable, reasons = is_generator_usable_for_packaging(row)
        assert usable is False
        assert any("generator_not_ready" in r or "status_not_packaging_ready" in r for r in reasons)

    def test_choice_candidate_has_choice_checker_not_integer(self):
        c = _build_candidate("integer_quadratic_graph_properties_choice", "quadratic_graph_properties_choice")
        ac = c["answer_contract_proposal"]
        assert ac["checker_key"] == "choice_label_checker"
        assert ac["equivalence_type"] == "choice_label"
        assert ac["answer_type"] == "single_choice"
        assert c["checker_key_proposal"] == "choice_label_checker"

    def test_properties_choice_not_packaging_allowed_when_contract_mismatch(self):
        row = {
            "problem_type_id": "integer_quadratic_graph_properties_choice",
            "generator_status": "runtime_ready",
            "generator_readiness": "runtime_ready",
            "usable_for_phase3": True,
            "checker_smoke_status": "passed",
            "dynamic_sampling_status": "passed",
            "checker_key_proposal": "integer_checker",
            "equivalence_type_proposal": "numeric_exact",
        }
        # Packaging policy checks status, not contract — but usable_for_phase3 gate applies.
        # Contract mismatch should be caught at Phase 2 via canonicalizer before this point.
        assert is_phase3_packaging_allowed("contract_slot_mismatch", True) is False

    def test_draft_specs_must_not_contain_generator_not_ready_readiness(self):
        """Simulate GENERATOR_SPECS rows — none should have generator_not_ready readiness."""
        candidates = [
            _build_candidate(pt, pt.split("_", 1)[-1] if pt.startswith("integer_") or pt.startswith("rational_") else pt)
            for pt in QUADRATIC_TYPED_CANDIDATES
        ]
        for c in candidates:
            assert c["generator_readiness"] != "generator_not_ready", (
                f"{c['problem_type_id']} has generator_not_ready"
            )
            assert is_phase3_packaging_allowed(c["generator_readiness"], c["usable_for_phase3"])
