from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from core.gencode.pipeline_orchestrator import run_gencode_phase2


def _phase1_payload(
    *,
    alignment_blockers: list[str] | None = None,
    source_alignment_status: str = "warn",
    requires_human_action: bool = False,
    reject_ids: list[int] | None = None,
    candidate: dict | None = None,
) -> dict:
    c = candidate or {
        "problem_type_id": "numeric_interpret_function_notation_short_answer",
        "matched_example_count": 3,
        "matched_example_ids": [1, 2, 3],
        "answer_contract_proposal": {"answer_type": "numeric"},
        "checker_key_proposal": "numeric_checker",
        "equivalence_type_proposal": "numeric_equivalence",
        "spec_source": "phase1_induced_draft",
        "generator_readiness": "runtime_ready",
        "requires_human_action": False,
        "problem_type_spec_draft": {
            "problem_type_id": "numeric_interpret_function_notation_short_answer",
            "target_task": "interpret_function_notation",
            "answer_contract": {"answer_type": "numeric"},
            "generator_contract": {"template_families": ["interpret_function_notation"]},
        },
    }
    return {
        "source_alignment_status": source_alignment_status,
        "alignment_blockers": alignment_blockers or [],
        "requires_human_action": requires_human_action,
        "semantic_alignment": {"source_quality_reject_examples": list(reject_ids or [])},
        "rejected_source_examples": [{"example_id": int(x), "reason": "source_quality_reject"} for x in (reject_ids or [])],
        "candidate_problem_types": [c],
    }


def _run_with_phase1(skill_id: str, phase1_payload: dict) -> dict:
    from core.gencode import pipeline_orchestrator as po

    with tempfile.TemporaryDirectory() as td:
        report_dir = Path(td)
        (report_dir / f"{skill_id}_phase1_summary.json").write_text(
            json.dumps(phase1_payload, ensure_ascii=False),
            encoding="utf-8",
        )
        with patch.object(po, "REPORT_DIR", report_dir), patch.object(po, "DRAFT_DIR", report_dir / "drafts"):
            out = run_gencode_phase2(skill_id, dry_run=True)
    return out


def test_phase1_global_requires_human_action_does_not_block_clean_candidate():
    phase1 = _phase1_payload(requires_human_action=True)
    out = _run_with_phase1("mock_phase2_gate_global_human", phase1)
    rows = out.get("generator_results") or []
    assert rows
    blockers = rows[0].get("blockers") or []
    assert "manual_review_or_malformed_source" not in blockers


def test_source_quality_reject_ids_not_in_candidate_do_not_block():
    phase1 = _phase1_payload(reject_ids=[10, 11, 12])
    out = _run_with_phase1("mock_phase2_gate_reject_not_hit", phase1)
    row = (out.get("generator_results") or [])[0]
    blockers = row.get("blockers") or []
    assert "manual_review_or_malformed_source" not in blockers


def test_all_candidate_sources_rejected_blocks_candidate():
    cand = {
        "problem_type_id": "numeric_interpret_function_notation_short_answer",
        "matched_example_count": 2,
        "matched_example_ids": [20, 21],
        "answer_contract_proposal": {"answer_type": "numeric"},
        "checker_key_proposal": "numeric_checker",
        "equivalence_type_proposal": "numeric_equivalence",
        "spec_source": "phase1_induced_draft",
        "generator_readiness": "runtime_ready",
        "requires_human_action": False,
        "problem_type_spec_draft": {
            "problem_type_id": "numeric_interpret_function_notation_short_answer",
            "target_task": "interpret_function_notation",
            "answer_contract": {"answer_type": "numeric"},
            "generator_contract": {"template_families": ["interpret_function_notation"]},
        },
    }
    phase1 = _phase1_payload(reject_ids=[20, 21], candidate=cand)
    out = _run_with_phase1("mock_phase2_gate_all_rejected", phase1)
    row = (out.get("generator_results") or [])[0]
    blockers = row.get("blockers") or []
    assert "manual_review_or_malformed_source" in blockers


def test_manual_review_checker_still_blocks():
    cand = {
        "problem_type_id": "manual_review_problem_type",
        "matched_example_count": 3,
        "matched_example_ids": [1, 2, 3],
        "answer_contract_proposal": {"answer_type": "manual_review"},
        "checker_key_proposal": "manual_review_checker",
        "equivalence_type_proposal": "manual_review_or_ai_judged",
        "spec_source": "phase1_induced_draft",
        "generator_readiness": "runtime_ready",
        "requires_human_action": True,
        "problem_type_spec_draft": {
            "problem_type_id": "manual_review_problem_type",
            "target_task": "manual_review",
            "answer_contract": {"answer_type": "manual_review"},
            "generator_contract": {"template_families": ["manual_review"]},
        },
    }
    phase1 = _phase1_payload(candidate=cand)
    out = _run_with_phase1("mock_phase2_gate_manual_checker", phase1)
    row = (out.get("generator_results") or [])[0]
    blockers = row.get("blockers") or []
    assert "manual_review_or_malformed_source" in blockers


def test_alignment_blockers_still_global_block():
    phase1 = _phase1_payload(alignment_blockers=["majority_needs_review"], source_alignment_status="block")
    out = _run_with_phase1("mock_phase2_gate_alignment_block", phase1)
    row = (out.get("generator_results") or [])[0]
    blockers = row.get("blockers") or []
    assert "phase1_semantic_alignment_blocked" in blockers

