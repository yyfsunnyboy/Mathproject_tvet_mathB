from core.textbook_processor import (
    _extract_chart_metadata_for_mathb4_32,
    _is_mathb4_chart_target,
)


def test_old_non_32_target_does_not_enable_chart_metadata():
    assert _is_mathb4_chart_target("2-2 機率的運算", "vh_數學B4_ProbabilityProperties") is False


def test_32_table_question_generates_chart_data():
    text = "次數分配表：10-20 3，20-30 5，30-40 2，請畫直方圖"
    meta = _extract_chart_metadata_for_mathb4_32(text)
    assert meta.get("chart_renderable") is True
    assert meta.get("requires_chart") is True
    assert isinstance(meta.get("chart_data"), dict)
    assert len(meta["chart_data"]["labels"]) >= 2


def test_32_image_dependent_question_without_table_not_renderable():
    text = "如下圖所示，請依直方圖回答問題"
    meta = _extract_chart_metadata_for_mathb4_32(text)
    assert meta == {}


def test_probability_or_permutation_text_not_affected_by_chart_metadata():
    assert _extract_chart_metadata_for_mathb4_32("P(A \\cap B)=0.3") == {}
    assert _extract_chart_metadata_for_mathb4_32("P^{5}_{3}") == {}
