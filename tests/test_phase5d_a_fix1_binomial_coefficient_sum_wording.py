import pytest
from core.vocational_math_b4.services.question_router import generate_for_skill
from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import validate_b4_deterministic_adaptive_generator_payload

def test_binomial_coefficient_sum_wording():
    skill_id = "vh_數學B4_BinomialCoefficientIdentities"

    counts = {}
    for seed in range(1, 1001):
        payload = generate_for_skill(
            skill_id=skill_id,
            seed=seed,
        )
        pid = payload.get("problem_type_id")
        counts[pid] = counts.get(pid, 0) + 1
        
        if pid == "binomial_coefficient_sum":
            text = payload["question_text"]
            assert "展開" not in text
            assert "係數和" not in text
            assert "C^{" in text or "C^{n}" in text
            
            answer = payload["answer"]
            n = payload["parameters"]["n"]
            assert answer == 2 ** n
            
        elif pid == "binomial_odd_even_coefficient_sum":
            text = payload["question_text"]
            assert "展開" not in text
            assert "係數和" not in text
            assert "C^{" in text
            
            answer = payload["answer"]
            n = payload["parameters"]["n"]
            assert answer == 2 ** (n - 1)
            
        ok_payload, deny_reason = validate_b4_deterministic_adaptive_generator_payload(
            skill_id, payload
        )
        assert ok_payload is True, f"Failed on seed {seed}: {deny_reason}"

    assert counts.get("binomial_coefficient_sum", 0) > 0
    assert counts.get("binomial_odd_even_coefficient_sum", 0) > 0
    assert counts.get("combination_hockey_stick_sum", 0) > 0
    
    assert counts.get("tree_diagram_listing", 0) == 0
    assert counts.get("binomial_expansion_basic", 0) == 0
    assert counts.get("pascal_triangle_derivation", 0) == 0
