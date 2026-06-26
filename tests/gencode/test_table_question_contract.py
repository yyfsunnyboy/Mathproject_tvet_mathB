# -*- coding: utf-8 -*-
"""Generic table-fill question contract normalization tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.gencode.cumulative_component_runtime import generate_cumulative_component_payload
from core.gencode.table_question_contract import (
    is_fillable_table_payload,
    is_readonly_table_payload,
    normalize_table_question_payload,
    normalize_table_student_answer,
)

SKILL = Path("agent_skills_v3") / "vh_數學B4_CumulativeFrequencyTablesAndGraphs"


def _gen(component_id: str, seed: int = 1) -> dict:
    component_dir = SKILL / "components" / component_id
    if not (component_dir / "generator_config.json").is_file():
        pytest.skip(f"{component_id} missing")
    return generate_cumulative_component_payload(component_dir, seed=seed, component_id=component_id)


def test_normalize_assigns_student_labels_for_engineering_keys():
    payload = _gen("src_3831", seed=1)
    assert is_fillable_table_payload(payload)
    blanks = payload["table_data"]["blank_cells"]
    labels = [cell["label"] for cell in blanks]
    assert len(labels) == 10
    assert labels == list("abcdefghij")
    assert all(cell["field_key"].startswith(("lt_", "gt_")) for cell in blanks)
    assert payload["table_data"]["show_blank_labels"] is False
    assert payload["table_data"]["blank_label_mode"] == "complete_table"
    flat = [cell for row in payload["table_data"]["visible_table"] for cell in row]
    assert "a" not in flat


def test_src_3834_shows_blank_labels_when_stem_asks_abcd():
    payload = _gen("src_3834", seed=1)
    assert payload["table_data"]["show_blank_labels"] is True
    assert payload["table_data"]["blank_label_mode"] == "named_blanks"
    flat = [cell for row in payload["table_data"]["visible_table"] for cell in row]
    assert flat.count("a") == 1
    assert "試求" in payload["question_text"] or "a" in payload["question_text"]


def test_src_3834_four_labeled_blanks_with_field_keys():
    payload = _gen("src_3834", seed=1)
    blanks = payload["table_data"]["blank_cells"]
    assert [cell["label"] for cell in blanks] == ["a", "b", "c", "d"]
    assert payload["table_data"]["type"] == "table_fill"
    assert payload["table_question"]["answer_order"]


def test_answer_contract_uses_student_labels_not_engineering_keys():
    payload = _gen("src_3831", seed=1)
    parts = payload["answer_contract"]["parts"]
    assert all(part["label"] in "abcdefghij" for part in parts)
    assert all(part["key"].startswith(("lt_", "gt_")) for part in parts)


def test_checker_accepts_dict_answers_by_field_key():
    payload = _gen("src_3834", seed=1)
    answers = {
        part["key"]: part["expected_answer"]
        for part in payload["answer_contract"]["parts"]
    }
    ordered = normalize_table_student_answer(answers, payload)
    result = check_multi_part_answer(
        ordered,
        payload["correct_answer"],
        answer_contract=payload["answer_contract"],
        payload=payload,
    )
    assert result["is_correct"] is True


def test_legacy_readonly_table_without_blanks():
    payload = normalize_table_question_payload(
        {
            "table_data": {
                "html": "<table><tr><td>1</td></tr></table>",
            }
        }
    )
    assert is_readonly_table_payload(payload)
    assert payload["table_data"]["legacy_readonly"] is True


def test_subquestions_hide_engineering_names():
    payload = _gen("src_3831", seed=1)
    for sq in payload["subquestions"]:
        part = str(sq.get("part") or "")
        assert not part.startswith("lt_")
        assert not part.startswith("gt_")


def test_explicit_show_blank_labels_override():
    payload = normalize_table_question_payload(
        {
            "question_text": "請完成表格。",
            "table_data": {
                "headers": ["x"],
                "rows": [["", 1]],
                "blank_cells": [{"row": 0, "col": 0, "label": "a", "field_key": "a"}],
                "show_blank_labels": True,
                "blank_label_mode": "named_blanks",
            },
            "subquestions": [{"part": "a", "expected_answer": 5}],
            "answer_contract": {
                "answer_type": "multi_part",
                "parts": [{"key": "a", "label": "a", "expected_answer": 5}],
            },
        }
    )
    assert payload["table_data"]["show_blank_labels"] is True


def test_complete_table_mode_hides_labels_in_visible_table():
    payload = normalize_table_question_payload(
        {
            "question_text": "試完成下方之累積次數分配表。",
            "table_data": {
                "headers": ["A", "B"],
                "rows": [[1, ""]],
                "blank_cells": [{"row": 0, "col": 1}],
            },
            "subquestions": [{"part": "lt_1", "expected_answer": 2}],
            "answer_contract": {
                "answer_type": "multi_part",
                "parts": [{"key": "lt_1", "label": "lt_1", "expected_answer": 2}],
            },
        }
    )
    assert payload["table_data"]["show_blank_labels"] is False
    assert payload["table_data"]["visible_table"][0][1] == ""


def test_graph_components_not_fillable_tables():
    for component_id in ("src_3830", "src_3832", "src_3833"):
        payload = _gen(component_id, seed=1)
        assert not is_fillable_table_payload(payload)
