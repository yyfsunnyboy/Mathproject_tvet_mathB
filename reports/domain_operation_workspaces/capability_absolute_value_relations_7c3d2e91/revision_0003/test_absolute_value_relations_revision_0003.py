# -*- coding: utf-8 -*-
"""Revision 0003 review evidence for algebra.absolute_value_relations: formal preflight plus an
isolated (temp-store) promotion.  Nothing here writes the production store or package root.

Revision 0003 keeps every revision 0002 fix, extends the domain (constant-0 relation side, rational /
a>b weighted points, symbolic distance statements, a number-line statement operation and the
tolerance-range application) and adjusts presentation (AP:BP, brace systems).  Until a human
approves revision 0003, the isolated promotion records the approval on a temp copy only.
"""

from __future__ import annotations

import importlib
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

from core.gencode.answer_payload import validate_answer_contract_consistency
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.reviewed_capability_promotion import BUNDLE_FILENAME, preflight_reviewed_bundle, promote_reviewed_workspace
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority
from core.registry import promoted_capability_store as store_mod
from core.registry.domain_operation_registry import get_domain_spec

REVISION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = REVISION_DIR.parents[3]
PRODUCTION_STORE = PROJECT_ROOT / "configs" / "gencode_promoted_capabilities.json"
DOMAIN_KEY = "algebra.absolute_value_relations"
POINT, EQ, INEQ = (
    "gh_PointDivisionFormulaOnNumberLine", "gh_LinearEquationsWithAbsoluteValue", "gh_LinearInequalitiesWithAbsoluteValue",
)
SKILLS = [POINT, EQ, INEQ]
DIVISION, EQUATIONS, INEQUALITIES = (
    "evaluate_number_line_division_points", "solve_absolute_value_equations", "solve_absolute_value_inequalities",
)
RECOVER, STATEMENTS, EXTREME = (
    "recover_absolute_value_parameters", "evaluate_absolute_value_statements", "select_extreme_weighted_point",
)
LINE_STATEMENTS, TOLERANCE = "evaluate_number_line_statements", "solve_tolerance_range_application"
OLD_OPERATIONS = {DIVISION, EQUATIONS, INEQUALITIES, RECOVER, STATEMENTS, EXTREME}
OPERATIONS = OLD_OPERATIONS | {LINE_STATEMENTS, TOLERANCE}
BINDINGS = {
    POINT: [DIVISION, LINE_STATEMENTS, EXTREME],
    EQ: [EQUATIONS],
    INEQ: [INEQUALITIES, RECOVER, STATEMENTS, TOLERANCE],
}


def F(*pairs):
    return [[c, d] for c, d in zip(pairs[::2], pairs[1::2])]


def ABS(form, coef=1):
    return {"abs": form} if coef == 1 else {"abs": form, "coef": coef}


def C(c):
    return [{"poly": [[c, 0]]}]


ZERO = C(0)


def REL(lhs, op, rhs):
    return {"lhs": lhs, "op": op, "rhs": rhs}


def ONE(form, op, c):
    return {"relations": [REL([ABS(form)], op, C(c))]}


def CHAIN(form, low, op1, op2, high):
    return {"joiner": "chain", "relations": [REL(C(low), op1, [ABS(form)]), REL([ABS(form)], op2, C(high))]}


def BRACE(*relations):
    return {"joiner": "and", "relations": list(relations)}


SHIFT_A = [[1, 1], [{"param": "a", "sign": -1}, 0]]

