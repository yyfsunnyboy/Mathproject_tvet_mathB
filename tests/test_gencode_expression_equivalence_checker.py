from __future__ import annotations

import uuid

import pytest

from app import create_app
from core.checkers.expression_equivalence_checker import (
    check_expression_equivalence_answer,
    check_expression_equivalence_debug,
)
from core.gencode.answer_grading import grade_answer_for_current_question
from core.gencode.runtime_skill_wrapper import check_answer

CORRECT_SQRT17 = r"\sqrt{17}"


@pytest.mark.parametrize(
    "user_answer",
    ["sqrt(17)", "sqrt{17}", r"\sqrt{17}", r"\sqrt(17)", "√17", "√(17)"],
)
def test_sqrt17_variants_accepted(user_answer: str) -> None:
    assert check_expression_equivalence_answer(user_answer, CORRECT_SQRT17)


@pytest.mark.parametrize(
    "user_answer",
    ["2sqrt(5)", "2 sqrt(5)", "2*sqrt(5)", "2√5", "2√(5)", r"2\sqrt{5}", r"\sqrt{20}", "sqrt(20)"],
)
def test_coef_radical_equivalent(user_answer: str) -> None:
    assert check_expression_equivalence_answer(user_answer, r"2\sqrt{5}")


@pytest.mark.parametrize("user_answer", ["5", "5.0"])
def test_integer_decimal_equivalent(user_answer: str) -> None:
    assert check_expression_equivalence_answer(user_answer, "5")


@pytest.mark.parametrize("user_answer", ["17", "sqrt(16)", "4"])
def test_sqrt17_wrong_rejected(user_answer: str) -> None:
    assert not check_expression_equivalence_answer(user_answer, CORRECT_SQRT17)


def test_debug_normalization_fields() -> None:
    dbg = check_expression_equivalence_debug("sqrt(17)", CORRECT_SQRT17)
    assert dbg["correct"] is True
    assert dbg["normalized_user_expression"] == "sqrt(17)"
    assert dbg["normalized_correct_expression"] == "sqrt(17)"


def test_runtime_wrapper_expression_payload() -> None:
    payload = {
        "answer_contract": {
            "answer_type": "numeric_or_radical",
            "checker": "expression_equivalence_checker",
            "answer_equivalence": "expression_equivalence",
        },
        "checker": "expression_equivalence_checker",
    }
    assert check_answer("sqrt(17)", CORRECT_SQRT17, payload=payload)


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    from models import User, db

    with app.app_context():
        user = User(
            username=f"expr_{uuid.uuid4().hex[:10]}",
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


def test_check_answer_route_expression(logged_client) -> None:
    current = {
        "skill": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
        "question_text": "求 A(3,-1) 與 B(4,3) 的距離。",
        "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "answer_type": "numeric_or_radical",
        "checker": "expression_equivalence_checker",
        "equivalence": "expression_equivalence",
        "correct_answer": CORRECT_SQRT17,
        "answer": CORRECT_SQRT17,
        "choices": [],
        "answer_contract": {
            "answer_type": "numeric_or_radical",
            "checker": "expression_equivalence_checker",
            "answer_equivalence": "expression_equivalence",
        },
        "metadata": {"givens": [], "target": "AB", "derivation": []},
    }
    with logged_client.session_transaction() as sess:
        sess["current_data"] = dict(current)
    resp = logged_client.post("/check_answer", json={"answer": "sqrt(17)"}).get_json() or {}
    assert resp.get("correct") is True, resp


def test_grade_answer_numeric_or_radical() -> None:
    current = {
        "answer_type": "numeric_or_radical",
        "checker": "expression_equivalence_checker",
        "equivalence": "expression_equivalence",
        "correct_answer": CORRECT_SQRT17,
        "answer_contract": {
            "answer_type": "numeric_or_radical",
            "checker": "expression_equivalence_checker",
        },
    }
    result = grade_answer_for_current_question("sqrt(17)", current, "vh_數學B1_DistanceBetweenTwoPointsInPlane")
    assert result is not None and result["correct"] is True
