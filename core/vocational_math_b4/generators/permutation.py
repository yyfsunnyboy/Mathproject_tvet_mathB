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
    combination,
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
NON_DISTINCT_OBJECTS_PROBLEM_TYPE_ID = "non_distinct_objects_arrangement"
NON_DISTINCT_OBJECTS_GENERATOR_KEY = "b4.permutation.non_distinct_objects_arrangement"
NON_ADJACENT_ARRANGEMENT_PROBLEM_TYPE_ID = "permutation_non_adjacent_arrangement"
NON_ADJACENT_ARRANGEMENT_GENERATOR_KEY = "b4.permutation.permutation_non_adjacent_arrangement"
_MAX_NON_ADJACENT_ANSWER = 5_000_000

_NON_ADJACENT_TEMPLATE_CONTEXTS = (
    "boys_girls_lineup",
    "team_a_b_lineup",
    "color_balls_arrangement",
    "VIP_general_seating",
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


def _sample_non_distinct_objects_params(rng: random.Random, difficulty: int) -> tuple[int, list[int], int, str]:
    if difficulty <= 1:
        duplicate_pool = [[2], [3], [2, 2]]
        singleton_min, singleton_max = 1, 3
        answer_limit = 360
    elif difficulty == 2:
        duplicate_pool = [[2], [3], [4], [2, 2], [2, 3], [3, 3], [2, 2, 2]]
        singleton_min, singleton_max = 0, 3
        answer_limit = 5040
    else:
        duplicate_pool = [
            [2, 2],
            [2, 3],
            [2, 4],
            [3, 3],
            [2, 2, 2],
            [2, 2, 3],
            [2, 3, 3],
            [2, 2, 2, 2],
        ]
        singleton_min, singleton_max = 0, 3
        answer_limit = 100000

    contexts = ["letters", "colored_balls", "objects", "word_tiles", "badge_strip"]
    for _ in range(50):
        duplicate_counts = list(rng.choice(duplicate_pool))
        singleton_count = rng.randint(singleton_min, singleton_max)
        total_count = sum(duplicate_counts) + singleton_count
        if difficulty <= 1 and not 4 <= total_count <= 6:
            continue
        if difficulty == 2 and not 5 <= total_count <= 8:
            continue
        if difficulty >= 3 and not 7 <= total_count <= 10:
            continue
        denominator = 1
        for count in duplicate_counts:
            denominator *= factorial(count)
        answer = factorial(total_count) // denominator
        if answer <= answer_limit:
            return total_count, duplicate_counts, singleton_count, rng.choice(contexts)

    fallback = (4, [2], 2, rng.choice(contexts)) if difficulty <= 1 else (7, [2, 2], 3, rng.choice(contexts))
    return fallback


def _non_distinct_answer(total_count: int, duplicate_counts: list[int]) -> int:
    denominator = 1
    for count in duplicate_counts:
        denominator *= factorial(count)
    return factorial(total_count) // denominator


def _format_factorial_denominator(counts: list[int]) -> str:
    return "".join(f"{count}!" for count in counts)


def _build_letter_like_labels(duplicate_counts: list[int], singleton_count: int) -> str:
    labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    parts: list[str] = []
    index = 0
    for count in duplicate_counts:
        parts.extend([labels[index]] * count)
        index += 1
    for _ in range(singleton_count):
        parts.append(labels[index])
        index += 1
    return "、".join(parts)


def _format_letters_question(duplicate_counts: list[int], singleton_count: int, total_count: int) -> str:
    letters_text = _build_letter_like_labels(duplicate_counts, singleton_count)
    return f"用 {letters_text} 共 {total_count} 個字母排成一列，共有多少種不同排列？"


def _format_word_tiles_question(duplicate_counts: list[int], singleton_count: int, total_count: int) -> str:
    letters_text = _build_letter_like_labels(duplicate_counts, singleton_count)
    return (
        f"拼字遊戲桌上有字卡 {letters_text} 共 {total_count} 張（相同字卡不可辨），"
        f"全數排成一列，共有多少種不同排法？"
    )


def _format_badge_strip_question(duplicate_counts: list[int], singleton_count: int, total_count: int) -> str:
    letters_text = _build_letter_like_labels(duplicate_counts, singleton_count)
    return (
        f"活動識別帶上需依序排列 {letters_text} 共 {total_count} 個圖樣標誌（相同標誌不可辨），"
        f"共有多少種不同排法？"
    )


def _format_colored_balls_question(duplicate_counts: list[int], singleton_count: int, total_count: int) -> str:
    duplicate_colors = ["紅球", "白球", "藍球", "黃球"]
    singleton_colors = ["黑球", "綠球", "紫球"]
    descriptions = [f"{count} 個{duplicate_colors[idx]}相同" for idx, count in enumerate(duplicate_counts)]
    descriptions.extend(f"1 個{singleton_colors[idx]}" for idx in range(singleton_count))
    return f"有 {total_count} 個球，其中 {'、'.join(descriptions)}，排成一列共有多少種不同排列？"


def _format_objects_question(duplicate_counts: list[int], singleton_count: int, total_count: int) -> str:
    if len(duplicate_counts) == 1:
        duplicate_text = f"{duplicate_counts[0]} 個相同"
    else:
        duplicate_text = "、".join(f"一組 {count} 個相同" for count in duplicate_counts)
    if singleton_count == 0:
        singleton_text = "沒有其他不同物件"
    else:
        singleton_text = f"其餘 {singleton_count} 個都不同"
    return f"有 {total_count} 個物件，其中 {duplicate_text}，{singleton_text}，排成一列共有多少種不同排列？"


def non_distinct_objects_arrangement(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate deterministic multiset permutation problems."""
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    total_count = singleton_count = 0
    duplicate_counts: list[int] = []
    context = ""

    if seed is not None and 1 <= seed <= 5 and difficulty <= 1:
        total_count, duplicate_counts, singleton_count, context = [
            (4, [2], 2, "letters"),
            (5, [2], 3, "objects"),
            (6, [2, 2], 2, "colored_balls"),
            (6, [3], 3, "letters"),
            (5, [3], 2, "colored_balls"),
        ][seed - 1]
        candidate = (
            NON_DISTINCT_OBJECTS_PROBLEM_TYPE_ID,
            total_count,
            tuple(sorted(duplicate_counts)),
            singleton_count,
            context,
        )
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(50):
        if parameter_tuple is not None:
            break
        total_count, duplicate_counts, singleton_count, context = _sample_non_distinct_objects_params(rng, difficulty)
        candidate = (
            NON_DISTINCT_OBJECTS_PROBLEM_TYPE_ID,
            total_count,
            tuple(sorted(duplicate_counts)),
            singleton_count,
            context,
        )
        if candidate not in seen:
            parameter_tuple = candidate
            break
    if parameter_tuple is None:
        raise ValueError("Failed to find a new parameter tuple after 50 retries.")

    duplicate_counts = list(sorted(duplicate_counts))
    answer = _non_distinct_answer(total_count, duplicate_counts)
    if context == "letters":
        question_text = _format_letters_question(duplicate_counts, singleton_count, total_count)
    elif context == "word_tiles":
        question_text = _format_word_tiles_question(duplicate_counts, singleton_count, total_count)
    elif context == "badge_strip":
        question_text = _format_badge_strip_question(duplicate_counts, singleton_count, total_count)
    elif context == "colored_balls":
        question_text = _format_colored_balls_question(duplicate_counts, singleton_count, total_count)
    else:
        question_text = _format_objects_question(duplicate_counts, singleton_count, total_count)

    denominator_counts = duplicate_counts + [1] * singleton_count
    denominator_text = _format_factorial_denominator(denominator_counts)
    explanation = (
        f"若先把所有物件都當作相異，共有 ${total_count}!$ 種排列。"
        "但相同物互換不產生新排列，所以要除以相同物內部交換數。"
        f"本題共有 ${total_count}$ 個物件，故不同排列數為 "
        f"$\\frac{{{total_count}!}}{{{denominator_text}}}={answer}$。"
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": NON_DISTINCT_OBJECTS_PROBLEM_TYPE_ID,
        "generator_key": NON_DISTINCT_OBJECTS_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "non_distinct_objects_arrangement",
            "permutation",
            "multiset_permutation",
        ],
        "remediation_candidates": [
            "factorial_evaluation",
            "permutation_full_arrangement",
            "division_by_duplicate_factorials",
        ],
        "source_style_refs": [
            "tc_perm_non_distinct_objects_01",
            "non_distinct_objects_arrangement",
        ],
        "parameters": {
            "total_count": total_count,
            "duplicate_counts": duplicate_counts,
            "singleton_count": singleton_count,
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


def _non_adjacent_arrangement_count(m: int, k: int) -> int:
    return factorial(m) * combination(m + 1, k) * factorial(k)


def _pick_non_adjacent_template_context(rng: random.Random, seed: int | None) -> str:
    if seed is not None:
        return _NON_ADJACENT_TEMPLATE_CONTEXTS[seed % len(_NON_ADJACENT_TEMPLATE_CONTEXTS)]
    return rng.choice(_NON_ADJACENT_TEMPLATE_CONTEXTS)


def _non_adjacent_labels(template_context: str) -> tuple[str, str, str]:
    """Returns (majority_group_label, minority_group_label, minority_phrase_for_pair_restriction)."""
    if template_context == "boys_girls_lineup":
        return ("男生", "女生", "位女生")
    if template_context == "team_a_b_lineup":
        return ("甲組學生", "乙組學生", "位乙組學生")
    if template_context == "color_balls_arrangement":
        return ("藍球", "紅球", "顆紅球")
    return ("一般成員", "貴賓", "位貴賓")


def _build_non_adjacent_question_text(
    template_context: str,
    m: int,
    k: int,
    min_pair_phrase: str,
) -> str:
    distinct_note = (
        "（每位／每個皆視為不同，彼此可區分、互不相同）"
        if template_context != "color_balls_arrangement"
        else "（各球彼此可辨識、互不相同）"
    )
    if template_context == "boys_girls_lineup":
        opener = f"有 ${m}$ 位男生與 ${k}$ 位女生{distinct_note}，要排成一列。"
    elif template_context == "team_a_b_lineup":
        opener = f"有 ${m}$ 位甲組學生與 ${k}$ 位乙組學生{distinct_note}，要排成一列。"
    elif template_context == "color_balls_arrangement":
        opener = f"有 ${m}$ 個相異藍球與 ${k}$ 個相異紅球{distinct_note}，要排成一列。"
    else:
        opener = f"有 ${m}$ 位一般成員與 ${k}$ 位貴賓{distinct_note}，要排成一列。"
    restriction = f"若規定任兩{min_pair_phrase}不得相鄰"
    return (
        opener
        + restriction
        + "，則共有多少種排法？（只需回答方法數，不必列出所有排列。）"
    )


def _build_non_adjacent_explanation(
    m: int,
    k: int,
    maj_label: str,
    min_label: str,
    gap_choose: int,
    maj_fact: int,
    min_fact: int,
    answer: int,
) -> str:
    return (
        "插空法：先將 "
        f"${m}$ 位（個）{maj_label}排成一列，有 $\\displaystyle {m}!={maj_fact}$ 種；"
        f"形成 ${m}+1={m + 1}$ 個空位。自這 ${m + 1}$ 個空位中選 ${k}$ 個放入 {min_label}，"
        f"有 $\\displaystyle C^{{{m + 1}}}_{{{k}}}={gap_choose}$ 種；"
        f"再將 ${k}$ 位（個）{min_label}排列，有 $\\displaystyle {k}!={min_fact}$ 種。"
        f"故總數為 $\\displaystyle {m}!\\times C^{{{m + 1}}}_{{{k}}}\\times {k}!={answer}$，"
        f"亦等於 $\\displaystyle {m}!\\times P^{{{m + 1}}}_{{{k}}}$。"
    )


def _sample_non_adjacent_mk(rng: random.Random, difficulty: int) -> tuple[int, int]:
    if difficulty <= 1:
        k = 2
        m = rng.randint(3, 6)
    elif difficulty == 2:
        k = rng.choice([2, 3])
        m = rng.randint(max(3, k), 7)
    else:
        k = rng.choice([2, 3])
        m = rng.randint(max(3, k), 8)
    if m < k:
        m = k
    return m, k


def permutation_non_adjacent_arrangement(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Gap method: arrange majority m first, place k minority in m+1 gaps so none adjacent."""
    rng = random.Random(seed)
    seen = _ensure_seen_set(seen_parameter_tuples)

    parameter_tuple: tuple | None = None
    m = k = 0
    template_context = "boys_girls_lineup"

    if seed is not None and 1 <= seed <= 8 and difficulty <= 1:
        presets = [
            (3, 2, "boys_girls_lineup"),
            (4, 2, "team_a_b_lineup"),
            (5, 2, "color_balls_arrangement"),
            (4, 2, "VIP_general_seating"),
            (5, 2, "boys_girls_lineup"),
            (6, 2, "team_a_b_lineup"),
            (4, 3, "color_balls_arrangement"),
            (6, 3, "VIP_general_seating"),
        ]
        m, k, template_context = presets[seed - 1]
        candidate = (NON_ADJACENT_ARRANGEMENT_PROBLEM_TYPE_ID, m, k, template_context)
        if candidate not in seen:
            parameter_tuple = candidate

    for _ in range(80):
        if parameter_tuple is not None:
            break
        template_context = _pick_non_adjacent_template_context(rng, seed)
        m, k = _sample_non_adjacent_mk(rng, difficulty)
        candidate = (NON_ADJACENT_ARRANGEMENT_PROBLEM_TYPE_ID, m, k, template_context)
        if candidate in seen:
            continue
        ans_try = _non_adjacent_arrangement_count(m, k)
        if ans_try <= 0 or ans_try > _MAX_NON_ADJACENT_ANSWER:
            continue
        parameter_tuple = candidate
        break

    if parameter_tuple is None:
        raise ValueError("Failed to find a new non-adjacent arrangement parameter tuple after 80 retries.")

    m, k, template_context = parameter_tuple[1], parameter_tuple[2], parameter_tuple[3]
    maj_label, min_label, min_pair_phrase = _non_adjacent_labels(template_context)
    gap_count = m + 1
    gap_choose_val = combination(gap_count, k)
    maj_fact = factorial(m)
    min_fact = factorial(k)
    answer = maj_fact * gap_choose_val * min_fact

    question_text = _build_non_adjacent_question_text(template_context, m, k, min_pair_phrase)
    explanation = _build_non_adjacent_explanation(
        m, k, maj_label, min_label, gap_choose_val, maj_fact, min_fact, answer
    )

    payload = {
        "question_text": question_text,
        "choices": _make_numeric_choices(answer, rng) if multiple_choice else [],
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": NON_ADJACENT_ARRANGEMENT_PROBLEM_TYPE_ID,
        "generator_key": NON_ADJACENT_ARRANGEMENT_GENERATOR_KEY,
        "difficulty": difficulty,
        "diagnosis_tags": [
            "permutation_non_adjacent_arrangement",
            "permutation",
            "gap_method",
            "non_adjacent",
        ],
        "remediation_candidates": [],
        "source_style_refs": [
            "tc_perm_non_adjacent_arrangement_01",
            "permutation_non_adjacent_arrangement",
        ],
        "parameters": {
            "majority_group_label": maj_label,
            "minority_group_label": min_label,
            "majority_count": m,
            "minority_count": k,
            "gap_count": gap_count,
            "chosen_gap_count": k,
            "template_context": template_context,
            "formula_components": {
                "majority_factorial": maj_fact,
                "gap_choose": gap_choose_val,
                "minority_factorial": min_fact,
            },
            "answer": answer,
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
