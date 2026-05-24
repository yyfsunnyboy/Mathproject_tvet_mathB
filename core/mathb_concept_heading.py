# -*- coding: utf-8 -*-
"""
Math B section_textbook：通用概念標題辨識（numbered / plain scoped）。
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Callable

LogFn = Callable[[str], None]
_log_fn: LogFn | None = None

SCOPE_SECTION_TEXTBOOK = "section_textbook"

_DASH_CLASS = r"[-－–—﹣]"
_NUMBERED_HEADING_RE = re.compile(
    rf"^(\d+)\s*{_DASH_CLASS}\s*(\d+)\s*\.\s*(\d+)\s*(.+)$",
    re.UNICODE,
)

_EXCLUDE_LINE_RE = re.compile(
    r"^\s*(?:"
    r"(?:例|例題)\s*\d|"
    r"隨堂練習|"
    r"\d+-\d+\s*習題|"
    r"基礎題|進階題|挑戰題|"
    r"題目|"
    r"KEY|"
    r"輸入訊息|"
    r"[▲△]?\s*圖\s*\d+|"
    r"表\s*\d+|"
    r"^\d{1,3}\s*$|"
    r"[\(（]\s*[A-DＡ-Ｄa-dａ-ｄ]\s*[\)）]"
    r")\s*",
    re.IGNORECASE | re.UNICODE,
)

_EXCLUDE_CONCEPT_NAME_RE = re.compile(
    r"^(?:例|例題|隨堂練習|習題|題目|KEY|基礎題|進階題|挑戰題|輸入訊息)$",
    re.IGNORECASE,
)

_PLAIN_PROBLEM_START_RE = re.compile(
    r"^(?:已知|試求|解下列|求|設|若|當|令|比較|化簡|展開|因式分解)",
    re.UNICODE,
)

_SOLUTION_DISCOURSE_RE = re.compile(
    r"^(?:所以|故|整理得|可得|因此|亦即)",
    re.UNICODE,
)

_STRUCTURE_EVIDENCE_RE = re.compile(
    r"(設|則|稱為|這就是|性質|公式|定理|原理|被除式|餘式|因式|定義|亦即)",
    re.UNICODE,
)

_FOLLOW_ANCHOR_RE = re.compile(
    r"^\s*(?:例|例題|隨堂練習)\s*[0-9０-９]",
    re.UNICODE,
)

_LATEX_HEAVY_RE = re.compile(r"\\(?:frac|left|right|sqrt|\[)")


def set_concept_heading_log_fn(fn: LogFn | None) -> None:
    global _log_fn
    _log_fn = fn


def _log(msg: str) -> None:
    if _log_fn:
        _log_fn(msg)


def _normalize_heading_line(line: str) -> str:
    t = unicodedata.normalize("NFKC", str(line or ""))
    t = re.sub(r"[\t\u00a0\u3000]+", " ", t)
    return re.sub(r" +", " ", t).strip()


def canonical_concept_code_from_parts(ch: str, sec: str, sub: str) -> str:
    return f"{ch}-{sec}.{sub}"


def section_code_from_concept_code(concept_code: str) -> str:
    cc = unicodedata.normalize("NFKC", str(concept_code or "").strip())
    m = re.match(r"^(\d+-\d+)(?:\.|\:\:)", cc)
    return m.group(1) if m else ""


def pseudo_concept_code(section_code: str, concept_name: str) -> str:
    sec = unicodedata.normalize("NFKC", str(section_code or "").strip())
    name = str(concept_name or "").strip()
    if not sec or not name:
        return ""
    return f"{sec}::{name}"


def is_persistable_concept_code(concept_code: str) -> bool:
    code = unicodedata.normalize("NFKC", str(concept_code or "").strip())
    if re.fullmatch(r"\d+-\d+\.\d+", code):
        return True
    return bool(re.fullmatch(r"\d+-\d+::.+", code))


def _count_cjk(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", str(text or "")))


def _is_excluded_line(line: str) -> bool:
    t = _normalize_heading_line(line)
    if not t:
        return True
    if _EXCLUDE_LINE_RE.match(t):
        return True
    if _PLAIN_PROBLEM_START_RE.match(t):
        return True
    if _SOLUTION_DISCOURSE_RE.match(t):
        return True
    if _LATEX_HEAVY_RE.search(t) and _count_cjk(t) < 4:
        return True
    if re.search(r"[=＝≠<>≤≥×÷]", t):
        return True
    if len(t) > 40 and _count_cjk(t) > 15:
        return True
    return False


def _plain_heading_has_structure_evidence(next_lines: list[str]) -> bool:
    window = "\n".join(_normalize_heading_line(x) for x in (next_lines or [])[:15])
    if not window.strip():
        return False
    if _STRUCTURE_EVIDENCE_RE.search(window):
        return True
    for nl in (next_lines or [])[:15]:
        if _FOLLOW_ANCHOR_RE.match(_normalize_heading_line(nl)):
            return True
    return False


def _detect_numbered_heading(line: str) -> dict[str, Any] | None:
    norm = _normalize_heading_line(line)
    if not norm or _is_excluded_line(norm):
        return None
    m = _NUMBERED_HEADING_RE.match(norm)
    if not m:
        return None
    ch, sec, sub, name_raw = m.groups()
    name = str(name_raw or "").strip()
    if not name or _EXCLUDE_CONCEPT_NAME_RE.match(name):
        return None
    if _is_excluded_line(name):
        return None
    concept_code = canonical_concept_code_from_parts(ch, sec, sub)
    section_code = f"{ch}-{sec}"
    spaced = bool(re.search(rf"\d\s*\.\s*\d+\s+", norm))
    kind = "numbered_spaced" if spaced else "numbered_compact"
    return {
        "is_concept_heading": True,
        "concept_code": concept_code,
        "concept_name": name,
        "section_code": section_code,
        "heading_kind": kind,
        "confidence": "high",
        "reason": kind,
    }


def _detect_plain_scoped_heading(
    line: str,
    *,
    current_section_code: str,
    next_lines: list[str],
) -> dict[str, Any] | None:
    sec = unicodedata.normalize("NFKC", str(current_section_code or "").strip())
    if not sec or not re.fullmatch(r"\d+-\d+", sec):
        return None
    norm = _normalize_heading_line(line)
    if not norm or _is_excluded_line(norm):
        return None
    if re.search(r"\d+-\d+", norm):
        return None
    if re.search(r"[=＝≠<>≤≥×÷]", norm):
        return None
    cjk = _count_cjk(norm)
    if cjk < 2 or cjk > 20:
        return None
    if len(norm) > 24:
        return None
    if not _plain_heading_has_structure_evidence(next_lines):
        return None
    name = norm
    return {
        "is_concept_heading": True,
        "concept_code": pseudo_concept_code(sec, name),
        "concept_name": name,
        "section_code": sec,
        "heading_kind": "plain_scoped",
        "confidence": "medium",
        "reason": "plain_scoped_with_structure_evidence",
    }


def detect_mathb_concept_heading(
    line: str,
    *,
    current_section_code: str = "",
    previous_lines: list[str] | None = None,
    next_lines: list[str] | None = None,
    current_source_scope: str = SCOPE_SECTION_TEXTBOOK,
    current_concept_name: str = "",
) -> dict[str, Any] | None:
    """
    通用概念標題偵測。
    回傳 dict 或 None；不針對特定課名 hardcode。
    """
    _ = previous_lines
    scope = str(current_source_scope or SCOPE_SECTION_TEXTBOOK).strip()
    if scope != SCOPE_SECTION_TEXTBOOK:
        return None

    numbered = _detect_numbered_heading(line)
    if numbered:
        _log(
            "[CONCEPT_HEADING_DETECTED] "
            f"kind={numbered['heading_kind']} section_code={numbered['section_code']!r} "
            f"concept_code={numbered['concept_code']!r} concept_name={numbered['concept_name']!r}"
        )
        return numbered

    plain = _detect_plain_scoped_heading(
        line,
        current_section_code=current_section_code,
        next_lines=list(next_lines or []),
    )
    if not plain:
        return None

    if current_concept_name and plain["concept_name"] == current_concept_name.strip():
        _log(
            "[CONCEPT_HEADING_DUPLICATE_MERGED] "
            f"section_code={plain['section_code']!r} concept_name={plain['concept_name']!r} "
            f"source=plain_after_numbered"
        )
        plain["duplicate_merge"] = True
    else:
        _log(
            "[CONCEPT_HEADING_DETECTED] "
            f"kind={plain['heading_kind']} section_code={plain['section_code']!r} "
            f"concept_code={plain['concept_code']!r} concept_name={plain['concept_name']!r}"
        )
    return plain
