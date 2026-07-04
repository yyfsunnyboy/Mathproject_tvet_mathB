# -*- coding: utf-8 -*-
"""Canonical single-choice contract validation for V3 generate payloads."""

from __future__ import annotations

from typing import Any

from core.gencode.v3_error_codes import CHOICE_CONTRACT_INCOMPLETE
from core.gencode.choice_math_display import format_choice_math_display

MIN_SINGLE_CHOICE_COUNT = 2
MAX_SINGLE_CHOICE_COUNT = 8
_VALID_CHOICE_CHECKERS = frozenset({"choice_label_checker"})


def _payload_dict(payload: dict[str, Any] | None) -> dict[str, Any]:
    return payload if isinstance(payload, dict) else {}


def _answer_contract(payload: dict[str, Any]) -> dict[str, Any]:
    ac = payload.get("answer_contract")
    return ac if isinstance(ac, dict) else {}


def requires_choice_contract(payload: dict[str, Any]) -> bool:
    """Return True when payload must satisfy the single-choice contract."""
    p = _payload_dict(payload)
    mode = str(p.get("presentation_mode") or "").strip()
    if mode == "single_choice":
        return True
    ac = _answer_contract(p)
    if str(ac.get("presentation_mode") or "").strip() == "single_choice":
        return True
    ui = p.get("ui_contract")
    if isinstance(ui, dict) and str(ui.get("presentation_mode") or "").strip() == "single_choice":
        return True
    return False


def normalize_canonical_choices(choices: Any) -> list[dict[str, str]]:
    """Normalize choices to canonical [{key, label, text, value?}, ...].

    Accepts legacy shapes:
    - {"key": "A", "text": "..."}
    - {"label": "A", "text": "...", "value": "..."}
    - plain strings (assigned sequential A/B/C/...)
    """
    if not isinstance(choices, list) or not choices:
        return []

    normalized: list[dict[str, str]] = []
    for index, item in enumerate(choices):
        if isinstance(item, dict):
            key = str(item.get("key") or item.get("label") or "").strip()
            text = str(item.get("text") or item.get("value") or "").strip()
            value = str(item.get("value") or text or "").strip()
            if not key:
                key = chr(ord("A") + index)
            normalized.append(
                {
                    "key": key,
                    "label": key,
                    "text": text,
                    "value": value,
                    "display": str(
                        item.get("display") or format_choice_math_display(text)
                    ).strip(),
                }
            )
            continue
        text = str(item or "").strip()
        key = chr(ord("A") + index)
        normalized.append(
            {
                "key": key,
                "label": key,
                "text": text,
                "value": text,
                "display": format_choice_math_display(text),
            }
        )
    return normalized


def _resolve_checker(payload: dict[str, Any]) -> str:
    p = _payload_dict(payload)
    ac = _answer_contract(p)
    return str(
        p.get("checker_key")
        or p.get("checker")
        or ac.get("checker_key")
        or ac.get("checker")
        or ""
    ).strip()


def _resolve_answer(payload: dict[str, Any]) -> str:
    p = _payload_dict(payload)
    answer = p.get("answer")
    if answer is None:
        answer = p.get("correct_answer")
    return str(answer or "").strip()


def _answer_matches_choice(answer: str, choice: dict[str, str]) -> bool:
    if not answer:
        return False
    key = str(choice.get("key") or choice.get("label") or "").strip()
    text = str(choice.get("text") or "").strip()
    value = str(choice.get("value") or "").strip()
    answer_key = answer.strip("()[] .").upper()
    if key and answer_key == key.strip("()[] .").upper():
        return True
    if text and answer == text:
        return True
    if value and answer == value:
        return True
    return False


def validate_choice_contract(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate single-choice presentation contract.

    Returns:
        {
            "ok": bool,
            "error_code": str,
            "details": dict,
            "blockers": list[str],
            "choices": list[dict],
        }
    """
    p = _payload_dict(payload)
    if not requires_choice_contract(p):
        return {
            "ok": True,
            "error_code": "",
            "details": {"applicable": False},
            "blockers": [],
            "choices": [],
        }

    blockers: list[str] = []
    normalized = normalize_canonical_choices(p.get("choices"))
    details: dict[str, Any] = {
        "applicable": True,
        "choice_count": len(normalized),
    }

    if not normalized:
        blockers.append(f"{CHOICE_CONTRACT_INCOMPLETE}:choices_empty")

    if normalized:
        if len(normalized) < MIN_SINGLE_CHOICE_COUNT or len(normalized) > MAX_SINGLE_CHOICE_COUNT:
            blockers.append(f"{CHOICE_CONTRACT_INCOMPLETE}:invalid_choice_count")

        keys = [str(c.get("key") or "").strip() for c in normalized]
        if any(not key for key in keys):
            blockers.append(f"{CHOICE_CONTRACT_INCOMPLETE}:empty_choice_key")
        upper_keys = [key.strip("()[] .").upper() for key in keys if key]
        if len(upper_keys) != len(set(upper_keys)):
            blockers.append(f"{CHOICE_CONTRACT_INCOMPLETE}:duplicate_choice_keys")

        texts = [str(c.get("text") or "").strip() for c in normalized]
        if any(not text for text in texts):
            blockers.append(f"{CHOICE_CONTRACT_INCOMPLETE}:empty_choice_text")
        if len(texts) != len(set(texts)):
            blockers.append(f"{CHOICE_CONTRACT_INCOMPLETE}:duplicate_choice_text")

        answer = _resolve_answer(p)
        if not answer:
            blockers.append(f"{CHOICE_CONTRACT_INCOMPLETE}:answer_empty")
        else:
            matches = [choice for choice in normalized if _answer_matches_choice(answer, choice)]
            if not matches:
                blockers.append(f"{CHOICE_CONTRACT_INCOMPLETE}:answer_not_in_choices")
            elif len(matches) > 1:
                blockers.append(f"{CHOICE_CONTRACT_INCOMPLETE}:ambiguous_answer_mapping")

    question_text = str(p.get("question_text") or p.get("question") or "")
    if normalized:
        from core.gencode.v3_presentation_inference import question_text_has_embedded_abcd_choices

        if question_text_has_embedded_abcd_choices(question_text):
            blockers.append(f"{CHOICE_CONTRACT_INCOMPLETE}:choices_embedded_in_question_text")

    checker = _resolve_checker(p)
    if checker not in _VALID_CHOICE_CHECKERS:
        blockers.append(f"{CHOICE_CONTRACT_INCOMPLETE}:checker_not_dispatchable")

    ui = p.get("ui_contract")
    if isinstance(ui, dict):
        ui_mode = str(ui.get("presentation_mode") or ui.get("render_mode") or "").strip()
        if ui_mode and ui_mode not in {"single_choice", "multiple_choice"}:
            blockers.append(f"{CHOICE_CONTRACT_INCOMPLETE}:ui_contract_not_dispatchable")

    blockers = list(dict.fromkeys(blockers))
    ok = not blockers
    details["blockers"] = blockers
    return {
        "ok": ok,
        "error_code": "" if ok else CHOICE_CONTRACT_INCOMPLETE,
        "details": details,
        "blockers": blockers,
        "choices": normalized,
    }


def choice_contract_valid_from_spec(spec: dict[str, Any] | None) -> bool:
    """Return whether tracker/publish evidence marks choice contract as valid."""
    if not isinstance(spec, dict):
        return True
    if not requires_choice_contract(spec):
        return True
    return spec.get("choice_contract_valid") is True
