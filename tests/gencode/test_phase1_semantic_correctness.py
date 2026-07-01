# -*- coding: utf-8 -*-
"""Semantic correctness tests for Phase 1 skills."""
from __future__ import annotations

import sqlite3
from pathlib import Path
import pytest

from core.registry.taxonomy_registry import resolve_domain_for_skill
from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"

EXPECTED_SEMANTICS = {
    "vh_數學B1_CartesianCoordinateSystemEstablishment": {
        "domain": "coordinate_geometry.line_equation",
        "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
        "capability": "cartesian_coordinate_quadrant_symbol_reasoning",
    },
    "vh_數學B1_LinearFunction": {
        "domain": "coordinate_geometry.line_equation",
        "problem_type_id": "integer_numeric_evaluate_function_notation",
        "capability": "integer_numeric_evaluate_function_notation",
    },
    "vh_數學B1_QuadraticFunctionGraph": {
        "domain": "coordinate_geometry.line_equation",
        "problem_type_id": "text_short_compute_vertex_and_axis",
        "capability": "text_short_compute_vertex_and_axis",
    },
    "vh_數學B1_SlopeOfALine": {
        "domain": "coordinate_geometry.line_equation",
        "problem_type_id": "text_short_slope_of_line_problems",
        "capability": "text_short_slope_of_line_problems",
    },
    "vh_數學B1_PropertiesOfParallelLines": {
        "domain": "coordinate_geometry.line_equation",
        "problem_type_id": "parallel_lines_properties",
        "capability": "parallel_lines_properties",
    },
    "vh_數學B1_PropertiesOfPerpendicularLines": {
        "domain": "coordinate_geometry.line_equation",
        "problem_type_id": "perpendicular_lines_properties",
        "capability": "perpendicular_lines_properties",
    },
    "vh_數學B1_DistanceBetweenTwoPointsInPlane": {
        "domain": "coordinate_geometry.line_equation",
        "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
        "capability": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    },
}


def test_skills_semantic_properties() -> None:
    """Verify that resolved domain, problem_type_id, and capabilities match math semantics."""
    assert DB_PATH.is_file(), f"Database file missing: {DB_PATH}"
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    try:
        for skill_id, expected in EXPECTED_SEMANTICS.items():
            # 1. Verify Taxonomy Domain Mapping
            routing = resolve_domain_for_skill(skill_id)
            assert routing.get("fixed_domain_key") == expected["domain"], (
                f"Skill {skill_id} mapped to wrong domain: "
                f"expected {expected['domain']}, got {routing.get('fixed_domain_key')}"
            )
            
            # 2. Query a sample example from the database
            rows = conn.execute(
                "SELECT * FROM textbook_examples WHERE skill_id=? LIMIT 1",
                (skill_id,)
            ).fetchall()
            assert rows, f"No textbook examples found for skill: {skill_id}"
            
            # 3. Verify Phase 1 Induction Semantics
            row = dict(rows[0])
            res = run_v3_no_llm_phase1_for_example(skill_id, row, conn=conn)
            
            assert res.get("classification_status") == "resolved", (
                f"Skill {skill_id}: Classification failed"
            )
            assert res.get("problem_type_id") == expected["problem_type_id"], (
                f"Skill {skill_id} resolved to wrong problem_type_id: "
                f"expected {expected['problem_type_id']}, got {res.get('problem_type_id')}"
            )
            assert expected["capability"] in (res.get("required_capabilities") or []), (
                f"Skill {skill_id} resolved without expected capability {expected['capability']}"
            )
            
    finally:
        conn.close()
