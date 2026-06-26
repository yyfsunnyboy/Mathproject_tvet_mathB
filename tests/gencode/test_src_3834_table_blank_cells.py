# -*- coding: utf-8 -*-
"""src_3834 labeled blank-cell table contract and renderer tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.domain.statistics.cumulative_frequency_renderer import render_cumulative_frequency_table
from core.gencode.cumulative_component_runtime import generate_cumulative_component_payload
from core.gencode.services.v3_component_preview_service import generate_component_preview

SKILL_ID = "vh_數學B4_CumulativeFrequencyTablesAndGraphs"
SRC_3834_DIR = Path("agent_skills_v3") / SKILL_ID / "components" / "src_3834"
OTHER_TABLE_COMPONENTS = [
    Path("agent_skills_v3") / SKILL_ID / "components" / "src_3831",
]


def _generate_src_3834(seed: int = 1) -> dict:
    if not (SRC_3834_DIR / "generator_config.json").is_file():
        pytest.skip("src_3834 generator_config missing")
    return generate_cumulative_component_payload(
        SRC_3834_DIR,
        seed=seed,
        component_id="src_3834",
    )


def test_src_3834_blank_cells_have_four_labels():
    payload = _generate_src_3834(seed=1)
    blank_cells = payload["table_data"]["blank_cells"]
    labels = [cell["label"] for cell in blank_cells]
    assert len(blank_cells) == 4
    assert labels == ["a", "b", "c", "d"]
    assert payload["table_data"]["type"] == "table_fill"
    assert all(cell.get("field_key") for cell in blank_cells)


def test_src_3834_html_not_required_for_interactive_table():
    payload = _generate_src_3834(seed=1)
    assert payload["table_data"].get("interaction_mode") == "inline_input"
    assert payload.get("table_question")


def test_src_3834_visible_table_shows_labels_when_enabled():
    payload = _generate_src_3834(seed=1)
    assert payload["table_data"]["show_blank_labels"] is True
    flat = [cell for row in payload["table_data"]["visible_table"] for cell in row]
    assert flat.count("a") == 1


def test_src_3834_subquestion_labels_match_blank_cells():
    payload = _generate_src_3834(seed=1)
    blank_labels = {cell["label"] for cell in payload["table_data"]["blank_cells"]}
    sub_parts = {sq["part"] for sq in payload["subquestions"]}
    assert sub_parts == blank_labels
    assert all(not str(sq.get("part", "")).startswith("lt_") for sq in payload["subquestions"])


def test_src_3834_checker_still_accepts_correct_answers():
    payload = _generate_src_3834(seed=1)
    expected = [sq["expected_answer"] for sq in payload["subquestions"]]
    result = check_multi_part_answer(
        expected,
        expected,
        answer_contract=payload.get("answer_contract") or {},
        payload=payload,
    )
    assert result["is_correct"] is True


def test_src_3834_question_stem_mentions_abcd():
    payload = _generate_src_3834(seed=1)
    assert "a" in payload["question_text"]
    assert "d" in payload["question_text"]


def test_renderer_labeled_blank_cells_without_numeric_leak():
    result = render_cumulative_frequency_table(
        headers=["成績(分)", "次數(人)", "以下累積次數(人)"],
        rows=[
            ["0~20", 4, 4],
            ["20~40", "a", 12],
            ["40~60", 10, "b"],
            ["60~80", 12, 34],
            ["80~100", "c", "d"],
        ],
        blank_cells=[(1, 1), (2, 2), (4, 1), (4, 2)],
    )
    td = result["table_data"]
    assert td["blank_cells"] == [
        {"row": 1, "col": 1, "label": "a"},
        {"row": 2, "col": 2, "label": "b"},
        {"row": 4, "col": 1, "label": "c"},
        {"row": 4, "col": 2, "label": "d"},
    ]
    assert 'class="blank-label">a</span>' in td["html"]


def test_bidirectional_table_blank_cells_get_auto_labels():
    """src_3831-style tables assign a..j while keeping internal field keys."""
    from core.domain.statistics.cumulative_frequency_renderer import render_cumulative_frequency_table
    from core.gencode.table_question_contract import normalize_table_question_payload

    rows = [
        ["50~60", 5, 5, 45],
        ["60~70", 10, 15, 40],
    ]
    result = render_cumulative_frequency_table(
        headers=["成績(分)", "次數(人)", "以下累積次數(人)", "以上累積次數(人)"],
        rows=rows,
        blank_cells=[(0, 2), (0, 3), (1, 2), (1, 3)],
    )
    payload = normalize_table_question_payload(
        {
            "answer_type": "multi_part",
            "subquestions": [
                {"part": "lt_1", "expected_answer": 5},
                {"part": "gt_1", "expected_answer": 45},
                {"part": "lt_2", "expected_answer": 15},
                {"part": "gt_2", "expected_answer": 40},
            ],
            "answer_contract": {
                "answer_type": "multi_part",
                "parts": [
                    {"key": "lt_1", "label": "lt_1", "expected_answer": 5},
                    {"key": "gt_1", "label": "gt_1", "expected_answer": 45},
                    {"key": "lt_2", "label": "lt_2", "expected_answer": 15},
                    {"key": "gt_2", "label": "gt_2", "expected_answer": 40},
                ],
            },
            "table_data": result["table_data"],
        }
    )
    labels = [cell["label"] for cell in payload["table_data"]["blank_cells"]]
    assert labels == ["a", "b", "c", "d"]


@pytest.mark.parametrize("component_dir", OTHER_TABLE_COMPONENTS)
def test_other_cumulative_table_components_unaffected(component_dir: Path):
    if not (component_dir / "generator_config.json").is_file():
        pytest.skip(f"{component_dir.name} not ready")
    payload = generate_cumulative_component_payload(
        component_dir,
        seed=1,
        component_id=component_dir.name,
    )
    html = payload["table_data"].get("html", "")
    assert payload["table_data"]["type"] == "table_fill"
    if html:
        assert 'class="blank-label">' not in html
