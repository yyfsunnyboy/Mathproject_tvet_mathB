# -*- coding: utf-8 -*-
"""Regression tests for B2 §2-2-3 right-triangle measurement V3 capability."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from core.domain.trigonometry_right_triangle_measurement_domain import (
    OPS,
    build_trigonometry_right_triangle_measurement_matrix,
    solve_adjacent_from_hypotenuse_ground_angle,
    solve_broken_tree_original_height,
    solve_building_height_with_flagpole_elevations,
    solve_height_decimal_from_sight_line_elevation,
    solve_height_from_sight_line_elevation,
    solve_horizontal_from_height_and_angle,
    solve_opposite_from_adjacent_elevation,
    solve_two_elevation_horizontal_shift,
    solve_two_elevation_unknown_height,
    validate_trigonometry_right_triangle_measurement_matrix,
)
from core.gencode.b2_223_right_triangle_measurement_capability_adapter import (
    adapt_b2_223_right_triangle_measurement_matrix,
)
from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example
from core.gencode.services.v3_skill_capability_preflight_service import evaluate_skill_v3_capability
from core.registry.domain_operation_registry import check_registry_consistency, get_domain_spec
from core.registry.taxonomy_registry import resolve_domain_for_skill

SKILL = "vh_數學B2_SubSection_2_2_3"
ROOT = Path(__file__).resolve().parents[2]
PROD_DB = ROOT / "instance" / "kumon_math.db"


def test_registry_binding():
    routing = resolve_domain_for_skill(SKILL)
    assert routing["fixed_domain_key"] == "trigonometry.right_triangle_measurement"
    assert set(routing["allowed_operations"]) == set(OPS)
    assert check_registry_consistency() == []
    assert get_domain_spec("trigonometry.right_triangle_measurement") is not None


def test_textbook_exact_answers():
    assert solve_height_from_sight_line_elevation(sight_length=100, elevation_degrees=60)["canonical"] == "50*sqrt(3)"
    assert solve_adjacent_from_hypotenuse_ground_angle(hypotenuse=6, ground_angle_degrees=45)["canonical"] == "3*sqrt(2)"
    assert solve_adjacent_from_hypotenuse_ground_angle(hypotenuse=6, ground_angle_degrees=60)["canonical"] == "3"
    assert solve_opposite_from_adjacent_elevation(adjacent=60, elevation_degrees=30)["canonical"] == "20*sqrt(3)"
    assert solve_opposite_from_adjacent_elevation(adjacent=50, elevation_degrees=60)["canonical"] == "50*sqrt(3)"
    assert solve_horizontal_from_height_and_angle(height=300, angle_degrees=60)["canonical"] == "100*sqrt(3)"
    assert solve_horizontal_from_height_and_angle(height=508, angle_degrees=30)["canonical"] == "508*sqrt(3)"
    assert (
        solve_two_elevation_horizontal_shift(
            height=300, near_elevation_degrees=45, far_elevation_degrees=30
        )["canonical"]
        == "-300 + 300*sqrt(3)"
    )
    assert (
        solve_two_elevation_unknown_height(
            advance_distance=40, near_elevation_degrees=60, far_elevation_degrees=45
        )["canonical"]
        == "20*sqrt(3) + 60"
    )
    assert (
        solve_two_elevation_unknown_height(
            advance_distance=500, near_elevation_degrees=45, far_elevation_degrees=30
        )["canonical"]
        == "250 + 250*sqrt(3)"
    )
    assert (
        solve_building_height_with_flagpole_elevations(
            flagpole_length=20,
            building_top_elevation_degrees=45,
            flagpole_top_elevation_degrees=60,
        )["canonical"]
        == "10 + 10*sqrt(3)"
    )
    assert solve_broken_tree_original_height(tip_to_root=6, broken_angle_degrees=30)["canonical"] == "6*sqrt(3)"
    assert (
        solve_height_decimal_from_sight_line_elevation(sight_length=80, elevation_degrees=65, precision=3)[
            "canonical"
        ]
        == "72.505"
    )


@pytest.mark.parametrize("operation", sorted(OPS))
def test_matrix_validate_and_adapter(operation: str):
    matrix = build_trigonometry_right_triangle_measurement_matrix(operation=operation, seed=11)
    assert validate_trigonometry_right_triangle_measurement_matrix(matrix)
    payload = adapt_b2_223_right_triangle_measurement_matrix(matrix, domain_operation=operation, seed=11)
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
        assert len(rows) == 15
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

        for eid in (11687, 11689, 11690, 11698, 11704, 11720, 11723, 11728, 11729, 11730):
            induced = run_v3_no_llm_phase1_for_example(SKILL, by_id[eid], conn=conn)
            assert induced.get("classification_status") == "resolved", eid

        blocked = run_v3_no_llm_phase1_for_example(SKILL, by_id[11725], conn=conn)
        assert blocked.get("classification_status") == "unresolved"
        assert "BLOCKED" in str(blocked.get("reason") or "")

        preflight = evaluate_skill_v3_capability(conn, SKILL, probe_examples=True)
        assert preflight["domain_key"] == "trigonometry.right_triangle_measurement"
        assert preflight["capability_status"] == "partial"
        assert preflight["resolvable_example_count"] == 14
        assert preflight["unresolved_example_ids"] == [11725]
    finally:
        conn.close()
