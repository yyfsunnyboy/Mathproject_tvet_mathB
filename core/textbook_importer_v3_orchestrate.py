# -*- coding: utf-8 -*-
"""V3 教材匯入：薄 orchestration（resolve LaTeX DOCX → V2 importer）。"""

from __future__ import annotations

import os
import queue
import re
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from core.textbook_filename_parser import (
    parse_textbook_filename_metadata,
    resolve_upload_filenames,
)
from core.textbook_importer_v3_source import get_base_name
from core.textbook_importer_v3_storage import resolve_source_directory

B2_11_SECTION_CODE = "1-1"
B2_11_GLOB_DOCX = "*1-1*課本*.docx"
B2_11_GLOB_PDF = "*1-1*課本*.pdf"

_LATEX_SUFFIX_VARIANTS = ("_Latex.docx", "_latex.docx")


@dataclass(frozen=True)
class LatexDocxResolveResult:
    status: str
    path: Path | None = None
    resolved_filename: str = ""
    reason: str = ""


@dataclass(frozen=True)
class B211SourcePairStatus:
    source_dir: Path
    original_docx: Path | None = None
    pdf: Path | None = None
    latex_docx: Path | None = None
    latex_resolve: LatexDocxResolveResult | None = None
    missing: tuple[str, ...] = ()


def _stem_without_latex_suffix(filename: str) -> str:
    stem = get_base_name(filename)
    for suffix in ("_Latex", "_latex", "Latex", "latex"):
        if stem.lower().endswith(suffix.lower()):
            return stem[: -len(suffix)]
    return stem


def _is_latex_docx_filename(filename: str) -> bool:
    lower = str(filename or "").lower()
    if not lower.endswith(".docx"):
        return False
    stem = get_base_name(filename).lower()
    return stem.endswith("_latex") or stem.endswith("_latex.docx") or "_latex" in stem


def resolve_latex_docx_path(source_dir: Path | str, original_docx_filename: str) -> LatexDocxResolveResult:
    """
    Resolve converted LaTeX DOCX beside source files.

    Never falls back to raw MathType DOCX.
    """
    directory = Path(source_dir)
    name = os.path.basename(str(original_docx_filename or "").strip())
    if not name:
        return LatexDocxResolveResult(status="missing_latex_docx", reason="empty_filename")

    if _is_latex_docx_filename(name):
        direct = directory / name
        if direct.is_file():
            return LatexDocxResolveResult(
                status="ok",
                path=direct.resolve(),
                resolved_filename=direct.name,
                reason="input_is_latex_docx",
            )
        return LatexDocxResolveResult(
            status="missing_latex_docx",
            reason="latex_input_not_found",
            resolved_filename=name,
        )

    stem = _stem_without_latex_suffix(name)
    for variant in _LATEX_SUFFIX_VARIANTS:
        candidate = directory / f"{stem}{variant}"
        if candidate.is_file():
            return LatexDocxResolveResult(
                status="ok",
                path=candidate.resolve(),
                resolved_filename=candidate.name,
                reason=f"resolved{variant}",
            )

    return LatexDocxResolveResult(
        status="missing_latex_docx",
        reason="missing_latex_docx",
        resolved_filename=f"{stem}_Latex.docx",
    )


