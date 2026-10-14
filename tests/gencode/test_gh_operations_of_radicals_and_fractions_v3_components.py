from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path

import pytest
import sympy as sp

from core.checkers.expression_equivalence_checker import _parse_sympy
from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.gencode.answer_payload import validate_answer_contract_consistency
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.services.admin_gencode_action_service import (
    _execute_component_direct_smoke_and_validation,
)
from core.gencode.services.v3_question_integrity_validator import validate_component_payload
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_ID = "gh_OperationsOfRadicalsAndFractions"
DOMAIN_KEY = "algebra.radical_operations"
COMPONENTS_DIR = PROJECT_ROOT / "agent_skills_v3" / SKILL_ID / "components"
DRYRUN_COMPONENTS_DIR = PROJECT_ROOT / "reports" / "gencode_v3_dryrun" / SKILL_ID / "components"
STORE_PATH = PROJECT_ROOT / "configs" / "gencode_promoted_capabilities.json"
SEEDS = range(20)

FRACTIONS = "simplify_radical_fraction_expressions"
DENEST = "denest_square_roots"
PARTS = "evaluate_integer_fraction_part_expression"
ORDER = "order_radical_numbers"
DILATION = "evaluate_time_dilation_relations"
AM_GM = "optimize_by_am_gm"
NEAREST = "nearest_integer_from_radical_relation"

# seed 0 = textbook item; answers worked out from the textbook statements
TEXTBOOK = {
    "src_12302": (FRACTIONS, {"part_1": "sqrt(2)+sqrt(3)", "part_2": "3"}),
    "src_12303": (ORDER, {"part_1": "c>b>a"}),
    "src_12304": (DILATION, {"part_1": "65", "part_2": "36"}),
    "src_12305": (DENEST, {"part_1": "1+sqrt(3)", "part_2": "-sqrt(2)+sqrt(5)", "part_3": "-sqrt(2)+sqrt(6)"}),
    "src_12306": (PARTS, "1-sqrt(2)"),
    "src_12307": (AM_GM, "9"),
    "src_12308": (FRACTIONS, {"part_1": "11sqrt(3)", "part_2": "8", "part_3": "2sqrt(5)/5"}),
    "src_12309": (FRACTIONS, {"part_1": "2-sqrt(3)", "part_2": "4"}),
    "src_12310": (ORDER, {"part_1": "c>b>a"}),
    "src_12311": (DILATION, "sqrt(3)/2"),
    "src_12312": (DENEST, {"part_1": "-1+sqrt(5)", "part_2": "1+sqrt(7)", "part_3": "sqrt(2)+sqrt(10)"}),
    "src_12313": (PARTS, "3+sqrt(5)"),
    "src_12314": (AM_GM, "8"),
    "src_12315": (FRACTIONS, {"part_1": "-5sqrt(3)", "part_2": "1/4", "part_3": "10"}),
    "src_12316": (NEAREST, "29"),
    "src_12317": (DENEST, {"part_1": "-sqrt(3)+sqrt(5)", "part_2": "1+sqrt(6)", "part_3": "3-sqrt(2)"}),
    "src_12318": (DENEST, "3+sqrt(5)"),
    "src_12319": (PARTS, "3/2-sqrt(3)/2"),
    "src_12320": (AM_GM, {"area": "200", "length": "20", "width": "10"}),
    "src_12321": (AM_GM, {"length": "4", "width": "4"}),
}
PUBLISHED_COMPONENT_IDS = sorted(TEXTBOOK)
# 化簡 / 化至最簡 demand the simplest radical form; 求值 rows only require equivalence
SIMPLEST_FORM_IDS = {"src_12302", "src_12305", "src_12308", "src_12309", "src_12312", "src_12315", "src_12317", "src_12318"}


def _ids(*operations):
    return [cid for cid, (op, _) in TEXTBOOK.items() if op in operations]


