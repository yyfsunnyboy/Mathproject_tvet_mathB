# -*- coding: utf-8 -*-
"""
tests/gencode/test_phase1_quadratic_function_graph_regression.py
================================================================
Regression test for vh_數學B1_QuadraticFunctionGraph Phase 1 anchor.

Ensures the complete infer_skill_families_from_terms + build_main_skill_anchor
pipeline no longer misclassifies quadratic function graph skills as
coordinate_system_family due to chapter background terms.
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.main_skill_anchor import build_main_skill_anchor
from core.gencode.semantic_alignment import extract_skill_terms, _infer_core_skill_concept
from core.gencode.task_families import (
    COORDINATE_SYSTEM_FAMILY,
    FUNCTION_CONCEPT_FAMILY,
    QUADRATIC_FUNCTION_GRAPH_FAMILY,
    infer_skill_families_from_terms,
    infer_skill_families,
)


SKILL_ID = "vh_數學B1_QuadraticFunctionGraph"

META = {
    "skill_id": SKILL_ID,
    "skill_en_name": "QuadraticFunctionGraph",
    "skill_ch_name": "二次函數的圖形",
    "category": "1-3 二次函數",
    "description": "數學B1 1 坐標系與函數圖形 1-3 二次函數 - 二次函數的圖形",
    "chapter": "1 坐標系與函數圖形",
    "section_code": "1-3",
}

BAD_COORDINATE_SUBSKILLS = frozenset({
    "classify_quadrant",
    "choose_possible_coordinate",
    "compute_axis_distance",
})

EXPECTED_QUADRATIC_SUBSKILLS = frozenset({
    "quadratic_graph_translation",
    "quadratic_vertex_axis_identification",
    "quadratic_graph_properties_choice",
    "quadratic_standard_to_vertex_properties",
})


# ---------------------------------------------------------------------------
# Family inference via task_families.py
# ---------------------------------------------------------------------------

def test_infer_skill_families_from_terms_quadratic():
    """infer_skill_families_from_terms must return quadratic family for quadratic skill terms."""
    terms = {"QuadraticFunctionGraph", "二次函數的圖形", "quadratic", "二次函數"}
    families = infer_skill_families_from_terms(terms)
    assert QUADRATIC_FUNCTION_GRAPH_FAMILY in families, (
        f"Expected quadratic_function_graph_family in {families}"
    )


def test_infer_skill_families_coordinate_system_absent_for_quadratic():
    """When quadratic hints are present, coordinate_system_family must be excluded."""
    terms = {"QuadraticFunctionGraph", "二次函數的圖形", "坐標系", "coordinate system"}
    families = infer_skill_families_from_terms(terms)
    assert QUADRATIC_FUNCTION_GRAPH_FAMILY in families
    assert COORDINATE_SYSTEM_FAMILY not in families, (
        "coordinate_system_family must be discarded when quadratic family dominates"
    )


# ---------------------------------------------------------------------------
# Full anchor build
# ---------------------------------------------------------------------------

def test_anchor_families_contain_quadratic():
    anchor = build_main_skill_anchor(SKILL_ID, META)
    families = set(anchor["expected_task_families"])
    assert QUADRATIC_FUNCTION_GRAPH_FAMILY in families


def test_anchor_families_exclude_coordinate_system():
    anchor = build_main_skill_anchor(SKILL_ID, META)
    families = set(anchor["expected_task_families"])
    assert COORDINATE_SYSTEM_FAMILY not in families, (
        f"coordinate_system_family must not be in anchor.expected_task_families; got {families}"
    )


def test_anchor_subskills_contain_quadratic_tasks():
    anchor = build_main_skill_anchor(SKILL_ID, META)
    candidates = set(anchor["expected_subskill_candidates"])
    missing = EXPECTED_QUADRATIC_SUBSKILLS - candidates
    assert not missing, f"Missing quadratic subskill candidates: {missing}"


def test_anchor_subskills_exclude_coordinate_tasks():
    anchor = build_main_skill_anchor(SKILL_ID, META)
    candidates = set(anchor["expected_subskill_candidates"])
    bad = candidates & BAD_COORDINATE_SUBSKILLS
    assert not bad, (
        f"Coordinate-system subskills must not appear in quadratic anchor: {bad}"
    )


# ---------------------------------------------------------------------------
# Core skill concept
# ---------------------------------------------------------------------------

def test_core_skill_concept_is_quadratic():
    anchor = build_main_skill_anchor(SKILL_ID, META)
    concept = _infer_core_skill_concept(anchor)
    assert concept == "quadratic_function_graph", (
        f"core_skill_concept must be 'quadratic_function_graph', got '{concept}'"
    )


# ---------------------------------------------------------------------------
# Scope lock fields
# ---------------------------------------------------------------------------

def test_scope_lock_fields():
    anchor = build_main_skill_anchor(SKILL_ID, META)
    assert anchor["source_skill_scope_locked"] is True
    assert anchor["classification_scope"] == "within_current_skill"
    assert anchor["skill_mapping_authority"] == "textbook_examples.skill_id"
    assert anchor["source_skill_id"] == SKILL_ID


# ---------------------------------------------------------------------------
# Skill terms include quadratic signals even when chapter contains 坐標系
# ---------------------------------------------------------------------------

def test_skill_terms_include_quadratic_tokens():
    terms = extract_skill_terms(SKILL_ID, META)
    blob = " ".join(terms).lower()
    # Must contain quadratic-related tokens from skill_en_name or skill_ch_name
    quadratic_signals = ["quadratic", "二次", "graph"]
    found = [s for s in quadratic_signals if s in blob]
    assert found, (
        f"skill_terms must contain quadratic signals; blob snippet: {blob[:200]}"
    )
