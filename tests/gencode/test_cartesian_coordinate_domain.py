# -*- coding: utf-8 -*-
from __future__ import annotations

import pytest
from core.domain.coordinate_geometry.cartesian_coordinate_domain import build_cartesian_coordinate_matrix

def _test_build(cond: str, x: str, y: str) -> dict:
    return build_cartesian_coordinate_matrix(
        seed=42,
        domain_operation="cartesian_coordinate_quadrant_symbol_reasoning",
        constraints={
            "variable_conditions": cond,
            "x_expression": x,
            "y_expression": y,
        }
    )

def test_cartesian_coordinate_domain_cases() -> None:
    # Case 1: a < b 且已知正負號 (a > 0, b > 0) -> a - b 是負，a**2*b 是正 -> 第二象限
    res = _test_build("a > 0, b > 0, a < b", "a - b", "a**2 * b")
    assert res["answer"]["canonical_form"] == "第二象限"
    assert res["validation_facts"]["x_sign"] == "-"
    assert res["validation_facts"]["y_sign"] == "+"

    # Case 2: a < b < 0 -> ab 是正，a+b 是負 -> 第四象限
    res = _test_build("a < b < 0", "a * b", "a + b")
    assert res["answer"]["canonical_form"] == "第四象限"
    assert res["validation_facts"]["x_sign"] == "+"
    assert res["validation_facts"]["y_sign"] == "-"
    
    # Case 3: x > 0, y > 0 -> 第一象限
    res = _test_build("x > 0, y > 0", "x", "y")
    assert res["answer"]["canonical_form"] == "第一象限"

    # Case 4: x < 0, y > 0 -> 第二象限
    res = _test_build("x < 0, y > 0", "x", "y")
    assert res["answer"]["canonical_form"] == "第二象限"

    # Case 5: x < 0, y < 0 -> 第三象限
    res = _test_build("x < 0, y < 0", "x", "y")
    assert res["answer"]["canonical_form"] == "第三象限"

    # Case 6: x > 0, y < 0 -> 第四象限
    res = _test_build("x > 0, y < 0", "x", "y")
    assert res["answer"]["canonical_form"] == "第四象限"

    # Case 7: 其中一個座標為 0 -> 不屬於任何象限 (ValueError)
    with pytest.raises(ValueError, match="unresolved_quadrant_signs"):
        _test_build("x == 0, y > 0", "x", "y")
        
    with pytest.raises(ValueError, match="unresolved_quadrant_signs"):
        _test_build("x > 0, y == 0", "x", "y")

    # Case 8: 條件不足 (只知 a < b) -> unresolved (ValueError)
    with pytest.raises(ValueError, match="unresolved_quadrant_signs"):
        _test_build("a < b", "a - b", "a * b")

    # Case 9: 平方項恆非負，且已知 a != 0 -> 正
    res = _test_build("a < 0", "a**2", "-a")
    assert res["answer"]["canonical_form"] == "第一象限"

    # Case 10: 不合法或無法解析的 expression -> fail-fast
    with pytest.raises(Exception):
        _test_build("a > 0", "a + @", "a")
