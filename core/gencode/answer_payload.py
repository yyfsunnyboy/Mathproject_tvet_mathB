from __future__ import annotations

import ast
import re
from fractions import Fraction
from typing import Any

from core.gencode.answer_contract_gate import coerce_single_choice_contract

SOLUTION_SET_TYPES = frozenset({"set", "solution_set", "integer_set", "number_set"})
INTERVAL_TYPES = frozenset(
    {
        "interval",
        "union_of_intervals",
        "interval_set",
        "inequality",
        "inequality_solution",
        "real_solution_set",
    }
)
CLASSIFICATION_TYPES = frozenset({"classification", "quadrant_label", "text_label", "category"})
NUMERIC_TYPES = frozenset({"numeric", "integer", "decimal", "number"})
RATIONAL_TYPES = frozenset({"fraction", "rational", "rational_fraction"})
RADICAL_TYPES = frozenset({"numeric_or_radical", "math_expression", "radical_number", "expression"})
CHOICE_TYPES = frozenset({"single_choice", "multi_choice", "choice", "choice_label"})
COORDINATE_PAIR_TYPES = frozenset({"coordinate_pair", "ordered_pair"})
EQUATION_TYPES = frozenset({"equation"})
LINEAR_EQUATION_SHAPES = frozenset({"linear_equation"})
TEXT_SHORT_TYPES = frozenset({"text", "text_short", "exact_string", "case_insensitive_string"})
MULTI_PART_TYPES = frozenset({"multi_part", "table_fill"})

ANSWER_TYPE_ALIASES: dict[str, str] = {
    "integer": "numeric",
    "decimal": "numeric",
    "number": "numeric",
    "number_set": "solution_set",
    "integer_set": "solution_set",
    "union_of_intervals": "interval",
    "inequality": "interval",
    "inequality_solution": "interval",
    "real_solution_set": "interval",
    "quadrant_label": "classification",
    "text_label": "classification",
    "category": "classification",
    "math_expression": "numeric_or_radical",
    "radical_number": "numeric_or_radical",
    "rational": "fraction",
    "rational_fraction": "fraction",
    "choice": "single_choice",
    "choice_label": "single_choice",
    "ordered_pair": "coordinate_pair",
    "text": "short_answer",
    "text_short": "short_answer",
    "exact_string": "short_answer",
    "case_insensitive_string": "short_answer",
    "string": "short_answer",
    "multi_part": "multi_part",
    "table_fill": "multi_part",
}

VALID_ANSWER_TYPES = frozenset(
    {
        "short_answer",
        "single_choice",
        "multi_choice",
        "numeric",
        "fraction",
        "rational",
        "rational_fraction",
        "expression",
        "set",
        "solution_set",
        "interval",
        "classification",
        "numeric_or_radical",
        "table",
        "manual_review",
        "equation",
        "multi_part",
        "short_answer",
        "drawing",
    }
    | SOLUTION_SET_TYPES
    | EQUATION_TYPES
    | MULTI_PART_TYPES
    | INTERVAL_TYPES
    | CLASSIFICATION_TYPES
    | NUMERIC_TYPES
    | RATIONAL_TYPES
    | RADICAL_TYPES
    | CHOICE_TYPES
    | COORDINATE_PAIR_TYPES
    | TEXT_SHORT_TYPES
)

_RADICAL_TOKEN = re.compile(r"\\sqrt|sqrt\s*\(|√", re.I)


