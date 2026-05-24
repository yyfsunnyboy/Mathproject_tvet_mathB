# -*- coding: utf-8 -*-
"""通用教材 DOCX/PDF 檔名與內容 metadata 解析（Math B B1–B4）。"""

from __future__ import annotations

import os
import re
from typing import Any

_CN_DIGIT = {
    "零": 0,
    "〇": 0,
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}

_EXT_RE = re.compile(r"\.(docx|doc|pdf)$", re.IGNORECASE)
_SUFFIX_RE = re.compile(
    r"(?:[-_]\s*)?(?:課本)?(?:[-_]\s*)?(?:Latex|LaTeX|latex)(?:[-_]\s*)?(?:課本)?$",
    re.IGNORECASE,
)
_TAIL_NOISE_RE = re.compile(r"[-_]\s*課本\s*$", re.IGNORECASE)
_CHAPTER_ZH_RE = re.compile(r"第\s*([一二三四五六七八九十百零〇\d]+)\s*章")
_CHAPTER_CH_RE = re.compile(r"CH\s*(\d+)\s*(?:章)?", re.IGNORECASE)
_CHAPTER_SA_RE = re.compile(r"CH\s*(\d+)\s*自我評量", re.IGNORECASE)
_VOLUME_HINT_RE = re.compile(r"(?:數學\s*)?B\s*([1-4])", re.IGNORECASE)
_SECTION_CODE_TITLE_RE = re.compile(
    r"(?<!\d)(\d+)-(\d+)\s+([\s\S]+?)(?=(?:[-_]\s*課本|$)|$)"
)
_SECTION_CODE_BARE_RE = re.compile(r"(?<!\d)(\d+)-(\d+)(?:\s|$|[-_])")
_SELF_ASSESSMENT_RE = re.compile(r"自我評量|章末評量")
_SECTION_HEADING_LINE_RE = re.compile(r"^\s*(\d+-\d+)\s+(.+?)\s*$")
_CH_SA_CONTENT_CHAPTER_RE = re.compile(r"第\s*(\d+)\s*章")
_CH_SA_CONTENT_MARKER_RE = re.compile(r"CH\s*(\d+)\s*自我評量", re.IGNORECASE)


def _cn_to_int(token: str) -> int | None:
    raw = str(token or "").strip()
    if not raw:
        return None
    if raw.isdigit():
        return int(raw)
    if raw == "十":
        return 10
    if raw.startswith("十") and len(raw) == 2 and raw[1] in _CN_DIGIT:
        return 10 + _CN_DIGIT[raw[1]]
    if raw.endswith("十") and len(raw) == 2 and raw[0] in _CN_DIGIT:
        return _CN_DIGIT[raw[0]] * 10
    if "十" in raw:
        left, _, right = raw.partition("十")
        tens = _CN_DIGIT.get(left, 1 if not left else None) if left else 1
        ones = _CN_DIGIT.get(right, 0 if not right else None) if right else 0
        if tens is None or ones is None:
            return None
        return tens * 10 + ones
    if len(raw) == 1 and raw in _CN_DIGIT:
        return _CN_DIGIT[raw]
    return None


def _clean_basename(filename: str) -> str:
    base = os.path.basename(str(filename or "")).strip()
    base = _EXT_RE.sub("", base).strip()
    base = _SUFFIX_RE.sub("", base).strip()
    base = _TAIL_NOISE_RE.sub("", base).strip()
    return base.strip(" -_")


def extract_volume_hint_from_filename(filename: str) -> str | None:
    """檔名中的 B1–B4 冊別提示；僅供輔助，不可覆蓋表單明確值。"""
    clean = _clean_basename(filename)
    m = _VOLUME_HINT_RE.search(clean)
    if not m:
        return None
    return f"數學B{int(m.group(1))}"


def resolve_parse_filename_for_import(
    file_path: str = "",
    curriculum_info: dict | None = None,
) -> str:
    """匯入流程統一：優先 original / parse_filename，最後才用 saved path。"""
    info = curriculum_info or {}
    return (
        str(info.get("parse_filename") or "").strip()
        or str(info.get("original_filename") or "").strip()
        or os.path.basename(str(file_path or ""))
    )


