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
from core.gencode.services.v3_capability_compatibility_validator import official_matrix_fields
from core.gencode.services.v3_skill_capability_preflight_service import (
    CAPABILITY_MISSING,
    CAPABILITY_READY,
)

OFFICIAL_DOMAIN = "coordinate_geometry.line_equation"
OFFICIAL_MODULE = "core.domain.coordinate_geometry.line_equation_domain"
OFFICIAL_ENTRY = "build_line_equation_matrix"
REGRESSION_SKILL = "vh_數學B1_SlopeInterceptForm"
OFFICIAL_OP = "two_points"


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


def _arch_json(skill_id: str, example_ids: list[int] | None = None) -> str:
    ids = list(example_ids or [])
    coverage = [
        {
            "textbook_example_id": eid,
            "operation": OFFICIAL_OP,
            "answer_contract": {
                "checker_key": "rational_checker",
                "answer_type": "rational",
                "answer_schema_key": "line_equation",
            },
        }
        for eid in ids
    ]
    return json.dumps(
        {
            "skill_id": skill_id,
            "capability_status": "missing",
            "domain_key": OFFICIAL_DOMAIN,
            "domain_module": OFFICIAL_MODULE,
            "entrypoint": OFFICIAL_ENTRY,
            "required_operations": [OFFICIAL_OP],
            "registry_operation_proposals": [],
            "matrix_required_fields": official_matrix_fields(),
            "answer_schema": {OFFICIAL_OP: "line_equation"},
            "checker": {OFFICIAL_OP: "rational_checker"},
            "example_coverage": coverage,
            "allowed_official_files": [
                "configs/gencode_taxonomy/k12_component_taxonomy.yaml",
                "tests/gencode/test_v3_fill_contract_demo.py",
            ],
            "regression_guards": [REGRESSION_SKILL],
            "missing_layers": ["domain_registry_binding"],
            "isomorphism_groups": [{"group_key": "t", "textbook_example_ids": ids}],
            "candidate_plan": {
                "files": [
                    "mutations/k12_component_taxonomy.yaml",
                    "tests/gencode/test_v3_fill_contract_demo.py",
                    "coverage_matrix.json",
                ],
                "summary": "bind existing line_equation domain",
            },
            "constraints": ["isolated_candidate_only", "official_architecture_only"],
        },
        ensure_ascii=False,
    )


