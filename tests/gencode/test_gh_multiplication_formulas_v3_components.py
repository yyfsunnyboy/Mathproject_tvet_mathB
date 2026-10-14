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
SKILL_ID = "gh_MultiplicationFormulas"
DOMAIN_KEY = "algebra.multiplication_formulas"
COMPONENTS_DIR = PROJECT_ROOT / "agent_skills_v3" / SKILL_ID / "components"
DRYRUN_COMPONENTS_DIR = PROJECT_ROOT / "reports" / "gencode_v3_dryrun" / SKILL_ID / "components"
STORE_PATH = PROJECT_ROOT / "configs" / "gencode_promoted_capabilities.json"
SEEDS = range(20)

EXPAND = "expand_polynomial_expressions"
FACTOR = "factor_by_cube_formulas"
RECIPROCAL = "evaluate_reciprocal_power_expressions"
RADICAL = "simplify_radical_expressions"
SQUARED = "solve_rational_unknowns_from_squared_radical_identity"
POWER = "evaluate_product_under_power_relation"

# seed 0 = textbook item; answers worked out from the textbook expressions
TEXTBOOK = {
    "src_12286": (EXPAND, {"part_1": "5a^2+5b^2", "part_2": "a^2-2ab+b^2-1", "part_3": "a^2-4ab+6ac+4b^2-12bc+9c^2"}),
    "src_12287": (EXPAND, {"part_1": "a^3+6a^2b+12ab^2+8b^3", "part_2": "8a^3-36a^2b+54ab^2-27b^3"}),
    "src_12288": (EXPAND, {"part_1": "a^3+8b^3", "part_2": "8a^3-b^3"}),
    "src_12289": (FACTOR, {"part_1": "(x+1)(x^2-x+1)", "part_2": "(3x-1)(9x^2+3x+1)", "part_3": "(x+3)^3"}),
    "src_12290": (RECIPROCAL, {"part_1": "7", "part_2": "18"}),
    "src_12291": (RADICAL, {"part_1": "7sqrt(3)", "part_2": "5", "part_3": "sqrt(6)/2"}),
    "src_12292": (EXPAND, {"part_1": "2a^2+2", "part_2": "a^2-b^2-2bc-c^2", "part_3": "a^2-2ab+4a+b^2-4b+4"}),
    "src_12293": (EXPAND, {"part_1": "27a^3+54a^2b+36ab^2+8b^3", "part_2": "8a^3-12a^2+6a-1"}),
    "src_12294": (EXPAND, {"part_1": "a^3-27b^3", "part_2": "a^3+1"}),
    "src_12295": (FACTOR, {"part_1": "(2x+1)(4x^2-2x+1)", "part_2": "(x-5)(x^2+5x+25)", "part_3": "(x-2)^3"}),
    "src_12296": (RECIPROCAL, {"part_1": "6", "part_2": "-14"}),
    "src_12297": (SQUARED, {"a": "1", "b": "13"}),
    "src_12298": (EXPAND, {"part_1": "a^2+4ab+6a+4b^2+12b+9", "part_2": "27a^3-54a^2b+36ab^2-8b^3", "part_3": "a^3/8-b^3/27"}),
    "src_12299": (FACTOR, {"part_1": "(3x-y)(9x^2+3xy+y^2)", "part_2": "(x+2y)(x^2-2xy+4y^2)", "part_3": "(x+1)^3"}),
    "src_12300": (RECIPROCAL, {"part_1": "4", "part_2": "14", "part_3": "52"}),
    "src_12301": (POWER, "3"),
}
PUBLISHED_COMPONENT_IDS = sorted(TEXTBOOK)
REQUIRED_FORM = {EXPAND: "expanded", FACTOR: "fully_factorized", RADICAL: "simplest_radical"}


def _ids(*operations):
    return [cid for cid, (op, _) in TEXTBOOK.items() if op in operations]


def _load(component_id: str, filename: str):
    path = COMPONENTS_DIR / component_id / filename
    spec = importlib.util.spec_from_file_location(f"gh_multiplication_{component_id}_{path.stem}", path)
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


def _poly(terms):
    return sp.Add(*[sp.Rational(c) * sp.Mul(*[sp.Symbol(v) ** int(e) for v, e in mono.items()]) for c, mono in terms])


