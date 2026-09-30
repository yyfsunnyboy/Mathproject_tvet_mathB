# -*- coding: utf-8 -*-
import importlib
import json
import random
from types import SimpleNamespace

import pytest

from core import practice_type_rotation as ptr

SECTION_3_TYPES = "vh_數學B3_SubSection_4_1_1"
SECTION_7_TYPES = "vh_數學B3_SubSection_1_2_1"
SECTION_EXAMPLE_INCLASS = "vh_數學B3_SubSection_4_5_1"


def _pool(section):
    return ptr.get_practice_type_pool(section, module=importlib.import_module(f"skills.{section}"))


def _first_round(section, types, seed=0):
    rng = random.Random(seed)
    state = ptr.new_state(section, types, rng)
    picks = []
    for _ in range(state["n"]):
        picks.append(ptr.next_pick(state, types, rng))
    return state, picks


def test_type_key_prefers_problem_type_id_and_never_uses_example_identity():
    spec = {
        "component_id": "src_1",
        "textbook_example_id": 1,
        "problem_type_id": "pt",
        "family_id": "fam",
        "practice_type_key": "k",
    }
    assert ptr.resolve_type_key(spec) == ("pt", "problem_type_id")
    assert ptr.resolve_type_key({"component_id": "src_1", "family_id": "fam"}) == ("fam", "family_id")
    assert ptr.resolve_type_key({"component_id": "src_1", "textbook_example_id": 9}) == ("", "")


def test_unresolved_component_marks_pool_unreliable():
    pool = ptr.build_type_pool([{"component_id": "a", "problem_type_id": "x"}, {"component_id": "b"}])
    assert pool["reliable"] is False
    assert pool["unresolved_components"] == ["b"]
    assert set(pool["types"]) == {"x", "component:b"}


@pytest.mark.parametrize(
    "section, expected_types",
    [(SECTION_3_TYPES, 3), (SECTION_7_TYPES, 7)],
)
def test_first_round_length_equals_unique_type_count(section, expected_types):
    types = _pool(section)
    assert len(types) == expected_types
    state, picks = _first_round(section, types)
    assert state["n"] == expected_types
    assert len(picks) == expected_types
    assert sorted(p["type_key"] for p in picks) == sorted(types)
    assert all(p["round"] == 1 for p in picks)


def test_example_and_in_class_of_same_type_only_one_is_served_in_first_round():
    types = _pool(SECTION_EXAMPLE_INCLASS)
    table_lookup = types["common_log_table_lookup"]
    ids = [c["component_id"] for c in table_lookup]
    assert {"src_12221", "src_12222"} <= set(ids)
    kinds = {c["component_id"]: c["source_kind"] for c in table_lookup}
    assert kinds["src_12221"] == "textbook_example"
    assert kinds["src_12222"] == "in_class_practice"
    for seed in range(20):
        _, picks = _first_round(SECTION_EXAMPLE_INCLASS, types, seed)
        assert len(picks) == 2
        served_components = [p["component_id"] for p in picks]
        assert sum(1 for cid in served_components if cid in ids) == 1


def test_question_count_is_dynamic_not_configured():
    for n in (1, 2, 5, 11):
        specs = []
        for t in range(n):
            specs.append({"component_id": f"ex_{t}", "problem_type_id": f"type_{t}"})
            specs.append({"component_id": f"ic_{t}", "problem_type_id": f"type_{t}"})
        types = ptr.build_type_pool(specs)["types"]
        state, picks = _first_round("synthetic", types)
        assert len(picks) == n == state["n"]


def _serve(state, types, rng, uid):
    pick = ptr.next_pick(state, types, rng)
    if pick is not None:
        ptr.register_served_question(state, types, uid, pick["type_key"])
    return pick


def test_wrong_type_is_deferred_until_other_unseen_types_finish_then_retried():
    types = _pool(SECTION_3_TYPES)
    rng = random.Random(3)
    state = ptr.new_state(SECTION_3_TYPES, types, rng)

    first = _serve(state, types, rng, "q1")
    assert ptr.record_result(state, types, "q1", False) == first["type_key"]
    assert ptr.type_status(state, types)[first["type_key"]] == ptr.STATUS_WEAK

    second = _serve(state, types, rng, "q2")
    ptr.record_result(state, types, "q2", True)
    third = _serve(state, types, rng, "q3")
    ptr.record_result(state, types, "q3", True)
    round_one = [first["type_key"], second["type_key"], third["type_key"]]
    assert sorted(round_one) == sorted(types)
    assert state["r"] == 1

    retry = _serve(state, types, rng, "q4")
    assert retry["type_key"] == first["type_key"]
    assert retry["round"] == 2
    if len(types[first["type_key"]]) > 1:
        assert retry["component_id"] != first["component_id"]
    assert not state["c"]

    ptr.record_result(state, types, "q4", True)
    assert state["c"] == 1
    assert ptr.summarize(state, types)["section_completed"] is True
    assert ptr.next_pick(state, types, rng) is None


