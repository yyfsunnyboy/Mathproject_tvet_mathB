# -*- coding: utf-8 -*-
"""Revision 0001 review evidence for algebra.multiplication_formulas: formal preflight plus an
isolated (temp-store) promotion.  Nothing here writes the production store or package root.
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
DOMAIN_KEY = "algebra.multiplication_formulas"
SKILL_ID = "gh_MultiplicationFormulas"
OPERATIONS = {
    "expand_polynomial_expressions",
    "factor_by_cube_formulas",
    "evaluate_reciprocal_power_expressions",
    "simplify_radical_expressions",
    "solve_rational_unknowns_from_squared_radical_identity",
    "evaluate_product_under_power_relation",
}


def _poly(*pairs):
    return [[c, p] for c, p in zip(pairs[::2], pairs[1::2])]


def _square(*pairs, power=2):
    return {"factors": [[_poly(*pairs), power]]}


# textbook rows, written in the domain's structured input form
SOURCES = {
    12286: ("expand_polynomial_expressions", {"expressions": [
        [_square(1, {"a": 1}, -2, {"b": 1}), _square(2, {"a": 1}, 1, {"b": 1})],
        [{"factors": [[_poly(1, {"a": 1}, -1, {"b": 1}, 1, {}), 1], [_poly(1, {"a": 1}, -1, {"b": 1}, -1, {}), 1]]}],
        [_square(1, {"a": 1}, -2, {"b": 1}, 3, {"c": 1})],
    ]}, {"part_1": "5a^2+5b^2", "part_2": "a^2-2ab+b^2-1", "part_3": "a^2-4ab+6ac+4b^2-12bc+9c^2"}),
    12287: ("expand_polynomial_expressions", {"expressions": [
        [_square(1, {"a": 1}, 2, {"b": 1}, power=3)], [_square(2, {"a": 1}, -3, {"b": 1}, power=3)],
    ]}, {"part_1": "a^3+6a^2b+12ab^2+8b^3", "part_2": "8a^3-36a^2b+54ab^2-27b^3"}),
    12289: ("factor_by_cube_formulas", {"polynomials": [
        _poly(1, {"x": 3}, 1, {}), _poly(27, {"x": 3}, -1, {}), _poly(1, {"x": 3}, 9, {"x": 2}, 27, {"x": 1}, 27, {}),
    ]}, {"part_1": "(x+1)(x^2-x+1)", "part_2": "(3x-1)(9x^2+3x+1)", "part_3": "(x+3)^3"}),
    12290: ("evaluate_reciprocal_power_expressions", {
        "base": {"kind": "relation", "sign": 1, "value": 3},
        "targets": [{"power": 2, "sign": 1}, {"power": 3, "sign": 1}],
    }, {"part_1": "7", "part_2": "18"}),
    12291: ("simplify_radical_expressions", {"expressions": [
        [{"factors": [[[1, 12]]]}, {"factors": [[[1, 75]]]}],
        [{"factors": [[[1, 7], [1, 2]], [[1, 7], [-1, 2]]]}],
        [{"factors": [[[1, "3/2"]]]}],
    ]}, {"part_1": "7sqrt(3)", "part_2": "5", "part_3": "sqrt(6)/2"}),
    12296: ("evaluate_reciprocal_power_expressions", {
        "base": {"kind": "relation", "sign": -1, "value": -2},
        "targets": [{"power": 2, "sign": 1}, {"power": 3, "sign": -1}],
    }, {"part_1": "6", "part_2": "-14"}),
    12297: ("solve_rational_unknowns_from_squared_radical_identity",
            {"coefficient": 2, "radicand": 3, "rhs_radical": 4}, {"a": "1", "b": "13"}),
    12298: ("expand_polynomial_expressions", {"expressions": [
        [{"factors": [[_poly("1/2", {"a": 1}, "-1/3", {"b": 1}), 1],
                      [_poly("1/4", {"a": 2}, "1/6", {"a": 1, "b": 1}, "1/9", {"b": 2}), 1]]}],
    ]}, {"part_1": "a^3/8-b^3/27"}),
    12299: ("factor_by_cube_formulas", {"polynomials": [_poly(27, {"x": 3}, -1, {"y": 3}), _poly(1, {"x": 3}, 8, {"y": 3})]},
            {"part_1": "(3x-y)(9x^2+3xy+y^2)", "part_2": "(x+2y)(x^2-2xy+4y^2)"}),
    12300: ("evaluate_reciprocal_power_expressions", {
        "base": {"kind": "radical", "rational": 2, "radical": -1, "radicand": 3},
        "targets": [{"power": 1, "sign": 1}, {"power": 2, "sign": 1}, {"power": 3, "sign": 1}],
    }, {"part_1": "4", "part_2": "14", "part_3": "52"}),
    12301: ("evaluate_product_under_power_relation", {"variable": "a", "power": 3, "value": 2, "expression": [{"factors": [
        [_poly(1, {"a": 1}, -1, {}), 1], [_poly(1, {"a": 1}, 1, {}), 1],
        [_poly(1, {"a": 2}, -1, {"a": 1}, 1, {}), 1], [_poly(1, {"a": 2}, 1, {"a": 1}, 1, {}), 1],
    ]}]}, "3"),
}


def _production_package_names() -> list[str]:
    return sorted(p.name for p in (PROJECT_ROOT / "core" / "domain" / "promoted").iterdir() if p.name != "__pycache__")


@pytest.fixture(scope="module")
def promoted():
    production_store_bytes = PRODUCTION_STORE.read_bytes()
    production_before = _production_package_names()
    prefix_dir = f"multiplication_formulas_revision_0001_{uuid.uuid4().hex[:10]}"
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
            domain=importlib.import_module(f"{package_import}.multiplication_formulas_domain"),
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


@pytest.mark.parametrize("example_id", sorted(SOURCES))
def test_textbook_rows_match_textbook_answers(promoted, example_id):
    op, constraints, expected = SOURCES[example_id]
    matrix, payload = _dispatch(op, **constraints)
    assert getattr(promoted.domain, f"validate_{op}_matrix")(matrix)
    assert payload["correct_answer"] == expected
    assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"
    assert validate_answer_contract_consistency(payload["answer_contract"]) == []
    assert check_answer(expected, expected, payload=payload)


@pytest.mark.parametrize(("example_id", "answer", "accepted"), [
    (12286, {"part_1": "5b^2+5a^2", "part_2": "-1+b^2-2ab+a^2", "part_3": "a^2+4b^2+9c^2-4ab-12bc+6ac"}, True),
    (12286, {"part_1": "(a-2b)^2+(2a+b)^2", "part_2": "a^2-2ab+b^2-1", "part_3": "a^2-4ab+6ac+4b^2-12bc+9c^2"}, False),
    (12286, {"part_1": "5(a^2+b^2)", "part_2": "a^2-2ab+b^2-1", "part_3": "a^2-4ab+6ac+4b^2-12bc+9c^2"}, False),
    (12286, {"part_1": "5a^2+5b^2", "part_2": "a^2-2ab+b^2+1", "part_3": "a^2-4ab+6ac+4b^2-12bc+9c^2"}, False),
    (12287, {"part_1": "8b^3+12ab^2+6a^2b+a^3", "part_2": "-27b^3+54ab^2-36a^2b+8a^3"}, True),
    (12287, {"part_1": "(a+2b)^3", "part_2": "8a^3-36a^2b+54ab^2-27b^3"}, False),
    (12298, {"part_1": "\\frac{a^{3}}{8}-\\frac{b^{3}}{27}"}, True),
    (12298, {"part_1": "a^3/8+b^3/27"}, False),
    (12289, {"part_1": "(x^2-x+1)(x+1)", "part_2": "(9x^2+3x+1)(3x-1)", "part_3": "(x+3)(x+3)(x+3)"}, True),
    (12289, {"part_1": "x^3+1", "part_2": "(3x-1)(9x^2+3x+1)", "part_3": "(x+3)^3"}, False),
    (12289, {"part_1": "(x+1)(x^2-x+1)", "part_2": "(3x-1)(9x^2+3x+1)", "part_3": "(x+3)(x^2+6x+9)"}, False),
    (12289, {"part_1": "(x+1)(x^2+x+1)", "part_2": "(3x-1)(9x^2+3x+1)", "part_3": "(x+3)^3"}, False),
    (12299, {"part_1": "(3x-y)(9x^2+3xy+y^2)", "part_2": "(x+2y)(x^2+2xy+4y^2)"}, False),
    (12291, {"part_1": "7\\sqrt{3}", "part_2": "5", "part_3": "\\frac{\\sqrt{6}}{2}"}, True),
    (12291, {"part_1": "\\sqrt{12}+\\sqrt{75}", "part_2": "5", "part_3": "\\frac{\\sqrt{6}}{2}"}, False),
    (12291, {"part_1": "2\\sqrt{3}+5\\sqrt{3}", "part_2": "5", "part_3": "\\frac{\\sqrt{6}}{2}"}, False),
    (12291, {"part_1": "7\\sqrt{3}", "part_2": "7-2", "part_3": "\\frac{\\sqrt{6}}{2}"}, False),
    (12291, {"part_1": "7\\sqrt{3}", "part_2": "5", "part_3": "\\sqrt{\\frac{3}{2}}"}, False),
    (12291, {"part_1": "7\\sqrt{3}", "part_2": "5", "part_3": "\\frac{\\sqrt{3}}{\\sqrt{2}}"}, False),
    (12290, {"part_1": "7", "part_2": "18"}, True),
    (12290, {"part_1": "9", "part_2": "27"}, False),
    (12297, {"a": "1", "b": "13"}, True),
    (12297, {"a": "1", "b": "16"}, False),
    (12300, {"part_1": "4", "part_2": "14", "part_3": "52"}, True),
    (12300, {"part_1": "4", "part_2": "16", "part_3": "64"}, False),
])
def test_grading_uses_equivalence_and_required_form(promoted, example_id, answer, accepted):
    op, constraints, expected = SOURCES[example_id]
    _, payload = _dispatch(op, **constraints)
    assert bool(check_answer(answer, payload["correct_answer"], payload=payload)) is accepted


def test_power_relation_grading(promoted):
    op, constraints, _ = SOURCES[12301]
    _, payload = _dispatch(op, **constraints)
    assert check_answer("3", "3", payload=payload) and check_answer("3.0", "3", payload=payload)
    for wrong in ("2", "a^6-1", "7", ""):
        assert not check_answer(wrong, "3", payload=payload), wrong


def test_refuses_inputs_outside_the_formulas(promoted):
    with pytest.raises(ValueError):
        _dispatch("factor_by_cube_formulas", polynomials=[_poly(1, {"x": 3}, 2, {})])
    with pytest.raises(ValueError):
        _dispatch("factor_by_cube_formulas", polynomials=[_poly(1, {"x": 3}, 9, {"x": 2}, 27, {"x": 1}, 28, {})])
    with pytest.raises(ValueError):
        _dispatch("evaluate_reciprocal_power_expressions", base={"kind": "relation", "sign": 1, "value": 3},
                  targets=[{"power": 1, "sign": -1}])
    with pytest.raises(ValueError):
        _dispatch("evaluate_product_under_power_relation", variable="a", power=3, value=2,
                  expression=[{"factors": [[_poly(1, {"a": 1}, -1, {}), 1]]}])
    with pytest.raises(ValueError):
        _dispatch("solve_rational_unknowns_from_squared_radical_identity", coefficient=2, radicand=4, rhs_radical=4)


def test_seeded_operations_are_deterministic_valid_and_checker_legal(promoted):
    for op in sorted(OPERATIONS):
        validator = getattr(promoted.domain, f"validate_{op}_matrix")
        seen = set()
        for seed in range(30):
            matrix, payload = _dispatch(op, seed=seed)
            assert _dispatch(op, seed=seed) == (matrix, payload)
            assert validator(matrix)
            assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"
            assert check_answer(payload["correct_answer"], payload["correct_answer"], payload=payload)
            seen.add(json.dumps(matrix["givens"], sort_keys=True))
        assert len(seen) > 5, op
