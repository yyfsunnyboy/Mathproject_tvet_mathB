from __future__ import annotations

import itertools
import re

import pytest

from core.vocational_math_b4.domain.counting_domain_functions import factorial
from core.vocational_math_b4.generators import permutation as permutation_generators


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


def _assert_common_payload(payload: dict) -> None:
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert isinstance(payload["answer"], int)
    assert "[BLANK]" not in payload["question_text"]
    assert "[BLANK]" not in payload["explanation"]
    assert "parameter_tuple" in payload["parameters"]
    text = f"{payload['question_text']} {payload['explanation']}"
    assert "$" in text
    assert "C(n,r)" not in text
    assert "P(n,r)" not in text
    assert re.search(r"\b\d+\^\d+\b", text) is None


def _bruteforce_digit_parity(digits: list[int], positions: int, variant: str) -> int:
    count = 0
    for seq in itertools.permutations(digits, positions):
        if seq[0] == 0:
            continue
        if variant == "odd_number" and seq[-1] % 2 == 0:
            continue
        if variant == "even_number" and seq[-1] % 2 != 0:
            continue
        count += 1
    return count


def test_generators_importable() -> None:
    assert hasattr(permutation_generators, "permutation_adjacent_block")
    assert hasattr(permutation_generators, "permutation_digit_parity")


def test_adjacent_block_contract_and_answer() -> None:
    payload = permutation_generators.permutation_adjacent_block(
        skill_id="vh_數學B4_Test",
        subskill_id="test",
        difficulty=2,
        seed=7,
    )
    _assert_common_payload(payload)
    assert payload["problem_type_id"] == "permutation_adjacent_block"
    assert payload["generator_key"] == "b4.permutation.permutation_adjacent_block"
    p = payload["parameters"]
    expected = factorial(p["n"] - p["block_size"] + 1) * factorial(p["block_size"])
    assert payload["answer"] == expected
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]
    assert "!" in payload["explanation"]
    assert "$" in payload["explanation"]
    assert "\\times" in payload["explanation"]
    assert "!*" not in payload["explanation"]
    assert "×" not in payload["explanation"]
    assert "C(n,r)" not in payload["explanation"]
    assert "P(n,r)" not in payload["explanation"]


def test_adjacent_block_multiple_choice_false() -> None:
    payload = permutation_generators.permutation_adjacent_block(
        skill_id="vh_數學B4_Test",
        subskill_id="test",
        difficulty=1,
        seed=1,
        multiple_choice=False,
    )
    _assert_common_payload(payload)
    assert payload["choices"] == []


def test_digit_parity_contract_and_answer_with_bruteforce() -> None:
    payload = permutation_generators.permutation_digit_parity(
        skill_id="vh_數學B4_Test",
        subskill_id="test",
        difficulty=2,
        seed=8,
    )
    _assert_common_payload(payload)
    assert payload["problem_type_id"] == "permutation_digit_parity"
    assert payload["generator_key"] == "b4.permutation.permutation_digit_parity"
    p = payload["parameters"]
    digits = list(range(0, p["digit_pool_size"])) if p["allow_zero"] else list(range(1, p["digit_pool_size"] + 1))
    expected = _bruteforce_digit_parity(digits, p["positions"], p["variant"])
    assert payload["answer"] == expected
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]
    assert "\\times" in payload["explanation"]
    assert "!" in payload["explanation"]


def test_digit_parity_multiple_choice_false() -> None:
    payload = permutation_generators.permutation_digit_parity(
        skill_id="vh_數學B4_Test",
        subskill_id="test",
        difficulty=1,
        seed=1,
        multiple_choice=False,
    )
    _assert_common_payload(payload)
    assert payload["choices"] == []


