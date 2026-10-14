"""Browser coverage for the existing local practice question flow."""
from __future__ import annotations

import threading

import pytest
from flask_login import UserMixin
from werkzeug.serving import make_server

from app import app, login_manager
from models import PracticeAttempt, Progress, StudentAbility, db

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright


def _session_cookie(client):
    with client.session_transaction() as session:
        return app.session_interface.get_signing_serializer(app).dumps(dict(session))


@pytest.mark.parametrize("skill_id", [
    "vh_數學B1_AbsoluteValue",
    "vh_數學B2_AngleMeasurementAndConversion",
])
@pytest.mark.parametrize("guest", [True, False])
def test_local_practice_full_flow_preserves_session(monkeypatch, guest, skill_id):
    class Student(UserMixin):
        id = -2
        username = "browser_test_student"
        role = "student"
        is_admin = False

    monkeypatch.setattr(login_manager, "_user_callback", lambda _id: Student())
    app.config.update(TESTING=True)
    with app.app_context():
        before = tuple(db.session.query(model).count() for model in (
            PracticeAttempt, Progress, StudentAbility,
        ))
    with app.test_client() as client:
        if not guest:
            with client.session_transaction() as session:
                session["_user_id"] = str(Student.id)
                session["_fresh"] = True
                session["current_curriculum"] = "vocational"
        cookie = _session_cookie(client) if not guest else None

    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            if cookie:
                context.add_cookies([{
                    "name": app.config.get("SESSION_COOKIE_NAME", "session"),
                    "value": cookie, "domain": "127.0.0.1", "path": "/",
                }])
            page = context.new_page()
            question_responses = []
            ai_requests = []
            page.on("response", lambda response: question_responses.append(response)
                    if "/get_next_question?" in response.url else None)
            page.on("request", lambda request: ai_requests.append(request)
                    if request.method == "POST" and any(path in request.url for path in (
                        "/chat_ai", "/analyze_handwriting", "/api/practice/ai-check-handwriting",
                    )) else None)
            base = f"http://127.0.0.1:{server.server_port}"
            if guest:
                page.goto(f"{base}/review-demo", wait_until="domcontentloaded")
                assert page.url.endswith("/teacher_dashboard")
                page.goto(f"{base}/dashboard", wait_until="domcontentloaded")
                assert "展示學生" in page.locator("body").inner_text()
            page.goto(
                f"{base}/practice/{skill_id}",
                wait_until="domcontentloaded",
            )
            if guest:
                assert page.locator("[data-guest-demo-warning]").inner_text() == (
                    "此為展示頁面，AI 助教與 AI 批改功能需登入後使用。"
                )
                assert "此為展示頁面，AI 助教功能請登入後使用。" in page.locator("#chat-history").inner_text()
                page.locator("#chat-input").fill("測試")
                page.locator("#chat-send-button").click()
                page.locator("#analyze-handwriting-button").click()
                assert "此為展示頁面，請登入後再行操作。" in page.locator("#result-display").inner_text()
                assert "連線發生錯誤" not in page.locator("#chat-history").inner_text()
                assert not ai_requests
            else:
                assert page.locator("[data-guest-demo-warning]").count() == 0
                assert "你好！有問題問我～" in page.locator("#chat-history").inner_text()
            if guest:
                browser_session = next(c["value"] for c in context.cookies()
                                       if c["name"] == app.config.get("SESSION_COOKIE_NAME", "session"))
                assert app.session_interface.get_signing_serializer(app).loads(browser_session)["guest_demo"] is True
            page.wait_for_function("document.querySelector('#question-text')?.textContent && !document.querySelector('#question-text').textContent.includes('載入題目中')")
            first = page.locator("#question-text").inner_text()
            page.locator("#next-question-btn").click()
            page.wait_for_function("document.querySelector('#question-text')?.textContent && !document.querySelector('#question-text').textContent.includes('載入題目中')")
            second = page.locator("#question-text").inner_text()
            assert first and second
            assert "出題失敗" not in second
            assert len(question_responses) >= 2
            assert all(response.status == 200 for response in question_responses[:2])
            assert all(response.headers.get("content-type", "").startswith("application/json")
                       for response in question_responses[:2])
            assert all(response.json().get("route_source") == "gencode_wrapper"
                       for response in question_responses[:2])
            if guest:
                browser_session = next(c["value"] for c in context.cookies()
                                       if c["name"] == app.config.get("SESSION_COOKIE_NAME", "session"))
                assert app.session_interface.get_signing_serializer(app).loads(browser_session)["guest_demo"] is True
                assert page.request.get(f"{base}/api/runtime_ai_status").status == 403
            browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)
    with app.app_context():
        after = tuple(db.session.query(model).count() for model in (
            PracticeAttempt, Progress, StudentAbility,
        ))
    assert after == before
