from __future__ import annotations

import importlib
import pytest
from typing import Any

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
PT_REASONING = "cartesian_coordinate_quadrant_symbol_reasoning"
QUADRANT_LABELS = {"第一象限", "第二象限", "第三象限", "第四象限"}

def test_gencode_v3_wrapper_generation() -> None:
    mod = importlib.import_module(f"skills.{SKILL_ID}")
    
    # Verify module structure
    assert hasattr(mod, "generate")
    assert hasattr(mod, "check")
    assert mod.SKILL_ID == SKILL_ID
    assert PT_REASONING in mod.VERIFIED_CANDIDATE_MODULES
    
    # Generate samples and test outputs
    for seed in range(20):
        payload = mod.generate(level=1, seed=seed)
        assert payload["problem_type_id"] == PT_REASONING
        assert payload["skill_id"] == SKILL_ID
        
        # Verify question text is formatted correctly
        qtext = payload["question_text"]
        assert "象限" in qtext
        assert "平面上的點" in qtext
        
        # Verify choices
        assert len(payload["choices"]) == 4
        assert set(payload["choices"]) == QUADRANT_LABELS
        
        # Verify correct answer choices match
        correct_label = payload["correct_answer"]
        assert correct_label in ("A", "B", "C", "D")
        
        correct_quadrant = payload["choices"]["ABCD".index(correct_label)]
        assert correct_quadrant in QUADRANT_LABELS
        
        # Test check function
        res_correct = mod.check(correct_label, correct_label, payload)
        assert res_correct["correct"] is True
        
        bad_label = "A" if correct_label != "A" else "B"
        res_incorrect = mod.check(bad_label, correct_label, payload)
        assert res_incorrect["correct"] is False
