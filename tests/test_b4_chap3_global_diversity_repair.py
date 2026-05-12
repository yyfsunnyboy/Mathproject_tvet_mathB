from __future__ import annotations

from core.vocational_math_b4.services.question_router import generate_for_chap3_skill


S_METHODS = "vh_?詨飛B4_SamplingMethods"
PT_METHODS = "sampling_methods_classification_choice"
S_BASIC = "vh_?詨飛B4_StatisticalBasicConcepts"
PT_BASIC = "statistical_basic_concepts_choice"


def test_chap3_global_diversity_sampling_methods_not_fixed_to_single_text() -> None:
    payloads = [
        generate_for_chap3_skill(skill_id=S_METHODS, problem_type_id=PT_METHODS, seed=i, level=1)
        for i in range(1, 31)
    ]
    texts = [str(p["question_text"]) for p in payloads]
    assert len(set(texts)) >= 15
    assert all(a != b for a, b in zip(texts, texts[1:]))


def test_chap3_global_diversity_statistical_basic_still_multi_text() -> None:
    payloads = [
        generate_for_chap3_skill(skill_id=S_BASIC, problem_type_id=PT_BASIC, seed=i, level=1)
        for i in range(1, 11)
    ]
    texts = {str(p["question_text"]) for p in payloads}
    assert len(texts) >= 3
