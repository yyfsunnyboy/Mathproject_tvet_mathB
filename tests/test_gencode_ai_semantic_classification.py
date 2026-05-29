from __future__ import annotations

from unittest.mock import patch

from core.gencode.ai_semantic_classifier import (
    classify_example_semantics_with_ai,
    set_ai_semantic_classifier_mock,
)
from core.gencode.classification_policy import (
    build_classification_diagnostic,
    build_classified_example_feature,
    merge_ai_and_rule_classification,
)
from core.gencode.example_feature_extractor import extract_example_feature_rule_only
from core.gencode.main_skill_anchor import build_main_skill_anchor
from core.gencode.problem_type_induction import induce_problem_types_from_examples
from core.gencode.task_families import (
    DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    DIVISION_POINT_COORDINATES_FAMILY,
)


def _ai(**kwargs) -> dict:
    base = {
        "available": True,
        "target_task": "",
        "task_family": "",
        "math_objects": [],
        "answer_type": "",
        "answer_shape": "",
        "confidence": 0.0,
        "evidence": [],
        "negative_evidence": {},
        "requires_human_action": False,
        "notes": "",
        "error": "",
    }
    base.update(kwargs)
    return base


def _rule_from_stem(stem: str, answer: str = "(1,2)") -> dict:
    feat = extract_example_feature_rule_only(
        {"id": 1, "problem_text": stem, "correct_answer": answer}
    )
    return {
        "target_task": feat["target_task"],
        "task_family": feat["task_family"],
        "math_objects": feat.get("math_objects", []),
        "answer_type": feat.get("answer_type", ""),
        "answer_shape": feat.get("answer_shape", ""),
        "question_text": stem,
    }


def test_high_confidence_ai_overrides_rule_division_vs_distance():
    stem = "點 P 在 AB 上，AP=2PB，求 P 坐標"
    rule = _rule_from_stem(stem)
    rule["target_task"] = "compute_distance_between_two_points"
    rule["task_family"] = DISTANCE_BETWEEN_TWO_POINTS_FAMILY
    ai = _ai(
        target_task="compute_internal_division_point_coordinates",
        task_family=DIVISION_POINT_COORDINATES_FAMILY,
        confidence=0.92,
        evidence=["點 P 在 AB 上", "AP=2PB", "求 P 坐標"],
        negative_evidence={
            "distance_between_two_points_family": "題目不是求 AB 長度，而是用線段比例求分點坐標。",
        },
    )
    merged = merge_ai_and_rule_classification(ai, rule, {})
    assert merged["final_task_family"] == DIVISION_POINT_COORDINATES_FAMILY
    assert merged["classifier_source"] == "ai_overrode_rule"
    assert merged["final_target_task"] == "compute_internal_division_point_coordinates"


def test_high_confidence_ai_and_rule_agree_distance():
    stem = "求 A(1,2) 與 B(5,6) 的距離"
    rule = _rule_from_stem(stem, "5")
    ai = _ai(
        target_task="compute_distance_between_two_points",
        task_family=DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
        confidence=0.91,
    )
    merged = merge_ai_and_rule_classification(ai, rule, {})
    assert merged["final_task_family"] == DISTANCE_BETWEEN_TWO_POINTS_FAMILY
    assert merged["classifier_source"] == "ai"


def test_medium_confidence_same_family_uses_ai_task():
    rule = _rule_from_stem("求 AB 中點", "(3,4)")
    ai = _ai(
        target_task="compute_midpoint_coordinates",
        task_family=DIVISION_POINT_COORDINATES_FAMILY,
        confidence=0.60,
    )
    rule["task_family"] = DIVISION_POINT_COORDINATES_FAMILY
    rule["target_task"] = "compute_midpoint_coordinates"
    merged = merge_ai_and_rule_classification(ai, rule, {})
    assert merged["classifier_source"] == "ai_rule_agree_family"
    assert merged["final_target_task"] == "compute_midpoint_coordinates"


