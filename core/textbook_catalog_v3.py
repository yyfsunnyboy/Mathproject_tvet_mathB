# -*- coding: utf-8 -*-
"""V3 whole-book catalog import: PDF table of contents → outline SkillInfo/SkillCurriculum.

Reuses the existing SkillInfo + SkillCurriculum tables used by section outline ensure.
Does not create a second outline table.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from flask import current_app

from models import SkillCurriculum, SkillInfo, db
from core.textbook_processor import grade_for_vocational_math_volume
from core.textbook_processor_v2 import _ensure_outline_skill_info_v2
from core.textbook_section_outline import (
    _normalize_space,
    build_outline_skill_id_for_section,
    outline_display_order_from_section_code,
)

_logger = logging.getLogger(__name__)


def _chapters_to_list(chapters: list[CatalogChapter]) -> list[dict]:
    """Serialise CatalogChapter list to plain JSON-able dicts."""
    out = []
    for ch in chapters:
        out.append({
            "chapter_index": ch.chapter_index,
            "chapter_title": ch.chapter_title,
            "sections": [
                {
                    "section_code": s.section_code,
                    "section_index": s.section_index,
                    "section_title": s.section_title,
                    "page": s.page,
                }
                for s in ch.sections
            ],
        })
    return out


def _chapters_from_list(data: list[dict]) -> list[CatalogChapter]:
    """Deserialise plain dicts back to CatalogChapter list."""
    chapters = []
    for ch in data:
        sections = []
        for s in ch.get("sections") or []:
            sections.append(
                CatalogSection(
                    section_code=str(s.get("section_code") or ""),
                    section_index=int(s.get("section_index") or 0),
                    section_title=str(s.get("section_title") or ""),
                    page=s.get("page"),
                )
            )
        chapters.append(
            CatalogChapter(
                chapter_index=int(ch.get("chapter_index") or 0),
                chapter_title=str(ch.get("chapter_title") or ""),
                sections=sections,
            )
        )
    return chapters


def apply_catalog_from_token(
    token: str,
    *,
    commit: bool = True,
) -> dict[str, Any]:
    """Confirm step: decode a preview token and apply it to the DB.

    Raises ValueError (with a human-readable message) on any token failure.
    """
    try:
        payload = decode_preview_token(token)
    except ValueError as exc:
        raise ValueError(f"預覽資料已失效，請重新解析目錄。（{exc}）") from exc

    # Validate required fields
    curriculum = str(payload.get("curriculum") or "").strip()
    volume = str(payload.get("volume") or "").strip()
    grade = payload.get("grade")
    chapters_data = payload.get("chapters")
    if not curriculum or not volume or grade is None or not chapters_data:
        raise ValueError("預覽資料已失效，請重新解析目錄。（missing_fields）")

    try:
        grade = int(grade)
        chapters = _chapters_from_list(chapters_data)
    except Exception as exc:
        raise ValueError(f"預覽資料格式錯誤，請重新解析目錄。（{exc}）") from exc

    report = _apply_catalog_to_db(
        curriculum=curriculum,
        volume=volume,
        grade=grade,
        chapters=chapters,
        dry_run=False,
        commit=commit,
    )
    return {
        **report.to_dict(),
        "curriculum": curriculum,
        "volume": volume,
        "grade": grade,
        "confirmed": True,
    }


# ---------------------------------------------------------------------------
# Preview token: server-signed payload so the confirm step can trust it
# without re-calling the AI.  TTL = 30 minutes.
# ---------------------------------------------------------------------------
_PREVIEW_TOKEN_TTL = 1800  # seconds


def _preview_secret() -> bytes:
    """Return a stable per-process secret derived from Flask SECRET_KEY."""
    try:
        key = current_app.secret_key or b"fallback-catalog-preview-secret"
        if isinstance(key, str):
            key = key.encode()
        return key
    except RuntimeError:
        return b"fallback-catalog-preview-secret"


def encode_preview_token(catalog_payload: dict) -> str:
    """Encode a catalog payload dict as a signed token string (JSON + HMAC).

    Format: <base64-like hex>.<timestamp>.<hmac>
    We use a simple JSON + HMAC-SHA256 approach without external deps.
    """
    ts = str(int(time.time()))
    body = json.dumps(catalog_payload, ensure_ascii=False, separators=(",", ":"))
    body_hex = body.encode().hex()
    sig = hmac.new(_preview_secret(), f"{body_hex}.{ts}".encode(), hashlib.sha256).hexdigest()
    return f"{body_hex}.{ts}.{sig}"


def decode_preview_token(token: str) -> dict:
    """Decode and verify a preview token.  Raises ValueError on any failure."""
    if not token or not isinstance(token, str):
        raise ValueError("missing_token")
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("invalid_token_format")
    body_hex, ts_str, sig = parts
    try:
        ts = int(ts_str)
    except ValueError:
        raise ValueError("invalid_token_timestamp")
    age = int(time.time()) - ts
    if age < 0 or age > _PREVIEW_TOKEN_TTL:
        raise ValueError("token_expired")
    expected_sig = hmac.new(
        _preview_secret(), f"{body_hex}.{ts_str}".encode(), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        raise ValueError("token_signature_invalid")
    try:
        body = bytes.fromhex(body_hex).decode()
        return json.loads(body)
    except Exception as exc:
        raise ValueError(f"token_decode_error: {exc}") from exc


class V3CatalogError(Exception):
    """Fatal catalog validation or extraction failure."""

    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


@dataclass
class CatalogSection:
    section_code: str
    section_index: int
    section_title: str
    page: int | None = None


@dataclass
class CatalogChapter:
    chapter_index: int
    chapter_title: str
    sections: list[CatalogSection] = field(default_factory=list)


@dataclass
class CatalogImportReport:
    ok: bool = True
    chapters_created: int = 0
    chapters_updated: int = 0
    sections_created: int = 0
    sections_reused: int = 0
    sections_updated: int = 0
    conflicts: list[dict] = field(default_factory=list)
    needs_review: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "chapters_created": self.chapters_created,
            "chapters_updated": self.chapters_updated,
            "sections_created": self.sections_created,
            "sections_reused": self.sections_reused,
            "sections_updated": self.sections_updated,
            "conflicts": self.conflicts,
            "needs_review": self.needs_review,
            "errors": self.errors,
        }


def _is_likely_toc_page(page_text: str) -> bool:
    """Heuristic: a TOC page should mention chapter markers and section codes."""
    text = str(page_text or "")
    has_chapter_marker = bool(re.search(r"第\s*\d+\s*章", text))
    section_codes = re.findall(r"\b\d+-\d+\b", text)
    return has_chapter_marker and len(section_codes) >= 2


def _detect_catalog_pages(pdf_path: str | Path, max_pages: int = 10) -> list[int]:
    """Scan the first N pages of a PDF and return page numbers that look like a TOC."""
    import fitz

    path = str(pdf_path or "").strip()
    if not path or not os.path.isfile(path):
        raise V3CatalogError("pdf_not_found", f"PDF not found: {path}")
    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise V3CatalogError("pdf_open_failed", f"Failed to open PDF: {exc}")

    try:
        page_count = len(doc)
        candidates = []
        for i in range(min(max_pages, page_count)):
            page_text = doc[i].get_text() or ""
            if _is_likely_toc_page(page_text):
                candidates.append(i + 1)
        if not candidates:
            # Fallback: render the first few pages so the vision model can locate the TOC.
            fallback = min(5, page_count)
            candidates = list(range(1, fallback + 1))
        return candidates
    finally:
        doc.close()


def _render_pages_to_images(pdf_path: str | Path, page_numbers: list[int], dpi: int = 200) -> list[str]:
    """Render selected PDF pages to PNG images. Returns a list of temp file paths."""
    from core.question_image_assets import render_pdf_page_to_image
    import tempfile

    temp_dir = Path(tempfile.mkdtemp(prefix="catalog_v3_"))
    paths = []
    for page_no in page_numbers:
        out_path = temp_dir / f"page_{page_no:03d}.png"
        render_pdf_page_to_image(
            str(pdf_path),
            page_index=page_no - 1,
            output_path=str(out_path),
            dpi=dpi,
        )
        paths.append(str(out_path))
    return paths


def _build_catalog_extraction_prompt(page_numbers: list[int], volume: str) -> str:
    return (
        "You are a textbook catalog extractor. "
        "The following images are pages from the table of contents of a vocational math textbook. "
        "Return a single strict JSON object with this exact schema:\n\n"
        "{\n"
        '  "volume": "' + (volume or "數學B2") + '",\n'
        '  "chapters": [\n'
        "    {\n"
        '      "chapter_index": 1,\n'
        '      "chapter_title": "三角函數",\n'
        '      "sections": [\n'
        "        {\n"
        '          "section_code": "1-1",\n'
        '          "section_index": 1,\n'
        '          "section_title": "角度的基本性質",\n'
        '          "page": 2\n'
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "1. chapter_index must be a positive integer.\n"
        "2. section_code must be exactly 'chapter_index-section_index' (e.g. 1-2).\n"
        "3. Do NOT include '第X章' prefix in chapter_title; return only the title text (e.g. '三角函數').\n"
        "4. Do NOT include section_code prefix in section_title; return only the title text (e.g. '銳角三角函數').\n"
        "5. 'page' is optional and may be omitted or set to null.\n"
        "6. Return ONLY valid JSON, no markdown, no explanation.\n"
        f"Pages provided: {page_numbers}."
    )


def _call_gemini_catalog_vision(model, prompt: str, image_paths: list[str]) -> str:
    """Call Gemini vision model with catalog page images."""
    import google.generativeai as genai

    uploaded_files = []
    try:
        uploaded_files = [genai.upload_file(path=p) for p in image_paths]
        last_exc: Exception | None = None
        for attempt in range(1, 4):
            try:
                response = model.generate_content(
                    [prompt] + uploaded_files,
                    generation_config={
                        "temperature": 0.0,
                        "max_output_tokens": 4096,
                    },
                )
                raw = str(response.text or "").strip()
                if raw:
                    return raw
                raise RuntimeError("empty response")
            except Exception as exc:
                last_exc = exc
                _logger.warning("[catalog_v3] Gemini vision attempt %s failed: %s", attempt, exc)
        raise V3CatalogError(
            "gemini_catalog_vision_failed",
            f"Gemini vision catalog extraction failed after retries: {last_exc}",
        )
    finally:
        for f in uploaded_files:
            try:
                genai.delete_file(f.name)
            except Exception:
                pass
        # Best-effort cleanup of the locally rendered temp files.
        for p in image_paths:
            try:
                if os.path.exists(p):
                    os.unlink(p)
            except Exception:
                pass
        try:
            if image_paths:
                temp_dir = Path(image_paths[0]).parent
                if temp_dir.exists():
                    temp_dir.rmdir()
        except Exception:
            pass


def _parse_catalog_json(raw: str) -> dict:
    """Parse Gemini JSON response, cleaning markdown fences if needed."""
    from core.ai_analyzer import clean_and_parse_json

    try:
        return clean_and_parse_json(raw)
    except Exception as exc:
        # Fallback: try to isolate the outer JSON object
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        raise V3CatalogError(
            "catalog_json_parse_failed",
            f"Failed to parse catalog JSON: {exc}",
            {"raw_preview": raw[:500]},
        )


def _normalize_title(raw: str) -> str:
    """NFKC normalize and collapse whitespace."""
    text = unicodedata.normalize("NFKC", str(raw or "")).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def validate_catalog_payload(payload: dict) -> list[str]:
    """Deterministic validation of the catalog AI JSON."""
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload must be a JSON object"]

    volume = str(payload.get("volume") or "").strip()
    if not volume:
        errors.append("missing volume")

    chapters = payload.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        errors.append("chapters must be a non-empty list")
        return errors

    seen_chapters: set[int] = set()
    seen_section_codes: set[str] = set()

    for ch in chapters:
        if not isinstance(ch, dict):
            errors.append("each chapter must be an object")
            continue

        ch_idx_raw = ch.get("chapter_index")
        try:
            ch_idx = int(ch_idx_raw)
            if ch_idx <= 0:
                raise ValueError
        except (TypeError, ValueError):
            errors.append(f"invalid chapter_index: {ch_idx_raw!r}")
            continue

        if ch_idx in seen_chapters:
            errors.append(f"duplicate chapter_index: {ch_idx}")
        seen_chapters.add(ch_idx)

        ch_title = _normalize_title(ch.get("chapter_title"))
        if not ch_title:
            errors.append(f"chapter {ch_idx} missing chapter_title")

        sections = ch.get("sections")
        if not isinstance(sections, list) or not sections:
            errors.append(f"chapter {ch_idx} has no sections")
            continue

        for sec in sections:
            if not isinstance(sec, dict):
                errors.append(f"chapter {ch_idx} section must be an object")
                continue

            sec_code = str(sec.get("section_code") or "").strip()
            if not re.match(r"^\d+-\d+$", sec_code):
                errors.append(f"chapter {ch_idx} invalid section_code: {sec_code!r}")
                continue

            sec_ch_part = sec_code.split("-")[0]
            try:
                sec_ch_idx = int(sec_ch_part)
            except ValueError:
                errors.append(f"section {sec_code} has non-numeric chapter part")
                continue

            if sec_ch_idx != ch_idx:
                errors.append(
                    f"section {sec_code} chapter part {sec_ch_idx} does not match "
                    f"chapter_index {ch_idx}"
                )
                continue

            sec_idx_raw = sec.get("section_index")
            try:
                sec_idx = int(sec_idx_raw)
                if sec_idx <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                errors.append(f"section {sec_code} invalid section_index: {sec_idx_raw!r}")
                continue

            expected_code = f"{ch_idx}-{sec_idx}"
            if sec_code != expected_code:
                errors.append(
                    f"section {sec_code} does not match chapter_index-section_index "
                    f"({expected_code})"
                )
                continue

            sec_title = _normalize_title(sec.get("section_title"))
            if not sec_title:
                errors.append(f"section {sec_code} missing section_title")
                continue

            if sec_code in seen_section_codes:
                errors.append(f"duplicate section_code: {sec_code}")
            seen_section_codes.add(sec_code)

    return errors


def _canonical_chapter_display(chapter_index: int, chapter_title: str) -> str:
    """Return chapter string for canonical storage, e.g. '第1章 三角函數'.

    Normalisation rules:
    - Strip any leading '第N章' / 'N ' prefix from chapter_title before re-attaching,
      so that titles like '第1章 三角函數' or '1 三角函數' don't produce duplicates.
    - Output format: '第{chapter_index}章 {bare_title}'.strip()
    """
    title = _normalize_title(chapter_title)
    # Remove leading numeric prefix variants so we can re-attach the canonical one.
    # Matches: "第1章 ...", "第1章...", "1 ...", "1. ..."
    bare = re.sub(r"^第\d+章\s*", "", title).strip()
    bare = re.sub(r"^\d+[.\s]\s*", "", bare).strip()
    if not bare:
        bare = title  # fallback: keep original if stripping left nothing
    chapter_label = f"第{chapter_index}章"
    return f"{chapter_label} {bare}".strip() if bare else chapter_label


def _canonical_section_display(section_code: str, section_title: str) -> str:
    """Return section string for canonical storage (e.g. '1-2 銳角三角函數')."""
    title = _normalize_title(section_title)
    return f"{section_code} {title}".strip()


def _parse_catalog(payload: dict) -> list[CatalogChapter]:
    """Convert validated payload into dataclasses."""
    out: list[CatalogChapter] = []
    for ch in payload.get("chapters") or []:
        if not isinstance(ch, dict):
            continue
        sections = []
        for sec in ch.get("sections") or []:
            if not isinstance(sec, dict):
                continue
            page = sec.get("page")
            try:
                page = int(page) if page is not None else None
            except (TypeError, ValueError):
                page = None
            sections.append(
                CatalogSection(
                    section_code=str(sec.get("section_code") or "").strip(),
                    section_index=int(sec.get("section_index")),
                    section_title=_normalize_title(sec.get("section_title")),
                    page=page,
                )
            )
        out.append(
            CatalogChapter(
                chapter_index=int(ch.get("chapter_index")),
                chapter_title=_normalize_title(ch.get("chapter_title")),
                sections=sections,
            )
        )
    return out


def _resolve_grade(volume: str, grade: int | None) -> int:
    mapped = grade_for_vocational_math_volume(volume)
    if mapped is not None:
        return mapped
    try:
        return int(grade or 10)
    except (TypeError, ValueError):
        return 10


def _extract_chapter_index(chapter_str: str) -> int | None:
    """Extract the numeric chapter index from any chapter alias string.

    Handles:
    - "第1章 三角函數"  → 1
    - "第1章"           → 1
    - "1 三角函數"      → 1
    - "1"               → 1
    - "1."              → 1
    Returns None when no numeric index can be found.
    """
    s = _normalize_space(chapter_str or "")
    m = re.match(r"^第(\d+)章", s)
    if m:
        return int(m.group(1))
    m = re.match(r"^(\d+)[\s.\u3002]", s)
    if m:
        return int(m.group(1))
    m = re.match(r"^(\d+)$", s)
    if m:
        return int(m.group(1))
    return None


def _find_existing_rows_by_chapter_index(
    *,
    curriculum: str,
    volume: str,
    grade: int,
    chapter_index: int,
) -> list[SkillCurriculum]:
    """Return all SkillCurriculum rows for this volume whose chapter alias maps to chapter_index.

    Covers all skill_id formats (real skills and outline placeholders alike).
    """
    # Pull all rows for this curriculum+grade+volume, then filter by alias.
    # We do it in Python because the alias extraction requires regex.
    all_rows = (
        SkillCurriculum.query.filter(
            SkillCurriculum.curriculum == curriculum,
            SkillCurriculum.volume == volume,
            SkillCurriculum.grade == grade,
            SkillCurriculum.chapter.isnot(None),
        ).all()
    )
    return [r for r in all_rows if _extract_chapter_index(r.chapter or "") == chapter_index]


def _find_existing_rows_by_section_code(
    *,
    curriculum: str,
    volume: str,
    grade: int,
    section_code: str,
) -> list[SkillCurriculum]:
    """Return all rows whose section starts with the given section code (any skill_id format)."""
    prefix = f"{section_code} "
    exact = section_code  # also match section == section_code (no title suffix)
    return (
        SkillCurriculum.query.filter(
            SkillCurriculum.curriculum == curriculum,
            SkillCurriculum.volume == volume,
            SkillCurriculum.grade == grade,
        )
        .filter(
            db.or_(
                SkillCurriculum.section.startswith(prefix),
                SkillCurriculum.section == exact,
            )
        )
        .order_by(SkillCurriculum.display_order.asc(), SkillCurriculum.id.asc())
        .all()
    )


def _find_existing_row_by_skill_id(
    *,
    curriculum: str,
    volume: str,
    grade: int,
    skill_id: str,
) -> SkillCurriculum | None:
    return (
        SkillCurriculum.query.filter(
            SkillCurriculum.curriculum == curriculum,
            SkillCurriculum.volume == volume,
            SkillCurriculum.grade == grade,
            SkillCurriculum.skill_id == skill_id,
        )
        .first()
    )


def _update_skill_info_description(
    skill_id: str,
    volume: str,
    chapter_display: str,
    section_display: str,
) -> None:
    """Keep the outline placeholder skill description in sync with chapter/section."""
    skill_info = db.session.get(SkillInfo, skill_id)
    if skill_info is not None:
        description = (
            f"{volume} {chapter_display} {section_display} outline placeholder"
        ).strip()
        skill_info.description = description


def _apply_catalog_to_db(
    *,
    curriculum: str,
    volume: str,
    grade: int,
    chapters: list[CatalogChapter],
    dry_run: bool = True,
    commit: bool = False,
) -> CatalogImportReport:
    """Create, reuse, or update outline rows from a whole-book catalog."""
    report = CatalogImportReport()
    chapters_with_created_section: set[int] = set()
    chapters_with_updated_chapter_title: set[int] = set()

    # ── Phase 0: chapter alias rename ──────────────────────────────────────
    # Before touching individual sections, rename any existing chapter aliases
    # so that the section-level lookup finds rows under the authoritative name.
    # This turns "第1章" → "第1章 三角函數" in-place (all matching rows),
    # without touching skill_id, section, or any other relation.
    for ch in chapters:
        chapter_display = _canonical_chapter_display(ch.chapter_index, ch.chapter_title)
        alias_rows = _find_existing_rows_by_chapter_index(
            curriculum=curriculum, volume=volume, grade=grade, chapter_index=ch.chapter_index
        )
        rows_needing_rename = [
            r for r in alias_rows
            if _normalize_space(r.chapter or "") != chapter_display
        ]
        if rows_needing_rename:
            if not dry_run:
                for r in rows_needing_rename:
                    r.chapter = chapter_display
                db.session.flush()
            # Count as updated chapter (once per chapter_index)
            chapters_with_updated_chapter_title.add(ch.chapter_index)
    # ───────────────────────────────────────────────────────────────────────

    for ch in chapters:
        chapter_title = ch.chapter_title
        chapter_display = _canonical_chapter_display(ch.chapter_index, chapter_title)

        for sec in ch.sections:
            section_display = _canonical_section_display(sec.section_code, sec.section_title)
            skill_id, canonical_code, canonical_section = build_outline_skill_id_for_section(
                curriculum=curriculum,
                volume=volume,
                section_code=sec.section_code,
                section=section_display,
            )
            if not skill_id or not canonical_code or not canonical_section:
                report.errors.append(
                    f"chapter {ch.chapter_index} section {sec.section_code} canonicalization failed"
                )
                report.ok = False
                continue

            display_order = outline_display_order_from_section_code(canonical_code)

            existing_by_sid = _find_existing_row_by_skill_id(
                curriculum=curriculum,
                volume=volume,
                grade=grade,
                skill_id=skill_id,
            )

            if existing_by_sid is not None:
                existing_section = _normalize_space(existing_by_sid.section or "")
                if existing_section != canonical_section:
                    # skill_id collision or title drift: treat as conflict.
                    report.conflicts.append(
                        {
                            "chapter_index": ch.chapter_index,
                            "section_code": canonical_code,
                            "incoming_section": section_display,
                            "incoming_chapter": chapter_display,
                            "existing_sections": [
                                {
                                    "skill_id": existing_by_sid.skill_id,
                                    "chapter": existing_by_sid.chapter,
                                    "section": existing_by_sid.section,
                                }
                            ],
                        }
                    )
                    report.ok = False
                    continue

                existing_chapter = _normalize_space(existing_by_sid.chapter or "")
                if existing_chapter != chapter_display:
                    if not dry_run:
                        existing_by_sid.chapter = chapter_display
                        existing_by_sid.display_order = display_order
                        _update_skill_info_description(
                            skill_id, volume, chapter_display, canonical_section
                        )
                        db.session.flush()
                    report.sections_updated += 1
                    chapters_with_updated_chapter_title.add(ch.chapter_index)
                else:
                    report.sections_reused += 1
                continue

            # No exact skill_id match: look for rows with the same section code.
            same_code_rows = _find_existing_rows_by_section_code(
                curriculum=curriculum,
                volume=volume,
                grade=grade,
                section_code=canonical_code,
            )
            matching_rows = [
                r
                for r in same_code_rows
                if _normalize_space(r.section or "") == canonical_section
            ]

            if matching_rows:
                if len(matching_rows) > 1:
                    # Ambiguous: multiple rows share the same section code + title.
                    report.conflicts.append(
                        {
                            "chapter_index": ch.chapter_index,
                            "section_code": canonical_code,
                            "incoming_section": section_display,
                            "incoming_chapter": chapter_display,
                            "existing_sections": [
                                {
                                    "skill_id": row.skill_id,
                                    "chapter": row.chapter,
                                    "section": row.section,
                                }
                                for row in same_code_rows
                            ],
                        }
                    )
                    report.ok = False
                    continue

                existing = matching_rows[0]
                existing_chapter = _normalize_space(existing.chapter or "")
                if existing_chapter != chapter_display:
                    if not dry_run:
                        existing.chapter = chapter_display
                        existing.display_order = display_order
                        _update_skill_info_description(
                            existing.skill_id, volume, chapter_display, canonical_section
                        )
                        db.session.flush()
                    report.sections_updated += 1
                    chapters_with_updated_chapter_title.add(ch.chapter_index)
                else:
                    report.sections_reused += 1
                continue

            if same_code_rows:
                # Same section code but different title -> conflict.
                report.conflicts.append(
                    {
                        "chapter_index": ch.chapter_index,
                        "section_code": canonical_code,
                        "incoming_section": section_display,
                        "incoming_chapter": chapter_display,
                        "existing_sections": [
                            {
                                "skill_id": row.skill_id,
                                "chapter": row.chapter,
                                "section": row.section,
                            }
                            for row in same_code_rows
                        ],
                    }
                )
                report.ok = False
                continue

            # No existing row => create.
            if not dry_run:
                _ensure_outline_skill_info_v2(
                    skill_id=skill_id,
                    section_title=canonical_section,
                    chapter_title=chapter_display,
                    curriculum=curriculum,
                    volume=volume,
                    grade=grade,
                )
                row = SkillCurriculum(
                    skill_id=skill_id,
                    curriculum=curriculum,
                    grade=grade,
                    volume=volume,
                    chapter=chapter_display,
                    section=canonical_section,
                    paragraph=None,
                    display_order=display_order,
                    difficulty_level=1,
                )
                db.session.add(row)
                db.session.flush()
                chapters_with_created_section.add(ch.chapter_index)
            report.sections_created += 1
            chapters_with_created_section.add(ch.chapter_index)

    report.chapters_created = len(chapters_with_created_section)
    report.chapters_updated = len(chapters_with_updated_chapter_title)

    if not report.ok:
        # Conflicts were recorded; if not dry_run, rollback to avoid partial writes.
        if not dry_run and not commit:
            db.session.rollback()
        return report

    if not dry_run and commit:
        db.session.commit()

    return report


def import_catalog_from_pdf_v3(
    pdf_path: str | Path,
    *,
    curriculum: str = "vocational",
    volume: str = "數學B2",
    grade: int | None = None,
    dry_run: bool = True,
    commit: bool = False,
    max_pages: int = 10,
) -> dict[str, Any]:
    """End-to-end catalog import from a PDF-only catalog file.

    Detects TOC pages, renders them to images, calls a vision model, validates the
    JSON response, and applies the resulting outline to the existing SkillInfo +
    SkillCurriculum tables.

    Returns a report dict with created/reused/updated/conflict counts.
    """
    from core.ai_analyzer import get_model

    curriculum = _normalize_space(curriculum) or "vocational"
    volume = _normalize_space(volume)
    if not volume:
        raise V3CatalogError("missing_volume", "volume is required")
    resolved_grade = _resolve_grade(volume, grade)

    page_numbers = _detect_catalog_pages(pdf_path, max_pages=max_pages)
    if not page_numbers:
        raise V3CatalogError("no_catalog_pages", "No catalog pages detected in PDF")

    _logger.info("[catalog_v3] detected candidate TOC pages: %s", page_numbers)

    image_paths = _render_pages_to_images(pdf_path, page_numbers)
    try:
        model = get_model("vision")
        prompt = _build_catalog_extraction_prompt(page_numbers, volume)
        raw = _call_gemini_catalog_vision(model, prompt, image_paths)
    finally:
        # _call_gemini_catalog_vision already cleans up image_paths; this is a safety net.
        for p in image_paths:
            try:
                if os.path.exists(p):
                    os.unlink(p)
            except Exception:
                pass

    payload = _parse_catalog_json(raw)
    errors = validate_catalog_payload(payload)
    if errors:
        raise V3CatalogError(
            "invalid_catalog_payload",
            "Catalog AI output failed deterministic validation",
            {"errors": errors, "payload_preview": json.dumps(payload, ensure_ascii=False)[:500]},
        )

    chapters = _parse_catalog(payload)
    report = _apply_catalog_to_db(
        curriculum=curriculum,
        volume=volume,
        grade=resolved_grade,
        chapters=chapters,
        dry_run=dry_run,
        commit=commit,
    )
    chapters_serialized = _chapters_to_list(chapters)
    result: dict[str, Any] = {
        **report.to_dict(),
        "curriculum": curriculum,
        "volume": volume,
        "grade": resolved_grade,
        "pages_rendered": len(page_numbers),
        "page_numbers": page_numbers,
        "dry_run": dry_run,
        "preview_chapters": chapters_serialized,
    }
    if dry_run:
        token_payload = {
            "curriculum": curriculum,
            "volume": volume,
            "grade": resolved_grade,
            "chapters": chapters_serialized,
        }
        result["preview_token"] = encode_preview_token(token_payload)
    return result


# ---------------------------------------------------------------------------
# V2-text bridge: reuse V2 PDF text extraction + Gemini text model,
# then feed the normalised chapters/sections into _apply_catalog_to_db.
# ---------------------------------------------------------------------------

def import_catalog_from_pdf_v2_text(
    pdf_path: str | Path,
    *,
    curriculum: str = "vocational",
    volume: str = "數學B2",
    grade: int | None = None,
    dry_run: bool = True,
    commit: bool = False,
    max_pages: int = 5,
) -> dict[str, Any]:
    """Import a whole-book catalog using the V2 PDF text-extraction pipeline.

    Steps:
    1. Extract text from the first *max_pages* pages with extract_pdf_directory_text_v2.
    2. Call Gemini (text model) via _call_gemini_pdf_outline / _normalize_parsed_pdf_outline_payload.
    3. Convert the normalised V2 payload into V3 CatalogChapter / CatalogSection dataclasses.
    4. Apply to DB via _apply_catalog_to_db (same reuse/conflict logic as vision mode).

    Returns the same dict shape as import_catalog_from_pdf_v3.
    """
    from core.textbook_processor_v2 import (
        extract_pdf_directory_text_v2,
        _call_gemini_pdf_outline,
        _normalize_parsed_pdf_outline_payload,
    )
    import re as _re

    pdf_path = Path(pdf_path)
    curriculum = _normalize_space(curriculum) or "vocational"
    volume = _normalize_space(volume)
    if not volume:
        raise V3CatalogError("missing_volume", "volume is required")

    resolved_grade = _resolve_grade(volume, grade)

    # curriculum_info dict expected by V2 helpers
    curriculum_info: dict[str, Any] = {
        "curriculum": curriculum,
        "volume": volume,
        "grade": resolved_grade,
    }

    # Step 1: extract PDF text (V2)
    pdf_text, pages_read = extract_pdf_directory_text_v2(
        str(pdf_path), max_pages=max_pages
    )
    if not pdf_text.strip():
        raise V3CatalogError("empty_pdf_text", "PDF 前幾頁無法提取任何文字。")

    # Step 2: AI parse via V2 Gemini text model (queue=None for non-background use)
    normalised = _call_gemini_pdf_outline(pdf_text, curriculum_info, queue=None)
    # normalised already passed through _normalize_parsed_pdf_outline_payload inside
    # _call_gemini_pdf_outline, so chapters have canonical chapter_title / section strings.

    # Step 3: convert V2 payload to V3 dataclasses
    # V2 chapter_title comes from _canonical_outline_chapter_title, e.g. "1 三角函數"
    # V2 section: {"section_code": "1-1", "section_title": "1-1 銳角三角函數"}
    _chapter_re = _re.compile(r"^(\d+)\s*(.*)$")
    catalog_chapters: list[CatalogChapter] = []
    for ch_idx, ch_data in enumerate(normalised.get("chapters") or [], start=1):
        chapter_title_raw = str(ch_data.get("chapter_title") or "").strip()
        m = _chapter_re.match(chapter_title_raw)
        if m:
            chapter_index = int(m.group(1))
            chapter_title = m.group(2).strip() or chapter_title_raw
        else:
            chapter_index = ch_idx
            chapter_title = chapter_title_raw

        sections: list[CatalogSection] = []
        for sec_idx, sec_data in enumerate(ch_data.get("sections") or [], start=1):
            code = str(sec_data.get("section_code") or "").strip()
            title_raw = str(sec_data.get("section_title") or "").strip()
            # Strip leading "1-1 " prefix from section_title if present
            title = _re.sub(r"^\d+-\d+\s*", "", title_raw).strip() or title_raw
            if not code:
                continue
            sections.append(
                CatalogSection(
                    section_code=code,
                    section_index=sec_idx,
                    section_title=title,
                )
            )
        if sections:
            catalog_chapters.append(
                CatalogChapter(
                    chapter_index=chapter_index,
                    chapter_title=chapter_title,
                    sections=sections,
                )
            )

    if not catalog_chapters:
        raise V3CatalogError("no_chapters_parsed", "AI 未解析出任何章節，請確認 PDF 目錄格式。")

    # Step 4: apply to DB (V3 persistence)
    report = _apply_catalog_to_db(
        curriculum=curriculum,
        volume=volume,
        grade=resolved_grade,
        chapters=catalog_chapters,
        dry_run=dry_run,
        commit=commit,
    )

    chapters_serialized = _chapters_to_list(catalog_chapters)
    result: dict[str, Any] = {
        **report.to_dict(),
        "curriculum": curriculum,
        "volume": volume,
        "grade": resolved_grade,
        "pages_read": pages_read,
        "dry_run": dry_run,
        "parse_mode": "v2_text",
        "preview_chapters": chapters_serialized,
    }
    if dry_run:
        token_payload = {
            "curriculum": curriculum,
            "volume": volume,
            "grade": resolved_grade,
            "chapters": chapters_serialized,
        }
        result["preview_token"] = encode_preview_token(token_payload)
    return result
