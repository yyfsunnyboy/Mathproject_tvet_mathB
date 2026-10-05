# -*- coding: utf-8 -*-
"""Cut student stems at textbook solution markers, including Word EQ badges."""

from __future__ import annotations

import re

# Word EQ overlay that draws a shape on 解: eq \o\ac(○,解) / eq \o\ac(■,解)
# The converter keeps this instruction as text, often wrapped as \( ... \).
_EQ_SOLUTION_RE = re.compile(
    r"(?:\\\()?\s*(?:eq\s*)?\\o\s*\\ac\s*\(\s*[○〇●■□]\s*,\s*解\s*\)\s*(?:\\\))?",
    re.IGNORECASE,
)
_CIRCLE_SOLUTION_RE = re.compile(r"○\s*解")
# A solution label owns the line. A stem that merely contains 解, such as 解方程式, does not.
_LABEL_SOLUTION_RE = re.compile(
    r"(?m)^\s*(?:(?:解析|詳解|解)\s*[:：]\s*|(?:解析|詳解|解)\s*$)"
)


def split_student_stem_at_solution_marker(text: str) -> tuple[str, str] | None:
    """Return (stem, solution) when a solution marker is present.

    The marker itself is removed. Text before it stays the student stem.
    Text after it is the solution region.
    """
    raw = str(text or "")
    if not raw:
        return None
    spans = [(m.start(), m.end()) for m in _EQ_SOLUTION_RE.finditer(raw)]
    spans.extend((m.start(), m.end()) for m in _CIRCLE_SOLUTION_RE.finditer(raw))
    spans.extend((m.start(), m.end()) for m in _LABEL_SOLUTION_RE.finditer(raw))
    if not spans:
        return None
    start, end = min(spans, key=lambda item: (item[0], item[0] - item[1]))
    stem = raw[:start].strip()
    solution = raw[end:].strip()
    return stem, solution


def student_stem_has_solution_residue(text: str) -> bool:
    return split_student_stem_at_solution_marker(text) is not None
