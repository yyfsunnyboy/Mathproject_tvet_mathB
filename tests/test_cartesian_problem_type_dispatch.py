from __future__ import annotations

import importlib
SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
PT_REASONING = "cartesian_coordinate_quadrant_symbol_reasoning"
PUBLISHED_PROBLEM_TYPES = {
    PT_REASONING,
    "axis_distance_coordinate_point_numerical_choice",
    "quadrant_statement_reasoning_choice",
}

def test_gencode_v3_wrapper_generation() -> None:
    mod = importlib.import_module(f"skills.{SKILL_ID}")
    
    # Verify module structure
    assert hasattr(mod, "generate")
    assert hasattr(mod, "check")
    assert mod.SKILL_ID == SKILL_ID
    assert mod.GENERATOR_KEYS == ["src_4417", "src_4435", "src_4509", "src_4510"]
    
    # Generate samples and test outputs
    for seed in range(20):
        payload = mod.generate(level=1, seed=seed)
        assert payload["problem_type_id"] in PUBLISHED_PROBLEM_TYPES
        assert payload["skill_id"] == SKILL_ID
        
        # Verify question text is formatted correctly
        qtext = payload["question_text"]
        assert qtext.strip()
        
        # Verify choices
        assert len(payload["choices"]) == 4
        
        # Verify correct answer choices match
        correct_label = payload["correct_answer"]
        assert correct_label in ("A", "B", "C", "D")
        
        assert payload["choices"]["ABCD".index(correct_label)]
        
        # Test check function
        res_correct = mod.check(correct_label, correct_label, payload)
        assert (res_correct.get("correct") if isinstance(res_correct, dict) else res_correct) is True
        
        bad_label = "A" if correct_label != "A" else "B"
        res_incorrect = mod.check(bad_label, correct_label, payload)
        assert (res_incorrect.get("correct") if isinstance(res_incorrect, dict) else res_incorrect) is False
