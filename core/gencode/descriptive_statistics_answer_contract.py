"""Canonical answer contract normalization for descriptive statistics domain."""

from __future__ import annotations

import math
import re
from fractions import Fraction
from typing import Any

from core.gencode.checker_registry import (
    CHECKER_CAPABILITIES,
    validate_answer_contract_capability,
)

NO_MODE_SENTINEL = "無眾數"

_RADICAL_PATTERN = re.compile(r"\\sqrt|sqrt\s*\(|√", re.IGNORECASE)
_RATIONAL_PATTERN = re.compile(r"^-?\d+\s*/\s*-?\d+$")
_INTEGER_PATTERN = re.compile(r"^-?\d+$")
_DECIMAL_PATTERN = re.compile(r"^-?\d+\.\d+$")

DESCRIPTIVE_ANSWER_SHAPES = frozenset(
    {
        "single_numeric",
        "single_expression",
        "multi_blank",
        "multi_part",
        "table_fill",
        "unordered_set",
        "text_short",
        "single_choice",
    }
)


class DescriptiveStatisticsContractError(ValueError):
    """Raised when descriptive-statistics matrix or payload contract is incomplete."""


def _answer_text(answer: Any) -> str:
    if answer is None:
        return ""
    if isinstance(answer, (list, tuple, set)):
        return ", ".join(str(item) for item in answer)
    if isinstance(answer, dict):
        return "; ".join(f"{k}={v}" for k, v in answer.items())
    return str(answer).strip()


