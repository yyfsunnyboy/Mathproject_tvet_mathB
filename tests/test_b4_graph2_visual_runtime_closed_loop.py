from __future__ import annotations

import re
import uuid
from urllib.parse import quote

import pytest

from app import create_app
from models import User, db
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill


S_CENT = "vh_數學B4_CentralTendencyMeasures"
S_DISP = "vh_數學B4_DispersionMeasures"
S_WEIGHT = "vh_數學B4_WeightedMean"
S_VARSTD = "vh_數學B4_VarianceAndStandardDeviation"
S_TREE = "vh_數學B4_TreeDiagramCounting"

PT_GRAPH1_A = "chart_mode_bar_reading"
PT_GRAPH1_B = "chart_range_line_reading"
PT_GRAPH2_A = "frequency_table_mean_reading"
PT_GRAPH2_B = "frequency_table_range_reading"

REPORT_PATH = "reports/b4_generator_planning/b4_graph2_visual_runtime_closed_loop_summary.md"


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
            username=f"b4_graph2_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def test_inventory_selection_evidence_in_report() -> None:
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    assert "Candidate families table" in text
    assert "selected_or_not" in text
    selected_count = len(re.findall(r"\|\s*selected\s*\|", text))
    assert selected_count == 2
    assert PT_GRAPH2_A in text
    assert PT_GRAPH2_B in text


@pytest.mark.parametrize(
    "skill_id,problem_type",
    [(S_CENT, PT_GRAPH2_A), (S_DISP, PT_GRAPH2_B)],
)
def test_generator_payload_contract_graph2(skill_id: str, problem_type: str) -> None:
    payload = generate_for_chap3_skill(
        skill_id=skill_id,
        problem_type_id=problem_type,
        seed=17,
        level=1,
    )
    assert payload["problem_type_id"] == problem_type
    assert payload["visual_backed"] is True
    assert payload["visual_asset_type"] == "table"
    assert payload["runtime_mode"] == "visual_reading_with_short_answer"
    assert payload["check_mode"] == "deterministic_auto_checked"
    assert payload["grading_mode"] == "deterministic"
    assert payload.get("scenario_family") or payload.get("parameters", {}).get("scenario_family")
    assert payload.get("visual_aids") or payload.get("image_base64")
    assert payload["answer_type"] == "integer"
    assert str(payload["answer"]).strip().lstrip("-").isdigit()


@pytest.mark.parametrize(
    "skill_id,problem_type,forbidden_phrases",
    [
        (
            S_CENT,
            PT_GRAPH2_A,
            ["Read the frequency table", "arithmetic mean", "Frequency Table", "Value", "Frequency"],
        ),
        (
            S_DISP,
            PT_GRAPH2_B,
            ["Read the frequency table", "range", "Frequency Table", "Value", "Frequency"],
        ),
    ],
)
def test_graph2_chinese_text_localization(
    skill_id: str, problem_type: str, forbidden_phrases: list[str]
) -> None:
    payload = generate_for_chap3_skill(
        skill_id=skill_id,
        problem_type_id=problem_type,
        seed=23,
        level=1,
    )
    q_text = str(payload.get("question_text", ""))
    for phrase in forbidden_phrases:
        assert phrase not in q_text

    # If image text is not directly machine-readable, assert Chinese source
    # fields in visual_aids/table metadata are already Chinese.
    aids = payload.get("visual_aids") or []
    assert aids, "visual_aids required for table localization source-of-truth"
    table_obj = aids[0]
    joined = " ".join(
        [
            str(table_obj.get("title", "")),
            str(table_obj.get("caption", "")),
            " ".join([str(h) for h in table_obj.get("headers", [])]),
            str(payload.get("table_title", "")),
        ]
    )
    assert "次數分配表" in joined
    assert "數值" in joined
    assert "次數" in joined
    assert "Frequency Table" not in joined
    assert "Value" not in joined
    assert "Frequency" not in joined


def test_router_supports_graph2_and_keeps_graph1() -> None:
    p_new = generate_for_chap3_skill(skill_id=S_CENT, problem_type_id=PT_GRAPH2_A, seed=5, level=1)
    p_old = generate_for_chap3_skill(skill_id=S_CENT, problem_type_id=PT_GRAPH1_A, seed=5, level=1)
    assert p_new["problem_type_id"] == PT_GRAPH2_A
    assert p_old["problem_type_id"] == PT_GRAPH1_A


