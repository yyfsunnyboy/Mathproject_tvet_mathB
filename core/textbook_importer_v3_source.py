# -*- coding: utf-8 -*-
"""V3 教材匯入：多組 DOCX + PDF 來源驗證、配對與分類（Phase 1）。"""

from __future__ import annotations

import os
import re
from typing import Any

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_DOCX_EXT = ".docx"
ALLOWED_PDF_EXT = ".pdf"

_SECTION_CODE_RE = re.compile(r"(?<!\d)(\d+)-(\d+)")
_CHAPTER_LABEL_RE = re.compile(r"^第([一二三四五六七八九十]+)章")
_CHAPTER_ASSESSMENT_RE = re.compile(r"^第([一二三四五六七八九十]+)章\s*自我評量")

_CHINESE_CHAPTER_MAP = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}


def get_base_name(filename: str) -> str:
    base = os.path.basename(str(filename or "").strip())
    last_dot = base.rfind(".")
    if last_dot <= 0:
        return base
    return base[:last_dot]


def _is_safe_upload_filename(filename: str) -> bool:
    raw = str(filename or "").strip()
    if not raw:
        return False
    if any(token in raw for token in ("..", "/", "\\", "\x00")):
        return False
    basename = os.path.basename(raw)
    if not basename:
        return False
    # secure_filename 會剝離非 ASCII；此處僅用於排除明顯危險字元，保留中文檔名。
    sanitized = secure_filename(basename)
    if basename != sanitized and not re.search(r"[^\x00-\x7F]", basename):
        return bool(sanitized)
    return True


def _normalized_extension(filename: str) -> str:
    return os.path.splitext(os.path.basename(str(filename or "")))[1].lower()


def parse_chinese_chapter_number(chinese_num: str) -> int | None:
    token = str(chinese_num or "").strip()
    if not token:
        return None
    if token == "十":
        return 10
    if len(token) == 1:
        return _CHINESE_CHAPTER_MAP.get(token)
    if token.startswith("十") and len(token) == 2:
        unit = _CHINESE_CHAPTER_MAP.get(token[1])
        return 10 + unit if unit is not None else 10
    if token.endswith("十") and len(token) == 2:
        tens = _CHINESE_CHAPTER_MAP.get(token[0])
        return tens * 10 if tens is not None else None
    if "十" in token:
        left, _, right = token.partition("十")
        tens = _CHINESE_CHAPTER_MAP.get(left, 1 if not left else None) if left else 1
        ones = _CHINESE_CHAPTER_MAP.get(right, 0 if not right else None) if right else 0
        if tens is None or ones is None:
            return None
        return tens * 10 + ones
    return _CHINESE_CHAPTER_MAP.get(token)


def classify_textbook_source(base_name: str) -> dict[str, Any]:
    name = str(base_name or "").strip()
    if not name:
        return {"type": "unknown", "chapter": None, "section": None}

    assessment_match = _CHAPTER_ASSESSMENT_RE.match(name)
    if assessment_match:
        return {
            "type": "chapter_assessment",
            "chapter": parse_chinese_chapter_number(assessment_match.group(1)),
            "section": None,
        }

    section_match = _SECTION_CODE_RE.search(name)
    if section_match:
        section_chapter = int(section_match.group(1))
        section_num = int(section_match.group(2))

        label_match = _CHAPTER_LABEL_RE.match(name)
        if label_match:
            label_chapter = parse_chinese_chapter_number(label_match.group(1))
            if label_chapter is not None and label_chapter != section_chapter:
                return {
                    "type": "chapter_mismatch",
                    "chapter": None,
                    "section": None,
                    "label_chapter": label_chapter,
                    "section_chapter": section_chapter,
                    "section_number": section_num,
                }

        return {
            "type": "section",
            "chapter": section_chapter,
            "section": section_num,
        }

    return {"type": "unknown", "chapter": None, "section": None}


def _pair_sort_key(pair: dict[str, Any]) -> tuple:
    classification = pair.get("classification") or {}
    pair_type = classification.get("type")
    if pair_type == "section":
        return (0, int(classification.get("chapter") or 0), int(classification.get("section") or 0), pair["base_name"])
    if pair_type == "chapter_assessment":
        return (1, int(classification.get("chapter") or 999), 0, pair["base_name"])
    if pair_type == "chapter_mismatch":
        return (2, 0, 0, pair["base_name"])
    return (3, 0, 0, pair["base_name"])