def test_weak_type_stays_weak_on_resubmit_of_same_question():
    types = _pool(SECTION_3_TYPES)
    rng = random.Random(1)
    state = ptr.new_state(SECTION_3_TYPES, types, rng)
    pick = _serve(state, types, rng, "q1")
    ptr.record_result(state, types, "q1", False)
    assert ptr.record_result(state, types, "q1", True) is None
    assert ptr.type_status(state, types)[pick["type_key"]] == ptr.STATUS_WEAK


def test_repeated_weak_retry_rotates_candidates_within_type():
    types = _pool(SECTION_EXAMPLE_INCLASS)
    rng = random.Random(5)
    state = ptr.new_state(SECTION_EXAMPLE_INCLASS, types, rng)
    served = []
    uid = 0
    while len(served) < 6:
        uid += 1
        pick = _serve(state, types, rng, f"q{uid}")
        correct = pick["type_key"] != "common_log_table_lookup"
        ptr.record_result(state, types, f"q{uid}", correct)
        if pick["type_key"] == "common_log_table_lookup":
            served.append(pick["component_id"])
    candidate_count = len(types["common_log_table_lookup"])
    assert len(set(served[:candidate_count])) == candidate_count


def test_state_is_compact_for_cookie_session():
    types = _pool(SECTION_7_TYPES)
    rng = random.Random(0)
    state = ptr.new_state(SECTION_7_TYPES, types, rng)
    for i in range(30):
        pick = _serve(state, types, rng, f"uid-{i:032d}")
        if pick is None:
            break
        ptr.record_result(state, types, f"uid-{i:032d}", i % 3 != 0)
    assert len(json.dumps(state)) < 400


def _row(skill_id, chapter, section, order, curriculum="vocational", volume="數學B3"):
    return SimpleNamespace(
        skill_id=skill_id, curriculum=curriculum, volume=volume,
        chapter=chapter, section=section, display_order=order,
    )


def test_resolve_next_section_follows_textbook_order_within_chapter():
    ch4 = "第4章 指數與對數"
    rows = [
        _row("s_4_2_1", ch4, "4-2 指數函數及其圖形", 1),
        _row("s_4_1_2", ch4, "4-1 指數", 2),
        _row("s_4_1_1", ch4, "4-1 指數", 1),
        _row("s_4_1_3", ch4, "4-1 指數", 3),
        _row("s_1_2_1", "第1章 數列與級數", "1-2 等比數列與等比級數", 1),
        _row("s_1_2_4", "第1章 數列與級數", "1-2 等比數列與等比級數", 5),
        _row("s_2_1_1", "第2章 不等式", "2-1 一元一次方程式", 1),
        _row("other", ch4, "4-1 指數", 1, volume="數學B2"),
    ]
    assert ptr.resolve_next_section("s_4_1_1", rows) == "s_4_1_2"
    assert ptr.resolve_next_section("s_4_1_3", rows) == "s_4_2_1"
    assert ptr.resolve_next_section("s_1_2_1", rows) == "s_1_2_4"
    assert ptr.resolve_next_section("s_4_1_2", rows, is_available=lambda s: s != "s_4_1_3") == "s_4_2_1"


def test_resolve_next_section_never_crosses_into_next_chapter():
    rows = [
        _row("s_1_2_4", "第1章 數列與級數", "1-2 等比數列與等比級數", 5),
        _row("s_2_1_1", "第2章 不等式", "2-1 一元一次方程式", 1),
        _row("s_4_2_1", "第4章 指數與對數", "4-2 指數函數及其圖形", 1),
    ]
    assert ptr.resolve_next_section("s_1_2_4", rows) == ""
    assert ptr.resolve_next_section("s_4_2_1", rows) == ""
    assert ptr.resolve_next_section("s_1_2_4", rows, is_available=lambda s: False) == ""


