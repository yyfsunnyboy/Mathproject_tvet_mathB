"""Bounded, per-question context shared by chat and handwriting tutoring."""

from __future__ import annotations

from typing import Any
import re

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
    **details: Any,
) -> bool:
    turn: dict[str, Any] = {"role": role, "kind": kind, "content": content}
    turn.update(details)
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
        when = turn.get("at", "")
        lines.append(f"- {when} {role}/{kind}: {content}{authority}")
    return "\n".join(lines)


def normalize_suggested_questions(
    proposed: Any, *, question_text: str, student_work: str, ai_reply: str,
    correct_answer: str = "",
) -> list[str]:
    """Normalize one model response; keep the reply even when its prompts are malformed."""
    accepted: list[str] = []
    answer = str(correct_answer or "").strip()

    def contains_answer(value: str) -> bool:
        if not answer:
            return False
        compact_answer = re.sub(r"\s+", "", answer)
        compact_value = re.sub(r"\s+", "", value)
        if len(compact_answer) >= 2:
            return compact_answer in compact_value
        if compact_answer.isalnum():
            return re.search(
                rf"(?<![A-Za-z0-9]){re.escape(compact_answer)}(?![A-Za-z0-9])",
                compact_value,
            ) is not None
        return False

    for item in proposed if isinstance(proposed, list) else []:
        value = re.sub(r"\s+", " ", str(item or "")).strip()[:120]
        generic = value.startswith(("問題1", "問題2", "問題3")) or any(
            marker in value for marker in ("【觀察】", "【聯想】", "【執行】")
        )
        leaks_answer = contains_answer(value)
        if value and not generic and not leaks_answer and value not in accepted and ("?" in value or "？" in value):
            accepted.append(value)
        if len(accepted) == 3:
            break
    if len(accepted) == 3:
        return accepted
    def focus(value: str) -> str:
        lines = [re.sub(r"\s+", " ", line).strip() for line in str(value or "").splitlines()]
        return next((line[:32] for line in lines if line), "這一題")
    work = focus(student_work)
    hint = focus(ai_reply)
    if contains_answer(work):
        work = "我目前寫出的步驟"
    if contains_answer(hint):
        hint = "剛才的檢查提示"
    question = focus(question_text)
    if contains_answer(question):
        question = "目前這一題"
    fallback = [
        f"我寫的「{work}」這一步，應先檢查哪個條件？",
        f"依照剛才的提示「{hint}」，我下一步該怎麼驗證？",
        f"回到題目「{question}」，有沒有另一種檢查方法？",
    ]
    for item in fallback:
        if item not in accepted:
            accepted.append(item)
        if len(accepted) == 3:
            break
    return accepted[:3]


__all__ = ["AI_CONVERSATION_MAX_TURNS", "add_turn", "format_for_prompt", "get_context", "normalize_suggested_questions"]
