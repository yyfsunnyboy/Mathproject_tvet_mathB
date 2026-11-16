"""Shared Word stem parsing: data rows are not headings (Defect B), keyword presence does not end a stem (Defect A)."""
import pytest

from core.textbook_processor import (
    _gh_stem_continues,
    _gh_stem_is_complete,
    is_numeric_data_row,
    is_structural_boundary_line,
    scan_general_high_layout,
    segment_question_block_text,
)


# ---- Defect B: data rows vs structural headings -------------------------------------------------------------
@pytest.mark.parametrize(
    "line",
    [
        "186, 188, 189, 191, 226，",
        "3.8%, 3.5%, 3.2%, 3.1%。",
        "21, 13, 8, 34, 5",
        "2, 5, 6, 9。",
        "1，2，3，4",
        "-3, 4, 0.5, 12",
        "1, 2, …, 10",
    ],
)
def test_numeric_data_rows_are_not_structural_boundaries(line):
    assert is_numeric_data_row(line) is True
    assert is_structural_boundary_line(line) is False


@pytest.mark.parametrize(
    "line",
    [
        "8一維數據分析",
        "2 三角函數",
        "1-1.3乘法原理",
        "1-1 排列組合",
        "第3章 機率",
        "例題3",
        "隨堂練習2",
        "8習題",
        "基礎題",
        "進階題2",
    ],
)
def test_headings_stay_structural_boundaries(line):
    assert is_numeric_data_row(line) is False
    assert is_structural_boundary_line(line) is True


def test_segment_keeps_data_rows_and_still_cuts_heading():
    text = "例題1 求下列數據的標準差。\n186, 188, 189, 191, 226，\n共5個數據。\n8一維數據分析\n後面的內文"
    seg, _ = segment_question_block_text(text, question_title="例題1")
    assert "186, 188, 189, 191, 226" in seg
    assert "共5個數據" in seg
    assert "8一維數據分析" not in seg
    assert "後面的內文" not in seg


# ---- Defect A: a stem ends by structure, not by keyword presence --------------------------------------------
def _cur(*stem, kind="practice"):
    return {"kind": kind, "stem_lines": list(stem)}


def test_stem_with_keyword_but_open_lead_in_is_not_complete():
    # "求" appears in the first sentence, yet the last sentence still promises data.
    assert _gh_stem_is_complete(["為了求得平均利潤，某店統計各月營業額如下表。"]) is False
    assert _gh_stem_continues(_cur("為了求得平均利潤，某店統計各月營業額如下表。"), "已知三月份的利潤為5萬元，求x的值。", set()) is True


def test_stem_with_ask_is_complete_and_exposition_does_not_reopen_it():
    stem = ["下表為某班成績，試求平均數。"]
    assert _gh_stem_is_complete(stem) is True
    assert _gh_stem_continues(_cur(*stem), "因此本章接著介紹另一個概念。", set()) is False


def test_exam_or_require_words_are_not_asks():
    assert _gh_stem_is_complete(["某次考試的成績分別為"]) is False
    assert _gh_stem_is_complete(["依照要求，成績依序如下："]) is False


def test_data_rows_continue_an_open_stem_and_ask_line_follows():
    stem = ["已知十位同學的體重（公斤）分別為"]
    assert _gh_stem_continues(_cur(*stem), "55, 56, 59, 59, 59, 60, 60, 63, 68, 71，", set()) is True
    stem.append("55, 56, 59, 59, 59, 60, 60, 63, 68, 71，")
    assert _gh_stem_continues(_cur(*stem), "求這10個數據的算術平均數。", set()) is True


def test_scan_collects_data_rows_and_all_ask_lines():
    text = "\n".join(
        [
            "8習題",
            "基礎題",
            "1.\t下列為某班的得分，",
            "186, 188, 189, 191, 226，",
            "已知滿分為250分，求這組數據的標準差。",
            "2.\t求下列各數據的標準差。",
        ]
    )
    scan = scan_general_high_layout(text, body_paragraphs=[])
    stems = {}
    for item in scan.get("items", scan.get("blocks", [])):
        stems[str(item.get("question_number") or item.get("number") or len(stems) + 1)] = item
    joined = repr(scan)
    assert "186, 188, 189, 191, 226" in joined
    assert "求這組數據的標準差" in joined


def test_scan_cell_structure_keeps_ask_line_after_data_lead_in():
    cell = ["例題2", "甲生的分數與比重如下表。", "試以比重為權數，計算學期成績。"]
    text = "\n".join(cell + ["解", "以比重為權數可得 83×0.3"])
    scan = scan_general_high_layout(text, body_paragraphs=[], table_cells=[cell])
    assert "試以比重為權數，計算學期成績" in repr(scan)


def test_scan_keeps_array_and_ask_after_standalone_table():
    from core.docx_data_tables import grid_to_latex

    array = grid_to_latex([["", "平常成績", "期末考"], ["分數", "65", "x"], ["比重", "30%", "30%"]])
    text = "\n".join(
        [
            "8習題",
            "基礎題",
            "2.\t某生本學期數學科的分數與比重如下表。",
            array,
            "已知該生的數學科學期成績為60分，求x的值。",
            "3.\t求平均成長率。",
        ]
    )
    stem = scan_general_high_layout(text, body_paragraphs=[])["blocks"]["8習題 基礎題2"]
    assert "\\begin{array}" in stem
    assert "求x的值" in stem
    assert "求平均成長率" not in stem


def test_scan_nested_cell_keeps_array_between_lead_in_and_ask():
    from core.docx_data_tables import grid_to_latex

    array = grid_to_latex([["顧客狀況", "被隔離"], ["機率", "0.001"]])
    cell = ["隨堂練習", "該公司推估機率如下表。", array, "試以機率為權數，計算平均利潤。"]
    text = "\n".join(cell + ["解", "平均利潤為499元。"])
    stem = scan_general_high_layout(text, body_paragraphs=[], table_cells=[cell])["blocks"]["隨堂練習1"]
    assert "\\begin{array}" in stem and "0.001" in stem
    assert "試以機率為權數，計算平均利潤" in stem
    assert "平均利潤為499元" not in stem
