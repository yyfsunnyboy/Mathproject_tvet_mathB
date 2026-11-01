# -*- coding: utf-8 -*-
"""Server-side record of a question served by /get_next_question.

The HTTP body sent to the student no longer carries the answer; tests that need it read the trusted copy that
/check_answer, the AI tutor and handwriting analysis use, looked up by question_uid.
"""
from __future__ import annotations

from typing import Any

from core.practice_question_store import _STORE, _STORE_LOCK


def stored_question(payload: dict[str, Any]) -> dict[str, Any]:
    uid = str((payload or {}).get("question_uid") or "").strip()
    with _STORE_LOCK:
        for rows in _STORE.values():
            if uid and uid in rows:
                return dict(rows[uid])
    raise AssertionError(f"question_uid {uid!r} is not in the practice question store")


def stored_answer(payload: dict[str, Any]) -> Any:
    return stored_question(payload).get("correct_answer")


def with_stored_answer(payload: dict[str, Any]) -> dict[str, Any]:
    """The student payload plus the trusted answer fields, for tests that grade or inspect the canonical answer."""
    stored = stored_question(payload)
    out = dict(payload)
    for key in ("answer", "correct_answer", "display_answer"):
        if key in stored:
            out[key] = stored[key]
    if isinstance(stored.get("answer_contract"), dict) and stored["answer_contract"]:
        out["answer_contract"] = stored["answer_contract"]
    semantic = (stored.get("metadata") or {}).get("semantic_answer")
    if semantic is not None:
        out["semantic_answer"] = semantic
    return out
