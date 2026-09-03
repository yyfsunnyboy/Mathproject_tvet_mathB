# -*- coding: utf-8 -*-
"""Stable textbook question anchors for V3 PDF matching (no DB / no PDF)."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

from core.textbook_importer_v3_storage import VOLUME_DIRECTORY_MAP

SHA256_HEX_LEN = 64

SOURCE_TYPE_TO_QUESTION_TYPE: dict[str, str] = {
    "textbook_example": "example",
    "in_class_practice": "in_class_practice",
    "textbook_exercise": "exercise",
    "basic_exercise": "exercise",
    "textbook_practice": "exercise",
    "advanced_exercise": "advanced_exercise",
    "exam_practice": "exam",
    "self_assessment": "self_assessment",
    "section_exposition": "exposition",
}

_REQUIRED_ANCHOR_FIELDS = (
    "anchor_id",
    "curriculum",
    "publisher",
    "volume",
    "chapter",
    "section",
    "question_type",
    "question_number",
    "source_order",
    "question_label",
    "text_fingerprint",
)


def volume_slug(volume: str) -> str:
    raw = str(volume or "").strip()
    mapped = VOLUME_DIRECTORY_MAP.get(raw)
    if mapped:
        return mapped
    m = re.search(r"數學\s*B\s*(\d+)", raw, flags=re.IGNORECASE)
    if m:
        return f"math_B{int(m.group(1))}"
    slug = re.sub(r"[^0-9A-Za-z_]+", "_", raw).strip("_")
    return slug or "unknown_volume"


def normalize_question_label(label: str) -> str:
    """Deterministic label normalization (NFKC, compact type+number)."""
    text = unicodedata.normalize("NFKC", str(label or "")).strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^例題\s*", "例", text)
    text = re.sub(r"^例\s+(\d+)", r"例\1", text)
    text = re.sub(r"^隨堂練習\s+", "隨堂練習", text)
    text = re.sub(r"(\d+-\d+)\s*習題\s+", r"\1習題 ", text)
    text = re.sub(r"基礎題\s+(\d+)", r"基礎題\1", text)
    text = re.sub(r"進階題\s+(\d+)", r"進階題\1", text)
    text = re.sub(r"自我評量\s+題\s+", "自我評量 題", text)
    text = re.sub(r"題\s+(\d+)", r"題\1", text)
    text = re.sub(r"(\d{2,3})\s*統測\s*([A-Ca-c])", lambda m: f"{int(m.group(1))}統測{m.group(2).upper()}", text)
    return text.strip()


def infer_source_type_from_label(label: str, fallback: str = "") -> str:
    text = normalize_question_label(label)
    if re.match(r"^例\d+", text) or re.match(r"^例題\d+", text):
        return "textbook_example"
    if text.startswith("隨堂練習"):
        return "in_class_practice"
    if "自我評量" in text:
        return "self_assessment"
    if "統測" in text or "學測" in text:
        return "exam_practice"
    if "進階題" in text:
        return "advanced_exercise"
    if "基礎題" in text or "習題" in text:
        return "textbook_exercise"
    return str(fallback or "").strip()


def canonicalize_question_type(source_type: str, question_label: str = "") -> str:
    raw = str(source_type or "").strip()
    mapped = SOURCE_TYPE_TO_QUESTION_TYPE.get(raw)
    if mapped:
        return mapped
    inferred = infer_source_type_from_label(question_label)
    return SOURCE_TYPE_TO_QUESTION_TYPE.get(inferred, inferred or "unknown")


def extract_question_number(label: str, source_type: str = "") -> str:
    """Return a stable question number token; empty string if none."""
    _ = source_type
    text = normalize_question_label(label)
    if not text:
        return ""
    m = re.search(r"(\d{2,3})統測([A-C])", text)
    if m:
        return f"{int(m.group(1))}{m.group(2)}"
    m = re.match(r"^例(\d+)$", text)
    if m:
        return str(int(m.group(1)))
    m = re.match(r"^隨堂練習(\d+)$", text)
    if m:
        return str(int(m.group(1)))
    m = re.search(r"(?:基礎題|進階題)(\d+)$", text)
    if m:
        return str(int(m.group(1)))
    m = re.search(r"題(\d+)$", text)
    if m:
        return str(int(m.group(1)))
    m = re.search(r"(\d+)$", text)
    if m:
        return str(int(m.group(1)))
    return ""


def resolve_chapter_token(
    *,
    section_code: str = "",
    curriculum_info: dict[str, Any] | None = None,
) -> str:
    info = curriculum_info or {}
    raw_idx = info.get("chapter_index")
    if raw_idx is not None and str(raw_idx).strip() != "":
        try:
            return str(int(raw_idx))
        except (TypeError, ValueError):
            pass
    m = re.match(r"^(\d+)\s*-", str(section_code or "").strip())
    if m:
        return str(int(m.group(1)))
    return "0"


def resolve_section_code(
    *,
    block_meta: dict[str, Any] | None = None,
    curriculum_info: dict[str, Any] | None = None,
    question_label: str = "",
) -> str:
    meta = block_meta or {}
    info = curriculum_info or {}
    for candidate in (
        meta.get("section_code"),
        info.get("section_code"),
    ):
        code = str(candidate or "").strip()
        if re.match(r"^\d+-\d+$", code):
            return code
    m = re.search(r"(?<!\d)(\d+-\d+)(?!\d)", str(question_label or ""))
    if m:
        return m.group(1)
    return ""


def normalize_fingerprint_text(text: str) -> str:
    """Deterministic text for fingerprinting. Keeps CJK, digits, and LaTeX tokens."""
    value = unicodedata.normalize("NFKC", str(text or ""))
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[\t\f\v]+", " ", value)
    value = re.sub(r"\n+", " ", value)
    value = re.sub(r" +", " ", value)
    return value.strip()


def build_text_fingerprint(text: str) -> str:
    payload = normalize_fingerprint_text(text).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _question_number_token(question_number: str) -> str:
    raw = str(question_number or "").strip()
    if not raw:
        return "x"
    if raw.isdigit():
        return f"{int(raw):03d}"
    token = re.sub(r"[^0-9A-Za-z]+", "", raw).lower()
    return token or "x"


def _safe_id_token(value: str, *, default: str) -> str:
    token = re.sub(r"[^0-9A-Za-z\-]+", "_", str(value or "").strip())
    token = re.sub(r"_+", "_", token).strip("_-")
    return token or default


def build_anchor_id(
    *,
    curriculum: str,
    volume: str,
    section: str,
    question_type: str,
    question_number: str,
    source_order: int,
    occurrence_index: int = 1,
) -> str:
    parts = [
        _safe_id_token(curriculum, default="unknown"),
        _safe_id_token(volume_slug(volume), default="unknown_volume"),
        _safe_id_token(section or "section", default="section"),
        _safe_id_token(question_type, default="unknown"),
        _question_number_token(question_number),
        f"{int(source_order):03d}",
    ]
    anchor_id = "_".join(parts)
    if int(occurrence_index or 1) > 1:
        anchor_id = f"{anchor_id}_occ{int(occurrence_index):02d}"
    return anchor_id


def build_anchor_key(
    *,
    curriculum: str,
    publisher: str,
    volume: str,
    chapter: str,
    section: str,
    question_type: str,
    question_number: str,
    source_order: int,
) -> str:
    return "|".join(
        [
            str(curriculum or "").strip() or "unknown",
            str(publisher or "").strip() or "unknown",
            volume_slug(volume),
            str(chapter or "").strip() or "0",
            str(section or "").strip() or "section",
            str(question_type or "").strip() or "unknown",
            str(question_number or "").strip() or "x",
            str(int(source_order)),
        ]
    )


def build_question_anchor(
    *,
    question_label: str,
    problem_text: str,
    source_order: int,
    curriculum: str = "vocational",
    publisher: str = "longteng",
    volume: str = "",
    chapter: str = "",
    section: str = "",
    source_type: str = "",
    question_type: str = "",
    question_number: str | None = None,
    occurrence_index: int = 1,
    block_index: int | None = None,
) -> dict[str, Any]:
    label = normalize_question_label(question_label)
    q_type = str(question_type or "").strip() or canonicalize_question_type(source_type, label)
    if question_number is None:
        q_number = extract_question_number(label, source_type=source_type)
    else:
        q_number = str(question_number).strip()
    order = int(source_order)
    occ = max(1, int(occurrence_index or 1))
    fingerprint = build_text_fingerprint(problem_text)
    anchor_id = build_anchor_id(
        curriculum=curriculum,
        volume=volume,
        section=section,
        question_type=q_type,
        question_number=q_number,
        source_order=order,
        occurrence_index=occ,
    )
    return {
        "anchor_id": anchor_id,
        "anchor_key": build_anchor_key(
            curriculum=curriculum,
            publisher=publisher,
            volume=volume,
            chapter=str(chapter or "").strip() or "0",
            section=str(section or "").strip(),
            question_type=q_type,
            question_number=q_number,
            source_order=order,
        ),
        "curriculum": str(curriculum or "").strip(),
        "publisher": str(publisher or "").strip(),
        "volume": str(volume or "").strip(),
        "chapter": str(chapter or "").strip() or "0",
        "section": str(section or "").strip(),
        "question_type": q_type,
        "question_number": q_number,
        "source_order": order,
        "block_index": int(block_index) if block_index is not None else order - 1,
        "occurrence_index": occ,
        "question_label": label,
        "source_type": str(source_type or infer_source_type_from_label(label)).strip(),
        "text_fingerprint": fingerprint,
    }


def validate_question_anchor(anchor: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(anchor, dict):
        return False, ["anchor_not_dict"]
    for field in _REQUIRED_ANCHOR_FIELDS:
        if field not in anchor:
            errors.append(f"missing_{field}")
    fingerprint = str(anchor.get("text_fingerprint") or "")
    if not fingerprint:
        errors.append("empty_text_fingerprint")
    elif not re.fullmatch(r"[0-9a-f]{" + str(SHA256_HEX_LEN) + r"}", fingerprint):
        errors.append("invalid_text_fingerprint")
    try:
        order = int(anchor.get("source_order"))
        if order < 1:
            errors.append("source_order_not_positive")
    except (TypeError, ValueError):
        errors.append("source_order_not_int")
    if not str(anchor.get("anchor_id") or "").strip():
        errors.append("empty_anchor_id")
    if not str(anchor.get("question_label") or "").strip():
        errors.append("empty_question_label")
    return not errors, errors


def detect_anchor_id_collisions(anchors: list[dict[str, Any]]) -> list[str]:
    counts = Counter(str(row.get("anchor_id") or "") for row in anchors)
    return sorted(anchor_id for anchor_id, n in counts.items() if anchor_id and n > 1)


def detect_type_number_collisions(anchors: list[dict[str, Any]]) -> list[tuple[str, str]]:
    counts = Counter(
        (str(row.get("question_type") or ""), str(row.get("question_number") or ""))
        for row in anchors
        if str(row.get("question_number") or "")
    )
    return sorted((q_type, q_num) for (q_type, q_num), n in counts.items() if n > 1)


def source_order_is_monotonic(anchors: list[dict[str, Any]]) -> bool:
    orders = [int(row["source_order"]) for row in anchors]
    return orders == list(range(1, len(orders) + 1))


def _apply_occurrence_tie_breakers(anchors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """If anchor_id collides, append deterministic occurrence index. Never use UUID."""
    seen: dict[str, int] = {}
    adjusted: list[dict[str, Any]] = []
    for row in anchors:
        base_id = str(row.get("anchor_id") or "")
        seen[base_id] = seen.get(base_id, 0) + 1
        occ = seen[base_id]
        if occ == 1:
            adjusted.append(row)
            continue
        rebuilt = dict(row)
        rebuilt["occurrence_index"] = occ
        rebuilt["anchor_id"] = build_anchor_id(
            curriculum=str(row.get("curriculum") or ""),
            volume=str(row.get("volume") or ""),
            section=str(row.get("section") or ""),
            question_type=str(row.get("question_type") or ""),
            question_number=str(row.get("question_number") or ""),
            source_order=int(row.get("source_order") or 0),
            occurrence_index=occ,
        )
        adjusted.append(rebuilt)
    return adjusted


def build_anchors_from_block_meta(
    block_meta: dict[str, dict[str, Any]],
    curriculum_info: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Convert V2 Phase2 `_DOCX_BLOCK_META` into stable question anchors.

    `source_order` is 1-based insertion order of the Phase2 meta dict
    (document scan order from `_build_anchor_blocks_v2`).
    """
    info = dict(curriculum_info or {})
    curriculum = str(info.get("curriculum") or "vocational").strip() or "vocational"
    publisher = str(info.get("publisher") or "longteng").strip() or "longteng"
    volume = str(info.get("volume") or "").strip()

    anchors: list[dict[str, Any]] = []
    for source_order, (raw_key, meta) in enumerate((block_meta or {}).items(), start=1):
        block = meta if isinstance(meta, dict) else {}
        label = str(block.get("anchor") or raw_key or "").strip()
        source_type = str(block.get("source_type") or "").strip() or infer_source_type_from_label(label)
        section = resolve_section_code(
            block_meta=block,
            curriculum_info=info,
            question_label=label,
        )
        chapter = resolve_chapter_token(section_code=section, curriculum_info=info)
        problem_text = str(block.get("problem_text") or "")
        anchors.append(
            build_question_anchor(
                question_label=label,
                problem_text=problem_text,
                source_order=source_order,
                curriculum=curriculum,
                publisher=publisher,
                volume=volume,
                chapter=chapter,
                section=section,
                source_type=source_type,
                block_index=source_order - 1,
            )
        )
    return _apply_occurrence_tie_breakers(anchors)


