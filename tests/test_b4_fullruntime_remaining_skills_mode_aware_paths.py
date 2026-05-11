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
    "reports/b4_generator_planning/b4_fullruntime_remaining_11_skills_mode_aware_paths_summary.md"
)
SAMPLE_DIR = Path("reports/b4_generator_planning/fullruntime_samples")

S_NORMAL = "vh_數學B4_NormalDistributionAndEmpiricalRule"
S_SAMPLING = "vh_數學B4_SamplingMethods"
S_BASIC = "vh_數學B4_StatisticalBasicConcepts"
S_TREE = "vh_數學B4_TreeDiagramCounting"
S_FREQ_TABLE = "vh_數學B4_FrequencyDistributionTableConstruction"
S_GRAPH1 = "vh_數學B4_CentralTendencyMeasures"
S_GRAPH3 = "vh_數學B4_HistogramsAndFrequencyPolygons"

PT_NORMAL = "empirical_rule_interval_percentage"
PT_SAMPLING = "sampling_methods_classification_choice"
PT_BASIC = "statistical_basic_concepts_choice"
PT_TREE = "tree_diagram_completion_or_listing"
PT_FREQ_TABLE = "table_completion_handwriting"


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
            username=f"b4_fullruntime_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def test_remaining_11_matrix_complete_and_no_unknown() -> None:
    text = REPORT_PATH.read_text(encoding="utf-8")
    required_skills = [
        "vh_數學B4_TreeDiagramCounting",
        "vh_數學B4_PascalTriangle",
        "vh_數學B4_SamplingMethods",
        "vh_數學B4_SamplingSurvey",
        "vh_數學B4_StatisticalBasicConcepts",
        "vh_數學B4_CumulativeFrequencyTablesAndGraphs",
        "vh_數學B4_DataOrganizationAndCharts",
        "vh_數學B4_FrequencyDistributionTableConstruction",
        "vh_數學B4_StatisticalChartReading",
        "vh_數學B4_NormalDistributionAndEmpiricalRule",
        "vh_數學B4_OpinionPollInterpretation",
    ]
    for skill in required_skills:
        assert skill in text
    for key in ["recommended_runtime_mode", "check_mode", "grading_mode"]:
        assert key in text
    assert "unknown" not in text.lower()


@pytest.mark.parametrize(
    ("skill_id", "problem_type_id", "runtime_mode", "check_mode", "grading_mode"),
    [
        (S_NORMAL, PT_NORMAL, "deterministic_short_answer", "deterministic_auto_checked", "deterministic"),
        (S_SAMPLING, PT_SAMPLING, "deterministic_choice", "deterministic_auto_checked", "deterministic"),
        (S_BASIC, PT_BASIC, "deterministic_choice", "deterministic_auto_checked", "deterministic"),
        (S_TREE, PT_TREE, "visual_or_handwriting_ai_checked", "handwriting_ai_checked", "ai_assisted_review"),
        (S_FREQ_TABLE, PT_FREQ_TABLE, "visual_or_handwriting_ai_checked", "handwriting_ai_checked", "ai_assisted_review"),
    ],
)
def test_first_batch_router_payload(skill_id, problem_type_id, runtime_mode, check_mode, grading_mode) -> None:
    payload = generate_for_chap3_skill(
        skill_id=skill_id,
        problem_type_id=problem_type_id,
        seed=11,
        level=1,
    )
    assert payload["skill_id"] == skill_id
    assert payload["problem_type_id"] == problem_type_id
    assert payload["runtime_mode"] == runtime_mode
    assert payload["check_mode"] == check_mode
    assert payload["grading_mode"] == grading_mode
    assert payload.get("scenario_family") or payload.get("scenario_id")
    assert "question_text" in payload and str(payload["question_text"]).strip()
    assert "explanation" in payload and str(payload["explanation"]).strip()


def test_route_get_next_question_for_first_batch_encoded_decoded(logged_client) -> None:
    for skill, pt in [
        (S_NORMAL, PT_NORMAL),
        (S_SAMPLING, PT_SAMPLING),
        (S_BASIC, PT_BASIC),
        (S_TREE, PT_TREE),
        (S_FREQ_TABLE, PT_FREQ_TABLE),
    ]:
        for sid in (skill, quote(skill)):
            resp = logged_client.get(
                f"/get_next_question?skill={sid}&problem_type={pt}&gen_seed=9&level=1"
            )
            assert resp.status_code == 200, resp.get_data(as_text=True)
            data = resp.get_json() or {}
            if skill == S_TREE:
                assert data.get("problem_type_id") in {PT_TREE, "tree_diagram_listing"}
            else:
                assert data.get("problem_type_id") == pt
            assert data.get("runtime_mode")
            assert data.get("check_mode")
            assert data.get("grading_mode")


