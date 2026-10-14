# -*- coding: utf-8 -*-
"""Regression tests for B2 §2-2-5 solid measurement V3 capability."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
import sympy as sp

from core.domain.trigonometry_solid_measurement_domain import (
    OPS,
    build_trigonometry_solid_measurement_matrix,
    solve_height_from_isosceles_bearing_walk_elevation,
    solve_height_from_two_elevation_tan_ratios,
    solve_tower_two_elevation_path_and_river_width,
    validate_trigonometry_solid_measurement_matrix,
)
from core.gencode.b2_225_solid_measurement_capability_adapter import (
    adapt_b2_225_solid_measurement_matrix,
)
from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example
from core.gencode.services.v3_skill_capability_preflight_service import evaluate_skill_v3_capability
from core.registry.domain_operation_registry import check_registry_consistency, get_domain_spec
from core.registry.taxonomy_registry import resolve_domain_for_skill

SKILL = "vh_數學B2_SubSection_2_2_5"
ROOT = Path(__file__).resolve().parents[2]
PROD_DB = ROOT / "instance" / "kumon_math.db"


def test_registry_binding():
    routing = resolve_domain_for_skill(SKILL)
    assert routing["fixed_domain_key"] == "trigonometry.solid_measurement"
    assert set(routing["allowed_operations"]) == set(OPS)
    assert check_registry_consistency() == []
    assert get_domain_spec("trigonometry.solid_measurement") is not None


def test_textbook_answers_reuse_elevation_solvers():
    tower = solve_tower_two_elevation_path_and_river_width(
        tower_height=300, near_elevation_degrees=60, far_elevation_degrees=45
    )
    assert tower["canonical"] == {"AC": "100*sqrt(3)", "BC": "300", "AB": "100*sqrt(6)"}
    tan_h = solve_height_from_two_elevation_tan_ratios(
        advance_distance=31, far_tan=sp.Rational(3, 4), near_tan=sp.Rational(4, 3)
    )
    assert tan_h["canonical"] == "53"
    bearing = solve_height_from_isosceles_bearing_walk_elevation(
        walk_distance=200, base_bearing_degrees=60, elevation_degrees=45
    )
    assert bearing["canonical"] == "200"
    assert bearing["reused_elevation_solver"] is True


@pytest.mark.parametrize("operation", sorted(OPS))
def test_matrix_validate_and_adapter(operation: str):
    matrix = build_trigonometry_solid_measurement_matrix(operation=operation, seed=5)
    assert validate_trigonometry_solid_measurement_matrix(matrix)
    payload = adapt_b2_225_solid_measurement_matrix(matrix, domain_operation=operation, seed=5)
    assert payload.get("answer") is not None
    q = str(payload.get("question_text") or payload.get("question") or "")
    assert q and "placeholder" not in q.lower()


def test_phase1_and_preflight_readonly():
    if not PROD_DB.exists():
        pytest.skip("production db unavailable")
    conn = sqlite3.connect(f"file:{PROD_DB.resolve().as_posix()}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            "SELECT id, skill_id, problem_text, correct_answer, detailed_solution, source_description, problem_type, notes "
            "FROM textbook_examples WHERE skill_id=? ORDER BY id",
            (SKILL,),
        ).fetchall()
        assert len(rows) == 4
        cols = [
            "id",
            "skill_id",
            "problem_text",
            "correct_answer",
            "detailed_solution",
            "source_description",
            "problem_type",
            "notes",
        ]
        by_id = {int(r[0]): dict(zip(cols, r)) for r in rows}

        for eid in (11695, 11697, 11724):
            induced = run_v3_no_llm_phase1_for_example(SKILL, by_id[eid], conn=conn)
            assert induced.get("classification_status") == "resolved", eid

        blocked = run_v3_no_llm_phase1_for_example(SKILL, by_id[11696], conn=conn)
        assert blocked.get("classification_status") == "unresolved"
        assert "BLOCKED" in str(blocked.get("reason") or "")

        preflight = evaluate_skill_v3_capability(conn, SKILL, probe_examples=True)
        assert preflight["domain_key"] == "trigonometry.solid_measurement"
        assert preflight["capability_status"] == "partial"
        assert preflight["resolvable_example_count"] == 3
        assert preflight["unresolved_example_ids"] == [11696]
    finally:
        conn.close()
