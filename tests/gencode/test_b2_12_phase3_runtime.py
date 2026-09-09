# -*- coding: utf-8 -*-
"""Final-seal runtime checks for Math B2 section 1-2 V3 wrappers."""

from __future__ import annotations

import importlib
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from core.gencode.b2_12_component_specs import COMPONENT_SPECS
from core.gencode.checker_registry import validate_answer_contract_capability


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_COMPONENT_COUNTS = {
    "vh_數學B2_RatioAndRatioValue": 2,
    "vh_數學B2_TrigonometricFunctionsOfAcuteAngles": 10,
    "vh_數學B2_TrigonometricValuesOfSpecialAngles": 6,
    "vh_數學B2_CalculatingFunctionValuesUsingCalculator": 2,
    "vh_數學B2_FundamentalTrigonometricIdentities": 10,
}
RUNTIME_EXCLUDED_EXAMPLE_IDS = frozenset({11575})


def _facade(skill_id: str) -> Any:
    return importlib.import_module(f"skills.{skill_id}")


def _expected_ids(skill_id: str) -> list[str]:
    return [
        f"src_{example_id}"
        for example_id, spec in sorted(COMPONENT_SPECS.items())
        if (
            spec["skill_id"] == skill_id
            and example_id not in RUNTIME_EXCLUDED_EXAMPLE_IDS
        )
    ]


def _wrong_answer(correct: Any) -> Any:
    if isinstance(correct, dict):
        return {key: "__definitely_wrong__" for key in correct}
    return "__definitely_wrong__"


@pytest.mark.parametrize("skill_id,expected_count", SKILL_COMPONENT_COUNTS.items())
def test_published_wrapper_manifest_and_facade_are_exact(
    skill_id: str, expected_count: int
) -> None:
    wrapper = importlib.import_module(f"agent_skills_v3.{skill_id}")
    facade = _facade(skill_id)
    expected_ids = _expected_ids(skill_id)
    manifest_path = PROJECT_ROOT / "agent_skills_v3" / skill_id / "component_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert len(expected_ids) == expected_count
    assert wrapper.GENERATOR_KEYS == expected_ids
    assert len(wrapper.GENERATOR_KEYS) == len(set(wrapper.GENERATOR_KEYS))
    assert len(wrapper.GENERATOR_SPECS) == expected_count
    assert manifest["publish_status"] == "production_manifest_compiled"
    assert manifest["component_count"] == expected_count
    assert [row["component_id"] for row in manifest["components"]] == expected_ids
    assert all(row["status"] == "verified" for row in manifest["components"])
    assert callable(facade.generate) and callable(facade.check) and callable(facade.get_hint)

    source = (PROJECT_ROOT / "agent_skills_v3" / skill_id / "__init__.py").read_text(
        encoding="utf-8"
    )
    facade_source = (PROJECT_ROOT / "skills" / f"{skill_id}.py").read_text(
        encoding="utf-8"
    )
    forbidden = ("old_generator", "nearest_template", "nearest-template", "llm")
    assert not any(token in (source + facade_source).lower() for token in forbidden)


@pytest.mark.parametrize("skill_id", SKILL_COMPONENT_COUNTS)
def test_every_component_generates_multiple_runtime_questions_and_grades(
    skill_id: str,
) -> None:
    facade = _facade(skill_id)
    for component_id in _expected_ids(skill_id):
        payloads = [
            facade.generate(level=1, seed=seed, component_id=component_id)
            for seed in range(3)
        ]
        for payload in payloads:
            assert payload["component_id"] == component_id
            assert payload.get("question_text")
            assert payload.get("correct_answer") not in (None, "", {}, [])
            contract = payload.get("answer_contract")
            assert isinstance(contract, dict) and contract
            validation = validate_answer_contract_capability(contract)
            assert validation["checker_capability_status"] != "blocked", validation

        canonical = payloads[0]["correct_answer"]
        assert facade.check(canonical, canonical, payloads[0]) is True
        assert facade.check(_wrong_answer(canonical), canonical, payloads[0]) is False


