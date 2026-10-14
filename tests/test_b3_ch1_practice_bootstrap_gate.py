# -*- coding: utf-8 -*-
"""B3 Chapter 1 practice bootstrap gate (extends shared contract)."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from urllib.parse import quote

import pytest

COVERAGE = json.loads(
    Path("reports/b3_ch1_family_coverage.json").read_text(encoding="utf-8")
)
B3_CH1_SKILLS = [row["skill_id"] for row in COVERAGE["skill_summary"]]


@pytest.mark.parametrize("skill_id", B3_CH1_SKILLS)
def test_b3_ch1_practice_bootstrap(skill_id: str) -> None:
    from app import create_app
    from models import User, db

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"b3boot_{uuid.uuid4().hex[:8]}",
            password_hash="x",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id

    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True

    page = client.get(f"/practice/{quote(skill_id)}")
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    assert "function buildMultiPartFieldGroups" in html
    assert "def buildMultiPartFieldGroups" not in html

    resp = client.get(f"/get_next_question?skill={quote(skill_id)}&level=1")
    data = resp.get_json(silent=True) or {}
    q = str(data.get("question_text") or data.get("new_question_text") or "").strip()
    assert resp.status_code == 200, data
    assert not data.get("error"), data.get("error")
    assert q, f"empty question for {skill_id}"

    resp2 = client.get(f"/get_next_question?skill={quote(skill_id)}&level=1")
    data2 = resp2.get_json(silent=True) or {}
    q2 = str(data2.get("question_text") or "").strip()
    assert resp2.status_code == 200 and q2 and not data2.get("error")
