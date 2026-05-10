"""Deterministic B4 Chapter 2 basic-sets counting generators – Phase 6K.

Skill:
  vh_數學B4_BasicConceptsOfSets  (2-1 樣本空間與事件 — 集合的基本概念)

Problem types implemented:
  1. set_operation_count           (集合元素 / 子集 / 補集 個數)
  2. inclusion_exclusion_count     (兩集合容斥計數 n(A∪B), n(U)-n(A∪B), …)

Strictly excluded:
  - subset_listing             (handwriting / listing — never enters allowlist)
  - listing all elements       (handwriting)
  - Venn diagram image
  - handwriting / free-response

Answer format:
  - integer
"""

from __future__ import annotations

import math
import random

from core.vocational_math_b4.domain.b4_validators import (
    validate_no_unfilled_placeholder,
    validate_problem_payload_contract,
)

SET_OPERATION_COUNT_PROBLEM_TYPE_ID = "set_operation_count"
SET_OPERATION_COUNT_GENERATOR_KEY = "b4.chap2.set_operation_count"

INCLUSION_EXCLUSION_COUNT_PROBLEM_TYPE_ID = "inclusion_exclusion_count"
INCLUSION_EXCLUSION_COUNT_GENERATOR_KEY = "b4.chap2.inclusion_exclusion_count"


