# -*- coding: utf-8 -*-
"""Tests for Proposal Draft Orchestrator service."""

from __future__ import annotations

import json
import shutil
import pytest
from pathlib import Path
from typing import Any

from core.gencode.services.proposal_draft_orchestrator_service import build_pending_domain_drafts

@pytest.fixture
def temp_dirs(tmp_path: Path) -> tuple[Path, Path]:
    proposal_root = tmp_path / "proposals"
    draft_root = tmp_path / "drafts"
    proposal_root.mkdir()
    draft_root.mkdir()
    return proposal_root, draft_root

def test_proposal_draft_orchestrator_scenarios(temp_dirs: tuple[Path, Path]):
    proposal_root, draft_root = temp_dirs

    # 1. Setup: 3 proposals
    # Prop 1: approved
    p1 = {
        "proposal_schema": "domain_capability_proposal.v1",
        "proposal_id": "capability_prop1",
        "skill_id": "test_skill",
        "component_id": "src_1",
        "problem_type_id": "cap1",
        "required_capabilities": ["cap1"],
        "candidate_domains": [
            {
                "domain_key": "coordinate_geometry.line_equation",
                "domain_module": "core.domain.coordinate_geometry.line_equation_domain"
            }
        ],
        "best_reuse_domain": "coordinate_geometry.line_equation",
        "missing_operation": "cap1",
        "source_example_ids": [1],
        "status": "approved"
    }
    # Prop 2: proposed (unapproved) -> skipped
    p2 = {
        "proposal_schema": "domain_capability_proposal.v1",
        "proposal_id": "capability_prop2",
        "skill_id": "test_skill",
        "component_id": "src_2",
        "problem_type_id": "cap2",
        "required_capabilities": ["cap2"],
        "candidate_domains": [],
        "best_reuse_domain": "coordinate_geometry.line_equation",
        "missing_operation": "cap2",
        "source_example_ids": [2],
        "status": "proposed"
    }
    # Prop 3: approved, but other skill -> skipped
    p3 = {
        "proposal_schema": "domain_capability_proposal.v1",
        "proposal_id": "capability_prop3",
        "skill_id": "other_skill",
        "component_id": "src_3",
        "problem_type_id": "cap3",
        "required_capabilities": ["cap3"],
        "candidate_domains": [],
        "best_reuse_domain": "coordinate_geometry.line_equation",
        "missing_operation": "cap3",
        "source_example_ids": [3],
        "status": "approved"
    }

    # Write proposals to disk
    (proposal_root / "capability_prop1.json").write_text(json.dumps(p1), encoding="utf-8")
    (proposal_root / "capability_prop2.json").write_text(json.dumps(p2), encoding="utf-8")
    (proposal_root / "capability_prop3.json").write_text(json.dumps(p3), encoding="utf-8")

    # A) Test dry run: zero side effects
    report_dry = build_pending_domain_drafts(
        skill_id="test_skill",
        dry_run=True,
        proposal_root=proposal_root,
        draft_root=draft_root
    )
    assert report_dry["total_proposals"] == 2  # prop1 and prop2
    assert report_dry["approved_pending"] == 1  # prop1
    assert report_dry["skipped_unapproved"] == 1  # prop2
    assert report_dry["drafts_created"] == 1  # prop1 planned creation
    assert report_dry["drafts_reused"] == 0
    
    # Check that no files were written to draft_root
    assert len(list(draft_root.glob("**/*"))) == 0

    # B) Test actual execution (First Run)
    report_run1 = build_pending_domain_drafts(
        skill_id="test_skill",
        dry_run=False,
        proposal_root=proposal_root,
        draft_root=draft_root
    )
    assert report_run1["drafts_created"] == 1
    assert report_run1["drafts_reused"] == 0
    
    # Check index and draft files exist
    assert (draft_root / "capability_prop1" / "revisions.json").is_file()
    assert (draft_root / "capability_prop1" / "revision_0001" / "domain_operation_draft.json").is_file()

    # C) Test actual execution (Second Run - Idempotency)
    report_run2 = build_pending_domain_drafts(
        skill_id="test_skill",
        dry_run=False,
        proposal_root=proposal_root,
        draft_root=draft_root
    )
    assert report_run2["drafts_created"] == 0
    assert report_run2["drafts_reused"] == 1  # reused because proposal hash is unchanged

    # D) Test revision increment when proposal hash changes
    # Modify proposal to change its hash
    p1["source_example_ids"] = [1, 999]
    (proposal_root / "capability_prop1.json").write_text(json.dumps(p1), encoding="utf-8")

    report_run3 = build_pending_domain_drafts(
        skill_id="test_skill",
        dry_run=False,
        proposal_root=proposal_root,
        draft_root=draft_root
    )
    assert report_run3["drafts_created"] == 1  # New revision created
    assert report_run3["drafts_reused"] == 0
    assert (draft_root / "capability_prop1" / "revision_0002" / "domain_operation_draft.json").is_file()
