from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

from core.gencode.constraint_evaluator import evaluate_hard_constraints
from core.gencode.problem_type_canonicalizer import evaluate_typed_prefix_readiness
from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.slot_generators import SLOT_REGISTRY, generate_from_problem_type_spec
from core.gencode.validators import validate_generator_payload


SKILL_ID = "vh_數學B4_HistogramsAndFrequencyPolygons"
PROBLEM_TYPE_ID = "frequency_distribution_chart_construction"


def _spec() -> dict:
    spec = load_problem_type_spec(SKILL_ID, PROBLEM_TYPE_ID, prefer="curated")
    assert spec is not None
    return spec


def _component():
    path = Path("agent_skills_v3") / SKILL_ID / "components" / "src_3826" / "generate.py"
    module_spec = importlib.util.spec_from_file_location("src_3826_generate", path)
    assert module_spec is not None and module_spec.loader is not None
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def _core(payload: dict) -> tuple:
    givens = payload["metadata"]["givens"]
    return (
        givens["categories"],
        givens["frequencies"],
        givens["total_frequency"],
        payload["expected_drawing_spec"]["expected_values"],
    )


def test_registered_slot_signature_and_seed_zero_compiled_path():
    slot = SLOT_REGISTRY[PROBLEM_TYPE_ID]
    assert list(inspect.signature(slot).parameters) == ["skill_id", "pt", "spec", "seed"]

    spec = _spec()
    direct = slot(SKILL_ID, PROBLEM_TYPE_ID, spec, 0)
    compiled = generate_from_problem_type_spec(SKILL_ID, spec, seed=0)

    assert _core(direct) == _core(compiled)
    assert compiled["skill_id"] == SKILL_ID
    assert compiled["problem_type_id"] == PROBLEM_TYPE_ID
    assert compiled["answer_type"] == "drawing"
    assert compiled["answer_shape"] == "drawing"
    assert compiled["choices"] == []
    assert compiled["question"] == compiled["question_text"]
    assert compiled["correct_answer"]
    assert compiled["expected_drawing_spec"]
    assert compiled["answer_contract"]["expected_drawing_spec"]
    assert compiled["metadata"]["expected_drawing_spec"]
    assert isinstance(compiled["metadata"]["givens"], dict)
    assert compiled["metadata"]["givens"]["total_frequency"] >= 12
    assert validate_generator_payload(compiled, problem_type_spec=spec) == []

    ok, failures = evaluate_hard_constraints(
        spec["hard_constraints"],
        compiled["metadata"]["givens"],
    )
    assert ok is True
    assert failures == []


def test_seed_zero_matches_src_3826_and_is_reproducible():
    spec = _spec()
    first = generate_from_problem_type_spec(SKILL_ID, spec, seed=0)
    second = generate_from_problem_type_spec(SKILL_ID, spec, seed=0)
    component = _component().generate(seed=0)

    assert _core(first) == _core(second)
    assert _core(first) == _core(component)
    assert first["correct_answer"] == component["correct_answer"]
    assert first["answer_contract"] == component["answer_contract"]


def test_twenty_fixed_seeds_use_compiled_slot_successfully():
    spec = _spec()
    for seed in range(20):
        payload = generate_from_problem_type_spec(SKILL_ID, spec, seed=seed)
        assert payload["answer_type"] == "drawing"
        assert payload["metadata"]["givens"]["total_frequency"] >= 12
        assert validate_generator_payload(payload, problem_type_spec=spec) == []


def test_slot_registration_makes_readiness_naturally_runtime_ready():
    spec = _spec()
    readiness, usable, blockers = evaluate_typed_prefix_readiness(spec)
    assert readiness == "runtime_ready"
    assert usable is True
    assert blockers == []
