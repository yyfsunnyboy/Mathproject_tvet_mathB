# -*- coding: utf-8 -*-
"""Official compatibility gates for V3 capability fill (no live model calls)."""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

from core.gencode.services.v3_capability_ai_fill_service import _job_is_reusable
from core.gencode.services.v3_capability_compatibility_validator import (
    BLOCK_INCOMPATIBLE,
    validate_architect_spec,
    validate_official_compatibility,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = PROJECT_ROOT / "tests" / "gencode" / "fixtures" / "incompatible_slope_of_a_line_33147281"
SKILL_ID = "vh_數學B1_SlopeOfALine"
EXAMPLE_IDS = [4519, 4520, 4521, 4522, 4523, 4524, 4525, 4529, 4533, 4534, 4590, 4601]


def _load_spec() -> dict:
    return json.loads((FIXTURE_DIR / "capability_spec.json").read_text(encoding="utf-8"))


def test_incompatible_slope_fixture_is_blocked_by_official_gates(tmp_path: Path):
    job_dir = tmp_path / "job"
    cand = job_dir / "candidate"
    cand.mkdir(parents=True)
    for name in (
        "math_geometry_domain_registry_v1.yaml",
        "slope_calculator_engine.py",
        "isomorphism_mapping_table.json",
    ):
        shutil.copy(FIXTURE_DIR / name, cand / name)
    spec = _load_spec()
    result = validate_official_compatibility(
        job_dir,
        spec,
        skill_id=SKILL_ID,
        example_ids=EXAMPLE_IDS,
    )
    assert result["passed"] is False
    blockers = set(result["blockers"])
    expected = {
        "skill_id_mismatch",
        "invented_domain_forbidden",
        "standalone_helper_forbidden",
        "placeholder_or_pending",
        "unwired_artifact",
        "missing_focused_tests",
        "example_coverage_incomplete",
        "unknown_example_id",
        "math_boundary_fraction_missing",
    }
    missing = expected - blockers
    assert not missing, missing
    assert any(b.startswith("unwired_artifact:") for b in blockers)
    assert any(b.startswith("operation_unregistered:") for b in blockers)


def test_architect_invented_domain_is_rejected():
    spec = _load_spec()
    blockers = validate_architect_spec(spec, skill_id=SKILL_ID, example_ids=EXAMPLE_IDS)
    assert "skill_id_mismatch" in blockers
    assert "invented_domain_forbidden" in blockers
    assert "spec_missing_taxonomy_binding_proposal" in blockers


def test_compile_only_helper_cannot_pass_compatibility(tmp_path: Path):
    job_dir = tmp_path / f"job_{uuid.uuid4().hex[:6]}"
    cand = job_dir / "candidate"
    cand.mkdir(parents=True)
    (cand / "domain_module.py").write_text(
        "DOMAIN_KEY = 'demo_domain'\nREQUIRED_OPERATIONS = ['demo_op']\n\n"
        "def build_fixture_matrix():\n    return {'operations': REQUIRED_OPERATIONS}\n",
        encoding="utf-8",
    )
    spec = {
        "skill_id": "skill_compile_only",
        "domain_key_suggestion": "demo_domain",
        "required_operations": ["demo_op"],
        "candidate_plan": {"files": ["domain_module.py"], "summary": "compile only"},
    }
    result = validate_official_compatibility(
        job_dir,
        spec,
        skill_id="skill_compile_only",
        example_ids=[1],
    )
    assert result["passed"] is False
    assert "invented_domain_forbidden" in result["blockers"]
    assert "unwired_artifact" in result["blockers"] or any(
        b.startswith("unwired_artifact:") for b in result["blockers"]
    )
    assert "missing_focused_tests" in result["blockers"]


def test_incompatible_status_is_not_reusable():
    job = {
        "job_id": "old-incompatible",
        "status": "awaiting_admin_confirm",
        "ai_output_valid": True,
        "spec_origin": "architect",
        "candidate_origin": "coder",
        "validation_passed": True,
        "block_reason": BLOCK_INCOMPATIBLE,
        "official_compatibility_passed": False,
        "promotion_allowed": False,
    }
    assert _job_is_reusable(job) is False
