# -*- coding: utf-8 -*-
"""Orchestrator for isolated Qwen Gencode experiment jobs."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any, Callable

from core.gencode.qwen_experiment.artifact_store import (
    PROJECT_ROOT,
    ArtifactStore,
    make_job_id,
    resolve_output_root,
    sha256_text,
    utc_now_iso,
)
from core.gencode.qwen_experiment.constants import (
    DEFAULT_MAX_REPAIR_ROUNDS,
    DEFAULT_MODEL_PRESET,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_PROMPT_MODE,
    DEFAULT_SEED,
    DEFAULT_TIMEOUT_SECONDS,
    PROMPT_VERSION,
)
from core.gencode.qwen_experiment.context_loader import build_experiment_context
from core.gencode.qwen_experiment.extract import (
    CodeExtractionError,
    DangerousCodeError,
    extract_and_sanitize,
)
from core.gencode.qwen_experiment.ollama_client import (
    OllamaExperimentClient,
    OllamaUnavailableError,
)
from core.gencode.qwen_experiment.prompt_builder import (
    build_generation_prompt,
    build_repair_prompt,
)
from core.gencode.qwen_experiment.validator_loop import validate_generated_component


def _git_meta(project_root: Path | None = None) -> dict[str, Any]:
    root = Path(project_root or PROJECT_ROOT)
    sha = ""
    dirty = False
    try:
        sha = (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=str(root),
                stderr=subprocess.DEVNULL,
                text=True,
            )
            .strip()
        )
    except Exception:
        sha = ""
    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=str(root),
            stderr=subprocess.DEVNULL,
            text=True,
        )
        dirty = bool(status.strip())
    except Exception:
        dirty = True
    return {"git_commit_sha": sha, "worktree_dirty": dirty}


def _default_hint_py() -> str:
    return '''from __future__ import annotations
from typing import Any

def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return "請先整理已知條件，再代入對應公式。"
'''


def _default_metadata_py(context: dict[str, Any]) -> str:
    return f'''from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "{context.get("component_id")}"
SKILL_ID: Final[str] = "{context.get("skill_id")}"
TEXTBOOK_EXAMPLE_ID: Final[int] = {int(context.get("textbook_example_id") or 0)}
GENERATOR_READINESS: Final[str] = "qwen_experiment_draft"
'''


def run_qwen_gencode_experiment(
    *,
    example_id: int,
    seed: int = DEFAULT_SEED,
    model_preset: str = DEFAULT_MODEL_PRESET,
    max_repair_rounds: int = DEFAULT_MAX_REPAIR_ROUNDS,
    output_root: str | Path | None = DEFAULT_OUTPUT_ROOT,
    resume: bool = False,
    prompt_mode: str = DEFAULT_PROMPT_MODE,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    job_id: str | None = None,
    db_path: str | Path | None = None,
    client: OllamaExperimentClient | None = None,
    client_factory: Callable[..., OllamaExperimentClient] | None = None,
    skip_ollama_check: bool = False,
) -> dict[str, Any]:
    """
    Run one isolated Qwen generate→validate→repair job.

    Never writes tracker verified/published, never touches agent_skills_v3,
    never switches global AI mode, never falls back to Gemini.
    """
    started_at = utc_now_iso()
    t0 = time.time()
    context = build_experiment_context(int(example_id), db_path=db_path)
    component_id = str(context["component_id"])
    skill_id = str(context["skill_id"])

    root = resolve_output_root(output_root)
    root.mkdir(parents=True, exist_ok=True)

    if resume and job_id:
        job_dir = root / str(job_id)
    elif resume:
        # Resume latest matching example/seed prefix if present.
        prefix = f"ex{int(example_id)}_s{int(seed)}_"
        candidates = sorted(
            [p for p in root.glob(f"{prefix}*") if p.is_dir()],
            key=lambda p: p.name,
            reverse=True,
        )
        if not candidates:
            raise FileNotFoundError(f"resume_job_not_found:prefix={prefix}")
        job_dir = candidates[0]
    else:
        jid = job_id or make_job_id(int(example_id), int(seed), started_at)
        job_dir = root / jid

    store = ArtifactStore(job_dir)
    existing_final = store.read_json("final_result.json")
    if resume and existing_final:
        status = str(existing_final.get("status") or "")
        # PASS is terminal. BLOCKED (e.g. Ollama down) is terminal unless caller starts a new job_id.
        # FAIL may continue repair rounds up to max_repair_rounds without re-running completed rounds.
        if status == "PASS":
            return existing_final
        if status == "BLOCKED":
            return existing_final

    git_meta = _git_meta()
    if client is None:
        factory = client_factory or OllamaExperimentClient
        try:
            client = factory(
                preset_key=model_preset,
                timeout=timeout,
                skip_availability_check=skip_ollama_check,
            )
        except OllamaUnavailableError as exc:
            blocked = {
                "status": "BLOCKED",
                "raw_pass": False,
                "repaired_pass": False,
                "rounds_used": 0,
                "elapsed_seconds": round(time.time() - t0, 3),
                "failure_layer": "ollama_unavailable",
                "variation_status": "not_run",
                "error": str(exc),
                "job_dir": str(job_dir),
                "model": {"provider": "ollama", "preset_key": model_preset},
                "artifact_sha256": {},
                "tracker_written": False,
                "production_written": False,
            }
            store.write_json("final_result.json", blocked)
            store.write_json("job.json", {"blocked": True, "error": str(exc), "started_at": started_at})
            return blocked

    assert client is not None
    model_snapshot = {
        **client.model_snapshot_fields(),
        "prompt_version": PROMPT_VERSION,
        "seed": int(seed),
        "started_at": started_at,
        "example_id": int(example_id),
        "skill_id": skill_id,
        "component_id": component_id,
        **git_meta,
        "no_gemini_fallback": True,
        "global_ai_mode_untouched": True,
    }
    store.write_json("model_snapshot.json", model_snapshot)

    job_state = store.read_json("job.json") or {
        "job_id": job_dir.name,
        "example_id": int(example_id),
        "skill_id": skill_id,
        "component_id": component_id,
        "seed": int(seed),
        "max_repair_rounds": int(max_repair_rounds),
        "prompt_mode": prompt_mode,
        "started_at": started_at,
        "completed_rounds": [],
        "status": "running",
    }
    completed_rounds = set(int(x) for x in (job_state.get("completed_rounds") or []) if str(x).isdigit() or isinstance(x, int))
    store.write_json("job.json", job_state)

    max_rounds = max(1, int(max_repair_rounds))
    previous_code = ""
    last_validation: dict[str, Any] = {}
    raw_pass = False
    repaired_pass = False
    rounds_used = 0
    final_status = "FAIL"
    failure_layer = ""
    variation_status = "not_run"

    for round_idx in range(1, max_rounds + 1):
        rounds_used = round_idx
        validation_name = f"validation_round_{round_idx}.json"
        extracted_name = f"extracted_generate_round_{round_idx}.py"

        if resume and store.exists(validation_name):
            last_validation = store.read_json(validation_name) or {}
            if store.exists(extracted_name):
                previous_code = store.path(extracted_name).read_text(encoding="utf-8")
            completed_rounds.add(round_idx)
            if last_validation.get("passed"):
                if round_idx == 1:
                    raw_pass = True
                repaired_pass = True
                final_status = "PASS"
                variation_status = str(last_validation.get("variation_status") or "")
                break
            # Failed completed round: continue to next repair round without re-calling model
            # for this completed round.
            continue

        if round_idx == 1:
            prompt = build_generation_prompt(context, seed=int(seed), prompt_mode=prompt_mode)
        else:
            prompt = build_repair_prompt(
                previous_code=previous_code,
                validation_errors=last_validation,
                context=context,
                seed=int(seed),
                round_idx=round_idx,
            )
        store.write_text(f"prompt_round_{round_idx}.txt", prompt)

        try:
            response = client.generate(prompt)
        except OllamaUnavailableError as exc:
            final_status = "BLOCKED"
            failure_layer = "ollama_unavailable"
            last_validation = {
                "passed": False,
                "failure_layer": failure_layer,
                "blockers": [str(exc)],
                "warnings": [],
                "checks": {},
                "variation_status": "not_run",
            }
            store.write_json(validation_name, last_validation)
            break

        store.write_text(f"raw_response_round_{round_idx}.txt", response.text)
        if response.thinking:
            store.write_text(f"thinking_round_{round_idx}.txt", response.thinking)

        try:
            extracted = extract_and_sanitize(response.text)
            code = extracted["code"]
        except (CodeExtractionError, DangerousCodeError) as exc:
            last_validation = {
                "passed": False,
                "failure_layer": "extract" if isinstance(exc, CodeExtractionError) else "dangerous_code",
                "blockers": [str(exc)],
                "warnings": [],
                "checks": {},
                "variation_status": "not_run",
            }
            store.write_json(validation_name, last_validation)
            previous_code = previous_code or ""
            completed_rounds.add(round_idx)
            job_state["completed_rounds"] = sorted(completed_rounds)
            store.write_json("job.json", job_state)
            failure_layer = str(last_validation["failure_layer"])
            continue

        store.write_text(extracted_name, code)
        previous_code = code
        # Write isolated component artifacts only under job dir.
        store.write_component_file(component_id, "generate.py", code)
        if "def get_hint" not in code:
            store.write_component_file(component_id, "get_hint.py", _default_hint_py())
        store.write_component_file(component_id, "metadata.py", _default_metadata_py(context))

        generate_path = store.components_dir / component_id / "generate.py"
        last_validation = validate_generated_component(
            generate_path=generate_path,
            component_id=component_id,
            skill_id=skill_id,
            workspace_root=store.job_dir,
            primary_seed=int(seed),
        )
        store.write_json(validation_name, last_validation)
        completed_rounds.add(round_idx)
        job_state["completed_rounds"] = sorted(completed_rounds)
        store.write_json("job.json", job_state)

        variation_status = str(last_validation.get("variation_status") or "")
        if last_validation.get("passed"):
            if round_idx == 1:
                raw_pass = True
            else:
                repaired_pass = True
            if round_idx == 1:
                repaired_pass = False
            final_status = "PASS"
            failure_layer = ""
            break
        failure_layer = str(last_validation.get("failure_layer") or "validation")

    if final_status != "PASS" and final_status != "BLOCKED":
        final_status = "FAIL"
        repaired_pass = False

    # If passed on round>1, raw_pass stays False; repaired_pass True.
    if final_status == "PASS" and rounds_used > 1:
        repaired_pass = True
        raw_pass = False
    elif final_status == "PASS" and rounds_used == 1:
        raw_pass = True
        repaired_pass = False

    elapsed = round(time.time() - t0, 3)
    artifact_hashes = store.collect_artifact_hashes()
    final_result = {
        "status": final_status,
        "raw_pass": bool(raw_pass),
        "repaired_pass": bool(repaired_pass and final_status == "PASS" and rounds_used > 1),
        "rounds_used": rounds_used,
        "elapsed_seconds": elapsed,
        "failure_layer": failure_layer if final_status != "PASS" else "",
        "variation_status": variation_status,
        "model": model_snapshot,
        "artifact_sha256": artifact_hashes,
        "job_id": job_dir.name,
        "job_dir": str(job_dir),
        "example_id": int(example_id),
        "skill_id": skill_id,
        "component_id": component_id,
        "seed": int(seed),
        "prompt_version": PROMPT_VERSION,
        "tracker_written": False,
        "production_written": False,
        "code_sha256": sha256_text(previous_code) if previous_code else None,
        "last_validation": {
            "passed": bool(last_validation.get("passed")),
            "failure_layer": last_validation.get("failure_layer"),
            "blockers": list(last_validation.get("blockers") or [])[:50],
            "variation_status": last_validation.get("variation_status"),
        },
    }
    store.write_json("final_result.json", final_result)
    job_state["status"] = final_status
    job_state["finished_at"] = utc_now_iso()
    job_state["completed_rounds"] = sorted(completed_rounds)
    store.write_json("job.json", job_state)
    return final_result
