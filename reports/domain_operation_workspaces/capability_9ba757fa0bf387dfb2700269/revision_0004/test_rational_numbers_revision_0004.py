# -*- coding: utf-8 -*-
"""Revision 0004 review evidence: formal preflight plus an isolated (temp-store) promotion.

Revision 0004 adds decimal_to_simplest_fraction and construct_rational_between_bounds on top of
the published revision 0003.  Nothing here writes the production store or package root.
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
from core.gencode.runtime_skill_wrapper import check_answer
from core.registry import promoted_capability_store as store_mod
from core.registry.domain_operation_registry import get_domain_spec

REVISION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = REVISION_DIR.parents[3]
PRODUCTION_STORE = PROJECT_ROOT / "configs" / "gencode_promoted_capabilities.json"
DOMAIN_KEY = "number_system.rational_numbers"
SKILL_ID = "gh_RationalNumbers"
NEW_OPERATIONS = {"decimal_to_simplest_fraction", "construct_rational_between_bounds"}
PREVIOUS_OPERATIONS = {
    "plot_rational_points_on_number_line",
    "evaluate_rationality_statements",
    "identify_rational_numbers",
    "fraction_to_decimal_expansion",
}
READY_OPERATIONS = PREVIOUS_OPERATIONS | NEW_OPERATIONS


def _production_package_names() -> list[str]:
    return sorted(p.name for p in (PROJECT_ROOT / "core" / "domain" / "promoted").iterdir() if p.name != "__pycache__")


@pytest.fixture(scope="module")
def promoted():
    production_store_bytes = PRODUCTION_STORE.read_bytes()
    production_before = _production_package_names()
    prefix_dir = f"rational_revision_0004_{uuid.uuid4().hex[:10]}"
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
            workspace, teacher_approved=True, store_path=store, package_root=package_root, package_import_prefix=prefix,
        )
        yield SimpleNamespace(
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


def test_formal_preflight_passes_and_adds_only_the_two_operations():
    report = preflight_reviewed_bundle(REVISION_DIR)
    assert report["passed"], report["blockers"]
    bundle = report["bundle"]
    previous = load_reviewed_bundle(REVISION_DIR.parent / "revision_0003")
    assert bundle["proposal_revision"] == 4 == bundle["review"]["approved_revision"]
    assert set(bundle["operations"]) == READY_OPERATIONS
    assert set(bundle["skill_bindings"][SKILL_ID]["allowed_operations"]) == READY_OPERATIONS
    for op in PREVIOUS_OPERATIONS:
        assert bundle["operations"][op] == previous["operations"][op]
        assert bundle["smoke_cases"][op] == previous["smoke_cases"][op]
    assert bundle["files"]["rational_numbers_domain.py"] == previous["files"]["rational_numbers_domain.py"]
    assert bundle["files"]["__init__.py"] == previous["files"]["__init__.py"]


def test_isolated_promotion_exposes_six_operations(promoted):
    result = promoted.result
    assert result["promoted"] and not result["unchanged"]
    assert set(result["allowed_operations"]) == READY_OPERATIONS
    assert set(result["operations_executed"]) == READY_OPERATIONS
    assert set(get_domain_spec(DOMAIN_KEY).allowed_operations) == READY_OPERATIONS
    assert promoted.adapter.CHECKER_BLOCKED_OPERATIONS == {}


@pytest.mark.parametrize(
    "decimals, fractions",
    [
        (["0.28", "0.(32)", "1.4(5)"], ["7/25", "32/99", "131/90"]),
        (["0.732", "5.(12)", "0.1(58)"], ["183/250", "169/33", "157/990"]),
        (["0.(27)", "5.4(38)"], ["3/11", "2692/495"]),
    ],
)
def test_decimal_to_simplest_fraction_payload_and_grading(promoted, decimals, fractions):
    matrix, payload = _dispatch("decimal_to_simplest_fraction", decimals=decimals)
    assert promoted.domain.validate_decimal_to_simplest_fraction_matrix(matrix)
    contract = payload["answer_contract"]
    assert (contract["answer_type"], contract["checker_key"]) == ("multi_part", "multi_part_answer_checker")
    assert validate_answer_contract_capability(contract)["checker_capability_status"] == "ok"
    assert [p["checker"] for p in contract["parts"]] == ["simplest_fraction_checker"] * len(decimals)
    expected = payload["correct_answer"]
    assert list(expected.values()) == fractions
    assert check_answer(expected, expected, payload=payload)
    latex = {k: "\\frac{%s}{%s}" % tuple(v.split("/")) for k, v in expected.items()}
    assert check_answer(latex, expected, payload=payload)
    doubled = {k: "%d/%d" % tuple(2 * int(x) for x in v.split("/")) for k, v in expected.items()}
    assert not check_multi_part_answer(doubled, expected, payload=payload)["overall_correct"]
    assert not check_answer(dict(zip(expected, decimals)), expected, payload=payload)


def test_construct_rational_between_bounds_is_predicate_graded(promoted):
    matrix, payload = _dispatch("construct_rational_between_bounds", lower="3/2", upper="5/3")
    assert promoted.domain.validate_construct_rational_between_bounds_matrix(matrix)
    contract = payload["answer_contract"]
    assert (contract["answer_type"], contract["checker_key"]) == ("short_answer", "rational_between_bounds_checker")
    assert (contract["lower"], contract["upper"]) == ("3/2", "5/3")
    assert validate_answer_contract_capability(contract)["checker_capability_status"] == "ok"
    example = payload["correct_answer"]
    assert example == "19/12"
    for answer in ("19/12", "8/5", "1.6", "\\frac{8}{5}"):
        assert check_answer(answer, example, payload=payload), answer
    for answer in ("3/2", "5/3", "1.5", "2", "1"):
        assert not check_answer(answer, example, payload=payload), answer


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
