# -*- coding: utf-8 -*-
"""Chapter 4 questions that can only be answered with a calculator may be skipped.

The formal skill ``vh_數學B3_SubSection_4_5_2`` stays in the curriculum even when
every question under it is skipped. A source question count of 0 is legal.
"""

from __future__ import annotations

import re
from typing import Any

SKIP_REASON = "calculator_required"
CALCULATOR_KEY_SKILL_ID = "vh_數學B3_SubSection_4_5_2"

_SPACE_RE = re.compile(r"\s+")
_BAN_RE = re.compile(r"不[可要得]使用計算機|不必使用計算機|無需使用計算機|不准使用計算機")
_REQUIRED_RES = (
    re.compile(r"在計算機上輸入"),
    re.compile(r"計算機會顯示"),
    re.compile(r"按[^。\n]{0,16}(?:log|LOG|對數)[^。\n]{0,8}鍵"),
    re.compile(r"(?:log|LOG|對數)鍵"),
    re.compile(r"(?:使用|利用|用|以)計算機"),
    re.compile(r"計算機求"),
)
_OPTIONAL_RE = re.compile(
    r"(?:也可以|亦可|可|可用|可利用|請自行|自行).{0,8}計算機|計算機.{0,6}驗證|驗證.{0,12}計算機"
)
_TABLE_RE = re.compile(r"對數表|查表")
_PROPERTY_RE = re.compile(r"換底|對數的性質|對數性質")
_KEY_PROCEDURE_RE = re.compile(
    r"在計算機上輸入|按[^。\n]{0,16}(?:log|LOG|對數)[^。\n]{0,8}鍵|(?:log|LOG|對數)鍵"
)
_TABLE_UNAVAILABLE_RE = re.compile(r"無法查表|不能查表|不可查表")


def is_b3_chapter4(curriculum_info: dict | None) -> bool:
    """Vocational 數學B 第四章, including its self-assessment file."""
    info = curriculum_info or {}
    if str(info.get("curriculum") or "").strip() != "vocational":
        return False
    volume = str(info.get("volume") or "")
    if "B3" not in volume:
        return False
    filename_meta = info.get("filename_meta") if isinstance(info.get("filename_meta"), dict) else {}
    if _chapter_index(info.get("chapter_index")) == 4 or _chapter_index(filename_meta.get("chapter_index")) == 4:
        return True
    section_code = str(info.get("section_code") or filename_meta.get("section_code") or "").strip()
    if section_code == "4" or section_code.startswith("4-"):
        return True
    chapter = "".join(
        str(info.get(key) or "")
        for key in ("chapter", "chapter_label", "chapter_title")
    )
    return "第四章" in chapter or "第4章" in chapter


def question_requires_calculator(problem_text: str) -> bool:
    """True when the stem cannot be finished by textbook hand methods."""
    text = _SPACE_RE.sub("", str(problem_text or ""))
    text = _BAN_RE.sub("", text)
    if not text or not _has_calculator_method(text):
        return False
    if not _has_calculator_method(_OPTIONAL_RE.sub("", text)):
        return False
    return not _hand_method_is_sufficient(text)


def chapter4_calculator_skip(
    curriculum_info: dict | None,
    problem_text: str,
    source_label: str,
) -> dict[str, str] | None:
    """Audit record for a legal skip. Other chapters never match."""
    if not is_b3_chapter4(curriculum_info):
        return None
    if not question_requires_calculator(problem_text):
        return None
    return {
        "source_label": str(source_label or "").strip(),
        "skip_reason": SKIP_REASON,
    }


def keeps_formal_skill_when_source_count_is_zero(skill_id: str, source_question_count: int) -> bool:
    """4-5.2 remains a formal skill when no question is imported."""
    return str(skill_id or "") == CALCULATOR_KEY_SKILL_ID and int(source_question_count) == 0


def chapter4_corpus_acceptance(
    *,
    parsed_source_questions: int,
    imported_questions: int,
    legitimate_calculator_required_skips: int,
) -> dict[str, Any]:
    """parsed_source_questions = imported_questions + legitimate calculator skips."""
    parsed_n = int(parsed_source_questions)
    imported_n = int(imported_questions)
    skipped_n = int(legitimate_calculator_required_skips)
    return {
        "parsed_source_questions": parsed_n,
        "imported_questions": imported_n,
        "legitimate_calculator_required_skips": skipped_n,
        "calculator_required_skipped": skipped_n,
        "balanced": parsed_n == imported_n + skipped_n,
    }


def replacement_counts_match(
    *,
    inserted: int,
    updated: int,
    parsed: int,
    calculator_required_skipped: int,
) -> bool:
    """A section replace counts calculator skips as accounted questions."""
    return int(updated) == 0 and int(inserted) + int(calculator_required_skipped) == int(parsed)


def _chapter_index(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _has_calculator_method(text: str) -> bool:
    return any(pattern.search(text) for pattern in _REQUIRED_RES)


def _hand_method_is_sufficient(text: str) -> bool:
    if _TABLE_UNAVAILABLE_RE.search(text):
        return False
    if _TABLE_RE.search(text):
        return True
    return bool(_PROPERTY_RE.search(text) and not _KEY_PROCEDURE_RE.search(text))
