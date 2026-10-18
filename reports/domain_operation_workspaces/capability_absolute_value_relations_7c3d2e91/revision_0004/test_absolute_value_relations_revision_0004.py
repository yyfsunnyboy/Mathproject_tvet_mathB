# -*- coding: utf-8 -*-
"""Revision 0004 review evidence for algebra.absolute_value_relations: formal preflight plus an
isolated (temp-store) promotion.  Nothing here writes the production store or package root.

Revision 0004 keeps revision 0003 unchanged for its eight operations and adds
place_weighted_points_on_number_line (textbook 例題2 / 隨堂練習2: mark P, Q, R on AB and order them).
Part (1) is graded by number_line_placement_checker (relative positions on AB against exact fractions,
per-point tolerance), part (2) by ordered_inequality_checker; the multipart checker requires both.
Requires the runtime with number_line_placement_checker registered.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import random
import re
import shutil
import sys
import uuid
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.checkers.number_line_placement_checker import check_number_line_placement_answer, parse_placement
from core.gencode.answer_payload import validate_answer_contract_consistency
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.reviewed_capability_promotion import BUNDLE_FILENAME, preflight_reviewed_bundle, promote_reviewed_workspace
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority
from core.registry import promoted_capability_store as store_mod
from core.registry.domain_operation_registry import get_domain_spec

REVISION_DIR = Path(__file__).resolve().parent
REV3_DIR = REVISION_DIR.parent / "revision_0003"
PROJECT_ROOT = REVISION_DIR.parents[3]
PRODUCTION_STORE = PROJECT_ROOT / "configs" / "gencode_promoted_capabilities.json"
DOMAIN_KEY = "algebra.absolute_value_relations"
POINT, EQ, INEQ = (
    "gh_PointDivisionFormulaOnNumberLine", "gh_LinearEquationsWithAbsoluteValue", "gh_LinearInequalitiesWithAbsoluteValue",
)
SKILLS = [POINT, EQ, INEQ]
PLACE = "place_weighted_points_on_number_line"
OLD_OPERATIONS = {
    "evaluate_number_line_division_points", "solve_absolute_value_equations", "solve_absolute_value_inequalities",
    "recover_absolute_value_parameters", "evaluate_absolute_value_statements", "select_extreme_weighted_point",
    "evaluate_number_line_statements", "solve_tolerance_range_application",
}
OPERATIONS = OLD_OPERATIONS | {PLACE}
BINDINGS = {
    POINT: ["evaluate_number_line_division_points", "evaluate_number_line_statements", "select_extreme_weighted_point",
            PLACE],
    EQ: ["solve_absolute_value_equations"],
    INEQ: ["solve_absolute_value_inequalities", "recover_absolute_value_parameters", "evaluate_absolute_value_statements",
           "solve_tolerance_range_application"],
}


def PT(label, p, q):
    return {"label": label, "weights": [p, q]}


# textbook rows 1029 (例題2) and 12323 (隨堂練習2) in the domain's structured input form, with textbook answers
SOURCES = {
    1029: ({"points": [PT("P", 1, 3), PT("Q", 1, 1), PT("R", 3, 1)], "notation": "coordinate"},
           {"part_1": "P=3/4, Q=1/2, R=1/4", "part_2": "R<Q<P"}),
    12323: ({"points": [PT("P", 1, 1), PT("Q", 1, 5), PT("R", 2, 1)], "notation": "equals"},
            {"part_1": "P=1/2, Q=5/6, R=1/3", "part_2": "R<P<Q"}),
}


def _production_package_names() -> list[str]:
    return sorted(p.name for p in (PROJECT_ROOT / "core" / "domain" / "promoted").iterdir() if p.name != "__pycache__")


def _load_revision_package(revision_dir: Path, alias: str):
    package_dir = revision_dir / "production_package"
    spec = importlib.util.spec_from_file_location(alias, package_dir / "__init__.py",
                                                  submodule_search_locations=[str(package_dir)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return (importlib.import_module(f"{alias}.absolute_value_relations_domain"),
            importlib.import_module(f"{alias}.absolute_value_relations_adapter"))


@pytest.fixture(scope="module")
def promoted():
    production_store_bytes = PRODUCTION_STORE.read_bytes()
    production_before = _production_package_names()
    prefix_dir = f"absolute_value_relations_revision_0004_{uuid.uuid4().hex[:10]}"
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
    if bundle["review"].get("status") != "human_approved":
        bundle["review"].update(status="human_approved", approved_by="isolated_test_only", approved_revision=4)
        (workspace / BUNDLE_FILENAME).write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    package_import = f"{prefix}.{bundle['package_name']}"
    snapshot = store_mod.snapshot_runtime_state(DOMAIN_KEY, SKILLS, package_import)
    rev3_alias = f"rev3_{uuid.uuid4().hex[:8]}"
    try:
        result = promote_reviewed_workspace(
            workspace, teacher_approved=True, store_path=store, package_root=package_root, package_import_prefix=prefix,
        )
        rev3_domain, rev3_adapter = _load_revision_package(REV3_DIR, rev3_alias)
        yield SimpleNamespace(
            result=result,
            store=json.loads(store.read_text(encoding="utf-8")),
            domain=importlib.import_module(f"{package_import}.absolute_value_relations_domain"),
            adapter=importlib.import_module(f"{package_import}.absolute_value_relations_adapter"),
            rev3_domain=rev3_domain,
            rev3_adapter=rev3_adapter,
        )
    finally:
        store_mod.restore_runtime_state(snapshot)
        for name in [n for n in sys.modules if n.startswith((f"temp.{prefix_dir}", rev3_alias))]:
            sys.modules.pop(name, None)
        shutil.rmtree(base, ignore_errors=True)
        assert PRODUCTION_STORE.read_bytes() == production_store_bytes
        assert _production_package_names() == production_before


def _dispatch(op: str, seed: int = 1, **constraints):
    return dispatch_registered_operation(DOMAIN_KEY, op, seed=seed, constraints=constraints)


def _source_payload(example_id: int):
    constraints, _ = SOURCES[example_id]
    return _dispatch(PLACE, seed=0, **constraints)


def _latex_ok(text: str) -> bool:
    if "\\(" in text or "\\)" in text or text.count("$") % 2:
        return False
    for chunk in text.split("$")[1::2]:
        depth = 0
        for ch in re.sub(r"\\[{}]", "", chunk):
            depth += {"{": 1, "}": -1}.get(ch, 0)
            if depth < 0:
                return False
        if depth or chunk.count("\\left") != chunk.count("\\right"):
            return False
    return True


def _placed(**positions) -> str:
    """The practice page submits part (1) as a JSON object of relative positions."""
    return json.dumps(positions)


# --- formal review state ---------------------------------------------------------

def test_formal_preflight_blocks_only_on_pending_review():
    report = preflight_reviewed_bundle(REVISION_DIR)
    bundle = report["bundle"]
    assert bundle["proposal_revision"] == 4
    if bundle["review"].get("status") == "human_approved":
        assert report["passed"], report["blockers"]
        assert bundle["review"]["approved_revision"] == 4
    else:
        assert report["blockers"] == ["human_review_not_approved", "approved_revision_mismatch"]
    assert set(bundle["operations"]) == OPERATIONS == set(bundle["capabilities"])
    assert {k: v["allowed_operations"] for k, v in bundle["skill_bindings"].items()} == BINDINGS


def test_package_compiles_and_keeps_revision_0003_init():
    rev3 = json.loads((REV3_DIR / BUNDLE_FILENAME).read_text(encoding="utf-8"))
    rev4 = json.loads((REVISION_DIR / BUNDLE_FILENAME).read_text(encoding="utf-8"))
    assert set(rev4["files"]) == set(rev3["files"])
    assert rev4["files"]["__init__.py"] == rev3["files"]["__init__.py"]
    for name in rev4["files"]:
        path = REVISION_DIR / rev4["package_dir"] / name
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    for op in OLD_OPERATIONS:
        assert rev4["operations"][op] == rev3["operations"][op]
        assert rev4["smoke_cases"][op] == rev3["smoke_cases"][op]


def test_isolated_promotion_keeps_existing_domains(promoted):
    result = promoted.result
    assert result["promoted"]
    assert set(result["allowed_operations"]) == OPERATIONS == set(result["operations_executed"])
    assert set(get_domain_spec(DOMAIN_KEY).allowed_operations) == OPERATIONS
    production = json.loads(PRODUCTION_STORE.read_text(encoding="utf-8"))
    for key, entry in production["domains"].items():
        if key != DOMAIN_KEY:
            assert promoted.store["domains"][key] == entry
    for key, entry in production.get("skill_bindings", {}).items():
        if key not in SKILLS:
            assert promoted.store["skill_bindings"][key] == entry


# --- backward compatibility: the 26 published components keep identical matrices and payloads ----

def test_existing_operations_are_identical_to_revision_0003(promoted):
    rev3 = json.loads((REV3_DIR / BUNDLE_FILENAME).read_text(encoding="utf-8"))
    checked = 0
    for op in sorted(OLD_OPERATIONS):
        cases = [(c["seed"], c["constraints"]) for c in rev3["smoke_cases"][op]] + [(s, {}) for s in range(40)]
        for seed, constraints in cases:
            old = promoted.rev3_domain.build_absolute_value_relations_matrix(
                domain_operation=op, seed=seed, constraints=constraints)
            new = promoted.domain.build_absolute_value_relations_matrix(
                domain_operation=op, seed=seed, constraints=constraints)
            assert new == old, (op, seed)
            assert promoted.adapter.adapt_absolute_value_relations_matrix(new, domain_operation=op) == \
                promoted.rev3_adapter.adapt_absolute_value_relations_matrix(old, domain_operation=op), (op, seed)
            assert getattr(promoted.domain, f"validate_{op}_matrix")(new)
            checked += 1
    assert checked == 40 * len(OLD_OPERATIONS) + sum(len(rev3["smoke_cases"][op]) for op in OLD_OPERATIONS)


def test_skill_bindings_route_only_their_operations(promoted):
    for skill, ops in BINDINGS.items():
        for op in OPERATIONS:
            resolution = resolve_domain_authority(skill, selected_operation=op)
            if op in ops:
                assert resolution.binding_status == "confirmed" and resolution.selected_operation == op, (skill, op)
                assert resolution.fixed_domain_key == DOMAIN_KEY
            else:
                assert resolution.selected_operation != op or resolution.binding_status != "confirmed", (skill, op)


# --- textbook rows ------------------------------------------------------------------

@pytest.mark.parametrize("example_id", sorted(SOURCES))
def test_textbook_rows_match_textbook_answers(promoted, example_id):
    _, expected = SOURCES[example_id]
    matrix, payload = _source_payload(example_id)
    assert promoted.domain.validate_place_weighted_points_on_number_line_matrix(matrix)
    assert payload["correct_answer"] == expected
    assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"
    assert validate_answer_contract_consistency(payload["answer_contract"]) == []
    assert check_answer(expected, expected, payload=payload)
    assert _latex_ok(payload["question_text"]) and all(_latex_ok(s) for s in payload["explanation_steps"])
    assert _latex_ok(payload["display_answer"])
    part_1, part_2 = payload["answer_contract"]["parts"]
    assert part_1["input_kind"] == "number_line_placement" and part_1["placeholder"] == "請在下方作圖區作答"
    assert part_1["placement"]["labels"] == ["P", "Q", "R"]
    assert part_2["checker"] == "ordered_inequality_checker"


def test_textbook_texts(promoted):
    q1029 = _source_payload(1029)[1]["question_text"]
    assert q1029.startswith("設 $a<b$，且 $P\\left(\\frac{a+3b}{4}\\right)$、$Q\\left(\\frac{a+b}{2}\\right)$、"
                            "$R\\left(\\frac{3a+b}{4}\\right)$。")
    assert "(1) 在下方數線上分別標出 P、Q、R 三點所在的位置。" in q1029
    q12323 = _source_payload(12323)[1]["question_text"]
    assert q12323.startswith("設 $a<b$，且 $P=\\frac{a+b}{2}$、$Q=\\frac{a+5b}{6}$、$R=\\frac{2a+b}{3}$。")
    assert "比較 $\\frac{a+b}{2}$、$\\frac{a+5b}{6}$、$\\frac{2a+b}{3}$ 三數的大小" in q12323
    assert "$\\frac{3a+b}{4}<\\frac{a+b}{2}<\\frac{a+3b}{4}$" in _source_payload(1029)[1]["display_answer"]


@pytest.mark.parametrize(("example_id", "answer", "accepted"), [
    # both parts correct
    (1029, {"part_1": _placed(P=0.75, Q=0.5, R=0.25), "part_2": "R<Q<P"}, True),
    (1029, {"part_1": _placed(P=0.78, Q=0.47, R=0.23), "part_2": "R<Q<P"}, True),
    (1029, {"part_1": _placed(P=0.75, Q=0.5, R=0.25), "part_2": "P>Q>R"}, True),
    # correct order but a wrong drawing
    (1029, {"part_1": _placed(P=0.9, Q=0.5, R=0.1), "part_2": "R<Q<P"}, False),
    (1029, {"part_1": _placed(P=0.75, Q=0.6, R=0.25), "part_2": "R<Q<P"}, False),
    (1029, {"part_1": _placed(P=0.66, Q=0.5, R=0.33), "part_2": "R<Q<P"}, False),
    # one point misplaced, swapped, missing, extra or off the segment
    (1029, {"part_1": _placed(P=0.75, Q=0.5, R=0.4), "part_2": "R<Q<P"}, False),
    (1029, {"part_1": _placed(P=0.25, Q=0.5, R=0.75), "part_2": "R<Q<P"}, False),
    (1029, {"part_1": _placed(P=0.75, Q=0.5), "part_2": "R<Q<P"}, False),
    (1029, {"part_1": _placed(P=0.75, Q=0.5, R=0.25, S=0.1), "part_2": "R<Q<P"}, False),
    (1029, {"part_1": _placed(P=0.75, Q=0.5, R=-0.25), "part_2": "R<Q<P"}, False),
    # correct drawing but a wrong or empty order
    (1029, {"part_1": _placed(P=0.75, Q=0.5, R=0.25), "part_2": "P<Q<R"}, False),
    (1029, {"part_1": _placed(P=0.75, Q=0.5, R=0.25), "part_2": "R<P<Q"}, False),
    (1029, {"part_1": _placed(P=0.75, Q=0.5, R=0.25), "part_2": "R≤Q≤P"}, False),
    (1029, {"part_1": _placed(P=0.75, Q=0.5, R=0.25), "part_2": ""}, False),
    (1029, {"part_1": "", "part_2": "R<Q<P"}, False),
    (12323, {"part_1": _placed(P=0.5, Q=0.8333, R=0.3333), "part_2": "R<P<Q"}, True),
    (12323, {"part_1": _placed(P=0.52, Q=0.86, R=0.31), "part_2": "Q>P>R"}, True),
    (12323, {"part_1": _placed(P=0.5, Q=0.95, R=0.3333), "part_2": "R<P<Q"}, False),
    (12323, {"part_1": _placed(P=0.5, Q=0.75, R=0.25), "part_2": "R<P<Q"}, False),
    (12323, {"part_1": _placed(P=0.5, Q=0.8333, R=0.3333), "part_2": "R<Q<P"}, False),
])
def test_grading_requires_both_drawing_and_order(promoted, example_id, answer, accepted):
    _, payload = _source_payload(example_id)
    assert bool(check_answer(answer, payload["correct_answer"], payload=payload)) is accepted


# --- the placement operation against an independent oracle ------------------------------------

def test_seeded_placements_against_concrete_endpoints(promoted):
    rng = random.Random("rev4-placement")
    orders = set()
    for seed in range(300):
        matrix, payload = _dispatch(PLACE, seed=seed)
        a = Fraction(rng.randint(-20, 5))
        b = a + rng.randint(1, 30)
        values = {}
        for point in matrix["givens"]["points"]:
            p, q = point["weights"]
            values[point["label"]] = (p * a + q * b) / (p + q)
            t = (values[point["label"]] - a) / (b - a)
            assert Fraction(matrix["answer"]["positions"][point["label"]]) == t
        order = sorted(values, key=values.get)
        assert payload["correct_answer"]["part_2"] == "<".join(order)
        gaps = sorted((v - a) / (b - a) for v in values.values())
        assert min(y - x for x, y in zip(gaps, gaps[1:])) >= Fraction(1, 6)
        assert promoted.domain.validate_place_weighted_points_on_number_line_matrix(matrix)
        orders.add(payload["correct_answer"]["part_2"])
        exact = {label: float(Fraction(t)) for label, t in matrix["answer"]["positions"].items()}
        good = {"part_1": json.dumps(exact), "part_2": payload["correct_answer"]["part_2"]}
        assert check_answer(good, payload["correct_answer"], payload=payload)
        nudged = dict(exact, **{order[-1]: exact[order[-1]] - 0.2})
        assert not check_answer({**good, "part_1": json.dumps(nudged)}, payload["correct_answer"], payload=payload)
    assert len(orders) == 6


def test_validator_rejects_tampered_answers(promoted):
    matrix, _ = _source_payload(1029)
    for field, value in (("positions", {"P": "1/2", "Q": "1/2", "R": "1/4"}), ("relation", "Q<R<P"),
                         ("order", ["P", "Q", "R"]), ("tolerance", "1/5")):
        tampered = json.loads(json.dumps(matrix))
        tampered["answer"][field] = value
        assert not promoted.domain.validate_place_weighted_points_on_number_line_matrix(tampered), field


def test_refuses_ambiguous_or_malformed_placements(promoted):
    for constraints in (
        {"points": [PT("P", 1, 1), PT("Q", 2, 3)]},
        {"points": [PT("P", 1, 1), PT("Q", 2, 2)]},
        {"points": [PT("A", 1, 1), PT("Q", 1, 3)]},
        {"points": [PT("P", 1, 1), PT("P", 1, 3)]},
        {"points": [PT("P", 0, 1), PT("Q", 1, 3)]},
        {"points": [PT("P", "1/2", 1), PT("Q", 1, 3)]},
        {"points": [PT("P", 1, 1)]},
        {"points": [PT("P", 1, 1), PT("Q", 1, 3)], "notation": "interval"},
    ):
        with pytest.raises(ValueError):
            _dispatch(PLACE, **constraints)


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
            assert _latex_ok(payload["question_text"])
            seen.add(json.dumps(matrix["givens"], sort_keys=True))
        assert len(seen) > 2, op


# --- the placement checker itself ---------------------------------------------------------------

def test_placement_checker_formats_and_tolerance_boundary():
    expected = "P=3/4, Q=1/2, R=1/4"
    assert parse_placement('{"p": 0.75, "Q": "1/2", "R": 0.25}') == {"P": Fraction(3, 4), "Q": Fraction(1, 2),
                                                                    "R": Fraction(1, 4)}
    assert parse_placement("P=3/4，Q=1/2，R=1/4") == parse_placement(expected)
    assert parse_placement("P 3/4") is None and parse_placement("") is None and parse_placement({"P": True}) is None
    contract = {"tolerance": "1/20"}
    edge = {"P": "4/5", "Q": "1/2", "R": "1/4"}
    assert check_number_line_placement_answer(edge, expected, answer_contract=contract)["correct"]
    beyond = {"P": "801/1000", "Q": "1/2", "R": "1/4"}
    result = check_number_line_placement_answer(beyond, expected, answer_contract=contract)
    assert not result["correct"] and result["misplaced"] == ["P"]
    assert check_number_line_placement_answer("not json", expected)["reason"] == "unparseable_placement"
    assert check_number_line_placement_answer({"P": 0.5}, "garbage")["system_error"]
