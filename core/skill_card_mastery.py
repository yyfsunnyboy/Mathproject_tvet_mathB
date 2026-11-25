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

# Active DB shells with no Stage-1 TE and no runtime Generator.
# Formal DB deactivate remains NEEDS_DECISION; runtime must not invite 404 practice.
KNOWN_EMPTY_SHELL_SKILL_IDS = frozenset(
    {
        "vh_數學B1_SubSection332",
    }
)


def is_known_empty_shell_skill(skill_id: str) -> bool:
    return str(skill_id or "").strip() in KNOWN_EMPTY_SHELL_SKILL_IDS


def _binding_meta(skill_id: str, *, pass_target: int) -> tuple[bool, str | None, str | None]:
    """Return (binding_issue, binding_issue_code, binding_issue_label)."""
    sid = str(skill_id or "").strip()
    if is_known_empty_shell_skill(sid) or pass_target <= 0:
        if is_known_empty_shell_skill(sid):
            return True, "empty_shell_no_runtime", "本單元尚無可練習題型（空殼，待教材來源／停用決策）"
        return True, "missing_textbook_references", "暫無可練習題型"
    return False, None, None


def get_pass_targets(skill_ids: Sequence[str]) -> dict[str, int]:
    """Return the global practice target: bound textbook-example count per skill."""
    ids = list(dict.fromkeys(str(value or "").strip() for value in skill_ids))
    ids = [skill_id for skill_id in ids if skill_id]
    if not ids:
        return {}
    counts = {
        str(skill_id): int(count or 0)
        for skill_id, count in (
            db.session.query(TextbookExample.skill_id, func.count(TextbookExample.id))
            .filter(TextbookExample.skill_id.in_(ids))
            .group_by(TextbookExample.skill_id)
            .all()
        )
    }
    return {skill_id: counts.get(skill_id, 0) for skill_id in ids}


def get_pass_target(skill_id: str) -> int:
    """Return one skill's global practice target, or zero when unbound."""
    normalized = str(skill_id or "").strip()
    return get_pass_targets([normalized]).get(normalized, 0)


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
    student_id: int | None,
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

    reference_counts = get_pass_targets(ids)
    if student_id is None:
        # Anonymous/Guest Demo has no student identity. Return before any
        # personal PracticeAttempt or Progress query and never borrow records.
        guest_cards: dict[str, dict[str, Any]] = {}
        for skill_id in ids:
            target = reference_counts.get(skill_id, 0)
            issue, code, label = _binding_meta(skill_id, pass_target=target)
            guest_cards[skill_id] = {
                "skill_id": skill_id,
                "pass_target": target,
                "reference_count": target,
                "binding_issue": issue,
                "binding_issue_code": code,
                "binding_issue_label": label,
                "practice_enabled": not is_known_empty_shell_skill(skill_id),
                "current_streak": 0,
                "attempt_count": 0,
                "recent_attempt_count": 0,
                "recent_correct_count": 0,
                "recent_accuracy": 0.0,
                "recent_accuracy_label": "0%",
                "card_status": "unpracticed",
                "card_status_label": "展示模式／尚無個人學習紀錄",
                "card_color": STATUS_COLORS["unpracticed"],
            }
        return guest_cards

    normalized_student_id = int(student_id)
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
            PracticeAttempt.student_id == normalized_student_id,
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
                .filter(Progress.user_id == normalized_student_id, Progress.skill_id.in_(ids))
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
        issue, code, label = _binding_meta(skill_id, pass_target=pass_target)
        # Prefer empty-shell classification over generic zero-reference alarm.
        binding_issue = issue
        result[skill_id] = {
            "skill_id": skill_id,
            "pass_target": pass_target,
            "reference_count": pass_target,
            "binding_issue": binding_issue,
            "binding_issue_code": code,
            "binding_issue_label": label,
            "practice_enabled": not is_known_empty_shell_skill(skill_id),
            "current_streak": int(current_streak_by_skill.get(skill_id, 0) or 0),
            "attempt_count": attempt_count,
            "recent_attempt_count": recent_count,
            "recent_correct_count": recent_correct,
            "recent_accuracy": recent_accuracy,
            "recent_accuracy_label": f"{recent_accuracy:g}%",
            "card_status": status,
            "card_status_label": STATUS_LABELS[status],
            "card_color": STATUS_COLORS[status],
            "progress_mode": "streak",
            "progress_label": (
                f"連續答對 {int(current_streak_by_skill.get(skill_id, 0) or 0)} / "
                f"{'暫無門檻' if binding_issue else f'{pass_target} 題'}"
            ),
        }

    # B1 overlay: skill-card gate uses Generator problem-type mastery (X/Y),
    # without changing non-B1 streak semantics.
    try:
        from core.practice_type_mastery import get_skill_type_progress, is_b1_type_mastery_skill

        for skill_id, card in result.items():
            if not is_b1_type_mastery_skill(skill_id):
                continue
            mp = get_skill_type_progress(normalized_student_id, skill_id)
            total = int(mp.get("total_types") or 0)
            mastered = int(mp.get("mastered_count") or 0)
            card["progress_mode"] = "problem_type_mastery"
            card["pass_target"] = total
            card["current_streak"] = mastered
            if is_known_empty_shell_skill(skill_id):
                card["binding_issue"] = True
                card["binding_issue_code"] = "empty_shell_no_runtime"
                card["binding_issue_label"] = "本單元尚無可練習題型（空殼，待教材來源／停用決策）"
                card["practice_enabled"] = False
                card["progress_label"] = "暫無可練習題型"
            else:
                card["binding_issue"] = total == 0
                card["binding_issue_code"] = "missing_runtime_problem_types" if total == 0 else None
                card["binding_issue_label"] = "暫無可練習題型" if total == 0 else None
                card["practice_enabled"] = total > 0
                card["progress_label"] = (
                    f"已掌握題型 {mastered}/{total}" if total > 0 else "暫無可練習題型"
                )
            if total > 0 and mastered >= total:
                card["card_status"] = "mastered"
                card["card_status_label"] = STATUS_LABELS["mastered"]
                card["card_color"] = STATUS_COLORS["mastered"]
    except Exception:
        # Card display must not break practice browsing if mastery table is absent.
        pass

    return result