def test_normal_distribution_deterministic_check_answer(logged_client) -> None:
    seed = 23
    resp = logged_client.get(
        f"/get_next_question?skill={quote(S_NORMAL)}&problem_type={PT_NORMAL}&gen_seed={seed}&level=1"
    )
    assert resp.status_code == 200
    expected = generate_for_chap3_skill(skill_id=S_NORMAL, problem_type_id=PT_NORMAL, seed=seed, level=1)
    answer = str(expected["answer"])
    ok = logged_client.post("/check_answer", json={"answer": answer}).get_json() or {}
    bad = logged_client.post("/check_answer", json={"answer": "__wrong__"}).get_json() or {}
    assert ok.get("correct") is True
    assert bad.get("correct") is False
    assert "經驗法則" in str(expected.get("explanation", ""))


@pytest.mark.parametrize(
    ("skill_id", "problem_type_id"),
    [(S_SAMPLING, PT_SAMPLING), (S_BASIC, PT_BASIC)],
)
def test_choice_payload_and_check(skill_id, problem_type_id, logged_client) -> None:
    payload = generate_for_chap3_skill(skill_id=skill_id, problem_type_id=problem_type_id, seed=17, level=1)
    choices = payload.get("choices") or []
    assert choices
    assert str(payload["answer"]) in {"1", "2", "3", "4"}
    assert any(str(payload["answer"]) in c for c in choices)

    resp = logged_client.get(
        f"/get_next_question?skill={quote(skill_id)}&problem_type={problem_type_id}&gen_seed=17&level=1"
    )
    assert resp.status_code == 200
    ok = logged_client.post("/check_answer", json={"answer": str(payload["answer"])}).get_json() or {}
    bad = logged_client.post("/check_answer", json={"answer": "9"}).get_json() or {}
    assert ok.get("correct") is True
    assert bad.get("correct") is False


@pytest.mark.parametrize(
    ("skill_id", "problem_type_id", "require_key"),
    [(S_TREE, PT_TREE, "requires_listing_or_tree"), (S_FREQ_TABLE, PT_FREQ_TABLE, "answer_type")],
)
def test_ai_guard_for_non_deterministic(skill_id, problem_type_id, require_key, logged_client) -> None:
    resp = logged_client.get(
        f"/get_next_question?skill={quote(skill_id)}&problem_type={problem_type_id}&gen_seed=5&level=1"
    )
    assert resp.status_code == 200
    data = resp.get_json() or {}
    assert data.get("check_mode") == "handwriting_ai_checked"
    if skill_id == S_TREE:
        assert data.get("grading_mode") in {"ai_assisted_review", "ai_judged_free_response"}
    else:
        assert data.get("grading_mode") == "ai_assisted_review"
    if skill_id == S_TREE:
        assert data.get("requires_listing_or_tree") is True
    else:
        assert data.get("answer_type") == "handwriting"
    guard = logged_client.post("/check_answer", json={"answer": "任意作答"}).get_json() or {}
    assert guard.get("correct") is False
    assert "AI/Review" in str(guard.get("result", ""))


def test_localization_for_first_batch() -> None:
    forbidden = ["Read", "Choose", "Explain", "Please", "Question"]
    for skill, pt in [
        (S_NORMAL, PT_NORMAL),
        (S_SAMPLING, PT_SAMPLING),
        (S_BASIC, PT_BASIC),
        (S_TREE, PT_TREE),
        (S_FREQ_TABLE, PT_FREQ_TABLE),
    ]:
        payload = generate_for_chap3_skill(skill_id=skill, problem_type_id=pt, seed=3, level=1)
        text = " ".join(
            [
                str(payload.get("question_text", "")),
                str(payload.get("explanation", "")),
                " ".join(str(x) for x in (payload.get("choices") or [])),
            ]
        )
        for bad in forbidden:
            assert bad not in text


def test_regression_graph1_graph3_still_work() -> None:
    g1 = generate_for_chap3_skill(
        skill_id=S_GRAPH1,
        problem_type_id="chart_mode_bar_reading",
        seed=7,
        level=1,
    )
    g3 = generate_for_chap3_skill(
        skill_id=S_GRAPH3,
        problem_type_id="histogram_reading",
        seed=7,
        level=1,
    )
    assert g1["problem_type_id"] == "chart_mode_bar_reading"
    assert g3["problem_type_id"] == "histogram_reading"


def test_export_fullruntime_sample_artifacts() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    samples = [
        ("normal_distribution_empirical_rule_sample_01.json", S_NORMAL, PT_NORMAL),
        ("sampling_methods_sample_01.json", S_SAMPLING, PT_SAMPLING),
        ("statistical_basic_concepts_sample_01.json", S_BASIC, PT_BASIC),
        ("tree_diagram_counting_sample_01.json", S_TREE, PT_TREE),
        ("frequency_distribution_table_construction_sample_01.json", S_FREQ_TABLE, PT_FREQ_TABLE),
    ]
    for filename, skill, pt in samples:
        payload = generate_for_chap3_skill(skill_id=skill, problem_type_id=pt, seed=29, level=1)
        out = SAMPLE_DIR / filename
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        assert out.exists()
