# -*- coding: utf-8 -*-
"""Chapter review runs (本章總複習存檔).

A run is the set of ``practice_attempts`` rows with ``source="chapter_review"``
and ``session_id=<run_id>``.  Every graded answer is already committed as one
such row, so each submission is the checkpoint.  The cookie session only keeps a
pointer to the active run; progress, accuracy and streak are always rebuilt from
the run's attempts.

Within a run only the first definitive verdict of a ``question_uid`` counts;
handwriting re-submissions of the same question add rows but not answers.
"""

from __future__ import annotations

import uuid
from typing import Any, Iterable

from core.practice_attempt_service import SOURCE_CHAPTER_REVIEW
from core.practice_type_rotation import STATUS_PASSED, STATUS_UNSEEN, STATUS_WEAK

SESSION_POINTER_KEY = "chapter_review_run"


def new_run_id() -> str:
    return "cr_" + uuid.uuid4().hex


def load_first_verdicts(student_id: int, run_id: str) -> list[dict[str, Any]]:
    """Run attempts in answer order, keeping only the first verdict per question_uid."""
    from models import PracticeAttempt, db

    rows = (
        db.session.query(
            PracticeAttempt.skill_id,
            PracticeAttempt.problem_type_id,
            PracticeAttempt.question_uid,
            PracticeAttempt.is_correct,
        )
        .filter(
            PracticeAttempt.student_id == int(student_id),
            PracticeAttempt.source == SOURCE_CHAPTER_REVIEW,
            PracticeAttempt.session_id == str(run_id),
        )
        .order_by(PracticeAttempt.created_at.asc(), PracticeAttempt.id.asc())
        .all()
    )
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for skill_id, problem_type_id, question_uid, is_correct in rows:
        uid = str(question_uid or "").strip()
        if uid:
            if uid in seen:
                continue
            seen.add(uid)
        out.append(
            {
                "skill_id": str(skill_id or ""),
                "type_key": str(problem_type_id or ""),
                "correct": bool(is_correct),
            }
        )
    return out


def latest_run_id(student_id: int, skill_ids: Iterable[str]) -> str:
    """Run id of the most recent chapter review answer within these sections; ``""`` if none."""
    from models import PracticeAttempt, db

    ids = [str(s) for s in skill_ids if s]
    if not ids:
        return ""
    row = (
        db.session.query(PracticeAttempt.session_id)
        .filter(
            PracticeAttempt.student_id == int(student_id),
            PracticeAttempt.source == SOURCE_CHAPTER_REVIEW,
            PracticeAttempt.skill_id.in_(ids),
            PracticeAttempt.session_id.isnot(None),
        )
        .order_by(PracticeAttempt.created_at.desc(), PracticeAttempt.id.desc())
        .first()
    )
    return str(row[0]) if row and row[0] else ""


def type_statuses(verdicts: list[dict[str, Any]]) -> dict[tuple[str, str], str]:
    """``(skill_id, type_key) -> passed | weak``; types without verdicts are absent (unseen)."""
    out: dict[tuple[str, str], str] = {}
    for v in verdicts:
        key = (v["skill_id"], v["type_key"])
        if v["correct"]:
            out[key] = STATUS_PASSED
        elif out.get(key) != STATUS_PASSED:
            out[key] = STATUS_WEAK
    return out


def section_statuses(statuses: dict[tuple[str, str], str], section: str, type_keys: Iterable[str]) -> dict[str, str]:
    return {k: statuses.get((section, k), STATUS_UNSEEN) for k in type_keys}


def summarize_run(
    verdicts: list[dict[str, Any]],
    sections: list[tuple[str, list[str]]],
) -> dict[str, Any]:
    """Accuracy, trailing streak and chapter progress for one run.

    ``sections`` is the chapter's available sections in textbook order with their
    practice type keys.
    """
    answered = len(verdicts)
    correct = sum(1 for v in verdicts if v["correct"])
    streak = 0
    for v in reversed(verdicts):
        if not v["correct"]:
            break
        streak += 1
    statuses = type_statuses(verdicts)
    total = sum(len(keys) for _, keys in sections)
    passed = sum(1 for sid, keys in sections for k in keys if statuses.get((sid, k)) == STATUS_PASSED)
    finished = [sid for sid, keys in sections if all(statuses.get((sid, k)) == STATUS_PASSED for k in keys)]
    current = next((sid for sid, _ in sections if sid not in finished), "")
    return {
        "answered": answered,
        "correct": correct,
        "wrong": answered - correct,
        "accuracy": int(correct * 100 / answered + 0.5) if answered else None,
        "streak": streak,
        "types_passed": passed,
        "types_total": total,
        "sections_completed": len(finished),
        "current_section": current,
        "completed": bool(total) and not current,
    }
