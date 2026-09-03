# -*- coding: utf-8 -*-
"""Deterministic formal concept (vh_*) ensure from authoritative DOCX headings.

Creates SkillInfo(vh_*) + SkillCurriculum(paragraph=concept_name) under an
existing section outline_*. Does not commit; does not call Gemini when
allow_ai_description=False (default for this API).
"""

from __future__ import annotations

import re
from typing import Any

from models import SkillCurriculum, SkillInfo, db

AUTHORITATIVE_CONCEPT_SOURCES = frozenset(
    {
        "docx_heading",
        "deterministic_docx_heading",
        "authoritative_source_context",
        "reviewed_heading",
    }
)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def is_authoritative_concept_source(authority_source: str) -> bool:
    return _norm(authority_source) in AUTHORITATIVE_CONCEPT_SOURCES


def display_order_from_concept_code(concept_code: str) -> int:
    """Match V2: 1-1.3 → 3."""
    m = re.match(r"^\d+-\d+\.(\d+)$", _norm(concept_code))
    if m:
        return int(m.group(1))
    return 0


def build_formal_skill_id_from_en_id(*, volume: str, concept_en_id: str) -> str:
    from core.textbook_processor import parse_volume
    from core.utils import normalize_vocational_math_skill_id

    subject, vol_num = parse_volume(volume)
    clean = re.sub(r"[^a-zA-Z0-9_]", "", str(concept_en_id or "")) or "UnknownConcept"
    if subject == "B" and vol_num is not None:
        return normalize_vocational_math_skill_id(subject, str(vol_num), clean)
    return f"vh_{clean}"


def get_section_formal_skill_candidates(
    *,
    curriculum: str,
    volume: str,
    section: str = "",
    section_code: str = "",
    chapter: str = "",
) -> list[dict[str, Any]]:
    """Formal vh_* candidates for a section — excludes outline_*."""
    from core.textbook_processor_v2 import (
        _canonical_outline_section_title,
        _get_formal_skills_for_section_v2,
        extract_section_code_from_title,
    )

    code = _norm(section_code) or extract_section_code_from_title(section)
    _, sec_title = _canonical_outline_section_title(code, section or code)
    rows = _get_formal_skills_for_section_v2(
        curriculum=_norm(curriculum),
        volume=_norm(volume),
        chapter_title=_norm(chapter),
        section_title=sec_title,
        section_code=code,
    )
    # Attach display_order from SkillCurriculum when available.
    out: list[dict[str, Any]] = []
    for item in rows:
        sid = str(item.get("skill_id") or "").strip()
        if not sid.startswith("vh_") or sid.startswith("outline_"):
            continue
        sc = (
            SkillCurriculum.query.filter_by(
                curriculum=_norm(curriculum),
                volume=_norm(volume),
                skill_id=sid,
            )
            .order_by(SkillCurriculum.display_order.asc(), SkillCurriculum.id.asc())
            .first()
        )
        out.append(
            {
                "skill_id": sid,
                "concept_name": str(item.get("concept_name") or "").strip(),
                "concept_en_id": str(item.get("concept_en_id") or "").strip(),
                "paragraph": str(item.get("paragraph") or "").strip(),
                "display_order": int(getattr(sc, "display_order", 0) or 0) if sc else 0,
                "chapter": str(getattr(sc, "chapter", "") or "") if sc else _norm(chapter),
                "section": str(getattr(sc, "section", "") or "") if sc else sec_title,
            }
        )
    out.sort(key=lambda r: (int(r.get("display_order") or 0), str(r.get("skill_id") or "")))
    return out


