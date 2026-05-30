from __future__ import annotations

from core.gencode.phase1_result_messages import (
    MSG_LOW_CORE_SOURCE_EXAMPLES,
    MSG_MAJORITY_NEEDS_REVIEW,
    apply_phase1_display_fields,
    is_only_low_core_blockers,
    resolve_phase1_phase_status,
)


def test_only_low_core_blockers_status_and_message():
    payload = {
        "alignment_blockers": ["low_core_source_examples", "semantic_alignment_blocked"],
        "source_alignment_status": "block",
        "skipped_enrichment_examples": [{"example_id": 4430}, {"example_id": 4431}],
        "core_example_count": 0,
        "enrichment_example_count": 2,
        "phase_status": "phase1_blocked_semantic_alignment",
    }
    out = apply_phase1_display_fields(payload)
    assert out["phase_status"] == "phase1_blocked_low_core_sources"
    assert MSG_LOW_CORE_SOURCE_EXAMPLES in out["summary_message"]
    assert MSG_MAJORITY_NEEDS_REVIEW not in out["summary_message"]
    assert "enrichment example_id" in out["example_ids_note"]
    assert "低對齊" not in out["example_ids_note"]
    assert out["alignment_display_kind"] == "low_core_sources"
    assert out["alignment_severity"] == "warning"


def test_majority_needs_review_keeps_semantic_message():
    payload = {
        "alignment_blockers": ["majority_needs_review"],
        "source_alignment_status": "block",
        "phase_status": "phase1_blocked_semantic_alignment",
        "source_example_alignment": [
            {"example_id": 1, "aligned_with_skill": False, "induction_tier": "core"},
        ],
    }
    out = apply_phase1_display_fields(payload)
    assert out["alignment_user_message"] == MSG_MAJORITY_NEEDS_REVIEW
    assert out["alignment_display_kind"] == "semantic_mismatch"
    assert "低對齊 example_id" in out["example_ids_note"]


def test_resolve_phase1_phase_status_low_core():
    st = resolve_phase1_phase_status(
        source_count=2,
        source_alignment_status="block",
        alignment_blockers=["low_core_source_examples"],
        ex_gate_required=False,
        has_fatal=False,
        has_risk_examples=False,
    )
    assert st == "phase1_blocked_low_core_sources"
    assert is_only_low_core_blockers(["low_core_source_examples"])


def test_source_quality_reject_message_kind():
    payload = {
        "alignment_blockers": [],
        "source_alignment_status": "warn",
        "rejected_source_examples": [{"example_id": 1}],
    }
    out = apply_phase1_display_fields(payload)
    assert out["alignment_display_kind"] == "source_quality_reject"
    assert "品質不可用" in out["alignment_user_message"]
