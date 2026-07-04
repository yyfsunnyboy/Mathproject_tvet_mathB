from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.gencode.domain_capability_proposal_service import (
    create_or_reuse_capability_proposal,
)
from core.gencode.skill_fixed_domain_authority import (
    ComponentOverrideContext,
    SkillFixedDomainError,
    resolve_fixed_domain_context,
)
from core.gencode.v3_error_codes import DOMAIN_CAPABILITY_UNRESOLVED
from core.registry.domain_operation_registry import list_registered_domains


def test_unresolved_provider_creates_complete_review_only_proposal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DOMAIN_CAPABILITY_PROPOSAL_ROOT", str(tmp_path))
    registry_before = list_registered_domains()
    with ComponentOverrideContext(
        {
            "problem_type_id": "abstract_graph_intercepts_and_equation",
            "required_capabilities": ["abstract_graph_intercepts_and_equation"],
            "classification_source": "test",
            "source_example_id": 99001,
        },
        component_id="src_99001",
    ):
        with pytest.raises(SkillFixedDomainError) as exc:
            resolve_fixed_domain_context("abstract_unregistered_skill")

    assert exc.value.code == DOMAIN_CAPABILITY_UNRESOLVED
    proposal = exc.value.details["capability_proposal"]
    required = {
        "skill_id",
        "component_id",
        "problem_type_id",
        "required_capabilities",
        "candidate_domains",
        "best_reuse_domain",
        "missing_operation",
        "source_example_ids",
        "status",
    }
    assert required <= proposal.keys()
    assert proposal["status"] == "proposed"
    assert proposal["production_publish_allowed"] is False
    assert proposal["tracker_status_change"] is None
    assert Path(proposal["proposal_path"]).is_file()
    assert list_registered_domains() == registry_before


def test_same_capability_is_deduplicated_and_sources_are_merged(tmp_path: Path) -> None:
    first = create_or_reuse_capability_proposal(
        skill_id="skill_a",
        component_id="src_1",
        problem_type_id="shared_missing_operation",
        required_capabilities=["shared_missing_operation"],
        source_example_ids=[1],
        proposal_root=tmp_path,
    )
    second = create_or_reuse_capability_proposal(
        skill_id="skill_b",
        component_id="src_2",
        problem_type_id="shared_missing_operation",
        required_capabilities=["shared_missing_operation"],
        source_example_ids=[2],
        proposal_root=tmp_path,
    )
    assert first["proposal_id"] == second["proposal_id"]
    assert len(list(tmp_path.glob("*.json"))) == 1
    persisted = json.loads(Path(second["proposal_path"]).read_text(encoding="utf-8"))
    assert persisted["source_example_ids"] == [1, 2]
    assert persisted["component_ids"] == ["src_1", "src_2"]


def test_linear_graph_capability_prefers_existing_line_equation_domain(tmp_path: Path) -> None:
    proposal = create_or_reuse_capability_proposal(
        skill_id="any_skill",
        component_id="src_1",
        problem_type_id="graph_intercepts_and_linear_equation",
        required_capabilities=["graph_intercepts_and_linear_equation"],
        source_example_ids=[1],
        proposal_root=tmp_path,
    )
    assert proposal["best_reuse_domain"] == "coordinate_geometry.line_equation"
    assert proposal["recommended_action"] == "new_generic_operation"


def test_resolved_capability_does_not_create_proposal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DOMAIN_CAPABILITY_PROPOSAL_ROOT", str(tmp_path))
    context = resolve_fixed_domain_context("vh_數學B1_DistanceBetweenTwoParallelLines")
    assert "distance_between_parallel_lines" in context.allowed_operations
    assert list(tmp_path.glob("*.json")) == []
