# -*- coding: utf-8 -*-
"""Integration tests for B4 cumulative component dryrun chain."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from core.gencode.component_induced_config import (
    build_component_generate_context,
    induced_constraints_from_config,
    load_component_induced_config,
)
from core.gencode.cumulative_component_runtime import generate_cumulative_component_payload

SKILL_ID = "vh_數學B4_CumulativeFrequencyTablesAndGraphs"
AGENT_ROOT = Path("agent_skills_v3") / SKILL_ID
DRYRUN_ROOT = Path("reports/gencode_v3_dryrun") / SKILL_ID

COMPONENTS = [
    ("src_3830", "cumulative_frequency_graph_reading"),
    ("src_3831", "cumulative_frequency_table_construction"),
    ("src_3832", "greater_than_cumulative_frequency_reading"),
    ("src_3833", "cumulative_frequency_graph_reading"),
    ("src_3834", "class_frequency_from_cumulative_difference"),
]


@pytest.mark.parametrize("component_id,expected_operation", COMPONENTS)
def test_component_local_config_loads(component_id: str, expected_operation: str):
    component_dir = AGENT_ROOT / "components" / component_id
    config_path = component_dir / "generator_config.json"
    if not config_path.is_file():
        pytest.skip("generator_config not materialized yet")
    config = load_component_induced_config(component_dir)
    assert config["domain_operation"] == expected_operation
    constraints = induced_constraints_from_config(config)
    assert "example_id" not in constraints
    assert "3830" not in json.dumps(constraints, ensure_ascii=False)


def test_domain_code_has_no_example_id_branch():
    domain_path = Path("core/domain/statistics/frequency_distribution_domain.py")
    text = domain_path.read_text(encoding="utf-8")
    assert "3830" not in text
    assert "src_3830" not in text
    assert "example_id" not in text


@pytest.mark.parametrize("component_id,expected_operation", COMPONENTS)
def test_component_operations_distinct(component_id: str, expected_operation: str):
    component_dir = AGENT_ROOT / "components" / component_id
    if not (component_dir / "generator_config.json").is_file():
        pytest.skip("generator_config not materialized yet")
    ctx = build_component_generate_context(component_dir)
    assert ctx["domain_operation"] == expected_operation


@pytest.mark.parametrize("component_id,_op", COMPONENTS)
def test_generate_payload_preserves_visual_fields(component_id: str, _op: str):
    component_dir = DRYRUN_ROOT / "components" / component_id
    if not (component_dir / "generate.py").is_file():
        component_dir = AGENT_ROOT / "components" / component_id
    if not (component_dir / "generator_config.json").is_file():
        pytest.skip("component not ready")
    payload = generate_cumulative_component_payload(component_dir, seed=7, component_id=component_id)
    assert payload.get("domain_operation")
    if component_id in {"src_3830", "src_3832", "src_3833"}:
        assert payload.get("image_base64")
    if component_id in {"src_3831", "src_3834"}:
        assert payload.get("table_data", {}).get("html")
    if component_id in {"src_3830", "src_3831", "src_3832", "src_3833", "src_3834"}:
        if payload.get("answer_type") == "multi_part":
            assert len(payload.get("subquestions") or []) >= 2


@pytest.mark.parametrize("component_id,_op", COMPONENTS)
@pytest.mark.parametrize("seed", list(range(1, 16)))
def test_fifteen_seeds_per_component(component_id: str, _op: str, seed: int):
    component_dir = DRYRUN_ROOT / "components" / component_id
    if not (component_dir / "generate.py").is_file():
        component_dir = AGENT_ROOT / "components" / component_id
    if not (component_dir / "generator_config.json").is_file():
        pytest.skip("component not ready")
    payload = generate_cumulative_component_payload(component_dir, seed=seed, component_id=component_id)
    assert payload.get("question_text")
    assert payload.get("answer_type") != "integer" or component_id not in {"src_3830", "src_3831", "src_3832", "src_3833"}


def test_candidate_verified_is_not_tracker_verified():
    evidence_path = DRYRUN_ROOT / "component_dryrun_evidence.json"
    if not evidence_path.is_file():
        pytest.skip("dryrun evidence missing")
    report = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert report.get("tracker_updated") is False
    assert "candidate_verified" in json.dumps(report, ensure_ascii=False)


def test_direct_component_preview_without_wrapper_randomness():
    component_dir = DRYRUN_ROOT / "components" / "src_3830"
    if not (component_dir / "generate.py").is_file():
        pytest.skip("dryrun component missing")
    path = component_dir / "generate.py"
    spec = importlib.util.spec_from_file_location("preview_src_3830", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    p1 = module.generate(seed=42, component_id="src_3830")
    p2 = module.generate(seed=42, component_id="src_3830")
    assert p1["question_text"] == p2["question_text"]
    assert p1.get("image_base64") == p2.get("image_base64")
