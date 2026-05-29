from __future__ import annotations

import ast
import re
from fractions import Fraction
from typing import Any

SOLUTION_SET_TYPES = frozenset({"set", "solution_set", "integer_set", "number_set"})
INTERVAL_TYPES = frozenset({"interval", "union_of_intervals", "interval_set"})
CLASSIFICATION_TYPES = frozenset({"classification", "quadrant_label", "text_label", "category"})
NUMERIC_TYPES = frozenset({"numeric", "integer", "decimal", "number"})
RADICAL_TYPES = frozenset({"numeric_or_radical", "math_expression", "radical_number", "expression"})
CHOICE_TYPES = frozenset({"single_choice", "multi_choice", "choice", "choice_label"})

ANSWER_TYPE_ALIASES: dict[str, str] = {
    "integer": "numeric",
    "decimal": "numeric",
    "number": "numeric",
    "number_set": "solution_set",
    "integer_set": "solution_set",
    "union_of_intervals": "interval",
    "quadrant_label": "classification",
    "text_label": "classification",
    "category": "classification",
    "math_expression": "numeric_or_radical",
    "radical_number": "numeric_or_radical",
    "choice": "single_choice",
    "choice_label": "single_choice",
}

VALID_ANSWER_TYPES = frozenset(
    {
        "short_answer",
        "single_choice",
        "multi_choice",
        "numeric",
        "fraction",
        "expression",
        "set",
        "solution_set",
        "interval",
        "classification",
        "numeric_or_radical",
        "table",
        "manual_review",
    }
    | SOLUTION_SET_TYPES
    | INTERVAL_TYPES
    | CLASSIFICATION_TYPES
    | NUMERIC_TYPES
    | RADICAL_TYPES
    | CHOICE_TYPES
)

_RADICAL_TOKEN = re.compile(r"\\sqrt|sqrt\s*\(|√", re.I)


def coerce_correct_answer(value: Any) -> Any:
    """Preserve list/tuple/set; parse JSON-like list strings from session."""
    if isinstance(value, (list, tuple, set)):
        return list(value) if isinstance(value, set) else value
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return value
    if text.startswith("[") or text.startswith("(") or text.startswith("{"):
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, set):
                return sorted(parsed)
            if isinstance(parsed, (list, tuple)):
                return list(parsed)
        except Exception:
            pass
    return value


def canonical_answer_type(answer_type: str) -> str:
    raw = str(answer_type or "").strip()
    if not raw:
        return ""
    return ANSWER_TYPE_ALIASES.get(raw, raw)


def answer_type_family(answer_type: str) -> str:
    canon = canonical_answer_type(answer_type)
    if canon in SOLUTION_SET_TYPES:
        return "solution_set"
    if canon in INTERVAL_TYPES:
        return "interval"
    if canon in CLASSIFICATION_TYPES:
        return "classification"
    if canon in CHOICE_TYPES:
        return "single_choice"
    if canon in RADICAL_TYPES:
        return "numeric_or_radical"
    if canon in NUMERIC_TYPES:
        return "numeric"
    return canon


