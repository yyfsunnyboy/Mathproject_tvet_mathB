from __future__ import annotations

import pytest

from core.handwriting_ai_check import (
    HandwritingCheckContext,
    build_handwriting_check_response,
)


def _ctx(correct_answer="4", **overrides):
    data = {
        "question_uid": "q1",
        "skill_id": "skill_a",
        "question_text": "Compute.",
        "problem_type_id": "ptype",
        "answer_type": "numeric",
        "correct_answer": correct_answer,
        "answer_contract": {"answer_type": "numeric", "checker": "rational_checker"},
    }
    data.update(overrides)
    return HandwritingCheckContext(**data)


def _check(expected):
    def checker(user_answer, correct_answer, **kwargs):
        return str(user_answer).strip() == str(expected).strip()

    return checker


def _build(ai, *, correct_answer="4", checker=None, image="data:image/png;base64,ink"):
    return build_handwriting_check_response(
        image_base64=image,
        ctx=_ctx(correct_answer),
        ai_result=ai,
        checker=checker or _check(correct_answer),
    )


@pytest.mark.parametrize(
    ("recognized", "correct_answer"),
    [
        ("4", "4"),
        ("8/13", "8/13"),
        ("sqrt(5)", "sqrt(5)"),
    ],
)
def test_final_answer_only_accepts_integer_fraction_and_radical(recognized, correct_answer):
    result = _build(
        {"mode": "final_answer_only", "recognized_answer": recognized, "confidence": 0.98},
        correct_answer=correct_answer,
    )

    assert result["mode"] == "final_answer_only"
    assert result["is_correct"] is True
    assert result["should_record_attempt"] is True


def test_final_answer_only_accepts_choice_a():
    result = build_handwriting_check_response(
        image_base64="data:image/png;base64,ink",
        ctx=_ctx(
            "A",
            answer_type="choice",
            presentation_mode="single_choice",
            answer_contract={"answer_type": "choice", "checker": "choice_label_checker"},
            choices=["A. one", "B. two"],
        ),
        ai_result={"mode": "final_answer_only", "recognized_answer": "A", "confidence": 0.96},
        checker=_check("A"),
    )

    assert result["is_correct"] is True
    assert result["recognized_answer"] == "A"


def test_complete_correct_solution_with_steps_records_attempt():
    result = _build(
        {
            "mode": "solution_with_steps",
            "recognized_answer": "4",
            "recognized_steps": ["2+2=4", "answer=4"],
            "process_correct": True,
            "confidence": 0.94,
        }
    )

    assert result["is_correct"] is True
    assert result["final_answer_correct"] is True
    assert result["process_correct"] is True
    assert result["should_record_attempt"] is True


def test_first_line_formula_error_is_not_correct_even_when_answer_wrong():
    result = _build(
        {
            "mode": "solution_with_steps",
            "recognized_answer": "5/2",
            "recognized_steps": ["d=|c1-c2|/b", "d=5/2"],
            "process_correct": False,
            "first_error_step": 1,
            "error_type": "formula_error",
            "confidence": 0.94,
        }
    )

    assert result["is_correct"] is False
    assert result["process_correct"] is False
    assert result["first_error_step"] == 1
    assert result["should_record_attempt"] is True


def test_middle_arithmetic_error_reports_process_failure():
    result = _build(
        {
            "mode": "solution_with_steps",
            "recognized_answer": "5",
            "recognized_steps": ["2+2=5", "answer=5"],
            "process_correct": False,
            "first_error_step": 1,
            "error_type": "arithmetic_error",
            "confidence": 0.91,
        }
    )

    assert result["error_type"] == "arithmetic_error"
    assert result["is_correct"] is False


def test_correct_process_wrong_final_answer_uses_specific_feedback():
    result = _build(
        {
            "mode": "solution_with_steps",
            "recognized_answer": "5",
            "recognized_steps": ["sqrt(5)", "answer=5"],
            "process_correct": True,
            "confidence": 0.92,
        },
        correct_answer="sqrt(5)",
    )

    assert result["is_correct"] is False
    assert result["final_answer_correct"] is False
    assert result["process_correct"] is True
    assert "方法正確" in result["feedback"]


def test_wrong_process_accidentally_correct_answer_is_not_marked_correct():
    result = _build(
        {
            "mode": "solution_with_steps",
            "recognized_answer": "4",
            "recognized_steps": ["2*3=4", "answer=4"],
            "process_correct": False,
            "first_error_step": 1,
            "confidence": 0.9,
        }
    )

    assert result["is_correct"] is False
    assert result["final_answer_correct"] is True
    assert result["process_correct"] is False
    assert "最終答案正確" in result["feedback"]


def test_process_only_does_not_record_attempt():
    result = _build(
        {
            "mode": "process_only",
            "recognized_steps": ["2+2"],
            "process_correct": True,
            "confidence": 0.88,
        }
    )

    assert result["mode"] == "process_only"
    assert result["should_record_attempt"] is False
    assert "尚未寫出最後答案" in result["feedback"]


def test_blank_canvas_is_unrecognized_and_not_recorded():
    result = _build({"mode": "final_answer_only", "recognized_answer": "4", "confidence": 0.99}, image="blank")

    assert result["mode"] == "unrecognized"
    assert result["should_record_attempt"] is False
    assert result["error_type"] == "blank"


def test_low_confidence_is_not_recorded():
    result = _build({"mode": "final_answer_only", "recognized_answer": "4", "confidence": 0.4})

    assert result["mode"] == "unrecognized"
    assert result["should_record_attempt"] is False


def test_ai_timeout_shape_is_not_recorded():
    result = _build(None)

    assert result["mode"] == "unrecognized"
    assert result["should_record_attempt"] is False


def test_unrecognized_does_not_increase_fail_streak_contract():
    result = _build({"mode": "unrecognized", "confidence": 0.95})

    assert result["should_record_attempt"] is False
    assert result["is_correct"] is False


def test_response_does_not_leak_semantic_answer_or_contract():
    result = build_handwriting_check_response(
        image_base64="data:image/png;base64,ink",
        ctx=_ctx("4", semantic_answer="hidden", rubric="hidden rubric"),
        ai_result={"mode": "final_answer_only", "recognized_answer": "4", "confidence": 0.95},
        checker=_check("4"),
    )

    assert "semantic_answer" not in result
    assert "answer_contract" not in result
    assert "rubric" not in result


def test_deterministic_checker_decides_final_equivalence():
    calls = []

    def checker(user_answer, correct_answer, **kwargs):
        calls.append((user_answer, correct_answer, kwargs))
        return True

    result = _build(
        {"mode": "final_answer_only", "recognized_answer": "2/4", "confidence": 0.96},
        correct_answer="1/2",
        checker=checker,
    )

    assert result["is_correct"] is True
    assert calls and calls[0][0] == "2/4"
