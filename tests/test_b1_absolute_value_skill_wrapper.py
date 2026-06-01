from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from core.vocational_math_b1 import generated_candidate_loader as loader

SKILL_MODULE = "skills.vh_數學B1_AbsoluteValue"
SKILL_ID = "vh_數學B1_AbsoluteValue"


def _write_candidate(path: Path, skill_id: str = SKILL_ID) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""
def generate(seed=None, difficulty="easy"):
    return {{
        "problem_type_id": "absolute_value_numeric_evaluation",
        "skill_id": "{skill_id}",
        "question_text": "求 $|-3|$ 的值。",
        "answer": "3",
        "answer_type": "integer",
        "checker_type": "integer_checker",
        "solution_steps": ["絕對值表示到 0 的距離。", "答案為 3。"],
        "metadata": {{
            "scenario_family": "absolute_value_numeric_evaluation",
            "scenario_id": 1,
            "parameter_signature": "absolute_value_numeric_evaluation:n=-3:difficulty=easy",
            "question_pattern_id": "p1"
        }},
    }}
""",
        encoding="utf-8",
    )


def _prepare_verified_env(tmp_path: Path) -> None:
    candidate = (
        tmp_path
        / "generated_candidates"
        / "vocational_math_b1"
        / "section_1_1"
        / "absolute_value_numeric_evaluation"
        / "candidate_v1.py"
    )
    _write_candidate(candidate)

    registry = tmp_path / "configs" / "generated_registry" / "b1_section_1_1_verified_registry.v0.1.yaml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        "verified_problem_types:\n"
        "  -\n"
        "    problem_type_id: absolute_value_numeric_evaluation\n"
        f"    skill_id: {SKILL_ID}\n"
        "    status: verified\n"
        f"    candidate_path: {candidate.as_posix()}\n"
        "    function_name: generate\n"
        "    answer_type: integer\n"
        "    checker_type: integer_checker\n",
        encoding="utf-8",
    )


def test_wrapper_module_importable() -> None:
    module = importlib.import_module(SKILL_MODULE)
    assert hasattr(module, "generate")
    assert hasattr(module, "generate_question")
    assert hasattr(module, "check")


def test_wrapper_generate_from_verified_candidate(monkeypatch: pytest.MonkeyPatch) -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        _prepare_verified_env(tmp_path)
        monkeypatch.setattr(
            loader,
            "REGISTRY_PATH",
            tmp_path / "configs" / "generated_registry" / "b1_section_1_1_verified_registry.v0.1.yaml",
        )
        monkeypatch.setattr(
            loader,
            "GENERATED_BASE",
            tmp_path / "generated_candidates" / "vocational_math_b1" / "section_1_1",
        )

        module = importlib.import_module(SKILL_MODULE)
        payload = module.generate(seed=1)

        assert payload["question_text"]
        assert payload["question"]
        assert payload["answer"] == "3"
        assert payload["correct_answer"] == "3"
        assert payload["problem_type_id"] == "absolute_value_numeric_evaluation"
        assert payload["skill_id"] == SKILL_ID


def test_wrapper_clear_error_when_no_verified_candidate(monkeypatch: pytest.MonkeyPatch) -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        monkeypatch.setattr(
            loader,
            "REGISTRY_PATH",
            tmp_path / "configs" / "generated_registry" / "b1_section_1_1_verified_registry.v0.1.yaml",
        )
        monkeypatch.setattr(
            loader,
            "GENERATED_BASE",
            tmp_path / "generated_candidates" / "vocational_math_b1" / "section_1_1",
        )

        module = importlib.import_module(SKILL_MODULE)
        with pytest.raises(RuntimeError) as exc:
            module.generate(seed=1)
        assert "尚未開放" in str(exc.value)



def test_solution_set_equivalence_for_absolute_value_equation_basic() -> None:
    module = importlib.import_module(SKILL_MODULE)
    correct_answer = "x=-17 或 x=17"

    assert module.check("17,-17", correct_answer)["correct"] is True
    assert module.check("-17,17", correct_answer)["correct"] is True
    assert module.check("17，-17", correct_answer)["correct"] is True
    assert module.check("x=17 或 x=-17", correct_answer)["correct"] is True
    assert module.check("x = 17 或 x = -17", correct_answer)["correct"] is True
    assert module.check("{17,-17}", correct_answer)["correct"] is True
    assert module.check("±17", correct_answer)["correct"] is True
    assert module.check("+-17", correct_answer)["correct"] is True

    assert module.check("17", correct_answer)["correct"] is False
    assert module.check("17,-16", correct_answer)["correct"] is False
    assert module.check("x=17", correct_answer)["correct"] is False


def test_non_equation_cases_unchanged() -> None:
    module = importlib.import_module(SKILL_MODULE)

    assert module.check("3", "3")["correct"] is True
    assert module.check("A", "A")["correct"] is True
    assert module.check("A", "B")["correct"] is False
