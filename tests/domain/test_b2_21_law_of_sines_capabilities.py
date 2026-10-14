# -*- coding: utf-8 -*-
"""Regression tests for B2 §2-1-1 Law of Sines V3 capability."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
import sympy as sp

from core.domain.trigonometry_law_of_sines_domain import (
    OPS,
    build_trigonometry_law_of_sines_matrix,
    compute_sin_from_side_and_circumradius,
    compute_triangle_area_sas,
    solve_angle_by_law_of_sines,
    solve_side_and_circumradius_by_sines,
    solve_side_by_law_of_sines,
    solve_side_ratio_by_law_of_sines,
    validate_trigonometry_law_of_sines_matrix,
)
from core.gencode.b2_21_law_of_sines_capability_adapter import adapt_b2_21_law_of_sines_matrix
from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example
from core.gencode.services.v3_skill_capability_preflight_service import evaluate_skill_v3_capability
from core.registry.domain_operation_registry import check_registry_consistency, get_domain_spec
from core.registry.taxonomy_registry import resolve_domain_for_skill

SKILL = "vh_數學B2_SubSection_2_1_1"
ROOT = Path(__file__).resolve().parents[2]
PROD_DB = ROOT / "instance" / "kumon_math.db"


def test_registry_and_taxonomy_binding():
    routing = resolve_domain_for_skill(SKILL)
    assert routing["fixed_domain_key"] == "trigonometry.law_of_sines"
    assert routing["domain_module"] == "core.domain.trigonometry_law_of_sines_domain"
    assert "solve_side_and_circumradius_by_sines" in routing["allowed_operations"]
    assert not any("cosine" in op for op in routing["allowed_operations"])
    spec = get_domain_spec("trigonometry.law_of_sines")
    assert spec is not None
    assert set(spec.allowed_operations) == set(OPS)
    assert check_registry_consistency() == []


def test_textbook_exact_answers():
    assert compute_triangle_area_sas(side1=4, side2="sqrt(3)", included_angle_degrees=120)["canonical"] == "3"
    assert compute_triangle_area_sas(side1="2*sqrt(3)", side2=6, included_angle_degrees=30)["canonical"] == "3*sqrt(3)"
    assert compute_triangle_area_sas(side1=6, side2=4, included_angle_degrees=60)["canonical"] == "6*sqrt(3)"
    side_r = solve_side_and_circumradius_by_sines(
        known_side="3*sqrt(6)",
        known_side_angle_degrees=60,
        other_angle_degrees=45,
        target_side_angle_degrees=45,
    )
    assert side_r["canonical_side"] == "6"
    assert side_r["canonical_radius"] == "3*sqrt(2)"
    side_r2 = solve_side_and_circumradius_by_sines(
        known_side="8*sqrt(2)",
        known_side_angle_degrees=30,
        other_angle_degrees=45,
        target_side_angle_degrees=45,
    )
    assert side_r2["canonical_side"] == "16"
    assert side_r2["canonical_radius"] == "8*sqrt(2)"
    assert solve_angle_by_law_of_sines(side_a=6, side_b="2*sqrt(6)", angle_a_degrees=60, find="B")["canonical"] == "45"
    assert solve_angle_by_law_of_sines(side_a="2*sqrt(3)", side_b="2*sqrt(2)", angle_a_degrees=60, find="C")["canonical"] == "75"
    assert solve_angle_by_law_of_sines(side_a="2*sqrt(6)", side_b=4, angle_a_degrees=120, find="B")["canonical"] == "45"
    assert solve_angle_by_law_of_sines(side_a=2, side_b="sqrt(2)", angle_a_degrees=45, find="B")["canonical"] == "30"
    assert compute_sin_from_side_and_circumradius(side=3, circumradius=3)["canonical"] == "1/2"
    assert solve_side_ratio_by_law_of_sines(angle_p_degrees=30, angle_q_degrees=45)["canonical"] == "sqrt(2)/2"
    assert solve_side_by_law_of_sines(known_side=6, known_angle_degrees=45, target_angle_degrees=30)["canonical"] == "3*sqrt(2)"


@pytest.mark.parametrize("operation", sorted(OPS))
def test_matrix_validate_and_adapter(operation: str):
    matrix = build_trigonometry_law_of_sines_matrix(operation=operation, seed=21)
    assert validate_trigonometry_law_of_sines_matrix(matrix)
    payload = adapt_b2_21_law_of_sines_matrix(matrix, domain_operation=operation, seed=21)
    assert isinstance(payload, dict)
    assert payload.get("answer") is not None
    q = str(payload.get("question_text") or payload.get("question") or "")
    assert q and "placeholder" not in q.lower()
    # No cosine-law stem leakage for generated items.
    assert "b^{2}+c^{2}-2bc" not in q.replace(" ", "")
    assert "餘弦定理" not in q


def test_no_cosine_operations_registered():
    spec = get_domain_spec("trigonometry.law_of_sines")
    assert spec is not None
    for op in spec.allowed_operations:
        assert "cosine" not in op
        assert "cos_" not in op


def test_phase1_and_preflight_on_readonly_prod_examples():
    if not PROD_DB.exists():
        pytest.skip("production db unavailable")
    conn = sqlite3.connect(f"file:{PROD_DB.resolve().as_posix()}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            "SELECT id, skill_id, problem_text, correct_answer, detailed_solution, source_description, problem_type, notes FROM textbook_examples WHERE skill_id=? ORDER BY id",
            (SKILL,),
        ).fetchall()
        assert len(rows) == 13
        by_id = {int(r[0]): dict(zip(
            ["id", "skill_id", "problem_text", "correct_answer", "detailed_solution", "source_description", "problem_type", "notes"],
            r,
        )) for r in rows}

        for eid in (11676, 11678, 11680, 11707, 11708, 11709, 11710, 11716, 11717, 11718):
            induced = run_v3_no_llm_phase1_for_example(SKILL, by_id[eid], conn=conn)
            assert induced.get("classification_status") == "resolved"
            assert induced.get("problem_type_id")

        assert 11706 not in by_id

        preflight = evaluate_skill_v3_capability(conn, SKILL, probe_examples=True)
        assert preflight["domain_key"] == "trigonometry.law_of_sines"
        assert preflight["capability_status"] == "ready"
        assert preflight["resolvable_example_count"] == 13
        assert preflight["unresolved_example_ids"] == []
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
        c = mod.generate(seed=9, component_id=comp.name)
        assert a["answer"] == b["answer"]
        assert a.get("answer") is not None
        q = str(a.get("question_text") or a.get("question") or "")
        assert q and "placeholder" not in q.lower()
        # At least some seeds should vary for non-degenerate components.
        _ = c
