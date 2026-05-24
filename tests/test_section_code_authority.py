# -*- coding: utf-8 -*-
"""通用 section_code 權威決策：form 不得覆蓋 DOCX / 檔名。"""

from unittest.mock import MagicMock

import pytest

from core.textbook_filename_parser import parse_textbook_filename_metadata
from core.textbook_processor_v2 import (
    _build_anchor_blocks_v2,
    _resolve_import_source_metadata,
    normalize_section_code,
    phase2_mathb_chapter_self_assessment_slice,
    resolve_section_code_with_authority,
)


def test_form_stale_overridden_by_concept_and_filename():
    fn = parse_textbook_filename_metadata("第二章 2-1 斜率-課本_Latex.docx")
    info = {
        "curriculum": "vocational",
        "volume": "數學B1",
        "section_code": "1-4",
        "source_scope": "section_textbook",
        "filename_meta": fn,
        "filename_section_code": fn["section_code"],
        "form_section_code": "1-4",
    }
    got = resolve_section_code_with_authority(
        source_scope="section_textbook",
        block_meta={"concept_code": "2-1.1", "section_code": "1-4"},
        concept_code="2-1.1",
        filename_meta=fn,
        curriculum_info=info,
        authority_mode="phase4",
    )
    assert got["section_code"] == "2-1"
    assert got["source"] == "concept_heading"
    assert got["overrode_form"] is True


def test_chapter3_section32_generic():
    fn = parse_textbook_filename_metadata("第三章 3-2 範例標題-課本_Latex.docx")
    got = resolve_section_code_with_authority(
        source_scope="section_textbook",
        concept_code="3-2.1",
        filename_meta=fn,
        curriculum_info={
            "section_code": "1-4",
            "form_section_code": "1-4",
            "filename_section_code": "3-2",
        },
        authority_mode="phase4",
    )
    assert got["section_code"] == "3-2"
    assert got["source"] == "concept_heading"


def test_form_fallback_when_no_other_signal():
    got = resolve_section_code_with_authority(
        source_scope="section_textbook",
        curriculum_info={"section_code": "1-4", "form_section_code": "1-4"},
        authority_mode="phase4",
    )
    assert got["section_code"] == "1-4"
    assert got["source"] == "form"
    assert got["overrode_form"] is False


def test_self_assessment_ignores_form():
    text = (
        "CH2自我評量\n"
        "自我評量\n"
        "2-2 直線方程式\n"
        "1.\t第一題內容\n"
    )
    meta = phase2_mathb_chapter_self_assessment_slice(
        text.splitlines(),
        curriculum_info={"section_code": "1-4", "chapter_index": 2},
        chapter_index=2,
    )
    assert meta
    key = next(iter(meta))
    assert meta[key]["section_code"] == "2-2"
    got = resolve_section_code_with_authority(
        source_scope="chapter_self_assessment",
        block_meta=meta[key],
        curriculum_info={"section_code": "1-4", "form_section_code": "1-4"},
        authority_mode="self_assessment",
    )
    assert got["section_code"] == "2-2"
    assert got["source"] == "block_meta"


def test_build_anchor_blocks_concept_heading_sets_section(monkeypatch):
    monkeypatch.setattr(
        "core.textbook_processor_v2._resolve_formal_concept_en_id_v2",
        lambda **_k: {
            "concept_name": "直線的斜率",
            "concept_en_id": "SlopeOfALine",
            "formal_skill_id": "vh_數學B1_SlopeOfALine",
        },
    )
    monkeypatch.setattr(
        "core.textbook_processor_v2._persist_formal_skill_from_docx_heading",
        lambda **_k: None,
    )
    lines = ["2-1.1 直線的斜率", "例1", "題目內容", "解", "詳解"]
    _, meta = _build_anchor_blocks_v2(
        lines,
        curriculum_info={
            "curriculum": "vocational",
            "volume": "數學B1",
            "section_code": "1-4",
            "chapter": "1 坐標系與函數圖形",
        },
    )
    assert meta
    sample = next(iter(meta.values()))
    assert sample["section_code"] == "2-1"
    assert sample["concept_code"] == "2-1.1"


def test_filename_14_not_overridden_when_consistent():
    fn = parse_textbook_filename_metadata("第一章 1-4 一元二次不等式-課本_Latex.docx")
    bundle = _resolve_import_source_metadata(
        parse_filename="第一章 1-4 一元二次不等式-課本_Latex.docx",
        lines=[],
        curriculum_info={"section_code": "1-4", "volume": "數學B1"},
    )
    info = bundle["curriculum_info"]
    assert info["section_code"] == "1-4"
    assert info.get("form_section_code") == "1-4"
    got = resolve_section_code_with_authority(
        source_scope="section_textbook",
        filename_meta=fn,
        curriculum_info=info,
        authority_mode="phase4",
    )
    assert got["section_code"] == "1-4"
    assert got["source"] in {"filename_meta", "form", "block_meta"}


def test_normalize_fullwidth_section_code():
    assert normalize_section_code("２－１") == "2-1"


def test_section_textbook_skill_coords_from_outline(monkeypatch):
    from core.textbook_processor_v2 import _persist_formal_skill_from_docx_heading

    outline = MagicMock()
    outline.chapter = "2 直線方程式"
    outline.section = "2-1 斜率"
    outline.curriculum = "vocational"
    outline.volume = "數學B1"

    captured: dict = {}

    def _fake_ensure(**kwargs):
        captured.update(kwargs)
        return MagicMock()

    monkeypatch.setattr(
        "core.textbook_processor_v2._lookup_outline_section_curriculum_row",
        lambda _info, code: outline if code == "2-1" else None,
    )
    monkeypatch.setattr(
        "core.textbook_processor_v2._ensure_formal_skill_info_and_curriculum_v2",
        _fake_ensure,
    )
    _persist_formal_skill_from_docx_heading(
        concept_code="2-1.1",
        concept_name="直線的斜率",
        concept_en_id="SlopeOfALine",
        formal_skill_id="vh_數學B1_SlopeOfALine",
        curriculum_info={"curriculum": "vocational", "volume": "數學B1", "section_code": "1-4"},
        section_code="2-1",
        section_title="2-1 斜率",
    )
    assert captured["chapter_title"] == "2 直線方程式"
    assert captured["section_title"] == "2-1 斜率"
