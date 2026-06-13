# -*- coding: utf-8 -*-
"""
tests/gencode/test_problem_type_bridge.py
=========================================
ProblemType Bridge 單元測試

驗收條件：
A. text_short_compute_vertex_and_axis 能讀到 bridge。
B. bridge 展開至少產生 5 個 runtime variants。
C. 每個 variant 有正確 answer_contract。
D. text_short variant 不會用 choice checker。
E. choice variant 不會用 text_short checker。
F. bridge 缺失時回傳 pending，不 fallback contextual_application。
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.problem_type_bridge import (
    BRIDGE_MISSING,
    all_bridge_primary_ids,
    expand_primary_to_runtime_variants,
    get_bridge,
    get_runtime_variants,
    has_bridge,
    is_bridge_primary,
    reset_bridge_cache,
)

SKILL_ID = "vh_數學B1_QuadraticFunctionGraph"
PRIMARY_PT = "text_short_compute_vertex_and_axis"
EXPECTED_VARIANTS = {
    "quadratic_graph_translation_fill_blank",
    "quadratic_graph_translation_short_answer",
    "quadratic_graph_vertex_axis_choice",
    "quadratic_vertex_form_properties",
    "quadratic_standard_to_vertex_properties",
}


@pytest.fixture(autouse=True)
def reset_cache():
    reset_bridge_cache()
    yield
    reset_bridge_cache()


class TestBridgeLookup:
    def test_bridge_exists_for_primary(self):
        assert has_bridge(PRIMARY_PT), f"No bridge for {PRIMARY_PT}"

    def test_bridge_entry_has_correct_structure(self):
        entry = get_bridge(PRIMARY_PT)
        assert isinstance(entry, dict)
        assert "semantic_family" in entry
        assert "runtime_variants" in entry
        assert isinstance(entry["runtime_variants"], list)

    def test_bridge_primary_ids_includes_primary(self):
        all_ids = all_bridge_primary_ids()
        assert PRIMARY_PT in all_ids

    def test_is_bridge_primary_true(self):
        assert is_bridge_primary(PRIMARY_PT)

    def test_is_bridge_primary_false_for_runtime_variant(self):
        assert not is_bridge_primary("quadratic_graph_vertex_axis_choice")

    def test_has_bridge_false_for_unknown(self):
        assert not has_bridge("totally_unknown_pt_xyz")

    def test_get_bridge_returns_none_for_unknown(self):
        assert get_bridge("totally_unknown_pt_xyz") is None


class TestRuntimeVariants:
    def test_variants_count_at_least_5(self):
        variants = get_runtime_variants(PRIMARY_PT)
        assert len(variants) >= 5, (
            f"Expected >=5 variants, got {len(variants)}: {[v.get('problem_type_id') for v in variants]}"
        )

    def test_all_expected_variants_present(self):
        variants = get_runtime_variants(PRIMARY_PT)
        pt_ids = {v["problem_type_id"] for v in variants}
        missing = EXPECTED_VARIANTS - pt_ids
        assert not missing, f"Missing variants: {missing}"

    def test_each_variant_has_required_fields(self):
        required_fields = [
            "problem_type_id",
            "presentation_mode",
            "answer_type",
            "checker_key",
            "equivalence_type",
            "template_slot",
        ]
        for v in get_runtime_variants(PRIMARY_PT):
            for field in required_fields:
                assert field in v, (
                    f"Variant {v.get('problem_type_id')} missing field {field}"
                )

    def test_text_short_variant_does_not_use_choice_checker(self):
        for v in get_runtime_variants(PRIMARY_PT):
            if v["answer_type"] in {"text_short", "short_answer"} or v["presentation_mode"] == "short_answer":
                assert v["checker_key"] != "choice_label_checker", (
                    f"text_short variant {v['problem_type_id']} uses choice_label_checker"
                )

    def test_choice_variant_does_not_use_text_short_checker(self):
        for v in get_runtime_variants(PRIMARY_PT):
            if v["presentation_mode"] == "single_choice" or v["answer_type"] in {"single_choice", "choice"}:
                assert v["checker_key"] != "text_short_checker", (
                    f"choice variant {v['problem_type_id']} uses text_short_checker"
                )


class TestExpandPrimary:
    def test_expand_returns_ok_with_5_variants(self):
        variants, status = expand_primary_to_runtime_variants(SKILL_ID, PRIMARY_PT, [4450, 4460])
        assert status == "ok", f"Expected 'ok', got {status!r}"
        assert len(variants) >= 5

    def test_each_expanded_variant_has_answer_contract(self):
        variants, _ = expand_primary_to_runtime_variants(SKILL_ID, PRIMARY_PT)
        for v in variants:
            ac = v.get("answer_contract")
            assert isinstance(ac, dict), f"Variant {v.get('problem_type_id')} missing answer_contract"
            assert "answer_type" in ac

    def test_each_expanded_variant_has_generator_contract(self):
        variants, _ = expand_primary_to_runtime_variants(SKILL_ID, PRIMARY_PT)
        for v in variants:
            gc = v.get("generator_contract")
            assert isinstance(gc, dict), f"Variant {v.get('problem_type_id')} missing generator_contract"

    def test_expanded_variants_carry_semantic_primary_id(self):
        variants, _ = expand_primary_to_runtime_variants(SKILL_ID, PRIMARY_PT)
        for v in variants:
            assert v.get("semantic_primary_problem_type_id") == PRIMARY_PT

    def test_expanded_variants_carry_source_bridge_problem_type_id(self):
        variants, _ = expand_primary_to_runtime_variants(SKILL_ID, PRIMARY_PT)
        for v in variants:
            assert v.get("source_bridge_problem_type_id") == PRIMARY_PT

    def test_expanded_variants_usable_for_phase3(self):
        variants, _ = expand_primary_to_runtime_variants(SKILL_ID, PRIMARY_PT)
        for v in variants:
            assert v.get("usable_for_phase3") is True

    def test_source_example_ids_propagated(self):
        ex_ids = [4450, 4460, 4466, 4503]
        variants, _ = expand_primary_to_runtime_variants(SKILL_ID, PRIMARY_PT, ex_ids)
        for v in variants:
            assert v.get("source_example_ids") == ex_ids

    def test_text_short_expanded_variant_answer_contract_is_text_short(self):
        variants, _ = expand_primary_to_runtime_variants(SKILL_ID, PRIMARY_PT)
        fill_blank = next(
            v for v in variants
            if v["problem_type_id"] == "quadratic_graph_translation_fill_blank"
        )
        ac = fill_blank["answer_contract"]
        assert ac["answer_type"] in {"text_short", "short_answer"}, (
            f"fill_blank answer_type={ac['answer_type']!r}"
        )
        assert ac["checker_key"] == "text_short_checker", (
            f"fill_blank checker_key={ac['checker_key']!r}"
        )

    def test_choice_expanded_variant_answer_contract_is_choice(self):
        variants, _ = expand_primary_to_runtime_variants(SKILL_ID, PRIMARY_PT)
        vtx_choice = next(
            v for v in variants
            if v["problem_type_id"] == "quadratic_graph_vertex_axis_choice"
        )
        ac = vtx_choice["answer_contract"]
        assert ac["answer_type"] in {"single_choice", "choice"}, (
            f"vertex_axis_choice answer_type={ac['answer_type']!r}"
        )
        assert ac["checker_key"] == "choice_label_checker", (
            f"vertex_axis_choice checker_key={ac['checker_key']!r}"
        )


class TestBridgeMissing:
    def test_missing_bridge_returns_bridge_missing_status(self):
        _, status = expand_primary_to_runtime_variants(SKILL_ID, "totally_unknown_pt_xyz")
        assert status == BRIDGE_MISSING

    def test_missing_bridge_returns_empty_variants(self):
        variants, _ = expand_primary_to_runtime_variants(SKILL_ID, "totally_unknown_pt_xyz")
        assert variants == []

    def test_missing_bridge_does_not_produce_contextual_application(self):
        variants, status = expand_primary_to_runtime_variants(
            SKILL_ID, "totally_unknown_pt_xyz"
        )
        if status != "ok":
            for v in variants:
                assert "contextual_application" not in v.get("problem_type_id", ""), (
                    f"contextual_application fallback produced for missing bridge"
                )

    def test_get_runtime_variants_returns_empty_for_missing(self):
        variants = get_runtime_variants("totally_unknown_pt_xyz")
        assert variants == []
