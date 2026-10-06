# -*- coding: utf-8 -*-
"""Revision 0001 review evidence for number_system.real_numbers: formal preflight plus an
isolated (temp-store) promotion.  Nothing here writes the production store or package root.
"""

from __future__ import annotations

import importlib
import json
import shutil
import sys
import uuid
from fractions import Fraction
from math import isqrt
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.gencode.answer_payload import validate_answer_contract_consistency
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.reviewed_capability_promotion import BUNDLE_FILENAME, preflight_reviewed_bundle, promote_reviewed_workspace
from core.gencode.runtime_skill_wrapper import check_answer
from core.registry import promoted_capability_store as store_mod
from core.registry.domain_operation_registry import get_domain_spec

REVISION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = REVISION_DIR.parents[3]
PRODUCTION_STORE = PROJECT_ROOT / "configs" / "gencode_promoted_capabilities.json"
DOMAIN_KEY = "number_system.real_numbers"
SKILL_ID = "gh_IrrationalAndRealNumbers"
OPERATIONS = {"solve_rational_unknowns_from_radical_identity", "approximate_square_root_by_decimal_search"}
EXAMPLE_3 = {"radicand": 2, "coefficients": {"a": {"rational": 3, "radical": 5}, "b": {"rational": 2, "radical": -1}},
             "rhs": {"rational": -1, "radical": 7}}
PRACTICE_5 = {"radicand": 2, "coefficients": {"a": {"rational": 3, "radical": 2}, "b": {"rational": 2, "radical": -1}},
              "rhs": {"rational": 0, "radical": 7}}


def _production_package_names() -> list[str]:
    return sorted(p.name for p in (PROJECT_ROOT / "core" / "domain" / "promoted").iterdir() if p.name != "__pycache__")


@pytest.fixture(scope="module")
def promoted():
    production_store_bytes = PRODUCTION_STORE.read_bytes()
    production_before = _production_package_names()
    prefix_dir = f"real_numbers_revision_0001_{uuid.uuid4().hex[:10]}"
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
            store=json.loads(store.read_text(encoding="utf-8")),
            domain=importlib.import_module(f"{package_import}.real_numbers_domain"),
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


def test_formal_preflight_passes_with_new_domain_only():
    report = preflight_reviewed_bundle(REVISION_DIR)
    assert report["passed"], report["blockers"]
    bundle = report["bundle"]
    assert bundle["proposal_revision"] == 1 == bundle["review"]["approved_revision"]
    assert set(bundle["operations"]) == OPERATIONS
    assert list(bundle["skill_bindings"]) == [SKILL_ID]


def test_isolated_promotion_keeps_existing_domains(promoted):
    result = promoted.result
    assert result["promoted"] and not result["unchanged"]
    assert set(result["allowed_operations"]) == OPERATIONS == set(result["operations_executed"])
    assert set(get_domain_spec(DOMAIN_KEY).allowed_operations) == OPERATIONS
    production = json.loads(PRODUCTION_STORE.read_text(encoding="utf-8"))
    for key, entry in production["domains"].items():
        if key != DOMAIN_KEY:
            assert promoted.store["domains"][key] == entry


@pytest.mark.parametrize(
    "constraints, values",
    [(EXAMPLE_3, {"a": "1", "b": "-2"}), (PRACTICE_5, {"a": "2", "b": "-3"})],
)
def test_textbook_identities_solve_exactly_and_grade(promoted, constraints, values):
    matrix, payload = _dispatch("solve_rational_unknowns_from_radical_identity", **constraints)
    assert promoted.domain.validate_solve_rational_unknowns_from_radical_identity_matrix(matrix)
    contract = payload["answer_contract"]
    assert (contract["answer_type"], contract["checker_key"]) == ("multi_part", "multi_part_answer_checker")
    assert [p["checker"] for p in contract["parts"]] == ["rational_checker", "rational_checker"]
    assert validate_answer_contract_capability(contract)["checker_capability_status"] == "ok"
    assert validate_answer_contract_consistency(contract) == []
    expected = payload["correct_answer"]
    assert expected == values
    assert check_answer(expected, expected, payload=payload)
    assert check_answer({k: f"{v}.0" for k, v in expected.items()}, expected, payload=payload)
    assert not check_answer({"a": expected["b"], "b": expected["a"]}, expected, payload=payload)
    assert not check_multi_part_answer(dict(expected, b="0"), expected, payload=payload)["overall_correct"]


