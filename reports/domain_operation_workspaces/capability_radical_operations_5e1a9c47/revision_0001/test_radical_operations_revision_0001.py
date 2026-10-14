# -*- coding: utf-8 -*-
"""Revision 0001 review evidence for algebra.radical_operations: formal preflight plus an
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
DOMAIN_KEY = "algebra.radical_operations"
SKILL_ID = "gh_OperationsOfRadicalsAndFractions"
OPERATIONS = {
    "simplify_radical_fraction_expressions",
    "denest_square_roots",
    "evaluate_integer_fraction_part_expression",
    "order_radical_numbers",
    "evaluate_time_dilation_relations",
    "optimize_by_am_gm",
    "nearest_integer_from_radical_relation",
}


def S(*pairs):
    return [[c, r] for c, r in zip(pairs[::2], pairs[1::2])]


def T(num=None, den=None, coef=1):
    term = {"coefficient": coef}
    if num is not None:
        term["numerator"] = num
    if den is not None:
        term["denominator"] = den
    return term


def R(p, k, q):
    return {"rational": p, "radical": [k, q]}


FRACTIONS, DENEST, PARTS = (
    "simplify_radical_fraction_expressions", "denest_square_roots", "evaluate_integer_fraction_part_expression",
)
ORDER, DILATION, AM_GM = "order_radical_numbers", "evaluate_time_dilation_relations", "optimize_by_am_gm"

# textbook rows, written in the domain's structured input form
SOURCES = {
    12302: (FRACTIONS, {"expressions": [
        [T(den=[S(1, 3, -1, 2)])], [T(den=[S(2, 1, 1, 3)]), T(num=[S(2, 1)], den=[S(1, 3, -1, 1)])],
    ]}, {"part_1": "sqrt(2)+sqrt(3)", "part_2": "3"}),
    12303: (ORDER, {"numbers": [{"label": "a", "term": T(num=[S(1, 2, 1, 11)])}, {"label": "b", "term": T(num=[S(1, 3, 1, 10)])},
                                {"label": "c", "term": T(num=[S(1, 6, 1, 7)])}]}, {"part_1": "c>b>a"}),
    12304: (DILATION, {"relations": [
        {"find": "earth_years", "traveler_years": 60, "speed_ratio": "5/13"},
        {"find": "travel_years_from_age_match", "traveler_age": 27, "child_age": 3, "speed_ratio": "4/5"},
    ]}, {"part_1": "65", "part_2": "36"}),
    12305: (DENEST, {"roots": [R(4, 2, 3), R(7, -1, 40), R(8, -4, 3)]},
            {"part_1": "1+sqrt(3)", "part_2": "-sqrt(2)+sqrt(5)", "part_3": "-sqrt(2)+sqrt(6)"}),
    12306: (PARTS, {"root": R(3, 2, 2), "sign": -1}, "1-sqrt(2)"),
    12307: (AM_GM, {"problem": {"kind": "max_product_linear_sum", "p": 2, "q": 2, "total": 12, "context": "rope_rectangle"}}, "9"),
    12308: (FRACTIONS, {"expressions": [
        [T(num=[S(3, 5, 6, 3, -1, 45, 1, 75)])],
        [T(num=[{"terms": S(1, 3, 1, 1), "power": 2}]), T(num=[{"terms": S(1, 3, -1, 1), "power": 2}])],
        [T(num=[S(1, "4/5")])],
    ]}, {"part_1": "11sqrt(3)", "part_2": "8", "part_3": "2sqrt(5)/5"}),
    12309: (FRACTIONS, {"expressions": [
        [T(num=[S(1, 6, -1, 2)], den=[S(1, 6, 1, 2)])], [T(den=[S(1, 5, -2, 1)]), T(coef=-1, den=[S(1, 5, 2, 1)])],
    ]}, {"part_1": "2-sqrt(3)", "part_2": "4"}),
    12310: (ORDER, {"numbers": [{"label": "a", "term": T(num=[S(2, 1)], den=[S(1, 6, -1, 4)])},
                                {"label": "b", "term": T(num=[S(5, 1)], den=[S(1, 8, -1, 3)])},
                                {"label": "c", "term": T(num=[S(10, 1)], den=[S(1, 12, -1, 2)])}]}, {"part_1": "c>b>a"}),
    12311: (DILATION, {"relations": [{"find": "speed_ratio", "traveler_years": 10, "earth_years": 20}]}, "sqrt(3)/2"),
    12312: (DENEST, {"roots": [R(6, -2, 5), R(8, 1, 28), R(12, 4, 5)]},
            {"part_1": "-1+sqrt(5)", "part_2": "1+sqrt(7)", "part_3": "sqrt(2)+sqrt(10)"}),
    12313: (PARTS, {"root": R(6, -2, 5), "sign": 1}, "3+sqrt(5)"),
    12314: (AM_GM, {"problem": {"kind": "min_linear_sum_fixed_product", "p": 1, "q": 2, "product": 8,
                                "context": "positive_pair"}}, "8"),
    12315: (FRACTIONS, {"expressions": [
        [T(num=[S(1, 3, 1, 12, -2, 48)])],
        [T(den=[S(7, 1, 1, 41)]), T(den=[S(1, 41, 1, 33)]), T(den=[S(1, 33, 5, 1)])],
        [T(num=[S(3, 1, 1, 6)], den=[S(3, 1, -1, 6)]), T(num=[S(3, 1, -1, 6)], den=[S(3, 1, 1, 6)])],
    ]}, {"part_1": "-5sqrt(3)", "part_2": "1/4", "part_3": "10"}),
    12316: ("nearest_integer_from_radical_relation", {"known": 5, "rhs": 10, "sign": -1}, "29"),
    12317: (DENEST, {"roots": [R(8, -2, 15), R(7, 1, 24), R(11, -6, 2)]},
            {"part_1": "-sqrt(3)+sqrt(5)", "part_2": "1+sqrt(6)", "part_3": "3-sqrt(2)"}),
    12318: (DENEST, {"roots": [R(14, 6, 5)], "context": "square_area"}, "3+sqrt(5)"),
    12319: (PARTS, {"root": R(4, 2, 3), "sign": -1}, "3/2-sqrt(3)/2"),
    12320: (AM_GM, {"problem": {"kind": "max_product_linear_sum", "p": 2, "q": 1, "total": 40, "context": "river_fence"}},
            {"area": "200", "length": "20", "width": "10"}),
    12321: (AM_GM, {"problem": {"kind": "min_box_surface", "height": 2, "volume": 32, "context": "paper_box"}},
            {"length": "4", "width": "4"}),
}


def _production_package_names() -> list[str]:
    return sorted(p.name for p in (PROJECT_ROOT / "core" / "domain" / "promoted").iterdir() if p.name != "__pycache__")


@pytest.fixture(scope="module")
def promoted():
    production_store_bytes = PRODUCTION_STORE.read_bytes()
    production_before = _production_package_names()
    prefix_dir = f"radical_operations_revision_0001_{uuid.uuid4().hex[:10]}"
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
            domain=importlib.import_module(f"{package_import}.radical_operations_domain"),
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
    op, _, expected = SOURCES[example_id]
    matrix, payload = _source_payload(example_id)
    assert getattr(promoted.domain, f"validate_{op}_matrix")(matrix)
    assert payload["correct_answer"] == expected
    assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"
    assert validate_answer_contract_consistency(payload["answer_contract"]) == []
    assert check_answer(expected, expected, payload=payload)


@pytest.mark.parametrize(("example_id", "answer", "accepted"), [
    (12302, {"part_1": "\\sqrt{3}+\\sqrt{2}", "part_2": "3"}, True),
    (12302, {"part_1": "\\frac{1}{\\sqrt{3}-\\sqrt{2}}", "part_2": "3"}, False),
    (12302, {"part_1": "\\sqrt{3}-\\sqrt{2}", "part_2": "3"}, False),
    (12308, {"part_1": "11\\sqrt{3}", "part_2": "8", "part_3": "\\frac{2\\sqrt{5}}{5}"}, True),
    (12308, {"part_1": "11\\sqrt{3}", "part_2": "8", "part_3": "\\frac{2}{\\sqrt{5}}"}, False),
    (12308, {"part_1": "11\\sqrt{3}", "part_2": "8", "part_3": "\\sqrt{\\frac{4}{5}}"}, False),
    (12308, {"part_1": "6\\sqrt{3}+5\\sqrt{3}", "part_2": "8", "part_3": "\\frac{2\\sqrt{5}}{5}"}, False),
    (12315, {"part_1": "-5\\sqrt{3}", "part_2": "0.25", "part_3": "10"}, True),
    (12315, {"part_1": "-5\\sqrt{3}", "part_2": "\\frac{1}{4}", "part_3": "12"}, False),
    (12305, {"part_1": "\\sqrt{3}+1", "part_2": "\\sqrt{5}-\\sqrt{2}", "part_3": "\\sqrt{6}-\\sqrt{2}"}, True),
    (12305, {"part_1": "\\sqrt{4+2\\sqrt{3}}", "part_2": "\\sqrt{5}-\\sqrt{2}", "part_3": "\\sqrt{6}-\\sqrt{2}"}, False),
    (12305, {"part_1": "\\sqrt{3}+1", "part_2": "\\sqrt{2}-\\sqrt{5}", "part_3": "\\sqrt{6}-\\sqrt{2}"}, False),
    (12317, {"part_1": "\\sqrt{5}-\\sqrt{3}", "part_2": "\\sqrt{6}+1", "part_3": "\\sqrt{9}-\\sqrt{2}"}, False),
    (12318, "\\sqrt{5}+3", True),
    (12318, "\\sqrt{14+6\\sqrt{5}}", False),
    (12318, "3-\\sqrt{5}", False),
    (12303, {"part_1": "a<b<c"}, True),
    (12303, {"part_1": "c>a>b"}, False),
    (12310, {"part_1": "a<b<c"}, True),
    (12310, {"part_1": "a>b>c"}, False),
    (12304, {"part_1": "65", "part_2": "36"}, True),
    (12304, {"part_1": "65", "part_2": "24"}, False),
    (12311, "\\frac{\\sqrt{3}}{2}", True),
    (12311, "\\sqrt{\\frac{3}{4}}", True),
    (12311, "\\frac{1}{2}", False),
    (12306, "-\\sqrt{2}+1", True),
    (12306, "1+\\sqrt{2}", False),
    (12313, "\\sqrt{5}+3", True),
    (12313, "\\sqrt{5}+1", False),
    (12319, "\\frac{3-\\sqrt{3}}{2}", True),
    (12319, "\\frac{3+\\sqrt{3}}{2}", False),
    (12316, "29", True),
    (12316, "30", False),
    (12307, "9", True),
    (12307, "36", False),
    (12314, "8", True),
    (12314, "4\\sqrt{2}", False),
    (12320, {"area": "200", "length": "20", "width": "10"}, True),
    (12320, {"area": "200", "length": "10", "width": "20"}, False),
    (12321, {"length": "4", "width": "4"}, True),
    (12321, {"length": "8", "width": "2"}, False),
])
def test_grading_uses_equivalence_and_required_form(promoted, example_id, answer, accepted):
    _, payload = _source_payload(example_id)
    assert bool(check_answer(answer, payload["correct_answer"], payload=payload)) is accepted


def test_refuses_inputs_outside_the_operations(promoted):
    with pytest.raises(ValueError):
        _dispatch(DENEST, roots=[R(5, 2, 3)])
    with pytest.raises(ValueError):
        _dispatch(DILATION, relations=[{"find": "earth_years", "traveler_years": 10, "speed_ratio": "1/2"}])
    with pytest.raises(ValueError):
        _dispatch(ORDER, numbers=[{"label": "a", "term": T(num=[S(1, 8)])}, {"label": "b", "term": T(num=[S(2, 2)])}])
    with pytest.raises(ValueError):
        _dispatch(AM_GM, problem={"kind": "min_linear_sum_fixed_product", "p": 1, "q": 2, "product": 3})
    with pytest.raises(ValueError):
        _dispatch(FRACTIONS, expressions=[[T(den=[S(1, 2, 1, 3, 1, 5)])]])
    with pytest.raises(ValueError):
        _dispatch("nearest_integer_from_radical_relation", known=10, rhs=5, sign=1)


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
