# -*- coding: utf-8 -*-
"""Focused tests for system AI capability fill (phase-1, mock clients only)."""

from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from unittest import mock

import pytest

from core.gencode.services import v3_capability_ai_fill_service as fill_mod
from core.gencode.services.v3_capability_ai_fill_service import (
    FORBIDDEN_GENCODE_AI_RESOLVE,
    STATE_AWAITING,
    STATE_BLOCKED,
    assert_edge_roles_are_local,
    run_system_ai_capability_fill,
)
from core.gencode.services.v3_skill_capability_preflight_service import (
    CAPABILITY_MISSING,
    CAPABILITY_READY,
)


class _MockResp:
    def __init__(self, text: str):
        self.text = text


class _MockClient:
    def __init__(self, text: str, *, api_url: str = "http://127.0.0.1:11434/api/generate"):
        self._text = text
        self.api_url = api_url
        self.calls = 0

    def generate_content(self, prompt, image_path=None):
        self.calls += 1
        return _MockResp(self._text)


def _conn_with_examples(skill_id: str, example_ids: list[int]) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            problem_text TEXT,
            correct_answer TEXT,
            detailed_solution TEXT,
            source_description TEXT,
            problem_type TEXT,
            notes TEXT
        )
        """
    )
    for eid in example_ids:
        conn.execute(
            """
            INSERT INTO textbook_examples (
                id, skill_id, problem_text, correct_answer, detailed_solution,
                source_description, problem_type, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (eid, skill_id, f"Q{eid}", f"A{eid}", "", f"src{eid}", "t", ""),
        )
    conn.commit()
    return conn


def _arch_json(skill_id: str) -> str:
    return json.dumps(
        {
            "skill_id": skill_id,
            "capability_status": "missing",
            "domain_key_suggestion": "demo_domain",
            "required_operations": ["demo_op"],
            "missing_layers": ["domain_registry_binding"],
            "isomorphism_groups": [{"group_key": "t", "textbook_example_ids": [1]}],
            "candidate_plan": {"files": ["domain_module.py"], "summary": "demo"},
            "constraints": ["isolated_candidate_only"],
        },
        ensure_ascii=False,
    )


def _coder_json_ok() -> str:
    return json.dumps(
        {
            "files": [
                {
                    "path": "domain_module.py",
                    "content": "DOMAIN_KEY = 'demo_domain'\nREQUIRED_OPERATIONS = ['demo_op']\n\ndef build_fixture_matrix():\n    return {'operations': REQUIRED_OPERATIONS}\n",
                }
            ],
            "notes": "ok",
        },
        ensure_ascii=False,
    )


def _coder_json_bad_syntax() -> str:
    return json.dumps(
        {
            "files": [
                {
                    "path": "domain_module.py",
                    "content": "def broken(\n",
                }
            ],
            "notes": "bad",
        },
        ensure_ascii=False,
    )


def test_source_forbids_resolve_gencode_ai_client():
    src = Path(fill_mod.__file__).read_text(encoding="utf-8")
    assert "from core.gencode.gencode_ai_resolve" not in src
    assert "import resolve_gencode_ai_client" not in src
    assert FORBIDDEN_GENCODE_AI_RESOLVE in src  # documented forbid constant only


def test_edge_architect_and_coder_map_to_local_presets():
    from core.routes.admin import _generate_model_roles

    available = [
        {"key": "qwen3-8b"},
        {"key": "qwen3-vl-8b"},
        {"key": "gemini-3.5-flash"},
    ]
    edge_roles = _generate_model_roles("edge", available, cloud_model="gemini-3.5-flash")
    assert edge_roles["architect"] == edge_roles["coder"]
    assert "gemini" not in str(edge_roles["architect"]).lower()

    hybrid_roles = _generate_model_roles("hybrid", available, cloud_model="gemini-3.5-flash")
    assert "gemini" in str(hybrid_roles["architect"]).lower() or hybrid_roles["architect"] == "gemini-3.5-flash"
    assert "gemini" not in str(hybrid_roles["coder"]).lower()


