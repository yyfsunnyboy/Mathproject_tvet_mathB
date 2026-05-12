from __future__ import annotations

import uuid
from urllib.parse import quote

import pytest

from app import create_app
from core.vocational_math_b4.services import question_router as chap3_router
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill
from models import User, db


FORBIDDEN_OPEN_ENDED = [
    "請說明",
    "請簡述",
    "請討論",
    "請描述",
    "簡述理由",
    "提出理由",
    "提出改善方式",
    "可能有哪些偏誤",
    "是否合理",
    "是否具有代表性",
]


def _resolve_skill_id(suffix: str) -> str:
    for key in chap3_router._CHAP3_PHASE7B_REGISTRY.keys():
        if str(key).endswith(suffix):
            return str(key)
    raise AssertionError(f"Missing skill suffix={suffix}")


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"b4_chap3_no_open_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    return client


def test_data_organization_level1_no_open_ended_and_choice_only() -> None:
    skill_id = _resolve_skill_id("DataOrganizationAndCharts")
    payloads = [generate_for_chap3_skill(skill_id=skill_id, level=1, seed=i + 1) for i in range(20)]
    qtexts = [str(p.get("question_text", "")) for p in payloads]
    scenario_ids = [str(p.get("scenario_id", "")) for p in payloads]

    open_ended_count = 0
    deterministic_choice_count = 0
    choices_missing_count = 0
    for p in payloads:
        q = str(p.get("question_text", ""))
        if any(t in q for t in FORBIDDEN_OPEN_ENDED):
            open_ended_count += 1
        if p.get("runtime_mode") == "deterministic_choice":
            deterministic_choice_count += 1
        if not (p.get("choices") or []):
            choices_missing_count += 1

    consecutive_dup = sum(1 for i in range(1, len(qtexts)) if qtexts[i] == qtexts[i - 1])

    assert open_ended_count == 0
    assert deterministic_choice_count >= 20
    assert choices_missing_count == 0
    assert len(set(qtexts)) >= 8
    assert len(set(scenario_ids)) >= 6
    assert consecutive_dup == 0


def test_data_organization_choice_checker_with_alias(logged_client) -> None:
    skill_id = _resolve_skill_id("DataOrganizationAndCharts")

    trend_seed = None
    category_seed = None
    ratio_seed = None
    for s in range(1, 200):
        p = generate_for_chap3_skill(
            skill_id=skill_id, level=1, seed=s, problem_type_id="chart_type_selection_by_purpose"
        )
        q = str(p.get("question_text", ""))
        if "變化趨勢" in q and trend_seed is None:
            trend_seed = s
        if "比較各類別人數" in q and category_seed is None:
            category_seed = s
        if "占比" in q and ratio_seed is None:
            ratio_seed = s
        if trend_seed and category_seed and ratio_seed:
            break

    assert trend_seed is not None
    assert category_seed is not None
    assert ratio_seed is not None

    for seed in (trend_seed, category_seed, ratio_seed):
        resp = logged_client.get(
            f"/get_next_question?skill={quote(skill_id)}&level=1&problem_type=chart_type_selection_by_purpose&gen_seed={seed}"
        )
        assert resp.status_code == 200
        ok1 = (logged_client.post("/check_answer", json={"answer": "1"}).get_json() or {})
        okA = (logged_client.post("/check_answer", json={"answer": "A"}).get_json() or {})
        bad2 = (logged_client.post("/check_answer", json={"answer": "2"}).get_json() or {})
        assert ok1.get("correct") is True
        assert okA.get("correct") is True
        assert bad2.get("correct") is False
        for item in (ok1, okA, bad2):
            msg = str(item.get("result", ""))
            assert "AI/Review" not in msg
            assert "模組載入錯誤" not in msg


def test_review_explicit_path_only() -> None:
    skill_id = _resolve_skill_id("DataOrganizationAndCharts")
    p = generate_for_chap3_skill(
        skill_id=skill_id, level=1, seed=1, problem_type_id="data_organization_chart_selection_review"
    )
    assert p.get("problem_type_id") == "data_organization_chart_selection_review"
    assert p.get("runtime_mode") == "teacher_review"
    assert p.get("check_mode") == "review_mode"
    assert p.get("grading_mode") == "teacher_review"
    assert p.get("expected_answer_schema") or p.get("rubric")


def test_chap3_level1_global_no_open_ended_audit() -> None:
    skills = [
        _resolve_skill_id("StatisticalBasicConcepts"),
        _resolve_skill_id("SamplingSurvey"),
        _resolve_skill_id("SamplingMethods"),
        _resolve_skill_id("DataOrganizationAndCharts"),
        _resolve_skill_id("StatisticalChartReading"),
        _resolve_skill_id("CumulativeFrequencyTablesAndGraphs"),
        _resolve_skill_id("FrequencyDistributionTableConstruction"),
        _resolve_skill_id("HistogramsAndFrequencyPolygons"),
    ]
    deterministic_suffixes = {
        "StatisticalBasicConcepts",
        "SamplingSurvey",
        "SamplingMethods",
        "DataOrganizationAndCharts",
        "StatisticalChartReading",
        "HistogramsAndFrequencyPolygons",
    }
    review_modes = {"review_mode", "handwriting_ai_checked", "visual_ai_checked"}

    for skill_id in skills:
        payloads = [generate_for_chap3_skill(skill_id=skill_id, level=1, seed=i + 1) for i in range(20)]
        suffix = skill_id.split("B4_")[-1]
        open_ended_default_count = 0
        for p in payloads:
            q = str(p.get("question_text", ""))
            if any(t in q for t in FORBIDDEN_OPEN_ENDED):
                open_ended_default_count += 1
            if suffix in deterministic_suffixes:
                assert p.get("runtime_mode") in {"deterministic_choice", "visual_reading_with_short_answer"}
            else:
                if p.get("check_mode") in review_modes:
                    assert p.get("expected_answer_schema") or p.get("rubric")
                    assert p.get("table") or p.get("visual_aids") or p.get("image_base64") or p.get("raw_data")
        if suffix in deterministic_suffixes:
            assert open_ended_default_count == 0
