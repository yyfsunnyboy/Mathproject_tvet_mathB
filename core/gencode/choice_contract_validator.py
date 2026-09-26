# -*- coding: utf-8 -*-
"""Canonical single-choice contract validation for V3 generate payloads."""

from __future__ import annotations

import re
from typing import Any

from core.gencode.v3_error_codes import CHOICE_CONTRACT_INCOMPLETE
from core.gencode.choice_math_display import format_choice_math_display

MIN_SINGLE_CHOICE_COUNT = 2
MAX_SINGLE_CHOICE_COUNT = 8
VOCATIONAL_MC_CHOICE_COUNT = 4
_VALID_CHOICE_CHECKERS = frozenset({"choice_label_checker"})
_TECHNICAL_SUFFIX_RE = re.compile(r"_+\d+$")
_LATEX_FRAC_RE = re.compile(r"(-?)\\frac\{(-?\d+)\}\{(-?\d+)\}")
_LATEX_SQRT_RE = re.compile(r"\\sqrt\{([^}]+)\}")


def plainify_math_token(token: str) -> str:
    """Convert common classroom LaTeX tokens into sympy-friendly plain text."""
    text = str(token or "").strip()
    if not text:
        return text
    text = text.replace(r"\,", "").replace(r"\ ", "").replace(" ", "")
    text = text.replace(r"\left", "").replace(r"\right", "")
    text = _LATEX_FRAC_RE.sub(r"(\1\2)/(\3)", text)
    text = _LATEX_SQRT_RE.sub(r"sqrt(\1)", text)
    text = text.replace(r"\sqrt", "sqrt")
    return text


def infer_choice_answer_shape(text: Any) -> str:
    """Classify a choice into a coarse semantic answer shape for MCQ gating."""
    raw = str(text or "").strip()
    if not raw:
        return "empty"
    cleaned = raw.replace("$", "").replace(r"\(", "").replace(r"\)", "").strip()
    cleaned_cf = cleaned.casefold()
    if "π" in cleaned or r"\pi" in cleaned or re.search(r"(?<![a-z])pi(?![a-z])", cleaned_cf):
        return "area_or_pi"
    if "=" in cleaned and re.search(r"[xy]", cleaned_cf):
        return "equation"
    if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", cleaned.replace(" ", "")):
        return "number"
    if re.search(r"[\(\[]\s*[^,]+,\s*[^)\]]+\s*[\)\]]", cleaned):
        return "coordinate"
    # Classification labels / intervals / short Chinese answers.
    if re.search(r"[\u4e00-\u9fff]", cleaned) or cleaned_cf in {
        "相離", "相切", "相交", "圓內", "圓外", "圓上",
    }:
        return "classification"
    if any(tok in cleaned for tok in ("<", ">", "≤", "≥", r"\le", r"\ge", "k")):
        return "interval_or_param"
    return "expression"


def validate_choice_answer_shapes(payload: dict[str, Any]) -> list[str]:
    """Reject MCQ packs whose distractors do not share the correct answer shape."""
    choices = normalize_canonical_choices(payload.get("choices"))
    if len(choices) < 2:
        return []
    expected = str(
        payload.get("expected_answer_shape")
        or (_answer_contract(payload).get("answer_shape") if isinstance(_answer_contract(payload), dict) else "")
        or payload.get("choice_answer_shape")
        or ""
    ).strip()
    semantic = str(
        payload.get("semantic_answer")
        or payload.get("canonical_answer")
        or payload.get("display_answer")
        or ""
    ).strip()
    # Prefer explicit metadata; else infer from semantic / correct choice text.
    if not expected:
        if semantic and semantic.upper() not in {"A", "B", "C", "D"}:
            expected = infer_choice_answer_shape(semantic)
        else:
            answer = _resolve_answer(payload)
            for choice in choices:
                if _answer_matches_choice(answer, choice):
                    expected = infer_choice_answer_shape(choice.get("value") or choice.get("text"))
                    break
    if not expected or expected in {"empty", "expression"}:
        # Soft: still compare pairwise consistency when correct shape is known-ish.
        shapes = [infer_choice_answer_shape(c.get("value") or c.get("text")) for c in choices]
        if len(set(shapes)) > 1 and {"equation", "area_or_pi"} <= set(shapes):
            return ["vocational_choice_shape_mismatch"]
        if len(set(shapes)) > 1 and "equation" in shapes and any(
            s in {"number", "area_or_pi", "classification", "coordinate"} for s in shapes
        ):
            return ["vocational_choice_shape_mismatch"]
        return []
    errors: list[str] = []
    for choice in choices:
        shape = infer_choice_answer_shape(choice.get("value") or choice.get("text"))
        if shape != expected and not (
            expected == "area_or_pi" and shape in {"area_or_pi", "number"}
        ):
            # Allow number/area cross-fill for π-free numeric areas.
            if expected == "number" and shape == "area_or_pi":
                continue
            errors.append("vocational_choice_shape_mismatch")
            break
    return errors


