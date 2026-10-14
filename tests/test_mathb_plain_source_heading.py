# -*- coding: utf-8 -*-
"""Plain source headings stay distinct from printed concept codes and exercise numbers."""

from core.mathb_plain_source_heading import (
    assign_plain_source_questions,
    collect_plain_source_headings,
    parse_plain_source_heading,
)
from pathlib import Path

from core.textbook_importer_v3_docx import extract_docx_skill_headings

_ROOT = Path(__file__).resolve().parents[1] / "textbook_import" / "source" / "vocational"


def _original_docx(volume: str, section_code: str) -> Path:
    return next(
        path
        for path in (_ROOT / volume).glob(f"*{section_code}*-課本.docx")
        if "_Latex" not in path.name
    )


def test_exercise_and_prompt_numbering_is_not_a_source_heading():
    assert parse_plain_source_heading("1. 二元一次不等式的定義", style_name="02-內文1.")["concept_name"] == "二元一次不等式的定義"
    assert parse_plain_source_heading("1.\t圖示下列不等式的解", style_name="02-內文1.") is None
    assert parse_plain_source_heading("1. 試判斷下列何者", style_name="05a-習題1.") is None
    assert parse_plain_source_heading("5. 設點 A 試求 k", style_name="04d-隨1.") is None
    assert parse_plain_source_heading("1.\n計算步驟", style_name="02-內文1.") is None


def test_collection_stops_at_the_exercise_heading():
    paragraphs = [
        {"text": "1. 二元一次不等式的定義", "style": "02-內文1.", "source_order": 10, "next_text": "說明"},
        {"text": "3-2習題", "style": "00-1-1", "source_order": 20, "next_text": ""},
        {"text": "1. 這不是概念", "style": "02-內文1.", "source_order": 30, "next_text": "選項"},
    ]
    found = collect_plain_source_headings(paragraphs, section_code="3-2", volume="數學B3")
    assert [item["concept_name"] for item in found["plain_source_headings"]] == ["二元一次不等式的定義"]
    assert found["plain_source_headings"][0]["printed_concept_code"] is None
    assert found["plain_source_headings"][0]["internal_coordinate"] == "3-2#1"


def test_questions_follow_answering_skill_not_document_order():
    headings = extract_docx_skill_headings(
        str(_original_docx("math_B3", "3-2")), section_code="3-2", volume="數學B3"
    )["plain_source_headings"]
    samples = {
        "例1": "圖示下列二元一次不等式的解",
        "例4": "判斷點分別位在哪一區，以及是否在同一區",
        "小蘇": "營養師建議每天攝取量不能超過下列範圍，判斷數對是否符合",
        "基礎題8": "兩點在直線的異側，求參數",
        "進階題10": "如圖，寫出滿足圖示之不等式，並判斷一點是否為不等式的解",
    }
    rows = assign_plain_source_questions(
        {title: {"problem_text": text, "source_type": "textbook_example"} for title, text in samples.items()},
        headings,
    )
    by_title = {row["title"]: row for row in rows}
    assert by_title["例1"]["internal_coordinate"] == "3-2#3"
    assert by_title["例4"]["internal_coordinate"] == "3-2#4"
    assert by_title["小蘇"]["internal_coordinate"] == "3-2#2"
    assert by_title["基礎題8"]["internal_coordinate"] == "3-2#4"
    assert by_title["進階題10"]["internal_coordinate"] == "3-2#3"
    assert all(row["printed_concept_code"] is None for row in rows)


def test_b3_3_1_keeps_numbered_concepts():
    audit = extract_docx_skill_headings(str(_original_docx("math_B3", "3-1")), section_code="3-1", volume="數學B3")
    assert [item["concept_code"] for item in audit["skill_candidates"]] == ["3-1.1", "3-1.2", "3-1.3"]
    assert audit["plain_source_heading_count"] == 0
