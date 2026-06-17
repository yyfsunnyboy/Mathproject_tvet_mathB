# -*- coding: utf-8 -*-
"""Tests for V3 skill house generate() contract merge."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_ID = "vh_數學B1_HorizontalAndVerticalLineEquations"


def _load_skill_house_generate():
    init_path = PROJECT_ROOT / "agent_skills_v3" / SKILL_ID / "__init__.py"
    if not init_path.is_file():
        pytest.skip("production V3 house not published yet")
    spec = importlib.util.spec_from_file_location("hv_v3_house", init_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_wrapper_house_generate_merges_generator_spec_fields():
    module = _load_skill_house_generate()
    if not hasattr(module, "GENERATOR_SPECS") or not module.GENERATOR_SPECS:
        pytest.skip("GENERATOR_SPECS missing")
    payload = module.generate(seed=6, component_id=module.GENERATOR_SPECS[0]["component_id"])
    assert payload.get("component_id")
    assert payload.get("textbook_example_id")
    assert payload.get("problem_type_id")
    assert payload.get("presentation_mode")
    meta = payload.get("metadata") or {}
    assert meta.get("presentation_mode")
    assert payload.get("answer_contract")
