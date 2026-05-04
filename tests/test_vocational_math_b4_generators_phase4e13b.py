import pytest

from core.vocational_math_b4.domain.binomial_domain_functions import (
    binomial_expansion_coefficients,
)
from core.vocational_math_b4.domain.counting_domain_functions import combination
from core.vocational_math_b4.generators.binomial import (
    binomial_coefficient_sum,
    binomial_equation_solve_n,
    binomial_specific_term_coefficient,
)


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

GENERATORS = [
    binomial_coefficient_sum,
    binomial_specific_term_coefficient,
    binomial_equation_solve_n,
]


def _payload(generator, seed=1, multiple_choice=True, **kwargs):
    return generator(
        skill_id="vh_數學B4_BinomialTheorem",
        subskill_id="b4_ch1_binomial_test",
        difficulty=kwargs.pop("difficulty", 1),
        seed=seed,
        seen_parameter_tuples=kwargs.pop("seen_parameter_tuples", None),
        multiple_choice=multiple_choice,
    )


def _assert_contract(payload):
    assert REQUIRED_KEYS <= payload.keys()
    assert "parameter_tuple" in payload["parameters"]
    assert "correct_answer" not in payload


def _assert_no_placeholder(payload):
    blocked = ["[BLANK]", "[FORMULA_MISSING]", "[WORD_EQUATION_UNPARSED]", "□", "＿＿"]
    for token in blocked:
        assert token not in payload["question_text"]
        assert token not in payload["explanation"]


def _assert_latex(payload):
    text = payload["question_text"] + payload["explanation"]
    assert "$" in text
    assert "^{" in text
    assert "2^2" not in text
    assert "C(n,r)" not in text
    assert "P(n,r)" not in text
    if payload["problem_type_id"] == "binomial_equation_solve_n":
        assert "C^{" in text or "\\binom" in text


def _assert_choices(payload):
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]


def _exhausted_difficulty_one_tuples(generator):
    if generator is binomial_coefficient_sum:
        return {("binomial_coefficient_sum", 1, b, n) for b in range(1, 5) for n in range(2, 6)}
    if generator is binomial_specific_term_coefficient:
        return {
            ("binomial_specific_term_coefficient", 1, b, n, k)
            for b in range(1, 5)
            for n in range(2, 6)
            for k in range(0, n + 1)
        }

    r1 = {
        ("binomial_equation_solve_n", n, 1, combination(n, 1), "r1")
        for n in range(3, 13)
    }
    r2 = {
        ("binomial_equation_solve_n", n, 2, combination(n, 2), "r2")
        for n in range(4, 11)
    }
    return r1 | r2


def test_three_generators_can_import():
    assert callable(binomial_coefficient_sum)
    assert callable(binomial_specific_term_coefficient)
    assert callable(binomial_equation_solve_n)


@pytest.mark.parametrize("generator", GENERATORS)
def test_payload_contract_common_fields(generator):
    payload = _payload(generator, seed=1)
    _assert_contract(payload)
    _assert_no_placeholder(payload)
    _assert_latex(payload)
    _assert_choices(payload)
    assert isinstance(payload["answer"], int)


def test_binomial_coefficient_sum_answer_uses_coefficients():
    payload = _payload(binomial_coefficient_sum, seed=2)
    params = payload["parameters"]
    expected = sum(binomial_expansion_coefficients(params["a"], params["b"], params["n"]))
    assert payload["problem_type_id"] == "binomial_coefficient_sum"
    assert payload["generator_key"] == "b4.binomial.binomial_coefficient_sum"
    assert payload["answer"] == expected


def test_binomial_specific_term_coefficient_answer_uses_coefficients():
    payload = _payload(binomial_specific_term_coefficient, seed=2)
    params = payload["parameters"]
    coefficients = binomial_expansion_coefficients(params["a"], params["b"], params["n"])
    expected = coefficients[params["n"] - params["k"]]
    assert payload["problem_type_id"] == "binomial_specific_term_coefficient"
    assert payload["generator_key"] == "b4.binomial.binomial_specific_term_coefficient"
    assert payload["answer"] == expected


def test_binomial_equation_solve_n_answer_uses_combination_for_m():
    payload = _payload(binomial_equation_solve_n, seed=2)
    params = payload["parameters"]
    assert payload["problem_type_id"] == "binomial_equation_solve_n"
    assert payload["generator_key"] == "b4.binomial.binomial_equation_solve_n"
    assert params["m"] == combination(params["n"], params["r"])
    assert payload["answer"] == params["n"]


@pytest.mark.parametrize("generator", GENERATORS)
def test_multiple_choice_false_has_empty_choices(generator):
    payload = _payload(generator, seed=1, multiple_choice=False)
    assert payload["choices"] == []
    assert isinstance(payload["answer"], int)


@pytest.mark.parametrize("generator", GENERATORS)
def test_same_seed_is_deterministic(generator):
    first = _payload(generator, seed=3)
    second = _payload(generator, seed=3)
    assert first["parameters"]["parameter_tuple"] == second["parameters"]["parameter_tuple"]
    assert first["answer"] == second["answer"]


@pytest.mark.parametrize("generator", GENERATORS)
def test_ten_seeds_produce_variety(generator):
    tuples = {_payload(generator, seed=seed)["parameters"]["parameter_tuple"] for seed in range(1, 11)}
    assert len(tuples) >= 2


@pytest.mark.parametrize("generator", GENERATORS)
def test_seed_one_to_five_are_distinct(generator):
    tuples = [_payload(generator, seed=seed)["parameters"]["parameter_tuple"] for seed in range(1, 6)]
    assert len(set(tuples)) == 5


@pytest.mark.parametrize("generator", GENERATORS)
def test_seen_parameter_tuples_prevents_reuse(generator):
    seen = set()
    first = _payload(generator, seed=1, seen_parameter_tuples=seen)
    second = _payload(generator, seed=1, seen_parameter_tuples=seen)
    assert first["parameters"]["parameter_tuple"] in seen
    assert second["parameters"]["parameter_tuple"] in seen
    assert first["parameters"]["parameter_tuple"] != second["parameters"]["parameter_tuple"]


@pytest.mark.parametrize("generator", GENERATORS)
def test_fifty_retries_raise_value_error(generator):
    seen = _exhausted_difficulty_one_tuples(generator)
    with pytest.raises(ValueError):
        _payload(generator, seed=1, seen_parameter_tuples=seen)
