# -*- coding: utf-8 -*-
"""Unit tests for descriptive statistics domain analyzer."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from core.domain.statistics.descriptive_statistics_analyzer import (
    analyze_textbook_row,
    resolve_descriptive_operation,
)
from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example
from core.gencode.v3_presentation_inference import fetch_textbook_example_row

REPO = Path(__file__).resolve().parents[2]
SKILL = "vh_數學B4_DispersionMeasures"
EXAMPLES = {
    3845: "compute_quartiles_and_iqr",
    3846: "compare_dispersion",
    3847: "compare_dispersion",
    3891: "conceptual_dispersion_judgment",
    3892: "compute_population_standard_deviation",
}


@pytest.fixture(scope="module")
def db_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(REPO / "instance" / "kumon_math.db")
    yield conn
    conn.close()


@pytest.mark.parametrize(
    ("example_id", "expected_operation"),
    list(EXAMPLES.items()),
)
def test_analyzer_resolves_dispersion_examples(
    db_conn: sqlite3.Connection,
    example_id: int,
    expected_operation: str,
) -> None:
    row = fetch_textbook_example_row(db_conn, example_id)
    assert row is not None
    from core.gencode.v3_presentation_inference import infer_presentation_mode_from_textbook_row

    presentation_mode = str(infer_presentation_mode_from_textbook_row(row).get("presentation_mode") or "short_answer")
    analysis = analyze_textbook_row(row, presentation_mode=presentation_mode)
    assert analysis is not None
    assert analysis.status == "resolved"
    assert analysis.selected_operation == expected_operation


@pytest.mark.parametrize("example_id", list(EXAMPLES))
def test_phase1_uses_domain_analyzer(db_conn: sqlite3.Connection, example_id: int) -> None:
    row = fetch_textbook_example_row(db_conn, example_id)
    phase1 = run_v3_no_llm_phase1_for_example(SKILL, row, conn=db_conn)
    assert phase1.get("classification_status") == "resolved"
    assert phase1.get("classification_source") == "descriptive_statistics_domain_analyzer"
    op = resolve_descriptive_operation(
        required_capabilities=phase1.get("required_capabilities") or [],
        problem_type_id=str(phase1.get("problem_type_id") or ""),
        question_text=str(row.get("problem_text") or ""),
        presentation_mode=str(phase1.get("presentation_mode") or ""),
    )
    assert op == EXAMPLES[example_id]


def test_table_completion_requires_table_structure() -> None:
    op = resolve_descriptive_operation(
        required_capabilities=["range", "median", "variance"],
        problem_type_id="range_computation",
        question_text="資料 1,2,3 求全距",
        presentation_mode="short_answer",
    )
    assert op != "complete_descriptive_statistics_table"


def test_descriptive_statistics_table_with_stat_measures_still_matches() -> None:
    row = {
        "id": 999001,
        "skill_id": "vh_數學B4_CentralTendencyMeasures",
        "problem_text": "資料 2, 5, 7, 9，完成下表各統計量。",
        "correct_answer": "",
    }
    analysis = analyze_textbook_row(row, presentation_mode="short_answer")
    assert analysis is not None
    assert analysis.problem_type_id == "descriptive_statistics_table_completion"
    row = {
        "id": 4618,
        "skill_id": "vh_數學B1_PolynomialBasicConcepts",
        "problem_text": r"已知$f\left( x \right)=2{{x}^{2}}+{{x}^{3}}-3x-5$，試按降冪排列完成下表：",
        "correct_answer": "",
    }
    analysis = analyze_textbook_row(row, presentation_mode="short_answer")
    assert analysis is None
    phase1 = run_v3_no_llm_phase1_for_example("vh_數學B1_PolynomialBasicConcepts", row)
    assert phase1.get("classification_source") != "descriptive_statistics_domain_analyzer"
    assert phase1.get("fixed_domain_key") != "statistics.descriptive_statistics"
    assert phase1.get("problem_type_id") != "descriptive_statistics_table_completion"