def sort_source_pairs(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(pairs, key=_pair_sort_key)


def build_file_map(
    files: list[FileStorage],
    allowed_ext: str,
) -> tuple[dict[str, FileStorage], dict[str, Any] | None]:
    """
    Build basename -> FileStorage map.

    Returns (file_map, error_payload). error_payload is None when successful.
    """
    file_map: dict[str, FileStorage] = {}
    invalid_extensions: list[str] = []
    unsafe_filenames: list[str] = []
    duplicate_basenames: list[str] = []
    seen_basenames: set[str] = set()

    for upload in files or []:
        if not upload or not upload.filename:
            continue

        original_name = str(upload.filename).strip()
        if not _is_safe_upload_filename(original_name):
            unsafe_filenames.append(original_name)
            continue

        ext = _normalized_extension(original_name)
        if ext != allowed_ext:
            invalid_extensions.append(os.path.basename(original_name))
            continue

        base_name = get_base_name(original_name)
        if not base_name:
            unsafe_filenames.append(original_name)
            continue

        if base_name in seen_basenames:
            if base_name not in duplicate_basenames:
                duplicate_basenames.append(base_name)
            continue

        seen_basenames.add(base_name)
        file_map[base_name] = upload

    if unsafe_filenames:
        return {}, {
            "ok": False,
            "error": "unsafe_filename",
            "message": "上傳檔名包含不安全字元或路徑。",
            "filenames": unsafe_filenames,
        }

    if invalid_extensions:
        error_code = "invalid_docx_extension" if allowed_ext == ALLOWED_DOCX_EXT else "invalid_pdf_extension"
        label = "DOCX" if allowed_ext == ALLOWED_DOCX_EXT else "PDF"
        return {}, {
            "ok": False,
            "error": error_code,
            "message": f"僅允許 {label} 副檔名 {allowed_ext}。",
            "filenames": invalid_extensions,
        }

    if duplicate_basenames:
        error_code = "duplicate_docx_basename" if allowed_ext == ALLOWED_DOCX_EXT else "duplicate_pdf_basename"
        return {}, {
            "ok": False,
            "error": error_code,
            "message": "偵測到重複的教材 basename。",
            "basenames": duplicate_basenames,
        }

    return file_map, None


def build_source_pairs(
    docx_map: dict[str, FileStorage],
    pdf_map: dict[str, FileStorage],
) -> list[dict[str, Any]]:
    all_basenames = set(docx_map.keys()) | set(pdf_map.keys())
    pairs: list[dict[str, Any]] = []

    for base_name in all_basenames:
        docx_file = docx_map.get(base_name)
        pdf_file = pdf_map.get(base_name)
        if docx_file and pdf_file:
            status = "ready"
        elif docx_file:
            status = "missing_pdf"
        else:
            status = "missing_docx"

        classification = classify_textbook_source(base_name)
        pairs.append(
            {
                "base_name": base_name,
                "type": classification["type"],
                "chapter": classification["chapter"],
                "section": classification["section"],
                "classification": classification,
                "docx": os.path.basename(docx_file.filename) if docx_file and docx_file.filename else None,
                "pdf": os.path.basename(pdf_file.filename) if pdf_file and pdf_file.filename else None,
                "status": status,
            }
        )

    return sort_source_pairs(pairs)


def _parse_grade(raw_grade: Any) -> int | None:
    try:
        return int(raw_grade)
    except (TypeError, ValueError):
        return None


def validate_textbook_source_batch(
    *,
    docx_files: list[FileStorage],
    pdf_files: list[FileStorage],
    curriculum: str,
    publisher: str,
    grade: Any,
    volume: str,
) -> tuple[dict[str, Any], int]:
    curriculum_val = str(curriculum or "").strip()
    publisher_val = str(publisher or "").strip()
    volume_val = str(volume or "").strip()
    grade_val = _parse_grade(grade)

    if not curriculum_val or not publisher_val or not volume_val or grade_val is None:
        return {
            "ok": False,
            "error": "missing_required_metadata",
            "message": "缺少必要的教材設定欄位（curriculum / publisher / grade / volume）。",
        }, 400

    docx_list = [f for f in (docx_files or []) if f and f.filename]
    pdf_list = [f for f in (pdf_files or []) if f and f.filename]

    if not docx_list:
        return {
            "ok": False,
            "error": "missing_docx_collection",
            "message": "至少需要上傳 1 個 DOCX 檔案。",
        }, 400

    if not pdf_list:
        return {
            "ok": False,
            "error": "missing_pdf_collection",
            "message": "至少需要上傳 1 個 PDF 檔案。",
        }, 400

    docx_map, docx_error = build_file_map(docx_list, ALLOWED_DOCX_EXT)
    if docx_error:
        return docx_error, 400

    pdf_map, pdf_error = build_file_map(pdf_list, ALLOWED_PDF_EXT)
    if pdf_error:
        return pdf_error, 400

    pairs = build_source_pairs(docx_map, pdf_map)
    missing_pdf = [p["base_name"] for p in pairs if p["status"] == "missing_pdf"]
    missing_docx = [p["base_name"] for p in pairs if p["status"] == "missing_docx"]

    if missing_pdf or missing_docx:
        return {
            "ok": False,
            "error": "source_pair_validation_failed",
            "message": "DOCX 與 PDF 教材 basename 配對不完整。",
            "missing_pdf": missing_pdf,
            "missing_docx": missing_docx,
        }, 400

    chapter_mismatches = [
        {
            "base_name": pair["base_name"],
            "label_chapter": (pair.get("classification") or {}).get("label_chapter"),
            "section_chapter": (pair.get("classification") or {}).get("section_chapter"),
            "section_number": (pair.get("classification") or {}).get("section_number"),
        }
        for pair in pairs
        if (pair.get("classification") or {}).get("type") == "chapter_mismatch"
    ]
    if chapter_mismatches:
        return {
            "ok": False,
            "error": "chapter_metadata_mismatch",
            "message": "教材檔名的章節標記與小節編號不一致。",
            "mismatches": chapter_mismatches,
        }, 400

    ready_pairs = [
        {
            "base_name": pair["base_name"],
            "type": pair["type"],
            "chapter": pair["chapter"],
            "section": pair["section"],
            "docx": pair["docx"],
            "pdf": pair["pdf"],
            "status": pair["status"],
        }
        for pair in pairs
        if pair["status"] == "ready"
    ]

    return {
        "ok": True,
        "batch": {
            "curriculum": curriculum_val,
            "publisher": publisher_val,
            "grade": grade_val,
            "volume": volume_val,
            "total_pairs": len(ready_pairs),
        },
        "pairs": ready_pairs,
    }, 200
