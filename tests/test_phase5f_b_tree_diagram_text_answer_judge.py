# -*- coding: utf-8 -*-
"""Phase 5F-B: tree diagram text-answer judge prototype tests."""

from __future__ import annotations

from core.vocational_math_b4.free_response.tree_diagram_judge import (
    build_tree_diagram_listing_payload,
    judge_tree_diagram_text_answer,
    parse_tree_diagram_text_answer,
)


def _judge(variant: str, answer: str) -> dict:
    return judge_tree_diagram_text_answer(
        build_tree_diagram_listing_payload(variant),
        answer,
    )


def test_fixed_stage_binary_tree_correct() -> None:
    result = _judge(
        "fixed_stage_binary_tree",
        "正正正、正正反、正反正、正反反、反正正、反正反、反反正、反反反",
    )
    assert result["status"] == "correct"
    assert result["score"] == 1.0
    assert result["missing_paths"] == []
    assert result["extra_paths"] == []


def test_fixed_stage_binary_tree_count_only_is_partial() -> None:
    result = _judge("fixed_stage_binary_tree", "8 種")
    assert result["status"] == "partial"
    assert result["count_only_answer"] is True
    assert result["score"] <= 0.4


def test_fixed_stage_binary_tree_missing_one_is_partial() -> None:
    result = _judge(
        "fixed_stage_binary_tree",
        "正正正、正正反、正反正、正反反、反正正、反正反、反反正",
    )
    assert result["status"] == "partial"
    assert "反反反" in result["missing_paths"]


def test_early_stopping_game_correct() -> None:
    result = _judge(
        "early_stopping_game",
        "甲甲、甲乙甲、甲乙乙、乙甲甲、乙甲乙、乙乙",
    )
    assert result["status"] == "correct"
    assert result["score"] == 1.0


def test_early_stopping_game_count_only_is_partial() -> None:
    result = _judge("early_stopping_game", "6 種")
    assert result["status"] == "partial"
    assert result["count_only_answer"] is True
    assert result["score"] <= 0.4


def test_early_stopping_game_common_four_path_mistake_is_partial() -> None:
    result = _judge("early_stopping_game", "甲甲、甲乙甲、乙乙、乙甲乙")
    assert result["status"] == "partial"
    assert "甲乙乙" in result["missing_paths"]
    assert "乙甲甲" in result["missing_paths"]


def test_early_stopping_game_fixed_three_round_wrong_is_not_correct() -> None:
    result = _judge(
        "early_stopping_game",
        "甲甲甲、甲甲乙、甲乙甲、甲乙乙、乙甲甲、乙甲乙、乙乙甲、乙乙乙",
    )
    assert result["status"] in {"partial", "incorrect"}
    assert result["status"] != "correct"
    assert "先贏兩場即停止" in result["main_issue"]
    assert "甲甲甲" in result["extra_paths"]
    assert "乙乙乙" in result["extra_paths"]


def test_duplicated_paths_are_reported() -> None:
    result = _judge(
        "early_stopping_game",
        "甲甲、甲甲、甲乙甲、甲乙乙、乙甲甲、乙甲乙、乙乙",
    )
    assert result["status"] == "partial"
    assert result["duplicated_paths"] == ["甲甲"]


def test_parser_supports_newline_and_punctuation() -> None:
    payload = build_tree_diagram_listing_payload("early_stopping_game")
    parsed = parse_tree_diagram_text_answer(
        "共有 6 種：\n甲甲；甲乙甲，甲乙乙\n乙甲甲、乙甲乙 乙乙。",
        payload["path_labels"],
    )
    assert parsed["detected_paths"] == [
        "甲甲",
        "甲乙甲",
        "甲乙乙",
        "乙甲甲",
        "乙甲乙",
        "乙乙",
    ]
    result = judge_tree_diagram_text_answer(payload, "甲甲；甲乙甲，甲乙乙\n乙甲甲、乙甲乙 乙乙。")
    assert result["status"] == "correct"


def test_empty_answer_needs_review_and_is_not_correct() -> None:
    result = _judge("fixed_stage_binary_tree", "   ")
    assert result["status"] == "needs_review"
    assert result["status"] != "correct"
    assert result["teacher_review_needed"] is True


def test_parametric_fixed_stage_binary_tree_changes_by_index() -> None:
    first = build_tree_diagram_listing_payload("fixed_stage_binary_tree", index=0)
    second = build_tree_diagram_listing_payload("fixed_stage_binary_tree", index=1)
    assert first["question_text"] != second["question_text"]
    assert first["expected_paths"] != second["expected_paths"]
    assert first["expected_count"] in {4, 8}
    assert second["expected_count"] in {4, 8}


def test_parametric_early_stopping_game_red_blue_correct() -> None:
    payload = build_tree_diagram_listing_payload("early_stopping_game", index=1)
    assert payload["path_labels"] == ["紅", "藍"]
    assert payload["expected_paths"] == ["紅紅", "紅藍紅", "紅藍藍", "藍紅紅", "藍紅藍", "藍藍"]
    result = judge_tree_diagram_text_answer(
        payload,
        "紅紅、紅藍紅、紅藍藍、藍紅紅、藍紅藍、藍藍",
    )
    assert result["status"] == "correct"


def test_parametric_fixed_stage_binary_tree_two_stage_correct() -> None:
    payload = build_tree_diagram_listing_payload("fixed_stage_binary_tree", index=1)
    assert payload["expected_count"] == 4
    result = judge_tree_diagram_text_answer(
        payload,
        "成成、成敗、敗成、敗敗",
    )
    assert result["status"] == "correct"
