# -*- coding: utf-8 -*-
from core.gencode.problem_type_canonicalizer import (
    MATH_META_TAG_APPLIED_CONTEXT,
    MATH_META_TAG_PARAMETER_RANGE,
    MATH_META_TAG_REVERSE_VIETA,
    MATH_META_TAG_SPECIAL_CASES_D_NEG,
    extract_math_meta_tags,
    resolve_target_task_from_math_meta_tags,
)
from core.gencode.example_feature_extractor import extract_example_feature_rule_only


def test_extract_special_case_d_negative():
    stem = "解不等式 x^2+x+5>0（判別式 D<0），解為任意實數"
    tags = extract_math_meta_tags(stem)
    assert MATH_META_TAG_SPECIAL_CASES_D_NEG in tags
    assert resolve_target_task_from_math_meta_tags(tags) == "solve_quadratic_inequality_special_cases"


def test_extract_special_case_parameter_range():
    stem = "若 kx^2+2x+3>0 對於任意實數 x 均成立，求 k 的範圍"
    tags = extract_math_meta_tags(stem)
    assert MATH_META_TAG_PARAMETER_RANGE in tags
    assert resolve_target_task_from_math_meta_tags(tags) == "solve_quadratic_inequality_parameter_range"


def test_extract_applied_profit_keywords():
    stem = "某商品成本與收入滿足利润模型，求 x 使利润大于 0"
    tags = extract_math_meta_tags(stem)
    assert MATH_META_TAG_APPLIED_CONTEXT in tags
    assert resolve_target_task_from_math_meta_tags(tags) == "applied_quadratic_inequality_problem"


def test_extract_reverse_vieta():
    stem = "若不等式 ax^2+bx+c<0 的解為 -2<x<5，求 a+b 的值"
    tags = extract_math_meta_tags(stem)
    assert MATH_META_TAG_REVERSE_VIETA in tags
    assert resolve_target_task_from_math_meta_tags(tags) == "reverse_quadratic_inequality_coefficients"


def test_extract_applied_context():
    stem = "已知三角形三邊長為 x、x+1 與 7，求 x 的範圍使三邊能構成三角形"
    tags = extract_math_meta_tags(stem)
    assert MATH_META_TAG_APPLIED_CONTEXT in tags
    assert resolve_target_task_from_math_meta_tags(tags) == "applied_quadratic_inequality_problem"


def test_rule_feature_forced_target_task():
    ex = {
        "example_id": 1,
        "question": "若不等式 ax^2+bx+1<0 的解為 1<x<4，求 a 之值",
        "answer": "2",
    }
    feat = extract_example_feature_rule_only(ex)
    assert feat["forced_target_task"] == "reverse_quadratic_inequality_coefficients"
    assert feat["target_task"] == "reverse_quadratic_inequality_coefficients"

def test_parameter_range_hint_never_leaks_dynamic_answer():
    from core.gencode.answer_contract_policy import build_quadratic_inequality_parameter_range_contract
    from core.gencode.answer_format_hint import (
        QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE,
        answer_format_example_for_contract,
        build_answer_format_suffix,
    )

    ac = build_quadratic_inequality_parameter_range_contract()
    assert answer_format_example_for_contract(ac) == QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE
    assert build_answer_format_suffix(ac) == f"（答案範例：{QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE}）"
    leaked = dict(ac)
    leaked["answer_format_example"] = "k<-3"
    assert answer_format_example_for_contract(leaked) == QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE

    from core.gencode.answer_contract_policy import build_quadratic_inequality_special_case_contract
    from core.gencode.answer_format_hint import (
        answer_format_example_for_contract,
        build_answer_format_suffix,
    )

    ac = build_quadratic_inequality_special_case_contract()
    assert answer_format_example_for_contract(ac) == QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE
    assert build_answer_format_suffix(ac) == f"（答案範例：{QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE}）"

    leaked = dict(ac)
    leaked["answer_format_example"] = "無解"
    assert answer_format_example_for_contract(leaked) == QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE
