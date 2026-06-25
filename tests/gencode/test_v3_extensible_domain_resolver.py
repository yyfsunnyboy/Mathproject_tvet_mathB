from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.domain.statistics.table_chart_domain import build_statistical_chart_reading_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_example
from core.gencode.skill_fixed_domain_authority import SkillFixedDomainError, resolve_fixed_domain_context
from core.gencode.v3_error_codes import DOMAIN_CAPABILITY_UNRESOLVED


@pytest.fixture
def memory_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            problem_type TEXT,
            problem_text TEXT,
            correct_answer TEXT,
            detailed_solution TEXT
        )
        """
    )
    apply_tracker_ddl(conn)
    try:
        yield conn
    finally:
        conn.close()


def test_unregistered_skill_resolves_from_component_text_and_generates(memory_conn: sqlite3.Connection, tmp_path: Path) -> None:
    skill_id = "vh_數學B4_NewTableChartReadingSkill_NotInRegistry"
    memory_conn.execute(
        """
        INSERT INTO textbook_examples
            (id, skill_id, problem_type, problem_text, correct_answer, detailed_solution)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            990001,
            skill_id,
            "textbook_example",
            "The table chart shows A=3, B=5, C=8, D=2. Compare the value of C and A. (A) 3 (B) 5 (C) 8 (D) 2",
            "5",
            "Read the chart values and compare category C with category A.",
        ),
    )
    memory_conn.commit()

    result = run_admin_v3_dryrun_for_example(
        conn=memory_conn,
        textbook_example_id=990001,
        skill_id=skill_id,
        dryrun_base_dir=str(tmp_path),
        seed=42,
        allow_non_mvp_skill=True,
    )

    assert result["status"] == "verified"
    component = tmp_path / skill_id / "components" / "src_990001" / "generate.py"
    assert component.exists()

    tracker = memory_conn.execute(
        "SELECT gencode_status, gencode_error_log FROM gencode_component_tracker WHERE textbook_example_id = ?",
        (990001,),
    ).fetchone()
    assert tracker["gencode_status"] == "verified"
    assert tracker["gencode_error_log"] is None


def test_unregistered_unknown_component_stays_unresolved_with_trace() -> None:
    with pytest.raises(SkillFixedDomainError) as exc:
        resolve_fixed_domain_context(
            "vh_數學B4_NewOpaqueSkill_NotInRegistry",
            textbook_example={
                "id": 990002,
                "problem_type": "opaque_task",
                "problem_text": "A context-rich task with no mathematical domain signals.",
                "correct_answer": "unknown",
                "detailed_solution": "",
            },
        )

    assert exc.value.code == DOMAIN_CAPABILITY_UNRESOLVED
    details = exc.value.details
    assert "inference_trace" in details
    assert details["inference_trace"]["layers"][-1] == "unsupported"
    assert "text_answer_capability_inference" not in details.get("resolver_path", [])


def test_registered_chart_reading_not_reclassified_as_frequency_distribution() -> None:
    skill_id = "vh_數學B4_StatisticalChartReading"
    ctx = resolve_fixed_domain_context(
        skill_id,
        textbook_example={
            "id": 3884,
            "skill_id": skill_id,
            "problem_type": "mixed_counting",
            "problem_text": "某班英文段考成績的以上累積次數分配折線圖如右，試問：以60分為準，不及格者有多少人？",
            "correct_answer": "",
            "detailed_solution": "需觀察圖中60分對應的以上累積次數。",
        },
        problem_type_id="mixed_counting",
    )

    assert ctx.fixed_domain_key == "statistics.table_chart"
    assert ctx.domain_module == "core.domain.statistics.table_chart_domain"


def test_table_chart_compare_payload_uses_numeric_semantic_answer() -> None:
    matrix = build_statistical_chart_reading_matrix(
        seed=42,
        domain_operation="compare_category_values",
        constraints={"categories": ["A", "B", "C", "D"], "values": [8, 5, 13, 20], "compare_a": "A", "compare_b": "B"},
    )

    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="integer",
        problem_type_id="compare_category_values",
        component_id="src_3885",
        textbook_example_id=3885,
        domain_operation="compare_category_values",
    )

    assert payload["problem_type_id"] == "compare_category_values"
    assert "比較 A 與 B" in payload["question_text"]
    assert payload["answer_type"] == "integer"
    assert payload["checker"] == "choice_label_checker"
    assert payload["semantic_answer"] == 3
    assert payload["display_answer"] == "3"
    assert payload["answer"] in {"A", "B", "C", "D"}
    assert payload["answer"] != "D"
