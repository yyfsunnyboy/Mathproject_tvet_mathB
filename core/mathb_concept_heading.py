# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import unicodedata
from typing import Any, Callable

LogFn = Callable[[str], None]
_log_fn: LogFn | None = None

SCOPE_SECTION_TEXTBOOK = "section_textbook"

_NUMBERED_HEADING_RE = re.compile(
    r"^\s*([0-9０-９]+\s*[-－–—]\s*[0-9０-９]+\s*\.\s*[0-9０-９]+)\s*(\S.+?)\s*$"
)
_CANONICAL_CODE_RE = re.compile(r"^(\d+)-(\d+)\.(\d+)$")
_GENERIC_LABELS = {
    "公式",
    "說明",
    "延伸",
    "註",
    "key",
    "題目",
    "基礎題",
    "進階題",
    "隨堂練習",
    "輸入訊息",
}
_SENTENCE_HINTS = (
    "這就是",
    "上述討論",
    "接著我們",
    "綜合以上",
    "一般來說",
    "利用",
    "可得",
    "所以",
    "因此",
    "故",
    "已知",
    "設",
    "試求",
    "求",
    "若",
)
_MATH_FORMULA_RE = re.compile(
    r"(=|×|\+|\\frac|\\left|\\right|f\(x\)|g\(x\)|\{|\}|\^|→|<-|<=|>=|∴|∵)"
)

# Section identity: ``4-2`` / ``4-2 圓與直線的關係`` / ``4-2圓與直線的關係``.
# Negative lookahead excludes concept headings like ``4-2.1 …``.
_SECTION_IDENTITY_RE = re.compile(
    r"^\s*(?P<section_code>[0-9０-９]+\s*[-－–—]\s*[0-9０-９]+)(?!\s*\.\s*[0-9０-９])\s*"
    r"(?P<title>\S.+?)\s*$"
)

# Exercise / assessment block titles must never become section identity.
# Align with processor outline-skip tokens and explicit user exclusions.
_EXERCISE_BLOCK_SECTION_TITLES = frozenset(
    {
        "習題",
        "基礎題",
        "進階題",
        "練習題",
        "自我評量",
        "挑戰題",
        "章末評量",
        "總複習",
        "隨堂練習",
        "題組",
        "統測題組",
    }
)


def set_concept_heading_log_fn(fn: LogFn | None) -> None:
    global _log_fn
    _log_fn = fn


def _log(msg: str) -> None:
    if _log_fn:
        _log_fn(msg)


def _normalize_line(text: str) -> str:
    t = unicodedata.normalize("NFKC", str(text or ""))
    t = re.sub(r"[\t\u00a0\u3000]+", " ", t)
    return re.sub(r" +", " ", t).strip()


def _to_ascii_digits(text: str) -> str:
    return str(text or "").translate(str.maketrans("０１２３４５６７８９", "0123456789"))


def canonical_concept_code_from_parts(ch: str, sec: str, sub: str) -> str:
    return f"{int(ch)}-{int(sec)}.{int(sub)}"


def section_code_from_concept_code(concept_code: str) -> str:
    cc = _normalize_line(concept_code)
    m = re.match(r"^(\d+-\d+)\.", cc)
    return m.group(1) if m else ""


def pseudo_concept_code(section_code: str, concept_name: str) -> str:
    sec = _normalize_line(section_code)
    name = str(concept_name or "").strip()
    if not sec or not name:
        return ""
    return f"{sec}::{name}"


def is_persistable_concept_code(concept_code: str) -> bool:
    code = _normalize_line(concept_code)
    return bool(_CANONICAL_CODE_RE.fullmatch(code))


def normalize_section_title(title: str) -> str:
    """Collapse whitespace / NFKC for section-title identity comparison."""
    return _normalize_line(title)


def canonical_section_code(section_code: str) -> str:
    """Normalize ``4-2`` / fullwidth digits / dash variants to ``ch-sec``."""
    raw = _to_ascii_digits(_normalize_line(section_code))
    raw = raw.replace("－", "-").replace("–", "-").replace("—", "-")
    raw = re.sub(r"\s+", "", raw)
    m = re.fullmatch(r"(\d+)-(\d+)", raw)
    if not m:
        return ""
    return f"{int(m.group(1))}-{int(m.group(2))}"


def is_exercise_block_section_title(title: str) -> bool:
    """True when the title is an exercise/assessment block, not a curriculum section."""
    t = normalize_section_title(title)
    if not t:
        return False
    if t in _EXERCISE_BLOCK_SECTION_TITLES:
        return True
    # ``習題基礎題`` / ``1-1習題`` style leftovers after code strip.
    return any(t == tok or t.startswith(tok) for tok in _EXERCISE_BLOCK_SECTION_TITLES)