def test_chapter_progress_counters_and_completion():
    key = ptr.chapter_key("vocational", "數學B3", "第1章")
    progress = ptr.ensure_chapter_progress(None, key)
    ptr.record_chapter_verdict(progress, False, section_completed=False)
    ptr.record_chapter_verdict(progress, True, section_completed=False)
    ptr.record_chapter_verdict(progress, True, section_completed=True)
    assert ptr.ensure_chapter_progress(progress, key) is progress
    ptr.mark_chapter_completed(progress, "s_last")
    summary = ptr.chapter_summary(progress)
    assert summary == {
        "total_answered": 3,
        "correct": 2,
        "wrong": 1,
        "accuracy": 66.7,
        "types_completed": 2,
        "sections_completed": 1,
        "chapter_completed": True,
    }
    assert ptr.ensure_chapter_progress(progress, key)["a"] == 0
    assert ptr.ensure_chapter_progress({"ch": "other", "a": 5}, key)["a"] == 0


def test_route_glue_serves_one_per_type_and_reports_completion(monkeypatch):
    from app import create_app
    from core.routes import practice as practice_routes

    module = importlib.import_module(f"skills.{SECTION_3_TYPES}")
    app = create_app()
    app.config["TESTING"] = True
    anchor = _row(SECTION_3_TYPES, "第4章", "4-1 指數", 1)
    monkeypatch.setattr(practice_routes, "_practice_chapter_scope", lambda sid: (anchor, [anchor]))
    monkeypatch.setattr(practice_routes, "_practice_type_rotation_next_section", lambda sid, rows: "next_skill")

    with app.test_request_context("/get_next_question"):
        served = []
        for i in range(3):
            pick = practice_routes._practice_type_rotation_next(SECTION_3_TYPES, module)
            practice_routes._practice_type_rotation_register(SECTION_3_TYPES, module, f"uid{i}", pick["type_key"])
            served.append(pick)
        assert len({p["type_key"] for p in served}) == 3
        assert served[0]["first_round_size"] == 3

        outs = []
        for i, pick in enumerate(served):
            out = {"correct": i != 0, "status": "correct" if i != 0 else "incorrect"}
            practice_routes._practice_type_rotation_apply_verdict(f"uid{i}", SECTION_3_TYPES, out)
            outs.append(out["practice_type_rotation"])
        assert outs[0]["type_status"] == ptr.STATUS_WEAK
        assert outs[-1]["section_completed"] is False
        assert outs[-1]["weak_types"] == [served[0]["type_key"]]

        retry = practice_routes._practice_type_rotation_next(SECTION_3_TYPES, module)
        assert retry["type_key"] == served[0]["type_key"]
        assert retry["round"] == 2
        practice_routes._practice_type_rotation_register(SECTION_3_TYPES, module, "uid-retry", retry["type_key"])
        out = {"correct": True, "status": "correct"}
        practice_routes._practice_type_rotation_apply_verdict("uid-retry", SECTION_3_TYPES, out)
        assert out["practice_type_rotation"]["section_completed"] is True
        assert out["practice_type_rotation"]["next_section_skill_id"] == "next_skill"
        assert out["practice_type_rotation"]["chapter_completed"] is False
        assert practice_routes._practice_chapter_completed_summary(SECTION_3_TYPES) is None


def test_last_section_of_chapter_completes_chapter_and_stops(monkeypatch):
    from app import create_app
    from core.routes import practice as practice_routes

    module = importlib.import_module(f"skills.{SECTION_3_TYPES}")
    app = create_app()
    app.config["TESTING"] = True
    anchor = _row(SECTION_3_TYPES, "第9章", "9-9 最後一節", 1)
    monkeypatch.setattr(practice_routes, "_practice_chapter_scope", lambda sid: (anchor, [anchor]))

    with app.test_request_context("/get_next_question"):
        verdicts = [False, True, True, True]
        last = None
        for i, correct in enumerate(verdicts):
            pick = practice_routes._practice_type_rotation_next(SECTION_3_TYPES, module)
            practice_routes._practice_type_rotation_register(SECTION_3_TYPES, module, f"u{i}", pick["type_key"])
            out = {"correct": correct, "status": "correct" if correct else "incorrect"}
            practice_routes._practice_type_rotation_apply_verdict(f"u{i}", SECTION_3_TYPES, out)
            last = out["practice_type_rotation"]
        assert last["section_completed"] is True
        assert last["next_section_skill_id"] == ""
        assert last["chapter_completed"] is True
        assert last["chapter_summary"] == {
            "total_answered": 4,
            "correct": 3,
            "wrong": 1,
            "accuracy": 75.0,
            "types_completed": 3,
            "sections_completed": 1,
            "chapter_completed": True,
        }
        assert practice_routes._practice_chapter_completed_summary(SECTION_3_TYPES)["total_answered"] == 4
        assert practice_routes._practice_chapter_completed_summary(SECTION_7_TYPES) is None


