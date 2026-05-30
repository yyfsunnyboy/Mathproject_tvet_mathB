from __future__ import annotations

from core.gencode.pipeline_orchestrator import _normalize_phase_response


def test_default_problem_type_summary_not_claim_continue_when_blocked():
    payload = {
        "ok": False,
        "phase": "phase1",
        "skill_id": "vh_mock_linear_function",
        "source_example_count": 5,
        "source_alignment_status": "block",
        "alignment_blockers": ["majority_needs_review"],
        "alignment_warnings": [],
        "candidate_problem_types": [],
        "induced_problem_type_specs": [],
        "classifier_source": "ai_bootstrap_with_default_fallback",
        "default_problem_type_used": True,
        "exception_review_gate": {"required": True, "reasons": ["majority_needs_review"]},
        "risk_examples": [],
    }
    out = _normalize_phase_response(payload)
    msg = str(out.get("summary_message", ""))
    assert "可進入 Phase 2" not in msg
    assert "需人工確認" in msg
    warns = out.get("alignment_warnings") or []
    assert "default_problem_type_inconsistent_with_final_specs" in warns
    assert out.get("can_continue") is False

