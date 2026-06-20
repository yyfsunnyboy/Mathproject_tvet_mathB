# -*- coding: utf-8 -*-
"""Tests for V3 source semantic fidelity gate."""

from __future__ import annotations

from core.gencode.services.v3_source_fidelity_service import verify_source_fidelity


def test_fidelity_success():
    classification = {
        "problem_type_id": "slope_from_general_form",
        "presentation_mode": "short_answer",
        "answer_type": "numeric_or_undefined",
    }
    metadata = {
        "PROBLEM_TYPE_ID": "slope_from_general_form",
        "PRESENTATION_MODE": "short_answer",
        "ANSWER_TYPE": "numeric_or_undefined",
    }
    res = verify_source_fidelity(classification, metadata)
    assert res["fidelity_passed"]
    assert len(res["errors"]) == 0


def test_fidelity_problem_type_mismatch():
    classification = {
        "problem_type_id": "slope_from_general_form",
        "presentation_mode": "short_answer",
        "answer_type": "numeric_or_undefined",
    }
    metadata = {
        "PROBLEM_TYPE_ID": "write_line_equation_from_point_slope",
        "PRESENTATION_MODE": "short_answer",
        "ANSWER_TYPE": "numeric_or_undefined",
    }
    res = verify_source_fidelity(classification, metadata)
    assert not res["fidelity_passed"]
    assert any("problem_type_id mismatch" in err for err in res["errors"])
    assert any("component leaked default point-slope fallback" in err for err in res["errors"])


def test_fidelity_presentation_mode_mismatch():
    classification = {
        "problem_type_id": "slope_from_general_form",
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
    }
    metadata = {
        "PROBLEM_TYPE_ID": "slope_from_general_form",
        "PRESENTATION_MODE": "short_answer",
        "ANSWER_TYPE": "single_choice",
    }
    res = verify_source_fidelity(classification, metadata)
    assert not res["fidelity_passed"]
    assert any("presentation_mode mismatch" in err for err in res["errors"])
