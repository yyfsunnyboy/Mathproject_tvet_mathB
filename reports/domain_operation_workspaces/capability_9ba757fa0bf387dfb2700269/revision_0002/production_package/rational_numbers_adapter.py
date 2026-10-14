"""Question payload contracts for number_system.rational_numbers.

Every payload is graded by a checker registered in ``CHECKER_CAPABILITIES``; the
expected answer always comes from the domain matrix.  Operations whose answer
semantics no registered checker can grade exactly are refused, not approximated.
"""

from __future__ import annotations

import re
from fractions import Fraction
from math import ceil, floor, lcm
from typing import Any, Callable

from .rational_numbers_domain import DOMAIN_KEY, parse_exact_rational

TRUE_FALSE_CHOICES = ({"label": "A", "text": "正確"}, {"label": "B", "text": "錯誤"})

CHECKER_BLOCKED_OPERATIONS = {
    "fraction_to_decimal_expansion": (
        "checker_capability_missing", "no registered checker parses repeating-decimal notation",
    ),
    "construct_rational_between_bounds": (
        "checker_capability_missing", "no registered checker grades a strict-between predicate",
    ),
    "decimal_to_simplest_fraction": (
        "checker_required_form_blocked", "no registered checker enforces a simplest-fraction single answer",
    ),
}


def rational_latex(value: Any) -> str:
    exact = parse_exact_rational(value)
    if exact.denominator == 1:
        return str(exact.numerator)
    body = f"\\frac{{{abs(exact.numerator)}}}{{{exact.denominator}}}"
    return f"-{body}" if exact < 0 else body


def decimal_latex(text: str) -> str:
    repeating = re.fullmatch(r"(.*)\((\d+)\)", str(text))
    return f"{repeating.group(1)}\\overline{{{repeating.group(2)}}}" if repeating else str(text)


def descriptor_latex(descriptor: dict[str, Any]) -> str:
    kind = descriptor["kind"]
    if kind == "rational":
        return rational_latex(descriptor["value"])
    if kind in {"finite_decimal", "repeating_decimal"}:
        return decimal_latex(descriptor["value"])
    if kind == "sqrt":
        return f"\\sqrt{{{int(descriptor['radicand'])}}}"
    if kind == "sum":
        return " + ".join(descriptor_latex(term) for term in descriptor["terms"]).replace("+ -", "- ")
    raise ValueError(f"unsupported rationality descriptor kind: {kind}")


def statement_text(statement: dict[str, Any]) -> str:
    predicate = statement["predicate"]
    if predicate == "is_rational":
        return f"${descriptor_latex(statement['value'])}$ 是有理數"
    if predicate == "is_irrational":
        return f"${descriptor_latex(statement['value'])}$ 是無理數"
    if predicate == "equals":
        return f"${descriptor_latex(statement['left'])} = {descriptor_latex(statement['right'])}$"
    if predicate == "no_rational_between":
        return f"${rational_latex(statement['lower'])}$ 與 ${rational_latex(statement['upper'])}$ 之間沒有其他有理數"
    if predicate == "all_irrational":
        return "、".join(f"${descriptor_latex(value)}$" for value in statement["values"]) + " 都是無理數"
    if predicate == "sqrt_difference_identity":
        a, b = int(statement["left_radicand"]), int(statement["right_radicand"])
        return f"$\\sqrt{{(\\sqrt{{{a}}}-\\sqrt{{{b}}})^2}} = \\sqrt{{{a}}}-\\sqrt{{{b}}}$"
    raise ValueError(f"unsupported statement predicate: {predicate}")


def _contract(answer_type: str, presentation_mode: str, checker: str, equivalence: str, **extra: Any) -> dict[str, Any]:
    return {
        "presentation_mode": presentation_mode,
        "answer_type": answer_type,
        "checker": checker,
        "checker_key": checker,
        "answer_equivalence": equivalence,
        "equivalence": equivalence,
        "equivalence_type": equivalence,
        **extra,
    }


def _payload(
    matrix: dict[str, Any],
    *,
    question: str,
    answer: Any,
    display_answer: str,
    contract: dict[str, Any],
    explanation_steps: list[str],
    **extra: Any,
) -> dict[str, Any]:
    operation = matrix["domain_operation"]
    return {
        "question_text": question,
        "question": question,
        "answer": answer,
        "correct_answer": answer,
        "display_answer": display_answer,
        "semantic_answer": matrix["answer"],
        "answer_type": contract["answer_type"],
        "presentation_mode": contract["presentation_mode"],
        "problem_type_id": operation,
        "domain_operation": operation,
        "fixed_domain_key": DOMAIN_KEY,
        "answer_contract": {**contract, "semantic_answer": matrix["answer"]},
        "explanation_steps": explanation_steps,
        "choices": [],
        "options": [],
        "math_core": {
            "givens": matrix["givens"],
            "target": matrix["answer"],
            "validation_facts": matrix["validation_facts"],
        },
        **extra,
    }