def is_linear_equation_contract(answer_contract: dict[str, Any] | None) -> bool:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    if str(ac.get("answer_shape", "")).strip() in LINEAR_EQUATION_SHAPES:
        return True
    if str(ac.get("semantic_answer_shape", "")).strip() in LINEAR_EQUATION_SHAPES:
        return True
    if str(ac.get("checker", ac.get("checker_key", ""))).strip() == "linear_equation_equivalent_checker":
        return True
    equiv = str(ac.get("answer_equivalence", ac.get("equivalence_type", ""))).strip()
    if equiv == "linear_equation_equivalent":
        return True
    return answer_type_family(str(ac.get("answer_type", ""))) == "linear_equation"


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
    
    resolved = dict(ac)
    is_drawing = False
    try:
        from core.checkers.free_response_drawing_checker import is_drawing_answer_contract
        if is_drawing_answer_contract(ac, payload):
            is_drawing = True
    except Exception:
        pass

    if resolved.get("answer_type"):
        pass
    elif is_drawing:
        ans_type = str(ac.get("answer_type") or payload.get("answer_type") or "").strip()
        if ans_type != "string":
            resolved.setdefault("answer_type", "drawing")
            resolved.setdefault("answer_equivalence", "drawing_equivalence")
            resolved.setdefault("checker", "free_response_drawing_checker")
            
    if not resolved.get("answer_type"):
        if is_coordinate_pair_contract(ac):
            pass
        elif answer_type_family(str(ac.get("answer_type", ""))) == "solution_set":
            pass
        elif is_coordinate_pair_runtime_payload(payload):
            resolved.setdefault("answer_type", "ordered_pair")
            resolved.setdefault("answer_shape", "coordinate_pair")
            resolved.setdefault("answer_equivalence", "coordinate_pair_equivalence")
            resolved.setdefault("checker", "coordinate_pair_checker")
        else:
            sid = str(skill_id or payload.get("skill_id", payload.get("skill", ""))).strip()
            pt = str(payload.get("problem_type_id", "")).strip()
            if sid and pt:
                from core.gencode.problem_type_spec import get_answer_contract, load_problem_type_spec
                spec = load_problem_type_spec(sid, pt, prefer="auto")
                if spec:
                    resolved = dict(get_answer_contract(spec))
                    
    consistency_errors = validate_answer_contract_consistency(resolved)
    if consistency_errors:
        import logging
        logging.getLogger(__name__).warning(
            "[PRODUCTION CONTRACT INCONSISTENCY] question_uid=%s errors=%s resolved_contract=%s",
            payload.get("question_uid"), consistency_errors, resolved
        )
    return resolved


def refresh_runtime_question_session(payload: dict[str, Any], *, skill_id: str = "") -> dict[str, Any]:
    """Normalize practice session payload: contract resolution + coordinate_pair string answers."""
    if not isinstance(payload, dict):
        return payload
    out = dict(payload)
    sid = str(skill_id or out.get("skill_id", out.get("skill", ""))).strip()
    from core.gencode.table_question_contract import normalize_table_question_payload

    out = normalize_table_question_payload(out)
    from core.gencode.single_choice_payload_normalizer import normalize_single_choice_payload

    out = normalize_single_choice_payload(out)
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

    if not coord_contract and family not in {"coordinate_pair", "interval"} and text.startswith(("[", "(", "{")):
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, set):
                return sorted(parsed)
            if isinstance(parsed, (list, tuple)):
                # A 2-tuple string like "(2,7)" is an open interval in inequality
                # answers; do not collapse it into a Python list.
                if len(parsed) == 2:
                    return value
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
    if canon in EQUATION_TYPES:
        return "linear_equation"
    if canon in MULTI_PART_TYPES:
        return "multi_part"
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


def parse_rational_literal(value: Any) -> Fraction | None:
    """Parse JSON-safe rational literals without eval.

    Accepted examples: Fraction(3, 2), 5, "5", "-9/8", " 3 / 2 ", "+7/4".
    Floats are accepted only when they are exact integers.
    """
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, float):
        return Fraction(int(value), 1) if value.is_integer() else None
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    int_pat = r"[+-]?\d+"
    if re.fullmatch(int_pat, text):
        return Fraction(int(text), 1)
    if "/" in text:
        m = re.fullmatch(rf"\s*({int_pat})\s*/\s*({int_pat})\s*", text)
        if not m:
            return None
        numerator = int(m.group(1))
        denominator = int(m.group(2))
        if denominator == 0:
            return None
        return Fraction(numerator, denominator)
    return None


def parse_single_numeric(
    value: Any,
    *,
    require_integer: bool = False,
) -> tuple[float | None, str | None]:
    """Parse a single numeric student answer: integer, decimal, or fraction.

    Returns (numeric_value, error) where error is ``empty``, ``invalid``, or None.
    When ``require_integer`` is True (only for ``answer_type == "integer"``),
    decimal and non-integer fraction forms are rejected as ``invalid``.
    """
    if value is None:
        return None, "empty"
    if isinstance(value, bool):
        return None, "invalid"
    if isinstance(value, int):
        return float(value), None
    if isinstance(value, float):
        if require_integer and not value.is_integer():
            return None, "invalid"
        return value, None
    if isinstance(value, Fraction):
        if require_integer and value.denominator != 1:
            return None, "invalid"
        return float(value), None

    text = str(value).strip()
    if not text:
        return None, "empty"

    int_pat = r"[+-]?\d+"
    if re.fullmatch(int_pat, text):
        return float(int(text)), None

    if "/" in text:
        frac = parse_rational_literal(text)
        if frac is None:
            return None, "invalid"
        if require_integer and frac.denominator != 1:
            return None, "invalid"
        return float(frac), None

    if re.fullmatch(r"[+-]?\d+\.\d+", text):
        if require_integer:
            return None, "invalid"
        try:
            return float(text), None
        except ValueError:
            return None, "invalid"

    return None, "invalid"