def question_anchor_notes_payload(anchor: dict[str, Any]) -> dict[str, Any]:
    """JSON-ready payload for TextbookExample.notes.question_anchor."""
    return {
        "question_anchor": {
            key: anchor.get(key)
            for key in (
                "anchor_id",
                "anchor_key",
                "curriculum",
                "publisher",
                "volume",
                "chapter",
                "section",
                "question_type",
                "question_number",
                "source_order",
                "block_index",
                "occurrence_index",
                "question_label",
                "source_type",
                "text_fingerprint",
            )
        }
    }


def build_pdf_match_stub(anchor: dict[str, Any]) -> dict[str, Any]:
    """Future PDF matcher record. Values stay null this round."""
    return {
        "anchor_id": str(anchor.get("anchor_id") or ""),
        "textbook_example_id": None,
        "pdf_page": None,
        "pdf_bbox": None,
        "match_method": None,
        "match_score": None,
        "image_path": None,
    }


def summarize_anchor_collection(anchors: list[dict[str, Any]]) -> dict[str, Any]:
    collisions = detect_anchor_id_collisions(anchors)
    type_number_collisions = detect_type_number_collisions(anchors)
    invalid = []
    for row in anchors:
        ok, errors = validate_question_anchor(row)
        if not ok:
            invalid.append({"anchor_id": row.get("anchor_id"), "errors": errors})
    empty_fp = [row["anchor_id"] for row in anchors if not str(row.get("text_fingerprint") or "")]
    return {
        "anchor_count": len(anchors),
        "collision_count": len(collisions),
        "collisions": collisions,
        "type_number_collision_count": len(type_number_collisions),
        "type_number_collisions": type_number_collisions,
        "source_order_monotonic": source_order_is_monotonic(anchors),
        "invalid_count": len(invalid),
        "invalid": invalid,
        "empty_fingerprint_count": len(empty_fp),
        "pdf_match_stubs": [build_pdf_match_stub(row) for row in anchors],
    }


