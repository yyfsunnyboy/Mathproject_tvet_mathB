"""PRACTICE_MCQ_CHOICE_IDENTITY_GATE

generate
  -> store the current question
  -> retrieve that stored question
  -> browser-visible A/B/C/D
  -> submit the visible letter
  -> backend checker

The letter, the stored choice value, and the semantic option stay the same
record. Chapter 3 can reuse the same cases by adding a (skill, component) row.
"""
from __future__ import annotations

import importlib
import os

import pytest

os.environ.setdefault("ADV_RAG_EAGER_INIT", "0")

from tests.test_b3_ch2_submit_checker_gate import (  # noqa: E402
    FIXTURE_PASSWORD,
    fetch_question,
    submit_answer,
)


@pytest.fixture(scope="module")
def auth_client(tmp_path_factory):
    import config
    from werkzeug.security import generate_password_hash

    db_path = tmp_path_factory.mktemp("mcq_identity") / "practice_mcq_identity.db"
    db_uri = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    patch = pytest.MonkeyPatch()
    patch.setattr(config.Config, "SQLALCHEMY_DATABASE_URI", db_uri)

    from app import create_app
    from models import User, db

    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.app_context():
        user = User(
            username="practice_mcq_identity",
            password_hash=generate_password_hash(FIXTURE_PASSWORD),
            role="student",
        )
        db.session.add(user)
        db.session.commit()
    client = app.test_client()
    login = client.post(
        "/login",
        data={"username": "practice_mcq_identity", "password": FIXTURE_PASSWORD},
        follow_redirects=False,
    )
    assert login.status_code in {302, 303}
    try:
        yield client
    finally:
        with app.app_context():
            db.session.remove()
            db.engine.dispose()
        patch.undo()

CASES = (
    ("b3_ch2", "vh_數學B3_SubSection_2_1_1", "src_12032"),
    ("b3_ch1", "vh_數學B3_SubSection_1_1_2", "src_11951"),
    ("b2", "vh_數學B2_SubSection_4_1_1", "src_11886"),
)


def _pairs(choices: list) -> list[tuple[str, str]]:
    found = []
    for index, choice in enumerate(choices or []):
        label = str(choice.get("label") or "ABCD"[index]).strip().upper()
        value = str(choice.get("value") or "").strip()
        found.append((label, value))
    return found


def _visible_letter(question: dict) -> str:
    answer = str(question.get("answer") or question.get("correct_answer") or "").strip().upper()
    assert len(answer) == 1 and answer in "ABCD", answer
    return answer


def test_stored_choice_value_survives_retrieve_and_grading_refresh():
    from core.gencode.answer_payload import refresh_runtime_question_session
    from core.practice_question_store import slim_payload_for_store

    for chapter, skill_id, component_id in CASES:
        module = importlib.import_module(f"skills.{skill_id}")
        letters = set()
        for seed in (1, 2, 3):
            generated = module.generate(level=1, seed=seed, component_id=component_id)
            generated["question_uid"] = f"mcq-identity-{chapter}-{seed}"
            visible = _pairs(generated.get("choices") or [])
            letter = _visible_letter(generated)
            letters.add(letter)
            semantic = str(generated.get("display_answer") or generated.get("semantic_answer") or "")
            matched = next(value for label, value in visible if label == letter)
            assert matched, (chapter, visible)
            if semantic and semantic.upper() not in "ABCD":
                assert semantic in matched or matched in semantic or semantic in str(
                    next(c for c in generated["choices"] if str(c.get("label")).upper() == letter)
                ), (chapter, semantic, matched)

            stored = slim_payload_for_store(
                generated, skill_id=skill_id, question_uid=generated["question_uid"]
            )
            stored_pairs = _pairs(stored.get("choices") or [])
            assert stored_pairs == visible, (chapter, visible, stored_pairs)
            retrieved = refresh_runtime_question_session(stored, skill_id=skill_id)
            assert _pairs(retrieved.get("choices") or []) == visible, chapter
            assert _visible_letter(retrieved) == letter, chapter
        assert len(letters) >= 1, chapter


@pytest.mark.parametrize("chapter,skill_id,component_id", CASES)
def test_visible_letter_matches_checker_after_store(auth_client, chapter, skill_id, component_id):
    client = auth_client
    letters = set()
    for seed in (1, 2):
        question = fetch_question(client, skill=skill_id, component_id=component_id, seed=seed)
        letter = _visible_letter(question)
        letters.add(letter)
        choices = question.get("choices") or []
        matched = None
        for index, choice in enumerate(choices):
            label = str(choice.get("label") or "ABCD"[index]).strip().upper()
            if label == letter:
                matched = choice
                break
        assert matched is not None, (chapter, letter, choices)
        value = str(matched.get("value") or matched.get("text") or "")
        semantic = str(question.get("display_answer") or question.get("semantic_answer") or "")
        if semantic and semantic.upper() not in "ABCD":
            compact = value.replace(" ", "").replace("$", "").replace("\\", "")
            assert semantic.replace(" ", "") in compact or semantic in value, (chapter, semantic, value)
        status, payload = submit_answer(client, question, letter)
        assert status == 200 and payload.get("correct") is True, (chapter, letter, status, payload)
        question = fetch_question(client, skill=skill_id, component_id=component_id, seed=seed)
        letter = _visible_letter(question)
        wrong = next(item for item in "ABCD" if item != letter)
        status, payload = submit_answer(client, question, wrong)
        assert status == 200 and payload.get("correct") is False, (chapter, wrong, status, payload)
    assert len(letters) >= 1