def _to_exact_rational(value: Any) -> Fraction | None:
    frac = parse_rational_literal(value)
    if frac is not None:
        return frac
    if isinstance(value, bool) or value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        if re.fullmatch(r"[+-]?\d+\.\d+", text) or re.fullmatch(r"[+-]?\d+", text):
            return Fraction(text)
    except (ValueError, ZeroDivisionError):
        return None
    return None


def check_decimal_tolerance_answer(
    user_answer: Any,
    canonical_answer: Any,
    tolerance: float,
) -> dict[str, Any]:
    """Grade a decimal-tolerance contract using canonical_answer and tolerance."""
    user_val, user_err = parse_single_numeric(user_answer, require_integer=False)
    if user_err == "empty":
        return {"correct": False, "invalid_input": True, "result": "invalid input"}
    if user_err or user_val is None:
        return {"correct": False, "invalid_input": True, "result": "invalid input"}

    canon_val, canon_err = parse_single_numeric(canonical_answer, require_integer=False)
    if canon_err or canon_val is None:
        return {
            "correct": False,
            "system_error": True,
            "result": "批改系統錯誤：標準答案格式無效",
        }

    is_correct = abs(user_val - canon_val) <= float(tolerance) + 1e-12
    return {"correct": is_correct}


def grade_numeric_contract_answer(
    user_answer: Any,
    correct_answer: Any,
    answer_contract: dict[str, Any],
    *,
    checker: str = "",
) -> dict[str, Any]:
    """Dispatch numeric checker by answer_contract.checker_key."""
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    checker_key = str(
        checker or ac.get("checker_key") or ac.get("checker") or ""
    ).strip()
    answer_type = str(ac.get("answer_type") or "").strip()
    require_integer = answer_type == "integer"
    canonical = ac.get("canonical_answer", correct_answer)

    undef = {"無", "不存在", "斜率不存在", "m不存在"}
    user_token = str(user_answer or "").strip().replace(" ", "")
    canon_token = str(canonical or "").strip().replace(" ", "")
    if user_token in undef or canon_token in undef:
        normalized_user = "不存在" if user_token in undef else user_token
        normalized_canon = "不存在" if canon_token in undef else canon_token
        return {"correct": normalized_user == normalized_canon and bool(normalized_user)}

    if checker_key == "decimal_tolerance_checker":
        tolerance = ac.get("tolerance")
        if tolerance is None:
            return {
                "correct": False,
                "system_error": True,
                "result": "批改系統錯誤：缺少容許誤差設定",
            }
        try:
            tol = float(tolerance)
        except (TypeError, ValueError):
            return {
                "correct": False,
                "system_error": True,
                "result": "批改系統錯誤：容許誤差格式無效",
            }
        return check_decimal_tolerance_answer(user_answer, canonical, tol)

    user_val, user_err = parse_single_numeric(user_answer, require_integer=require_integer)
    if user_err == "empty":
        return {"correct": False, "invalid_input": True, "result": "invalid input"}
    if user_err or user_val is None:
        return {"correct": False, "invalid_input": True, "result": "invalid input"}

    if checker_key == "integer_checker":
        exp_val, exp_err = parse_single_numeric(canonical, require_integer=False)
        if exp_err or exp_val is None:
            exp_frac = parse_rational_literal(canonical)
            if exp_frac is None or exp_frac.denominator != 1:
                return {
                    "correct": False,
                    "system_error": True,
                    "result": "批改系統錯誤：整數標準答案格式無效",
                }
            exp_val = float(exp_frac.numerator)
        if require_integer and abs(user_val - round(user_val)) > 1e-9:
            return {"correct": False}
        return {"correct": abs(user_val - exp_val) < 1e-9}

    if checker_key in {"rational_checker", "fraction_checker"}:
        user_frac = _to_exact_rational(user_answer)
        exp_frac = _to_exact_rational(canonical)
        if user_frac is None or exp_frac is None:
            return {"correct": False, "invalid_input": True, "result": "invalid input"}
        return {"correct": user_frac == exp_frac}

    if checker_key == "numeric_checker" or checker_key:
        exp_val, exp_err = parse_single_numeric(canonical, require_integer=False)
        if exp_err or exp_val is None:
            exp_frac = _to_exact_rational(canonical)
            if exp_frac is not None:
                exp_val = float(exp_frac)
            else:
                return {
                    "correct": False,
                    "system_error": True,
                    "result": "批改系統錯誤：標準答案格式無效",
                }
        return {"correct": abs(user_val - exp_val) < 1e-9}

    return {
        "correct": False,
        "system_error": True,
        "result": "批改系統錯誤：未支援的數值 checker",
    }


