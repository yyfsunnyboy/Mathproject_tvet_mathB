# -*- coding: utf-8 -*-
from __future__ import annotations

from app import app
from core.mistake_notebook_notes import (
    LEGACY_UNRECOVERABLE_NOTE,
    UNRECOVERABLE_NOTE_MESSAGE,
)
from models import MistakeNotebookEntry, User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True


def test_known_unrecoverable_note_is_display_normalized_only() -> None:
    with app.app_context():
        user = User(username="notebook_encoding_display", password_hash="x", role="student")
        db.session.add(user)
        db.session.flush()
        entry = MistakeNotebookEntry(student_id=user.id, notes=LEGACY_UNRECOVERABLE_NOTE)
        db.session.add(entry)
        db.session.commit()

        persisted = db.session.get(MistakeNotebookEntry, entry.id)
        assert persisted.notes == LEGACY_UNRECOVERABLE_NOTE
        assert persisted.to_dict()["notes"] == UNRECOVERABLE_NOTE_MESSAGE


def test_new_traditional_chinese_note_round_trips_through_api_and_page() -> None:
    note = "移項時忘記改變正負號，下次先檢查符號。"
    with app.app_context():
        user = User(username="notebook_encoding_write", password_hash="x", role="student")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    client = app.test_client()
    _login(client, user_id)
    response = client.post(
        "/mistake-notebook/add",
        json={"exam_image_path": None, "skill_id": None, "notes": note, "question_data": None},
    )
    assert response.status_code == 200
    assert response.get_json()["success"] is True

    with app.app_context():
        entry = (
            MistakeNotebookEntry.query.filter_by(student_id=user_id)
            .order_by(MistakeNotebookEntry.id.desc())
            .first()
        )
        assert entry is not None
        assert entry.notes == note

    api_response = client.get("/api/mistake-notebook")
    assert api_response.status_code == 200
    assert api_response.get_json()[0]["notes"] == note

    page_response = client.get("/mistake-notebook")
    assert page_response.status_code == 200
    assert "筆記與心得" in page_response.get_data(as_text=True)
