from __future__ import annotations

import uuid

import pytest

from app import create_app
from core.checkers.solution_set_checker import check_solution_set_answer
from core.gencode.answer_grading import grade_answer_for_current_question
from core.gencode.runtime_skill_wrapper import check_answer
from models import User, db

SKILL_ID = "vh_數學B1_DistanceBetweenTwoPointsInPlane"
PT_SOLVE = "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"


@pytest.mark.parametrize(
    "user_answer",
    ["2,14", "14,2", "2，14", "{2,14}", "{14,2}", "2 或 14", "14 或 2", "k=2 或 k=14", "k = 14 或 k = 2", "2 or 14"],
)
def test_solution_set_checker_accepts_variants(user_answer: str) -> None:
    assert check_solution_set_answer(user_answer, [2, 14])


@pytest.mark.parametrize("user_answer", ["2", "14", "2,13", "2,14,16"])
def test_solution_set_checker_rejects_wrong(user_answer: str) -> None:
    assert not check_solution_set_answer(user_answer, [2, 14])


def test_runtime_wrapper_check_solution_set_payload() -> None:
    payload = {
        "skill_id": SKILL_ID,
        "problem_type_id": PT_SOLVE,
        "answer_contract": {
            "answer_type": "solution_set",
            "answer_shape": "unordered_set",
            "checker": "solution_set_checker",
            "answer_equivalence": "unordered_solution_set",
        },
        "checker": "solution_set_checker",
    }
    assert check_answer("2,14", [2, 14], payload=payload, skill_id=SKILL_ID)


def test_grade_answer_for_current_question_solution_set() -> None:
    current = {
        "skill": SKILL_ID,
        "problem_type_id": PT_SOLVE,
        "answer_type": "solution_set",
        "checker": "solution_set_checker",
        "equivalence": "unordered_solution_set",
        "correct_answer": [2, 14],
        "answer": [2, 14],
        "answer_contract": {
            "answer_type": "solution_set",
            "checker": "solution_set_checker",
            "answer_equivalence": "unordered_solution_set",
        },
    }
    result = grade_answer_for_current_question("2,14", current, SKILL_ID)
    assert result is not None
    assert result["correct"] is True


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"solset_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    return client


def test_check_answer_route_solution_set(logged_client) -> None:
    current = {
        "skill": SKILL_ID,
        "question_text": "已知 A(3,k)、B(11,8)，且 AB=10，求 k 的所有可能值。",
        "problem_type_id": PT_SOLVE,
        "answer_type": "solution_set",
        "checker": "solution_set_checker",
        "equivalence": "unordered_solution_set",
        "correct_answer": [2, 14],
        "answer": [2, 14],
        "choices": [],
        "answer_contract": {
            "answer_type": "solution_set",
            "answer_shape": "unordered_set",
            "checker": "solution_set_checker",
            "answer_equivalence": "unordered_solution_set",
        },
        "metadata": {"givens": [], "target": "k", "derivation": []},
    }
    with logged_client.session_transaction() as sess:
        saved = dict(current)
        saved["skill"] = SKILL_ID
        sess["current_data"] = saved
    resp = logged_client.post("/check_answer", json={"answer": "2,14"}).get_json() or {}
    assert resp.get("correct") is True, resp
