# -*- coding: utf-8 -*-
"""Teacher-facing student learning analysis (read-only analytics)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_, case, func, or_, text

from models import (
    AdaptiveLearningLog,
    B4Chap2VisibilityAuditLog,
    Class,
    ClassStudent,
    PracticeAttempt,
    SkillCurriculum,
    SkillFamilyBridge,
    SkillInfo,
    User,
    db,
)

# Current runtime does not persist reliable student answer duration.
# adaptive.execution_latency is API latency only — never use for learning time.
LEARNING_TIME_UNAVAILABLE = "—"

VALID_RANGES = frozenset({"all", "today", "7d", "30d"})

STATUS_NO_DATA = "NO_DATA"
STATUS_ATTENTION = "ATTENTION"
STATUS_WATCH = "WATCH"
STATUS_NORMAL = "NORMAL"
STATUS_LOW_SAMPLE = "LOW_SAMPLE"

STATUS_UI = {
    STATUS_NO_DATA: {"label": "⚪ 尚無資料", "css": "status-none"},
    STATUS_ATTENTION: {"label": "🔴 建議介入", "css": "status-attention"},
    STATUS_WATCH: {"label": "🟡 需要留意", "css": "status-watch"},
    STATUS_NORMAL: {"label": "🟢 正常", "css": "status-normal"},
    STATUS_LOW_SAMPLE: {"label": "🔵 資料不足", "css": "status-low-sample"},
}


@dataclass(frozen=True)
class TimeRange:
    key: str
    start: datetime | None
    end: datetime | None


@dataclass(frozen=True)
class PracticeStats:
    total: int = 0
    correct: int = 0
    incorrect: int = 0
    accuracy: float | None = None
    last_activity: datetime | None = None

    @classmethod
    def merge(cls, *items: PracticeStats) -> PracticeStats:
        total = sum(i.total for i in items)
        correct = sum(i.correct for i in items)
        incorrect = total - correct
        accuracy = (correct / total) if total else None
        last_candidates = [i.last_activity for i in items if i.last_activity]
        last_activity = max(last_candidates) if last_candidates else None
        return cls(total=total, correct=correct, incorrect=incorrect, accuracy=accuracy, last_activity=last_activity)


def teacher_analysis_authorized(user: Any) -> bool:
    """Align with b4_chap2_teacher_audit: admin or teacher role."""
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_admin", False):
        return True
    return getattr(user, "role", None) == "teacher"


def parse_time_range(raw: str | None) -> TimeRange:
    key = (raw or "all").strip().lower()
    if key not in VALID_RANGES:
        key = "all"
    now = datetime.utcnow()
    if key == "all":
        return TimeRange(key=key, start=None, end=None)
    if key == "today":
        start = datetime(now.year, now.month, now.day)
        return TimeRange(key=key, start=start, end=now)
    if key == "7d":
        return TimeRange(key=key, start=now - timedelta(days=7), end=now)
    return TimeRange(key=key, start=now - timedelta(days=30), end=now)


def calculate_learning_status(total: int, correct: int) -> dict[str, str]:
    """Return status code, UI label, css class, and human-readable reason."""
    if total <= 0:
        ui = STATUS_UI[STATUS_NO_DATA]
        return {
            "status": STATUS_NO_DATA,
            "label": ui["label"],
            "css": ui["css"],
            "reason": "尚無練習紀錄",
        }

    accuracy = correct / total
    pct = round(accuracy * 100)

    if total < 10:
        ui = STATUS_UI[STATUS_LOW_SAMPLE]
        return {
            "status": STATUS_LOW_SAMPLE,
            "label": ui["label"],
            "css": ui["css"],
            "reason": f"目前只有 {total} 題，樣本不足",
        }

    reason = f"最近 {total} 題正確率 {pct}%"
    if accuracy < 0.60:
        ui = STATUS_UI[STATUS_ATTENTION]
        return {"status": STATUS_ATTENTION, "label": ui["label"], "css": ui["css"], "reason": reason}
    if accuracy < 0.70:
        ui = STATUS_UI[STATUS_WATCH]
        return {
            "status": STATUS_WATCH,
            "label": ui["label"],
            "css": ui["css"],
            "reason": f"目前正確率 {pct}%",
        }
    ui = STATUS_UI[STATUS_NORMAL]
    return {
        "status": STATUS_NORMAL,
        "label": ui["label"],
        "css": ui["css"],
        "reason": f"目前正確率 {pct}%",
    }


def format_accuracy(accuracy: float | None) -> str:
    if accuracy is None:
        return "—"
    return f"{round(accuracy * 100)}%"


def format_learning_time() -> str:
    return LEARNING_TIME_UNAVAILABLE


def format_last_activity(dt: datetime | None) -> str:
    if not dt:
        return "—"
    now = datetime.utcnow()
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    diff = now - dt
    if diff.days == 0:
        return f"今天 {dt.strftime('%H:%M')}"
    if diff.days == 1:
        return "昨天"
    if diff.days < 7:
        return f"{diff.days} 天前"
    return dt.strftime("%Y-%m-%d")


def format_datetime_short(dt: datetime | None) -> str:
    if not dt:
        return "—"
    return dt.strftime("%Y-%m-%d %H:%M")


def student_display_name(user: User) -> str:
    name = (getattr(user, "real_name", None) or "").strip()
    if name:
        return name
    return user.username or "—"


def _apply_time_filter(column, time_range: TimeRange):
    if time_range.start is not None:
        column = column >= time_range.start
        return column
    return None


def _b4_time_filters(time_range: TimeRange) -> list:
    filters = [B4Chap2VisibilityAuditLog.record_kind == "deterministic_answer"]
    if time_range.start is not None:
        filters.append(B4Chap2VisibilityAuditLog.created_at >= time_range.start)
    if time_range.end is not None:
        filters.append(B4Chap2VisibilityAuditLog.created_at <= time_range.end)
    return filters


def _adaptive_time_filters(time_range: TimeRange) -> list:
    filters = []
    if time_range.start is not None:
        filters.append(AdaptiveLearningLog.created_at >= time_range.start)
    if time_range.end is not None:
        filters.append(AdaptiveLearningLog.created_at <= time_range.end)
    return filters


def _practice_attempt_time_filters(time_range: TimeRange) -> list:
    filters = []
    if time_range.start is not None:
        filters.append(PracticeAttempt.created_at >= time_range.start)
    if time_range.end is not None:
        filters.append(PracticeAttempt.created_at <= time_range.end)
    return filters


def get_accessible_classes(user: Any) -> list[Class]:
    if getattr(user, "is_admin", False):
        return db.session.query(Class).order_by(Class.name.asc()).all()
    return (
        db.session.query(Class)
        .filter(Class.teacher_id == user.id)
        .order_by(Class.name.asc())
        .all()
    )


def get_class_for_user(class_id: int, user: Any) -> Class | None:
    q = db.session.query(Class).filter(Class.id == class_id)
    if not getattr(user, "is_admin", False):
        q = q.filter(Class.teacher_id == user.id)
    return q.first()


def get_class_student_ids(class_id: int) -> list[int]:
    rows = (
        db.session.query(ClassStudent.student_id)
        .filter(ClassStudent.class_id == class_id)
        .all()
    )
    return [int(r[0]) for r in rows]


def get_class_students(class_id: int) -> list[User]:
    return (
        db.session.query(User)
        .join(ClassStudent, ClassStudent.student_id == User.id)
        .filter(ClassStudent.class_id == class_id)
        .order_by(ClassStudent.seat_no.asc(), User.username.asc())
        .all()
    )


def get_class_student_memberships(class_id: int) -> dict[int, ClassStudent]:
    rows = (
        db.session.query(ClassStudent)
        .filter(ClassStudent.class_id == class_id)
        .all()
    )
    return {int(r.student_id): r for r in rows}


def verify_student_in_class(student_id: int, class_id: int) -> bool:
    return (
        db.session.query(ClassStudent.id)
        .filter(ClassStudent.class_id == class_id, ClassStudent.student_id == student_id)
        .first()
        is not None
    )


def _load_skill_names() -> dict[str, str]:
    rows = db.session.query(SkillInfo.skill_id, SkillInfo.skill_ch_name).all()
    return {sid: (name or sid) for sid, name in rows}


def _load_skill_unit_map() -> dict[str, dict[str, str]]:
    """Map skill_id -> {volume, chapter, unit_label} using earliest display_order row."""
    rows = (
        db.session.query(
            SkillCurriculum.skill_id,
            SkillCurriculum.volume,
            SkillCurriculum.chapter,
            SkillCurriculum.display_order,
        )
        .order_by(SkillCurriculum.display_order.asc(), SkillCurriculum.id.asc())
        .all()
    )
    out: dict[str, dict[str, str]] = {}
    for skill_id, volume, chapter, _order in rows:
        if skill_id in out:
            continue
        vol = (volume or "").strip()
        chap = (chapter or "").strip()
        label = f"{vol}｜{chap}" if vol and chap else (vol or chap or skill_id)
        out[skill_id] = {"volume": vol, "chapter": chap, "unit_label": label}
    return out


def _load_reliable_family_skill_map() -> dict[str, str]:
    """family_id -> skill_id only when exactly one skill maps to the family."""
    rows = db.session.execute(
        text(
            """
            SELECT family_id, MIN(skill_id) AS skill_id, COUNT(DISTINCT skill_id) AS cnt
            FROM skill_family_bridge
            GROUP BY family_id
            HAVING cnt = 1
            """
        )
    ).fetchall()
    return {str(r[0]): str(r[1]) for r in rows if r[0] and r[1]}


def _stats_from_row(total: int, correct: int, last_activity) -> PracticeStats:
    total = int(total or 0)
    correct = int(correct or 0)
    incorrect = max(total - correct, 0)
    accuracy = (correct / total) if total else None
    return PracticeStats(
        total=total,
        correct=correct,
        incorrect=incorrect,
        accuracy=accuracy,
        last_activity=last_activity,
    )


def _aggregate_b4_by_student(student_ids: list[int], time_range: TimeRange) -> dict[int, PracticeStats]:
    if not student_ids:
        return {}
    q = (
        db.session.query(
            B4Chap2VisibilityAuditLog.student_id,
            func.count(B4Chap2VisibilityAuditLog.id),
            func.sum(case((B4Chap2VisibilityAuditLog.is_correct == True, 1), else_=0)),  # noqa: E712
            func.max(B4Chap2VisibilityAuditLog.created_at),
        )
        .filter(
            B4Chap2VisibilityAuditLog.student_id.in_(student_ids),
            *_b4_time_filters(time_range),
        )
        .group_by(B4Chap2VisibilityAuditLog.student_id)
    )
    out: dict[int, PracticeStats] = {}
    for sid, total, correct, last_at in q.all():
        out[int(sid)] = _stats_from_row(total, correct, last_at)
    return out


def _aggregate_adaptive_by_student(student_ids: list[int], time_range: TimeRange) -> dict[int, PracticeStats]:
    if not student_ids:
        return {}
    filters = [AdaptiveLearningLog.student_id.in_(student_ids), *_adaptive_time_filters(time_range)]
    q = (
        db.session.query(
            AdaptiveLearningLog.student_id,
            func.count(AdaptiveLearningLog.log_id),
            func.sum(case((AdaptiveLearningLog.is_correct == True, 1), else_=0)),  # noqa: E712
            func.max(AdaptiveLearningLog.created_at),
        )
        .filter(*filters)
        .group_by(AdaptiveLearningLog.student_id)
    )
    out: dict[int, PracticeStats] = {}
    for sid, total, correct, last_at in q.all():
        out[int(sid)] = _stats_from_row(total, correct, last_at)
    return out


def _aggregate_practice_by_student(student_ids: list[int], time_range: TimeRange) -> dict[int, PracticeStats]:
    if not student_ids:
        return {}
    q = (
        db.session.query(
            PracticeAttempt.student_id,
            func.count(PracticeAttempt.id),
            func.sum(case((PracticeAttempt.is_correct == True, 1), else_=0)),  # noqa: E712
            func.max(PracticeAttempt.created_at),
        )
        .filter(
            PracticeAttempt.student_id.in_(student_ids),
            *_practice_attempt_time_filters(time_range),
        )
        .group_by(PracticeAttempt.student_id)
    )
    out: dict[int, PracticeStats] = {}
    for sid, total, correct, last_at in q.all():
        out[int(sid)] = _stats_from_row(total, correct, last_at)
    return out


def _merge_student_stats(
    b4_map: dict[int, PracticeStats],
    adaptive_map: dict[int, PracticeStats],
    student_ids: list[int],
    practice_map: dict[int, PracticeStats] | None = None,
) -> dict[int, PracticeStats]:
    merged: dict[int, PracticeStats] = {}
    practice_map = practice_map or {}
    for sid in student_ids:
        merged[sid] = PracticeStats.merge(
            b4_map.get(sid, PracticeStats()),
            adaptive_map.get(sid, PracticeStats()),
            practice_map.get(sid, PracticeStats()),
        )
    return merged


def _class_list_stats(
    classes: list[Class],
    time_range: TimeRange,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cls in classes:
        student_ids = get_class_student_ids(cls.id)
        b4 = _aggregate_b4_by_student(student_ids, time_range)
        adaptive = _aggregate_adaptive_by_student(student_ids, time_range)
        practice = _aggregate_practice_by_student(student_ids, time_range)
        merged = _merge_student_stats(b4, adaptive, student_ids, practice)
        class_stats = PracticeStats.merge(*merged.values()) if merged else PracticeStats()
        attention_count = sum(
            1
            for sid in student_ids
            if calculate_learning_status(merged[sid].total, merged[sid].correct)["status"] == STATUS_ATTENTION
        )
        rows.append(
            {
                "class": cls,
                "student_count": len(student_ids),
                "stats": class_stats,
                "attention_count": attention_count,
                "status": calculate_learning_status(class_stats.total, class_stats.correct),
            }
        )
    return rows


def get_home_summary(classes: list[Class], time_range: TimeRange) -> dict[str, Any]:
    all_student_ids: set[int] = set()
    for cls in classes:
        all_student_ids.update(get_class_student_ids(cls.id))
    student_ids = list(all_student_ids)
    b4 = _aggregate_b4_by_student(student_ids, time_range)
    adaptive = _aggregate_adaptive_by_student(student_ids, time_range)
    practice = _aggregate_practice_by_student(student_ids, time_range)
    merged = _merge_student_stats(b4, adaptive, student_ids, practice)
    overall = PracticeStats.merge(*merged.values()) if merged else PracticeStats()
    return {
        "class_count": len(classes),
        "student_count": len(student_ids),
        "practice_total": overall.total,
        "practice_accuracy": overall.accuracy,
    }


def get_class_overview(class_obj: Class, time_range: TimeRange) -> dict[str, Any]:
    student_ids = get_class_student_ids(class_obj.id)
    b4 = _aggregate_b4_by_student(student_ids, time_range)
    adaptive = _aggregate_adaptive_by_student(student_ids, time_range)
    practice = _aggregate_practice_by_student(student_ids, time_range)
    merged = _merge_student_stats(b4, adaptive, student_ids, practice)
    class_stats = PracticeStats.merge(*merged.values()) if merged else PracticeStats()
    attention_count = sum(
        1
        for sid in student_ids
        if calculate_learning_status(merged[sid].total, merged[sid].correct)["status"] == STATUS_ATTENTION
    )
    return {
        "student_count": len(student_ids),
        "stats": class_stats,
        "attention_count": attention_count,
        "status": calculate_learning_status(class_stats.total, class_stats.correct),
    }


def get_class_students_stats(
    class_obj: Class,
    time_range: TimeRange,
    *,
    search: str = "",
    sort: str = "seat",
    order: str = "asc",
) -> list[dict[str, Any]]:
    students = get_class_students(class_obj.id)
    memberships = get_class_student_memberships(class_obj.id)
    student_ids = [s.id for s in students]
    b4 = _aggregate_b4_by_student(student_ids, time_range)
    adaptive = _aggregate_adaptive_by_student(student_ids, time_range)
    practice = _aggregate_practice_by_student(student_ids, time_range)
    merged = _merge_student_stats(b4, adaptive, student_ids, practice)

    rows: list[dict[str, Any]] = []
    needle = (search or "").strip().lower()
    for student in students:
        display = student_display_name(student)
        if needle and needle not in display.lower() and needle not in (student.username or "").lower():
            continue
        membership = memberships.get(student.id)
        stats = merged.get(student.id, PracticeStats())
        status = calculate_learning_status(stats.total, stats.correct)
        rows.append(
            {
                "student": student,
                "display_name": display,
                "seat_no": membership.seat_no if membership else None,
                "stats": stats,
                "status": status,
            }
        )

    reverse = (order or "asc").lower() == "desc"

    def sort_key(row: dict[str, Any]):
        if sort == "total":
            return row["stats"].total
        if sort == "incorrect":
            return row["stats"].incorrect
        if sort == "accuracy":
            acc = row["stats"].accuracy
            return acc if acc is not None else -1.0
        if sort == "last_activity":
            la = row["stats"].last_activity
            return la or datetime.min
        if sort == "name":
            return row["display_name"].lower()
        seat = row.get("seat_no")
        return (seat is None, seat if seat is not None else 9999, row["display_name"].lower())

    rows.sort(key=sort_key, reverse=reverse)
    return rows


def get_attention_students(student_rows: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    attention = [r for r in student_rows if r["status"]["status"] == STATUS_ATTENTION]
    attention.sort(key=lambda r: (r["stats"].accuracy if r["stats"].accuracy is not None else 1.0))
    return attention[:limit]


def _unit_key_from_skill(skill_id: str, unit_map: dict[str, dict[str, str]]) -> tuple[str, str, str, str]:
    """Return (kind, volume, chapter, unit_label). kind is 'curriculum' or 'skill'."""
    info = unit_map.get(skill_id)
    if info and info.get("volume") and info.get("chapter"):
        return "curriculum", info["volume"], info["chapter"], info["unit_label"]
    return "skill", "", "", skill_id


def _aggregate_b4_by_skill(student_id: int, time_range: TimeRange) -> dict[str, PracticeStats]:
    q = (
        db.session.query(
            B4Chap2VisibilityAuditLog.skill_id,
            func.count(B4Chap2VisibilityAuditLog.id),
            func.sum(case((B4Chap2VisibilityAuditLog.is_correct == True, 1), else_=0)),  # noqa: E712
            func.max(B4Chap2VisibilityAuditLog.created_at),
        )
        .filter(B4Chap2VisibilityAuditLog.student_id == student_id, *_b4_time_filters(time_range))
        .group_by(B4Chap2VisibilityAuditLog.skill_id)
    )
    return {sid: _stats_from_row(t, c, la) for sid, t, c, la in q.all()}


def _aggregate_practice_by_skill(student_id: int, time_range: TimeRange) -> dict[str, PracticeStats]:
    q = (
        db.session.query(
            PracticeAttempt.skill_id,
            func.count(PracticeAttempt.id),
            func.sum(case((PracticeAttempt.is_correct == True, 1), else_=0)),  # noqa: E712
            func.max(PracticeAttempt.created_at),
        )
        .filter(
            PracticeAttempt.student_id == student_id,
            *_practice_attempt_time_filters(time_range),
        )
        .group_by(PracticeAttempt.skill_id)
    )
    return {sid: _stats_from_row(t, c, la) for sid, t, c, la in q.all()}


def _aggregate_adaptive_mapped_by_skill(
    student_id: int,
    time_range: TimeRange,
    family_map: dict[str, str],
) -> dict[str, PracticeStats]:
    if not family_map:
        return {}
    family_ids = list(family_map.keys())
    filters = [
        AdaptiveLearningLog.student_id == student_id,
        AdaptiveLearningLog.target_family_id.in_(family_ids),
        *_adaptive_time_filters(time_range),
    ]
    rows = (
        db.session.query(
            AdaptiveLearningLog.target_family_id,
            AdaptiveLearningLog.is_correct,
            AdaptiveLearningLog.created_at,
        )
        .filter(*filters)
        .all()
    )
    buckets: dict[str, list[tuple[bool, datetime | None]]] = {}
    for family_id, is_correct, created_at in rows:
        skill_id = family_map.get(str(family_id))
        if not skill_id:
            continue
        buckets.setdefault(skill_id, []).append((bool(is_correct), created_at))

    out: dict[str, PracticeStats] = {}
    for skill_id, items in buckets.items():
        total = len(items)
        correct = sum(1 for ok, _ in items if ok)
        last_at = max((ts for _, ts in items if ts), default=None)
        out[skill_id] = _stats_from_row(total, correct, last_at)
    return out


def get_student_overview(student: User, time_range: TimeRange) -> dict[str, Any]:
    b4 = _aggregate_b4_by_student([student.id], time_range).get(student.id, PracticeStats())
    adaptive = _aggregate_adaptive_by_student([student.id], time_range).get(student.id, PracticeStats())
    practice = _aggregate_practice_by_student([student.id], time_range).get(student.id, PracticeStats())
    stats = PracticeStats.merge(b4, adaptive, practice)
    return {
        "display_name": student_display_name(student),
        "stats": stats,
        "status": calculate_learning_status(stats.total, stats.correct),
    }


def get_student_units(student_id: int, time_range: TimeRange) -> list[dict[str, Any]]:
    unit_map = _load_skill_unit_map()
    skill_names = _load_skill_names()
    family_map = _load_reliable_family_skill_map()

    b4_by_skill = _aggregate_b4_by_skill(student_id, time_range)
    adaptive_by_skill = _aggregate_adaptive_mapped_by_skill(student_id, time_range, family_map)
    practice_by_skill = _aggregate_practice_by_skill(student_id, time_range)

    unit_buckets: dict[tuple[str, str, str], dict[str, Any]] = {}

    def add_skill(skill_id: str, stats: PracticeStats) -> None:
        kind, volume, chapter, label = _unit_key_from_skill(skill_id, unit_map)
        if kind == "curriculum":
            key = ("curriculum", volume, chapter)
            display = label
        else:
            key = ("skill", skill_id, "")
            display = skill_names.get(skill_id, skill_id)
        if key not in unit_buckets:
            unit_buckets[key] = {
                "kind": key[0],
                "volume": volume,
                "chapter": chapter,
                "skill_id": skill_id if key[0] == "skill" else "",
                "unit_label": display,
                "stats": PracticeStats(),
            }
        unit_buckets[key]["stats"] = PracticeStats.merge(unit_buckets[key]["stats"], stats)

    for skill_id, stats in b4_by_skill.items():
        add_skill(skill_id, stats)
    for skill_id, stats in adaptive_by_skill.items():
        add_skill(skill_id, stats)
    for skill_id, stats in practice_by_skill.items():
        add_skill(skill_id, stats)

    rows: list[dict[str, Any]] = []
    for data in unit_buckets.values():
        stats: PracticeStats = data["stats"]
        rows.append(
            {
                **data,
                "stats": stats,
                "status": calculate_learning_status(stats.total, stats.correct),
            }
        )
    rows.sort(key=lambda r: (-r["stats"].total, r["unit_label"]))
    return rows


def _skills_for_unit(
    volume: str,
    chapter: str,
    skill_unit: str | None,
    unit_map: dict[str, dict[str, str]],
) -> set[str]:
    if skill_unit:
        return {skill_unit}
    skills: set[str] = set()
    for skill_id, info in unit_map.items():
        if info.get("volume") == volume and info.get("chapter") == chapter:
            skills.add(skill_id)
    return skills


def get_student_unit_detail(
    student_id: int,
    *,
    volume: str | None,
    chapter: str | None,
    skill_unit: str | None,
    time_range: TimeRange,
) -> dict[str, Any]:
    unit_map = _load_skill_unit_map()
    skill_names = _load_skill_names()
    family_map = _load_reliable_family_skill_map()

    if skill_unit:
        unit_label = skill_names.get(skill_unit, skill_unit)
        skill_ids = {skill_unit}
    else:
        vol = (volume or "").strip()
        chap = (chapter or "").strip()
        unit_label = f"{vol}｜{chap}" if vol and chap else "—"
        skill_ids = _skills_for_unit(vol, chap, None, unit_map)

    b4_by_skill = _aggregate_b4_by_skill(student_id, time_range)
    adaptive_by_skill = _aggregate_adaptive_mapped_by_skill(student_id, time_range, family_map)
    practice_by_skill = _aggregate_practice_by_skill(student_id, time_range)

    unit_stats = PracticeStats()
    skill_rows: list[dict[str, Any]] = []
    for skill_id in skill_ids:
        stats = PracticeStats.merge(
            b4_by_skill.get(skill_id, PracticeStats()),
            adaptive_by_skill.get(skill_id, PracticeStats()),
            practice_by_skill.get(skill_id, PracticeStats()),
        )
        if stats.total == 0:
            continue
        unit_stats = PracticeStats.merge(unit_stats, stats)
        skill_rows.append(
            {
                "skill_id": skill_id,
                "skill_name": skill_names.get(skill_id, skill_id),
                "stats": stats,
                "status": calculate_learning_status(stats.total, stats.correct),
            }
        )
    skill_rows.sort(key=lambda r: (-r["stats"].total, r["skill_name"]))

    trend = get_unit_trend(student_id, skill_ids, time_range)
    recent = get_recent_attempts(student_id, skill_ids, time_range, limit=30)
    latest_apr = _latest_apr_for_skills(student_id, skill_ids, family_map, time_range)

    return {
        "unit_label": unit_label,
        "volume": volume or "",
        "chapter": chapter or "",
        "skill_unit": skill_unit or "",
        "stats": unit_stats,
        "status": calculate_learning_status(unit_stats.total, unit_stats.correct),
        "skills": skill_rows,
        "trend": trend,
        "recent_attempts": recent,
        "latest_apr": latest_apr,
    }


def get_unit_trend(student_id: int, skill_ids: set[str], time_range: TimeRange) -> dict[str, Any]:
    if not skill_ids:
        return {"labels": [], "chart_values": [], "has_enough": False}

    day_expr_b4 = func.date(B4Chap2VisibilityAuditLog.created_at)
    b4_q = (
        db.session.query(
            day_expr_b4.label("day"),
            func.count(B4Chap2VisibilityAuditLog.id),
            func.sum(case((B4Chap2VisibilityAuditLog.is_correct == True, 1), else_=0)),  # noqa: E712
        )
        .filter(
            B4Chap2VisibilityAuditLog.student_id == student_id,
            B4Chap2VisibilityAuditLog.skill_id.in_(list(skill_ids)),
            *_b4_time_filters(time_range),
        )
        .group_by(day_expr_b4)
    )

    family_map = _load_reliable_family_skill_map()
    reverse_family = {v: k for k, v in family_map.items() if v in skill_ids}
    adaptive_days: dict[str, list[bool]] = {}

    if reverse_family:
        day_expr_a = func.date(AdaptiveLearningLog.created_at)
        a_q = (
            db.session.query(
                day_expr_a.label("day"),
                AdaptiveLearningLog.is_correct,
            )
            .filter(
                AdaptiveLearningLog.student_id == student_id,
                AdaptiveLearningLog.target_family_id.in_(list(reverse_family.keys())),
                *_adaptive_time_filters(time_range),
            )
            .all()
        )
        for day, is_correct in a_q:
            adaptive_days.setdefault(str(day), []).append(bool(is_correct))

    day_stats: dict[str, PracticeStats] = {}
    for day, total, correct in b4_q.all():
        day_stats[str(day)] = _stats_from_row(total, correct, None)

    for day, results in adaptive_days.items():
        total = len(results)
        correct = sum(1 for ok in results if ok)
        existing = day_stats.get(day, PracticeStats())
        day_stats[day] = PracticeStats.merge(existing, _stats_from_row(total, correct, None))

    day_expr_p = func.date(PracticeAttempt.created_at)
    practice_q = (
        db.session.query(
            day_expr_p.label("day"),
            func.count(PracticeAttempt.id),
            func.sum(case((PracticeAttempt.is_correct == True, 1), else_=0)),  # noqa: E712
        )
        .filter(
            PracticeAttempt.student_id == student_id,
            PracticeAttempt.skill_id.in_(list(skill_ids)),
            *_practice_attempt_time_filters(time_range),
        )
        .group_by(day_expr_p)
    )
    for day, total, correct in practice_q.all():
        existing = day_stats.get(str(day), PracticeStats())
        day_stats[str(day)] = PracticeStats.merge(existing, _stats_from_row(total, correct, None))

    if not day_stats:
        return {"labels": [], "chart_values": [], "has_enough": False}

    sorted_days = sorted(day_stats.keys())
    labels = []
    chart_values = []
    for day in sorted_days:
        stats = day_stats[day]
        labels.append(day[5:] if len(day) >= 10 else day)
        chart_values.append(round((stats.accuracy or 0) * 100))

    return {"labels": labels, "chart_values": chart_values, "has_enough": len(sorted_days) >= 2}


def _latest_apr_for_skills(
    student_id: int,
    skill_ids: set[str],
    family_map: dict[str, str],
    time_range: TimeRange,
) -> float | None:
    reverse = {v: k for k, v in family_map.items() if v in skill_ids}
    if not reverse:
        return None
    filters = [
        AdaptiveLearningLog.student_id == student_id,
        AdaptiveLearningLog.target_family_id.in_(list(reverse.keys())),
        *_adaptive_time_filters(time_range),
    ]
    row = (
        db.session.query(AdaptiveLearningLog.current_apr)
        .filter(*filters)
        .order_by(AdaptiveLearningLog.created_at.desc(), AdaptiveLearningLog.log_id.desc())
        .first()
    )
    if not row:
        return None
    return float(row[0])


def get_recent_attempts(
    student_id: int,
    skill_ids: set[str],
    time_range: TimeRange,
    *,
    limit: int = 30,
) -> list[dict[str, Any]]:
    if not skill_ids:
        return []

    skill_names = _load_skill_names()
    family_map = _load_reliable_family_skill_map()
    reverse_family = {v: k for k, v in family_map.items() if v in skill_ids}

    b4_rows = (
        db.session.query(B4Chap2VisibilityAuditLog)
        .filter(
            B4Chap2VisibilityAuditLog.student_id == student_id,
            B4Chap2VisibilityAuditLog.skill_id.in_(list(skill_ids)),
            *_b4_time_filters(time_range),
        )
        .order_by(B4Chap2VisibilityAuditLog.created_at.desc(), B4Chap2VisibilityAuditLog.id.desc())
        .limit(limit)
        .all()
    )

    attempts: list[dict[str, Any]] = []
    for row in b4_rows:
        attempts.append(
            {
                "source": "b4",
                "created_at": row.created_at,
                "skill_id": row.skill_id,
                "skill_name": skill_names.get(row.skill_id, row.skill_id),
                "problem_type": row.problem_type_id,
                "question_text": None,
                "user_answer": row.user_answer,
                "expected_answer": row.expected_answer,
                "is_correct": bool(row.is_correct),
                "apr": None,
            }
        )

    practice_rows = (
        db.session.query(PracticeAttempt)
        .filter(
            PracticeAttempt.student_id == student_id,
            PracticeAttempt.skill_id.in_(list(skill_ids)),
            *_practice_attempt_time_filters(time_range),
        )
        .order_by(PracticeAttempt.created_at.desc(), PracticeAttempt.id.desc())
        .limit(limit)
        .all()
    )
    for row in practice_rows:
        attempts.append(
            {
                "source": row.source or "general_practice",
                "created_at": row.created_at,
                "skill_id": row.skill_id,
                "skill_name": skill_names.get(row.skill_id, row.skill_id),
                "problem_type": row.problem_type_id,
                "question_text": row.question_text,
                "user_answer": row.user_answer,
                "expected_answer": row.expected_answer,
                "is_correct": bool(row.is_correct),
                "apr": None,
            }
        )

    if reverse_family:
        adaptive_rows = (
            db.session.query(AdaptiveLearningLog)
            .filter(
                AdaptiveLearningLog.student_id == student_id,
                AdaptiveLearningLog.target_family_id.in_(list(reverse_family.keys())),
                *_adaptive_time_filters(time_range),
            )
            .order_by(AdaptiveLearningLog.created_at.desc(), AdaptiveLearningLog.log_id.desc())
            .limit(limit)
            .all()
        )
        for row in adaptive_rows:
            skill_id = family_map.get(str(row.target_family_id), "")
            attempts.append(
                {
                    "source": "adaptive",
                    "created_at": row.created_at,
                    "skill_id": skill_id,
                    "skill_name": skill_names.get(skill_id, row.target_family_id),
                    "problem_type": row.target_family_id,
                    "user_answer": None,
                    "expected_answer": None,
                    "is_correct": bool(row.is_correct),
                    "apr": float(row.current_apr),
                }
            )

    attempts.sort(key=lambda a: a["created_at"] or datetime.min, reverse=True)
    return attempts[:limit]


def build_analysis_page_context(
    user: Any,
    *,
    class_id: int | None,
    student_id: int | None,
    volume: str | None,
    chapter: str | None,
    skill_unit: str | None,
    time_range: TimeRange,
    search: str = "",
    sort: str = "name",
    order: str = "asc",
) -> dict[str, Any]:
    """Build template context; set error='not_found' when access denied."""
    classes = get_accessible_classes(user)
    ctx: dict[str, Any] = {
        "view": "home",
        "time_range": time_range,
        "classes": classes,
        "breadcrumb": [{"label": "學生分析", "url": None}],
        "back_url": None,
        "error": None,
    }

    if not class_id:
        class_rows = _class_list_stats(classes, time_range)
        ctx.update(
            {
                "view": "home",
                "class_rows": class_rows,
                "summary": get_home_summary(classes, time_range),
            }
        )
        return ctx

    class_obj = get_class_for_user(class_id, user)
    if not class_obj:
        return {"error": "not_found", "view": "home", "time_range": time_range, "classes": classes}

    base_params = {"class_id": class_id, "range": time_range.key}
    ctx["class_obj"] = class_obj
    ctx["breadcrumb"].append({"label": class_obj.name, "url": "class"})

    if not student_id:
        student_rows = get_class_students_stats(
            class_obj, time_range, search=search, sort=sort, order=order
        )
        ctx.update(
            {
                "view": "class",
                "class_overview": get_class_overview(class_obj, time_range),
                "student_rows": student_rows,
                "attention_students": get_attention_students(student_rows),
                "search": search,
                "sort": sort,
                "order": order,
                "back_url": {"endpoint": "teacher_analysis", "params": {"range": time_range.key}},
            }
        )
        return ctx

    if not verify_student_in_class(student_id, class_id):
        return {"error": "not_found", "view": "home", "time_range": time_range, "classes": classes}

    student = db.session.get(User, student_id)
    if not student:
        return {"error": "not_found", "view": "home", "time_range": time_range, "classes": classes}

    student_name = student_display_name(student)
    ctx["student"] = student
    ctx["breadcrumb"].append({"label": student_name, "url": "student"})

    has_unit = bool((volume and chapter) or skill_unit)
    if not has_unit:
        ctx.update(
            {
                "view": "student",
                "student_overview": get_student_overview(student, time_range),
                "unit_rows": get_student_units(student_id, time_range),
                "back_url": {
                    "endpoint": "teacher_analysis",
                    "params": {**base_params, "range": time_range.key},
                },
            }
        )
        return ctx

    unit_detail = get_student_unit_detail(
        student_id,
        volume=volume,
        chapter=chapter,
        skill_unit=skill_unit,
        time_range=time_range,
    )
    ctx["breadcrumb"].append({"label": unit_detail["unit_label"], "url": None})
    ctx.update(
        {
            "view": "unit",
            "unit_detail": unit_detail,
            "student_overview": get_student_overview(student, time_range),
            "back_url": {
                "endpoint": "teacher_analysis",
                "params": {
                    **base_params,
                    "student_id": student_id,
                    "range": time_range.key,
                },
            },
        }
    )
    return ctx