def test_medium_confidence_family_conflict_requires_human():
    rule = _rule_from_stem("點 P 在 AB 上，AP=2PB，求 P 坐標")
    ai = _ai(
        target_task="compute_internal_division_point_coordinates",
        task_family=DIVISION_POINT_COORDINATES_FAMILY,
        confidence=0.60,
    )
    merged = merge_ai_and_rule_classification(ai, rule, {})
    assert merged["classifier_source"] == "ai_rule_conflict_review"
    assert merged["requires_human_action"] is True


def test_low_ai_confidence_rule_fallback():
    rule = _rule_from_stem("求 A(1,2) 與 B(5,6) 的距離", "5")
    ai = _ai(
        target_task="compute_internal_division_point_coordinates",
        task_family=DIVISION_POINT_COORDINATES_FAMILY,
        confidence=0.30,
    )
    merged = merge_ai_and_rule_classification(ai, rule, {})
    assert merged["classifier_source"] == "rule_fallback_low_ai_confidence"
    assert merged["final_task_family"] == DISTANCE_BETWEEN_TWO_POINTS_FAMILY


def test_ai_unavailable_rule_fallback():
    rule = _rule_from_stem("求 A(1,2) 與 B(5,6) 的距離", "5")
    ai = _ai(available=False, error="ai_api_key_missing", confidence=0.0)
    merged = merge_ai_and_rule_classification(ai, rule, {})
    assert merged["classifier_source"] == "rule_fallback_ai_unavailable"
    assert merged["final_task_family"] == DISTANCE_BETWEEN_TWO_POINTS_FAMILY


def test_anchor_mismatch_keeps_ai_distance():
    meta = {"skill_ch_name": "分點坐標"}
    anchor = build_main_skill_anchor("vh_mock_Division", meta)
    rule = _rule_from_stem("點 P 在 AB 上，AP=2PB，求 P 坐標")
    ai = _ai(
        target_task="compute_distance_between_two_points",
        task_family=DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
        confidence=0.88,
        evidence=["求 AB 長度"],
    )
    merged = merge_ai_and_rule_classification(ai, rule, anchor)
    assert merged["final_task_family"] == DISTANCE_BETWEEN_TWO_POINTS_FAMILY
    assert merged["source_mapping_warning"] == "expected_family_mismatch"
    assert merged["final_target_task"] == "compute_distance_between_two_points"


def test_induce_with_mock_ai_ap_over_pb():
    skill_id = "mock_ai_division"
    stem = "點 P 在 AB 上，AP=2PB，求 P 坐標"

    def _mock_ai(example, anchor):
        cands = example.get("_skill_scoped_candidates") or []
        cid = next(
            (str(c["candidate_id"]) for c in cands if c.get("target_task") == "compute_internal_division_point_coordinates"),
            "needs_review",
        )
        return {
            "best_candidate_id": cid,
            "confidence": 0.92,
            "evidence": ["AP=2PB"],
            "rejected_candidates": {},
            "requires_human_action": False,
            "notes": "",
        }

    def _rule_distance(ex):
        feat = extract_example_feature_rule_only(ex)
        feat["target_task"] = "compute_distance_between_two_points"
        feat["task_family"] = DISTANCE_BETWEEN_TWO_POINTS_FAMILY
        return feat

    set_ai_semantic_classifier_mock(_mock_ai)
    try:
        meta = {"skill_ch_name": "分點坐標"}
        with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
            with patch(
                "core.gencode.classification_policy.extract_example_feature_rule_only",
                side_effect=_rule_distance,
            ):
                out = induce_problem_types_from_examples(
                    skill_id,
                    [{"id": 1, "skill_id": skill_id, "problem_text": stem, "correct_answer": "(2,3)"}],
                    spec_mode="ai_first_induce_from_sources",
                )
        sem = (out.get("semantic_classifications") or [])[0]
        assert sem["classifier_source"] == "ai_overrode_rule"
        feat = (out.get("example_features") or [])[0]
        assert feat["target_task"] == "compute_internal_division_point_coordinates"
        assert feat["task_family"] == DIVISION_POINT_COORDINATES_FAMILY
    finally:
        set_ai_semantic_classifier_mock(None)


