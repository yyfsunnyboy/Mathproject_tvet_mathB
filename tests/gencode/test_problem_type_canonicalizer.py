# -*- coding: utf-8 -*-
"""tests/gencode/test_problem_type_canonicalizer.py — typed-prefix canonicalization unit tests."""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.problem_type_canonicalizer import (
    canonicalize_problem_type_id,
    enrich_spec_with_canonicalization,
    evaluate_typed_prefix_readiness,
    infer_presentation_mode,
)


class TestCanonicalizeProblemTypeId:
    def test_integer_translation_fill_blank(self):
        c = canonicalize_problem_type_id("integer_quadratic_graph_translation_fill_blank")
        assert c["value_type_prefix"] == "integer"
        assert c["base_problem_type_id"] == "quadratic_graph_translation_fill_blank"
        assert c["base_target_task"] == "quadratic_graph_translation_fill_blank"

    def test_rational_translation_fill_blank(self):
        c = canonicalize_problem_type_id("rational_quadratic_graph_translation_fill_blank")
        assert c["value_type_prefix"] == "rational"
        assert c["base_problem_type_id"] == "quadratic_graph_translation_fill_blank"

    def test_integer_properties_choice(self):
        c = canonicalize_problem_type_id("integer_quadratic_graph_properties_choice")
        assert c["value_type_prefix"] == "integer"
        assert c["base_problem_type_id"] == "quadratic_graph_properties_choice"
        assert "properties_choice" in c["base_target_task"] or c["base_target_task"] == "quadratic_graph_properties_choice"

    def test_no_prefix_unchanged(self):
        c = canonicalize_problem_type_id("quadratic_graph_vertex_axis_choice")
        assert c["value_type_prefix"] == ""
        assert c["base_problem_type_id"] == "quadratic_graph_vertex_axis_choice"

    def test_unknown_prefix_not_mistaken(self):
        """problem_type_id whose first segment is NOT a typed prefix stays intact."""
        c = canonicalize_problem_type_id("quadratic_graph_translation_fill_blank")
        assert c["value_type_prefix"] == ""
        assert c["base_problem_type_id"] == "quadratic_graph_translation_fill_blank"

    def test_text_short_prefix(self):
        c = canonicalize_problem_type_id("text_short_compute_vertex_and_axis")
        assert c["value_type_prefix"] == "text_short"
        assert c["base_problem_type_id"] == "compute_vertex_and_axis"


class TestPresentationMode:
    def test_properties_choice_is_single_choice(self):
        assert infer_presentation_mode("quadratic_graph_properties_choice") == "single_choice"

    def test_fill_blank_is_short_answer(self):
        assert infer_presentation_mode("quadratic_graph_translation_fill_blank") == "short_answer"

    def test_source_has_choices_overrides(self):
        assert infer_presentation_mode("some_task", source_has_choices=True) == "single_choice"


class TestEnrichSpec:
    def test_enrich_sets_slot_for_integer_fill_blank(self):
        spec = enrich_spec_with_canonicalization({
            "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
            "target_task": "quadratic_graph_translation_fill_blank",
            "answer_contract": {"answer_type": "integer", "checker_key": "integer_checker"},
            "generator_contract": {},
        })
        assert spec.get("_resolved_template_slot") == "quadratic_graph_translation_fill_blank"
        ac = spec["answer_contract"]
        assert ac["checker_key"] == "text_short_checker"
        assert ac["answer_type"] == "text_short"

    def test_enrich_sets_choice_contract_for_properties(self):
        spec = enrich_spec_with_canonicalization({
            "problem_type_id": "integer_quadratic_graph_properties_choice",
            "target_task": "quadratic_graph_properties_choice",
            "answer_contract": {"answer_type": "integer", "checker_key": "integer_checker"},
            "generator_contract": {},
        })
        ac = spec["answer_contract"]
        assert ac["checker_key"] == "choice_label_checker"
        assert ac["answer_type"] == "single_choice"
        assert ac["equivalence_type"] == "choice_label"