def _coder_json_ok(skill_id: str, example_ids: list[int] | None = None) -> str:
    ids = list(example_ids or [])
    yaml_content = (
        "skills:\n"
        f"  {skill_id}:\n"
        f"    fixed_domain_key: {OFFICIAL_DOMAIN}\n"
        f"    domain_module: {OFFICIAL_MODULE}\n"
        f"    entrypoint: {OFFICIAL_ENTRY}\n"
        "    concrete: true\n"
        "    allowed_types:\n"
        f"      - {OFFICIAL_OP}\n"
    )
    test_content = (
        "from fractions import Fraction\n\n"
        f"def test_{skill_id}_regression_guard():\n"
        "    from core.registry.taxonomy_registry import resolve_domain_for_skill\n"
        f"    routing = resolve_domain_for_skill({REGRESSION_SKILL!r})\n"
        f"    assert routing['fixed_domain_key'] == {OFFICIAL_DOMAIN!r}\n"
        "    # vertical / undefined slope boundary: 斜率不存在\n"
        "    assert Fraction(1, 2) == Fraction(2, 4)\n"
    )
    coverage = [
        {
            "textbook_example_id": eid,
            "operation": OFFICIAL_OP,
            "answer_contract": {
                "checker_key": "rational_checker",
                "answer_type": "rational",
                "answer_schema_key": "line_equation",
            },
        }
        for eid in ids
    ]
    return json.dumps(
        {
            "skill_id": skill_id,
            "files": [
                {
                    "path": "mutations/k12_component_taxonomy.yaml",
                    "target": "configs/gencode_taxonomy/k12_component_taxonomy.yaml",
                    "mutation": "upsert_skill_binding",
                    "content": yaml_content,
                },
                {
                    "path": "tests/gencode/test_v3_fill_contract_demo.py",
                    "target": "tests/gencode/test_v3_fill_contract_demo.py",
                    "mutation": "add_focused_tests",
                    "content": test_content,
                },
            ],
            "coverage_matrix": coverage,
            "notes": "official mutation proposal",
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
        "architect": _MockClient(_arch_json(skill_id, [11, 12])),
        "coder": _MockClient(_coder_json_ok(skill_id, [11, 12])),
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
        assert (job_dir / "candidate" / "mutations" / "k12_component_taxonomy.yaml").is_file()
        assert (job_dir / "candidate" / "coverage_matrix.json").is_file()
        assert (job_dir / "candidate" / "tests" / "gencode" / "test_v3_fill_contract_demo.py").is_file()
        job = json.loads((job_dir / "job.json").read_text(encoding="utf-8"))
        assert job.get("official_compatibility_passed") is True
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
        job = json.loads((job_dir / "job.json").read_text(encoding="utf-8"))
        assert job["status"] == STATE_AWAITING
        assert job["ai_output_valid"] is True
        assert job["spec_origin"] == "architect"
        assert job["candidate_origin"] == "coder"
        spec = json.loads((job_dir / "capability_spec.json").read_text(encoding="utf-8"))
        assert spec["origin"] == "architect"
        assert spec["ai_generated"] is True
        manifest = json.loads((job_dir / "candidate_manifest.json").read_text(encoding="utf-8"))
        assert manifest["origin"] == "coder"
        for line in evidence_lines:
            row = json.loads(line)
            assert row["request_result"] == "ok"
            assert row.get("empty_model_output") is False
            blob = json.dumps(row, ensure_ascii=False)
            assert "你是系統角色" not in blob
            assert "capability_spec=" not in blob
            assert "GEMINI" not in blob.upper() or "gemini" not in str(row.get("provider") or "").lower()
    finally:
        shutil.rmtree(root, ignore_errors=True)
        conn.close()


def test_ai_fill_repair_then_block_or_await():
    import shutil

    skill_id = "skill_ai_fill_repair"
    conn = _conn_with_examples(skill_id, [21])
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    coder_texts = [_coder_json_bad_syntax(), _coder_json_ok(skill_id, [21])]

    class _CoderFlip(_MockClient):
        def generate_content(self, prompt, image_path=None):
            self.calls += 1
            return _MockResp(coder_texts[min(self.calls - 1, len(coder_texts) - 1)])

    clients = {
        "architect": _MockClient(_arch_json(skill_id, [21])),
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
        "architect": _MockClient(_arch_json(skill_id, [31])),
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
        "architect": _MockClient(_arch_json(skill_id, [41])),
        "coder": _MockClient(_coder_json_ok(skill_id, [41])),
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
        "architect": _MockClient(_arch_json(skill_id, [61])),
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
        assert not (job_dir / "candidate" / "escape.py").exists()
        assert result["status"] == STATE_BLOCKED
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
    assert "直接原因" in html
    assert "block_reason" in html
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
        assert result.get("block_reason") == "edge_cloud_role_blocked"
        assert called["n"] == 0
    finally:
        shutil.rmtree(root, ignore_errors=True)
        conn.close()


class _ThinkingResp:
    def __init__(self, text: str, thinking: str = "", *, empty_model_output: bool | None = None, http_ok: bool = True):
        self.text = text
        self.thinking = thinking
        self.http_ok = http_ok
        self.empty_model_output = (
            bool(empty_model_output) if empty_model_output is not None else not str(text or "").strip()
        )


class _ThinkingClient:
    def __init__(self, text: str, thinking: str = "", *, api_url: str = "http://127.0.0.1:11434/api/generate"):
        self._text = text
        self._thinking = thinking
        self.api_url = api_url
        self.calls = 0

    def generate_content(self, prompt, image_path=None):
        self.calls += 1
        return _ThinkingResp(self._text, self._thinking)


def _run_fill_with_clients(skill_id: str, example_ids: list[int], clients: dict, root: Path):
    conn = _conn_with_examples(skill_id, example_ids)
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
                "model": "qwen3.5:9b",
                "preset_key": "qwen3.5-9b",
                "_resolved_source": "test",
            },
        ):
            result = run_system_ai_capability_fill(
                conn,
                skill_id,
                candidate_root=root,
                client_factory=lambda role: clients[role],
            )
        return result
    finally:
        conn.close()


def test_thinking_with_visible_content_awaits():
    import shutil

    skill_id = "skill_think_ok"
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    clients = {
        "architect": _ThinkingClient(_arch_json(skill_id, [81]), thinking="internal chain"),
        "coder": _ThinkingClient(_coder_json_ok(skill_id, [81]), thinking="planning files"),
    }
    try:
        result = _run_fill_with_clients(skill_id, [81], clients, root)
        assert result["status"] == STATE_AWAITING
        assert result.get("ai_output_valid") is True
        lines = (Path(result["job_dir"]) / "model_call_evidence.jsonl").read_text(encoding="utf-8").strip().splitlines()
        for line in lines:
            row = json.loads(line)
            assert row["request_result"] == "ok"
            assert row["thinking_present"] is True
            assert row["thinking_enabled"] is False
            assert row["empty_model_output"] is False
            assert "internal chain" not in line
            assert "planning files" not in line
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_http200_empty_text_blocks_empty_model_output():
    import shutil

    skill_id = "skill_empty_text"
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    clients = {
        "architect": _ThinkingClient("", thinking="only thinking json {\"skill_id\":\"x\"}"),
        "coder": _MockClient(_coder_json_ok(skill_id, [82])),
    }
    try:
        result = _run_fill_with_clients(skill_id, [82], clients, root)
        assert result["ok"] is False
        assert result["status"] == STATE_BLOCKED
        assert result["block_reason"] == "empty_model_output"
        job = json.loads((Path(result["job_dir"]) / "job.json").read_text(encoding="utf-8"))
        assert job["status"] == STATE_BLOCKED
        assert job["block_reason"] == "empty_model_output"
        spec_path = Path(result["job_dir"]) / "capability_spec.json"
        if spec_path.is_file():
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            assert spec.get("candidate_plan", {}).get("summary") != "fallback_spec_from_preflight"
        evidence = json.loads(
            (Path(result["job_dir"]) / "model_call_evidence.jsonl").read_text(encoding="utf-8").strip().splitlines()[0]
        )
        assert evidence["request_result"] == "empty_model_output"
        assert evidence["empty_model_output"] is True
        assert evidence["thinking_present"] is True
        assert evidence["thinking_enabled"] is False
        assert clients["coder"].calls == 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_architect_invalid_json_blocks():
    import shutil

    skill_id = "skill_arch_bad_json"
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    clients = {
        "architect": _MockClient("not-json sorry"),
        "coder": _MockClient(_coder_json_ok(skill_id, [83])),
    }
    try:
        result = _run_fill_with_clients(skill_id, [83], clients, root)
        assert result["status"] == STATE_BLOCKED
        assert result["block_reason"] == "architect_invalid_spec"
        assert clients["coder"].calls == 0
        job = json.loads((Path(result["job_dir"]) / "job.json").read_text(encoding="utf-8"))
        assert job["block_reason"] == "architect_invalid_spec"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_coder_invalid_json_blocks():
    import shutil

    skill_id = "skill_coder_bad_json"
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    clients = {
        "architect": _MockClient(_arch_json(skill_id, [84])),
        "coder": _MockClient("definitely not candidate json"),
    }
    try:
        result = _run_fill_with_clients(skill_id, [84], clients, root)
        assert result["status"] == STATE_BLOCKED
        assert result["block_reason"] == "coder_invalid_contract"
        assert clients["coder"].calls == 1
        manifest = Path(result["job_dir"]) / "candidate_manifest.json"
        if manifest.is_file():
            data = json.loads(manifest.read_text(encoding="utf-8"))
            assert data.get("origin") != "deterministic_scaffold"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_diagnostic_fallback_cannot_enter_awaiting():
    spec = fill_mod.build_diagnostic_fallback_spec(
        {"capability_status": "missing", "domain_key": "d", "supported_operations": ["op"], "missing_layers": []},
        skill_id="skill_diag",
    )
    assert spec["origin"] == fill_mod.ORIGIN_DIAGNOSTIC_NON_AI
    assert spec["promotion_allowed"] is False
    assert spec["ai_generated"] is False
    with pytest.raises(fill_mod.CapabilityAiFillError) as exc:
        fill_mod._assert_awaiting_allowed(
            spec=spec,
            spec_origin=fill_mod.ORIGIN_DIAGNOSTIC_NON_AI,
            candidate_origin=fill_mod.ORIGIN_SCAFFOLD,
            architect_ok=True,
            coder_ok=True,
            validator_passed=True,
        )
    assert exc.value.code == "awaiting_gate_failed"
    src = Path(fill_mod.__file__).read_text(encoding="utf-8")
    assert "Minimal deterministic scaffold if model returned prose" not in src
    assert '"summary": "fallback_spec_from_preflight"' not in src


def test_gemini_like_client_without_thinking_attr_still_awaits():
    import shutil

    skill_id = "skill_gemini_like"
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    clients = {
        "architect": _MockClient(_arch_json(skill_id, [85]), api_url=""),
        "coder": _MockClient(_coder_json_ok(skill_id, [85]), api_url=""),
    }
    clients["architect"].api_url = None  # type: ignore[assignment]
    try:
        result = _run_fill_with_clients(skill_id, [85], clients, root)
        assert result["status"] == STATE_AWAITING
        assert result.get("ai_output_valid") is True
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_old_fallback_job_is_not_reusable():
    skill_id = "skill_old_fallback"
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    job_dir = root / "oldjob"
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "job.json").write_text(
        json.dumps(
            {
                "job_id": "oldjob",
                "skill_id": skill_id,
                "gap_fingerprint": "abc",
                "status": STATE_AWAITING,
            }
        ),
        encoding="utf-8",
    )
    job = json.loads((job_dir / "job.json").read_text(encoding="utf-8"))
    assert fill_mod._job_is_reusable(job) is False
    shutil = __import__("shutil")
    shutil.rmtree(root, ignore_errors=True)


