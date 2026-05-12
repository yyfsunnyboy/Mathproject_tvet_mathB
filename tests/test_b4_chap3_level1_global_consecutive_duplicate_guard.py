from __future__ import annotations

import uuid
from urllib.parse import quote

import pytest

from app import create_app
from core.vocational_math_b4.services import question_router as chap3_router
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill
from models import User, db


OPEN_ENDED_TOKENS = [
    "請說明", "請簡述", "請討論", "簡述理由", "提出理由", "可能有哪些偏誤", "是否具有代表性", "提出改善方式"
]

CHAP3_SUFFIXES = [
    "StatisticalBasicConcepts",
    "SamplingSurvey",
    "SamplingMethods",
    "DataOrganizationAndCharts",
    "StatisticalChartReading",
    "CumulativeFrequencyTablesAndGraphs",
    "FrequencyDistributionTableConstruction",
    "HistogramsAndFrequencyPolygons",
    "CentralTendencyMeasures",
    "DispersionMeasures",
    "WeightedMean",
    "VarianceAndStandardDeviation",
    "LinearTransformationOfData",
    "NormalDistributionAndEmpiricalRule",
]


def _resolve_skill_id(suffix: str) -> str:
    for key in chap3_router._CHAP3_PHASE7B_REGISTRY.keys():
        if str(key).endswith(suffix):
            return str(key)
    raise AssertionError(f"missing skill suffix={suffix}")


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"b4_chap3_global_dup_{uuid.uuid4().hex[:10]}",
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


def test_global_route_duplicate_guard_across_chap3_level1(logged_client) -> None:
    for suffix in CHAP3_SUFFIXES:
        skill = _resolve_skill_id(suffix)
        qtexts = []
        sids = []
        psigs = []
        for _ in range(20):
            r = logged_client.get(f"/get_next_question?skill={quote(skill)}&level=1")
            assert r.status_code == 200
            payload = r.get_json() or {}
            qtexts.append(str(payload.get("new_question_text", "")))
            sids.append(str(payload.get("scenario_id", "")))
            psigs.append(str(payload.get("parameter_signature", "")))

        assert sum(1 for i in range(1, len(qtexts)) if qtexts[i] == qtexts[i - 1]) == 0
        if any(sids):
            assert sum(1 for i in range(1, len(sids)) if sids[i] and sids[i] == sids[i - 1]) == 0
        if any(psigs):
            assert sum(1 for i in range(1, len(psigs)) if psigs[i] and psigs[i] == psigs[i - 1]) == 0


def test_no_open_ended_fallback_regression_for_deterministic_mixed_level1() -> None:
    deterministic_mixed = [
        "StatisticalBasicConcepts",
        "SamplingSurvey",
        "SamplingMethods",
        "DataOrganizationAndCharts",
        "StatisticalChartReading",
        "HistogramsAndFrequencyPolygons",
        "CentralTendencyMeasures",
        "DispersionMeasures",
        "WeightedMean",
        "VarianceAndStandardDeviation",
        "LinearTransformationOfData",
        "NormalDistributionAndEmpiricalRule",
    ]
    for suffix in deterministic_mixed:
        skill = _resolve_skill_id(suffix)
        payloads = [generate_for_chap3_skill(skill_id=skill, level=1, seed=i + 1) for i in range(20)]
        for p in payloads:
            q = str(p.get("question_text", ""))
            assert not any(tok in q for tok in OPEN_ENDED_TOKENS)


def test_metadata_presence_level1_chap3() -> None:
    for suffix in CHAP3_SUFFIXES:
        skill = _resolve_skill_id(suffix)
        p = generate_for_chap3_skill(skill_id=skill, level=1, seed=1)
        assert p.get("problem_type_id")
        assert p.get("scenario_id") or p.get("question_pattern_id")
        if "parameter_signature" in p:
            assert str(p.get("parameter_signature", "")).strip()
        if p.get("visual_asset_type") in {"table", "histogram"}:
            has_visual_hash = bool(
                p.get("table_spec_hash") or p.get("chart_spec_hash") or p.get("visual_asset_hash")
            )
            assert has_visual_hash or p.get("table") or p.get("chart_spec") or p.get("visual_aids")


def test_known_regression_cases_non_consecutive_fixed_patterns() -> None:
    # SamplingSurvey food 2000/100 should not appear consecutively in generated seeds.
    skill_sampling = _resolve_skill_id("SamplingSurvey")
    texts = [str(generate_for_chap3_skill(skill_id=skill_sampling, level=1, seed=i + 1).get("question_text", "")) for i in range(20)]
    target_food = "2000 包餅乾"
    positions = [i for i, t in enumerate(texts) if target_food in t]
    assert all((positions[i] - positions[i - 1]) > 1 for i in range(1, len(positions)))

    # DataOrganization ratio/pie style should not appear consecutively.
    skill_data = _resolve_skill_id("DataOrganizationAndCharts")
    texts2 = [str(generate_for_chap3_skill(skill_id=skill_data, level=1, seed=i + 1).get("question_text", "")) for i in range(20)]
    target_ratio = "占比"
    pos2 = [i for i, t in enumerate(texts2) if target_ratio in t]
    assert all((pos2[i] - pos2[i - 1]) > 1 for i in range(1, len(pos2)))


def test_checker_regression_sampling_and_data_org(logged_client) -> None:
    # SamplingSurvey 5000/250: 3/C/c correct
    skill_sampling = _resolve_skill_id("SamplingSurvey")
    target_seed = None
    for s in range(1, 300):
        p = generate_for_chap3_skill(skill_id=skill_sampling, level=1, seed=s)
        q = str(p.get("question_text", ""))
        if "5000 位機車族" in q and "250 位" in q and "樣本" in q:
            target_seed = s
            break
    assert target_seed is not None
    r = logged_client.get(
        f"/get_next_question?skill={quote(skill_sampling)}&level=1&problem_type=sampling_survey_foundation_identification&gen_seed={target_seed}"
    )
    assert r.status_code == 200
    assert (logged_client.post("/check_answer", json={"answer": "3"}).get_json() or {}).get("correct") is True
    assert (logged_client.post("/check_answer", json={"answer": "C"}).get_json() or {}).get("correct") is True
    assert (logged_client.post("/check_answer", json={"answer": "c"}).get_json() or {}).get("correct") is True

    # DataOrganization deterministic choice: alias works and wrong answer fails.
    skill_data = _resolve_skill_id("DataOrganizationAndCharts")
    r2 = logged_client.get(
        f"/get_next_question?skill={quote(skill_data)}&level=1&problem_type=chart_type_selection_by_purpose&gen_seed=1"
    )
    assert r2.status_code == 200
    assert (logged_client.post("/check_answer", json={"answer": "1"}).get_json() or {}).get("correct") is True
    assert (logged_client.post("/check_answer", json={"answer": "A"}).get_json() or {}).get("correct") is True
    assert (logged_client.post("/check_answer", json={"answer": "2"}).get_json() or {}).get("correct") is False
