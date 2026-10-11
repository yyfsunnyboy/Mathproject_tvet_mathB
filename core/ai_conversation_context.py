"""Bounded, per-question context shared by chat and handwriting tutoring."""

from __future__ import annotations

from typing import Any
import re

from core.ai_tutor_disclosure import find_answer_disclosure
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


def current_teaching_round(question_uid: str, submission_id: str = "") -> int:
    """Round of the next tutoring reply on this question (1-based, server-side only).

    Only successful teaching replies carry ``teaching_round``; failed or duplicate
    submissions never reach the store.  Using the highest recorded round, not a
    count, keeps concurrent requests from the same round from skipping ahead.
    A resent ``submission_id`` keeps the round it was first answered in.
    """
    turns = get_context(question_uid)
    submission_id = str(submission_id or "").strip()
    if submission_id:
        for turn in turns:
            if turn.get("submission_id") == submission_id and isinstance(turn.get("teaching_round"), int):
                return turn["teaching_round"]
    rounds = [turn["teaching_round"] for turn in turns if isinstance(turn.get("teaching_round"), int)]
    return (max(rounds) if rounds else 0) + 1


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
        label = f"第{turn['teaching_round']}輪 " if isinstance(turn.get("teaching_round"), int) else ""
        lines.append(f"- {when} {label}{role}/{kind}: {content}{authority}")
    return "\n".join(lines)


_LATEX_READABLE = (
    (r"\\sqrt\s*\{([^{}]*)\}", r"√(\1)"),
    (r"\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"(\1)/(\2)"),
    (r"\\times", "×"),
    (r"\\cdot", "·"),
    (r"\\div", "÷"),
    (r"\\pi", "π"),
    (r"\\(?:leq|le)\b", "≤"),
    (r"\\(?:geq|ge)\b", "≥"),
    (r"\\(?:neq|ne)\b", "≠"),
)


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
        if find_answer_disclosure(value, answer).disclosed:
            return True
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
    def lines_of(value: str) -> list[str]:
        cleaned = str(value or "").replace("$", "")
        for pattern, repl in _LATEX_READABLE:
            cleaned = re.sub(pattern, repl, cleaned)
        cleaned = re.sub(r"\\[A-Za-z]+|[{}]", "", cleaned)
        parts = (re.sub(r"\s+", " ", line).strip(" 。？?！!，,：:") for line in re.split(r"[\n；;]", cleaned))
        return [part for part in parts if part]

    work_lines = lines_of(student_work)
    latest_work = work_lines[-1][:32] if work_lines else ""
    reply_lines = lines_of(ai_reply)
    hint = reply_lines[-1][:32] if reply_lines else ""
    if latest_work and not contains_answer(latest_work):
        check_question = f"我寫的「{latest_work}」對嗎？下一步要算什麼？"
    else:
        check_question = "我目前寫的步驟對嗎？下一步要算什麼？"
    if hint and not contains_answer(hint):
        example_question = f"「{hint}」可以用這題的數字示範一次嗎？"
    else:
        example_question = "剛才說的下一步，可以用這題的數字示範一次嗎？"
    fallback = [
        check_question,
        example_question,
        "這一步用到的公式或定義是什麼意思？",
    ]
    for item in fallback:
        if item not in accepted:
            accepted.append(item)
        if len(accepted) == 3:
            break
    return accepted[:3]


__all__ = [
    "AI_CONVERSATION_MAX_TURNS",
    "add_turn",
    "current_teaching_round",
    "format_for_prompt",
    "get_context",
    "normalize_suggested_questions",
]
