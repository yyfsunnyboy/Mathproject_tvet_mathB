import re

import pytest

from core.vocational_math_b4.domain.b4_validators import validate_problem_payload_contract
from core.vocational_math_b4.domain.counting_domain_functions import (
    addition_principle_count,
    repeated_choice_count,
)
from core.vocational_math_b4.domain.counting_domain_functions import combination
from core.vocational_math_b4.generators.combination import combination_properties_simplification
from core.vocational_math_b4.generators.counting import (
    add_principle_mutually_exclusive_choice,
    repeated_choice_basic,
)


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
    assert callable(add_principle_mutually_exclusive_choice)
    assert callable(combination_properties_simplification)
    assert callable(repeated_choice_basic)


@pytest.mark.parametrize(
    "fn",
    [
        add_principle_mutually_exclusive_choice,
        combination_properties_simplification,
        repeated_choice_basic,
    ],
)
def test_payload_contract_and_answer_type(fn) -> None:
    payload = fn(
        skill_id="vh_b4_test",
        subskill_id="unit_test",
        difficulty=2,
        seed=11,
        multiple_choice=True,
    )
    _check_contract(payload)
    assert isinstance(payload["answer"], int)


def test_answer_correct_addition_principle() -> None:
    payload = add_principle_mutually_exclusive_choice(
        skill_id="vh_b4_addition_principle",
        subskill_id="add_principle_mutually_exclusive_choice",
        seed=3,
    )
    assert payload["answer"] == addition_principle_count(payload["parameters"]["counts"])


def test_answer_correct_combination_properties() -> None:
    payload = combination_properties_simplification(
        skill_id="vh_b4_combination_properties",
        subskill_id="combination_properties_simplification",
        seed=4,
    )
    assert payload["answer"] == combination(payload["parameters"]["n"], payload["parameters"]["r"])


def test_answer_correct_repeated_choice() -> None:
    payload = repeated_choice_basic(
        skill_id="vh_b4_repeated_choice",
        subskill_id="repeated_choice_basic",
        seed=5,
    )
    assert payload["answer"] == repeated_choice_count(
        payload["parameters"]["choices_per_position"],
        payload["parameters"]["positions"],
    )


@pytest.mark.parametrize(
    "fn,has_sup_or_comb",
    [
        (add_principle_mutually_exclusive_choice, False),
        (combination_properties_simplification, True),
        (repeated_choice_basic, True),
    ],
)
def test_placeholder_and_latex_format(fn, has_sup_or_comb: bool) -> None:
    payload = fn(
        skill_id="vh_b4_test",
        subskill_id="unit_test",
        seed=7,
    )
    q = payload["question_text"]
    e = payload["explanation"]
    assert "[BLANK]" not in q and "[BLANK]" not in e
    _check_latex(q if "$" in q else e)
    if has_sup_or_comb:
        target = q + "\n" + e
        assert (re.search(r"\^\{[^}]+\}", target) is not None) or ("$C(" in target) or ("\\binom" in target)


@pytest.mark.parametrize(
    "fn",
    [
        add_principle_mutually_exclusive_choice,
        combination_properties_simplification,
        repeated_choice_basic,
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
        add_principle_mutually_exclusive_choice,
        combination_properties_simplification,
        repeated_choice_basic,
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
        add_principle_mutually_exclusive_choice,
        combination_properties_simplification,
        repeated_choice_basic,
    ],
)
def test_different_seed_generates_variety(fn) -> None:
    tuples = {
        fn(skill_id="vh", subskill_id="sub", seed=seed)["parameters"]["parameter_tuple"]
        for seed in range(1, 11)
    }
    assert len(tuples) >= 2


@pytest.mark.parametrize(
    "fn",
    [
        add_principle_mutually_exclusive_choice,
        combination_properties_simplification,
        repeated_choice_basic,
    ],
)
def test_seed_1_to_5_all_distinct(fn) -> None:
    tuples = [
        fn(skill_id="vh", subskill_id="sub", seed=seed)["parameters"]["parameter_tuple"]
        for seed in range(1, 6)
    ]
    assert len(set(tuples)) == 5


@pytest.mark.parametrize(
    "fn",
    [
        add_principle_mutually_exclusive_choice,
        combination_properties_simplification,
        repeated_choice_basic,
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
        add_principle_mutually_exclusive_choice,
        combination_properties_simplification,
        repeated_choice_basic,
    ],
)
def test_retry_50_failure_raises(fn, monkeypatch) -> None:
    if fn is add_principle_mutually_exclusive_choice:
        def _fixed_addition(_rng, _difficulty):
            return ["球類社團", "音樂社團"], [3, 4]

        monkeypatch.setattr(
            "core.vocational_math_b4.generators.counting._sample_addition_parameters",
            _fixed_addition,
        )
        seen = {("add_principle_mutually_exclusive_choice", ("球類社團", "音樂社團"), (3, 4))}
    elif fn is combination_properties_simplification:
        def _fixed_comb(_rng, _difficulty):
            return 10, 8, "symmetry"

        monkeypatch.setattr(
            "core.vocational_math_b4.generators.combination._sample_combination_properties_parameters",
            _fixed_comb,
        )
        seen = {("combination_properties_simplification", 10, 8, "symmetry")}
    else:
        def _fixed_repeat(_rng, _difficulty):
            return 2, 2

        monkeypatch.setattr(
            "core.vocational_math_b4.generators.counting._sample_repeated_choice_parameters",
            _fixed_repeat,
        )
        seen = {("repeated_choice_basic", 2, 2)}

    with pytest.raises(ValueError):
        fn(skill_id="vh", subskill_id="sub", seed=1, seen_parameter_tuples=seen)


def test_combination_properties_simplification_formatting() -> None:
    for seed in range(10):
        payload = combination_properties_simplification(
            skill_id="test", subskill_id="test", seed=seed
        )
        q = payload["question_text"]
        e = payload["explanation"]

        assert "$C(" not in q
        assert "C^{" in q or "C^{" in e
        assert "C(n,r)" not in e
