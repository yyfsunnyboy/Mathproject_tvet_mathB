# -*- coding: utf-8 -*-
import json
import sqlite3
import shutil
from pathlib import Path
import pytest

from core.gencode.services.v3_variation_audit_service import audit_skill_variation

SKILL_ID = "vh_test_VariationSkill"
PROJECT_ROOT = Path(__file__).resolve().parents[2]

@pytest.fixture
def custom_temp_dir():
    temp_dir = PROJECT_ROOT / "reports" / "test_temp_variation_audit"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

@pytest.fixture
def mock_db_with_tracker(custom_temp_dir):
    db_path = custom_temp_dir / "test_kumon.db"
    conn = sqlite3.connect(str(db_path))
    ddl_path = PROJECT_ROOT / "core" / "gencode" / "schema" / "gencode_component_tracker.sql"
    ddl = ddl_path.read_text(encoding="utf-8")
    conn.executescript(ddl)
    
    conn.execute(
        "INSERT INTO gencode_component_tracker (textbook_example_id, skill_id, component_id, gencode_status) VALUES (1, ?, 'comp_static', 'verified')",
        (SKILL_ID,)
    )
    conn.execute(
        "INSERT INTO gencode_component_tracker (textbook_example_id, skill_id, component_id, gencode_status) VALUES (2, ?, 'comp_dynamic', 'verified')",
        (SKILL_ID,)
    )
    conn.execute(
        "INSERT INTO gencode_component_tracker (textbook_example_id, skill_id, component_id, gencode_status) VALUES (3, ?, 'comp_partial', 'verified')",
        (SKILL_ID,)
    )
    conn.execute(
        "INSERT INTO gencode_component_tracker (textbook_example_id, skill_id, component_id, gencode_status) VALUES (4, ?, 'comp_unsafe', 'verified')",
        (SKILL_ID,)
    )
    conn.commit()
    yield conn
    conn.close()

def _write_generator(staging_root: Path, comp_id: str, content: str):
    comp_dir = staging_root / "agent_skills_v3" / SKILL_ID / "components" / comp_id
    comp_dir.mkdir(parents=True, exist_ok=True)
    (comp_dir / "generate.py").write_text(content, encoding="utf-8")

def test_audit_skill_variation_categories(custom_temp_dir, mock_db_with_tracker):
    staging_root = custom_temp_dir / "staging"
    staging_root.mkdir(parents=True, exist_ok=True)

    # 1. Static Generator
    static_code = """
def generate(seed=None, **kwargs):
    return {
        "question_text": "Static question text",
        "correct_answer": "42",
        "display_answer": "42",
        "answer_contract": {"checker": "integer_checker", "answer_type": "integer"},
        "presentation_mode": "short_answer",
        "component_id": "comp_static",
        "textbook_example_id": 1,
    }
"""
    _write_generator(staging_root, "comp_static", static_code)

    # 2. Dynamic Generator
    dynamic_code = """
def generate(seed=None, **kwargs):
    val = seed if seed is not None else 1
    return {
        "question_text": f"Dynamic question text with {val}",
        "correct_answer": str(val),
        "display_answer": str(val),
        "answer_contract": {"checker": "integer_checker", "answer_type": "integer"},
        "presentation_mode": "short_answer",
        "component_id": "comp_dynamic",
        "textbook_example_id": 2,
    }
"""
    _write_generator(staging_root, "comp_dynamic", dynamic_code)

    # 3. Partially Dynamic (choices change but question text and correct answer are static)
    partial_code = """
def generate(seed=None, **kwargs):
    val = seed if seed is not None else 1
    choices = [
        {"label": "A", "text": "10"},
        {"label": "B", "text": f"val_{val}"},
        {"label": "C", "text": "30"},
        {"label": "D", "text": "40"}
    ]
    return {
        "question_text": "Calculate 5 + 5",
        "correct_answer": "A",
        "choices": choices,
        "semantic_answer": "10",
        "answer_contract": {"checker": "choice_label_checker", "answer_type": "single_choice"},
        "presentation_mode": "single_choice",
        "component_id": "comp_partial",
        "textbook_example_id": 3,
    }
"""
    _write_generator(staging_root, "comp_partial", partial_code)

    # 4. Unsafe Dynamic (choices count != 4 for single choice)
    unsafe_code = """
def generate(seed=None, **kwargs):
    val = seed if seed is not None else 1
    choices = [
        {"label": "A", "text": f"val_{val}"},
        {"label": "B", "text": "20"}
    ]
    return {
        "question_text": f"Unsafe question with {val}",
        "correct_answer": "A",
        "choices": choices,
        "semantic_answer": "10",
        "answer_contract": {"checker": "choice_label_checker", "answer_type": "single_choice"},
        "presentation_mode": "single_choice",
        "component_id": "comp_unsafe",
        "textbook_example_id": 4,
    }
"""
    _write_generator(staging_root, "comp_unsafe", unsafe_code)

    # Run audit
    report = audit_skill_variation(
        skill_id=SKILL_ID,
        sample_size=5,
        min_samples_per_component=5,
        source="staging",
        staging_root=str(staging_root),
        conn=mock_db_with_tracker,
    )

    by_comp = report["variation_status_by_component"]
    
    assert by_comp["comp_static"]["variation_status"] == "static"
    assert by_comp["comp_dynamic"]["variation_status"] == "dynamic"
    assert by_comp["comp_partial"]["variation_status"] == "partially_dynamic"
    assert by_comp["comp_unsafe"]["variation_status"] == "unsafe_dynamic"

    # 5. Insufficient sample check
    report_insufficient = audit_skill_variation(
        skill_id=SKILL_ID,
        sample_size=3,
        min_samples_per_component=5,
        source="staging",
        staging_root=str(staging_root),
        conn=mock_db_with_tracker,
    )
    by_comp_ins = report_insufficient["variation_status_by_component"]
    for comp in by_comp_ins.values():
        assert comp["variation_status"] == "insufficient_sample"
