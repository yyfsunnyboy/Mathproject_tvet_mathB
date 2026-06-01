from __future__ import annotations

from core.gencode.semantic_alignment import evaluate_semantic_alignment, evaluate_source_example_alignment


def _feat(example_id: int, candidate_source: str, *, source_quality_reject: bool = False) -> dict:
    return {
        "source_example_id": example_id,
        "target_task": "",
        "task_family": "",
        "source_quality_reject": source_quality_reject,
        "semantic_classification": {
            "candidate_source": candidate_source,
            "classifier_source": candidate_source,
            "ai_best_candidate_id": "needs_review",
            "ai_semantic_status": "partial_unavailable" if "unavailable" in candidate_source else "ok",
            "final_task_family": "",
            "in_anchor_scope": False,
        },
    }


def test_non_semantic_ai_fallback_not_trigger_majority_needs_review():
    anchor = {
        "expected_task_families": ["function_concept_family"],
        "expected_subskill_candidates": ["evaluate_function_value", "interpret_function_notation"],
        "source_belongs_to_current_skill_by_default": True,
        "skill_anchor_scope": "default",
    }
    features = [
        _feat(1, "ai_needs_review"),
        _feat(2, "rule_fallback_ai_unavailable"),
        _feat(3, "ai_needs_review"),
        _feat(4, "rule_fallback_ai_unavailable"),
    ]
    out = evaluate_semantic_alignment(
        "vh_mock_linear_function",
        source_features=features,
        candidate_specs=[],
        main_skill_anchor=anchor,
        ai_semantic_status="partial_unavailable",
        induction_source_report={"core_example_count": 4, "enrichment_example_count": 0},
    )
    assert "majority_needs_review" not in (out.get("blockers") or [])
    assert "ai_unavailable_fallback_to_same_as_main" in (out.get("warnings") or [])


def test_ai_needs_review_with_rule_same_family_uses_rule_fallback_same_family():
    anchor = {
        "expected_task_families": ["function_concept_family"],
        "expected_subskill_candidates": ["evaluate_function_value", "interpret_function_notation"],
        "source_belongs_to_current_skill_by_default": True,
        "skill_anchor_scope": "default",
    }
    feat = {
        "source_example_id": 4433,
        "target_task": "",
        "task_family": "",
        "source_quality_reject": False,
        "semantic_classification": {
            "candidate_source": "needs_review",
            "classifier_source": "ai_needs_review",
            "ai_best_candidate_id": "needs_review",
            "ai_semantic_status": "ok",
            "rule_target_task": "interpret_function_notation",
            "rule_task_family": "function_concept_family",
            "final_target_task": "",
            "final_task_family": "",
            "requires_human_action": True,
        },
    }
    row = evaluate_source_example_alignment(set(), feat, main_skill_anchor=anchor)
    assert row["alignment_kind"] == "rule_fallback_same_family"
    assert row["included_in_phase1"] is True
    assert row["target_task"] == "interpret_function_notation"


def test_outside_family_needs_review_still_can_block():
    anchor = {
        "expected_task_families": ["function_concept_family"],
        "expected_subskill_candidates": ["evaluate_function_value", "interpret_function_notation"],
        "source_belongs_to_current_skill_by_default": True,
        "skill_anchor_scope": "default",
    }
    features = []
    for i in range(1, 6):
        f = _feat(i, "needs_review")
        f["semantic_classification"]["source_mapping_warning"] = "expected_family_mismatch"
        f["semantic_classification"]["rule_task_family"] = "distance_between_two_points_family"
        f["semantic_classification"]["rule_target_task"] = "compute_distance_between_two_points"
        features.append(f)
    out = evaluate_semantic_alignment(
        "vh_mock_linear_function",
        source_features=features,
        candidate_specs=[],
        main_skill_anchor=anchor,
        ai_semantic_status="ok",
        induction_source_report={"core_example_count": 5, "enrichment_example_count": 0},
    )
    assert str(out.get("decision", "")) == "block"


def test_source_quality_reject_does_not_semantic_block_when_core_enough():
    anchor = {
        "expected_task_families": ["function_concept_family"],
        "expected_subskill_candidates": ["evaluate_function_value", "interpret_function_notation"],
        "source_belongs_to_current_skill_by_default": True,
        "skill_anchor_scope": "default",
    }
    features = []
    for i in range(1, 7):
        f = _feat(i, "needs_review")
        f["semantic_classification"]["classifier_source"] = "ai_needs_review"
        f["semantic_classification"]["rule_task_family"] = "function_concept_family"
        f["semantic_classification"]["rule_target_task"] = "interpret_function_notation"
        features.append(f)
    bad = _feat(99, "rule_fallback_ai_unavailable", source_quality_reject=True)
    bad["semantic_classification"]["rule_task_family"] = "function_concept_family"
    bad["semantic_classification"]["rule_target_task"] = "evaluate_function_value"
    features.append(bad)
    out = evaluate_semantic_alignment(
        "vh_mock_linear_function",
        source_features=features,
        candidate_specs=[],
        main_skill_anchor=anchor,
        ai_semantic_status="partial_unavailable",
        induction_source_report={"core_example_count": 7, "enrichment_example_count": 0},
    )
    assert "semantic_alignment_blocked" not in (out.get("blockers") or [])
    assert "majority_needs_review" not in (out.get("blockers") or [])
    assert 99 in (out.get("source_quality_reject_examples") or [])

