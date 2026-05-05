from __future__ import annotations

import pytest

from core.vocational_math_b4.domain.counting_domain_functions import factorial
from core.vocational_math_b4.generators import counting as counting_generators
from core.vocational_math_b4.generators import permutation as permutation_generators
from core.vocational_math_b4.services import question_router


SKILL_ID = "vh_數學B4_PermutationOfNonDistinctObjects"
SUBSKILL_ID = "b4_ch1_perm_non_distinct_objects_01"
PROBLEM_TYPE_ID = "non_distinct_objects_arrangement"
GENERATOR_KEY = "b4.permutation.non_distinct_objects_arrangement"
REQUIRED_KEYS = {
    "question_text",
    "choices",
    "answer",
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
}


def _generate(**kwargs) -> dict:
    return permutation_generators.non_distinct_objects_arrangement(
        skill_id=SKILL_ID,
        subskill_id=SUBSKILL_ID,
        **kwargs,
    )


def _expected_answer(payload: dict) -> int:
    params = payload["parameters"]
    denominator = 1
    for count in params["duplicate_counts"]:
        denominator *= factorial(count)
    return factorial(params["total_count"]) // denominator


def _assert_payload(payload: dict) -> None:
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert payload["problem_type_id"] == PROBLEM_TYPE_ID
    assert payload["generator_key"] == GENERATOR_KEY
    assert payload["skill_id"] == SKILL_ID
    assert isinstance(payload["answer"], int)
    assert payload["answer"] == _expected_answer(payload)
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]
    assert "[BLANK]" not in payload["question_text"]
    assert "[BLANK]" not in payload["explanation"]
    assert "\\frac" in payload["explanation"]
    assert "!" in payload["explanation"]
    assert "$" in payload["explanation"]
    forbidden_explanation = ["n!/", "4!/2!", "6!/", "C(n,r)", "P(n,r)"]
    assert all(token not in payload["explanation"] for token in forbidden_explanation)
    forbidden_question = ["可重複使用", "每位可重複", "每次可重複選"]
    assert all(token not in payload["question_text"] for token in forbidden_question)
    params = payload["parameters"]
    assert {"total_count", "duplicate_counts", "singleton_count", "context", "parameter_tuple"}.issubset(
        params.keys()
    )
    assert any(count >= 2 for count in params["duplicate_counts"])
    assert params["total_count"] == sum(params["duplicate_counts"]) + params["singleton_count"]
    assert "non_distinct_objects_arrangement" in payload["diagnosis_tags"]
    assert "permutation" in payload["diagnosis_tags"]
    assert "multiset_permutation" in payload["diagnosis_tags"]


def test_generator_importable() -> None:
    assert callable(permutation_generators.non_distinct_objects_arrangement)


def test_generate_contract_and_answer() -> None:
    payload = _generate(difficulty=1, seed=1)
    _assert_payload(payload)


def test_multiple_choice_false_returns_empty_choices() -> None:
    payload = _generate(difficulty=1, seed=2, multiple_choice=False)

    assert payload["choices"] == []
    assert payload["answer"] == _expected_answer(payload)
    assert payload["problem_type_id"] == PROBLEM_TYPE_ID
    assert payload["generator_key"] == GENERATOR_KEY


def test_same_seed_is_deterministic() -> None:
    p1 = _generate(difficulty=1, seed=3)
    p2 = _generate(difficulty=1, seed=3)

    assert p1["parameters"]["parameter_tuple"] == p2["parameters"]["parameter_tuple"]
    assert p1["answer"] == p2["answer"]


def test_seed_1_to_5_parameter_tuples_are_distinct() -> None:
    tuples = {
        _generate(difficulty=1, seed=seed)["parameters"]["parameter_tuple"]
        for seed in range(1, 6)
    }

    assert len(tuples) == 5


def test_seed_1_to_30_covers_at_least_two_contexts() -> None:
    contexts = {
        _generate(difficulty=1, seed=seed)["parameters"]["context"]
        for seed in range(1, 31)
    }

    assert len(contexts) >= 2


def test_colored_balls_question_spacing_after_qizhong() -> None:
    payload = None
    for seed in range(1, 31):
        candidate = _generate(difficulty=1, seed=seed)
        if candidate["parameters"]["context"] == "colored_balls":
            payload = candidate
            break

    assert payload is not None, "expected colored_balls within seeds 1-30"

    qt = payload["question_text"]
    assert "其中2" not in qt
    assert "其中3" not in qt
    assert "其中1" not in qt
    assert ("其中 " in qt) or ("其中：" in qt)

    _assert_payload(payload)


def test_seen_parameter_tuples_blocks_duplicate() -> None:
    seen: set[tuple] = set()
    first = _generate(difficulty=1, seed=1, seen_parameter_tuples=seen)
    second = _generate(difficulty=1, seed=1, seen_parameter_tuples=seen)

    assert first["parameters"]["parameter_tuple"] != second["parameters"]["parameter_tuple"]


def test_raises_after_50_retries_when_space_exhausted(monkeypatch) -> None:
    def _fixed_params(_rng, _difficulty):
        return 4, [2], 2, "letters"

    monkeypatch.setattr(
        "core.vocational_math_b4.generators.permutation._sample_non_distinct_objects_params",
        _fixed_params,
    )
    seen = {(PROBLEM_TYPE_ID, 4, (2,), 2, "letters")}

    with pytest.raises(ValueError):
        _generate(difficulty=1, seed=100, seen_parameter_tuples=seen)


def test_does_not_modify_repeated_permutation_digits_generator() -> None:
    payload = counting_generators.generate(
        skill_id="vh_數學B4_RepeatedPermutation",
        subskill_id="b4_ch1_rep_perm_digits_01",
        difficulty=1,
        seed=1,
    )

    assert payload["problem_type_id"] == "repeated_permutation_digits"
    assert payload["generator_key"] == "b4.counting.repeated_permutation_digits"


def test_not_connected_to_router_in_this_phase() -> None:
    entries = question_router._REGISTRY[SKILL_ID]

    assert all(entry["problem_type_id"] != PROBLEM_TYPE_ID for entry in entries)
