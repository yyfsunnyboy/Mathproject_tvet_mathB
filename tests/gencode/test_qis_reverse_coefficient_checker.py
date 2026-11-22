# -*- coding: utf-8 -*-
"""Regression: QIS reverse-coefficient answers must use integer checker contract."""
from __future__ import annotations

import importlib
import sys

import pytest

SKILL_ID = "vh_數學B1_QuadraticInequalitySolution"
REVERSE_PT = "integer_reverse_quadratic_inequality_coefficients"
REVERSE_COMPONENTS = ("src_4474", "src_4482", "src_4493", "src_4507")


def _reload_skill():
    for name in list(sys.modules):
        if SKILL_ID in name or name.endswith("QuadraticInequalitySolution"):
            del sys.modules[name]
    return importlib.import_module(f"skills.{SKILL_ID}")


def _is_correct(result) -> bool:
    if isinstance(result, dict):
        return bool(result.get("correct") or result.get("is_correct") or result.get("overall_correct"))
    return bool(result)


def test_reverse_coefficient_payload_uses_integer_checker_not_linear_equation():
    mod = _reload_skill()
    payload = mod.generate(level=1, seed=1, component_id="src_4474")
    ac = payload.get("answer_contract") or {}
    assert payload.get("problem_type_id") == REVERSE_PT
    assert str(ac.get("answer_type") or payload.get("answer_type")) == "integer"
    checker = str(ac.get("checker") or ac.get("checker_key") or payload.get("checker") or "")
    assert checker == "integer_checker"
    assert "linear_equation" not in checker


@pytest.mark.parametrize("component_id", REVERSE_COMPONENTS)
def test_reverse_coefficient_correct_answer_passes(component_id: str):
    mod = _reload_skill()
    payload = mod.generate(level=1, seed=17, component_id=component_id)
    assert payload.get("problem_type_id") == REVERSE_PT
    answer = payload.get("correct_answer")
    if answer is None:
        answer = payload.get("answer")
    assert str(answer).strip() != ""
    assert _is_correct(mod.check(answer, answer, payload))
    assert _is_correct(mod.check(str(answer).strip(), answer, payload))


@pytest.mark.parametrize("component_id", REVERSE_COMPONENTS)
def test_reverse_coefficient_wrong_answer_fails(component_id: str):
    mod = _reload_skill()
    payload = mod.generate(level=1, seed=19, component_id=component_id)
    answer = payload.get("correct_answer")
    if answer is None:
        answer = payload.get("answer")
    wrong = str(int(str(answer).strip()) + 7)
    assert not _is_correct(mod.check(wrong, answer, payload))


def test_reverse_coefficient_equivalent_numeric_forms():
    mod = _reload_skill()
    payload = mod.generate(level=1, seed=23, component_id="src_4474")
    answer = str(payload.get("correct_answer") or payload.get("answer")).strip()
    # Leading plus / whitespace should still grade as the same integer.
    assert _is_correct(mod.check(f" {answer} ", answer, payload))
    if answer.lstrip("-").isdigit() and not answer.startswith("-") and answer != "0":
        assert _is_correct(mod.check(f"+{answer}", answer, payload))


def test_all_qis_components_generate_and_self_check():
    mod = _reload_skill()
    keys = list(getattr(mod, "GENERATOR_KEYS", []) or [])
    assert len(keys) >= 5
    failures = []
    for index, component_id in enumerate(keys):
        payload = mod.generate(level=1, seed=100 + index, component_id=component_id)
        pt = str(payload.get("problem_type_id") or "")
        answer = payload.get("correct_answer")
        if answer is None:
            answer = payload.get("answer")
        ac = payload.get("answer_contract") or {}
        checker = str(ac.get("checker") or ac.get("checker_key") or payload.get("checker") or "")
        if pt == REVERSE_PT and checker != "integer_checker":
            failures.append((component_id, pt, f"bad_checker:{checker}"))
            continue
        if not str(payload.get("question") or payload.get("question_text") or "").strip():
            failures.append((component_id, pt, "empty_question"))
            continue
        if answer is None or str(answer).strip() == "":
            failures.append((component_id, pt, "empty_answer"))
            continue
        if not _is_correct(mod.check(answer, answer, payload)):
            failures.append((component_id, pt, f"self_check_failed checker={checker}"))
    assert not failures, failures
