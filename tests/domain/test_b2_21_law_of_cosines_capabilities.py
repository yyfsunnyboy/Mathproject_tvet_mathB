# -*- coding: utf-8 -*-
"""Regression tests for B2 §2-1-2 Law of Cosines V3 capability."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from core.domain.trigonometry_law_of_cosines_domain import (
    OPS,
    build_trigonometry_law_of_cosines_matrix,
    compute_circumradius_from_three_sides,
    solve_angle_by_law_of_cosines,
    solve_cosine_identity_angle,
    solve_detour_extra_distance_by_cosines,
    solve_side_by_law_of_cosines,
    validate_trigonometry_law_of_cosines_matrix,
)
from core.gencode.b2_21_law_of_cosines_capability_adapter import adapt_b2_21_law_of_cosines_matrix
from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example
from core.gencode.services.v3_skill_capability_preflight_service import evaluate_skill_v3_capability
from core.registry.domain_operation_registry import check_registry_consistency, get_domain_spec
from core.registry.taxonomy_registry import resolve_domain_for_skill

SKILL = "vh_數學B2_SubSection_2_1_2"
ROOT = Path(__file__).resolve().parents[2]
PROD_DB = ROOT / "instance" / "kumon_math.db"


def test_registry_binding_no_sine_ops():
    routing = resolve_domain_for_skill(SKILL)
    assert routing["fixed_domain_key"] == "trigonometry.law_of_cosines"
    assert set(routing["allowed_operations"]) == set(OPS)
    assert not any(
        op.endswith("_sines") or "law_of_sines" in op or op.startswith("compute_sin")
        for op in routing["allowed_operations"]
    )
    assert check_registry_consistency() == []
    assert get_domain_spec("trigonometry.law_of_cosines") is not None


def test_textbook_exact_answers():
    assert solve_side_by_law_of_cosines(side_b=5, side_c=3, included_angle_degrees=120)["canonical"] == "7"
    assert solve_side_by_law_of_cosines(side_b="1+sqrt(3)", side_c=2, included_angle_degrees=30)["canonical"] == "sqrt(2)"
    assert solve_angle_by_law_of_cosines(side_a=7, side_b=5, side_c=3, find="A")["canonical"] == "120"
    assert solve_angle_by_law_of_cosines(side_a=3, side_b=8, side_c=7, find="C")["canonical"] == "60"
    assert solve_detour_extra_distance_by_cosines(direct_side=300, first_leg=800, included_angle_degrees=60)["canonical"] == "1200"
    assert solve_cosine_identity_angle()["canonical"] == "120"
    assert solve_side_by_law_of_cosines(side_b=3, side_c=4, included_angle_degrees=60)["canonical"] == "sqrt(13)"
    assert solve_side_by_law_of_cosines(side_b=3, side_c=5, included_angle_degrees=60)["canonical"] == "sqrt(19)"
    assert compute_circumradius_from_three_sides(side_a=50, side_b=70, side_c=80)["canonical"] == "70*sqrt(3)/3"
    assert solve_angle_by_law_of_cosines(side_a=7, side_b=8, side_c=5, find="A")["canonical"] == "60"


@pytest.mark.parametrize("operation", sorted(OPS))
def test_matrix_validate_and_adapter(operation: str):
    matrix = build_trigonometry_law_of_cosines_matrix(operation=operation, seed=17)
    assert validate_trigonometry_law_of_cosines_matrix(matrix)
    payload = adapt_b2_21_law_of_cosines_matrix(matrix, domain_operation=operation, seed=17)
    assert payload.get("answer") is not None
    q = str(payload.get("question_text") or payload.get("question") or "")
    assert q and "placeholder" not in q.lower()
    assert "正弦定理" not in q
    assert "a/\\sin" not in q.replace(" ", "")


def test_json_givens_roundtrip_for_extra_path():
    """Regression: distractors must accept JSON-serialized numeric givens (str)."""
    matrix = build_trigonometry_law_of_cosines_matrix(
        operation="solve_detour_extra_distance_by_cosines",
        seed=0,
    )
    rebuilt = build_trigonometry_law_of_cosines_matrix(
        operation="solve_detour_extra_distance_by_cosines",
        **matrix["givens"],
    )
    assert rebuilt["answer"] == matrix["answer"]


def test_phase1_and_preflight_readonly():
    if not PROD_DB.exists():
        pytest.skip("production db unavailable")
    conn = sqlite3.connect(f"file:{PROD_DB.resolve().as_posix()}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            "SELECT id, skill_id, problem_text, correct_answer, detailed_solution, source_description, problem_type, notes FROM textbook_examples WHERE skill_id=? ORDER BY id",
            (SKILL,),
        ).fetchall()
        assert len(rows) == 14
        cols = ["id", "skill_id", "problem_text", "correct_answer", "detailed_solution", "source_description", "problem_type", "notes"]
        by_id = {int(r[0]): dict(zip(cols, r)) for r in rows}

        for eid in (11682, 11684, 11686, 11711, 11713, 11714, 11715, 11727):
            induced = run_v3_no_llm_phase1_for_example(SKILL, by_id[eid], conn=conn)
            assert induced.get("classification_status") == "resolved"

        for eid in (11706, 11726):
            blocked = run_v3_no_llm_phase1_for_example(SKILL, by_id[eid], conn=conn)
            assert blocked.get("classification_status") == "unresolved"
            assert "BLOCKED" in str(blocked.get("reason") or "")

        preflight = evaluate_skill_v3_capability(conn, SKILL, probe_examples=True)
        assert preflight["domain_key"] == "trigonometry.law_of_cosines"
        assert preflight["capability_status"] == "partial"
        assert preflight["resolvable_example_count"] == 12
        assert preflight["unresolved_example_ids"] == [11706, 11726]
    finally:
        conn.close()


def test_published_generator_smoke_if_present():
    root = ROOT / "agent_skills_v3" / SKILL / "components"
    if not root.exists():
        pytest.skip("published components not present")
    comps = sorted(p for p in root.iterdir() if (p / "generate.py").is_file())
    assert len(comps) >= 6
    import importlib.util

    for comp in comps[:3]:
        spec = importlib.util.spec_from_file_location(f"pub_{comp.name}", comp / "generate.py")
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        a = mod.generate(seed=3, component_id=comp.name)
        b = mod.generate(seed=3, component_id=comp.name)
        assert a["answer"] == b["answer"]
        q = str(a.get("question_text") or a.get("question") or "")
        assert q and "placeholder" not in q.lower()
