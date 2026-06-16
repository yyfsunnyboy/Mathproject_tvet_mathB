# -*- coding: utf-8 -*-
"""Integration tests for V3 sandbox disk I/O and manifest compilation."""

from __future__ import annotations

import json
import shutil
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.pipeline_orchestrator import (
    build_v3_component_draft_from_skill,
    compile_v3_component_manifest,
    write_v3_component_to_disk,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_SKILLS_DIR = PROJECT_ROOT / "agent_skills_v3"
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B1_PointSlopeForm"
COMPONENT_FILES = ("metadata.py", "generate.py", "get_hint.py")


@pytest.fixture
def sandbox_base() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


def _build_draft() -> dict[str, object]:
    return build_v3_component_draft_from_skill(
        skill_id=SKILL_ID,
        textbook_example_id=1,
        source_kind="ex_1",
        seed=42,
    )


def test_write_v3_component_to_disk_writes_isolated_component_files(sandbox_base: Path):
    draft = _build_draft()
    component_dir = write_v3_component_to_disk(draft, str(sandbox_base))

    expected_dir = sandbox_base / SKILL_ID / "components" / "src_1"
    assert Path(component_dir) == expected_dir.resolve()

    for filename in COMPONENT_FILES:
        file_path = expected_dir / filename
        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == draft["files"][filename]


def test_compile_v3_component_manifest_writes_traceable_manifest(sandbox_base: Path):
    draft = _build_draft()
    component_dir = write_v3_component_to_disk(draft, str(sandbox_base))

    component_status = {
        "component_id": "src_1",
        "status": "draft_written",
        "presentation_mode": "single_choice",
        "source_kind": draft["source_kind"],
        "textbook_example_id": draft["textbook_example_id"],
        "line_type": draft["line_type"],
        "domain_module": draft["domain_module"],
        "entrypoint": draft["entrypoint"],
        "component_dir": component_dir,
    }

    manifest = compile_v3_component_manifest(
        skill_id=SKILL_ID,
        component_statuses=[component_status],
        base_dir=str(sandbox_base),
    )

    manifest_path = sandbox_base / SKILL_ID / "component_manifest.json"
    assert manifest_path.exists()

    loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert loaded["skill_id"] == SKILL_ID
    assert loaded["compiled_at"]
    assert loaded["publish_status"] == "dryrun_manifest_compiled"
    assert isinstance(loaded["components"], list)
    assert loaded["components"][0]["component_id"] == "src_1"
    assert loaded["components"][0]["status"] == "draft_written"
    assert loaded["components"][0]["source_kind"] == "ex_1"
    assert loaded["components"][0]["textbook_example_id"] == 1
    assert loaded["components"][0]["line_type"] == "point_slope"
    assert loaded["components"][0]["domain_module"] == (
        "core.domain.coordinate_geometry.line_equation_domain"
    )
    assert loaded["components"][0]["entrypoint"] == "build_line_equation_matrix"
    assert loaded["components"][0]["component_dir"] == component_dir
    assert manifest == loaded


def test_write_v3_component_to_disk_rejects_production_base_dir():
    draft = _build_draft()
    with pytest.raises(ValueError, match="agent_skills_v3"):
        write_v3_component_to_disk(draft, "agent_skills_v3")


def test_compile_v3_component_manifest_rejects_production_base_dir():
    with pytest.raises(ValueError, match="agent_skills_v3"):
        compile_v3_component_manifest(
            skill_id=SKILL_ID,
            component_statuses=[
                {
                    "component_id": "src_1",
                    "status": "draft_written",
                }
            ],
            base_dir="agent_skills_v3",
        )


def test_v3_io_does_not_pollute_production_agent_skills_v3(sandbox_base: Path):
    before_exists = PRODUCTION_SKILLS_DIR.exists()
    before_children = (
        set(PRODUCTION_SKILLS_DIR.iterdir()) if before_exists else set()
    )

    draft = _build_draft()
    component_dir = write_v3_component_to_disk(draft, str(sandbox_base))
    compile_v3_component_manifest(
        skill_id=SKILL_ID,
        component_statuses=[
            {
                "component_id": "src_1",
                "status": "draft_written",
                "presentation_mode": "single_choice",
                "source_kind": draft["source_kind"],
                "textbook_example_id": draft["textbook_example_id"],
                "line_type": draft["line_type"],
                "domain_module": draft["domain_module"],
                "entrypoint": draft["entrypoint"],
                "component_dir": component_dir,
            }
        ],
        base_dir=str(sandbox_base),
    )

    if before_exists:
        assert set(PRODUCTION_SKILLS_DIR.iterdir()) == before_children
    else:
        assert not PRODUCTION_SKILLS_DIR.exists()
