# -*- coding: utf-8 -*-
"""Focused test for vh_數學B4_LinearTransformationOfData multi-fill & single choice representation."""

from __future__ import annotations

import pytest
from agent_skills_v3.vh_數學B4_LinearTransformationOfData import generate, check


def test_src_3852_multi_fill_payload() -> None:
    for seed in [None, 0, 42, 100]:
        payload = generate(seed=seed, component_id="src_3852")
        assert payload["skill_id"] == "vh_數學B4_LinearTransformationOfData"
        assert payload["component_id"] == "src_3852"
        assert payload["presentation_mode"] == "multi_blank"
        assert payload["answer_type"] == "multi_part"
        assert payload["answer_shape"] == "multi_blank"
        assert len(payload["answer"]) == 6
        correct = payload["correct_answer"]
        check_res = check(correct, correct, question_payload=payload)
        assert check_res is True or (isinstance(check_res, dict) and check_res.get("overall_correct") is True)


def test_src_3853_multi_fill_payload() -> None:
    for seed in [None, 0, 42, 100]:
        payload = generate(seed=seed, component_id="src_3853")
        assert payload["skill_id"] == "vh_數學B4_LinearTransformationOfData"
        assert payload["component_id"] == "src_3853"
        assert payload["presentation_mode"] == "multi_blank"
        assert payload["answer_type"] == "multi_part"
        assert payload["answer_shape"] == "multi_blank"
        assert len(payload["answer"]) == 6
        correct = payload["correct_answer"]
        check_res = check(correct, correct, question_payload=payload)
        assert check_res is True or (isinstance(check_res, dict) and check_res.get("overall_correct") is True)


def test_src_3854_multi_fill_validation_20_seeds() -> None:
    for seed in range(20):
        payload = generate(seed=seed, component_id="src_3854")
        assert payload["skill_id"] == "vh_數學B4_LinearTransformationOfData"
        assert payload["component_id"] == "src_3854"
        assert payload["presentation_mode"] == "multi_blank"
        assert payload["answer_type"] == "multi_part"
        assert payload["answer_shape"] == "multi_blank"
        
        # Verify no missing formula in question text or explanation
        assert "[FORMULA_MISSING]" not in payload["question_text"]
        assert "[FORMULA_MISSING]" not in payload["explanation"]
        
        # Verify 6 blanks
        assert len(payload["answer"]) == 6
        assert len(payload["correct_answer"]) == 6
        assert len(payload["subquestions"]) == 6
        
        # Check that group labels in answer section do not contain formula/equations (only (1), (2), (3))
        for group in payload["ui_contract"]["field_groups"]:
            assert group["group_label"] in ["(1)", "(2)", "(3)"]
            
        correct = payload["correct_answer"]
        # Verify checker validates the correct answer successfully
        check_res = check(correct, correct, question_payload=payload)
        assert check_res is True or (isinstance(check_res, dict) and check_res.get("overall_correct") is True)


def test_src_3855_single_choice_validation_20_seeds() -> None:
    answer_labels_seen = set()
    for seed in range(20):
        payload = generate(seed=seed, component_id="src_3855")
        assert payload["skill_id"] == "vh_數學B4_LinearTransformationOfData"
        assert payload["component_id"] == "src_3855"
        assert payload["presentation_mode"] == "single_choice"
        assert payload["answer_type"] == "choice_label"
        assert payload["answer_shape"] == "single_choice"
        
        assert "[FORMULA_MISSING]" not in payload["question_text"]
        assert "[FORMULA_MISSING]" not in payload["explanation"]
        
        # Verify choices
        choices = payload["choices"]
        assert len(choices) == 4
        labels = [c["label"] for c in choices]
        assert labels == ["A", "B", "C", "D"]
        
        # Verify no duplicate choices
        choice_texts = [c["text"] for c in choices]
        assert len(set(choice_texts)) == 4
        
        # Verify correct answer and grading
        answer = payload["answer"]
        assert answer in ["A", "B", "C", "D"]
        answer_labels_seen.add(answer)
        
        # Verify checker
        check_res = check(answer, answer, question_payload=payload)
        assert check_res is True or (isinstance(check_res, dict) and check_res.get("overall_correct") is True)
        
        # Verify incorrect choices fail check
        for label in ["A", "B", "C", "D"]:
            if label != answer:
                check_res_inc = check(label, answer, question_payload=payload)
                assert check_res_inc is False or (isinstance(check_res_inc, dict) and check_res_inc.get("overall_correct") is False)

    # Verify randomized shuffling results in at least two different correct answer positions across 20 seeds
    assert len(answer_labels_seen) >= 2
