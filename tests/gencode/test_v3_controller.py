# -*- coding: utf-8 -*-
"""Tests for V3 sandbox repair radius and publish decision controller."""

from __future__ import annotations

import shutil
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.skill_wrapper_compiler import assert_safe_sandbox_root
from gencode_closed_loop.controller import (
    make_v3_publish_decision,
    repair_v3_component_file,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B1_PointSlopeForm"


@pytest.fixture
def sandbox_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_controller_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


def _component_generate_path(
    sandbox_root: Path,
    component_id: str,
) -> Path:
    return (
        sandbox_root
        / "agent_skills_v3"
        / SKILL_ID
        / "components"
        / component_id
        / "generate.py"
    )


def _write_component_generate(
    sandbox_root: Path,
    component_id: str,
    content: str,
) -> Path:
    path = _component_generate_path(sandbox_root, component_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_repair_v3_component_file_only_touches_target_component(sandbox_root: Path):
    src_1_path = _write_component_generate(sandbox_root, "src_1", "generate_src_1\n")
    src_2_path = _write_component_generate(sandbox_root, "src_2", "generate_src_2\n")
    src_2_original = src_2_path.read_text(encoding="utf-8")

    result = repair_v3_component_file(
        str(sandbox_root),
        SKILL_ID,
        "src_1",
        error_log="mock_error",
        attempt=1,
    )

    assert result["status"] == "repaired"
    assert result["component_id"] == "src_1"
    assert "# repaired_attempt_1" in src_1_path.read_text(encoding="utf-8")
    assert src_2_path.read_text(encoding="utf-8") == src_2_original


def test_repair_v3_component_file_max_retry_does_not_modify_file(sandbox_root: Path):
    src_1_path = _write_component_generate(sandbox_root, "src_1", "generate_src_1\n")
    original = src_1_path.read_text(encoding="utf-8")

    result = repair_v3_component_file(
        str(sandbox_root),
        SKILL_ID,
        "src_1",
        error_log="mock_error",
        attempt=4,
    )

    assert result["status"] == "max_retry_exceeded"
    assert src_1_path.read_text(encoding="utf-8") == original


def test_repair_v3_component_file_rejects_unsafe_sandbox_root(sandbox_root: Path):
    _write_component_generate(sandbox_root, "src_1", "generate_src_1\n")
    for unsafe_root in ("", ".", "skills", "agent_skills_v3"):
        with pytest.raises(ValueError, match="unsafe_sandbox_root"):
            repair_v3_component_file(
                unsafe_root,
                SKILL_ID,
                "src_1",
                error_log="mock_error",
                attempt=1,
            )


def test_make_v3_publish_decision_partial_published():
    decision = make_v3_publish_decision(
        SKILL_ID,
        required_core_components=["src_1"],
        current_components_status=[
            {"component_id": "src_1", "status": "verified"},
            {"component_id": "src_2", "status": "failed"},
        ],
    )

    assert decision["publish_status"] == "partial_published"
    assert decision["can_continue_compile"] is True
    assert "src_1" in decision["publishable_components"]
    assert "src_2" in decision["excluded_components"]


def test_make_v3_publish_decision_full_published():
    decision = make_v3_publish_decision(
        SKILL_ID,
        required_core_components=["src_1"],
        current_components_status=[
            {"component_id": "src_1", "status": "verified"},
            {"component_id": "src_2", "status": "verified"},
        ],
    )

    assert decision["publish_status"] == "full_published"
    assert decision["can_continue_compile"] is True
    assert decision["excluded_components"] == []


def test_make_v3_publish_decision_blocked_when_core_not_verified():
    decision = make_v3_publish_decision(
        SKILL_ID,
        required_core_components=["src_1"],
        current_components_status=[
            {"component_id": "src_1", "status": "failed"},
            {"component_id": "src_2", "status": "verified"},
        ],
    )

    assert decision["publish_status"] == "blocked"
    assert decision["can_continue_compile"] is False
    assert "src_1" in decision["non_verified_core_components"]


def test_make_v3_publish_decision_blocked_when_core_missing():
    decision = make_v3_publish_decision(
        SKILL_ID,
        required_core_components=["src_999"],
        current_components_status=[
            {"component_id": "src_1", "status": "verified"},
        ],
    )

    assert decision["publish_status"] == "blocked"
    assert decision["can_continue_compile"] is False
    assert "src_999" in decision["missing_core_components"]


def test_assert_safe_sandbox_root_blocks_production_paths():
    for unsafe_root in ("", ".", "skills", "agent_skills_v3"):
        with pytest.raises(ValueError, match="unsafe_sandbox_root"):
            assert_safe_sandbox_root(unsafe_root)

    with pytest.raises(ValueError, match="unsafe_sandbox_root"):
        assert_safe_sandbox_root(str(PROJECT_ROOT))
