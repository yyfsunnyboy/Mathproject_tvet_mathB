"""Lossless-as-possible text sanitation for Excel/XML exports.

This module deliberately repairs only corruption signatures whose intended
LaTex token is unambiguous.  It is shared by persistence and backup code so a
bad client payload cannot both poison a future export and make an existing
backup fail.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


# XML 1.0 excludes these code points.  TAB, LF, and CR are intentionally not
# included: they retain their normal textual meaning in an Excel worksheet.
XML_ILLEGAL_CONTROL_CHARS = frozenset(
    list(range(0x00, 0x09)) + [0x0B, 0x0C] + list(range(0x0E, 0x20))
)

# Evidence-backed only.  Do not add broad TAB/LF/CR replacements: they are
# normal whitespace unless their surrounding text independently proves a LaTeX
# escape was consumed by Python/JSON parsing.
_LATEX_ESCAPE_REPAIRS: tuple[tuple[str, str, str], ...] = (
    ("\x0crac{", r"\frac{", "form_feed_frac"),
)


@dataclass
class ExcelSanitizationReport:
    sanitized_cells: int = 0
    repaired_latex_cells: int = 0
    removed_or_escaped_chars: int = 0
    cells: list[dict[str, Any]] = field(default_factory=list)

    def add(self, *, table: str, row: Any, column: str, repairs: list[str], escaped: list[str]) -> None:
        self.sanitized_cells += 1
        if repairs:
            self.repaired_latex_cells += 1
        self.removed_or_escaped_chars += len(escaped)
        self.cells.append(
            {
                "table": table,
                "row": row,
                "column": column,
                "latex_repairs": repairs,
                "escaped_chars": escaped,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sanitized_cells": self.sanitized_cells,
            "repaired_latex_cells": self.repaired_latex_cells,
            "removed_or_escaped_chars": self.removed_or_escaped_chars,
            "cells": list(self.cells),
        }


def repair_known_latex_escape_corruption(value: object) -> tuple[object, list[str]]:
    """Repair only known, semantically unambiguous consumed escape tokens."""
    if not isinstance(value, str):
        return value, []
    repaired = value
    repairs: list[str] = []
    for broken, correct, label in _LATEX_ESCAPE_REPAIRS:
        if broken in repaired:
            repaired = repaired.replace(broken, correct)
            repairs.append(label)
    return repaired, repairs


def sanitize_excel_text(value: object) -> tuple[object, list[str], list[str]]:
    """Return Excel-safe text while preserving valid strings byte-for-byte.

    Remaining illegal XML controls have no recoverable meaning, so encode them
    visibly as ``\\uXXXX`` rather than deleting data or failing the workbook.
    """
    repaired, repairs = repair_known_latex_escape_corruption(value)
    if not isinstance(repaired, str):
        return repaired, repairs, []
    escaped: list[str] = []
    out: list[str] = []
    for char in repaired:
        if ord(char) in XML_ILLEGAL_CONTROL_CHARS:
            escaped.append(f"U+{ord(char):04X}")
            out.append(f"\\u{ord(char):04x}")
        else:
            out.append(char)
    return "".join(out), repairs, escaped


def sanitize_export_frames(
    frames: dict[str, pd.DataFrame],
) -> tuple[dict[str, pd.DataFrame], ExcelSanitizationReport]:
    """Copy export frames and sanitize only string cells for openpyxl/XML."""
    report = ExcelSanitizationReport()
    sanitized: dict[str, pd.DataFrame] = {}
    for table, frame in frames.items():
        copied = frame.copy()
        for column in copied.columns:
            for index, value in copied[column].items():
                if not isinstance(value, str):
                    continue
                cleaned, repairs, escaped = sanitize_excel_text(value)
                if cleaned == value:
                    continue
                row = copied.at[index, "id"] if "id" in copied.columns else index
                report.add(
                    table=str(table), row=row, column=str(column),
                    repairs=repairs, escaped=escaped,
                )
                copied.at[index, column] = cleaned
        sanitized[table] = copied
    return sanitized, report
