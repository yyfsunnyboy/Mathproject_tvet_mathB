# -*- coding: utf-8 -*-
"""Revision 0002 review evidence: formal preflight plus an isolated (temp-store) promotion.

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
from core.checkers.solution_set_checker import check_solution_set_answer
from core.gencode.answer_payload import validate_answer_contract_consistency
from core.gencode.checker_registry import CHECKER_CAPABILITIES, validate_answer_contract_capability
from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.reviewed_capability_promotion import (
    BUNDLE_FILENAME,
    preflight_reviewed_bundle,
    promote_reviewed_workspace,
)
from core.registry import promoted_capability_store as store_mod
from core.registry.domain_operation_registry import get_domain_spec
from core.registry.taxonomy_registry import get_confirmed_skill_binding

REVISION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = REVISION_DIR.parents[3]
DOMAIN_KEY = "number_system.rational_numbers"
SKILL_ID = "gh_RationalNumbers"
READY_OPERATIONS = {
    "plot_rational_points_on_number_line",
    "evaluate_rationality_statements",
    "identify_rational_numbers",
}
CHECKER_BLOCKED = {"fraction_to_decimal_expansion", "construct_rational_between_bounds", "decimal_to_simplest_fraction"}

STATEMENTS = [
    {"predicate": "is_irrational", "value": {"kind": "finite_decimal", "value": "1.414"}},
    {"predicate": "equals",
     "left": {"kind": "sum", "terms": [{"kind": "repeating_decimal", "value": "0.(4)"}, {"kind": "repeating_decimal", "value": "0.(6)"}]},
     "right": {"kind": "rational", "value": "1"}},
    {"predicate": "no_rational_between", "lower": "21/13", "upper": "35/21"},
    {"predicate": "all_irrational",
     "values": [{"kind": "sqrt", "radicand": 5}, {"kind": "sum", "terms": [{"kind": "rational", "value": "0"}, {"kind": "sqrt", "radicand": 5}]}]},
    {"predicate": "sqrt_difference_identity", "left_radicand": 3, "right_radicand": 5},
]
CANDIDATES = [
    {"kind": "rational", "value": "-4/9"},
    {"kind": "rational", "value": "0"},
    {"kind": "finite_decimal", "value": "3.14159"},
    {"kind": "sum", "terms": [{"kind": "rational", "value": "3"}, {"kind": "sqrt", "radicand": 2}]},
    {"kind": "sum", "terms": [{"kind": "rational", "value": "12/11"}, {"kind": "rational", "value": "11/12"}]},
]


def _production_package_names() -> list[str]:
    return sorted(p.name for p in (PROJECT_ROOT / "core" / "domain" / "promoted").iterdir() if p.name != "__pycache__")


@pytest.fixture(scope="module")
def promoted():
    assert not (PROJECT_ROOT / "configs" / "gencode_promoted_capabilities.json").exists()
    production_before = _production_package_names()
    run = uuid.uuid4().hex[:10]
    prefix_dir = f"rational_revision_0002_{run}"
    base = PROJECT_ROOT / "temp" / prefix_dir
    prefix = f"temp.{prefix_dir}.packages"
    package_root = base / "packages"
    package_root.mkdir(parents=True)
    workspace = base / "workspace"
    shutil.copytree(REVISION_DIR, workspace, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    bundle_path = workspace / BUNDLE_FILENAME
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle["review"] = {
        "status": "human_approved",
        "approved_by": "isolated_fixture_reviewer",
        "approved_revision": bundle["proposal_revision"],
    }
    bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    store = base / "store" / "promoted_capabilities.json"
    package_import = f"{prefix}.{bundle['package_name']}"
    snapshot = store_mod.snapshot_runtime_state(DOMAIN_KEY, [SKILL_ID], package_import)
    try:
        approved_preflight = preflight_reviewed_bundle(workspace, store_path=store)
        result = promote_reviewed_workspace(
            workspace,
            teacher_approved=True,
            store_path=store,
            package_root=package_root,
            package_import_prefix=prefix,
        )
        yield SimpleNamespace(
            bundle=bundle,
            approved_preflight=approved_preflight,
            result=result,
            store=store,
            domain=importlib.import_module(f"{package_import}.rational_numbers_domain"),
            adapter=importlib.import_module(f"{package_import}.rational_numbers_adapter"),
        )
    finally:
        store_mod.restore_runtime_state(snapshot)
        for name in [n for n in sys.modules if n == f"temp.{prefix_dir}" or n.startswith(f"temp.{prefix_dir}.")]:
            sys.modules.pop(name, None)
        shutil.rmtree(base, ignore_errors=True)
        assert get_domain_spec(DOMAIN_KEY) is None
        assert get_confirmed_skill_binding(SKILL_ID) is None
        assert not (PROJECT_ROOT / "configs" / "gencode_promoted_capabilities.json").exists()
        assert _production_package_names() == production_before


def _dispatch(op: str, seed: int = 1, **constraints):
    return dispatch_registered_operation(DOMAIN_KEY, op, seed=seed, constraints=constraints)


# --- formal preflight on the real revision (pending human review) -----------

def test_formal_preflight_blocks_only_on_pending_human_review():
    report = preflight_reviewed_bundle(REVISION_DIR)
    assert report["blockers"] == ["human_review_not_approved", "approved_revision_mismatch"]
    bundle = report["bundle"]
    assert set(bundle["operations"]) == READY_OPERATIONS
    assert set(bundle["capabilities"]) == READY_OPERATIONS
    assert set(bundle["smoke_cases"]) == READY_OPERATIONS
    assert set(bundle["skill_bindings"][SKILL_ID]["allowed_operations"]) == READY_OPERATIONS
    for op in bundle["operations"].values():
        assert all(CHECKER_CAPABILITIES[key]["runtime_available"] for key in op["checker_keys"])


def test_approved_copy_preflight_and_isolated_promotion_pass(promoted):
    assert promoted.approved_preflight["passed"], promoted.approved_preflight["blockers"]
    result = promoted.result
    assert result["promoted"] and not result["unchanged"]
    assert set(result["allowed_operations"]) == READY_OPERATIONS
    assert set(result["operations_executed"]) == READY_OPERATIONS
    assert result["skill_bindings"][SKILL_ID]["fixed_domain_key"] == DOMAIN_KEY
    assert set(result["skill_bindings"][SKILL_ID]["allowed_operations"]) == READY_OPERATIONS
    assert set(get_domain_spec(DOMAIN_KEY).allowed_operations) == READY_OPERATIONS


# --- semantic smoke through the registered dispatch -------------------------

def test_plot_number_line_semantic_coordinates_without_source_visual(promoted):
    matrix, payload = _dispatch("plot_rational_points_on_number_line", points=["3/5", "-3/5"])
    assert matrix["answer"]["ordered_points"] == ["-3/5", "3/5"]
    spec = payload["expected_drawing_spec"]
    assert spec["drawing_type"] == "number_line"
    assert [(p["label"], p["value"]) for p in spec["points"]] == [("A", "3/5"), ("B", "-3/5")]
    assert spec["ordered_labels"] == ["B", "A"]
    assert payload["answer_contract"]["checker_key"] == "free_response_drawing_checker"
    assert validate_answer_contract_consistency(payload["answer_contract"]) == []
    dumped = json.dumps(payload, ensure_ascii=False).lower()
    assert not any(token in dumped for token in ("12277", ".png", ".jpg", "asset", "source_image"))


def test_rationality_statements_truth_values(promoted):
    matrix, payload = _dispatch("evaluate_rationality_statements", statements=STATEMENTS)
    assert matrix["answer"]["truth_values"] == [False, False, False, True, False]
    expected = payload["correct_answer"]
    assert list(expected.values()) == ["錯誤", "錯誤", "錯誤", "正確", "錯誤"]
    by_label = {key: ("A" if value == "正確" else "B") for key, value in expected.items()}
    assert check_multi_part_answer(by_label, expected, payload=payload)["overall_correct"]
    flipped = dict(expected, statement_4="錯誤")
    assert not check_multi_part_answer(flipped, expected, payload=payload)["overall_correct"]


def test_identify_rational_numbers_is_unordered_solution_set(promoted):
    matrix, payload = _dispatch("identify_rational_numbers", candidates=CANDIDATES)
    assert matrix["answer"]["indices"] == promoted.domain.identify_rational_numbers(CANDIDATES) == [1, 2, 3, 5]
    contract = payload["answer_contract"]
    assert (contract["answer_type"], contract["presentation_mode"]) == ("short_answer", "short_answer")
    assert (payload["answer_type"], payload["presentation_mode"]) == ("short_answer", "short_answer")
    assert (contract["checker_key"], contract["equivalence_type"]) == ("solution_set_checker", "unordered_solution_set")
    assert validate_answer_contract_capability(contract)["checker_capability_status"] == "ok"
    for answer in ("(1)(2)(3)(5)", "1,2,3,5", "{1,2,3,5}", "5,3,2,1,1"):
        assert check_solution_set_answer(answer, payload["correct_answer"])
        assert check_answer(answer, payload["correct_answer"], payload=payload)
    for answer in ("1,2,3", "1,2,3,4,5", "(1)(2)(3)(5)(4)", "1235"):
        assert not check_solution_set_answer(answer, payload["correct_answer"])
        assert not check_answer(answer, payload["correct_answer"], payload=payload)
    changed = [dict(c) for c in CANDIDATES]
    changed[3] = {"kind": "sqrt", "radicand": 9}
    assert _dispatch("identify_rational_numbers", candidates=changed)[1]["correct_answer"] == [1, 2, 3, 4, 5]


def test_seeded_operations_are_deterministic_valid_and_checker_legal(promoted):
    validators = {op: getattr(promoted.domain, f"validate_{op}_matrix") for op in READY_OPERATIONS}
    for op in sorted(READY_OPERATIONS):
        seen = set()
        for seed in range(40):
            matrix, payload = _dispatch(op, seed=seed)
            assert _dispatch(op, seed=seed) == (matrix, payload)
            assert validators[op](matrix)
            contract = payload["answer_contract"]
            capability = validate_answer_contract_capability(contract)
            assert capability["checker_capability_status"] != "blocked", (op, capability)
            seen.add(json.dumps(matrix["givens"], sort_keys=True))
        assert len(seen) > 10, op


# --- checker-blocked operations: exact in the domain, refused by the adapter --

def test_fraction_to_decimal_expansion_exact_cycles_but_not_registered(promoted):
    domain = promoted.domain
    for fraction, decimal in (("11/40", "0.275"), ("2/11", "0.(18)"), ("1/37", "0.(027)"), ("9/22", "0.4(09)")):
        part = domain.fraction_to_decimal_expansion(fraction)
        assert part["decimal"] == decimal
        assert part["kind"] == ("terminating" if "(" not in decimal else "repeating")
    matrix = domain.build_rational_numbers_matrix(domain_operation="fraction_to_decimal_expansion", seed=3, constraints={"fractions": ["9/22"]})
    assert domain.validate_fraction_to_decimal_expansion_matrix(matrix)
    tampered = json.loads(json.dumps(matrix))
    tampered["answer"]["parts"][0].update(decimal="0.40(90)", nonrepeating="40", cycle="90")
    assert not domain.validate_fraction_to_decimal_expansion_matrix(tampered)
    with pytest.raises(ValueError, match="checker_capability_missing"):
        promoted.adapter.adapt_rational_numbers_matrix(matrix, domain_operation="fraction_to_decimal_expansion")


def test_decimal_to_simplest_fraction_exact_but_required_form_blocked(promoted):
    domain = promoted.domain
    matrix = domain.build_rational_numbers_matrix(
        domain_operation="decimal_to_simplest_fraction", seed=1, constraints={"decimals": ["0.28", "0.(32)", "1.4(5)", "-0.5"]}
    )
    assert [p["fraction"] for p in matrix["answer"]["parts"]] == ["7/25", "32/99", "131/90", "-1/2"]
    assert domain.validate_decimal_to_simplest_fraction_matrix(matrix)
    tampered = json.loads(json.dumps(matrix))
    tampered["answer"]["parts"][0].update(fraction="28/100", numerator=28, denominator=100)
    assert not domain.validate_decimal_to_simplest_fraction_matrix(tampered)
    with pytest.raises(ValueError, match="checker_required_form_blocked"):
        promoted.adapter.adapt_rational_numbers_matrix(matrix, domain_operation="decimal_to_simplest_fraction")


def test_strict_between_predicate_exact_but_not_registered(promoted):
    domain = promoted.domain
    matrix = domain.build_rational_numbers_matrix(domain_operation="construct_rational_between_bounds", seed=1, constraints={"lower": "3/2", "upper": "5/3"})
    assert matrix["answer"]["example"] == "19/12"
    assert domain.validate_construct_rational_between_bounds_matrix(matrix)
    assert domain.is_strictly_between("8/5", "3/2", "5/3")
    assert not domain.is_strictly_between("3/2", "3/2", "5/3")
    with pytest.raises(ValueError):
        domain.construct_rational_between_bounds("5/3", "5/3")
    with pytest.raises(ValueError, match="checker_capability_missing"):
        promoted.adapter.adapt_rational_numbers_matrix(matrix, domain_operation="construct_rational_between_bounds")
    for op in CHECKER_BLOCKED:
        with pytest.raises(Exception):
            _dispatch(op)