def parse_mathb_section_heading(
    line: str,
    *,
    expected_section_code: str = "",
) -> dict[str, Any] | None:
    """Parse a textbook section identity heading (not concept / not 習題).

    Accepts optional whitespace after the section code:
    ``4-2 圓與直線的關係``, ``4-2圓與直線的關係``, ``4-2  圓與直線的關係``.

    Rejects concept headings (``4-2.1 …``) and exercise-block titles
    (``4-2 習題``, ``4-2 基礎題``, …).
    """
    raw = str(line or "")
    norm = _normalize_line(raw)
    if not norm:
        return None
    m = _SECTION_IDENTITY_RE.match(norm)
    if not m:
        return None
    section_code = canonical_section_code(m.group("section_code"))
    title = normalize_section_title(m.group("title"))
    if not section_code or not title:
        return None
    if is_exercise_block_section_title(title):
        return None
    expected = canonical_section_code(expected_section_code) if expected_section_code else ""
    if expected and section_code != expected:
        return None
    return {
        "is_section_heading": True,
        "section_code": section_code,
        "section_title": title,
        "source_heading_text": raw.strip(),
        "normalized_identity": f"{section_code}{title}",
    }


def section_identities_match(
    detected: str | dict[str, Any] | None,
    authoritative: str | dict[str, Any] | None,
    *,
    expected_section_code: str = "",
) -> bool:
    """Compare section identity by parsed code + normalized title (not raw strings)."""

    def _as_parts(value: str | dict[str, Any] | None) -> dict[str, str] | None:
        if value is None:
            return None
        if isinstance(value, dict):
            code = canonical_section_code(
                str(value.get("section_code") or "")
            ) or canonical_section_code(
                str(value.get("source_heading_text") or value.get("section") or "")
            )
            title = normalize_section_title(
                str(value.get("section_title") or value.get("title") or "")
            )
            if not title:
                parsed = parse_mathb_section_heading(
                    str(value.get("source_heading_text") or value.get("section") or ""),
                    expected_section_code=expected_section_code,
                )
                if parsed:
                    return {
                        "section_code": parsed["section_code"],
                        "section_title": parsed["section_title"],
                    }
            if code and title and not is_exercise_block_section_title(title):
                return {"section_code": code, "section_title": title}
            return None
        return parse_mathb_section_heading(
            str(value),
            expected_section_code=expected_section_code,
        )

    left = _as_parts(detected)
    right = _as_parts(authoritative)
    if not left or not right:
        return False
    return (
        left["section_code"] == right["section_code"]
        and left["section_title"] == right["section_title"]
    )


def _reject(line: str, reason: str) -> None:
    _log(f"[CONCEPT_HEADING_REJECTED] line={line!r} reason={reason}")


def detect_mathb_concept_heading(
    line: str,
    *,
    current_section_code: str = "",
    previous_lines: list[str] | None = None,
    next_lines: list[str] | None = None,
    current_source_scope: str = SCOPE_SECTION_TEXTBOOK,
    current_concept_name: str = "",
) -> dict[str, Any] | None:
    _ = (previous_lines, next_lines, current_section_code)
    if str(current_source_scope or SCOPE_SECTION_TEXTBOOK).strip() != SCOPE_SECTION_TEXTBOOK:
        return None

    raw = str(line or "")
    norm = _normalize_line(raw)
    if not norm:
        return None

    m = _NUMBERED_HEADING_RE.match(norm)
    if not m:
        low = norm.lower().rstrip(":：")
        if low in _GENERIC_LABELS:
            _reject(raw, "generic_label")
            return None
        if any(k in norm for k in _SENTENCE_HINTS):
            _reject(raw, "sentence_like")
            return None
        if _MATH_FORMULA_RE.search(norm):
            _reject(raw, "math_formula")
            return None
        if len(norm) > 28:
            _reject(raw, "too_long")
            return None
        if current_concept_name and norm == str(current_concept_name).strip():
            _log(
                "[CONCEPT_HEADING_DUPLICATE_MERGED] "
                f"section_code={_normalize_line(current_section_code)!r} "
                f"concept_name={norm!r} source=plain_heading_same_as_current"
            )
            return {
                "is_concept_heading": True,
                "concept_code": "",
                "concept_name": norm,
                "section_code": _normalize_line(current_section_code),
                "heading_kind": "plain_heading_same_as_current",
                "duplicate_merge": True,
            }
        _reject(raw, "plain_heading_no_numbered_source")
        return None

    raw_code, name = m.groups()
    code_nfkc = _to_ascii_digits(
        _normalize_line(raw_code).replace("－", "-").replace("–", "-").replace("—", "-")
    )
    code_nfkc = re.sub(r"\s+", "", code_nfkc)
    mm = re.match(r"^(\d+)-(\d+)\.(\d+)$", code_nfkc)
    if not mm:
        _reject(raw, "plain_heading_no_numbered_source")
        return None
    concept_code = canonical_concept_code_from_parts(mm.group(1), mm.group(2), mm.group(3))
    section_code = f"{int(mm.group(1))}-{int(mm.group(2))}"
    concept_name = str(name or "").strip()
    if not concept_name:
        _reject(raw, "plain_heading_no_numbered_source")
        return None
    if _MATH_FORMULA_RE.search(concept_name):
        _reject(raw, "math_formula")
        return None
    if len(concept_name) > 40:
        _reject(raw, "too_long")
        return None
    kind = "numbered_spaced" if re.search(r"\.\d+\s+\S", norm) else "numbered_compact"
    _log(
        "[CONCEPT_HEADING_DETECTED] "
        f"kind={kind} concept_code={concept_code} section_code={section_code} concept_name={concept_name}"
    )
    return {
        "is_concept_heading": True,
        "concept_code": concept_code,
        "concept_name": concept_name,
        "section_code": section_code,
        "heading_kind": kind,
    }
