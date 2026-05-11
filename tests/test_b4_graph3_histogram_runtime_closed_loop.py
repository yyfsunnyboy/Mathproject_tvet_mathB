from __future__ import annotations

import re
import uuid
import json
import base64
from pathlib import Path
from urllib.parse import quote

import pytest

from app import create_app
from models import User, db
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill


S_HIST = "vh_數學B4_HistogramsAndFrequencyPolygons"
S_CENT = "vh_數學B4_CentralTendencyMeasures"
S_DISP = "vh_數學B4_DispersionMeasures"
S_WEIGHT = "vh_數學B4_WeightedMean"
S_VARSTD = "vh_數學B4_VarianceAndStandardDeviation"

PT_HIST = "histogram_reading"
PT_G1_A = "chart_mode_bar_reading"
PT_G1_B = "chart_range_line_reading"
PT_G2_A = "frequency_table_mean_reading"
PT_G2_B = "frequency_table_range_reading"

REPORT_PATH = "reports/b4_generator_planning/b4_graph3_histogram_runtime_closed_loop_summary.md"
SAMPLE_DIR = Path("reports/b4_generator_planning/graph3_samples")


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
            username=f"b4_graph3_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def test_inventory_selection_evidence() -> None:
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    assert "candidate_family" in text
    assert "histogram_reading" in text
    selected_count = len(re.findall(r"\|\s*selected\s*\|", text))
    assert selected_count == 1
    assert "frequency_polygon" in text
    assert "cumulative_frequency_graph" in text
    assert "not_selected" in text


def test_generator_payload_contract_histogram() -> None:
    payload = generate_for_chap3_skill(skill_id=S_HIST, problem_type_id=PT_HIST, seed=11, level=1)
    assert payload["problem_type_id"] == PT_HIST
    assert payload["visual_backed"] is True
    assert payload["visual_asset_type"] == "histogram"
    assert payload["runtime_mode"] == "visual_reading_with_short_answer"
    assert payload["check_mode"] == "deterministic_auto_checked"
    assert payload["grading_mode"] == "deterministic"
    assert payload.get("scenario_family") or payload.get("parameters", {}).get("scenario_family")
    assert payload.get("visual_aids") or payload.get("image_base64")
    assert payload["answer_type"] == "integer"
    assert str(payload["answer"]).strip().lstrip("-").isdigit()


def test_histogram_visual_spec_consistency() -> None:
    payload = generate_for_chap3_skill(skill_id=S_HIST, problem_type_id=PT_HIST, seed=13, level=1)
    aid = (payload.get("visual_aids") or [{}])[0]
    bins = aid.get("bins") or payload.get("parameters", {}).get("bins")
    freqs = aid.get("frequencies") or payload.get("parameters", {}).get("frequencies")
    assert isinstance(bins, list) and isinstance(freqs, list)
    assert len(bins) >= 4
    assert len(bins) == len(freqs)
    assert all(isinstance(v, int) and v >= 0 for v in freqs)
    assert sum(freqs) > 0

    sid = payload.get("parameters", {}).get("scenario_id")
    answer = int(payload["answer"])
    if sid == "histogram_total_frequency":
        assert answer == sum(freqs)
    else:
        idx = payload.get("parameters", {}).get("target_idx")
        assert isinstance(idx, int)
        assert answer == freqs[idx]


def test_localization_regression_histogram() -> None:
    payload = generate_for_chap3_skill(skill_id=S_HIST, problem_type_id=PT_HIST, seed=17, level=1)
    q_text = str(payload.get("question_text", ""))
    exp = str(payload.get("explanation", ""))
    joined_text = f"{q_text} {exp}"
    for bad in ["Histogram", "Frequency", "Read the histogram", "interval", "count", "total frequency"]:
        assert bad not in joined_text

    aid = (payload.get("visual_aids") or [{}])[0]
    meta_join = " ".join(
        [
            str(aid.get("title", "")),
            str(aid.get("caption", "")),
            str(aid.get("alt_text", "")),
            str(aid.get("x_label", "")),
            str(aid.get("y_label", "")),
            str(payload.get("chart_title", "")),
        ]
    )
    assert "直方圖" in meta_join
    assert ("次數" in meta_join) or ("人數" in meta_join)
    assert ("組別" in meta_join) or ("分數區間" in meta_join) or ("資料區間" in meta_join)
    for bad in ["Histogram", "Frequency", "Read the histogram", "interval", "count", "total frequency"]:
        assert bad not in meta_join


def test_router_and_regression_graph1_graph2_not_broken() -> None:
    p_hist = generate_for_chap3_skill(skill_id=S_HIST, problem_type_id=PT_HIST, seed=5, level=1)
    p_g1a = generate_for_chap3_skill(skill_id=S_CENT, problem_type_id=PT_G1_A, seed=5, level=1)
    p_g1b = generate_for_chap3_skill(skill_id=S_DISP, problem_type_id=PT_G1_B, seed=5, level=1)
    p_g2a = generate_for_chap3_skill(skill_id=S_CENT, problem_type_id=PT_G2_A, seed=5, level=1)
    p_g2b = generate_for_chap3_skill(skill_id=S_DISP, problem_type_id=PT_G2_B, seed=5, level=1)
    assert p_hist["problem_type_id"] == PT_HIST
    assert p_g1a["problem_type_id"] == PT_G1_A
    assert p_g1b["problem_type_id"] == PT_G1_B
    assert p_g2a["problem_type_id"] == PT_G2_A
    assert p_g2b["problem_type_id"] == PT_G2_B


