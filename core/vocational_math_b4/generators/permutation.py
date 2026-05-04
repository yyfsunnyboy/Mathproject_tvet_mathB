"""Deterministic B4 permutation generators (Phase 4B-2)."""

from __future__ import annotations

import random

from core.vocational_math_b4.domain.b4_validators import (
    validate_answer_in_choices,
    validate_choices_unique,
    validate_no_unfilled_placeholder,
    validate_problem_payload_contract,
)
from core.vocational_math_b4.domain.counting_domain_functions import (
    factorial,
    multiplication_principle_count,
    permutation,
)

PROBLEM_TYPE_ID = "permutation_role_assignment"
GENERATOR_KEY = "b4.permutation.permutation_role_assignment"
FORMULA_EVAL_PROBLEM_TYPE_ID = "permutation_formula_evaluation"
FORMULA_EVAL_GENERATOR_KEY = "b4.permutation.permutation_formula_evaluation"
FULL_ARRANGEMENT_PROBLEM_TYPE_ID = "permutation_full_arrangement"
FULL_ARRANGEMENT_GENERATOR_KEY = "b4.permutation.permutation_full_arrangement"
ADJACENT_BLOCK_PROBLEM_TYPE_ID = "permutation_adjacent_block"
ADJACENT_BLOCK_GENERATOR_KEY = "b4.permutation.permutation_adjacent_block"
DIGIT_PARITY_PROBLEM_TYPE_ID = "permutation_digit_parity"
DIGIT_PARITY_GENERATOR_KEY = "b4.permutation.permutation_digit_parity"


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


def _ensure_seen_set(seen_parameter_tuples: set[tuple] | None) -> set[tuple]:
    if seen_parameter_tuples is None:
        return set()
    if not isinstance(seen_parameter_tuples, set):
        raise ValueError("seen_parameter_tuples must be a set or None.")
    return seen_parameter_tuples


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


def _sample_permutation_formula_params(rng: random.Random, difficulty: int) -> tuple[int, int, str]:
    if difficulty <= 1:
        n = rng.randint(5, 9)
        r = rng.randint(2, 4)
    elif difficulty == 2:
        n = rng.randint(8, 12)
        r = rng.randint(2, 5)
    else:
        n = rng.randint(10, 16)
        r = rng.randint(3, 6)
    if r > n:
        r = n
    variant = rng.choice(["symbolic", "arrange"])
    return n, r, variant


