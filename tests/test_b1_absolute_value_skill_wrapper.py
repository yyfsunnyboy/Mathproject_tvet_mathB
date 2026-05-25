from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from core.vocational_math_b1 import generated_candidate_loader as loader


def _write_candidate(path: Path, skill_id: str = "vh_數學B1_AbsoluteValue") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""
def generate(seed=None, difficulty="easy"):
    return {{
        "problem_type_id": "absolute_value_numeric_evaluation",
        "skill_id": "{skill_id}",
        "question_text": "求 $|{-3}|$ 的值。",
        "answer": "3",
        "answer_type": "numeric_or_expression",
        "checker_type": "deterministic_checker",
        "solution_steps": ["絕對值表示距離。", "答案為 3。"],
        "metadata": {{"scenario_family": "absolute_value_numeric_evaluation", "scenario_id": 1, "parameter_signature": "sig1", "question_pattern_id": "p1"}},
    }}
""",
        encoding="utf-8",
    )


def _prepare_verified_env(tmp_path: Path) -> None:
    registry = tmp_path / "configs" / "generated_registry" / "b1_section_1_1_verified_registry.v0.1.yaml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        "verified_problem_types:\n"
        "  - absolute_value_numeric_evaluation\n",
        encoding="utf-8",
    )
    problem_types = (
        tmp_path
        / "agent_skills_v2"
        / "vocational_math_b1"
        / "chapter_1"
        / "section_1_1_number_line_absolute_value"
        / "problem_types.yaml"
    )
    problem_types.parent.mkdir(parents=True, exist_ok=True)
    problem_types.write_text(
        "items:\n"
        "  -\n"
        "    problem_type_id: absolute_value_numeric_evaluation\n"
        "    skill_id: vh_數學B1_AbsoluteValue\n",
        encoding="utf-8",
    )
    candidate = (
        tmp_path
        / "generated_candidates"
        / "vocational_math_b1"
        / "section_1_1"
        / "absolute_value_numeric_evaluation"
        / "candidate_v1.py"
    )
    _write_candidate(candidate)


def test_wrapper_module_importable() -> None:
    module = importlib.import_module("skills.vh_數學B1_AbsoluteValue")
    assert hasattr(module, "generate")
    assert hasattr(module, "generate_question")


def test_wrapper_generate_from_verified_candidate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _prepare_verified_env(tmp_path)
    monkeypatch.setattr(loader, "REGISTRY_PATH", tmp_path / "configs" / "generated_registry" / "b1_section_1_1_verified_registry.v0.1.yaml")
    monkeypatch.setattr(
        loader,
        "PROBLEM_TYPES_PATH",
        tmp_path / "agent_skills_v2" / "vocational_math_b1" / "chapter_1" / "section_1_1_number_line_absolute_value" / "problem_types.yaml",
    )
    monkeypatch.setattr(loader, "GENERATED_BASE", tmp_path / "generated_candidates" / "vocational_math_b1" / "section_1_1")

    module = importlib.import_module("skills.vh_數學B1_AbsoluteValue")
    payload = module.generate(seed=1)

    assert payload["question_text"]
    assert payload["question"]
    assert payload["answer"]
    assert payload["correct_answer"]
    assert payload["problem_type_id"] == "absolute_value_numeric_evaluation"
    assert payload["skill_id"] == "vh_數學B1_AbsoluteValue"


def test_wrapper_clear_error_when_no_verified_candidate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(loader, "REGISTRY_PATH", tmp_path / "configs" / "generated_registry" / "b1_section_1_1_verified_registry.v0.1.yaml")
    monkeypatch.setattr(
        loader,
        "PROBLEM_TYPES_PATH",
        tmp_path / "agent_skills_v2" / "vocational_math_b1" / "chapter_1" / "section_1_1_number_line_absolute_value" / "problem_types.yaml",
    )
    monkeypatch.setattr(loader, "GENERATED_BASE", tmp_path / "generated_candidates" / "vocational_math_b1" / "section_1_1")

    module = importlib.import_module("skills.vh_數學B1_AbsoluteValue")
    with pytest.raises(RuntimeError) as exc:
        module.generate(seed=1)
    assert "此技能尚未開放自動出題" in str(exc.value)