@pytest.mark.parametrize(
    "allow_zero,variant",
    [
        (True, "odd_number"),
        (True, "even_number"),
        (False, "odd_number"),
        (False, "even_number"),
    ],
)
def test_digit_parity_targeted_variants(allow_zero: bool, variant: str) -> None:
    found = False
    for seed in range(1, 150):
        payload = permutation_generators.permutation_digit_parity(
            skill_id="vh_數學B4_Test",
            subskill_id="test",
            difficulty=2,
            seed=seed,
        )
        p = payload["parameters"]
        if p["allow_zero"] == allow_zero and p["variant"] == variant:
            found = True
            digits = list(range(0, p["digit_pool_size"])) if p["allow_zero"] else list(
                range(1, p["digit_pool_size"] + 1)
            )
            assert payload["answer"] == _bruteforce_digit_parity(digits, p["positions"], p["variant"])
            break
    assert found


@pytest.mark.parametrize(
    "fn",
    [
        permutation_generators.permutation_adjacent_block,
        permutation_generators.permutation_digit_parity,
    ],
)
def test_same_seed_same_parameter_tuple_and_answer(fn) -> None:
    p1 = fn(skill_id="vh_數學B4_Test", subskill_id="test", difficulty=1, seed=3)
    p2 = fn(skill_id="vh_數學B4_Test", subskill_id="test", difficulty=1, seed=3)
    assert p1["parameters"]["parameter_tuple"] == p2["parameters"]["parameter_tuple"]
    assert p1["answer"] == p2["answer"]


@pytest.mark.parametrize(
    "fn",
    [
        permutation_generators.permutation_adjacent_block,
        permutation_generators.permutation_digit_parity,
    ],
)
def test_seed_diversity_in_first_10(fn) -> None:
    tuples = {
        fn(skill_id="vh_數學B4_Test", subskill_id="test", difficulty=1, seed=seed)["parameters"]["parameter_tuple"]
        for seed in range(1, 11)
    }
    assert len(tuples) >= 2


@pytest.mark.parametrize(
    "fn",
    [
        permutation_generators.permutation_adjacent_block,
        permutation_generators.permutation_digit_parity,
    ],
)
def test_seed_1_to_5_all_distinct(fn) -> None:
    tuples = {
        fn(skill_id="vh_數學B4_Test", subskill_id="test", difficulty=1, seed=seed)["parameters"]["parameter_tuple"]
        for seed in range(1, 6)
    }
    assert len(tuples) == 5


def test_seen_parameter_tuples_blocks_duplicates() -> None:
    seen: set[tuple] = set()
    first = permutation_generators.permutation_adjacent_block(
        skill_id="vh_數學B4_Test",
        subskill_id="test",
        difficulty=1,
        seed=1,
        seen_parameter_tuples=seen,
    )
    second = permutation_generators.permutation_adjacent_block(
        skill_id="vh_數學B4_Test",
        subskill_id="test",
        difficulty=1,
        seed=1,
        seen_parameter_tuples=seen,
    )
    assert first["parameters"]["parameter_tuple"] != second["parameters"]["parameter_tuple"]


def test_adjacent_block_raises_after_50_retries_when_space_exhausted() -> None:
    seen = {
        ("permutation_adjacent_block", n, 2, context)
        for n in range(5, 8)
        for context in ["students_line", "books_shelf", "photos_row"]
    }
    with pytest.raises(ValueError):
        permutation_generators.permutation_adjacent_block(
            skill_id="vh_數學B4_Test",
            subskill_id="test",
            difficulty=1,
            seed=10,
            seen_parameter_tuples=seen,
        )


def test_digit_parity_raises_after_50_retries_when_space_exhausted() -> None:
    seen = {
        ("permutation_digit_parity", digit_pool_size, positions, allow_zero, variant)
        for digit_pool_size in range(5, 8)
        for positions in [2, 3]
        for allow_zero in [True, False]
        for variant in ["odd_number", "even_number"]
    }
    with pytest.raises(ValueError):
        permutation_generators.permutation_digit_parity(
            skill_id="vh_數學B4_Test",
            subskill_id="test",
            difficulty=1,
            seed=10,
            seen_parameter_tuples=seen,
        )
