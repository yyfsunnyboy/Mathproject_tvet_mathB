# -*- coding: utf-8 -*-
from __future__ import annotations
import importlib.util
from collections import Counter
from pathlib import Path
from typing import Any
import pytest

from core.gencode.b2_14_component_specs import SPECS,VIS
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.services.v3_question_integrity_validator import validate_component_payload
from core.question_image_assets import production_question_asset_relpath

ROOT=Path(__file__).resolve().parents[2]; V3_ROOT=ROOT/"agent_skills_v3"

def _dir(example_id:int)->Path:
    return V3_ROOT/str(SPECS[example_id]["skill_id"])/"components"/f"src_{example_id}"
def _load(example_id:int)->Any:
    path=_dir(example_id)/"generate.py"; spec=importlib.util.spec_from_file_location(f"b2_14_{example_id}",path)
    assert spec and spec.loader; module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
def _wrong(payload:dict[str,Any])->Any:
    correct=payload["correct_answer"]
    if isinstance(correct,dict):
        wrong=dict(correct); wrong[next(iter(wrong))]="__wrong__"; return wrong
    if payload["answer_type"]=="single_choice": return next(c["value"] for c in payload["choices"] if c["value"]!=correct)
    return "__wrong__"
def _equivalent(payload:dict[str,Any])->Any:
    correct=payload["correct_answer"]
    if payload["answer_type"]=="single_choice": return next(c["label"] for c in payload["choices"] if c["value"]==correct)
    if not isinstance(correct,dict): return f"2*({correct})/2"
    contracts={p["key"]:p for p in payload["answer_contract"]["parts"]}
    result={}
    for key,value in correct.items():
        part=contracts[key]
        if part["checker"]=="ordered_inequality_checker":
            terms=[v.strip() for v in str(value).split("<")]; result[key]=" > ".join(reversed(terms))
        elif part["checker"]=="decimal_tolerance_checker": result[key]=str(value)
        else: result[key]=f"2*({value})/2"
    return result

def test_exactly_one_component_per_sealed_example():
    assert len(SPECS)==21
    for example_id in SPECS:
        directory=_dir(example_id); assert directory.is_dir()
        assert {p.name for p in directory.iterdir() if p.is_file()}=={"generate.py","metadata.py","get_hint.py"}

def test_skill_answer_type_oracle_and_visual_counts():
    assert Counter(s["skill_id"] for s in SPECS.values())=={"vh_數學B2_SubSection_1_4_3":8,"vh_數學B2_SubSection_1_4_4":13}
    assert Counter(s["answer_type"] for s in SPECS.values())=={"short_answer":4,"single_choice":2,"multi_part":15}
    assert Counter(s["oracle_source"] for s in SPECS.values())=={"source_provided":6,"domain_operation":15}
    production_paths=[production_question_asset_relpath(path) for path in VIS.values()]
    assert len(VIS)==8 and all(path and (ROOT/path).is_file() for path in production_paths)

@pytest.mark.parametrize("example_id",sorted(SPECS))
def test_component_twenty_seed_verified_contract(example_id:int):
    module=_load(example_id); spec=SPECS[example_id]
    for seed in range(20):
        first=module.generate(seed=seed); second=module.generate(seed=seed)
        assert first==second
        assert first["skill_id"]==spec["skill_id"] and first["component_id"]==f"src_{example_id}"
        assert first["textbook_example_id"]==example_id and first["domain_operation"]==spec["operation"]
        assert first["answer_type"]==spec["answer_type"] and first["correct_answer"] not in (None,"",{},[])
        assert validate_component_payload(first,f"src_{example_id}")["passed"] is True
        assert validate_answer_contract_capability(first["answer_contract"])["checker_capability_status"]=="ok"
        if example_id in VIS:
            assert first["visual_spec"]["asset_path"]==VIS[example_id]
            assert first["visual_spec"]["usage"]=="practice_scratchpad_background"
            assert first["visual_response_contract"]["rubric_authority"]=="source_visual_reference"
        else: assert not (first.get("visual_spec") or {}).get("required")

@pytest.mark.parametrize("example_id",sorted(SPECS))
def test_shared_checker_accepts_correct_equivalent_and_rejects_wrong(example_id:int):
    payload=_load(example_id).generate(seed=7); correct=payload["correct_answer"]
    common={"payload":payload,"answer_contract":payload["answer_contract"],"skill_id":SPECS[example_id]["skill_id"]}
    assert check_answer(correct,correct,**common) is True
    assert check_answer(_equivalent(payload),correct,**common) is True
    assert check_answer(_wrong(payload),correct,**common) is False

def test_required_forms_and_no_local_math_or_grading_authority():
    for example_id in (11655,11656,11666):
        assert all(p["required_form"]=="ordered_inequality" for p in _load(example_id).generate()["answer_contract"]["parts"])
    for example_id in (11659,11660,11661,11662,11663,11664,11669,11670,11671,11672,11675):
        payload=_load(example_id).generate(); assert any(p.get("required_form")=="positive_minimum_period" for p in payload["answer_contract"]["parts"])
    forbidden=("import sympy","from sympy","def check(","math.sin","math.cos","math.tan")
    for example_id in SPECS:
        source=(_dir(example_id)/"generate.py").read_text(encoding="utf-8")
        assert not any(token in source for token in forbidden)
        assert "generate_b2_14_component_payload" in source