def format_anchor_report(
    *,
    latex_docx_path: str,
    phase1_line_count: int,
    phase2_block_count: int,
    anchors: list[dict[str, Any]],
    summary: dict[str, Any],
    preview_limit: int = 10,
    preview_chars: int = 50,
) -> str:
    lines = [
        "B2 1-1 Question Anchor Report",
        "-----------------------------",
        f"Source: {latex_docx_path}",
        f"Phase1 lines: {phase1_line_count}",
        f"Phase2 blocks: {phase2_block_count}",
        f"Anchors: {summary.get('anchor_count', 0)}",
        f"anchor_id collisions: {summary.get('collision_count', 0)}",
        f"type+number collisions: {summary.get('type_number_collision_count', 0)}",
        f"source_order monotonic: {summary.get('source_order_monotonic')}",
        f"empty fingerprints: {summary.get('empty_fingerprint_count', 0)}",
        "",
        "Representative questions:",
    ]
    for row in anchors[: max(0, int(preview_limit))]:
        text = normalize_fingerprint_text(str(row.get("_problem_text") or row.get("problem_text") or ""))
        snippet = text[: int(preview_chars)]
        fp = str(row.get("text_fingerprint") or "")[:12]
        lines.append(
            f"- order={row.get('source_order')} label={row.get('question_label')!r} "
            f"type={row.get('question_type')} num={row.get('question_number')!r} "
            f"anchor_id={row.get('anchor_id')} fp={fp} text={snippet!r}"
        )
    return "\n".join(lines) + "\n"