def generate(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a deterministic permutation-role-assignment problem payload."""
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

    answer = permutation(n, r)
    question_text = f"從 {n} 位同學中選出 {r} 位分別擔任不同職務，共有多少種安排方式？"
    explanation = (
        "職務不同且順序重要，使用 $P^{n}_{r}=\\frac{n!}{(n-r)!}$，"
        f"所以 $P^{{{n}}}_{{{r}}}={answer}$。"
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
        "diagnosis_tags": ["permutation_role_assignment", "permutation", "order_matters"],
        "remediation_candidates": [],
        "source_style_refs": ["tc_perm_role_assignment_03", "permutation_role_assignment"],
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


def permutation_formula_evaluation(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic P(n,r) formula evaluation problems."""
    rng = random.Random(seed)
    if seed is not None:
        for _ in range(seed * 13):
            rng.random()
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    n = r = 0
    variant = ""
    for _ in range(50):
        n, r, variant = _sample_permutation_formula_params(rng, difficulty)
        candidate = (FORMULA_EVAL_PROBLEM_TYPE_ID, n, r, variant)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = permutation(n, r)
    if variant == "symbolic":
        question_text = f"計算排列數 $P^{{{n}}}_{{{r}}}$ 的值。"
    else:
        question_text = (
            f"從 {n} 個不同物件中取出 {r} 個排成一列，共有多少種排法？"
        )
    explanation = (
        "使用 $P^{n}_{r}=\\frac{n!}{(n-r)!}$，"
        f"所以 $P^{{{n}}}_{{{r}}}={answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": FORMULA_EVAL_PROBLEM_TYPE_ID,
        "generator_key": FORMULA_EVAL_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["permutation_formula_evaluation", "permutation", "order_matters"],
        "remediation_candidates": [],
        "source_style_refs": ["tc_perm_formula_evaluation_01", "permutation_formula_evaluation"],
        "parameters": {
            "n": n,
            "r": r,
            "variant": variant,
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


def _sample_full_arrangement_params(rng: random.Random, difficulty: int) -> tuple[int, str]:
    if difficulty <= 1:
        n = rng.randint(3, 6)
    elif difficulty == 2:
        n = rng.randint(5, 8)
    else:
        n = rng.randint(7, 10)
    context = rng.choice(["students_line", "books_shelf", "photos_row", "tasks_order"])
    return n, context


def permutation_full_arrangement(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    from core.vocational_math_b4.domain.counting_domain_functions import factorial

    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    n = 0
    context = ""

    if seed is not None and 1 <= seed <= 5 and difficulty == 1:
        preset = [
            (3, "students_line"),
            (4, "books_shelf"),
            (5, "photos_row"),
            (6, "tasks_order"),
            (4, "students_line"),
        ][seed - 1]
        n, context = preset
        candidate = (FULL_ARRANGEMENT_PROBLEM_TYPE_ID, n, context)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        n, context = _sample_full_arrangement_params(rng, difficulty)
        candidate = (FULL_ARRANGEMENT_PROBLEM_TYPE_ID, n, context)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = factorial(n)
    if context == "students_line":
        question_text = f"{n} 位同學排成一列，共有多少種排法？"
    elif context == "books_shelf":
        question_text = f"{n} 本不同書排在書架上，共有多少種排法？"
    elif context == "photos_row":
        question_text = f"{n} 張不同照片排成一排，共有多少種排法？"
    else:
        question_text = f"{n} 件不同任務安排順序，共有多少種排法？"
    explanation = f"${n}$ 位相異對象全取排列，方法數為 ${n}!={answer}$。"

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": FULL_ARRANGEMENT_PROBLEM_TYPE_ID,
        "generator_key": FULL_ARRANGEMENT_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["permutation_full_arrangement", "permutation", "factorial"],
        "remediation_candidates": [],
        "source_style_refs": ["tc_perm_full_arrangement_01", "permutation_full_arrangement"],
        "parameters": {
            "n": n,
            "context": context,
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


def _sample_adjacent_block_params(rng: random.Random, difficulty: int) -> tuple[int, int, str]:
    if difficulty <= 1:
        n = rng.randint(5, 7)
        block_size = 2
    elif difficulty == 2:
        n = rng.randint(6, 9)
        block_size = rng.choice([2, 3])
    else:
        n = rng.randint(8, 10)
        block_size = rng.choice([2, 3])
    context = rng.choice(["students_line", "books_shelf", "photos_row"])
    return n, block_size, context


def _build_digit_pool(digit_pool_size: int, allow_zero: bool) -> list[int]:
    if allow_zero:
        return list(range(0, digit_pool_size))
    return list(range(1, digit_pool_size + 1))


def _count_digit_parity_arrangements(digits: list[int], positions: int, variant: str) -> int:
    if variant not in {"odd_number", "even_number"}:
        raise ValueError("variant must be odd_number or even_number.")
    if positions < 2 or positions > len(digits):
        raise ValueError("positions must satisfy 2 <= positions <= len(digits).")

    total = 0
    for last in digits:
        if variant == "odd_number" and last % 2 == 0:
            continue
        if variant == "even_number" and last % 2 != 0:
            continue

        remaining_digits = [d for d in digits if d != last]
        first_choices_count = sum(1 for d in remaining_digits if d != 0)
        if first_choices_count == 0:
            continue

        if positions - 2 == 0:
            tail_count = 1
        else:
            tail_count = permutation(len(remaining_digits) - 1, positions - 2)
        total += multiplication_principle_count([first_choices_count, tail_count])
    return total


def _sample_digit_parity_params(rng: random.Random, difficulty: int) -> tuple[int, int, bool, str]:
    if difficulty <= 1:
        digit_pool_size = rng.randint(5, 7)
        positions = rng.randint(2, 3)
    elif difficulty == 2:
        digit_pool_size = rng.randint(6, 9)
        positions = rng.randint(3, 4)
    else:
        digit_pool_size = rng.randint(7, 10)
        positions = rng.randint(3, 5)
    if positions > digit_pool_size:
        positions = digit_pool_size
    allow_zero = rng.choice([True, False])
    variant = rng.choice(["odd_number", "even_number"])
    return digit_pool_size, positions, allow_zero, variant


def permutation_adjacent_block(
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
    n = block_size = 0
    context = ""

    if seed is not None and 1 <= seed <= 5 and difficulty <= 1:
        n, block_size, context = [
            (5, 2, "students_line"),
            (6, 2, "books_shelf"),
            (7, 2, "photos_row"),
            (6, 2, "students_line"),
            (7, 2, "books_shelf"),
        ][seed - 1]
        candidate = (ADJACENT_BLOCK_PROBLEM_TYPE_ID, n, block_size, context)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        n, block_size, context = _sample_adjacent_block_params(rng, difficulty)
        if not (2 <= block_size < n):
            continue
        candidate = (ADJACENT_BLOCK_PROBLEM_TYPE_ID, n, block_size, context)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    answer = factorial(n - block_size + 1) * factorial(block_size)
    if context == "students_line":
        if block_size == 2:
            question_text = f"{n} 位同學排成一列，若甲、乙必須相鄰，共有多少種排法？"
        else:
            question_text = f"{n} 位同學排成一列，若指定 {block_size} 位同學必須相鄰，共有多少種排法？"
    elif context == "books_shelf":
        question_text = f"{n} 本不同書排在書架上，若指定 {block_size} 本必須相鄰，共有多少種排法？"
    else:
        question_text = f"{n} 張不同照片排成一排，若指定 {block_size} 張必須相鄰，共有多少種排法？"
    external_units = n - block_size + 1
    explanation = (
        f"將指定的 {block_size} 個對象視為一塊，外部共有 ${external_units}!$ 種排法，"
        f"塊內有 ${block_size}!$ 種排法，所以 "
        f"$({external_units})!\\times({block_size})!={answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": ADJACENT_BLOCK_PROBLEM_TYPE_ID,
        "generator_key": ADJACENT_BLOCK_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": ["permutation_adjacent_block", "permutation", "block_method"],
        "remediation_candidates": [],
        "source_style_refs": ["tc_perm_adjacent_block_01", "permutation_adjacent_block"],
        "parameters": {
            "n": n,
            "block_size": block_size,
            "context": context,
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


def permutation_digit_parity(
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
    digit_pool_size = positions = 0
    allow_zero = False
    variant = "odd_number"

    if seed is not None and 1 <= seed <= 5 and difficulty <= 1:
        digit_pool_size, positions, allow_zero, variant = [
            (5, 2, True, "odd_number"),
            (6, 3, True, "even_number"),
            (7, 3, False, "odd_number"),
            (6, 2, False, "even_number"),
            (7, 3, True, "odd_number"),
        ][seed - 1]
        candidate = (DIGIT_PARITY_PROBLEM_TYPE_ID, digit_pool_size, positions, allow_zero, variant)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        digit_pool_size, positions, allow_zero, variant = _sample_digit_parity_params(rng, difficulty)
        if positions > digit_pool_size:
            continue
        candidate = (DIGIT_PARITY_PROBLEM_TYPE_ID, digit_pool_size, positions, allow_zero, variant)
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    digits = _build_digit_pool(digit_pool_size, allow_zero)
    answer = _count_digit_parity_arrangements(digits, positions, variant)
    digits_text = "、".join(str(d) for d in digits)
    parity_text = "奇數" if variant == "odd_number" else "偶數"
    question_text = (
        f"使用 {digits_text} 共 {digit_pool_size} 個數字，組成不重複的 {positions} 位{parity_text}，"
        "共有多少個？"
    )
    explanation = (
        f"{parity_text}需由末位決定；先分類末位，再選首位與其餘位排列，"
        "且首位不可為 $0$，全程數字不重複。"
        "其餘位可用 $P^{n}_{r}=\\frac{n!}{(n-r)!}$ 計算，分類後以 $\\times$ 相乘再加總，"
        f"可得答案為 ${answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": DIGIT_PARITY_PROBLEM_TYPE_ID,
        "generator_key": DIGIT_PARITY_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "permutation_digit_parity",
            "permutation",
            "digits_no_repeat",
            "parity",
        ],
        "remediation_candidates": [],
        "source_style_refs": ["tc_perm_digit_parity_01", "permutation_digit_parity"],
        "parameters": {
            "digit_pool_size": digit_pool_size,
            "positions": positions,
            "allow_zero": allow_zero,
            "variant": variant,
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
