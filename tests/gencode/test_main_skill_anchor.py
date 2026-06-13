# -*- coding: utf-8 -*-
"""
tests/gencode/test_main_skill_anchor.py
=========================================
Tests for main_skill_anchor.py:
  - quadratic_function_graph_family anti-hijack (requirement §8)
  - linear function anti-hijack preserved
  - genuine coordinate system skill still works
  - source_skill_scope_locked always emitted
  - classification_scope / skill_mapping_authority fields present
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.main_skill_anchor import build_main_skill_anchor
from core.gencode.task_families import (
    COORDINATE_SYSTEM_FAMILY,
    FUNCTION_CONCEPT_FAMILY,
    QUADRATIC_FUNCTION_GRAPH_FAMILY,
)


# ---------------------------------------------------------------------------
# Test B: QuadraticFunctionGraph regression
# ---------------------------------------------------------------------------

QUAD_META = {
    "skill_id": "vh_數學B1_QuadraticFunctionGraph",
    "skill_en_name": "QuadraticFunctionGraph",
    "skill_ch_name": "二次函數的圖形",
    "category": "1-3 二次函數",
    "description": "數學B1 1 坐標系與函數圖形 1-3 二次函數 - 二次函數的圖形",
    "chapter": "1 坐標系與函數圖形",
    "section_code": "1-3",
}


def test_quadratic_family_present():
    anchor = build_main_skill_anchor("vh_數學B1_QuadraticFunctionGraph", QUAD_META)
    families = set(anchor["expected_task_families"])
    assert QUADRATIC_FUNCTION_GRAPH_FAMILY in families, (
        "expected_task_families must include quadratic_function_graph_family"
    )


def test_coordinate_system_family_removed_for_quadratic():
    anchor = build_main_skill_anchor("vh_數學B1_QuadraticFunctionGraph", QUAD_META)
    families = set(anchor["expected_task_families"])
    assert COORDINATE_SYSTEM_FAMILY not in families, (
        "coordinate_system_family must not appear as anchor for a quadratic function graph skill"
    )


def test_quadratic_subskill_candidates_not_coordinate():
    anchor = build_main_skill_anchor("vh_數學B1_QuadraticFunctionGraph", QUAD_META)
    bad_subskills = {"classify_quadrant", "choose_possible_coordinate", "compute_axis_distance"}
    got = set(anchor["expected_subskill_candidates"])
    overlap = got & bad_subskills
    assert not overlap, (
        f"expected_subskill_candidates must not contain coordinate-system subskills {overlap}"
    )


def test_quadratic_subskill_candidates_present():
    anchor = build_main_skill_anchor("vh_數學B1_QuadraticFunctionGraph", QUAD_META)
    got = set(anchor["expected_subskill_candidates"])
    expected_quadratic = {
        "quadratic_graph_translation",
        "quadratic_vertex_axis_identification",
        "quadratic_graph_properties_choice",
        "quadratic_standard_to_vertex_properties",
    }
    missing = expected_quadratic - got
    assert not missing, f"Missing quadratic subskills: {missing}"


# ---------------------------------------------------------------------------
# Test C: Genuine coordinate system still works
# ---------------------------------------------------------------------------

COORD_META = {
    "skill_id": "vh_數學1上_CartesianCoordinateSystem",
    "skill_en_name": "CartesianCoordinateSystem",
    "skill_ch_name": "平面直角坐標系",
    "category": "坐標系",
    "description": "平面直角坐標系、象限、坐標軸、點坐標",
    "chapter": "平面直角坐標系",
    "section_code": "1-1",
}


def test_genuine_coordinate_system_family():
    anchor = build_main_skill_anchor("vh_數學1上_CartesianCoordinateSystem", COORD_META)
    families = set(anchor["expected_task_families"])
    assert COORDINATE_SYSTEM_FAMILY in families or "classify_quadrant_family" in families, (
        "Genuine coordinate system skill must include coordinate_system_family or classify_quadrant_family"
    )


def test_genuine_coordinate_system_no_quadratic():
    anchor = build_main_skill_anchor("vh_數學1上_CartesianCoordinateSystem", COORD_META)
    families = set(anchor["expected_task_families"])
    assert QUADRATIC_FUNCTION_GRAPH_FAMILY not in families


# ---------------------------------------------------------------------------
# Test D: Linear function anti-hijack preserved
# ---------------------------------------------------------------------------

LINEAR_META = {
    "skill_id": "jh_數學1上_FourArithmeticOperationsOfNumbers",
    "skill_en_name": "LinearFunction",
    "skill_ch_name": "線型函數",
    "category": "一次函數",
    "description": "線型函數 y=kx+b 的圖形",
    "chapter": "函數與圖形",
    "section_code": "3-2",
}


def test_linear_function_not_hijacked_by_coordinate_system():
    anchor = build_main_skill_anchor("jh_數學1上_LinearFunction", LINEAR_META)
    families = set(anchor["expected_task_families"])
    assert FUNCTION_CONCEPT_FAMILY in families
    assert COORDINATE_SYSTEM_FAMILY not in families


def test_linear_function_not_hijacked_by_quadratic():
    anchor = build_main_skill_anchor("jh_數學1上_LinearFunction", LINEAR_META)
    families = set(anchor["expected_task_families"])
    assert QUADRATIC_FUNCTION_GRAPH_FAMILY not in families


# ---------------------------------------------------------------------------
# Source Skill Binding Supremacy §3: scope lock fields always present
# ---------------------------------------------------------------------------

def test_source_skill_scope_locked_present():
    anchor = build_main_skill_anchor("vh_數學B1_QuadraticFunctionGraph", QUAD_META)
    assert anchor.get("source_skill_scope_locked") is True
    assert anchor.get("classification_scope") == "within_current_skill"
    assert anchor.get("skill_mapping_authority") == "textbook_examples.skill_id"
    assert anchor.get("source_skill_id") == "vh_數學B1_QuadraticFunctionGraph"