def collect_question_anchors_from_latex_docx(
    latex_docx_path: Path | str,
    curriculum_info: dict[str, Any],
    *,
    app: Any = None,
) -> dict[str, Any]:
    """
    Run V2 Phase1 + Phase2 only. Never Phase3/Phase4. Rollback any incidental DB writes.
    """
    from core.textbook_processor_v2 import (
        _DOCX_BLOCK_META,
        phase1_extract_docx_lines,
        phase2_deterministic_block_slice,
    )

    path = str(Path(latex_docx_path).resolve())
    ctx = app.app_context() if app is not None else None
    entered = False
    try:
        if ctx is not None:
            ctx.__enter__()
            entered = True
        lines = phase1_extract_docx_lines(path)
        scope = str((curriculum_info or {}).get("source_scope") or "section_textbook")
        blocks = phase2_deterministic_block_slice(
            lines,
            source_scope=scope,
            curriculum_info=curriculum_info,
        )
        block_meta = dict(_DOCX_BLOCK_META or {})
        if not block_meta:
            block_meta = {
                key: {
                    "anchor": key,
                    "source_type": infer_source_type_from_label(key),
                    "problem_text": text,
                    "section_code": str((curriculum_info or {}).get("section_code") or ""),
                }
                for key, text in (blocks or {}).items()
            }
        anchors = build_anchors_from_block_meta(block_meta, curriculum_info)
        for row, key in zip(anchors, block_meta.keys()):
            row["_problem_text"] = str((block_meta.get(key) or {}).get("problem_text") or "")
        summary = summarize_anchor_collection(anchors)
        return {
            "status": "ok",
            "latex_docx_path": path,
            "phase1_line_count": len(lines),
            "phase2_block_count": len(blocks),
            "block_keys": list(block_meta.keys()),
            "block_meta_fields": sorted({field for meta in block_meta.values() for field in meta.keys()}),
            "anchors": anchors,
            "summary": summary,
            "report": format_anchor_report(
                latex_docx_path=path,
                phase1_line_count=len(lines),
                phase2_block_count=len(blocks),
                anchors=anchors,
                summary=summary,
            ),
        }
    except Exception as exc:
        return {
            "status": "phase2_failed" if "phase" in str(exc).lower() else "collect_failed",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "latex_docx_path": path,
        }
    finally:
        if entered:
            try:
                from models import db

                db.session.rollback()
            except Exception:
                pass
            ctx.__exit__(None, None, None)


