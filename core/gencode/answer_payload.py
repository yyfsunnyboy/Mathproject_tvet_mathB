from __future__ import annotations

import ast
import re
from fractions import Fraction
from typing import Any

from core.gencode.answer_contract_gate import coerce_single_choice_contract

SOLUTION_SET_TYPES = frozenset({"set", "solution_set", "integer_set", "number_set"})
INTERVAL_TYPES = frozenset({"interval", "union_of_intervals", "interval_set"})
CLASSIFICATION_TYPES = frozenset({"classification", "quadrant_label", "text_label", "category"})
NUMERIC_TYPES = frozenset({"numeric", "integer", "decimal", "number"})
RADICAL_TYPES = frozenset({"numeric_or_radical", "math_expression", "radical_number", "expression"})
CHOICE_TYPES = frozenset({"single_choice", "multi_choice", "choice", "choice_label"})
COORDINATE_PAIR_TYPES = frozenset({"coordinate_pair", "ordered_pair"})
TEXT_SHORT_TYPES = frozenset({"text", "text_short", "exact_string", "case_insensitive_string"})

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
    "ordered_pair": "coordinate_pair",
    "text": "short_answer",
    "text_short": "short_answer",
    "exact_string": "short_answer",
    "case_insensitive_string": "short_answer",
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
    | COORDINATE_PAIR_TYPES
    | TEXT_SHORT_TYPES
)

_RADICAL_TOKEN = re.compile(r"\\sqrt|sqrt\s*\(|√", re.I)


def is_coordinate_pair_contract(answer_contract: dict[str, Any] | None) -> bool:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    if str(ac.get("answer_shape", "")).strip() == "coordinate_pair":
        return True
    if str(ac.get("semantic_answer_shape", "")).strip() == "coordinate_pair":
        return True
    if str(ac.get("checker", "")).strip() == "coordinate_pair_checker":
        return True
    if str(ac.get("answer_equivalence", ac.get("equivalence_type", ""))).strip() == "coordinate_pair_equivalence":
        return True
    return answer_type_family(str(ac.get("answer_type", ""))) == "coordinate_pair"


def is_coordinate_pair_runtime_payload(payload: dict[str, Any]) -> bool:
    """Detect coordinate_pair grading from payload fields (not only embedded answer_contract)."""
    if not isinstance(payload, dict):
        return False
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    if is_coordinate_pair_contract(ac):
        return True
    if str(payload.get("checker") or payload.get("checker_type") or "").strip() == "coordinate_pair_checker":
        return True
    if str(payload.get("equivalence") or payload.get("equivalence_type") or "").strip() == "coordinate_pair_equivalence":
        return True
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    if (
        str(meta.get("presentation_mode", "")).strip() == "short_answer"
        and str(meta.get("semantic_answer_shape", "")).strip() == "coordinate_pair"
    ):
        return True
    if str(meta.get("presentation_mode", "")).strip() == "short_answer":
        from core.checkers.coordinate_pair_checker import parse_coordinate_pair_answer

        if parse_coordinate_pair_answer(meta.get("semantic_answer")) is not None:
            return True
    return False


def resolve_answer_contract_for_runtime(
    payload: dict[str, Any],
    *,
    skill_id: str = "",
) -> dict[str, Any]:
    """Merge answer_contract from payload, checker, equivalence, metadata, or problem_type spec."""
    if not isinstance(payload, dict):
        return {}
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    if is_coordinate_pair_contract(ac):
        return dict(ac)
    if answer_type_family(str(ac.get("answer_type", ""))) == "solution_set":
        return dict(ac)
    if is_coordinate_pair_runtime_payload(payload):
        merged = dict(ac)
        merged.setdefault("answer_type", "ordered_pair")
        merged.setdefault("answer_shape", "coordinate_pair")
        merged.setdefault("answer_equivalence", "coordinate_pair_equivalence")
        merged.setdefault("checker", "coordinate_pair_checker")
        return merged
    sid = str(skill_id or payload.get("skill_id", payload.get("skill", ""))).strip()
    pt = str(payload.get("problem_type_id", "")).strip()
    if sid and pt:
        from core.gencode.problem_type_spec import get_answer_contract, load_problem_type_spec

        spec = load_problem_type_spec(sid, pt, prefer="auto")
        if spec:
            return dict(get_answer_contract(spec))
    return dict(ac)


