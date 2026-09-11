# -*- coding: utf-8 -*-
"""Phase-2 verification for all 29 Math B2 section 1-3 components."""

from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from core.gencode.b2_13_component_specs import SPECS
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.services.v3_question_integrity_validator import validate_component_payload


ROOT = Path(__file__).resolve().parents[2]
V3_ROOT = ROOT / "agent_skills_v3"


def _component_dir(example_id: int) -> Path:
    spec = SPECS[example_id]
    return V3_ROOT / str(spec["skill_id"]) / "components" / f"src_{example_id}"


def _load_generator(example_id: int) -> Any:
    path = _component_dir(example_id) / "generate.py"
    module_spec = importlib.util.spec_from_file_location(f"b2_13_component_{example_id}", path)
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
        return next(choice["value"] for choice in payload["choices"] if choice["value"] != correct)
    return "__wrong__"


def _equivalent_scalar(value: Any, part: dict[str, Any]) -> Any:
    text = str(value)
    checker = str(part.get("checker") or part.get("checker_key") or "")
    if checker in {"text_checker", "text_short_checker", "quadrant_checker"}:
        return text
    if checker == "integer_checker":
        return f"{int(text) * 2}/2"
    if checker == "expression_checker" and text.lstrip("-").isdigit():
        return f"+{text}" if not text.startswith("-") else text
    return f"2*({text})/2"


def _equivalent_answer(payload: dict[str, Any]) -> Any:
    correct = payload["correct_answer"]
    contract = payload["answer_contract"]
    if payload["answer_type"] == "single_choice":
        return next(choice["label"] for choice in payload["choices"] if choice["value"] == correct)
    if isinstance(correct, dict):
        parts = {str(part["key"]): part for part in contract["parts"]}
        return {key: _equivalent_scalar(value, parts[key]) for key, value in correct.items()}
    return _equivalent_scalar(correct, contract)


def test_b2_13_has_exactly_one_physical_component_per_example() -> None:
    assert len(SPECS) == 29
    for example_id in SPECS:
        directory = _component_dir(example_id)
        assert directory.is_dir()
        assert {path.name for path in directory.iterdir() if path.is_file()} == {
            "generate.py", "metadata.py", "get_hint.py"
        }


def test_b2_13_fixed_skill_answer_type_and_oracle_counts() -> None:
    assert Counter(str(spec["skill_id"]) for spec in SPECS.values()) == {
        "vh_數學B2_SubSection_1_3_1": 3,
        "vh_數學B2_SubSection_1_3_2": 3,
        "vh_數學B2_SubSection_1_3_4": 7,
        "vh_數學B2_SubSection_1_3_5": 3,
        "vh_數學B2_SubSection_1_3_6": 6,
        "vh_數學B2_SubSection_1_3_7": 7,
    }
    assert Counter(str(spec["answer_type"]) for spec in SPECS.values()) == {
        "short_answer": 4, "single_choice": 1, "multi_part": 23, "table_fill": 1
    }
    assert Counter(str(spec["oracle_source"]) for spec in SPECS.values()) == {
        "source_provided": 9, "domain_operation": 20
    }


@pytest.mark.parametrize("example_id", sorted(SPECS))
def test_component_import_validator_contract_and_twenty_seeds(example_id: int) -> None:
    module = _load_generator(example_id)
    spec = SPECS[example_id]
    for seed in range(20):
        first = module.generate(seed=seed)
        second = module.generate(seed=seed)
        assert first == second
        assert first["skill_id"] == spec["skill_id"]
        assert first["component_id"] == f"src_{example_id}"
        assert first["textbook_example_id"] == example_id
        assert first["domain_operation"] == spec["operation"]
        assert first["answer_type"] == spec["answer_type"]
        assert first["correct_answer"] not in (None, "", {}, [])
        assert validate_component_payload(first, f"src_{example_id}")["passed"] is True
        capability = validate_answer_contract_capability(first["answer_contract"])
        assert capability["checker_capability_status"] == "ok", capability


@pytest.mark.parametrize("example_id", sorted(SPECS))
def test_component_shared_checker_accepts_correct_and_equivalent_rejects_wrong(example_id: int) -> None:
    payload = _load_generator(example_id).generate(seed=7)
    correct = payload["correct_answer"]
    common = {
        "payload": payload,
        "answer_contract": payload["answer_contract"],
        "skill_id": str(SPECS[example_id]["skill_id"]),
    }
    assert check_answer(correct, correct, **common) is True
    assert check_answer(_wrong_answer(payload), correct, **common) is False
    assert check_answer(_equivalent_answer(payload), correct, **common) is True


def test_single_choice_uses_semantic_canonical_answer() -> None:
    payload = _load_generator(11644).generate(seed=11)
    assert payload["correct_answer"] == "第四象限"
    assert payload["correct_answer"] not in {"A", "B", "C", "D"}
    assert payload["answer_contract"]["semantic_canonical_answer"] == "第四象限"


def test_table_fill_uses_formal_contract_and_shared_checker() -> None:
    payload = _load_generator(11651).generate(seed=11)
    contract = payload["answer_contract"]
    assert contract["answer_type"] == "table_fill"
    assert contract["checker_key"] == "table_fill_checker"
    assert len(contract["parts"]) == 12
    assert len(contract["blank_cells"]) == 6


def test_generators_contain_no_local_math_or_grading_authority() -> None:
    forbidden = ("import sympy", "from sympy", "def check(", "math.sin", "math.cos", "math.tan")
    for example_id in SPECS:
        source = (_component_dir(example_id) / "generate.py").read_text(encoding="utf-8")
        assert not any(token in source for token in forbidden), (example_id, source)
        assert "generate_b2_13_component_payload" in source

    domain_source = (ROOT / "core/domain/trigonometry_arbitrary_domain.py").read_text(encoding="utf-8")
    assert not any(str(example_id) in domain_source for example_id in SPECS)
