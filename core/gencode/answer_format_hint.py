# -*- coding: utf-8 -*-
"""
core/gencode/answer_format_hint.py
===================================
Central module for answer_format_hint: a canonical string that describes the
expected runtime answer format for a problem type.

Design goals
------------
* `answer_format_hint` is the HIGHEST-PRIORITY source of truth for answer_contract.
* It is derived from source examples (source_has_choices, answer content, answer_fields).
* It CANNOT be overridden by problem_type_id prefix (integer_/rational_/…).
* It drives checker, equivalence_type, answer_type — not the other way around.
* Properties slots (vertex_form_properties, standard_to_vertex_properties) are NOT
  permanently locked to single_choice.  The actual format comes from the hint.

Supported hint values (canonical tokens)
-----------------------------------------
"A/B/C/D"         — multiple-choice with A/B/C/D labels
"integer"         — single integer value
"rational"        — fraction / rational number
"(h,k)"           — ordered coordinate pair, e.g. (1,-2)
"x=h"             — equation of a line / axis, e.g. x=-3
"向右 a, 向上 b"   — two-field translation description (horizontal, vertical)
"頂點=(h,k), 對稱軸=x=h"  — multi-field vertex + axis
"開口=向上"        — opening direction label
"text_short"      — free-form short text (last resort text fallback)
null / ""         — unknown; Phase 2 should flag as needs_review
"""
from __future__ import annotations

import re
from typing import Any

# ── Canonical hint tokens ─────────────────────────────────────────────────────

HINT_CHOICE = "A/B/C/D"
HINT_INTEGER = "integer"
HINT_RATIONAL = "rational"
HINT_COORDINATE = "(h,k)"
HINT_AXIS_TEXT = "x=h"
HINT_TRANSLATION_TEXT = "向右 a, 向上 b"
HINT_VERTEX_AXIS_TEXT = "頂點=(h,k), 對稱軸=x=h"
HINT_OPENING_DIRECTION = "開口=向上"
HINT_TEXT_SHORT = "text_short"
HINT_EXPRESSION = "expression"
HINT_INTERVAL = "interval"
HINT_SOLUTION_SET = "solution_set"
HINT_UNKNOWN = ""

# ── Answer-contract definitions keyed by hint ─────────────────────────────────

