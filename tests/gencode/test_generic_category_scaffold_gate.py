from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.validators import check_complete_frequency_data, validate_generator_payload


SKILL_ID = "vh_數學B4_HistogramsAndFrequencyPolygons"
PROBLEM_TYPE_ID = "frequency_distribution_chart_construction"
CATEGORIES = ["A組", "B組", "C組", "D組"]
SCAFFOLD_ERROR = "SCAFFOLD_NOT_PUBLISHABLE:"


def _complete_givens() -> dict:
    return {
        "categories": CATEGORIES,
        "frequencies": [3, 4, 5, 6],
        "frequency_map": {"A組": 3, "B組": 4, "C組": 5, "D組": 6},
        "total_frequency": 18,
    }


def _payload(givens: dict, *, question_text: str = "請根據資料完成統計圖。") -> dict:
    expected = {"drawing_type": "histogram"}
    return {
        "skill_id": SKILL_ID,
        "problem_type_id": PROBLEM_TYPE_ID,
        "question": question_text,
        "question_text": question_text,
        "answer": "作圖",
        "correct_answer": "作圖",
        "answer_type": "drawing",
        "answer_shape": "drawing",
        "choices": [],
        "expected_drawing_spec": expected,
        "answer_contract": {
            "answer_type": "drawing",
            "answer_shape": "drawing",
            "checker": "free_response_drawing_checker",
            "checker_key": "free_response_drawing_checker",
            "answer_equivalence": "drawing_equivalence",
            "expected_drawing_spec": expected,
        },
        "metadata": {"givens": givens, "expected_drawing_spec": expected},
        "image_base64": "cG5n",
    }


def _errors(payload: dict) -> list[str]:
    spec = load_problem_type_spec(SKILL_ID, PROBLEM_TYPE_ID, prefer="curated")
    assert spec is not None
    return validate_generator_payload(payload, problem_type_spec=spec)


def _has_scaffold_error(errors: list[str]) -> bool:
    return any(error.startswith(SCAFFOLD_ERROR) for error in errors)


@pytest.mark.parametrize(
    "givens",
    [
        {"categories": CATEGORIES},
        {"categories": CATEGORIES, "frequencies": [3, 4, 5, 6]},
        {
            **_complete_givens(),
            "frequency_map": {"A組": 3, "B組": 4, "C組": 5, "X組": 6},
        },
        {
            **_complete_givens(),
            "frequency_map": {"A組": 3, "B組": 4, "C組": 5, "D組": 7},
        },
        {**_complete_givens(), "total_frequency": 99},
        {
            **_complete_givens(),
            "frequencies": [3, True, 5, 6],
            "frequency_map": {"A組": 3, "B組": True, "C組": 5, "D組": 6},
        },
        {**_complete_givens(), "total_frequency": True},
    ],
)
def test_incomplete_generic_frequency_data_is_blocked(givens):
    assert check_complete_frequency_data(givens, givens["categories"]) is False
    assert _has_scaffold_error(_errors(_payload(givens)))


def test_complete_generic_frequency_data_is_not_blocked():
    givens = _complete_givens()
    assert check_complete_frequency_data(givens, CATEGORIES) is True
    assert not _has_scaffold_error(_errors(_payload(givens)))


def test_drawing_spec_is_not_required_to_avoid_category_false_positive():
    payload = _payload(_complete_givens())
    payload.pop("expected_drawing_spec")
    payload["answer_contract"].pop("expected_drawing_spec")
    payload["metadata"].pop("expected_drawing_spec")
    errors = _errors(payload)
    assert not _has_scaffold_error(errors)
    assert any("expected_drawing_spec" in error for error in errors)


def test_complete_data_also_avoids_question_text_heuristic_false_positive():
    question = "請根據 A組、B組、C組、D組 完成統計圖。"
    assert not _has_scaffold_error(_errors(_payload(_complete_givens(), question_text=question)))


def test_src_3826_seed_zero_is_not_blocked():
    path = Path("agent_skills_v3") / SKILL_ID / "components" / "src_3826" / "generate.py"
    spec = importlib.util.spec_from_file_location("src_3826_generate", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.generate(seed=0)
    assert not _has_scaffold_error(_errors(payload))


def test_empty_scaffold_remains_blocked():
    assert _has_scaffold_error(_errors(_payload({"categories": CATEGORIES})))


def test_non_generic_categories_remain_unaffected():
    givens = {"categories": ["甲組", "乙組", "丙組", "丁組"]}
    assert not _has_scaffold_error(_errors(_payload(givens)))
