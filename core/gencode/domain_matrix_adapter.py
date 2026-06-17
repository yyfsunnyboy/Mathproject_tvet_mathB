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


def _build_line_equation_answer_contract(
    *,
    presentation_mode: str,
    answer_type: str,
    semantic_answer: str,
    task_type: str = "",
) -> dict[str, Any]:
    if presentation_mode == "single_choice":
        return {
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence": "choice_label",
            "semantic_answer": semantic_answer,
        }
    if task_type == "slope_intercept_find_x_intercept":
        return {
            "presentation_mode": "short_answer",
            "answer_type": "rational",
            "checker": "rational_checker",
            "checker_key": "rational_checker",
            "answer_equivalence": "rational_equivalent",
            "equivalence": "rational_equivalent",
            "semantic_answer": semantic_answer,
        }
    if task_type == "slope_intercept_read_slope_and_intercept":
        return {
            "presentation_mode": "short_answer",
            "answer_type": "text_short",
            "checker": "text_short_checker",
            "checker_key": "text_short_checker",
            "answer_equivalence": "exact_string",
            "equivalence": "exact_string",
            "semantic_answer": semantic_answer,
        }
    return {
        "presentation_mode": "short_answer",
        "answer_type": answer_type,
        "checker": "linear_equation_equivalent_checker",
        "checker_key": "linear_equation_equivalent_checker",
        "answer_equivalence": "linear_equation_equivalent",
        "equivalence": "linear_equation_equivalent",
        "semantic_answer": semantic_answer,
    }


