import re

import pytest

from core.vocational_math_b4.domain.b4_validators import validate_problem_payload_contract
from core.vocational_math_b4.domain.counting_domain_functions import combination, factorial, permutation
from core.vocational_math_b4.generators.combination import (
    combination_restricted_selection,
    combination_seat_assignment,
)
from core.vocational_math_b4.generators.permutation import permutation_full_arrangement


def _check_contract(payload: dict) -> None:
    validate_problem_payload_contract(payload)
    required = {
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
    assert required.issubset(payload.keys())


def _check_latex(text: str) -> None:
    assert "$" in text
    assert "2^2" not in text
    assert "C(n,r)" not in text
    assert "P(n,r)" not in text


def _check_mc(payload: dict, multiple_choice: bool) -> None:
    if multiple_choice:
        assert len(payload["choices"]) == 4
        assert len(set(payload["choices"])) == 4
        assert payload["answer"] in payload["choices"]
    else:
        assert payload["choices"] == []


def test_generators_importable() -> None:
    assert callable(permutation_full_arrangement)
    assert callable(combination_restricted_selection)
    assert callable(combination_seat_assignment)


@pytest.mark.parametrize(
    "fn",
    [
        permutation_full_arrangement,
        combination_restricted_selection,
        combination_seat_assignment,
    ],
)
def test_payload_contract_and_answer_type(fn) -> None:
    payload = fn(skill_id="vh", subskill_id="sub", difficulty=2, seed=11)
    _check_contract(payload)
    assert isinstance(payload["answer"], int)


def test_answer_correct_permutation_full_arrangement() -> None:
    payload = permutation_full_arrangement(skill_id="vh", subskill_id="sub", seed=3)
    assert payload["answer"] == factorial(payload["parameters"]["n"])


def test_answer_correct_comb_restricted_at_least_one() -> None:
    for seed in range(1, 30):
        payload = combination_restricted_selection(skill_id="vh", subskill_id="sub", seed=seed)
        if payload["parameters"]["variant"] == "at_least_one_from_group":
            a = payload["parameters"]["a"]
            b = payload["parameters"]["b"]
            r = payload["parameters"]["r"]
            total = combination(a + b, r)
            invalid = combination(b, r) if r <= b else 0
            assert payload["answer"] == total - invalid
            return
    pytest.fail("no at_least_one_from_group sample found")


def test_answer_correct_comb_restricted_exactly_k() -> None:
    for seed in range(1, 30):
        payload = combination_restricted_selection(skill_id="vh", subskill_id="sub", seed=seed)
        if payload["parameters"]["variant"] == "exactly_k_from_group":
            a = payload["parameters"]["a"]
            b = payload["parameters"]["b"]
            r = payload["parameters"]["r"]
            k = payload["parameters"]["k"]
            assert payload["answer"] == combination(a, k) * combination(b, r - k)
            return
    pytest.fail("no exactly_k_from_group sample found")


def test_answer_correct_combination_seat_assignment() -> None:
    payload = combination_seat_assignment(skill_id="vh", subskill_id="sub", seed=5)
    n = payload["parameters"]["n"]
    r = payload["parameters"]["r"]
    assert payload["answer"] == combination(n, r) * permutation(r, r)


@pytest.mark.parametrize(
    "fn",
    [
        permutation_full_arrangement,
        combination_restricted_selection,
        combination_seat_assignment,
    ],
)
def test_placeholder_and_latex(fn) -> None:
    payload = fn(skill_id="vh", subskill_id="sub", seed=7)
    q = payload["question_text"]
    e = payload["explanation"]
    assert "[BLANK]" not in q and "[BLANK]" not in e
    _check_latex(q if "$" in q else e)
    combo_or_perm = q + "\n" + e
    assert ("C^{" in combo_or_perm) or ("\\binom" in combo_or_perm) or ("!" in combo_or_perm) or ("P^{" in combo_or_perm)
    if fn is combination_seat_assignment:
        assert "\\times" in combo_or_perm


@pytest.mark.parametrize(
    "fn",
    [
        permutation_full_arrangement,
        combination_restricted_selection,
        combination_seat_assignment,
    ],
)
def test_multiple_choice_and_free_response(fn) -> None:
    payload_mc = fn(skill_id="vh", subskill_id="sub", seed=12, multiple_choice=True)
    _check_mc(payload_mc, True)
    payload_fr = fn(skill_id="vh", subskill_id="sub", seed=12, multiple_choice=False)
    _check_mc(payload_fr, False)


@pytest.mark.parametrize(
    "fn",
    [
        permutation_full_arrangement,
        combination_restricted_selection,
        combination_seat_assignment,
    ],
)
def test_same_seed_stable_parameter_tuple_and_answer(fn) -> None:
    p1 = fn(skill_id="vh", subskill_id="sub", seed=101)
    p2 = fn(skill_id="vh", subskill_id="sub", seed=101)
    assert p1["parameters"]["parameter_tuple"] == p2["parameters"]["parameter_tuple"]
    assert p1["answer"] == p2["answer"]


@pytest.mark.parametrize(
    "fn",
    [
        permutation_full_arrangement,
        combination_restricted_selection,
        combination_seat_assignment,
    ],
)
def test_different_seed_generates_variety(fn) -> None:
    tuples = {fn(skill_id="vh", subskill_id="sub", seed=s)["parameters"]["parameter_tuple"] for s in range(1, 11)}
    assert len(tuples) >= 2


@pytest.mark.parametrize(
    "fn",
    [
        permutation_full_arrangement,
        combination_restricted_selection,
        combination_seat_assignment,
    ],
)
def test_seed_1_to_5_all_distinct(fn) -> None:
    tuples = [fn(skill_id="vh", subskill_id="sub", seed=s)["parameters"]["parameter_tuple"] for s in range(1, 6)]
    assert len(set(tuples)) == 5


@pytest.mark.parametrize(
    "fn",
    [
        permutation_full_arrangement,
        combination_restricted_selection,
        combination_seat_assignment,
    ],
)
def test_seen_parameter_tuples_blocks_duplicates(fn) -> None:
    seen: set[tuple] = set()
    p1 = fn(skill_id="vh", subskill_id="sub", seed=31, seen_parameter_tuples=seen)
    p2 = fn(skill_id="vh", subskill_id="sub", seed=31, seen_parameter_tuples=seen)
    assert p1["parameters"]["parameter_tuple"] != p2["parameters"]["parameter_tuple"]


@pytest.mark.parametrize(
    "fn",
    [
        permutation_full_arrangement,
        combination_restricted_selection,
        combination_seat_assignment,
    ],
)
def test_retry_50_failure_raises(fn, monkeypatch) -> None:
    if fn is permutation_full_arrangement:
        def _fixed_perm(_rng, _difficulty):
            return 3, "students_line"

        monkeypatch.setattr("core.vocational_math_b4.generators.permutation._sample_full_arrangement_params", _fixed_perm)
        seen = {("permutation_full_arrangement", 3, "students_line")}
    elif fn is combination_restricted_selection:
        def _fixed_restricted(_rng, _difficulty):
            return 3, 4, 2, 1, "at_least_one_from_group"

        monkeypatch.setattr(
            "core.vocational_math_b4.generators.combination._sample_restricted_selection_params",
            _fixed_restricted,
        )
        seen = {("combination_restricted_selection", 3, 4, 2, 1, "at_least_one_from_group")}
    else:
        def _fixed_seat(_rng, _difficulty):
            return 5, 2, "seats"

        monkeypatch.setattr(
            "core.vocational_math_b4.generators.combination._sample_seat_assignment_params",
            _fixed_seat,
        )
        seen = {("combination_seat_assignment", 5, 2, "seats")}

    with pytest.raises(ValueError):
        fn(skill_id="vh", subskill_id="sub", seed=999, seen_parameter_tuples=seen)
