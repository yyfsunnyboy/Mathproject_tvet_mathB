from __future__ import annotations

import sqlite3
from pathlib import Path

from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example
from core.gencode.source_topology_rules import classify_source_topology

SKILL_ID = "vh_數學B1_LinearFunction"
DB_PATH = Path(__file__).resolve().parents[2] / "instance" / "kumon_math.db"

EXPECTED = {
    4424: "graph_intercepts_and_linear_equation",
    4425: "graph_based_tiered_linear_application_multi_part",
    4426: "collinear_trisection_coordinate",
    4433: "draw_constant_function_graph",
    4434: "draw_linear_function_graph",
    4441: "graph_intercepts_and_linear_equation",
    4442: "graph_based_linear_application_inverse",
    4444: "graph_intercepts_and_linear_equation",
    4445: "graph_based_tiered_linear_application_multi_part",
    4446: "robust_budget_feasibility_choice",
    4448: "draw_constant_function_graph",
    4449: "draw_linear_function_graph",
    4500: "graph_based_linear_model_equation",
    4515: "linear_equation_from_two_points_choice",
    4516: "linear_graph_feasibility_choice",
}


def _load_rows() -> tuple[sqlite3.Connection, list[dict]]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    rows = [
        dict(row)
        for row in connection.execute(
            "SELECT * FROM textbook_examples WHERE skill_id = ? ORDER BY id",
            (SKILL_ID,),
        ).fetchall()
    ]
    return connection, rows


def test_all_fifteen_sources_preserve_phase1_topology() -> None:
    connection, rows = _load_rows()
    try:
        assert len(rows) == 15
        for row in rows:
            result = run_v3_no_llm_phase1_for_example(SKILL_ID, row, conn=connection)
            assert result["classification_status"] == "resolved"
            assert result["problem_type_id"] == EXPECTED[row["id"]]
            assert result["required_givens"]
            assert result["requested_quantity"]
            assert result["topology_tags"]
            assert result["answer_schema"]
            assert result["presentation_mode"]
    finally:
        connection.close()


def test_src_4424_preserves_graph_multi_part_contract() -> None:
    connection, rows = _load_rows()
    try:
        row = next(row for row in rows if row["id"] == 4424)
        result = run_v3_no_llm_phase1_for_example(SKILL_ID, row, conn=connection)
    finally:
        connection.close()

    assert result["problem_type_id"] == "graph_intercepts_and_linear_equation"
    assert result["problem_type_id"] != "integer_numeric_evaluate_function_notation"
    assert result["required_givens"] == ["linear_function_graph"]
    assert result["requested_quantity"] == [
        "x_intercept",
        "y_intercept",
        "linear_function_equation",
    ]
    assert result["answer_schema"] == "multi_part_intercepts_and_expression"
    assert result["presentation_mode"] == "graph_multi_part"


def test_topology_rules_do_not_depend_on_skill_or_component_identity() -> None:
    row = {
        "id": 999999,
        "skill_id": "unrelated_container",
        "component_id": "arbitrary_component",
        "problem_text": (
            "右圖為函數 $y=f\\left( x \\right)=ax+b$ 的圖形。"
            "(1) 試求直線的x截距與y截距。"
            "(2) 試求 $f\\left( x \\right)$。"
        ),
    }
    result = classify_source_topology(row)
    assert result is not None
    assert result["problem_type_id"] == "graph_intercepts_and_linear_equation"
