from __future__ import annotations

from fractions import Fraction
from math import gcd
import random
from typing import Any

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice_label"
PROBLEM_TYPE_ID = "parallel_lines_distance_single_choice"
TEXTBOOK_EXAMPLE_ID = 4584
COMPONENT_ID = "src_4584"


def _square_free_factor(n: int) -> tuple[int, int]:
    outside = 1
    inside = int(n)
    factor = 2
    while factor * factor <= inside:
        square = factor * factor
        while inside % square == 0:
            outside *= factor
            inside //= square
        factor += 1
    return outside, inside


def _latex_int(n: int) -> str:
    return str(n)


def _latex_fraction(frac: Fraction) -> str:
    if frac.denominator == 1:
        return _latex_int(frac.numerator)
    sign = "-" if frac.numerator < 0 else ""
    return f"{sign}\\frac{{{abs(frac.numerator)}}}{{{frac.denominator}}}"


def _latex_distance(k: int, norm_sq: int) -> str:
    outside, inside = _square_free_factor(norm_sq)
    numerator_coeff = k * outside
    common = gcd(numerator_coeff, norm_sq)
    numerator_coeff //= common
    denominator = norm_sq // common

    if inside == 1:
        if denominator == 1:
            return str(numerator_coeff)
        return f"\\frac{{{numerator_coeff}}}{{{denominator}}}"

    radical = f"\\sqrt{{{inside}}}"
    if numerator_coeff == 1:
        numerator = radical
    else:
        numerator = f"{numerator_coeff}{radical}"
    if denominator == 1:
        return numerator
    return f"\\frac{{{numerator}}}{{{denominator}}}"


def _line_expression(b: int) -> str:
    if b == 1:
        return "ax+y+k=0"
    if b == -1:
        return "ax-y+k=0"
    if b > 0:
        return f"ax+{b}y+k=0"
    return f"ax{b}y+k=0"


def _choice_rows(correct_value: int, rng: random.Random) -> tuple[list[dict[str, str]], str]:
    distractors = {
        correct_value - 4,
        correct_value - 2,
        correct_value + 2,
        correct_value + 4,
        correct_value + 6,
        abs(correct_value),
        correct_value + 8,
    }
    distractors.discard(correct_value)
    while len(distractors) < 3:
        distractors.add(correct_value + rng.choice([-10, -8, -6, 6, 8, 10, 12]))
        distractors.discard(correct_value)

    values = [correct_value] + sorted(distractors, key=lambda x: (abs(x - correct_value), x))[:3]
    rng.shuffle(values)
    labels = ["A", "B", "C", "D"]
    choices = [{"label": label, "text": str(value)} for label, value in zip(labels, values)]
    answer_label = next(item["label"] for item in choices if int(item["text"]) == correct_value)
    return choices, answer_label


def _parameter_pool() -> list[tuple[int, int, int]]:
    return [
        (-2, 4, 10),  # 112 統測 B 同構核心：m=1/2, d=sqrt(5), a+k=8
        (-3, 6, 15),
        (-4, 8, 20),
        (-1, 2, 5),
        (-6, 4, 10),
        (-4, 6, 13),
        (-8, 6, 25),
        (2, 4, 10),
        (3, 6, 15),
        (4, 8, 20),
        (6, 4, 10),
        (4, 6, 13),
        (8, 6, 25),
        (-5, 12, 13),
        (5, 12, 13),
        (-7, 24, 25),
        (7, 24, 25),
    ]


