# -*- coding: utf-8 -*-
"""Deterministic section-level outline_* ensure (authoritative metadata only).

Creates SkillInfo(outline_*) + SkillCurriculum(outline_*) for a single section
when chapter/section are known from trusted sources — never from Gemini free output.

Does not commit; callers own the transaction boundary.
Does not create vh_* formal skills or TextbookExample rows.
"""

from __future__ import annotations

import re
from typing import Any

from models import SkillCurriculum, SkillInfo, db

# Trusted sources only. Phase3 Gemini free output is intentionally excluded.
AUTHORITATIVE_OUTLINE_SOURCES = frozenset(
    {
        "filename",
        "curriculum_info",
        "docx_section",
        "authoritative_source_context",
        "form_confirmed",
        "v3_source_context",
    }
)

_PLACEHOLDER_RE = re.compile(r"<[^>]+>")


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def outline_display_order_from_section_code(section_code: str) -> int:
    """Deterministic display_order from section code (1-1→11, 2-3→23, 1-10→110).

    PDF outline sync uses a book-wide running index; a single-section ensure cannot
    know that sequence. Lookup does not depend on display_order. Using the digit
    payload of the section code is idempotent and stable across re-runs.
    """
    code = _normalize_space(section_code)
    digits = re.sub(r"[^0-9]", "", code)
    if digits.isdigit():
        return int(digits)
    return 0


def is_authoritative_outline_source(authority_source: str) -> bool:
    return str(authority_source or "").strip() in AUTHORITATIVE_OUTLINE_SOURCES


def _looks_like_placeholder(text: str) -> bool:
    t = str(text or "")
    return bool(_PLACEHOLDER_RE.search(t)) or t.strip() in {
        "<chapter_title>",
        "<section_title>",
        "<section_code>",
    }


def validate_authoritative_section_outline_metadata(
    *,
    curriculum: str,
    volume: str,
    chapter: str,
    section: str = "",
    section_code: str = "",
    authority_source: str = "",
) -> tuple[bool, str]:
    if not is_authoritative_outline_source(authority_source):
        return False, "non_authoritative_source"
    if not _normalize_space(curriculum):
        return False, "missing_curriculum"
    if not _normalize_space(volume):
        return False, "missing_volume"
    if not _normalize_space(chapter) or _looks_like_placeholder(chapter):
        return False, "missing_or_placeholder_chapter"
    if not _normalize_space(section) and not _normalize_space(section_code):
        return False, "missing_section"
    if _looks_like_placeholder(section) or _looks_like_placeholder(section_code):
        return False, "placeholder_section"
    return True, ""


def _canonical_section_pair(section_code: str, section: str) -> tuple[str, str]:
    from core.textbook_processor_v2 import _canonical_outline_section_title

    return _canonical_outline_section_title(
        str(section_code or "").strip(),
        str(section or "").strip(),
    )


def _canonical_chapter_title(chapter: str, curriculum_info: dict | None = None) -> str:
    from core.textbook_processor_v2 import _canonical_outline_chapter_title

    return _canonical_outline_chapter_title(
        str(chapter or "").strip(),
        curriculum_info or {},
    )


def build_outline_skill_id_for_section(
    *,
    curriculum: str,
    volume: str,
    section_code: str = "",
    section: str = "",
) -> tuple[str, str, str]:
    """Return (skill_id, section_code, canonical_section_title) using B1 ID rules."""
    from core.textbook_processor_v2 import _outline_placeholder_skill_id

    code, title = _canonical_section_pair(section_code, section)
    if not code or not title:
        return "", code, title
    skill_id = _outline_placeholder_skill_id(curriculum, volume, title)
    return skill_id, code, title


def _find_existing_outline_curriculum_row(
    *,
    curriculum: str,
    volume: str,
    section_code: str,
    skill_id: str,
) -> SkillCurriculum | None:
    """Find outline row by skill_id or section-code outline lookup."""
    by_sid = (
        SkillCurriculum.query.filter_by(
            curriculum=curriculum,
            volume=volume,
            skill_id=skill_id,
        )
        .order_by(SkillCurriculum.display_order.asc(), SkillCurriculum.id.asc())
        .first()
    )
    if by_sid is not None:
        return by_sid

    from core.textbook_import_authority import ImportAuthorityResolver

    return ImportAuthorityResolver.lookup_outline_row(curriculum, volume, section_code)


def _meta_equal(a: str, b: str) -> bool:
    return _normalize_space(a) == _normalize_space(b)


