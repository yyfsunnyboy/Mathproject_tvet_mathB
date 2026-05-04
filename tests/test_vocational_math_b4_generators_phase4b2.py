import pytest

from core.vocational_math_b4.domain.counting_domain_functions import (
    combination,
    permutation,
    repeated_digit_arrangement_count,
)
from core.vocational_math_b4.generators import counting, combination as comb_gen, permutation as perm_gen

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


def _assert_mc_contract(payload: dict) -> None:
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]


def test_combination_generator_payload_and_answer() -> None:
    payload = comb_gen.generate(skill_id="s", subskill_id="ss", difficulty=2, seed=10, multiple_choice=True)
    _assert_mc_contract(payload)
    n = payload["parameters"]["n"]
    r = payload["parameters"]["r"]
    assert payload["answer"] == combination(n, r)
    assert "[BLANK]" not in payload["question_text"]
    assert "[BLANK]" not in payload["explanation"]
    assert "C(n," not in payload["explanation"]
    assert "C(" not in payload["explanation"]
    assert "$" in payload["explanation"]
    assert "C^{" in payload["explanation"]


def test_permutation_generator_payload_and_answer() -> None:
    payload = perm_gen.generate(skill_id="s", subskill_id="ss", difficulty=2, seed=20, multiple_choice=True)
    _assert_mc_contract(payload)
    n = payload["parameters"]["n"]
    r = payload["parameters"]["r"]
    assert payload["answer"] == permutation(n, r)
    assert "[FORMULA_MISSING]" not in payload["question_text"]
    assert "[FORMULA_MISSING]" not in payload["explanation"]
    exp = payload["explanation"]
    assert "$" in exp
    assert "P^{" in exp
    assert "P(n," not in exp
    assert "P(" not in exp


def test_repeated_digits_generator_payload_and_answer() -> None:
    payload = counting.generate(skill_id="s", subskill_id="ss", difficulty=2, seed=30, multiple_choice=True)
    _assert_mc_contract(payload)
    digit_count = payload["parameters"]["digit_count"]
    length = payload["parameters"]["length"]
    assert payload["answer"] == repeated_digit_arrangement_count(
        digit_count=digit_count,
        length=length,
        allow_leading_zero=True,
        last_digit_filter=None,
    )


def test_multiple_choice_false_returns_empty_choices() -> None:
    payload1 = comb_gen.generate(skill_id="s", subskill_id="ss", seed=1, multiple_choice=False)
    payload2 = perm_gen.generate(skill_id="s", subskill_id="ss", seed=2, multiple_choice=False)
    payload3 = counting.generate(skill_id="s", subskill_id="ss", seed=3, multiple_choice=False)
    assert payload1["choices"] == []
    assert payload2["choices"] == []
    assert payload3["choices"] == []


def test_same_seed_same_parameters_and_answer() -> None:
    p1 = comb_gen.generate(skill_id="s", subskill_id="ss", seed=99)
    p2 = comb_gen.generate(skill_id="s", subskill_id="ss", seed=99)
    assert p1["parameters"]["parameter_tuple"] == p2["parameters"]["parameter_tuple"]
    assert p1["answer"] == p2["answer"]


def test_different_seeds_produce_variety() -> None:
    tuples = set()
    for sd in range(10):
        payload = perm_gen.generate(skill_id="s", subskill_id="ss", seed=sd)
        tuples.add(payload["parameters"]["parameter_tuple"])
    assert len(tuples) >= 2


def test_seen_parameter_tuples_blocks_duplicates() -> None:
    seen: set[tuple] = set()
    first = counting.generate(skill_id="s", subskill_id="ss", seed=7, seen_parameter_tuples=seen)
    second = counting.generate(skill_id="s", subskill_id="ss", seed=7, seen_parameter_tuples=seen)
    assert first["parameters"]["parameter_tuple"] != second["parameters"]["parameter_tuple"]


def test_invalid_seen_parameter_tuples_raise_value_error() -> None:
    with pytest.raises(ValueError):
        comb_gen.generate(skill_id="s", subskill_id="ss", seen_parameter_tuples=[])


def test_raise_when_retries_exhausted() -> None:
    blocked = {
        ("combination_definition_basic", n, r)
        for n in range(5, 9)
        for r in range(2, 4)
        if n >= r
    }
    with pytest.raises(ValueError):
        comb_gen.generate(skill_id="s", subskill_id="ss", difficulty=1, seed=123, seen_parameter_tuples=blocked)
