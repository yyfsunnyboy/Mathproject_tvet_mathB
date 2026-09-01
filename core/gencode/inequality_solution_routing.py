from __future__ import annotations

import re
from typing import Any

from core.gencode.answer_payload import (
    INTERVAL_TYPES,
    SOLUTION_SET_TYPES,
    answer_type_family,
    is_coordinate_pair_contract,
)

INEQUALITY_SOLUTION_CHECKERS = frozenset(
    {
        "interval_checker",
        "inequality_solution_checker",
    }
)
INEQUALITY_SOLUTION_EQUIV = frozenset(
    {
        "interval_set",
        "interval_equivalence",
        "inequality_solution_equivalence",
    }
)
INEQUALITY_SOLUTION_ANSWER_TYPES = INTERVAL_TYPES | frozenset(
    {
        "inequality",
        "inequality_solution",
        "real_solution_set",
        "union_of_intervals",
    }
)
_CHOICE_CHECKERS = frozenset(
    {
        "choice_label_checker",
        "choice_checker",
    }
)
_INCLUDE_TOKEN_RE = re.compile(
    r"inequality|interval_set|union_of_intervals|interval_or_union|"
    r"interval_interpretation|parameter_range|solve_inequality|"
    r"inequality_solution",
    re.I,
)
_EXCLUDE_TOKEN_RE = re.compile(
    r"integer_solution_count|ordered_pair|coordinate_pair|quadrant|"
    r"factor_quadratic|reverse_quadratic|histogram|choice",
    re.I,
)
_REL_HINT_RE = re.compile(
    r"[<>≤≥＜＞]|\\le|\\ge|\\lt|\\gt|∈|\\in|∪|\\cup|或|且|\band\b|\bor\b|"
    r"無解|空集|任意實數|所有實數|ℝ",
    re.I,
)
_HALF_OPEN_RE = re.compile(r"[\[\(]\s*[^,]+,\s*[^\]\)]+\s*[\]\)]")
_CLOSED_INTERVAL_RE = re.compile(r"\[\s*[^,]+,\s*[^]]+\s*\]")


def _blob(payload: dict[str, Any], ac: dict[str, Any]) -> str:
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    math_objects = meta.get("math_objects") or payload.get("math_objects") or ac.get("math_objects") or []
    if isinstance(math_objects, (list, tuple)):
        mo = " ".join(str(x) for x in math_objects)
    else:
        mo = str(math_objects or "")
    parts = [
        payload.get("problem_type_id", ""),
        payload.get("line_type", ""),
        payload.get("domain_operation", ""),
        payload.get("target_task", ""),
        payload.get("answer_shape", ""),
        ac.get("answer_shape", ""),
        ac.get("answer_semantics", ""),
        meta.get("problem_type_id", ""),
        meta.get("line_type", ""),
        meta.get("domain_operation", ""),
        meta.get("target_task", ""),
        mo,
    ]
    return " ".join(str(p or "") for p in parts)


def looks_like_relational_solution_text(text: object) -> bool:
    """True for inequality / union / membership / half-open forms.

    Bare `(a,b)` is intentionally False so coordinate pairs stay coordinates.
    """
    s = str(text or "").strip()
    if not s:
        return False
    if _REL_HINT_RE.search(s):
        return True
    if _CLOSED_INTERVAL_RE.search(s) or re.search(r"[\[\(][^,]+,[^\]]+[\)\]]", s) and (
        "[" in s or "]" in s
    ):
        return True
    if _HALF_OPEN_RE.search(s) and ("[" in s or "]" in s or "inf" in s.lower() or "∞" in s):
        return True
    compact = re.sub(r"\s+", "", s.lower())
    if compact in {"r", "ℝ", "∅", "empty", "emptyset", "{}", "無解", "空集合", "任意實數", "所有實數"}:
        return True
    if "(-inf,inf)" in compact or "(-∞,∞)" in s.replace(" ", ""):
        return True
    return False


def is_inequality_solution_context(
    payload: dict[str, Any] | None,
    answer_contract: dict[str, Any] | None = None,
    correct_answer: object = None,
) -> bool:
    """Whether grading should prefer the shared real-set checker.

    Never hijacks coordinate pairs, discrete integer solution sets, or choices.
    Does not treat a bare `(a,b)` as an interval without supporting metadata.
    """
    payload = payload if isinstance(payload, dict) else {}
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    if not ac:
        raw = payload.get("answer_contract")
        ac = dict(raw) if isinstance(raw, dict) else {}

    checker = str(
        ac.get("checker")
        or ac.get("checker_key")
        or payload.get("checker")
        or payload.get("checker_key")
        or payload.get("checker_type")
        or ""
    ).strip()
    family = answer_type_family(str(ac.get("answer_type") or payload.get("answer_type") or ""))

    if is_coordinate_pair_contract(ac):
        return False
    if checker == "coordinate_pair_checker":
        return False
    if family == "coordinate_pair":
        return False
    equiv = str(
        ac.get("answer_equivalence")
        or ac.get("equivalence_type")
        or payload.get("equivalence")
        or payload.get("equivalence_type")
        or ""
    ).strip()
    answer_type = str(ac.get("answer_type") or payload.get("answer_type") or "").strip()
    presentation = str(
        ac.get("presentation_mode") or payload.get("presentation_mode") or ""
    ).strip()

    if presentation == "single_choice" or family == "choice" or checker in _CHOICE_CHECKERS:
        return False
    if family in {"coordinate_pair", "drawing", "multi_part", "numeric"}:
        return False
    if family in SOLUTION_SET_TYPES or family == "solution_set":
        if checker in {"solution_set_checker", "set_checker", "unordered_set_checker"}:
            return False
        if equiv in {"unordered_solution_set", "set_equal"}:
            return False

    if checker in INEQUALITY_SOLUTION_CHECKERS:
        return True
    if equiv in INEQUALITY_SOLUTION_EQUIV:
        return True
    if answer_type in INEQUALITY_SOLUTION_ANSWER_TYPES or family == "interval":
        return True

    blob = _blob(payload, ac)
    if _EXCLUDE_TOKEN_RE.search(blob):
        return False
    if _INCLUDE_TOKEN_RE.search(blob):
        if checker in {
            "integer_checker",
            "numeric_checker",
            "rational_checker",
            "fraction_checker",
            "decimal_tolerance_checker",
            "coordinate_pair_checker",
            "solution_set_checker",
            "set_checker",
            "unordered_set_checker",
            "choice_label_checker",
            "free_response_drawing_checker",
            "multi_part_answer_checker",
        }:
            return False
        return True

    if looks_like_relational_solution_text(correct_answer):
        if checker in {"integer_checker", "numeric_checker", "coordinate_pair_checker"}:
            return False
        if family in {"numeric", "coordinate_pair", "choice"}:
            return False
        return True
    return False


def try_grade_inequality_solution(user_answer: object, correct_answer: object) -> bool | None:
    from core.checkers.inequality_solution_checker import check_inequality_solution_answer

    return check_inequality_solution_answer(user_answer, correct_answer)
