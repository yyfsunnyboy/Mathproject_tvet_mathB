from __future__ import annotations

import uuid
from urllib.parse import quote

import pytest

from app import create_app
from models import User, db


S_CHART = "vh_數學B4_StatisticalChartReading"
S_CUM = "vh_數學B4_CumulativeFrequencyTablesAndGraphs"

PT_CHART = "statistical_chart_reading_visibility_review"
PT_CUM = "cumulative_frequency_table_completion_review"


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
            username=f"b4_32_review_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def test_statistical_chart_reading_friendly_route_and_guard(logged_client) -> None:
    q = logged_client.get(f"/get_next_question?skill={quote(S_CHART)}&gen_seed=31&level=1")
    assert q.status_code == 200
    d = q.get_json() or {}
    msg_blob = " ".join(
        [
            str(d.get("message", "")),
            str(d.get("new_question_text", "")),
            str(d.get("context_string", "")),
        ]
    )
    assert "Chap3 skill not enabled in current deterministic runtime" not in msg_blob
    assert "此技能尚未開放自動出題" not in msg_blob
    assert d.get("check_mode") == "review_mode"
    assert d.get("runtime_mode") in {"visibility_only", "teacher_review"}
    assert d.get("grading_mode") in {"visibility_only", "teacher_review"}

    guarded = logged_client.post("/check_answer", json={"answer": "任意作答"}).get_json() or {}
    assert guarded.get("correct") is False
    assert "AI" in str(guarded.get("result", "")) or "教師覆核" in str(guarded.get("result", ""))


def test_cumulative_frequency_table_visual_payload_and_guard(logged_client) -> None:
    q = logged_client.get(
        f"/get_next_question?skill={quote(S_CUM)}&problem_type={PT_CUM}&gen_seed=41&level=1"
    )
    assert q.status_code == 200
    d = q.get_json() or {}
    text = str(d.get("new_question_text", ""))

    if ("下表" in text) or ("補齊累積次數" in text):
        has_visual = bool(d.get("table")) or bool(d.get("visual_aids")) or bool(d.get("image_base64"))
        assert has_visual

    table = d.get("table") or {}
    headers = table.get("headers", [])
    assert "次數" in headers
    assert "累積次數" in headers
    assert d.get("runtime_mode") != "deterministic_short_answer"
    assert d.get("check_mode") in {"review_mode", "handwriting_ai_checked", "visual_ai_checked"}

    guarded = logged_client.post("/check_answer", json={"answer": "任意作答"}).get_json() or {}
    assert guarded.get("correct") is False
    assert "補表與說明" in str(guarded.get("result", "")) or "教師覆核" in str(guarded.get("result", ""))


def test_localization_review_payload_text_is_chinese(logged_client) -> None:
    forbidden = [
        "Please",
        "Chart",
        "Review mode",
        "not enabled",
        "deterministic runtime",
    ]
    for skill, pt in [(S_CHART, PT_CHART), (S_CUM, PT_CUM)]:
        q = logged_client.get(
            f"/get_next_question?skill={quote(skill)}&problem_type={pt}&gen_seed=51&level=1"
        )
        assert q.status_code == 200
        d = q.get_json() or {}
        joined = " ".join(
            [
                str(d.get("message", "")),
                str(d.get("new_question_text", "")),
                str(d.get("table_title", "")),
                str(d.get("context_string", "")),
                str(d.get("inequality_string", "")),
            ]
        )
        table = d.get("table") or {}
        joined += " " + " ".join(str(x) for x in table.get("headers", []))
        joined += " " + " ".join(" ".join(str(c) for c in row) for row in table.get("rows", []))
        for bad in forbidden:
            assert bad not in joined

