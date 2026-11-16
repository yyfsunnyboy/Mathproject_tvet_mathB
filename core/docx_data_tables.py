# -*- coding: utf-8 -*-
"""DOCX data tables -> LaTeX ``array`` (the table form already used by imported textbook stems).

A Word table is only a *data table* when it carries a rectangular grid of short cells.  Everything else is
layout: the 1x1 table that frames an example / practice, picture strips, merged-cell designs.  A layout table is
never turned into a table; a table-like grid that ``array`` cannot express faithfully (merged cells, nested
tables, pictures) is reported as not representable instead of being forced into wrong LaTeX.

Pure XML helpers: no Flask, no database, no file writes.  Paragraph text is supplied by the caller so the
caller's faithful converter (MathType -> LaTeX, symbols, scripts) is the single text source.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any, Callable

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

MAX_CELL_CHARS = 40  # a data cell is a label or a number, not a sentence

_NUMERIC_CELL_RE = re.compile(r"^[-+\u2212]?\d+(?:[.,]\d+)?\s*%?$")
_VARIABLE_CELL_RE = re.compile(r"^[A-Za-z](?:_\{?\w+\}?)?$")
_MATH_SPAN_RE = re.compile(r"\\\((.*?)\\\)", re.S)
_TEXT_ESCAPES = {"%": r"\%", "&": r"\&", "#": r"\#", "$": r"\$", "_": r"\_", "{": r"\{", "}": r"\}"}


def is_layout_container(tbl) -> bool:
    """The 1x1 table that frames one example / practice (never data)."""
    rows = tbl.findall(W + "tr")
    return len(rows) == 1 and len(rows[0].findall(W + "tc")) == 1


def _pictures(el) -> int:
    return len(list(el.iter(W + "drawing"))) + len([p for p in el.iter(W + "pict")])


def analyze_table(tbl, paragraph_text: Callable[[Any], str]) -> dict[str, Any]:
    """Classify one ``w:tbl`` element.

    Returns ``{"kind": "layout"|"data"|"unrepresentable", "rows": [[cell text]], "reason": str}``.  ``rows``
    is filled for ``data`` and ``unrepresentable``; ``paragraph_text(w:p)`` supplies cell paragraph text.
    """
    trs = tbl.findall(W + "tr")
    if not trs or is_layout_container(tbl):
        return {"kind": "layout", "rows": [], "reason": "frame_or_empty"}
    counts = [len(tr.findall(W + "tc")) for tr in trs]
    pics = _pictures(tbl)
    merged = len(list(tbl.iter(W + "gridSpan"))) + len(list(tbl.iter(W + "vMerge")))
    nested = sum(1 for tc in tbl.iter(W + "tc") for ch in tc if ch.tag == W + "tbl")

    def cell_text(tc) -> str:
        parts = [paragraph_text(p).strip() for p in tc.iter(W + "p") if p.getparent() is tc]
        return " ".join(x for x in parts if x).strip()

    rows = [[cell_text(tc) for tc in tr.findall(W + "tc")] for tr in trs]
    if len(trs) < 2 or max(counts) < 2:
        return {"kind": "layout", "rows": [], "reason": "not_a_grid"}
    if pics:
        # Picture strips (graph pairs, labelled figures) are figures, not data.
        return {"kind": "layout", "rows": [], "reason": "contains_pictures"}
    if len(set(counts)) != 1 or merged or nested:
        reason = "merged_cells" if merged else "nested_table" if nested else "ragged_rows"
        return {"kind": "unrepresentable", "rows": rows, "reason": reason}
    if max((len(c) for r in rows for c in r), default=0) > MAX_CELL_CHARS:
        return {"kind": "layout", "rows": [], "reason": "long_text_cells"}
    if not any(c for r in rows for c in r):
        return {"kind": "layout", "rows": [], "reason": "empty"}
    return {"kind": "data", "rows": rows, "reason": ""}


def _escape_text(text: str) -> str:
    return "".join(_TEXT_ESCAPES.get(ch, ch) for ch in text)


def cell_to_latex(text: str) -> str:
    """One cell: numbers and single variables stay math, words go through ``\\text``, formulas keep their LaTeX."""
    value = str(text or "").strip()
    if not value:
        return ""
    plain = re.sub(r"\s+", "", value)
    if _NUMERIC_CELL_RE.match(plain):
        return plain.replace("\u2212", "-").replace("%", r"\%")
    if _VARIABLE_CELL_RE.match(plain):
        return plain
    out: list[str] = []
    pos = 0
    for m in _MATH_SPAN_RE.finditer(value):
        if value[pos:m.start()].strip():
            out.append(r"\text{%s}" % _escape_text(value[pos:m.start()].strip()))
        out.append(m.group(1).strip())
        pos = m.end()
    if value[pos:].strip():
        out.append(r"\text{%s}" % _escape_text(value[pos:].strip()))
    return " ".join(out)


def grid_to_latex(rows: list[list[str]]) -> str:
    """Same shape as the hand-repaired stems: ``\\(\\begin{array}{|c|c|}\\hline a & b \\\\ \\hline … \\end{array}\\)``."""
    ncols = len(rows[0])
    body = " \\\\ \\hline ".join(" & ".join(cell_to_latex(c) for c in row) for row in rows)
    return "\\(\\begin{array}{" + "|c" * ncols + "|}\\hline " + body + " \\\\ \\hline \\end{array}\\)"


def _norm_cell(value: str) -> str:
    s = str(value or "")
    s = re.sub(r"\\text\s*\{", "", s)
    s = s.replace("\\%", "%").replace("\\(", "").replace("\\)", "").replace("\\ ", "").replace("\u2212", "-")
    return re.sub(r"[\s{}]", "", s)


def grid_fingerprint(rows: list[list[str]]) -> str:
    cells = [[_norm_cell(c) for c in row] for row in rows]
    return hashlib.sha256(repr(cells).encode("utf-8")).hexdigest()[:20]


_ARRAY_RE = re.compile(r"\\begin\{array\}\{[^}]*\}(.*?)\\end\{array\}", re.S)


def array_fingerprints(text: str) -> list[str]:
    """Fingerprints of every ``array`` found in imported text, comparable to :func:`grid_fingerprint`."""
    found = []
    for m in _ARRAY_RE.finditer(str(text or "")):
        body = m.group(1).replace("\\hline", "")
        rows = [r for r in re.split(r"\\\\", body) if r.strip()]
        grid = [[c for c in re.split(r"(?<!\\)&", r)] for r in rows]
        found.append(grid_fingerprint(grid))
    return found


def expected_stem_tables(evidence: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Data tables the student-facing stem must retain (DOCX evidence, not keywords)."""
    return [
        t for t in ((evidence or {}).get("tables") or [])
        if isinstance(t, dict) and t.get("expected") and t.get("location") == "stem"
    ]


def expected_stem_pictures(evidence: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Pictures the student-facing stem must retain (DOCX evidence, not the bare character 圖)."""
    return [
        p for p in ((evidence or {}).get("pictures") or [])
        if isinstance(p, dict) and p.get("expected") and p.get("location") == "stem"
    ]


def stem_retains_table(problem_text: str, table: dict[str, Any]) -> bool:
    """True when ``problem_text`` contains an ``array`` whose cells match ``table['fingerprint']``."""
    fp = str(table.get("fingerprint") or "")
    return bool(fp) and fp in array_fingerprints(problem_text)