def build_curriculum_info_for_v3_import(
    *,
    latex_docx_path: Path | str,
    original_docx_filename: str,
    curriculum: str = "vocational",
    publisher: str = "longteng",
    grade: int = 10,
    volume: str = "數學B2",
    import_mode: str = "docx_problems",
    apply_policy: bool = True,
    logger: Any = None,
) -> dict[str, Any]:
    """Build V2-compatible curriculum_info from V3 source metadata."""
    original = os.path.basename(str(original_docx_filename or "").strip())
    latex_name = os.path.basename(str(latex_docx_path or "").strip())
    upload_names = resolve_upload_filenames(original, latex_name)
    filename_meta = parse_textbook_filename_metadata(upload_names["parse_filename"])

    section_code = str((filename_meta or {}).get("section_code") or "").strip()
    if str((filename_meta or {}).get("source_scope") or "") == "chapter_self_assessment":
        section_code = ""

    try:
        grade_val = int(grade)
    except (TypeError, ValueError):
        grade_val = 10

    volume_val = str(volume or "").strip()
    from core.textbook_processor import grade_for_vocational_math_volume

    mapped_grade = grade_for_vocational_math_volume(volume_val)
    if mapped_grade is not None:
        grade_val = mapped_grade

    curriculum_info: dict[str, Any] = {
        "curriculum": str(curriculum or "vocational").strip() or "vocational",
        "publisher": str(publisher or "longteng").strip() or "longteng",
        "grade": grade_val,
        "volume": volume_val,
        "section_code": section_code,
        "import_mode": str(import_mode or "docx_problems").strip() or "docx_problems",
        "original_filename": upload_names["original_filename"],
        "saved_filename": upload_names["saved_filename"],
        "parse_filename": upload_names["parse_filename"],
        "chapter_index": (filename_meta or {}).get("chapter_index"),
        "source_scope": (filename_meta or {}).get("source_scope"),
    }

    if apply_policy:
        from core.routes.admin import apply_mathb_import_policy

        apply_mathb_import_policy(
            curriculum_info,
            {},
            filenames=[curriculum_info["parse_filename"]],
            logger=logger,
        )

    return curriculum_info


def _pick_b2_11_file(source_dir: Path, glob_pattern: str, *, latex: bool | None = None) -> Path | None:
    matches = sorted(
        (p for p in source_dir.glob(glob_pattern) if p.is_file()),
        key=lambda p: p.name.lower(),
    )
    for path in matches:
        if latex is True and not _is_latex_docx_filename(path.name):
            continue
        if latex is False and _is_latex_docx_filename(path.name):
            continue
        if "自我評量" in path.name:
            continue
        if not re.search(r"(?<!\d)1-1(?!\d)", path.name):
            continue
        return path
    return None


def find_b2_11_source_pair(project_root: Path | str) -> B211SourcePairStatus:
    """Locate B2 chapter 1 section 1 source pair under V3 storage."""
    root = Path(project_root)
    source_dir, _relative = resolve_source_directory(root, "vocational", "數學B2")

    original_docx = _pick_b2_11_file(source_dir, B2_11_GLOB_DOCX, latex=False)
    pdf = _pick_b2_11_file(source_dir, B2_11_GLOB_PDF)
    latex_docx: Path | None = None
    latex_resolve: LatexDocxResolveResult | None = None
    missing: list[str] = []

    if original_docx is None:
        missing.append("original_docx")
    if pdf is None:
        missing.append("pdf")

    if original_docx is not None:
        latex_resolve = resolve_latex_docx_path(source_dir, original_docx.name)
        if latex_resolve.status == "ok" and latex_resolve.path is not None:
            latex_docx = latex_resolve.path
        else:
            missing.append("latex_docx")
    else:
        latex_candidate = _pick_b2_11_file(source_dir, B2_11_GLOB_DOCX, latex=True)
        if latex_candidate is not None:
            latex_docx = latex_candidate
            latex_resolve = resolve_latex_docx_path(source_dir, latex_candidate.name)
        else:
            missing.append("latex_docx")

    return B211SourcePairStatus(
        source_dir=source_dir,
        original_docx=original_docx,
        pdf=pdf,
        latex_docx=latex_docx,
        latex_resolve=latex_resolve,
        missing=tuple(missing),
    )


