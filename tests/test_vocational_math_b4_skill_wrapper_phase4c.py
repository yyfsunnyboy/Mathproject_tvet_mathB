from __future__ import annotations

import importlib


def test_wrapper_import_and_symbols():
    module = importlib.import_module("skills.vh_數學B4_CombinationDefinition")
    assert hasattr(module, "generate")
    assert hasattr(module, "check")


def test_generate_payload_contract_and_values():
    module = importlib.import_module("skills.vh_數學B4_CombinationDefinition")
    payload = module.generate(level=1, seed=1)
    assert isinstance(payload, dict)

    required_keys = {
        "question_text",
        "answer",
        "correct_answer",
        "choices",
        "explanation",
        "skill_id",
        "subskill_id",
        "problem_type_id",
        "generator_key",
        "difficulty",
        "diagnosis_tags",
        "remediation_candidates",
        "source_style_refs",
        "parameters",
    }
    assert required_keys.issubset(set(payload.keys()))
    assert payload["correct_answer"] == payload["answer"]
    assert payload["skill_id"] == "vh_數學B4_CombinationDefinition"
    assert payload["problem_type_id"] == "combination_definition_basic"
    assert payload["generator_key"] == "b4.combination.combination_definition_basic"
    assert isinstance(payload["choices"], list)
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]


def test_check_correct_and_incorrect():
    module = importlib.import_module("skills.vh_數學B4_CombinationDefinition")
    payload = module.generate(level=1, seed=1)
    answer = payload["answer"]

    ok = module.check(str(answer), answer)
    assert ok["correct"] is True
    assert ok["result"] == "答對了"

    wrong = module.check("999999", answer)
    assert wrong["correct"] is False
    assert "答錯了" in wrong["result"]


def test_seed_determinism_and_diversity_note():
    module = importlib.import_module("skills.vh_數學B4_CombinationDefinition")
    p1 = module.generate(level=1, seed=1)
    p1_again = module.generate(level=1, seed=1)
    p2 = module.generate(level=1, seed=2)

    t1 = p1["parameters"]["parameter_tuple"]
    t1_again = p1_again["parameters"]["parameter_tuple"]
    t2 = p2["parameters"]["parameter_tuple"]

    assert t1 == t1_again
    assert p1["answer"] == p1_again["answer"]

    # Per requirement: if seed=1 and seed=2 happen to collide, do not fail.
    assert isinstance(t2, tuple)

