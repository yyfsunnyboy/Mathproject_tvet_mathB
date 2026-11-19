# -*- coding: utf-8 -*-
"""src_4584 belongs to point-line distance, not parallel-lines distance."""

from __future__ import annotations

from fractions import Fraction

from agent_skills_v3.vh_數學B1_DistanceBetweenPointAndLine.components.src_4584.generate import (
    _parameter_pool,
    generate,
)
from core.gencode.runtime_skill_wrapper import check_answer
from skills import vh_數學B1_DistanceBetweenPointAndLine as point_skill
from skills import vh_數學B1_DistanceBetweenTwoParallelLines as parallel_skill


def _choice_value(payload: dict) -> int:
    label = payload["answer"]
    for choice in payload["choices"]:
        if choice["label"] == label:
            return int(choice["text"])
    raise AssertionError("correct label missing from choices")


def _assert_isomorphic(payload: dict) -> None:
    raw = payload["metadata"]["raw_givens"]
    a = int(raw["a"])
    b = int(raw["b"])
    k = int(raw["k"])
    slope = Fraction(str(raw["slope"]))
    distance_squared = Fraction(str(raw["origin_distance_squared"]))

    assert payload["problem_type_id"] == "slope_and_point_line_distance_parameter_choice"
    assert payload["component_id"] == "src_4584"
    assert b != 0 and k > 0
    assert int(-slope * b) == a
    assert distance_squared * (a * a + b * b) == k * k
    assert _choice_value(payload) == a + k
    assert check_answer(payload["answer"], payload["correct_answer"], payload=payload)


def test_src_4584_is_bound_to_point_line_skill_only() -> None:
    assert "src_4584" in point_skill.GENERATOR_KEYS
    assert "src_4584" not in parallel_skill.GENERATOR_KEYS
    assert any(
        row.get("problem_type_id") == "slope_and_point_line_distance_parameter_choice"
        for row in point_skill.GENERATOR_SPECS
    )
    assert all(
        row.get("problem_type_id") != "parallel_lines_distance_single_choice"
        for row in parallel_skill.GENERATOR_SPECS
    )
    assert all(
        row.get("problem_type_id") != "slope_and_point_line_distance_parameter_choice"
        for row in parallel_skill.GENERATOR_SPECS
    )


def test_src_4584_reported_cases_are_in_family_pool() -> None:
    pool = set(_parameter_pool())
    assert (-5, 12, 13) in pool  # slope 5/12, a+k=8
    assert (-7, 24, 25) in pool  # slope 7/24, a+k=18


def test_src_4584_all_parameter_pool_variants_are_valid() -> None:
    for a, b, k in _parameter_pool():
        payload = generate.__globals__["_build_payload"](a, b, k, seed=0, component_id="src_4584")
        _assert_isomorphic(payload)
        slope = Fraction(str(payload["metadata"]["raw_givens"]["slope"]))
        assert slope == Fraction(-a, b)
        assert int(payload["metadata"]["raw_givens"]["answer_value"]) == a + k


def test_src_4584_seed_samples_cover_reported_isomorphs() -> None:
    seen_answers = set()
    seen_slopes = set()
    for seed in range(80):
        payload = generate(seed=seed, component_id="src_4584")
        _assert_isomorphic(payload)
        raw = payload["metadata"]["raw_givens"]
        seen_answers.add(int(raw["answer_value"]))
        seen_slopes.add(str(raw["slope"]))
    assert 8 in seen_answers
    assert 18 in seen_answers
    assert "5/12" in seen_slopes
    assert "7/24" in seen_slopes


def test_both_skills_still_generate_diverse_problem_types() -> None:
    point_types = set()
    for seed in range(40):
        payload = point_skill.generate(seed=seed)
        point_types.add(payload.get("problem_type_id") or payload.get("metadata", {}).get("problem_type_id"))
    assert "slope_and_point_line_distance_parameter_choice" in point_types
    assert len(point_types) >= 2

    parallel_types = set()
    for seed in range(40):
        payload = parallel_skill.generate(seed=seed)
        parallel_types.add(payload.get("problem_type_id") or payload.get("metadata", {}).get("problem_type_id"))
    assert "slope_and_point_line_distance_parameter_choice" not in parallel_types
    assert "parallel_lines_distance_single_choice" not in parallel_types
    assert len(parallel_types) >= 2
    assert any(
        t in parallel_types
        for t in (
            "distance_between_parallel_lines",
            "solve_parameter_from_parallel_distance",
            "area_using_parallel_distance",
        )
    )