def convert_line_equation_matrix_to_question_payload(
    matrix: dict[str, Any],
    *,
    presentation_mode: str | None = None,
    answer_type: str | None = None,
    problem_type_id: str | None = None,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    source_kind: str | None = None,
    generator_key: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Map a line-equation domain matrix into a standard outward question payload."""
    _ = kwargs
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
    semantic_answer = canonical
    question_text = _build_line_equation_question_text(givens, validation_facts)
    mode = str(presentation_mode or "short_answer").strip()
    task_type = str(validation_facts.get("task_type") or validation_facts.get("line_type") or "").strip()
    if mode == "single_choice":
        default_answer_type = "single_choice"
    elif task_type == "slope_intercept_find_x_intercept":
        default_answer_type = "rational"
    elif task_type == "slope_intercept_read_slope_and_intercept":
        default_answer_type = "text_short"
    else:
        default_answer_type = "expression"
    resolved_answer_type = str(answer_type or default_answer_type).strip()
    if task_type == "slope_intercept_find_x_intercept" and mode != "single_choice":
        resolved_answer_type = "rational"
    elif task_type == "slope_intercept_read_slope_and_intercept" and mode != "single_choice":
        resolved_answer_type = "text_short"

    math_objects = _infer_math_objects(validation_facts)
    math_core: dict[str, Any] = {
        "givens": _format_givens_for_hint(givens),
        "target": canonical,
        "math_objects": math_objects,
        "derivation": [str(step) for step in explanation_steps],
        "validation_facts": validation_facts,
    }

    contract_fields = {
        "problem_type_id": problem_type_id,
        "component_id": component_id,
        "textbook_example_id": textbook_example_id,
        "source_kind": source_kind,
        "generator_key": generator_key or component_id,
    }
    metadata: dict[str, Any] = {
        "givens": math_core["givens"],
        "target": canonical,
        "derivation": math_core["derivation"],
        "coefficients": answer.get("coefficients"),
        "general_form": answer.get("general_form"),
        "line_equation": answer.get("line_equation") or canonical,
        "presentation_mode": mode,
        "answer_type": resolved_answer_type,
        "semantic_answer": semantic_answer,
    }
    for key, value in contract_fields.items():
        if value is not None:
            metadata[key] = value

    if mode == "single_choice":
        if task_type == "slope_intercept_find_x_intercept":
            choices, correct_label = _build_x_intercept_choice_options(
                canonical,
                givens,
                seed_text=f"{canonical}|{givens.get('slope')}|{givens.get('y_intercept')}",
            )
        else:
            choices, correct_label = _build_choice_options(canonical, distractors, seed_text=canonical)
        payload_answer = correct_label
        payload_correct = correct_label
        display_answer = _format_latex_display_answer(semantic_answer, task_type)
        choices = [
            {**choice, "text": _format_latex_display_answer(str(choice["text"]), task_type)}
            for choice in choices
        ]
        options = [str(choice["text"]) for choice in choices]
        answer_contract = _build_line_equation_answer_contract(
            presentation_mode=mode,
            answer_type=resolved_answer_type,
            semantic_answer=semantic_answer,
            task_type=task_type,
        )
    else:
        choices = []
        options = []
        payload_answer = semantic_answer
        payload_correct = semantic_answer
        display_answer = _format_latex_display_answer(semantic_answer, task_type)
        answer_contract = _build_line_equation_answer_contract(
            presentation_mode=mode,
            answer_type=resolved_answer_type,
            semantic_answer=semantic_answer,
            task_type=task_type,
        )

    payload: dict[str, Any] = {
        "question_text": question_text,
        "question": question_text,
        "correct_answer": payload_correct,
        "answer": payload_answer,
        "display_answer": display_answer,
        "semantic_answer": semantic_answer,
        "choices": choices,
        "options": options,
        "visual_spec": visual_spec,
        "math_core": math_core,
        "presentation_mode": mode,
        "answer_type": resolved_answer_type,
        "metadata": metadata,
        "answer_contract": answer_contract,
        "checker": answer_contract.get("checker"),
        "checker_type": answer_contract.get("checker"),
        "equivalence": answer_contract.get("answer_equivalence"),
    }
    if problem_type_id:
        payload["problem_type_id"] = problem_type_id
    if component_id:
        payload["component_id"] = component_id
    if textbook_example_id is not None:
        payload["textbook_example_id"] = textbook_example_id
    if source_kind:
        payload["source_kind"] = source_kind
    if generator_key or component_id:
        payload["generator_key"] = generator_key or component_id
    return payload


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


def _latex_inline(value: Any) -> str:
    return f"\\({_format_latex_math_text(str(value))}\\)"


def _latex_inline_equation(value: Any) -> str:
    return f"\\({_format_latex_math_text(str(value))}\\)"


def _format_latex_display_answer(value: str, task_type: str = "") -> str:
    text = str(value or "").strip()
    if not text:
        return text
    if task_type.startswith("slope_intercept"):
        return _latex_inline_equation(text)
    return text


def _format_latex_math_text(text: str) -> str:
    import re

    normalized = str(text or "").strip().replace("−", "-")

    def repl_fraction(match: re.Match[str]) -> str:
        sign = "-" if match.group(1) == "-" else ""
        numerator = match.group(2)
        denominator = match.group(3)
        return f"{sign}\\frac{{{numerator}}}{{{denominator}}}"

    normalized = re.sub(r"(?<![\\\w])(-?)(\d+)/(\d+)", repl_fraction, normalized)
    return normalized


def _build_line_equation_question_text(
    givens: dict[str, Any],
    validation_facts: dict[str, Any],
) -> str:
    line_type = str(validation_facts.get("line_type", ""))
    task_type = str(validation_facts.get("task_type", ""))

    if task_type == "slope_intercept_equation":
        slope = givens.get("slope")
        y_intercept = givens.get("y_intercept")
        return (
            f"已知直線的斜率為 {_latex_inline(slope)}，且 y 截距為 {_latex_inline(y_intercept)}，"
            "試求此直線方程式。"
        )

    if task_type == "slope_intercept_find_x_intercept":
        slope = givens.get("slope")
        y_intercept = givens.get("y_intercept")
        return (
            f"設直線 L 的斜率為 {_latex_inline(slope)}，且 y 截距為 {_latex_inline(y_intercept)}，"
            "求 L 的 x 截距。"
        )

    if task_type == "slope_intercept_read_slope_and_intercept":
        equation = givens.get("equation")
        return f"已知直線方程式為 {_latex_inline_equation(equation)}，判斷其斜率與 y 截距。"

    if "point_a" in givens and "point_b" in givens:
        pa = givens["point_a"]
        pb = givens["point_b"]
        ax, ay = int(pa[0]), int(pa[1])
        bx, by = int(pb[0]), int(pb[1])
        if ax == bx:
            return (
                f"試求通過 $C({ax},\\,{ay})$ 與 $D({bx},\\,{by})$ 兩點之直線方程式。"
            )
        if ay == by:
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


def _parse_fraction_text(value: Any) -> Fraction:
    text = str(value or "").strip()
    if not text:
        return Fraction(0, 1)
    return Fraction(text)


def _format_fraction_text(value: Fraction) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _build_x_intercept_choice_options(
    canonical: str,
    givens: dict[str, Any],
    *,
    seed_text: str,
) -> tuple[list[dict[str, str]], str]:
    correct = _parse_fraction_text(canonical)
    slope = _parse_fraction_text(givens.get("slope"))
    y_intercept = _parse_fraction_text(givens.get("y_intercept"))
    rng = random.Random(sum(ord(ch) for ch in seed_text))

    candidate_values: list[Fraction] = [
        correct,
        -correct,
        correct + 1,
        correct - 1,
        correct + Fraction(1, 2),
        correct - Fraction(1, 2),
        y_intercept,
        -y_intercept,
        slope,
        -slope,
    ]
    for offset in range(2, 10):
        candidate_values.append(correct + offset)
        candidate_values.append(correct - offset)

    wrong_values: list[Fraction] = []
    seen: set[Fraction] = {correct}
    for value in candidate_values:
        value = Fraction(value)
        if value in seen:
            continue
        seen.add(value)
        wrong_values.append(value)
        if len(wrong_values) >= 3:
            break
    while len(wrong_values) < 3:
        value = Fraction(rng.randint(-8, 8), rng.choice([1, 2, 3, 4, 5]))
        if value in seen:
            continue
        seen.add(value)
        wrong_values.append(value)

    option_values = [correct] + wrong_values[:3]
    rng.shuffle(option_values)

    choices: list[dict[str, str]] = []
    correct_label = "A"
    for index, value in enumerate(option_values):
        label = chr(ord("A") + index)
        text = _format_fraction_text(value)
        choices.append({"label": label, "text": text})
        if value == correct:
            correct_label = label
    return choices, correct_label


def _infer_math_objects(validation_facts: dict[str, Any]) -> list[str]:
    objects = ["coordinate_point", "linear_equation"]
    task_type = str(validation_facts.get("task_type") or "")
    if task_type.startswith("slope_intercept"):
        objects.append("slope_intercept_form")
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
    if "equation" in givens:
        formatted.append(f"equation={givens['equation']}")
    return formatted