def collect_b2_11_question_anchors(project_root: Path | str, *, app: Any = None) -> dict[str, Any]:
    from core.textbook_importer_v3_orchestrate import (
        build_curriculum_info_for_v3_import,
        find_b2_11_source_pair,
    )

    pair = find_b2_11_source_pair(project_root)
    if pair.latex_docx is None:
        return {
            "status": "missing_latex_docx",
            "source_dir": str(pair.source_dir),
            "missing": list(pair.missing),
            "original_docx": str(pair.original_docx) if pair.original_docx else None,
            "pdf": str(pair.pdf) if pair.pdf else None,
            "latex_docx": None,
        }
    original_name = pair.original_docx.name if pair.original_docx else pair.latex_docx.name
    curriculum_info = build_curriculum_info_for_v3_import(
        latex_docx_path=pair.latex_docx,
        original_docx_filename=original_name,
        apply_policy=False,
    )
    result = collect_question_anchors_from_latex_docx(
        pair.latex_docx,
        curriculum_info,
        app=app,
    )
    result["source_dir"] = str(pair.source_dir)
    result["original_docx"] = str(pair.original_docx) if pair.original_docx else None
    result["pdf"] = str(pair.pdf) if pair.pdf else None
    result["curriculum_info"] = curriculum_info
    return result
