# -*- coding: utf-8 -*-
"""Reviewed workspace -> production capability promotion (generic, fixture-only)."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.gencode import reviewed_capability_promotion as promotion
from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.reviewed_capability_promotion import CapabilityPromotionError, promote_reviewed_workspace
from core.gencode.skill_fixed_domain_authority import DOMAIN_PROVIDERS, resolve_domain_authority
from core.registry import domain_operation_registry as registry
from core.registry import promoted_capability_store as store_mod
from core.registry import taxonomy_registry as taxonomy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_SKILL = "vh_數學B1_PointSlopeForm"
OPS_3 = ["fixture_sum", "fixture_product", "fixture_difference"]

DOMAIN_TEMPLATE = '''import random

OPS = {ops!r}
FAILING = {failing!r}


def build_fixture_matrix(*, domain_operation=None, seed=None, constraints=None, **_):
    op = str(domain_operation or "")
    if op not in OPS:
        raise ValueError(f"unsupported_fixture_operation:{{op}}")
    if op == FAILING:
        raise RuntimeError("forced_fixture_operation_failure")
    rng = random.Random(0 if seed is None else int(seed))
    a, b = rng.randint(1, 9), rng.randint(1, 9)
    value = {{"fixture_sum": a + b, "fixture_product": a * b}}.get(op, a - b)
    return {{
        "domain_operation": op,
        "givens": {{"a": a, "b": b}},
        "answer": {{"value": value}},
        "validation_facts": {{"domain_operation": op, "seed": seed}},
    }}


def validate_fixture_matrix(matrix):
    facts = matrix["validation_facts"]
    return build_fixture_matrix(domain_operation=facts["domain_operation"], seed=facts["seed"]) == matrix
'''

ADAPTER_TEMPLATE = '''{import_line}

CHECKER = {checker!r}


def adapt_fixture_matrix(matrix, *, domain_operation, **kwargs):
    if domain_operation not in OPS:
        raise ValueError(domain_operation)
    value = str(matrix["answer"]["value"])
    return {{
        "question_text": f"{{domain_operation}}:{{matrix['givens']}}",
        "answer": value,
        "correct_answer": value,
        "answer_type": "short_answer",
        "answer_contract": {{"answer_type": "short_answer", "checker_key": CHECKER}},
    }}
'''


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree(root: Path) -> dict[str, bytes]:
    if not root.exists():
        return {}
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts
    }


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch):
    run = uuid.uuid4().hex[:10]
    base = PROJECT_ROOT / "temp" / f"pytest_capability_promotion_{run}"
    import_root = base / "importroot"
    prefix = f"pytest_promoted_{run}"
    package_root = import_root / prefix
    package_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    monkeypatch.syspath_prepend(str(import_root))
    ns = SimpleNamespace(
        run=run,
        base=base,
        prefix=prefix,
        package_root=package_root,
        store=base / "store" / "promoted_capabilities.json",
        snapshots=[],
    )
    try:
        yield ns
    finally:
        for snapshot in reversed(ns.snapshots):
            store_mod.restore_runtime_state(snapshot)
        for name in [n for n in sys.modules if n == prefix or n.startswith(prefix + ".")]:
            sys.modules.pop(name, None)
        shutil.rmtree(base, ignore_errors=True)


def _names(env, tag: str) -> SimpleNamespace:
    names = SimpleNamespace(
        domain_key=f"fixture_domain_{tag}.ops_{env.run}",
        skill_id=f"fixture_skill_{tag}_{env.run}",
        package_name=f"fixture_pkg_{tag}_{env.run}",
    )
    env.snapshots.append(
        store_mod.snapshot_runtime_state(
            names.domain_key, [names.skill_id, STATIC_SKILL], f"{env.prefix}.{names.package_name}"
        )
    )
    return names


def _workspace(
    env,
    names,
    operations: list[str],
    *,
    revision: int = 1,
    failing: str | None = None,
    checker: str = "integer_checker",
    local_import: bool = False,
    mutate=None,
) -> Path:
    ws = env.base / "workspaces" / names.package_name / f"revision_{revision:04d}"
    pkg = ws / "production_package"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "domain.py").write_text(DOMAIN_TEMPLATE.format(ops=tuple(operations), failing=failing), encoding="utf-8")
    import_line = "from domain import OPS" if local_import else "from .domain import OPS"
    (pkg / "adapter.py").write_text(ADAPTER_TEMPLATE.format(import_line=import_line, checker=checker), encoding="utf-8")
    bundle = {
        "schema": "reviewed_capability_bundle.v1",
        "proposal_id": f"capability_fixture_{env.run}",
        "proposal_revision": revision,
        "review": {"status": "human_approved", "approved_by": "fixture_reviewer", "approved_revision": revision},
        "domain_key": names.domain_key,
        "package_name": names.package_name,
        "package_dir": "production_package",
        "files": {name: _sha(pkg / name) for name in ("__init__.py", "domain.py", "adapter.py")},
        "domain_module": "domain",
        "entrypoint": "build_fixture_matrix",
        "capabilities": list(operations),
        "operations": {
            op: {
                "validator": "validate_fixture_matrix",
                "payload_adapter": "adapter.adapt_fixture_matrix",
                "checker_keys": [checker],
                "supported_answer_types": ["short_answer"],
            }
            for op in operations
        },
        "skill_bindings": {names.skill_id: {"default_curriculum_profile": "general_high"}},
        "smoke_cases": {op: [{"seed": 7}, {"seed": 42, "constraints": {}}] for op in operations},
    }
    if mutate:
        mutate(bundle, pkg)
    (ws / "promotion_bundle.json").write_text(json.dumps(bundle, ensure_ascii=False), encoding="utf-8")
    return ws


def _promote(env, ws):
    return promote_reviewed_workspace(
        ws,
        teacher_approved=True,
        store_path=env.store,
        package_root=env.package_root,
        package_import_prefix=env.prefix,
    )


def _state(env, names) -> dict:
    spec = registry.get_domain_spec(names.domain_key)
    provider = DOMAIN_PROVIDERS.get(names.domain_key)
    package_import = f"{env.prefix}.{names.package_name}"
    return {
        "store": env.store.read_bytes() if env.store.exists() else None,
        "package_tree": _tree(env.package_root),
        "registry": None if spec is None else (spec.domain_module, sorted(spec.allowed_operations)),
        "allowed": taxonomy.DOMAIN_ALLOWED_OPERATIONS.get(names.domain_key),
        "provider": None if provider is None else sorted(provider["allowed_operations"]),
        "routing": taxonomy.SKILL_TO_DOMAIN.get(names.skill_id),
        "profile": taxonomy.SKILL_DOMAIN_PROFILE.get(names.skill_id),
        "static_routing": taxonomy.SKILL_TO_DOMAIN.get(STATIC_SKILL),
        "modules": sorted(n for n in sys.modules if n == package_import or n.startswith(package_import + ".")),
    }


def _assert_no_leftovers(env, names) -> None:
    assert not (env.package_root / f".{names.package_name}.staging").exists()
    assert not (env.package_root / f".{names.package_name}.rollback").exists()


def _assert_capability_live(names, operations: list[str]) -> None:
    binding = taxonomy.get_confirmed_skill_binding(names.skill_id)
    assert binding["fixed_domain_key"] == names.domain_key
    assert binding["default_curriculum_profile"] == "general_high"
    assert set(taxonomy.get_allowed_operations(names.domain_key, skill_id=names.skill_id)) == set(operations)
    assert set(DOMAIN_PROVIDERS[names.domain_key]["allowed_operations"]) == set(operations)
    for op in operations:
        resolved = resolve_domain_authority(names.skill_id, selected_operation=op)
        assert (resolved.fixed_domain_key, resolved.selected_operation) == (names.domain_key, op)
        matrix, payload = dispatch_registered_operation(names.domain_key, op, seed=5)
        assert matrix["domain_operation"] == op
        assert payload["answer_contract"]["checker_key"] == "integer_checker"
        assert payload["correct_answer"] == str(matrix["answer"]["value"])


def test_single_operation_promotion_binds_skill_and_dispatches(env) -> None:
    names = _names(env, "single")
    result = _promote(env, _workspace(env, names, ["fixture_sum"]))
    assert result["promoted"] is True and result["unchanged"] is False
    assert result["allowed_operations"] == ["fixture_sum"]
    _assert_capability_live(names, ["fixture_sum"])
    _assert_no_leftovers(env, names)


def test_multi_operation_promotion_registers_every_operation(env) -> None:
    names = _names(env, "multi")
    ws = _workspace(env, names, OPS_3)
    result = _promote(env, ws)
    assert result["allowed_operations"] == sorted(OPS_3)
    assert result["operations_executed"] == {op: 2 for op in OPS_3}
    _assert_capability_live(names, OPS_3)
    stored = json.loads(env.store.read_text(encoding="utf-8"))["domains"]
    assert list(stored) == [names.domain_key]
    assert set(stored[names.domain_key]["operations"]) == set(OPS_3)
    assert _tree(env.package_root / names.package_name) == _tree(ws / "production_package")
    assert registry.check_registry_consistency() == []


def _tamper(bundle, pkg):
    (pkg / "adapter.py").write_text("# changed after review\n", encoding="utf-8")


def _extra_file(bundle, pkg):
    (pkg / "unreviewed.py").write_text("X = 1\n", encoding="utf-8")


def _drop_smoke(bundle, pkg):
    bundle["smoke_cases"].pop(OPS_3[-1])


@pytest.mark.parametrize(
    ("case", "kwargs", "expected"),
    [
        ("unapproved", {"mutate": lambda b, p: b["review"].update(status="pending")}, "human_review_not_approved"),
        ("revision_mismatch", {"mutate": lambda b, p: b["review"].update(approved_revision=99)}, "approved_revision_mismatch"),
        ("tampered_file", {"mutate": _tamper}, "package_file_hash_mismatch:adapter.py"),
        ("unreviewed_file", {"mutate": _extra_file}, "package_unreviewed_file:unreviewed.py"),
        ("unregistered_checker", {"checker": "fixture_unknown_checker"}, "checker_not_registered:"),
        ("workspace_local_import", {"local_import": True}, "workspace_local_import:adapter.py:domain"),
        ("missing_smoke_case", {"mutate": _drop_smoke}, f"smoke_cases_missing:{OPS_3[-1]}"),
        ("static_domain_conflict", {"mutate": lambda b, p: b.update(domain_key="vector.plane")}, "domain_conflict_static"),
        (
            "static_skill_conflict",
            {"mutate": lambda b, p: b.update(skill_bindings={STATIC_SKILL: {"default_curriculum_profile": "general_high"}})},
            f"skill_binding_conflict_static:{STATIC_SKILL}",
        ),
    ],
)
def test_preflight_blockers_leave_production_state_unchanged(env, case, kwargs, expected) -> None:
    names = _names(env, case)
    ws = _workspace(env, names, OPS_3, **kwargs)
    before = _state(env, names)
    with pytest.raises(CapabilityPromotionError) as raised:
        _promote(env, ws)
    assert raised.value.code == "preflight_failed"
    assert any(blocker.startswith(expected) for blocker in raised.value.details["blockers"])
    assert _state(env, names) == before


def test_promotion_requires_teacher_approval(env) -> None:
    names = _names(env, "noapprove")
    ws = _workspace(env, names, OPS_3)
    before = _state(env, names)
    with pytest.raises(CapabilityPromotionError) as raised:
        promote_reviewed_workspace(ws, teacher_approved=False, store_path=env.store, package_root=env.package_root, package_import_prefix=env.prefix)
    assert raised.value.code == "teacher_not_approved"
    assert _state(env, names) == before


def test_nth_operation_failure_during_promotion_rolls_back_everything(env) -> None:
    other = _names(env, "other")
    _promote(env, _workspace(env, other, ["fixture_sum"]))
    names = _names(env, "nth")
    ws = _workspace(env, names, OPS_3, failing=OPS_3[-1])
    before, other_before = _state(env, names), _state(env, other)
    with pytest.raises(CapabilityPromotionError) as raised:
        _promote(env, ws)
    assert raised.value.code == "post_promotion_verification_failed"
    assert raised.value.details["rolled_back"] is True
    assert any(OPS_3[-1] in b for b in raised.value.details["blockers"])
    assert _state(env, names) == before
    assert _state(env, other) == other_before
    _assert_capability_live(other, ["fixture_sum"])
    _assert_no_leftovers(env, names)


@pytest.mark.parametrize("failure", ["store_partial_write", "package_copy"])
def test_write_failures_roll_back_everything(env, monkeypatch, failure) -> None:
    other = _names(env, "keep")
    _promote(env, _workspace(env, other, ["fixture_sum"]))
    names = _names(env, failure)
    ws = _workspace(env, names, OPS_3)
    before = _state(env, names)
    real_write, real_copytree = store_mod.write_store_atomic, shutil.copytree
    if failure == "store_partial_write":
        def _broken_write(path, payload):
            Path(path).write_text('{"schema": "promoted_capability_store.v1", "domains": {', encoding="utf-8")
            raise OSError("forced_store_write_failure")

        monkeypatch.setattr(store_mod, "write_store_atomic", _broken_write)
    else:
        def _broken_copytree(src, dst, *args, **kwargs):
            real_copytree(src, dst, *args, **kwargs)
            raise OSError("forced_package_copy_failure")

        monkeypatch.setattr(promotion.shutil, "copytree", _broken_copytree)
    with pytest.raises(CapabilityPromotionError) as raised:
        _promote(env, ws)
    assert raised.value.details["rolled_back"] is True
    monkeypatch.setattr(store_mod, "write_store_atomic", real_write)
    monkeypatch.setattr(promotion.shutil, "copytree", real_copytree)
    assert _state(env, names) == before
    _assert_capability_live(other, ["fixture_sum"])
    _assert_no_leftovers(env, names)


def test_failed_repromotion_restores_previous_revision(env) -> None:
    names = _names(env, "rev")
    _promote(env, _workspace(env, names, OPS_3[:2], revision=1))
    before = _state(env, names)
    with pytest.raises(CapabilityPromotionError) as raised:
        _promote(env, _workspace(env, names, OPS_3, revision=2, failing=OPS_3[-1]))
    assert raised.value.details["rolled_back"] is True
    assert _state(env, names) == before
    _assert_capability_live(names, OPS_3[:2])
    _assert_no_leftovers(env, names)


def test_successful_repromotion_replaces_revision_cleanly(env) -> None:
    names = _names(env, "upgrade")
    first = _promote(env, _workspace(env, names, OPS_3[:2], revision=1))
    second = _promote(env, _workspace(env, names, OPS_3, revision=2))
    assert first["registry_revision"] != second["registry_revision"]
    _assert_capability_live(names, OPS_3)
    stored = json.loads(env.store.read_text(encoding="utf-8"))["domains"]
    assert list(stored) == [names.domain_key]
    assert stored[names.domain_key]["proposal_revision"] == 2
    _assert_no_leftovers(env, names)


def test_idempotent_rerun_does_not_touch_production_state(env) -> None:
    names = _names(env, "idem")
    ws = _workspace(env, names, OPS_3)
    _promote(env, ws)
    first_state = _state(env, names)
    rerun = _promote(env, ws)
    assert rerun["unchanged"] is True
    assert _state(env, names) == first_state
    stored = json.loads(env.store.read_text(encoding="utf-8"))["domains"]
    assert list(stored) == [names.domain_key]
    _assert_capability_live(names, OPS_3)


def test_startup_loaders_rebuild_promoted_capability_from_store(env) -> None:
    names = _names(env, "startup")
    _promote(env, _workspace(env, names, OPS_3))
    store_mod.remove_promoted_entry(names.domain_key, json.loads(env.store.read_text(encoding="utf-8"))["domains"][names.domain_key])
    assert registry.get_domain_spec(names.domain_key) is None

    assert store_mod.register_promoted_domain_specs(env.store) == [names.domain_key]
    assert set(registry.get_domain_operations(names.domain_key)) == set(OPS_3)
    assert store_mod.register_promoted_domain_specs(env.store) == []

    routing, profiles = store_mod.promoted_skill_bindings(env.store, existing_skills=frozenset())
    assert routing[names.skill_id]["fixed_domain_key"] == names.domain_key
    assert set(routing[names.skill_id]["allowed_types"]) == set(OPS_3)
    assert profiles[names.skill_id]["curriculum_profile"] == "general_high"
    assert store_mod.promoted_skill_bindings(env.store, existing_skills=frozenset({names.skill_id})) == ({}, {})


def test_missing_store_registers_nothing(env) -> None:
    missing = env.base / "no_such_store.json"
    assert store_mod.register_promoted_domain_specs(missing) == []
    assert store_mod.promoted_skill_bindings(missing) == ({}, {})
