from __future__ import annotations

import uuid
from urllib.parse import quote

import pytest

from app import create_app
from models import User, db
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill


S_BASIC = "vh_數學B4_StatisticalBasicConcepts"
S_SURVEY = "vh_數學B4_SamplingSurvey"
S_METHODS = "vh_數學B4_SamplingMethods"

PT_BASIC = "statistical_basic_concepts_choice"
PT_SURVEY = "sampling_survey_bias_review"
PT_METHODS = "sampling_methods_classification_choice"


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
            username=f"b4_31_boundary_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def test_skill_boundary_no_cross_contamination() -> None:
    p_basic = generate_for_chap3_skill(skill_id=S_BASIC, problem_type_id=PT_BASIC, seed=1, level=1)
    p_survey = generate_for_chap3_skill(skill_id=S_SURVEY, problem_type_id=PT_SURVEY, seed=1, level=1)
    p_methods = generate_for_chap3_skill(skill_id=S_METHODS, problem_type_id=PT_METHODS, seed=1, level=1)

    assert p_basic.get("scenario_family") == "statistical_basic_concepts_boundary_aligned"
    assert p_survey.get("scenario_family") == "sampling_survey_foundation_identification"
    assert p_methods.get("scenario_family") == "sampling_methods_boundary_aligned"

    assert "抽樣方法" not in str(p_basic.get("question_text", ""))
    assert "分層隨機抽樣" not in str(p_survey.get("question_text", ""))
    assert "樣本平均數" not in str(p_methods.get("question_text", ""))


def test_statistical_basic_concepts_fidelity() -> None:
    bad_terms = ["樣本平均數", "母體平均數", "統計量稱為什麼", "參數稱為什麼"]
    good_hit = 0
    for seed in range(1, 12):
        p = generate_for_chap3_skill(skill_id=S_BASIC, problem_type_id=PT_BASIC, seed=seed, level=1)
        q = str(p.get("question_text", ""))
        for b in bad_terms:
            assert b not in q
        if any(k in q for k in ["敘述統計", "統計研究", "普查", "抽查"]):
            good_hit += 1
    assert good_hit >= 6


def test_sampling_survey_fidelity_choice_not_empty() -> None:
    p = generate_for_chap3_skill(skill_id=S_SURVEY, problem_type_id=PT_SURVEY, seed=3, level=1)
    q = str(p.get("question_text", ""))
    assert any(k in q for k in ["學生", "抽出", "樣本", "母群體", "普查", "抽查"])
    assert p.get("choices")
    assert p.get("answer") in {c.split(".")[0] for c in p.get("choices", []) if "." in c}


def test_sampling_methods_fidelity_multi_coverage() -> None:
    seen = set()
    for seed in range(1, 30):
        p = generate_for_chap3_skill(skill_id=S_METHODS, problem_type_id=PT_METHODS, seed=seed, level=1)
        q = str(p.get("question_text", ""))
        if "抽籤" in q or "亂數" in q:
            seen.add("簡單隨機抽樣")
        if "每隔" in q or "間距" in q:
            seen.add("系統抽樣")
        if "分層" in q or "比例" in q:
            seen.add("分層隨機抽樣")
        if "社區" in q or "班級" in q:
            seen.add("部落抽樣")
    assert len(seen) >= 3


@pytest.mark.parametrize(
    ("skill_id", "problem_type_id"),
    [(S_BASIC, PT_BASIC), (S_SURVEY, PT_SURVEY), (S_METHODS, PT_METHODS)],
)
def test_choice_payload_and_check_answer(skill_id, problem_type_id, logged_client) -> None:
    p = generate_for_chap3_skill(skill_id=skill_id, problem_type_id=problem_type_id, seed=9, level=1)
    assert p.get("choices")
    ans = str(p.get("answer"))
    assert any(ans == c.split(".")[0] for c in p.get("choices", []) if "." in c)

    q = logged_client.get(
        f"/get_next_question?skill={quote(skill_id)}&problem_type={problem_type_id}&gen_seed=9&level=1"
    )
    assert q.status_code == 200
    if skill_id == S_SURVEY:
        guarded = logged_client.post("/check_answer", json={"answer": ans}).get_json() or {}
        assert guarded.get("correct") is False
    else:
        ok = logged_client.post("/check_answer", json={"answer": ans}).get_json() or {}
        bad = logged_client.post("/check_answer", json={"answer": "__wrong__"}).get_json() or {}
        assert ok.get("correct") is True
        assert bad.get("correct") is False


def test_localization_all_chinese() -> None:
    forbidden = ["Read", "Choose", "Explain", "Please", "Question", "sample mean", "population mean"]
    for sid, pt in [(S_BASIC, PT_BASIC), (S_SURVEY, PT_SURVEY), (S_METHODS, PT_METHODS)]:
        p = generate_for_chap3_skill(skill_id=sid, problem_type_id=pt, seed=5, level=1)
        text = " ".join(
            [
                str(p.get("question_text", "")),
                str(p.get("explanation", "")),
                " ".join(str(c) for c in p.get("choices", [])),
                str(p.get("textbook_alignment_note", "")),
                str(p.get("source_style_summary", "")),
            ]
        )
        for bad in forbidden:
            assert bad not in text

