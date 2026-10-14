# -*- coding: utf-8 -*-
"""Regression tests for XML 1.0 text sanitization at OOXML write boundaries."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
from lxml import etree

from core.textbook_mathtype_converter import _make_latex_run, convert_docx_mathtype_to_latex_docx
from core.xml_text_compat import (
    find_illegal_xml_characters,
    is_xml_1_0_char,
    sanitize_xml_text,
)

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_sanitize_keeps_normal_chinese_and_ascii():
    text = "正常中文 ABC 123"
    assert sanitize_xml_text(text) is text or sanitize_xml_text(text) == text
    assert sanitize_xml_text(text) == text


def test_sanitize_strips_null_byte():
    assert sanitize_xml_text("a\x00b") == "ab"


def test_sanitize_strips_vertical_tab():
    assert sanitize_xml_text("a\x0bb") == "ab"


def test_sanitize_strips_form_feed():
    assert sanitize_xml_text("a\x0cb") == "ab"


def test_sanitize_keeps_tab_lf_cr():
    assert sanitize_xml_text("a\tb\nc\rd") == "a\tb\nc\rd"


def test_sanitize_keeps_mathtype_pua_ef01():
    text = "向量 \uef01 數學"
    assert sanitize_xml_text(text) == text
    assert "\uef01" in sanitize_xml_text(text)


def test_sanitize_keeps_chinese_and_latex():
    text = r"設 $x^2+1=0$"
    assert sanitize_xml_text(text) == text


def test_sanitize_non_str_passthrough():
    assert sanitize_xml_text(None) is None
    assert sanitize_xml_text(12) == 12
    assert sanitize_xml_text(["a"]) == ["a"]


def test_find_illegal_reports_codepoint():
    hits = find_illegal_xml_characters("a\x02b")
    assert hits == [{"index": 1, "repr": "'\\x02'", "codepoint": "U+0002"}]


def test_xml_1_0_char_ranges():
    assert is_xml_1_0_char(0x9)
    assert is_xml_1_0_char(0xA)
    assert is_xml_1_0_char(0xD)
    assert is_xml_1_0_char(0x20)
    assert is_xml_1_0_char(0xEF01)
    assert not is_xml_1_0_char(0x0)
    assert not is_xml_1_0_char(0x2)
    assert not is_xml_1_0_char(0xB)
    assert not is_xml_1_0_char(0xC)


def test_make_latex_run_persists_illegal_control_without_raising():
    latex = r"\cdots +" + "\x02" + r"\left[ a_{1} \right]" + "\uef08"
    run = _make_latex_run(latex)
    text_node = run.find(f"{{{W_NS}}}t")
    assert text_node is not None
    assert text_node.text is not None
    assert "\x02" not in text_node.text
    assert "\uef08" in text_node.text
    assert r"\cdots +" in text_node.text
    # Round-trip through lxml serialization must also succeed.
    xml = etree.tostring(run, encoding="unicode")
    assert "\x02" not in xml
    assert "\\cdots +" in xml


def _minimal_docx_bytes(body_xml: str) -> bytes:
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        "</Relationships>"
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}"><w:body>{body_xml}</w:body></w:document>'
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document)
    return buf.getvalue()


def test_convert_docx_path_survives_when_make_latex_run_gets_controls(tmp_path, monkeypatch):
    """Representative persistence path: OOXML rewrite must not raise ValueError."""
    source = tmp_path / "plain.docx"
    source.write_bytes(_minimal_docx_bytes("<w:p><w:r><w:t>ok</w:t></w:r></w:p><w:sectPr/>"))
    out = tmp_path / "out.docx"

    from core import textbook_mathtype_converter as conv

    original = conv._make_latex_run

    def force_control(latex_text: str):
        return original((latex_text or "") + "\x0b" + "\uef01")

    monkeypatch.setattr(conv, "_make_latex_run", force_control)
    # No OLE objects → converter still rewrites document.xml; ensure helper itself is safe.
    run = conv._make_latex_run(r"\alpha")
    assert "\x0b" not in (run.find(f"{{{W_NS}}}t").text or "")
    assert "\uef01" in (run.find(f"{{{W_NS}}}t").text or "")

    report = convert_docx_mathtype_to_latex_docx(source, out)
    assert out.is_file()
    assert report["output"] == str(out)


@pytest.mark.skipif(
    not (PROJECT_ROOT / "textbook_import" / "source" / "vocational" / "math_B3").exists(),
    reason="B3 source not present",
)
def test_b3_offending_formula_conversion_no_longer_raises(tmp_path):
    b3_dir = PROJECT_ROOT / "textbook_import" / "source" / "vocational" / "math_B3"
    docx = next(b3_dir.glob("*.docx"), None)
    if docx is None:
        pytest.skip("B3 docx missing")
    out = tmp_path / "b3_latex.docx"
    report = convert_docx_mathtype_to_latex_docx(docx, out)
    assert out.is_file()
    assert int(report.get("mathtype_ole") or 0) > 0
    # Offending formula previously contained U+0002; conversion must complete.
    assert report.get("converted_ok", 0) + report.get("converted_failed", 0) == report.get("mathtype_ole")