def _expression(expression):
    return sp.Add(*[sp.Rational(p.get("coefficient", "1")) * sp.Mul(*[_poly(f) ** int(n) for f, n in p["factors"]])
                    for p in expression])


def _expression_text(expression):
    return " + ".join(f"({p.get('coefficient', '1')})*" + "*".join(f"({_poly(f)})**{n}" for f, n in p["factors"])
                      for p in expression)


def _radical(expression):
    return sp.Add(*[sp.Rational(p.get("coefficient", "1")) * sp.Mul(*[
        sp.Add(*[sp.Rational(c) * sp.sqrt(sp.Rational(r)) for c, r in f]) for f in p["factors"]]) for p in expression])


def _radical_text(expression):
    return " + ".join(f"({p.get('coefficient', '1')})*" + "*".join(
        "(" + "+".join(f"({c})*sqrt({r})" for c, r in f) + ")" for f in p["factors"]) for p in expression)


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
    for forbidden in ("domain_operation_workspaces", "revision_0", "temp.", "skills.", "Fraction", "sympy", "isqrt",
                      "math.sqrt", "expand(", "factor(", "check_answer"):
        assert forbidden not in source


@pytest.mark.parametrize("component_id", PUBLISHED_COMPONENT_IDS)
def test_metadata_matches_payload_contract(component_id):
    operation = TEXTBOOK[component_id][0]
    metadata = _load(component_id, "metadata.py")
    payload = _load(component_id, "generate.py").generate(seed=3)
    assert metadata.TEXTBOOK_EXAMPLE_ID == int(component_id.removeprefix("src_"))
    assert metadata.SKILL_ID == SKILL_ID
    assert metadata.DOMAIN_OPERATION == payload["domain_operation"] == operation
    expected_mode, checker = (("short_answer", "rational_checker") if operation == POWER
                              else ("multiple_inputs", "multi_part_answer_checker"))
    assert metadata.PRESENTATION_MODE == metadata.RESPONSE_MODE == payload["presentation_mode"] == expected_mode
    assert metadata.ANSWER_VERIFICATION_TYPE["checker_key"] == payload["answer_contract"]["checker_key"] == checker
    assert metadata.ANSWER_VERIFICATION_TYPE["equivalence_type"] == payload["answer_contract"]["equivalence_type"]


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
    operation, source_answer = TEXTBOOK[component_id]
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
        if operation == POWER:
            continue
        assert list(payload["correct_answer"]) == list(source_answer)
        assert [p["key"] for p in contract["parts"]] == list(source_answer)
        if operation in REQUIRED_FORM:
            assert {(p["checker"], p.get("required_form")) for p in contract["parts"]} == {
                ("expression_checker", REQUIRED_FORM[operation])}
    assert len(questions) == 20


# --- independent sympy oracle + grading ------------------------------------------

@pytest.mark.parametrize("component_id", _ids(EXPAND))
def test_expansion_matches_sympy_and_requires_expanded_form(component_id):
    generator = _load(component_id, "generate.py")
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        expected = payload["correct_answer"]
        reordered, unexpanded = {}, {}
        for i, expression in enumerate(payload["math_core"]["givens"]["expressions"], start=1):
            key = f"part_{i}"
            truth = sp.expand(_expression(expression))
            assert sp.expand(_parse_sympy(expected[key]) - truth) == 0
            reordered[key] = " + ".join(str(t) for t in reversed(sp.Add.make_args(truth)))
            unexpanded[key] = _expression_text(expression)
        assert _grade(payload, expected) and _grade(payload, reordered)
        assert check_multi_part_answer(reordered, expected, payload=payload)["overall_correct"]
        assert not _grade(payload, {**expected, "part_1": unexpanded["part_1"]})
        assert not _grade(payload, {**expected, "part_1": f"{expected['part_1']}+1"})