def is_valid_rational_literal(value: Any) -> bool:
    return parse_rational_literal(value) is not None


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
        return is_valid_rational_literal(value), "fraction_invalid"
    if family == "coordinate_pair":
        from core.checkers.coordinate_pair_checker import parse_coordinate_pair_answer

        if parse_coordinate_pair_answer(value) is not None:
            return True, ""
        return False, "coordinate_pair_invalid"
    if family == "linear_equation" or is_linear_equation_contract(ac):
        from core.checkers.linear_equation_equivalent_checker import (
            canonicalize_linear_equation,
            check_linear_equation_equivalent_answer,
        )

        text = str(value).strip()
        if not text:
            return False, "linear_equation_empty"
        if canonicalize_linear_equation(text) is None:
            return False, "linear_equation_invalid"
        if not check_linear_equation_equivalent_answer(text, text):
            return False, "linear_equation_checker_self_test_failed"
        return True, ""
    if family == "multi_part":
        parts = ac.get("parts") if isinstance(ac.get("parts"), list) else []
        if not parts:
            return False, "multi_part_parts_missing"
        if not isinstance(value, (dict, list, tuple)):
            return False, "multi_part_answer_invalid"
        if isinstance(value, dict):
            for idx, part in enumerate(parts):
                if not isinstance(part, dict):
                    continue
                key = str(part.get("key") or part.get("id") or f"part_{idx + 1}").strip()
                if key not in value or value.get(key) in (None, ""):
                    return False, f"multi_part_missing:{key}"
        elif len(value) < len(parts):
            return False, "multi_part_missing"
        return True, ""
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
        "fraction": "rational/fraction allows Fraction, int, integer string, or a/b string",
        "short_answer": "short_answer allows non-empty string",
        "coordinate_pair": "coordinate_pair allows (x,y) string or equivalent formats",
        "linear_equation": "linear_equation allows parseable binary linear equation strings",
        "multi_part": "multi_part allows dict/list values matching answer_contract.parts",
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
            out["answer_type"] = canonical_answer_type(str(ac.get("answer_type")))
        checker_name = str(ac.get("checker", "")).strip() or str(ac.get("checker_key", "")).strip()
        if checker_name:
            out["checker"] = checker_name
            out["checker_type"] = checker_name
        equiv_type = str(ac.get("answer_equivalence", "")).strip() or str(ac.get("equivalence_type", "")).strip()
        if equiv_type:
            out["equivalence"] = equiv_type
        
        # Ensure ui_contract is populated and has presentation_mode
        ui = out.get("ui_contract") or ac.get("ui_contract")
        if not ui and ac.get("presentation_mode"):
            ui = {"presentation_mode": str(ac.get("presentation_mode"))}
        if ui:
            out["ui_contract"] = ui
            ac["ui_contract"] = ui
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
    from core.gencode.single_choice_payload_normalizer import normalize_single_choice_payload

    return normalize_single_choice_payload(out)


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


def validate_answer_contract_consistency(contract: dict[str, Any]) -> list[str]:
    """Validate answer contract consistency.
    
    Returns a list of error strings if any inconsistency is found.
    """
    if not isinstance(contract, dict):
        return ["contract_must_be_dict"]
        
    errors = []
    checker = str(contract.get("checker") or contract.get("checker_key") or "").strip()
    answer_type = str(contract.get("answer_type") or "").strip()
    answer_shape = str(contract.get("answer_shape") or "").strip()
    ui_contract = contract.get("ui_contract") or {}
    expected_drawing_spec = contract.get("expected_drawing_spec")
    
    # 1. answer_type=string 不得搭配 drawing checker
    if answer_type == "string" and checker == "free_response_drawing_checker":
        errors.append("INVALID_CONTRACT: answer_type=string must not use drawing checker")
        
    # 2. drawing checker 必須搭配 answer_type=drawing
    if checker == "free_response_drawing_checker" and answer_type != "drawing":
        errors.append("INVALID_CONTRACT: drawing checker must use answer_type=drawing")
        
    # 3. drawing checker 必須有 expected_drawing_spec
    if checker == "free_response_drawing_checker" and not expected_drawing_spec:
        errors.append("INVALID_CONTRACT: drawing checker must have expected_drawing_spec")
        
    # 4. answer_type=drawing 必須有 answer_shape=drawing
    if answer_type == "drawing" and answer_shape != "drawing":
        errors.append("INVALID_CONTRACT: answer_type=drawing must have answer_shape=drawing")
        
    # 5. drawing UI contract 不得套在文字題
    ui_response_mode = str(ui_contract.get("response_mode") or "").strip()
    if ui_response_mode == "drawing" and checker != "free_response_drawing_checker":
        errors.append("INVALID_CONTRACT: drawing UI contract must not be applied to non-drawing tasks")
        
    return errors
