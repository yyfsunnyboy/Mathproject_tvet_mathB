from __future__ import annotations

import uuid
from urllib.parse import quote

import pytest

from app import create_app
from core.vocational_math_b4.services import question_router as chap3_router
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill
from models import User, db


FORBIDDEN = ["請說明", "請簡述", "請討論", "簡述理由", "提出理由"]


def _resolve_skill_id(suffix: str) -> str:
    for key in chap3_router._CHAP3_PHASE7B_REGISTRY.keys():
        if str(key).endswith(suffix):
            return str(key)
    raise AssertionError(f"missing skill suffix={suffix}")


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"b4_data_org_dup_{uuid.uuid4().hex[:10]}",
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


def test_generator_consecutive_duplicate_guard_level1() -> None:
    skill = _resolve_skill_id("DataOrganizationAndCharts")
    payloads = [generate_for_chap3_skill(skill_id=skill, level=1, seed=i + 1) for i in range(20)]
    qtexts = [str(p.get("question_text", "")) for p in payloads]
    scenarios = [str(p.get("scenario_id", "")) for p in payloads]

    deterministic_choice_count = 0
    open_ended_review_count = 0
    choices_missing_count = 0
    for p in payloads:
        if p.get("runtime_mode") == "deterministic_choice":
            deterministic_choice_count += 1
        q = str(p.get("question_text", ""))
        if any(t in q for t in FORBIDDEN):
            open_ended_review_count += 1
        if not (p.get("choices") or []):
            choices_missing_count += 1
        assert p.get("scenario_id")
        assert p.get("parameter_signature") or p.get("parameters", {}).get("parameter_signature")
        assert p.get("problem_type_id")

    consecutive_duplicate_count = sum(1 for i in range(1, len(qtexts)) if qtexts[i] == qtexts[i - 1])
    consecutive_scenario_dup = sum(1 for i in range(1, len(scenarios)) if scenarios[i] == scenarios[i - 1])

    assert deterministic_choice_count >= 20
    assert open_ended_review_count == 0
    assert choices_missing_count == 0
    assert len(set(qtexts)) >= 8
    assert len(set(scenarios)) >= 6
    assert consecutive_duplicate_count == 0
    assert consecutive_scenario_dup == 0


def test_route_consecutive_duplicate_guard_level1(logged_client) -> None:
    skill = _resolve_skill_id("DataOrganizationAndCharts")
    qtexts = []
    scenarios = []
    for _ in range(20):
        r = logged_client.get(f"/get_next_question?skill={quote(skill)}&level=1")
        assert r.status_code == 200
        data = r.get_json() or {}
        qtexts.append(str(data.get("new_question_text", "")))
        scenarios.append(str(data.get("scenario_id", "")))
        assert data.get("runtime_mode") == "deterministic_choice"
        assert data.get("check_mode") == "deterministic_auto_checked"
        assert data.get("choices")

    assert sum(1 for i in range(1, len(qtexts)) if qtexts[i] == qtexts[i - 1]) == 0
    assert sum(1 for i in range(1, len(scenarios)) if scenarios[i] == scenarios[i - 1]) == 0


def test_no_open_ended_regression_level1() -> None:
    skill = _resolve_skill_id("DataOrganizationAndCharts")
    payloads = [generate_for_chap3_skill(skill_id=skill, level=1, seed=i + 1) for i in range(20)]
    for p in payloads:
        q = str(p.get("question_text", ""))
        for t in FORBIDDEN:
            assert t not in q


def test_choice_contract_and_checker(logged_client) -> None:
    skill = _resolve_skill_id("DataOrganizationAndCharts")
    # Use explicit deterministic problem_type for stable checker assertions.
    r = logged_client.get(
        f"/get_next_question?skill={quote(skill)}&level=1&problem_type=chart_type_selection_by_purpose&gen_seed=1"
    )
    assert r.status_code == 200
    data = r.get_json() or {}
    choices = data.get("choices") or []
    assert len(choices) >= 4

    ok1 = (logged_client.post("/check_answer", json={"answer": "1"}).get_json() or {})
    okA = (logged_client.post("/check_answer", json={"answer": "A"}).get_json() or {})
    bad2 = (logged_client.post("/check_answer", json={"answer": "2"}).get_json() or {})
    assert ok1.get("correct") is True
    assert okA.get("correct") is True
    assert bad2.get("correct") is False
