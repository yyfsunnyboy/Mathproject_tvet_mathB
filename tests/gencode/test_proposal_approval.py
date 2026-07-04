# -*- coding: utf-8 -*-
"""Tests for Proposal Approval Gate service."""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from core.gencode.services.proposal_approval_service import review_capability_proposals

@pytest.fixture
def temp_proposal_dir(tmp_path: Path) -> Path:
    proposal_root = tmp_path / "proposals"
    proposal_root.mkdir()
    return proposal_root

def test_proposal_approval_scenarios(temp_proposal_dir: Path):
    proposal_root = temp_proposal_dir

    # 1. Setup: 3 proposed proposals, and 1 invalid proposal
    p1 = {
        "proposal_schema": "domain_capability_proposal.v1",
        "proposal_id": "capability_prop1",
        "skill_id": "test_skill",
        "required_capabilities": ["cap1"],
        "source_example_ids": [1],
        "best_reuse_domain": "coordinate_geometry.line_equation",
        "recommended_action": "new_generic_operation",
        "status": "proposed"
    }
    p2 = {
        "proposal_schema": "domain_capability_proposal.v1",
        "proposal_id": "capability_prop2",
        "skill_id": "test_skill",
        "required_capabilities": ["cap2"],
        "source_example_ids": [2],
        "best_reuse_domain": "coordinate_geometry.line_equation",
        "recommended_action": "new_generic_operation",
        "status": "proposed"
    }
    p3 = {
        "proposal_schema": "domain_capability_proposal.v1",
        "proposal_id": "capability_prop3",
        "skill_id": "test_skill",
        "required_capabilities": ["cap3"],
        "source_example_ids": [3],
        "best_reuse_domain": "coordinate_geometry.line_equation",
        "recommended_action": "new_generic_operation",
        "status": "proposed"
    }
    p_invalid = {
        "proposal_schema": "invalid_schema.v1",
        "proposal_id": "capability_propinvalid",
        "skill_id": "test_skill",
        "status": "proposed"
    }

    (proposal_root / "capability_prop1.json").write_text(json.dumps(p1), encoding="utf-8")
    (proposal_root / "capability_prop2.json").write_text(json.dumps(p2), encoding="utf-8")
    (proposal_root / "capability_prop3.json").write_text(json.dumps(p3), encoding="utf-8")
    (proposal_root / "capability_propinvalid.json").write_text(json.dumps(p_invalid), encoding="utf-8")

    # A) Test dry run: zero side effects
    decisions = {
        "capability_prop1": "approve",
        "capability_prop2": "reject",
        "capability_prop3": "hold",
        "capability_propinvalid": "approve"
    }
    report_dry = review_capability_proposals(
        skill_id="test_skill",
        decisions=decisions,
        dry_run=True,
        proposal_root=proposal_root
    )
    assert report_dry["total_pending"] == 4
    assert report_dry["approved"] == 1  # prop1 planned approval (invalid one fails schema validation)
    assert report_dry["rejected"] == 1  # prop2 planned reject
    assert report_dry["held"] == 1      # prop3 hold
    assert report_dry["failed"] == 1    # propinvalid fails schema validation
    
    # Check that file content on disk is completely unchanged
    p1_disk = json.loads((proposal_root / "capability_prop1.json").read_text(encoding="utf-8"))
    assert p1_disk["status"] == "proposed"

    # B) Test actual execution (First Run)
    report_run = review_capability_proposals(
        skill_id="test_skill",
        decisions=decisions,
        dry_run=False,
        proposal_root=proposal_root
    )
    assert report_run["approved"] == 1
    assert report_run["rejected"] == 1
    assert report_run["held"] == 1
    assert report_run["failed"] == 1
    
    # Check files updated correctly
    p1_disk = json.loads((proposal_root / "capability_prop1.json").read_text(encoding="utf-8"))
    assert p1_disk["status"] == "approved"
    assert "reviewed_at" in p1_disk
    assert p1_disk["reviewed_by"] == "human_reviewer"
    assert "proposal_hash" in p1_disk
    
    p2_disk = json.loads((proposal_root / "capability_prop2.json").read_text(encoding="utf-8"))
    assert p2_disk["status"] == "rejected"
    assert "rejected_reason" in p2_disk

    p3_disk = json.loads((proposal_root / "capability_prop3.json").read_text(encoding="utf-8"))
    assert p3_disk["status"] == "proposed"

    # C) Test idempotency: already reviewed cannot be overwritten again
    decisions_new = {
        "capability_prop1": "reject",  # attempt to reject an approved proposal
        "capability_prop2": "approve"  # attempt to approve a rejected proposal
    }
    report_idem = review_capability_proposals(
        skill_id="test_skill",
        decisions=decisions_new,
        dry_run=False,
        proposal_root=proposal_root
    )
    assert report_idem["unchanged"] == 4
    
    p1_disk_idem = json.loads((proposal_root / "capability_prop1.json").read_text(encoding="utf-8"))
    assert p1_disk_idem["status"] == "approved"  # remains approved
    
    p2_disk_idem = json.loads((proposal_root / "capability_prop2.json").read_text(encoding="utf-8"))
    assert p2_disk_idem["status"] == "rejected"  # remains rejected
