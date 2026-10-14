# -*- coding: utf-8 -*-
"""Phase-2 verification for all 31 Math B2 section 1-2 components."""

from __future__ import annotations

import importlib.util
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

from core.gencode.b2_12_capability_adapter import B2_12_EXAMPLE_OPERATION_MAP
from core.gencode.b2_12_component_specs import COMPONENT_SPECS
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.services.v3_question_integrity_validator import validate_component_payload
from core.question_image_assets import production_question_asset_relpath


ROOT = Path(__file__).resolve().parents[2]
V3_ROOT = ROOT / "agent_skills_v3"


def _component_dir(example_id: int) -> Path:
    spec = COMPONENT_SPECS[example_id]
    return V3_ROOT / str(spec["skill_id"]) / "components" / f"src_{example_id}"


def _load_generator(example_id: int) -> Any:
    path = _component_dir(example_id) / "generate.py"
    module_spec = importlib.util.spec_from_file_location(f"b2_12_component_{example_id}", path)
    assert module_spec is not None and module_spec.loader is not None
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def _wrong_answer(payload: dict[str, Any]) -> Any:
    correct = payload["correct_answer"]
    if isinstance(correct, dict):
        wrong = dict(correct)
        wrong[next(iter(wrong))] = "__wrong__"
        return wrong
    if payload["answer_type"] == "single_choice":
        return next(choice["text"] for choice in payload["choices"] if choice["text"] != correct)
    return f"({correct})+1"


def _equivalent_scalar(value: Any, part: dict[str, Any]) -> Any:
    text = str(value)
    checker = str(part.get("checker") or part.get("checker_key") or "")
    if checker in {"text_checker", "text_short_checker"}:
        return text
    if checker == "decimal_tolerance_checker":
        return f"+{text}"
    if checker in {"numeric_checker", "integer_checker", "rational_checker", "fraction_checker"}:
        value_fraction = Fraction(text)
        return f"{value_fraction.numerator * 2}/{value_fraction.denominator * 2}"
    if checker == "solution_set_checker":
        values = [token.strip() for token in text.strip("{}").split(",")]
        return "{" + ",".join(reversed(values)) + "}"
    if part.get("required_form") == "simplified_trig":
        return text
    if part.get("required_form") == "pi_expression" and "pi" in text:
        return f"2*({text})/2"
    return f"2*({text})/2"


def _equivalent_answer(payload: dict[str, Any]) -> Any:
    correct = payload["correct_answer"]
    contract = payload["answer_contract"]
    if payload["answer_type"] == "single_choice":
        return next(choice["label"] for choice in payload["choices"] if choice["text"] == correct)
    if isinstance(correct, dict):
        parts = {str(part["key"]): part for part in contract["parts"]}
        return {key: _equivalent_scalar(value, parts[key]) for key, value in correct.items()}
    return f"2*({correct})/2"


def test_b2_12_has_exactly_one_physical_component_per_example() -> None:
    assert set(COMPONENT_SPECS) == set(B2_12_EXAMPLE_OPERATION_MAP) == set(range(11556, 11587))
    for example_id in COMPONENT_SPECS:
        directory = _component_dir(example_id)
        assert directory.is_dir()
        assert {path.name for path in directory.iterdir() if path.is_file()} == {
            "generate.py", "metadata.py", "get_hint.py"
        }


def test_b2_12_fixed_skill_and_answer_type_counts() -> None:
    skill_counts = Counter(str(spec["skill_id"]) for spec in COMPONENT_SPECS.values())
    assert skill_counts == {
        "vh_數學B2_RatioAndRatioValue": 2,
        "vh_數學B2_TrigonometricFunctionsOfAcuteAngles": 11,
        "vh_數學B2_TrigonometricValuesOfSpecialAngles": 6,
        "vh_數學B2_CalculatingFunctionValuesUsingCalculator": 2,
        "vh_數學B2_FundamentalTrigonometricIdentities": 10,
    }
    assert Counter(str(spec["answer_type"]) for spec in COMPONENT_SPECS.values()) == {
        "short_answer": 4, "single_choice": 1, "multi_part": 26
    }
    assert Counter(str(spec["oracle_source"]) for spec in COMPONENT_SPECS.values()) == {
        "source_provided": 10, "domain_operation": 21
    }


@pytest.mark.parametrize("example_id", sorted(COMPONENT_SPECS))
def test_component_import_validator_contract_and_twenty_seeds(example_id: int) -> None:
    module = _load_generator(example_id)
    spec = COMPONENT_SPECS[example_id]
    for seed in range(20):
        first = module.generate(seed=seed)
        second = module.generate(seed=seed)
        assert first == second
        assert first["skill_id"] == spec["skill_id"]
        assert first["component_id"] == f"src_{example_id}"
        assert first["textbook_example_id"] == example_id
        assert first["domain_operation"] == B2_12_EXAMPLE_OPERATION_MAP[example_id]
        assert first["answer_type"] == spec["answer_type"]
        assert first["correct_answer"] not in (None, "", {}, [])
        assert validate_component_payload(first, f"src_{example_id}")["passed"] is True
        capability = validate_answer_contract_capability(first["answer_contract"])
        assert capability["checker_capability_status"] == "ok", capability


@pytest.mark.parametrize("example_id", sorted(COMPONENT_SPECS))
def test_component_shared_checker_accepts_correct_and_equivalent_rejects_wrong(example_id: int) -> None:
    spec = COMPONENT_SPECS[example_id]
    payload = _load_generator(example_id).generate(seed=7)
    correct = payload["correct_answer"]
    common = {
        "payload": payload,
        "answer_contract": payload["answer_contract"],
        "skill_id": str(spec["skill_id"]),
    }
    assert check_answer(correct, correct, **common) is True
    assert check_answer(_wrong_answer(payload), correct, **common) is False
    assert check_answer(_equivalent_answer(payload), correct, **common) is True


def test_single_choice_canonical_answer_is_semantic_not_position() -> None:
    payload = _load_generator(11585).generate(seed=11)
    assert payload["correct_answer"] == "0<a<1/2"
    assert payload["correct_answer"] not in {"A", "B", "C", "D"}
    assert payload["answer_contract"]["semantic_canonical_answer"] == "0<a<1/2"
    assert payload["answer_contract"]["semantic_choice_unique"] is True


def test_required_source_visuals_are_mounted_and_exist() -> None:
    for example_id in (11567, 11583, 11584):
        payload = _load_generator(example_id).generate(seed=0)
        visual = payload["visual_spec"]
        assert visual["required"] is True
        production_path = production_question_asset_relpath(visual["asset_path"])
        assert production_path and production_path.startswith("static/question_assets/")
        assert (ROOT / production_path).is_file()


def test_generators_contain_no_local_math_or_grading_authority() -> None:
    forbidden = (
        "import sympy", "from sympy", "def check(", "solve_proportion(",
        "sin(", "cos(", "tan(", "s=r", "cross_product", "raw string",
    )
    for example_id in COMPONENT_SPECS:
        source = (_component_dir(example_id) / "generate.py").read_text(encoding="utf-8")
        assert not any(token in source for token in forbidden), (example_id, source)
        assert "generate_b2_12_component_payload" in source

    domain_sources = (
        (ROOT / "core/domain/trigonometry_acute_domain.py").read_text(encoding="utf-8")
        + (ROOT / "core/domain/geometry_similarity_domain.py").read_text(encoding="utf-8")
    )
    assert not any(str(example_id) in domain_sources for example_id in COMPONENT_SPECS)
