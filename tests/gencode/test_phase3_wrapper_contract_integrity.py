# -*- coding: utf-8 -*-
"""
tests/gencode/test_phase3_wrapper_contract_integrity.py
=======================================================
Phase 3 packaging integrity gate tests.
Ensures validate_phase3_generator_spec_integrity() catches all mismatch cases.
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.packaging_policy import validate_phase3_generator_spec_integrity


class TestPhase3IntegrityBlocked:
    def test_fill_blank_slot_with_integer_checker_blocked(self) -> None:
        row = {
            "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
            "template_slot": "quadratic_graph_translation_fill_blank",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "answer_type": "integer",
            "answer_shape": "text_short",
            "generator_readiness": "runtime_ready_with_warning",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert any("fill_blank_slot_numeric_checker" in b or "answer_shape_type" in b for b in blockers), (
            f"Expected contract mismatch blocker, got {blockers}"
        )

    def test_choice_slot_with_integer_checker_blocked(self) -> None:
        row = {
            "problem_type_id": "integer_quadratic_graph_properties_choice",
            "template_slot": "quadratic_vertex_form_properties",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "answer_type": "integer",
            "answer_shape": "single_choice",
            "generator_readiness": "runtime_ready_with_warning",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert any("choice_slot" in b for b in blockers), (
            f"Expected choice_slot mismatch blocker, got {blockers}"
        )

    def test_answer_shape_text_short_with_integer_type_blocked(self) -> None:
        row = {
            "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
            "template_slot": "quadratic_graph_translation_fill_blank",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "answer_type": "integer",
            "answer_shape": "text_short",
            "generator_readiness": "runtime_ready_with_warning",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        mismatch_blockers = [b for b in blockers if "answer_shape_type_mismatch" in b or "fill_blank_slot_numeric" in b]
        assert mismatch_blockers, f"Expected mismatch blocker, got {blockers}"

    def test_generator_not_ready_blocked(self) -> None:
        row = {
            "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
            "template_slot": "quadratic_graph_translation_fill_blank",
            "checker_key": "text_short_checker",
            "equivalence_type": "exact_string",
            "answer_type": "text_short",
            "answer_shape": "text_short",
            "generator_readiness": "generator_not_ready",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert any("generator_not_ready" in b for b in blockers)

    def test_typed_prefix_without_canonical_fields_blocked(self) -> None:
        row = {
            "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
            "template_slot": "quadratic_graph_translation_fill_blank",
            "checker_key": "text_short_checker",
            "equivalence_type": "exact_string",
            "answer_type": "text_short",
            "generator_readiness": "runtime_ready_with_warning",
            # NO base_problem_type_id or canonical_base_problem_type_id
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert any("canonicalized_spec_missing" in b for b in blockers)


class TestPhase3IntegrityPass:
    def test_canonical_translation_spec_passes(self) -> None:
        row = {
            "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
            "base_problem_type_id": "quadratic_graph_translation_fill_blank",
            "template_slot": "quadratic_graph_translation_fill_blank",
            "checker_key": "text_short_checker",
            "equivalence_type": "exact_string",
            "answer_type": "text_short",
            "answer_shape": "text_short",
            "presentation_mode": "short_answer",
            "generator_readiness": "runtime_ready_with_warning",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert not blockers, f"Expected no blockers, got {blockers}"

    def test_canonical_choice_spec_passes(self) -> None:
        row = {
            "problem_type_id": "integer_quadratic_graph_properties_choice",
            "base_problem_type_id": "quadratic_graph_properties_choice",
            "template_slot": "quadratic_vertex_form_properties",
            "checker_key": "choice_label_checker",
            "equivalence_type": "choice_label",
            "answer_type": "single_choice",
            "answer_shape": "single_choice",
            "presentation_mode": "single_choice",
            "generator_readiness": "runtime_ready_with_warning",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert not blockers, f"Expected no blockers, got {blockers}"

    def test_formal_quadratic_fill_blank_passes(self) -> None:
        row = {
            "problem_type_id": "quadratic_graph_translation_fill_blank",
            "template_slot": "quadratic_graph_translation_fill_blank",
            "checker_key": "text_short_checker",
            "equivalence_type": "exact_string",
            "answer_type": "text_short",
            "generator_readiness": "runtime_ready",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert not blockers, f"Expected no blockers, got {blockers}"

    def test_formal_choice_passes(self) -> None:
        row = {
            "problem_type_id": "quadratic_graph_vertex_axis_choice",
            "template_slot": "quadratic_graph_vertex_axis_choice",
            "checker_key": "choice_label_checker",
            "equivalence_type": "choice_label",
            "answer_type": "single_choice",
            "generator_readiness": "runtime_ready",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert not blockers, f"Expected no blockers, got {blockers}"


class TestPhase3RequiredFields:
    def test_case1_valid_row(self) -> None:
        row = {
            "problem_type_id": "integer_example",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "generator_readiness": "runtime_ready",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        required_missing = [b for b in blockers if "phase3_required_field_missing" in b]
        assert not required_missing

    def test_case2_missing_problem_type_id(self) -> None:
        row = {
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "generator_readiness": "runtime_ready",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert "phase3_required_field_missing:problem_type_id" in blockers

    def test_case3_missing_checker_key_and_fallback(self) -> None:
        row = {
            "problem_type_id": "integer_example",
            "equivalence_type": "numeric_exact",
            "generator_readiness": "runtime_ready",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert "phase3_required_field_missing:checker_key" in blockers

    def test_case4_only_checker_fallback(self) -> None:
        row = {
            "problem_type_id": "integer_example",
            "equivalence_type": "numeric_exact",
            "generator_readiness": "runtime_ready",
            "checker": "text_short_checker"
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert "phase3_required_field_missing:checker_key" not in blockers

    def test_case5_missing_equivalence_type_and_fallback(self) -> None:
        row = {
            "problem_type_id": "integer_example",
            "checker_key": "integer_checker",
            "generator_readiness": "runtime_ready",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert "phase3_required_field_missing:equivalence_type" in blockers

    def test_case6_only_answer_equivalence_fallback(self) -> None:
        row = {
            "problem_type_id": "integer_example",
            "checker_key": "integer_checker",
            "generator_readiness": "runtime_ready",
            "answer_equivalence": "numeric_exact"
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert "phase3_required_field_missing:equivalence_type" not in blockers

    def test_case7_non_dict_row(self) -> None:
        blockers = validate_phase3_generator_spec_integrity([])
        assert "invalid_generator_spec_row" in blockers

    def test_m1_2_case1_missing_field(self) -> None:
        row = {
            "problem_type_id": "sample",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert "phase3_required_field_missing:generator_readiness" in blockers

    def test_m1_2_case2_empty_string(self) -> None:
        row = {
            "problem_type_id": "sample",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "generator_readiness": "",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert "phase3_required_field_missing:generator_readiness" in blockers

    def test_m1_2_case3_whitespace(self) -> None:
        row = {
            "problem_type_id": "sample",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "generator_readiness": "   ",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert "phase3_required_field_missing:generator_readiness" in blockers

    def test_m1_2_case4_none(self) -> None:
        row = {
            "problem_type_id": "sample",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "generator_readiness": None,
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert "phase3_required_field_missing:generator_readiness" in blockers

    def test_m1_2_case5_runtime_ready(self) -> None:
        row = {
            "problem_type_id": "sample",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "generator_readiness": "runtime_ready",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert "phase3_required_field_missing:generator_readiness" not in blockers

    def test_m1_2_case6_runtime_ready_with_warning(self) -> None:
        row = {
            "problem_type_id": "sample",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "generator_readiness": "runtime_ready_with_warning",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert "phase3_required_field_missing:generator_readiness" not in blockers

    def test_m1_2_case7_generator_not_ready(self) -> None:
        row = {
            "problem_type_id": "sample",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "generator_readiness": "generator_not_ready",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert "phase3_generator_not_ready_in_wrapper" in blockers
        assert "phase3_required_field_missing:generator_readiness" not in blockers

    def test_m1_2_case8_unknown_status(self) -> None:
        row = {
            "problem_type_id": "sample",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
            "generator_readiness": "unknown_status",
        }
        blockers = validate_phase3_generator_spec_integrity(row)
        assert "phase3_required_field_missing:generator_readiness" not in blockers


    def test_m2_1_cases_answer_type_family(self) -> None:
        from core.gencode.answer_payload import answer_type_family

        # Case A: table_fill
        assert answer_type_family("table_fill") == "multi_part"
        
        # Case B: multi_part
        assert answer_type_family("multi_part") == "multi_part"
        
        # Case C: drawing
        assert answer_type_family("drawing") == "drawing"
        
        # Case D: text
        assert answer_type_family("text") == "short_answer"
        assert answer_type_family("text_short") == "short_answer"
        
        # Case E: unknown token
        assert answer_type_family("unknown_random_token") == "unknown_random_token"
        
        # Case F & G: priority & fallback in grade_answer_for_current_question
        from core.gencode.answer_grading import grade_answer_for_current_question
        # We can test helper indirectly if needed, but direct family tests are sufficient.