_HINT_TO_CONTRACT: dict[str, dict[str, Any]] = {
    HINT_CHOICE: {
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "answer_semantics": "choice_label",
        "answer_equivalence": "choice_label",
        "equivalence_type": "choice_label",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "presentation_mode": "single_choice",
        "choices_required": True,
        "frontend_render_choices": True,
        "accepted_formats": ["A", "B", "C", "D"],
    },
    HINT_INTEGER: {
        "answer_type": "integer",
        "answer_shape": "scalar",
        "answer_equivalence": "numeric_exact",
        "equivalence_type": "numeric_exact",
        "checker": "integer_checker",
        "checker_key": "integer_checker",
        "presentation_mode": "short_answer",
        "choices_required": False,
    },
    HINT_RATIONAL: {
        "answer_type": "rational",
        "answer_shape": "scalar",
        "answer_equivalence": "rational_equivalent",
        "equivalence_type": "rational_equivalent",
        "checker": "rational_checker",
        "checker_key": "rational_checker",
        "presentation_mode": "short_answer",
        "choices_required": False,
    },
    HINT_COORDINATE: {
        "answer_type": "coordinate_pair",
        "answer_shape": "coordinate_pair",
        "answer_semantics": "coordinate_pair",
        "answer_equivalence": "ordered_tuple_exact",
        "equivalence_type": "ordered_tuple_exact",
        "checker": "coordinate_pair_checker",
        "checker_key": "coordinate_pair_checker",
        "presentation_mode": "short_answer",
        "choices_required": False,
    },
    HINT_AXIS_TEXT: {
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "answer_semantics": "axis_equation",
        "answer_equivalence": "normalized_expression",
        "equivalence_type": "exact_string",
        "checker": "structured_text_checker",
        "checker_key": "structured_text_checker",
        "presentation_mode": "short_answer",
        "choices_required": False,
        "answer_fields": ["axis"],
    },
    HINT_TRANSLATION_TEXT: {
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "answer_semantics": "translation_description",
        "answer_equivalence": "normalized_text",
        "equivalence_type": "exact_string",
        "checker": "structured_text_checker",
        "checker_key": "structured_text_checker",
        "presentation_mode": "short_answer",
        "choices_required": False,
        "answer_fields": ["horizontal_shift", "vertical_shift"],
        "answer_separator": ",",
    },
    HINT_VERTEX_AXIS_TEXT: {
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "answer_semantics": "vertex_and_axis",
        "answer_equivalence": "fieldwise_equivalent",
        "equivalence_type": "exact_string",
        "checker": "structured_text_checker",
        "checker_key": "structured_text_checker",
        "presentation_mode": "short_answer",
        "choices_required": False,
        "answer_fields": ["vertex", "axis"],
        "answer_separator": ",",
    },
    HINT_OPENING_DIRECTION: {
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "answer_semantics": "opening_direction",
        "answer_equivalence": "normalized_text",
        "equivalence_type": "exact_string",
        "checker": "structured_text_checker",
        "checker_key": "structured_text_checker",
        "presentation_mode": "short_answer",
        "choices_required": False,
        "answer_fields": ["opening_direction"],
    },
    HINT_TEXT_SHORT: {
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "answer_equivalence": "exact_string",
        "equivalence_type": "exact_string",
        "checker": "text_short_checker",
        "checker_key": "text_short_checker",
        "presentation_mode": "short_answer",
        "choices_required": False,
    },
    HINT_EXPRESSION: {
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "answer_semantics": "algebraic_expression",
        "answer_equivalence": "algebraic_equivalent",
        "equivalence_type": "algebraic_equivalent",
        "checker": "expression_checker",
        "checker_key": "expression_checker",
        "presentation_mode": "short_answer",
        "choices_required": False,
        "accepted_formats": ["(x-5)(x+3)", "(2x-1)(x+5)", "2(x-1)(3x+2)"],
    },
    HINT_INTERVAL: {
        "answer_type": "interval",
        "answer_shape": "interval_or_union",
        "answer_semantics": "interval_union",
        "answer_equivalence": "interval_equivalence",
        "equivalence_type": "interval_equivalence",
        "checker": "interval_checker",
        "checker_key": "interval_checker",
        "presentation_mode": "short_answer",
        "choices_required": False,
        "accepted_formats": ["x<-2 or x>5", "-2<x<5", "x<=-2 or x>=5"],
    },
    HINT_SOLUTION_SET: {
        "answer_type": "solution_set",
        "answer_shape": "unordered_set",
        "answer_equivalence": "unordered_solution_set",
        "equivalence_type": "unordered_solution_set",
        "checker": "solution_set_checker",
        "checker_key": "solution_set_checker",
        "presentation_mode": "short_answer",
        "choices_required": False,
        "accepted_formats": ["-3, 7", "7, -3", "{-3, 7}", "k=-3 或 k=7", "-3 或 7"],
    },
}

# answer_fields → canonical hint (when hint is absent but fields give evidence)
_FIELDS_TO_HINT: dict[str, str] = {
    "choice_label":       HINT_CHOICE,
    "vertex":             HINT_COORDINATE,
    "coordinate_pair":    HINT_COORDINATE,
    "coordinate":         HINT_COORDINATE,
    "ordered_pair":       HINT_COORDINATE,
    "axis":               HINT_AXIS_TEXT,
    "horizontal_shift":   HINT_TRANSLATION_TEXT,
    "vertical_shift":     HINT_TRANSLATION_TEXT,
    "opening_direction":  HINT_OPENING_DIRECTION,
}

# Regex patterns for auto-detecting hint from answer text samples
_COORD_RE = re.compile(r"^\s*[（(]\s*-?\d+\s*[，,]\s*-?\d+\s*[）)]\s*$")
_AXIS_RE  = re.compile(r"^\s*x\s*=\s*-?\d+\s*$", re.IGNORECASE)
_CHOICE_LABEL_RE = re.compile(r"^\s*[ABCD]\s*$")
_INTEGER_RE = re.compile(r"^\s*-?\d+\s*$")
_RATIONAL_RE = re.compile(r"^\s*-?\d+\s*/\s*\d+\s*$")
_FACTOR_RE = re.compile(r"\(.*?\)\s*\(.*?\)")
_TRANSLATION_RE = re.compile(r"向[左右][^，,]*[，,].*向[上下]")
_OPENING_RE = re.compile(r"(開口|開口方向).*[向]?(上|下)")


