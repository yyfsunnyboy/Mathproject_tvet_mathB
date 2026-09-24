# -*- coding: utf-8 -*-
"""Focused MTEF regressions from 3-1 Equation.DSMT4 empty_latex root cause.

Root cause: SIZE record select=101 (explicit point size) was always read as
two raw bytes (lsize,dsize), desynchronizing the stream so the next payload
byte 0x20 was misclassified as unknown record 32 → Valid=False → empty_latex.

Vector formulas use tmLIM + upper slot U+20D1 (COMBINING RIGHT ARROW ABOVE).
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from core.mtef import MTEF, equation_native_to_latex
from core.mtef.record import MtAST, MtChar, MtLine, MtTmpl, RecordType, SelectorType

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "mtef_dsmt4_3_1"


def _load(name: str) -> bytes:
    path = FIXTURE_DIR / name
    assert path.is_file(), f"missing fixture {path}"
    return path.read_bytes()


def _render_ast(root_children: list[MtAST]) -> str:
    eqn = MTEF()
    eqn.Valid = True
    root = MtAST(RecordType.ROOT, None, None)
    root.children = root_children
    eqn.ast = root
    return eqn.Translate()


def _ast_char(mtcode: int, typeface: int = 128 + 3) -> MtAST:
    ch = MtChar()
    ch.mtcode = mtcode
    ch.typeface = typeface
    return MtAST(RecordType.CHAR, ch, None)


def _ast_line(children: list[MtAST], null: bool = False) -> MtAST:
    line = MtLine()
    line.null = null
    node = MtAST(RecordType.LINE, line, None)
    node.children = children
    return node


def test_a_already_ok_simple_formula_still_converts():
    latex, meta = equation_native_to_latex(_load("ok_simple_r_gt_0.eqn_native"))
    assert meta.get("valid") is True
    assert meta.get("error") is None
    assert "r" in latex and "0" in latex
    assert ">" in latex or "\\gt" in latex or "＞" in latex


def test_b_vector_ab_overrightarrow_from_real_dsmt4():
    latex, meta = equation_native_to_latex(_load("vector_AB.eqn_native"))
    assert meta.get("valid") is True, meta
    assert "overrightarrow{AB}" in latex.replace(" ", "")


def test_c_vector_single_letter_uses_vec():
    latex, meta = equation_native_to_latex(_load("vector_a.eqn_native"))
    assert meta.get("valid") is True, meta
    assert r"\vec{a}" in latex.replace(" ", "") or r"\vec{a}" in latex


def test_d_fraction_with_vector_still_converts():
    latex, meta = equation_native_to_latex(_load("fract_3_2_vec_a.eqn_native"))
    assert meta.get("valid") is True, meta
    assert r"\frac" in latex
    assert r"\vec{a}" in latex or "overrightarrow" in latex


def test_e_equality_with_vectors_still_converts():
    latex, meta = equation_native_to_latex(_load("vector_eq_a_AB.eqn_native"))
    assert meta.get("valid") is True, meta
    assert "=" in latex
    assert r"\vec{a}" in latex or "vec{a}" in latex.replace(" ", "")
    assert "overrightarrow{AB}" in latex.replace(" ", "")


def test_f_unsupported_record_does_not_silently_become_empty_latex():
    latex, meta = equation_native_to_latex(_load("unsupported_record_32.eqn_native"))
    assert latex == ""
    assert meta.get("valid") is False
    assert meta.get("error") == "mtef_unsupported_record:32"
    assert meta.get("failure_stage") == "mtef_unsupported_record"
    assert meta.get("unknown_record") == 32
    # Must not collapse to the vague empty_latex label.
    assert meta.get("error") != "empty_latex"


def test_size_101_explicit_point_size_does_not_desync_stream():
    # Header + FULL + LINE + SIZE(101, int16) + CHAR 'A' + END + END
    point = (960).to_bytes(2, "little", signed=True)  # 0x03c0 as in 3-1 samples
    body = bytes(
        [
            5, 0, 0, 0, 0, 0, 0,  # MTEF header + empty app + inline
            RecordType.FULL,
            RecordType.LINE, 0,
            RecordType.SIZE, 101, point[0], point[1],
            RecordType.CHAR, 0, 128 + 3, ord("A"), 0,
            RecordType.END,
            RecordType.END,
        ]
    )
    eqn = MTEF()
    eqn.reader = io.BytesIO(body)
    eqn.readRecord()
    eqn.makeAST()
    assert eqn.Valid, (
        getattr(eqn, "_unknown_record", None),
        getattr(eqn, "_unknown_offset", None),
    )
    assert "A" in eqn.Translate()


def test_tm_lim_arrow_accent_ast_serializer():
    tmpl = MtTmpl()
    tmpl.selector = SelectorType.tmLIM
    tmpl.variation = 32
    node = MtAST(RecordType.TMPL, tmpl, None)
    node.children = [
        _ast_line([_ast_char(ord("A")), _ast_char(ord("B"))]),
        _ast_line([], null=True),
        _ast_line([_ast_char(0x20D1)]),
    ]
    latex = _render_ast([_ast_line([node])])
    assert "overrightarrow{AB}" in latex.replace(" ", "")


def test_abs_vec_equals_overline_fixture():
    latex, meta = equation_native_to_latex(_load("abs_vec_eq_overline.eqn_native"))
    assert meta.get("valid") is True, meta
    assert "overrightarrow{AB}" in latex.replace(" ", "")
    assert "overline" in latex
    assert "=" in latex
