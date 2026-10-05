"""Question payload contracts for number_system.real_numbers.

Every payload is graded by a checker registered in ``CHECKER_CAPABILITIES``; the
expected answer always comes from the domain matrix.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable

from .real_numbers_domain import DOMAIN_KEY, parse_exact_rational

_PLACE_WORDS = {1: "一", 2: "二", 3: "三", 4: "四"}


def rational_latex(value: Any) -> str:
    exact = parse_exact_rational(value)
    if exact.denominator == 1:
        return str(exact.numerator)
    body = f"\\frac{{{abs(exact.numerator)}}}{{{exact.denominator}}}"
    return f"-{body}" if exact < 0 else body


def _signed_terms(terms: list[tuple[Fraction, str]]) -> str:
    """Join ``coefficient·symbol`` terms; an empty symbol is a constant term."""
    text = ""
    for coefficient, symbol in terms:
        if coefficient == 0:
            continue
        magnitude = abs(coefficient)
        body = rational_latex(magnitude) if (not symbol or magnitude != 1) else ""
        body += symbol
        if not text:
            text = f"-{body}" if coefficient < 0 else body
        else:
            text += f"-{body}" if coefficient < 0 else f"+{body}"
    return text or "0"


def radical_number_latex(number: dict[str, Any], radicand: int) -> str:
    return _signed_terms([
        (parse_exact_rational(number["rational"]), ""),
        (parse_exact_rational(number["radical"]), f"\\sqrt{{{radicand}}}"),
    ])


def _coefficient_term(number: dict[str, Any], radicand: int, unknown: str) -> tuple[str, bool]:
    """Return (latex, negative) for ``coefficient·unknown`` written as in the textbook."""
    rational, radical = parse_exact_rational(number["rational"]), parse_exact_rational(number["radical"])
    if rational != 0 and radical != 0:
        return f"\\left({radical_number_latex(number, radicand)}\\right){unknown}", False
    if radical == 0:
        return _signed_terms([(abs(rational), unknown)]), rational < 0
    return _signed_terms([(abs(radical), f"\\sqrt{{{radicand}}}{unknown}")]), radical < 0


def identity_latex(givens: dict[str, Any]) -> str:
    radicand = givens["radicand"]
    left = ""
    for unknown, number in givens["coefficients"].items():
        term, negative = _coefficient_term(number, radicand, unknown)
        left += ("-" if negative else ("+" if left else "")) + term
    return f"{left}={radical_number_latex(givens['rhs'], radicand)}"


def _linear_equation_latex(coefficients: dict[str, str], constant: str) -> str:
    left = _signed_terms([(parse_exact_rational(c), name) for name, c in coefficients.items()])
    return f"{left}={rational_latex(constant)}"


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
    }


def _solve_rational_unknowns_from_radical_identity(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    radicand, names, values = givens["radicand"], answer["unknowns"], answer["values"]
    parts = [
        {
            "key": name,
            "label": name,
            "display_label": f"{name} =",
            "checker": "rational_checker",
            "checker_key": "rational_checker",
            "equivalence_type": "rational_equivalent",
            "answer_type": "rational",
            "expected_answer": values[name],
        }
        for name in names
    ]
    listed = ", ".join(names)
    return _payload(
        matrix,
        question=f"已知 {listed} 是有理數，且 ${identity_latex(givens)}$，求 {listed} 的值。",
        answer={name: values[name] for name in names},
        display_answer="，".join(f"${name}={rational_latex(values[name])}$" for name in names),
        contract=_contract(
            "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer",
            answer_shape="rational_unknown_values", parts=parts,
        ),
        explanation_steps=[
            f"因為 {listed} 都是有理數，而 $\\sqrt{{{radicand}}}$ 是無理數，等號兩邊的有理數部分與 $\\sqrt{{{radicand}}}$ 的係數必須分別相等：",
            f"$\\begin{{cases}} {_linear_equation_latex(**answer['rational_part_equation'])} \\\\ "
            f"{_linear_equation_latex(**answer['radical_part_equation'])} \\end{{cases}}$",
            "解得 " + "，".join(f"${name}={rational_latex(values[name])}$" for name in names) + "。",
        ],
    )


def _approximate_square_root_by_decimal_search(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    radicand, places, approximation = givens["radicand"], givens["places"], answer["approximation"]
    precision = f"小數點後第{_PLACE_WORDS[places]}位" if places else "整數位"
    root = f"\\sqrt{{{radicand}}}"
    return _payload(
        matrix,
        question=f"以十分逼近法求 ${root}$ 的近似值。（無條件捨去到{precision}）",
        answer=approximation,
        display_answer=f"${root} \\approx {approximation}$",
        contract=_contract(
            "rational", "short_answer", "rational_checker", "rational_equivalent",
            answer_shape="truncated_decimal_approximation", allow_decimal=True, required_form="decimal",
            decimal_places=places,
        ),
        explanation_steps=[
            f"由 ${step['lower']}^2={step['lower_square']}$、${step['upper']}^2={step['upper_square']}$，"
            f"可得 ${step['lower']}<{root}<{step['upper']}$。"
            for step in answer["steps"]
        ] + [f"無條件捨去到{precision}，得 ${root} \\approx {approximation}$。"],
    )


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "solve_rational_unknowns_from_radical_identity": _solve_rational_unknowns_from_radical_identity,
    "approximate_square_root_by_decimal_search": _approximate_square_root_by_decimal_search,
}


def adapt_real_numbers_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_real_numbers_operation:{operation}")
    return builder(matrix)