def _build_payload(a: int, b: int, k: int, *, seed: int | None, component_id: str) -> dict[str, Any]:
    if b == 0:
        raise ValueError("src_4584_invalid_parameter:b_zero")
    if k <= 0:
        raise ValueError("src_4584_invalid_parameter:k_not_positive")

    slope = Fraction(-a, b)
    norm_sq = a * a + b * b
    distance_latex = _latex_distance(k, norm_sq)
    distance_squared = Fraction(k * k, norm_sq)
    answer_value = a + k
    rng = random.Random(f"src_4584|choices|{seed}|{a}|{b}|{k}")
    choices, answer_label = _choice_rows(answer_value, rng)

    line_expr = _line_expression(b)
    slope_latex = _latex_fraction(slope)
    question_text = (
        f"已知 $k>0$。若直線 $L: {line_expr}$ 的斜率為 ${slope_latex}$，"
        f"且點 $(0,0)$ 到直線 $L$ 的距離為 ${distance_latex}$，則 $a+k=$？"
    )
    derivation = [
        f"由斜率 -a/b=m：-{a}/{b}={slope_latex}，可唯一求得 a={a}。",
        f"由 k/sqrt(a^2+b^2)=d 且 k>0：k/sqrt({norm_sq})={distance_latex}，可唯一求得 k={k}。",
        f"a+k={answer_value}。",
    ]

    payload: dict[str, Any] = {
        "question_text": question_text,
        "question": question_text,
        "choices": choices,
        "options": [item["text"] for item in choices],
        "answer": answer_label,
        "correct_answer": answer_label,
        "display_answer": answer_label,
        "semantic_answer": answer_label,
        "presentation_mode": PRESENTATION_MODE,
        "response_mode": PRESENTATION_MODE,
        "interaction_type": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "answer_value_type": ANSWER_TYPE,
        "problem_type_id": PROBLEM_TYPE_ID,
        "component_id": component_id,
        "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
        "generator_key": COMPONENT_ID,
        "seed": seed,
        "math_core": {
            "givens": [
                f"b={b}",
                f"m={slope}",
                f"d={distance_latex}",
                "k>0",
            ],
            "raw_givens": {
                "a": a,
                "b": b,
                "k": k,
                "line_expression": line_expr,
                "slope": str(slope),
                "slope_latex": slope_latex,
                "origin_distance": distance_latex,
                "origin_distance_squared": str(distance_squared),
                "norm_squared": norm_sq,
                "answer_value": answer_value,
            },
            "target": "a+k",
            "math_objects": ["coordinate_point", "linear_equation"],
            "derivation": derivation,
            "validation_facts": {
                "domain_operation": PROBLEM_TYPE_ID,
                "task_type": PROBLEM_TYPE_ID,
                "line_type": PROBLEM_TYPE_ID,
                "isomorphic_to_textbook_112_tvet_b": True,
                "slope_determines_a": True,
                "distance_and_k_positive_determine_k": True,
            },
        },
        "metadata": {
            "givens": [
                f"b={b}",
                f"slope={slope}",
                f"distance={distance_latex}",
                "k>0",
            ],
            "raw_givens": {
                "a": a,
                "b": b,
                "k": k,
                "line_expression": line_expr,
                "slope": str(slope),
                "slope_latex": slope_latex,
                "origin_distance": distance_latex,
                "origin_distance_squared": str(distance_squared),
                "norm_squared": norm_sq,
                "answer_value": answer_value,
            },
            "target": "a+k",
            "derivation": derivation,
            "semantic_answer": answer_label,
            "display_answer": answer_label,
            "answer_value": answer_value,
            "component_id": component_id,
            "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
            "generator_key": COMPONENT_ID,
        },
        "answer_contract": {
            "presentation_mode": PRESENTATION_MODE,
            "answer_type": ANSWER_TYPE,
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence": "choice_label",
            "semantic_answer": answer_label,
        },
        "checker": "choice_label_checker",
        "checker_type": "choice_label_checker",
        "equivalence": "choice_label",
    }
    return payload


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(f"src_4584|{seed}|{level}")
    params = list(_parameter_pool())
    a, b, k = params[rng.randrange(len(params))]
    component_id = str(kwargs.get("component_id") or COMPONENT_ID)
    return _build_payload(a, b, k, seed=seed, component_id=component_id)
