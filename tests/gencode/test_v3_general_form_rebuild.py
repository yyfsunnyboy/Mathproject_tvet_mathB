# -*- coding: utf-8 -*-
"""Tests for GeneralFormOfLinearEquation skill rebuild and staging/production flows."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
import pytest

from core.gencode.services.v3_example_semantic_classifier import (
    TextbookExampleSource,
    classify_textbook_example,
    calculate_source_hash,
)
from core.registry.taxonomy_registry import resolve_domain_for_skill
from core.registry.taxonomy_registry import resolve_domain_for_skill, get_fixed_domain_key
from core.gencode.services.v3_cross_component_audit_service import check_cross_example_collapse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"
SKILL_ID = "vh_數學B1_GeneralFormOfLinearEquation"


def test_general_form_has_fixed_domain_in_registry():
    assert get_fixed_domain_key(SKILL_ID) == "coordinate_geometry.line_equation"


def test_registry_metadata_for_general_form():
    entry = resolve_domain_for_skill(SKILL_ID)
    assert entry is not None
    assert entry["domain_module"] == "core.domain.coordinate_geometry.line_equation_domain"
    assert entry["entrypoint"] == "build_line_equation_matrix"
    
    allowed = entry.get("allowed_types") or entry.get("allowed_problem_types") or []
    assert "slope_from_general_or_intercept_form" in allowed
    assert "line_through_point_parallel_to_line" in allowed
    assert "line_through_point_perpendicular_to_line" in allowed


@pytest.mark.skipif(not DB_PATH.exists(), reason="kumon_math.db not found for integration test")
def test_general_form_examples_classification():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Target 17 textbook example IDs
    ids = [4565, 4566, 4567, 4572, 4573, 4574, 4581, 4582, 4585, 4592, 4593, 4594, 4595, 4596, 4597, 4598, 4599]
    placeholders = ",".join("?" for _ in ids)
    cursor.execute(f"SELECT * FROM textbook_examples WHERE id IN ({placeholders})", ids)
    rows = cursor.fetchall()
    
    assert len(rows) > 0, "No textbook examples found in database for testing"
    
    taxonomy_entry = resolve_domain_for_skill(SKILL_ID)
    
    classifications = {}
    for row in rows:
        row_id = row["id"]
        q_text = row["problem_text"] or ""
        ans_text = row["correct_answer"] or ""
        sol_text = row["detailed_solution"] or ""
        s_hash = calculate_source_hash(q_text, ans_text, sol_text)
        
        src = TextbookExampleSource(
            skill_id=SKILL_ID,
            textbook_example_id=row_id,
            question_text=q_text,
            answer=ans_text,
            choices=[],
            explanation=sol_text,
            source_label=row["source_description"],
            source_type=row["problem_type"],
            presentation_mode="short_answer" if "A)" not in q_text else "single_choice",
            question_type=row["problem_type"],
            source_hash=s_hash,
        )
        
        res = classify_textbook_example(src, taxonomy_entry)
        classifications[row_id] = res
        
    # Verify key example classifications are correct
    assert classifications[4565]["problem_type_id"] == "slope_from_general_or_intercept_form"
    assert classifications[4566]["problem_type_id"] == "line_through_point_parallel_to_line"
    assert classifications[4567]["problem_type_id"] == "line_through_point_perpendicular_to_line"
    assert classifications[4593]["problem_type_id"] == "perpendicular_condition_parameter"
    assert classifications[4597]["problem_type_id"] == "line_through_intersection_parallel_to_line"
    assert classifications[4599]["problem_type_id"] == "perpendicular_bisector_application"
    
    # Assert not all 17 collapsed to same type
    unique_types = {c["problem_type_id"] for c in classifications.values()}
    assert len(unique_types) > 1, f"Collapsed to single type: {unique_types}"
    
    conn.close()


@pytest.mark.skipif(not DB_PATH.exists(), reason="kumon_math.db not found for integration test")
def test_shadow_bridge_dryrun_generates_correct_metas():
    from core.gencode.pipeline_orchestrator import run_gencode_phase2_v3_shadow_bridge
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    try:
        # Run shadow bridge dry-run for example 4565
        res = run_gencode_phase2_v3_shadow_bridge(
            conn=conn,
            skill_id=SKILL_ID,
            textbook_example_id=4565,
            source_kind="ex_4565",
        )
        assert res["route"] == "v3_shadow_bridge"
        assert res["tracker_status"] == "verified"
        assert res["component_id"] == "src_4565"
        
        # Load and verify metadata.py of the generated component
        meta_path = Path(res["component_dir"]) / "metadata.py"
        assert meta_path.exists()
        
        locs = {}
        exec(meta_path.read_text(encoding="utf-8"), {}, locs)
        assert locs["PROBLEM_TYPE_ID"] == "slope_from_general_or_intercept_form"
        
    finally:
        conn.close()
