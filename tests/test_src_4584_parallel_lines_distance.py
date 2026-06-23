from __future__ import annotations

from fractions import Fraction

from agent_skills_v3.vh_數學B1_DistanceBetweenTwoParallelLines.components.src_4584.generate import (
    generate,
)
from core.gencode.runtime_skill_wrapper import check_answer


def _choice_value(payload: dict) -> int:
    label = payload["answer"]
    for choice in payload["choices"]:
        if choice["label"] == label:
            return int(choice["text"])
    raise AssertionError("correct label missing from choices")


def _assert_src_4584_isomorphic(payload: dict) -> None:
    question = payload["question_text"]
    raw = payload["metadata"]["raw_givens"]
    a = int(raw["a"])
    b = int(raw["b"])
    k = int(raw["k"])
    slope = Fraction(str(raw["slope"]))
    distance_squared = Fraction(str(raw["origin_distance_squared"]))

    assert "a>0" not in question
    assert "a=" not in question
    assert "ax+2ay+k=0" not in question
    assert b != 0
    assert k > 0

    solved_a = -slope * b
    assert solved_a.denominator == 1
    assert int(solved_a) == a

    norm_sq = a * a + b * b
    solved_k_squared = distance_squared * norm_sq
    assert solved_k_squared.denominator == 1
    assert int(solved_k_squared) == k * k
    assert k == abs(k)

    assert a + k == int(raw["answer_value"])
    assert _choice_value(payload) == a + k
    assert payload["answer"] == payload["correct_answer"] == payload["display_answer"] == payload["semantic_answer"]

    choices = payload["choices"]
    labels = [choice["label"] for choice in choices]
    values = [choice["text"] for choice in choices]
    assert labels == ["A", "B", "C", "D"]
    assert len(values) == len(set(values)) == 4
    assert str(a + k) in values

    assert payload["problem_type_id"] == "parallel_lines_distance_single_choice"
    assert payload["component_id"] == "src_4584"
    assert payload["textbook_example_id"] == 4584
    assert payload["answer_contract"]["checker"] == "choice_label_checker"
    assert check_answer(payload["answer"], payload["correct_answer"], payload=payload)


def test_src_4584_seed_1_preserves_112_tvet_b_structure() -> None:
    payload = generate(seed=1, component_id="src_4584")
    raw = payload["metadata"]["raw_givens"]

    assert (raw["a"], raw["b"], raw["k"]) == (-2, 4, 10)
    assert raw["slope"] == "1/2"
    assert raw["origin_distance"] == "\\sqrt{5}"
    assert _choice_value(payload) == 8
    _assert_src_4584_isomorphic(payload)


def test_src_4584_samples_50_isomorphic_items() -> None:
    seen_questions = set()
    for seed in range(50):
        payload = generate(seed=seed, component_id="src_4584")
        _assert_src_4584_isomorphic(payload)
        seen_questions.add(payload["question_text"])

    assert len(seen_questions) >= 10


def test_src_4584_final_answer_contract_fields_are_choice_label() -> None:
    payload = generate(seed=8, component_id="src_4584")

    assert payload["answer_type"] == "choice_label"
    assert payload["answer_value_type"] == "choice_label"
    assert payload["answer_contract"]["answer_type"] == "choice_label"
    assert payload["answer_contract"]["answer_equivalence"] == "choice_label"