def _make_integer_choices(answer: int, rng: random.Random) -> list[int]:
    """Generate 4 unique non-negative integer choices including the correct answer."""
    pool: set[int] = {answer}
    spans = [
        answer - 1,
        answer + 1,
        answer - 2,
        answer + 2,
        max(0, answer - 3),
        answer + 3,
        max(0, answer * 2 - 1),
        max(0, answer // 2),
    ]
    for v in spans:
        if v >= 0 and v != answer:
            pool.add(v)
        if len(pool) >= 6:
            break
    pool.discard(answer)
    distractors = list(pool)
    rng.shuffle(distractors)
    out = [answer] + distractors[:3]
    while len(out) < 4:
        extra = answer + rng.randint(2, max(3, answer + 4))
        if extra not in out:
            out.append(extra)
    rng.shuffle(out)
    return out


def set_operation_count(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a basic set element / subset / complement counting problem.

    Variants (Phase 6K):
      - subset_total_count:  given finite set A with n elements, find |2^A|
      - complement_count:    given n(U), n(A), find n(A')
      - element_count:       given small finite set in roster form, find n(A)
    """
    rng = random.Random(seed)
    seen: set[tuple] = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    sub_types = ["subset_total_count", "complement_count", "element_count"]
    if seed is not None:
        sub_type = sub_types[abs(int(seed)) % len(sub_types)]
    else:
        sub_type = rng.choice(sub_types)

    rotate = list(range(len(sub_types)))
    start = sub_types.index(sub_type)
    rotated = rotate[start:] + rotate[:start]

    parameter_tuple: tuple | None = None
    question_text = explanation = ""
    answer = 0

    for _ in range(120):
        for offset in rotated:
            sub_type_try = sub_types[offset]

            if sub_type_try == "subset_total_count":
                if difficulty <= 1:
                    n_pool = [2, 3, 4]
                elif difficulty == 2:
                    n_pool = [3, 4, 5]
                else:
                    n_pool = [4, 5, 6]
                n = rng.choice(n_pool)
                candidate = (
                    SET_OPERATION_COUNT_PROBLEM_TYPE_ID,
                    "subset_total_count",
                    n,
                )
                if candidate in seen:
                    continue
                element_pool = ["a", "b", "c", "d", "e", "f"][:n]
                set_repr = "\\{" + ", ".join(element_pool) + "\\}"
                answer = 2 ** n
                question_text = (
                    f"設集合 $A={set_repr}$（共有 ${n}$ 個元素），"
                    "請問 $A$ 共有多少個子集合？"
                )
                explanation = (
                    f"設集合 $A$ 共有 $n={n}$ 個元素，則其子集合的個數為 $2^n$。\n"
                    f"故 $A$ 的子集合個數為 $2^{{{n}}}={answer}$。"
                )
                parameter_tuple = candidate
                break

            if sub_type_try == "complement_count":
                if difficulty <= 1:
                    u_pool = [10, 12, 15, 20]
                elif difficulty == 2:
                    u_pool = [20, 25, 30, 36]
                else:
                    u_pool = [30, 40, 50, 60]
                u_size = rng.choice(u_pool)
                a_size = rng.randint(1, u_size - 1)
                candidate = (
                    SET_OPERATION_COUNT_PROBLEM_TYPE_ID,
                    "complement_count",
                    u_size,
                    a_size,
                )
                if candidate in seen:
                    continue
                answer = u_size - a_size
                question_text = (
                    f"設宇集 $U$ 共有 ${u_size}$ 個元素，子集 $A\\subseteq U$ 共有 "
                    f"${a_size}$ 個元素，求補集 $A'$ 的元素個數 $n(A')$。"
                )
                explanation = (
                    "由補集定義：$n(A')=n(U)-n(A)$。\n"
                    f"代入得 $n(A')={u_size}-{a_size}={answer}$。"
                )
                parameter_tuple = candidate
                break

            # element_count
            if difficulty <= 1:
                n_pool = [3, 4, 5]
            elif difficulty == 2:
                n_pool = [4, 5, 6, 7]
            else:
                n_pool = [5, 6, 7, 8]
            n = rng.choice(n_pool)
            start_int = rng.randint(1, 5)
            elements = list(range(start_int, start_int + n))
            candidate = (
                SET_OPERATION_COUNT_PROBLEM_TYPE_ID,
                "element_count",
                tuple(elements),
            )
            if candidate in seen:
                continue
            set_repr = "\\{" + ", ".join(str(x) for x in elements) + "\\}"
            answer = n
            question_text = (
                f"設集合 $A={set_repr}$，求 $A$ 的元素個數 $n(A)$。"
            )
            explanation = (
                f"集合 $A$ 中以 \"$,$\" 分隔的相異元素共 ${n}$ 個，\n"
                f"故 $n(A)={n}$。"
            )
            parameter_tuple = candidate
            break

        if parameter_tuple is not None:
            break

    if parameter_tuple is None:
        raise ValueError(
            "set_operation_count: failed to generate after retries."
        )

    choices = _make_integer_choices(answer, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": SET_OPERATION_COUNT_PROBLEM_TYPE_ID,
        "generator_key": SET_OPERATION_COUNT_GENERATOR_KEY,
        "answer_type": "integer",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "basic_concepts_of_sets",
            "set_operation_count",
            "subset_count",
            "complement_count",
        ],
        "remediation_candidates": [
            "sample_space_count_numeric",
        ],
        "source_style_refs": [
            "tc_b4_ch2_set_operation_count_01",
            "set_operation_count",
        ],
        "parameters": {
            "parameter_tuple": parameter_tuple,
            "answer": answer,
        },
    }
    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload


def inclusion_exclusion_count(
    *,
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
) -> dict:
    """Generate a two-set inclusion-exclusion counting problem.

    Variants (Phase 6K):
      - student_preference_union:    n(A∪B)=n(A)+n(B)-n(A∩B)
      - student_preference_neither:  n(U)-n(A∪B)
      - integer_multiples_union:     1..N 中為 a 倍數或 b 倍數的個數
                                     (= count(a) + count(b) - count(lcm(a,b)))
    """
    rng = random.Random(seed)
    seen: set[tuple] = seen_parameter_tuples if seen_parameter_tuples is not None else set()

    sub_types = [
        "student_preference_union",
        "student_preference_neither",
        "integer_multiples_union",
    ]
    if seed is not None:
        sub_type = sub_types[abs(int(seed)) % len(sub_types)]
    else:
        sub_type = rng.choice(sub_types)

    rotate = list(range(len(sub_types)))
    start = sub_types.index(sub_type)
    rotated = rotate[start:] + rotate[:start]

    parameter_tuple: tuple | None = None
    question_text = explanation = ""
    answer = 0

    sport_pairs = [
        ("打籃球", "踢足球"),
        ("游泳", "跑步"),
        ("吃水餃", "吃麵食"),
        ("看電影", "看書"),
        ("學鋼琴", "學吉他"),
    ]

    for _ in range(120):
        for offset in rotated:
            sub_type_try = sub_types[offset]

            if sub_type_try in ("student_preference_union", "student_preference_neither"):
                if difficulty <= 1:
                    u_pool = [30, 40, 50]
                elif difficulty == 2:
                    u_pool = [40, 50, 60, 80]
                else:
                    u_pool = [60, 80, 100]
                n_u = rng.choice(u_pool)
                n_inter = rng.randint(1, max(2, n_u // 5))
                n_a = rng.randint(n_inter + 2, max(n_inter + 3, n_u // 2))
                n_b = rng.randint(n_inter + 2, max(n_inter + 3, n_u // 2))
                paub = n_a + n_b - n_inter
                if paub <= 0 or paub > n_u:
                    continue
                if paub == n_a or paub == n_b:
                    continue

                pair = rng.choice(sport_pairs)
                a_label, b_label = pair

                if sub_type_try == "student_preference_union":
                    candidate = (
                        INCLUSION_EXCLUSION_COUNT_PROBLEM_TYPE_ID,
                        "student_preference_union",
                        n_u,
                        n_a,
                        n_b,
                        n_inter,
                        a_label,
                        b_label,
                    )
                    if candidate in seen:
                        continue
                    answer = paub
                    question_text = (
                        f"某班共 ${n_u}$ 位學生，調查興趣後得知喜歡{a_label}的有 "
                        f"${n_a}$ 人，喜歡{b_label}的有 ${n_b}$ 人，"
                        f"兩者皆喜歡的有 ${n_inter}$ 人。"
                        f"問至少喜歡其中一項的學生有多少人？"
                    )
                    explanation = (
                        "由兩集合容斥原理：\n"
                        "$n(A\\cup B)=n(A)+n(B)-n(A\\cap B)$。\n"
                        f"代入得 $n(A\\cup B)={n_a}+{n_b}-{n_inter}={answer}$。"
                    )
                    parameter_tuple = candidate
                    break

                # student_preference_neither
                neither = n_u - paub
                if neither <= 0:
                    continue
                candidate = (
                    INCLUSION_EXCLUSION_COUNT_PROBLEM_TYPE_ID,
                    "student_preference_neither",
                    n_u,
                    n_a,
                    n_b,
                    n_inter,
                    a_label,
                    b_label,
                )
                if candidate in seen:
                    continue
                answer = neither
                question_text = (
                    f"某班共 ${n_u}$ 位學生，喜歡{a_label}的有 ${n_a}$ 人，"
                    f"喜歡{b_label}的有 ${n_b}$ 人，兩者皆喜歡的有 ${n_inter}$ 人。"
                    f"問兩項都不喜歡的學生有多少人？"
                )
                explanation = (
                    "由兩集合容斥原理先求至少喜歡一項：\n"
                    f"$n(A\\cup B)=n(A)+n(B)-n(A\\cap B)={n_a}+{n_b}-{n_inter}={paub}$。\n"
                    f"再由補集個數：兩項都不喜歡的人數 $=n(U)-n(A\\cup B)={n_u}-{paub}={answer}$。"
                )
                parameter_tuple = candidate
                break

            # integer_multiples_union
            if difficulty <= 1:
                N_pool = [30, 40, 60]
                pair_pool = [(2, 3), (3, 4), (2, 5), (4, 6)]
            elif difficulty == 2:
                N_pool = [60, 90, 100, 120]
                pair_pool = [(2, 3), (3, 4), (2, 5), (3, 5), (4, 6)]
            else:
                N_pool = [100, 200, 300]
                pair_pool = [(2, 3), (3, 4), (2, 5), (3, 5), (4, 7), (6, 9)]
            N = rng.choice(N_pool)
            a, b = rng.choice(pair_pool)
            lcm = a * b // math.gcd(a, b)
            ca = N // a
            cb = N // b
            cab = N // lcm
            count_union = ca + cb - cab
            if count_union <= 0 or count_union > N:
                continue
            candidate = (
                INCLUSION_EXCLUSION_COUNT_PROBLEM_TYPE_ID,
                "integer_multiples_union",
                N,
                a,
                b,
            )
            if candidate in seen:
                continue
            answer = count_union
            question_text = (
                f"從 $1$ 到 ${N}$ 的整數中，是 ${a}$ 的倍數或是 ${b}$ 的倍數的整數共有多少個？"
            )
            explanation = (
                f"令 $A$ 為 ${a}$ 的倍數所成集合，$B$ 為 ${b}$ 的倍數所成集合，"
                f"則 $n(A)=\\lfloor {N}/{a}\\rfloor={ca}$、"
                f"$n(B)=\\lfloor {N}/{b}\\rfloor={cb}$、"
                f"$n(A\\cap B)=\\lfloor {N}/{lcm}\\rfloor={cab}$。\n"
                "由兩集合容斥：\n"
                f"$n(A\\cup B)={ca}+{cb}-{cab}={answer}$。"
            )
            parameter_tuple = candidate
            break

        if parameter_tuple is not None:
            break

    if parameter_tuple is None:
        raise ValueError(
            "inclusion_exclusion_count: failed to generate after retries."
        )

    choices = _make_integer_choices(answer, rng) if multiple_choice else []

    payload = {
        "question_text": question_text,
        "choices": choices,
        "answer": answer,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": INCLUSION_EXCLUSION_COUNT_PROBLEM_TYPE_ID,
        "generator_key": INCLUSION_EXCLUSION_COUNT_GENERATOR_KEY,
        "answer_type": "integer",
        "difficulty": difficulty,
        "diagnosis_tags": [
            "basic_concepts_of_sets",
            "inclusion_exclusion_count",
            "two_set_inclusion_exclusion",
        ],
        "remediation_candidates": [
            "set_operation_count",
            "sample_space_count_numeric",
        ],
        "source_style_refs": [
            "tc_b4_ch2_inclusion_exclusion_count_01",
            "inclusion_exclusion_count",
        ],
        "parameters": {
            "parameter_tuple": parameter_tuple,
            "answer": answer,
        },
    }
    validate_problem_payload_contract(payload)
    validate_no_unfilled_placeholder(payload["question_text"])
    validate_no_unfilled_placeholder(payload["explanation"])
    if seen_parameter_tuples is not None:
        seen_parameter_tuples.add(parameter_tuple)
    return payload
