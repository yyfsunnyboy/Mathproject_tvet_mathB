import pytest
from core.vocational_math_b4.generators.chap3_statistical_measures import (
    sampling_survey_foundation_choice,
    sampling_survey_bias_review_shell,
)
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill
from app import create_app

def test_sampling_survey_foundation_choice_metadata():
    payload = sampling_survey_foundation_choice(
        skill_id="vh_數學B4_SamplingSurvey",
        subskill_id="b4_ch3_sampling_survey_foundation_01",
        seed=42,
    )
    
    assert payload["runtime_mode"] == "deterministic_choice"
    assert payload["check_mode"] == "deterministic_auto_checked"
    assert payload["grading_mode"] == "deterministic"
    assert "requires_teacher_review" not in payload or not payload["requires_teacher_review"]
    
    assert payload["answer_input_type"] == "choice"
    assert "choices" in payload
    assert len(payload["choices"]) >= 4
    
    # Check that answer is one of the choices or represents an index
    answer = payload["answer"]
    assert answer in ["1", "2", "3", "4"]

def test_sampling_survey_router_selection():
    # It should be able to generate deterministic choice question
    payload = generate_for_chap3_skill(
        skill_id="vh_數學B4_SamplingSurvey",
        seed=123,
        problem_type_id="sampling_survey_foundation_identification"
    )
    
    assert payload["problem_type_id"] == "sampling_survey_foundation_identification"
    assert payload["runtime_mode"] == "deterministic_choice"

    # It should still be able to generate review mode for future open ended
    payload_review = generate_for_chap3_skill(
        skill_id="vh_數學B4_SamplingSurvey",
        seed=123,
        problem_type_id="sampling_survey_bias_review"
    )
    
    assert payload_review["problem_type_id"] == "sampling_survey_bias_review"
    assert payload_review["runtime_mode"] == "teacher_review"

@pytest.fixture
def test_client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client

def test_check_answer_api(test_client):
    # Simulate a check answer call for deterministic choice
    payload = sampling_survey_foundation_choice(
        skill_id="vh_數學B4_SamplingSurvey",
        subskill_id="b4_ch3_sampling_survey_foundation_01",
        seed=42,
    )
    
    # This is a unit test approximation of the router logic
    # Assuming practice.py receives correct check_mode, it won't block it with "此題為 AI/Review 判分路徑"
    check_mode = payload.get("check_mode", "")
    assert check_mode == "deterministic_auto_checked"
    assert check_mode not in {
        "ai_judged_free_response",
        "visual_ai_checked",
        "handwriting_ai_checked",
        "review_mode",
    }
