from __future__ import annotations

from datetime import datetime, timedelta

from app import app
from core.mistake_notebook_service import create_active_mistake, resolve_active_mistake
from models import MistakeNotebookEntry, PracticeAttempt, SkillCurriculum, SkillInfo, User, db


SKILL_A = "test_notebook_active_a"
SKILL_B = "test_notebook_active_b"
SKILL_C = "test_notebook_active_c"


def _login(client, user_id: int) -> None:
    with client.session_transaction() as state:
        state["_user_id"] = str(user_id)
        state["_fresh"] = True
        state["current_curriculum"] = "test_notebook_curriculum"


def _skill(skill_id: str, name: str) -> None:
    if db.session.get(SkillInfo, skill_id) is None:
        db.session.add(SkillInfo(
            skill_id=skill_id, skill_en_name=name, skill_ch_name=name,
            category="test", description="test", gemini_prompt="test",
        ))


def _curriculum(skill_id: str, volume: str, chapter: str, section: str) -> None:
    if not SkillCurriculum.query.filter_by(skill_id=skill_id, curriculum="test_notebook_curriculum").first():
        db.session.add(SkillCurriculum(
            skill_id=skill_id, curriculum="test_notebook_curriculum", grade=1,
            volume=volume, chapter=chapter, section=section, display_order=1,
        ))


def _attempt(student_id: int, skill_id: str, correct: bool = False) -> PracticeAttempt:
    row = PracticeAttempt(
        student_id=student_id, skill_id=skill_id, question_text="$x+1=2$",
        user_answer="0", expected_answer="1", is_correct=correct,
        source="general_practice", problem_type_id="type-a",
    )
    db.session.add(row)
    db.session.flush()
    return row


def test_active_notebook_groups_owned_rows_and_resolves_one_record() -> None:
    with app.app_context():
        owner = User(username="notebook_active_owner", password_hash="x", role="student")
        other = User(username="notebook_active_other", password_hash="x", role="student")
        db.session.add_all([owner, other])
        _skill(SKILL_A, "技能 A"); _skill(SKILL_B, "技能 B"); _skill(SKILL_C, "技能 C")
        db.session.flush()
        _curriculum(SKILL_A, "第一冊", "第 1 章", "1-1"); _curriculum(SKILL_B, "第一冊", "第 1 章", "1-2"); _curriculum(SKILL_C, "第二冊", "第 3 章", "3-1")
        db.session.flush()
        payload = {"question_text": "求 $x$", "problem_type_id": "type-a", "component_id": "component_1", "difficulty": 1}
        e1 = create_active_mistake(student_id=owner.id, attempt=_attempt(owner.id, SKILL_A), question=payload, user_answer="0")
        e2 = create_active_mistake(student_id=owner.id, attempt=_attempt(owner.id, SKILL_A), question=payload, user_answer="0")
        e3 = create_active_mistake(student_id=owner.id, attempt=_attempt(owner.id, SKILL_B), question=payload, user_answer="0")
        e4 = create_active_mistake(student_id=owner.id, attempt=_attempt(owner.id, SKILL_C), question=payload, user_answer="0")
        e5 = create_active_mistake(student_id=owner.id, attempt=_attempt(owner.id, SKILL_C), question=payload, user_answer="0")
        foreign = create_active_mistake(student_id=other.id, attempt=_attempt(other.id, SKILL_A), question=payload, user_answer="0")
        e1.created_at = datetime.utcnow() - timedelta(days=2)
        e2.created_at = datetime.utcnow() - timedelta(days=1)
        e3.created_at = datetime.utcnow() - timedelta(hours=12)
        e4.created_at = datetime.utcnow() - timedelta(hours=4)
        e5.created_at = datetime.utcnow() - timedelta(hours=1)
        db.session.commit()
        owner_id, other_id, e1_id, foreign_id = owner.id, other.id, e1.id, foreign.id

    client = app.test_client(); _login(client, owner_id)
    curricula = client.get("/api/mistake-notebook/tree").get_json()["curricula"]
    assert [(item["name"], item["count"]) for item in curricula] == [("test_notebook_curriculum", 5)]
    tree = curricula[0]["volumes"]
    assert [(item["name"], item["count"]) for item in tree] == [("第二冊", 2), ("第一冊", 3)]
    assert tree[1]["chapters"][0]["sections"][0]["skills"][0]["count"] == 1
    leaf_key = tree[0]["chapters"][0]["sections"][0]["skills"][0]["key"]
    entries = client.get("/api/mistake-notebook/entries", query_string={"key": leaf_key}).get_json()["entries"]
    assert len(entries) == 2
    assert all(entry["student_wrong_answer"] == "0" for entry in entries)

    with app.app_context():
        completed = _attempt(owner_id, SKILL_A, correct=True)
        assert resolve_active_mistake(mistake_id=e1_id, student_id=owner_id, resolved_attempt=completed)
        assert not resolve_active_mistake(mistake_id=foreign_id, student_id=owner_id, resolved_attempt=completed)
        db.session.commit()
        assert db.session.get(MistakeNotebookEntry, e1_id).resolved_at is not None

    tree_after = client.get("/api/mistake-notebook/tree").get_json()["curricula"]
    assert sum(item["count"] for item in tree_after) == 4
    assert client.get(f"/mistake-notebook/review/{foreign_id}").location.endswith("/mistake-notebook")
