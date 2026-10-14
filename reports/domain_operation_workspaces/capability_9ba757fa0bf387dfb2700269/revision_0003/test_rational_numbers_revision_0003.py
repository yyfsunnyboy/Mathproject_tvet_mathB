# -*- coding: utf-8 -*-
"""Revision 0003 review evidence: formal preflight plus an isolated (temp-store) promotion.

Revision 0003 adds only fraction_to_decimal_expansion on top of the published revision 0002.
Nothing here writes the production promoted store or the production package root.
"""

from __future__ import annotations

import importlib
import json
import shutil
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.reviewed_capability_promotion import (
    BUNDLE_FILENAME,
    load_reviewed_bundle,
    preflight_reviewed_bundle,
    promote_reviewed_workspace,
)
from core.registry import promoted_capability_store as store_mod
from core.registry.domain_operation_registry import get_domain_spec

REVISION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = REVISION_DIR.parents[3]
PRODUCTION_STORE = PROJECT_ROOT / "configs" / "gencode_promoted_capabilities.json"
DOMAIN_KEY = "number_system.rational_numbers"
SKILL_ID = "gh_RationalNumbers"
NEW_OPERATION = "fraction_to_decimal_expansion"
PREVIOUS_OPERATIONS = {
    "plot_rational_points_on_number_line",
    "evaluate_rationality_statements",
    "identify_rational_numbers",
}
READY_OPERATIONS = PREVIOUS_OPERATIONS | {NEW_OPERATION}
STILL_BLOCKED = {"construct_rational_between_bounds", "decimal_to_simplest_fraction"}


def _production_package_names() -> list[str]:
    return sorted(p.name for p in (PROJECT_ROOT / "core" / "domain" / "promoted").iterdir() if p.name != "__pycache__")


