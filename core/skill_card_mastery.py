"""Global, curriculum-neutral skill-card mastery aggregation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import case, func

from models import PracticeAttempt, Progress, TextbookExample, db


RECENT_ATTEMPT_LIMIT = 10

STATUS_LABELS = {
    "unpracticed": "尚未練習",
    "needs_improvement": "需要加強",
    "learning": "學習中",
    "proficient": "熟練",
    "mastered": "精熟",
}

STATUS_COLORS = {
    "unpracticed": "white",
    "needs_improvement": "red",
    "learning": "light_green",
    "proficient": "medium_green",
    "mastered": "dark_green",
}


def classify_skill_card_status(
    *,
    attempt_count: int,
    recent_accuracy: float,
    pass_target: int,
    binding_issue: bool,
) -> str:
    if attempt_count == 0:
        return "unpracticed"
    if recent_accuracy < 50:
        return "needs_improvement"
    if recent_accuracy < 70:
        return "learning"
    if recent_accuracy < 85:
        return "proficient"
    if not binding_issue and attempt_count >= pass_target:
        return "mastered"
    return "proficient"


def build_skill_card_mastery(
    *,
    student_id: int,
    skill_ids: Sequence[str],
    current_streak_by_skill: Mapping[str, int] | None = None,
    recent_limit: int = RECENT_ATTEMPT_LIMIT,
) -> dict[str, dict[str, Any]]:
    """Return card metrics for all requested skills using bounded batch queries.

    ``pass_target`` is always derived from bound textbook references.  The
    legacy ``skills_info.consecutive_correct_required`` value is intentionally
    not read here.
    """
    ordered_ids = list(dict.fromkeys(str(value or "").strip() for value in skill_ids))
    ids = [skill_id for skill_id in ordered_ids if skill_id]
    if not ids:
        return {}
    limit = max(1, int(recent_limit))

    reference_counts = {
        str(skill_id): int(count or 0)
        for skill_id, count in (
            db.session.query(TextbookExample.skill_id, func.count(TextbookExample.id))
            .filter(TextbookExample.skill_id.in_(ids))
            .group_by(TextbookExample.skill_id)
            .all()
        )
    }

    ranked_attempts = (
        db.session.query(
            PracticeAttempt.skill_id.label("skill_id"),
            PracticeAttempt.is_correct.label("is_correct"),
            func.row_number()
            .over(
                partition_by=PracticeAttempt.skill_id,
                order_by=(PracticeAttempt.created_at.desc(), PracticeAttempt.id.desc()),
            )
            .label("recent_rank"),
            func.count(PracticeAttempt.id)
            .over(partition_by=PracticeAttempt.skill_id)
            .label("attempt_count"),
        )
        .filter(
            PracticeAttempt.student_id == int(student_id),
            PracticeAttempt.skill_id.in_(ids),
        )
        .subquery()
    )
    attempt_rows = (
        db.session.query(
            ranked_attempts.c.skill_id,
            func.max(ranked_attempts.c.attempt_count),
            func.count(),
            func.sum(case((ranked_attempts.c.is_correct.is_(True), 1), else_=0)),
        )
        .filter(ranked_attempts.c.recent_rank <= limit)
        .group_by(ranked_attempts.c.skill_id)
        .all()
    )
    attempts_by_skill = {
        str(skill_id): {
            "attempt_count": int(attempt_count or 0),
            "recent_attempt_count": int(recent_count or 0),
            "recent_correct_count": int(recent_correct or 0),
        }
        for skill_id, attempt_count, recent_count, recent_correct in attempt_rows
    }

    if current_streak_by_skill is None:
        current_streak_by_skill = {
            str(skill_id): int(streak or 0)
            for skill_id, streak in (
                db.session.query(Progress.skill_id, Progress.consecutive_correct)
                .filter(Progress.user_id == int(student_id), Progress.skill_id.in_(ids))
                .all()
            )
        }

    result: dict[str, dict[str, Any]] = {}
    for skill_id in ids:
        pass_target = reference_counts.get(skill_id, 0)
        binding_issue = pass_target == 0
        attempt_stats = attempts_by_skill.get(skill_id, {})
        attempt_count = int(attempt_stats.get("attempt_count", 0))
        recent_count = int(attempt_stats.get("recent_attempt_count", 0))
        recent_correct = int(attempt_stats.get("recent_correct_count", 0))
        recent_accuracy = round(100.0 * recent_correct / recent_count, 1) if recent_count else 0.0
        status = classify_skill_card_status(
            attempt_count=attempt_count,
            recent_accuracy=recent_accuracy,
            pass_target=pass_target,
            binding_issue=binding_issue,
        )
        result[skill_id] = {
            "skill_id": skill_id,
            "pass_target": pass_target,
            "reference_count": pass_target,
            "binding_issue": binding_issue,
            "binding_issue_code": "missing_textbook_references" if binding_issue else None,
            "current_streak": int(current_streak_by_skill.get(skill_id, 0) or 0),
            "attempt_count": attempt_count,
            "recent_attempt_count": recent_count,
            "recent_correct_count": recent_correct,
            "recent_accuracy": recent_accuracy,
            "recent_accuracy_label": f"{recent_accuracy:g}%",
            "card_status": status,
            "card_status_label": STATUS_LABELS[status],
            "card_color": STATUS_COLORS[status],
        }
    return result
