# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any
import pytest

from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example

SKILL = "vh_數學B1_DistanceBetweenTwoPointsInPlane"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"


@pytest.fixture(scope="module")
def production_examples() -> list[dict[str, Any]]:
    """Load the 4 textbook examples from production DB."""
    if not DB_PATH.exists():
        pytest.skip(f"Production DB not found: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM textbook_examples WHERE skill_id=? ORDER BY id",
        (SKILL,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def test_distance_between_two_points_examples(production_examples) -> None:
    """Verify that all 4 examples are resolved correctly with exact problem_type_ids and answer contracts."""
    assert len(production_examples) == 4, f"Expected 4 examples, got {len(production_examples)}"
    
    expected_mappings = {
        4419: {
            "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
            "answer_type": "expression",
            "checker_key": "expression_checker",
            "equivalence_type": "algebraic_equivalent",
        },
        4432: {
            "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
            "answer_type": "expression",
            "checker_key": "expression_checker",
            "equivalence_type": "algebraic_equivalent",
        },
        4436: {
            "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
            "answer_type": "expression",
            "checker_key": "expression_checker",
            "equivalence_type": "algebraic_equivalent",
        },
        4437: {
            "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
            "answer_type": "expression",
            "checker_key": "expression_checker",
            "equivalence_type": "algebraic_equivalent",
        },
    }

    conn = sqlite3.connect(str(DB_PATH))
    try:
        for ex in production_examples:
            ex_id = ex["id"]
            res = run_v3_no_llm_phase1_for_example(SKILL, ex, conn=conn)
            
            assert res.get("classification_status") == "resolved", f"Example {ex_id} failed classification: {res}"
            assert "reason" not in res or res["reason"] != "phase1_classifier_not_registered"
            
            exp = expected_mappings[ex_id]
            assert res.get("problem_type_id") == exp["problem_type_id"], (
                f"Example {ex_id}: expected problem_type_id {exp['problem_type_id']}, got {res.get('problem_type_id')}"
            )
            
            # Verify classification contract requirements
            assert "source_example_id" in res
            assert res["source_example_id"] == ex_id
            assert res.get("skill_id") == SKILL
            assert "required_capabilities" in res
            assert exp["problem_type_id"] in res["required_capabilities"]
            assert "presentation_mode" in res
            
            ac = res.get("answer_contract") or {}
            assert ac.get("answer_type") == exp["answer_type"]
            assert ac.get("checker_key") == exp["checker_key"]
            assert ac.get("equivalence_type") == exp["equivalence_type"]
    finally:
        conn.close()


def test_distance_domain_matrix_seeds() -> None:
    """Run at least 10 different seeds for both operations and check correctness."""
    from core.domain.coordinate_geometry.distance_between_two_points_domain import (
        build_distance_between_two_points_matrix,
    )
    
    # 1. Test distance compute
    for seed in range(100, 110):
        matrix = build_distance_between_two_points_matrix(
            seed=seed,
            domain_operation="short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
            curriculum_profile="vocational_high_b",
            difficulty_profile="normal",
        )
        # Check basic matrix layout
        assert "givens" in matrix
        assert "answer" in matrix
        ans = matrix["answer"]
        assert "distance" in ans
        assert "canonical_form" in ans
        assert "general_form" in ans
        assert "coefficients" in ans
        
        # Verify direct calculation distance correctness
        givens = matrix["givens"]
        x1, y1 = givens["x1"], givens["y1"]
        x2, y2 = givens["x2"], givens["y2"]
        dx, dy = x2 - x1, y2 - y1
        d2 = dx * dx + dy * dy
        dist_str = ans["distance"]
        if dist_str.startswith("sqrt("):
            val = int(dist_str[5:-1])
            assert val == d2
        else:
            assert int(dist_str) * int(dist_str) == d2

    # 2. Test solve unknown coordinate (unordered_solution_set)
    for seed in range(200, 210):
        matrix = build_distance_between_two_points_matrix(
            seed=seed,
            domain_operation="short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
            curriculum_profile="vocational_high_b",
            difficulty_profile="normal",
        )
        assert "givens" in matrix
        assert "answer" in matrix
        ans = matrix["answer"]
        assert "solutions" in ans
        
        solutions = ans["solutions"]
        assert len(solutions) in (1, 2)
        
        # Verify the two solutions are correct and satisfy the distance condition
        givens = matrix["givens"]
        d = givens["distance"]
        
        # Determine which coordinate was replaced by k
        coords = [givens["x1"], givens["y1"], givens["x2"], givens["y2"]]
        param_idx = coords.index("k")
        
        for k in solutions:
            test_coords = list(coords)
            test_coords[param_idx] = k
            tx1, ty1, tx2, ty2 = test_coords
            assert (tx2 - tx1) ** 2 + (ty2 - ty1) ** 2 == d * d


def test_phase1_summary_json_canonical_fields() -> None:
    """Verify that phase1_summary.json contains downstream canonical summary fields."""
    import json
    summary_path = PROJECT_ROOT / "reports" / "gencode_closed_loop" / f"{SKILL}_phase1_summary.json"
    assert summary_path.is_file(), f"phase1_summary.json not found at {summary_path}"
    
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "observed_problem_types" in data
    assert "answer_contract_summary" in data
    
    pts = data["observed_problem_types"]
    assert "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2" in pts
    assert "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2" in pts


def test_wrapper_routing_and_fallback() -> None:
    """Verify routing by component_id, problem_type_id, and invalid key routing error."""
    import skills.vh_數學B1_DistanceBetweenTwoPointsInPlane as skill
    
    # 1. Routing by component_id
    for seed in range(5):
        payload = skill.generate(component_id="src_4436", seed=seed)
        assert payload["problem_type_id"] == "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2"
        assert payload["metadata"]["component_id"] == "src_4436"

    # 2. Routing by problem_type_id
    pt_id = "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
    for seed in range(5):
        payload = skill.generate(problem_type_id=pt_id, seed=seed)
        assert payload["problem_type_id"] == pt_id

    # 3. Invalid routing raises KeyError
    with pytest.raises(KeyError):
        skill.generate(component_id="src_9999")
        
    with pytest.raises(KeyError):
        skill.generate(problem_type_id="invalid_pt")
        
    # 4. Default dispatch is backward compatible
    payload = skill.generate()
    assert "problem_type_id" in payload



