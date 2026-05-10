"""Tests for B4 Chapter 3 Phase 7D Dispersion Measures Deterministic Batch."""

import pytest
import urllib.parse
from flask import url_for
from app import app
from models import db, User

from core.vocational_math_b4.services.question_router import generate_for_chap3_skill
from core.vocational_math_b4.adaptive.b4_chapter3_phase7b_allowlist import (
    B4_CHAPTER3_PHASE7B_ALLOWLIST,
    is_b4_chapter3_phase7b_deterministic_skill,
    is_b4_chapter3_skill_not_enabled,
)
from core.vocational_math_b4.domain.b4_validators import (
    validate_no_unfilled_placeholder,
    check_integer_answer,
    check_rational_answer,
)
from werkzeug.security import generate_password_hash

# Test User
TEST_USER_USERNAME = "b4_chap3_7d_test_user"
TEST_USER_PASSWORD = "password123"

@pytest.fixture(scope="module")
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["LOGIN_DISABLED"] = True
    with app.test_client() as client:
        with app.app_context():
            user = db.session.query(User).filter_by(username=TEST_USER_USERNAME).first()
            if not user:
                user = User(
                    username=TEST_USER_USERNAME,
                    password_hash=generate_password_hash(TEST_USER_PASSWORD),
                    email="b4_chap3_7d_test@example.com",
                    role="student"
                )
                db.session.add(user)
                db.session.commit()
            
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
            
            yield client

def test_generator_validity_multiple_seeds():
    """Verify generators produce valid payload across multiple seeds without placeholders."""
    skill_id = "vh_數學B4_DispersionMeasures"
    for seed in range(10):
        payload = generate_for_chap3_skill(skill_id=skill_id, seed=seed)
        
        assert payload["skill_id"] == skill_id
        assert "problem_type_id" in payload
        assert payload["answer_type"] in ["integer", "rational_fraction"]
        assert payload["answer"] == payload["correct_answer"]
        assert payload["explanation"].strip() != ""
        
        validate_no_unfilled_placeholder(payload["question_text"])
        validate_no_unfilled_placeholder(payload["explanation"])
        
        assert "handwriting" not in payload["answer_type"]
        assert "ai_judged" not in payload["answer_type"]
        
        # Checker test
        ans = str(payload["correct_answer"])
        if payload["answer_type"] == "integer":
            assert check_integer_answer(ans, int(ans))
        else:
            from fractions import Fraction
            if "/" in ans:
                num, den = map(int, ans.split("/"))
            else:
                f = Fraction(str(ans))
                num, den = f.numerator, f.denominator
            assert check_rational_answer(ans, num, den, allow_decimal=True, validate_probability_range=False)

def test_generator_scenario_diversity():
    """Verify that multiple scenarios are generated for the dispersion measures generators."""
    from core.vocational_math_b4.generators.chap3_statistical_measures import (
        range_basic_numeric,
        percentile_basic_numeric,
        quartile_basic_numeric,
        interquartile_range_basic
    )
    
    generators = [
        range_basic_numeric,
        percentile_basic_numeric,
        quartile_basic_numeric,
        interquartile_range_basic
    ]
    
    for gen in generators:
        scenarios_seen = set()
        for seed in range(50):
            payload = gen(skill_id="test", subskill_id="test", seed=seed)
            if "scenario" in payload["parameters"]:
                scenarios_seen.add(payload["parameters"]["scenario"])
        
        # Each generator should have at least 3 scenarios now
        assert len(scenarios_seen) >= 3, f"{gen.__name__} only produced scenarios: {scenarios_seen}"

def test_router_and_allowlist():
    """Verify router and allowlist integration for Phase 7D."""
    skill_id = "vh_數學B4_DispersionMeasures"
    assert is_b4_chapter3_phase7b_deterministic_skill(skill_id)
    assert not is_b4_chapter3_skill_not_enabled(skill_id)

def test_practice_route_encoded_decoded(client):
    """Verify practice entry accepts both encoded and decoded skill_ids."""
    skill_id = "vh_數學B4_DispersionMeasures"
    encoded_skill = urllib.parse.quote(skill_id)
    
    # Decoded
    resp1 = client.get(f"/practice?skill={skill_id}")
    assert resp1.status_code == 200
    
    # Encoded
    resp2 = client.get(f"/practice?skill={encoded_skill}")
    assert resp2.status_code == 200
    
    # Path based
    resp3 = client.get(f"/practice/{encoded_skill}")
    assert resp3.status_code == 200

def test_get_next_question_and_check_answer(client):
    """Verify full loop: get_next_question -> check_answer."""
    skill_id = "vh_數學B4_DispersionMeasures"
    encoded_skill = urllib.parse.quote(skill_id)
    
    resp = client.get(f"/get_next_question?skill={encoded_skill}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["new_question_text"]
    assert "problem_type_id" in data
    
    with client.session_transaction() as sess:
        current_data = sess.get('current_question_data', {})
        if not current_data:
            current_data = sess.get("skill_contexts", {}).get(skill_id, {})
        correct_ans = current_data.get("correct_answer", "0")
        
    check_resp = client.post("/check_answer", json={"answer": str(correct_ans)})
    assert check_resp.status_code == 200
    check_data = check_resp.get_json()
    assert "correct" in check_data

def test_unsupported_skill_friendly_error(client):
    """Verify unsupported skill returns friendly error."""
    skill_id = "vh_數學B4_StatisticalChartReading"
    resp = client.get(f"/get_next_question?skill={skill_id}")
    assert resp.status_code == 422
    data = resp.get_json()
    assert "error" in data
    assert "此技能尚未開放自動出題" in data["error"]
