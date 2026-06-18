# -*- coding: utf-8 -*-
import json
import sqlite3
import shutil
from pathlib import Path
from unittest import mock
import pytest

from core.gencode.v3_production_publish_service import publish_single_v3_skill_to_production
from core.gencode.services.v3_variation_audit_service import audit_skill_variation

PROJECT_ROOT = Path(__file__).resolve().parents[2]

@pytest.fixture
def custom_temp_dir():
    temp_dir = PROJECT_ROOT / "reports" / "test_temp_publish_gate"
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
    conn.execute(
        """CREATE TABLE gencode_component_tracker (
            textbook_example_id INTEGER PRIMARY KEY,
            skill_id TEXT,
            component_id TEXT,
            gencode_status TEXT,
            induced_spec_payload TEXT
        )"""
    )
    
    mock_payload = {
        "presentation_mode": "short_answer",
        "answer_type": "integer",
        "problem_type_id": "integer_exercise",
        "display_order": 1,
        "sampling_weight": 10.0
    }
    
    conn.execute(
        "INSERT INTO gencode_component_tracker VALUES (1, 'vh_數學B1_InterceptForm', 'src_4555', 'verified', ?)",
        (json.dumps(mock_payload),)
    )
    conn.execute(
        "INSERT INTO gencode_component_tracker VALUES (2, 'vh_數學B1_InterceptForm', 'src_4604', 'verified', ?)",
        (json.dumps(mock_payload),)
    )
    conn.commit()
    yield conn
    conn.close()

def _write_generator(staging_root: Path, skill_id: str, comp_id: str, content: str):
    comp_dir = staging_root / "agent_skills_v3" / skill_id / "components" / comp_id
    comp_dir.mkdir(parents=True, exist_ok=True)
    (comp_dir / "generate.py").write_text(content, encoding="utf-8")
    
    meta_content = """
PRESENTATION_MODE = 'short_answer'
SOURCE_KIND = 'ex'
ANSWER_VERIFICATION_TYPE = {'answer_type': 'integer'}
TARGET_TASK = 'integer_exercise'
"""
    (comp_dir / "metadata.py").write_text(meta_content, encoding="utf-8")
    (comp_dir / "get_hint.py").write_text("def get_hint(step, payload): return ''", encoding="utf-8")

def test_variation_gate_policies(custom_temp_dir, mock_db_with_tracker):
    staging_root = custom_temp_dir / "staging"
    project_root = custom_temp_dir / "project"
    
    staging_root.mkdir(parents=True, exist_ok=True)
    project_root.mkdir(parents=True, exist_ok=True)
    
    skill_id = "vh_數學B1_InterceptForm"
    
    # Write components to staging (static)
    static_code = """
def generate(seed=None, **kwargs):
    return {
        "question_text": "Static question",
        "correct_answer": "42",
        "display_answer": "42",
        "answer_contract": {"checker": "integer_checker", "answer_type": "integer"},
        "presentation_mode": "short_answer",
        "component_id": kwargs.get("component_id") or "src_4555",
        "textbook_example_id": 1 if (kwargs.get("component_id") == "src_4555") else 2,
    }
"""
    _write_generator(staging_root, skill_id, "src_4555", static_code)
    _write_generator(staging_root, skill_id, "src_4604", static_code)
    
    # Mock database textbook_examples table too
    mock_db_with_tracker.execute("CREATE TABLE textbook_examples (id INTEGER PRIMARY KEY, skill_id TEXT)")
    mock_db_with_tracker.execute("INSERT INTO textbook_examples VALUES (1, 'vh_數學B1_InterceptForm')")
    mock_db_with_tracker.execute("INSERT INTO textbook_examples VALUES (2, 'vh_數學B1_InterceptForm')")
    mock_db_with_tracker.commit()
    
    # Setup mock project thin facade structure
    (project_root / "skills").mkdir(parents=True, exist_ok=True)
    (project_root / "agent_skills_v3").mkdir(parents=True, exist_ok=True)
    
    # Ensure allowlist check passes
    with mock.patch("core.gencode.v3_production_publish_service.V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS", frozenset([skill_id])):
        # Case 1: First publish, not in V3_VARIATION_REQUIRED_SKILLS -> Should allow publish with warning
        with mock.patch("core.gencode.v3_production_publish_service.V3_VARIATION_REQUIRED_SKILLS", frozenset()):
            result = publish_single_v3_skill_to_production(
                conn=mock_db_with_tracker,
                skill_id=skill_key if 'skill_key' in locals() else skill_id,
                project_root=str(project_root),
                staging_root=str(staging_root),
            )
            assert result["status"] == "runtime_ready_with_variation_warning"
            assert result["static_count"] == 2
            
        # Clear files in mock project to simulate first publish again
        shutil.rmtree(project_root)
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "skills").mkdir(parents=True, exist_ok=True)
        (project_root / "agent_skills_v3").mkdir(parents=True, exist_ok=True)
        
        # Case 2: In V3_VARIATION_REQUIRED_SKILLS -> Should block publish
        with mock.patch("core.gencode.v3_production_publish_service.V3_VARIATION_REQUIRED_SKILLS", frozenset([skill_id])):
            with pytest.raises(ValueError, match="production_publish_blocked: variation gate failed"):
                publish_single_v3_skill_to_production(
                    conn=mock_db_with_tracker,
                    skill_id=skill_id,
                    project_root=str(project_root),
                    staging_root=str(staging_root),
                )

def test_intercept_form_audit_production_files():
    # Audit InterceptForm in production
    # It must have 7 components and all must be dynamic now
    report = audit_skill_variation(
        skill_id="vh_數學B1_InterceptForm",
        sample_size=10,
        min_samples_per_component=3,
        source="production",
    )
    assert report["status"] == "dynamic"
    assert report["components_checked"] == 7
    assert report["static_count"] == 0
    assert report["dynamic_count"] == 7


def test_general_form_registration():
    import yaml
    from pathlib import Path
    from core.registry.taxonomy_registry import resolve_domain_for_skill
    
    taxonomy_path = Path("configs/gencode_taxonomy/k12_component_taxonomy.yaml")
    assert taxonomy_path.is_file()
    data = yaml.safe_load(taxonomy_path.read_text(encoding="utf-8"))
    v1_scope = data["mvp_scope"]["v1"]
    
    assert "vh_數學B1_GeneralFormOfLinearEquation" in v1_scope
    assert "vh_數學B1_InterceptForm" in v1_scope
    assert "vh_數學B1_PointSlopeForm" in v1_scope
    
    entry = resolve_domain_for_skill("vh_數學B1_GeneralFormOfLinearEquation")
    assert entry["domain_module"] == "core.domain.coordinate_geometry.line_equation_domain"
    assert entry["entrypoint"] == "build_line_equation_matrix"
    assert "slope_from_general_form" in entry["allowed_types"]
    assert "line_through_point_parallel_to_line" in entry["allowed_types"]
    assert "line_through_point_perpendicular_to_line" in entry["allowed_types"]
    assert "parallel_condition_parameter" in entry["allowed_types"]


