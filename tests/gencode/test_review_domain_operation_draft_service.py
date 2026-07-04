from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from core.gencode.review_domain_operation_draft_service import (
    build_review_domain_operation_draft,
)
from core.gencode.skill_fixed_domain_authority import resolve_fixed_domain_context

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_FILES = (
    PROJECT_ROOT / "core" / "registry" / "domain_operation_registry.py",
    PROJECT_ROOT / "core" / "domain" / "coordinate_geometry" / "line_equation_domain.py",
)


def _write_proposal(root: Path, *, status: str = "approved", marker: str = "v1") -> str:
    proposal_id = "capability_0123456789abcdef01234567"
    payload = {
        "proposal_schema": "domain_capability_proposal.v1",
        "proposal_id": proposal_id,
        "required_capabilities": ["generic_missing_capability"],
        "candidate_domains": [
            {
                "domain_key": "coordinate_geometry.line_equation",
                "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
            }
        ],
        "best_reuse_domain": "coordinate_geometry.line_equation",
        "missing_operation": "generic_missing_operation",
        "source_example_ids": [1],
        "recommended_action": "new_generic_operation",
        "status": status,
        "marker": marker,
    }
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{proposal_id}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return proposal_id


def _hashes(paths: tuple[Path, ...]) -> dict[str, str]:
    return {
        str(path): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
    }


def test_proposed_status_cannot_build_draft(tmp_path: Path) -> None:
    proposal_root = tmp_path / "proposals"
    proposal_id = _write_proposal(proposal_root, status="proposed")

    with pytest.raises(ValueError, match="capability_proposal_not_approved:proposed"):
        build_review_domain_operation_draft(
            proposal_id,
            proposal_root=proposal_root,
            draft_root=tmp_path / "drafts",
        )


def test_approved_proposal_builds_complete_staging_artifact(tmp_path: Path) -> None:
    proposal_root = tmp_path / "proposals"
    proposal_id = _write_proposal(proposal_root)
    draft = build_review_domain_operation_draft(
        proposal_id,
        proposal_root=proposal_root,
        draft_root=tmp_path / "drafts",
    )

    required = {
        "proposal_id",
        "proposal_hash",
        "revision",
        "capability",
        "target_domain",
        "operation_name",
        "operation_signature",
        "input_schema",
        "output_schema",
        "mathematical_invariants",
        "validation_rules",
        "source_example_ids",
        "registry_patch_preview",
        "implementation_file_preview",
        "test_file_preview",
        "status",
        "production_publish_allowed",
    }
    assert required <= draft.keys()
    assert draft["status"] == "draft"
    assert draft["production_publish_allowed"] is False
    assert draft["tracker_status_change"] is None
    assert Path(draft["artifact_path"]).is_file()
    assert Path(draft["index_path"]).is_file()
    assert draft["registry_patch_preview"]["apply"] is False
    assert draft["implementation_file_preview"]["apply"] is False
    assert draft["test_file_preview"]["apply"] is False


def test_revision_is_reused_until_proposal_content_changes(tmp_path: Path) -> None:
    proposal_root = tmp_path / "proposals"
    draft_root = tmp_path / "drafts"
    proposal_id = _write_proposal(proposal_root)

    first = build_review_domain_operation_draft(
        proposal_id,
        proposal_root=proposal_root,
        draft_root=draft_root,
    )
    second = build_review_domain_operation_draft(
        proposal_id,
        proposal_root=proposal_root,
        draft_root=draft_root,
    )
    assert first["revision"] == second["revision"] == 1
    assert first["proposal_hash"] == second["proposal_hash"]
    assert second["reused_revision"] is True

    _write_proposal(proposal_root, marker="v2")
    third = build_review_domain_operation_draft(
        proposal_id,
        proposal_root=proposal_root,
        draft_root=draft_root,
    )
    assert third["revision"] == 2
    assert third["proposal_hash"] != first["proposal_hash"]
    assert third["reused_revision"] is False
    index = json.loads(Path(third["index_path"]).read_text(encoding="utf-8"))
    assert len(index["revisions"]) == 2


def test_builder_does_not_mutate_production_or_tracker(tmp_path: Path) -> None:
    proposal_root = tmp_path / "proposals"
    proposal_id = _write_proposal(proposal_root)
    before = _hashes(PRODUCTION_FILES)

    draft = build_review_domain_operation_draft(
        proposal_id,
        proposal_root=proposal_root,
        draft_root=tmp_path / "drafts",
    )

    assert _hashes(PRODUCTION_FILES) == before
    assert draft["tracker_status_change"] is None
    assert all(
        Path(draft[key]["target_file"]) not in PRODUCTION_FILES
        or draft[key]["apply"] is False
        for key in (
            "registry_patch_preview",
            "implementation_file_preview",
            "test_file_preview",
        )
    )


def test_resolved_capability_flow_is_unchanged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOMAIN_OPERATION_DRAFT_ROOT", str(tmp_path / "drafts"))
    context = resolve_fixed_domain_context(
        "vh_\u6578\u5b78B1_DistanceBetweenTwoParallelLines"
    )

    assert "distance_between_parallel_lines" in context.allowed_operations
    assert not (tmp_path / "drafts").exists()
