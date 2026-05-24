# -*- coding: utf-8 -*-
"""ImportAuthorityResolver 系統性測試（非單檔補丁）。"""

from unittest.mock import MagicMock

import pytest

from core.textbook_filename_parser import parse_textbook_filename_metadata
from core.textbook_import_authority import (
    ImportAuthorityResolver,
    normalize_section_code,
    resolve_section_code_with_authority,
)
from core.textbook_processor_v2 import (
    MATHB1_CHAPTER1_CANONICAL_TITLE,
    _build_anchor_blocks_v2,
    _force_mathb_chapter_title_if_section_matches,
    _resolve_import_source_metadata,
    phase2_mathb_chapter_self_assessment_slice,
)


def test_section_textbook_form_stale_vs_21(monkeypatch):
    fn = parse_textbook_filename_metadata("第二章 2-1 斜率-課本_Latex.docx")
    got = resolve_section_code_with_authority(
        source_scope="section_textbook",
        block_meta={"concept_code": "2-1.1", "section_code": "1-4"},
        concept_code="2-1.1",
        filename_meta=fn,
        curriculum_info={"section_code": "1-4", "form_section_code": "1-4"},
        authority_mode="phase4",
    )
    assert got["section_code"] == "2-1"
    assert got["source"] == "concept_heading"
    assert got["overrode_form"] is True


def test_generic_chapter32():
    fn = parse_textbook_filename_metadata("第三章 3-2 範例-課本_Latex.docx")
    got = resolve_section_code_with_authority(
        source_scope="section_textbook",
        concept_code="3-2.1",
        filename_meta=fn,
        curriculum_info={"form_section_code": "1-4"},
        authority_mode="phase4",
    )
    assert got["section_code"] == "3-2"


def test_form_fallback_only():
    got = resolve_section_code_with_authority(
        source_scope="section_textbook",
        curriculum_info={"section_code": "1-4", "form_section_code": "1-4"},
        authority_mode="phase4",
    )
    assert got["section_code"] == "1-4"
    assert got["source"] == "form"


def test_self_assessment_section_from_content():
    text = "CH2自我評量\n自我評量\n2-2 直線方程式\n1.\t題目\n"
    meta = phase2_mathb_chapter_self_assessment_slice(
        text.splitlines(), chapter_index=2
    )
    key = next(iter(meta))
    got = resolve_section_code_with_authority(
        source_scope="chapter_self_assessment",
        block_meta=meta[key],
        curriculum_info={"section_code": "1-4", "form_section_code": "1-4"},
        authority_mode="self_assessment",
    )
    assert got["section_code"] == "2-2"
    policy = ImportAuthorityResolver.skill_policy_for_scope("chapter_self_assessment")
    assert policy == "use_existing_only"


def test_b1_chapter2_not_forced_to_chapter1():
    assert (
        _force_mathb_chapter_title_if_section_matches(
            "2 直線方程式",
            "2-1",
        )
        == "2 直線方程式"
    )
    assert (
        _force_mathb_chapter_title_if_section_matches(
            "第一章 坐標系與函數圖形",
            "1-1",
        )
        == MATHB1_CHAPTER1_CANONICAL_TITLE
    )


def test_chapter14_filename_consistent():
    bundle = _resolve_import_source_metadata(
        parse_filename="第一章 1-4 一元二次不等式-課本_Latex.docx",
        lines=[],
        curriculum_info={"section_code": "1-4", "volume": "數學B1"},
    )
    assert bundle["curriculum_info"]["section_code"] == "1-4"


def test_self_assessment_scope_from_filename():
    scope, evidence, _info = ImportAuthorityResolver.resolve_import_source_scope(
        "第一章 自我評量-課本_Latex.docx",
        ["CH1自我評量", "自我評量", "1-1 數線\n", "1.\t題1\n"],
        {"section_code": "1-4"},
    )
    assert scope == "chapter_self_assessment"
    assert evidence.source_scope_candidates.get("filename") == "chapter_self_assessment"


def test_outline_authority_from_row(monkeypatch):
    row = MagicMock()
    row.chapter = "2 直線方程式"
    row.section = "2-1 斜率"
    row.volume = "數學B1"
    row.skill_id = "outline_vocational_數學B1_21"
    monkeypatch.setattr(
        ImportAuthorityResolver,
        "lookup_outline_row",
        lambda _c, _v, code: row if code == "2-1" else None,
    )
    auth = ImportAuthorityResolver.resolve_outline_authority(
        {"curriculum": "vocational", "volume": "數學B1"},
        "2-1",
        source_scope="section_textbook",
    )
    assert auth.chapter_title == "2 直線方程式"
    assert auth.section_title == "2-1 斜率"
    assert auth.skill_policy == "create_or_reuse_from_docx_heading"


def test_three_concept_headings_block_meta(monkeypatch):
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
    lines = [
        "2-1.1 直線的斜率",
        "例1",
        "題目",
        "2-1.2 兩平行線的性質",
        "例2",
        "題目2",
        "2-1.3 兩垂直線的性質",
        "例3",
        "題目3",
    ]
    _, meta = _build_anchor_blocks_v2(
        lines,
        curriculum_info={"volume": "數學B1", "section_code": "1-4"},
    )
    codes = {m.get("concept_code") for m in meta.values() if m.get("concept_code")}
    sections = {m.get("section_code") for m in meta.values()}
    assert len(codes) >= 2
    assert all(str(c).startswith("2-1.") for c in codes)
    assert sections == {"2-1"}
    assert "1-4" not in sections
