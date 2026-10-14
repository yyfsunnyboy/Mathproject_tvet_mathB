from __future__ import annotations

from typing import Any


_NUMERIC_CHECKERS = frozenset(
    {
        "integer_checker",
        "numeric_checker",
        "rational_checker",
        "fraction_checker",
        "decimal_tolerance_checker",
        "percentage_checker",
    }
)


def align_generated_answer_to_contract(payload: dict[str, Any]) -> dict[str, Any]:
    """Keep generated answer fields in the same shape as their answer contract.

    This is intentionally opt-in at component generation boundaries.  It repairs
    legacy generated artifacts whose display answer was rounded differently from
    the numeric oracle, or whose multipart semantic answer used grouped arrays
    while student submissions use part keys.
    """
    if not isinstance(payload, dict):
        return payload
    out = dict(payload)
    contract = out.get("answer_contract")
    if not isinstance(contract, dict):
        return out

    checker = str(contract.get("checker") or contract.get("checker_key") or "").strip()
    answer_type = str(contract.get("answer_type") or "").strip()

    if checker in _NUMERIC_CHECKERS:
        canonical = contract.get("canonical_answer")
        if canonical is None:
            canonical = contract.get("semantic_answer")
        if canonical is not None and str(canonical).strip():
            canonical_text = str(canonical).strip()
            out["answer"] = canonical_text
            out["correct_answer"] = canonical_text
            out["answer_type"] = answer_type or out.get("answer_type")
        return out

    if checker == "multi_part_answer_checker" or answer_type == "multi_part":
        parts = contract.get("parts") if isinstance(contract.get("parts"), list) else []
        keyed_answer: dict[str, Any] = {}
        for index, part in enumerate(parts):
            if not isinstance(part, dict):
                continue
            key = str(part.get("key") or part.get("field_key") or f"part_{index + 1}").strip()
            if key and part.get("expected_answer") is not None:
                keyed_answer[key] = part.get("expected_answer")
        if keyed_answer:
            out["answer"] = dict(keyed_answer)
            out["correct_answer"] = dict(keyed_answer)
            out["answer_type"] = "multi_part"
        return out

    return out