def _tick_unit(values: list[Fraction]) -> str:
    denominator = lcm(*(value.denominator for value in values))
    return "1" if denominator == 1 else f"1/{denominator}"


def _plot_rational_points_on_number_line(matrix: dict[str, Any]) -> dict[str, Any]:
    points = matrix["answer"]["points"]
    values = [parse_exact_rational(point["value"]) for point in points]
    axis_range = {"min": floor(min(values)) - 1, "max": ceil(max(values)) + 1}
    spec = {
        "drawing_type": "number_line",
        "points": [
            {"label": p["label"], "value": p["value"], "latex": rational_latex(p["value"]), "approx": round(float(v), 6)}
            for p, v in zip(points, values)
        ],
        "ordered_labels": [p["label"] for p, _ in sorted(zip(points, values), key=lambda item: item[1])],
        "axis_range": axis_range,
        "tick_unit": _tick_unit(values),
        "required_elements": ["number_line", "origin", "labelled_points"],
    }
    ui_contract = {
        "response_mode": "drawing",
        "canvas_required": True,
        "text_input_enabled": False,
        "normal_submit_enabled": False,
        "allow_text_answer": False,
        "allow_image_upload": False,
    }
    labelled = "、".join(f"${p['label']}({rational_latex(p['value'])})$" for p in points)
    return _payload(
        matrix,
        question=f"在數線上標出下列各點：{labelled}",
        answer=spec,
        display_answer=labelled,
        contract=_contract(
            "drawing", "canvas", "free_response_drawing_checker", "drawing_equivalence",
            answer_shape="drawing", expected_drawing_spec=spec, ui_contract=ui_contract,
        ),
        explanation_steps=[f"由左至右依序為 {'、'.join(spec['ordered_labels'])}。"],
        answer_shape="drawing",
        interaction_type="handwriting_drawing",
        expected_drawing_spec=spec,
        visual_spec={"kind": "number_line_canvas", "axis_range": axis_range, "editable": True},
        metadata={"expected_drawing_spec": spec, "ui_contract": ui_contract, "answer_type": "drawing", "answer_shape": "drawing"},
    )


def _evaluate_rationality_statements(matrix: dict[str, Any]) -> dict[str, Any]:
    statements = matrix["givens"]["statements"]
    verdicts = ["正確" if value else "錯誤" for value in matrix["answer"]["truth_values"]]
    parts = [
        {
            "key": f"statement_{index}",
            "label": f"({index})",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "equivalence_type": "choice_label",
            "choices": [dict(choice) for choice in TRUE_FALSE_CHOICES],
            "expected_answer": verdict,
        }
        for index, verdict in enumerate(verdicts, start=1)
    ]
    lines = "\n".join(f"({i}) {statement_text(s)}" for i, s in enumerate(statements, start=1))
    return _payload(
        matrix,
        question=f"判斷下列敘述是否正確：\n{lines}",
        answer={part["key"]: part["expected_answer"] for part in parts},
        display_answer="　".join(f"({i}) {v}" for i, v in enumerate(verdicts, start=1)),
        contract=_contract(
            "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer",
            answer_shape="statement_truth_parts", parts=parts,
        ),
        explanation_steps=[f"({i}) {statement_text(s)}：{v}" for i, (s, v) in enumerate(zip(statements, verdicts), start=1)],
    )


def _identify_rational_numbers(matrix: dict[str, Any]) -> dict[str, Any]:
    candidates = matrix["givens"]["candidates"]
    indices = list(matrix["answer"]["indices"])
    items = "　".join(f"({i}) ${descriptor_latex(c)}$" for i, c in enumerate(candidates, start=1))
    return _payload(
        matrix,
        question=f"下列各數中，哪些是有理數？請寫出所有有理數的編號：{items}",
        answer=indices,
        display_answer="".join(f"({i})" for i in indices),
        contract=_contract(
            "short_answer", "short_answer", "solution_set_checker", "unordered_solution_set",
            answer_shape="selected_candidate_index_set",
        ),
        explanation_steps=["能寫成兩整數之比（分母不為 0）的數是有理數：" + "".join(f"({i})" for i in indices)],
    )


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "plot_rational_points_on_number_line": _plot_rational_points_on_number_line,
    "evaluate_rationality_statements": _evaluate_rationality_statements,
    "identify_rational_numbers": _identify_rational_numbers,
}


def adapt_rational_numbers_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    if operation in CHECKER_BLOCKED_OPERATIONS:
        status, reason = CHECKER_BLOCKED_OPERATIONS[operation]
        raise ValueError(f"{status}:{operation}:{reason}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_rational_numbers_operation:{operation}")
    return builder(matrix)