# the new (Stage 1) textbook rows of 單元2, in the domain's structured input form, with textbook answers
SOURCES = {
    1027: (DIVISION, {"points": {"A": -1, "B": 15}, "intro": "points_first", "parts": [
        {"find": "internal", "label": "P", "variable": "x", "ratio": [3, 5]},
        {"find": "external", "label": "Q", "variable": "y", "ratio": [3, 5]}]}, {"part_1": "5", "part_2": "-25"}),
    1028: (DIVISION, {"points": {"A": 12, "B": -6}, "intro": "line_first", "parts": [
        {"find": "internal", "label": "P", "ratio": [2, 1], "ratio_style": "multiple", "position": "between"},
        {"find": "external", "label": "Q", "ratio": [7, 1]}]}, {"part_1": "0", "part_2": "-9"}),
    1038: (LINE_STATEMENTS, {"statements": [{"kind": "symbolic_distance", "parameter": "a",
                                             "points": {"A": [[1, 1]], "B": -4},
                                             "claim": {"abs": True, "form": [[1, 1], [4, 0]]}}]}, "○"),
    1039: (LINE_STATEMENTS, {"statements": [{"kind": "weighted_point_order", "left": [2, 1], "op": ">", "right": [1, 2]}]},
           "×"),
    1041: (DIVISION, {"points": {"A": 5, "B": 12}, "parts": [
        {"find": "distance"}, {"find": "internal", "label": "P", "variable": "x", "ratio": [3, 4]},
        {"find": "external", "label": "Q", "variable": "y", "ratio": [3, 4]}]},
           {"part_1": "7", "part_2": "8", "part_3": "-16"}),
    1042: (EXTREME, {"options": [[4, 1], [2, 3], [3, 2], [1, 4]], "extreme": "max"}, "D"),
    1030: (EQUATIONS, {"equations": [REL([ABS(F(1, 1, -1, 0))], "=", C(2)), REL([ABS(F(2, 0, -1, 1))], "=", C(4)),
                                     REL([ABS(F(2, 1, -3, 0))], "=", C(5))]},
           {"part_1": "-1, 3", "part_2": "-2, 6", "part_3": "-1, 4"}),
    12327: (EQUATIONS, {"equations": [REL([ABS(F(1, 1, 3, 0)), {"poly": F(-2, 1)}], "=", ZERO)]}, "3"),
    1047: (EQUATIONS, {"equations": [REL([ABS(F(1, 1, 7, 0))], "=", [ABS(F(1, 1, -1, 0), 3)])],
                       "prompt": "find_real_x", "state_solution_count": True}, "-1, 5"),
    1035: (INEQUALITIES, {"systems": [BRACE(REL([ABS(F(1, 1))], "<", C(2)), REL([ABS(F(1, 1, -2, 0))], "<", C(1))),
                                      CHAIN(F(2, 1, -1, 0), 1, "<=", "<", 5)]},
           {"part_1": "(1,2)", "part_2": "(-2,0]∪[1,3)"}),
    12331: (INEQUALITIES, {"systems": [BRACE(REL([ABS(F(1, 1, 1, 0))], "<", C(3)), REL([ABS(F(1, 0, -1, 1))], "<=", C(4))),
                                       CHAIN(F(2, 1, -3, 0), 1, "<", "<", 4)]},
            {"part_1": "[-3,2)", "part_2": "(-1/2,1)∪(2,7/2)"}),
    1045: (INEQUALITIES, {"systems": [BRACE(REL([ABS(F(1, 1, -2, 0))], "<", C(3)), REL([ABS(F(1, 1))], ">", C(4))),
                                      CHAIN(F(-3, 1, 2, 0), 2, "<=", "<", 5)]},
           {"part_1": "(4,5)", "part_2": "(-1,0]∪[4/3,7/3)"}),
    12332: (INEQUALITIES, {"systems": [{"relations": [REL([ABS(F(1, 1, -6, 0))], ">=", [{"poly": F(1, 1)}])]}]}, "(-∞,3]"),
    1040: (STATEMENTS, {"statements": [{"kind": "same_solution_set", "left": REL([ABS(F(1, 1, -1, 0))], "<=", C(3)),
                                        "right": REL([ABS(F(1, 0, -1, 1))], "<=", C(3))}]}, "○"),
    1046: (RECOVER, {"relations": [{"inner": SHIFT_A, "op": "<=", "bound": {"param": "b"}}], "parameters": ["a", "b"],
                     "prompt": "pregnancy_weeks", "target": [[37, 41, True, True]]}, {"a": "39", "b": "2"}),
    12333: (TOLERANCE, {"profile": "standard_weight_male", "height": 180, "tolerance_percent": 10},
            {"part_1": "70", "a": "70", "b": "7"}),
}
SOURCE_SKILL = {1027: POINT, 1028: POINT, 1038: POINT, 1039: POINT, 1041: POINT, 1042: POINT,
                1030: EQ, 12327: EQ, 1047: EQ}


def _production_package_names() -> list[str]:
    return sorted(p.name for p in (PROJECT_ROOT / "core" / "domain" / "promoted").iterdir() if p.name != "__pycache__")


@pytest.fixture(scope="module")
def promoted():
    production_store_bytes = PRODUCTION_STORE.read_bytes()
    production_before = _production_package_names()
    prefix_dir = f"absolute_value_relations_revision_0003_{uuid.uuid4().hex[:10]}"
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
        bundle["review"].update(status="human_approved", approved_by="isolated_test_only", approved_revision=3)
        (workspace / BUNDLE_FILENAME).write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
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
        if chunk.count("\\begin{") != chunk.count("\\end{"):
            return False
    return True


