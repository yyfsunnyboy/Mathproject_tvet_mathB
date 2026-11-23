# -*- coding: utf-8 -*-
"""B1 Generator problem-type mastery progression (skill completion by type coverage).

Non-B1 curricula keep the legacy consecutive-correct streak. This module is the
authoritative source for B1 practice-page ``X/Y`` progress where:
  X = distinct MASTERED problem_type_id values
  Y = runtime-usable problem_type_id count from generator inventory
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.exc import OperationalError

STATUS_NOT_STARTED = "NOT_STARTED"
STATUS_PRACTICING = "PRACTICING"
STATUS_REMEDIATION = "REMEDIATION"
STATUS_MASTERED = "MASTERED"

_ASSISTED_SESSION_KEY = "b1_assisted_question_uids"
_WRONG_STREAK_FOR_REMEDIATION = 2

# B2 opt-in allowlist (shared mastery path; not full-volume default).
# Phase-1: chapter-1 named skills.
# Phase-1b (teacher 2026-11-22): chapter-1 A-class practice SubSections with
# TE + facade + Y>=1 (excludes empty 1_4_1 / 1_4_2 shells).
# Phase-2: chapter-2 practice SubSections with runtime-usable types.
# Phase-3: chapter-3 practice SubSections with TE + facade + Y>=1
#          (quality sample 2026-11-23; no separate named skills).
# Other B2 chapters / incomplete shells stay on legacy consecutive-correct.
# Do not convert Progress.consecutive_correct into MASTERED rows.
# Mastery is per (user, skill, problem_type); shared type ids across skills
# do not auto-credit and are not migrated from legacy streaks.
B2_TYPE_MASTERY_PILOT_SKILL_IDS: frozenset[str] = frozenset(
    {
        # Chapter 1 named (phase 1)
        "vh_數學B2_RatioAndRatioValue",
        "vh_數學B2_TrigonometricFunctionsOfAcuteAngles",
        "vh_數學B2_AngleMeasurementAndConversion",
        "vh_數學B2_TrigonometricValuesOfSpecialAngles",
        "vh_數學B2_CoterminalAngles",
        "vh_數學B2_FundamentalTrigonometricIdentities",
        "vh_數學B2_ArcLengthAndAreaOfSector",
        "vh_數學B2_CalculatingFunctionValuesUsingCalculator",
        # Chapter 1 A-class practice SubSections (phase 1b)
        "vh_數學B2_SubSection_1_3_1",
        "vh_數學B2_SubSection_1_3_2",
        "vh_數學B2_SubSection_1_3_4",
        "vh_數學B2_SubSection_1_3_5",
        "vh_數學B2_SubSection_1_3_6",
        "vh_數學B2_SubSection_1_3_7",
        "vh_數學B2_SubSection_1_4_3",
        "vh_數學B2_SubSection_1_4_4",
        # Chapter 2 practice SubSections (phase 2) — B2 ch2 has no separate named skills
        "vh_數學B2_SubSection_2_1_1",
        "vh_數學B2_SubSection_2_1_2",
        "vh_數學B2_SubSection_2_2_3",
        "vh_數學B2_SubSection_2_2_4",
        "vh_數學B2_SubSection_2_2_5",
        # Chapter 3 practice SubSections (phase 3) — vectors; no separate named skills
        "vh_數學B2_SubSection_3_1_1",
        "vh_數學B2_SubSection_3_1_2",
        "vh_數學B2_SubSection_3_1_3",
        "vh_數學B2_SubSection_3_1_4",
        "vh_數學B2_SubSection_3_2_1",
        "vh_數學B2_SubSection_3_2_2",
        "vh_數學B2_SubSection_3_2_3",
        "vh_數學B2_SubSection_3_2_4",
        "vh_數學B2_SubSection_3_2_5",
        "vh_數學B2_SubSection_3_2_6",
        "vh_數學B2_SubSection_3_3_1",
        "vh_數學B2_SubSection_3_3_2",
        "vh_數學B2_SubSection_3_3_3",
        "vh_數學B2_SubSection_3_3_4",
        "vh_數學B2_SubSection_3_3_5",
    }
)


def is_b1_type_mastery_skill(skill_id: str) -> bool:
    """True when problem-type mastery (X/Y) is enabled for this skill.

    Name kept for compatibility: covers full B1 plus the explicit B2 pilot set.
    """
    sid = str(skill_id or "").strip()
    if sid in B2_TYPE_MASTERY_PILOT_SKILL_IDS:
        return True
    if not sid.startswith("vh_數學B1_"):
        return False
    if sid.startswith("outline_") or "SubSection" in sid:
        return False
    return True


def is_type_mastery_skill(skill_id: str) -> bool:
    """Alias for callers that prefer volume-agnostic naming."""
    return is_b1_type_mastery_skill(skill_id)


def normalize_type_id(problem_type_id: str) -> str:
    from core.gencode.services.generator_problem_type_inventory import normalize_problem_type_id

    return normalize_problem_type_id(problem_type_id)


def mark_question_assisted(session: Any, question_uid: str) -> None:
    uid = str(question_uid or "").strip()
    if not uid or session is None:
        return
    raw = session.get(_ASSISTED_SESSION_KEY)
    mapping = dict(raw) if isinstance(raw, dict) else {}
    mapping[uid] = True
    # Bound growth: keep recent UIDs only.
    if len(mapping) > 40:
        keys = list(mapping.keys())[-40:]
        mapping = {k: mapping[k] for k in keys}
    session[_ASSISTED_SESSION_KEY] = mapping
    try:
        session.modified = True
    except Exception:  # noqa: BLE001
        pass


def question_was_assisted(session: Any, question_uid: str) -> bool:
    uid = str(question_uid or "").strip()
    if not uid or session is None:
        return False
    raw = session.get(_ASSISTED_SESSION_KEY)
    if not isinstance(raw, dict):
        return False
    return bool(raw.get(uid))


def clear_question_assisted(session: Any, question_uid: str) -> None:
    uid = str(question_uid or "").strip()
    if not uid or session is None:
        return
    raw = session.get(_ASSISTED_SESSION_KEY)
    if not isinstance(raw, dict) or uid not in raw:
        return
    raw = dict(raw)
    raw.pop(uid, None)
    session[_ASSISTED_SESSION_KEY] = raw
    try:
        session.modified = True
    except Exception:  # noqa: BLE001
        pass


def list_required_problem_types(skill_id: str) -> list[str]:
    """Runtime-usable problem_type_id list for the skill (deduped, normalized)."""
    from core.gencode.services.generator_problem_type_inventory import (
        inventory_skill_generator_problem_types,
    )

    inv = inventory_skill_generator_problem_types(skill_id)
    if inv.get("is_outline"):
        return []
    ids = inv.get("usable_problem_type_ids") or []
    out: list[str] = []
    seen: set[str] = set()
    for raw in ids:
        pt = normalize_type_id(str(raw or ""))
        if not pt or pt in seen:
            continue
        seen.add(pt)
        out.append(pt)
    return out


def get_pass_target_for_skill(skill_id: str) -> int | None:
    """Return type-count target for B1 mastery skills; None means 'use legacy target'."""
    if not is_b1_type_mastery_skill(skill_id):
        return None
    return len(list_required_problem_types(skill_id))


def _section_order_key(section: Any, display_order: Any, skill_id: Any = "") -> tuple:
    """Textbook order within a chapter: section numbers → display_order → skill_id.

    Matches ``practice._chapter_review_ordered_sections`` (not plain display_order,
    which incorrectly interleaves different sections).
    """
    import re

    nums = tuple(int(n) for n in re.findall(r"\d+", str(section or ""))[:3])
    try:
        order = int(display_order or 0)
    except (TypeError, ValueError):
        order = 0
    return (nums, order, str(skill_id or ""))


def _is_practiceable_b1_skill(skill_id: str, info: Any | None) -> bool:
    sid = str(skill_id or "").strip()
    if not is_b1_type_mastery_skill(sid):
        return False
    if info is not None and getattr(info, "is_active", True) is False:
        return False
    return len(list_required_problem_types(sid)) > 0


def _skill_nav_payload(
    *,
    skill_id: str,
    skill_ch_name: str,
    volume: str,
    chapter: str,
    nav_kind: str,
    button_label: str,
    celebration_kind: str = "skill",
) -> dict[str, Any]:
    return {
        "skill_id": skill_id,
        "skill_ch_name": skill_ch_name or skill_id,
        "volume": volume,
        "chapter": chapter,
        "nav_kind": nav_kind,
        "button_label": button_label,
        "celebration_kind": celebration_kind,
        "target": "practice",
    }


def _continue_label(skill_ch_name: str) -> str:
    name = str(skill_ch_name or "").strip() or "下一個技能"
    return f"繼續挑戰：{name}"


def is_skill_complete_for_user(user_id: int | None, skill_id: str) -> bool:
    """True when this student has MASTERED all currently required runtime types."""
    if not user_id:
        return False
    progress = get_skill_type_progress(int(user_id), skill_id)
    return bool(progress.get("complete"))


def _b1_curriculum_anchor(skill_id: str):
    from sqlalchemy import case

    from models import SkillCurriculum, db

    sid = str(skill_id or "").strip()
    return (
        db.session.query(SkillCurriculum)
        .filter(SkillCurriculum.skill_id == sid)
        .order_by(
            case((SkillCurriculum.curriculum == "vocational", 0), else_=1),
            SkillCurriculum.display_order.asc(),
            SkillCurriculum.id.asc(),
        )
        .first()
    )


def list_practiceable_b1_skills_in_chapter(
    *,
    curriculum: str,
    volume: str,
    chapter: str,
) -> list[dict[str, Any]]:
    """Practiceable B1 skills in one chapter, textbook section order."""
    from models import SkillCurriculum, SkillInfo, db

    rows = (
        db.session.query(SkillCurriculum, SkillInfo)
        .outerjoin(SkillInfo, SkillInfo.skill_id == SkillCurriculum.skill_id)
        .filter(
            SkillCurriculum.curriculum == curriculum,
            SkillCurriculum.volume == volume,
            SkillCurriculum.chapter == chapter,
        )
        .all()
    )
    rows_sorted = sorted(
        rows,
        key=lambda pair: _section_order_key(
            getattr(pair[0], "section", ""),
            getattr(pair[0], "display_order", 0),
            getattr(pair[0], "skill_id", ""),
        ),
    )
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row, info in rows_sorted:
        rid = str(row.skill_id or "").strip()
        if not rid or rid in seen:
            continue
        seen.add(rid)
        if not _is_practiceable_b1_skill(rid, info):
            continue
        out.append(
            {
                "skill_id": rid,
                "skill_ch_name": str(getattr(info, "skill_ch_name", "") or "") if info else rid,
                "volume": volume,
                "chapter": chapter,
                "section": str(getattr(row, "section", "") or ""),
                "display_order": int(getattr(row, "display_order", 0) or 0),
            }
        )
    return out


def _first_incomplete(
    rows: list[dict[str, Any]],
    *,
    user_id: int | None,
    skip_skill_id: str | None = None,
) -> dict[str, Any] | None:
    for row in rows:
        rid = row["skill_id"]
        if skip_skill_id and rid == skip_skill_id:
            continue
        if user_id and is_skill_complete_for_user(user_id, rid):
            continue
        return row
    return None


def resolve_next_b1_practice_skill(
    skill_id: str,
    user_id: int | None = None,
    *,
    exclude_current: bool = True,
) -> dict[str, Any]:
    """Resolve B1 next learning target for one student.

    Priority:
      1. Same chapter, after current: first incomplete practiceable skill
      2. Same chapter, before current: first incomplete (backfill)
      3. Later chapters: first incomplete practiceable skill
      4. Volume complete → dashboard

    Skips inactive / outline / empty-shell / already-complete skills.
    ``user_id=None`` keeps structural next-neighbour behaviour (no mastery filter).
    """
    from core.utils import get_chapters_by_curriculum_volume

    sid = str(skill_id or "").strip()
    if not is_b1_type_mastery_skill(sid):
        return {
            "nav_kind": "fallback_dashboard",
            "button_label": "返回學習儀表板",
            "celebration_kind": "skill",
            "target": "dashboard",
            "reason": "not_b1_mastery_skill",
            "skill_id": None,
        }

    current = _b1_curriculum_anchor(sid)
    if current is None:
        return {
            "nav_kind": "fallback_dashboard",
            "button_label": "返回學習儀表板",
            "celebration_kind": "skill",
            "target": "dashboard",
            "reason": "missing_curriculum_row",
            "skill_id": None,
        }

    curriculum = str(current.curriculum or "")
    volume = str(current.volume or "")
    chapter = str(current.chapter or "")
    if not curriculum or not volume or not chapter:
        return {
            "nav_kind": "fallback_dashboard",
            "button_label": "返回學習儀表板",
            "celebration_kind": "skill",
            "target": "dashboard",
            "reason": "incomplete_curriculum_mapping",
            "skill_id": None,
            "volume": volume,
            "chapter": chapter,
        }

    same_chapter = list_practiceable_b1_skills_in_chapter(
        curriculum=curriculum, volume=volume, chapter=chapter
    )
    same_ids = [row["skill_id"] for row in same_chapter]
    idx = same_ids.index(sid) if sid in same_ids else -1

    # 1) After current in same chapter
    after_rows = same_chapter[idx + 1 :] if idx >= 0 else []
    if idx < 0:
        current_key = _section_order_key(current.section, current.display_order, sid)
        after_rows = [
            row
            for row in same_chapter
            if _section_order_key(row["section"], row["display_order"], row["skill_id"])
            > current_key
        ]
    nxt = _first_incomplete(after_rows, user_id=user_id)
    if nxt:
        return _skill_nav_payload(
            skill_id=nxt["skill_id"],
            skill_ch_name=nxt["skill_ch_name"],
            volume=volume,
            chapter=chapter,
            nav_kind="same_chapter",
            button_label=_continue_label(nxt["skill_ch_name"]),
            celebration_kind="skill",
        )

    # 2) Backfill earlier incomplete skills — only when student mastery is known.
    # Without user_id, keep forward-only structural navigation (chapter end → next chapter).
    if user_id:
        before_rows = same_chapter[:idx] if idx >= 0 else []
        if idx < 0:
            current_key = _section_order_key(current.section, current.display_order, sid)
            before_rows = [
                row
                for row in same_chapter
                if _section_order_key(row["section"], row["display_order"], row["skill_id"])
                < current_key
            ]
        nxt = _first_incomplete(
            before_rows,
            user_id=user_id,
            skip_skill_id=sid if exclude_current else None,
        )
        if nxt:
            return _skill_nav_payload(
                skill_id=nxt["skill_id"],
                skill_ch_name=nxt["skill_ch_name"],
                volume=volume,
                chapter=chapter,
                nav_kind="same_chapter_backfill",
                button_label=_continue_label(nxt["skill_ch_name"]),
                celebration_kind="skill",
            )

    chapters = get_chapters_by_curriculum_volume(curriculum, volume) or []
    if chapter not in chapters:
        from core.utils import chapter_natural_sort_key

        chapters = sorted(set(list(chapters) + [chapter]), key=chapter_natural_sort_key)

    try:
        chapter_idx = chapters.index(chapter)
    except ValueError:
        return {
            "nav_kind": "fallback_dashboard",
            "button_label": "返回學習儀表板",
            "celebration_kind": "skill",
            "target": "dashboard",
            "reason": "chapter_not_in_volume_list",
            "skill_id": None,
            "volume": volume,
            "chapter": chapter,
        }

    # Chapter is complete for this student (all practiceable skills done / skipped).
    for next_chapter in chapters[chapter_idx + 1 :]:
        candidates = list_practiceable_b1_skills_in_chapter(
            curriculum=curriculum, volume=volume, chapter=str(next_chapter)
        )
        nxt = _first_incomplete(candidates, user_id=user_id)
        if not nxt:
            continue
        return _skill_nav_payload(
            skill_id=nxt["skill_id"],
            skill_ch_name=nxt["skill_ch_name"],
            volume=volume,
            chapter=str(next_chapter),
            nav_kind="chapter_complete",
            button_label="前往下一章",
            celebration_kind="chapter",
        )

    return {
        "nav_kind": "volume_complete",
        "button_label": "返回學習儀表板",
        "celebration_kind": "volume",
        "target": "dashboard",
        "skill_id": None,
        "volume": volume,
        "chapter": chapter,
        "reason": "all_practiceable_skills_complete_in_volume",
    }


def build_skill_completion_payload(
    *,
    user_id: int,
    skill_id: str,
    was_complete_before: bool,
    persisted: bool,
) -> dict[str, Any]:
    """Authoritative completion fields for check_answer (B1 only)."""
    progress = get_skill_type_progress(user_id, skill_id)
    complete = bool(progress.get("complete"))
    just_completed = bool(
        persisted
        and not was_complete_before
        and complete
        and int(progress.get("total_types") or 0) > 0
    )
    next_nav = (
        resolve_next_b1_practice_skill(skill_id, user_id=user_id, exclude_current=True)
        if just_completed
        else None
    )
    celebration_kind = "skill"
    chapter_just_completed = False
    volume_just_completed = False
    if just_completed and isinstance(next_nav, dict):
        kind = str(next_nav.get("nav_kind") or "")
        if kind == "chapter_complete":
            celebration_kind = "chapter"
            chapter_just_completed = True
        elif kind == "volume_complete":
            celebration_kind = "volume"
            chapter_just_completed = True
            volume_just_completed = True
        else:
            celebration_kind = str(next_nav.get("celebration_kind") or "skill")
        next_nav = dict(next_nav)
        next_nav["celebration_kind"] = celebration_kind

    return {
        "progress": progress,
        "skill_complete": complete,
        "skill_just_completed": just_completed,
        "chapter_just_completed": chapter_just_completed,
        "volume_just_completed": volume_just_completed,
        "celebration_kind": celebration_kind,
        "next_skill": next_nav,
        "next_nav": next_nav,
    }


def _row_query(user_id: int, skill_id: str, problem_type_id: str):
    from models import StudentProblemTypeMastery, db

    return (
        db.session.query(StudentProblemTypeMastery)
        .filter_by(
            user_id=int(user_id),
            skill_id=str(skill_id),
            problem_type_id=str(problem_type_id),
        )
        .first()
    )


def get_skill_type_progress(user_id: int, skill_id: str) -> dict[str, Any]:
    required = list_required_problem_types(skill_id)
    total = len(required)
    rows_by_type: dict[str, Any] = {}
    if total and user_id:
        try:
            from models import StudentProblemTypeMastery, db

            rows = (
                db.session.query(StudentProblemTypeMastery)
                .filter_by(user_id=int(user_id), skill_id=str(skill_id))
                .all()
            )
            for row in rows:
                pt = normalize_type_id(row.problem_type_id)
                if pt:
                    rows_by_type[pt] = row
        except OperationalError:
            # Table not yet migrated in this process — treat as empty progress.
            rows_by_type = {}

    type_states: list[dict[str, Any]] = []
    mastered = 0
    for pt in required:
        row = rows_by_type.get(pt)
        status = str(getattr(row, "status", STATUS_NOT_STARTED) or STATUS_NOT_STARTED)
        if status == STATUS_MASTERED:
            mastered += 1
        type_states.append(
            {
                "problem_type_id": pt,
                "status": status,
                "consecutive_wrong": int(getattr(row, "consecutive_wrong", 0) or 0),
                "needs_independent_verify": bool(getattr(row, "needs_independent_verify", False)),
                "mastered_at": getattr(row, "mastered_at", None),
            }
        )

    complete = bool(total > 0 and mastered >= total)
    return {
        "mode": "problem_type_mastery",
        "skill_id": skill_id,
        "mastered_count": mastered,
        "total_types": total,
        "complete": complete,
        "types": type_states,
        "display_label": (
            f"已掌握題型 {mastered}/{total}"
            if total > 0
            else "暫無可練習題型"
        ),
        # Compatibility aliases for existing streak UI fields.
        "consecutive_correct": mastered,
        "pass_target": total,
    }


def rotation_status_map(user_id: int, skill_id: str) -> dict[str, str]:
    """Map DB mastery → practice_type_rotation statuses (passed/weak/unseen)."""
    from core.practice_type_rotation import STATUS_PASSED, STATUS_UNSEEN, STATUS_WEAK

    progress = get_skill_type_progress(user_id, skill_id)
    out: dict[str, str] = {}
    for row in progress.get("types") or []:
        pt = str(row.get("problem_type_id") or "")
        status = str(row.get("status") or STATUS_NOT_STARTED)
        if status == STATUS_MASTERED:
            out[pt] = STATUS_PASSED
        elif status in {STATUS_REMEDIATION, STATUS_PRACTICING}:
            out[pt] = STATUS_WEAK
        else:
            out[pt] = STATUS_UNSEEN
    return out


def record_type_attempt(
    *,
    user_id: int,
    skill_id: str,
    problem_type_id: str,
    is_correct: bool,
    question_uid: str | None = None,
    practice_attempt_id: int | None = None,
    assisted: bool = False,
    commit: bool = False,
) -> dict[str, Any]:
    """Update per-type mastery for one graded attempt. Idempotent for MASTERED."""
    from models import StudentProblemTypeMastery, db

    if not is_b1_type_mastery_skill(skill_id):
        return {"skipped": True, "reason": "not_b1_mastery_skill"}

    pt = normalize_type_id(problem_type_id)
    if not pt:
        return {"skipped": True, "reason": "missing_problem_type_id"}

    required = set(list_required_problem_types(skill_id))
    if required and pt not in required:
        # Still track off-pool types for evidence, but they do not count toward Y.
        pass

    now = datetime.utcnow()
    row = _row_query(user_id, skill_id, pt)
    if row is None:
        row = StudentProblemTypeMastery(
            user_id=int(user_id),
            skill_id=str(skill_id),
            problem_type_id=pt,
            status=STATUS_NOT_STARTED,
            consecutive_wrong=0,
            needs_independent_verify=False,
            attempt_count=0,
        )
        db.session.add(row)

    row.attempt_count = int(row.attempt_count or 0) + 1
    row.last_attempt_at = now
    if practice_attempt_id:
        row.last_attempt_id = int(practice_attempt_id)
    if question_uid:
        row.last_question_uid = str(question_uid)[:64]

    already_mastered = str(row.status or "") == STATUS_MASTERED

    if is_correct:
        row.consecutive_wrong = 0
        if already_mastered:
            # Repeat correct on mastered type: no change.
            pass
        elif assisted:
            # Hint / step teaching / solution view: keep practicing, require a
            # fresh same-type variant answered independently for MASTERED.
            row.status = STATUS_REMEDIATION
            row.needs_independent_verify = True
        else:
            # Independent correct — including post-remediation verification.
            row.status = STATUS_MASTERED
            row.needs_independent_verify = False
            if row.mastered_at is None:
                row.mastered_at = now
            if practice_attempt_id:
                row.mastery_attempt_id = int(practice_attempt_id)
    else:
        row.consecutive_wrong = int(row.consecutive_wrong or 0) + 1
        if already_mastered:
            # Keep MASTERED; wrongs on this or other types must not revoke it.
            pass
        elif row.consecutive_wrong >= _WRONG_STREAK_FOR_REMEDIATION:
            row.status = STATUS_REMEDIATION
            row.needs_independent_verify = True
        else:
            row.status = STATUS_PRACTICING

    if commit:
        db.session.commit()

    progress = get_skill_type_progress(user_id, skill_id)
    return {
        "skipped": False,
        "problem_type_id": pt,
        "status": row.status,
        "already_mastered": already_mastered,
        "assisted": bool(assisted),
        "progress": progress,
    }