def resolve_upload_filenames(
    original_filename: str,
    saved_filename: str | None = None,
) -> dict[str, str]:
    """區分上傳原始檔名、儲存檔名、語意解析用檔名。"""
    original = str(original_filename or "").strip()
    saved = str(saved_filename or original or "").strip()
    parse_name = original or saved
    return {
        "original_filename": original,
        "saved_filename": saved,
        "parse_filename": parse_name,
    }


def _extract_chapter_index(clean_name: str, text_blob: str = "") -> tuple[int | None, str | None]:
    for pattern in (_CHAPTER_SA_RE, _CHAPTER_CH_RE, _CHAPTER_ZH_RE):
        m = pattern.search(clean_name) or pattern.search(text_blob)
        if not m:
            continue
        token = m.group(1)
        if pattern is _CHAPTER_ZH_RE:
            num = _cn_to_int(token)
        else:
            num = int(token)
        if num is None:
            continue
        label = f"第{num}章"
        return num, label
    return None, None


def _is_chapter_self_assessment_name(clean_name: str) -> bool:
    if not _SELF_ASSESSMENT_RE.search(clean_name) and not _CHAPTER_SA_RE.search(clean_name):
        return False
    sec = _SECTION_CODE_BARE_RE.search(clean_name)
    if sec:
        before = clean_name[: sec.start()]
        if _CHAPTER_ZH_RE.search(before) or _CHAPTER_CH_RE.search(before):
            tail = clean_name[sec.end() :].strip(" -_")
            if tail and not _SELF_ASSESSMENT_RE.search(tail):
                return False
        return False
    return True


def parse_textbook_filename_metadata(filename: str) -> dict[str, Any]:
    """
    解析教材檔名 metadata。
    支援小節課本、章末自我評量、B1–B4 前綴、_Latex 後綴等通用格式。
    """
    if not filename:
        return {}

    clean_name = _clean_basename(filename)
    metadata: dict[str, Any] = {
        "chapter_label": None,
        "chapter_index": None,
        "section_code": None,
        "section_index": None,
        "section_title": clean_name,
        "source_scope": "section_textbook",
        "volume_hint": extract_volume_hint_from_filename(filename),
        "parse_filename": os.path.basename(str(filename)),
    }

    chapter_index, chapter_label = _extract_chapter_index(clean_name)
    if chapter_index is not None:
        metadata["chapter_index"] = chapter_index
        metadata["chapter_label"] = chapter_label

    if _is_chapter_self_assessment_name(clean_name):
        metadata["section_code"] = None
        metadata["section_index"] = None
        metadata["section_title"] = None
        metadata["source_scope"] = "chapter_self_assessment"
        return metadata

    sec_match = _SECTION_CODE_TITLE_RE.search(clean_name)
    if sec_match:
        ch_part, sec_part, title_tail = sec_match.groups()
        metadata["section_code"] = f"{ch_part}-{sec_part}"
        metadata["section_index"] = int(sec_part)
        title_tail = re.sub(r"^[_-]+", "", str(title_tail or "")).strip()
        metadata["section_title"] = (
            f"{metadata['section_code']} {title_tail}".strip()
            if title_tail
            else metadata["section_code"]
        )
        if metadata["chapter_index"] is None:
            metadata["chapter_index"] = int(ch_part)
            metadata["chapter_label"] = f"第{metadata['chapter_index']}章"
        metadata["source_scope"] = "section_textbook"
        return metadata

    bare = _SECTION_CODE_BARE_RE.search(clean_name)
    if bare:
        ch_part, sec_part = bare.groups()
        metadata["section_code"] = f"{ch_part}-{sec_part}"
        metadata["section_index"] = int(sec_part)
        tail = clean_name[bare.end() :].strip(" -_")
        metadata["section_title"] = (
            f"{metadata['section_code']} {tail}".strip() if tail else metadata["section_code"]
        )
        if metadata["chapter_index"] is None:
            metadata["chapter_index"] = int(ch_part)
            metadata["chapter_label"] = f"第{metadata['chapter_index']}章"
        metadata["source_scope"] = "section_textbook"

    return metadata