class _ThinkAwareClient:
    def __init__(self, text: str):
        self._text = text
        self.think_args: list[object] = []
        self.api_url = "http://127.0.0.1:11434/api/generate"
        self.calls = 0

    def generate_content(self, prompt, image_path=None, *, think=None):
        self.calls += 1
        self.think_args.append(think)
        return _MockResp(self._text)


def test_fill_passes_think_false_and_records_thinking_enabled_false():
    import shutil

    skill_id = "skill_think_false"
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    clients = {
        "architect": _ThinkAwareClient(_arch_json(skill_id, [86])),
        "coder": _ThinkAwareClient(_coder_json_ok(skill_id, [86])),
    }
    try:
        result = _run_fill_with_clients(skill_id, [86], clients, root)
        assert result["status"] == STATE_AWAITING
        assert clients["architect"].think_args == [False]
        assert clients["coder"].think_args == [False]
        lines = (Path(result["job_dir"]) / "model_call_evidence.jsonl").read_text(encoding="utf-8").strip().splitlines()
        for line in lines:
            row = json.loads(line)
            assert row["thinking_enabled"] is False
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_fill_compatible_with_clients_that_reject_think_kwarg():
    import shutil

    skill_id = "skill_no_think_kw"
    root = Path("reports") / f"pytest_ai_fill_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    clients = {
        "architect": _MockClient(_arch_json(skill_id, [87])),
        "coder": _MockClient(_coder_json_ok(skill_id, [87])),
    }
    try:
        result = _run_fill_with_clients(skill_id, [87], clients, root)
        assert result["status"] == STATE_AWAITING
        assert clients["architect"].calls == 1
        assert clients["coder"].calls == 1
        evidence = json.loads(
            (Path(result["job_dir"]) / "model_call_evidence.jsonl").read_text(encoding="utf-8").strip().splitlines()[0]
        )
        assert evidence["thinking_enabled"] is False
    finally:
        shutil.rmtree(root, ignore_errors=True)
