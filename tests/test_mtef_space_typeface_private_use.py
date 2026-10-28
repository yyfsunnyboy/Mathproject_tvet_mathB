# -*- coding: utf-8 -*-
"""Regression: MathType space-typeface U+EF08 (permutation symbol P_k^n) and the private-use Stage 1 gate.

Evidence (數學2 單元4 排列 DOCX + paired PDF): ``P`` + char U+EF08 (typeface 128+fnSPACE) + SUBSUP template is
the printed permutation symbol P_k^n; the PDF has no glyph for U+EF08, only a small gap.  The fix is scoped to the
space typeface; an unknown private-use code anywhere else must stay visible so the Gate blocks it.
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

import pytest

from core.mtef import mtef_bytes_to_latex
from core.mtef.mtef import MTEF
from core.mtef.record import MtAST, MtChar, MtLine, RecordType
from core.textbook_stage1_gate import evaluate_row, evaluate_stage1_gate, private_use_symbols

ROOT = Path(__file__).resolve().parents[1]
UNIT4_DOCX = ROOT / "textbook_import/uploaded_sources/general/數學2/327f295a06d7_單元04-排列.docx"
PRIVATE_USE = re.compile("[\ue000-\uf8ff]")


def _char(mtcode: int, typeface: int) -> MtAST:
    ch = MtChar()
    ch.mtcode = mtcode
    ch.typeface = typeface
    return MtAST(RecordType.CHAR, ch, None)


def _render(chars: list[MtAST]) -> str:
    eqn = MTEF()
    eqn.Valid = True
    line = MtAST(RecordType.LINE, MtLine(), None)
    line.children = chars
    root = MtAST(RecordType.ROOT, None, None)
    root.children = [line]
    eqn.ast = root
    return eqn.Translate()


def test_ef08_in_space_typeface_is_layout_spacing_only():
    out = _render([_char(ord("P"), 128 + 3), _char(0xEF08, 128 + 24), _char(ord("3"), 128 + 8)])
    assert "P" in out and "3" in out
    assert "\uef08" not in out


def test_ef08_outside_space_typeface_is_not_guessed():
    out = _render([_char(ord("P"), 128 + 3), _char(0xEF08, 128 + 2)])
    assert "\uef08" in out  # stays visible -> Gate blocker


def test_existing_space_and_symbol_mappings_unchanged():
    assert _render([_char(ord("a"), 128 + 3), _char(0xEF02, 128 + 24), _char(ord("b"), 128 + 3)]).count("\\,") == 1
    assert _render([_char(0xEF05, 128 + 24)]).count("\\quad") == 1
    assert "\\parallel" in _render([_char(ord("a"), 128 + 3), _char(0xEF04, 128 + 24), _char(ord("/"), 128 + 2),
                                    _char(0xEF01, 128 + 24), _char(ord("/"), 128 + 2), _char(ord("b"), 128 + 3)])
    assert "\\mathfrak{A}" in _render([_char(0xF000, 128 + 6)])


@pytest.mark.skipif(not UNIT4_DOCX.is_file(), reason="Unit 4 authoritative DOCX unavailable")
def test_unit4_real_permutation_ole_objects_have_no_private_use():
    with zipfile.ZipFile(UNIT4_DOCX) as package:
        oles = [n for n in package.namelist() if n.startswith("word/embeddings/oleObject")]
        results = {n: mtef_bytes_to_latex(package.read(n)) for n in oles}
    assert len(oles) == 81
    assert all(meta.get("valid") for _, meta in results.values())
    assert not [n for n, (latex, _) in results.items() if PRIVATE_USE.search(latex)]
    permutations = [latex for latex, _ in results.values() if re.fullmatch(r"\$ P_\{ \d \}\s+\^\{ \d \} \$", latex)]
    assert any("_{ 3 }" in latex and "^{ 5 }" in latex for latex in permutations)


def _row(stem: str, solution: str = "") -> dict:
    return {"problem_text": stem, "detailed_solution": solution, "notes": "{}", "problem_type": "", "id": 1,
            "source_description": "t"}


def test_gate_blocks_unresolved_private_use_in_stem_and_solution():
    stem_row = _row("共有\\(P\uef08_{ 3 } ^{ 5 }\\)種排法。")
    assert "stem_unresolved_private_use_symbol" in evaluate_row(stem_row)["blockers"]
    solution_row = _row("求\\(x\\)的值。", "\\(P\uef08_{ 3 } ^{ 5 }=60\\)")
    assert "solution_unresolved_private_use_symbol" in evaluate_row(solution_row)["blockers"]
    gate = evaluate_stage1_gate([stem_row, solution_row])
    assert gate["status"] == "BLOCKED" and gate["reasons"]["stem_unresolved_private_use_symbol"] == 1
    assert private_use_symbols("a\uef08b\uf0c7") == ["U+EF08", "U+F0C7"]


def test_gate_does_not_flag_normal_math_or_resolved_symbols():
    row = _row("共有\\(P_{ 3 } ^{ 5 }\\cap A\\)種排法，∩ ∪ ′ ＞。", "\\(P_{ 3 } ^{ 5 }=60\\)")
    assert evaluate_row(row) == {"blockers": [], "reviews": []}
    assert private_use_symbols("") == []