def test_get_next_question_stops_after_chapter_completed():
    from urllib.parse import quote

    client = _student_client()
    with client.session_transaction() as sess:
        sess[ptr.CHAPTER_SESSION_KEY] = {
            "ch": "x", "a": 5, "k": 4, "t": 4, "s": 2, "done": 1, "last": ptr.section_token(SECTION_3_TYPES),
        }
    payload = client.get(
        f"/get_next_question?skill={quote(SECTION_3_TYPES)}&level=1&mode=type_rotation"
    ).get_json()
    assert payload["chapter_completed"] is True
    assert payload["chapter_summary"]["accuracy"] == 80.0
    assert payload["chapter_summary"]["sections_completed"] == 2
    assert "question_text" not in payload


def test_route_glue_falls_back_when_types_are_unreliable():
    from app import create_app
    from core.routes import practice as practice_routes

    module = SimpleNamespace(
        GENERATOR_KEYS=["src_1", "src_2"],
        GENERATOR_SPECS=[{"component_id": "src_1", "problem_type_id": "a"}, {"component_id": "src_2"}],
    )
    app = create_app()
    with app.test_request_context("/get_next_question"):
        assert practice_routes._practice_type_rotation_next("s", module) is None


def _student_client():
    from app import create_app

    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "1"
        sess["_fresh"] = True
    return client


def test_chapter_review_label_and_section_order_come_from_curriculum_rows():
    from core.routes import practice as practice_routes

    assert practice_routes._chapter_review_label("1 坐標系與函數圖形") == "第1章 坐標系與函數圖形"
    assert practice_routes._chapter_review_label("第3章 向 量") == "第3章 向 量"
    ch4 = "第4章 指數與對數"
    rows = [
        _row("s_4_2_1", ch4, "4-2 指數函數及其圖形", 1),
        _row("s_4_1_2", ch4, "4-1 指數", 2),
        _row("s_4_1_1", ch4, "4-1 指數", 1),
    ]
    assert practice_routes._chapter_review_ordered_sections(rows) == ["s_4_1_1", "s_4_1_2", "s_4_2_1"]


def test_single_chapter_entry_redirects_to_chapter_review(monkeypatch):
    from core.routes import practice as practice_routes

    monkeypatch.setattr(
        practice_routes, "_chapter_review_entry",
        lambda chapter, curriculum="", volume="": {"label": "第4章 指數與對數", "first_section": SECTION_3_TYPES},
    )
    client = _student_client()
    resp = client.get("/adaptive_practice?mode=single&skill_ids=4+指數與對數&curriculum=vocational&volume=數學B3")
    assert resp.status_code == 302
    assert "chapter_review=start" in resp.headers["Location"]
    assert "/practice/" in resp.headers["Location"]


def test_chapter_review_page_shows_review_header_without_adaptive_v2_labels(monkeypatch):
    from urllib.parse import quote

    from core.routes import practice as practice_routes

    anchor = _row(SECTION_3_TYPES, "第4章 指數與對數", "4-1 指數", 1)
    monkeypatch.setattr(practice_routes, "_practice_chapter_scope", lambda sid: (anchor, [anchor]))
    client = _student_client()
    body = client.get(f"/practice/{quote(SECTION_3_TYPES)}?chapter_review=start").get_data(as_text=True)
    assert "<title>第4章 指數與對數｜本章總複習</title>" in body
    assert "本章總複習｜第4章 指數與對數" in body
    for label in ("本章正確率", "已作答", "答對", "待補題型", "本章複習進度", "目前小節", "本節題型完成數", "下一小節"):
        assert label in body
    assert "0 / 3" in body
    assert '"await_start": true' in body
    for forbidden in ("Local APR", "PPO", "微技能待診斷", "動態精熟軌跡", "開始診斷"):
        assert forbidden not in body

    plain = client.get(f"/practice/{quote(SECTION_3_TYPES)}").get_data(as_text=True)
    assert 'id="chapter-review-banner"' not in plain
    assert "const CHAPTER_REVIEW = null;" in plain


def test_get_next_question_type_rotation_is_opt_in():
    from urllib.parse import quote

    client = _student_client()
    default = client.get(f"/get_next_question?skill={quote(SECTION_3_TYPES)}&level=1").get_json()
    assert default.get("practice_type_rotation") is None

    served = []
    for _ in range(3):
        payload = client.get(
            f"/get_next_question?skill={quote(SECTION_3_TYPES)}&level=1&mode=type_rotation"
        ).get_json()
        rotation = payload["practice_type_rotation"]
        assert payload["component_id"] == rotation["component_id"]
        assert rotation["first_round_size"] == 3
        served.append(rotation["type_key"])
    assert sorted(served) == sorted(_pool(SECTION_3_TYPES))
