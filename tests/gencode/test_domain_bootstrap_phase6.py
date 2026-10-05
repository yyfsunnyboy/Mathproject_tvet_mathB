# -*- coding: utf-8 -*-
"""Phase 6 domain bootstrap closed-loop tests (mock AI only)."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.domain_bootstrap.candidate_registry import (
    list_verified_bootstrap_providers,
    load_verified_candidates_from_disk,
    unregister_verified_candidate,
)
from core.gencode.domain_bootstrap.candidate_store import CandidateStore
from core.gencode.domain_bootstrap.gap_service import (
    build_gap_report_from_resolver_error,
    detect_or_reuse_domain_gap,
)
from core.gencode.domain_bootstrap.healer import MockBootstrapAIClient
from core.gencode.domain_bootstrap.models import BootstrapSession, BootstrapState
from core.gencode.domain_bootstrap.orchestrator import DomainBootstrapOrchestrator
from core.gencode.domain_bootstrap.planner import estimate_bootstrap_cost
from core.gencode.domain_bootstrap.promotion_service import PromotionError, promote_candidate_to_verified
from core.gencode.domain_bootstrap.retry_service import retry_affected_components
from core.gencode.domain_bootstrap.scaffold_builder import ABSTRACT_FIXTURE_CAPABILITY
from core.gencode.domain_bootstrap.validation_runner import validate_candidate_domain
from core.gencode.skill_fixed_domain_authority import (
    SkillFixedDomainError,
    get_domain_providers_for_resolution,
)
from core.gencode.v3_error_codes import DOMAIN_CAPABILITY_PARTIAL, DOMAIN_CAPABILITY_UNRESOLVED
from core.registry.domain_operation_registry import list_registered_domains

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_REGISTRY_PATH = PROJECT_ROOT / "core" / "registry" / "domain_operation_registry.py"


@pytest.fixture
def isolated_store() -> Iterator[CandidateStore]:
    run_id = uuid.uuid4().hex
    bootstrap_root = PROJECT_ROOT / "reports" / "domain_bootstrap" / f"pytest_{run_id}"
    candidate_root = PROJECT_ROOT / "agent_domains_candidate" / f"pytest_{run_id}"
    store = CandidateStore(bootstrap_root=bootstrap_root, candidate_root=candidate_root)
    try:
        yield store
    finally:
        shutil.rmtree(bootstrap_root, ignore_errors=True)
        shutil.rmtree(candidate_root, ignore_errors=True)


@pytest.fixture
def registry_store(isolated_store: CandidateStore) -> Path:
    return isolated_store.bootstrap_root / "verified_candidates.json"


def _gap_exc(code: str, *, capabilities: list[str], example_id: int = 99001) -> SkillFixedDomainError:
    return SkillFixedDomainError(
        code,
        f"{code}:fixture",
        details={
            "required_capabilities": capabilities,
            "matched_capabilities": [],
            "problem_type_id": "fixture_problem_type",
            "textbook_example_id": example_id,
        },
    )


def test_unknown_capability_produces_gap_report(isolated_store: CandidateStore) -> None:
    exc = _gap_exc(DOMAIN_CAPABILITY_UNRESOLVED, capabilities=[ABSTRACT_FIXTURE_CAPABILITY])
    result = DomainBootstrapOrchestrator(isolated_store).handle_resolver_gap(
        exc=exc,
        skill_id="fixture_skill_alpha",
        textbook_example_id=99001,
        component_id="src_99001",
        phase1_spec={"presentation_mode": "short_answer"},
        source_hash="hash-a",
    )
    report = result["gap_report"]
    assert report["gap_id"].startswith("gap_")
    assert ABSTRACT_FIXTURE_CAPABILITY in report["missing_capabilities"]
    assert "fixture_skill_alpha" in report["affected_skill_ids"]


def test_same_gap_is_reused(isolated_store: CandidateStore) -> None:
    exc = _gap_exc(DOMAIN_CAPABILITY_UNRESOLVED, capabilities=[ABSTRACT_FIXTURE_CAPABILITY], example_id=99001)
    first = detect_or_reuse_domain_gap(
        store=isolated_store,
        error_code=exc.code,
        error_details=exc.details,
        skill_id="fixture_skill_alpha",
        textbook_example_id=99001,
        component_id="src_99001",
        source_hash="hash-a",
    )
    second = detect_or_reuse_domain_gap(
        store=isolated_store,
        error_code=exc.code,
        error_details=exc.details,
        skill_id="fixture_skill_beta",
        textbook_example_id=99002,
        component_id="src_99002",
        source_hash="hash-a",
    )
    assert first.gap_id == second.gap_id
    assert 99002 in second.source_example_ids


def test_partial_and_unresolved_aggregate_capabilities(isolated_store: CandidateStore) -> None:
    unresolved = build_gap_report_from_resolver_error(
        error_code=DOMAIN_CAPABILITY_UNRESOLVED,
        error_details={"required_capabilities": ["cap_a"], "matched_capabilities": []},
        skill_id="s1",
        textbook_example_id=1,
        component_id="src_1",
        source_hash="same-hash",
    )
    partial = build_gap_report_from_resolver_error(
        error_code=DOMAIN_CAPABILITY_PARTIAL,
        error_details={"required_capabilities": ["cap_b"], "matched_capabilities": ["cap_x"]},
        skill_id="s2",
        textbook_example_id=2,
        component_id="src_2",
        source_hash="other-hash",
    )
    isolated_store.save_gap_report(unresolved)
    isolated_store.save_gap_report(partial)
    assert unresolved.error_code == DOMAIN_CAPABILITY_UNRESOLVED
    assert partial.error_code == DOMAIN_CAPABILITY_PARTIAL
    assert partial.matched_capabilities == ["cap_x"]


def test_cost_estimate_requires_ai_authorization(isolated_store: CandidateStore) -> None:
    exc = _gap_exc(DOMAIN_CAPABILITY_UNRESOLVED, capabilities=[ABSTRACT_FIXTURE_CAPABILITY])
    gap = detect_or_reuse_domain_gap(
        store=isolated_store,
        error_code=exc.code,
        error_details=exc.details,
        skill_id="fixture_skill_alpha",
        textbook_example_id=99001,
        component_id="src_99001",
    )
    cost = estimate_bootstrap_cost(gap_report=gap, store=isolated_store, allow_ai=False)
    assert cost["estimated_ai_calls"] == 0
    assert cost["requires_explicit_ai_authorization"] is False
    cost_ai = estimate_bootstrap_cost(gap_report=gap, store=isolated_store, allow_ai=True)
    assert cost_ai["estimated_ai_calls"] >= 1
    assert cost_ai["requires_explicit_ai_authorization"] is True


def test_candidate_writes_only_isolated_workspace(isolated_store: CandidateStore) -> None:
    exc = _gap_exc(DOMAIN_CAPABILITY_UNRESOLVED, capabilities=[ABSTRACT_FIXTURE_CAPABILITY])
    gap = detect_or_reuse_domain_gap(
        store=isolated_store,
        error_code=exc.code,
        error_details=exc.details,
        skill_id="fixture_skill_alpha",
        textbook_example_id=99001,
        component_id="src_99001",
    )
    isolated_store.save_session(BootstrapSession(gap_id=gap.gap_id, gap_report=gap))
    result = DomainBootstrapOrchestrator(isolated_store).start_bootstrap(gap.gap_id, allow_ai=False)
    candidate_dir = isolated_store.candidate_dir(gap.gap_id)
    assert candidate_dir.is_dir()
    assert (candidate_dir / "domain_manifest.json").is_file()
    assert not (PROJECT_ROOT / "core" / "domain").joinpath("fixture").exists()
    assert result["state"] in {
        BootstrapState.AWAITING_TEACHER_REVIEW.value,
        BootstrapState.CANDIDATE.value,
    }


def test_valid_candidate_reaches_awaiting_teacher_review(isolated_store: CandidateStore) -> None:
    exc = _gap_exc(DOMAIN_CAPABILITY_UNRESOLVED, capabilities=[ABSTRACT_FIXTURE_CAPABILITY])
    gap = detect_or_reuse_domain_gap(
        store=isolated_store,
        error_code=exc.code,
        error_details=exc.details,
        skill_id="fixture_skill_alpha",
        textbook_example_id=99001,
        component_id="src_99001",
    )
    from core.gencode.domain_bootstrap.models import BootstrapSession

    isolated_store.save_session(BootstrapSession(gap_id=gap.gap_id, gap_report=gap))
    result = DomainBootstrapOrchestrator(isolated_store).start_bootstrap(
        gap.gap_id,
        allow_ai=False,
    )
    assert result["state"] == BootstrapState.AWAITING_TEACHER_REVIEW.value
    assert result["ai_calls"] == 0


def test_validation_failure_triggers_healer(isolated_store: CandidateStore) -> None:
    MockBootstrapAIClient.calls = 0
    exc = _gap_exc(DOMAIN_CAPABILITY_UNRESOLVED, capabilities=[ABSTRACT_FIXTURE_CAPABILITY])
    gap = detect_or_reuse_domain_gap(
        store=isolated_store,
        error_code=exc.code,
        error_details=exc.details,
        skill_id="fixture_skill_alpha",
        textbook_example_id=99001,
        component_id="src_99001",
    )
    from core.gencode.domain_bootstrap.models import BootstrapSession

    isolated_store.save_session(BootstrapSession(gap_id=gap.gap_id, gap_report=gap))
    result = DomainBootstrapOrchestrator(isolated_store).start_bootstrap(
        gap.gap_id,
        deliberately_broken=True,
    )
    assert result["validation"]["passed"] is True
    assert MockBootstrapAIClient.calls >= 1


def test_healer_does_not_modify_production_registry(isolated_store: CandidateStore) -> None:
    before = set(list_registered_domains())
    exc = _gap_exc(DOMAIN_CAPABILITY_UNRESOLVED, capabilities=[ABSTRACT_FIXTURE_CAPABILITY])
    gap = detect_or_reuse_domain_gap(
        store=isolated_store,
        error_code=exc.code,
        error_details=exc.details,
        skill_id="fixture_skill_alpha",
        textbook_example_id=99001,
        component_id="src_99001",
    )
    from core.gencode.domain_bootstrap.models import BootstrapSession

    isolated_store.save_session(BootstrapSession(gap_id=gap.gap_id, gap_report=gap))
    DomainBootstrapOrchestrator(isolated_store).start_bootstrap(gap.gap_id, deliberately_broken=True)
    after = set(list_registered_domains())
    assert before == after


def test_healer_exhaustion_moves_to_needs_admin_review(isolated_store: CandidateStore) -> None:
    exc = _gap_exc(DOMAIN_CAPABILITY_UNRESOLVED, capabilities=[ABSTRACT_FIXTURE_CAPABILITY])
    gap = detect_or_reuse_domain_gap(
        store=isolated_store,
        error_code=exc.code,
        error_details=exc.details,
        skill_id="fixture_skill_alpha",
        textbook_example_id=99001,
        component_id="src_99001",
    )
    from core.gencode.domain_bootstrap.models import BootstrapSession

    isolated_store.save_session(BootstrapSession(gap_id=gap.gap_id, gap_report=gap))
    result = DomainBootstrapOrchestrator(isolated_store).start_bootstrap(
        gap.gap_id,
        force_unhealable=True,
    )
    assert result["state"] == BootstrapState.NEEDS_ADMIN_REVIEW.value


def test_unapproved_candidate_not_in_resolver(isolated_store: CandidateStore) -> None:
    providers = get_domain_providers_for_resolution()
    assert all(not key.startswith("candidate.") for key in providers.keys() if "fixture" in key)


def test_approve_promotes_verified_candidate(
    isolated_store: CandidateStore,
    registry_store: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    verified_root = isolated_store.bootstrap_root / "verified_domains"
    monkeypatch.setattr(
        "core.gencode.domain_bootstrap.promotion_service.VERIFIED_DOMAIN_ROOT",
        verified_root,
    )
    exc = _gap_exc(DOMAIN_CAPABILITY_UNRESOLVED, capabilities=[ABSTRACT_FIXTURE_CAPABILITY])
    gap = detect_or_reuse_domain_gap(
        store=isolated_store,
        error_code=exc.code,
        error_details=exc.details,
        skill_id="fixture_skill_alpha",
        textbook_example_id=99001,
        component_id="src_99001",
    )
    from core.gencode.domain_bootstrap.models import BootstrapSession

    isolated_store.save_session(BootstrapSession(gap_id=gap.gap_id, gap_report=gap))
    orch = DomainBootstrapOrchestrator(isolated_store)
    orch.start_bootstrap(gap.gap_id, deliberately_broken=True)
    approved = orch.approve_and_promote(
        gap.gap_id,
        teacher_answers={"approved": True},
        registry_store_path=str(registry_store),
    )
    assert approved["approved"] is True
    load_verified_candidates_from_disk(store_path=registry_store)
    assert list_verified_bootstrap_providers()


def test_promotion_failure_rolls_back_registry(
    isolated_store: CandidateStore,
    registry_store: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exc = _gap_exc(DOMAIN_CAPABILITY_UNRESOLVED, capabilities=[ABSTRACT_FIXTURE_CAPABILITY])
    gap = detect_or_reuse_domain_gap(
        store=isolated_store,
        error_code=exc.code,
        error_details=exc.details,
        skill_id="fixture_skill_alpha",
        textbook_example_id=99001,
        component_id="src_99001",
    )
    with pytest.raises(PromotionError):
        promote_candidate_to_verified(
            store=isolated_store,
            gap_report=gap,
            artifact_hash="",
            teacher_approved=False,
            registry_store_path=registry_store,
        )
    load_verified_candidates_from_disk(store_path=registry_store)
    assert not list_verified_bootstrap_providers()


def _write_multi_operation_manifest(store: CandidateStore, gap_id: str, operations: list[str]) -> None:
    path = store.candidate_dir(gap_id) / "domain_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["operations"] = operations
    path.write_text(json.dumps(manifest), encoding="utf-8")


def test_multi_operation_promotion_registers_full_capability_and_is_idempotent(
    isolated_store: CandidateStore,
    registry_store: Path,
    monkeypatch: pytest.MonkeyPatch,
    isolated_verified_memory: None,
) -> None:
    verified_root = isolated_store.bootstrap_root / "verified_domains"
    monkeypatch.setattr("core.gencode.domain_bootstrap.promotion_service.VERIFIED_DOMAIN_ROOT", verified_root)
    capabilities = ["fixture_capability_a", "fixture_capability_b", "fixture_capability_c"]
    exc = _gap_exc(DOMAIN_CAPABILITY_UNRESOLVED, capabilities=capabilities)
    gap = detect_or_reuse_domain_gap(
        store=isolated_store, error_code=exc.code, error_details=exc.details,
        skill_id="fixture_skill_alpha", textbook_example_id=99001, component_id="src_99001",
    )
    from core.gencode.domain_bootstrap.scaffold_builder import build_candidate_scaffold

    scaffold = build_candidate_scaffold(store=isolated_store, gap_report=gap)
    operations = ["fixture_operation_a", "fixture_operation_b", "fixture_operation_c"]
    _write_multi_operation_manifest(isolated_store, gap.gap_id, operations)
    validation = validate_candidate_domain(store=isolated_store, gap_report=gap)
    assert validation["passed"] is True
    assert {row["operation"] for row in validation["seed_results"]} == set(operations)

    first = promote_candidate_to_verified(
        store=isolated_store, gap_report=gap, artifact_hash=scaffold["artifact_hash"],
        teacher_approved=True, registry_store_path=registry_store,
    )
    second = promote_candidate_to_verified(
        store=isolated_store, gap_report=gap, artifact_hash=scaffold["artifact_hash"],
        teacher_approved=True, registry_store_path=registry_store,
    )
    assert first["allowed_operations"] == operations
    assert second["allowed_operations"] == operations
    stored = json.loads(registry_store.read_text(encoding="utf-8"))
    assert list(stored) == [first["domain_key"]]
    assert stored[first["domain_key"]]["allowed_operations"] == operations
    memory = list_verified_bootstrap_providers()
    assert list(memory) == [first["domain_key"]]
    assert memory[first["domain_key"]]["allowed_operations"] == operations
    assert sorted(p.name for p in verified_root.iterdir()) == [gap.gap_id]


def test_nth_operation_validation_failure_leaves_verified_state_unchanged(
    isolated_store: CandidateStore,
    registry_store: Path,
    monkeypatch: pytest.MonkeyPatch,
    isolated_verified_memory: None,
) -> None:
    verified_root = isolated_store.bootstrap_root / "verified_domains"
    monkeypatch.setattr("core.gencode.domain_bootstrap.promotion_service.VERIFIED_DOMAIN_ROOT", verified_root)
    capabilities = ["fixture_capability_a", "fixture_capability_b", "fixture_capability_c"]
    exc = _gap_exc(DOMAIN_CAPABILITY_UNRESOLVED, capabilities=capabilities)
    gap = detect_or_reuse_domain_gap(
        store=isolated_store, error_code=exc.code, error_details=exc.details,
        skill_id="fixture_skill_alpha", textbook_example_id=99001, component_id="src_99001",
    )
    from core.gencode.domain_bootstrap.scaffold_builder import build_candidate_scaffold

    scaffold = build_candidate_scaffold(store=isolated_store, gap_report=gap)
    operations = ["fixture_operation_a", "fixture_operation_b", "fixture_operation_c"]
    _write_multi_operation_manifest(isolated_store, gap.gap_id, operations)
    domain_path = isolated_store.candidate_dir(gap.gap_id) / "domain_module.py"
    domain_path.write_text(domain_path.read_text(encoding="utf-8").replace(
        "constraints = dict(constraints or {})",
        "constraints = dict(constraints or {})\n    if domain_operation == 'fixture_operation_c':\n        raise RuntimeError('forced_nth_operation_failure')",
    ), encoding="utf-8")
    before = _production_state(registry_store, verified_root)
    validation = validate_candidate_domain(store=isolated_store, gap_report=gap)
    assert validation["passed"] is False
    assert any("fixture_operation_c" in blocker for blocker in validation["blockers"])
    with pytest.raises(PromotionError, match="candidate gate not passed"):
        promote_candidate_to_verified(
            store=isolated_store, gap_report=gap, artifact_hash=scaffold["artifact_hash"],
            teacher_approved=True, registry_store_path=registry_store,
        )
    assert _production_state(registry_store, verified_root) == before
    assert not (verified_root / gap.gap_id).exists()


def _tree_digest(root: Path) -> dict[str, bytes]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def _production_state(registry_store: Path, verified_root: Path) -> dict[str, object]:
    return {
        "registry": registry_store.read_bytes() if registry_store.exists() else None,
        "memory": list_verified_bootstrap_providers(),
        "verified": _tree_digest(verified_root),
    }


@pytest.fixture
def isolated_verified_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    from core.gencode.domain_bootstrap import candidate_registry

    monkeypatch.setattr(candidate_registry, "_verified_providers", {})


def _prepare_operation_candidate(
    store: CandidateStore, operations: list[str] | None
) -> tuple[object, dict]:
    from core.gencode.domain_bootstrap.scaffold_builder import build_candidate_scaffold

    capabilities = ["fixture_capability_a", "fixture_capability_b", "fixture_capability_c"]
    exc = _gap_exc(DOMAIN_CAPABILITY_UNRESOLVED, capabilities=capabilities)
    gap = detect_or_reuse_domain_gap(
        store=store, error_code=exc.code, error_details=exc.details,
        skill_id="fixture_skill_alpha", textbook_example_id=99001, component_id="src_99001",
    )
    scaffold = build_candidate_scaffold(store=store, gap_report=gap)
    if operations is not None:
        _write_multi_operation_manifest(store, gap.gap_id, operations)
    return gap, scaffold


def _seed_unrelated_verified_provider(registry_store: Path) -> None:
    from core.gencode.domain_bootstrap.candidate_registry import (
        VerifiedCandidateProvider,
        register_verified_candidate,
    )

    register_verified_candidate(
        VerifiedCandidateProvider(
            domain_key="candidate.fixture_unrelated",
            domain_module="agent_domains_verified.fixture_unrelated.domain_module",
            entrypoint="build_fixture_matrix",
            capabilities=frozenset({"fixture_unrelated_capability"}),
            allowed_operations=("fixture_unrelated_operation",),
            gap_id="fixture_unrelated",
            artifact_hash="fixture-unrelated-hash",
            registry_revision="bootstrap-fixture",
        ),
        store_path=registry_store,
    )


@pytest.mark.parametrize("failure_mode", ["registry_written_then_fail", "registry_truncated", "artifact_copy"])
def test_promotion_time_failure_rolls_back_all_multi_operation_state(
    isolated_store: CandidateStore,
    registry_store: Path,
    monkeypatch: pytest.MonkeyPatch,
    isolated_verified_memory: None,
    failure_mode: str,
) -> None:
    from core.gencode.domain_bootstrap import candidate_registry, promotion_service

    verified_root = isolated_store.bootstrap_root / "verified_domains"
    monkeypatch.setattr(promotion_service, "VERIFIED_DOMAIN_ROOT", verified_root)
    operations = ["fixture_operation_a", "fixture_operation_b", "fixture_operation_c"]
    gap, scaffold = _prepare_operation_candidate(isolated_store, operations)
    _seed_unrelated_verified_provider(registry_store)
    before = _production_state(registry_store, verified_root)

    if failure_mode == "artifact_copy":
        real_copytree = shutil.copytree
        candidate_dir = isolated_store.candidate_dir(gap.gap_id)

        def _failing_copytree(src, dst, *args, **kwargs):
            result = real_copytree(src, dst, *args, **kwargs)
            if Path(src) == candidate_dir:
                raise OSError("forced_artifact_copy_failure")
            return result

        monkeypatch.setattr(promotion_service.shutil, "copytree", _failing_copytree)
    else:
        real_save = candidate_registry._save_store

        def _failing_save(path, payload):
            if failure_mode == "registry_truncated":
                Path(path).write_text('{"partial": ', encoding="utf-8")
            else:
                real_save(path, payload)
            raise OSError("forced_registry_write_failure")

        monkeypatch.setattr(candidate_registry, "_save_store", _failing_save)

    with pytest.raises(PromotionError) as raised:
        promote_candidate_to_verified(
            store=isolated_store, gap_report=gap, artifact_hash=scaffold["artifact_hash"],
            teacher_approved=True, registry_store_path=registry_store,
        )
    assert raised.value.code == "promotion_failed"
    assert _production_state(registry_store, verified_root) == before
    assert not (verified_root / gap.gap_id).exists()
    assert not (verified_root / f"{gap.gap_id}.rollback").exists()


def test_repromotion_failure_restores_previous_verified_capability(
    isolated_store: CandidateStore,
    registry_store: Path,
    monkeypatch: pytest.MonkeyPatch,
    isolated_verified_memory: None,
) -> None:
    from core.gencode.domain_bootstrap import candidate_registry, promotion_service

    verified_root = isolated_store.bootstrap_root / "verified_domains"
    monkeypatch.setattr(promotion_service, "VERIFIED_DOMAIN_ROOT", verified_root)
    old_operations = ["fixture_operation_a", "fixture_operation_b"]
    gap, scaffold = _prepare_operation_candidate(isolated_store, old_operations)
    promote_candidate_to_verified(
        store=isolated_store, gap_report=gap, artifact_hash=scaffold["artifact_hash"],
        teacher_approved=True, registry_store_path=registry_store,
    )
    before = _production_state(registry_store, verified_root)

    _write_multi_operation_manifest(
        isolated_store, gap.gap_id, ["fixture_operation_a", "fixture_operation_b", "fixture_operation_c"]
    )

    def _failing_save(path, payload):
        raise OSError("forced_registry_write_failure")

    monkeypatch.setattr(candidate_registry, "_save_store", _failing_save)
    with pytest.raises(PromotionError, match="forced_registry_write_failure"):
        promote_candidate_to_verified(
            store=isolated_store, gap_report=gap, artifact_hash=scaffold["artifact_hash"],
            teacher_approved=True, registry_store_path=registry_store,
        )
    after = _production_state(registry_store, verified_root)
    assert after == before
    (domain_key,) = after["memory"].keys()
    assert after["memory"][domain_key]["allowed_operations"] == old_operations
    assert not (verified_root / f"{gap.gap_id}.rollback").exists()


def test_single_operation_promotion_backward_compatible(
    isolated_store: CandidateStore,
    registry_store: Path,
    monkeypatch: pytest.MonkeyPatch,
    isolated_verified_memory: None,
) -> None:
    verified_root = isolated_store.bootstrap_root / "verified_domains"
    monkeypatch.setattr("core.gencode.domain_bootstrap.promotion_service.VERIFIED_DOMAIN_ROOT", verified_root)
    gap, scaffold = _prepare_operation_candidate(isolated_store, None)
    manifest = json.loads(isolated_store.read_candidate_file(gap.gap_id, "domain_manifest.json"))
    assert len(manifest["operations"]) == 1
    (operation,) = manifest["operations"]

    validation = validate_candidate_domain(store=isolated_store, gap_report=gap)
    assert validation["passed"] is True
    assert {row["operation"] for row in validation["seed_results"]} == {operation}

    first = promote_candidate_to_verified(
        store=isolated_store, gap_report=gap, artifact_hash=scaffold["artifact_hash"],
        teacher_approved=True, registry_store_path=registry_store,
    )
    state_after_first = _production_state(registry_store, verified_root)
    second = promote_candidate_to_verified(
        store=isolated_store, gap_report=gap, artifact_hash=scaffold["artifact_hash"],
        teacher_approved=True, registry_store_path=registry_store,
    )
    assert first["allowed_operations"] == second["allowed_operations"] == [operation]
    memory = list_verified_bootstrap_providers()
    assert list(memory) == [first["domain_key"]]
    assert memory[first["domain_key"]]["allowed_operations"] == [operation]
    assert _production_state(registry_store, verified_root)["verified"] == state_after_first["verified"]
    stored = json.loads(registry_store.read_text(encoding="utf-8"))
    assert list(stored) == [first["domain_key"]]


def test_verified_promotion_retries_only_affected_components() -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE textbook_examples (id INTEGER PRIMARY KEY, skill_id TEXT NOT NULL)")
    conn.execute(
        """
        CREATE TABLE gencode_component_tracker (
            textbook_example_id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            component_id TEXT NOT NULL,
            gencode_status TEXT NOT NULL,
            induced_spec_payload TEXT,
            gencode_error_log TEXT
        )
        """
    )
    conn.execute("INSERT INTO textbook_examples VALUES (101, 'fixture_skill_alpha')")
    conn.execute("INSERT INTO textbook_examples VALUES (102, 'fixture_skill_alpha')")
    conn.execute(
        "INSERT INTO gencode_component_tracker VALUES (101, 'fixture_skill_alpha', 'src_101', 'needs_human_review', ?, ?)",
        (
            json.dumps({"error_code": DOMAIN_CAPABILITY_UNRESOLVED}),
            DOMAIN_CAPABILITY_UNRESOLVED,
        ),
    )
    conn.execute(
        "INSERT INTO gencode_component_tracker VALUES (102, 'fixture_skill_alpha', 'src_102', 'verified', '{}', '')",
    )
    gap = build_gap_report_from_resolver_error(
        error_code=DOMAIN_CAPABILITY_UNRESOLVED,
        error_details={"required_capabilities": [ABSTRACT_FIXTURE_CAPABILITY]},
        skill_id="fixture_skill_alpha",
        textbook_example_id=101,
        component_id="src_101",
    )

    calls: list[int] = []

    def _runner(**kwargs):
        calls.append(int(kwargs["textbook_example_id"]))
        return {"status": "processed"}

    result = retry_affected_components(conn, gap_report=gap, dryrun_runner=_runner)
    assert calls == [101]
    assert result["success_count"] == 1


def test_single_gap_failure_does_not_block_other_skill_retry() -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE gencode_component_tracker (
            textbook_example_id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            component_id TEXT NOT NULL,
            gencode_status TEXT NOT NULL,
            induced_spec_payload TEXT,
            gencode_error_log TEXT
        )
        """
    )
    conn.execute(
        "INSERT INTO gencode_component_tracker VALUES (201, 'fixture_skill_alpha', 'src_201', 'failed', ?, ?)",
        (json.dumps({"error_code": DOMAIN_CAPABILITY_UNRESOLVED}), DOMAIN_CAPABILITY_UNRESOLVED),
    )
    conn.execute(
        "INSERT INTO gencode_component_tracker VALUES (202, 'fixture_skill_beta', 'src_202', 'failed', ?, ?)",
        (json.dumps({"error_code": DOMAIN_CAPABILITY_UNRESOLVED}), DOMAIN_CAPABILITY_UNRESOLVED),
    )
    gap = build_gap_report_from_resolver_error(
        error_code=DOMAIN_CAPABILITY_UNRESOLVED,
        error_details={"required_capabilities": [ABSTRACT_FIXTURE_CAPABILITY]},
        skill_id="fixture_skill_alpha",
        textbook_example_id=201,
        component_id="src_201",
    )

    def _runner(**kwargs):
        if kwargs["skill_id"] == "fixture_skill_beta":
            raise RuntimeError("should_not_retry_other_skill")
        return {"status": "processed"}

    result = retry_affected_components(conn, gap_report=gap, dryrun_runner=_runner)
    assert result["affected_count"] == 1


@pytest.mark.parametrize(
    "relative_path",
    [
        "core/gencode/domain_bootstrap/gap_service.py",
        "core/gencode/domain_bootstrap/orchestrator.py",
        "core/gencode/domain_bootstrap/healer.py",
        "core/gencode/domain_bootstrap/validation_runner.py",
    ],
)
def test_production_bootstrap_modules_have_no_skill_literals(relative_path: str) -> None:
    path = PROJECT_ROOT / relative_path
    content = path.read_text(encoding="utf-8")
    assert "CentralTendency" not in content
    assert "3835" not in content
    assert "3887" not in content
