# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/session.py
功能說明 (Description): 練習 session：cookie 僅存指標，完整題目存 server-side store。
=============================================================================
"""

from __future__ import annotations

from typing import Any

from core.practice_question_store import (
    clear_practice_state,
    load_current_question,
    persist_current_question,
)


def set_current(skill: str, data: dict[str, Any]) -> None:
    """Store generated question in server-side store; cookie keeps uid pointers only."""
    if not isinstance(data, dict):
        return
    saved_data = dict(data)
    saved_data["skill"] = str(skill).strip()
    saved_data["skill_id"] = str(skill).strip()
    if "question_text" in saved_data:
        saved_data["question"] = saved_data["question_text"]
    if "inequality_string" in saved_data:
        saved_data["inequality"] = saved_data["inequality_string"]
    persist_current_question(str(skill).strip(), saved_data)


def get_current() -> dict[str, Any]:
    """Load current question payload by session.current_question_uid from server store."""
    return load_current_question()


def clear() -> None:
    """Clear practice pointers and server-side store for this owner."""
    clear_practice_state()