def ensure_formal_concept_from_authoritative_heading_v2(
    *,
    curriculum: str,
    volume: str,
    chapter: str,
    section: str,
    concept_code: str,
    concept_name: str,
    concept_en_id: str,
    section_code: str = "",
    grade: int | None = None,
    authority_source: str = "",
    dry_run: bool = True,
    flush: bool = True,
    formal_skill_id: str = "",
) -> dict[str, Any]:
    """Ensure one vh_* SkillInfo + SkillCurriculum for an authoritative DOCX heading."""
    from core.textbook_processor_v2 import (
        _canonical_outline_section_title,
        _ensure_formal_skill_info_and_curriculum_v2,
        _lookup_outline_section_curriculum_row,
        _resolve_outline_grade,
        extract_section_code_from_title,
    )
    from core.textbook_section_outline import _canonical_chapter_title

    base: dict[str, Any] = {
        "curriculum": _norm(curriculum),
        "volume": _norm(volume),
        "chapter": _norm(chapter),
        "section": _norm(section),
        "section_code": _norm(section_code),
        "concept_code": _norm(concept_code),
        "concept_name": _norm(concept_name),
        "concept_en_id": _norm(concept_en_id),
        "authority_source": _norm(authority_source),
        "dry_run": bool(dry_run),
        "wrote": False,
        "skill_info_created": False,
        "skill_curriculum_created": False,
        "skill_id": None,
        "paragraph": _norm(concept_name),
        "display_order": display_order_from_concept_code(concept_code),
    }

    if not is_authoritative_concept_source(authority_source):
        return {**base, "action": "invalid_authority", "reason": "non_authoritative_source"}
    if not base["curriculum"] or not base["volume"]:
        return {**base, "action": "invalid_authority", "reason": "missing_curriculum_or_volume"}
    if not base["chapter"] or not base["concept_name"] or not base["concept_code"]:
        return {**base, "action": "invalid_authority", "reason": "missing_heading_fields"}
    if not base["concept_en_id"] and not _norm(formal_skill_id):
        return {**base, "action": "invalid_authority", "reason": "missing_concept_en_id"}

    code = base["section_code"] or extract_section_code_from_title(base["section"])
    code, section_title = _canonical_outline_section_title(code, base["section"] or code)
    chapter_title = _canonical_chapter_title(base["chapter"], {"volume": base["volume"]})
    base.update({"section_code": code, "section": section_title, "chapter": chapter_title})

    info = {
        "curriculum": base["curriculum"],
        "volume": base["volume"],
        "chapter": chapter_title,
        "section": section_title,
        "section_code": code,
    }
    from core.textbook_processor import grade_for_vocational_math_volume

    mapped_grade = grade_for_vocational_math_volume(base["volume"])
    if mapped_grade is not None:
        info["grade"] = mapped_grade
    elif grade is not None:
        info["grade"] = int(grade)
    else:
        info["grade"] = _resolve_outline_grade(
            {"curriculum": base["curriculum"], "volume": base["volume"]}
        )
    outline = _lookup_outline_section_curriculum_row(info, code)
    if outline is None:
        return {**base, "action": "missing_outline", "reason": "section_outline_not_found"}

    resolved_grade = int(info["grade"])
    display_order = base["display_order"] or display_order_from_concept_code(concept_code)

    # DB authoritative mapping by paragraph (reuse over new naming).
    existing_by_para = (
        SkillCurriculum.query.filter(
            SkillCurriculum.curriculum == base["curriculum"],
            SkillCurriculum.volume == base["volume"],
            SkillCurriculum.section == section_title,
            SkillCurriculum.paragraph == base["concept_name"],
            SkillCurriculum.skill_id.startswith("vh_"),
        )
        .order_by(SkillCurriculum.id.asc())
        .first()
    )

    incoming_sid = _norm(formal_skill_id) or build_formal_skill_id_from_en_id(
        volume=base["volume"], concept_en_id=base["concept_en_id"]
    )
    if existing_by_para is not None:
        mapped_sid = str(existing_by_para.skill_id or "").strip()
        if mapped_sid and mapped_sid != incoming_sid:
            return {
                **base,
                "action": "conflict",
                "reason": "paragraph_mapped_to_different_skill_id",
                "skill_id": incoming_sid,
                "existing": {
                    "skill_id": mapped_sid,
                    "paragraph": existing_by_para.paragraph,
                    "chapter": existing_by_para.chapter,
                    "section": existing_by_para.section,
                },
                "incoming": {
                    "skill_id": incoming_sid,
                    "paragraph": base["concept_name"],
                    "chapter": chapter_title,
                    "section": section_title,
                },
            }
        incoming_sid = mapped_sid or incoming_sid

    base["skill_id"] = incoming_sid
    base["display_order"] = display_order

    si = db.session.get(SkillInfo, incoming_sid)
    sc_by_sid = (
        SkillCurriculum.query.filter_by(
            skill_id=incoming_sid,
            curriculum=base["curriculum"],
            volume=base["volume"],
        )
        .order_by(SkillCurriculum.id.asc())
        .first()
    )

    if si is not None:
        existing_ch = _norm(getattr(si, "skill_ch_name", "") or "")
        if existing_ch and existing_ch != base["concept_name"]:
            return {
                **base,
                "action": "conflict",
                "reason": "skill_ch_name_mismatch",
                "existing": {"skill_id": incoming_sid, "skill_ch_name": existing_ch},
                "incoming": {"skill_id": incoming_sid, "concept_name": base["concept_name"]},
            }
        if sc_by_sid is not None:
            if _norm(sc_by_sid.chapter) != chapter_title or _norm(sc_by_sid.section) != section_title:
                return {
                    **base,
                    "action": "conflict",
                    "reason": "curriculum_chapter_section_mismatch",
                    "existing": {
                        "skill_id": incoming_sid,
                        "chapter": sc_by_sid.chapter,
                        "section": sc_by_sid.section,
                        "paragraph": sc_by_sid.paragraph,
                    },
                    "incoming": {
                        "skill_id": incoming_sid,
                        "chapter": chapter_title,
                        "section": section_title,
                        "paragraph": base["concept_name"],
                    },
                }
            para = _norm(sc_by_sid.paragraph or "")
            if para and para != base["concept_name"]:
                return {
                    **base,
                    "action": "conflict",
                    "reason": "curriculum_paragraph_mismatch",
                    "existing": {"paragraph": para},
                    "incoming": {"paragraph": base["concept_name"]},
                }
            return {
                **base,
                "action": "existing",
                "existing": {
                    "skill_id": incoming_sid,
                    "paragraph": sc_by_sid.paragraph,
                    "display_order": sc_by_sid.display_order,
                    "chapter": sc_by_sid.chapter,
                    "section": sc_by_sid.section,
                },
            }
        # SkillInfo exists but no curriculum row for this volume — treat as would_create curriculum only
        # but still conflict if Chinese name mismatch already handled.

    if dry_run:
        return {
            **base,
            "action": "would_create",
            "incoming": {
                "skill_id": incoming_sid,
                "concept_code": base["concept_code"],
                "concept_name": base["concept_name"],
                "concept_en_id": base["concept_en_id"],
                "paragraph": base["concept_name"],
                "display_order": display_order,
                "chapter": chapter_title,
                "section": section_title,
                "grade": resolved_grade,
            },
        }

    existed_si = si is not None
    existed_sc = sc_by_sid is not None
    _ensure_formal_skill_info_and_curriculum_v2(
        formal_skill_id=incoming_sid,
        concept_name=base["concept_name"],
        concept_en_id=base["concept_en_id"] or _norm(getattr(si, "skill_en_name", "") if si else ""),
        curriculum=base["curriculum"],
        grade=resolved_grade,
        volume=base["volume"],
        chapter_title=chapter_title,
        section_title=section_title,
        paragraph=base["concept_name"],
        section_code=code,
        concept_code=base["concept_code"],
        display_order=display_order,
        allow_ai_description=False,
    )
    if flush:
        db.session.flush()

    return {
        **base,
        "action": "created",
        "wrote": True,
        "skill_info_created": not existed_si,
        "skill_curriculum_created": not existed_sc,
        "incoming": {
            "skill_id": incoming_sid,
            "concept_code": base["concept_code"],
            "concept_name": base["concept_name"],
            "concept_en_id": base["concept_en_id"],
            "paragraph": base["concept_name"],
            "display_order": display_order,
            "chapter": chapter_title,
            "section": section_title,
            "grade": resolved_grade,
        },
    }


# Canonical B2 1-1 Phase2 naming results (no new Gemini).
B2_1_1_AUTHORITATIVE_CONCEPTS: list[dict[str, str]] = [
    {
        "concept_code": "1-1.1",
        "concept_name": "有向角",
        "concept_en_id": "DirectedAngle",
        "formal_skill_id": "vh_數學B2_DirectedAngle",
    },
    {
        "concept_code": "1-1.2",
        "concept_name": "角的度量與換算",
        "concept_en_id": "AngleMeasurementAndConversion",
        "formal_skill_id": "vh_數學B2_AngleMeasurementAndConversion",
    },
    {
        "concept_code": "1-1.3",
        "concept_name": "扇形的弧長與面積",
        "concept_en_id": "ArcLengthAndSectorArea",
        "formal_skill_id": "vh_數學B2_ArcLengthAndSectorArea",
    },
    {
        "concept_code": "1-1.4",
        "concept_name": "同界角",
        "concept_en_id": "CoterminalAngles",
        "formal_skill_id": "vh_數學B2_CoterminalAngles",
    },
]
