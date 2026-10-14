from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import case, func
from sqlalchemy.orm import aliased

from core.teacher_analysis_service import student_display_name
from core.skill_card_mastery import build_skill_card_mastery
from core.vocational_mock_exam_scope import mock_exam_cards
from core.utils import (
    get_chapters_by_curriculum_volume,
    get_volumes_by_curriculum,
    normalize_curriculum,
)
from models import Class, ClassStudent, PracticeAttempt, Progress, SkillCurriculum, SkillInfo, User, db

VOCATIONAL_KEY = "vocational"
_TAIPEI_OFFSET = timedelta(hours=8)


def is_vocational_student(user: Any) -> bool:
    """True only for students whose profile/class membership is vocational."""
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if str(getattr(user, "role", "") or "").strip() != "student":
        return False
    code = normalize_curriculum(getattr(user, "curriculum_code", None) or "")
    if code == VOCATIONAL_KEY:
        return True
    if code in {"junior_high", "general"}:
        return False
    # Unset curriculum_code: class-enrolled students in this product are 技高 roster.
    uid = getattr(user, "id", None)
    if uid is None:
        return False
    return (
        db.session.query(ClassStudent.id)
        .filter(ClassStudent.student_id == uid)
        .first()
        is not None
    )


def _local_now() -> datetime:
    return datetime.utcnow() + _TAIPEI_OFFSET


def _as_local(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None) + _TAIPEI_OFFSET
    return dt + _TAIPEI_OFFSET


def format_recent_activity(dt: datetime | None) -> str:
    local = _as_local(dt)
    if local is None:
        return "尚未開始"
    now = _local_now()
    today = now.date()
    day = local.date()
    clock = local.strftime("%H:%M")
    if day == today:
        return f"今天 {clock}"
    if day == today - timedelta(days=1):
        return f"昨天 {clock}"
    return local.strftime("%m/%d %H:%M")