def _element_to_number(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else value
    text = str(value).strip()
    if not text:
        return None
    try:
        if "/" in text:
            return float(Fraction(text))
        num = float(text)
        return int(num) if num.is_integer() else num
    except Exception:
        return None


def normalize_solution_set_value(value: Any) -> list[int | float]:
    """Canonical list form for solution_set correct_answer (JSON-safe, sorted)."""
    from core.checkers.solution_set_checker import parse_solution_set_answer

    if isinstance(value, (list, tuple, set)):
        parsed = parse_solution_set_answer(list(value))
    else:
        parsed = parse_solution_set_answer(value)
    out: list[int | float] = sorted(parsed)
    return out


def normalize_correct_answer_for_contract(value: Any, answer_contract: dict[str, Any]) -> Any:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    family = answer_type_family(str(ac.get("answer_type", "")))
    if family == "solution_set":
        return normalize_solution_set_value(value)
    if family == "numeric_or_radical":
        return str(value).strip() if value is not None else ""
    if family in {"numeric", "fraction"}:
        if isinstance(value, (int, float)):
            return value
        return str(value).strip()
    return value


def is_valid_answer_payload(value: Any, answer_contract: dict[str, Any]) -> tuple[bool, str]:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    family = answer_type_family(str(ac.get("answer_type", "")))
    if value is None:
        return False, "answer_is_none"
    if family == "solution_set":
        try:
            normalized = normalize_solution_set_value(value)
        except Exception as ex:
            return False, f"solution_set_parse_failed:{ex}"
        if len(normalized) < 1:
            return False, "solution_set_empty"
        return True, ""
    if family == "interval":
        ok = bool(str(value).strip())
        return ok, ("" if ok else "interval_empty")
    if family == "classification":
        ok = bool(str(value).strip())
        return ok, ("" if ok else "classification_empty")
    if family == "single_choice":
        return bool(str(value).strip()), "choice_empty"
    if family == "numeric":
        return _element_to_number(value) is not None, "numeric_invalid"
    if family == "numeric_or_radical":
        text = str(value).strip()
        if not text:
            return False, "expression_empty"
        if _element_to_number(text) is not None:
            return True, ""
        if _RADICAL_TOKEN.search(text):
            return True, ""
        return bool(re.search(r"[0-9a-zA-Z+\-*/^=()\\]", text)), "expression_invalid"
    if family == "fraction":
        try:
            Fraction(str(value).strip())
            return True, ""
        except Exception:
            return False, "fraction_invalid"
    return bool(str(value).strip()), "answer_empty"


def expected_answer_shape_hint(answer_contract: dict[str, Any]) -> str:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    family = answer_type_family(str(ac.get("answer_type", "")))
    shape = str(ac.get("answer_shape", "")).strip()
    hints = {
        "solution_set": "solution_set allows list/tuple/set/string (unordered_set -> sorted list canonical)",
        "interval": "interval allows interval string or supported interval object/list",
        "classification": "classification allows normalized label string",
        "single_choice": "single_choice allows A/B/C/D or choice label text",
        "numeric": "numeric allows int/float/numeric string",
        "numeric_or_radical": "numeric_or_radical allows int/float/expression string",
        "fraction": "fraction allows fraction string or numeric",
        "short_answer": "short_answer allows non-empty string",
    }
    base = hints.get(family, f"{family} allows non-empty answer per contract")
    if shape:
        return f"{base}; answer_shape={shape}"
    return base


def build_answer_validation_diagnostics(
    payload: dict[str, Any],
    *,
    answer_contract: dict[str, Any] | None = None,
    failed_validator_name: str = "",
    validation_reason: str = "",
) -> dict[str, Any]:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    if not ac and isinstance(payload.get("answer_contract"), dict):
        ac = payload["answer_contract"]
    answer_val = payload.get("answer")
    correct_val = payload.get("correct_answer", answer_val)
    return {
        "problem_type_id": str(payload.get("problem_type_id", "")),
        "answer_type": str(ac.get("answer_type", payload.get("answer_type", ""))),
        "answer_shape": str(ac.get("answer_shape", "")),
        "checker": str(ac.get("checker", payload.get("checker", payload.get("checker_type", "")))),
        "equivalence": str(
            ac.get("answer_equivalence", payload.get("equivalence", payload.get("equivalence_type", "")))
        ),
        "answer_repr": repr(answer_val),
        "answer_python_type": type(answer_val).__name__,
        "correct_answer_repr": repr(correct_val),
        "correct_answer_python_type": type(correct_val).__name__,
        "validator_expected_types": sorted(VALID_ANSWER_TYPES),
        "expected_answer_shape": expected_answer_shape_hint(ac),
        "failed_validator_name": failed_validator_name,
        "validation_reason": validation_reason,
    }


def format_invalid_answer_type_error(
    *,
    problem_type_id: str,
    answer_contract: dict[str, Any],
    answer_value: Any,
    answer_field: str = "correct_answer",
    checker: str = "",
    equivalence: str = "",
) -> str:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    return (
        f"invalid_answer_type: problem_type_id={problem_type_id or '?'}"
        f" answer_type={ac.get('answer_type', '')}"
        f" answer_shape={ac.get('answer_shape', '')}"
        f" {answer_field}={repr(answer_value)}"
        f" {answer_field}_type={type(answer_value).__name__}"
        f" checker={checker or ac.get('checker', '')}"
        f" equivalence={equivalence or ac.get('answer_equivalence', '')}"
        f" expected={expected_answer_shape_hint(ac)}"
    )


def finalize_generator_payload(payload: dict[str, Any], answer_contract: dict[str, Any]) -> dict[str, Any]:
    """Normalize generator output to standard runtime dict contract (JSON-safe)."""
    out = dict(payload)
    ac = dict(answer_contract) if isinstance(answer_contract, dict) else {}
    if ac:
        out["answer_contract"] = ac
        if ac.get("answer_type"):
            out["answer_type"] = str(ac.get("answer_type"))
        checker_name = str(ac.get("checker", "")).strip()
        if checker_name:
            out["checker"] = checker_name
            out.setdefault("checker_type", checker_name)
        if ac.get("answer_equivalence"):
            out["equivalence"] = str(ac.get("answer_equivalence"))
    family = answer_type_family(str(ac.get("answer_type", "")))
    raw_answer = out.get("correct_answer", out.get("answer"))
    if family == "solution_set":
        canon = normalize_correct_answer_for_contract(raw_answer, ac)
        out["correct_answer"] = canon
        out["answer"] = canon
        if canon:
            out["display_answer"] = " 或 ".join(str(x) for x in canon)
    elif family == "numeric_or_radical" and raw_answer is not None:
        text = str(raw_answer).strip()
        out["correct_answer"] = text
        out["answer"] = text
    return out


def validate_generated_answer_shape(
    payload: dict[str, Any],
    *,
    answer_contract: dict[str, Any] | None = None,
    problem_type_id: str = "",
) -> tuple[bool, list[str], dict[str, Any]]:
    """Contract-aware answer shape validation for runtime smoke / generators."""
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    if not ac and isinstance(payload.get("answer_contract"), dict):
        ac = payload["answer_contract"]
    pt = str(problem_type_id or payload.get("problem_type_id", "")).strip()
    raw_type = str(ac.get("answer_type", "")).strip()
    canon_type = canonical_answer_type(raw_type)
    blockers: list[str] = []

    if raw_type and raw_type not in VALID_ANSWER_TYPES and canon_type not in VALID_ANSWER_TYPES:
        blockers.append(
            format_invalid_answer_type_error(
                problem_type_id=pt,
                answer_contract=ac,
                answer_value=payload.get("correct_answer", payload.get("answer")),
                checker=str(ac.get("checker", "")),
                equivalence=str(ac.get("answer_equivalence", "")),
            )
        )
        diag = build_answer_validation_diagnostics(
            payload,
            answer_contract=ac,
            failed_validator_name="answer_contract_type_registry",
            validation_reason="unknown_answer_type",
        )
        return False, blockers, diag

    answer_val = payload.get("answer")
    correct_val = payload.get("correct_answer", answer_val)
    for field_name, value in (("answer", answer_val), ("correct_answer", correct_val)):
        if value is None and field_name == "correct_answer" and answer_val is not None:
            continue
        ok, reason = is_valid_answer_payload(value, ac)
        if not ok:
            blockers.append(
                format_invalid_answer_type_error(
                    problem_type_id=pt,
                    answer_contract=ac,
                    answer_value=value,
                    answer_field=field_name,
                    checker=str(ac.get("checker", "")),
                    equivalence=str(ac.get("answer_equivalence", "")),
                )
            )
            diag = build_answer_validation_diagnostics(
                payload,
                answer_contract=ac,
                failed_validator_name="validate_generated_answer_shape",
                validation_reason=reason or "invalid_answer_shape",
            )
            return False, blockers, diag

    diag = build_answer_validation_diagnostics(payload, answer_contract=ac)
    return True, [], diag
