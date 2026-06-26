# -*- coding: utf-8 -*-
"""Tests for single_choice stem / choices separation."""

from __future__ import annotations

from core.gencode.choice_contract_validator import validate_choice_contract
from core.gencode.single_choice_payload_normalizer import normalize_single_choice_payload
from core.gencode.v3_presentation_inference import (
    has_abcd_choice_group,
    split_question_stem_and_abcd_choices,
)


PROBLEM_3891 = (
    "甲同學想要網購某支特定手機，上網逛了7家購物網站後，告訴好友說：「該款手機的價差在100元以內」。"
    "試問甲所說的話中，應用了下列哪一種統計量？"
    " (A)四分位距 (B)全距 (C)標準差 (D)算術平均數。"
)

PROBLEM_3892 = (
    "阿德期末考5科的成績分別為87分、75分、78分、79分、81分，"
    "則此成績的母體標準差為 (A) 4分 (B) 5分 (C) 6分 (D) 7分。"
)


def test_split_stem_3891() -> None:
    stem, choices, source = split_question_stem_and_abcd_choices(PROBLEM_3891)
    assert stem.endswith("應用了下列哪一種統計量？")
    assert "(A)" not in stem
    assert len(choices) == 4
    assert choices[0]["key"] == "A"
    assert choices[1]["text"] == "全距"
    assert source == PROBLEM_3891


def test_split_stem_3892() -> None:
    stem, choices, source = split_question_stem_and_abcd_choices(PROBLEM_3892)
    assert stem.endswith("則此成績的母體標準差為")
    assert "(A)" not in stem
    assert len(choices) == 4
    assert source == PROBLEM_3892


def test_multi_part_not_detected_as_abcd_group() -> None:
    assert not has_abcd_choice_group("（1）求平均數。（2）求全距。")


def test_normalize_strips_embedded_choices_when_canonical_present() -> None:
    payload = {
        "presentation_mode": "single_choice",
        "question_text": PROBLEM_3891,
        "answer": "B",
        "checker_key": "choice_label_checker",
        "choices": [
            {"key": "A", "text": "四分位距"},
            {"key": "B", "text": "全距"},
            {"key": "C", "text": "標準差"},
            {"key": "D", "text": "算術平均數"},
        ],
        "answer_contract": {
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "checker_key": "choice_label_checker",
        },
    }
    out = normalize_single_choice_payload(payload)
    assert out["question_text"].endswith("應用了下列哪一種統計量？")
    assert "(A)" not in out["question_text"]
    assert out["source_problem_text"] == PROBLEM_3891
    assert len(out["choices"]) == 4
    result = validate_choice_contract(out)
    assert result["ok"] is True


def test_embedded_choices_blocked_then_normalized() -> None:
    payload = {
        "presentation_mode": "single_choice",
        "question_text": PROBLEM_3892,
        "answer": "A",
        "checker_key": "choice_label_checker",
        "choices": [
            {"key": "A", "text": "4分"},
            {"key": "B", "text": "5分"},
            {"key": "C", "text": "6分"},
            {"key": "D", "text": "7分"},
        ],
        "answer_contract": {
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "checker_key": "choice_label_checker",
        },
    }
    dirty = dict(payload)
    result = validate_choice_contract(dirty)
    assert result["ok"] is False
    assert any("choices_embedded_in_question_text" in b for b in result["blockers"])

    clean = normalize_single_choice_payload(dirty)
    result2 = validate_choice_contract(clean)
    assert result2["ok"] is True
    assert clean["question_text"].endswith("則此成績的母體標準差為")
