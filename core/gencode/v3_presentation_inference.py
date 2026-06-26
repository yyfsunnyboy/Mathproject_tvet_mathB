"""Infer V3 presentation_mode / answer_type from textbook_examples rows."""

from __future__ import annotations

import re
import sqlite3
from typing import Any, Mapping

CHOICE_LABEL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"[\(（]\s*([A-Ea-e])\s*[\)）]"),
    re.compile(r"(?:^|[\s\u3000])([A-Ea-e])\."),
    re.compile(r"(?:^|[\s\u3000])([A-Ea-e])："),
    re.compile(r"(?:^|[\s\u3000])([A-Ea-e])[、．]"),
)

SHORT_ANSWER_KEYWORDS: tuple[str, ...] = (
    "試求",
    "求",
    "計算",
    "化簡",
    "解",
    "寫出",
)

SHORT_ANSWER_PROBLEM_TYPES: frozenset[str] = frozenset(
    {
        "textbook_example",
        "textbook_exercise",
        "in_class_practice",
    }
)

SELF_ASSESSMENT_TYPE = "self_assessment"


def _row_to_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, Mapping):
        return dict(row)
    if hasattr(row, "keys"):
        return {key: row[key] for key in row.keys()}
    if isinstance(row, (tuple, list)):
        keys = (
            "id",
            "skill_id",
            "source_description",
            "source_section",
            "source_paragraph",
            "problem_type",
            "problem_text",
            "correct_answer",
            "difficulty_level",
            "difficulty_h",
        )
        return {keys[i]: row[i] for i in range(min(len(row), len(keys)))}
    raise TypeError(f"Unsupported textbook row type: {type(row)!r}")


def _detect_choice_labels(problem_text: str) -> set[str]:
    labels: set[str] = set()
    for pattern in CHOICE_LABEL_PATTERNS:
        for match in pattern.finditer(problem_text):
            labels.add(str(match.group(1)).upper())
    return labels


def has_abcd_choice_group(problem_text: str) -> bool:
    """Return True when A/B/C/D (or E) labels appear as a choice group, not sub-question numbers."""
    labels = _detect_choice_labels(problem_text)
    abcd = labels & {"A", "B", "C", "D", "E"}
    if len(abcd) >= 3:
        return True
    if "A" in abcd and any(label in abcd for label in ("B", "C", "D")):
        return True
    return False


_TEXTBOOK_ROW_FIELDS: tuple[str, ...] = (
    "id",
    "skill_id",
    "source_description",
    "source_section",
    "source_paragraph",
    "problem_type",
    "problem_type_id",
    "line_type",
    "problem_text",
    "correct_answer",
    "detailed_solution",
    "explanation",
    "difficulty_level",
    "difficulty_h",
)


def _available_textbook_columns(conn: Any) -> set[str]:
    cursor = conn.execute("PRAGMA table_info(textbook_examples)")
    rows = cursor.fetchall()
    names: set[str] = set()
    for row in rows:
        if isinstance(row, sqlite3.Row):
            names.add(str(row["name"]))
        else:
            names.add(str(row[1]))
    return names


def _sqlite_cursor_row_to_dict(cursor: Any, row: Any) -> dict[str, Any]:
    if row is None:
        return {}
    if isinstance(row, Mapping):
        return dict(row)
    if isinstance(row, sqlite3.Row) or hasattr(row, "keys"):
        return {key: row[key] for key in row.keys()}
    columns = [str(col[0]) for col in (getattr(cursor, "description", None) or [])]
    if columns and isinstance(row, (tuple, list)):
        return {
            columns[index]: row[index]
            for index in range(min(len(columns), len(row)))
        }
    return _row_to_dict(row)


def fetch_textbook_example_row(conn: Any, textbook_example_id: int) -> dict[str, Any] | None:
    """Load one textbook_examples row as a dict."""
    if conn is None:
        return None
    available = _available_textbook_columns(conn)
    if "id" not in available:
        return None
    selected = [field for field in _TEXTBOOK_ROW_FIELDS if field in available]
    if not selected:
        selected = ["id"]
    query = f"SELECT {', '.join(selected)} FROM textbook_examples WHERE id = ?"
    cursor = conn.execute(query, (int(textbook_example_id),))
    row = cursor.fetchone()
    if row is None:
        return None
    return _sqlite_cursor_row_to_dict(cursor, row)


