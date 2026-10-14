from __future__ import annotations

from pathlib import Path
import uuid

import pytest

from app import create_app
from core.gencode.runtime_skill_wrapper import check_answer
from core.skill_card_mastery import build_skill_card_mastery
from models import PracticeAttempt, Progress, SkillInfo, TextbookExample, User, db


ROOT = Path(__file__).resolve().parents[1]
STANDARD_TEMPLATE = ROOT / "templates" / "index.html"
ADAPTIVE_TEMPLATE = ROOT / "templates" / "adaptive_practice_v2.html"
SHARED_FLOW = ROOT / "static" / "js" / "practice_correct_answer_flow.js"
FLOW_SKILL = "test_global_unified_correct_flow"


@pytest.fixture()
def flow_app(tmp_path):
    import config as cfg

    db_path = tmp_path / "unified_correct_flow.db"
    previous_uri = cfg.Config.SQLALCHEMY_DATABASE_URI
    cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + db_path.resolve().as_posix()
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            user = User(
                username=f"unified_{uuid.uuid4().hex[:10]}",
                password_hash="x",
                role="student",
            )
            db.session.add(user)
            db.session.add(
                SkillInfo(
                    skill_id=FLOW_SKILL,
                    skill_en_name="Unified correct flow",
                    skill_ch_name="共用答對流程",
                    description="test",
                    gemini_prompt="test",
                    is_active=True,
                )
            )
            db.session.add(
                TextbookExample(
                    skill_id=FLOW_SKILL,
                    source_curriculum="general",
                    source_volume="test",
                    source_chapter="test",
                    source_section="test",
                    source_description="reference",
                    problem_text="x + 1 = 2",
                )
            )
            db.session.commit()
            yield app, user.id
    finally:
        cfg.Config.SQLALCHEMY_DATABASE_URI = previous_uri


def _function_body(source: str, marker: str) -> str:
    start = source.index(marker)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[brace : index + 1]
    raise AssertionError(f"function body not found: {marker}")


def test_active_practice_pages_reuse_one_shared_success_handler() -> None:
    standard = STANDARD_TEMPLATE.read_text(encoding="utf-8")
    adaptive = ADAPTIVE_TEMPLATE.read_text(encoding="utf-8")
    shared_name = "js/practice_correct_answer_flow.js"

    assert shared_name in standard
    assert shared_name in adaptive
    for source in (standard, adaptive):
        body = _function_body(source, "function handleCorrectAnswer")
        assert "PracticeCorrectAnswerFlow.handleCorrectAnswer" in body
        assert "SUCCESS_MESSAGES" not in body


def test_shared_success_waits_for_confirmation_before_next_question() -> None:
    source = SHARED_FLOW.read_text(encoding="utf-8")
    body = _function_body(source, "async function handleCorrectAnswer")

    confirm_position = body.index("await config.confirmMessage(message)")
    next_position = body.index("return config.onConfirm()")
    assert confirm_position < next_position
    assert "setTimeout" not in source
    assert "auto_next" not in source


def test_every_success_message_explicitly_says_answer_is_correct() -> None:
    source = SHARED_FLOW.read_text(encoding="utf-8")
    messages_block = source.split("SUCCESS_MESSAGES", 1)[1].split("]);", 1)[0]
    quoted_messages = [
        line.strip().strip(",").strip('"')
        for line in messages_block.splitlines()
        if line.strip().startswith('"')
    ]
    assert quoted_messages
    assert all("答對" in message for message in quoted_messages)


def test_standard_text_structured_and_drawing_paths_share_success_handler() -> None:
    source = STANDARD_TEMPLATE.read_text(encoding="utf-8")
    submit_body = _function_body(source, "function setupSubmit")
    drawing_body = _function_body(source, "function submitDrawingAnswerFromCanvas")

    assert "buildCheckAnswerPayload(userAnswer)" in submit_body
    assert "isMultiPartQuestion(currentQuestion)" in submit_body
    assert "await handleCorrectAnswer()" in submit_body
    assert "fetch('/check_answer'" in drawing_body
    assert "await handleCorrectAnswer()" in drawing_body


def test_handwriting_recognition_uses_checker_before_success_flow() -> None:
    standard = STANDARD_TEMPLATE.read_text(encoding="utf-8")
    adaptive = ADAPTIVE_TEMPLATE.read_text(encoding="utf-8")
    standard_ai = _function_body(standard, "function setupAIButton")
    adaptive_ai = _function_body(adaptive, "async function analyzeHandwriting")

    assert "submitHandwritingAsAnswer" in standard_ai
    assert "enableHandwritingNextQuestion" not in standard_ai
    assert "fetch(\"/check_answer\"" in adaptive_ai
    assert adaptive_ai.index('fetch("/check_answer"') < adaptive_ai.index("handleCorrectAnswer(submitAttempt)")
    assert "if (grade.correct === true)" in adaptive_ai


def test_standard_handwriting_is_submitted_as_first_class_answer() -> None:
    source = STANDARD_TEMPLATE.read_text(encoding="utf-8")
    body = _function_body(source, "async function submitHandwritingAsAnswer")

    recognition_pos = body.index("/api/practice/ai-check-handwriting")
    checker_pos = body.index("/check_answer")
    correct_pos = body.index("if (grade.correct === true)")
    success_pos = body.index("await handleCorrectAnswer()")
    feedback_pos = body.index("/analyze_handwriting")
    assert recognition_pos < checker_pos < correct_pos < success_pos < feedback_pos
    assert "buildCheckAnswerPayload(normalizedAnswer)" in body
    assert "updateStreak(grade.correct === true, grade.consecutive_correct, grade.pass_target)" in body


def test_wrong_handwriting_stays_on_question_and_requests_socratic_feedback() -> None:
    standard = STANDARD_TEMPLATE.read_text(encoding="utf-8")
    adaptive = ADAPTIVE_TEMPLATE.read_text(encoding="utf-8")
    standard_body = _function_body(standard, "async function submitHandwritingAsAnswer")
    adaptive_body = _function_body(adaptive, "async function analyzeHandwriting")

    assert "/analyze_handwriting" in standard_body
    assert "/analyze_handwriting" in adaptive_body
    assert standard_body.index("if (grade.correct === true)") < standard_body.index("/analyze_handwriting")
    assert adaptive_body.index("if (grade.correct === true)") < adaptive_body.index("/analyze_handwriting")


def test_blank_and_in_progress_never_reach_check_answer() -> None:
    standard = STANDARD_TEMPLATE.read_text(encoding="utf-8")
    adaptive = ADAPTIVE_TEMPLATE.read_text(encoding="utf-8")
    for body in (
        _function_body(standard, "async function submitHandwritingAsAnswer"),
        _function_body(adaptive, "async function analyzeHandwriting"),
    ):
        blank_pos = body.index("completion_state")
        in_progress_pos = body.index("in_progress", blank_pos)
        checker_pos = body.index("/check_answer")
        assert blank_pos < checker_pos
        assert in_progress_pos < checker_pos
        assert "return;" in body[blank_pos:checker_pos]


@pytest.mark.parametrize(
    ("answer_type", "checker", "equivalence", "user_answer", "correct_answer"),
    [
        ("short_answer", "text_checker", "exact_text", "第二象限", "第二象限"),
        ("structured_text", "text_checker", "exact_text", "向右1,向上2", "向右1,向上2"),
        ("expression", "expression_equivalence_checker", "expression_equivalence", "sqrt(20)", "2*sqrt(5)"),
        ("equation", "equation_checker", "equation_equivalent", "2*x+2=0", "x+1=0"),
        (
            "multi_part",
            "multi_part_answer_checker",
            "multi_part_answer",
            {"slope": "2", "equation": "y=2*x+1"},
            {"slope": "2", "equation": "y=2*x+1"},
        ),
    ],
)
def test_authoritative_answer_contract_accepts_supported_correct_types(
    answer_type: str,
    checker: str,
    equivalence: str,
    user_answer: object,
    correct_answer: object,
) -> None:
    payload = {
        "answer_type": answer_type,
        "checker": checker,
        "equivalence": equivalence,
        "answer_contract": {
            "answer_type": answer_type,
            "checker": checker,
            "answer_equivalence": equivalence,
        },
    }
    if answer_type == "multi_part":
        payload["answer_contract"]["parts"] = [
            {
                "key": "slope",
                "checker": "numeric_checker",
                "equivalence_type": "numeric_exact",
            },
            {
                "key": "equation",
                "checker": "equation_checker",
                "equivalence_type": "equation_equivalent",
            },
        ]
    assert check_answer(user_answer, correct_answer, payload=payload) is True


def test_wrong_answer_does_not_enter_success_handler_branch() -> None:
    source = STANDARD_TEMPLATE.read_text(encoding="utf-8")
    submit_body = _function_body(source, "function setupSubmit")
    completion_flow = submit_body.split(
        "updateStreak(data.correct, data.consecutive_correct, data.pass_target);", 1
    )[1]
    success_branch, wrong_branch = completion_flow.split("// [Phase 6]", 1)

    assert "handleCorrectAnswer" in success_branch
    assert "return;" in success_branch
    assert "handleCorrectAnswer" not in wrong_branch
    assert "loadQuestion" not in wrong_branch


def test_correct_checker_result_records_progress_without_waiting_for_ai(flow_app, monkeypatch) -> None:
    app, user_id = flow_app

    def fail_if_ai_is_called(*_args, **_kwargs):
        raise TimeoutError("AI must not run on authoritative correct")

    monkeypatch.setattr("core.routes.practice.diagnose_error", fail_if_ai_is_called)
    client = app.test_client()
    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True
        session["current_data"] = {
            "skill": FLOW_SKILL,
            "skill_id": FLOW_SKILL,
            "question_text": "解 x + 1 = 2",
            "problem_type_id": "global_equation_test",
            "answer_type": "equation",
            "checker": "equation_checker",
            "equivalence": "equation_equivalent",
            "correct_answer": "x=1",
            "answer": "x=1",
            "answer_contract": {
                "answer_type": "equation",
                "checker": "equation_checker",
                "answer_equivalence": "equation_equivalent",
            },
        }

    response = client.post("/check_answer", json={"answer": "2*x=2"})
    data = response.get_json() or {}
    assert response.status_code == 200
    assert data.get("correct") is True

    with app.app_context():
        attempt = PracticeAttempt.query.filter_by(student_id=user_id, skill_id=FLOW_SKILL).one()
        progress = db.session.get(Progress, (user_id, FLOW_SKILL))
        mastery = build_skill_card_mastery(
            student_id=user_id,
            skill_ids=[FLOW_SKILL],
            current_streak_by_skill={FLOW_SKILL: progress.consecutive_correct},
        )[FLOW_SKILL]
        assert attempt.is_correct is True
        assert progress.consecutive_correct == 1
        assert mastery["attempt_count"] == 1
        assert mastery["recent_accuracy"] == 100.0
        assert mastery["card_status"] == "mastered"
