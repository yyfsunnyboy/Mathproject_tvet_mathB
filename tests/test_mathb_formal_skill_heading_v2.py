# -*- coding: utf-8 -*-

from core.mathb_concept_heading import detect_mathb_concept_heading
from core.textbook_processor_v2 import _parse_mathb_concept_line


def test_numbered_compact_heading():
    parsed = _parse_mathb_concept_line("3-2.1除法原理", section_code="3-2")
    assert parsed is not None
    code, name, switch_current, meta = parsed
    assert code == "3-2.1"
    assert name == "除法原理"
    assert switch_current is True
    assert meta["heading_kind"] == "numbered_compact"
    assert meta["section_code"] == "3-2"


def test_numbered_spaced_heading():
    p1 = _parse_mathb_concept_line("3-2.2 餘式定理", section_code="3-2")
    p2 = _parse_mathb_concept_line("3-2.3 因式定理", section_code="3-2")
    assert p1 is not None and p2 is not None
    assert p1[0] == "3-2.2" and p1[1] == "餘式定理" and p1[3]["heading_kind"] == "numbered_spaced"
    assert p2[0] == "3-2.3" and p2[1] == "因式定理" and p2[3]["heading_kind"] == "numbered_spaced"


def test_generic_section_number_not_hardcoded():
    parsed = _parse_mathb_concept_line("4-1.2某個概念名稱", section_code="4-1")
    assert parsed is not None
    assert parsed[0] == "4-1.2"
    assert parsed[1] == "某個概念名稱"
    assert parsed[3]["section_code"] == "4-1"


def test_fullwidth_and_dash_variants_normalize():
    parsed = _parse_mathb_concept_line("３－２.１除法原理", section_code="3-2")
    assert parsed is not None
    assert parsed[0] == "3-2.1"
    assert parsed[3]["section_code"] == "3-2"
    parsed2 = _parse_mathb_concept_line("3—2.1除法原理", section_code="3-2")
    assert parsed2 is not None
    assert parsed2[0] == "3-2.1"


def test_plain_heading_does_not_create_new_skill():
    assert _parse_mathb_concept_line("除法原理", section_code="3-2") is None
    parsed_dup = _parse_mathb_concept_line(
        "除法原理",
        section_code="3-2",
        current_concept_name="除法原理",
    )
    assert parsed_dup is not None
    assert parsed_dup[2] is False
    assert parsed_dup[3].get("duplicate_merge") is True


def test_sentence_generic_formula_are_rejected():
    bad_lines = [
        "這就是多項式的「除法原理」。",
        "上述討論的結果,我們稱為餘式定理。",
        "接著我們用以下例題來說明餘式定理。",
        "延伸:",
        "說明:",
        "公式",
        "一般來說,因式定理可以推廣如下:",
        "利用餘式定理可得",
        "f(x)=x+1",
    ]
    for line in bad_lines:
        assert _parse_mathb_concept_line(line, section_code="3-2") is None


def test_chapter_self_assessment_scope_no_heading_detection():
    hit = detect_mathb_concept_heading(
        "3-2.1除法原理",
        current_source_scope="chapter_self_assessment",
    )
    assert hit is None
