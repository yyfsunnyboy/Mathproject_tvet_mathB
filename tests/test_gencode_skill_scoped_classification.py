from __future__ import annotations

from unittest.mock import patch

from core.gencode.classification_candidates import (
    NEEDS_REVIEW_ID,
    build_generator_contract_for_task,
    build_skill_scoped_candidates,
)
from core.gencode.classification_policy import build_classified_example_feature, merge_skill_scoped_classification
from core.gencode.example_feature_extractor import extract_example_feature_rule_only
from core.gencode.main_skill_anchor import build_main_skill_anchor, example_skill_id_mismatch
from core.gencode.problem_type_induction import induce_problem_types_from_examples
from core.gencode.semantic_alignment import evaluate_semantic_alignment
from core.gencode.task_families import DIVISION_POINT_COORDINATES_FAMILY
from core.gencode.ai_semantic_classifier import set_ai_semantic_classifier_mock


def _anchor_division(skill_id: str = "mock_DivisionPoint") -> dict:
    return build_main_skill_anchor(skill_id, {"skill_ch_name": "分點坐標"})


def _pick_candidate_id(candidates: list, target_task: str) -> str:
    for c in candidates:
        if c.get("target_task") == target_task:
            return str(c["candidate_id"])
    return NEEDS_REVIEW_ID


def _mock_select(target_task: str, confidence: float = 0.92):
    def _fn(example, anchor):
        cands = example.get("_skill_scoped_candidates") or []
        return {
            "best_candidate_id": _pick_candidate_id(cands, target_task),
            "confidence": confidence,
            "evidence": ["mock"],
            "rejected_candidates": {},
            "requires_human_action": False,
            "notes": "",
        }

    return _fn


def test_internal_division_over_rule_distance():
    skill_id = "mock_division"
    anchor = _anchor_division(skill_id)
    stem = "點 P 在 AB 上，AP=2PB，求 P 坐標"
    ex = {"id": 4420, "skill_id": skill_id, "problem_text": stem, "correct_answer": "(2,3)"}
    rule = extract_example_feature_rule_only(ex)
    rule["target_task"] = "compute_distance_between_two_points"
    rule["task_family"] = "distance_between_two_points_family"

    set_ai_semantic_classifier_mock(_mock_select("compute_internal_division_point_coordinates"))
    try:
        with patch(
            "core.gencode.classification_policy.extract_example_feature_rule_only",
            return_value=rule,
        ):
            feat, trace = build_classified_example_feature(ex, anchor, spec_mode="ai_first_induce_from_sources")
        assert trace["final_target_task"] == "compute_internal_division_point_coordinates"
        assert trace["classifier_source"] in {"ai", "ai_overrode_rule", "ai_subskill_selected"}
        assert trace["candidate_source"] == "anchor"
        assert "mixed_source_families" not in str(trace.get("conflict_reason", ""))
    finally:
        set_ai_semantic_classifier_mock(None)


def test_centroid_selection():
    anchor = _anchor_division()
    ex = {"id": 2, "skill_id": anchor["skill_id"], "problem_text": "△ABC 的重心坐標", "correct_answer": "(1,2)"}
    set_ai_semantic_classifier_mock(_mock_select("compute_centroid_coordinates"))
    try:
        feat, trace = build_classified_example_feature(ex, anchor, spec_mode="ai_first_induce_from_sources")
        assert trace["final_target_task"] == "compute_centroid_coordinates"
    finally:
        set_ai_semantic_classifier_mock(None)


