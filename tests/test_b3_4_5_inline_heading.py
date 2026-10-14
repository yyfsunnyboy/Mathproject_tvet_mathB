# -*- coding: utf-8 -*-
"""4-5.2 keeps its audited heading when the LaTeX title contains the log key."""

from core.mathb_concept_heading import (
    detect_mathb_concept_heading,
    reconcile_inline_formula_heading,
)

_CANDIDATES = [
    {"concept_code": "4-5.1", "concept_name": "常用對數表的使用"},
    {"concept_code": "4-5.2", "concept_name": "使用計算機鍵"},
    {"concept_code": "4-5.3", "concept_name": "首數、尾數及其應用"},
]


def test_latex_log_key_reconciles_to_the_audited_heading():
    line = r"4-5.2使用計算機\(\boxed{ log }\)鍵"
    assert detect_mathb_concept_heading(line, current_section_code="4-5") is None
    hit = reconcile_inline_formula_heading(
        line, current_section_code="4-5", candidates=_CANDIDATES
    )
    assert hit["concept_code"] == "4-5.2"
    assert hit["concept_name"] == "使用計算機鍵"


def test_inline_formula_does_not_invent_a_heading():
    line = r"4-5.2\(x=1\)"
    assert (
        reconcile_inline_formula_heading(
            line, current_section_code="4-5", candidates=_CANDIDATES
        )
        is None
    )


def test_plain_numbered_heading_stays_on_the_detector():
    line = "4-5.1常用對數表的使用"
    assert reconcile_inline_formula_heading(
        line, current_section_code="4-5", candidates=_CANDIDATES
    ) is None
    assert detect_mathb_concept_heading(line, current_section_code="4-5")["concept_code"] == "4-5.1"


def test_exercises_bind_to_one_audited_heading():
    from core.textbook_structural_metadata import unique_common_log_exercise_heading

    table = "試利用對數表查出下列對數的近似值： (1) log4.58"
    characteristic = "設 logx 約 2.5888，試求 logx 之首數與尾數。 x之整數部分為幾位數？"
    inverse = "已知 log2950 約 3.4698，若 logN=-2.5302，試求N之值。"
    years = "試問幾年後，媽媽在銀行存款的本利和會超過30萬元？"
    assert unique_common_log_exercise_heading(table, _CANDIDATES)["concept_code"] == "4-5.1"
    assert unique_common_log_exercise_heading(characteristic, _CANDIDATES)["concept_code"] == "4-5.3"
    assert unique_common_log_exercise_heading(inverse, _CANDIDATES)["concept_code"] == "4-5.3"
    assert unique_common_log_exercise_heading(years, _CANDIDATES)["concept_code"] == "4-5.3"
    assert unique_common_log_exercise_heading("用計算機求值", _CANDIDATES)["concept_code"] == "4-5.2"