def test_example_3_question_text_matches_textbook(promoted):
    _, payload = _dispatch("solve_rational_unknowns_from_radical_identity", **EXAMPLE_3)
    assert payload["question_text"] == (
        "已知 a, b 是有理數，且 $\\left(3+5\\sqrt{2}\\right)a+\\left(2-\\sqrt{2}\\right)b=-1+7\\sqrt{2}$，求 a, b 的值。"
    )
    _, payload = _dispatch("solve_rational_unknowns_from_radical_identity", **PRACTICE_5)
    assert "=7\\sqrt{2}$" in payload["question_text"]


def test_dependent_identity_is_refused(promoted):
    dependent = {"radicand": 2, "coefficients": {"a": {"rational": 1, "radical": 2}, "b": {"rational": 2, "radical": 4}},
                 "rhs": {"rational": 1, "radical": 2}}
    with pytest.raises(ValueError):
        _dispatch("solve_rational_unknowns_from_radical_identity", **dependent)
    with pytest.raises(ValueError):
        _dispatch("solve_rational_unknowns_from_radical_identity", **dict(EXAMPLE_3, radicand=4))


@pytest.mark.parametrize(
    "radicand, places, approximation",
    [(3, 2, "1.73"), (2, 3, "1.414"), (5, 2, "2.23"), (7, 1, "2.6"), (10, 2, "3.16"), (11, 0, "3")],
)
def test_decimal_search_truncates_exactly(promoted, radicand, places, approximation):
    matrix, payload = _dispatch("approximate_square_root_by_decimal_search", radicand=radicand, places=places)
    assert promoted.domain.validate_approximate_square_root_by_decimal_search_matrix(matrix)
    assert payload["correct_answer"] == approximation
    scaled = isqrt(radicand * 100 ** places)
    assert Fraction(approximation) == Fraction(scaled, 10 ** places)
    assert len(matrix["answer"]["steps"]) == places + 1
    contract = payload["answer_contract"]
    assert (contract["answer_type"], contract["checker_key"]) == ("rational", "rational_checker")
    assert validate_answer_contract_capability(contract)["checker_capability_status"] == "ok"


def test_decimal_search_grading_is_exact(promoted):
    _, payload = _dispatch("approximate_square_root_by_decimal_search", radicand=5, places=2)
    expected = payload["correct_answer"]
    assert expected == "2.23"
    for accepted in ("2.23", "2.230"):
        assert check_answer(accepted, expected, payload=payload), accepted
    for rejected in ("2.24", "2.236", "2.2", "\\sqrt{5}", "2", "abc", ""):
        assert not check_answer(rejected, expected, payload=payload), rejected


def test_textbook_sqrt3_steps(promoted):
    matrix, _ = _dispatch("approximate_square_root_by_decimal_search", radicand=3, places=2)
    steps = matrix["answer"]["steps"]
    assert [(s["lower"], s["upper"]) for s in steps] == [("1", "2"), ("1.7", "1.8"), ("1.73", "1.74")]
    assert [(s["lower_square"], s["upper_square"]) for s in steps] == [("1", "4"), ("2.89", "3.24"), ("2.9929", "3.0276")]


def test_seeded_operations_are_deterministic_valid_and_checker_legal(promoted):
    for op in sorted(OPERATIONS):
        validator = getattr(promoted.domain, f"validate_{op}_matrix")
        seen = set()
        for seed in range(40):
            matrix, payload = _dispatch(op, seed=seed)
            assert _dispatch(op, seed=seed) == (matrix, payload)
            assert validator(matrix)
            assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"
            seen.add(json.dumps(matrix["givens"], sort_keys=True))
        assert len(seen) > 5, op
