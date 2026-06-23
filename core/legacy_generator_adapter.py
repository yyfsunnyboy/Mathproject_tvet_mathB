"""Legacy generator invocation helpers for practice runtime."""

from __future__ import annotations

from types import ModuleType
from typing import Any


def normalize_legacy_payload(payload: dict[str, Any], *, skill_id: str) -> dict[str, Any]:
    """Fill the minimal API fields expected by the current practice frontend."""

    if "question_text" in payload and "new_question_text" not in payload:
        payload["new_question_text"] = payload["question_text"]

    if "answer" in payload and "correct_answer" not in payload:
        payload["correct_answer"] = payload["answer"]
    if "correct_answer" in payload and "answer" not in payload:
        payload["answer"] = payload["correct_answer"]

    if payload.get("choices") is None:
        payload["choices"] = []

    if "answer_type" not in payload:
        payload["answer_type"] = "multiple_choice" if payload.get("choices") else "text"

    payload["generator_mode"] = "legacy"
    payload["route_source"] = "legacy_skill"
    payload["question_source"] = "legacy_skill"
    payload.setdefault("skill_id", skill_id)
    return payload


def invoke_legacy_generator(
    module: ModuleType,
    *,
    skill_id: str,
    level: int,
) -> dict[str, Any]:
    """Invoke a legacy skill without modern runtime kwargs."""

    generate = getattr(module, "generate", None)
    if not callable(generate):
        raise RuntimeError(f"legacy_generate_missing:{skill_id}")

    payload = generate(level=level)
    if not isinstance(payload, dict):
        raise RuntimeError(f"legacy_generate_non_dict:{skill_id}")

    return normalize_legacy_payload(payload, skill_id=skill_id)
