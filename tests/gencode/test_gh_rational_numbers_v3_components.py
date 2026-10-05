from __future__ import annotations

import ast
import importlib.util
import json
import re
from pathlib import Path

import pytest

from core.domain.promoted.number_system_rational_numbers import rational_numbers_domain as domain
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
SKILL_ID = "gh_RationalNumbers"
DOMAIN_KEY = "number_system.rational_numbers"
COMPONENTS_DIR = PROJECT_ROOT / "agent_skills_v3" / SKILL_ID / "components"
DRYRUN_COMPONENTS_DIR = PROJECT_ROOT / "reports" / "gencode_v3_dryrun" / SKILL_ID / "components"
PUBLISHED_COMPONENT_IDS = [
    "src_12273", "src_12274", "src_12275", "src_12276", "src_12278",
    "src_12279", "src_12280", "src_12281", "src_12282",
]
DECIMAL_COMPONENT_IDS = ["src_12273", "src_12275", "src_12281"]
SIMPLEST_FRACTION_COMPONENT_IDS = ["src_12274", "src_12276", "src_12282"]
BOUNDS_COMPONENT_IDS = ["src_12278"]
UNVERIFIED_COMPONENT_IDS = ["src_12277"]
STORE_PATH = PROJECT_ROOT / "configs" / "gencode_promoted_capabilities.json"
SEEDS = range(1, 21)

STATEMENT_ORDER = [
    "is_irrational",
    "equals",
    "no_rational_between",
    "all_irrational",
    "sqrt_difference_identity",
]
# Textbook 1習題 觀念澄清1 (12279), radicals written as square-root descriptors.
SOURCE_STATEMENTS = [
    {"predicate": "is_irrational", "value": {"kind": "finite_decimal", "value": "1.414"}},
    {
        "predicate": "equals",
        "left": {
            "kind": "sum",
            "terms": [
                {"kind": "repeating_decimal", "value": "0.(4)"},
                {"kind": "repeating_decimal", "value": "0.(6)"},
            ],
        },
        "right": {"kind": "rational", "value": "1"},
    },
    {"predicate": "no_rational_between", "lower": "21/13", "upper": "35/21"},
    {
        "predicate": "all_irrational",
        "values": [
            {"kind": "sqrt", "radicand": 5},
            {"kind": "sqrt", "radicand": 20},
            {"kind": "sqrt", "radicand": 45},
        ],
    },
    {"predicate": "sqrt_difference_identity", "left_radicand": 3, "right_radicand": 5},
]
# Textbook 1習題 基礎題1 (12280).
SOURCE_CANDIDATES = [
    {"kind": "rational", "value": "-4/9"},
    {"kind": "rational", "value": "0"},
    {"kind": "finite_decimal", "value": "3.14159"},
    {"kind": "sum", "terms": [{"kind": "rational", "value": "3"}, {"kind": "sqrt", "radicand": 2}]},
    {"kind": "sum", "terms": [{"kind": "rational", "value": "12/11"}, {"kind": "rational", "value": "11/12"}]},
]


