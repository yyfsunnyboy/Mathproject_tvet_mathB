"""Deterministic B4 combination generators (Phase 4B-2)."""

from __future__ import annotations

import random

from core.vocational_math_b4.domain.b4_validators import (
    validate_answer_in_choices,
    validate_choices_unique,
    validate_no_unfilled_placeholder,
    validate_problem_payload_contract,
)
from core.vocational_math_b4.domain.counting_domain_functions import (
    combination,
    polygon_diagonal_count,
    polygon_triangle_count,
)

PROBLEM_TYPE_ID = "combination_definition_basic"
GENERATOR_KEY = "b4.combination.combination_definition_basic"
POLYGON_PROBLEM_TYPE_ID = "combination_polygon_count"
POLYGON_GENERATOR_KEY = "b4.combination.combination_polygon_count"
REQ_EXC_PROBLEM_TYPE_ID = "combination_required_excluded_person"
REQ_EXC_GENERATOR_KEY = "b4.combination.combination_required_excluded_person"
GROUP_SELECTION_PROBLEM_TYPE_ID = "combination_group_selection"
GROUP_SELECTION_GENERATOR_KEY = "b4.combination.combination_group_selection"


def _make_numeric_choices(answer: int, rng: random.Random) -> list[int]:
    if answer < 0:
        raise ValueError("answer must be nonnegative for choice generation.")
    candidates = {
        answer,
        max(0, answer - 1),
        max(0, answer + 1),
        max(0, answer - 2),
        max(0, answer + 2),
        answer * 2,
        max(0, answer // 2),
        answer + 3,
    }
    choices = [answer]
    for value in candidates:
        if value not in choices:
            choices.append(value)
        if len(choices) == 4:
            break
    while len(choices) < 4:
        extra = max(0, answer + rng.randint(4, 12))
        if extra not in choices:
            choices.append(extra)
    rng.shuffle(choices)
    return choices


def _sample_parameters(rng: random.Random, difficulty: int) -> tuple[int, int]:
    if difficulty <= 1:
        n = rng.randint(5, 8)
        r = rng.randint(2, 3)
    elif difficulty == 2:
        n = rng.randint(8, 12)
        r = rng.randint(2, 4)
    else:
        n = rng.randint(10, 15)
        r = rng.randint(3, 5)
    if r > n:
        r = n
    return n, r


def generate(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a deterministic combination-definition problem payload."""
    if seen_parameter_tuples is not None and not isinstance(seen_parameter_tuples, set):
        raise ValueError("seen_parameter_tuples must be a set or None.")

    rng = random.Random(seed)
    seen = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    parameter_tuple: tuple | None = None
    n = r = 0
    for _ in range(50):
        n, r = _sample_parameters(rng, difficulty)
        candidate = (PROBLEM_TYPE_ID, n, r)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = combination(n, r)
    question_text = f"從 {n} 件不同作品中選出 {r} 件展示，共有多少種選法？"
    explanation = f"此題不計順序，使用 C(n,r)=n!/(r!(n-r)!)，所以 C({n},{r})={answer}。"

    choices = _make_numeric_choices(answer, rng) if multiple_choice else []
    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": PROBLEM_TYPE_ID,
        "generator_key": GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["combination_definition_basic", "combination", "n_ge_r"],
        "remediation_candidates": [],
        "source_style_refs": ["tc_comb_definition_01", "combination_definition_basic"],
        "parameters": {
            "n": n,
            "r": r,
            "parameter_tuple": parameter_tuple,
        },
    }

    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if multiple_choice:
        validate_choices_unique(payload["choices"])
        validate_answer_in_choices(payload["answer"], payload["choices"])

    seen.add(parameter_tuple)
    return payload


def _ensure_seen_set(seen_parameter_tuples: set[tuple] | None) -> set[tuple]:
    if seen_parameter_tuples is None:
        return set()
    if not isinstance(seen_parameter_tuples, set):
        raise ValueError("seen_parameter_tuples must be a set or None.")
    return seen_parameter_tuples


def _validate_and_finalize(payload: dict, multiple_choice: bool) -> None:
    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if multiple_choice:
        validate_choices_unique(payload["choices"])
        validate_answer_in_choices(payload["answer"], payload["choices"])


def _sample_polygon_n(rng: random.Random, difficulty: int) -> int:
    if difficulty <= 1:
        return rng.randint(5, 8)
    if difficulty == 2:
        return rng.randint(7, 10)
    return rng.randint(9, 12)


def combination_polygon_count(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic polygon counting problems."""
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    n = 0
    question_variant = ""
    for _ in range(50):
        for _ in range(7):
            _ = rng.random()  # Shift PRNG state to prevent early seed collisions
        n = _sample_polygon_n(rng, difficulty)
        question_variant = rng.choice(["diagonal", "triangle"])
        candidate = (POLYGON_PROBLEM_TYPE_ID, n, question_variant)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    if question_variant == "diagonal":
        answer = polygon_diagonal_count(n)
        question_text = f"一個正 {n} 邊形共有多少條對角線？"
        explanation = f"對角線數公式為 C(n,2)-n，所以 C({n},2)-{n}={answer}。"
    else:
        answer = polygon_triangle_count(n)
        question_text = f"一個正 {n} 邊形任取 3 個頂點可形成多少個三角形？"
        explanation = f"三角形數為 C(n,3)，所以 C({n},3)={answer}。"

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": POLYGON_PROBLEM_TYPE_ID,
        "generator_key": POLYGON_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["combination_polygon_count", "combination", "geometry_counting"],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_comb_geometry_02",
            "tc_comb_polygon_diagonal_triangle_02",
            "combination_polygon_count",
        ],
        "parameters": {
            "n": n,
            "question_variant": question_variant,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def _sample_required_excluded_parameters(rng: random.Random, difficulty: int) -> tuple[int, int, str, int]:
    if difficulty <= 1:
        n = rng.randint(6, 10)
        r = rng.randint(2, 4)
        k = 1
    elif difficulty == 2:
        n = rng.randint(8, 12)
        r = rng.randint(3, 5)
        k = 1
    else:
        n = rng.randint(10, 15)
        r = rng.randint(3, 6)
        k = rng.choice([1, 2])
    constraint_type = rng.choice(["required", "excluded"])
    if r > n:
        r = n
    if constraint_type == "required" and r < k:
        r = k
    if n - k < r:
        r = n - k
    return n, r, constraint_type, k


def combination_required_excluded_person(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic required/excluded person combination problems."""
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    n = r = k = 0
    constraint_type = ""
    for _ in range(50):
        _ = rng.random()  # Shift PRNG state to prevent early seed collisions
        n, r, constraint_type, k = _sample_required_excluded_parameters(rng, difficulty)
        candidate = (REQ_EXC_PROBLEM_TYPE_ID, n, r, constraint_type, k)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    if constraint_type == "required":
        answer = combination(n - k, r - k)
        question_text = (
            f"某班有 {n} 位同學，今選出 {r} 位參加活動，若甲必須入選，共有多少種選法？"
        )
        explanation = (
            f"必選情況先固定指定人物，再從剩下 {n-k} 人選 {r-k} 人，"
            f"使用 C(n,r) 得 C({n-k},{r-k})={answer}。"
        )
    else:
        answer = combination(n - k, r)
        question_text = (
            f"某班有 {n} 位同學，今選出 {r} 位參加活動，若甲不能入選，共有多少種選法？"
        )
        explanation = (
            f"不可選情況先排除指定人物，再從剩下 {n-k} 人選 {r} 人，"
            f"使用 C(n,r) 得 C({n-k},{r})={answer}。"
        )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": REQ_EXC_PROBLEM_TYPE_ID,
        "generator_key": REQ_EXC_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "combination_required_excluded_person",
            "combination",
            "constraint_selection",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_comb_required_or_excluded_person_01",
            "combination_required_excluded_person",
        ],
        "parameters": {
            "n": n,
            "r": r,
            "constraint_type": constraint_type,
            "k": k,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def _sample_group_selection_parameters(rng: random.Random, difficulty: int) -> tuple[list[int], list[int]]:
    if difficulty <= 1:
        group_count = 2
        size_low, size_high = 4, 8
        pick_low, pick_high = 1, 3
    elif difficulty == 2:
        group_count = rng.choice([2, 3])
        size_low, size_high = 5, 10
        pick_low, pick_high = 1, 4
    else:
        group_count = 3
        size_low, size_high = 6, 12
        pick_low, pick_high = 2, 5

    group_sizes = [rng.randint(size_low, size_high) for _ in range(group_count)]
    picks: list[int] = []
    for size in group_sizes:
        picks.append(rng.randint(pick_low, min(pick_high, size)))
    return group_sizes, picks


def combination_group_selection(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic multi-group combination selection problems."""
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    group_sizes: list[int] = []
    picks: list[int] = []
    for _ in range(50):
        group_sizes, picks = _sample_group_selection_parameters(rng, difficulty)
        candidate = (GROUP_SELECTION_PROBLEM_TYPE_ID, tuple(group_sizes), tuple(picks))
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    parts = []
    coeffs = []
    answer = 1
    for idx, (size, pick) in enumerate(zip(group_sizes, picks), start=1):
        parts.append(f"第{idx}組有 {size} 人，選 {pick} 人")
        coeffs.append(f"\\binom{{{size}}}{{{pick}}}")
        answer *= combination(size, pick)

    question_text = f"{'、'.join(parts)}，共有多少種選法？"
    latex_product = " \\times ".join(coeffs)
    explanation = f"各組獨立，使用 ${latex_product}={answer}$。"

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": GROUP_SELECTION_PROBLEM_TYPE_ID,
        "generator_key": GROUP_SELECTION_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "combination_group_selection",
            "combination",
            "multiplication_principle",
        ],
        "remediation_candidates": [],
        "source_style_refs": ["tc_comb_group_selection_03", "combination_group_selection"],
        "parameters": {
            "group_sizes": group_sizes,
            "picks": picks,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def _sample_combination_properties_parameters(rng: random.Random, difficulty: int) -> tuple[int, int, str]:
    if difficulty <= 1:
        n = rng.randint(5, 10)
        r = rng.randint(1, 4)
    elif difficulty == 2:
        n = rng.randint(8, 15)
        r = rng.randint(2, 6)
    else:
        n = rng.randint(12, 20)
        r = rng.randint(3, 8)
    if r > n:
        r = n

    variant = rng.choice(["symmetry", "direct"])
    if variant == "symmetry" and r <= n - r:
        r = n - rng.randint(1, min(4, n - 1))
        if r < 0:
            r = 0
        if r > n:
            r = n
    return n, r, variant


def combination_properties_simplification(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    from core.vocational_math_b4.domain.counting_domain_functions import combination

    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)
    problem_type_id = "combination_properties_simplification"
    generator_key = "b4.combination.combination_properties_simplification"

    parameter_tuple: tuple | None = None
    n = r = 0
    variant = ""
    for _ in range(50):
        n, r, variant = _sample_combination_properties_parameters(rng, difficulty)
        candidate = (problem_type_id, n, r, variant)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = combination(n, r)
    if variant == "symmetry":
        question_text = f"利用組合性質 $C^{{n}}_{{r}}=C^{{n}}_{{n-r}}$，求 $C^{{{n}}}_{{{r}}}$ 的值。"
        explanation = (
            f"使用 $C^{{n}}_{{r}}=C^{{n}}_{{n-r}}$，所以 $C^{{{n}}}_{{{r}}}=C^{{{n}}}_{{{n-r}}}={answer}$。"
        )
    else:
        question_text = f"計算組合數 $C^{{{n}}}_{{{r}}}$ 的值。"
        explanation = (
            f"使用 $C^{{n}}_{{r}}=\\frac{{n!}}{{r!(n-r)!}}$ 計算，可得 $C^{{{n}}}_{{{r}}}={answer}$。"
        )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": problem_type_id,
        "generator_key": generator_key,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "combination_properties_simplification",
            "combination",
            "symmetry_identity",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_comb_properties_simplification_01",
            "combination_properties_simplification",
        ],
        "parameters": {
            "n": n,
            "r": r,
            "variant": variant,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload
