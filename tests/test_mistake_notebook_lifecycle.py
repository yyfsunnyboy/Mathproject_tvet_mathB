from __future__ import annotations

from app import app
from core.mistake_notebook_service import create_active_mistake, record_active_review_verdict
from models import MistakeNotebookEntry, PracticeAttempt, SkillInfo, User, db


def _attempt(student_id: int, skill_id: str, uid: str, *, correct: bool = False) -> PracticeAttempt:
    row = PracticeAttempt(
        student_id=student_id, skill_id=skill_id, question_uid=uid,
        question_text="題幹", user_answer="0", expected_answer="1",
        is_correct=correct, source="general_practice", problem_type_id="type-a",
    )
    db.session.add(row)
    db.session.flush()
    return row


def test_notebook_deduplicates_question_uid_and_resolves_only_owned_retry() -> None:
    with app.app_context():
        owner = User(username="notebook_lifecycle_owner", password_hash="x", role="student")
        other = User(username="notebook_lifecycle_other", password_hash="x", role="student")
        skill = SkillInfo(skill_id="test_notebook_lifecycle", skill_en_name="test", skill_ch_name="測試", category="test", description="test", gemini_prompt="test")
        db.session.add_all([owner, other, skill]); db.session.flush()
        payload = {"question_text": "題幹", "problem_type_id": "type-a", "component_id": "component-a"}
        first = create_active_mistake(student_id=owner.id, attempt=_attempt(owner.id, skill.skill_id, "same-question"), question=payload, user_answer="0")
        duplicate = create_active_mistake(student_id=owner.id, attempt=_attempt(owner.id, skill.skill_id, "same-question"), question=payload, user_answer="9")
        other_question = create_active_mistake(student_id=owner.id, attempt=_attempt(owner.id, skill.skill_id, "other-question"), question=payload, user_answer="0")
        db.session.flush()
        assert first.id == duplicate.id
        assert first.user_answer == "0"  # attempt value is authoritative over browser value
        assert MistakeNotebookEntry.query.filter_by(student_id=owner.id, resolved_at=None).count() == 2

        retry_wrong = _attempt(owner.id, skill.skill_id, "retry-question")
        recorded, resolved = record_active_review_verdict(mistake_id=first.id, student_id=owner.id, retry_attempt=retry_wrong, current_question=payload, is_correct=False)
        assert (recorded, resolved) == (True, False)
        assert first.retry_count == 1 and first.resolved_at is None

        foreign_retry = _attempt(other.id, skill.skill_id, "foreign-retry", correct=True)
        assert record_active_review_verdict(mistake_id=first.id, student_id=other.id, retry_attempt=foreign_retry, current_question=payload, is_correct=True) == (False, False)

        retry_correct = _attempt(owner.id, skill.skill_id, "retry-question-2", correct=True)
        assert record_active_review_verdict(mistake_id=first.id, student_id=owner.id, retry_attempt=retry_correct, current_question=payload, is_correct=True) == (True, True)
        assert first.retry_count == 2 and first.resolved_attempt_id == retry_correct.id
        assert other_question.resolved_at is None


def test_notebook_groups_all_curricula_without_session_filter() -> None:
    with app.app_context():
        owner = User(username="notebook_curriculum_owner", password_hash="x", role="student")
        skill_a = SkillInfo(skill_id="test_notebook_general", skill_en_name="g", skill_ch_name="普高技能", category="test", description="test", gemini_prompt="test")
        skill_b = SkillInfo(skill_id="test_notebook_vocational", skill_en_name="v", skill_ch_name="技高技能", category="test", description="test", gemini_prompt="test")
        db.session.add_all([owner, skill_a, skill_b]); db.session.flush()
        db.session.add_all([
            MistakeNotebookEntry(student_id=owner.id, source_type="test", curriculum="general", volume="第一冊", chapter="第一章", section="1-1", skill_id=skill_a.skill_id),
            MistakeNotebookEntry(student_id=owner.id, source_type="test", curriculum="vocational", volume="數學B4", chapter="1 統計", section="1-1 資料", skill_id=skill_b.skill_id),
            MistakeNotebookEntry(student_id=owner.id, source_type="test", curriculum="vocational", volume="數學B4", chapter="1 統計", section="1-2 圖表", skill_id=skill_b.skill_id),
        ])
        db.session.commit(); owner_id = owner.id

    client = app.test_client()
    with client.session_transaction() as state:
        state["_user_id"] = str(owner_id); state["_fresh"] = True; state["current_curriculum"] = "general"
    curricula = client.get("/api/mistake-notebook/tree").get_json()["curricula"]
    assert {(row["name"], row["count"]) for row in curricula} == {("general", 1), ("vocational", 2)}
