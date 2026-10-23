from __future__ import annotations

import sqlite3
from pathlib import Path

from core.utils import textbook_skill_sort_key

DB = Path(__file__).resolve().parents[1] / "instance" / "kumon_math.db"


def _row(paragraph, order, name="x"):
    return {"paragraph": paragraph, "display_order": order, "skill_ch_name": name}


def test_paragraph_mark_beats_display_order_and_unmarked_fall_back_stably():
    rows = [_row("己.不等式", 1), _row("乙.方程式", 9), _row("甲.斜率", 5), _row("相異物的排列", 2, "b"), _row("樹狀圖", 2, "a"), _row("丁、向量", 3)]
    assert [r["paragraph"] for r in sorted(rows, key=textbook_skill_sort_key)] == ["甲.斜率", "乙.方程式", "丁、向量", "己.不等式", "樹狀圖", "相異物的排列"]


def test_real_curriculum_orders():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        def order(chapter):
            rows = con.execute("select paragraph, display_order, skill_id from skill_curriculum where curriculum='general' and volume='數學1' and chapter=?", (chapter,)).fetchall()
            return [r["paragraph"][0] for r in sorted(({"paragraph": p, "display_order": d, "skill_ch_name": s} for p, d, s in rows), key=textbook_skill_sort_key)]

        assert order("單元5 直線方程式") == list("甲乙丙丁戊己")
        assert order("單元3 指數") == list("甲乙丙丁")
        assert order("單元4 科學記號與常用對數") == list("甲乙")
        voc = con.execute("select skill_id, display_order, paragraph from skill_curriculum where curriculum='vocational' and volume='數學B1' limit 50").fetchall()
        for chapter_rows in [voc]:
            keys = sorted(({"paragraph": p, "display_order": d, "skill_ch_name": s} for s, d, p in chapter_rows), key=textbook_skill_sort_key)
            assert [k["display_order"] for k in keys] == sorted(k["display_order"] for k in keys)  # no marks -> display_order kept
    finally:
        con.close()


def test_general_math1_units_1_to_5_follow_textbook_marks():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        expected = {"單元1 實數": "甲乙丙丁", "單元2 絕對值": "甲乙丙", "單元3 指數": "甲乙丙丁", "單元4 科學記號與常用對數": "甲乙", "單元5 直線方程式": "甲乙丙丁戊己"}
        for chapter, marks in expected.items():
            rows = [
                {"paragraph": p, "display_order": d, "skill_ch_name": s}
                for p, d, s in con.execute(
                    "select sc.paragraph, sc.display_order, si.skill_ch_name from skill_curriculum sc join skills_info si on si.skill_id=sc.skill_id "
                    "where sc.curriculum='general' and sc.volume='數學1' and sc.chapter=? and si.is_active=1", (chapter,))
            ]
            assert "".join(r["paragraph"][0] for r in sorted(rows, key=textbook_skill_sort_key)) == marks, chapter
    finally:
        con.close()


def test_import_keeps_marker_in_paragraph_even_when_only_the_name_had_it():
    from core.textbook_processor import general_high_paragraph_with_marker as keep

    assert keep("己 二元一次不等式", "未提供內容") == "己.二元一次不等式"
    assert keep("二元一次不等式", "己.二元一次不等式") == "己.二元一次不等式"
    assert keep("乙.圓的一般式", "圓一般式說明文字") == "乙.圓一般式說明文字"
    assert keep("沒有標記", "也沒有標記") == "也沒有標記"  # stays unmarked -> display_order fallback + warning at import
