# -*- coding: utf-8 -*-
"""Regression: AbsoluteValueInequality must not emit table-less placeholder stems."""
from __future__ import annotations

import importlib

from core.domain.absolute_value_domain import build_absolute_value_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.generated_question_format_validator import validate_generated_question_format

SKILL = "vh_數學B1_AbsoluteValueInequality"
BAD_STEM = "閱讀下列資料，根據表格回答問題。"
PT = "absolute_value_inequality_integer_solution_count_choice"


def test_src_4499_integer_solution_count_has_real_stem_not_table_placeholder() -> None:
    mod = importlib.import_module(
        "agent_skills_v3.vh_數學B1_AbsoluteValueInequality.components.src_4499.generate"
    )
    for seed in range(20):
        q = mod.generate(level=1, seed=seed)
        qt = str(q.get("question_text") or "")
        assert qt, f"empty question_text seed={seed}"
        assert BAD_STEM not in qt
        assert "根據表格" not in qt
        assert "整數" in qt
        assert "\\left|" in qt or "| " in qt or "\\left|" in qt
        assert q.get("problem_type_id") == PT
        assert isinstance(q.get("choices"), list) and len(q["choices"]) == 4
        assert not q.get("table_data")
        errors = validate_generated_question_format(q, skill_id=SKILL)
        assert "stem_references_table_but_missing" not in errors


def test_adapter_integer_solution_count_builds_abs_inequality_stem() -> None:
    matrix = build_absolute_value_matrix(
        seed=1,
        line_type=PT,
        curriculum_profile="vocational_high_b",
        difficulty_profile="hard",
    )
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="choice",
        problem_type_id=PT,
        component_id="src_4499",
        textbook_example_id=4499,
        domain_operation=PT,
        seed=1,
    )
    qt = str(payload.get("question_text") or "")
    assert BAD_STEM not in qt
    assert "整數" in qt
    assert "\\left|" in qt
    givens = matrix["givens"]
    assert str(givens["a"]) in qt or (givens["a"] == 1 and "x" in qt)
    assert str(givens["c"]) in qt


def test_skill_generate_never_emits_table_placeholder() -> None:
    mod = importlib.import_module(f"skills.{SKILL}")
    observed_pts: set[str] = set()
    for seed in range(40):
        q = mod.generate(level=1, seed=seed)
        qt = str(q.get("question_text") or "")
        assert qt
        assert BAD_STEM not in qt
        assert "根據表格" not in qt
        pt = str(q.get("problem_type_id") or "")
        assert pt
        observed_pts.add(pt)
        if pt == PT:
            assert "整數" in qt
            assert "\\left|" in qt
            assert isinstance(q.get("choices"), list) and len(q["choices"]) >= 2
    assert PT in observed_pts
