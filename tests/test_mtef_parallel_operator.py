# -*- coding: utf-8 -*-
"""Regression: MathType / unicode parallel → \\parallel."""

from __future__ import annotations

from pathlib import Path

from core.mtef import equation_native_to_latex, normalize_parallel_latex
from core.mtef.record import MtAST, MtChar, MtLine, RecordType
from core.mtef.mtef import MTEF
from core.textbook_mathtype_converter import extract_equation_native, wrap_latex_for_v2
from core.textbook_processor_v2 import _sanitize_db_latex_delimiters

PROJECT_ROOT = Path(__file__).resolve().parents[1]
B2_32_DOCX = next(
    (PROJECT_ROOT / "textbook_import/source/vocational/math_B2").glob("*3-2*課本.docx"),
    None,
)


def _ast_char(mtcode: int, typeface: int = 128 + 8) -> MtAST:
    ch = MtChar()
    ch.mtcode = mtcode
    ch.typeface = typeface
    return MtAST(RecordType.CHAR, ch, None)


def _ast_line(children: list[MtAST]) -> MtAST:
    node = MtAST(RecordType.LINE, MtLine(), None)
    node.children = children
    return node


def _render_ast(root_children: list[MtAST]) -> str:
    eqn = MTEF()
    eqn.Valid = True
    root = MtAST(RecordType.ROOT, None, None)
    root.children = root_children
    eqn.ast = root
    return eqn.Translate()


def test_normalize_parallel_preserves_canonical_command():
    src = r"\vec{a} \parallel \vec{b}"
    out = normalize_parallel_latex(src)
    assert r"\parallel" in out
    assert "Math input error" not in out
    assert "\uef01" not in out


def test_normalize_parallel_preserves_norm_and_absolute_value():
    assert normalize_parallel_latex(r"\|\vec{a}\|") == r"\|\vec{a}\|"
    assert normalize_parallel_latex(r"|x|") == r"|x|"
    assert normalize_parallel_latex(r"\Vert v \Vert") == r"\Vert v \Vert"
    # U+2016 is a norm bar in this codebase (chars.py → \|), not parallel.
    assert normalize_parallel_latex("‖v‖") == "‖v‖"
    assert normalize_parallel_latex("a || b") == "a || b"
    assert normalize_parallel_latex("a||b") == "a||b"


def test_normalize_parallel_unicode_operator():
    out = normalize_parallel_latex("\\(\\vec{a}\u2225\\vec{b}\\)")
    assert r"\parallel" in out
    assert "\u2225" not in out
    assert "Math input error" not in out


def test_normalize_parallel_mathtype_trigraph_uef01():
    broken = f"\\(\\vec{{a}}\\ /{chr(0xEF01)}/\\vec{{b}}\\)"
    out = normalize_parallel_latex(broken)
    assert out == r"\(\vec{a}\parallel \vec{b}\)"
    assert chr(0xEF01) not in out
    assert "Math input error" not in out


def test_sanitize_db_path_rewrites_parallel_trigraph():
    db_text = (
        f"設\\(\\vec{{a}}=\\left ( {{ 2,\\ -1 }} \\right )\\)、"
        f"\\(\\vec{{b}}=\\left ( {{ k,\\ 3 }} \\right )\\)，"
        f"若\\(\\vec{{a}}\\ /{chr(0xEF01)}/\\vec{{b}}\\)，試求k的值。"
    )
    out = _sanitize_db_latex_delimiters(db_text)
    assert r"\parallel" in out
    assert chr(0xEF01) not in out
    assert "//" not in out.replace(r"\parallel", "")


def test_mtef_parallel_trigraph_ast_renders_parallel():
    # MathType encoding observed in B2 3-2: spacing + "/" + U+EF01 + "/"
    latex = _render_ast(
        [
            _ast_line(
                [
                    _ast_char(ord("a"), typeface=128 + 3),
                    _ast_char(0xEF04, typeface=128 + 24),  # MT space → "\ "
                    _ast_char(ord("/"), typeface=128 + 2),
                    _ast_char(0xEF01, typeface=128 + 24),
                    _ast_char(ord("/"), typeface=128 + 2),
                    _ast_char(ord("b"), typeface=128 + 3),
                ]
            )
        ]
    )
    assert r"\parallel" in latex
    assert "\uef01" not in latex
    wrapped = wrap_latex_for_v2(latex)
    assert wrapped == r"\(a\parallel b\)"


def test_b2_32_real_ole_parallel_equation():
    if B2_32_DOCX is None or not B2_32_DOCX.is_file():
        import pytest

        pytest.skip("B2 3-2 source DOCX unavailable")
    import zipfile

    with zipfile.ZipFile(B2_32_DOCX) as zf:
        data = zf.read("word/embeddings/oleObject206.bin")
    native, err = extract_equation_native(data)
    assert err is None and native
    latex, meta = equation_native_to_latex(native)
    assert meta.get("valid")
    assert r"\parallel" in latex
    assert "\uef01" not in latex
    assert wrap_latex_for_v2(latex) == r"\(\vec{a}\parallel \vec{b}\)"
