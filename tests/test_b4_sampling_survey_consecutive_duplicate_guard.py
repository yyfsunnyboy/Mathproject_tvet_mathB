from __future__ import annotations

import uuid
from urllib.parse import quote

import pytest

from app import create_app
from core.vocational_math_b4.services import question_router as chap3_router
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill
from models import User, db


FORBIDDEN_OPEN_ENDED = [
    "請說明",
    "請討論",
    "請簡述",
    "可能有哪些偏誤",
    "是否具有代表性",
    "提出改善方式",
]


def _resolve_skill_id(suffix: str) -> str:
    for key in chap3_router._CHAP3_PHASE7B_REGISTRY.keys():
        if str(key).endswith(suffix):
            return str(key)
    raise AssertionError(f"Missing skill with suffix={suffix}")


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"b4_sampling_survey_dup_guard_{uuid.uuid4().hex[:10]}",
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
    skill_id = _resolve_skill_id("SamplingSurvey")
    payloads = [generate_for_chap3_skill(skill_id=skill_id, level=1, seed=i + 1) for i in range(20)]

    qtexts = [str(p.get("question_text", "")) for p in payloads]
    scenario_ids = [str(p.get("scenario_id", "")) for p in payloads]
    det_count = sum(1 for p in payloads if p.get("runtime_mode") == "deterministic_choice")
    open_count = sum(1 for q in qtexts if any(t in q for t in FORBIDDEN_OPEN_ENDED))
    consecutive_dup = sum(1 for i in range(1, len(qtexts)) if qtexts[i] == qtexts[i - 1])
    consecutive_sid_dup = sum(1 for i in range(1, len(scenario_ids)) if scenario_ids[i] == scenario_ids[i - 1])

    assert det_count == 20
    assert open_count == 0
    assert len(set(qtexts)) >= 8
    assert len(set(scenario_ids)) >= 8
    assert consecutive_dup == 0
    assert consecutive_sid_dup == 0


def test_route_consecutive_duplicate_guard_level1(logged_client) -> None:
    skill_id = _resolve_skill_id("SamplingSurvey")
    qtexts = []
    scenario_ids = []

    for _ in range(20):
        resp = logged_client.get(f"/get_next_question?skill={quote(skill_id)}&level=1")
        assert resp.status_code == 200
        data = resp.get_json() or {}
        qtexts.append(str(data.get("new_question_text", "")))
        scenario_ids.append(str(data.get("scenario_id", "")))
        assert data.get("runtime_mode") == "deterministic_choice"
        assert data.get("check_mode") == "deterministic_auto_checked"

    consecutive_dup = sum(1 for i in range(1, len(qtexts)) if qtexts[i] == qtexts[i - 1])
    consecutive_sid_dup = sum(1 for i in range(1, len(scenario_ids)) if scenario_ids[i] == scenario_ids[i - 1])
    assert consecutive_dup == 0
    assert consecutive_sid_dup == 0


def test_level1_no_open_ended_regression() -> None:
    skill_id = _resolve_skill_id("SamplingSurvey")
    payloads = [generate_for_chap3_skill(skill_id=skill_id, level=1, seed=i + 1) for i in range(20)]
    for p in payloads:
        q = str(p.get("question_text", ""))
        for token in FORBIDDEN_OPEN_ENDED:
            assert token not in q
        assert p.get("runtime_mode") == "deterministic_choice"


def test_choice_contract_regression() -> None:
    skill_id = _resolve_skill_id("SamplingSurvey")
    payloads = [generate_for_chap3_skill(skill_id=skill_id, level=1, seed=i + 1) for i in range(20)]
    for p in payloads:
        choices = p.get("choices") or []
        assert isinstance(choices, list) and len(choices) >= 4
        ans = str(p.get("answer", "")).strip()
        codes = {str(c).split(".", 1)[0].strip() for c in choices}
        assert ans in codes


def test_screenshot_regression_with_checker(logged_client) -> None:
    skill_id = _resolve_skill_id("SamplingSurvey")
    found_seed = None
    for s in range(1, 300):
        p = generate_for_chap3_skill(skill_id=skill_id, level=1, seed=s)
        q = str(p.get("question_text", ""))
        if "5000 位機車族" in q and "250 位" in q and "樣本" in q:
            found_seed = s
            break
    assert found_seed is not None

    resp = logged_client.get(
        f"/get_next_question?skill={quote(skill_id)}&problem_type=sampling_survey_foundation_identification&gen_seed={found_seed}&level=1"
    )
    assert resp.status_code == 200

    ok3 = (logged_client.post("/check_answer", json={"answer": "3"}).get_json() or {})
    okC = (logged_client.post("/check_answer", json={"answer": "C"}).get_json() or {})
    okc = (logged_client.post("/check_answer", json={"answer": "c"}).get_json() or {})
    bad1 = (logged_client.post("/check_answer", json={"answer": "1"}).get_json() or {})
    bad2 = (logged_client.post("/check_answer", json={"answer": "2"}).get_json() or {})
    bad4 = (logged_client.post("/check_answer", json={"answer": "4"}).get_json() or {})

    assert ok3.get("correct") is True
    assert okC.get("correct") is True
    assert okc.get("correct") is True
    assert bad1.get("correct") is False
    assert bad2.get("correct") is False
    assert bad4.get("correct") is False
    for item in (ok3, okC, okc, bad1, bad2, bad4):
        msg = str(item.get("result", ""))
        assert "模組載入錯誤" not in msg
        assert "AI/Review" not in msg
