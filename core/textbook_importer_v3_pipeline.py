# -*- coding: utf-8 -*-
"""V3 textbook import orchestration: raw DOCX+PDF → Phase4 DB → PDF visual enrichment.

Reuses V2 phases, MTEF converter, outline/concept ensure, stable anchors, and
core.textbook_pdf_visual for paired-PDF diagram mounting.
"""

from __future__ import annotations

import json
import queue
import re
import shutil
import threading
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.globals import TASK_QUEUES, V3_IMPORT_TASKS
from core.mathb_concept_heading import is_persistable_concept_code
from core.textbook_importer_v3_docx import parse_docx_summary
from core.textbook_importer_v3_orchestrate import build_curriculum_info_for_v3_import
from core.textbook_importer_v3_phase3_dryrun import GeminiUsageTracker
from core.textbook_mathtype_converter import convert_docx_mathtype_to_latex_docx
from core.textbook_question_anchor import (
    build_anchors_from_block_meta,
    detect_anchor_id_collisions,
    normalize_question_label,
    question_anchor_notes_payload,
    summarize_anchor_collection,
)

# Public stage ids (backend). UI maps via STAGE_TO_UI_STEP.
STAGE_FILE_VALIDATION = "FILE_VALIDATION"
STAGE_SOURCE_STORAGE = "SOURCE_STORAGE"
STAGE_WORD_SCAN = "WORD_SCAN"
STAGE_FORMULA_CONVERSION = "FORMULA_CONVERSION"
STAGE_QUESTION_PARSE = "QUESTION_PARSE"
STAGE_CURRICULUM_BINDING = "CURRICULUM_BINDING"
STAGE_AI_ALIGNMENT = "AI_ALIGNMENT"
STAGE_ANCHOR = "ANCHOR"
STAGE_DB_WRITE = "DB_WRITE"
STAGE_COMPLETE = "COMPLETE"
STAGE_PDF_VISUAL = "PDF_VISUAL"
STAGE_IMAGE_LINKING = "IMAGE_LINKING"

PIPELINE_STAGES = (
    STAGE_FILE_VALIDATION,
    STAGE_SOURCE_STORAGE,
    STAGE_WORD_SCAN,
    STAGE_FORMULA_CONVERSION,
    STAGE_QUESTION_PARSE,
    STAGE_CURRICULUM_BINDING,
    STAGE_AI_ALIGNMENT,
    STAGE_ANCHOR,
    STAGE_DB_WRITE,
    STAGE_PDF_VISUAL,
    STAGE_IMAGE_LINKING,
    STAGE_COMPLETE,
)

STAGE_TO_UI_STEP = {
    STAGE_FILE_VALIDATION: "file_validation",
    STAGE_SOURCE_STORAGE: "file_validation",
    STAGE_WORD_SCAN: "word_parse",
    STAGE_FORMULA_CONVERSION: "equation_convert",
    STAGE_QUESTION_PARSE: "question_parse",
    STAGE_CURRICULUM_BINDING: "curriculum_binding",
    STAGE_AI_ALIGNMENT: "ai_alignment",
    STAGE_ANCHOR: "ai_alignment",
    STAGE_DB_WRITE: "db_write",
    STAGE_PDF_VISUAL: "pdf_alignment",
    STAGE_IMAGE_LINKING: "asset_linking",
    STAGE_COMPLETE: "db_write",
}

_PENDING_NOT_IMPLEMENTED = frozenset()

_CHAPTER_LINE_RE = re.compile(
    r"^(?:第\s*)?(\d+)\s*章\s*[．.\s　]*(.+)$"
)
_CHAPTER_PLAIN_RE = re.compile(r"^(\d+)\s+([^\d\-].+)$")


