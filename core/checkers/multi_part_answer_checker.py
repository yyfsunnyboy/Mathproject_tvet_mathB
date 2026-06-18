from __future__ import annotations

from fractions import Fraction
from typing import Any


SUPPORTED_PART_CHECKERS = frozenset(
    {
        "numeric_checker",
        "integer_checker",
        "rational_checker",
        "fraction_checker",
        "expression_checker",
        "expression_equivalence_checker",
        "linear_equation_equivalent_checker",
        "choice_label_checker",
    }
)


def _part_key(part: dict[str, Any], index: int) -> str:
    return str(part.get("key") or part.get("id") or f"part_{index + 1}").strip()


def _value_for_part(answer: Any, key: str, index: int) -> Any:
    if isinstance(answer, dict):
        if key in answer:
            return answer.get(key)
        return None
    if isinstance(answer, (list, tuple)):
        return answer[index] if index < len(answer) else None
    return None


def _normalize_scalar(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _check_numeric_equivalent(student: Any, expected: Any) -> bool:
    try:
        student_frac = Fraction(str(student).strip())
        expected_frac = Fraction(str(expected).strip())
    except Exception:
        return False
    return student_frac == expected_frac


def _check_part(
    *,
    student_answer: Any,
    expected_answer: Any,
    checker: str,
    equivalence_type: str,
    part: dict[str, Any],
) -> bool:
    checker_key = checker.strip()
    equiv = equivalence_type.strip()
    if checker_key in {"numeric_checker", "integer_checker"} or equiv == "numeric_exact":
        return _check_numeric_equivalent(student_answer, expected_answer)
    if checker_key in {"rational_checker", "fraction_checker"} or equiv == "rational_equivalent":
        return _check_numeric_equivalent(student_answer, expected_answer)
    if checker_key in {"expression_checker", "expression_equivalence_checker"} or equiv == "algebraic_equivalent":
        from core.checkers.expression_equivalence_checker import check_expression_equivalence_answer

        return check_expression_equivalence_answer(student_answer, expected_answer)
    if checker_key == "linear_equation_equivalent_checker" or equiv == "linear_equation_equivalent":
        from core.checkers.linear_equation_equivalent_checker import check_linear_equation_equivalent_answer

        return check_linear_equation_equivalent_answer(student_answer, expected_answer)
    if checker_key == "choice_label_checker" or equiv == "choice_label":
        from core.checkers.choice_label_checker import check_choice_label

        choices = part.get("choices") if isinstance(part.get("choices"), list) else []
        return bool(check_choice_label(student_answer, expected_answer, choices))
    return _normalize_scalar(student_answer) == _normalize_scalar(expected_answer)


def check_multi_part_answer(
    student_answer: Any,
    correct_answer: Any,
    *,
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Check multi-part answers where each part can use its own checker.

    Contract shape:
      {
        "answer_type": "multi_part",
        "checker": "multi_part_answer_checker",
        "equivalence_type": "multi_part_answer",
        "parts": [
          {
            "key": "equation",
            "label": "equation",
            "checker": "linear_equation_equivalent_checker",
            "equivalence_type": "linear_equation_equivalent",
            "expected_answer": "x + y - 6 = 0",
          }
        ],
      }
    """
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    if not ac and isinstance(payload, dict) and isinstance(payload.get("answer_contract"), dict):
        ac = payload["answer_contract"]
    parts = ac.get("parts") if isinstance(ac.get("parts"), list) else []

    per_part_results: list[dict[str, Any]] = []
    failed_parts: list[str] = []
    normalized_student: dict[str, Any] = {}
    normalized_correct: dict[str, Any] = {}

    for index, raw_part in enumerate(parts):
        if not isinstance(raw_part, dict):
            continue
        key = _part_key(raw_part, index)
        label = str(raw_part.get("label") or key).strip()
        checker = str(raw_part.get("checker") or raw_part.get("checker_key") or "").strip()
        equivalence = str(raw_part.get("equivalence_type") or raw_part.get("answer_equivalence") or "").strip()
        expected = raw_part.get("expected_answer")
        if expected is None:
            expected = _value_for_part(correct_answer, key, index)
        student = _value_for_part(student_answer, key, index)

        missing = student is None or _normalize_scalar(student) == ""
        supported = checker in SUPPORTED_PART_CHECKERS or equivalence in {
            "numeric_exact",
            "rational_equivalent",
            "algebraic_equivalent",
            "linear_equation_equivalent",
            "choice_label",
        }
        correct = False
        reason = ""
        if missing:
            reason = "missing_part"
        elif not supported:
            reason = "unsupported_part_checker"
        else:
            correct = _check_part(
                student_answer=student,
                expected_answer=expected,
                checker=checker,
                equivalence_type=equivalence,
                part=raw_part,
            )
            reason = "correct" if correct else "incorrect"

        normalized_student[key] = student
        normalized_correct[key] = expected
        row = {
            "key": key,
            "label": label,
            "checker": checker,
            "equivalence_type": equivalence,
            "correct": correct,
            "reason": reason,
            "student_answer": student,
            "expected_answer": expected,
        }
        per_part_results.append(row)
        if not correct:
            failed_parts.append(key)

    overall_correct = bool(parts) and not failed_parts and len(per_part_results) == len(parts)
    return {
        "overall_correct": overall_correct,
        "is_correct": overall_correct,
        "checker": "multi_part_answer_checker",
        "per_part_results": per_part_results,
        "failed_parts": failed_parts,
        "normalized_student_answer": normalized_student,
        "normalized_correct_answer": normalized_correct,
    }