def infer_answer_format_hint(spec: dict[str, Any]) -> str:
    """Infer the canonical answer_format_hint from a problem_type spec.

    Priority order (highest first):
      1. Explicit `answer_format_hint` already in spec
      2. source_has_choices / choices_count in answer_contract
      3. answer_fields  
      4. answer_contract.answer_semantics / answer_shape
      5. answer text sample patterns (from source answers)
      6. Return HINT_UNKNOWN if truly ambiguous
    """
    hint = str(spec.get("answer_format_hint") or "").strip()
    if hint and hint != HINT_UNKNOWN:
        return hint

    ac = spec.get("answer_contract") if isinstance(spec.get("answer_contract"), dict) else {}

    # 2. Choices evidence
    if ac.get("source_has_choices") or ac.get("choices_required") or \
       (ac.get("choice_count") and int(ac.get("choice_count") or 0) > 0):
        return HINT_CHOICE
    if ac.get("answer_type") in {"single_choice", "choice", "choice_label"} or \
       ac.get("presentation_mode") == "single_choice":
        return HINT_CHOICE

    # 3. answer_fields
    fields = list(ac.get("answer_fields") or spec.get("answer_fields") or [])
    for field in fields:
        candidate = _FIELDS_TO_HINT.get(str(field or "").strip().lower())
        if candidate:
            return candidate

    # 4. answer_semantics / answer_shape
    semantics = str(
        ac.get("answer_semantics") or ac.get("answer_shape") or
        spec.get("answer_semantics") or ""
    ).strip().lower()
    if "coordinate_pair" in semantics or "ordered_pair" in semantics or "vertex" in semantics:
        return HINT_COORDINATE
    if "translation" in semantics:
        return HINT_TRANSLATION_TEXT
    if "axis" in semantics:
        return HINT_AXIS_TEXT
    if "opening" in semantics or "direction" in semantics:
        return HINT_OPENING_DIRECTION

    # 5. answer_type fallback — ONLY for reliable non-numeric types.
    # integer/rational/numeric are value-type prefix artifacts and must NOT
    # automatically become a hint; they should fall through to HINT_UNKNOWN
    # so that slot-based canonicalization can take over.
    at = str(ac.get("answer_type", "")).strip().lower()
    if at in {"single_choice", "choice"}:
        return HINT_CHOICE
    if at == "coordinate_pair":
        return HINT_COORDINATE
    if at in {"text_short", "short_answer", "text"}:
        return HINT_TEXT_SHORT
    if at == "expression":
        return HINT_EXPRESSION
    if at == "interval":
        return HINT_INTERVAL
    if at in {"solution_set", "set"}:
        return HINT_SOLUTION_SET
    # integer / rational / numeric: do NOT map to a hint here.
    # These are unreliable when derived from a typed-prefix problem_type_id.
    # The caller should fall through to slot-based or marker-based inference.

    return HINT_UNKNOWN


def infer_answer_format_hint_from_answers(sample_answers: list[str]) -> str:
    """Guess hint by looking at a batch of source answer strings.

    Only used when no other evidence is available.
    """
    if not sample_answers:
        return HINT_UNKNOWN
    votes: dict[str, int] = {}

    for raw in sample_answers:
        ans = str(raw or "").strip()
        if not ans:
            continue
        if _CHOICE_LABEL_RE.match(ans):
            votes[HINT_CHOICE] = votes.get(HINT_CHOICE, 0) + 1
        elif _COORD_RE.match(ans):
            votes[HINT_COORDINATE] = votes.get(HINT_COORDINATE, 0) + 1
        elif _AXIS_RE.match(ans):
            votes[HINT_AXIS_TEXT] = votes.get(HINT_AXIS_TEXT, 0) + 1
        elif _TRANSLATION_RE.search(ans):
            votes[HINT_TRANSLATION_TEXT] = votes.get(HINT_TRANSLATION_TEXT, 0) + 1
        elif _OPENING_RE.search(ans):
            votes[HINT_OPENING_DIRECTION] = votes.get(HINT_OPENING_DIRECTION, 0) + 1
        elif _INTEGER_RE.match(ans):
            votes[HINT_INTEGER] = votes.get(HINT_INTEGER, 0) + 1
        elif _RATIONAL_RE.match(ans):
            votes[HINT_RATIONAL] = votes.get(HINT_RATIONAL, 0) + 1
        elif _FACTOR_RE.search(ans):
            votes[HINT_EXPRESSION] = votes.get(HINT_EXPRESSION, 0) + 1
        elif re.search(r"x\s*[<>≤≥=]", ans) or re.search(r"<\s*x\s*<", ans):
            votes[HINT_INTERVAL] = votes.get(HINT_INTERVAL, 0) + 1
        elif "," in ans or "或" in ans:
            votes[HINT_SOLUTION_SET] = votes.get(HINT_SOLUTION_SET, 0) + 1
        else:
            votes[HINT_TEXT_SHORT] = votes.get(HINT_TEXT_SHORT, 0) + 1

    if not votes:
        return HINT_UNKNOWN
    # Majority vote; ties broken by priority order
    return max(votes, key=lambda h: votes[h])


