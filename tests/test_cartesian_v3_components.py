# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import agent_skills_v3.vh_數學B1_CartesianCoordinateSystemEstablishment as skill_mod


def test_v3_components_exist():
    assert len(skill_mod.GENERATOR_KEYS) == 4
    for key in skill_mod.GENERATOR_KEYS:
        assert key in skill_mod._COMPONENT_DISPATCH
        
        # Test generate.py exists and has generate
        module = skill_mod._load_component_module(key, "generate.py")
        assert hasattr(module, "generate")
        assert hasattr(module, "check")
        
        # Test metadata.py exists
        meta = skill_mod._load_component_module(key, "metadata.py")
        assert hasattr(meta, "COMPONENT_ID")
        assert getattr(meta, "COMPONENT_ID") == key
        
        # Test get_hint.py exists and has get_hint
        hint = skill_mod._load_component_module(key, "get_hint.py")
        assert hasattr(hint, "get_hint")


def test_v3_generation_and_hints():
    for key in skill_mod.GENERATOR_KEYS:
        # Generate with seed
        payload = skill_mod.generate(seed=42, component_id=key)
        assert isinstance(payload, dict)
        assert payload["component_id"] == key
        assert "question" in payload
        assert "choices" in payload
        assert "answer" in payload
        assert "checker_type" in payload
        assert "answer_contract" in payload
        
        # Test checking
        choices = payload["choices"]
        correct_ans = payload["answer"]
        chk_res = skill_mod.check(correct_ans, correct_ans, payload)
        assert chk_res["correct"] is True
        
        # Test hints
        hint_s1 = skill_mod.get_hint(1, payload)
        hint_s2 = skill_mod.get_hint(2, payload)
        hint_s3 = skill_mod.get_hint(3, payload)
        assert isinstance(hint_s1, str) and len(hint_s1) > 0
        assert isinstance(hint_s2, str) and len(hint_s2) > 0
        assert isinstance(hint_s3, str) and len(hint_s3) > 0