def test_ai_unavailable_induction_status():
    set_ai_semantic_classifier_mock(None)
    skill_id = "mock_ai_down"
    def _unavailable(ex, anchor, **kwargs):
        return _ai(available=False, error="down")

    with patch("core.gencode.classification_policy.classify_example_semantics_with_ai", side_effect=_unavailable):
        with patch(
            "core.gencode.problem_type_induction.load_skill_metadata_from_db",
            return_value={"skill_ch_name": "分點坐標"},
        ):
            out = induce_problem_types_from_examples(
                skill_id,
                [{"id": 1, "skill_id": skill_id, "problem_text": "求 AB 距離", "correct_answer": "5"}],
                spec_mode="ai_first_induce_from_sources",
            )
    assert out.get("ai_semantic_status") == "unavailable"
    sem = (out.get("semantic_classifications") or [])[0]
    assert sem["classifier_source"] == "rule_fallback_ai_unavailable"


def test_ai_first_no_mixed_source_families_when_finals_agree():
    skill_id = "mock_division_batch"
    stems = {
        4420: "A(3,4)、B(6,-5)、C(x,y)，C 在 AB 上，AC:CB=2:1，求 C 點坐標。",
        4421: "小恩家位於線段 AB 上，且小恩家到醫院的距離等於小恩家到學校距離的 3 倍，求 P(x,y)。",
        4438: "A(-3,0)、B(9,6)，P 在 AB 上，AP=2PB，求 P 點坐標。",
    }

    def _mock_ai(example, anchor):
        cands = example.get("_skill_scoped_candidates") or []
        cid = next(
            (str(c["candidate_id"]) for c in cands if c.get("target_task") == "compute_internal_division_point_coordinates"),
            "needs_review",
        )
        return {
            "best_candidate_id": cid,
            "confidence": 0.92,
            "evidence": ["section ratio"],
            "rejected_candidates": {
                "distance_between_two_points_family": "不是求 AB 長度，而是分點坐標",
            },
        }

    def _rule_distance(ex):
        feat = extract_example_feature_rule_only(ex)
        feat["target_task"] = "compute_distance_between_two_points"
        feat["task_family"] = DISTANCE_BETWEEN_TWO_POINTS_FAMILY
        return feat

    examples = [
        {"id": eid, "skill_id": skill_id, "problem_text": stem, "correct_answer": "(1,2)"}
        for eid, stem in stems.items()
    ]
    set_ai_semantic_classifier_mock(_mock_ai)
    try:
        with patch(
            "core.gencode.problem_type_induction.load_skill_metadata_from_db",
            return_value={"skill_ch_name": "\u5206\u9ede\u5750\u6a19"},
        ):
            with patch(
                "core.gencode.classification_policy.extract_example_feature_rule_only",
                side_effect=_rule_distance,
            ):
                out = induce_problem_types_from_examples(skill_id, examples, spec_mode="ai_first_induce_from_sources")
        assert out.get("ai_semantic_status") == "ok"
        blockers = out.get("alignment_blockers") or []
        assert "mixed_source_families" not in blockers
        assert "source_examples_mismatch" not in blockers
        for d in out.get("classification_diagnostics") or []:
            assert d["final_task_family"] == DIVISION_POINT_COORDINATES_FAMILY
            assert d["classifier_source"] in {"ai", "ai_overrode_rule"}
    finally:
        set_ai_semantic_classifier_mock(None)