def _load(component_id: str, filename: str):
    path = COMPONENTS_DIR / component_id / filename
    spec = importlib.util.spec_from_file_location(f"gh_radicals_{component_id}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _grade(payload, user_answer):
    return bool(check_answer(
        user_answer,
        payload["correct_answer"],
        payload=payload,
        answer_contract=payload["answer_contract"],
        skill_id=SKILL_ID,
    ))


def _embedded_variants(component_id):
    tree = ast.parse((COMPONENTS_DIR / component_id / "generate.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "_materialize_generation_constraints":
            return ast.literal_eval(node.args[0].args[0])["generation_constraints"]["variants"]
    raise AssertionError("generation constraints literal missing")


# --- independent sympy model of the givens ------------------------------------------

def _q(value):
    return sp.Rational(str(value))


def _sum(terms):
    return sp.Add(*[_q(c) * sp.sqrt(_q(r)) for c, r in terms])


def _product(factors):
    return sp.Mul(*[_sum(f["terms"]) ** int(f["power"]) for f in factors])


def _term(term):
    denominator = _product(term["denominator"]) if term["denominator"] else sp.Integer(1)
    return _q(term["coefficient"]) * _product(term["numerator"]) / denominator


def _term_text(term):
    def product(factors):
        return "*".join("(" + "+".join(f"({c})*sqrt({r})" for c, r in f["terms"]) + f")**{f['power']}" for f in factors)
    return f"({term['coefficient']})*({product(term['numerator'])})/({product(term['denominator']) or '1'})"


def _nested(root):
    return sp.sqrt(_q(root["rational"]) + _q(root["radical"][0]) * sp.sqrt(int(root["radical"][1])))


def _same(a, b):
    return sp.simplify(sp.radsimp(a - b)) == 0 or abs(sp.N(a - b, 60)) < sp.Float("1e-45")


def _reversed(text):
    return " + ".join(f"({t})" for t in reversed(sp.Add.make_args(sp.expand(_parse_sympy(text)))))


# --- component contract ------------------------------------------------------

@pytest.mark.parametrize("component_id", PUBLISHED_COMPONENT_IDS)
def test_component_files_follow_v3_contract(component_id):
    directory = COMPONENTS_DIR / component_id
    assert {p.name for p in directory.iterdir() if p.is_file()} == {"generate.py", "metadata.py", "get_hint.py"}
    assert (directory / "get_hint.py").read_text(encoding="utf-8") == _build_get_hint_py()
    for filename in ("generate.py", "metadata.py", "get_hint.py"):
        assert (directory / filename).read_bytes() == (DRYRUN_COMPONENTS_DIR / component_id / filename).read_bytes()


def test_published_wrapper_routes_only_published_components():
    manifest = json.loads((COMPONENTS_DIR.parent / "component_manifest.json").read_text(encoding="utf-8"))
    assert [row["component_id"] for row in manifest["components"]] == PUBLISHED_COMPONENT_IDS
    wrapper = (PROJECT_ROOT / "skills" / f"{SKILL_ID}.py").read_text(encoding="utf-8")
    assert f"GENERATOR_KEYS = {PUBLISHED_COMPONENT_IDS!r}" in wrapper
    assert "backup_GenByGemini" not in wrapper


@pytest.mark.parametrize("component_id", PUBLISHED_COMPONENT_IDS)
def test_generation_constraint_variants_are_inputs_only_and_seed_stable(component_id):
    variants = _embedded_variants(component_id)
    assert len(variants) == 20
    assert len({json.dumps(v, sort_keys=True) for v in variants}) == 20
    forbidden = {"answer", "correct_answer", "canonical_answer", "answer_contract", "checker", "checker_key"}
    assert all(set(v) == set(variants[0]) and not forbidden & set(v) for v in variants)
    generator = _load(component_id, "generate.py")
    for seed in (0, 7, 19):
        assert generator.generate(seed=seed)["math_core"]["givens"] == generator.generate(seed=seed + 20)["math_core"]["givens"]


@pytest.mark.parametrize("component_id", PUBLISHED_COMPONENT_IDS)
def test_generator_only_uses_production_dispatch(component_id):
    source = (COMPONENTS_DIR / component_id / "generate.py").read_text(encoding="utf-8")
    imported = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module)
    production_route = {"core.gencode.registered_operation_dispatch", "core.gencode.skill_fixed_domain_authority"}
    assert production_route <= imported <= production_route | {"__future__", "copy", "typing"}
    code = source.replace(SKILL_ID, "")
    for forbidden in ("domain_operation_workspaces", "revision_0", "temp.", "skills.", "Fraction", "sympy", "isqrt",
                      "math.sqrt", "sqrt(", "check_answer"):
        assert forbidden not in code


@pytest.mark.parametrize("component_id", PUBLISHED_COMPONENT_IDS)
def test_metadata_matches_payload_contract(component_id):
    operation, source_answer = TEXTBOOK[component_id]
    metadata = _load(component_id, "metadata.py")
    payload = _load(component_id, "generate.py").generate(seed=3)
    contract = payload["answer_contract"]
    assert metadata.TEXTBOOK_EXAMPLE_ID == int(component_id.removeprefix("src_"))
    assert metadata.SKILL_ID == SKILL_ID
    assert metadata.DOMAIN_OPERATION == payload["domain_operation"] == operation
    assert metadata.PRESENTATION_MODE == metadata.RESPONSE_MODE == payload["presentation_mode"]
    assert payload["presentation_mode"] == ("multiple_inputs" if isinstance(source_answer, dict) else "short_answer")
    assert metadata.ANSWER_VERIFICATION_TYPE["checker_key"] == contract["checker_key"]
    assert metadata.ANSWER_VERIFICATION_TYPE["equivalence_type"] == contract["equivalence_type"]
    if not isinstance(source_answer, dict):
        assert metadata.ANSWER_TYPE == payload["answer_type"]


@pytest.mark.parametrize("component_id", PUBLISHED_COMPONENT_IDS)
def test_routes_through_confirmed_binding_to_promoted_domain(component_id):
    payload = _load(component_id, "generate.py").generate(seed=11)
    store = json.loads(STORE_PATH.read_text(encoding="utf-8"))
    resolution = payload["domain_resolution"]
    assert resolution["binding_status"] == "confirmed"
    assert resolution["resolution_source"] == "confirmed_binding"
    assert resolution["fixed_domain_key"] == payload["fixed_domain_key"] == DOMAIN_KEY
    assert resolution["selected_operation"] == payload["domain_operation"]
    assert resolution["registry_revision"] == store["domains"][DOMAIN_KEY]["registry_revision"]


@pytest.mark.parametrize("component_id", PUBLISHED_COMPONENT_IDS)
def test_formal_direct_smoke_and_integrity_validation(component_id):
    result = _execute_component_direct_smoke_and_validation(
        skill_id=SKILL_ID, component_id=component_id, dryrun_base_dir="agent_skills_v3", seed=42,
    )
    assert result["compile_passed"] and result["smoke_passed"] and result["validation_passed"], result


# --- source fidelity -----------------------------------------------------------

@pytest.mark.parametrize("component_id", PUBLISHED_COMPONENT_IDS)
def test_seed_zero_is_textbook_item(component_id):
    _, answer = TEXTBOOK[component_id]
    assert _load(component_id, "generate.py").generate(seed=0)["correct_answer"] == answer


@pytest.mark.parametrize("component_id", PUBLISHED_COMPONENT_IDS)
def test_seeds_keep_subpart_topology_and_contract(component_id):
    _, source_answer = TEXTBOOK[component_id]
    generator = _load(component_id, "generate.py")
    questions = set()
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        contract = payload["answer_contract"]
        assert validate_answer_contract_capability(contract)["checker_capability_status"] == "ok"
        assert validate_answer_contract_consistency(contract) == []
        integrity = validate_component_payload(payload, component_id=component_id)
        assert integrity["passed"], integrity["blockers"]
        questions.add(payload["question_text"])
        form = "simplest_radical" if component_id in SIMPLEST_FORM_IDS else None
        if isinstance(source_answer, dict):
            assert list(payload["correct_answer"]) == list(source_answer)
            assert [p["key"] for p in contract["parts"]] == list(source_answer)
            assert {p.get("required_form") for p in contract["parts"]} == {form}
        else:
            assert isinstance(payload["correct_answer"], str)
            assert contract.get("required_form") == form
    assert len(questions) == 20


# --- independent sympy oracle + grading ------------------------------------------

@pytest.mark.parametrize("component_id", _ids(FRACTIONS))
def test_fraction_simplification_matches_sympy_and_requires_simplest_form(component_id):
    generator = _load(component_id, "generate.py")
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        expected = payload["correct_answer"]
        reordered = {}
        for i, expression in enumerate(payload["math_core"]["givens"]["expressions"], start=1):
            key = f"part_{i}"
            assert _same(sp.Add(*[_term(t) for t in expression]), _parse_sympy(expected[key]))
            reordered[key] = _reversed(expected[key])
            assert not _grade(payload, {**expected, key: " + ".join(_term_text(t) for t in expression)})
        assert _grade(payload, expected) and _grade(payload, reordered)
        assert check_multi_part_answer(reordered, expected, payload=payload)["overall_correct"]
        assert not _grade(payload, {**expected, "part_1": f"{expected['part_1']}+1"})


@pytest.mark.parametrize("component_id", _ids(DENEST))
def test_denesting_matches_sympy_and_requires_simplest_form(component_id):
    generator = _load(component_id, "generate.py")
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        expected = payload["correct_answer"]
        roots = payload["math_core"]["givens"]["roots"]
        answers = expected if isinstance(expected, dict) else {"_": expected}
        for root, text in zip(roots, answers.values()):
            truth = _nested(root)
            assert sp.sqrtdenest(truth) != truth and _same(truth, _parse_sympy(text))
        nested_text = f"sqrt({roots[0]['rational']}+({roots[0]['radical'][0]})*sqrt({roots[0]['radical'][1]}))"
        if isinstance(expected, dict):
            assert _grade(payload, {k: _reversed(v) for k, v in expected.items()})
            assert not _grade(payload, {**expected, "part_1": nested_text})
            assert not _grade(payload, {**expected, "part_1": str(-_parse_sympy(expected["part_1"]))})
        else:
            assert _grade(payload, _reversed(expected))
            assert not _grade(payload, nested_text)
            assert not _grade(payload, str(-_parse_sympy(expected)))


@pytest.mark.parametrize("component_id", _ids(PARTS))
def test_integer_and_fraction_part_value_matches_sympy(component_id):
    generator = _load(component_id, "generate.py")
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        givens, expected = payload["math_core"]["givens"], payload["correct_answer"]
        value = sp.sqrtdenest(_nested(givens["root"]))
        a = int(sp.floor(value))
        b = value - a
        assert _same(a + givens["sign"] / b, _parse_sympy(expected))
        assert _grade(payload, expected) and _grade(payload, _reversed(expected))
        assert _grade(payload, f"{a}+({givens['sign']})/({sp.sstr(b)})")
        assert not _grade(payload, sp.sstr(sp.radsimp(a - givens["sign"] / b)))


@pytest.mark.parametrize("component_id", _ids(ORDER))
def test_ordering_matches_high_precision_values(component_id):
    generator = _load(component_id, "generate.py")
    orders = set()
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        numbers = payload["math_core"]["givens"]["numbers"]
        order = sorted((n["label"] for n in numbers),
                       key=lambda label: sp.N(_term(next(n["term"] for n in numbers if n["label"] == label)), 60), reverse=True)
        assert payload["correct_answer"] == {"part_1": ">".join(order)}
        orders.add(">".join(order))
        assert _grade(payload, {"part_1": "<".join(reversed(order))})
        assert not _grade(payload, {"part_1": ">".join(reversed(order))})
    assert len(orders) > 1


@pytest.mark.parametrize("component_id", _ids(DILATION))
def test_time_dilation_matches_sympy(component_id):
    generator = _load(component_id, "generate.py")
    t, x = sp.Symbol("t", positive=True), sp.Symbol("x", positive=True)
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        relations, expected = payload["math_core"]["givens"]["relations"], payload["correct_answer"]
        answers = expected if isinstance(expected, dict) else {"_": expected}
        for relation, text in zip(relations, answers.values()):
            if relation["find"] == "earth_years":
                truth = _q(relation["traveler_years"]) / sp.sqrt(1 - _q(relation["speed_ratio"]) ** 2)
            elif relation["find"] == "travel_years_from_age_match":
                gamma = 1 / sp.sqrt(1 - _q(relation["speed_ratio"]) ** 2)
                truth = sp.solve(sp.Eq(_q(relation["traveler_age"]) + t, _q(relation["child_age"]) + gamma * t), t)[0]
            else:
                truth = sp.solve(sp.Eq(_q(relation["traveler_years"]) / sp.sqrt(1 - x ** 2), _q(relation["earth_years"])), x)[0]
            assert _same(truth, _parse_sympy(text))
        assert _grade(payload, expected)
        if isinstance(expected, dict):
            assert not _grade(payload, {**expected, "part_2": str(_q(expected["part_2"]) + 1)})
        else:
            assert not _grade(payload, str(_parse_sympy(expected) ** 2))


@pytest.mark.parametrize("component_id", _ids(AM_GM))
def test_am_gm_optimum_matches_calculus(component_id):
    generator = _load(component_id, "generate.py")
    x = sp.Symbol("x", positive=True)
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        problem, expected = payload["math_core"]["givens"]["problem"], payload["correct_answer"]
        if problem["kind"] == "max_product_linear_sum":
            p, q, total = _q(problem["p"]), _q(problem["q"]), _q(problem["total"])
            objective, other = x * (total - p * x) / q, (total - p * x) / q
        elif problem["kind"] == "min_linear_sum_fixed_product":
            p, q, product = _q(problem["p"]), _q(problem["q"]), _q(problem["product"])
            objective, other = p * x + q * product / x, product / x
        else:
            h, base = _q(problem["height"]), _q(problem["volume"]) / _q(problem["height"])
            objective, other = 2 * base + 2 * h * (x + base / x), base / x
        best = [s for s in sp.solve(sp.diff(objective, x), x) if s > 0][0]
        if isinstance(expected, str):
            assert _q(expected) == objective.subs(x, best)
            assert _grade(payload, f"{expected}.0") and not _grade(payload, str(_q(expected) + 1))
        elif "area" in expected:
            assert (_q(expected["area"]), _q(expected["length"]), _q(expected["width"])) == (
                objective.subs(x, best), other.subs(x, best), best)
            assert not _grade(payload, {**expected, "length": expected["width"], "width": expected["length"]})
        else:
            assert (_q(expected["length"]), _q(expected["width"])) == (other.subs(x, best), best)
            assert not _grade(payload, {"length": str(2 * _q(expected["length"])), "width": str(_q(expected["width"]) / 2)})
        assert _grade(payload, expected)


def test_nearest_integer_matches_high_precision_value():
    generator = _load("src_12316", "generate.py")
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        givens, expected = payload["math_core"]["givens"], payload["correct_answer"]
        a = sp.expand((sp.sqrt(_q(givens["rhs"])) - givens["sign"] * sp.sqrt(_q(givens["known"]))) ** 2)
        assert int(expected) == int(sp.floor(sp.N(a, 60) + sp.Rational(1, 2)))
        assert _grade(payload, expected) and not _grade(payload, str(int(expected) + 1))


def test_domain_dispatch_refuses_non_denestable_roots():
    with pytest.raises(Exception):
        dispatch_registered_operation(DOMAIN_KEY, DENEST, seed=0, constraints={"roots": [{"rational": 5, "radical": [2, 3]}]})
