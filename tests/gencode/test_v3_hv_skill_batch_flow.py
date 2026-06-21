# -*- coding: utf-8 -*-
"""Integration flow for HV skill batch dryrun and coverage."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_skill
from core.gencode.services.v3_skill_coverage_service import get_v3_skill_component_coverage
from core.gencode.skill_wrapper_compiler import _build_generator_specs

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B1_HorizontalAndVerticalLineEquations"
EXAMPLE_IDS = (4544, 4553, 4562, 4591)


@pytest.fixture
def memory_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            source_description TEXT,
            problem_type TEXT,
            problem_text TEXT,
            correct_answer TEXT,
            problem_type_id TEXT,
            line_type TEXT
        )
        """
    )
    apply_tracker_ddl(conn)
    textbook_rows = {
        4544: ("2-2習題 基礎題 5", "textbook_exercise", "試求通過兩點之直線方程式。", "", "vertical_line", "vertical_line"),
        4553: ("例5", "textbook_example", "(1) 求通過 A(0,-1) 與 B(4,-1) 的直線方程式。", "", "horizontal_line", "horizontal_line"),
        4562: ("隨堂練習5", "in_class_practice", "(1) 求通過 A(1,2) 與 B(1,5) 的直線方程式。", "", "vertical_line", "vertical_line"),
        4591: (
            "CH1自我評量 題10",
            "self_assessment",
            "求通過兩點之直線方程式。\n(A) x = 1\n(B) y = 2\n(C) x + y = 3\n(D) x - y = 4",
            "",
            "vertical_line",
            "vertical_line"
        ),
    }
    for example_id in EXAMPLE_IDS:
        desc, problem_type, problem_text, correct_answer, problem_type_id, line_type = textbook_rows[example_id]
        conn.execute(
            """
            INSERT INTO textbook_examples (
                id, skill_id, source_description, problem_type, problem_text, correct_answer, problem_type_id, line_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (example_id, SKILL_ID, desc, problem_type, problem_text, correct_answer, problem_type_id, line_type),
        )
    conn.commit()
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def dryrun_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_hv_batch_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_hv_skill_textbook_examples_count(memory_conn):
    coverage = get_v3_skill_component_coverage(memory_conn, SKILL_ID)
    assert coverage["total_examples"] == 4
    example_ids = [row["textbook_example_id"] for row in coverage["examples"]]
    assert example_ids == list(EXAMPLE_IDS)


def test_hv_skill_batch_dryrun_writes_tracker_and_manifest(memory_conn, dryrun_root):
    result = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
    )

    assert result["total_examples"] == 4
    assert result["success_count"] == 4
    coverage = get_v3_skill_component_coverage(memory_conn, SKILL_ID)
    assert coverage["missing_tracker_count"] == 0

    manifest = json.loads(
        (dryrun_root / SKILL_ID / "component_manifest.json").read_text(encoding="utf-8")
    )
    manifest_ids = [row["textbook_example_id"] for row in manifest["components"]]
    assert manifest_ids == list(EXAMPLE_IDS)

    row = memory_conn.execute(
        """
        SELECT induced_spec_payload
        FROM gencode_component_tracker
        WHERE textbook_example_id = 4544
        """
    ).fetchone()
    payload = json.loads(row["induced_spec_payload"])
    assert payload["presentation_mode"] == "short_answer"
    assert payload["answer_type"] == "expression"
    assert payload["presentation_evidence"]["has_choices"] is False
    assert payload["sampling_weight"] >= 1

    metadata_path = dryrun_root / SKILL_ID / "components" / "src_4544" / "metadata.py"
    metadata_text = metadata_path.read_text(encoding="utf-8")
    assert 'PRESENTATION_MODE: Final[str] = "short_answer"' in metadata_text

    row_4591 = memory_conn.execute(
        """
        SELECT induced_spec_payload
        FROM gencode_component_tracker
        WHERE textbook_example_id = 4591
        """
    ).fetchone()
    payload_4591 = json.loads(row_4591["induced_spec_payload"])
    assert payload_4591["presentation_mode"] == "single_choice"


def test_generator_specs_include_weight_and_order_fields():
    components = [
        {
            "textbook_example_id": 4553,
            "component_id": "src_4553",
            "induced_spec_payload": {
                "presentation_mode": "single_choice",
                "source_kind": "ex_4553",
                "line_type": "horizontal_line",
                "sampling_weight": 20,
                "display_order": 4553,
                "source_order": 4553,
            },
        },
        {
            "textbook_example_id": 4544,
            "component_id": "src_4544",
            "induced_spec_payload": {
                "presentation_mode": "single_choice",
                "source_kind": "ex_4544",
                "line_type": "vertical_line",
                "sampling_weight": 10,
                "display_order": 4544,
                "source_order": 4544,
            },
        },
    ]
    keys, specs = _build_generator_specs(components)
    assert keys == ["src_4544", "src_4553"]
    assert specs[0]["sampling_weight"] == 10.0
    assert specs[1]["sampling_weight"] == 20.0
