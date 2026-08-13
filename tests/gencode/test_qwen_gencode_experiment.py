# -*- coding: utf-8 -*-
"""Focused tests for isolated Qwen Gencode experiment (mock Ollama only)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from core.gencode.qwen_experiment.artifact_store import ArtifactStore, resolve_output_root
from core.gencode.qwen_experiment.extract import (
    CodeExtractionError,
    DangerousCodeError,
    extract_and_sanitize,
    extract_python_code,
    scan_dangerous_code,
    strip_think_blocks,
)
from core.gencode.qwen_experiment.ollama_client import (
    OllamaCallResult,
    OllamaExperimentClient,
    OllamaUnavailableError,
)
from core.gencode.qwen_experiment.orchestrator import run_qwen_gencode_experiment
from core.gencode.qwen_experiment.prompt_builder import build_repair_prompt

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAFE_GENERATE = '''from __future__ import annotations
from typing import Any

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    s = int(seed or 0)
    return {
        "question_text": f"求斜率為 {s} 且過原點的直線方程式。",
        "correct_answer": f"y={s}x",
        "answer": f"y={s}x",
        "answer_type": "expression",
        "presentation_mode": "short_answer",
        "problem_type_id": "slope_intercept_equation",
        "choices": [],
        "answer_contract": {
            "answer_type": "expression",
            "checker_key": "expression_checker",
            "equivalence_type": "algebraic_equivalent",
        },
        "metadata": {"givens": {"slope": s}, "target": "line", "derivation": ["m"]},
        "component_id": kwargs.get("component_id"),
        "seed": seed,
    }

def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return "代入點斜式。"
'''

DANGEROUS_GENERATE = '''from __future__ import annotations
import subprocess
from typing import Any

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    subprocess.call(["echo", "x"])
    return {"question_text": "x", "answer": "1", "metadata": {"givens": {}, "target": "", "derivation": []}}
'''


class FakeOllama:
    def __init__(self, responses: list[str], *, fail_available: bool = False, missing_model: bool = False):
        self.responses = list(responses)
        self.calls = 0
        self.fail_available = fail_available
        self.missing_model = missing_model
        self.preset_key = "qwen3.5-9b"
        self.model = "qwen3.5:9b"
        self.base_url = "http://localhost:11434"
        self.temperature = 0.1
        self.max_tokens = 2048
        self.num_ctx = 8192
        self.timeout = 30
        if fail_available:
            raise OllamaUnavailableError("ollama_unreachable:mocked")
        if missing_model:
            raise OllamaUnavailableError("ollama_model_missing:qwen3.5:9b")

    def ensure_available(self) -> dict[str, Any]:
        return {"ok": True}

    def generate(self, prompt: str) -> OllamaCallResult:
        self.calls += 1
        if not self.responses:
            raise OllamaUnavailableError("ollama_no_more_mock_responses")
        text = self.responses.pop(0)
        return OllamaCallResult(text=text, raw={"message": {"content": text}}, thinking="")

    def model_snapshot_fields(self) -> dict[str, Any]:
        return {
            "provider": "ollama",
            "model": self.model,
            "preset_key": self.preset_key,
            "endpoint_type": "ollama_http",
            "endpoint": self.base_url,
            "temperature": self.temperature,
            "num_ctx": self.num_ctx,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
        }


def _fence(code: str, with_think: bool = False) -> str:
    body = f"```python\n{code}\n```"
    if with_think:
        return f"<think>secret reasoning</think>\n{body}\nThanks!"
    return body


@pytest.fixture
def exp_root(request) -> Path:
    # Avoid Windows permission issues on pytest's default Temp dir.
    root = (
        PROJECT_ROOT
        / "reports"
        / "gencode_qwen_dryrun"
        / "_pytest"
        / request.node.name
    )
    if root.exists():
        import shutil

        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_ollama_unavailable_stops_without_gemini(monkeypatch, exp_root: Path):
    def boom(**kwargs):
        raise OllamaUnavailableError("ollama_unreachable:mocked")

    monkeypatch.setattr(
        "core.gencode.qwen_experiment.orchestrator.build_experiment_context",
        lambda example_id, db_path=None: {
            "textbook_example_id": example_id,
            "skill_id": "vh_數學B1_SlopeInterceptForm",
            "component_id": f"src_{example_id}",
            "problem_text": "demo",
            "correct_answer": "y=x",
            "detailed_solution": "",
            "domain": {},
            "generate_interface_spec": "def generate",
            "allowed_checkers": ["expression_checker"],
            "answer_schema_keys": ["line_equation"],
        },
    )
    result = run_qwen_gencode_experiment(
        example_id=999001,
        seed=7,
        output_root=exp_root,
        client_factory=boom,
        skip_ollama_check=True,
    )
    assert result["status"] == "BLOCKED"
    assert result["failure_layer"] == "ollama_unavailable"
    assert "gemini" not in json.dumps(result).lower() or result["model"].get("provider") == "ollama"
    assert result.get("tracker_written") is False


def test_strip_think_and_extract_python():
    raw = _fence(SAFE_GENERATE, with_think=True)
    assert "<think>" not in strip_think_blocks(raw)
    code = extract_python_code(raw)
    assert "def generate" in code
    assert "<think>" not in code
    assert "Thanks" not in code
    out = extract_and_sanitize(raw)
    assert "def generate" in out["code"]


def test_dangerous_code_rejected():
    blockers = scan_dangerous_code(DANGEROUS_GENERATE)
    assert any("subprocess" in b or "forbidden" in b for b in blockers)
    with pytest.raises(DangerousCodeError):
        extract_and_sanitize(_fence(DANGEROUS_GENERATE))


def test_artifacts_only_under_experiment_dir(monkeypatch, exp_root: Path):
    monkeypatch.setattr(
        "core.gencode.qwen_experiment.orchestrator.build_experiment_context",
        lambda example_id, db_path=None: {
            "textbook_example_id": example_id,
            "skill_id": "vh_數學B1_SlopeInterceptForm",
            "component_id": f"src_{example_id}",
            "problem_text": "demo",
            "correct_answer": "y=x",
            "detailed_solution": "",
            "domain": {"fixed_domain_key": "x", "allowed_operations": [], "domain_module": "", "entrypoint": ""},
            "generate_interface_spec": "def generate",
            "allowed_checkers": ["expression_checker"],
            "answer_schema_keys": ["line_equation"],
        },
    )

    def fake_validate(**kwargs):
        return {
            "passed": True,
            "failure_layer": "",
            "blockers": [],
            "warnings": [],
            "checks": {},
            "variation_status": "dynamic",
        }

    monkeypatch.setattr(
        "core.gencode.qwen_experiment.orchestrator.validate_generated_component",
        fake_validate,
    )
    client = FakeOllama([_fence(SAFE_GENERATE, with_think=True)])
    result = run_qwen_gencode_experiment(
        example_id=999002,
        seed=7,
        output_root=exp_root,
        client=client,
        skip_ollama_check=True,
        job_id="ex999002_s7_testart",
    )
    job_dir = Path(result["job_dir"])
    assert exp_root.resolve() in job_dir.resolve().parents or job_dir.parent == exp_root.resolve()
    assert (job_dir / "components" / "src_999002" / "generate.py").is_file()
    # Must not land under production.
    assert "agent_skills_v3" not in str(job_dir)
    assert result["status"] == "PASS"
    assert result["tracker_written"] is False
    assert result["production_written"] is False


def test_validator_errors_enter_repair_prompt():
    prompt = build_repair_prompt(
        previous_code=SAFE_GENERATE,
        validation_errors={
            "passed": False,
            "failure_layer": "payload_validator",
            "blockers": ["generic_stem_detected"],
            "warnings": [],
            "checks": {"sample_payloads": [{"answer": "SECRET"}]},
            "hidden_answers": ["SHOULD_NOT_APPEAR"],
        },
        context={
            "skill_id": "vh_demo",
            "component_id": "src_1",
            "generate_interface_spec": "def generate",
            "allowed_checkers": ["expression_checker"],
            "domain": {},
        },
        seed=7,
        round_idx=2,
    )
    assert "generic_stem_detected" in prompt
    assert "SECRET" not in prompt
    assert "SHOULD_NOT_APPEAR" not in prompt
    assert "Previous code" in prompt


def test_stops_after_three_rounds(monkeypatch, exp_root: Path):
    monkeypatch.setattr(
        "core.gencode.qwen_experiment.orchestrator.build_experiment_context",
        lambda example_id, db_path=None: {
            "textbook_example_id": example_id,
            "skill_id": "vh_數學B1_SlopeInterceptForm",
            "component_id": f"src_{example_id}",
            "problem_text": "demo",
            "correct_answer": "y=x",
            "detailed_solution": "",
            "domain": {},
            "generate_interface_spec": "def generate",
            "allowed_checkers": ["expression_checker"],
            "answer_schema_keys": ["line_equation"],
        },
    )
    monkeypatch.setattr(
        "core.gencode.qwen_experiment.orchestrator.validate_generated_component",
        lambda **kwargs: {
            "passed": False,
            "failure_layer": "payload_validator",
            "blockers": ["generic_stem_detected"],
            "warnings": [],
            "checks": {},
            "variation_status": "static",
        },
    )
    client = FakeOllama([_fence(SAFE_GENERATE)] * 3)
    result = run_qwen_gencode_experiment(
        example_id=999003,
        seed=7,
        max_repair_rounds=3,
        output_root=exp_root,
        client=client,
        job_id="ex999003_s7_three",
    )
    assert result["status"] == "FAIL"
    assert result["rounds_used"] == 3
    assert client.calls == 3
    job_dir = Path(result["job_dir"])
    assert (job_dir / "validation_round_3.json").is_file()
    assert not (job_dir / "validation_round_4.json").exists()


def test_pass_does_not_write_tracker_or_publish(monkeypatch, exp_root: Path):
    written = {"tracker": False, "publish": False}

    def guard_tracker(*args, **kwargs):
        written["tracker"] = True
        raise AssertionError("tracker write attempted")

    monkeypatch.setattr(
        "core.gencode.qwen_experiment.orchestrator.build_experiment_context",
        lambda example_id, db_path=None: {
            "textbook_example_id": example_id,
            "skill_id": "vh_數學B1_SlopeInterceptForm",
            "component_id": f"src_{example_id}",
            "problem_text": "demo",
            "correct_answer": "y=x",
            "detailed_solution": "",
            "domain": {},
            "generate_interface_spec": "def generate",
            "allowed_checkers": ["expression_checker"],
            "answer_schema_keys": ["line_equation"],
        },
    )
    monkeypatch.setattr(
        "core.gencode.qwen_experiment.orchestrator.validate_generated_component",
        lambda **kwargs: {
            "passed": True,
            "failure_layer": "",
            "blockers": [],
            "warnings": [],
            "checks": {},
            "variation_status": "dynamic",
        },
    )
    # Ensure orchestrator module does not call tracker helpers even if imported elsewhere.
    import core.gencode.services.component_tracker_service as tracker_mod

    monkeypatch.setattr(tracker_mod, "save_tracker_record", guard_tracker)
    monkeypatch.setattr(tracker_mod, "update_status", guard_tracker)

    client = FakeOllama([_fence(SAFE_GENERATE)])
    result = run_qwen_gencode_experiment(
        example_id=999004,
        seed=7,
        output_root=exp_root,
        client=client,
        job_id="ex999004_s7_pass",
    )
    assert result["status"] == "PASS"
    assert result["tracker_written"] is False
    assert result["production_written"] is False
    assert written["tracker"] is False


def test_resume_skips_completed_rounds(monkeypatch, exp_root: Path):
    monkeypatch.setattr(
        "core.gencode.qwen_experiment.orchestrator.build_experiment_context",
        lambda example_id, db_path=None: {
            "textbook_example_id": example_id,
            "skill_id": "vh_數學B1_SlopeInterceptForm",
            "component_id": f"src_{example_id}",
            "problem_text": "demo",
            "correct_answer": "y=x",
            "detailed_solution": "",
            "domain": {},
            "generate_interface_spec": "def generate",
            "allowed_checkers": ["expression_checker"],
            "answer_schema_keys": ["line_equation"],
        },
    )
    # First run: fail round 1 only (max 1), then resume with max 3 and success on next call.
    monkeypatch.setattr(
        "core.gencode.qwen_experiment.orchestrator.validate_generated_component",
        lambda **kwargs: {
            "passed": False,
            "failure_layer": "payload_validator",
            "blockers": ["generic_stem_detected"],
            "warnings": [],
            "checks": {},
            "variation_status": "static",
        },
    )
    client1 = FakeOllama([_fence(SAFE_GENERATE)])
    first = run_qwen_gencode_experiment(
        example_id=999005,
        seed=7,
        max_repair_rounds=1,
        output_root=exp_root,
        client=client1,
        job_id="ex999005_s7_resume",
    )
    assert first["status"] == "FAIL"
    assert client1.calls == 1

    calls = {"n": 0}

    def validate_pass_second(**kwargs):
        # After resume, round1 skipped; round2 validation uses this.
        return {
            "passed": True,
            "failure_layer": "",
            "blockers": [],
            "warnings": [],
            "checks": {},
            "variation_status": "dynamic",
        }

    monkeypatch.setattr(
        "core.gencode.qwen_experiment.orchestrator.validate_generated_component",
        validate_pass_second,
    )
    client2 = FakeOllama([_fence(SAFE_GENERATE)])
    second = run_qwen_gencode_experiment(
        example_id=999005,
        seed=7,
        max_repair_rounds=3,
        output_root=exp_root,
        client=client2,
        job_id="ex999005_s7_resume",
        resume=True,
    )
    assert client2.calls == 1  # only round 2
    assert second["status"] == "PASS"
    assert second["rounds_used"] == 2


def test_production_files_hash_unchanged(monkeypatch, exp_root: Path):
    prod = PROJECT_ROOT / "agent_skills_v3"
    samples = []
    if prod.is_dir():
        for path in sorted(prod.rglob("generate.py"))[:3]:
            samples.append((path, hashlib.sha256(path.read_bytes()).hexdigest()))
    # Even if no production samples, experiment must still avoid writing there.
    monkeypatch.setattr(
        "core.gencode.qwen_experiment.orchestrator.build_experiment_context",
        lambda example_id, db_path=None: {
            "textbook_example_id": example_id,
            "skill_id": "vh_數學B1_SlopeInterceptForm",
            "component_id": f"src_{example_id}",
            "problem_text": "demo",
            "correct_answer": "y=x",
            "detailed_solution": "",
            "domain": {},
            "generate_interface_spec": "def generate",
            "allowed_checkers": ["expression_checker"],
            "answer_schema_keys": ["line_equation"],
        },
    )
    monkeypatch.setattr(
        "core.gencode.qwen_experiment.orchestrator.validate_generated_component",
        lambda **kwargs: {
            "passed": True,
            "failure_layer": "",
            "blockers": [],
            "warnings": [],
            "checks": {},
            "variation_status": "dynamic",
        },
    )
    client = FakeOllama([_fence(SAFE_GENERATE)])
    run_qwen_gencode_experiment(
        example_id=999006,
        seed=7,
        output_root=exp_root,
        client=client,
        job_id="ex999006_s7_prodhash",
    )
    for path, digest in samples:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest


def test_missing_generate_rejected():
    with pytest.raises(CodeExtractionError):
        extract_python_code("```python\nprint('hi')\n```")


def test_resolve_output_root_rejects_outside():
    with pytest.raises(ValueError):
        resolve_output_root(PROJECT_ROOT / "agent_skills_v3" / "not_experiment")


def test_ollama_client_rejects_non_local_preset(monkeypatch):
    from config import Config

    monkeypatch.setitem(
        Config.CODER_PRESETS,
        "fake-cloud",
        {"provider": "google", "model": "gemini-2.5-flash"},
    )
    with pytest.raises(OllamaUnavailableError):
        OllamaExperimentClient(preset_key="fake-cloud", skip_availability_check=True)
