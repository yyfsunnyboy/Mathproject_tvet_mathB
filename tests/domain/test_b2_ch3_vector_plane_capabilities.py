# -*- coding: utf-8 -*-
"""Regression tests for B2 Chapter 3 plane-vector V3 capability."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from core.domain.vector_plane_domain import (
    OPS,
    build_vector_plane_matrix,
    compute_directed_segment_and_magnitude,
    compute_dot_product_coordinates,
    compute_vector_components_and_magnitude,
    solve_equal_vector_coordinates,
    solve_parallelogram_fourth_vertex,
    solve_parallel_vector_parameter,
    solve_perpendicular_vector_parameter,
    validate_vector_plane_matrix,
)
from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example
from core.gencode.services.v3_skill_capability_preflight_service import evaluate_skill_v3_capability
from core.gencode.vector_plane_capability_adapter import adapt_vector_plane_matrix
from core.registry.domain_operation_registry import check_registry_consistency, get_domain_spec
from core.registry.taxonomy_registry import resolve_domain_for_skill

SKILL_COORD = "vh_數學B2_SubSection_3_2_1"
ROOT = Path(__file__).resolve().parents[2]
PROD_DB = ROOT / "instance" / "kumon_math.db"


def test_registry_and_taxonomy_binding():
    routing = resolve_domain_for_skill(SKILL_COORD)
    assert routing["fixed_domain_key"] == "vector.plane"
    assert routing["domain_module"] == "core.domain.vector_plane_domain"
    assert "compute_vector_components_and_magnitude" in routing["allowed_operations"]
    spec = get_domain_spec("vector.plane")
    assert spec is not None
    assert set(spec.allowed_operations) == set(OPS)
    assert check_registry_consistency() == []


def test_exact_textbook_oracles():
    assert compute_vector_components_and_magnitude(vector=[-3, 4])["canonical_magnitude"] == "5"
    assert solve_equal_vector_coordinates(left=["x+2", -5], right=[5, "y-1"])["canonical"] == {
        "x": "3",
        "y": "-4",
    }
    assert solve_equal_vector_coordinates(left=["x-y", "x+y"], right=[4, 6])["canonical"] == {
        "x": "5",
        "y": "1",
    }
    seg = compute_directed_segment_and_magnitude(start=[4, 8], end=[-1, 20])
    assert seg["canonical_vector"] == "(-5, 12)"
    assert seg["canonical_magnitude"] == "13"
    assert solve_parallelogram_fourth_vertex(a=[2, 3], b=[-1, 2], c=[1, 1])["canonical"] == "(4, 2)"
    assert solve_parallel_vector_parameter(a=[2, -1], b=["k", 3])["canonical"] == "-6"
    assert compute_dot_product_coordinates(a=[-1, -2], b=[3, 4])["canonical"] == "-11"
    # Textbook 11791 has two roots.
    perp = solve_perpendicular_vector_parameter(a=["k", 3], b=["k+2", -1])
    assert set(perp["canonical"] if isinstance(perp["canonical"], list) else [perp["canonical"]]) == {
        "-3",
        "1",
    }


@pytest.mark.parametrize("operation", sorted(OPS))
def test_matrix_validate_and_adapter(operation: str):
    matrix = build_vector_plane_matrix(operation=operation, seed=21)
    assert validate_vector_plane_matrix(matrix)
    payload = adapt_vector_plane_matrix(matrix, domain_operation=operation, seed=21)
    assert isinstance(payload, dict)
    assert payload.get("answer") is not None
    q = str(payload.get("question_text") or payload.get("question") or "")
    assert q and "placeholder" not in q.lower()


@pytest.mark.parametrize("seed", list(range(8)))
@pytest.mark.parametrize(
    "operation",
    [
        "compute_vector_components_and_magnitude",
        "solve_equal_vector_coordinates",
        "compute_directed_segment_and_magnitude",
        "solve_parallelogram_fourth_vertex",
        "compute_vector_sum_difference",
        "compute_dot_product_coordinates",
        "solve_parallel_vector_parameter",
        "compute_unit_vector",
    ],
)
def test_randomized_generation_stable(operation: str, seed: int):
    a = adapt_vector_plane_matrix(
        build_vector_plane_matrix(operation=operation, seed=seed),
        domain_operation=operation,
        seed=seed,
    )
    b = adapt_vector_plane_matrix(
        build_vector_plane_matrix(operation=operation, seed=seed),
        domain_operation=operation,
        seed=seed,
    )
    assert a["answer"] == b["answer"]
    assert str(a.get("question_text") or a.get("question") or "")


def test_phase1_and_preflight_coordinate_skill():
    if not PROD_DB.exists():
        pytest.skip("production db unavailable")
    conn = sqlite3.connect(f"file:{PROD_DB.resolve().as_posix()}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            "SELECT id, skill_id, problem_text, correct_answer, detailed_solution, "
            "source_description, problem_type, notes FROM textbook_examples "
            "WHERE skill_id=? ORDER BY id",
            (SKILL_COORD,),
        ).fetchall()
        assert len(rows) == 11
        by_id = {
            int(r[0]): dict(
                zip(
                    [
                        "id",
                        "skill_id",
                        "problem_text",
                        "correct_answer",
                        "detailed_solution",
                        "source_description",
                        "problem_type",
                        "notes",
                    ],
                    r,
                )
            )
            for r in rows
        }
        for eid in (11754, 11756, 11758, 11760, 11822):
            induced = run_v3_no_llm_phase1_for_example(SKILL_COORD, by_id[eid], conn=conn)
            assert induced.get("classification_status") == "resolved"
            assert induced.get("problem_type_id")
        blocked = run_v3_no_llm_phase1_for_example(SKILL_COORD, by_id[11775], conn=conn)
        assert blocked.get("classification_source") == "phase1_rule_pack_blocked"

        preflight = evaluate_skill_v3_capability(conn, SKILL_COORD, probe_examples=True)
        assert preflight["domain_key"] == "vector.plane"
        assert preflight["capability_status"] == "ready"
        assert preflight["resolvable_example_count"] == 10
        assert preflight["needs_capability_count"] == 0
        assert 11775 in (preflight.get("intentional_skip_ids") or [])
    finally:
        conn.close()


def test_diagram_skills_are_intentional_skip_not_fake_eligible():
    if not PROD_DB.exists():
        pytest.skip("production db unavailable")
    conn = sqlite3.connect(f"file:{PROD_DB.resolve().as_posix()}?mode=ro", uri=True)
    try:
        sid = "vh_數學B2_SubSection_3_1_1"
        preflight = evaluate_skill_v3_capability(conn, sid, probe_examples=True)
        assert preflight["domain_key"] == "vector.plane"
        assert preflight["capability_status"] == "ready"
        assert preflight["resolvable_example_count"] == 0
        assert preflight["intentional_skip_count"] == 3
        assert preflight["needs_capability_count"] == 0
    finally:
        conn.close()
