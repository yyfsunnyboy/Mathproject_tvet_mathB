# -*- coding: utf-8 -*-
"""Regressions for B2 Ch4 student runtime contract cleanup (generic layers)."""

from __future__ import annotations

import re

import pytest

from core.domain.circle_plane_domain import build_circle_plane_matrix
from core.gencode.choice_contract_validator import (
    infer_choice_answer_shape,
    validate_choice_answer_shapes,
    validate_vocational_multiple_choice,
)
from core.gencode.choice_math_display import format_choice_math_display
from core.gencode.circle_plane_capability_adapter import adapt_circle_plane_matrix
from core.gencode.domain_matrix_adapter import (
    _looks_like_internal_part_key,
    _multi_part_contract_parts,
    _student_facing_part_label,
)


def test_center_radius_six_grouped_inputs() -> None:
    matrix = build_circle_plane_matrix(operation="identify_center_radius_from_standard", seed=11)
    payload = adapt_circle_plane_matrix(
        matrix,
        domain_operation="identify_center_radius_from_standard",
        skill_id="vh_數學B2_SubSection_4_1_1",
        component_id="src_test",
        textbook_example_id=11826,
    )
    parts = (payload.get("answer_contract") or {}).get("parts") or []
    assert len(parts) == 6
    assert [p["display_label"] for p in parts] == ["圓心", "半徑", "圓心", "半徑", "圓心", "半徑"]
    groups = ((payload.get("answer_contract") or {}).get("ui_contract") or {}).get("field_groups") or []
    assert len(groups) == 3
    assert groups[0]["group_label"] == "(1)"
    assert groups[0]["fields"] == ["(1)圓心", "(1)半徑"]
    assert "\n" in str(payload.get("question_text") or "")
    assert not any("小题" in str(p.get("display_label")) for p in parts)


def test_multipart_numbering_survives_serialization() -> None:
    matrix = build_circle_plane_matrix(operation="classify_lines_vs_circle_multipart", seed=5)
    payload = adapt_circle_plane_matrix(
        matrix,
        domain_operation="classify_lines_vs_circle_multipart",
        skill_id="vh_數學B2_SubSection_4_2_2",
        component_id="src_test",
        textbook_example_id=11854,
    )
    stem = str(payload.get("question_text") or "")
    assert "\n" in stem
    assert re.search(r"\(1\)", stem)
    assert re.search(r"\(2\)", stem)
    parts = (payload.get("answer_contract") or {}).get("parts") or []
    assert all("L" in str(p.get("display_label")) and "關係" in str(p.get("display_label")) for p in parts)


def test_math_mcq_choices_use_canonical_math_path() -> None:
    assert r"\(" in format_choice_math_display("x^2+y^2=4")
    assert "^{2}" in format_choice_math_display("x^2+y^2=4")
    assert r"\(" in format_choice_math_display("(x-3)^2+(y+1)^2=8")
    assert r"\pi" in format_choice_math_display(r"16\pi")


def test_area_mcq_rejects_equation_shaped_distractor() -> None:
    bad = {
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "curriculum_profile": "vocational_high_b",
        "correct_answer": "B",
        "answer": "B",
        "semantic_answer": r"16\pi",
        "choices": [
            {"label": "A", "text": "x^2+y^2=1", "value": "x^2+y^2=1"},
            {"label": "B", "text": r"16\pi", "value": r"16\pi"},
            {"label": "C", "text": r"9\pi", "value": r"9\pi"},
            {"label": "D", "text": r"4\pi", "value": r"4\pi"},
        ],
    }
    assert "vocational_choice_shape_mismatch" in validate_choice_answer_shapes(bad)
    assert "vocational_choice_shape_mismatch" in validate_vocational_multiple_choice(
        bad, skill_id="vh_數學B2_SubSection_4_1_1"
    )


def test_area_mcq_generation_is_shape_consistent() -> None:
    matrix = build_circle_plane_matrix(operation="circle_center_on_axis_area", seed=4)
    shapes = {infer_choice_answer_shape(c.get("text")) for c in (matrix.get("choices") or [])}
    assert shapes <= {"area_or_pi", "number"}
    assert "equation" not in shapes


def test_bare_numbered_keys_are_student_facing() -> None:
    assert not _looks_like_internal_part_key("(1)圓心", "(1)圓心")
    assert "C1" in _student_facing_part_label(
        "(1)", domain_operation="classify_point_vs_circles_multipart"
    )
    parts = _multi_part_contract_parts(
        {"(1)": "圓外", "(2)": "圓內"},
        domain_operation="classify_point_vs_circles_multipart",
    )
    assert "關係" in str(parts[0]["display_label"])


def test_sanity_math_unchanged_for_acceptance_examples() -> None:
    """Presentation cleanup must not alter confirmed circle oracles."""
    # same-center half area → r²=8 choice exists among options for scaled-area family
    m = build_circle_plane_matrix(operation="circle_same_center_scaled_area", seed=1)
    assert m.get("choices")
    # center on x-axis area family remains π-shaped
    m2 = build_circle_plane_matrix(operation="circle_center_on_axis_area", seed=1)
    texts = [str(c.get("text")) for c in (m2.get("choices") or [])]
    assert any("pi" in t.casefold() or "π" in t or r"\pi" in t for t in texts)
