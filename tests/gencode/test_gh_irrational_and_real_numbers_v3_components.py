from __future__ import annotations

import ast
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

import pytest

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.domain.promoted.number_system_real_numbers import real_numbers_domain as domain
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
SKILL_ID = "gh_IrrationalAndRealNumbers"
DOMAIN_KEY = "number_system.real_numbers"
COMPONENTS_DIR = PROJECT_ROOT / "agent_skills_v3" / SKILL_ID / "components"
DRYRUN_COMPONENTS_DIR = PROJECT_ROOT / "reports" / "gencode_v3_dryrun" / SKILL_ID / "components"
PUBLISHED_COMPONENT_IDS = ["src_12283", "src_12284", "src_12285"]
IDENTITY_COMPONENT_IDS = ["src_12283", "src_12284"]
APPROXIMATION_COMPONENT_IDS = ["src_12285"]
STORE_PATH = PROJECT_ROOT / "configs" / "gencode_promoted_capabilities.json"
SEEDS = range(20)

# Textbook 例題3 (12283) and 隨堂練習5 (12284).
SOURCE_IDENTITIES = {
    "src_12283": (
        {"radicand": 2, "coefficients": {"a": {"rational": 3, "radical": 5}, "b": {"rational": 2, "radical": -1}},
         "rhs": {"rational": -1, "radical": 7}},
        {"a": "1", "b": "-2"},
    ),
    "src_12284": (
        {"radicand": 2, "coefficients": {"a": {"rational": 3, "radical": 2}, "b": {"rational": 2, "radical": -1}},
         "rhs": {"rational": 0, "radical": 7}},
        {"a": "2", "b": "-3"},
    ),
}


def _load(component_id: str, filename: str):
    path = COMPONENTS_DIR / component_id / filename
    spec = importlib.util.spec_from_file_location(f"gh_irrational_{component_id}_{path.stem}", path)
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


def _assert_contract(payload, component_id):
    assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"
    assert validate_answer_contract_consistency(payload) == []
    integrity = validate_component_payload(payload, component_id=component_id)
    assert integrity["passed"], integrity["blockers"]


def _exact(value):
    if isinstance(value, dict):
        return {key: _exact(item) for key, item in value.items()}
    return Fraction(str(value))