# --- formal review state ---------------------------------------------------------

def test_formal_preflight_blocks_only_on_pending_review():
    report = preflight_reviewed_bundle(REVISION_DIR)
    bundle = report["bundle"]
    assert bundle["proposal_revision"] == 3
    if bundle["review"].get("status") == "human_approved":
        assert report["passed"], report["blockers"]
        assert bundle["review"]["approved_revision"] == 3
    else:
        assert report["blockers"] == ["human_review_not_approved", "approved_revision_mismatch"]
    assert set(bundle["operations"]) == OPERATIONS == set(bundle["capabilities"])
    assert {k: v["allowed_operations"] for k, v in bundle["skill_bindings"].items()} == BINDINGS


def test_package_compiles_and_keeps_revision_0002_init():
    rev2 = json.loads((REVISION_DIR.parent / "revision_0002" / BUNDLE_FILENAME).read_text(encoding="utf-8"))
    rev3 = json.loads((REVISION_DIR / BUNDLE_FILENAME).read_text(encoding="utf-8"))
    assert set(rev3["files"]) == set(rev2["files"])
    assert rev3["files"]["__init__.py"] == rev2["files"]["__init__.py"]
    for name in rev3["files"]:
        path = REVISION_DIR / rev3["package_dir"] / name
        compile(path.read_text(encoding="utf-8"), str(path), "exec")


def test_isolated_promotion_keeps_existing_domains(promoted):
    result = promoted.result
    assert result["promoted"] and not result["unchanged"]
    assert set(result["allowed_operations"]) == OPERATIONS == set(result["operations_executed"])
    assert set(get_domain_spec(DOMAIN_KEY).allowed_operations) == OPERATIONS
    production = json.loads(PRODUCTION_STORE.read_text(encoding="utf-8"))
    for key, entry in production["domains"].items():
        if key != DOMAIN_KEY:
            assert promoted.store["domains"][key] == entry
    for key, entry in production.get("skill_bindings", {}).items():
        if key not in SKILLS:
            assert promoted.store["skill_bindings"][key] == entry


# --- backward compatibility --------------------------------------------------------

def test_existing_operations_give_identical_matrices_to_the_promoted_revision(promoted):
    from core.domain.promoted.algebra_absolute_value_relations import absolute_value_relations_domain as current

    rev2 = json.loads((REVISION_DIR.parent / "revision_0002" / BUNDLE_FILENAME).read_text(encoding="utf-8"))
    checked = 0
    for op in sorted(OLD_OPERATIONS):
        cases = [(c["seed"], c["constraints"]) for c in rev2["smoke_cases"][op]] + [(s, {}) for s in range(40)]
        for seed, constraints in cases:
            old = current.build_absolute_value_relations_matrix(domain_operation=op, seed=seed, constraints=constraints)
            new = promoted.domain.build_absolute_value_relations_matrix(domain_operation=op, seed=seed, constraints=constraints)
            assert new == old, (op, seed)
            assert getattr(promoted.domain, f"validate_{op}_matrix")(new)
            checked += 1
    assert checked > 250


# --- skill binding and routing -----------------------------------------------------

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
    op, _, expected = SOURCES[example_id]
    matrix, payload = _source_payload(example_id)
    assert getattr(promoted.domain, f"validate_{op}_matrix")(matrix)
    assert payload["correct_answer"] == expected
    assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"
    assert validate_answer_contract_consistency(payload["answer_contract"]) == []
    assert check_answer(expected, expected, payload=payload)
    assert _latex_ok(payload["question_text"]) and all(_latex_ok(s) for s in payload["explanation_steps"])
    assert _latex_ok(payload["display_answer"])