def _load(component_id: str, filename: str):
    path = COMPONENTS_DIR / component_id / filename
    spec = importlib.util.spec_from_file_location(f"gh_rational_{component_id}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def src_12279():
    return _load("src_12279", "generate.py")


@pytest.fixture(scope="module")
def src_12280():
    return _load("src_12280", "generate.py")


def _grade(payload, user_answer):
    return check_answer(
        user_answer,
        payload["correct_answer"],
        payload=payload,
        answer_contract=payload["answer_contract"],
        skill_id=SKILL_ID,
    )


def _assert_contract(payload, component_id):
    assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"
    assert validate_answer_contract_consistency(payload) == []
    integrity = validate_component_payload(payload, component_id=component_id)
    assert integrity["passed"], integrity["blockers"]


# --- component contract ------------------------------------------------------

@pytest.mark.parametrize("component_id", PUBLISHED_COMPONENT_IDS)
def test_component_files_follow_v3_contract(component_id):
    directory = COMPONENTS_DIR / component_id
    assert {p.name for p in directory.iterdir() if p.is_file()} == {"generate.py", "metadata.py", "get_hint.py"}
    assert (directory / "get_hint.py").read_text(encoding="utf-8") == _build_get_hint_py()
    for filename in ("generate.py", "metadata.py", "get_hint.py"):
        assert (directory / filename).read_bytes() == (DRYRUN_COMPONENTS_DIR / component_id / filename).read_bytes()


def test_published_wrapper_routes_only_verified_components():
    manifest = json.loads((COMPONENTS_DIR.parent / "component_manifest.json").read_text(encoding="utf-8"))
    assert [row["component_id"] for row in manifest["components"]] == PUBLISHED_COMPONENT_IDS
    wrapper = (PROJECT_ROOT / "skills" / f"{SKILL_ID}.py").read_text(encoding="utf-8")
    assert f"GENERATOR_KEYS = {PUBLISHED_COMPONENT_IDS!r}" in wrapper
    assert "backup_GenByGemini" not in wrapper
    package_init = (COMPONENTS_DIR.parent / "__init__.py").read_text(encoding="utf-8")
    for component_id in UNVERIFIED_COMPONENT_IDS:
        assert component_id not in wrapper
        assert component_id not in package_init


def _embedded_constraints(component_id):
    tree = ast.parse((COMPONENTS_DIR / component_id / "generate.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "_materialize_generation_constraints":
            return ast.literal_eval(node.args[0].args[0])
    raise AssertionError("generation constraints literal missing")


@pytest.mark.parametrize(
    ("component_id", "given_key", "variant_count"),
    [
        ("src_12279", "statements", 5),
        ("src_12280", "candidates", 5),
        ("src_12273", "fractions", 20),
        ("src_12275", "fractions", 20),
        ("src_12281", "fractions", 20),
        ("src_12274", "decimals", 20),
        ("src_12276", "decimals", 20),
        ("src_12282", "decimals", 20),
        ("src_12278", "lower", 20),
    ],
)
def test_generation_constraint_variants_are_seed_stable_and_answer_free(component_id, given_key, variant_count):
    variants = _embedded_constraints(component_id)["generation_constraints"]["variants"]
    forbidden = {"answer", "correct_answer", "canonical_answer", "answer_contract", "checker", "checker_key"}
    assert len(variants) == variant_count
    assert all(not forbidden & set(variant.get("constraints", variant)) for variant in variants)
    generator = _load(component_id, "generate.py")
    for seed in SEEDS:
        givens = generator.generate(seed=seed)["math_core"]["givens"][given_key]
        assert givens == generator.generate(seed=seed + len(variants))["math_core"]["givens"][given_key]


@pytest.mark.parametrize("component_id", PUBLISHED_COMPONENT_IDS)
def test_generator_only_uses_production_dispatch(component_id):
    source = (COMPONENTS_DIR / component_id / "generate.py").read_text(encoding="utf-8")
    imported = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module)
    production_route = {
        "core.gencode.registered_operation_dispatch",
        "core.gencode.skill_fixed_domain_authority",
    }
    assert production_route <= imported <= production_route | {"__future__", "copy", "typing"}
    for forbidden in (
        "domain_operation_workspaces", "revision_0", "temp.", "skills.", "正確", "錯誤", "Fraction", "isqrt",
        "divmod", "overline", "decimal_expansion(",
    ):
        assert forbidden not in source
    if component_id in DECIMAL_COMPONENT_IDS:
        assert not re.search(r"\d\.\d*\(\d+\)", source)
    if component_id in SIMPLEST_FRACTION_COMPONENT_IDS:
        assert not re.search(r"\d+/\d+", source)
    if component_id in BOUNDS_COMPONENT_IDS:
        variants = _embedded_constraints(component_id)["generation_constraints"]["variants"]
        assert all(set(variant) == {"lower", "upper"} for variant in variants)


@pytest.mark.parametrize(
    ("component_id", "operation", "answer_type", "presentation_mode", "checker"),
    [
        ("src_12279", "evaluate_rationality_statements", "multi_part", "multiple_inputs", "multi_part_answer_checker"),
        ("src_12280", "identify_rational_numbers", "short_answer", "short_answer", "solution_set_checker"),
        *[
            (cid, "fraction_to_decimal_expansion", "multi_part", "multiple_inputs", "multi_part_answer_checker")
            for cid in DECIMAL_COMPONENT_IDS
        ],
        *[
            (cid, "decimal_to_simplest_fraction", "multi_part", "multiple_inputs", "multi_part_answer_checker")
            for cid in SIMPLEST_FRACTION_COMPONENT_IDS
        ],
        ("src_12278", "construct_rational_between_bounds", "short_answer", "short_answer", "rational_between_bounds_checker"),
    ],
)
def test_metadata_matches_payload_contract(component_id, operation, answer_type, presentation_mode, checker):
    metadata = _load(component_id, "metadata.py")
    payload = _load(component_id, "generate.py").generate(seed=3)
    assert metadata.TEXTBOOK_EXAMPLE_ID == int(component_id.removeprefix("src_"))
    assert metadata.SKILL_ID == SKILL_ID
    assert metadata.DOMAIN_OPERATION == payload["domain_operation"] == operation
    assert payload["answer_type"] == answer_type
    assert metadata.PRESENTATION_MODE == metadata.RESPONSE_MODE == payload["presentation_mode"] == presentation_mode
    assert metadata.ANSWER_VERIFICATION_TYPE["checker_key"] == payload["answer_contract"]["checker_key"] == checker
    assert metadata.ANSWER_VERIFICATION_TYPE["equivalence_type"] == payload["answer_contract"]["equivalence_type"]


@pytest.mark.parametrize(("component_id", "operation"), [
    ("src_12279", "evaluate_rationality_statements"),
    ("src_12280", "identify_rational_numbers"),
    *[(cid, "fraction_to_decimal_expansion") for cid in DECIMAL_COMPONENT_IDS],
    *[(cid, "decimal_to_simplest_fraction") for cid in SIMPLEST_FRACTION_COMPONENT_IDS],
    ("src_12278", "construct_rational_between_bounds"),
])
def test_routes_through_confirmed_binding_to_promoted_domain(component_id, operation):
    payload = _load(component_id, "generate.py").generate(seed=11)
    store = json.loads(STORE_PATH.read_text(encoding="utf-8"))
    resolution = payload["domain_resolution"]
    assert resolution["binding_status"] == "confirmed"
    assert resolution["resolution_source"] == "confirmed_binding"
    assert resolution["fixed_domain_key"] == payload["fixed_domain_key"] == DOMAIN_KEY
    assert resolution["selected_operation"] == operation
    assert resolution["registry_revision"] == store["domains"][DOMAIN_KEY]["registry_revision"]


@pytest.mark.parametrize("component_id", PUBLISHED_COMPONENT_IDS)
def test_formal_direct_smoke_and_integrity_validation(component_id):
    result = _execute_component_direct_smoke_and_validation(
        skill_id=SKILL_ID, component_id=component_id, dryrun_base_dir="agent_skills_v3", seed=42,
    )
    assert result["compile_passed"] and result["smoke_passed"] and result["validation_passed"], result


# --- src_12279 evaluate_rationality_statements --------------------------------

def test_12279_source_topology_and_oracle():
    _, payload = dispatch_registered_operation(
        DOMAIN_KEY, "evaluate_rationality_statements", seed=0, constraints={"statements": SOURCE_STATEMENTS},
    )
    # Textbook key: (1)× (2)× (3)× (4)○ (5)×
    assert payload["correct_answer"] == {
        "statement_1": "錯誤",
        "statement_2": "錯誤",
        "statement_3": "錯誤",
        "statement_4": "正確",
        "statement_5": "錯誤",
    }


def test_12279_generated_items_keep_textbook_order(src_12279):
    for seed in SEEDS:
        payload = src_12279.generate(seed=seed)
        statements = payload["math_core"]["givens"]["statements"]
        assert [s["predicate"] for s in statements] == STATEMENT_ORDER
        assert [p["key"] for p in payload["answer_contract"]["parts"]] == [f"statement_{i}" for i in range(1, 6)]


def test_12279_deterministic_seed_and_parameter_variation(src_12279):
    assert src_12279.generate(seed=5) == src_12279.generate(seed=5)
    payloads = [src_12279.generate(seed=seed) for seed in SEEDS]
    assert len({p["question_text"] for p in payloads}) == 5
    assert len({tuple(p["correct_answer"].values()) for p in payloads}) >= 3


@pytest.mark.parametrize("seed", list(SEEDS))
def test_12279_twenty_seeds(src_12279, seed):
    payload = src_12279.generate(seed=seed)
    assert payload["seed"] == seed
    _assert_contract(payload, "src_12279")
    expected = domain.evaluate_rationality_statements(payload["math_core"]["givens"]["statements"])
    assert payload["math_core"]["target"] == {"truth_values": expected}
    assert list(payload["correct_answer"].values()) == ["正確" if v else "錯誤" for v in expected]

    correct = dict(payload["correct_answer"])
    labels = {key: "A" if value == "正確" else "B" for key, value in correct.items()}
    assert _grade(payload, correct) is True
    assert _grade(payload, labels) is True
    for key in correct:
        wrong = dict(correct)
        wrong[key] = "錯誤" if wrong[key] == "正確" else "正確"
        assert _grade(payload, wrong) is False
    missing = dict(correct)
    missing.pop("statement_5")
    assert _grade(payload, missing) is False


# --- src_12280 identify_rational_numbers --------------------------------------

def _source_identify_payload(candidates=SOURCE_CANDIDATES):
    _, payload = dispatch_registered_operation(
        DOMAIN_KEY, "identify_rational_numbers", seed=0, constraints={"candidates": candidates},
    )
    return payload


def test_12280_source_oracle_and_solution_set_forms():
    payload = _source_identify_payload()
    assert payload["correct_answer"] == [1, 2, 3, 5]
    assert payload["answer_type"] == "short_answer"
    contract = payload["answer_contract"]
    assert contract["checker_key"] == "solution_set_checker"
    assert contract["equivalence_type"] == "unordered_solution_set"
    for accepted in ("(1)(2)(3)(5)", "1,2,3,5", "{1,2,3,5}", "5,3,2,1,1"):
        assert _grade(payload, accepted) is True, accepted
    for rejected in ("(1)(2)(3)", "1,2,3,4,5", "{1,2,3}", "4", "1,2,3,5,4"):
        assert _grade(payload, rejected) is False, rejected


def test_12280_candidate_variation_changes_canonical_set():
    rational_root = [dict(c) for c in SOURCE_CANDIDATES]
    rational_root[3] = {"kind": "sum", "terms": [{"kind": "rational", "value": "3"}, {"kind": "sqrt", "radicand": 4}]}
    irrational_second = [dict(c) for c in SOURCE_CANDIDATES]
    irrational_second[1] = {"kind": "sqrt", "radicand": 2}
    assert _source_identify_payload(rational_root)["correct_answer"] == [1, 2, 3, 4, 5]
    assert _source_identify_payload(irrational_second)["correct_answer"] == [1, 3, 5]


def test_12280_generated_candidates_keep_textbook_forms(src_12280):
    def form(candidate):
        if candidate["kind"] == "sum":
            return "sum:" + "+".join(term["kind"] for term in candidate["terms"])
        return candidate["kind"]

    expected = sorted(form(c) for c in SOURCE_CANDIDATES)
    for seed in SEEDS:
        candidates = src_12280.generate(seed=seed)["math_core"]["givens"]["candidates"]
        assert sorted(form(c) for c in candidates) == expected


def test_12280_deterministic_seed_and_candidate_variation(src_12280):
    assert src_12280.generate(seed=5) == src_12280.generate(seed=5)
    payloads = [src_12280.generate(seed=seed) for seed in SEEDS]
    assert len({p["question_text"] for p in payloads}) == 5
    assert len({tuple(p["correct_answer"]) for p in payloads}) >= 3


@pytest.mark.parametrize("seed", list(SEEDS))
def test_12280_twenty_seeds(src_12280, seed):
    payload = src_12280.generate(seed=seed)
    assert payload["seed"] == seed
    _assert_contract(payload, "src_12280")
    indices = domain.identify_rational_numbers(payload["math_core"]["givens"]["candidates"])
    assert payload["correct_answer"] == indices
    assert payload["math_core"]["target"] == {"indices": indices}

    assert _grade(payload, "".join(f"({i})" for i in indices)) is True
    assert _grade(payload, ",".join(str(i) for i in indices)) is True
    assert _grade(payload, "{" + ",".join(str(i) for i in reversed(indices)) + "}") is True
    assert _grade(payload, ",".join(str(i) for i in indices + indices[:1])) is True
    others = [i for i in range(1, 6) if i not in indices]
    assert _grade(payload, ",".join(str(i) for i in indices[:-1])) is False
    assert _grade(payload, ",".join(str(i) for i in indices + [6])) is False
    if others:
        assert _grade(payload, ",".join(str(i) for i in indices + others[:1])) is False
        assert _grade(payload, ",".join(str(i) for i in others)) is False


# --- src_12273 / src_12275 / src_12281 fraction_to_decimal_expansion ----------

# Textbook 例題1 (12273), 隨堂練習1 (12275), 1習題 基礎題2 (12281).
DECIMAL_SOURCES = {
    "src_12273": (["11/40", "2/11"], ["0.275", "0.(18)"], ["terminating", "repeating"]),
    "src_12275": (["5/8", "1/7"], ["0.625", "0.(142857)"], ["terminating", "repeating"]),
    "src_12281": (["1/37", "9/22"], ["0.(027)", "0.4(09)"], ["pure_repeating", "mixed_repeating"]),
}


def _decimal_kind(fraction):
    part = domain.fraction_to_decimal_expansion(fraction)
    if part["kind"] == "terminating":
        return "terminating"
    return "mixed_repeating" if part["nonrepeating"] else "pure_repeating"


def _overline(decimal):
    return re.sub(r"\((\d+)\)$", r"\\overline{\1}", decimal)


def _rotate_cycle(decimal):
    match = re.fullmatch(r"(.*)\((\d+)\)", decimal)
    head, cycle = match.groups()
    bad = cycle[1:] + cycle[0] if len(set(cycle)) > 1 else str(int(cycle[0]) % 8 + 1) * len(cycle)
    return f"{head}({bad})"


@pytest.mark.parametrize("component_id", DECIMAL_COMPONENT_IDS)
def test_decimal_component_source_oracle(component_id):
    fractions, decimals, _ = DECIMAL_SOURCES[component_id]
    payload = _load(component_id, "generate.py").generate(seed=0)
    assert payload["math_core"]["givens"]["fractions"] == fractions
    assert list(payload["correct_answer"].values()) == decimals
    assert _grade(payload, dict(payload["correct_answer"])) is True
    assert _grade(payload, {k: _overline(v) for k, v in payload["correct_answer"].items()}) is True
    assert _grade(payload, dict(zip(payload["correct_answer"], fractions))) is False


@pytest.mark.parametrize("component_id", DECIMAL_COMPONENT_IDS)
def test_decimal_component_keeps_source_topology_and_varies(component_id):
    _, _, topology = DECIMAL_SOURCES[component_id]
    generator = _load(component_id, "generate.py")
    payloads = [generator.generate(seed=seed) for seed in range(20)]
    assert len({p["question_text"] for p in payloads}) == 20
    assert generator.generate(seed=4) == generator.generate(seed=4)
    kinds = set()
    for payload in payloads:
        part_kinds = [_decimal_kind(f) for f in payload["math_core"]["givens"]["fractions"]]
        for kind, wanted in zip(part_kinds, topology):
            assert kind == wanted or (wanted == "repeating" and kind.endswith("_repeating"))
        kinds.update(part_kinds)
    assert len(kinds) >= 2


@pytest.mark.parametrize("component_id", DECIMAL_COMPONENT_IDS)
@pytest.mark.parametrize("seed", range(20))
def test_decimal_component_twenty_seeds(component_id, seed):
    payload = _load(component_id, "generate.py").generate(seed=seed)
    _assert_contract(payload, component_id)
    fractions = payload["math_core"]["givens"]["fractions"]
    expected = [domain.fraction_to_decimal_expansion(f)["decimal"] for f in fractions]
    assert list(payload["correct_answer"].values()) == expected
    assert [p["checker"] for p in payload["answer_contract"]["parts"]] == ["repeating_decimal_checker"] * len(fractions)

    correct = dict(payload["correct_answer"])
    assert _grade(payload, correct) is True
    assert _grade(payload, {k: _overline(v) for k, v in correct.items()}) is True
    assert _grade(payload, dict(zip(correct, fractions))) is False
    for key, value in correct.items():
        if "(" in value:
            assert _grade(payload, dict(correct, **{key: _rotate_cycle(value)})) is False
            assert _grade(payload, dict(correct, **{key: value.replace("(", "").replace(")", "")})) is False


# --- src_12274 / src_12276 / src_12282 decimal_to_simplest_fraction -----------

# Textbook 例題2 (12274), 隨堂練習2 (12276), 1習題 基礎題3 (12282).
SIMPLEST_FRACTION_SOURCES = {
    "src_12274": (["0.28", "0.(32)", "1.4(5)"], ["7/25", "32/99", "131/90"]),
    "src_12276": (["0.732", "5.(12)", "0.1(58)"], ["183/250", "169/33", "157/990"]),
    "src_12282": (["0.(27)", "5.4(38)"], ["3/11", "2692/495"]),
}


def _decimal_shape(decimal):
    whole, nonrepeating, cycle = re.fullmatch(r"(\d+)\.(\d*)(?:\((\d+)\))?", decimal).groups()
    return whole == "0", len(nonrepeating), len(cycle or "")


def _scaled(fraction, factor):
    numerator, denominator = (int(x) for x in fraction.split("/"))
    return f"{numerator * factor}/{denominator * factor}"


def _latex(fraction):
    numerator, denominator = fraction.split("/")
    return rf"\frac{{{numerator}}}{{{denominator}}}"


@pytest.mark.parametrize("component_id", SIMPLEST_FRACTION_COMPONENT_IDS)
def test_simplest_fraction_component_source_oracle(component_id):
    decimals, fractions = SIMPLEST_FRACTION_SOURCES[component_id]
    payload = _load(component_id, "generate.py").generate(seed=0)
    assert payload["math_core"]["givens"]["decimals"] == decimals
    assert list(payload["correct_answer"].values()) == fractions
    assert "最簡分數" in payload["question_text"]
    assert _grade(payload, dict(payload["correct_answer"])) is True
    assert _grade(payload, {k: _latex(v) for k, v in payload["correct_answer"].items()}) is True
    assert _grade(payload, dict(zip(payload["correct_answer"], decimals))) is False


@pytest.mark.parametrize("component_id", SIMPLEST_FRACTION_COMPONENT_IDS)
def test_simplest_fraction_component_keeps_source_shape_and_varies(component_id):
    decimals, _ = SIMPLEST_FRACTION_SOURCES[component_id]
    generator = _load(component_id, "generate.py")
    payloads = [generator.generate(seed=seed) for seed in range(20)]
    assert len({p["question_text"] for p in payloads}) == 20
    assert generator.generate(seed=4) == generator.generate(seed=4)
    for payload in payloads:
        assert [_decimal_shape(d) for d in payload["math_core"]["givens"]["decimals"]] == [_decimal_shape(d) for d in decimals]
        assert len(payload["answer_contract"]["parts"]) == len(decimals)


@pytest.mark.parametrize("component_id", SIMPLEST_FRACTION_COMPONENT_IDS)
@pytest.mark.parametrize("seed", range(20))
def test_simplest_fraction_component_twenty_seeds(component_id, seed):
    payload = _load(component_id, "generate.py").generate(seed=seed)
    _assert_contract(payload, component_id)
    decimals = payload["math_core"]["givens"]["decimals"]
    expected = [domain.decimal_to_simplest_fraction(d)["fraction"] for d in decimals]
    assert list(payload["correct_answer"].values()) == expected
    assert [p["checker"] for p in payload["answer_contract"]["parts"]] == ["simplest_fraction_checker"] * len(decimals)

    correct = dict(payload["correct_answer"])
    assert _grade(payload, correct) is True
    assert _grade(payload, {k: _latex(v) for k, v in correct.items()}) is True
    assert _grade(payload, dict(zip(correct, decimals))) is False
    for key, value in correct.items():
        numerator, denominator = value.split("/")
        assert _grade(payload, dict(correct, **{key: _scaled(value, 2)})) is False
        assert _grade(payload, dict(correct, **{key: f"{int(numerator) + 1}/{denominator}"})) is False
        assert _grade(payload, dict(correct, **{key: f"-{numerator}/-{denominator}"})) is False


# --- src_12278 construct_rational_between_bounds -------------------------------

# Textbook 隨堂練習 (12278): 試找出一個介於 3/2 和 5/3 之間的有理數。
def test_12278_source_predicate_accepts_any_rational_strictly_between():
    payload = _load("src_12278", "generate.py").generate(seed=0)
    givens = payload["math_core"]["givens"]
    assert (givens["lower"], givens["upper"]) == ("3/2", "5/3")
    assert "找出一個介於" in payload["question_text"]
    contract = payload["answer_contract"]
    assert (contract["checker_key"], contract["equivalence_type"], contract["relation"]) == (
        "rational_between_bounds_checker", "strict_between_bounds", "strict_between",
    )
    for accepted in ("19/12", "8/5", "1.6", r"\frac{8}{5}", "16/10", "1.65"):
        assert _grade(payload, accepted) is True, accepted
    for rejected in ("3/2", "5/3", "1.5", "2", "1.7", "1", "abc", ""):
        assert _grade(payload, rejected) is False, rejected


@pytest.mark.parametrize("seed", range(20))
def test_12278_twenty_seeds(seed):
    from fractions import Fraction

    payload = _load("src_12278", "generate.py").generate(seed=seed)
    _assert_contract(payload, "src_12278")
    givens = payload["math_core"]["givens"]
    lower, upper = Fraction(givens["lower"]), Fraction(givens["upper"])
    assert lower < upper
    example = domain.construct_rational_between_bounds(givens["lower"], givens["upper"])["example"]
    assert payload["correct_answer"] == example
    assert lower < Fraction(example) < upper
    assert (payload["answer_contract"]["lower"], payload["answer_contract"]["upper"]) == (givens["lower"], givens["upper"])

    mediant = Fraction(lower.numerator + upper.numerator, lower.denominator + upper.denominator)
    third = lower + (upper - lower) / 3
    assert _grade(payload, example) is True
    assert _grade(payload, f"{mediant.numerator}/{mediant.denominator}") is True
    assert _grade(payload, f"{2 * third.numerator}/{2 * third.denominator}") is True
    assert _grade(payload, givens["lower"]) is False
    assert _grade(payload, givens["upper"]) is False
    below, above = lower - Fraction(1, 100), upper + Fraction(1, 100)
    assert _grade(payload, f"{below.numerator}/{below.denominator}") is False
    assert _grade(payload, f"{above.numerator}/{above.denominator}") is False


def test_12278_generated_bounds_vary_deterministically():
    generator = _load("src_12278", "generate.py")
    payloads = [generator.generate(seed=seed) for seed in range(20)]
    assert len({p["question_text"] for p in payloads}) == 20
    assert generator.generate(seed=7) == generator.generate(seed=7)
