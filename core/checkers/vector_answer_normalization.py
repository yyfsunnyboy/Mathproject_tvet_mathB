# -*- coding: utf-8 -*-
"""Keyboard-friendly normalization for vector-valued student answers.

Product rule: when the *expected* answer is vector-valued, students may type
plain keyboard forms (``BC``, ``a+b``, ``2a-b``) without LaTeX / arrow glyphs.
Scalar / algebra contexts must not coerce two-letter tokens into vectors.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

# Canonical directed-segment token used only inside the vector checker path.
_SEG_PREFIX = "dirseg:"

_VECTOR_SHAPES = frozenset(
    {
        "vector",
        "vector_expression",
        "directed_segment",
        "symbolic_vector",
        "plane_vector",
    }
)
_VECTOR_PART_KEYS = frozenset(
    {
        "vector",
        "simplified",
        "unit",
        "direction",
    }
)

# Domain operations whose free-response oracle is a plane-vector value.
DIRECTED_SEGMENT_ANSWER_OPS = frozenset(
    {
        "simplify_vector_path_expression",
    }
)
VECTOR_EXPRESSION_ANSWER_OPS = frozenset(
    {
        "express_linear_combination_from_givens",
        "express_named_vectors_in_given_basis",
        "express_section_point_vector",
        "compute_scaled_direction_vector",
        "compute_unit_vector",
        "compute_vector_linear_combination",
        "compute_vector_sum_difference",
        "compute_point_vectors_linear_combination",
        "compute_scalar_multiple_coordinates",
        "compute_directed_segment_and_magnitude",
        "compute_directed_segment_mixed_multipart",
        "compute_triangle_chain_and_perimeter",
        "solve_parallelogram_fourth_vertex",
    }
)


def answer_shape_for_domain_operation(domain_operation: object) -> str | None:
    op = str(domain_operation or "").strip()
    if op in DIRECTED_SEGMENT_ANSWER_OPS:
        return "directed_segment"
    if op in VECTOR_EXPRESSION_ANSWER_OPS:
        return "vector_expression"
    return None


_OVERRIGHTARROW = re.compile(
    r"(?:\\overrightarrow|overrightarrow)\s*\{([A-Za-z]{2})\}",
    re.IGNORECASE,
)
_VEC_BRACE_SEG = re.compile(r"(?:\\vec|vec)\s*\{([A-Za-z]{2})\}", re.IGNORECASE)
_VEC_PAREN_SEG = re.compile(r"vec\s*\(\s*([A-Za-z]{2})\s*\)", re.IGNORECASE)
_ARROW_PREFIX = re.compile(r"^->\s*([A-Za-z]{2})$")
_ARROW_SUFFIX = re.compile(r"^([A-Za-z]{2})\s*->$")
_BARE_SEG = re.compile(r"^([A-Za-z]{2})$")
_COORD_PAIR = re.compile(r"^\(\s*[^()]+\s*,\s*[^()]+\s*\)$")

_VEC_BRACE_SYM = re.compile(r"(?:\\vec|vec)\s*\{([A-Za-z])\}", re.IGNORECASE)
_VEC_PAREN_SYM = re.compile(r"vec\s*\(\s*([A-Za-z])\s*\)", re.IGNORECASE)
_OVERRIGHTARROW_IN_EXPR = re.compile(
    r"(?:\\overrightarrow|overrightarrow)\s*\{([A-Za-z]{2})\}",
    re.IGNORECASE,
)


def _strip_noise(text: object) -> str:
    s = unicodedata.normalize("NFKC", str(text or "")).strip()
    if not s:
        return ""
    return (
        s.replace("$", "")
        .replace("−", "-")
        .replace("－", "-")
        .replace("（", "(")
        .replace("）", ")")
        .replace(" ", "")
    )


def looks_like_coordinate_pair_answer(expected: object) -> bool:
    raw = _strip_noise(expected)
    return bool(raw and _COORD_PAIR.fullmatch(raw))


def _contract_blob(
    answer_contract: dict[str, Any] | None,
    payload: dict[str, Any] | None,
) -> dict[str, Any]:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    pl = payload if isinstance(payload, dict) else {}
    return {**pl, **ac}


def _shape_flags(blob: dict[str, Any]) -> set[str]:
    flags: set[str] = set()
    for key in (
        "answer_shape",
        "semantic_answer_shape",
        "answer_value_type",
        "semantic_answer_type",
        "canonical_answer_contract",
    ):
        val = str(blob.get(key) or "").strip().lower()
        if val:
            flags.add(val)
    equiv = str(
        blob.get("answer_equivalence")
        or blob.get("equivalence_type")
        or blob.get("equivalence")
        or ""
    ).strip().lower()
    if equiv:
        flags.add(equiv)
    return flags


def expected_is_directed_segment(expected: object) -> bool:
    """True when the oracle answer is a single directed-segment vector."""
    raw = _strip_noise(expected)
    if not raw:
        return False
    if _OVERRIGHTARROW.fullmatch(raw) or _VEC_BRACE_SEG.fullmatch(raw) or _VEC_PAREN_SEG.fullmatch(raw):
        return True
    if _ARROW_PREFIX.fullmatch(raw) or _ARROW_SUFFIX.fullmatch(raw):
        return True
    # Bare two-letter oracle (path simplifier sometimes stores canonical AD).
    # Point-label convention only: uppercase pairs. Never coerce lowercase algebra tokens.
    if _BARE_SEG.fullmatch(raw) and raw.isalpha() and raw.isupper():
        return True
    return False


def expected_is_symbolic_vector_expression(
    expected: object,
    *,
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> bool:
    """True when schema/expected indicates a basis / symbolic vector expression."""
    blob = _contract_blob(answer_contract, payload)
    flags = _shape_flags(blob)
    if flags & _VECTOR_SHAPES or any("vector" in f for f in flags):
        return True
    part_key = str(blob.get("key") or blob.get("field_key") or "").strip().lower()
    if part_key in _VECTOR_PART_KEYS:
        return True
    raw = _strip_noise(expected)
    if not raw:
        return False
    if re.search(r"(?:\\vec|vec)\s*\{[A-Za-z]\}", raw, flags=re.IGNORECASE):
        return True
    if re.search(r"vec\s*\(\s*[A-Za-z]\s*\)", raw, flags=re.IGNORECASE):
        return True
    return False


def is_vector_valued_answer_context(
    expected: object,
    *,
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> bool:
    """Gate: only enable keyboard→vector coercion for vector-valued oracles."""
    if looks_like_coordinate_pair_answer(expected):
        return False
    # Pure numeric / radical scalars must stay on the generic math path.
    raw = _strip_noise(expected)
    if raw and not re.search(r"[A-Za-z]", raw):
        return False
    if expected_is_directed_segment(expected):
        return True
    if expected_is_symbolic_vector_expression(
        expected, answer_contract=answer_contract, payload=payload
    ):
        return True
    blob = _contract_blob(answer_contract, payload)
    flags = _shape_flags(blob)
    if flags & _VECTOR_SHAPES or any("vector" in f for f in flags):
        # Schema says vector, but only if expected still looks symbolic/segment.
        if expected_is_directed_segment(expected) or re.search(r"[A-Za-z]", raw or ""):
            return True
    return False


def parse_directed_segment_token(text: object) -> str | None:
    """Return uppercase endpoint pair (e.g. ``BC``) or None if not a segment form."""
    raw = _strip_noise(text)
    if not raw:
        return None
    for pattern in (_OVERRIGHTARROW, _VEC_BRACE_SEG, _VEC_PAREN_SEG, _ARROW_PREFIX, _ARROW_SUFFIX):
        match = pattern.fullmatch(raw)
        if match:
            return match.group(1).upper()
    match = _BARE_SEG.fullmatch(raw)
    if match:
        return match.group(1).upper()
    return None


def canonicalize_directed_segment(text: object) -> str | None:
    seg = parse_directed_segment_token(text)
    if not seg:
        return None
    return f"{_SEG_PREFIX}{seg}"


def strip_symbolic_vector_markup(text: object) -> str:
    """Map ``\\vec{a}`` / ``vec(a)`` (and segment arrows inside expressions) to keyboard algebra."""
    raw = _strip_noise(text)
    if not raw:
        return ""

    def _sym(match: re.Match[str]) -> str:
        return match.group(1).lower()

    def _seg(match: re.Match[str]) -> str:
        # Inside a larger expression, keep two-letter tokens as identifiers.
        return match.group(1).upper()

    for _ in range(4):
        nxt = _VEC_BRACE_SYM.sub(_sym, raw)
        nxt = _VEC_PAREN_SYM.sub(_sym, nxt)
        nxt = _OVERRIGHTARROW_IN_EXPR.sub(_seg, nxt)
        nxt = _VEC_BRACE_SEG.sub(_seg, nxt)
        nxt = _VEC_PAREN_SEG.sub(_seg, nxt)
        if nxt == raw:
            break
        raw = nxt
    # Arrow keyboard sugar inside expressions: ->AB / AB->
    raw = re.sub(r"->([A-Za-z]{2})", lambda m: m.group(1).upper(), raw)
    raw = re.sub(r"([A-Za-z]{2})->", lambda m: m.group(1).upper(), raw)
    return raw


def vector_format_hint() -> str:
    return "可直接輸入 BC 表示向量 BC；可直接輸入 a+b 表示向量和。"


def try_check_vector_answer(
    user_answer: object,
    correct_answer: object,
    *,
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Return a debug-style result when vector context applies; else None.

    ``correct`` is True/False on success path. Parse failures set error_code but
    remain vector-aware so grading can show keyboard hints instead of a bare
    format rejection with no guidance.
    """
    if not is_vector_valued_answer_context(
        correct_answer, answer_contract=answer_contract, payload=payload
    ):
        return None

    ua_raw = str(user_answer or "").strip()
    ca_raw = str(correct_answer or "").strip()
    out: dict[str, Any] = {
        "correct": False,
        "vector_context": True,
        "normalized_user_expression": "",
        "normalized_correct_expression": "",
        "parser_error": "",
        "simplify_result": "",
        "error_code": "",
        "format_hint": vector_format_hint(),
    }
    if not ua_raw or not ca_raw:
        out["parser_error"] = "empty_answer"
        out["error_code"] = "ANSWER_PARSE_FAILED"
        return out

    # --- Directed segment path (BC / ->BC / \\overrightarrow{BC}) ---
    if expected_is_directed_segment(ca_raw):
        user_seg = canonicalize_directed_segment(ua_raw)
        correct_seg = canonicalize_directed_segment(ca_raw)
        out["normalized_user_expression"] = user_seg or _strip_noise(ua_raw)
        out["normalized_correct_expression"] = correct_seg or _strip_noise(ca_raw)
        if user_seg and correct_seg:
            out["correct"] = user_seg == correct_seg
            out["simplify_result"] = "directed_segment_identity" if out["correct"] else "directed_segment_mismatch"
            return out
        # Expected is a segment but student typed something else (maybe symbolic).
        # Fall through to symbolic compare when possible; otherwise format error.
        if not user_seg:
            # e.g. student typed a+b for expected AD → incorrect, not parse_error
            # unless it is totally unparseable junk.
            out["simplify_result"] = "directed_segment_unrecognized_student_form"
            out["correct"] = False
            # Keep as incorrect (not parse_error) when input has alnum content.
            if re.search(r"[A-Za-z0-9]", ua_raw):
                return out
            out["parser_error"] = "unrecognized_vector_form"
            out["error_code"] = "ANSWER_PARSE_FAILED"
            return out

    # --- Symbolic / basis vector expressions ---
    user_sym = strip_symbolic_vector_markup(ua_raw)
    correct_sym = strip_symbolic_vector_markup(ca_raw)
    out["normalized_user_expression"] = user_sym
    out["normalized_correct_expression"] = correct_sym
    if user_sym == correct_sym and user_sym:
        out["correct"] = True
        out["simplify_result"] = "vector_symbolic_normalized_identity"
        return out

    # Delegate algebraic equivalence on stripped keyboard forms.
    try:
        from core.checkers.expression_equivalence_checker import (
            normalize_math_expression,
            _parse_sympy,
            _numeric_equal,
        )
        from sympy import simplify

        user_expr = _parse_sympy(user_sym)
        correct_expr = _parse_sympy(correct_sym)
        diff = simplify(user_expr - correct_expr)
        out["simplify_result"] = str(diff)
        out["normalized_user_expression"] = normalize_math_expression(user_sym)
        out["normalized_correct_expression"] = normalize_math_expression(correct_sym)
        out["correct"] = bool(diff == 0 or _numeric_equal(user_expr, correct_expr))
        return out
    except Exception as ex:
        if normalize_fallback_equal(user_sym, correct_sym):
            out["correct"] = True
            out["simplify_result"] = "vector_symbolic_fallback_identity"
            return out
        out["parser_error"] = str(ex)
        out["error_code"] = "ANSWER_PARSE_FAILED"
        out["correct"] = False
        return out


def normalize_fallback_equal(left: str, right: str) -> bool:
    """Case-insensitive compacted equality after markup strip."""
    a = re.sub(r"\s+", "", str(left or "")).lower().replace("*", "")
    b = re.sub(r"\s+", "", str(right or "")).lower().replace("*", "")
    return bool(a) and a == b
