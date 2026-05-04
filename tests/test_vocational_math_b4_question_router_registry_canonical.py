from __future__ import annotations

from pathlib import Path

import pytest

from core.vocational_math_b4.services import question_router as question_router_module
from core.vocational_math_b4.services.question_router import generate_for_skill


ROUTER_PATH = Path("core/vocational_math_b4/services/question_router.py")

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

CANONICAL_SKILL_IDS = [
    "vh_數學B4_CombinationDefinition",
    "vh_數學B4_CombinationApplications",
    "vh_數學B4_MultiplicationPrinciple",
    "vh_數學B4_PermutationOfDistinctObjects",
    "vh_數學B4_RepeatedPermutation",
    "vh_數學B4_FactorialNotation",
    "vh_數學B4_AdditionPrinciple",
    "vh_數學B4_CombinationProperties",
    "vh_數學B4_PermutationWithRepetition",
    "vh_數學B4_Combination",
]


def test_router_source_contains_no_mojibake_marker() -> None:
    text = ROUTER_PATH.read_text(encoding="utf-8")
    assert "?詨飛" not in text


def test_registry_keys_are_canonical() -> None:
    registry = question_router_module._REGISTRY
    for key in registry:
        assert "?" not in key
        assert "詨飛" not in key


@pytest.mark.parametrize("skill_id", CANONICAL_SKILL_IDS)
def test_registry_contains_all_canonical_skill_ids(skill_id: str) -> None:
    assert skill_id in question_router_module._REGISTRY


@pytest.mark.parametrize("skill_id", CANONICAL_SKILL_IDS)
def test_generate_for_skill_with_canonical_skill_id(skill_id: str) -> None:
    payload = generate_for_skill(skill_id=skill_id, level=1, seed=1)
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert payload["skill_id"] == skill_id
    assert payload["correct_answer"] == payload["answer"]
    assert payload["router_trace"]["input_skill_id"] == skill_id


@pytest.mark.parametrize(
    "mojibake_skill_id",
    [
        "vh_?詨飛B4_CombinationDefinition",
        "vh_?詨飛B4_MultiplicationPrinciple",
    ],
)
def test_generate_for_skill_rejects_mojibake_skill_id(mojibake_skill_id: str) -> None:
    with pytest.raises(ValueError):
        generate_for_skill(skill_id=mojibake_skill_id, level=1, seed=1)