@pytest.mark.parametrize(("example_id", "answer", "accepted"), [
    (1027, {"part_1": "5", "part_2": "-25"}, True),
    (1027, {"part_1": "5", "part_2": "25"}, False),
    (1028, {"part_1": "0", "part_2": "-9"}, True),
    (1028, {"part_1": "0", "part_2": "9"}, False),
    (1038, "○", True),
    (1038, "A", True),
    (1038, "×", False),
    (1038, "B", False),
    (1039, "×", True),
    (1039, "B", True),
    (1039, "○", False),
    (1042, "D", True),
    (1042, "4", True),
    (1042, "\\frac{a+4b}{5}", True),
    (1042, "A", False),
    (12327, "3", True),
    (12327, "x=3", True),
    (12327, "-1", False),
    (12327, "3, -1", False),
    (12327, "無解", False),
    (1035, {"part_1": "1<x<2", "part_2": "-2<x\\le 0 或 1\\le x<3"}, True),
    (1035, {"part_1": "1<x<2", "part_2": "(-2,0)∪(1,3)"}, False),
    (12331, {"part_1": "-3\\le x<2", "part_2": "(-1/2,1)∪(2,7/2)"}, True),
    (12331, {"part_1": "(-3,2)", "part_2": "(-1/2,1)∪(2,7/2)"}, False),
    (12333, {"part_1": "70", "a": "70", "b": "7"}, True),
    (12333, {"part_1": "70.0", "a": "70", "b": "7.0"}, True),
    (12333, {"part_1": "70", "a": "7", "b": "70"}, False),
    (12333, {"part_1": "70", "a": "70", "b": "14"}, False),
    (12333, {"part_1": "63", "a": "70", "b": "7"}, False),
])
def test_grading_uses_exact_equivalence(promoted, example_id, answer, accepted):
    _, payload = _source_payload(example_id)
    assert bool(check_answer(answer, payload["correct_answer"], payload=payload)) is accepted


# --- presentation -----------------------------------------------------------------------

def test_division_ratio_is_written_ap_to_bp(promoted):
    text = _source_payload(1027)[1]["question_text"]
    assert "$\\overline{AP}:\\overline{BP}=3:5$" in text and "$\\overline{AQ}:\\overline{BQ}=3:5$" in text
    assert "$\\overline{AP}=2\\overline{BP}$" in _source_payload(1028)[1]["question_text"]
    assert "\\overline{PB}" not in json.dumps(_source_payload(1041)[1]["explanation_steps"])


def test_systems_use_a_left_brace(promoted):
    question = _source_payload(1035)[1]["question_text"]
    assert question.startswith("解下列各不等式：\n(1) $\\left\\{\\begin{array}{l}\\left|x\\right|<2\\\\\\left|x-2\\right|<1"
                               "\\end{array}\\right.$。\n(2) $1\\le \\left|2x-1\\right|<5$。")
    assert " 且 " not in question


def test_new_textbook_texts(promoted):
    assert _source_payload(1038)[1]["question_text"].endswith("數線上 $A(a)$ 與 $B(-4)$ 的距離為 $\\left|a+4\\right|$。")
    assert _source_payload(1039)[1]["question_text"].endswith("若 $a<b$，則 $\\frac{2a+b}{3}>\\frac{a+2b}{3}$。")
    assert _source_payload(12327)[1]["question_text"] == "解方程式 $\\left|x+3\\right|-2x=0$。"
    payload = _source_payload(12333)[1]
    assert "\\text{標準體重}_{(\\mathrm{kg})}" in payload["question_text"] and "$10\\%$" in payload["question_text"]
    assert [p["label"] for p in payload["answer_contract"]["parts"]] == ["(1)", "(2) a", "(2) b"]
    payload = _source_payload(1042)[1]
    assert [c["label"] for c in payload["choices"]] == ["A", "B", "C", "D"]
    assert all(c["text"] == c["value"] for c in payload["choices"])
    assert payload["correct_answer"] == "D" and payload["display_answer"] == "(D) $\\frac{a+4b}{5}$"


# --- new domain behaviour with independent oracles ------------------------------------

def _roots_bruteforce(relation, lo=-40, hi=40, den=6):
    from core.domain.promoted.algebra_absolute_value_relations.absolute_value_relations_domain import relation_holds

    return sorted({Fraction(n, den) for n in range(lo * den, hi * den + 1) if relation_holds(relation, Fraction(n, den))})


@pytest.mark.parametrize(("equation", "expected"), [
    (REL([ABS(F(1, 1, 3, 0)), {"poly": F(-2, 1)}], "=", ZERO), "3"),
    (REL([ABS(F(1, 1, -1, 0)), {"poly": F(-2, 0)}], "=", ZERO), "-1, 3"),
    (REL([ABS(F(1, 1)), {"poly": F(1, 0)}], "=", ZERO), "無解"),
    (REL(ZERO, "=", [ABS(F(2, 1, -3, 0)), {"poly": F(-1, 1)}]), "1, 3"),
])
def test_constant_zero_side_equations(promoted, equation, expected):
    matrix, payload = _dispatch(EQUATIONS, equations=[equation])
    assert payload["correct_answer"] == expected
    assert promoted.domain.validate_solve_absolute_value_equations_matrix(matrix)
    found = [Fraction(s) for s in matrix["answer"]["parts"][0]["solutions"]]
    assert found == _roots_bruteforce(matrix["givens"]["equations"][0])
    assert "=0" in payload["question_text"] or "0=" in payload["question_text"]


