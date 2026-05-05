from __future__ import annotations

import importlib
from pathlib import Path

from app import create_app
from core.vocational_math_b4.services import question_router
from core.vocational_math_b4.services.question_router import generate_for_skill


SKILL_ID = "vh_數學B4_PermutationOfNonDistinctObjects"
PROBLEM_TYPE_ID = "repeated_permutation_digits"
GENERATOR_KEY = "b4.counting.repeated_permutation_digits"
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


def _assert_payload(payload: dict) -> None:
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert payload["skill_id"] == SKILL_ID
    assert payload["problem_type_id"] == PROBLEM_TYPE_ID
    assert payload["generator_key"] == GENERATOR_KEY
    assert isinstance(payload["answer"], int)
    assert payload["correct_answer"] == payload["answer"]
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]
    assert "[BLANK]" not in payload["question_text"]
    assert "[BLANK]" not in payload["explanation"]
    assert "{{" not in payload["question_text"]
    assert "{{" not in payload["explanation"]
    assert "C(" not in payload["question_text"]
    assert "P(" not in payload["question_text"]


def test_wrapper_imports_and_exposes_contract() -> None:
    module = importlib.import_module("skills.vh_數學B4_PermutationOfNonDistinctObjects")

    assert hasattr(module, "generate")
    assert hasattr(module, "check")


def test_wrapper_generate_returns_repeated_permutation_digits_payload() -> None:
    module = importlib.import_module("skills.vh_數學B4_PermutationOfNonDistinctObjects")
    payload = module.generate(level=1, seed=1)

    _assert_payload(payload)
    assert module.check(str(payload["answer"]), payload["answer"])["correct"] is True
    assert module.check("999999", payload["answer"])["correct"] is False


def test_generate_for_skill_supports_canonical_non_distinct_skill() -> None:
    payload = generate_for_skill(skill_id=SKILL_ID, level=1, seed=1)

    _assert_payload(payload)
    assert payload["problem_type_id"] in {PROBLEM_TYPE_ID}


def test_router_registry_uses_canonical_skill_without_mojibake_alias() -> None:
    assert SKILL_ID in question_router._REGISTRY
    assert any(
        entry["problem_type_id"] == PROBLEM_TYPE_ID
        for entry in question_router._REGISTRY[SKILL_ID]
    )
    assert all("?詨飛" not in skill_id for skill_id in question_router._REGISTRY)


def test_no_new_deterministic_generator_added_for_postcheck_c() -> None:
    assert not Path("core/vocational_math_b4/generators/permutation_non_distinct.py").exists()
    assert not Path("core/vocational_math_b4/generators/non_distinct_permutation.py").exists()


def test_practice_page_loads_without_missing_wrapper_error() -> None:
    app = create_app()
    app.config.update(TESTING=True)
    client = app.test_client()

    response = client.get(f"/practice/{SKILL_ID}")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "No module named" not in body
    assert "生成題目失敗" not in body