class V3PipelineError(Exception):
    """Fatal stage failure — abort before DB write when raised early."""

    def __init__(
        self,
        stage: str,
        error_code: str,
        message: str,
        *,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.stage = stage
        self.error_code = error_code
        self.message = message
        self.details = details


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty_stage_map() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for stage in PIPELINE_STAGES:
        if stage in _PENDING_NOT_IMPLEMENTED:
            out[stage] = {
                "status": "pending",
                "ui_step": STAGE_TO_UI_STEP[stage],
                "message": "not_implemented_this_round",
            }
        else:
            out[stage] = {
                "status": "pending",
                "ui_step": STAGE_TO_UI_STEP[stage],
                "message": "",
            }
    return out


def _init_task_state(task_id: str) -> dict[str, Any]:
    state = {
        "task_id": task_id,
        "status": "running",
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
        "stages": _empty_stage_map(),
        "result": None,
        "error": None,
        "pair_index": 0,
        "pair_total": 0,
        "current_pair": None,
    }
    V3_IMPORT_TASKS[task_id] = state
    return state


def get_v3_import_task(task_id: str) -> dict[str, Any] | None:
    return V3_IMPORT_TASKS.get(task_id)


def _emit(
    task_id: str,
    task_queue: queue.Queue | None,
    *,
    stage: str,
    status: str,
    message: str = "",
    error_code: str = "",
    metrics: dict[str, Any] | None = None,
) -> None:
    state = V3_IMPORT_TASKS.get(task_id)
    if state is not None:
        stage_info = state["stages"].setdefault(
            stage,
            {"status": "pending", "ui_step": STAGE_TO_UI_STEP.get(stage, stage)},
        )
        stage_info["status"] = status
        if message:
            stage_info["message"] = message
        if error_code:
            stage_info["error_code"] = error_code
        if metrics is not None:
            stage_info["metrics"] = metrics
        stage_info["updated_at"] = _utc_now()
        state["updated_at"] = _utc_now()
        if status == "failed":
            state["status"] = "failed"
            state["error"] = {
                "stage": stage,
                "error_code": error_code or "stage_failed",
                "message": message,
            }

    payload = {
        "type": "stage",
        "stage": stage,
        "ui_step": STAGE_TO_UI_STEP.get(stage, stage),
        "status": status,
        "message": message,
        "error_code": error_code or None,
        "metrics": metrics or {},
    }
    if task_queue is not None:
        task_queue.put(payload)


def _resolve_abs_path(project_root: Path, maybe_rel: str | Path | None) -> Path | None:
    if not maybe_rel:
        return None
    path = Path(maybe_rel)
    if path.is_file():
        return path.resolve()
    candidate = (project_root / path).resolve()
    if candidate.is_file():
        return candidate
    return None


def _latex_output_path(docx_path: Path) -> Path:
    return docx_path.with_name(f"{docx_path.stem}_Latex.docx")


def ensure_db_backup(*, project_root: Path, label: str = "v3_import") -> dict[str, Any]:
    """Copy instance/kumon_math.db into instance/backups before Phase4."""
    db_path = project_root / "instance" / "kumon_math.db"
    backup_dir = project_root / "instance" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    if not db_path.is_file():
        raise V3PipelineError(
            STAGE_DB_WRITE,
            "db_backup_missing_source",
            f"Database file not found: {db_path}",
        )
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = backup_dir / f"kumon_math_before_{label}_{stamp}.db"
    shutil.copy2(db_path, dest)
    return {"backup_path": str(dest), "source_path": str(db_path), "created": True}


def _extract_chapter_title_from_lines(lines: list[str]) -> str:
    for raw in lines[:80]:
        line = re.sub(r"\s+", " ", str(raw or "")).strip()
        if not line or len(line) > 40:
            continue
        m = _CHAPTER_LINE_RE.match(line)
        if m:
            return f"{int(m.group(1))} {m.group(2).strip()}"
        m2 = _CHAPTER_PLAIN_RE.match(line)
        if m2 and "習題" not in line and "-" not in line.split()[0]:
            # Avoid section codes like 1-1; plain "1 三角函數" is OK.
            name = m2.group(2).strip()
            if name and "例" not in name[:2]:
                return f"{int(m2.group(1))} {name}"
    return ""


def _fill_chapter_section_from_outline_or_lines(
    curriculum_info: dict[str, Any],
    lines: list[str],
) -> dict[str, Any]:
    info = dict(curriculum_info)
    section_code = str(info.get("section_code") or "").strip()
    chapter = str(info.get("chapter") or "").strip()
    section = str(info.get("section") or "").strip()

    from core.textbook_processor_v2 import (
        _canonical_outline_section_title,
        _lookup_outline_section_curriculum_row,
    )

    if section_code:
        outline = _lookup_outline_section_curriculum_row(info, section_code)
        if outline is not None:
            if not chapter:
                chapter = str(outline.chapter or "").strip()
            if not section:
                section = str(outline.section or "").strip()

    if not section and section_code:
        fn_meta = info.get("filename_meta") or {}
        section_hint = str(
            info.get("section")
            or fn_meta.get("section_title")
            or section_code
        ).strip()
        _, section = _canonical_outline_section_title(section_code, section_hint)

    if not chapter:
        chapter = _extract_chapter_title_from_lines(lines)

    if chapter:
        info["chapter"] = chapter
    if section:
        info["section"] = section
    return info


def _collect_unique_concept_headings(
    block_meta: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, str]] = []
    for meta in (block_meta or {}).values():
        code = str((meta or {}).get("concept_code") or "").strip()
        name = str((meta or {}).get("concept_name") or "").strip()
        if not code or not name:
            continue
        if not is_persistable_concept_code(code):
            continue
        key = (code, name)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "concept_code": code,
                "concept_name": name,
                "concept_en_id": str((meta or {}).get("concept_en_id") or "").strip(),
                "formal_skill_id": str((meta or {}).get("formal_skill_id") or "").strip(),
            }
        )
    out.sort(key=lambda r: r["concept_code"])
    return out


def _ensure_formal_concepts_for_headings(
    *,
    headings: list[dict[str, str]],
    curriculum_info: dict[str, Any],
) -> list[dict[str, Any]]:
    from models import SkillCurriculum, SkillInfo
    from core.textbook_formal_concept import ensure_formal_concept_from_authoritative_heading_v2

    results: list[dict[str, Any]] = []
    curr = str(curriculum_info.get("curriculum") or "vocational").strip()
    vol = str(curriculum_info.get("volume") or "").strip()
    chapter = str(curriculum_info.get("chapter") or "").strip()
    section = str(curriculum_info.get("section") or "").strip()
    section_code = str(curriculum_info.get("section_code") or "").strip()
    grade = curriculum_info.get("grade")

    for heading in headings:
        en_id = heading.get("concept_en_id") or ""
        sid = heading.get("formal_skill_id") or ""
        name = heading["concept_name"]
        if not en_id:
            existing = (
                SkillCurriculum.query.filter(
                    SkillCurriculum.curriculum == curr,
                    SkillCurriculum.volume == vol,
                    SkillCurriculum.section == section,
                    SkillCurriculum.paragraph == name,
                    SkillCurriculum.skill_id.startswith("vh_"),
                )
                .order_by(SkillCurriculum.id.asc())
                .first()
            )
            if existing is not None:
                sid = str(existing.skill_id or "")
                si = SkillInfo.query.get(sid)
                en_id = str(getattr(si, "skill_en_name", "") or "").strip()
        if not en_id and sid.startswith("vh_"):
            # Derive PascalCase tail from skill_id when SkillInfo missing en name.
            parts = sid.split("_")
            en_id = parts[-1] if parts else ""

        if not en_id and not sid:
            results.append(
                {
                    "action": "skipped_missing_en_id",
                    "concept_code": heading["concept_code"],
                    "concept_name": name,
                }
            )
            continue

        result = ensure_formal_concept_from_authoritative_heading_v2(
            curriculum=curr,
            volume=vol,
            chapter=chapter,
            section=section,
            concept_code=heading["concept_code"],
            concept_name=name,
            concept_en_id=en_id,
            section_code=section_code,
            grade=int(grade) if grade is not None else None,
            authority_source="docx_heading",
            dry_run=False,
            flush=True,
            formal_skill_id=sid,
        )
        if result.get("action") == "conflict":
            raise V3PipelineError(
                STAGE_CURRICULUM_BINDING,
                "formal_skill_conflict",
                f"Formal skill conflict for {name}: {result.get('reason')}",
                details=result,
            )
        if result.get("action") == "missing_outline":
            raise V3PipelineError(
                STAGE_CURRICULUM_BINDING,
                "missing_authoritative_section",
                "Section outline missing when ensuring formal concepts",
                details=result,
            )
        results.append(result)
    return results


