from __future__ import annotations

import uuid
from urllib.parse import quote

import pytest

from app import create_app
from core.vocational_math_b4.generators.chap3_statistical_measures import (
    SAMPLING_METHODS_CLASSIFICATION_CONTEXTS,
    STRATIFIED_ALLOCATION_NUMERIC_POOL,
    SYSTEMATIC_INTERVAL_NUMERIC_POOL,
)
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill
from models import User, db


S_METHODS = "vh_?詨飛B4_SamplingMethods"
PT_METHODS = "sampling_methods_classification_choice"
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
            username=f"b4_sampling_param_{uuid.uuid4().hex[:10]}",
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


def _wrong(answer: str) -> str:
    return next(x for x in ("1", "2", "3", "4") if x != answer)


def test_parameterized_scenario_pool_shapes() -> None:
    assert set(SAMPLING_METHODS_CLASSIFICATION_CONTEXTS.keys()) == {
        "simple_random",
        "systematic",
        "stratified",
        "cluster",
    }
    for family, rows in SAMPLING_METHODS_CLASSIFICATION_CONTEXTS.items():
        assert len(rows) >= 2, family
    assert len(SYSTEMATIC_INTERVAL_NUMERIC_POOL) >= 5
    assert len(STRATIFIED_ALLOCATION_NUMERIC_POOL) >= 5


def test_repeated_generation_parameter_diversity() -> None:
    payloads = [
        generate_for_chap3_skill(skill_id=S_METHODS, problem_type_id=PT_METHODS, seed=i, level=1)
        for i in range(1, 31)
    ]
    texts = [str(p["question_text"]) for p in payloads]
    scenarios = [str(p["scenario_id"]) for p in payloads]
    signatures = [str(p.get("parameter_signature", "")) for p in payloads]
    assert len(set(texts)) >= 15
    assert len(set(scenarios)) >= 8
    assert len(set(signatures)) >= 15
    assert (1 - len(set(texts)) / len(texts)) <= 0.5
    assert all(a != b for a, b in zip(texts, texts[1:]))


def test_systematic_interval_answer_consistency() -> None:
    rows = []
    for i in range(1, 61):
        p = generate_for_chap3_skill(skill_id=S_METHODS, problem_type_id=PT_METHODS, seed=i, level=1)
        sig = str(p.get("parameter_signature", ""))
        if sig.startswith("systematic_interval:"):
            rows.append(p)
    assert rows
    for p in rows:
        num = p["parameters"]["numeric_params"]
        n_total = int(num["N"])
        sample_n = int(num["n"])
        k = int(num["k"])
        assert n_total % sample_n == 0
        assert k == n_total // sample_n
        assert str(p["answer"]) in _choice_codes(p["choices"])
        assert "÷" in str(p["explanation"]) or "間距" in str(p["explanation"])


def test_stratified_allocation_answer_consistency() -> None:
    rows = []
    for i in range(1, 61):
        p = generate_for_chap3_skill(skill_id=S_METHODS, problem_type_id=PT_METHODS, seed=i, level=1)
        sig = str(p.get("parameter_signature", ""))
        if sig.startswith("stratified_allocation:"):
            rows.append(p)
    assert rows
    for p in rows:
        num = p["parameters"]["numeric_params"]
        sample_total = int(num["sample_total"])
        layer_count = int(num["layer_count"])
        total = int(num["population_total"])
        expected = sample_total * layer_count // total
        assert sample_total * layer_count % total == 0
        assert expected == int(num["answer_people"])
        assert str(p["answer"]) in _choice_codes(p["choices"])
        assert "×" in str(p["explanation"]) or "比例" in str(p["explanation"])


def test_method_classification_coverage() -> None:
    seen = set()
    for i in range(1, 31):
        p = generate_for_chap3_skill(skill_id=S_METHODS, problem_type_id=PT_METHODS, seed=i, level=1)
        q = str(p["question_text"])
        if any(k in q for k in ["抽籤", "摸彩", "亂數"]):
            seen.add("simple_random")
        if any(k in q for k in ["每隔", "間距", "第"]):
            seen.add("systematic")
        if any(k in q for k in ["分層", "比例"]):
            seen.add("stratified")
        if any(k in q for k in ["社區", "班級", "部門", "群組"]):
            seen.add("cluster")
    assert seen == {"simple_random", "systematic", "stratified", "cluster"}


def test_textbook_boundary() -> None:
    forbidden = ["民調偏誤", "樣本平均數", "母體平均數", "平均數", "標準差", "中位數"]
    for i in range(1, 31):
        p = generate_for_chap3_skill(skill_id=S_METHODS, problem_type_id=PT_METHODS, seed=i, level=1)
        blob = " ".join([str(p["question_text"]), str(p["explanation"])])
        for bad in forbidden:
            assert bad not in blob


def test_choice_and_check_answer_regression(logged_client) -> None:
    for i in range(1, 16):
        expected = generate_for_chap3_skill(
            skill_id=S_METHODS, problem_type_id=PT_METHODS, seed=i, level=1
        )
        r = logged_client.get(
            f"/get_next_question?skill={quote(S_METHODS)}&problem_type={PT_METHODS}&gen_seed={i}&level=1"
        )
        assert r.status_code == 200
        d = r.get_json() or {}
        ans = str(expected["answer"])
        assert d.get("choices")
        assert ans in _choice_codes(d["choices"])
        ok = logged_client.post("/check_answer", json={"answer": ans}).get_json() or {}
        alias = chr(ord("A") + int(ans) - 1)
        ok_alias = logged_client.post("/check_answer", json={"answer": alias}).get_json() or {}
        bad = logged_client.post("/check_answer", json={"answer": _wrong(ans)}).get_json() or {}
        assert ok.get("correct") is True
        assert ok_alias.get("correct") is True
        assert bad.get("correct") is False


def test_regression_statistical_basic_not_broken() -> None:
    p = generate_for_chap3_skill(skill_id=S_BASIC, problem_type_id=PT_BASIC, seed=1, level=1)
    assert p.get("choices")
    assert p.get("scenario_family") == "statistical_basic_concepts_boundary_aligned"
