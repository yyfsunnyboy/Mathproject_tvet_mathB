# -*- coding: utf-8 -*-
"""Revision 0001 review evidence for algebra.absolute_value_relations: formal preflight plus an
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
DOMAIN_KEY = "algebra.absolute_value_relations"
SKILLS = ["gh_PointDivisionFormulaOnNumberLine", "gh_LinearEquationsWithAbsoluteValue", "gh_LinearInequalitiesWithAbsoluteValue"]
DIVISION, EQUATIONS, INEQUALITIES = (
    "evaluate_number_line_division_points", "solve_absolute_value_equations", "solve_absolute_value_inequalities",
)
RECOVER, STATEMENTS, EXTREME = (
    "recover_absolute_value_parameters", "evaluate_absolute_value_statements", "select_extreme_weighted_point",
)
OPERATIONS = {DIVISION, EQUATIONS, INEQUALITIES, RECOVER, STATEMENTS, EXTREME}


def F(*pairs):
    return [[c, d] for c, d in zip(pairs[::2], pairs[1::2])]


def ABS(form, coef=1):
    return {"abs": form} if coef == 1 else {"abs": form, "coef": coef}


def C(c):
    return [{"poly": [[c, 0]]}]


def REL(lhs, op, rhs):
    return {"lhs": lhs, "op": op, "rhs": rhs}


def ONE(form, op, c):
    return {"relations": [REL([ABS(form)], op, C(c))]}


def CHAIN(form, low, high):
    return {"joiner": "chain", "relations": [REL(C(low), "<", [ABS(form)]), REL([ABS(form)], "<", C(high))]}


SHIFT_A = [[1, 1], [{"param": "a", "sign": -1}, 0]]

# textbook rows, written in the domain's structured input form, with the textbook answers
SOURCES = {
    1027: (DIVISION, {"points": {"A": -3, "B": 12}, "intro": "points_first", "parts": [
        {"find": "internal", "label": "P", "variable": "x", "ratio": [3, 2]},
        {"find": "external", "label": "Q", "variable": "y", "ratio": [3, 5]}]}, {"part_1": "6", "part_2": "-51/2"}),
    1028: (DIVISION, {"points": {"A": 12, "B": -4}, "intro": "line_first", "parts": [
        {"find": "internal", "label": "P", "ratio": [2, 1], "ratio_style": "multiple", "position": "between"},
        {"find": "external", "label": "Q", "ratio": [7, 1]}]}, {"part_1": "4/3", "part_2": "-20/3"}),
    1030: (EQUATIONS, {"equations": [REL([ABS(F(1, 1, -1, 0))], "=", C(2)), REL([ABS(F(2, 0, -1, 1))], "=", C(4)),
                                     REL([ABS(F(2, 1, -3, 0))], "=", C(5))]},
           {"part_1": "-1, 3", "part_2": "-2, 6", "part_3": "-1, 4"}),
    1031: (EQUATIONS, {"equations": [REL([ABS(F(1, 1, 1, 0))], "=", C(3)), REL([ABS(F(1, 0, -1, 1))], "=", C(3)),
                                     REL([ABS(F(3, 1, 1, 0))], "=", C(2))]},
           {"part_1": "-4, 2", "part_2": "-2, 4", "part_3": "-1, 1/3"}),
    1032: (EQUATIONS, {"equations": [REL([ABS(F(1, 1)), ABS(F(1, 1, 3, 0))], "=", C(5))]}, "-4, 1"),
    1033: (INEQUALITIES, {"systems": [ONE(F(1, 1, -1, 0), "<=", 2), ONE(F(3, 0, -1, 1), ">", 2), ONE(F(2, 1, -1, 0), "<", 5)]},
           {"part_1": "[-1,3]", "part_2": "(-∞,1)∪(5,∞)", "part_3": "(-2,3)"}),
    1034: (INEQUALITIES, {"systems": [ONE(F(1, 1, 2, 0), ">", 1), ONE(F(-1, 1, -2, 0), "<=", 4), ONE(F(3, 1, 1, 0), ">", 2)]},
           {"part_1": "(-∞,-3)∪(-1,∞)", "part_2": "[-6,2]", "part_3": "(-∞,-1)∪(1/3,∞)"}),
    1035: (INEQUALITIES, {"systems": [
        {"joiner": "and", "relations": [REL([ABS(F(1, 1))], "<", C(2)), REL([ABS(F(1, 1, -2, 0))], "<", C(1))]},
        CHAIN(F(2, 1, -1, 0), 1, 5)]}, {"part_1": "(1,2)", "part_2": "(-2,0)∪(1,3)"}),
    1036: (INEQUALITIES, {"systems": [{"relations": [REL([ABS(F(1, 1, -1, 0), 2), {"poly": F(1, 1)}], "<", C(7))]}]}, "(-5,3)"),
    1037: (RECOVER, {"relations": [{"inner": SHIFT_A, "op": ">", "bound": {"param": "b"}}], "parameters": ["a", "b"],
                     "prompt": "body_temperature", "target": [["-oo", "35", False, False], ["38", "oo", False, False]]},
           {"a": "73/2", "b": "3/2"}),
    1038: (STATEMENTS, {"statements": [{"kind": "distance_expression", "points": {"A": -3, "B": 1}, "claim": [-3, "-", 1]}],
                        "item_labels": ["(1)"]}, "○"),
    1039: (STATEMENTS, {"statements": [{"kind": "weighted_point_order", "left": [1, 2], "op": ">", "right": [2, 1]}]}, "○"),
    1040: (STATEMENTS, {"statements": [{"kind": "same_solution_set", "left": REL([ABS(F(1, 1, -1, 0))], "<", C(3)),
                                        "right": REL([ABS(F(1, 0, -1, 1))], "<", C(3))}]}, "○"),
    1041: (DIVISION, {"points": {"A": -5, "B": 12}, "parts": [
        {"find": "distance"}, {"find": "internal", "label": "P", "variable": "x", "ratio": [3, 4]},
        {"find": "external", "label": "Q", "variable": "y", "ratio": [3, 4], "segment_order": "QB"}]},
           {"part_1": "17", "part_2": "16/7", "part_3": "-56"}),
    1042: (EXTREME, {"options": [[3, 1], [1, 3], [3, 2], [2, 3]], "extreme": "max"}, "\\frac{a+3b}{4}"),
    1043: (EQUATIONS, {"equations": [REL([ABS(F(-1, 0, 1, 1))], "=", C(3)), REL([ABS(F(3, 1, 1, 0))], "=", C(2))]},
           {"part_1": "-2, 4", "part_2": "-1, 1/3"}),
    1044: (INEQUALITIES, {"systems": [ONE(F(1, 1, -3, 0), "<=", 3), ONE(F(1, 1, 1, 0), ">", 5), ONE(F(5, 0, -2, 1), "<", 7)]},
           {"part_1": "[0,6]", "part_2": "(-∞,-6)∪(4,∞)", "part_3": "(-1,6)"}),
    1045: (INEQUALITIES, {"systems": [{"relations": [REL([ABS(F(1, 1, -1, 0))], "<", [ABS(F(1, 1, -4, 0))])]},
                                      CHAIN(F(-3, 1, 3, 0), 2, 5)]},
           {"part_1": "(-∞,5/2)", "part_2": "(-2/3,1/3)∪(5/3,8/3)"}),
    1046: (RECOVER, {"relations": [{"inner": SHIFT_A, "op": "<=", "bound": {"param": "b"}}], "parameters": ["a", "b"],
                     "prompt": "pregnancy_weeks", "target": [[37, 41, True, True]]}, {"a": "39", "b": "2"}),
    1047: (EQUATIONS, {"equations": [REL([ABS(F(1, 1, 7, 0))], "=", [ABS(F(1, 1, -1, 0), 3)])],
                       "prompt": "find_real_x", "state_solution_count": True}, "-1, 5"),
    1048: (RECOVER, {"relations": [{"inner": [[2, 1], [{"param": "a", "sign": 1}, 0]], "op": "<=", "bound": {"param": "b"}}],
                     "parameters": ["a", "b"], "target": [[-5, 2, True, True]]}, {"a": "3", "b": "7"}),
    1049: (RECOVER, {"relations": [{"inner": SHIFT_A, "op": "<", "bound": 2},
                                   {"inner": [[2, 1], [3, 0]], "op": ">", "bound": {"param": "b"}}],
                     "parameters": ["a", "b"], "prompt": "system", "target": [[2, 3, False, False]]}, {"a": "1", "b": "7"}),
}


def _production_package_names() -> list[str]:
    return sorted(p.name for p in (PROJECT_ROOT / "core" / "domain" / "promoted").iterdir() if p.name != "__pycache__")


@pytest.fixture(scope="module")
def promoted():
    production_store_bytes = PRODUCTION_STORE.read_bytes()
    production_before = _production_package_names()
    prefix_dir = f"absolute_value_relations_revision_0001_{uuid.uuid4().hex[:10]}"
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
    snapshot = store_mod.snapshot_runtime_state(DOMAIN_KEY, SKILLS, package_import)
    try:
        result = promote_reviewed_workspace(
            workspace, teacher_approved=True, store_path=store, package_root=package_root, package_import_prefix=prefix,
        )
        yield SimpleNamespace(
            result=result,
            store=json.loads(store.read_text(encoding="utf-8")),
            domain=importlib.import_module(f"{package_import}.absolute_value_relations_domain"),
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


def _source_payload(example_id: int):
    op, constraints, _ = SOURCES[example_id]
    return _dispatch(op, **constraints)


def test_formal_preflight_passes_with_new_domain_only():
    report = preflight_reviewed_bundle(REVISION_DIR)
    assert report["passed"], report["blockers"]
    bundle = report["bundle"]
    assert bundle["proposal_revision"] == 1 == bundle["review"]["approved_revision"]
    assert set(bundle["operations"]) == OPERATIONS
    assert list(bundle["skill_bindings"]) == SKILLS


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
    op, _, expected = SOURCES[example_id]
    matrix, payload = _source_payload(example_id)
    assert getattr(promoted.domain, f"validate_{op}_matrix")(matrix)
    assert payload["correct_answer"] == expected
    assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"
    assert validate_answer_contract_consistency(payload["answer_contract"]) == []
    assert check_answer(expected, expected, payload=payload)


@pytest.mark.parametrize(("example_id", "answer", "accepted"), [
    (1027, {"part_1": "6", "part_2": "-25.5"}, True),
    (1027, {"part_1": "6", "part_2": "-\\frac{51}{2}"}, True),
    (1027, {"part_1": "6", "part_2": "-24.5"}, False),
    (1028, {"part_1": "\\frac{4}{3}", "part_2": "-\\frac{20}{3}"}, True),
    (1028, {"part_1": "4/3", "part_2": "20/3"}, False),
    (1031, {"part_1": "x=2 或 x=-4", "part_2": "4,-2", "part_3": "x=\\frac{1}{3}, x=-1"}, True),
    (1031, {"part_1": "-4, 2", "part_2": "-2, 4", "part_3": "1, 3, -1"}, False),
    (1031, {"part_1": "-4, 2", "part_2": "-2, 4", "part_3": "-1"}, False),
    (1032, "x=1或x=-4", True),
    (1032, "1", False),
    (1032, "-4, 1, 0", False),
    (1033, {"part_1": "-1\\le x\\le 3", "part_2": "x<1 或 x>5", "part_3": "-2<x<3"}, True),
    (1033, {"part_1": "(-1,3)", "part_2": "x<1 或 x>5", "part_3": "-2<x<3"}, False),
    (1035, {"part_1": "1<x<2", "part_2": "-2<x<0 或 1<x<3"}, True),
    (1035, {"part_1": "1<x<2", "part_2": "(-2,3)"}, False),
    (1036, "-5<x<3", True),
    (1036, "(-5,3]", False),
    (1037, {"a": "36.5", "b": "1.5"}, True),
    (1037, {"a": "1.5", "b": "36.5"}, False),
    (1038, "○", True),
    (1038, "A", True),
    (1038, "×", False),
    (1042, "2", True),
    (1042, "B", True),
    (1042, "\\frac{a+3b}{4}", True),
    (1042, "1", False),
    (1045, {"part_1": "x<\\frac{5}{2}", "part_2": "(-2/3,1/3)∪(5/3,8/3)"}, True),
    (1045, {"part_1": "x>\\frac{5}{2}", "part_2": "(-2/3,1/3)∪(5/3,8/3)"}, False),
    (1047, "5, -1", True),
    (1047, "5", False),
    (1049, {"a": "1", "b": "7"}, True),
    (1049, {"a": "4", "b": "9"}, False),
])
def test_grading_uses_exact_equivalence(promoted, example_id, answer, accepted):
    _, payload = _source_payload(example_id)
    assert bool(check_answer(answer, payload["correct_answer"], payload=payload)) is accepted


def test_refuses_inputs_outside_the_operations(promoted):
    with pytest.raises(ValueError):
        _dispatch(DIVISION, points={"A": 2, "B": 2}, parts=[{"find": "distance"}])
    with pytest.raises(ValueError):
        _dispatch(DIVISION, points={"A": 0, "B": 4}, parts=[{"find": "external", "ratio": [2, 2]}])
    with pytest.raises(ValueError):
        _dispatch(EQUATIONS, equations=[REL([ABS(F(1, 1)), ABS(F(1, 1, -3, 0))], "=", C(3))])
    with pytest.raises(ValueError):
        _dispatch(INEQUALITIES, systems=[{"relations": [REL([ABS(F(0, 0, 1, 0))], "<", C(1))]}])
    with pytest.raises(ValueError):
        _dispatch(RECOVER, relations=[{"inner": SHIFT_A, "op": "<", "bound": 2}], parameters=["a"],
                  target=[[0, 1, False, False]])
    with pytest.raises(ValueError):
        _dispatch(EXTREME, options=[[1, 1], [2, 2]], extreme="max")


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
        assert len(seen) > 2, op