def run_or_enqueue_v3_word_import(
    latex_docx_path: Path | str,
    curriculum_info: dict[str, Any],
    *,
    enqueue: bool = False,
    app: Any = None,
    task_queues: dict[str, queue.Queue] | None = None,
    background_worker: Callable[..., None] | None = None,
) -> dict[str, Any]:
    """
    Run or enqueue V2 Word import via existing background worker.

    Synchronous mode calls process_textbook_file_v2 inside app context.
    """
    path = str(Path(latex_docx_path).resolve())
    if enqueue:
        if app is None:
            raise ValueError("app_required_for_enqueue")
        worker = background_worker
        if worker is None:
            from core.routes.admin import background_processing_v2

            worker = background_processing_v2

        task_id = str(uuid.uuid4())
        q: queue.Queue = queue.Queue()
        stores = task_queues if task_queues is not None else {}
        stores[task_id] = q
        threading.Thread(
            target=worker,
            args=(path, q, app.app_context(), curriculum_info),
        ).start()
        return {
            "mode": "enqueued",
            "task_id": task_id,
            "latex_docx_path": path,
            "task_queues": stores,
        }

    if app is None:
        raise ValueError("app_required_for_sync_import")

    from core.textbook_processor_v2 import process_textbook_file_v2

    logs: list[str] = []
    task_q: queue.Queue = queue.Queue()
    with app.app_context():
        try:
            result = process_textbook_file_v2(path, curriculum_info, task_q)
        except Exception as exc:
            while not task_q.empty():
                logs.append(str(task_q.get_nowait()))
            return {
                "mode": "sync",
                "success": False,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "latex_docx_path": path,
                "logs": logs,
            }

        while not task_q.empty():
            logs.append(str(task_q.get_nowait()))

    return {
        "mode": "sync",
        "success": bool(result.get("success")),
        "result": result,
        "latex_docx_path": path,
        "logs": logs,
    }


def verify_b2_11_word_import(project_root: Path | str, app: Any) -> dict[str, Any]:
    """End-to-end verification for B2 1-1 only (no PDF phase)."""
    pair = find_b2_11_source_pair(project_root)
    report: dict[str, Any] = {
        "source_dir": str(pair.source_dir),
        "original_docx": str(pair.original_docx) if pair.original_docx else None,
        "pdf": str(pair.pdf) if pair.pdf else None,
        "latex_docx": str(pair.latex_docx) if pair.latex_docx else None,
        "missing": list(pair.missing),
        "latex_resolve": None,
        "curriculum_info": None,
        "import": None,
        "textbook_examples": [],
    }

    if pair.latex_resolve is not None:
        report["latex_resolve"] = {
            "status": pair.latex_resolve.status,
            "reason": pair.latex_resolve.reason,
            "resolved_filename": pair.latex_resolve.resolved_filename,
            "path": str(pair.latex_resolve.path) if pair.latex_resolve.path else None,
        }

    if pair.missing:
        if "latex_docx" in pair.missing:
            report["status"] = "missing_latex_docx"
        else:
            report["status"] = "missing_source_files"
        return report

    assert pair.original_docx is not None
    assert pair.latex_docx is not None

    curriculum_info = build_curriculum_info_for_v3_import(
        latex_docx_path=pair.latex_docx,
        original_docx_filename=pair.original_docx.name,
    )
    report["curriculum_info"] = curriculum_info

    import_result = run_or_enqueue_v3_word_import(
        pair.latex_docx,
        curriculum_info,
        enqueue=False,
        app=app,
    )
    report["import"] = import_result

    if not import_result.get("success"):
        report["status"] = "import_failed"
        return report

    from models import TextbookExample

    with app.app_context():
        rows = (
            TextbookExample.query.filter_by(
                source_curriculum="vocational",
                source_volume="數學B2",
            )
            .filter(TextbookExample.source_section.like("1-1%"))
            .order_by(TextbookExample.id.asc())
            .all()
        )
        report["textbook_examples"] = [
            {
                "id": row.id,
                "source_description": row.source_description,
                "source_volume": row.source_volume,
                "source_chapter": row.source_chapter,
                "source_section": row.source_section,
                "problem_type": row.problem_type,
                "skill_id": row.skill_id,
            }
            for row in rows
        ]
        report["textbook_examples_count"] = len(rows)
        report["inserted"] = (import_result.get("result") or {}).get("inserted")
        report["updated"] = (import_result.get("result") or {}).get("updated")

    report["status"] = "ok"
    return report