@pytest.fixture(scope="module")
def promoted():
    production_store_bytes = PRODUCTION_STORE.read_bytes()
    production_before = _production_package_names()
    run = uuid.uuid4().hex[:10]
    prefix_dir = f"rational_revision_0003_{run}"
    base = PROJECT_ROOT / "temp" / prefix_dir
    prefix = f"temp.{prefix_dir}.packages"
    package_root = base / "packages"
    package_root.mkdir(parents=True)
    workspace = base / "workspace"
    shutil.copytree(REVISION_DIR, workspace, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    store = base / "store" / "promoted_capabilities.json"
    store.parent.mkdir(parents=True)
    store.write_bytes(production_store_bytes)
    bundle = json.loads((workspace / BUNDLE_FILENAME).read_text(encoding="utf-8"))
    package_import = f"{prefix}.{bundle['package_name']}"
    snapshot = store_mod.snapshot_runtime_state(DOMAIN_KEY, [SKILL_ID], package_import)
    try:
        result = promote_reviewed_workspace(
            workspace,
            teacher_approved=True,
            store_path=store,
            package_root=package_root,
            package_import_prefix=prefix,
        )
        yield SimpleNamespace(
            bundle=bundle,
            result=result,
            domain=importlib.import_module(f"{package_import}.rational_numbers_domain"),
            adapter=importlib.import_module(f"{package_import}.rational_numbers_adapter"),
        )
    finally:
        store_mod.restore_runtime_state(snapshot)
        for name in [n for n in sys.modules if n == f"temp.{prefix_dir}" or n.startswith(f"temp.{prefix_dir}.")]:
            sys.modules.pop(name, None)
        shutil.rmtree(base, ignore_errors=True)
        assert PRODUCTION_STORE.read_bytes() == production_store_bytes
        assert _production_package_names() == production_before


def _dispatch(op: str, seed: int = 1, **constraints):
    return dispatch_registered_operation(DOMAIN_KEY, op, seed=seed, constraints=constraints)


def test_formal_preflight_passes_and_adds_only_the_new_operation():
    report = preflight_reviewed_bundle(REVISION_DIR)
    assert report["passed"], report["blockers"]
    bundle = report["bundle"]
    previous = load_reviewed_bundle(REVISION_DIR.parent / "revision_0002")
    assert bundle["proposal_revision"] == 3 == bundle["review"]["approved_revision"]
    assert set(bundle["operations"]) == READY_OPERATIONS
    assert set(bundle["skill_bindings"][SKILL_ID]["allowed_operations"]) == READY_OPERATIONS
    for op in PREVIOUS_OPERATIONS:
        assert bundle["operations"][op] == previous["operations"][op]
        assert bundle["smoke_cases"][op] == previous["smoke_cases"][op]
    assert bundle["files"]["rational_numbers_domain.py"] == previous["files"]["rational_numbers_domain.py"]
    assert bundle["files"]["__init__.py"] == previous["files"]["__init__.py"]


def test_isolated_promotion_exposes_four_operations(promoted):
    result = promoted.result
    assert result["promoted"] and not result["unchanged"]
    assert set(result["allowed_operations"]) == READY_OPERATIONS
    assert set(result["operations_executed"]) == READY_OPERATIONS
    assert set(result["skill_bindings"][SKILL_ID]["allowed_operations"]) == READY_OPERATIONS
    assert set(get_domain_spec(DOMAIN_KEY).allowed_operations) == READY_OPERATIONS


@pytest.mark.parametrize(
    "fractions, decimals, good, wrong",
    [
        (["11/40", "2/11"], ["0.275", "0.(18)"], ["0.275", "0.\\overline{18}"], ["0.275", "0.(81)"]),
        (["5/8", "1/7"], ["0.625", "0.(142857)"], ["0.625", "0.\\overline{142857}"], ["0.625", "0.142857"]),
        (["1/37", "9/22"], ["0.(027)", "0.4(09)"], ["0.\\overline{027}", "0.4\\overline{09}"], ["0.(027)", "0.(409)"]),
    ],
)
def test_fraction_to_decimal_expansion_payload_and_grading(promoted, fractions, decimals, good, wrong):
    matrix, payload = _dispatch(NEW_OPERATION, fractions=fractions)
    assert promoted.domain.validate_fraction_to_decimal_expansion_matrix(matrix)
    contract = payload["answer_contract"]
    assert (contract["answer_type"], contract["checker_key"]) == ("multi_part", "multi_part_answer_checker")
    assert validate_answer_contract_capability(contract)["checker_capability_status"] == "ok"
    assert [p["checker"] for p in contract["parts"]] == ["repeating_decimal_checker"] * 2
    assert [p["expected_answer"] for p in contract["parts"]] == decimals
    expected = payload["correct_answer"]
    assert check_multi_part_answer(expected, expected, payload=payload)["overall_correct"]
    assert check_multi_part_answer(dict(zip(expected, good)), expected, payload=payload)["overall_correct"]
    assert not check_multi_part_answer(dict(zip(expected, wrong)), expected, payload=payload)["overall_correct"]
    assert not check_multi_part_answer(dict(zip(expected, fractions)), expected, payload=payload)["overall_correct"]


def test_seeded_operations_are_deterministic_valid_and_checker_legal(promoted):
    for op in sorted(READY_OPERATIONS):
        validator = getattr(promoted.domain, f"validate_{op}_matrix")
        seen = set()
        for seed in range(40):
            matrix, payload = _dispatch(op, seed=seed)
            assert _dispatch(op, seed=seed) == (matrix, payload)
            assert validator(matrix)
            assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] != "blocked"
            seen.add(json.dumps(matrix["givens"], sort_keys=True))
        assert len(seen) > 10, op


def test_remaining_blocked_operations_stay_refused(promoted):
    for op in sorted(STILL_BLOCKED):
        assert op in promoted.adapter.CHECKER_BLOCKED_OPERATIONS
        with pytest.raises(Exception):
            _dispatch(op)
    assert NEW_OPERATION not in promoted.adapter.CHECKER_BLOCKED_OPERATIONS
