"""Read-only Phase 4 decision preview for scoped chapter self-assessment."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from typing import Any

from flask import has_app_context, current_app

from models import db

from core.textbook_import_authority import ImportAuthorityResolver

# Per-question AI skill select bound (production Gemini has no request timeout).
_AI_SKILL_SELECT_TIMEOUT_SECONDS = 75.0


def _ai_select_with_timeout(
    select_fn,
    *,
    timeout_seconds: float = _AI_SKILL_SELECT_TIMEOUT_SECONDS,
    **kwargs,
):
    """Call production AI select with a hard wall-clock timeout.

    Flask app context is re-pushed inside the worker thread so ``get_model``
    and logging keep working.
    """
    flask_app = current_app._get_current_object() if has_app_context() else None

    def _run():
        if flask_app is None:
            return select_fn(**kwargs)
        with flask_app.app_context():
            return select_fn(**kwargs)

    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(_run).result(timeout=timeout_seconds)


def preflight_self_assessment_phase4(
    scope_report: dict[str, Any],
    block_metadata: dict[str, dict[str, Any]],
    curriculum_info: dict[str, Any],
    *,
    import_mode: str = "insert_missing_only",
    allow_ai: bool = False,
) -> dict[str, Any]:
    """Reuse Phase 4 skill/identity helpers without a mutation or commit.

    With ``allow_ai=False``, a question needing the production AI selector stays
    blocked. With ``allow_ai=True``, reuse
    ``_ai_select_formal_skill_for_problem_v2`` (same production path) then stop
    before any DB write.
    """
    import core.textbook_processor_v2 as tpv2

    if import_mode not in {"insert_missing_only", "update_existing"}:
        raise ValueError("Phase 4 preflight supports insert/update modes only")
    if str(curriculum_info.get("source_scope") or "") != "chapter_self_assessment":
        raise ValueError("Expected chapter self-assessment source scope")

    rows: list[dict[str, Any]] = []
    coords = tpv2._import_scope_coords(curriculum_info)
    with db.session.no_autoflush:
        for question in scope_report.get("questions") or []:
            if not question.get("target"):
                continue
            label = str(question.get("label") or "")
            meta = block_metadata.get(label) or {}
            source_type = str(meta.get("source_type") or question.get("source_type") or "")
            number = re.search(r"題\s*(\d+)\s*$", label)
            item = {
                "question_number": int(number.group(1)) if number else None,
                "source_label": label,
                "source_type": source_type,
                "subsection": str(meta.get("section_code") or ""),
                "question_preview": str(meta.get("problem_text") or "")[:100],
                "formula_count": int(question.get("formula_count") or 0),
                "image_candidates": list(question.get("image_candidates") or []),
                "skill_id": None,
                "skill_name": None,
                "ai_reason": None,
                "existing_db_id": None,
                "candidate_skills": [],
                "candidate_skill_ids": [],
                "decision": "BLOCKED_SKILL",
                "reason": "unresolved_section",
            }
            rows.append(item)
            if source_type != "self_assessment" or not meta:
                item["reason"] = "unsupported_source_or_missing_metadata"
                continue

            authority = ImportAuthorityResolver.resolve_phase4_item_authority(
                source_scope="chapter_self_assessment",
                curriculum_info=curriculum_info,
                block_meta=meta,
                matched_key=label,
                title=label,
            )
            item["subsection"] = authority.section_code
            outline = tpv2._lookup_outline_section_curriculum_row(
                curriculum_info, authority.section_code
            )
            if outline is None:
                item["reason"] = "missing_outline_binding"
                continue
            chapter = tpv2.normalize_chapter_title_for_db(outline.chapter)
            candidates = tpv2._get_self_assessment_skill_candidates_v2(
                curriculum=outline.curriculum,
                volume=outline.volume,
                chapter_title=chapter,
                section_code=authority.section_code,
                chapter_index=curriculum_info.get("chapter_index"),
            )
            item["candidate_skills"] = [
                {
                    "skill_id": c["skill_id"],
                    "skill_name": c.get("concept_name") or "",
                }
                for c in candidates
            ]
            item["candidate_skill_ids"] = [c["skill_id"] for c in candidates]
            if not candidates:
                item["reason"] = "no_bound_formal_skill"
                continue
            if not allow_ai:
                item["decision"] = (
                    "BLOCKED_AMBIGUOUS" if len(candidates) > 1 else "BLOCKED_SKILL"
                )
                item["reason"] = "AI_ALIGNMENT_REQUIRED"
                continue

            # Production self_assessment path: section-scoped candidates → AI pick.
            try:
                selected = _ai_select_with_timeout(
                    tpv2._ai_select_formal_skill_for_problem_v2,
                    problem_text=str(meta.get("problem_text") or ""),
                    source_description=label,
                    source_type="self_assessment",
                    section_code=authority.section_code,
                    section_title=str(
                        getattr(outline, "section", None)
                        or meta.get("section_title")
                        or ""
                    ),
                    available_skills=candidates,
                )
            except FuturesTimeout:
                item["decision"] = (
                    "BLOCKED_AMBIGUOUS" if len(candidates) > 1 else "BLOCKED_SKILL"
                )
                item["reason"] = "AI_ALIGNMENT_UNAVAILABLE"
                item["ai_reason"] = "timeout"
                continue
            except Exception as exc:
                item["decision"] = (
                    "BLOCKED_AMBIGUOUS" if len(candidates) > 1 else "BLOCKED_SKILL"
                )
                item["reason"] = "AI_ALIGNMENT_UNAVAILABLE"
                item["ai_reason"] = f"{type(exc).__name__}: {exc}"
                continue

            allowed = {c["skill_id"] for c in candidates}
            pick_id = str(
                (selected or {}).get("skill_id")
                or (selected or {}).get("formal_skill_id")
                or ""
            ).strip()
            item["ai_reason"] = str((selected or {}).get("reason") or "") or None
            if not pick_id or pick_id not in allowed:
                item["decision"] = (
                    "BLOCKED_AMBIGUOUS" if len(candidates) > 1 else "BLOCKED_SKILL"
                )
                item["reason"] = (
                    "AI_ALIGNMENT_UNAVAILABLE"
                    if not selected
                    else "ai_pick_not_in_candidates"
                )
                continue

            ok, guard_reason = tpv2.validate_existing_skill_binding_for_import(
                pick_id,
                source_type="self_assessment",
                section_code=authority.section_code,
                curriculum_info=curriculum_info,
                chapter_title=chapter,
            )
            if not ok:
                item["decision"] = "BLOCKED_SKILL"
                item["reason"] = f"skill_guard:{guard_reason}"
                continue

            formal_curriculum = tpv2._lookup_formal_skill_curriculum_row(
                pick_id,
                curriculum=outline.curriculum,
                volume=outline.volume,
                chapter_title=chapter,
                section_code=authority.section_code,
            )
            if formal_curriculum is None:
                item["decision"] = "BLOCKED_SKILL"
                item["reason"] = "missing_formal_curriculum_row"
                continue

            hit = next(c for c in candidates if c["skill_id"] == pick_id)
            binding = tpv2._curriculum_authority_coords(formal_curriculum)
            item["skill_id"] = pick_id
            item["skill_name"] = str(
                hit.get("concept_name") or selected.get("concept_name") or ""
            ).strip()
            lookup_coords = {
                "curriculum": binding["curriculum"],
                "volume": binding["volume"],
                "grade": tpv2._coords_from_curriculum_row(
                    formal_curriculum, curriculum_info
                ).get("grade", coords["grade"]),
            }
            existing = tpv2._find_existing_by_structural_title(
                skill_id=pick_id,
                curriculum_info=lookup_coords,
                chapter_title=binding["chapter_title"],
                section_title=binding["section_title"],
                source_type=source_type,
                title=label,
            )
            item["existing_db_id"] = existing.id if existing is not None else None
            item["decision"] = (
                "NEW_INSERT"
                if existing is None
                else "EXISTING_SKIP"
                if import_mode == "insert_missing_only"
                else "WOULD_UPDATE"
            )
            item["reason"] = ""

    decisions = {
        name: sum(row["decision"] == name for row in rows)
        for name in (
            "NEW_INSERT",
            "EXISTING_SKIP",
            "WOULD_UPDATE",
            "BLOCKED_SKILL",
            "BLOCKED_AMBIGUOUS",
        )
    }
    return {
        "questions": rows,
        "counts": decisions,
        "ai_alignment_required": any(
            row["reason"] == "AI_ALIGNMENT_REQUIRED" for row in rows
        ),
        "ai_alignment_unavailable": any(
            row["reason"] == "AI_ALIGNMENT_UNAVAILABLE" for row in rows
        ),
        "ready": bool(rows)
        and not any(row["decision"].startswith("BLOCKED") for row in rows),
        "db_actual_changes": 0,
    }