def choice_semantic_key(text: Any) -> str:
    """Normalize choice text for semantic uniqueness (coordinates / plain strings)."""
    raw = str(text or "").strip()
    if not raw:
        return ""
    cleaned = _TECHNICAL_SUFFIX_RE.sub("", raw).strip().strip("$").strip()
    cleaned = cleaned.replace(r"\left", "").replace(r"\right", "")
    cleaned = cleaned.replace(r"\,", "").replace(r"\ ", " ")
    # Circle equations: equivalent algebraic forms share one semantic key.
    try:
        if "=" in cleaned and ("x" in cleaned.casefold() or "y" in cleaned.casefold()):
            from core.domain.circle_plane_domain import circle_semantic_key

            key = circle_semantic_key(cleaned)
            if key and key.startswith("D="):
                return key
    except Exception:
        pass
    try:
        from core.domain.vector_plane_domain import format_pair

        m = re.search(
            r"[\(\[]\s*([^,]+)\s*,\s*([^)\]]+)\s*[\)\]]",
            cleaned.replace("$", ""),
        )
        if m:
            return format_pair(plainify_math_token(m.group(1)), plainify_math_token(m.group(2)))
    except Exception:
        pass
    return re.sub(r"\s+", "", cleaned).casefold()


def has_technical_choice_suffix(text: Any) -> bool:
    return bool(_TECHNICAL_SUFFIX_RE.search(str(text or "").strip().rstrip("$")))


def is_vocational_choice(payload: dict[str, Any], skill_id: str = "") -> bool:
    """Use curriculum metadata first, with legacy vh_ skill IDs as fallback."""
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    facts = payload.get("validation_facts") if isinstance(payload.get("validation_facts"), dict) else {}
    profile = str(payload.get("curriculum_profile") or facts.get("curriculum_profile") or meta.get("curriculum_profile") or "").lower()
    if profile:
        return profile.startswith("vocational")
    return str(skill_id or payload.get("skill_id") or "").startswith("vh_")


def validate_vocational_multiple_choice(payload: dict[str, Any], skill_id: str = "") -> list[str]:
    """Strict generator/build validation; runtime repair is a separate path."""
    choice_type = str(payload.get("answer_type") or payload.get("question_type") or "").lower()
    checker = str(payload.get("checker") or payload.get("checker_type") or "").lower()
    if not is_vocational_choice(payload, skill_id) or not (
        requires_choice_contract(payload)
        or choice_type in {"choice", "single_choice", "multiple_choice"}
        or "choice" in checker
    ):
        return []
    choices = normalize_canonical_choices(payload.get("choices"))
    errors = []
    if len(choices) != VOCATIONAL_MC_CHOICE_COUNT:
        errors.append("vocational_choice_count")
    if [c["label"] for c in choices] != list("ABCD"):
        errors.append("vocational_choice_labels")
    values = [c["value"].strip().casefold() for c in choices]
    if any(not value or value in {"?", "...", "待補"} for value in values):
        errors.append("vocational_choice_blank_or_placeholder")
    if any(has_technical_choice_suffix(c.get("text") or c.get("value") or "") for c in choices):
        errors.append("vocational_choice_technical_suffix")
    semantic_keys = [choice_semantic_key(c.get("value") or c.get("text") or "") for c in choices]
    if any(not key for key in semantic_keys) or len(set(semantic_keys)) != len(semantic_keys):
        errors.append("vocational_choice_semantic_duplicate")
    if len(set(values)) != len(values):
        errors.append("vocational_choice_duplicate")
    answer = _resolve_answer(payload)
    if sum(_answer_matches_choice(answer, c) for c in choices) != 1:
        errors.append("vocational_answer_mapping")
    # Exactly one choice may match the expected semantic answer.
    expected = str(payload.get("canonical_answer") or payload.get("semantic_answer") or "")
    if expected:
        matches = sum(1 for c in choices if choice_semantic_key(c.get("value") or c.get("text")) == choice_semantic_key(expected))
        if matches > 1:
            errors.append("vocational_multi_correct")
    errors.extend(validate_choice_answer_shapes(payload))
    return errors


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

    blockers.extend(f"{CHOICE_CONTRACT_INCOMPLETE}:{error}" for error in validate_vocational_multiple_choice(p))

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