def test_multiple_subskills_pass_not_block():
    skill_id = "mock_division_batch"
    anchor = _anchor_division(skill_id)
    examples = [
        {"id": 1, "skill_id": skill_id, "problem_text": "求 AB 中點", "correct_answer": "(1,1)"},
        {"id": 2, "skill_id": skill_id, "problem_text": "△ABC 重心", "correct_answer": "(2,2)"},
        {"id": 3, "skill_id": skill_id, "problem_text": "P 在 AB 上 AP=2PB 求 P", "correct_answer": "(3,3)"},
    ]

    def _mock_ai(example, a):
        text = str(example.get("problem_text", ""))
        if "重心" in text:
            return {"best_candidate_id": _pick_candidate_id(example.get("_skill_scoped_candidates") or [], "compute_centroid_coordinates"), "confidence": 0.9, "evidence": [], "rejected_candidates": {}}
        if "中點" in text or "中点" in text:
            return {"best_candidate_id": _pick_candidate_id(example.get("_skill_scoped_candidates") or [], "compute_midpoint_coordinates"), "confidence": 0.9, "evidence": [], "rejected_candidates": {}}
        return {"best_candidate_id": _pick_candidate_id(example.get("_skill_scoped_candidates") or [], "compute_internal_division_point_coordinates"), "confidence": 0.9, "evidence": [], "rejected_candidates": {}}

    set_ai_semantic_classifier_mock(_mock_ai)
    try:
        with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value={"skill_ch_name": "分點坐標"}):
            out = induce_problem_types_from_examples(skill_id, examples, spec_mode="ai_first_induce_from_sources")
        assert out.get("ai_semantic_status") == "ok"
        assert "mixed_source_families" not in (out.get("alignment_blockers") or [])
        assert out.get("source_alignment_status") in {"pass", "warn"}
    finally:
        set_ai_semantic_classifier_mock(None)


def test_needs_review_requires_human():
    anchor = _anchor_division()
    ex = {"id": 9, "skill_id": anchor["skill_id"], "problem_text": "無法判讀的圖形題", "correct_answer": "?"}
    set_ai_semantic_classifier_mock(lambda e, a: {"best_candidate_id": NEEDS_REVIEW_ID, "confidence": 0.2, "evidence": [], "rejected_candidates": {}})
    try:
        feat, trace = build_classified_example_feature(ex, anchor, spec_mode="ai_first_induce_from_sources")
        assert trace.get("requires_human_action") is True
        assert trace.get("ai_best_candidate_id") == NEEDS_REVIEW_ID
    finally:
        set_ai_semantic_classifier_mock(None)


def test_skill_id_mismatch_blocks():
    skill_id = "mock_division"
    anchor = _anchor_division(skill_id)
    examples = [{"id": 1, "skill_id": "other_skill", "problem_text": "P 在 AB 上", "correct_answer": "(1,2)"}]
    set_ai_semantic_classifier_mock(_mock_select("compute_internal_division_point_coordinates"))
    try:
        with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value={"skill_ch_name": "分點坐標"}):
            out = induce_problem_types_from_examples(skill_id, examples, spec_mode="ai_first_induce_from_sources")
        assert example_skill_id_mismatch(examples[0], skill_id)
        assert "skill_id_mismatch" in (out.get("alignment_blockers") or [])
    finally:
        set_ai_semantic_classifier_mock(None)


def test_generator_contract_internal_division():
    gc = build_generator_contract_for_task("compute_internal_division_point_coordinates")
    ps = gc.get("parameter_schema") or {}
    assert "ratio" in ps
    assert "coordinate_range" in ps
    assert gc.get("answer_shape") == "coordinate_pair"
    assert len(gc.get("template_variants") or []) >= 3


def test_generator_contract_centroid():
    gc = build_generator_contract_for_task("compute_centroid_coordinates")
    ps = gc.get("parameter_schema") or {}
    assert ps.get("point_count", {}).get("fixed") == 3
    assert "coordinate_range" in ps
    assert gc.get("answer_shape") == "coordinate_pair"


def test_outsider_candidate_not_default_final():
    anchor = _anchor_division()
    ex = {"id": 1, "skill_id": anchor["skill_id"], "problem_text": "求距離", "correct_answer": "5"}
    cands = build_skill_scoped_candidates(anchor, ex, {"target_task": "compute_distance_between_two_points", "task_family": "distance_between_two_points_family"})
    merged = merge_skill_scoped_classification(
        {
            "available": True,
            "best_candidate_id": _pick_candidate_id(cands, "compute_distance_between_two_points"),
            "target_task": "compute_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "candidate_source": "outsider",
            "confidence": 0.95,
            "evidence": [],
            "skill_scoped_candidates": cands,
        },
        {"target_task": "compute_distance_between_two_points", "task_family": "distance_between_two_points_family", "question_text": "求距離"},
        anchor,
        skill_scoped_candidates=cands,
    )
    assert merged["classifier_source"] == "ai_outsider_candidate"
    assert merged.get("source_mapping_warning")
