# -*- coding: utf-8 -*-
"""Tests for merged V3 dryrun component manifests."""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

import pytest

from core.gencode.pipeline_orchestrator import compile_v3_component_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_test_manifest_merge"


@pytest.fixture
def sandbox_root(tmp_path_factory):
    base = SANDBOX_ROOT / f"pytest_manifest_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


def _component_row(example_id: int) -> dict:
    component_id = f"src_{example_id}"
    return {
        "component_id": component_id,
        "status": "draft_written",
        "presentation_mode": "single_choice",
        "source_kind": f"ex_{example_id}",
        "textbook_example_id": example_id,
        "line_type": "vertical_line",
    }


def test_manifest_merge_accumulates_components(sandbox_root: Path):
    compile_v3_component_manifest(SKILL_ID, [_component_row(4544)], str(sandbox_root))
    compile_v3_component_manifest(SKILL_ID, [_component_row(4553)], str(sandbox_root))

    manifest_path = sandbox_root / SKILL_ID / "component_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    component_ids = [row["component_id"] for row in manifest["components"]]
    assert component_ids == ["src_4544", "src_4553"]


def test_manifest_merge_replaces_same_component_without_duplicate(sandbox_root: Path):
    first = _component_row(4544)
    first["presentation_mode"] = "short_answer"
    second = _component_row(4544)
    second["presentation_mode"] = "single_choice"

    compile_v3_component_manifest(SKILL_ID, [first], str(sandbox_root))
    compile_v3_component_manifest(SKILL_ID, [second], str(sandbox_root))

    manifest = json.loads(
        (sandbox_root / SKILL_ID / "component_manifest.json").read_text(encoding="utf-8")
    )
    assert len(manifest["components"]) == 1
    assert manifest["components"][0]["presentation_mode"] == "single_choice"
