# -*- coding: utf-8 -*-
"""Chapter 4 calculator-required questions are legal skips, not parse failures."""

from core.mathb_chapter4_calculator_skip import (
    CALCULATOR_KEY_SKILL_ID,
    chapter4_calculator_skip,
    chapter4_corpus_acceptance,
    is_b3_chapter4,
    keeps_formal_skill_when_source_count_is_zero,
    question_requires_calculator,
    replacement_counts_match,
)

_B3_CH4 = {"curriculum": "vocational", "volume": "數學B3", "chapter_index": 4}


def test_calculator_key_and_log_key_questions_skip():
    assert question_requires_calculator("用計算機求 log1.543 的值")
    assert question_requires_calculator("在計算機上輸入 1.543，可得到 0.185825359")
    assert question_requires_calculator("先按 log 鍵，再輸入 2.37")
    assert question_requires_calculator("若無法查表，利用計算機求 log2 的近似值")


def test_textbook_hand_methods_stay_importable():
    assert not question_requires_calculator("求 log_2 8 的值")
    assert not question_requires_calculator("已知 log2 與 log3，利用對數性質求 log12")
    assert not question_requires_calculator("利用換底公式求 log_3 27 的值")
    assert not question_requires_calculator("試利用對數表查出下列對數的近似值：log4.58")
    assert not question_requires_calculator("設 logx 約 2.5888，試求 logx 之首數與尾數。x 之整數部分為幾位數？")
    assert not question_requires_calculator("求 log_2 8，可以計算機驗證答案")
    assert not question_requires_calculator("不要使用計算機，利用對數性質求值")
    assert not question_requires_calculator("試利用對數表查出，或使用計算機求 log4.58")


def test_self_assessment_skip_keeps_source_label():
    record = chapter4_calculator_skip(
        {**_B3_CH4, "source_scope": "chapter_self_assessment"},
        "使用計算機的 log 鍵求 log2.37 的近似值",
        "CH4自我評量 題7",
    )
    assert record == {
        "source_label": "CH4自我評量 題7",
        "skip_reason": "calculator_required",
    }


def test_other_chapters_do_not_skip():
    info = {"curriculum": "vocational", "volume": "數學B2", "chapter_index": 4}
    assert not is_b3_chapter4(info)
    assert chapter4_calculator_skip(info, "用計算機求值", "例1") is None
    assert not is_b3_chapter4({"curriculum": "vocational", "volume": "數學B3", "section_code": "3-2"})


def test_corpus_counts_legitimate_skips():
    accepted = chapter4_corpus_acceptance(
        parsed_source_questions=28,
        imported_questions=27,
        legitimate_calculator_required_skips=1,
    )
    assert accepted["balanced"]
    assert accepted["calculator_required_skipped"] == 1
    assert accepted["parsed_source_questions"] == (
        accepted["imported_questions"] + accepted["legitimate_calculator_required_skips"]
    )
    gap = chapter4_corpus_acceptance(
        parsed_source_questions=28,
        imported_questions=26,
        legitimate_calculator_required_skips=1,
    )
    assert not gap["balanced"]


def test_calculator_skill_with_zero_questions_stays_legal():
    assert keeps_formal_skill_when_source_count_is_zero(CALCULATOR_KEY_SKILL_ID, 0)
    assert CALCULATOR_KEY_SKILL_ID == "vh_數學B3_SubSection_4_5_2"
    assert replacement_counts_match(inserted=0, updated=0, parsed=0, calculator_required_skipped=0)
    assert replacement_counts_match(inserted=27, updated=0, parsed=28, calculator_required_skipped=1)
    assert not replacement_counts_match(inserted=27, updated=0, parsed=28, calculator_required_skipped=0)