def test_zero_side_matches_the_equivalent_equation(promoted):
    rng = random.Random("rev3-zero-side")
    for _ in range(60):
        p, k = rng.choice([n for n in range(-9, 10) if n]), rng.randint(2, 4)
        zero_form, _ = _dispatch(EQUATIONS, equations=[REL([ABS(F(1, 1, p, 0)), {"poly": F(-k, 1)}], "=", ZERO)])
        moved, _ = _dispatch(EQUATIONS, equations=[REL([ABS(F(1, 1, p, 0))], "=", [{"poly": F(k, 1)}])])
        assert zero_form["answer"]["parts"][0]["solutions"] == moved["answer"]["parts"][0]["solutions"]


def _distance_truth_oracle(statement):
    a = statement["points"]["A"]
    b = statement["points"]["B"]

    def value(form, t):
        if not isinstance(form, list):
            return Fraction(form)
        return sum((Fraction(c) * (t if d == 1 else 1) for c, d in form), Fraction(0))

    cond = statement.get("condition")
    ok = True
    for n in range(-120, 121):
        t = Fraction(n, 6)
        if cond and not {"<": t < Fraction(cond["value"]), "<=": t <= Fraction(cond["value"]),
                         ">": t > Fraction(cond["value"]), ">=": t >= Fraction(cond["value"])}[cond["op"]]:
            continue
        claimed = value(statement["claim"]["form"], t)
        if statement["claim"]["abs"]:
            claimed = abs(claimed)
        ok &= abs(value(a, t) - value(b, t)) == claimed
    return ok


def test_symbolic_distance_against_bruteforce(promoted):
    rng = random.Random("rev3-symbolic")
    truths = []
    for _ in range(300):
        c = rng.randint(-9, 9)
        k = rng.choice([1, 1, 2, -1])
        a_form = [[k, 1]] if rng.random() < 0.7 else [[k, 1], [rng.choice([n for n in range(-5, 6) if n]), 0]]
        claim_form = rng.choice([
            [[k, 1], [-c, 0]], [[-k, 1], [c, 0]], [[k, 1], [c, 0]] if c else [[k, 1]], [[1, 1], [-c, 0]],
        ])
        claim_form = [[x, d] for x, d in claim_form if x] or [[1, 1]]
        statement = {"kind": "symbolic_distance", "parameter": "a", "points": {"A": a_form, "B": c},
                     "claim": {"abs": rng.random() < 0.7, "form": claim_form}}
        if rng.random() < 0.3:
            statement["condition"] = {"op": rng.choice(INEQ_OPS), "value": rng.randint(-6, 6)}
        try:
            matrix, payload = _dispatch(LINE_STATEMENTS, statements=[statement])
        except ValueError:
            continue
        truth = matrix["answer"]["truth_values"][0]
        assert truth == _distance_truth_oracle(statement), statement
        assert promoted.domain.validate_evaluate_number_line_statements_matrix(matrix)
        assert payload["correct_answer"] == ("○" if truth else "×")
        assert _latex_ok(payload["question_text"])
        truths.append(truth)
    assert len(truths) > 200 and any(truths) and not all(truths)


INEQ_OPS = ("<", "<=", ">", ">=")


def test_weighted_points_with_order_and_rational_weights(promoted):
    rng = random.Random("rev3-weighted")
    weights = [1, 2, 3, 4, "1/2", "1/3", "2/3", "3/4"]
    for _ in range(300):
        left, right = [rng.choice(weights) for _ in range(2)], [rng.choice(weights) for _ in range(2)]
        order, op = rng.choice(["a<b", "a>b"]), rng.choice(("<", ">", "<=", ">=", "="))
        statement = {"kind": "weighted_point_order", "left": left, "op": op, "right": right, "order": order}
        matrix, payload = _dispatch(LINE_STATEMENTS, statements=[statement])
        a, b = (Fraction(-7), Fraction(11)) if order == "a<b" else (Fraction(11), Fraction(-7))

        def val(w):
            p, q = Fraction(w[0]), Fraction(w[1])
            return (p * a + q * b) / (p + q)

        diff = val(left) - val(right)
        expected = {"<": diff < 0, ">": diff > 0, "<=": diff <= 0, ">=": diff >= 0, "=": diff == 0}[op]
        assert matrix["answer"]["truth_values"][0] == expected
        assert promoted.domain.validate_evaluate_number_line_statements_matrix(matrix)
        assert (order == "a>b") == ("$a>b$" in payload["question_text"])
        assert _latex_ok(payload["question_text"])