def test_11585_choice_oracle_is_semantic_not_positional() -> None:
    facade = _facade("vh_數學B2_FundamentalTrigonometricIdentities")
    observed_correct_labels: set[str] = set()
    for seed in range(12):
        payload = facade.generate(seed=seed, component_id="src_11585")
        semantic = payload["correct_answer"]
        matching = [row["label"] for row in payload["choices"] if row["text"] == semantic]
        assert len(matching) == 1
        correct_label = matching[0]
        observed_correct_labels.add(correct_label)
        wrong_label = next(row["label"] for row in payload["choices"] if row["text"] != semantic)
        assert payload["answer_contract"]["semantic_answer"] == semantic
        assert semantic not in {"A", "B", "C", "D"}
        assert facade.check(semantic, semantic, payload) is True
        assert facade.check(correct_label, semantic, payload) is True
        assert facade.check(wrong_label, semantic, payload) is False
    assert len(observed_correct_labels) > 1


@pytest.mark.parametrize("component_id", ["src_11561", "src_11571"])
def test_decimal_precision_and_tolerance_runtime(component_id: str) -> None:
    facade = _facade("vh_數學B2_CalculatingFunctionValuesUsingCalculator")
    payload = facade.generate(seed=7, component_id=component_id)
    within: dict[str, str] = {}
    outside: dict[str, str] = {}
    for part in payload["answer_contract"]["parts"]:
        key = part["key"]
        expected = str(payload["correct_answer"][key])
        precision = int(part["precision"])
        tolerance = Decimal(str(part["tolerance"]))
        assert len(expected.partition(".")[2]) == precision
        assert part["rounding_policy"] == "ROUND_HALF_UP"
        within[key] = str(Decimal(expected) + tolerance * Decimal("0.8"))
        outside[key] = str(Decimal(expected) + tolerance * Decimal("1.2"))
    assert facade.check(within, payload["correct_answer"], payload) is True
    assert facade.check(outside, payload["correct_answer"], payload) is False


def test_11583_chord_arc_shared_delegate_equivalence_and_hint_runtime() -> None:
    facade = _facade("vh_數學B2_TrigonometricFunctionsOfAcuteAngles")
    payload = facade.generate(seed=11, component_id="src_11583")
    assert payload["correct_answer"] == {"chord_length": "2", "arc_length": "2*pi/3"}
    assert (
        payload["validation_facts"]["cross_domain_delegate"]
        == "trigonometry.angle.sector_arc_and_area"
    )
    equivalent = {"chord_length": "2.0", "arc_length": "4*pi/6"}
    assert facade.check(equivalent, payload["correct_answer"], payload) is True
    assert facade.get_hint(1, payload)
    assert facade.get_hint(2, payload)


def test_final_runtime_component_total_is_30() -> None:
    assert len(COMPONENT_SPECS) == 31
    assert sum(SKILL_COMPONENT_COUNTS.values()) == 30
    assert sum(len(_expected_ids(skill_id)) for skill_id in SKILL_COMPONENT_COUNTS) == 30


def test_11575_source_is_preserved_but_runtime_unreachable() -> None:
    assert 11575 in COMPONENT_SPECS
    assert COMPONENT_SPECS[11575]["operation"] == "collinear_three_points_parameter"

    skill_id = "vh_數學B2_TrigonometricFunctionsOfAcuteAngles"
    wrapper = importlib.import_module(f"agent_skills_v3.{skill_id}")
    facade = _facade(skill_id)
    manifest_path = PROJECT_ROOT / "agent_skills_v3" / skill_id / "component_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert "src_11575" not in wrapper.GENERATOR_KEYS
    assert "src_11575" not in wrapper._COMPONENT_DISPATCH
    assert all(row["textbook_example_id"] != 11575 for row in manifest["components"])
    with pytest.raises(RuntimeError, match="unknown_component_id:src_11575"):
        facade.generate(seed=0, component_id="src_11575")