def infer_presentation_mode_from_textbook_row(row: Any) -> dict[str, Any]:
    """Infer presentation contract from a textbook_examples row."""
    data = _row_to_dict(row)
    problem_text = str(data.get("problem_text") or "")
    problem_type = str(data.get("problem_type") or "").strip()
    source_description = str(data.get("source_description") or "").strip()
    correct_answer = str(data.get("correct_answer") or "").strip()

    has_choices = has_abcd_choice_group(problem_text)
    matched_patterns: list[str] = []
    if has_choices:
        matched_patterns.append("abcd_choice_group")

    has_short_answer_keyword = any(keyword in problem_text for keyword in SHORT_ANSWER_KEYWORDS)
    if has_short_answer_keyword:
        matched_patterns.append("short_answer_keyword")

    presentation_mode = "short_answer"
    answer_type = "expression"
    reason = "default_short_answer_without_choice_group"

    if has_choices:
        if problem_type == SELF_ASSESSMENT_TYPE:
            presentation_mode = "single_choice"
            answer_type = "single_choice"
            reason = "self_assessment_with_abcd_choice_group"
        else:
            presentation_mode = "single_choice"
            answer_type = "single_choice"
            reason = "problem_text_contains_abcd_choice_group"
    elif problem_type in SHORT_ANSWER_PROBLEM_TYPES:
        presentation_mode = "short_answer"
        answer_type = "expression"
        reason = f"{problem_type}_without_choice_group"
    elif has_short_answer_keyword:
        presentation_mode = "short_answer"
        answer_type = "expression"
        reason = "short_answer_keyword_without_choice_group"
    elif problem_type == SELF_ASSESSMENT_TYPE:
        presentation_mode = "short_answer"
        answer_type = "expression"
        reason = "self_assessment_without_detected_choice_group"

    # Never infer single_choice from blank correct_answer.
    if not has_choices and presentation_mode == "single_choice":
        presentation_mode = "short_answer"
        answer_type = "expression"
        reason = "forced_short_answer_no_choice_group"

    # correct_answer shape must not override textbook text signals.
    _ = correct_answer

    return {
        "presentation_mode": presentation_mode,
        "answer_type": answer_type,
        "has_choices": has_choices,
        "evidence": {
            "reason": reason,
            "matched_patterns": matched_patterns,
            "source_problem_type": problem_type,
            "source_description": source_description,
            "has_short_answer_keyword": has_short_answer_keyword,
        },
    }


def parse_abcd_choices_from_text(problem_text: str) -> list[dict[str, str]]:
    """Parse A/B/C/D choice labels and texts; ignores (1)(2) sub-question markers."""
    if not has_abcd_choice_group(problem_text):
        return []
    marker = re.compile(r"[\(（]\s*([A-Da-d])\s*[\)）]")
    matches = list(marker.finditer(str(problem_text or "")))
    choices: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        label = str(match.group(1)).strip().upper()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(problem_text)
        text = str(problem_text[start:end]).strip().rstrip("。．.,，;；")
        if not text:
            continue
        choices.append({"key": label, "label": label, "text": text})
    return choices


_STEM_TRAILING_PUNCT = re.compile(r"[：:。.．,，;；]+$")
_ABCD_FIRST_MARKER = re.compile(r"[\(（]\s*([A-Da-d])\s*[\)）]")


def question_text_has_embedded_abcd_choices(question_text: str) -> bool:
    """True when question_text contains an A–D choice group (not sub-question (1)(2))."""
    text = str(question_text or "")
    if not text.strip():
        return False
    return has_abcd_choice_group(text) and bool(_ABCD_FIRST_MARKER.search(text))


def split_question_stem_and_abcd_choices(problem_text: str) -> tuple[str, list[dict[str, str]], str]:
    """Return (stem_only, parsed_choices, source_problem_text)."""
    source = str(problem_text or "")
    if not source.strip():
        return "", [], source
    if not has_abcd_choice_group(source):
        return source.strip(), [], source
    choices = parse_abcd_choices_from_text(source)
    first = _ABCD_FIRST_MARKER.search(source)
    if not first:
        return source.strip(), choices, source
    stem = _STEM_TRAILING_PUNCT.sub("", source[: first.start()].strip())
    return stem, choices, source


def build_presentation_evidence_payload(inferred: dict[str, Any]) -> dict[str, Any]:
    """Compact evidence block for induced_spec_payload / tracker."""
    evidence = inferred.get("evidence") if isinstance(inferred.get("evidence"), dict) else {}
    return {
        "reason": str(evidence.get("reason") or ""),
        "has_choices": bool(inferred.get("has_choices")),
        "source_problem_type": str(evidence.get("source_problem_type") or ""),
        "source_description": str(evidence.get("source_description") or ""),
        "matched_patterns": list(evidence.get("matched_patterns") or []),
    }
