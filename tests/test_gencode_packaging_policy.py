from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from core.gencode.packaging_policy import (
    is_generator_usable_for_packaging,
    merge_generator_records,
    select_generators_for_packaging,
)
from core.gencode.pipeline_orchestrator import run_gencode_phase2, run_gencode_phase3_package


def _row(**kwargs):
    base = {
        "problem_type_id": "pt_a",
        "generator_key": "skill:pt_a:draft_v1",
        "checker_smoke_status": "passed",
        "dynamic_sampling_status": "passed",
        "blockers": [],
        "warnings": [],
        "requires_human_action": False,
    }
    base.update(kwargs)
    return base


def test_usable_with_warning_only():
    ok, reasons = is_generator_usable_for_packaging(
        _row(generator_status="runtime_ready", warnings=["low_source_examples"])
    )
    assert ok is True
    assert reasons == []


def test_usable_status_field_alias():
    ok, _ = is_generator_usable_for_packaging(_row(status="runtime_ready", generator_status=""))
    assert ok is True


def test_usable_generator_status_field():
    ok, _ = is_generator_usable_for_packaging(_row(generator_status="runtime_ready"))
    assert ok is True


def test_blocked_by_blockers():
    ok, reasons = is_generator_usable_for_packaging(
        _row(generator_status="runtime_ready", blockers=["checker_contract_missing"])
    )
    assert ok is False
    assert any("blockers" in r for r in reasons)


def test_checker_smoke_failed():
    ok, reasons = is_generator_usable_for_packaging(
        _row(generator_status="runtime_ready", checker_smoke_status="failed")
    )
    assert ok is False
    assert any("checker_smoke" in r for r in reasons)


def test_dynamic_sampling_failed():
    ok, reasons = is_generator_usable_for_packaging(
        _row(generator_status="runtime_ready", dynamic_sampling_status="failed")
    )
    assert ok is False


def test_dynamic_sampling_diversity_warning_still_usable():
    ok, reasons = is_generator_usable_for_packaging(
        _row(
            generator_status="runtime_ready_with_warning",
            dynamic_sampling_status="runtime_ready_with_diversity_warning",
            warnings=["consecutive_same_template_variant", "low_source_examples"],
            usable_for_phase3=True,
        )
    )
    assert ok is True
    assert reasons == []


def test_merge_status_from_phase2_and_contract_from_draft():
    phase2 = {
        "generator_results": [
            _row(
                generator_status="runtime_ready",
                answer_contract={"checker": "solution_set_checker"},
            )
        ]
    }
    draft = {
        "generator_results": [
            {
                "problem_type_id": "pt_a",
                "generator_key": "skill:pt_a:draft_v1",
                "status": "runtime_ready",
            }
        ]
    }
    merged = merge_generator_records(phase2, draft)
    assert len(merged) == 1
    assert merged[0].get("generator_status") == "runtime_ready"
    assert merged[0].get("answer_contract", {}).get("checker") == "solution_set_checker"


def test_select_with_warnings_phase2_completed_style():
    phase2 = {
        "generator_results": [
            _row(generator_status="runtime_ready", warnings=["low_source_examples"]),
            _row(
                problem_type_id="pt_b",
                generator_key="skill:pt_b:draft_v1",
                generator_status="runtime_ready",
                warnings=[],
            ),
        ]
    }
    usable, diag = select_generators_for_packaging(phase2, {})
    assert len(usable) == 2
    assert diag["included_count"] == 2


def test_phase3_with_phase2_summary_only():
    skill_id = "mock_packaging_phase3"
    phase2_payload = {
        "ok": True,
        "phase": "phase2",
        "skill_id": skill_id,
        "generator_results": [
            _row(generator_status="runtime_ready", warnings=["low_source_examples"]),
        ],
        "accepted_generators": ["skill:pt_a:draft_v1"],
        "failed_generators": [],
    }
    from core.gencode import pipeline_orchestrator as po

    with tempfile.TemporaryDirectory() as td:
        report_dir = Path(td)
        draft_dir = report_dir / "drafts"
        draft_dir.mkdir(parents=True)
        (report_dir / f"{skill_id}_phase2_generator_summary.json").write_text(
            json.dumps(phase2_payload, ensure_ascii=False),
            encoding="utf-8",
        )
        with patch.object(po, "REPORT_DIR", report_dir), patch.object(po, "DRAFT_DIR", draft_dir):
            out = run_gencode_phase3_package(skill_id, dry_run=True)
    assert out.get("packaging_usable_count", 0) >= 1
    assert out.get("phase_status") != "phase3_blocked_no_usable_generators"
    assert "no usable generators" not in str(out.get("summary_message", "")).lower() or out.get("packaging_usable_count", 0) > 0


def test_phase3_blocked_lists_exclusions():
    skill_id = "mock_packaging_block"
    phase2_payload = {
        "generator_results": [
            _row(generator_status="blocked", blockers=["semantic_alignment_blocked"]),
        ],
    }
    from core.gencode import pipeline_orchestrator as po

    with tempfile.TemporaryDirectory() as td:
        report_dir = Path(td)
        draft_dir = report_dir / "drafts"
        draft_dir.mkdir(parents=True)
        (report_dir / f"{skill_id}_phase2_generator_summary.json").write_text(
            json.dumps(phase2_payload, ensure_ascii=False),
            encoding="utf-8",
        )
        with patch.object(po, "REPORT_DIR", report_dir), patch.object(po, "DRAFT_DIR", draft_dir):
            out = run_gencode_phase3_package(skill_id, dry_run=True)
    assert out.get("packaging_usable_count") == 0
    assert out.get("phase_status") == "phase3_blocked_no_usable_generators"
    assert "excluded" in str(out.get("summary_message", "")).lower() or "candidates=1" in str(
        out.get("summary_message", "")
    )
