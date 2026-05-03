from __future__ import annotations

import importlib


REQUIRED_KEYS = {
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
    "router_trace",
}

PLACEHOLDERS = ["[BLANK]", "[FORMULA_MISSING]", "[FORMULA_IMAGE", "[WORD_EQUATION_UNPARSED]", "□", "＿＿"]


def test_factorial_wrapper_import_and_symbols() -> None:
    module = importlib.import_module("skills.vh_數學B4_FactorialNotation")
    assert hasattr(module, "generate")
    assert hasattr(module, "check")


def test_factorial_wrapper_generate_payload_contract() -> None:
    module = importlib.import_module("skills.vh_數學B4_FactorialNotation")
    payload = module.generate(level=1, seed=1)
    assert isinstance(payload, dict)
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert payload["correct_answer"] == payload["answer"]
    assert payload["skill_id"] == "vh_數學B4_FactorialNotation"
    assert payload["problem_type_id"] == "factorial_equation_solve_n"
    assert payload["generator_key"] == "b4.counting.factorial_equation_solve_n"
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]
    for token in PLACEHOLDERS:
        assert token not in payload["question_text"]
        assert token not in payload["explanation"]
    assert "$" in payload["question_text"] or "$" in payload["explanation"]
    assert "\\frac" in payload["question_text"] or "\\frac" in payload["explanation"]


def test_factorial_wrapper_check() -> None:
    module = importlib.import_module("skills.vh_數學B4_FactorialNotation")
    payload = module.generate(level=1, seed=1)
    answer = payload["answer"]
    ok = module.check(str(answer), answer)
    assert ok["correct"] is True
    wrong = module.check("999999", answer)
    assert wrong["correct"] is False


def test_factorial_wrapper_import_and_generate_no_raise() -> None:
    import skills.vh_數學B4_FactorialNotation as fn
    # 確認不會 raise Unsupported skill_id
    payload = fn.generate(level=1, seed=1)
    assert payload["skill_id"] == "vh_數學B4_FactorialNotation"


