from __future__ import annotations

import json
import uuid
from pathlib import Path
from urllib.parse import quote

import pytest

from app import create_app
from models import User, db
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill


REPORT_PATH = Path(
    "reports/b4_generator_planning/b4_fullruntime2_remaining_6_skills_mode_aware_paths_summary.md"
)
SAMPLE_DIR = Path("reports/b4_generator_planning/fullruntime2_samples")

S_PASCAL = "vh_數學B4_PascalTriangle"
S_SURVEY = "vh_數學B4_SamplingSurvey"
S_CUM = "vh_數學B4_CumulativeFrequencyTablesAndGraphs"
S_DATA = "vh_數學B4_DataOrganizationAndCharts"
S_CHART = "vh_數學B4_StatisticalChartReading"
S_POLL = "vh_數學B4_OpinionPollInterpretation"

PT_PASCAL = "pascal_triangle_handwriting"
PT_SURVEY = "sampling_survey_bias_review"
PT_CUM = "cumulative_frequency_table_completion_review"
PT_DATA = "data_organization_chart_selection_review"
PT_CHART = "statistical_chart_reading_visibility_review"
PT_POLL = "opinion_poll_interpretation_review"


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
            username=f"b4_fullruntime2_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def test_remaining_6_matrix_complete_and_no_unknown() -> None:
    text = REPORT_PATH.read_text(encoding="utf-8")
    for sid in [S_PASCAL, S_SURVEY, S_CUM, S_DATA, S_CHART, S_POLL]:
        assert sid in text
    for key in ["recommended_runtime_mode", "check_mode", "grading_mode"]:
        assert key in text
    assert "unknown" not in text.lower()


@pytest.mark.parametrize(
    ("skill_id", "problem_type_id", "runtime_mode", "check_mode", "grading_mode"),
    [
        (S_SURVEY, PT_SURVEY, "teacher_review", "review_mode", "teacher_review"),
        (S_CUM, PT_CUM, "visual_or_handwriting_ai_checked", "review_mode", "teacher_review"),
        (S_DATA, PT_DATA, "teacher_review", "review_mode", "teacher_review"),
        (S_CHART, PT_CHART, "visibility_only", "review_mode", "visibility_only"),
        (S_POLL, PT_POLL, "teacher_review", "review_mode", "teacher_review"),
    ],
)
def test_router_payload_for_remaining_5(skill_id, problem_type_id, runtime_mode, check_mode, grading_mode) -> None:
    payload = generate_for_chap3_skill(skill_id=skill_id, problem_type_id=problem_type_id, seed=11, level=1)
    assert payload["problem_type_id"] == problem_type_id
    assert payload["runtime_mode"] == runtime_mode
    assert payload["check_mode"] == check_mode
    assert payload["grading_mode"] == grading_mode
    assert payload.get("answer_input_type")
    assert "question_text" in payload and str(payload["question_text"]).strip()
    assert "explanation" in payload and str(payload["explanation"]).strip()


def test_get_next_question_runtime_or_review_path_all_6(logged_client) -> None:
    cases = [
        (S_PASCAL, PT_PASCAL),
        (S_SURVEY, PT_SURVEY),
        (S_CUM, PT_CUM),
        (S_DATA, PT_DATA),
        (S_CHART, PT_CHART),
        (S_POLL, PT_POLL),
    ]
    for skill, pt in cases:
        for sid in (skill, quote(skill)):
            resp = logged_client.get(f"/get_next_question?skill={sid}&problem_type={pt}&gen_seed=7&level=1")
            assert resp.status_code == 200, resp.get_data(as_text=True)
            data = resp.get_json() or {}
            assert data.get("problem_type_id")
            assert data.get("runtime_mode")
            assert data.get("check_mode")
            assert data.get("grading_mode")
            assert data.get("answer_input_type")


@pytest.mark.parametrize(
    ("skill_id", "problem_type_id"),
    [
        (S_PASCAL, PT_PASCAL),
        (S_SURVEY, PT_SURVEY),
        (S_CUM, PT_CUM),
        (S_DATA, PT_DATA),
        (S_CHART, PT_CHART),
        (S_POLL, PT_POLL),
    ],
)
def test_ai_review_guard_for_remaining_6(skill_id, problem_type_id, logged_client) -> None:
    q = logged_client.get(
        f"/get_next_question?skill={quote(skill_id)}&problem_type={problem_type_id}&gen_seed=13&level=1"
    )
    assert q.status_code == 200
    d = q.get_json() or {}
    assert d.get("check_mode") in {"handwriting_ai_checked", "review_mode"}
    guarded = logged_client.post("/check_answer", json={"answer": "任意文字"}).get_json() or {}
    assert guarded.get("correct") is False
    assert "AI/Review" in str(guarded.get("result", ""))


def test_localization_for_remaining_6() -> None:
    forbidden = ["Read", "Choose", "Please", "Explain", "Question", "Survey result"]
    payloads = [
        generate_for_chap3_skill(skill_id=S_SURVEY, problem_type_id=PT_SURVEY, seed=3, level=1),
        generate_for_chap3_skill(skill_id=S_CUM, problem_type_id=PT_CUM, seed=3, level=1),
        generate_for_chap3_skill(skill_id=S_DATA, problem_type_id=PT_DATA, seed=3, level=1),
        generate_for_chap3_skill(skill_id=S_CHART, problem_type_id=PT_CHART, seed=3, level=1),
        generate_for_chap3_skill(skill_id=S_POLL, problem_type_id=PT_POLL, seed=3, level=1),
    ]
    for p in payloads:
        text = " ".join(
            [
                str(p.get("question_text", "")),
                str(p.get("explanation", "")),
                " ".join(str(x) for x in (p.get("choices") or [])),
                str((p.get("visual_aids") or [{}])[0].get("title", "")),
                str((p.get("visual_aids") or [{}])[0].get("caption", "")),
                str((p.get("visual_aids") or [{}])[0].get("alt_text", "")),
            ]
        )
        for bad in forbidden:
            assert bad not in text


def test_export_fullruntime2_sample_artifacts(logged_client) -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    artifacts = [
        ("pascal_triangle_sample_01.json", S_PASCAL, PT_PASCAL, "route"),
        ("sampling_survey_sample_01.json", S_SURVEY, PT_SURVEY, "router"),
        ("cumulative_frequency_tables_and_graphs_sample_01.json", S_CUM, PT_CUM, "router"),
        ("data_organization_and_charts_sample_01.json", S_DATA, PT_DATA, "router"),
        ("statistical_chart_reading_sample_01.json", S_CHART, PT_CHART, "router"),
        ("opinion_poll_interpretation_sample_01.json", S_POLL, PT_POLL, "router"),
    ]
    for filename, skill, pt, source in artifacts:
        if source == "route":
            resp = logged_client.get(
                f"/get_next_question?skill={quote(skill)}&problem_type={pt}&gen_seed=21&level=1"
            )
            assert resp.status_code == 200
            payload = resp.get_json() or {}
        else:
            payload = generate_for_chap3_skill(skill_id=skill, problem_type_id=pt, seed=21, level=1)
        out = SAMPLE_DIR / filename
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        assert out.exists()

