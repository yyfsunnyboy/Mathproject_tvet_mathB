# -*- coding: utf-8 -*-
"""Research Healer on the real V3 AI-Python path: capability AI fill coder files (mock clients)."""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from unittest import mock

import pytest

from core.gencode.research_healer.adapter import EVIDENCE_FILE_NAME, HEALER_MODE_ENV
from core.gencode.schema.gencode_v3_healer_telemetry_inspection import TABLE_NAME, healer_telemetry_table_exists
from core.gencode.services.v3_capability_ai_fill_service import (
    STATE_AWAITING,
    STATE_BLOCKED,
    run_system_ai_capability_fill,
)
from gencode.test_v3_capability_ai_fill import (
    _MockClient,
    _arch_json,
    _coder_json_ok,
    _conn_with_examples,
)

FENCE = "`" * 3
TEST_FILE = "tests/gencode/test_v3_fill_contract_demo.py"


def _fenced_coder_json(skill_id: str, example_ids: list[int]) -> str:
    payload = json.loads(_coder_json_ok(skill_id, example_ids))
    for item in payload["files"]:
        if item["path"] == TEST_FILE:
            item["content"] = f"Here is the test file:\n{FENCE}python\n{item['content']}{FENCE}\n"
    return json.dumps(payload, ensure_ascii=False)


def _clean_test_content(skill_id: str, example_ids: list[int]) -> str:
    payload = json.loads(_coder_json_ok(skill_id, example_ids))
    return next(item["content"] for item in payload["files"] if item["path"] == TEST_FILE)


def _run(mode: str | None, monkeypatch):
    if mode is None:
        monkeypatch.delenv(HEALER_MODE_ENV, raising=False)
    else:
        monkeypatch.setenv(HEALER_MODE_ENV, mode)
    skill_id = f"skill_rh_{uuid.uuid4().hex[:6]}"
    conn = _conn_with_examples(skill_id, [31])
    root = Path("reports") / f"pytest_ai_fill_rh_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    coder = _MockClient(_fenced_coder_json(skill_id, [31]))
    clients = {"architect": _MockClient(_arch_json(skill_id, [31])), "coder": coder}
    from core.registry.taxonomy_registry import SkillDomainNotRegisteredError

    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        side_effect=SkillDomainNotRegisteredError("missing"),
    ), mock.patch(
        "core.gencode.services.v3_capability_ai_fill_service.assert_edge_roles_are_local",
        return_value={"strategy": "local_first", "roles": {}},
    ), mock.patch(
        "core.gencode.services.v3_capability_ai_fill_service.get_effective_model_config",
        side_effect=lambda role: {"provider": "local", "model": "mock-local", "preset_key": "mock-local", "_resolved_source": "test"},
    ):
        result = run_system_ai_capability_fill(
            conn, skill_id, candidate_root=root, client_factory=lambda role: clients[role]
        )
    return result, conn, root, skill_id, coder


@pytest.fixture
def cleanup():
    items: list = []
    yield items
    for conn, root in items:
        conn.close()
        shutil.rmtree(root, ignore_errors=True)


def test_off_mode_keeps_ai_output_and_validator_blocks(monkeypatch, cleanup):
    result, conn, root, _, coder = _run(None, monkeypatch)
    cleanup.append((conn, root))
    assert result["status"] == STATE_BLOCKED
    assert coder.calls == 2
    job_dir = Path(result["job_dir"])
    assert not (job_dir / EVIDENCE_FILE_NAME).exists()
    manifest = json.loads((job_dir / "candidate_manifest.json").read_text(encoding="utf-8"))
    assert "research_healer" not in manifest
    assert not healer_telemetry_table_exists(conn)


def test_shadow_mode_records_evidence_but_validator_still_sees_ai_output(monkeypatch, cleanup):
    result, conn, root, _, _ = _run("shadow", monkeypatch)
    cleanup.append((conn, root))
    assert result["status"] == STATE_BLOCKED
    job_dir = Path(result["job_dir"])
    candidate = (job_dir / "candidate" / TEST_FILE).read_text(encoding="utf-8")
    assert candidate.startswith("Here is the test file:")
    evidence = [json.loads(x) for x in (job_dir / EVIDENCE_FILE_NAME).read_text(encoding="utf-8").splitlines()]
    assert [e["status"] for e in evidence] == ["REPAIRED", "REPAIRED"]
    assert all(e["applied_to_pipeline"] is False for e in evidence)
    rows = conn.execute(f"SELECT outcome FROM {TABLE_NAME} WHERE event_type='gate'").fetchall()
    assert rows == []


def test_repair_mode_existing_validator_accepts_fence_extraction(monkeypatch, cleanup):
    result, conn, root, skill_id, coder = _run("repair", monkeypatch)
    cleanup.append((conn, root))
    assert result["status"] == STATE_AWAITING
    assert coder.calls == 1
    job_dir = Path(result["job_dir"])
    candidate = (job_dir / "candidate" / TEST_FILE).read_text(encoding="utf-8")
    assert candidate == _clean_test_content(skill_id, [31])
    manifest = json.loads((job_dir / "candidate_manifest.json").read_text(encoding="utf-8"))
    assert manifest["promotion_allowed"] is False
    healer = manifest["research_healer"]
    assert len(healer) == 1 and healer[0]["status"] == "REPAIRED"
    assert healer[0]["semantic_preservation_proven"] is True and healer[0]["post_repair_gates"] == "passed"
    gate = [tuple(r) for r in conn.execute(f"SELECT outcome FROM {TABLE_NAME} WHERE event_type='gate'")]
    assert gate == [("passed",)]


def test_repair_mode_rolls_back_when_existing_validator_rejects(monkeypatch, cleanup):
    import core.gencode.services.v3_capability_ai_fill_service as fill_mod

    def _reject(*args, **kwargs):
        return {"passed": False, "blockers": ["forced_validator_rejection"]}

    monkeypatch.setattr(fill_mod, "validate_candidate_workspace", _reject)
    result, conn, root, _, _ = _run("repair", monkeypatch)
    cleanup.append((conn, root))
    assert result["status"] == STATE_BLOCKED
    job_dir = Path(result["job_dir"])
    candidate = (job_dir / "candidate" / TEST_FILE).read_text(encoding="utf-8")
    assert candidate.startswith("Here is the test file:")
    gates = [tuple(r) for r in conn.execute(f"SELECT outcome, gate_stage FROM {TABLE_NAME} WHERE event_type='gate'")]
    assert gates == [("failed", "official_compatibility"), ("failed", "official_compatibility")]