@pytest.mark.parametrize("component_id", _ids(FACTOR))
def test_cube_factoring_matches_sympy_and_requires_full_factorization(component_id):
    generator = _load(component_id, "generate.py")
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        expected = payload["correct_answer"]
        reordered = {}
        for i, terms in enumerate(payload["math_core"]["givens"]["polynomials"], start=1):
            key = f"part_{i}"
            truth = _poly(terms)
            answer = _parse_sympy(expected[key])
            assert sp.expand(answer - truth) == 0
            assert sorted((str(sp.expand(b)), e) for b, e in sp.factor_list(truth)[1]) == sorted(
                (str(sp.expand(f.base if f.is_Pow else f)), int(f.exp) if f.is_Pow else 1)
                for f in sp.Mul.make_args(answer) if not f.is_number)
            factors = sp.Mul.make_args(answer)
            reordered[key] = ("*".join(f"({f})" for f in reversed(factors)) if len(factors) > 1
                              else "*".join([f"({factors[0].base})"] * int(factors[0].exp)))
            assert not _grade(payload, {**expected, key: str(truth)})
        assert _grade(payload, expected) and _grade(payload, reordered)


@pytest.mark.parametrize("component_id", _ids(RECIPROCAL))
def test_reciprocal_power_values_match_sympy(component_id):
    generator = _load(component_id, "generate.py")
    x = sp.Symbol("x")
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        givens, expected = payload["math_core"]["givens"], payload["correct_answer"]
        base = givens["base"]
        if base["kind"] == "relation":
            value = sp.solve(sp.Eq(x + int(base["sign"]) / x, sp.Rational(base["value"])), x)[0]
        else:
            value = sp.Rational(base["rational"]) + sp.Rational(base["radical"]) * sp.sqrt(base["radicand"])
        for i, target in enumerate(givens["targets"], start=1):
            truth = sp.radsimp(sp.expand(value ** target["power"] + target["sign"] * value ** (-target["power"])))
            assert sp.simplify(truth - _parse_sympy(expected[f"part_{i}"])) == 0
        assert _grade(payload, expected)
        assert _grade(payload, {k: f"{v}.0" for k, v in expected.items()})
        assert not _grade(payload, {**expected, "part_1": str(sp.Rational(expected["part_1"]) + 2)})


def test_radical_simplification_matches_sympy_and_requires_simplest_form():
    generator = _load("src_12291", "generate.py")
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        expected = payload["correct_answer"]
        latex = {}
        for i, expression in enumerate(payload["math_core"]["givens"]["expressions"], start=1):
            key = f"part_{i}"
            answer = _parse_sympy(expected[key])
            assert sp.simplify(_radical(expression) - answer) == 0
            latex[key] = sp.latex(sp.radsimp(answer))
            assert not _grade(payload, {**expected, key: _radical_text(expression)})
        assert _grade(payload, expected) and _grade(payload, latex)


def test_squared_radical_identity_matches_sympy():
    generator = _load("src_12297", "generate.py")
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        givens, expected = payload["math_core"]["givens"], payload["correct_answer"]
        q, m, r = sp.Rational(givens["coefficient"]), int(givens["radicand"]), sp.Rational(givens["rhs_radical"])
        a, b = sp.Rational(expected["a"]), sp.Rational(expected["b"])
        assert sp.expand((a + q * sp.sqrt(m)) ** 2 - (b + r * sp.sqrt(m))) == 0
        assert _grade(payload, expected) and _grade(payload, {"a": f"{float(a)}", "b": f"{float(b)}"})
        assert not _grade(payload, {"a": expected["a"], "b": str(b + 1)})
        if a != b:
            assert not _grade(payload, {"a": expected["b"], "b": expected["a"]})


def test_power_relation_matches_polynomial_remainder():
    generator = _load("src_12301", "generate.py")
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        givens, expected = payload["math_core"]["givens"], payload["correct_answer"]
        var = sp.Symbol(givens["variable"])
        expression = sp.expand(_expression(givens["expression"]))
        remainder = sp.rem(sp.Poly(expression, var), sp.Poly(var ** int(givens["power"]) - sp.Rational(givens["value"]), var))
        assert remainder.as_expr() == sp.Rational(expected)
        assert _grade(payload, expected) and _grade(payload, f"{expected}.0")
        assert not _grade(payload, str(sp.Rational(expected) + 1))
        assert not _grade(payload, str(expression).replace("**", "^"))


def test_domain_dispatch_refuses_non_cube_polynomials():
    with pytest.raises(Exception):
        dispatch_registered_operation(
            DOMAIN_KEY, FACTOR, seed=0, constraints={"polynomials": [[["1", {"x": 3}], ["2", {}]]]},
        )
