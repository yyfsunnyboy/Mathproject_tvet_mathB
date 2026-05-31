from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from core.gencode.ai_semantic_classifier import (
    categorize_ai_unavailability,
    classify_example_semantics_with_ai,
    set_ai_semantic_classifier_mock,
)
from core.gencode.classification_policy import build_classified_example_feature, merge_ai_and_rule_classification
from core.gencode.main_skill_anchor import build_main_skill_anchor
from core.gencode.problem_type_induction import induce_problem_types_from_examples
from core.gencode.task_families import DIVISION_POINT_COORDINATES_FAMILY


def test_categorize_missing_api_key():
    assert categorize_ai_unavailability("ai_api_key_missing") == "missing_api_key"


def test_categorize_provider_response():
    assert categorize_ai_unavailability("Error: Google AI Error: permission denied") == "provider_response_error"


def test_classify_missing_api_key():
    set_ai_semantic_classifier_mock(None)
    with patch("core.ai_wrapper.resolve_gemini_api_key", return_value=(None, None)):
        out = classify_example_semantics_with_ai(
            {"id": 4420, "problem_text": "AP=2PB"},
            {"skill_id": "mock_skill"},
        )
    assert out["available"] is False
    assert out["ai_unavailable_reason"] == "missing_api_key"


def test_classify_provider_error():
    set_ai_semantic_classifier_mock(None)

    class _Client:
        model_name = "gemini-test"

    mock_client = _Client()
    err_resp = MagicMock()
    err_resp.text = "Error: Google AI Error: quota exceeded"

    anchor = {
        "skill_id": "mock",
        "skill_ch_name": "分點坐標",
        "expected_task_families": [DIVISION_POINT_COORDINATES_FAMILY],
        "expected_subskill_candidates": ["compute_internal_division_point_coordinates"],
        "skill_anchor_scope": "broad",
    }
    ex = {"id": 1, "skill_id": "mock", "problem_text": "test"}
    from core.gencode.classification_candidates import build_skill_scoped_candidates
    from core.gencode.example_feature_extractor import extract_example_feature_rule_only

    cands = build_skill_scoped_candidates(anchor, ex, extract_example_feature_rule_only(ex))
    with patch("core.ai_wrapper.resolve_gemini_api_key", return_value=("key", "env")):
        with patch("core.ai_wrapper.call_ai_with_retry", return_value=err_resp):
            out = classify_example_semantics_with_ai(
                ex,
                anchor,
                client=mock_client,
                skill_scoped_candidates=cands,
            )
    assert out["available"] is False
    assert out["ai_unavailable_reason"] == "provider_response_error"


def test_classify_valid_ai_response():
    set_ai_semantic_classifier_mock(None)

    class _Client:
        model_name = "gemini-test"

    mock_client = _Client()
    anchor = {"skill_id": "mock", "skill_ch_name": "分點坐標", "expected_subskill_candidates": ["compute_internal_division_point_coordinates"], "expected_task_families": [DIVISION_POINT_COORDINATES_FAMILY], "skill_anchor_scope": "broad"}
    ex = {"id": 4420, "skill_id": "mock", "problem_text": "AP=2PB", "correct_answer": "(1,2)"}
    from core.gencode.classification_candidates import build_skill_scoped_candidates
    from core.gencode.example_feature_extractor import extract_example_feature_rule_only

    rule = extract_example_feature_rule_only(ex)
    cands = build_skill_scoped_candidates(anchor, ex, rule)
    cid = cands[0]["candidate_id"]
    ok_resp = MagicMock()
    ok_resp.text = json.dumps({"best_candidate_id": cid, "confidence": 0.9, "evidence": ["ratio"], "rejected_candidates": {}})

    with patch("core.ai_wrapper.resolve_gemini_api_key", return_value=("key", "env")):
        with patch("core.ai_wrapper.call_ai_with_retry", return_value=ok_resp):
            out = classify_example_semantics_with_ai(
                ex,
                anchor,
                client=mock_client,
                skill_scoped_candidates=cands,
            )
    assert out["available"] is True
    assert out["task_family"] == DIVISION_POINT_COORDINATES_FAMILY
    assert not out.get("ai_unavailable_reason")


def test_ai_first_with_mock_not_rule_fallback_unavailable():
    skill_id = "mock_avail"
    anchor = build_main_skill_anchor(skill_id, {"skill_ch_name": "分點坐標"})

    def _mock_ai(example, a):
        return {
            "target_task": "compute_internal_division_point_coordinates",
            "task_family": DIVISION_POINT_COORDINATES_FAMILY,
            "confidence": 0.92,
            "evidence": ["ratio"],
            "negative_evidence": {},
        }

    set_ai_semantic_classifier_mock(_mock_ai)
    try:
        with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value={"skill_ch_name": "分點坐標"}):
            out = induce_problem_types_from_examples(
                skill_id,
                [{"id": 4420, "skill_id": skill_id, "problem_text": "AP=2PB", "correct_answer": "(1,2)"}],
                spec_mode="ai_first_induce_from_sources",
            )
        assert out.get("ai_semantic_status") == "ok"
        sem = (out.get("semantic_classifications") or [])[0]
        assert sem["classifier_source"] != "rule_fallback_ai_unavailable"
        feat, trace = build_classified_example_feature(
            {"id": 4420, "problem_text": "AP=2PB", "correct_answer": "(1,2)"},
            anchor,
            spec_mode="ai_first_induce_from_sources",
        )
        assert trace["classifier_source"] in {"ai", "ai_overrode_rule", "ai_rule_agree_family"}
    finally:
        set_ai_semantic_classifier_mock(None)


def test_merge_unavailable_sets_reason():
    rule = {"target_task": "t", "task_family": "f", "confidence": 0.5}
    ai = {"available": False, "error": "ai_api_key_missing", "ai_unavailable_reason": "missing_api_key", "confidence": 0.0}
    merged = merge_ai_and_rule_classification(ai, rule, {})
    assert merged["classifier_source"] == "rule_fallback_ai_unavailable"
    assert merged["ai_unavailable_reason"] == "missing_api_key"
