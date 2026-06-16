"""Adapter layer between Domain Full Matrix Dictionary and question payloads."""

from __future__ import annotations

import json
import random
from fractions import Fraction
from typing import Any

MATRIX_REQUIRED_FIELDS = (
    "givens",
    "answer",
    "distractors",
    "explanation_steps",
    "validation_facts",
    "visual_spec",
)

ANSWER_REQUIRED_FIELDS = (
    "canonical_form",
    "general_form",
    "coefficients",
    "slope",
    "intercept",
)


def validate_domain_matrix(matrix: dict[str, Any]) -> bool:
    """Assert that a domain matrix contains all six required top-level fields."""
    if not isinstance(matrix, dict):
        raise ValueError("matrix must be a dict.")

    missing = [field for field in MATRIX_REQUIRED_FIELDS if field not in matrix]
    if missing:
        raise ValueError(f"domain matrix missing required fields: {missing}")

    answer = matrix["answer"]
    if not isinstance(answer, dict):
        raise ValueError("matrix['answer'] must be a dict.")

    missing_answer = [field for field in ANSWER_REQUIRED_FIELDS if field not in answer]
    if missing_answer:
        raise ValueError(f"matrix['answer'] missing required fields: {missing_answer}")

    if not isinstance(matrix["distractors"], list):
        raise ValueError("matrix['distractors'] must be a list.")
    if not isinstance(matrix["explanation_steps"], list):
        raise ValueError("matrix['explanation_steps'] must be a list.")
    if not isinstance(matrix["validation_facts"], dict):
        raise ValueError("matrix['validation_facts'] must be a dict.")
    if not isinstance(matrix["visual_spec"], dict):
        raise ValueError("matrix['visual_spec'] must be a dict.")
    if not isinstance(matrix["givens"], dict):
        raise ValueError("matrix['givens'] must be a dict.")

    return True


def normalize_domain_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-serializable copy of a domain matrix using basic types only."""
    validate_domain_matrix(matrix)
    normalized = _normalize_value(matrix)
    if not isinstance(normalized, dict):
        raise ValueError("normalized matrix must remain a dict.")
    json.dumps(normalized, ensure_ascii=False)
    return normalized


def convert_line_equation_matrix_to_question_payload(matrix: dict[str, Any]) -> dict[str, Any]:
    """Map a line-equation domain matrix into a standard outward question payload."""
    normalized = normalize_domain_matrix(matrix)
    givens = normalized["givens"]
    answer = normalized["answer"]
    validation_facts = normalized["validation_facts"]
    visual_spec = normalized["visual_spec"]
    explanation_steps = normalized["explanation_steps"]
    distractors = normalized["distractors"]

    assert isinstance(givens, dict)
    assert isinstance(answer, dict)
    assert isinstance(validation_facts, dict)
    assert isinstance(visual_spec, dict)
    assert isinstance(explanation_steps, list)
    assert isinstance(distractors, list)

    canonical = str(answer["canonical_form"])
    question_text = _build_line_equation_question_text(givens, validation_facts)
    choices, correct_label = _build_choice_options(canonical, distractors, seed_text=canonical)

    math_objects = _infer_math_objects(validation_facts)
    math_core: dict[str, Any] = {
        "givens": _format_givens_for_hint(givens),
        "target": canonical,
        "math_objects": math_objects,
        "derivation": [str(step) for step in explanation_steps],
        "validation_facts": validation_facts,
    }

    return {
        "question_text": question_text,
        "question": question_text,
        "correct_answer": canonical,
        "answer": correct_label,
        "choices": choices,
        "options": [str(choice["text"]) for choice in choices],
        "visual_spec": visual_spec,
        "math_core": math_core,
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "metadata": {
            "givens": math_core["givens"],
            "target": canonical,
            "derivation": math_core["derivation"],
            "coefficients": answer.get("coefficients"),
            "general_form": answer.get("general_form"),
        },
    }


def _normalize_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return value.numerator
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): _normalize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_value(item) for item in value]
    if isinstance(value, set):
        return [_normalize_value(item) for item in sorted(value, key=str)]
    raise TypeError(f"Unsupported non-JSON-serializable value type: {type(value)!r}")


def _build_line_equation_question_text(
    givens: dict[str, Any],
    validation_facts: dict[str, Any],
) -> str:
    line_type = str(validation_facts.get("line_type", ""))

    if "point_a" in givens and "point_b" in givens:
        pa = givens["point_a"]
        pb = givens["point_b"]
        ax, ay = int(pa[0]), int(pa[1])
        bx, by = int(pb[0]), int(pb[1])
        if ax == bx:
            # 鉛直線：兩點 x 相同，課本慣例用 C、D 標記
            return (
                f"試求通過 $C({ax},\\,{ay})$ 與 $D({bx},\\,{by})$ 兩點之直線方程式。"
            )
        if ay == by:
            # 水平線：兩點 y 相同，課本慣例用 A、B 標記
            return (
                f"試求通過 $A({ax},\\,{ay})$ 與 $B({bx},\\,{by})$ 兩點之直線方程式。"
            )
        return (
            f"試求通過 $A({ax},\\,{ay})$ 與 $B({bx},\\,{by})$ 兩點之直線方程式。"
        )

    if "point" in givens and "slope" in givens:
        point = givens["point"]
        slope = givens["slope"]
        px, py = int(point[0]), int(point[1])
        return (
            f"已知直線過點 $({px},\\,{py})$，斜率為 ${slope}$，求此直線方程式。"
        )

    if line_type == "horizontal_line" or "y_intercept" in givens:
        y_val = givens.get("y_intercept")
        return f"寫出斜率為 0 且通過 y 軸上 {y_val} 的水平線方程式。"

    if line_type == "vertical_line" or "x_intercept" in givens:
        x_val = givens.get("x_intercept")
        return f"寫出鉛直且通過 x = {x_val} 的直線方程式。"

    return "請寫出符合題意的直線方程式。"


def _build_choice_options(
    canonical: str,
    distractors: list[Any],
    *,
    seed_text: str,
) -> tuple[list[dict[str, str]], str]:
    unique_wrong: list[str] = []
    seen: set[str] = {canonical}
    for item in distractors:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        unique_wrong.append(text)

    option_texts = [canonical] + unique_wrong[:3]
    rng = random.Random(sum(ord(ch) for ch in seed_text))
    rng.shuffle(option_texts)

    choices: list[dict[str, str]] = []
    correct_label = "A"
    for index, text in enumerate(option_texts):
        label = chr(ord("A") + index)
        choices.append({"label": label, "text": text})
        if text == canonical:
            correct_label = label
    return choices, correct_label


def _infer_math_objects(validation_facts: dict[str, Any]) -> list[str]:
    objects = ["coordinate_point", "linear_equation"]
    if validation_facts.get("is_horizontal"):
        objects.append("horizontal_line")
    if validation_facts.get("is_vertical"):
        objects.append("vertical_line")
    return objects


def _format_givens_for_hint(givens: dict[str, Any]) -> list[str]:
    formatted: list[str] = []
    if "point_a" in givens and "point_b" in givens:
        formatted.append(f"A={tuple(givens['point_a'])}")
        formatted.append(f"B={tuple(givens['point_b'])}")
    if "point" in givens:
        formatted.append(f"point={tuple(givens['point'])}")
    if "slope" in givens:
        formatted.append(f"slope={givens['slope']}")
    if "y_intercept" in givens:
        formatted.append(f"y_intercept={givens['y_intercept']}")
    if "x_intercept" in givens:
        formatted.append(f"x_intercept={givens['x_intercept']}")
    return formatted