def answer_contract_from_hint(
    hint: str,
    *,
    existing_ac: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the canonical answer_contract dict for a given hint.

    Merges with `existing_ac` but the hint-derived fields always win.
    """
    template = _HINT_TO_CONTRACT.get(hint)
    if not template:
        # Unknown / empty hint — preserve existing or return empty
        if isinstance(existing_ac, dict) and existing_ac:
            return dict(existing_ac)
        return {}
    base = dict(existing_ac or {})
    base.update(template)
    return base


def enrich_spec_with_answer_format_hint(spec: dict[str, Any]) -> dict[str, Any]:
    """Add / refresh `answer_format_hint`, `answer_fields`, `answer_separator`
    in a spec copy.  Does NOT overwrite an explicit hint already in the spec.
    """
    out = dict(spec)
    existing_hint = str(spec.get("answer_format_hint") or "").strip()
    hint = existing_hint if (existing_hint and existing_hint != HINT_UNKNOWN) else infer_answer_format_hint(spec)
    out["answer_format_hint"] = hint

    contract_template = _HINT_TO_CONTRACT.get(hint, {})
    if "answer_fields" in contract_template and not spec.get("answer_fields"):
        out["answer_fields"] = contract_template["answer_fields"]
    if "answer_separator" in contract_template and not spec.get("answer_separator"):
        out["answer_separator"] = contract_template["answer_separator"]
    return out


def answer_contract_from_spec_hint(spec: dict[str, Any]) -> dict[str, Any] | None:
    """Return answer_contract derived from spec's answer_format_hint, or None
    if hint is unknown/missing (caller should fall through to next priority)."""
    hint = str(spec.get("answer_format_hint") or "").strip()
    if not hint or hint == HINT_UNKNOWN:
        # Try to infer
        hint = infer_answer_format_hint(spec)
    if not hint or hint == HINT_UNKNOWN:
        return None
    existing_ac = spec.get("answer_contract") if isinstance(spec.get("answer_contract"), dict) else {}
    return answer_contract_from_hint(hint, existing_ac=existing_ac)


def naming_warning_if_prefix_contract_mismatch(
    problem_type_id: str,
    hint: str,
) -> str | None:
    """Return a naming warning token when the value-type prefix contradicts the hint."""
    if not problem_type_id or not hint:
        return None
    pt = str(problem_type_id).strip().lower()
    numeric_prefixes = ("integer_", "rational_", "numeric_")
    has_numeric_prefix = any(pt.startswith(p) for p in numeric_prefixes)
    if has_numeric_prefix and hint not in {HINT_INTEGER, HINT_RATIONAL, HINT_UNKNOWN}:
        return f"naming_warning:numeric_prefix_but_hint_is_{hint.replace(' ', '_')}"
    return None


# Static answer-shape examples for question_text suffix (SOP §4.3.6).
# Must NOT use runtime correct_answer — only contract shape.
# Quadratic-inequality family uses one composite decoy (no per-seed answer leak).
QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE = "任意實數/無解/ -1<x<3"
QUADRATIC_INEQUALITY_SPECIAL_CASE_HINT_EXAMPLE = QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE
QUADRATIC_INEQUALITY_PARAMETER_RANGE_HINT_EXAMPLE = QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE
_QUADRATIC_INEQUALITY_HINT_REASONS = frozenset({
    "quadratic_inequality_interval_solution",
    "quadratic_inequality_parameter_range",
    "quadratic_inequality_special_case",
})
_PARAMETER_RANGE_HINT_DECOYS = frozenset({"m>1", "k<-2", "m>=1", "k<=-2"})
_SPECIAL_CASE_LABEL_ANSWERS = frozenset({"無解", "任意实数", "任意實數", "无解"})
_LINEAR_EQUATION_DEFAULT_HINT = "（請輸入直線方程式，例如 $3x - y - 1 = 0$ 或 $y = 3x - 1$）"


def _is_linear_equation_contract(ac: dict[str, Any]) -> bool:
    checker = str(ac.get("checker") or ac.get("checker_key") or "").strip()
    answer_type = str(ac.get("answer_type") or "").strip().lower()
    answer_shape = str(ac.get("answer_shape") or "").strip().lower()
    return checker == "linear_equation_equivalent_checker" or (
        answer_type == "equation" and answer_shape == "linear_equation"
    )


def _latex_wrap_equation(expr: str) -> str:
    s = str(expr or "").strip()
    if not s:
        return s
    if s.startswith("$") and s.endswith("$"):
        return s
    return f"${s}$"


def _build_linear_equation_format_suffix(ac: dict[str, Any]) -> str:
    formats = [str(x).strip() for x in (ac.get("accepted_formats") or []) if str(x).strip()]
    if formats:
        examples = "、".join(_latex_wrap_equation(f) for f in formats[:3])
        return f"（可輸入等價方程式，例如 {examples}）"
    return _LINEAR_EQUATION_DEFAULT_HINT

_CONTRACT_SHAPE_EXAMPLES: dict[str, str] = {
    "integer_checker": "5",
    "numeric_checker": "5",
    "rational_checker": "-3/4",
    "fraction_checker": "-3/4",
    "expression_checker": "(x-2)(x+3)",
    "expression_equivalence_checker": "(x-2)(x+3)",
    "coordinate_pair_checker": "(1,-2)",
    "structured_text_checker": "x=3",
    "text_short_checker": "向上",
    "text_checker": "向上",
    "solution_set_checker": "-3, 7",
    "interval_checker": "x<-2 or x>5",
    "inequality_solution_checker": "x<-2 or x>5",
    "choice_label_checker": "",
}


def answer_format_example_for_contract(answer_contract: dict[str, Any] | None) -> str:
    """Return a static, contract-shaped answer example for UI suffix hints."""
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    if _is_linear_equation_contract(ac):
        return ""
    reason = str(ac.get("checker_selection_reason") or "").strip()
    if reason in _QUADRATIC_INEQUALITY_HINT_REASONS:
        return QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE

    semantics = str(ac.get("answer_semantics") or "").strip()
    is_special_case_inequality = (
        semantics == "special_case_solution_label"
        or reason == "quadratic_inequality_special_case"
    )
    if is_special_case_inequality:
        return QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE

    is_parameter_range = (
        semantics == "parameter_range"
        or reason == "quadratic_inequality_parameter_range"
    )
    if is_parameter_range:
        return QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE

    explicit = str(ac.get("answer_format_example") or "").strip()
    if explicit in _SPECIAL_CASE_LABEL_ANSWERS:
        return QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE
    if explicit in _PARAMETER_RANGE_HINT_DECOYS:
        return QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE
    if explicit:
        return explicit
    checker = str(ac.get("checker") or ac.get("checker_key") or "").strip()
    if checker and checker in _CONTRACT_SHAPE_EXAMPLES:
        return _CONTRACT_SHAPE_EXAMPLES[checker]

    hint = str(ac.get("answer_format_hint") or "").strip()
    if hint == HINT_INTEGER:
        return _CONTRACT_SHAPE_EXAMPLES["integer_checker"]
    if hint == HINT_RATIONAL:
        return _CONTRACT_SHAPE_EXAMPLES["rational_checker"]
    if hint == HINT_COORDINATE:
        return _CONTRACT_SHAPE_EXAMPLES["coordinate_pair_checker"]
    if hint == HINT_CHOICE:
        return ""

    answer_type = str(ac.get("answer_type") or "").strip().lower()
    if answer_type in {"integer", "numeric", "number", "decimal"}:
        return _CONTRACT_SHAPE_EXAMPLES["integer_checker"]
    if answer_type in {"rational", "fraction"}:
        return _CONTRACT_SHAPE_EXAMPLES["rational_checker"]
    if answer_type in {"coordinate_pair", "ordered_pair"}:
        return _CONTRACT_SHAPE_EXAMPLES["coordinate_pair_checker"]
    if answer_type in {"text_short", "short_answer", "text"}:
        return _CONTRACT_SHAPE_EXAMPLES["text_short_checker"]
    if answer_type == "expression":
        return _CONTRACT_SHAPE_EXAMPLES["expression_checker"]
    if answer_type == "interval":
        return _CONTRACT_SHAPE_EXAMPLES["interval_checker"]
    if answer_type == "equation":
        return ""
    if hint == HINT_EXPRESSION:
        return _CONTRACT_SHAPE_EXAMPLES["expression_checker"]
    if hint == HINT_INTERVAL:
        return _CONTRACT_SHAPE_EXAMPLES["interval_checker"]
    return _CONTRACT_SHAPE_EXAMPLES.get(checker, "5")


def build_answer_format_suffix(answer_contract: dict[str, Any] | None) -> str:
    """Build the Chinese answer-format suffix from contract shape, not runtime answer."""
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    if _is_linear_equation_contract(ac):
        return _build_linear_equation_format_suffix(ac)
    example = answer_format_example_for_contract(answer_contract)
    if not example:
        return ""
    return f"（答案範例：{example}）"
