from __future__ import annotations

import uuid
from urllib.parse import quote

import pytest

from app import create_app
from models import User, db
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill


S_BASIC = "vh_數學B4_StatisticalBasicConcepts"
S_METHODS = "vh_數學B4_SamplingMethods"
S_SURVEY = "vh_數學B4_SamplingSurvey"

PT_BASIC = "statistical_basic_concepts_choice"
PT_METHODS = "sampling_methods_classification_choice"
PT_SURVEY = "sampling_survey_bias_review"


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"b4_choice_render_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def _choice_codes(choices) -> set[str]:
    codes: set[str] = set()
    for c in choices or []:
        s = str(c).strip()
        if "." in s:
            codes.add(s.split(".", 1)[0].strip())
    return codes


def test_generator_choice_contract_statistical_basic() -> None:
    for seed in range(1, 12):
        p = generate_for_chap3_skill(skill_id=S_BASIC, problem_type_id=PT_BASIC, seed=seed, level=1)
        q = str(p.get("question_text", ""))
        if "選項代號" in q or str(p.get("answer_input_type", "")).lower() == "choice":
            choices = p.get("choices") or []
            assert choices
            assert len(choices) >= 4
            assert all(bool(str(c).strip()) for c in choices)
            assert str(p.get("answer")) in _choice_codes(choices)
            assert p.get("explanation")


def test_sampling_methods_choice_contract_contains_four_methods() -> None:
    p = generate_for_chap3_skill(skill_id=S_METHODS, problem_type_id=PT_METHODS, seed=3, level=1)
    choices_text = " ".join(str(c) for c in (p.get("choices") or []))
    assert p.get("choices")
    assert "簡單隨機抽樣" in choices_text
    assert "系統抽樣" in choices_text
    assert "分層隨機抽樣" in choices_text
    assert "部落抽樣" in choices_text


@pytest.mark.parametrize("skill_id,problem_type", [(S_BASIC, PT_BASIC), (S_METHODS, PT_METHODS)])
def test_route_response_keeps_choices(skill_id: str, problem_type: str, logged_client) -> None:
    q = logged_client.get(
        f"/get_next_question?skill={quote(skill_id)}&problem_type={problem_type}&gen_seed=11&level=1"
    )
    assert q.status_code == 200
    d = q.get_json() or {}
    assert isinstance(d.get("choices"), list)
    assert len(d.get("choices", [])) >= 4


def test_check_answer_aliases_accept_abcd_and_1234(logged_client) -> None:
    # lock to a known seed where answer is 1 for StatisticalBasicConcepts
    q = logged_client.get(
        f"/get_next_question?skill={quote(S_BASIC)}&problem_type={PT_BASIC}&gen_seed=1&level=1"
    )
    assert q.status_code == 200
    d = q.get_json() or {}
    answer = str(d.get("choices", ["1."])[0]).split(".", 1)[0].strip()
    # Ensure we have a numeric code in this contract
    assert answer in {"1", "2", "3", "4"}

    # numeric correct
    r_num = logged_client.post("/check_answer", json={"answer": answer}).get_json() or {}
    assert r_num.get("correct") is True

    # alphabet alias: 1->A, 2->B ...
    alpha = chr(ord("A") + int(answer) - 1)
    r_alpha_upper = logged_client.post("/check_answer", json={"answer": alpha}).get_json() or {}
    r_alpha_lower = logged_client.post("/check_answer", json={"answer": alpha.lower()}).get_json() or {}
    assert r_alpha_upper.get("correct") is True
    assert r_alpha_lower.get("correct") is True

    wrong = "4" if answer != "4" else "3"
    r_wrong = logged_client.post("/check_answer", json={"answer": wrong}).get_json() or {}
    assert r_wrong.get("correct") is False


def test_frontend_rendering_safety_contract_fields(logged_client) -> None:
    q_choice = logged_client.get(
        f"/get_next_question?skill={quote(S_BASIC)}&problem_type={PT_BASIC}&gen_seed=5&level=1"
    )
    d_choice = q_choice.get_json() or {}
    assert d_choice.get("choices") or d_choice.get("choices_display")

    q_non_choice = logged_client.get(
        f"/get_next_question?skill={quote(S_SURVEY)}&problem_type={PT_SURVEY}&gen_seed=5&level=1"
    )
    d_non_choice = q_non_choice.get_json() or {}
    assert q_non_choice.status_code == 200
    assert d_non_choice.get("check_mode") == "review_mode"