def test_assert_edge_roles_block_cloud_resolution():
    with mock.patch(
        "core.gencode.services.v3_capability_ai_fill_service.get_ai_settings_snapshot",
        return_value={"ai_global_strategy": "local_first"},
    ), mock.patch(
        "core.gencode.services.v3_capability_ai_fill_service.get_effective_model_config",
        side_effect=lambda role: {
            "provider": "google" if role == "architect" else "local",
            "model": "gemini-x",
            "preset_key": "gemini-x",
        },
    ):
        with pytest.raises(fill_mod.CapabilityAiFillError) as exc:
            assert_edge_roles_are_local()
    assert exc.value.code == "edge_cloud_role_blocked"


def test_ai_fill_success_awaits_admin_confirm():
    import shutil

    skill_id = "skill_ai_fill_ok"
    conn = _conn_with_examples(skill_id, [11, 12])
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    clients = {
        "architect": _MockClient(_arch_json(skill_id)),
        "coder": _MockClient(_coder_json_ok()),
    }

    from core.registry.taxonomy_registry import SkillDomainNotRegisteredError

    try:
        with mock.patch(
            "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
            side_effect=SkillDomainNotRegisteredError("missing"),
        ), mock.patch(
            "core.gencode.services.v3_capability_ai_fill_service.assert_edge_roles_are_local",
            return_value={"strategy": "local_first", "roles": {"architect": {"provider": "local"}, "coder": {"provider": "local"}}},
        ), mock.patch(
            "core.gencode.services.v3_capability_ai_fill_service.get_effective_model_config",
            side_effect=lambda role: {
                "provider": "local",
                "model": "mock-local",
                "preset_key": "mock-local",
                "_resolved_source": "test",
            },
        ):
            result = run_system_ai_capability_fill(
                conn,
                skill_id,
                candidate_root=root,
                client_factory=lambda role: clients[role],
            )

        assert result["ok"] is True
        assert result["status"] == STATE_AWAITING
        job_dir = Path(result["job_dir"])
        assert str(job_dir).startswith(str(root))
        assert (job_dir / "job.json").is_file()
        assert (job_dir / "preflight.json").is_file()
        assert (job_dir / "capability_spec.json").is_file()
        assert (job_dir / "candidate" / "domain_module.py").is_file()
        assert (job_dir / "model_call_evidence.jsonl").is_file()
        assert (job_dir / "validator_results.jsonl").is_file()

        evidence_lines = (job_dir / "model_call_evidence.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(evidence_lines) >= 2
        first = json.loads(evidence_lines[0])
        for key in (
            "role",
            "provider",
            "model",
            "preset_key",
            "endpoint",
            "request_result",
            "latency_ms",
            "prompt_sha256",
            "response_sha256",
            "timestamp",
        ):
            assert key in first
        assert "model_generation_invoked" not in first
        assert clients["architect"].calls == 1
        assert clients["coder"].calls == 1
    finally:
        shutil.rmtree(root, ignore_errors=True)
        conn.close()


def test_ai_fill_repair_then_block_or_await():
    import shutil

    skill_id = "skill_ai_fill_repair"
    conn = _conn_with_examples(skill_id, [21])
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    coder_texts = [_coder_json_bad_syntax(), _coder_json_ok()]

    class _CoderFlip(_MockClient):
        def generate_content(self, prompt, image_path=None):
            self.calls += 1
            return _MockResp(coder_texts[min(self.calls - 1, len(coder_texts) - 1)])

    clients = {
        "architect": _MockClient(_arch_json(skill_id)),
        "coder": _CoderFlip("x"),
    }
    from core.registry.taxonomy_registry import SkillDomainNotRegisteredError

    try:
        with mock.patch(
            "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
            side_effect=SkillDomainNotRegisteredError("missing"),
        ), mock.patch(
            "core.gencode.services.v3_capability_ai_fill_service.assert_edge_roles_are_local",
            return_value={"strategy": "hybrid_balanced", "roles": {}},
        ), mock.patch(
            "core.gencode.services.v3_capability_ai_fill_service.get_effective_model_config",
            side_effect=lambda role: {
                "provider": "local",
                "model": "mock-local",
                "preset_key": "mock-local",
                "_resolved_source": "test",
            },
        ):
            result = run_system_ai_capability_fill(
                conn,
                skill_id,
                candidate_root=root,
                client_factory=lambda role: clients[role],
            )

        assert result["status"] == STATE_AWAITING
        assert result.get("coder_rounds_used") == 2
        assert clients["coder"].calls == 2
    finally:
        shutil.rmtree(root, ignore_errors=True)
        conn.close()


def test_ai_fill_blocked_after_two_failed_rounds():
    import shutil

    skill_id = "skill_ai_fill_blocked"
    conn = _conn_with_examples(skill_id, [31])
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    clients = {
        "architect": _MockClient(_arch_json(skill_id)),
        "coder": _MockClient(_coder_json_bad_syntax()),
    }
    from core.registry.taxonomy_registry import SkillDomainNotRegisteredError

    try:
        with mock.patch(
            "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
            side_effect=SkillDomainNotRegisteredError("missing"),
        ), mock.patch(
            "core.gencode.services.v3_capability_ai_fill_service.assert_edge_roles_are_local",
            return_value={"strategy": "hybrid_balanced", "roles": {}},
        ), mock.patch(
            "core.gencode.services.v3_capability_ai_fill_service.get_effective_model_config",
            side_effect=lambda role: {
                "provider": "local",
                "model": "mock-local",
                "preset_key": "mock-local",
                "_resolved_source": "test",
            },
        ):
            result = run_system_ai_capability_fill(
                conn,
                skill_id,
                candidate_root=root,
                client_factory=lambda role: clients[role],
            )

        assert result["ok"] is False
        assert result["status"] == STATE_BLOCKED
        assert clients["coder"].calls == 2
    finally:
        shutil.rmtree(root, ignore_errors=True)
        conn.close()


def test_ai_fill_dedupes_same_fingerprint():
    import shutil

    skill_id = "skill_ai_fill_dedupe"
    conn = _conn_with_examples(skill_id, [41])
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    clients = {
        "architect": _MockClient(_arch_json(skill_id)),
        "coder": _MockClient(_coder_json_ok()),
    }
    from core.registry.taxonomy_registry import SkillDomainNotRegisteredError

    try:
        with mock.patch(
            "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
            side_effect=SkillDomainNotRegisteredError("missing"),
        ), mock.patch(
            "core.gencode.services.v3_capability_ai_fill_service.assert_edge_roles_are_local",
            return_value={"strategy": "local_first", "roles": {}},
        ), mock.patch(
            "core.gencode.services.v3_capability_ai_fill_service.get_effective_model_config",
            side_effect=lambda role: {
                "provider": "local",
                "model": "mock-local",
                "preset_key": "mock-local",
                "_resolved_source": "test",
            },
        ):
            first = run_system_ai_capability_fill(
                conn,
                skill_id,
                candidate_root=root,
                client_factory=lambda role: clients[role],
            )
            second = run_system_ai_capability_fill(
                conn,
                skill_id,
                candidate_root=root,
                client_factory=lambda role: clients[role],
            )

        assert first["reused"] is False
        assert second["reused"] is True
        assert first["job_id"] == second["job_id"]
        assert clients["architect"].calls == 1
    finally:
        shutil.rmtree(root, ignore_errors=True)
        conn.close()


def test_ai_fill_rejects_ready_skill():
    skill_id = "skill_ready_no_fill"
    conn = _conn_with_examples(skill_id, [51])
    with mock.patch(
        "core.gencode.services.v3_capability_ai_fill_service.evaluate_skill_v3_capability",
        return_value={
            "skill_id": skill_id,
            "capability_status": CAPABILITY_READY,
            "allow_v3_rebuild": True,
            "missing_layers": [],
            "unresolved_example_ids": [],
            "supported_operations": ["op"],
            "domain_key": "d",
            "domain_module": "m",
            "entrypoint": "e",
        },
    ):
        with pytest.raises(fill_mod.CapabilityAiFillError) as exc:
            run_system_ai_capability_fill(
                conn,
                skill_id,
                candidate_root=Path("reports") / f"pytest_skip_{uuid.uuid4().hex[:6]}",
            )
    assert exc.value.code == "capability_already_ready"
    conn.close()


def test_candidate_stays_under_allowed_root():
    import shutil

    skill_id = "skill_ai_fill_path"
    conn = _conn_with_examples(skill_id, [61])
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    escape_payload = json.dumps(
        {
            "files": [
                {"path": "../escape.py", "content": "x=1\n"},
                {
                    "path": "domain_module.py",
                    "content": "DOMAIN_KEY='d'\nREQUIRED_OPERATIONS=['op']\ndef build_fixture_matrix():\n    return {}\n",
                },
            ]
        }
    )
    clients = {
        "architect": _MockClient(_arch_json(skill_id)),
        "coder": _MockClient(escape_payload),
    }
    from core.registry.taxonomy_registry import SkillDomainNotRegisteredError

    try:
        with mock.patch(
            "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
            side_effect=SkillDomainNotRegisteredError("missing"),
        ), mock.patch(
            "core.gencode.services.v3_capability_ai_fill_service.assert_edge_roles_are_local",
            return_value={"strategy": "local_first", "roles": {}},
        ), mock.patch(
            "core.gencode.services.v3_capability_ai_fill_service.get_effective_model_config",
            side_effect=lambda role: {
                "provider": "local",
                "model": "mock-local",
                "preset_key": "mock-local",
                "_resolved_source": "test",
            },
        ):
            result = run_system_ai_capability_fill(
                conn,
                skill_id,
                candidate_root=root,
                client_factory=lambda role: clients[role],
            )

        job_dir = Path(result["job_dir"])
        assert not (root / "escape.py").exists()
        assert (job_dir / "candidate" / "domain_module.py").is_file()
        assert not (Path("core") / "escape.py").exists()
    finally:
        shutil.rmtree(root, ignore_errors=True)
        conn.close()


def test_ui_shows_system_ai_fill_and_export_diagnosis():
    html = (Path(__file__).resolve().parents[2] / "templates" / "admin_skills.html").read_text(
        encoding="utf-8"
    )
    assert "系統AI補全能力" in html
    assert "匯出診斷" in html
    assert "startSkillCapabilityAiFill" in html
    assert "exportSkillCapabilityDiagnosis" in html
    assert "v3_capability_ai_fill" in html
    assert "onclick=\"createSkillCapabilityHandoff(" not in html


def test_edge_cloud_blocks_before_model_call():
    import shutil

    skill_id = "skill_edge_block"
    conn = _conn_with_examples(skill_id, [71])
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    called = {"n": 0}

    def factory(role):
        called["n"] += 1
        return _MockClient("should_not_run")

    from core.registry.taxonomy_registry import SkillDomainNotRegisteredError

    try:
        with mock.patch(
            "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
            side_effect=SkillDomainNotRegisteredError("missing"),
        ), mock.patch(
            "core.gencode.services.v3_capability_ai_fill_service.get_ai_settings_snapshot",
            return_value={"ai_global_strategy": "local_first"},
        ), mock.patch(
            "core.gencode.services.v3_capability_ai_fill_service.get_effective_model_config",
            side_effect=lambda role: {
                "provider": "google",
                "model": "gemini-blocked",
                "preset_key": "gemini-blocked",
                "_resolved_source": "test",
            },
        ):
            result = run_system_ai_capability_fill(
                conn,
                skill_id,
                candidate_root=root,
                client_factory=factory,
            )

        assert result["status"] == STATE_BLOCKED
        assert result.get("error") == "edge_cloud_role_blocked"
        assert called["n"] == 0
    finally:
        shutil.rmtree(root, ignore_errors=True)
        conn.close()
