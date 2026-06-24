# -*- coding: utf-8 -*-
"""Tests for V3 cross-component collapse gate."""

from __future__ import annotations

from core.gencode.services.v3_cross_component_audit_service import (
    calculate_ast_hash,
    extract_template_signature,
    check_cross_example_collapse,
)


def test_calculate_ast_hash_ignores_literals():
    code_a = """
def generate(seed=42):
    x = 10
    y = "hello"
    return {"question": f"x is {x}", "answer": y}
"""
    code_b = """
def generate(seed=42):
    x = 99
    y = "world"
    return {"question": f"x is {x}", "answer": y}
"""
    assert calculate_ast_hash(code_a) == calculate_ast_hash(code_b)


def test_extract_template_signature():
    sig1 = extract_template_signature("Find equation of line: 3x - 2y + 5 = 0")
    sig2 = extract_template_signature("Find equation of line: x + y - 1 = 0")
    assert sig1 == sig2

    sig3 = extract_template_signature("Point A(2, 3) is given")
    sig4 = extract_template_signature("Point A(-5, 0) is given")
    assert sig3 == sig4


def test_single_problem_type_is_review_signal_not_collapse():
    components = [
        {
            "textbook_example_id": 1,
            "problem_type_id": "point_slope",
            "generate_code": "def generate(): pass",
            "sample_question_text": "find a line through a point",
        },
        {
            "textbook_example_id": 2,
            "problem_type_id": "point_slope",
            "generate_code": "def generate(): pass",
            "sample_question_text": "read a slope from a graph",
        },
    ]
    res = check_cross_example_collapse(components)
    assert not res["collapse_detected"]
    assert any("cross_example_semantic_collapse" in r for r in res["reasons"])


def test_collapse_detected_when_single_template_signature():
    components = [
        {
            "textbook_example_id": 1,
            "problem_type_id": "type_a",
            "generate_code": "def run_a(): pass",
            "sample_question_text": "Find equation of line: 3x - 2y + 5 = 0",
        },
        {
            "textbook_example_id": 2,
            "problem_type_id": "type_b",
            "generate_code": "def run_b(): pass",
            "sample_question_text": "Find equation of line: x + y - 1 = 0",
        },
    ]
    res = check_cross_example_collapse(components)
    assert res["collapse_detected"]
    assert any("template signature detected" in r for r in res["reasons"])


def test_no_collapse_when_diverse():
    components = [
        {
            "textbook_example_id": 1,
            "problem_type_id": "type_a",
            "generate_code": "def run_a(): return 1",
            "sample_question_text": "question one",
        },
        {
            "textbook_example_id": 2,
            "problem_type_id": "type_b",
            "generate_code": "class RunB:\n    def get(self): return 2",
            "sample_question_text": "question two",
        },
    ]
    res = check_cross_example_collapse(components)
    assert not res["collapse_detected"]
    assert res["metrics"]["unique_problem_type_count"] == 2
    assert res["metrics"]["unique_ast_hash_count"] == 2
