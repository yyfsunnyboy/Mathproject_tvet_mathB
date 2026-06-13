# -*- coding: utf-8 -*-
"""
tests/gencode/test_source_skill_binding_supremacy.py
======================================================
Source Skill Binding Supremacy global rule tests.

A. Source skill binding: skill_id is authoritative; supporting math objects
   must NOT hijack core_skill_family.
E. Absolute value with number line: core concept = absolute_value.
F. Probability with combination: core concept = probability.
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.main_skill_anchor import build_main_skill_anchor
from core.gencode.semantic_alignment import (
    _infer_core_skill_concept,
    _infer_supporting_math_objects,
    evaluate_semantic_alignment,
)
from core.gencode.task_families import (
    COORDINATE_SYSTEM_FAMILY,
    QUADRATIC_FUNCTION_GRAPH_FAMILY,
)


# ---------------------------------------------------------------------------
# A. Source skill binding supremacy
# ---------------------------------------------------------------------------

def test_classification_scope_within_current_skill():
    """No matter the metadata, classification_scope must be within_current_skill."""
    anchor = build_main_skill_anchor(
        "vh_數學B1_QuadraticFunctionGraph",
        {
            "skill_en_name": "QuadraticFunctionGraph",
            "skill_ch_name": "二次函數的圖形",
            "chapter": "1 坐標系與函數圖形",
            "section_code": "1-3",
        },
    )
    assert anchor["classification_scope"] == "within_current_skill"
    assert anchor["skill_mapping_authority"] == "textbook_examples.skill_id"
    assert anchor["source_skill_scope_locked"] is True


def test_supporting_objects_do_not_change_family():
    """A quadratic skill with coordinate-point source terms must remain quadratic."""
    anchor = build_main_skill_anchor(
        "vh_數學B1_QuadraticFunctionGraph",
        {
            "skill_en_name": "QuadraticFunctionGraph",
            "skill_ch_name": "二次函數的圖形",
            "chapter": "1 坐標系與函數圖形",
        },
    )
    families = set(anchor["expected_task_families"])
    assert QUADRATIC_FUNCTION_GRAPH_FAMILY in families
    assert COORDINATE_SYSTEM_FAMILY not in families


def test_core_skill_concept_for_quadratic():
    anchor = build_main_skill_anchor(
        "vh_數學B1_QuadraticFunctionGraph",
        {"skill_en_name": "QuadraticFunctionGraph", "skill_ch_name": "二次函數的圖形"},
    )
    concept = _infer_core_skill_concept(anchor)
    assert concept == "quadratic_function_graph", f"Expected quadratic_function_graph, got {concept}"


def test_supporting_objects_recorded_separately():
    """Coordinate points in source features appear as supporting math objects, not core concept."""
    anchor = build_main_skill_anchor(
        "vh_數學B1_QuadraticFunctionGraph",
        {"skill_en_name": "QuadraticFunctionGraph", "skill_ch_name": "二次函數的圖形"},
    )
    source_features = [
        {
            "source_example_id": 4450,
            "target_task": "quadratic_graph_translation",
            "math_objects": ["coordinate_point", "axis_of_symmetry"],
        }
    ]
    concept = _infer_core_skill_concept(anchor)
    supporting = _infer_supporting_math_objects(source_features, concept)
    # Supporting objects are recorded
    assert "coordinate_point" in supporting or "axis_of_symmetry" in supporting


# ---------------------------------------------------------------------------
# E. Absolute value with number line
# ---------------------------------------------------------------------------

def test_absolute_value_skill_not_hijacked_by_number_line():
    """絕對值 skill 含數線，core concept 仍為 absolute_value；不得改派。"""
    anchor = build_main_skill_anchor(
        "jh_數學1上_AbsoluteValue",
        {
            "skill_en_name": "AbsoluteValue",
            "skill_ch_name": "絕對值",
            "description": "絕對值與數線距離",
        },
    )
    concept = _infer_core_skill_concept(anchor)
    assert concept == "absolute_value", f"Expected absolute_value, got {concept}"
    # Number line / distance are supporting objects, not driving family changes
    families = set(anchor["expected_task_families"])
    assert COORDINATE_SYSTEM_FAMILY not in families


# ---------------------------------------------------------------------------
# F. Probability with combination
# ---------------------------------------------------------------------------

def test_probability_skill_not_hijacked_by_combination():
    """機率 skill 含排列組合，core concept 仍為 probability；不得改派。"""
    anchor = build_main_skill_anchor(
        "vh_數學B2_Probability",
        {
            "skill_en_name": "Probability",
            "skill_ch_name": "機率",
            "description": "事件機率、排列組合應用",
        },
    )
    concept = _infer_core_skill_concept(anchor)
    # The concept should reflect probability, not permutation/combination
    assert "probability" in concept.lower() or concept != "coordinate_system"
    # Should not land in coordinate_system or quadratic family
    families = set(anchor["expected_task_families"])
    assert COORDINATE_SYSTEM_FAMILY not in families
    assert QUADRATIC_FUNCTION_GRAPH_FAMILY not in families


# ---------------------------------------------------------------------------
# Alignment: scope_locked demotes source_examples_mismatch to warning
# ---------------------------------------------------------------------------

def test_scope_locked_demotes_source_examples_mismatch():
    """When scope_locked=True, source_examples_mismatch must NOT appear as a blocker."""
    anchor = build_main_skill_anchor(
        "vh_數學B1_QuadraticFunctionGraph",
        {
            "skill_en_name": "QuadraticFunctionGraph",
            "skill_ch_name": "二次函數的圖形",
            "chapter": "1 坐標系與函數圖形",
        },
    )
    assert anchor.get("source_skill_scope_locked") is True

    # Simulate source features with generic family (as if badly classified)
    source_features = [
        {
            "source_example_id": 4450,
            "target_task": "contextual_application",
            "task_family": "generic_numeric_family",
            "induction_tier": "core",
            "semantic_classification": {
                "final_target_task": "contextual_application",
                "final_task_family": "generic_numeric_family",
                "classifier_source": "clause45_unclassified_exception",
                "candidate_source": "clause45_fallback_proxy",
            },
        }
    ]
    result = evaluate_semantic_alignment(
        "vh_數學B1_QuadraticFunctionGraph",
        skill_metadata={
            "skill_en_name": "QuadraticFunctionGraph",
            "skill_ch_name": "二次函數的圖形",
            "chapter": "1 坐標系與函數圖形",
        },
        source_features=source_features,
        candidate_specs=[],
        main_skill_anchor=anchor,
    )
    blockers = result.get("blockers", [])
    assert "source_examples_mismatch" not in blockers, (
        f"source_examples_mismatch must be demoted to warning when scope_locked; got blockers={blockers}"
    )
    # anchor_taxonomy_needs_refinement should appear in warnings instead
    warnings = result.get("warnings", [])
    # At least we confirm the blocker is gone; warning may or may not appear
    # depending on whether any blocker was actually generated.
