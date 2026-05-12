from __future__ import annotations

import uuid
from urllib.parse import quote

import pytest

from app import create_app
from core.vocational_math_b4.generators.chap3_statistical_measures import (
    STATISTICAL_BASIC_CONCEPT_SCENARIOS,
)
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill
from models import User, db


S_BASIC = "vh_?詨飛B4_StatisticalBasicConcepts"
PT_BASIC = "statistical_basic_concepts_choice"


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
            username=f"b4_sbc_diversity_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def _choice_codes(choices: list[str]) -> set[str]:
    return {str(c).split(".", 1)[0].strip() for c in choices if "." in str(c)}


def _wrong_choice(answer: str) -> str:
    return next(c for c in ("1", "2", "3", "4") if c != answer)


def test_scenario_pool_size_and_required_ids() -> None:
    scenario_ids = {str(s["scenario_id"]) for s in STATISTICAL_BASIC_CONCEPT_SCENARIOS}
    assert len(scenario_ids) >= 8
    assert {
        "descriptive_statistics_identification",
        "inferential_statistics_identification",
        "statistics_process_collect_data",
        "statistics_process_organize_data",
        "statistics_process_present_data",
        "statistics_process_analyze_data",
        "statistics_process_interpret_data",
        "census_vs_sample_survey_census",
        "census_vs_sample_survey_sample",
        "statistics_purpose_identification",
    }.issubset(scenario_ids)


def test_repeated_generation_diversity_no_consecutive_duplicate() -> None:
    payloads = [
        generate_for_chap3_skill(skill_id=S_BASIC, problem_type_id=PT_BASIC, seed=i, level=1)
        for i in range(20)
    ]
    question_texts = [str(p["question_text"]) for p in payloads]
    scenario_ids = [str(p["scenario_id"]) for p in payloads]

    assert len(set(question_texts)) >= 6
    assert len(set(scenario_ids)) >= 6
    assert (1 - len(set(question_texts)) / len(question_texts)) <= 0.5
    assert all(a != b for a, b in zip(question_texts, question_texts[1:]))


def test_skill_boundary_stays_in_3_1_basic_concepts() -> None:
    forbidden = [
        "簡單隨機抽樣",
        "系統抽樣",
        "分層抽樣",
        "集群抽樣",
        "部落抽樣",
        "母群體",
        "樣本數",
        "樣本平均數",
        "母體平均數",
        "求平均數",
        "求中位數",
        "求標準差",
    ]
    required_scope_hits = 0
    for seed in range(24):
        p = generate_for_chap3_skill(skill_id=S_BASIC, problem_type_id=PT_BASIC, seed=seed, level=1)
        blob = " ".join(
            [
                str(p.get("question_text", "")),
                str(p.get("explanation", "")),
                " ".join(str(c) for c in p.get("choices", [])),
            ]
        )
        for bad in forbidden:
            assert bad not in blob
        if any(k in blob for k in ["敘述統計", "推論統計", "蒐集", "整理", "陳示", "分析", "解釋", "普查", "抽查"]):
            required_scope_hits += 1
    assert required_scope_hits >= 20


def test_choice_contract_and_check_answer(logged_client) -> None:
    scenario_answer = {
        str(s["scenario_id"]): str(s["answer"]) for s in STATISTICAL_BASIC_CONCEPT_SCENARIOS
    }
    for seed in range(12):
        p = generate_for_chap3_skill(skill_id=S_BASIC, problem_type_id=PT_BASIC, seed=seed, level=1)
        choices = p.get("choices") or []
        answer = str(p.get("answer"))
        assert p.get("runtime_mode") == "deterministic_choice"
        assert p.get("check_mode") == "deterministic_auto_checked"
        assert p.get("grading_mode") == "deterministic"
        assert p.get("answer_input_type") == "choice"
        assert len(choices) >= 4
        assert answer in _choice_codes(choices)
        assert p.get("choices_display") or p.get("choices")
        assert p.get("explanation")

        resp = logged_client.get(
            f"/get_next_question?skill={quote(S_BASIC)}&problem_type={PT_BASIC}&gen_seed={seed}&level=1"
        )
        assert resp.status_code == 200
        data = resp.get_json() or {}
        route_answer = scenario_answer[str(data["scenario_id"])]
        ok_num = logged_client.post("/check_answer", json={"answer": route_answer}).get_json() or {}
        alias = chr(ord("A") + int(route_answer) - 1)
        ok_alias = logged_client.post("/check_answer", json={"answer": alias}).get_json() or {}
        bad = logged_client.post(
            "/check_answer", json={"answer": _wrong_choice(route_answer)}
        ).get_json() or {}
        assert ok_num.get("correct") is True
        assert ok_alias.get("correct") is True
        assert bad.get("correct") is False


def test_route_avoids_previous_scenario_id_when_history_exists(logged_client) -> None:
    url = f"/get_next_question?skill={quote(S_BASIC)}&problem_type={PT_BASIC}&gen_seed=1&level=1"
    first = logged_client.get(url).get_json() or {}
    second = logged_client.get(url).get_json() or {}
    assert first.get("scenario_id")
    assert second.get("scenario_id")
    assert first["scenario_id"] != second["scenario_id"]
    assert first["new_question_text"] != second["new_question_text"]


def test_chap3_qa_gate_regression_not_high_repetition_major() -> None:
    payloads = [
        generate_for_chap3_skill(skill_id=S_BASIC, problem_type_id=PT_BASIC, seed=i, level=1)
        for i in range(10)
    ]
    unique_questions = {str(p.get("question_text", "")) for p in payloads}
    repeated_ratio = 1 - len(unique_questions) / len(payloads)
    assert repeated_ratio <= 0.5
