"""Four-option vocational MCQ contract and legacy runtime repair."""

from __future__ import annotations

import random
import re
from typing import Any

from core.gencode.choice_contract_validator import (
    VOCATIONAL_MC_CHOICE_COUNT,
    is_vocational_choice,
    normalize_canonical_choices,
    requires_choice_contract,
    validate_vocational_multiple_choice,
)


def _answer_index(value: Any, choices: list[dict[str, str]]) -> int | None:
    if isinstance(value, dict):
        for field in ("value", "label", "key", "index"):
            if field in value:
                found = _answer_index(value[field], choices)
                if found is not None:
                    return found
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        semantic = next((i for i, choice in enumerate(choices) if choice["value"] == str(value)), None)
        if semantic is not None:
            return semantic
        return value if 0 <= value < len(choices) else None
    raw = str(value if value is not None else "").strip()
    label = raw.strip("()[] .").upper()
    if len(label) == 1 and "A" <= label <= "Z":
        return next((i for i, choice in enumerate(choices) if choice["label"].upper() == label), None)
    if re.fullmatch(r"[1-9]\d*", raw):
        # A numeric string may be the semantic choice value. Prefer that match.
        semantic = next((i for i, choice in enumerate(choices) if choice["value"] == raw), None)
        if semantic is not None:
            return semantic
        index = int(raw) - 1
        return index if index < len(choices) else None
    return next((i for i, choice in enumerate(choices) if raw in {choice["value"], choice["text"]}), None)


def normalize_legacy_vocational_choices(payload: dict[str, Any], *, skill_id: str = "") -> dict[str, Any]:
    """Repair old 5/6-option payloads before session storage and grading."""
    if not isinstance(payload, dict) or not is_vocational_choice(payload, skill_id):
        return payload
    choices = normalize_canonical_choices(payload.get("choices"))
    choice_type = str(payload.get("answer_type") or payload.get("question_type") or "").lower()
    checker = str(payload.get("checker") or payload.get("checker_type") or "").lower()
    if not choices or not (requires_choice_contract(payload) or choice_type in {"choice", "single_choice", "multiple_choice"} or "choice" in checker):
        return payload
    if len(choices) == VOCATIONAL_MC_CHOICE_COUNT and not validate_vocational_multiple_choice(payload, skill_id):
        return payload
    if len(choices) < VOCATIONAL_MC_CHOICE_COUNT:
        raise ValueError("vocational_choice_count_insufficient")
    raw_answer = next((payload.get(field) for field in ("correct_answer", "answer", "correct_choice", "correct_option") if payload.get(field) is not None), None)
    correct_index = _answer_index(raw_answer, choices)
    if correct_index is None:
        raise ValueError("vocational_correct_answer_unresolvable")
    correct = choices[correct_index]
    seen = {correct["value"].strip().casefold()}
    wrong = []
    for index, choice in enumerate(choices):
        key = choice["value"].strip().casefold()
        if index == correct_index or not key or key in seen:
            continue
        seen.add(key)
        wrong.append(choice)
    if len(wrong) < VOCATIONAL_MC_CHOICE_COUNT - 1:
        raise ValueError("vocational_unique_distractors_insufficient")
    selected = [correct, *wrong[: VOCATIONAL_MC_CHOICE_COUNT - 1]]
    random.Random(str(payload.get("seed") or payload.get("question_uid") or correct["value"])).shuffle(selected)
    normalized = []
    for index, choice in enumerate(selected):
        normalized.append({**choice, "key": "ABCD"[index], "label": "ABCD"[index]})
    new_index = selected.index(correct)
    new_label = "ABCD"[new_index]
    out = dict(payload)
    out["choices"] = normalized
    out["options"] = [choice["text"] for choice in normalized]
    out["choices_display"] = list(normalized)
    out["answer"] = new_label
    out["correct_answer"] = new_label
    for field in ("correct_choice", "correct_option"):
        if field in out:
            out[field] = new_label
    if "answer_index" in out:
        out["answer_index"] = new_index
    if "correct_index" in out:
        out["correct_index"] = new_index
    out.setdefault("semantic_answer", correct["value"])
    errors = validate_vocational_multiple_choice(out, skill_id)
    if errors:
        raise ValueError("vocational_choice_repair_failed:" + ",".join(errors))
    return out
