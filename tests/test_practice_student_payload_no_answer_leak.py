# -*- coding: utf-8 -*-
"""/get_next_question must not send the answer before the student submits.

The full question stays in the server-side store, where /check_answer and the AI tutor read it by question_uid.
"""
from __future__ import annotations

import copy
from typing import Any
from urllib.parse import quote

import pytest

from _practice_served_question import stored_question
from app import create_app
from core.practice_student_payload import is_private_key, student_question_payload
from models import User

LEAKED_DOMAIN_FIELDS = {"closer_line", "farther_line", "comparison_result", "comparison_relation", "distances",
                        "target_direction", "raw_scores", "path_labels", "givens", "raw_givens", "target"}

CROSS_SKILLS = [
    "gh_MathematicalExpectation",
    "gh_Combination",
    "vh_數學B1_DistanceBetweenPointAndLine",
    "vh_數學B4_CumulativeFrequencyTablesAndGraphs",
    "jh_數學1上_AgeProblems",
]


def _private_paths(node: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            if is_private_key(key) or key in ("correct", "is_correct"):
                found.append(here)
            found.extend(_private_paths(value, here))
    elif isinstance(node, list):
        for item in node:
            found.extend(_private_paths(item, f"{path}[]"))
    return found


def _wrong(answer: Any) -> Any:
    if isinstance(answer, dict):
        return {key: "__wrong__" for key in answer}
    return "-98765" if str(answer).strip() != "-98765" else "13579"


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user_id = User.query.order_by(User.id).first().id
    test_client = app.test_client()
    with test_client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
    return test_client


def _serve(client, skill_id: str, seed: int) -> dict:
    response = client.get(f"/get_next_question?skill={quote(skill_id)}&level=1&gen_seed={seed}")
    assert response.status_code == 200
    return response.get_json()


def _check(client, question: dict, answer: Any) -> dict:
    body = {"skill_id": question["skill_id"], "question_uid": question["question_uid"],
            "problem_type_id": question.get("problem_type_id") or "", "answer": answer}
    if isinstance(answer, dict):
        body["answers"] = answer
    response = client.post("/check_answer", json=body)
    assert response.status_code == 200
    return response.get_json()


def test_filter_drops_nested_answers_and_keeps_rendering_fields() -> None:
    payload = {
        "skill_id": "s", "question_uid": "u", "question_text": "Q", "answer": "7", "correct_answer": "7",
        "display_answer": "7", "semantic_answer": "7", "solution": "x", "reference_solution": "x", "hint_internal": 1,
        "choices": [{"label": "A", "text": "7", "correct": True}, {"label": "B", "text": "8", "is_correct": False}],
        "visual_spec": {"type": "line", "points": [[0, 1]]},
        "metadata": {"semantic_answer": "7", "givens": {"a": 1}, "stem_structure": {"kind": "plain"}},
        "answer_contract": {
            "answer_type": "multi_part", "checker_key": "multi_part_checker", "semantic_answer": "7",
            "closer_line": "L_1", "comparison_result": "<", "expected_drawing_spec": {"slope": 2},
            "drawing_check": {"enabled": True, "mode": "line", "expected_from": [0, 0], "expected_to": [1, 1]},
            "parts": [{"key": "p1", "label": "(1)", "expected_answer": "7", "answer_format_example": "7",
                       "tolerance": 0.1, "choices": [{"label": "A", "value": "7", "correct": True}]}],
        },
        "table_data": {"rows": [["x", "1"], ["y", "2"]], "visible_table": [["x", "1"], ["y", ""]],
                       "blank_cells": [{"row": 1, "col": 1, "field_key": "c"}], "expected_answers": {"c": "2"}},
    }
    original = copy.deepcopy(payload)
    out = student_question_payload(payload)

    assert payload == original
    assert _private_paths(out) == []
    assert not set(out) & {"answer", "solution", "reference_solution", "hint_internal"}
    assert not LEAKED_DOMAIN_FIELDS & set(out["answer_contract"])
    assert out["answer_contract"]["drawing_check"] == {"enabled": True, "mode": "line"}
    assert out["answer_contract"]["parts"] == [{"key": "p1", "label": "(1)", "choices": [{"label": "A", "value": "7"}]}]
    assert out["metadata"] == {"stem_structure": {"kind": "plain"}}
    assert out["choices"] == [{"label": "A", "text": "7"}, {"label": "B", "text": "8"}]
    assert out["visual_spec"] == payload["visual_spec"] and out["question_text"] == "Q"
    assert out["table_data"]["rows"] == [["x", "1"], ["y", ""]]


@pytest.mark.parametrize("skill_id", CROSS_SKILLS)
def test_served_question_has_no_answer_but_the_server_copy_does(client, skill_id: str) -> None:
    for seed in (3, 11, 29):
        question = _serve(client, skill_id, seed)
        assert question.get("question_uid") and (question.get("question_text") or question.get("new_question_text"))
        assert _private_paths(question) == [], (skill_id, seed)
        assert not LEAKED_DOMAIN_FIELDS & set(question.get("answer_contract") or {})
        assert not LEAKED_DOMAIN_FIELDS & set(question.get("metadata") or {})
        assert stored_question(question).get("correct_answer") not in (None, "", {}, [])


@pytest.mark.parametrize("skill_id", CROSS_SKILLS)
def test_checker_grades_with_the_server_answer(client, skill_id: str) -> None:
    question = _serve(client, skill_id, 5)
    answer = stored_question(question)["correct_answer"]
    assert _check(client, question, answer).get("correct") is True

    question = _serve(client, skill_id, 6)
    wrong = _check(client, question, _wrong(stored_question(question)["correct_answer"]))
    assert wrong.get("correct") is False
    assert wrong.get("correct_answer_display") or wrong.get("result")


def test_client_supplied_answer_is_ignored(client) -> None:
    question = _serve(client, "gh_MathematicalExpectation", 7)
    response = client.post("/check_answer", json={
        "skill_id": question["skill_id"], "question_uid": question["question_uid"], "answer": "-98765",
        "correct_answer": "-98765", "answer_contract": {"semantic_answer": "-98765"},
    })
    assert response.get_json().get("correct") is False


def test_ai_tutor_gets_the_server_answer_after_a_wrong_submission(client, monkeypatch) -> None:
    import core.routes.analysis as analysis

    question = _serve(client, "gh_MathematicalExpectation", 9)
    trusted = stored_question(question)
    assert _check(client, question, "-98765").get("correct") is False

    seen: dict[str, Any] = {}
    real_build = analysis.build_chat_prompt

    def capture_build(*args, **kwargs):
        seen.update(kwargs)
        return real_build(*args, **kwargs)

    monkeypatch.setattr(analysis, "build_chat_prompt", capture_build)
    monkeypatch.setattr(analysis, "get_chat_response", lambda prompt, **_kwargs: {
        "hint_focus": "先列出期望值公式", "guided_question": "每個結果的機率是多少？", "micro_step": "列出機率",
        "follow_up_prompts": [], "forbidden": False,
    })
    response = client.post("/chat_ai", json={
        "question_uid": question["question_uid"], "question": "我哪裡錯了？", "student_answer": "-98765",
        "question_text": "偽造題目", "correct_answer": "偽造答案",
    })

    assert response.status_code == 200
    assert seen.get("correct_answer") == str(trusted["correct_answer"]).strip()
    assert "偽造" not in str(seen.get("full_question_context") or "") + str(seen.get("correct_answer"))