def _attach_anchor_notes_to_phase3(
    parsed: dict[str, Any],
    block_meta: dict[str, dict[str, Any]],
    curriculum_info: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Attach notes JSON (stable anchor) onto Phase3 items for all source types."""
    anchors = build_anchors_from_block_meta(block_meta, curriculum_info)
    by_label: dict[str, dict[str, Any]] = {}
    for anchor in anchors:
        for key in (
            str(anchor.get("question_label") or "").strip(),
            str(anchor.get("anchor_key") or "").strip(),
            normalize_question_label(str(anchor.get("question_label") or "")),
        ):
            if key:
                by_label[key] = anchor

    attached = 0
    missing = 0
    for chapter_data in parsed.get("chapters", []) or []:
        if not isinstance(chapter_data, dict):
            continue
        for section_data in chapter_data.get("sections", []) or []:
            if not isinstance(section_data, dict):
                continue
            for concept in section_data.get("concepts", []) or []:
                if not isinstance(concept, dict):
                    continue
                for bucket in ("examples", "practice_questions"):
                    for item in concept.get(bucket, []) or []:
                        if not isinstance(item, dict):
                            continue
                        title = str(item.get("title") or item.get("source_description") or "").strip()
                        anchor = by_label.get(title) or by_label.get(normalize_question_label(title))
                        if anchor is None:
                            missing += 1
                            continue
                        notes_obj = question_anchor_notes_payload(anchor)
                        item["notes"] = json.dumps(notes_obj, ensure_ascii=False)
                        item["anchor_id"] = anchor.get("anchor_id")
                        item["text_fingerprint"] = anchor.get("text_fingerprint")
                        attached += 1

    summary = summarize_anchor_collection(anchors)
    summary["collisions"] = detect_anchor_id_collisions(anchors)
    summary["collision_count"] = len(summary["collisions"])
    summary["phase3_attached"] = attached
    summary["phase3_missing"] = missing
    return anchors, summary


def run_v3_pair_pipeline(
    *,
    project_root: Path | str,
    docx_path: Path | str,
    pdf_path: Path | str | None,
    curriculum: str,
    volume: str,
    publisher: str = "longteng",
    grade: int = 10,
    task_id: str = "",
    task_queue: queue.Queue | None = None,
    allow_phase4: bool = True,
    emit_stream_end: bool = True,
    app: Any = None,
) -> dict[str, Any]:
    """Run full V3 orchestration for one DOCX+PDF pair."""
    import core.textbook_processor_v2 as tpv2
    from core.textbook_formal_concept import get_section_formal_skill_candidates
    from core.textbook_section_outline import (
        ensure_section_outline_from_authoritative_metadata_v2,
    )
    from models import TextbookExample, db

    if app is None:
        from app import app as flask_app
    else:
        flask_app = app

    root = Path(project_root)
    docx = Path(docx_path)
    pdf = Path(pdf_path) if pdf_path else None
    from core.textbook_processor import grade_for_vocational_math_volume

    mapped_grade = grade_for_vocational_math_volume(volume)
    if mapped_grade is not None:
        grade = mapped_grade
    tid = task_id or str(uuid.uuid4())
    if tid not in V3_IMPORT_TASKS:
        _init_task_state(tid)

    report: dict[str, Any] = {
        "ok": False,
        "task_id": tid,
        "base_name": docx.stem,
        "docx_path": str(docx),
        "pdf_path": str(pdf) if pdf else None,
        "stages": {},
        "metrics": {},
        "error": None,
    }

    tracker = GeminiUsageTracker()

    def fail(stage: str, code: str, message: str, details: Any = None) -> dict[str, Any]:
        _emit(tid, task_queue, stage=stage, status="failed", message=message, error_code=code)
        report["ok"] = False
        report["error"] = {
            "stage": stage,
            "error_code": code,
            "message": message,
            "details": details,
        }
        state = V3_IMPORT_TASKS.get(tid)
        if state is not None:
            state["status"] = "failed"
            state["error"] = report["error"]
            state["result"] = report
        if task_queue is not None:
            task_queue.put({"type": "error", **report["error"]})
            if emit_stream_end:
                task_queue.put("END_OF_STREAM")
        return report

    try:
        _emit(
            tid,
            task_queue,
            stage=STAGE_FILE_VALIDATION,
            status="success",
            message="pair accepted",
        )
        _emit(
            tid,
            task_queue,
            stage=STAGE_SOURCE_STORAGE,
            status="success",
            message="source files on disk",
        )

        # --- WORD_SCAN ---
        _emit(tid, task_queue, stage=STAGE_WORD_SCAN, status="running")
        if not docx.is_file():
            return fail(STAGE_WORD_SCAN, "missing_docx", f"DOCX not found: {docx}")
        word_parsed = parse_docx_summary(docx, filename=docx.name)
        word_summary = word_parsed.get("summary") or {}
        word_metrics = {
            "word_tables": word_summary.get("tables"),
            "table_cells": word_summary.get("table_cells"),
            "mathtype_found": word_summary.get("mathtype_ole"),
            "eq_fields": word_summary.get("eq_fields"),
            "independent_images": word_summary.get("independent_images"),
            "formula_preview_media": word_summary.get("media_wmf")
            or (word_summary.get("media_extension_counts") or {}).get("wmf"),
        }
        report["metrics"]["word_scan"] = word_metrics
        _emit(
            tid,
            task_queue,
            stage=STAGE_WORD_SCAN,
            status="success",
            metrics=word_metrics,
        )

        # --- FORMULA_CONVERSION ---
        _emit(tid, task_queue, stage=STAGE_FORMULA_CONVERSION, status="running")
        latex_path = _latex_output_path(docx)
        convert_report = convert_docx_mathtype_to_latex_docx(docx, latex_path)
        formula_metrics = {
            "mathtype_found": convert_report.get("mathtype_ole"),
            "mathtype_converted": convert_report.get("converted_ok"),
            "formula_failures": convert_report.get("converted_failed"),
            "eq_fields": convert_report.get("eq_fields"),
            "eq_converted": convert_report.get("eq_converted_ok"),
            "latex_docx": str(latex_path),
            "original_unchanged": convert_report.get("original_unchanged"),
        }
        report["metrics"]["formula_conversion"] = formula_metrics
        report["latex_docx"] = str(latex_path)
        if not latex_path.is_file():
            return fail(
                STAGE_FORMULA_CONVERSION,
                "mtef_conversion_failed",
                "LaTeX DOCX was not produced",
                details=formula_metrics,
            )
        _emit(
            tid,
            task_queue,
            stage=STAGE_FORMULA_CONVERSION,
            status="success",
            metrics=formula_metrics,
        )

        curriculum_info = build_curriculum_info_for_v3_import(
            latex_docx_path=latex_path,
            original_docx_filename=docx.name,
            curriculum=curriculum,
            publisher=publisher,
            grade=grade,
            volume=volume,
        )

        with flask_app.app_context():
            # --- QUESTION_PARSE (Phase1 + metadata + outline gate + Phase2) ---
            _emit(tid, task_queue, stage=STAGE_QUESTION_PARSE, status="running")
            lines = tpv2.phase1_extract_docx_lines(str(latex_path))
            scope_bundle = tpv2._resolve_import_source_metadata(
                parse_filename=str(curriculum_info.get("parse_filename") or docx.name),
                lines=lines,
                curriculum_info=curriculum_info,
            )
            curriculum_info = scope_bundle["curriculum_info"]
            source_scope = scope_bundle["source_scope"]
            curriculum_info = _fill_chapter_section_from_outline_or_lines(
                curriculum_info, lines
            )

            # Outline must exist before Phase2 formal skill persistence.
            _emit(tid, task_queue, stage=STAGE_CURRICULUM_BINDING, status="running")
            chapter = str(curriculum_info.get("chapter") or "").strip()
            section = str(curriculum_info.get("section") or "").strip()
            section_code = str(curriculum_info.get("section_code") or "").strip()
            if not chapter or (not section and not section_code):
                return fail(
                    STAGE_CURRICULUM_BINDING,
                    "missing_authoritative_section",
                    "Could not resolve authoritative chapter/section for outline ensure",
                    details={
                        "chapter": chapter,
                        "section": section,
                        "section_code": section_code,
                    },
                )

            outline_result = ensure_section_outline_from_authoritative_metadata_v2(
                curriculum=str(curriculum_info.get("curriculum") or "vocational"),
                volume=str(curriculum_info.get("volume") or volume),
                chapter=chapter,
                section=section,
                section_code=section_code,
                grade=int(curriculum_info.get("grade") or grade),
                authority_source="v3_source_context",
                dry_run=False,
                flush=True,
                curriculum_info=curriculum_info,
            )
            if outline_result.get("action") == "conflict":
                return fail(
                    STAGE_CURRICULUM_BINDING,
                    "outline_conflict",
                    "Existing section outline conflicts with authoritative metadata",
                    details=outline_result,
                )
            if outline_result.get("action") in ("invalid_authority", "would_create"):
                return fail(
                    STAGE_CURRICULUM_BINDING,
                    "outline_ensure_failed",
                    f"Outline ensure failed: {outline_result.get('action')}",
                    details=outline_result,
                )
            db.session.commit()
            curriculum_info["chapter"] = outline_result.get("chapter") or chapter
            curriculum_info["section"] = outline_result.get("section") or section

            question_blocks = tpv2.phase2_deterministic_block_slice(
                lines,
                source_scope=source_scope,
                curriculum_info=curriculum_info,
            )
            block_meta = dict(tpv2._DOCX_BLOCK_META or {})
            parse_metrics = {
                "phase1_lines": len(lines),
                "phase2_blocks": len(question_blocks or {}),
                "block_anchor_count": len(block_meta),
            }
            report["metrics"]["question_parse"] = parse_metrics
            if not block_meta:
                return fail(
                    STAGE_QUESTION_PARSE,
                    "question_parse_empty",
                    "Phase2 produced 0 question anchors",
                    details=parse_metrics,
                )
            _emit(
                tid,
                task_queue,
                stage=STAGE_QUESTION_PARSE,
                status="success",
                metrics=parse_metrics,
            )

            headings = _collect_unique_concept_headings(block_meta)
            concept_results = _ensure_formal_concepts_for_headings(
                headings=headings,
                curriculum_info=curriculum_info,
            )
            db.session.commit()
            formal_candidates = get_section_formal_skill_candidates(
                curriculum=str(curriculum_info.get("curriculum") or "vocational"),
                volume=str(curriculum_info.get("volume") or volume),
                section=str(curriculum_info.get("section") or ""),
                section_code=str(curriculum_info.get("section_code") or ""),
                chapter=str(curriculum_info.get("chapter") or ""),
            )
            binding_metrics = {
                "outline_action": outline_result.get("action"),
                "outline_skill_id": outline_result.get("skill_id"),
                "concepts_found": len(headings),
                "formal_skills": [
                    {
                        "action": r.get("action"),
                        "skill_id": r.get("skill_id"),
                        "concept_name": r.get("concept_name") or r.get("paragraph"),
                    }
                    for r in concept_results
                ],
                "section_candidate_count": len(formal_candidates),
                "section_candidates": [c.get("skill_id") for c in formal_candidates],
            }
            report["metrics"]["curriculum_binding"] = binding_metrics
            created_n = sum(1 for r in concept_results if r.get("action") == "created")
            reused_n = sum(1 for r in concept_results if r.get("action") == "existing")
            binding_metrics["formal_skills_created"] = created_n
            binding_metrics["formal_skills_reused"] = reused_n
            _emit(
                tid,
                task_queue,
                stage=STAGE_CURRICULUM_BINDING,
                status="success",
                metrics=binding_metrics,
            )

            # --- AI_ALIGNMENT (Phase3) ---
            _emit(tid, task_queue, stage=STAGE_AI_ALIGNMENT, status="running")
            from core.ai_analyzer import get_model, gemini_model_name

            model = get_model("architect")
            tracker.wrap_model(model)
            phase3_keys = sorted(question_blocks.keys())
            try:
                phase3_parsed = tpv2.phase3_ai_metadata_alignment(
                    phase3_keys, curriculum_info, task_queue
                )
            except Exception as exc:
                tracker.restore()
                db.session.rollback()
                return fail(
                    STAGE_AI_ALIGNMENT,
                    "gemini_api_error",
                    f"Phase3 Gemini failed: {exc}",
                    details={"error_type": type(exc).__name__},
                )

            gemini_summary = tracker.summary()
            gemini_summary["model"] = gemini_model_name or getattr(model, "model_name", None)
            report["metrics"]["gemini"] = gemini_summary

            # Count Phase3 questions
            phase3_q = 0
            for ch in phase3_parsed.get("chapters", []) or []:
                for sec in (ch or {}).get("sections", []) or []:
                    for con in (sec or {}).get("concepts", []) or []:
                        phase3_q += len((con or {}).get("examples") or [])
                        phase3_q += len((con or {}).get("practice_questions") or [])
            ai_metrics = {
                "phase3_questions": phase3_q,
                "gemini_requests": gemini_summary.get("request_count"),
                "gemini_total_tokens": gemini_summary.get("total_token_count_total"),
            }
            report["metrics"]["ai_alignment"] = ai_metrics
            _emit(
                tid,
                task_queue,
                stage=STAGE_AI_ALIGNMENT,
                status="success",
                metrics=ai_metrics,
            )

            # --- ANCHOR ---
            _emit(tid, task_queue, stage=STAGE_ANCHOR, status="running")
            anchors, anchor_summary = _attach_anchor_notes_to_phase3(
                phase3_parsed, block_meta, curriculum_info
            )
            report["metrics"]["anchor"] = {
                "anchor_count": len(anchors),
                "collision_count": anchor_summary.get("collision_count", 0),
                "summary": {
                    k: anchor_summary.get(k)
                    for k in ("total", "by_question_type", "collision_count")
                    if k in anchor_summary or True
                },
            }
            if anchor_summary.get("collision_count"):
                return fail(
                    STAGE_ANCHOR,
                    "anchor_collision",
                    f"Stable anchor collisions: {anchor_summary.get('collision_count')}",
                    details=anchor_summary.get("collisions"),
                )
            _emit(
                tid,
                task_queue,
                stage=STAGE_ANCHOR,
                status="success",
                metrics=report["metrics"]["anchor"],
            )

            # --- DB_WRITE (Phase4) ---
            if not allow_phase4:
                _emit(
                    tid,
                    task_queue,
                    stage=STAGE_DB_WRITE,
                    status="skipped",
                    message="allow_phase4=false",
                )
                report["ok"] = True
                report["metrics"]["db_write"] = {"skipped": True}
            else:
                _emit(tid, task_queue, stage=STAGE_DB_WRITE, status="running")
                backup_info = ensure_db_backup(project_root=root, label="v3_phase4")
                report["metrics"]["db_backup"] = backup_info

                te_before = TextbookExample.query.filter_by(
                    source_curriculum=str(curriculum_info.get("curriculum") or "vocational"),
                    source_volume=str(curriculum_info.get("volume") or volume),
                    source_section=str(curriculum_info.get("section") or ""),
                ).count()
                te_total_before = TextbookExample.query.count()

                try:
                    phase4_stats = tpv2.phase4_absolute_hydrate_and_save(
                        phase3_parsed,
                        question_blocks,
                        curriculum_info,
                        task_queue,
                    )
                except Exception as exc:
                    db.session.rollback()
                    return fail(
                        STAGE_DB_WRITE,
                        "phase4_db_error",
                        f"Phase4 DB write failed: {exc}",
                        details={"error_type": type(exc).__name__},
                    )

                te_after = TextbookExample.query.filter_by(
                    source_curriculum=str(curriculum_info.get("curriculum") or "vocational"),
                    source_volume=str(curriculum_info.get("volume") or volume),
                    source_section=str(curriculum_info.get("section") or ""),
                ).count()
                te_total_after = TextbookExample.query.count()

                section_rows = TextbookExample.query.filter_by(
                    source_curriculum=str(curriculum_info.get("curriculum") or "vocational"),
                    source_volume=str(curriculum_info.get("volume") or volume),
                    source_section=str(curriculum_info.get("section") or ""),
                ).all()
                skill_dist: dict[str, int] = {}
                null_answer = 0
                for row in section_rows:
                    sid = str(row.skill_id or "")
                    skill_dist[sid] = skill_dist.get(sid, 0) + 1
                    if row.correct_answer is None or str(row.correct_answer).strip() == "":
                        null_answer += 1

                db_metrics = {
                    "inserted": phase4_stats.get("inserted", 0),
                    "updated": phase4_stats.get("updated", 0),
                    "skipped": phase4_stats.get("skipped", 0),
                    "total": phase4_stats.get("total", 0),
                    "section_count_before": te_before,
                    "section_count_after": te_after,
                    "textbook_example_total_before": te_total_before,
                    "textbook_example_total_after": te_total_after,
                    "skill_distribution": skill_dist,
                    "correct_answer_null_count": null_answer,
                    "backup": backup_info,
                }
                report["metrics"]["db_write"] = db_metrics
                if int(phase4_stats.get("inserted", 0) or 0) + int(
                    phase4_stats.get("updated", 0) or 0
                ) == 0:
                    return fail(
                        STAGE_DB_WRITE,
                        "phase4_zero_writes",
                        "Phase4 completed with 0 inserted/updated rows",
                        details=db_metrics,
                    )
                _emit(
                    tid,
                    task_queue,
                    stage=STAGE_DB_WRITE,
                    status="success",
                    metrics=db_metrics,
                )

            # --- PDF_VISUAL + IMAGE_LINKING (enrichment; non-fatal) ---
            pdf_metrics: dict[str, Any] = {
                "questions_scanned": 0,
                "questions_matched": 0,
                "high_confidence": 0,
                "visual_candidates": 0,
                "mounted": 0,
                "skipped_decorative": 0,
                "skipped_low_confidence": 0,
                "errors": 0,
                "status": "skipped",
            }
            link_metrics: dict[str, Any] = {
                "linked_count": 0,
                "reused_count": 0,
                "status": "skipped",
            }
            if not allow_phase4:
                _emit(
                    tid,
                    task_queue,
                    stage=STAGE_PDF_VISUAL,
                    status="skipped",
                    message="allow_phase4=false",
                    metrics=pdf_metrics,
                )
                _emit(
                    tid,
                    task_queue,
                    stage=STAGE_IMAGE_LINKING,
                    status="skipped",
                    message="allow_phase4=false",
                    metrics=link_metrics,
                )
            elif not pdf or not Path(pdf).is_file():
                _emit(
                    tid,
                    task_queue,
                    stage=STAGE_PDF_VISUAL,
                    status="skipped",
                    message="paired_pdf_missing",
                    metrics=pdf_metrics,
                )
                _emit(
                    tid,
                    task_queue,
                    stage=STAGE_IMAGE_LINKING,
                    status="skipped",
                    message="paired_pdf_missing",
                    metrics=link_metrics,
                )
            else:
                _emit(tid, task_queue, stage=STAGE_PDF_VISUAL, status="running")
                try:
                    from core.textbook_pdf_visual import enrich_textbook_examples_with_pdf_visuals

                    section_rows = TextbookExample.query.filter_by(
                        source_curriculum=str(
                            curriculum_info.get("curriculum") or "vocational"
                        ),
                        source_volume=str(curriculum_info.get("volume") or volume),
                        source_section=str(curriculum_info.get("section") or ""),
                    ).all()
                    debug_dir = root / "textbook_import" / "debug" / f"v3_{tid}"
                    visual_summary = enrich_textbook_examples_with_pdf_visuals(
                        pdf_path=pdf,
                        examples=section_rows,
                        curriculum_info=curriculum_info,
                        project_root=root,
                        debug_dir=debug_dir,
                        write_notes=True,
                    )
                    try:
                        db.session.commit()
                    except Exception as commit_exc:
                        db.session.rollback()
                        visual_summary = dict(visual_summary or {})
                        visual_summary["warnings"] = list(
                            visual_summary.get("warnings") or []
                        ) + [f"notes_commit_failed:{type(commit_exc).__name__}"]
                        visual_summary["errors"] = int(visual_summary.get("errors") or 0) + 1

                    pdf_metrics = {
                        "questions_scanned": visual_summary.get("questions_scanned", 0),
                        "questions_matched": visual_summary.get("questions_matched", 0),
                        "high_confidence": visual_summary.get("high_confidence", 0),
                        "visual_candidates": visual_summary.get("visual_candidates", 0),
                        "mounted": visual_summary.get("mounted", 0),
                        "skipped_decorative": visual_summary.get("skipped_decorative", 0),
                        "skipped_low_confidence": visual_summary.get(
                            "skipped_low_confidence", 0
                        ),
                        "errors": visual_summary.get("errors", 0),
                        "text_layer_usable": visual_summary.get("text_layer_usable"),
                        "warnings": visual_summary.get("warnings") or [],
                        "status": "success",
                    }
                    link_metrics = {
                        "linked_count": visual_summary.get("linked_count", 0),
                        "reused_count": visual_summary.get("reused_count", 0),
                        "status": "success",
                    }
                    report["metrics"]["pdf_visual"] = pdf_metrics
                    report["metrics"]["image_linking"] = link_metrics
                    report["metrics"]["pdf_visual_debug"] = visual_summary.get("debug_path")
                    warn_msg = ""
                    if visual_summary.get("warnings"):
                        warn_msg = ";".join(str(w) for w in visual_summary.get("warnings")[:3])
                    _emit(
                        tid,
                        task_queue,
                        stage=STAGE_PDF_VISUAL,
                        status="success",
                        message=warn_msg,
                        metrics=pdf_metrics,
                    )
                    _emit(
                        tid,
                        task_queue,
                        stage=STAGE_IMAGE_LINKING,
                        status="success",
                        metrics=link_metrics,
                    )
                except Exception as visual_exc:
                    # Enrichment must not fail the successful text import.
                    pdf_metrics["status"] = "partial"
                    pdf_metrics["errors"] = int(pdf_metrics.get("errors") or 0) + 1
                    pdf_metrics["warnings"] = [f"{type(visual_exc).__name__}: {visual_exc}"]
                    report["metrics"]["pdf_visual"] = pdf_metrics
                    report["metrics"]["image_linking"] = link_metrics
                    try:
                        db.session.rollback()
                    except Exception:
                        pass
                    _emit(
                        tid,
                        task_queue,
                        stage=STAGE_PDF_VISUAL,
                        status="success",
                        message=f"enrichment_error:{type(visual_exc).__name__}",
                        metrics=pdf_metrics,
                    )
                    _emit(
                        tid,
                        task_queue,
                        stage=STAGE_IMAGE_LINKING,
                        status="skipped",
                        message="pdf_visual_failed",
                        metrics=link_metrics,
                    )

            _emit(tid, task_queue, stage=STAGE_COMPLETE, status="success")

            report["ok"] = True
            report["curriculum_info"] = {
                k: curriculum_info.get(k)
                for k in (
                    "curriculum",
                    "volume",
                    "chapter",
                    "section",
                    "section_code",
                    "source_scope",
                    "publisher",
                    "grade",
                )
            }
            report["stages"] = (V3_IMPORT_TASKS.get(tid) or {}).get("stages", {})

        tracker.restore()
        state = V3_IMPORT_TASKS.get(tid)
        if state is not None:
            state["status"] = "success" if report["ok"] else "failed"
            state["result"] = report
            state["updated_at"] = _utc_now()
        if task_queue is not None:
            task_queue.put({"type": "result", "result": report})
            if emit_stream_end:
                task_queue.put("END_OF_STREAM")
        return report

    except V3PipelineError as exc:
        tracker.restore()
        try:
            from models import db

            db.session.rollback()
        except Exception:
            pass
        return fail(exc.stage, exc.error_code, exc.message, details=exc.details)
    except Exception as exc:
        tracker.restore()
        try:
            from models import db

            db.session.rollback()
        except Exception:
            pass
        return fail(
            STAGE_COMPLETE,
            "pipeline_exception",
            f"{type(exc).__name__}: {exc}",
            details={"traceback": traceback.format_exc()[-2000:]},
        )


def build_v3_ui_result_payload(batch_report: dict[str, Any]) -> dict[str, Any]:
    """Map orchestration metrics into textbook_importer_v3.html result shape."""
    pairs = batch_report.get("pairs") or []
    ok_pairs = [p for p in pairs if p.get("ok")]
    failed_pairs = [p for p in pairs if not p.get("ok")]

    word_tables = None
    table_cells = None
    mathtype_found = 0
    mathtype_converted = 0
    eq_fields = 0
    formula_failures = 0
    formula_preview = None
    independent_images = None
    parsed_q = 0
    imported_q = 0
    inserted = 0
    updated = 0
    concepts_found = 0
    skills_created = 0
    skills_reused = 0
    gemini_requests = 0
    gemini_tokens = 0
    anchor_collisions = 0
    pdf_mounted = 0
    pdf_matched = 0
    pdf_linked = 0
    pdf_reused = 0
    pdf_skipped_decorative = 0
    pdf_skipped_low = 0

    for p in ok_pairs:
        m = p.get("metrics") or {}
        ws = m.get("word_scan") or {}
        fc = m.get("formula_conversion") or {}
        qp = m.get("question_parse") or {}
        cb = m.get("curriculum_binding") or {}
        ai = m.get("ai_alignment") or {}
        an = m.get("anchor") or {}
        dbm = m.get("db_write") or {}
        pvm = m.get("pdf_visual") or {}
        ilm = m.get("image_linking") or {}

        if ws.get("word_tables") is not None:
            word_tables = (word_tables or 0) + int(ws.get("word_tables") or 0)
        if ws.get("table_cells") is not None:
            table_cells = (table_cells or 0) + int(ws.get("table_cells") or 0)
        if ws.get("independent_images") is not None:
            independent_images = (independent_images or 0) + int(
                ws.get("independent_images") or 0
            )
        if ws.get("formula_preview_media") is not None:
            formula_preview = (formula_preview or 0) + int(ws.get("formula_preview_media") or 0)

        mathtype_found += int(fc.get("mathtype_found") or 0)
        mathtype_converted += int(fc.get("mathtype_converted") or 0)
        formula_failures += int(fc.get("formula_failures") or 0)
        eq_fields += int(fc.get("eq_fields") or 0)

        parsed_q += int(qp.get("phase2_blocks") or 0)
        imported_q += int(dbm.get("inserted") or 0) + int(dbm.get("updated") or 0)
        inserted += int(dbm.get("inserted") or 0)
        updated += int(dbm.get("updated") or 0)

        concepts_found += int(cb.get("concepts_found") or 0)
        skills_created += int(cb.get("formal_skills_created") or 0)
        skills_reused += int(cb.get("formal_skills_reused") or 0)

        gemini_requests += int(ai.get("gemini_requests") or 0)
        tokens = ai.get("gemini_total_tokens")
        if tokens is not None:
            gemini_tokens += int(tokens or 0)

        anchor_collisions += int(an.get("collision_count") or 0)
        pdf_mounted += int(pvm.get("mounted") or 0)
        pdf_matched += int(pvm.get("questions_matched") or 0)
        pdf_skipped_decorative += int(pvm.get("skipped_decorative") or 0)
        pdf_skipped_low += int(pvm.get("skipped_low_confidence") or 0)
        pdf_linked += int(ilm.get("linked_count") or 0)
        pdf_reused += int(ilm.get("reused_count") or 0)

    status = "success"
    if failed_pairs and ok_pairs:
        status = "partial"
    elif failed_pairs and not ok_pairs:
        status = "failed"
    elif not pairs:
        status = "failed"

    return {
        "status": status,
        "task_id": batch_report.get("task_id"),
        "sourcePairsStats": {
            "total": len(pairs),
            "successful": len(ok_pairs),
            "failed": len(failed_pairs),
            "needsReview": None,
        },
        "sourceFiles": {
            "docx": batch_report.get("storage_directory"),
            "pdf": f"stored {batch_report.get('files_saved', '—')} files"
            if batch_report.get("files_saved") is not None
            else None,
        },
        "contentParsing": {
            "wordTables": word_tables,
            "tableCells": table_cells,
            "mathTypeFound": mathtype_found if ok_pairs else None,
            "mathTypeConverted": mathtype_converted if ok_pairs else None,
            "eqFields": eq_fields if ok_pairs else None,
            "formulaPreviewMedia": formula_preview,
            "independentImages": independent_images,
            "formulaFailures": formula_failures if ok_pairs else None,
        },
        "questions": {
            "parsed": parsed_q if ok_pairs else None,
            "imported": imported_q if ok_pairs else None,
            "conceptsFound": concepts_found if ok_pairs else None,
            "formalSkillsCreated": skills_created if ok_pairs else None,
            "formalSkillsReused": skills_reused if ok_pairs else None,
            "geminiRequests": gemini_requests if ok_pairs else None,
            "geminiTokens": gemini_tokens if ok_pairs else None,
            "anchorCollisions": anchor_collisions if ok_pairs else None,
        },
        "images": {
            "pdfVisualAssets": pdf_mounted if ok_pairs else None,
            "linked": pdf_linked if ok_pairs else None,
            "unlinked": None,
            "needsReview": pdf_skipped_low if ok_pairs else None,
            "matched": pdf_matched if ok_pairs else None,
            "skippedDecorative": pdf_skipped_decorative if ok_pairs else None,
            "reused": pdf_reused if ok_pairs else None,
        },
        "database": {
            "questionsWritten": inserted if ok_pairs else None,
            "questionsUpdated": updated if ok_pairs else None,
            "assetsWritten": pdf_mounted if ok_pairs else None,
            "relationshipsCreated": None,
        },
        "pairDetails": [
            {
                "baseName": p.get("base_name"),
                "status": "success" if p.get("ok") else "failed",
                "message": (
                    json.dumps(p.get("metrics") or {}, ensure_ascii=False)[:500]
                    if p.get("ok")
                    else json.dumps(p.get("error") or {}, ensure_ascii=False)
                ),
            }
            for p in pairs
        ],
        "stages": batch_report.get("stages"),
        "raw": batch_report,
    }


def run_v3_batch_pipeline(
    *,
    project_root: Path | str,
    pairs: list[dict[str, Any]],
    curriculum: str,
    volume: str,
    publisher: str = "longteng",
    grade: int = 10,
    task_id: str | None = None,
    task_queue: queue.Queue | None = None,
    allow_phase4: bool = True,
) -> dict[str, Any]:
    """Run pipeline for each stored source pair."""
    from core.textbook_processor import grade_for_vocational_math_volume

    mapped_grade = grade_for_vocational_math_volume(volume)
    if mapped_grade is not None:
        grade = mapped_grade
    root = Path(project_root)
    tid = task_id or str(uuid.uuid4())
    state = _init_task_state(tid)
    state["pair_total"] = len(pairs)

    batch: dict[str, Any] = {
        "task_id": tid,
        "ok": False,
        "pairs": [],
        "curriculum": curriculum,
        "volume": volume,
    }

    for idx, pair in enumerate(pairs, start=1):
        docx = _resolve_abs_path(root, pair.get("docx_abs") or pair.get("docx_path"))
        pdf = _resolve_abs_path(root, pair.get("pdf_abs") or pair.get("pdf_path"))
        base_name = pair.get("base_name") or (docx.stem if docx else f"pair_{idx}")
        state["pair_index"] = idx
        state["current_pair"] = base_name
        if task_queue is not None:
            task_queue.put(
                {
                    "type": "batch_progress",
                    "current_name": base_name,
                    "current_index": idx,
                    "total_count": len(pairs),
                }
            )

        if docx is None:
            pair_report = {
                "ok": False,
                "base_name": base_name,
                "error": {
                    "stage": STAGE_FILE_VALIDATION,
                    "error_code": "missing_docx",
                    "message": "DOCX path unresolved",
                },
            }
            batch["pairs"].append(pair_report)
            continue

        pair_report = run_v3_pair_pipeline(
            project_root=root,
            docx_path=docx,
            pdf_path=pdf,
            curriculum=curriculum,
            volume=volume,
            publisher=publisher,
            grade=grade,
            task_id=tid,
            task_queue=task_queue,
            allow_phase4=allow_phase4,
            emit_stream_end=False,
            app=None,
        )
        batch["pairs"].append(pair_report)
        if not pair_report.get("ok"):
            # Stop batch on first fatal pair failure (no half-complete multi-pair state).
            break

    batch["ok"] = bool(batch["pairs"]) and all(p.get("ok") for p in batch["pairs"])
    batch["stages"] = state.get("stages")
    batch["ui_result"] = build_v3_ui_result_payload(batch)
    state["status"] = "success" if batch["ok"] else "failed"
    state["result"] = batch
    state["updated_at"] = _utc_now()
    if task_queue is not None:
        task_queue.put({"type": "result", "result": batch.get("ui_result") or batch})
        task_queue.put("END_OF_STREAM")
    return batch


def enqueue_v3_batch_pipeline(
    *,
    app: Any,
    project_root: Path | str,
    pairs: list[dict[str, Any]],
    curriculum: str,
    volume: str,
    publisher: str = "longteng",
    grade: int = 10,
    allow_phase4: bool = True,
    storage_meta: dict[str, Any] | None = None,
) -> str:
    """Background-thread runner compatible with importer SSE / status poll."""
    task_id = str(uuid.uuid4())
    q: queue.Queue = queue.Queue()
    TASK_QUEUES[task_id] = q
    state = _init_task_state(task_id)
    if storage_meta:
        state["storage"] = storage_meta

    # Enrich pairs with absolute paths under project_root.
    root = Path(project_root)
    enriched: list[dict[str, Any]] = []
    for pair in pairs:
        item = dict(pair)
        docx_rel = pair.get("docx_path")
        pdf_rel = pair.get("pdf_path")
        if docx_rel and not item.get("docx_abs"):
            abs_docx = _resolve_abs_path(root, docx_rel)
            if abs_docx:
                item["docx_abs"] = str(abs_docx)
        if pdf_rel and not item.get("pdf_abs"):
            abs_pdf = _resolve_abs_path(root, pdf_rel)
            if abs_pdf:
                item["pdf_abs"] = str(abs_pdf)
        enriched.append(item)

    def worker() -> None:
        with app.app_context():
            try:
                batch = run_v3_batch_pipeline(
                    project_root=root,
                    pairs=enriched,
                    curriculum=curriculum,
                    volume=volume,
                    publisher=publisher,
                    grade=grade,
                    task_id=task_id,
                    task_queue=q,
                    allow_phase4=allow_phase4,
                )
                if storage_meta:
                    batch["storage_directory"] = storage_meta.get("directory")
                    batch["files_saved"] = storage_meta.get("files_saved")
                    batch["ui_result"] = build_v3_ui_result_payload(batch)
                    state["result"] = batch
            except Exception as exc:
                state["status"] = "failed"
                state["error"] = {
                    "stage": STAGE_COMPLETE,
                    "error_code": "worker_exception",
                    "message": str(exc),
                }
                q.put(
                    {
                        "type": "error",
                        "stage": STAGE_COMPLETE,
                        "error_code": "worker_exception",
                        "message": str(exc),
                    }
                )
                q.put("END_OF_STREAM")

    threading.Thread(target=worker, daemon=True).start()
    return task_id