def test_practice_route_histogram_encoded_decoded(logged_client) -> None:
    r1 = logged_client.get(
        f"/get_next_question?skill={S_HIST}&problem_type={PT_HIST}&gen_seed=9&level=1"
    )
    r2 = logged_client.get(
        f"/get_next_question?skill={quote(S_HIST)}&problem_type={PT_HIST}&gen_seed=9&level=1"
    )
    for r in (r1, r2):
        assert r.status_code == 200, r.get_data(as_text=True)
        d = r.get_json() or {}
        assert d.get("problem_type_id") == PT_HIST
        assert d.get("visual_backed") is True
        assert d.get("visual_asset_type") == "histogram"
        assert d.get("runtime_mode") == "visual_reading_with_short_answer"
        assert d.get("check_mode") == "deterministic_auto_checked"
        assert d.get("grading_mode") == "deterministic"
        assert d.get("new_question_text")
        assert d.get("image_base64") or d.get("visual_aids")


def test_check_answer_histogram_correct_wrong(logged_client) -> None:
    seed = 21
    q = logged_client.get(
        f"/get_next_question?skill={quote(S_HIST)}&problem_type={PT_HIST}&gen_seed={seed}&level=1"
    )
    assert q.status_code == 200
    expected = generate_for_chap3_skill(skill_id=S_HIST, problem_type_id=PT_HIST, seed=seed, level=1)
    ans = str(expected["correct_answer"])
    ok = logged_client.post("/check_answer", json={"answer": ans}).get_json() or {}
    bad = logged_client.post("/check_answer", json={"answer": "__wrong__"}).get_json() or {}
    assert ok.get("correct") is True
    assert bad.get("correct") is False


def test_scenario_diversity_histogram_patterns() -> None:
    seen = set()
    stems = set()
    for seed in range(1, 25):
        p = generate_for_chap3_skill(skill_id=S_HIST, problem_type_id=PT_HIST, seed=seed, level=1)
        sid = p.get("parameters", {}).get("scenario_id")
        seen.add(sid)
        stems.add(str(p.get("question_text", "")))
    assert len(seen) >= 2
    assert len(stems) >= 2


def test_chap3_deterministic_spot_regression() -> None:
    p1 = generate_for_chap3_skill(skill_id=S_WEIGHT, problem_type_id="weighted_mean_basic", seed=7, level=1)
    p2 = generate_for_chap3_skill(skill_id=S_VARSTD, problem_type_id="variance_basic_numeric", seed=7, level=1)
    assert p1["problem_type_id"] == "weighted_mean_basic"
    assert p2["problem_type_id"] == "variance_basic_numeric"


def test_automated_visual_sample_smoke_and_export(logged_client) -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    seeds = [3, 11, 19]
    forbidden = ["Histogram", "Frequency", "Read the histogram", "interval", "count", "total frequency"]

    for idx, seed in enumerate(seeds, start=1):
        resp = logged_client.get(
            f"/get_next_question?skill={quote(S_HIST)}&problem_type={PT_HIST}&gen_seed={seed}&level=1"
        )
        assert resp.status_code == 200, resp.get_data(as_text=True)
        data = resp.get_json() or {}

        assert data.get("visual_backed") is True
        assert data.get("visual_asset_type") == "histogram"
        assert data.get("runtime_mode") == "visual_reading_with_short_answer"
        assert data.get("check_mode") == "deterministic_auto_checked"
        assert data.get("grading_mode") == "deterministic"
        assert data.get("image_base64") or data.get("visual_aids")

        payload = generate_for_chap3_skill(
            skill_id=S_HIST, problem_type_id=PT_HIST, seed=seed, level=1
        )
        q_text = str(payload.get("question_text", ""))
        exp_text = str(payload.get("explanation", ""))
        aid = (payload.get("visual_aids") or [{}])[0]
        meta = " ".join(
            [
                q_text,
                exp_text,
                str(aid.get("title", "")),
                str(aid.get("caption", "")),
                str(aid.get("alt_text", "")),
                str(aid.get("x_label", "")),
                str(aid.get("y_label", "")),
                str(payload.get("chart_title", "")),
            ]
        )
        assert "\u76f4\u65b9\u5716" in meta
        assert ("\u4eba\u6578" in meta) or ("\u6b21\u6578" in meta)
        assert ("\u7d44\u5225" in meta) or ("\u5206\u6578\u5340\u9593" in meta) or ("\u8cc7\u6599\u5340\u9593" in meta)
        for bad in forbidden:
            assert bad not in meta

        # answer consistency
        ans = str(payload["correct_answer"])
        ok = logged_client.post("/check_answer", json={"answer": ans}).get_json() or {}
        bad = logged_client.post("/check_answer", json={"answer": "__wrong__"}).get_json() or {}
        assert ok.get("correct") is True
        assert bad.get("correct") is False

        # export sample artifact (png preferred, json fallback)
        img_b64 = payload.get("image_base64", "")
        if isinstance(img_b64, str) and img_b64.strip():
            png_path = SAMPLE_DIR / f"graph3_histogram_sample_{idx:02d}.png"
            png_path.write_bytes(base64.b64decode(img_b64))
        else:
            json_path = SAMPLE_DIR / f"graph3_histogram_sample_{idx:02d}.json"
            json_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
