# -*- coding: utf-8 -*-
"""Regression tests for B2 §2-2-4 oblique-triangle measurement composition."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from core.domain.trigonometry_law_of_cosines_domain import solve_side_by_law_of_cosines
from core.domain.trigonometry_law_of_sines_domain import solve_side_by_law_of_sines
from core.domain.trigonometry_oblique_triangle_measurement_domain import (
    OPS,
    build_trigonometry_oblique_triangle_measurement_matrix,
    validate_trigonometry_oblique_triangle_measurement_matrix,
)
from core.gencode.b2_224_oblique_triangle_measurement_capability_adapter import (
    adapt_b2_224_oblique_triangle_measurement_matrix,
)
from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example
from core.gencode.services.v3_skill_capability_preflight_service import evaluate_skill_v3_capability
from core.registry.domain_operation_registry import check_registry_consistency, get_domain_spec
from core.registry.taxonomy_registry import resolve_domain_for_skill

SKILL = "vh_數學B2_SubSection_2_2_4"
ROOT = Path(__file__).resolve().parents[2]
PROD_DB = ROOT / "instance" / "kumon_math.db"


def test_registry_binding_reuses_sines_cosines_ops():
    routing = resolve_domain_for_skill(SKILL)
    assert routing["fixed_domain_key"] == "trigonometry.oblique_triangle_measurement"
    assert set(routing["allowed_operations"]) == set(OPS)
    assert check_registry_consistency() == []
    assert get_domain_spec("trigonometry.oblique_triangle_measurement") is not None
    # Underlying domains still exist independently.
    assert get_domain_spec("trigonometry.law_of_sines") is not None
    assert get_domain_spec("trigonometry.law_of_cosines") is not None


def test_textbook_answers_via_reused_solvers():
    assert solve_side_by_law_of_sines(known_side="sqrt(2)", known_angle_degrees=30, target_angle_degrees=45)["canonical"] == "2"
    assert solve_side_by_law_of_sines(known_side=50, known_angle_degrees=45, target_angle_degrees=60)["canonical"] == "25*sqrt(6)"
    assert solve_side_by_law_of_cosines(side_b=500, side_c=300, included_angle_degrees=120)["canonical"] == "700"
    assert solve_side_by_law_of_cosines(side_b=20, side_c=30, included_angle_degrees=60)["canonical"] == "10*sqrt(7)"
    assert solve_side_by_law_of_sines(known_side="4*sqrt(3)", known_angle_degrees=60, target_angle_degrees=45)["canonical"] == "4*sqrt(2)"
    assert solve_side_by_law_of_cosines(side_b=3, side_c=5, included_angle_degrees=120)["canonical"] == "7"
    assert solve_side_by_law_of_cosines(side_b=500, side_c=800, included_angle_degrees=60)["canonical"] == "700"
    assert solve_side_by_law_of_sines(known_side="20*sqrt(6)", known_angle_degrees=45, target_angle_degrees=60)["canonical"] == "60"


@pytest.mark.parametrize("operation", sorted(OPS))
def test_facade_delegates_and_adapts(operation: str):
    matrix = build_trigonometry_oblique_triangle_measurement_matrix(operation=operation, seed=7)
    assert validate_trigonometry_oblique_triangle_measurement_matrix(matrix)
    assert matrix["validation_facts"]["cross_domain_delegate"] in {
        "trigonometry.law_of_sines",
        "trigonometry.law_of_cosines",
    }
    payload = adapt_b2_224_oblique_triangle_measurement_matrix(matrix, domain_operation=operation, seed=7)
    assert payload.get("answer") is not None
    assert payload.get("fixed_domain_key") == "trigonometry.oblique_triangle_measurement"
    assert (payload.get("answer_contract") or {}).get("fixed_domain_key") == "trigonometry.oblique_triangle_measurement"
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
        assert len(rows) == 9
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

        for eid in (11691, 11692, 11693, 11694, 11702, 11703, 11721, 11722):
            induced = run_v3_no_llm_phase1_for_example(SKILL, by_id[eid], conn=conn)
            assert induced.get("classification_status") == "resolved", eid

        blocked = run_v3_no_llm_phase1_for_example(SKILL, by_id[11705], conn=conn)
        assert blocked.get("classification_status") == "unresolved"
        assert "BLOCKED" in str(blocked.get("reason") or "")

        preflight = evaluate_skill_v3_capability(conn, SKILL, probe_examples=True)
        assert preflight["domain_key"] == "trigonometry.oblique_triangle_measurement"
        assert preflight["capability_status"] == "partial"
        assert preflight["resolvable_example_count"] == 8
        assert preflight["unresolved_example_ids"] == [11705]
    finally:
        conn.close()
