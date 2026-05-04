import pytest

from core.vocational_math_b4.domain.counting_domain_functions import (
    combination,
    divisor_count_from_prime_factorization,
    polygon_diagonal_count,
    polygon_triangle_count,
)
from core.vocational_math_b4.generators.combination import (
    combination_polygon_count,
    combination_required_excluded_person,
)
from core.vocational_math_b4.generators.counting import divisor_count_prime_factorization

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

PLACEHOLDERS = ["[BLANK]", "[FORMULA_MISSING]", "[FORMULA_IMAGE", "[WORD_EQUATION_UNPARSED]", "□", "＿＿"]


def _assert_mc_contract(payload: dict) -> None:
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]


def _assert_placeholder_free(payload: dict) -> None:
    for token in PLACEHOLDERS:
        assert token not in payload["question_text"]
        assert token not in payload["explanation"]


def test_divisor_count_prime_factorization_payload_and_answer() -> None:
    payload = divisor_count_prime_factorization(
        skill_id="s", subskill_id="ss", difficulty=2, seed=10, multiple_choice=True
    )
    _assert_mc_contract(payload)
    _assert_placeholder_free(payload)
    exponents = payload["parameters"]["exponents"]
    assert payload["answer"] == divisor_count_from_prime_factorization(exponents)


def test_divisor_count_prime_factorization_question_text_uses_latex() -> None:
    payload = divisor_count_prime_factorization(
        skill_id="s", subskill_id="ss", difficulty=1, seed=1, multiple_choice=True
    )
    text = payload["question_text"]
    assert "$N =" in text
    assert "^{" in text
    assert r"\times" in text

    for prime, exponent in zip(payload["parameters"]["primes"], payload["parameters"]["exponents"]):
        assert f"{prime}^{exponent}" not in text


def test_combination_polygon_count_payload_and_answer() -> None:
    payload = combination_polygon_count(skill_id="s", subskill_id="ss", difficulty=2, seed=20)
    _assert_mc_contract(payload)
    _assert_placeholder_free(payload)
    assert "C(n," not in payload["explanation"]
    assert "C(" not in payload["explanation"]
    assert "$" in payload["explanation"]
    assert "C^{" in payload["explanation"]
    n = payload["parameters"]["n"]
    variant = payload["parameters"]["question_variant"]
    if variant == "diagonal":
        assert payload["answer"] == polygon_diagonal_count(n)
    else:
        assert payload["answer"] == polygon_triangle_count(n)


def test_combination_required_excluded_person_payload_and_answer() -> None:
    payload = combination_required_excluded_person(skill_id="s", subskill_id="ss", difficulty=3, seed=30)
    _assert_mc_contract(payload)
    _assert_placeholder_free(payload)
    assert "C(n," not in payload["explanation"]
    assert "C(" not in payload["explanation"]
    assert "$" in payload["explanation"]
    assert "C^{" in payload["explanation"]
    n = payload["parameters"]["n"]
    r = payload["parameters"]["r"]
    k = payload["parameters"]["k"]
    ctype = payload["parameters"]["constraint_type"]
    if ctype == "required":
        assert payload["answer"] == combination(n - k, r - k)
    else:
        assert payload["answer"] == combination(n - k, r)


def test_multiple_choice_false_returns_empty_choices() -> None:
    p1 = divisor_count_prime_factorization(skill_id="s", subskill_id="ss", seed=1, multiple_choice=False)
    p2 = combination_polygon_count(skill_id="s", subskill_id="ss", seed=2, multiple_choice=False)
    p3 = combination_required_excluded_person(skill_id="s", subskill_id="ss", seed=3, multiple_choice=False)
    assert p1["choices"] == []
    assert p2["choices"] == []
    assert p3["choices"] == []


def test_same_seed_same_parameters_and_answer() -> None:
    p1 = divisor_count_prime_factorization(skill_id="s", subskill_id="ss", seed=88)
    p2 = divisor_count_prime_factorization(skill_id="s", subskill_id="ss", seed=88)
    assert p1["parameters"]["parameter_tuple"] == p2["parameters"]["parameter_tuple"]
    assert p1["answer"] == p2["answer"]


def test_different_seeds_produce_variety() -> None:
    poly_tuples = set()
    req_tuples = set()
    for sd in range(1, 6):
        poly_payload = combination_polygon_count(skill_id="s", subskill_id="ss", seed=sd)
        poly_tuples.add(poly_payload["parameters"]["parameter_tuple"])
        req_payload = combination_required_excluded_person(skill_id="s", subskill_id="ss", seed=sd)
        req_tuples.add(req_payload["parameters"]["parameter_tuple"])
    
    assert len(poly_tuples) == 5, "combination_polygon_count should produce 5 unique tuples for seeds 1-5"
    assert len(req_tuples) == 5, "combination_required_excluded_person should produce 5 unique tuples for seeds 1-5"


def test_seen_parameter_tuples_blocks_duplicates() -> None:
    seen: set[tuple] = set()
    first = combination_required_excluded_person(skill_id="s", subskill_id="ss", seed=7, seen_parameter_tuples=seen)
    second = combination_required_excluded_person(skill_id="s", subskill_id="ss", seed=7, seen_parameter_tuples=seen)
    assert first["parameters"]["parameter_tuple"] != second["parameters"]["parameter_tuple"]


def test_invalid_seen_parameter_tuples_raise_value_error() -> None:
    with pytest.raises(ValueError):
        divisor_count_prime_factorization(skill_id="s", subskill_id="ss", seen_parameter_tuples=[])


def test_raise_when_retries_exhausted() -> None:
    blocked = {
        (
            "divisor_count_prime_factorization",
            tuple(primes),
            tuple(exponents),
        )
        for primes in ([2, 3], [2, 5], [2, 7], [2, 11], [3, 5], [3, 7], [3, 11], [5, 7], [5, 11], [7, 11])
        for exponents in (
            [1, 1], [1, 2], [1, 3],
            [2, 1], [2, 2], [2, 3],
            [3, 1], [3, 2], [3, 3],
        )
    }
    with pytest.raises(ValueError):
        divisor_count_prime_factorization(
            skill_id="s",
            subskill_id="ss",
            difficulty=1,
            seed=123,
            seen_parameter_tuples=blocked,
        )