def test_semantic_alignment_uses_final_not_rule_on_feature():
    from core.gencode.semantic_alignment import evaluate_semantic_alignment

    feat = {
        "source_example_id": 4438,
        "target_task": "compute_internal_division_point_coordinates",
        "task_family": DIVISION_POINT_COORDINATES_FAMILY,
        "semantic_classification": {
            "final_target_task": "compute_internal_division_point_coordinates",
            "final_task_family": DIVISION_POINT_COORDINATES_FAMILY,
            "rule_target_task": "compute_distance_between_two_points",
            "rule_task_family": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
        },
        "question_text": "AP=2PB",
    }
    anchor = build_main_skill_anchor("mock", {"skill_ch_name": "\u5206\u9ede\u5750\u6a19"})
    align = evaluate_semantic_alignment(
        "mock",
        source_features=[feat],
        candidate_specs=[],
        main_skill_anchor=anchor,
        ai_semantic_status="ok",
    )
    assert "mixed_source_families" not in (align.get("blockers") or [])
    assert align.get("source_family_distribution", {}).get(DIVISION_POINT_COORDINATES_FAMILY) == 1


def test_classification_diagnostics_fields_present():
    anchor = build_main_skill_anchor("mock", {"skill_ch_name": "\u5206\u9ede\u5750\u6a19"})
    ex = {"id": 1, "problem_text": "P 在 AB 上，AP=2PB", "correct_answer": "(1,2)"}
    def _mock_diag(e, a):
        cands = e.get("_skill_scoped_candidates") or []
        cid = next(
            (str(c["candidate_id"]) for c in cands if c.get("target_task") == "compute_internal_division_point_coordinates"),
            "needs_review",
        )
        return {"best_candidate_id": cid, "confidence": 0.9, "evidence": [], "rejected_candidates": {}}

    set_ai_semantic_classifier_mock(_mock_diag)
    try:
        with patch(
            "core.gencode.classification_policy.extract_example_feature_rule_only",
            side_effect=lambda e: {
                **extract_example_feature_rule_only(e),
                "target_task": "compute_distance_between_two_points",
                "task_family": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
            },
        ):
            feat, trace = build_classified_example_feature(ex, anchor, spec_mode="ai_first_induce_from_sources")
        diag = build_classification_diagnostic(feat, trace, anchor, ai_semantic_status="ok")
        for key in (
            "rule_target_task",
            "ai_target_task",
            "final_target_task",
            "classifier_source",
            "expected_task_families",
        ):
            assert key in diag
        assert diag["final_task_family"] == DIVISION_POINT_COORDINATES_FAMILY
    finally:
        set_ai_semantic_classifier_mock(None)


def test_classify_live_skips_when_mock_set():
    from core.gencode.classification_candidates import build_skill_scoped_candidates
    from core.gencode.example_feature_extractor import extract_example_feature_rule_only

    anchor = {
        "skill_id": "mock_quad",
        "skill_ch_name": "象限",
        "expected_task_families": ["classify_quadrant_family"],
        "expected_subskill_candidates": ["classify_quadrant"],
        "skill_anchor_scope": "narrow",
    }
    ex = {"id": 1, "skill_id": "mock_quad", "problem_text": "第幾象限", "correct_answer": "二"}

    def _mock_quad(example, a):
        cands = example.get("_skill_scoped_candidates") or []
        cid = next(
            (str(c["candidate_id"]) for c in cands if c.get("target_task") == "classify_quadrant"),
            "needs_review",
        )
        return {"best_candidate_id": cid, "confidence": 0.9, "evidence": [], "rejected_candidates": {}}

    set_ai_semantic_classifier_mock(_mock_quad)
    try:
        rule = extract_example_feature_rule_only(ex)
        cands = build_skill_scoped_candidates(anchor, ex, rule)
        ex["_skill_scoped_candidates"] = cands
        r = classify_example_semantics_with_ai(ex, anchor, skill_scoped_candidates=cands)
        assert any(c.get("target_task") == "classify_quadrant" for c in cands)
        assert r.get("best_candidate_id") != "needs_review"
        assert r["target_task"] == "classify_quadrant"
    finally:
        set_ai_semantic_classifier_mock(None)
