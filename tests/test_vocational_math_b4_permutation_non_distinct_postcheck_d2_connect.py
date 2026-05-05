from __future__ import annotations

import importlib
from pathlib import Path

from core.vocational_math_b4.services import question_router
from core.vocational_math_b4.services.question_router import generate_for_skill


SKILL_ID = "vh_數學B4_PermutationOfNonDistinctObjects"
PRIMARY_PROBLEM_TYPE_ID = "non_distinct_objects_arrangement"
PRIMARY_GENERATOR_KEY = "b4.permutation.non_distinct_objects_arrangement"
FALLBACK_PROBLEM_TYPE_ID = "repeated_permutation_digits"
FALLBACK_GENERATOR_KEY = "b4.counting.repeated_permutation_digits"
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


def _assert_primary_payload(payload: dict) -> None:
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert payload["problem_type_id"] == PRIMARY_PROBLEM_TYPE_ID
    assert payload["generator_key"] == PRIMARY_GENERATOR_KEY
    assert payload["skill_id"] == SKILL_ID
    assert isinstance(payload["answer"], int)
    assert payload["correct_answer"] == payload["answer"]
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]
    assert "可重複使用" not in payload["question_text"]
    assert "每位可重複" not in payload["question_text"]
    assert "每次可重複選" not in payload["question_text"]
    assert "\\frac" in payload["explanation"]
    assert "!" in payload["explanation"]
    assert "$" in payload["explanation"]
    assert {
        "total_count",
        "duplicate_counts",
        "singleton_count",
        "context",
        "parameter_tuple",
    }.issubset(payload["parameters"].keys())
    assert payload["router_trace"]["selected_problem_type_id"] == PRIMARY_PROBLEM_TYPE_ID
    assert payload["router_trace"]["selected_generator_key"] == PRIMARY_GENERATOR_KEY


def test_generate_for_skill_supports_primary_problem_type() -> None:
    payload = generate_for_skill(
        skill_id=SKILL_ID,
        level=1,
        seed=1,
        problem_type_id=PRIMARY_PROBLEM_TYPE_ID,
    )

    _assert_primary_payload(payload)


def test_wrapper_generate_can_specify_primary_problem_type_and_check_answer() -> None:
    module = importlib.import_module("skills.vh_數學B4_PermutationOfNonDistinctObjects")
    payload = module.generate(level=1, seed=1, problem_type_id=PRIMARY_PROBLEM_TYPE_ID)

    _assert_primary_payload(payload)
    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False


def test_default_selection_can_reach_primary_problem_type_in_seed_1_to_10() -> None:
    problem_types = [
        generate_for_skill(skill_id=SKILL_ID, level=1, seed=seed)["problem_type_id"]
        for seed in range(1, 11)
    ]

    assert PRIMARY_PROBLEM_TYPE_ID in problem_types


def test_repeated_permutation_digits_fallback_can_still_be_specified() -> None:
    payload = generate_for_skill(
        skill_id=SKILL_ID,
        level=1,
        seed=1,
        problem_type_id=FALLBACK_PROBLEM_TYPE_ID,
    )

    assert REQUIRED_KEYS.issubset(payload.keys())
    assert payload["problem_type_id"] == FALLBACK_PROBLEM_TYPE_ID
    assert payload["generator_key"] == FALLBACK_GENERATOR_KEY
    assert payload["skill_id"] == SKILL_ID
    assert payload["correct_answer"] == payload["answer"]
    assert payload["router_trace"]["selection_reason"] == "problem_type_id_specified"


def test_router_registry_keeps_canonical_skill_without_mojibake_alias() -> None:
    assert SKILL_ID in question_router._REGISTRY
    assert all("?詨飛" not in skill_id for skill_id in question_router._REGISTRY)
    assert all("?詨飛" not in skill_id for skill_id in question_router._ENRICHMENT_REGISTRY)


def test_no_new_wrapper_file_for_connect_phase() -> None:
    assert Path("skills/vh_數學B4_PermutationOfNonDistinctObjects.py").exists()
    assert not Path("skills/vh_數學B4_NonDistinctObjectsArrangement.py").exists()