def _week_start_utc() -> datetime:
    local = _local_now()
    monday = local - timedelta(days=local.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return monday - _TAIPEI_OFFSET


def _skill_meta(skill_id: str) -> dict[str, Any]:
    info = SkillInfo.query.filter_by(skill_id=skill_id).first()
    row = (
        SkillCurriculum.query.filter_by(skill_id=skill_id, curriculum=VOCATIONAL_KEY)
        .order_by(SkillCurriculum.display_order)
        .first()
    )
    if row is None:
        row = SkillCurriculum.query.filter_by(skill_id=skill_id).first()
    return {
        "skill_id": skill_id,
        "skill_name": (info.skill_ch_name if info else "") or skill_id,
        "skill_ch_name": (info.skill_ch_name if info else "") or skill_id,
        "description": (info.description if info else "") or "",
        "volume": row.volume if row else "",
        "chapter": row.chapter if row else "",
        "grade": row.grade if row else None,
    }


def _skill_meta_map(skill_ids: set[str]) -> dict[str, dict[str, Any]]:
    """Load dashboard skill labels and curriculum placement without per-row queries."""
    ids = {str(value or "").strip() for value in skill_ids if str(value or "").strip()}
    if not ids:
        return {}

    infos = {
        row.skill_id: row
        for row in SkillInfo.query.filter(SkillInfo.skill_id.in_(ids)).all()
    }
    curriculum_rows = (
        SkillCurriculum.query.filter(SkillCurriculum.skill_id.in_(ids))
        .order_by(
            SkillCurriculum.skill_id,
            case((SkillCurriculum.curriculum == VOCATIONAL_KEY, 0), else_=1),
            SkillCurriculum.display_order,
            SkillCurriculum.id,
        )
        .all()
    )
    curriculum_by_skill: dict[str, SkillCurriculum] = {}
    for row in curriculum_rows:
        curriculum_by_skill.setdefault(str(row.skill_id), row)

    result: dict[str, dict[str, Any]] = {}
    for skill_id in ids:
        info = infos.get(skill_id)
        row = curriculum_by_skill.get(skill_id)
        result[skill_id] = {
            "skill_id": skill_id,
            "skill_name": (info.skill_ch_name if info else "") or skill_id,
            "skill_ch_name": (info.skill_ch_name if info else "") or skill_id,
            "description": (info.description if info else "") or "",
            "volume": row.volume if row else "",
            "chapter": row.chapter if row else "",
            "grade": row.grade if row else None,
        }
    return result


def _latest_continue(
    user_id: int,
    *,
    latest_attempt: PracticeAttempt | None = None,
    skill_meta: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    attempt = latest_attempt
    if attempt is None:
        attempt = (
            PracticeAttempt.query.filter_by(student_id=user_id)
            .order_by(PracticeAttempt.created_at.desc(), PracticeAttempt.id.desc())
            .first()
        )
    if attempt is not None and attempt.skill_id:
        sid = str(attempt.skill_id)
        meta = dict((skill_meta or {}).get(sid) or _skill_meta(sid))
        meta["practiced_at"] = attempt.created_at
        meta["source"] = "practice_attempts"
        return meta
    progress = (
        Progress.query.filter_by(user_id=user_id)
        .order_by(Progress.last_practiced.desc())
        .first()
    )
    if progress is not None and progress.skill_id:
        meta = _skill_meta(str(progress.skill_id))
        meta["practiced_at"] = progress.last_practiced
        meta["source"] = "progress"
        return meta
    return None


def _weekly_stats(user_id: int) -> dict[str, Any]:
    start = _week_start_utc()
    row = (
        db.session.query(
            func.count(PracticeAttempt.id),
            func.coalesce(func.sum(case((PracticeAttempt.is_correct.is_(True), 1), else_=0)), 0),
            func.max(PracticeAttempt.created_at),
        )
        .filter(
            PracticeAttempt.student_id == user_id,
            PracticeAttempt.created_at >= start,
        )
        .first()
    )
    total = int(row[0] or 0) if row else 0
    correct = int(row[1] or 0) if row else 0
    last_at = row[2] if row else None
    if total <= 0:
        last_any = (
            db.session.query(func.max(PracticeAttempt.created_at))
            .filter(PracticeAttempt.student_id == user_id)
            .scalar()
        )
        return {
            "week_count": 0,
            "week_correct_rate": None,
            "week_correct_rate_label": "—",
            "recent_label": format_recent_activity(last_any) if last_any else "尚未開始",
        }
    rate = round(100.0 * correct / total)
    return {
        "week_count": total,
        "week_correct_rate": rate,
        "week_correct_rate_label": f"{rate}%",
        "recent_label": format_recent_activity(last_at),
    }


def _class_rows(user_id: int) -> list[dict[str, Any]]:
    teacher = aliased(User)
    memberships = (
        db.session.query(ClassStudent, Class, teacher)
        .join(Class, Class.id == ClassStudent.class_id)
        .outerjoin(teacher, teacher.id == Class.teacher_id)
        .filter(ClassStudent.student_id == user_id)
        .order_by(ClassStudent.joined_at.asc(), ClassStudent.id.asc())
        .all()
    )
    rows: list[dict[str, Any]] = []
    for ms, cls, teacher_row in memberships:
        teacher_name = student_display_name(teacher_row) if teacher_row is not None else "—"
        rows.append(
            {
                "name": cls.name,
                "teacher_name": teacher_name,
                "seat_no": ms.seat_no,
            }
        )
    return rows


def _volume_cards(
    user_id: int,
    *,
    attempts: list[PracticeAttempt] | None = None,
    skill_meta: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    grouped = get_volumes_by_curriculum(VOCATIONAL_KEY) or {}
    grade_map = {10: "一年級", 11: "二年級", 12: "三年級"}
    latest_by_volume: dict[str, datetime] = {}
    latest_skill_by_volume: dict[str, str] = {}
    if attempts is None:
        attempts = (
            PracticeAttempt.query.filter_by(student_id=user_id)
            .order_by(PracticeAttempt.created_at.desc())
            .limit(80)
            .all()
        )
    for att in attempts:
        sid = str(att.skill_id)
        meta = (skill_meta or {}).get(sid) or _skill_meta(sid)
        vol = str(meta.get("volume") or "")
        if vol and vol not in latest_skill_by_volume:
            latest_skill_by_volume[vol] = meta["skill_name"]
            latest_by_volume[vol] = att.created_at

    cards: list[dict[str, Any]] = []
    for grade in sorted(grouped.keys()):
        for volume in grouped[grade]:
            chapters = get_chapters_by_curriculum_volume(VOCATIONAL_KEY, volume) or []
            first_chapter = str(chapters[0]).strip() if chapters else ""
            cards.append(
                {
                    "volume": volume,
                    "grade": grade,
                    "grade_label": grade_map.get(grade, f"{grade}年級"),
                    "chapter_hint": first_chapter,
                    "recent_skill_name": latest_skill_by_volume.get(volume, ""),
                }
            )
    return cards


def build_vocational_home_context(user: Any) -> dict[str, Any]:
    uid = int(user.id)
    display_name = student_display_name(user)
    class_rows = _class_rows(uid)
    primary = class_rows[0] if class_rows else None
    recent_attempts = (
        PracticeAttempt.query.filter_by(student_id=uid)
        .order_by(PracticeAttempt.created_at.desc(), PracticeAttempt.id.desc())
        .limit(80)
        .all()
    )
    skill_meta = _skill_meta_map({str(row.skill_id) for row in recent_attempts})
    continue_item = _latest_continue(
        uid,
        latest_attempt=recent_attempts[0] if recent_attempts else None,
        skill_meta=skill_meta,
    )
    if continue_item:
        continue_item = dict(continue_item)
        continue_item["recent_label"] = format_recent_activity(continue_item.get("practiced_at"))
        continue_item.update(
            build_skill_card_mastery(
                student_id=uid,
                skill_ids=[continue_item["skill_id"]],
            )[continue_item["skill_id"]]
        )
        continue_item["action_label"] = "繼續練習"
    return {
        "view_mode": "vocational_home",
        "curriculum": VOCATIONAL_KEY,
        "display_name": display_name,
        "username": user.username,
        "primary_class_name": primary["name"] if primary else "",
        "primary_seat_no": primary["seat_no"] if primary else None,
        "class_rows": class_rows,
        "continue_learning": continue_item,
        "weekly_stats": _weekly_stats(uid),
        "volume_cards": _volume_cards(uid, attempts=recent_attempts, skill_meta=skill_meta),
        "mock_exam_cards": mock_exam_cards(),
        "hide_curriculum_switch": True,
    }
