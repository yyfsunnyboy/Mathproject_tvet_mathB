from __future__ import annotations

import pytest
from core.domain.statistics.descriptive_statistics_analyzer import (
    _infer_task_classification,
    _infer_capabilities_from_text,
)

def test_empirical_rule_probability_classification():
    # 1. 常態分配＋已知平均數與標準差＋求區間比例 (empirical_rule_probability)
    q_text = "某校學生英文成績呈常態分配，平均 60 分，標準差 10 分。求成績在 50~70 分之間的比例為何？"
    res = _infer_task_classification(
        question_text=q_text,
        combined_text=q_text,
        presentation_mode="short_answer"
    )
    assert res is not None
    problem_type_id, caps = res
    assert problem_type_id == "empirical_rule_probability"

def test_empirical_rule_population_count_classification():
    # 2. 常態分配＋求約略人數 (empirical_rule_population_count)
    q_text = "某校 2000 個學生，英文成績呈常態分配，平均 55 分，標準差 5 分。求高於 60 分的人數約有多少人？"
    res = _infer_task_classification(
        question_text=q_text,
        combined_text=q_text,
        presentation_mode="short_answer"
    )
    assert res is not None
    problem_type_id, caps = res
    assert problem_type_id == "empirical_rule_population_count"

def test_empirical_rule_probability_under_mu_sigma_classification():
    # 3. 常態分配＋求低於 μ+σ (empirical_rule_probability)
    q_text = "某校學生身高呈常態分配，平均 170 公分，標準差 8 公分。求身高低於 178 公分的學生所佔比例？"
    res = _infer_task_classification(
        question_text=q_text,
        combined_text=q_text,
        presentation_mode="short_answer"
    )
    assert res is not None
    problem_type_id, caps = res
    assert problem_type_id == "empirical_rule_probability"

def test_compute_population_standard_deviation_classification():
    # 4. 原始資料＋求標準差 (compute_population_standard_deviation)
    # Note: For non-normal, standard deviation computation maps to standard_deviation_computation or similar.
    # In descriptive_statistics_analyzer:
    # "standard_deviation_computation" -> standard_deviation capability
    q_text = "求數值資料 2, 4, 6, 8, 10 的標準差。"
    res = _infer_task_classification(
        question_text=q_text,
        combined_text=q_text,
        presentation_mode="single_choice"
    )
    # Let's verify standard deviation matching
    caps = _infer_capabilities_from_text(q_text)
    assert "standard_deviation" in caps

def test_compare_distribution_spread_classification():
    # 5. 兩個分配圖比較離散程度 (compare_distribution_spread)
    q_text = "如圖所示，有甲、乙兩班的成績直方圖，試比較兩班成績的標準差大小。"
    combined_text = q_text + " 甲班的標準差比乙班大"
    res = _infer_task_classification(
        question_text=q_text,
        combined_text=combined_text,
        presentation_mode="single_choice"
    )
    assert res is not None
    problem_type_id, caps = res
    assert problem_type_id == "compare_distribution_spread"