def _embedded_variants(component_id):
    tree = ast.parse((COMPONENTS_DIR / component_id / "generate.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "_materialize_generation_constraints":
            return ast.literal_eval(node.args[0].args[0])["generation_constraints"]["variants"]
    raise AssertionError("generation constraints literal missing")


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


@pytest.mark.parametrize(("component_id", "allowed_keys"), [
    *[(cid, {"radicand", "coefficients", "rhs"}) for cid in IDENTITY_COMPONENT_IDS],
    *[(cid, {"radicand", "places", "mode"}) for cid in APPROXIMATION_COMPONENT_IDS],
])
def test_generation_constraint_variants_are_inputs_only_and_seed_stable(component_id, allowed_keys):
    variants = _embedded_variants(component_id)
    assert len(variants) == 20
    assert all(set(variant) == allowed_keys for variant in variants)
    generator = _load(component_id, "generate.py")
    for seed in SEEDS:
        givens = generator.generate(seed=seed)["math_core"]["givens"]
        assert givens == generator.generate(seed=seed + len(variants))["math_core"]["givens"]


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
        "domain_operation_workspaces", "revision_0", "temp.", "skills.", "Fraction", "isqrt", "math.sqrt",
        "approximation", "'values'", "check_answer",
    ):
        assert forbidden not in source


@pytest.mark.parametrize(("component_id", "operation", "answer_type", "presentation_mode", "checker"), [
    *[(cid, "solve_rational_unknowns_from_radical_identity", "multi_part", "multiple_inputs", "multi_part_answer_checker")
      for cid in IDENTITY_COMPONENT_IDS],
    ("src_12285", "approximate_square_root_by_decimal_search", "rational", "short_answer", "rational_checker"),
])
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


# --- src_12283 / src_12284 solve_rational_unknowns_from_radical_identity ------

@pytest.mark.parametrize("component_id", IDENTITY_COMPONENT_IDS)
def test_identity_seed_zero_is_textbook_source(component_id):
    source_givens, source_values = SOURCE_IDENTITIES[component_id]
    payload = _load(component_id, "generate.py").generate(seed=0)
    assert _exact(payload["math_core"]["givens"]) == _exact(source_givens)
    assert payload["correct_answer"] == source_values
    assert "是有理數" in payload["question_text"]


@pytest.mark.parametrize("component_id", IDENTITY_COMPONENT_IDS)
def test_identity_seeds_preserve_topology_and_match_domain(component_id):
    generator = _load(component_id, "generate.py")
    rhs_rational_zero = component_id == "src_12284"
    questions, answers = set(), set()
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        _assert_contract(payload, component_id)
        givens, expected = payload["math_core"]["givens"], payload["correct_answer"]
        exact = _exact(givens)
        a_coef, b_coef, rhs = exact["coefficients"]["a"], exact["coefficients"]["b"], exact["rhs"]
        assert exact["radicand"] == 2
        assert a_coef["rational"] > 0 and a_coef["radical"] > 0 and b_coef["rational"] > 0 and b_coef["radical"] < 0
        assert (rhs["rational"] == 0) is rhs_rational_zero and rhs["radical"] != 0
        assert expected == domain.solve_rational_unknowns_from_radical_identity(
            2, givens["coefficients"], givens["rhs"])["values"]
        a, b = Fraction(expected["a"]), Fraction(expected["b"])
        assert a_coef["rational"] * a + b_coef["rational"] * b == rhs["rational"]
        assert a_coef["radical"] * a + b_coef["radical"] * b == rhs["radical"]
        assert [part["checker"] for part in payload["answer_contract"]["parts"]] == ["rational_checker"] * 2
        questions.add(payload["question_text"])
        answers.add(json.dumps(expected, sort_keys=True))
    assert len(questions) == 20 and len(answers) >= 10


@pytest.mark.parametrize("component_id", IDENTITY_COMPONENT_IDS)
def test_identity_grading_accepts_equivalent_and_rejects_wrong(component_id):
    generator = _load(component_id, "generate.py")
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        expected = payload["correct_answer"]
        ea, eb = expected["a"], expected["b"]
        accepted = [
            {"a": ea, "b": eb},
            {"a": f"{2 * int(ea)}/2", "b": f"{3 * int(eb)}/3"},
            {"a": f" {ea}.0 ", "b": f"{eb}.0"},
        ]
        rejected = [
            {"a": str(int(ea) + 1), "b": eb},
            {"a": ea, "b": str(int(eb) - 1)},
            {"a": str(-int(ea)), "b": eb},
            {"a": f"{ea}\\sqrt{{2}}", "b": eb},
            {"a": ea, "b": ""},
            {"a": "abc", "b": eb},
        ]
        if ea != eb:
            rejected.append({"a": eb, "b": ea})
        for answer in accepted:
            assert _grade(payload, answer), answer
            assert check_multi_part_answer(answer, expected, payload=payload)["overall_correct"]
        for answer in rejected:
            assert not _grade(payload, answer), answer
            assert not check_multi_part_answer(answer, expected, payload=payload)["overall_correct"]


# --- src_12285 approximate_square_root_by_decimal_search ----------------------

def test_approximation_seed_zero_is_textbook_source():
    payload = _load("src_12285", "generate.py").generate(seed=0)
    assert payload["math_core"]["givens"] == {"radicand": 3, "places": 2, "mode": "truncate"}
    assert payload["correct_answer"] == "1.73"
    assert "十分逼近法" in payload["question_text"] and "無條件捨去到小數點後第二位" in payload["question_text"]
    assert [step["lower"] for step in payload["answer_contract"]["semantic_answer"]["steps"]] == ["1", "1.7", "1.73"]


def test_approximation_seeds_truncate_and_match_domain():
    generator = _load("src_12285", "generate.py")
    radicands, truncation_not_rounding = set(), 0
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        _assert_contract(payload, "src_12285")
        givens, expected = payload["math_core"]["givens"], payload["correct_answer"]
        n = givens["radicand"]
        assert givens["places"] == 2 and givens["mode"] == "truncate" and not domain.is_perfect_square(n)
        assert expected == domain.approximate_square_root_by_decimal_search(n, 2, "truncate")["approximation"]
        value = Fraction(expected)
        assert value * value <= n < (value + Fraction(1, 100)) ** 2
        assert len(expected.split(".")[1]) == 2
        truncation_not_rounding += f"{n ** 0.5:.2f}" != expected
        radicands.add(n)
    assert len(radicands) == 20 and truncation_not_rounding > 0


def test_approximation_grading_is_exact_decimal():
    generator = _load("src_12285", "generate.py")
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        expected, n = payload["correct_answer"], payload["math_core"]["givens"]["radicand"]
        value = Fraction(expected)
        assert _grade(payload, expected)
        assert _grade(payload, expected + "0")
        rejected = {
            f"{float(value + Fraction(1, 100)):.2f}",
            f"{float(value - Fraction(1, 100)):.2f}",
            f"{float(value) + 0.001:.3f}",
            f"\\sqrt{{{n}}}",
            expected.split(".")[0],
            "abc",
            "",
        }
        rounded = f"{n ** 0.5:.2f}"
        if rounded != expected:
            rejected.add(rounded)
        for answer in rejected:
            assert not _grade(payload, answer), answer


def test_domain_dispatch_refuses_perfect_square_and_dependent_identity():
    with pytest.raises(Exception):
        dispatch_registered_operation(
            DOMAIN_KEY, "approximate_square_root_by_decimal_search", seed=0, constraints={"radicand": 4, "places": 2},
        )
    with pytest.raises(Exception):
        dispatch_registered_operation(
            DOMAIN_KEY, "solve_rational_unknowns_from_radical_identity", seed=0,
            constraints={"radicand": 2, "coefficients": {"a": {"rational": 1, "radical": 1}, "b": {"rational": 2, "radical": 2}},
                         "rhs": {"rational": 3, "radical": 3}},
        )
