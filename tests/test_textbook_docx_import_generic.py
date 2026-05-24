# -*- coding: utf-8 -*-
"""通用 DOCX 匯入：檔名、content fallback、自我評量 skill 防線。"""

from unittest.mock import MagicMock

import pytest

from core.textbook_filename_parser import (
    detect_docx_source_scope_from_content,
    merge_source_scope_detection,
    parse_textbook_filename_metadata,
    resolve_upload_filenames,
)
from core.textbook_processor_v2 import (
    _get_self_assessment_skill_candidates_v2,
    _mathb_fallback_formal_en_id,
    _phase4_resolve_mathb_formal_binding,
    phase2_deterministic_block_slice,
    phase2_mathb_chapter_self_assessment_slice,
    validate_existing_skill_binding_for_import,
)


def test_a_original_filename_used_for_parse():
    names = resolve_upload_filenames(
        "第一章 自我評量-課本_Latex.docx",
        "-_Latex.docx",
    )
    assert names["parse_filename"] == "第一章 自我評量-課本_Latex.docx"
    meta = parse_textbook_filename_metadata(names["parse_filename"])
    assert meta["source_scope"] == "chapter_self_assessment"
    assert meta["chapter_index"] == 1
    assert meta["section_code"] is None
    assert meta["section_title"] is None


def test_b_chapter_self_assessment_filenames():
    cases = [
        ("第二章 自我評量-課本_Latex.docx", 2),
        ("第3章自我評量-課本_Latex.docx", 3),
        ("CH4自我評量-課本_Latex.docx", 4),
        ("第一章自我評量-課本_Latex.docx", 1),
        ("數學B2 第二章 自我評量-課本_Latex.docx", 2),
    ]
    for filename, expected_ch in cases:
        meta = parse_textbook_filename_metadata(filename)
        assert meta["source_scope"] == "chapter_self_assessment", filename
        assert meta["chapter_index"] == expected_ch, filename
        assert meta["section_code"] is None, filename


def test_c_section_textbook_filenames():
    cases = [
        ("第一章 1-1 數線與絕對值-課本_Latex.docx", "1-1"),
        ("第二章 2-1 古典機率-課本_Latex.docx", "2-1"),
        ("第3章 3-2 統計圖表-課本_Latex.docx", "3-2"),
    ]
    for filename, expected_code in cases:
        meta = parse_textbook_filename_metadata(filename)
        assert meta["source_scope"] == "section_textbook", filename
        assert meta["section_code"] == expected_code, filename
        assert expected_code in str(meta["section_title"])


def test_d_content_fallback_self_assessment():
    lines = [
        "第2章 直線方程式",
        "CH2自我評量",
        "自我評量",
        "2-1 斜率",
        "1. 求斜率",
        "2-2 直線方程式",
        "2. 求直線",
    ]
    meta = detect_docx_source_scope_from_content(lines)
    assert meta["source_scope"] == "chapter_self_assessment"
    assert meta["chapter_index"] == 2
    assert len(meta["section_codes"]) >= 2

    merged = merge_source_scope_detection(
        parse_textbook_filename_metadata("-_Latex.docx"),
        meta,
    )
    assert merged["source_scope"] == "chapter_self_assessment"


def test_e_self_assessment_fallback_skill_id_disabled():
    assert _mathb_fallback_formal_en_id("1-1", "self_assessment") == ""


def test_f_phase4_rejects_ai_pick_outside_candidates(monkeypatch):
    class _OutlineRow:
        curriculum = "vocational"
        volume = "數學B1"
        chapter = "1 坐標系與函數圖形"
        section = "1-1 數線與絕對值"
        skill_id = "outline_vocational_數學B1_11"
        display_order = 1
        id = 1

    monkeypatch.setattr(
        "core.textbook_processor_v2._lookup_outline_section_curriculum_row",
        lambda *_a, **_k: _OutlineRow(),
    )
    monkeypatch.setattr(
        "core.textbook_processor_v2._get_self_assessment_skill_candidates_v2",
        lambda **_k: [{"skill_id": "vh_real_skill", "concept_name": "數線", "concept_en_id": "Line"}],
    )
    monkeypatch.setattr(
        "core.textbook_processor_v2._ai_select_formal_skill_for_problem_v2",
        lambda **_k: {"skill_id": "vh_not_in_candidates"},
    )

    result = _phase4_resolve_mathb_formal_binding(
        block_meta={
            "section_code": "1-1",
            "anchor": "CH1自我評量 題1",
            "formal_skill_id": "",
        },
        source_type="self_assessment",
        db_problem_text="題幹",
        curriculum_info={"curriculum": "vocational", "volume": "數學B1", "grade": 10},
        item_sec_code="1-1",
        coords={"curriculum": "vocational", "volume": "數學B1", "grade": 10},
        source_description="CH1自我評量 題1",
    )
    assert result is None


def test_g_chapter2_self_assessment_section_by_heading_not_question_number():
    text = (
        "CH2自我評量\n"
        "自我評量\n"
        "2-1 斜率\n"
        "1.\t第一題\n"
        "2.\t第二題\n"
        "3.\t第三題\n"
        "2-2 直線方程式\n"
        "4.\t第四題\n"
        "5.\t第五題\n"
        "2-3 點到直線距離\n"
        "9.\t第九題\n"
        "12.\t第十二題\n"
    )
    meta = phase2_mathb_chapter_self_assessment_slice(text.splitlines(), chapter_index=2)
    by_section = {}
    for item in meta.values():
        by_section.setdefault(item["section_code"], []).append(item["anchor"])

    assert set(by_section) == {"2-1", "2-2", "2-3"}
    assert len(by_section["2-1"]) == 3
    assert len(by_section["2-2"]) == 2
    assert len(by_section["2-3"]) == 2
    assert all(item["source_type"] == "self_assessment" for item in meta.values())
    assert all(item["formal_skill_id"] == "" for item in meta.values())

    blocks = phase2_deterministic_block_slice(
        text.splitlines(),
        source_scope="chapter_self_assessment",
        curriculum_info={"curriculum": "vocational", "volume": "數學B2", "grade": 11},
    )
    assert "CH2自我評量 題1" in blocks
    assert "CH2自我評量 題12" in blocks


def test_validate_existing_skill_binding_blocks_fallback_patterns():
    ok, reason = validate_existing_skill_binding_for_import(
        "SelfAssessment_1_1",
        source_type="self_assessment",
        section_code="1-1",
        curriculum_info={"curriculum": "vocational", "volume": "數學B1"},
    )
    assert ok is False
    assert reason == "fallback_pattern"

    ok2, reason2 = validate_existing_skill_binding_for_import(
        "vh_ok_skill",
        source_type="textbook_example",
        section_code="1-1",
        curriculum_info={"curriculum": "vocational", "volume": "數學B1"},
    )
    assert ok2 is True
    assert reason2 == ""