@pytest.mark.parametrize(
    "skill_id,problem_type",
    [(S_CENT, PT_GRAPH2_A), (S_DISP, PT_GRAPH2_B)],
)
def test_practice_get_next_question_graph2_encoded_decoded(
    logged_client, skill_id: str, problem_type: str
) -> None:
    # decoded
    r1 = logged_client.get(
        f"/get_next_question?skill={skill_id}&problem_type={problem_type}&gen_seed=9&level=1"
    )
    assert r1.status_code == 200, r1.get_data(as_text=True)
    d1 = r1.get_json() or {}
    # encoded
    r2 = logged_client.get(
        f"/get_next_question?skill={quote(skill_id)}&problem_type={problem_type}&gen_seed=9&level=1"
    )
    assert r2.status_code == 200, r2.get_data(as_text=True)
    d2 = r2.get_json() or {}

    for d in (d1, d2):
        assert d.get("problem_type_id") == problem_type
        assert d.get("visual_backed") is True
        assert d.get("visual_asset_type") == "table"
        assert d.get("runtime_mode") == "visual_reading_with_short_answer"
        assert d.get("check_mode") == "deterministic_auto_checked"
        assert d.get("grading_mode") == "deterministic"
        assert "new_question_text" in d
        assert "answer_type" in d
        assert d.get("image_base64") or d.get("visual_aids")


@pytest.mark.parametrize(
    "skill_id,problem_type,seed",
    [(S_CENT, PT_GRAPH2_A, 11), (S_DISP, PT_GRAPH2_B, 13)],
)
def test_check_answer_deterministic_correct_and_wrong(
    logged_client, skill_id: str, problem_type: str, seed: int
) -> None:
    q = logged_client.get(
        f"/get_next_question?skill={quote(skill_id)}&problem_type={problem_type}&gen_seed={seed}&level=1"
    )
    assert q.status_code == 200
    expected = generate_for_chap3_skill(
        skill_id=skill_id, problem_type_id=problem_type, seed=seed, level=1
    )
    ans = str(expected["correct_answer"])
    ok = logged_client.post("/check_answer", json={"answer": ans})
    assert ok.status_code == 200
    assert (ok.get_json() or {}).get("correct") is True

    bad = logged_client.post("/check_answer", json={"answer": "__wrong__"})
    assert bad.status_code == 200
    assert (bad.get_json() or {}).get("correct") is False


def test_check_answer_guard_for_ai_checked_mode(logged_client) -> None:
    q = logged_client.get(
        f"/get_next_question?skill={quote(S_TREE)}&problem_type=tree_diagram_listing&tree_diagram_index=0"
    )
    assert q.status_code == 200
    d = q.get_json() or {}
    assert d.get("grading_mode") == "ai_judged_free_response"
    guarded = logged_client.post("/check_answer", json={"answer": "any"})
    payload = guarded.get_json() or {}
    assert guarded.status_code == 200
    assert payload.get("correct") is False
    assert "AI" in str(payload.get("result", ""))


def test_scenario_diversity_graph2_not_number_only() -> None:
    seen_mean = set()
    seen_range = set()
    for seed in range(1, 20):
        p1 = generate_for_chap3_skill(skill_id=S_CENT, problem_type_id=PT_GRAPH2_A, seed=seed, level=1)
        p2 = generate_for_chap3_skill(skill_id=S_DISP, problem_type_id=PT_GRAPH2_B, seed=seed, level=1)
        seen_mean.add(tuple(p1["parameters"]["values"]))
        seen_range.add(tuple(p2["parameters"]["values"]))
        assert p1["visual_asset_type"] == "table"
        assert p2["visual_asset_type"] == "table"
    assert len(seen_mean) >= 2
    assert len(seen_range) >= 2


def test_regression_graph1_families_still_work() -> None:
    p1 = generate_for_chap3_skill(skill_id=S_CENT, problem_type_id=PT_GRAPH1_A, seed=3, level=1)
    p2 = generate_for_chap3_skill(skill_id=S_DISP, problem_type_id=PT_GRAPH1_B, seed=3, level=1)
    assert p1["problem_type_id"] == PT_GRAPH1_A
    assert p2["problem_type_id"] == PT_GRAPH1_B
    assert p1.get("visual_backed") is True
    assert p2.get("visual_backed") is True


def test_regression_existing_chap3_deterministic_skills() -> None:
    p_weight = generate_for_chap3_skill(skill_id=S_WEIGHT, problem_type_id="weighted_mean_basic", seed=4, level=1)
    p_var = generate_for_chap3_skill(skill_id=S_VARSTD, problem_type_id="variance_basic_numeric", seed=4, level=1)
    assert p_weight["problem_type_id"] == "weighted_mean_basic"
    assert p_var["problem_type_id"] == "variance_basic_numeric"
    assert p_weight["answer_type"] in {"integer", "rational_fraction"}
    assert p_var["answer_type"] in {"integer", "rational_fraction"}