def test_extreme_choice_respects_order(promoted):
    for order, extreme, label in (("a<b", "max", "D"), ("a>b", "max", "A"), ("a<b", "min", "A"), ("a>b", "min", "D")):
        constraints = {"options": [[4, 1], [2, 3], [3, 2], [1, 4]], "extreme": extreme}
        if order == "a>b":
            constraints["order"] = order
        matrix, payload = _dispatch(EXTREME, **constraints)
        assert payload["display_answer"].startswith(f"({label})")
        assert check_answer(label, payload["correct_answer"], payload=payload)
        assert promoted.domain.validate_select_extreme_weighted_point_matrix(matrix)
    rational, _ = _dispatch(EXTREME, options=[["1/2", "1/2"], ["1/3", "2/3"], ["3/4", "1/4"]], extreme="max")
    assert rational["answer"]["choice"] == 2


def test_tolerance_application_against_direct_arithmetic(promoted):
    profiles = {"standard_weight_male": (80, Fraction(7, 10), range(160, 191)),
                "standard_weight_female": (70, Fraction(6, 10), range(150, 181))}
    for profile, (offset, factor, heights) in profiles.items():
        for height in heights:
            for percent in (5, 10, 15, 20):
                matrix, payload = _dispatch(TOLERANCE, profile=profile, height=height, tolerance_percent=percent)
                w = (height - offset) * factor
                assert Fraction(payload["correct_answer"]["part_1"]) == w
                a, b = Fraction(payload["correct_answer"]["a"]), Fraction(payload["correct_answer"]["b"])
                assert (a, b) == (w, w * percent / 100)
                low, high = w * (1 - Fraction(percent, 100)), w * (1 + Fraction(percent, 100))
                assert (a - b, a + b) == (low, high)
                assert promoted.domain.validate_solve_tolerance_range_application_matrix(matrix)
                assert 30 <= w <= 90
                assert _latex_ok(payload["question_text"])


def test_refuses_inputs_outside_the_operations(promoted):
    with pytest.raises(ValueError):
        _dispatch(EQUATIONS, equations=[REL(ZERO, "=", ZERO)])
    with pytest.raises(ValueError):
        _dispatch(EQUATIONS, equations=[REL([ABS(F(1, 1)), {"poly": F(-1, 1)}], "=", ZERO)])
    with pytest.raises(ValueError):
        _dispatch(EQUATIONS, equations=[REL([ABS(F(1, 1))], "=", [{"poly": [[0, 0], [1, 1]]}])])
    with pytest.raises(ValueError):
        _dispatch(LINE_STATEMENTS, statements=[{"kind": "symbolic_distance", "parameter": "a", "points": {"A": 3, "B": -4},
                                                "claim": {"abs": True, "form": [[7, 0]]}}])
    with pytest.raises(ValueError):
        _dispatch(LINE_STATEMENTS, statements=[{"kind": "symbolic_distance", "parameter": "x",
                                                "points": {"A": [[1, 1]], "B": -4},
                                                "claim": {"abs": True, "form": [[1, 1], [4, 0]]}}])
    with pytest.raises(ValueError):
        _dispatch(LINE_STATEMENTS, statements=SOURCES[1040][1]["statements"])
    with pytest.raises(ValueError):
        _dispatch(LINE_STATEMENTS, statements=[{"kind": "weighted_point_order", "left": [-1, 2], "op": ">", "right": [1, 2]}])
    with pytest.raises(ValueError):
        _dispatch(LINE_STATEMENTS, statements=[{"kind": "weighted_point_order", "left": [1, 2], "op": ">", "right": [2, 1],
                                                "order": "a=b"}])
    with pytest.raises(ValueError):
        _dispatch(EXTREME, options=[[1, 1], ["1/2", "1/2"]], extreme="max")
    with pytest.raises(ValueError):
        _dispatch(TOLERANCE, profile="standard_weight_male", height=230, tolerance_percent=10)
    with pytest.raises(ValueError):
        _dispatch(TOLERANCE, profile="standard_weight_male", height=180, tolerance_percent=12)
    with pytest.raises(ValueError):
        _dispatch(TOLERANCE, profile="bmi", height=180, tolerance_percent=10)


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