def _is_exact_integer(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    text = _answer_text(value)
    if _INTEGER_PATTERN.match(text):
        return True
    try:
        num = float(text)
        return math.isfinite(num) and abs(num - round(num)) < 1e-9
    except (TypeError, ValueError):
        return False


def _is_exact_rational(value: Any) -> bool:
    text = _answer_text(value)
    if "/" in text or _RATIONAL_PATTERN.match(text):
        try:
            Fraction(text.replace(" ", ""))
            return True
        except (ValueError, ZeroDivisionError):
            return False
    return False


def _tolerance_from_policy(rounding_policy: dict[str, Any] | None) -> float | None:
    policy = rounding_policy if isinstance(rounding_policy, dict) else {}
    decimals = policy.get("decimal_places")
    if decimals is None:
        return None
    places = int(decimals)
    if places < 0:
        return None
    return 0.5 * (10 ** (-places))


def _requires_tolerance(rounding_policy: dict[str, Any] | None, answer: Any) -> bool:
    policy = rounding_policy if isinstance(rounding_policy, dict) else {}
    if policy.get("require_tolerance"):
        return True
    decimals = policy.get("decimal_places")
    if decimals is None:
        return False
    if bool(policy.get("prefer_integer")):
        return False
    text = _answer_text(answer)
    if _DECIMAL_PATTERN.match(text):
        return int(decimals) >= 0
    return False


def _checker_module(checker_key: str) -> str:
    cap = CHECKER_CAPABILITIES.get(checker_key) or {}
    module = str(cap.get("module") or "pipeline").strip()
    if module == "pipeline":
        return "core.gencode.runtime_skill_wrapper"
    if module.startswith("core."):
        return module
    return f"core.checkers.{checker_key}"


def normalize_answer_contract(
    answer: Any,
    expected_answer_shape: str,
    *,
    rounding_policy: dict[str, Any] | None = None,
    field_specs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build canonical runtime answer contract for descriptive statistics payloads."""
    shape = str(expected_answer_shape or "single_numeric").strip()
    if shape not in DESCRIPTIVE_ANSWER_SHAPES:
        raise DescriptiveStatisticsContractError(f"unsupported_answer_shape:{shape}")

    policy = dict(rounding_policy or {})
    text = _answer_text(answer)

    if shape == "text_short":
        canonical = NO_MODE_SENTINEL if not text else text
        contract = {
            "answer_shape": shape,
            "answer_type": "text_short",
            "checker_key": "text_short_checker",
            "checker": "text_short_checker",
            "equivalence_type": "exact_string",
            "answer_equivalence": "exact_string",
            "canonical_answer": canonical,
            "tolerance": None,
            "rounding_policy": policy,
            "field_specs": [],
            "presentation_mode": "short_answer",
        }
        return contract

    if shape == "unordered_set":
        if isinstance(answer, (list, tuple, set)):
            canonical = sorted({float(v) for v in answer})
            display = ", ".join(
                str(int(v)) if float(v).is_integer() else str(v) for v in canonical
            )
        else:
            display = text
            canonical = [
                float(part.strip())
                for part in re.split(r"[,、]", text)
                if part.strip()
            ]
        contract = {
            "answer_shape": shape,
            "answer_type": "solution_set",
            "checker_key": "unordered_set_checker",
            "checker": "unordered_set_checker",
            "equivalence_type": "unordered_solution_set",
            "answer_equivalence": "unordered_solution_set",
            "canonical_answer": canonical,
            "tolerance": None,
            "rounding_policy": policy,
            "field_specs": [],
            "presentation_mode": "short_answer",
            "semantic_answer": display,
        }
        return contract

    if shape in {"multi_blank", "table_fill", "multi_part"}:
        specs = [dict(item) for item in (field_specs or []) if isinstance(item, dict)]
        if not specs:
            raise DescriptiveStatisticsContractError("field_specs_required_for_multi_blank")
        keys = [str(spec.get("field_key") or spec.get("key") or "").strip() for spec in specs]
        if any(not key for key in keys):
            raise DescriptiveStatisticsContractError("field_specs_missing_field_key")
        if len(set(keys)) != len(keys):
            raise DescriptiveStatisticsContractError("field_specs_duplicate_field_key")
        parts: list[dict[str, Any]] = []
        canonical_map: dict[str, Any] = {}
        if isinstance(answer, dict):
            canonical_map = dict(answer)
        elif isinstance(answer, list):
            canonical_map = {
                str(spec.get("field_key") or spec.get("key") or f"part_{idx}"): value
                for idx, (spec, value) in enumerate(zip(specs, answer, strict=False))
            }
        for spec in specs:
            field_key = str(spec.get("field_key") or spec.get("key")).strip()
            expected = spec.get("expected_answer")
            if expected is None and field_key in canonical_map:
                expected = canonical_map[field_key]
            part_shape = str(spec.get("answer_shape") or "single_numeric").strip()
            if part_shape == "text_short" or str(spec.get("input_type") or "").strip() == "text":
                nested_shape = "text_short"
            else:
                nested_shape = "single_numeric"
            part_contract = normalize_answer_contract(
                expected,
                nested_shape,
                rounding_policy=spec.get("rounding_policy") or policy,
            )
            parts.append(
                {
                    "key": field_key,
                    "field_key": field_key,
                    "label": str(spec.get("label") or field_key),
                    "group_label": str(spec.get("group_label") or "").strip(),
                    "expected_answer": part_contract["canonical_answer"],
                    "checker": part_contract["checker_key"],
                    "checker_key": part_contract["checker_key"],
                    "equivalence_type": part_contract["equivalence_type"],
                    "answer_type": part_contract["answer_type"],
                    "input_type": str(spec.get("input_type") or "number"),
                }
            )
        ordered = [part["expected_answer"] for part in parts]
        enriched_specs: list[dict[str, Any]] = []
        for spec, part in zip(specs, parts, strict=False):
            enriched_specs.append(
                {
                    **spec,
                    "field_key": str(spec.get("field_key") or spec.get("key") or part["field_key"]),
                    "label": str(spec.get("label") or part["label"]),
                    "expected_answer": part["expected_answer"],
                    "checker": part["checker"],
                    "checker_key": part["checker_key"],
                    "equivalence_type": part["equivalence_type"],
                    "answer_type": part["answer_type"],
                }
            )
        response_mode = "table_fill" if shape == "table_fill" else ("multi_part" if shape == "multi_part" else "multi_blank")
        contract = {
            "answer_shape": shape,
            "answer_type": "multi_part",
            "checker_key": "multi_part_answer_checker",
            "checker": "multi_part_answer_checker",
            "equivalence_type": "multi_part_answer",
            "answer_equivalence": "multi_part_answer",
            "canonical_answer": ordered,
            "tolerance": None,
            "rounding_policy": policy,
            "field_specs": enriched_specs,
            "parts": parts,
            "presentation_mode": response_mode,
            "ui_contract": {
                "response_mode": response_mode,
                "text_input_enabled": True,
                "inline_table_inputs": shape == "table_fill",
            },
        }
        return contract

    if _RADICAL_PATTERN.search(text):
        contract = {
            "answer_shape": shape,
            "answer_type": "numeric_or_radical",
            "checker_key": "expression_equivalence_checker",
            "checker": "expression_equivalence_checker",
            "equivalence_type": "expression_equivalence",
            "answer_equivalence": "expression_equivalence",
            "canonical_answer": text,
            "tolerance": None,
            "rounding_policy": policy,
            "field_specs": [],
            "presentation_mode": "short_answer",
        }
        return contract

    if _is_exact_rational(answer):
        contract = {
            "answer_shape": shape,
            "answer_type": "rational",
            "checker_key": "rational_checker",
            "checker": "rational_checker",
            "equivalence_type": "rational_equivalent",
            "answer_equivalence": "rational_equivalent",
            "canonical_answer": text,
            "tolerance": None,
            "rounding_policy": policy,
            "field_specs": [],
            "presentation_mode": "short_answer",
        }
        return contract

    if _is_exact_integer(answer) and not bool(policy.get("require_tolerance")):
        canonical = int(round(float(text))) if text else answer
        contract = {
            "answer_shape": shape,
            "answer_type": "integer",
            "checker_key": "integer_checker",
            "checker": "integer_checker",
            "equivalence_type": "numeric_exact",
            "answer_equivalence": "numeric_exact",
            "canonical_answer": canonical,
            "tolerance": None,
            "rounding_policy": policy,
            "field_specs": [],
            "presentation_mode": "short_answer",
        }
        return contract

    if _requires_tolerance(policy, answer):
        tolerance = _tolerance_from_policy(policy)
        if tolerance is None:
            raise DescriptiveStatisticsContractError("rounding_policy_required_for_tolerance")
        contract = {
            "answer_shape": shape,
            "answer_type": "decimal",
            "checker_key": "decimal_tolerance_checker",
            "checker": "decimal_tolerance_checker",
            "equivalence_type": "decimal_tolerance",
            "answer_equivalence": "decimal_tolerance",
            "canonical_answer": text,
            "tolerance": tolerance,
            "rounding_policy": policy,
            "field_specs": [],
            "presentation_mode": "short_answer",
        }
        return contract

    contract = {
        "answer_shape": shape,
        "answer_type": "numeric",
        "checker_key": "numeric_checker",
        "checker": "numeric_checker",
        "equivalence_type": "numeric_exact",
        "answer_equivalence": "numeric_exact",
        "canonical_answer": text,
        "tolerance": None,
        "rounding_policy": policy,
        "field_specs": [],
        "presentation_mode": "short_answer",
    }
    return contract


def validate_contract_dispatchable(answer_contract: dict[str, Any]) -> list[str]:
    """Return blockers when checker contract is not runtime dispatchable."""
    result = validate_answer_contract_capability(answer_contract)
    return list(result.get("checker_contract_blockers") or [])


def build_scaffold_payload_meta(payload: dict[str, Any]) -> dict[str, Any]:
    """Derive scaffold payload_meta from a descriptive-statistics runtime payload."""
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    checker_key = str(ac.get("checker_key") or ac.get("checker") or payload.get("checker_key") or "").strip()
    equivalence_type = str(
        ac.get("equivalence_type") or ac.get("answer_equivalence") or payload.get("equivalence_type") or ""
    ).strip()
    presentation_mode = str(payload.get("presentation_mode") or ac.get("presentation_mode") or "short_answer")
    answer_type = str(payload.get("answer_type") or ac.get("answer_type") or "expression")
    return {
        "line_type": str(payload.get("domain_operation") or meta.get("selected_operation") or ""),
        "domain_operation": str(payload.get("domain_operation") or meta.get("selected_operation") or ""),
        "target_task": str(payload.get("problem_type_id") or meta.get("problem_type_id") or ""),
        "template_slot": str(payload.get("problem_type_id") or meta.get("problem_type_id") or ""),
        "presentation_mode": presentation_mode,
        "response_mode": str(ac.get("ui_contract", {}).get("response_mode") or presentation_mode),
        "answer_type": answer_type,
        "answer_value_type": answer_type,
        "problem_type_id": str(payload.get("problem_type_id") or meta.get("problem_type_id") or ""),
        "fixed_domain_key": str(payload.get("fixed_domain_key") or meta.get("fixed_domain_key") or ""),
        "checker_key": checker_key,
        "equivalence_type": equivalence_type,
        "checker_module": _checker_module(checker_key),
        "semantic_required_concepts": ("descriptive_statistics",),
        "math_objects": ("descriptive_statistics",),
        "taxonomy_path": "statistics:descriptive_statistics",
    }