def ensure_section_outline_from_authoritative_metadata_v2(
    *,
    curriculum: str,
    volume: str,
    chapter: str,
    section: str = "",
    section_code: str = "",
    grade: int | None = None,
    authority_source: str = "",
    dry_run: bool = True,
    flush: bool = True,
    curriculum_info: dict | None = None,
) -> dict[str, Any]:
    """Ensure section-level outline_* SkillInfo + SkillCurriculum.

    Returns action in: would_create | created | existing | conflict | invalid_authority
    Never commits. Optionally flushes when writing.
    """
    ok, reason = validate_authoritative_section_outline_metadata(
        curriculum=curriculum,
        volume=volume,
        chapter=chapter,
        section=section,
        section_code=section_code,
        authority_source=authority_source,
    )
    base = {
        "curriculum": _normalize_space(curriculum),
        "volume": _normalize_space(volume),
        "chapter": _normalize_space(chapter),
        "section": _normalize_space(section),
        "section_code": _normalize_space(section_code),
        "authority_source": _normalize_space(authority_source),
        "skill_id": None,
        "dry_run": bool(dry_run),
        "wrote": False,
        "skill_info_created": False,
        "skill_curriculum_created": False,
    }
    if not ok:
        return {
            **base,
            "action": "invalid_authority",
            "reason": reason,
        }

    info = dict(curriculum_info or {})
    info.setdefault("curriculum", curriculum)
    info.setdefault("volume", volume)
    info.setdefault("grade", grade)

    from core.textbook_processor import grade_for_vocational_math_volume
    from core.textbook_processor_v2 import (
        _ensure_outline_skill_info_v2,
        _resolve_outline_grade,
    )

    chapter_title = _canonical_chapter_title(chapter, info)
    skill_id, code, section_title = build_outline_skill_id_for_section(
        curriculum=_normalize_space(curriculum),
        volume=_normalize_space(volume),
        section_code=section_code,
        section=section,
    )
    base.update(
        {
            "chapter": chapter_title,
            "section": section_title,
            "section_code": code,
            "skill_id": skill_id,
        }
    )
    if not skill_id or not code or not section_title:
        return {
            **base,
            "action": "invalid_authority",
            "reason": "canonical_section_failed",
        }

    mapped_grade = grade_for_vocational_math_volume(volume)
    if mapped_grade is not None:
        resolved_grade = mapped_grade
    else:
        resolved_grade = int(grade) if grade is not None else _resolve_outline_grade(info)
    display_order = outline_display_order_from_section_code(code)

    existing = _find_existing_outline_curriculum_row(
        curriculum=_normalize_space(curriculum),
        volume=_normalize_space(volume),
        section_code=code,
        skill_id=skill_id,
    )
    if existing is not None:
        existing_meta = {
            "skill_id": str(existing.skill_id or ""),
            "chapter": str(existing.chapter or ""),
            "section": str(existing.section or ""),
            "paragraph": existing.paragraph,
            "grade": int(existing.grade) if existing.grade is not None else None,
            "display_order": int(existing.display_order or 0),
        }
        incoming_meta = {
            "skill_id": skill_id,
            "chapter": chapter_title,
            "section": section_title,
            "paragraph": None,
            "grade": resolved_grade,
            "display_order": display_order,
        }
        same_coords = _meta_equal(existing_meta["chapter"], chapter_title) and _meta_equal(
            existing_meta["section"], section_title
        )
        same_sid = _meta_equal(existing_meta["skill_id"], skill_id)
        if not same_coords or not same_sid:
            return {
                **base,
                "action": "conflict",
                "reason": "existing_outline_metadata_mismatch",
                "existing": existing_meta,
                "incoming": incoming_meta,
            }
        return {
            **base,
            "action": "existing",
            "existing": existing_meta,
            "incoming": incoming_meta,
        }

    if dry_run:
        return {
            **base,
            "action": "would_create",
            "incoming": {
                "skill_id": skill_id,
                "chapter": chapter_title,
                "section": section_title,
                "paragraph": None,
                "grade": resolved_grade,
                "display_order": display_order,
                "difficulty_level": 1,
            },
        }

    # Write path: add/flush only — no commit.
    skill_info_existed = db.session.get(SkillInfo, skill_id) is not None
    _ensure_outline_skill_info_v2(
        skill_id=skill_id,
        section_title=section_title,
        chapter_title=chapter_title,
        curriculum=_normalize_space(curriculum),
        volume=_normalize_space(volume),
        grade=resolved_grade,
    )
    row = SkillCurriculum(
        skill_id=skill_id,
        curriculum=_normalize_space(curriculum),
        grade=resolved_grade,
        volume=_normalize_space(volume),
        chapter=chapter_title,
        section=section_title,
        paragraph=None,
        display_order=display_order,
        difficulty_level=1,
    )
    db.session.add(row)
    if flush:
        db.session.flush()

    return {
        **base,
        "action": "created",
        "wrote": True,
        "skill_info_created": not skill_info_existed,
        "skill_curriculum_created": True,
        "incoming": {
            "skill_id": skill_id,
            "chapter": chapter_title,
            "section": section_title,
            "paragraph": None,
            "grade": resolved_grade,
            "display_order": display_order,
            "difficulty_level": 1,
        },
        "curriculum_row_id": getattr(row, "id", None),
    }


def ensure_section_outline_from_curriculum_info(
    curriculum_info: dict,
    *,
    authority_source: str = "curriculum_info",
    dry_run: bool = True,
    flush: bool = True,
) -> dict[str, Any]:
    """Convenience wrapper over curriculum_info authoritative fields."""
    info = curriculum_info if isinstance(curriculum_info, dict) else {}
    src = str(info.get("authority_source") or authority_source or "").strip()
    return ensure_section_outline_from_authoritative_metadata_v2(
        curriculum=str(info.get("curriculum") or "").strip(),
        volume=str(info.get("volume") or "").strip(),
        chapter=str(info.get("chapter") or info.get("chapter_title") or "").strip(),
        section=str(info.get("section") or info.get("section_title") or "").strip(),
        section_code=str(info.get("section_code") or "").strip(),
        grade=info.get("grade"),
        authority_source=src,
        dry_run=dry_run,
        flush=flush,
        curriculum_info=info,
    )
