# -*- coding: utf-8 -*-
"""Deterministic answer-arity helpers for practice UI runtime contract.

Single source of truth for field counts must come from structured payload
(``answer_contract.parts`` / MCQ choices / single-answer modes), never from
regex on question stem numbering.
"""

from __future__ import annotations

from typing import Any


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _contract_parts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    contract = _as_dict(payload.get("answer_contract"))
    parts = contract.get("parts")
    if isinstance(parts, list):
        return [p for p in parts if isinstance(p, dict)]
    return []


def resolve_multipart_fields(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Python port of templates/index.html ``resolveMultiPartFields``.

    Used by gates so renderer arity can be asserted without a browser.
    """
    parts = _contract_parts(payload)
    from_parts: list[dict[str, Any]] = []
    for index, part in enumerate(parts):
        key = str(part.get("key") or part.get("field_key") or "").strip()
        if not key:
            continue
        label = str(
            part.get("display_label")
            or part.get("label")
            or part.get("prompt")
            or key
            or f"欄位 {index + 1}"
        )
        from_parts.append(
            {
                "key": key,
                "field_key": key,
                "label": label,
                "prompt": label,
                "group_label": str(part.get("group_label") or ""),
                "input_type": str(part.get("input_type") or "text"),
                "choices": list(part.get("choices") or [])
                if isinstance(part.get("choices"), list)
                else [],
                "answer_order": part.get("answer_order", index),
            }
        )
    if from_parts:
        return from_parts

    subqs = payload.get("subquestions")
    if not isinstance(subqs, list):
        return []
    out: list[dict[str, Any]] = []
    for index, sq in enumerate(subqs):
        if not isinstance(sq, dict):
            continue
        key = str(sq.get("field_key") or sq.get("key") or sq.get("part") or "").strip()
        if not key:
            continue
        label = str(sq.get("prompt") or sq.get("label") or sq.get("part") or f"欄位 {index + 1}")
        out.append(
            {
                "key": key,
                "field_key": key,
                "label": label,
                "prompt": label,
                "answer_order": sq.get("answer_order", index),
            }
        )
    return out


def is_mcq_payload(payload: dict[str, Any]) -> bool:
    answer_type = str(
        payload.get("answer_type")
        or _as_dict(payload.get("answer_contract")).get("answer_type")
        or ""
    ).strip()
    if answer_type in {"single_choice", "multiple_choice", "mcq"}:
        return True
    mode = str(payload.get("presentation_mode") or "").strip()
    if mode == "single_choice":
        return True
    choices = payload.get("choices")
    return isinstance(choices, list) and len(choices) > 0


def expected_answer_field_count(payload: dict[str, Any]) -> int:
    """Declared student input arity from structured contract."""
    if is_mcq_payload(payload):
        return 1
    fields = resolve_multipart_fields(payload)
    if fields:
        return len(fields)
    return 1


def rendered_answer_field_count(payload: dict[str, Any]) -> int:
    """Fields the shared practice renderer would create.

    Matches ``renderSubquestionInputs`` / MCQ branch semantics:
    - MCQ → 1 selector (not text inputs)
    - multipart parts → N inputs
    - else → 1 legacy single input
    """
    if is_mcq_payload(payload):
        return 1
    fields = resolve_multipart_fields(payload)
    if fields:
        return len(fields)
    return 1


def checker_answer_count(payload: dict[str, Any]) -> int:
    """How many answer parts the checker contract expects."""
    if is_mcq_payload(payload):
        return 1
    parts = _contract_parts(payload)
    if parts:
        return len(parts)
    answer = payload.get("answer")
    if isinstance(answer, dict):
        nested = answer.get("parts")
        if isinstance(nested, dict) and nested:
            return len(nested)
        if answer and all(not isinstance(v, dict) for v in answer.values()):
            # Flat part map used as payload answer.
            if any(str(k).startswith("(") or str(k) in {"①", "②", "③", "④"} for k in answer):
                return len(answer)
            if len(answer) > 1 and all(
                str(k).startswith("(") or str(k).isdigit() for k in answer
            ):
                return len(answer)
    return 1


def generator_answer_count_from_matrix(matrix: dict[str, Any] | None) -> int:
    """Arity declared by domain matrix answer block (pre-wrapper)."""
    if not isinstance(matrix, dict):
        return 1
    if matrix.get("choices"):
        return 1
    answer = matrix.get("answer")
    if isinstance(answer, dict):
        parts = answer.get("parts")
        if isinstance(parts, dict) and parts:
            return len(parts)
        value = answer.get("value")
        if (
            isinstance(value, dict)
            and value
            and set(value.keys()) == {"parts"}
            and isinstance(value.get("parts"), dict)
        ):
            return len(value["parts"])
        if isinstance(value, dict) and value and all(not isinstance(v, dict) for v in value.values()):
            return len(value)
    return 1


def arity_status(
    *,
    expected: int,
    generator: int,
    wrapper: int,
    api: int,
    rendered: int,
    checker: int,
    is_mcq: bool = False,
) -> tuple[str, str]:
    """Return (status, reason) for audit rows."""
    counts = {
        "expected": expected,
        "generator": generator,
        "wrapper": wrapper,
        "api": api,
        "rendered": rendered,
        "checker": checker,
    }
    if is_mcq and expected == 1 and rendered == 1 and api == 1:
        if all(v == 1 for v in counts.values()):
            return "PASS", "mcq_single_selection"
        return "SCHEMA_MISMATCH", f"mcq_counts={counts}"

    if expected != rendered:
        if rendered == 1 and expected > 1:
            return "RENDERER_FALLBACK", f"expected={expected} rendered=1"
        return "ARITY_MISMATCH", f"expected={expected} rendered={rendered}"
    if expected != api or expected != wrapper or expected != generator:
        return "ARITY_MISMATCH", f"pipeline_counts={counts}"
    if expected != checker:
        return "CHECKER_MISMATCH", f"expected={expected} checker={checker}"
    if len({expected, generator, wrapper, api, rendered, checker}) != 1:
        return "SCHEMA_MISMATCH", f"counts={counts}"
    return "PASS", "arity_aligned"
