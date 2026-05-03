from __future__ import annotations

import importlib

import pytest

from core.vocational_math_b4.services.question_router import generate_for_skill


REQUIRED_KEYS = {
    "question_text",
    "answer",
    "correct_answer",
    "choices",
    "explanation",
    "skill_id",
    "subskill_id",
    "problem_type_id",
    "generator_key",
    "difficulty",
    "diagnosis_tags",
    "remediation_candidates",
    "source_style_refs",
    "parameters",
    "router_trace",
}


def _assert_common_payload(payload: dict) -> None:
    assert REQUIRED_KEYS.issubset(set(payload.keys()))
    assert payload["correct_answer"] == payload["answer"]
    assert isinstance(payload["router_trace"], dict)
    for k in [
        "input_skill_id",
        "selected_subskill_id",
        "selected_problem_type_id",
        "selected_generator_key",
        "selection_reason",
    ]:
        assert k in payload["router_trace"]
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]


@pytest.mark.parametrize(
    "skill_id",
    [
        "vh_數學B4_CombinationDefinition",
        "vh_數學B4_CombinationApplications",
        "vh_數學B4_MultiplicationPrinciple",
        "vh_數學B4_PermutationOfDistinctObjects",
        "vh_數學B4_RepeatedPermutation",
    ],
)
def test_generate_for_skill_supports_all_skill_ids(skill_id: str):
    payload = generate_for_skill(skill_id=skill_id, level=1, seed=1, multiple_choice=True)
    _assert_common_payload(payload)
    assert payload["skill_id"] == skill_id


def test_combination_applications_can_select_two_problem_types():
    observed = set()
    for seed in range(1, 21):
        payload = generate_for_skill(
            skill_id="vh_數學B4_CombinationApplications",
            level=1,
            seed=seed,
            multiple_choice=True,
        )
        observed.add(payload["problem_type_id"])
    assert "combination_polygon_count" in observed
    assert "combination_required_excluded_person" in observed


@pytest.mark.parametrize(
    ("problem_type_id", "expected_generator_key"),
    [
        ("combination_polygon_count", "b4.combination.combination_polygon_count"),
        ("combination_required_excluded_person", "b4.combination.combination_required_excluded_person"),
    ],
)
def test_problem_type_override(problem_type_id: str, expected_generator_key: str):
    payload = generate_for_skill(
        skill_id="vh_數學B4_CombinationApplications",
        level=1,
        seed=7,
        multiple_choice=True,
        problem_type_id=problem_type_id,
    )
    assert payload["problem_type_id"] == problem_type_id
    assert payload["generator_key"] == expected_generator_key
    assert payload["router_trace"]["selected_problem_type_id"] == problem_type_id


def test_unsupported_skill_raises():
    with pytest.raises(ValueError):
        generate_for_skill(skill_id="vh_數學B4_NotSupported", level=1, seed=1)


def test_invalid_problem_type_for_skill_raises():
    with pytest.raises(ValueError):
        generate_for_skill(
            skill_id="vh_數學B4_CombinationDefinition",
            level=1,
            seed=1,
            problem_type_id="combination_polygon_count",
        )


def test_wrapper_still_operates_via_router():
    module = importlib.import_module("skills.vh_數學B4_CombinationDefinition")
    payload = module.generate(level=1, seed=1)
    _assert_common_payload(payload)
    assert payload["generator_key"] == "b4.combination.combination_definition_basic"
    assert payload["router_trace"]["selected_generator_key"] == payload["generator_key"]

