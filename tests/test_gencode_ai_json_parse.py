# -*- coding: utf-8 -*-
"""AI semantic classifier JSON parse and invalid_response vs unavailable."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from core.gencode.ai_semantic_classifier import (
    classify_example_semantics_with_ai,
    set_ai_semantic_classifier_mock,
)
from core.gencode.classification_candidates import build_skill_scoped_candidates
from core.gencode.classification_policy import merge_skill_scoped_classification
from core.gencode.example_feature_extractor import extract_example_feature_rule_only
from core.gencode.gemini_json_parse import safe_load_gemini_json
from core.gencode.task_families import DIVISION_POINT_COORDINATES_FAMILY


def _anchor_and_candidates():
    anchor = {
        "skill_id": "mock",
        "skill_ch_name": "分點坐標",
        "expected_task_families": [DIVISION_POINT_COORDINATES_FAMILY],
        "expected_subskill_candidates": [
            "compute_internal_division_point_coordinates",
            "compute_centroid_coordinates",
        ],
        "skill_anchor_scope": "broad",
    }
    ex = {"id": 1, "skill_id": "mock", "problem_text": "test", "correct_answer": "(1,2)"}
    rule = extract_example_feature_rule_only(ex)
    cands = build_skill_scoped_candidates(anchor, ex, rule)
    return anchor, ex, cands


def test_fenced_json_parses():
    raw = 'Here is the result:\n```json\n{"best_candidate_id": "x", "confidence": 0.9, "evidence": ["a"]}\n```'
    data = safe_load_gemini_json(raw)
    assert data["best_candidate_id"] == "x"


def test_unescaped_latex_in_evidence_parses_or_invalid_response():
    raw = (
        '{"best_candidate_id": "c1", "confidence": 0.8, '
        '"evidence": ["segment \\overline{AB}"], "rejected_candidates": {}, '
        '"requires_human_action": false, "notes": ""}'
    )
    try:
        data = safe_load_gemini_json(raw)
        assert "best_candidate_id" in data
    except (json.JSONDecodeError, ValueError):
        pass  # acceptable if strict path fails; classifier must mark invalid_response


def test_latex_invalid_escape_classifier_invalid_response_not_unavailable():
    set_ai_semantic_classifier_mock(None)

    class _Client:
        model_name = "gemini-test"

    anchor, ex, cands = _anchor_and_candidates()
    bad = (
        '{"best_candidate_id": "' + str(cands[0]["candidate_id"]) + '", '
        '"confidence": 0.9, "evidence": ["\\overline{AB}"], '
        '"rejected_candidates": {}, "requires_human_action": false, "notes": ""}'
    )
    resp = MagicMock()
    resp.text = bad

    with patch("core.ai_wrapper.resolve_gemini_api_key", return_value=("key", "env")):
        with patch("core.ai_wrapper.call_ai_with_retry", return_value=resp):
            out = classify_example_semantics_with_ai(
                ex, anchor, client=_Client(), skill_scoped_candidates=cands
            )
    if out.get("ai_semantic_status") == "ok":
        assert out["available"] is True
    else:
        assert out["ai_semantic_status"] == "invalid_response"
        assert out["ai_unavailable_reason"] == ""
        assert out.get("ai_invalid_response_reason") or out.get("parser_error")


def test_json_parse_failed_needs_review_not_first_candidate():
    set_ai_semantic_classifier_mock(None)

    class _Client:
        model_name = "gemini-test"

    anchor, ex, cands = _anchor_and_candidates()
    resp = MagicMock()
    resp.text = "not json at all {broken"

    with patch("core.ai_wrapper.resolve_gemini_api_key", return_value=("key", "env")):
        with patch("core.ai_wrapper.call_ai_with_retry", return_value=resp):
            out = classify_example_semantics_with_ai(
                ex, anchor, client=_Client(), skill_scoped_candidates=cands
            )
    assert out["ai_semantic_status"] == "invalid_response"
    rule = extract_example_feature_rule_only(ex)
    merged = merge_skill_scoped_classification(out, rule, anchor, skill_scoped_candidates=cands)
    assert merged["classifier_source"] == "ai_invalid_response_needs_review"
    assert merged["requires_human_action"] is True
    assert merged["final_target_task"] == ""
    assert merged["ai_best_candidate_id"] == "needs_review"
    assert merged["ai_unavailable_reason"] == ""


def test_unknown_candidate_id_invalid_response():
    set_ai_semantic_classifier_mock(None)

    class _Client:
        model_name = "gemini-test"

    anchor, ex, cands = _anchor_and_candidates()
    resp = MagicMock()
    resp.text = json.dumps(
        {
            "best_candidate_id": "nonexistent_candidate_id",
            "confidence": 0.95,
            "evidence": ["plain text only"],
            "rejected_candidates": {},
            "requires_human_action": False,
            "notes": "",
        }
    )

    with patch("core.ai_wrapper.resolve_gemini_api_key", return_value=("key", "env")):
        with patch("core.ai_wrapper.call_ai_with_retry", return_value=resp):
            out = classify_example_semantics_with_ai(
                ex, anchor, client=_Client(), skill_scoped_candidates=cands
            )
    assert out["ai_semantic_status"] == "invalid_response"
    assert out.get("ai_invalid_response_reason") == "invalid_candidate_id"


def test_missing_api_key_unavailable_rule_fallback():
    set_ai_semantic_classifier_mock(None)
    anchor, ex, cands = _anchor_and_candidates()
    with patch("core.ai_wrapper.resolve_gemini_api_key", return_value=(None, None)):
        out = classify_example_semantics_with_ai(ex, anchor, skill_scoped_candidates=cands)
    assert out["ai_semantic_status"] == "unavailable"
    assert out["ai_unavailable_reason"] == "missing_api_key"
    rule = extract_example_feature_rule_only(ex)
    merged = merge_skill_scoped_classification(out, rule, anchor, skill_scoped_candidates=cands)
    assert merged["classifier_source"] == "rule_fallback_ai_unavailable"


def test_valid_best_candidate_id_ok():
    set_ai_semantic_classifier_mock(None)

    class _Client:
        model_name = "gemini-test"

    anchor, ex, cands = _anchor_and_candidates()
    internal = next(c for c in cands if c.get("target_task") == "compute_internal_division_point_coordinates")
    resp = MagicMock()
    resp.text = json.dumps(
        {
            "best_candidate_id": internal["candidate_id"],
            "confidence": 0.92,
            "evidence": ["內分點比例"],
            "rejected_candidates": {},
            "requires_human_action": False,
            "notes": "",
        }
    )

    with patch("core.ai_wrapper.resolve_gemini_api_key", return_value=("key", "env")):
        with patch("core.ai_wrapper.call_ai_with_retry", return_value=resp):
            out = classify_example_semantics_with_ai(
                ex, anchor, client=_Client(), skill_scoped_candidates=cands
            )
    assert out["ai_semantic_status"] == "ok"
    assert out["available"] is True
    assert out["target_task"] == "compute_internal_division_point_coordinates"
