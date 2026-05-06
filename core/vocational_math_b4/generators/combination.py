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
    permutation,
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
BASIC_SELECTION_PROBLEM_TYPE_ID = "combination_basic_selection"
BASIC_SELECTION_GENERATOR_KEY = "b4.combination.combination_basic_selection"
RESTRICTED_SELECTION_PROBLEM_TYPE_ID = "combination_restricted_selection"
RESTRICTED_SELECTION_GENERATOR_KEY = "b4.combination.combination_restricted_selection"
SEAT_ASSIGNMENT_PROBLEM_TYPE_ID = "combination_seat_assignment"
SEAT_ASSIGNMENT_GENERATOR_KEY = "b4.combination.combination_seat_assignment"
GRID_SHORTEST_PATH_PROBLEM_TYPE_ID = "grid_shortest_path_count"
GRID_SHORTEST_PATH_GENERATOR_KEY = "b4.combination.grid_shortest_path_count"
_MAX_GRID_PATH_ANSWER = 500_000

_GRID_PATH_TEMPLATE_CONTEXTS = (
    "chessboard_roads",
    "campus_grid",
    "street_grid",
    "generic_ab",
)


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
    template_context = "works_exhibit"
    context_pool = (
        "works_exhibit",
        "exam_pick",
        "committee",
        "sample_draw",
        "delegate_pick",
    )
    for _ in range(50):
        n, r = _sample_parameters(rng, difficulty)
        template_context = rng.choice(context_pool)
        candidate = (PROBLEM_TYPE_ID, n, r, template_context)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = combination(n, r)
    if template_context == "works_exhibit":
        question_text = (
            f"從 ${n}$ 件不同作品中選出 ${r}$ 件展示（不論展示順序），共有多少種選法？"
        )
    elif template_context == "exam_pick":
        question_text = (
            f"一份測驗共有 ${n}$ 題相異題目，需從中選答 ${r}$ 題（不論作答順序），共有多少種選題組合？"
        )
    elif template_context == "committee":
        question_text = (
            f"從 ${n}$ 人中選出 ${r}$ 人組成委員會（職務未指定、不計順序），共有多少種組成方式？"
        )
    elif template_context == "sample_draw":
        question_text = (
            f"從 ${n}$ 份相異樣本中抽出 ${r}$ 份檢驗（不計抽取順序），共有多少種抽法？"
        )
    else:
        question_text = (
            f"從 ${n}$ 位代表中推選 ${r}$ 人擔任工作小組（不計順序），共有多少種推選結果？"
        )

    explanation = (
        "不計順序，故為組合："
        f"$\\displaystyle C^{{{n}}}_{{{r}}}=\\frac{{{n}!}}{{{r}!({n}-{r})!}}={answer}$。"
    )

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
            "template_context": template_context,
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
        explanation = f"對角線數公式為 $C^{{n}}_{{2}}-n$，所以 $C^{{{n}}}_{{2}}-{n}={answer}$。"
    else:
        answer = polygon_triangle_count(n)
        question_text = f"一個正 {n} 邊形任取 3 個頂點可形成多少個三角形？"
        explanation = f"三角形數為 $C^{{n}}_{{3}}$，所以 $C^{{{n}}}_{{3}}={answer}$。"

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
            f"使用 $C^{{n}}_{{r}}$ 得 $C^{{{n-k}}}_{{{r-k}}}={answer}$。"
        )
    else:
        answer = combination(n - k, r)
        question_text = (
            f"某班有 {n} 位同學，今選出 {r} 位參加活動，若甲不能入選，共有多少種選法？"
        )
        explanation = (
            f"不可選情況先排除指定人物，再從剩下 {n-k} 人選 {r} 人，"
            f"使用 $C^{{n}}_{{r}}$ 得 $C^{{{n-k}}}_{{{r}}}={answer}$。"
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


def _sample_combination_properties_parameters(
    rng: random.Random, difficulty: int
) -> tuple[str, int, int, int | None]:
    """Return (variant, n, r_or_r1, r2_or_none). For two_term_sum: r1, r2 both set; else r2 is None."""
    variant = rng.choice(["symmetry", "direct", "symmetry_word", "two_term_sum"])
    if variant == "two_term_sum":
        if difficulty <= 1:
            n = rng.randint(8, 12)
        elif difficulty == 2:
            n = rng.randint(10, 15)
        else:
            n = rng.randint(12, 18)
        for _ in range(80):
            r1 = rng.randint(2, max(2, n - 3))
            r2 = rng.randint(2, max(2, n - 3))
            if r1 == r2:
                continue
            if combination(n, r1) + combination(n, r2) <= 8000:
                return "two_term_sum", n, r1, r2
        r1, r2 = 2, 3
        if n <= r2:
            n = 8
        return "two_term_sum", n, r1, r2

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

    if variant in {"symmetry", "symmetry_word"} and r <= n - r:
        r = n - rng.randint(1, min(4, max(1, n - 1)))
        if r < 0:
            r = 0
        if r > n:
            r = n
    return variant, n, r, None


def _sample_combination_basic_selection_params(
    rng: random.Random, difficulty: int
) -> tuple[int, int, str]:
    if difficulty <= 1:
        n = rng.randint(5, 10)
        r = rng.randint(2, 4)
    elif difficulty == 2:
        n = rng.randint(8, 15)
        r = rng.randint(2, 6)
    else:
        n = rng.randint(12, 20)
        r = rng.randint(3, 8)
    if r > n:
        r = n
    context = rng.choice(["books", "students", "questions", "gifts"])
    return n, r, context


def combination_basic_selection(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic basic combination selection (C(n,r)) problems."""
    rng = random.Random(seed)
    if seed is not None:
        for _ in range(seed * 11):
            rng.random()
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    n = r = 0
    context = ""
    for _ in range(50):
        n, r, context = _sample_combination_basic_selection_params(rng, difficulty)
        candidate = (BASIC_SELECTION_PROBLEM_TYPE_ID, n, r, context)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = combination(n, r)
    if context == "books":
        question_text = f"從 {n} 本不同的書中選出 {r} 本，共有多少種選法？"
    elif context == "students":
        question_text = f"從 {n} 位同學中選出 {r} 位，共有多少種選法？"
    elif context == "questions":
        question_text = f"從 {n} 題中選出 {r} 題作答，共有多少種選法？"
    else:
        question_text = f"從 {n} 件不同禮物中選出 {r} 件，共有多少種選法？"

    explanation = (
        "不考慮順序，使用 $C^{n}_{r}=\\frac{n!}{r!(n-r)!}$，"
        f"所以 $C^{{{n}}}_{{{r}}}={answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": BASIC_SELECTION_PROBLEM_TYPE_ID,
        "generator_key": BASIC_SELECTION_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["combination_basic_selection", "combination", "order_not_matters"],
        "remediation_candidates": [],
        "source_style_refs": ["tc_comb_basic_selection_01", "combination_basic_selection"],
        "parameters": {
            "n": n,
            "r": r,
            "context": context,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


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
    n = r = r1 = r2 = 0
    variant = ""
    for _ in range(50):
        variant, n, r1, r2 = _sample_combination_properties_parameters(rng, difficulty)
        if variant == "two_term_sum":
            assert r2 is not None
            candidate = (problem_type_id, variant, n, r1, r2)
        else:
            candidate = (problem_type_id, variant, n, r1)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    if variant == "two_term_sum":
        assert r2 is not None
        r = r1
        c1 = combination(n, r1)
        c2 = combination(n, r2)
        answer = c1 + c2
        question_text = (
            f"求 $C^{{{n}}}_{{{r1}}}+C^{{{n}}}_{{{r2}}}$ 的值（僅需算出數值）。"
        )
        explanation = (
            f"$C^{{{n}}}_{{{r1}}}={c1}$，$C^{{{n}}}_{{{r2}}}={c2}$，"
            f"故 $C^{{{n}}}_{{{r1}}}+C^{{{n}}}_{{{r2}}}={c1}+{c2}={answer}$。"
        )
    else:
        r = r1
        answer = combination(n, r)
        if variant == "symmetry":
            question_text = (
                f"利用組合性質 $C^{{n}}_{{r}}=C^{{n}}_{{n-r}}$，求 $C^{{{n}}}_{{{r}}}$ 的值。"
            )
            explanation = (
                f"使用 $C^{{n}}_{{r}}=C^{{n}}_{{n-r}}$，所以 "
                f"$C^{{{n}}}_{{{r}}}=C^{{{n}}}_{{{n-r}}}={answer}$。"
            )
        elif variant == "symmetry_word":
            question_text = (
                f"從 ${n}$ 位候選人中選出 ${r}$ 人與選出 ${n-r}$ 人（不計順序）的方法數相同，"
                f"求此相同的方法數。"
            )
            explanation = (
                f"由對稱性 $C^{{n}}_{{r}}=C^{{n}}_{{n-r}}$，所求即 $C^{{{n}}}_{{{r}}}$；"
                f"代入公式得 $C^{{{n}}}_{{{r}}}={answer}$。"
            )
        else:
            question_text = f"計算組合數 $C^{{{n}}}_{{{r}}}$ 的值。"
            explanation = (
                f"使用 $C^{{n}}_{{r}}=\\frac{{n!}}{{r!(n-r)!}}$ 計算，"
                f"可得 $C^{{{n}}}_{{{r}}}={answer}$。"
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
            "r2": r2 if variant == "two_term_sum" else None,
            "variant": variant,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def _sample_restricted_selection_params(
    rng: random.Random, difficulty: int
) -> tuple[int, int, int, int, str]:
    if difficulty <= 1:
        a = rng.randint(3, 6)
        b = rng.randint(4, 8)
        r = rng.randint(2, 4)
        k = rng.randint(1, min(2, r))
    elif difficulty == 2:
        a = rng.randint(4, 8)
        b = rng.randint(5, 10)
        r = rng.randint(3, 5)
        k = rng.randint(1, min(3, r))
    else:
        a = rng.randint(5, 10)
        b = rng.randint(6, 12)
        r = rng.randint(4, 6)
        k = rng.randint(1, min(4, r))
    if r > a + b:
        r = a + b
    variant = rng.choice(["at_least_one_from_group", "exactly_k_from_group"])
    if variant == "exactly_k_from_group":
        if k > a:
            k = a
        if r - k > b:
            r = min(a + b, b + k)
    return a, b, r, k, variant


def combination_restricted_selection(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    a = b = r = k = 0
    variant = ""

    if seed is not None and 1 <= seed <= 5 and difficulty == 1:
        preset = [
            (3, 4, 2, 1, "at_least_one_from_group"),
            (4, 5, 3, 1, "exactly_k_from_group"),
            (5, 6, 3, 2, "at_least_one_from_group"),
            (6, 4, 4, 2, "exactly_k_from_group"),
            (3, 8, 4, 1, "at_least_one_from_group"),
        ][seed - 1]
        a, b, r, k, variant = preset
        candidate = (RESTRICTED_SELECTION_PROBLEM_TYPE_ID, a, b, r, k, variant)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        a, b, r, k, variant = _sample_restricted_selection_params(rng, difficulty)
        candidate = (RESTRICTED_SELECTION_PROBLEM_TYPE_ID, a, b, r, k, variant)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    if variant == "at_least_one_from_group":
        total = combination(a + b, r)
        invalid = combination(b, r) if r <= b else 0
        answer = total - invalid
        question_text = (
            f"甲組有 {a} 人、乙組有 {b} 人，今共選 {r} 人，且至少選 1 位甲組成員，共有多少種選法？"
        )
        explanation = (
            f"先算全部選法 $C^{{{a+b}}}_{{{r}}}$，扣掉沒有甲組成員的情形 "
            f"$C^{{{b}}}_{{{r}}}$，所以 "
            f"$C^{{{a+b}}}_{{{r}}}-C^{{{b}}}_{{{r}}}={answer}$。"
        )
    else:
        answer = combination(a, k) * combination(b, r - k)
        question_text = (
            f"甲組有 {a} 人、乙組有 {b} 人，今共選 {r} 人，且恰選 {k} 位甲組成員，共有多少種選法？"
        )
        explanation = (
            f"甲組選 ${k}$ 人、乙組選 ${r-k}$ 人，方法數為 "
            f"$C^{{{a}}}_{{{k}}}\\times C^{{{b}}}_{{{r-k}}}={answer}$。"
        )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": RESTRICTED_SELECTION_PROBLEM_TYPE_ID,
        "generator_key": RESTRICTED_SELECTION_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "combination_restricted_selection",
            "combination",
            "restricted_selection",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_comb_restricted_selection_01",
            "combination_restricted_selection",
        ],
        "parameters": {
            "a": a,
            "b": b,
            "r": r,
            "k": k,
            "variant": variant,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def _sample_seat_assignment_params(rng: random.Random, difficulty: int) -> tuple[int, int, str]:
    if difficulty <= 1:
        n = rng.randint(5, 8)
        r = rng.randint(2, 3)
    elif difficulty == 2:
        n = rng.randint(7, 10)
        r = rng.randint(2, 4)
    else:
        n = rng.randint(9, 12)
        r = rng.randint(3, 5)
    if r > n:
        r = n
    context = rng.choice(["seats", "officers", "presentation_order"])
    return n, r, context


def combination_seat_assignment(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    n = r = 0
    context = ""

    if seed is not None and 1 <= seed <= 5 and difficulty == 1:
        preset = [
            (5, 2, "seats"),
            (6, 3, "officers"),
            (7, 2, "presentation_order"),
            (8, 3, "seats"),
            (6, 2, "officers"),
        ][seed - 1]
        n, r, context = preset
        candidate = (SEAT_ASSIGNMENT_PROBLEM_TYPE_ID, n, r, context)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        n, r, context = _sample_seat_assignment_params(rng, difficulty)
        candidate = (SEAT_ASSIGNMENT_PROBLEM_TYPE_ID, n, r, context)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = combination(n, r) * permutation(r, r)
    if context == "seats":
        question_text = f"從 {n} 位同學中選出 {r} 位，安排到 {r} 個不同座位，共有多少種安排方式？"
    elif context == "officers":
        question_text = f"從 {n} 人中選出 {r} 人擔任 {r} 個不同職務，共有多少種安排方式？"
    else:
        question_text = f"從 {n} 人中選出 {r} 人依序上台報告，共有多少種安排方式？"
    explanation = (
        f"先從 ${n}$ 人中選 ${r}$ 人，有 $C^{{{n}}}_{{{r}}}$ 種；再將 ${r}$ 人排列，"
        f"有 ${r}!$ 種，所以 $C^{{{n}}}_{{{r}}}\\times {r}!={answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": SEAT_ASSIGNMENT_PROBLEM_TYPE_ID,
        "generator_key": SEAT_ASSIGNMENT_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "combination_seat_assignment",
            "combination",
            "permutation",
            "mixed_counting",
        ],
        "remediation_candidates": [],
        "source_style_refs": ["tc_comb_seat_assignment_01", "combination_seat_assignment"],
        "parameters": {
            "n": n,
            "r": r,
            "context": context,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload


def _grid_right_up_path_count(dx: int, dy: int) -> int:
    if dx < 0 or dy < 0:
        raise ValueError("grid segments must be nonnegative.")
    return combination(dx + dy, dx)


def _sample_grid_shortest_path_core(
    rng: random.Random, difficulty: int
) -> tuple[int, int, int, int]:
    if difficulty <= 1:
        w = rng.randint(3, 5)
        h = rng.randint(3, 5)
    elif difficulty == 2:
        w = rng.randint(3, 7)
        h = rng.randint(3, 7)
    else:
        w = rng.randint(4, 8)
        h = rng.randint(4, 8)
    mid_x = rng.randint(1, w - 1)
    mid_y = rng.randint(1, h - 1)
    return w, h, mid_x, mid_y


def _grid_path_question_preamble(template_context: str, w: int, h: int) -> str:
    if template_context == "chessboard_roads":
        return (
            f"某棋盤狀方格道路中，從甲地到乙地須向右走 ${w}$ 段、向上走 ${h}$ 段；"
            f"每一步只能沿邊向右或向上前進一段（最短路徑）。"
        )
    if template_context == "campus_grid":
        return (
            f"某校園方格步道從甲地到乙地須向右走 ${w}$ 段、向上走 ${h}$ 段；"
            f"每一步只能沿步道向右或向上前進一段（最短路徑）。"
        )
    if template_context == "street_grid":
        return (
            f"某地街道路網呈方格狀，從甲地到乙地須向右走 ${w}$ 段、向上走 ${h}$ 段；"
            f"每一步只能沿道路向右或向上前進一段（最短路徑）。"
        )
    return (
        f"從甲地到乙地的方格路網中，須向右走 ${w}$ 段、向上走 ${h}$ 段；"
        f"每一步只能向右或向上前進一段（最短路徑）。"
    )


def _grid_path_explanation_basic(w: int, h: int, total: int) -> str:
    return (
        "只許向右或向上，最短路徑恰含所有右段與上段各走一次，"
        f"方法數為 $\\displaystyle C^{{{w}+{h}}}_{{{w}}}={total}$。"
    )


def _grid_path_explanation_via(
    w: int,
    h: int,
    mx: int,
    my: int,
    p_to_mid: int,
    mid_to_end: int,
    via: int,
) -> str:
    a2 = w - mx
    b2 = h - my
    return (
        "必經丙地時，先算甲→丙再算丙→乙，乘法原理："
        f"$\\displaystyle C^{{{mx}+{my}}}_{{{mx}}}\\times C^{{{a2}+{b2}}}_{{{a2}}}"
        f"={p_to_mid}\\times {mid_to_end}={via}$。"
    )


def _grid_path_explanation_avoid(
    w: int,
    h: int,
    mx: int,
    my: int,
    total: int,
    p_to_mid: int,
    mid_to_end: int,
    via: int,
    ans: int,
) -> str:
    a2 = w - mx
    b2 = h - my
    return (
        "不經過丙地：全部最短路徑扣除必經丙者："
        f"$\\displaystyle C^{{{w}+{h}}}_{{{w}}}-\\big(C^{{{mx}+{my}}}_{{{mx}}}\\cdot C^{{{a2}+{b2}}}_{{{a2}}}\\big)"
        f"={total}-{via}={ans}$。"
    )


def grid_shortest_path_count(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Grid shortest paths with only right/up moves; basic, via_point, or avoid_point."""
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    variants = ("basic", "via_point", "avoid_point")
    if seed is not None:
        variant = variants[seed % 3]
    else:
        variant = rng.choice(variants)

    parameter_tuple: tuple | None = None
    w = h = mx = my = 0
    template_context = "generic_ab"

    if seed is not None and 1 <= seed <= 6 and difficulty <= 1:
        presets = [
            ("basic", 4, 4, 2, 2, "street_grid"),
            ("via_point", 5, 4, 2, 2, "campus_grid"),
            ("avoid_point", 5, 5, 2, 3, "chessboard_roads"),
            ("basic", 3, 6, 1, 2, "generic_ab"),
            ("via_point", 6, 3, 3, 1, "street_grid"),
            ("avoid_point", 4, 4, 1, 2, "campus_grid"),
        ]
        variant, w, h, mx, my, template_context = presets[seed - 1]
        candidate = (
            GRID_SHORTEST_PATH_PROBLEM_TYPE_ID,
            variant,
            w,
            h,
            mx,
            my,
            template_context,
        )
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(80):
        if parameter_tuple is not None:
            break
        if seed is None:
            variant = rng.choice(variants)
        template_context = rng.choice(_GRID_PATH_TEMPLATE_CONTEXTS)
        w, h, mx, my = _sample_grid_shortest_path_core(rng, difficulty)
        candidate = (
            GRID_SHORTEST_PATH_PROBLEM_TYPE_ID,
            variant,
            w,
            h,
            mx,
            my,
            template_context,
        )
        if candidate in seen:
            continue
        total = _grid_right_up_path_count(w, h)
        p_to_mid = _grid_right_up_path_count(mx, my)
        mid_to_end = _grid_right_up_path_count(w - mx, h - my)
        via = p_to_mid * mid_to_end
        if variant == "basic":
            answer = total
        elif variant == "via_point":
            answer = via
        else:
            answer = total - via
        if answer <= 0 or answer > _MAX_GRID_PATH_ANSWER:
            continue
        parameter_tuple = candidate
        break

    if parameter_tuple is None:
        raise ValueError("Failed to find a new grid path parameter tuple after 80 retries.")

    variant = parameter_tuple[1]
    w, h, mx, my, template_context = (
        parameter_tuple[2],
        parameter_tuple[3],
        parameter_tuple[4],
        parameter_tuple[5],
        parameter_tuple[6],
    )

    total_paths = _grid_right_up_path_count(w, h)
    p_to_mid = _grid_right_up_path_count(mx, my)
    mid_to_end = _grid_right_up_path_count(w - mx, h - my)
    via_paths = p_to_mid * mid_to_end

    if variant == "basic":
        answer = total_paths
        via_paths_stored = 0
        mid_x = mid_y = None
        preamble = _grid_path_question_preamble(template_context, w, h)
        question_text = (
            preamble
            + "若不考慮繪製路線圖，僅以計數回答，則最短路徑共有幾種？"
        )
        explanation = _grid_path_explanation_basic(w, h, total_paths)
    else:
        mid_x, mid_y = mx, my
        a1, b1, a2, b2 = mx, my, w - mx, h - my
        preamble = _grid_path_question_preamble(template_context, w, h)
        via_clause = (
            f"途中有一路口丙；從甲到丙須向右走 ${a1}$ 段、向上走 ${b1}$ 段，"
            f"從丙到乙須向右走 ${a2}$ 段、向上走 ${b2}$ 段（仍只許每次向右或向上一段）。"
        )
        if variant == "via_point":
            answer = via_paths
            via_paths_stored = via_paths
            question_text = preamble + via_clause + "若最短路徑必須經過丙，則共有幾種？"
            explanation = _grid_path_explanation_via(w, h, mx, my, p_to_mid, mid_to_end, via_paths)
        else:
            answer = total_paths - via_paths
            via_paths_stored = via_paths
            if answer <= 0:
                raise ValueError("avoid_point grid path answer must be positive.")
            question_text = preamble + via_clause + "若最短路徑不得經過丙，則共有幾種？"
            explanation = _grid_path_explanation_avoid(
                w, h, mx, my, total_paths, p_to_mid, mid_to_end, via_paths, answer
            )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": GRID_SHORTEST_PATH_PROBLEM_TYPE_ID,
        "generator_key": GRID_SHORTEST_PATH_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "grid_shortest_path_count",
            "combination",
            "multiplication_principle",
            variant,
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_grid_shortest_path_count_01",
            "grid_shortest_path_count",
        ],
        "parameters": {
            "variant": variant,
            "width": w,
            "height": h,
            "a": w,
            "b": h,
            "mid_x": mid_x,
            "mid_y": mid_y,
            "total_paths": total_paths,
            "via_paths": via_paths_stored,
            "answer": answer,
            "template_context": template_context,
            "parameter_tuple": parameter_tuple,
        },
    }

    _validate_and_finalize(payload, multiple_choice)
    seen.add(parameter_tuple)
    return payload