def detect_docx_source_scope_from_content(
    lines_or_blob: list[str] | str,
    curriculum_info: dict | None = None,
) -> dict[str, Any]:
    """
    從 DOCX 內容推論 source_scope（filename 解析失敗時的 fallback）。
    """
    _ = curriculum_info
    if isinstance(lines_or_blob, list):
        text = "\n".join(str(x or "") for x in lines_or_blob)
        lines = [str(x or "") for x in lines_or_blob]
    else:
        text = str(lines_or_blob or "")
        lines = text.splitlines()

    section_codes: list[str] = []
    for ln in lines:
        line = str(ln or "").strip()
        if not line or "習題" in line:
            continue
        m = _SECTION_HEADING_LINE_RE.match(line)
        if m:
            section_codes.append(str(m.group(1)))

    unique_sections = sorted(
        set(section_codes),
        key=lambda x: tuple(int(p) for p in str(x).split("-")),
    )

    has_sa_label = bool(re.search(r"(?m)^\s*自我評量\s*$", text)) or bool(
        _SELF_ASSESSMENT_RE.search(text)
    )
    has_ch_sa = bool(_CH_SA_CONTENT_MARKER_RE.search(text))
    has_chapter_line = bool(_CH_SA_CONTENT_CHAPTER_RE.search(text))

    chapter_index: int | None = None
    m_ch = _CH_SA_CONTENT_MARKER_RE.search(text)
    if m_ch:
        chapter_index = int(m_ch.group(1))
    else:
        m_zh = _CH_SA_CONTENT_CHAPTER_RE.search(text)
        if m_zh:
            chapter_index = int(m_zh.group(1))

    result: dict[str, Any] = {
        "source_scope": "section_textbook",
        "chapter_index": chapter_index,
        "section_codes": unique_sections,
        "section_code": unique_sections[0] if len(unique_sections) == 1 else None,
    }

    if has_sa_label or has_ch_sa:
        if len(unique_sections) >= 2 or has_ch_sa or (has_chapter_line and unique_sections):
            result["source_scope"] = "chapter_self_assessment"
            result["section_code"] = None
            return result

    if len(unique_sections) >= 2 and (has_sa_label or has_chapter_line):
        result["source_scope"] = "chapter_self_assessment"
        result["section_code"] = None
        return result

    if len(unique_sections) == 1:
        result["source_scope"] = "section_textbook"
        result["section_code"] = unique_sections[0]

    return result


def merge_source_scope_detection(
    filename_meta: dict[str, Any] | None,
    content_meta: dict[str, Any] | None,
) -> dict[str, Any]:
    """合併 filename 與 content 判斷；content 明確為自我評量時優先。"""
    fn = dict(filename_meta or {})
    ct = dict(content_meta or {})
    fn_scope = str(fn.get("source_scope") or "section_textbook").strip()
    ct_scope = str(ct.get("source_scope") or "").strip()

    merged = {
        "source_scope": fn_scope,
        "chapter_index": fn.get("chapter_index") if fn.get("chapter_index") is not None else ct.get("chapter_index"),
        "section_code": fn.get("section_code"),
        "section_codes": ct.get("section_codes") or [],
    }

    if ct_scope == "chapter_self_assessment" and (
        _SELF_ASSESSMENT_RE.search(str(fn.get("parse_filename") or ""))
        or ct.get("section_codes")
        or ct.get("chapter_index") is not None
        or fn_scope in ("chapter_self_assessment", "chapter_review")
        or not fn.get("section_code")
    ):
        if fn_scope != "chapter_self_assessment":
            merged["override_reason"] = "content_self_assessment_detected"
        merged["source_scope"] = "chapter_self_assessment"
        merged["section_code"] = None
        return merged

    if fn_scope == "section_textbook" and fn.get("section_code") and ct_scope == "section_textbook":
        merged["source_scope"] = "section_textbook"
        if not merged.get("section_code"):
            merged["section_code"] = ct.get("section_code")
        return merged

    if fn_scope in ("chapter_self_assessment", "chapter_review"):
        merged["source_scope"] = "chapter_self_assessment"
        merged["section_code"] = None

    return merged
