from __future__ import annotations

from collections import Counter
from urllib.parse import quote

from app import app
from core.routes.practice import _build_b4_tree_diagram_runtime_payload
from core.vocational_math_b4.free_response.tree_diagram_judge import build_tree_diagram_listing_payload


SKILL = "vh_數學B4_TreeDiagramCounting"


def _is_open_ended_phrase(text: str) -> bool:
    forbidden = ["請說明", "請簡述", "請討論", "簡述理由", "提出理由"]
    return any(t in text for t in forbidden)


def test_scenario_diversity_over_20_generation() -> None:
    payloads = [_build_b4_tree_diagram_runtime_payload(tree_diagram_index=i) for i in range(20)]
    q_texts = [str(p.get("question_text", "")) for p in payloads]
    scenario_ids = [str(p.get("scenario_id", "")) for p in payloads]
    scenario_families = [str(p.get("scenario_family", "")) for p in payloads]
    param_sigs = [str(p.get("parameter_signature", "")) for p in payloads]

    assert len(set(q_texts)) >= 8
    assert len(set(scenario_ids)) >= 8
    assert len(set(scenario_families)) >= 5
    assert len(set(param_sigs)) >= 8


def test_no_adjacent_duplicate_for_core_identifiers() -> None:
    payloads = [_build_b4_tree_diagram_runtime_payload(tree_diagram_index=i) for i in range(20)]
    for prev, cur in zip(payloads, payloads[1:]):
        assert str(prev.get("question_text", "")) != str(cur.get("question_text", ""))
        assert str(prev.get("scenario_id", "")) != str(cur.get("scenario_id", ""))
        assert str(prev.get("parameter_signature", "")) != str(cur.get("parameter_signature", ""))


def test_handwriting_ai_checked_contract() -> None:
    payload = _build_b4_tree_diagram_runtime_payload(tree_diagram_index=5)
    assert payload.get("answer_type") == "handwriting"
    assert payload.get("requires_handwriting") is True
    assert payload.get("runtime_mode") == "visual_or_handwriting_ai_checked"
    assert payload.get("check_mode") in {"handwriting_ai_checked", "review_mode"}
    assert payload.get("grading_mode") in {"ai_judged_free_response", "ai_assisted_review"}
    assert payload.get("problem_type_id") == "tree_diagram_listing"
    assert payload.get("expected_answer_schema") or payload.get("rubric")


def test_textbook_boundedness_and_non_choice() -> None:
    payload = _build_b4_tree_diagram_runtime_payload(tree_diagram_index=6)
    text = str(payload.get("question_text", ""))
    assert ("樹狀圖" in text) or ("列舉" in text)
    assert payload.get("answer_type") == "handwriting"
    assert payload.get("choices") in (None, [])


def test_fake_diversity_detection_best_of_three_same_family() -> None:
    p_named = build_tree_diagram_listing_payload("early_stopping_game", index=0)
    p_red_blue = build_tree_diagram_listing_payload("early_stopping_game", index=1)
    p_ab = build_tree_diagram_listing_payload("early_stopping_game", index=2)
    assert p_named.get("scenario_family") == "best_of_three_binary_match"
    assert p_red_blue.get("scenario_family") == "best_of_three_binary_match"
    assert p_ab.get("scenario_family") == "best_of_three_binary_match"


def test_route_regression_no_adjacent_duplicate_and_not_open_ended() -> None:
    with app.test_client() as client:
        prev_q = ""
        prev_sid = ""
        for _ in range(20):
            r = client.get(f"/get_next_question?skill={quote(SKILL)}&level=1")
            assert r.status_code == 200
            data = r.get_json() or {}
            q = str(data.get("question_text", ""))
            sid = str(data.get("scenario_id", ""))
            assert q
            assert not _is_open_ended_phrase(q)
            if prev_q:
                assert q != prev_q
            if prev_sid and sid:
                assert sid != prev_sid
            prev_q = q
            prev_sid = sid


def test_final_coverage_regression_smoke() -> None:
    # Minimal smoke: ensure the skill still returns handwriting runtime payload.
    with app.test_client() as client:
        r = client.get(f"/get_next_question?skill={quote(SKILL)}&level=1")
        assert r.status_code == 200
        data = r.get_json() or {}
        assert data.get("answer_type") == "handwriting"
        assert data.get("requires_handwriting") is True
