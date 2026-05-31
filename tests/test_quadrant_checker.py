from __future__ import annotations

import importlib
import uuid
from urllib.parse import quote

import pytest

from app import create_app
from core.checkers.quadrant_checker import check_quadrant_answer, normalize_quadrant_answer
from core.gencode.runtime_skill_wrapper import check_answer as wrapper_check_answer
from models import User, db

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"

Q2_ACCEPT = [
    "第二象限",
    "第二",
    "2",
    "二",
    "第2象限",
    "第Ⅱ象限",
    "II",
    "Ⅱ",
]

Q2_REJECT = [
    "第一象限",
    "1",
    "一",
    "第三象限",
    "3",
    "三",
    "第四象限",
    "4",
    "四",
]

QUADRANT_CASES = {
    "第一象限": {
        "accept": ["第一象限", "第一", "1", "一", "第1象限", "第１象限", "I", "Ⅰ", "第I象限"],
        "reject": ["第二象限", "2", "二", "第三象限", "3", "三", "第四象限", "4", "四"],
    },
    "第二象限": {
        "accept": Q2_ACCEPT,
        "reject": Q2_REJECT,
    },
    "第三象限": {
        "accept": ["第三象限", "第三", "3", "三", "第3象限", "第３象限", "III", "Ⅲ", "第III象限"],
        "reject": ["第一象限", "1", "一", "第二象限", "2", "二", "第四象限", "4", "四"],
    },
    "第四象限": {
        "accept": ["第四象限", "第四", "4", "四", "第4象限", "第４象限", "IV", "Ⅳ", "第IV象限"],
        "reject": ["第一象限", "1", "一", "第二象限", "2", "二", "第三象限", "3", "三"],
    },
}


@pytest.mark.parametrize("correct", QUADRANT_CASES.keys())
def test_quadrant_checker_accepts_equivalent_answers(correct: str) -> None:
    for user in QUADRANT_CASES[correct]["accept"]:
        assert check_quadrant_answer(user, correct) is True, f"{user!r} should match {correct!r}"


@pytest.mark.parametrize("correct", QUADRANT_CASES.keys())
def test_quadrant_checker_rejects_other_quadrants(correct: str) -> None:
    for user in QUADRANT_CASES[correct]["reject"]:
        assert check_quadrant_answer(user, correct) is False, f"{user!r} should not match {correct!r}"


@pytest.mark.parametrize(
    ("label", "canonical"),
    [
        ("第一象限", "Q1"),
        ("第二象限", "Q2"),
        ("第三象限", "Q3"),
        ("第四象限", "Q4"),
        ("2", "Q2"),
        ("Ⅱ", "Q2"),
        ("第2象限", "Q2"),
    ],
)
def test_normalize_quadrant_answer(label: str, canonical: str) -> None:
    assert normalize_quadrant_answer(label) == canonical


def test_non_quadrant_correct_answer_falls_back_to_none() -> None:
    assert check_quadrant_answer("2", "42") is None
    assert check_quadrant_answer("A", "B") is None
    assert check_quadrant_answer("第二象限", "2") is None


def test_runtime_wrapper_quadrant_and_regressions() -> None:
    assert wrapper_check_answer("2", "第二象限") is True
    assert wrapper_check_answer("4", "第二象限") is False
    assert wrapper_check_answer("C", "C") is True
    assert wrapper_check_answer("c", "C") is True
    assert wrapper_check_answer("B", "A") is False
    assert wrapper_check_answer("42", "42") is True
    assert wrapper_check_answer("2", "2") is True
    assert wrapper_check_answer("3", "2") is False


def test_cartesian_skill_check_uses_quadrant_equivalence() -> None:
    mod = importlib.import_module(f"skills.{SKILL_ID}")
    assert mod.check("二", "第二象限") is True
    assert mod.check("4", "第二象限") is False


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"quadrant_checker_{uuid.uuid4().hex[:10]}",
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


def test_practice_route_quadrant_short_answer_check(logged_client) -> None:
    cart_mod = importlib.import_module(f"skills.{SKILL_ID}")

    target_seed = None
    for seed in range(80):
        payload = cart_mod.generate(level=1, seed=seed)
        if payload.get("choices"):
            continue
        if str(payload.get("answer", "")).strip() == "第二象限":
            target_seed = seed
            break
    assert target_seed is not None

    q = logged_client.get(
        f"/get_next_question?skill={quote(SKILL_ID)}&level=1&gen_seed={target_seed}"
    )
    assert q.status_code == 200

    ok = logged_client.post("/check_answer", json={"answer": "二"}).get_json() or {}
    assert ok.get("correct") is True

    q2 = logged_client.get(
        f"/get_next_question?skill={quote(SKILL_ID)}&level=1&gen_seed={target_seed}"
    )
    assert q2.status_code == 200
    bad = logged_client.post("/check_answer", json={"answer": "4"}).get_json() or {}
    assert bad.get("correct") is False
