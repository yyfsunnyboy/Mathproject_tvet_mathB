"""Bounded, per-question context shared by chat and handwriting tutoring."""

from __future__ import annotations

from typing import Any

from core.practice_question_store import (
    AI_CONVERSATION_MAX_TURNS,
    append_question_conversation_turn,
    get_question_conversation_context,
)


def get_context(question_uid: str) -> list[dict[str, Any]]:
    return get_question_conversation_context(question_uid)


def add_turn(
    question_uid: str,
    *,
    role: str,
    kind: str,
    content: str,
    authoritative_correct: bool | None = None,
    authoritative_status: str = "",
) -> bool:
    turn: dict[str, Any] = {"role": role, "kind": kind, "content": content}
    if authoritative_correct is not None:
        turn["authoritative_correct"] = authoritative_correct
    if authoritative_status:
        turn["authoritative_status"] = authoritative_status
    return append_question_conversation_turn(question_uid, turn)


def format_for_prompt(question_uid: str) -> str:
    turns = get_context(question_uid)
    if not turns:
        return ""
    lines = [
        "[同一題的近期對話；僅供銜接說明，不得用來判分或覆蓋 authoritative checker]"
    ]
    for turn in turns:
        role = turn.get("role") or "event"
        kind = turn.get("kind") or "message"
        content = str(turn.get("content") or "").strip()
        authority = ""
        if turn.get("authoritative_correct") is not None:
            authority = (
                f" [authoritative_correct={str(turn['authoritative_correct']).lower()}; "
                f"status={turn.get('authoritative_status') or 'unknown'}]"
            )
        lines.append(f"- {role}/{kind}: {content}{authority}")
    return "\n".join(lines)


__all__ = ["AI_CONVERSATION_MAX_TURNS", "add_turn", "format_for_prompt", "get_context"]
