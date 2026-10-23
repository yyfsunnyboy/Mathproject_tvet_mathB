"""Focused ordering checks for textbook chapter and unit selectors."""

from core.utils import chapter_natural_sort_key


def test_unit_and_chapter_numbers_sort_numerically():
    units = [f"單元{i} 名稱{i}" for i in range(12, 0, -1)]
    chapters = [f"第{i}章 名稱{i}" for i in range(12, 0, -1)]
    assert sorted(units, key=chapter_natural_sort_key) == units[::-1]
    assert sorted(chapters, key=chapter_natural_sort_key) == chapters[::-1]


def test_nested_numbers_and_unknown_label_fallback():
    labels = ["第2章 1-11", "附錄", "第2章 1-3", "第1章 2-1"]
    assert sorted(labels, key=chapter_natural_sort_key) == [
        "第1章 2-1", "第2章 1-3", "第2章 1-11", "附錄",
    ]