def refresh_runtime_question_session(payload: dict[str, Any], *, skill_id: str = "") -> dict[str, Any]:
    """Normalize practice session payload: contract resolution + coordinate_pair string answers."""
    if not isinstance(payload, dict):
        return payload
    out = dict(payload)
    sid = str(skill_id or out.get("skill_id", out.get("skill", ""))).strip()
    ac = resolve_answer_contract_for_runtime(out, skill_id=sid)
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
    if is_coordinate_pair_contract(ac) or is_coordinate_pair_runtime_payload(out):
        out = apply_coordinate_pair_runtime_fields(out, ac or {"answer_shape": "coordinate_pair"})
    return out


def format_coordinate_pair_display(value: Any) -> str:
    from core.checkers.coordinate_pair_checker import parse_coordinate_pair_answer

    parsed = parse_coordinate_pair_answer(value)
    if parsed is None:
        return ""
    x, y = parsed

    def _fmt_num(n: Any) -> str:
        if isinstance(n, Fraction):
            if n.denominator == 1:
                return str(n.numerator)
            return f"{float(n):.6g}"
        if isinstance(n, float) and n.is_integer():
            return str(int(n))
        return f"{n:.6g}"

    return f"({_fmt_num(x)},{_fmt_num(y)})"


def coerce_correct_answer(value: Any, answer_contract: dict[str, Any] | None = None) -> Any:
    """Preserve list/tuple/set; parse JSON-like list strings from session."""
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    coord_contract = is_coordinate_pair_contract(ac)

    if isinstance(value, (list, tuple)) and len(value) == 2 and coord_contract:
        text = format_coordinate_pair_display(value)
        return text or value
    if isinstance(value, set):
        return sorted(value)

    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return value

    if coord_contract:
        if format_coordinate_pair_display(text):
            return text

    family = answer_type_family(str(ac.get("answer_type", "")))
    if family == "solution_set" and text.startswith(("[", "(", "{")):
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, set):
                return sorted(parsed)
            if isinstance(parsed, (list, tuple)):
                return list(parsed)
        except Exception:
            pass
        return value

    if not coord_contract and family != "coordinate_pair" and text.startswith(("[", "(", "{")):
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, set):
                return sorted(parsed)
            if isinstance(parsed, (list, tuple)):
                return list(parsed)
        except Exception:
            pass
    return value


def apply_coordinate_pair_runtime_fields(payload: dict[str, Any], answer_contract: dict[str, Any]) -> dict[str, Any]:
    """Normalize coordinate_pair answers for session / practice feedback."""
    if not is_coordinate_pair_contract(answer_contract):
        return payload
    out = dict(payload)
    raw = out.get("correct_answer", out.get("answer"))
    canon = format_coordinate_pair_display(raw) or str(raw or "").strip()
    if canon:
        out["correct_answer"] = canon
        out["answer"] = canon
        out["display_answer"] = canon
    return out


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
    if canon in COORDINATE_PAIR_TYPES:
        return "coordinate_pair"
    if canon in TEXT_SHORT_TYPES:
        return "short_answer"
    return canon


def _is_text_short_numeric_string_contract(answer_contract: dict[str, Any], value: Any) -> bool:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    if str(ac.get("answer_type", "")).strip() != "text_short" and str(ac.get("answer_shape", "")).strip() != "text_short":
        return False
    if not isinstance(value, str):
        return False
    return bool(re.fullmatch(r"\s*[+-]?\d+\s*", value))


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
    if family == "coordinate_pair":
        text = format_coordinate_pair_display(value)
        return text or (str(value).strip() if value is not None else "")
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
    if family == "coordinate_pair":
        from core.checkers.coordinate_pair_checker import parse_coordinate_pair_answer

        if parse_coordinate_pair_answer(value) is not None:
            return True, ""
        return False, "coordinate_pair_invalid"
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
        "coordinate_pair": "coordinate_pair allows (x,y) string or equivalent formats",
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
    coerce_single_choice_contract(ac)
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
    elif family == "coordinate_pair" and raw_answer is not None:
        canon = normalize_correct_answer_for_contract(raw_answer, ac)
        if canon:
            out["correct_answer"] = canon
            out["answer"] = canon
            out["display_answer"] = canon
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
    ac = dict(ac)
    coerce_single_choice_contract(ac)
    pt = str(problem_type_id or payload.get("problem_type_id", "")).strip()
    raw_type = str(ac.get("answer_type", "")).strip()
    canon_type = canonical_answer_type(raw_type)
    blockers: list[str] = []

    raw_answer_value = payload.get("correct_answer", payload.get("answer"))
    if (
        raw_type
        and raw_type not in VALID_ANSWER_TYPES
        and canon_type not in VALID_ANSWER_TYPES
        and not _is_text_short_numeric_string_contract(ac, raw_answer_value)
    ):
        blockers.append(
            format_invalid_answer_type_error(
                problem_type_id=pt,
                answer_contract=ac,
                answer_value=raw_answer_value,
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
