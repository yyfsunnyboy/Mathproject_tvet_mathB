# -*- coding: utf-8 -*-
"""Validation-only reconciliation for existing V3 components.

Side-effect audit (why we do NOT call publish / _auto_promote directly):

- ``_auto_promote_valid_components``: does not rewrite generate.py, but writes
  tracker for *all* skill components; on source-completeness failure it may
  overwrite a verified row with ``needs_human_review``.
- ``publish_single_v3_skill_to_production``: calls auto-promote, then
  ``compile_and_double_write_skill``, staging sync, production smoke — full
  publish that rewrites wrappers / manifests / production tree.
- ``run_admin_v3_dryrun_for_skill(mode=verify_existing)``: only skips rebuild
  when tracker is already verified; missing tracker falls through to
  ``run_admin_v3_dryrun_for_example`` and can regenerate.
- ``save_tracker_record`` / ``update_status``: DB-only; safe when called after
  validation with an explicit whitelist.

This service only reads existing dryrun/production components, reuses the
official compile/smoke/integrity validators, and optionally writes tracker
rows for whitelisted source_ids that fully pass.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import py_compile
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from core.gencode.services.component_tracker_service import (
    assert_textbook_example_skill,
    derive_component_id,
    save_tracker_record,
)
from core.gencode.services.v3_question_integrity_validator import (
    DEFAULT_INTEGRITY_SEEDS,
    validate_component_payload,
)
from core.gencode.runtime_skill_wrapper import check_answer

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Explicit whitelist for this remediation wave.
ABSOLUTE_VALUE_SKILL = "vh_數學B1_AbsoluteValue"
ABSOLUTE_VALUE_SOURCE_IDS: tuple[int, ...] = (4398, 4399, 4408, 4412)

ABSOLUTE_VALUE_INEQUALITY_SKILL = "vh_數學B1_AbsoluteValueInequality"
ABSOLUTE_VALUE_INEQUALITY_SOURCE_IDS: tuple[int, ...] = (
    4400,
    4402,
    4403,
    4404,
    4405,
    4406,
    4407,
    4409,
    4413,
    4499,
)

DEFAULT_RECONCILE_TARGETS: dict[str, tuple[int, ...]] = {
    ABSOLUTE_VALUE_SKILL: ABSOLUTE_VALUE_SOURCE_IDS,
    ABSOLUTE_VALUE_INEQUALITY_SKILL: ABSOLUTE_VALUE_INEQUALITY_SOURCE_IDS,
}


def _sha256_file(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _load_module(path: Path, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module_load_failed:{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _parse_payload(raw: Any) -> dict[str, Any]:
    if raw is None or str(raw).strip() == "":
        return {}
    if isinstance(raw, dict):
        return dict(raw)
    try:
        data = json.loads(str(raw))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except Exception:
        return str(path)


def _component_paths(
    *,
    project_root: Path,
    skill_id: str,
    component_id: str,
    dryrun_base_dir: str,
    production_base_dir: str,
) -> dict[str, Path]:
    dryrun_dir = (
        project_root / dryrun_base_dir / skill_id / "components" / component_id
    )
    production_dir = (
        project_root / production_base_dir / skill_id / "components" / component_id
    )
    return {
        "dryrun_dir": dryrun_dir,
        "production_dir": production_dir,
        "dryrun_generate": dryrun_dir / "generate.py",
        "dryrun_metadata": dryrun_dir / "metadata.py",
        "dryrun_hint": dryrun_dir / "get_hint.py",
        "production_generate": production_dir / "generate.py",
        "production_metadata": production_dir / "metadata.py",
        "production_hint": production_dir / "get_hint.py",
    }


def _validate_tree(
    *,
    label: str,
    generate_py: Path,
    metadata_py: Path,
    hint_py: Path,
    component_id: str,
    skill_id: str,
    seeds: tuple[int, ...],
) -> dict[str, Any]:
    """Compile / import / smoke / integrity / checker for one on-disk tree."""
    result: dict[str, Any] = {
        "label": label,
        "compile_passed": False,
        "import_passed": False,
        "smoke_passed": False,
        "integrity_passed": False,
        "checker_passed": False,
        "payload_schema_passed": False,
        "blockers": [],
        "sample_problem_type_id": None,
    }
    required = {
        "generate.py": generate_py,
        "metadata.py": metadata_py,
        "get_hint.py": hint_py,
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        result["blockers"].append(f"missing_files:{','.join(missing)}")
        return result

    try:
        for path in required.values():
            py_compile.compile(str(path), doraise=True)
        result["compile_passed"] = True

        suffix = uuid.uuid4().hex
        gen_mod = _load_module(generate_py, f"recon_gen_{component_id}_{suffix}")
        meta_mod = _load_module(metadata_py, f"recon_meta_{component_id}_{suffix}")
        hint_mod = _load_module(hint_py, f"recon_hint_{component_id}_{suffix}")
        generate_fn = getattr(gen_mod, "generate", None)
        hint_fn = getattr(hint_mod, "get_hint", None)
        if not callable(generate_fn) or not callable(hint_fn):
            result["blockers"].append("missing_generate_or_hint_function")
            return result
        result["import_passed"] = True
        result["metadata_attrs"] = {
            attr.lower(): getattr(meta_mod, attr)
            for attr in dir(meta_mod)
            if attr.isupper() and not attr.startswith("_")
        }

        payload = generate_fn(seed=seeds[0], component_id=component_id)
        if not isinstance(payload, dict) or not payload:
            result["blockers"].append("generate_must_return_nonempty_dict")
            return result
        hint_fn(1, payload)
        result["smoke_passed"] = True
        result["sample_problem_type_id"] = payload.get("problem_type_id")
        result["sample_answer_type"] = payload.get("answer_type")
        result["payload_schema_passed"] = True

        for seed in seeds:
            sample = generate_fn(seed=seed, component_id=component_id)
            if not isinstance(sample, dict):
                result["blockers"].append(f"integrity_generate_not_dict:seed={seed}")
                return result
            validation = validate_component_payload(sample, component_id=component_id)
            if not validation.get("passed", True):
                blockers = validation.get("blockers") or ["integrity_validation_failed"]
                result["blockers"].extend(f"integrity:{b}" for b in blockers)
                return result
        result["integrity_passed"] = True

        checker_errors = _checker_correct_and_wrong(payload, skill_id=skill_id)
        if checker_errors:
            result["blockers"].extend(checker_errors)
            return result
        result["checker_passed"] = True
        return result
    except Exception as exc:
        result["blockers"].append(f"{exc.__class__.__name__}:{exc}")
        return result


def _is_drawing_payload(payload: dict[str, Any]) -> bool:
    answer_type = str(payload.get("answer_type") or "").strip().lower()
    presentation = str(payload.get("presentation_mode") or "").strip().lower()
    contract = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    checker_key = str(
        payload.get("checker_key")
        or contract.get("checker_key")
        or contract.get("checker")
        or ""
    ).strip().lower()
    if answer_type in {"drawing", "chart_drawing", "graph_drawing", "canvas_drawing"}:
        return True
    if presentation in {"canvas", "drawing"}:
        return True
    if checker_key in {"free_response_drawing_checker", "drawing_checker"}:
        return True
    return False


def _drawing_spec_contract_errors(payload: dict[str, Any]) -> list[str]:
    """Validate drawing payloads without feeding drawing_spec into image checkers."""
    errors: list[str] = []
    correct = payload.get("correct_answer", payload.get("answer"))
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    if correct is None:
        correct = meta.get("drawing_spec") or meta.get("expected_drawing_spec")
    if not isinstance(correct, dict) or not correct:
        errors.append("drawing_missing_spec")
        return errors
    # Minimal structural contract: must declare a drawable kind / geometry cue.
    kind = str(correct.get("kind") or correct.get("type") or "").strip()
    has_geometry = any(
        key in correct
        for key in ("points", "lines", "segments", "curves", "strokes", "equation", "y_intercept", "slope")
    )
    if not kind and not has_geometry:
        errors.append("drawing_spec_incomplete")
    return errors


def _checker_correct_and_wrong(payload: dict[str, Any], *, skill_id: str) -> list[str]:
    """Exercise official check_answer with correct + deliberately wrong answers."""
    if _is_drawing_payload(payload):
        return _drawing_spec_contract_errors(payload)

    errors: list[str] = []
    correct = payload.get("correct_answer", payload.get("answer"))
    if correct is None or (isinstance(correct, str) and not correct.strip()):
        # Some absolute-value payloads put the semantic answer only in metadata.
        meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        correct = meta.get("semantic_answer") or payload.get("semantic_answer")
    if correct is None or (isinstance(correct, str) and not str(correct).strip()):
        errors.append("checker_missing_correct_answer")
        return errors

    try:
        ok = check_answer(correct, correct, payload=payload, skill_id=skill_id)
    except Exception as exc:
        errors.append(f"checker_correct_exception:{exc.__class__.__name__}:{exc}")
        return errors
    if not ok:
        # Fallback: string form of correct answer for multi-value sets.
        try:
            ok = check_answer(str(correct), correct, payload=payload, skill_id=skill_id)
        except Exception as exc:
            errors.append(f"checker_correct_str_exception:{exc.__class__.__name__}:{exc}")
            return errors
    if not ok:
        errors.append("checker_correct_rejected")

    wrong_candidates = ("__recon_wrong__", "999999", "不可能的答案")
    false_positive = False
    for wrong in wrong_candidates:
        try:
            if check_answer(wrong, correct, payload=payload, skill_id=skill_id):
                false_positive = True
                break
        except Exception:
            # Wrong-answer exceptions are acceptable for strict checkers.
            continue
    if false_positive:
        errors.append("checker_wrong_accepted")
    return errors


def _fetch_tracker_row(
    conn: sqlite3.Connection,
    textbook_example_id: int,
) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT id, textbook_example_id, skill_id, component_id, gencode_status,
               induced_spec_payload, gencode_error_log, created_at, updated_at
        FROM gencode_component_tracker
        WHERE textbook_example_id = ?
        """,
        (textbook_example_id,),
    ).fetchone()
    if row is None:
        return None
    keys = (
        "id",
        "textbook_example_id",
        "skill_id",
        "component_id",
        "gencode_status",
        "induced_spec_payload",
        "gencode_error_log",
        "created_at",
        "updated_at",
    )
    if hasattr(row, "keys"):
        return {key: row[key] for key in keys}
    return dict(zip(keys, row, strict=True))


def validate_existing_component(
    *,
    conn: sqlite3.Connection,
    skill_id: str,
    textbook_example_id: int,
    project_root: str | Path | None = None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
    seeds: tuple[int, ...] | None = None,
) -> dict[str, Any]:
    """Validate one existing component without writing DB or files."""
    skill_key = str(skill_id or "").strip()
    if not skill_key:
        raise ValueError("missing_skill_id")
    if not isinstance(textbook_example_id, int) or isinstance(textbook_example_id, bool):
        raise ValueError("invalid_textbook_example_id")

    assert_textbook_example_skill(
        conn,
        textbook_example_id=textbook_example_id,
        skill_id=skill_key,
    )

    root = Path(project_root) if project_root is not None else PROJECT_ROOT
    component_id = derive_component_id(textbook_example_id)
    paths = _component_paths(
        project_root=root,
        skill_id=skill_key,
        component_id=component_id,
        dryrun_base_dir=dryrun_base_dir,
        production_base_dir=production_base_dir,
    )
    integrity_seeds = seeds or DEFAULT_INTEGRITY_SEEDS

    dryrun_hash_before = _sha256_file(paths["dryrun_generate"])
    prod_hash_before = _sha256_file(paths["production_generate"])
    tracker_before = _fetch_tracker_row(conn, textbook_example_id)

    report: dict[str, Any] = {
        "skill_id": skill_key,
        "textbook_example_id": textbook_example_id,
        "component_id": component_id,
        "tracker_before": {
            "exists": tracker_before is not None,
            "gencode_status": (tracker_before or {}).get("gencode_status"),
            "updated_at": (tracker_before or {}).get("updated_at"),
        },
        "dryrun_hash_before": dryrun_hash_before,
        "production_hash_before": prod_hash_before,
        "hash_consistent_before": bool(
            dryrun_hash_before and prod_hash_before and dryrun_hash_before == prod_hash_before
        ),
        "passed": False,
        "blockers": [],
        "dryrun_validation": None,
        "production_validation": None,
        "dryrun_hash_after": None,
        "production_hash_after": None,
        "hashes_unchanged": False,
        "production_file_changed": None,
    }

    if not dryrun_hash_before:
        report["blockers"].append("dryrun_generate_missing")
    if not prod_hash_before:
        report["blockers"].append("production_generate_missing")
    if dryrun_hash_before and prod_hash_before and dryrun_hash_before != prod_hash_before:
        report["blockers"].append("dryrun_production_hash_mismatch")

    if report["blockers"]:
        report["dryrun_hash_after"] = _sha256_file(paths["dryrun_generate"])
        report["production_hash_after"] = _sha256_file(paths["production_generate"])
        report["hashes_unchanged"] = (
            report["dryrun_hash_after"] == dryrun_hash_before
            and report["production_hash_after"] == prod_hash_before
        )
        report["production_file_changed"] = not (
            report["production_hash_after"] == prod_hash_before
        )
        return report

    dryrun_validation = _validate_tree(
        label="dryrun",
        generate_py=paths["dryrun_generate"],
        metadata_py=paths["dryrun_metadata"],
        hint_py=paths["dryrun_hint"],
        component_id=component_id,
        skill_id=skill_key,
        seeds=integrity_seeds,
    )
    production_validation = _validate_tree(
        label="production",
        generate_py=paths["production_generate"],
        metadata_py=paths["production_metadata"],
        hint_py=paths["production_hint"],
        component_id=component_id,
        skill_id=skill_key,
        seeds=integrity_seeds,
    )
    report["dryrun_validation"] = dryrun_validation
    report["production_validation"] = production_validation
    report["blockers"].extend(
        f"dryrun:{b}" for b in (dryrun_validation.get("blockers") or [])
    )
    report["blockers"].extend(
        f"production:{b}" for b in (production_validation.get("blockers") or [])
    )

    report["dryrun_hash_after"] = _sha256_file(paths["dryrun_generate"])
    report["production_hash_after"] = _sha256_file(paths["production_generate"])
    report["hashes_unchanged"] = (
        report["dryrun_hash_after"] == dryrun_hash_before
        and report["production_hash_after"] == prod_hash_before
    )
    report["production_file_changed"] = report["production_hash_after"] != prod_hash_before
    if not report["hashes_unchanged"]:
        report["blockers"].append("artifact_hash_changed_during_validation")

    report["passed"] = len(report["blockers"]) == 0
    return report


def _build_verified_payload(
    *,
    existing_payload: dict[str, Any],
    validation_report: dict[str, Any],
    project_root: Path,
    dryrun_generate: Path,
    production_generate: Path,
    run_id: str,
) -> dict[str, Any]:
    payload = dict(existing_payload)
    dry_meta = ((validation_report.get("dryrun_validation") or {}).get("metadata_attrs") or {})
    for key, value in dry_meta.items():
        if value is not None and key not in payload:
            payload[key] = value

    current_hash = validation_report["dryrun_hash_after"]
    payload["integrity_gate_passed"] = True
    payload["integrity_gate_blockers"] = []
    payload["integrity_gate_version"] = "v1"
    payload["compile_passed"] = True
    payload["smoke_passed"] = True
    payload["validation_passed"] = True
    payload["verified_generate_sha256"] = current_hash
    payload["verified_artifact_path"] = _relative_path(dryrun_generate, project_root)
    payload["published_generate_sha256"] = validation_report["production_hash_after"]
    payload["published_component_path"] = _relative_path(production_generate, project_root)
    payload["published_component_id"] = validation_report["component_id"]
    payload["published_textbook_example_id"] = validation_report["textbook_example_id"]
    payload["published_at"] = _now_iso()
    payload["reconciliation"] = {
        "mode": "validate_existing_artifacts",
        "run_id": run_id,
        "reconciled_at": _now_iso(),
        "dryrun_sha256": current_hash,
        "production_sha256": validation_report["production_hash_after"],
        "hashes_unchanged": True,
        "regenerate": False,
    }
    payload["component_id"] = validation_report["component_id"]
    payload["skill_id"] = validation_report["skill_id"]
    payload["textbook_example_id"] = validation_report["textbook_example_id"]
    return payload


def apply_tracker_sync_for_passed_component(
    *,
    conn: sqlite3.Connection,
    validation_report: dict[str, Any],
    project_root: str | Path | None = None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
    run_id: str | None = None,
) -> dict[str, Any]:
    """Write verified tracker only when validation_report.passed is True."""
    if not validation_report.get("passed"):
        raise ValueError("cannot_sync_failed_validation")
    if not validation_report.get("hashes_unchanged"):
        raise ValueError("cannot_sync_when_hashes_changed")

    skill_key = str(validation_report["skill_id"])
    textbook_example_id = int(validation_report["textbook_example_id"])
    component_id = str(validation_report["component_id"])
    root = Path(project_root) if project_root is not None else PROJECT_ROOT
    paths = _component_paths(
        project_root=root,
        skill_id=skill_key,
        component_id=component_id,
        dryrun_base_dir=dryrun_base_dir,
        production_base_dir=production_base_dir,
    )

    # Re-check hashes immediately before write.
    dry_now = _sha256_file(paths["dryrun_generate"])
    prod_now = _sha256_file(paths["production_generate"])
    if dry_now != validation_report.get("dryrun_hash_before") or prod_now != validation_report.get(
        "production_hash_before"
    ):
        raise ValueError("pre_write_hash_drift")

    existing = _fetch_tracker_row(conn, textbook_example_id)
    existing_payload = _parse_payload((existing or {}).get("induced_spec_payload"))
    payload = _build_verified_payload(
        existing_payload=existing_payload,
        validation_report={
            **validation_report,
            "dryrun_hash_after": dry_now,
            "production_hash_after": prod_now,
        },
        project_root=root,
        dryrun_generate=paths["dryrun_generate"],
        production_generate=paths["production_generate"],
        run_id=run_id or uuid.uuid4().hex,
    )

    saved = save_tracker_record(
        conn,
        textbook_example_id=textbook_example_id,
        skill_id=skill_key,
        gencode_status="verified",
        induced_spec_payload=payload,
        gencode_error_log=None,
    )

    dry_after = _sha256_file(paths["dryrun_generate"])
    prod_after = _sha256_file(paths["production_generate"])
    return {
        "tracker_after": {
            "exists": True,
            "gencode_status": saved.get("gencode_status"),
            "updated_at": saved.get("updated_at"),
            "component_id": saved.get("component_id"),
        },
        "dryrun_hash_after_write": dry_after,
        "production_hash_after_write": prod_after,
        "production_file_changed": prod_after != validation_report.get("production_hash_before"),
        "hashes_unchanged_after_write": (
            dry_after == validation_report.get("dryrun_hash_before")
            and prod_after == validation_report.get("production_hash_before")
        ),
    }


def reconcile_existing_artifacts(
    *,
    conn: sqlite3.Connection,
    targets: dict[str, tuple[int, ...] | list[int]] | None = None,
    project_root: str | Path | None = None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
    commit: bool = False,
    seeds: tuple[int, ...] | None = None,
) -> dict[str, Any]:
    """Validate whitelisted existing components; optionally sync tracker.

    ``commit=False`` (default): report-only, no DB writes.
    ``commit=True``: write verified tracker only for individually passed items.
    Failures never write verified and never mutate generate.py.
    """
    root = Path(project_root) if project_root is not None else PROJECT_ROOT
    selected = targets or DEFAULT_RECONCILE_TARGETS
    run_id = uuid.uuid4().hex
    components: list[dict[str, Any]] = []

    for skill_id, source_ids in selected.items():
        for textbook_example_id in source_ids:
            item = validate_existing_component(
                conn=conn,
                skill_id=str(skill_id),
                textbook_example_id=int(textbook_example_id),
                project_root=root,
                dryrun_base_dir=dryrun_base_dir,
                production_base_dir=production_base_dir,
                seeds=seeds,
            )
            item["run_id"] = run_id
            item["commit_requested"] = bool(commit)
            item["tracker_synced"] = False
            item["tracker_after"] = None

            if commit and item.get("passed"):
                sync_result = apply_tracker_sync_for_passed_component(
                    conn=conn,
                    validation_report=item,
                    project_root=root,
                    dryrun_base_dir=dryrun_base_dir,
                    production_base_dir=production_base_dir,
                    run_id=run_id,
                )
                item["tracker_synced"] = True
                item["tracker_after"] = sync_result.get("tracker_after")
                item["dryrun_hash_after"] = sync_result.get("dryrun_hash_after_write")
                item["production_hash_after"] = sync_result.get("production_hash_after_write")
                item["hashes_unchanged"] = sync_result.get("hashes_unchanged_after_write")
                item["production_file_changed"] = sync_result.get("production_file_changed")
            elif commit and not item.get("passed"):
                # Explicitly do not touch tracker on failure (preserve verified rows).
                item["tracker_after"] = item.get("tracker_before")

            components.append(item)

    passed_count = sum(1 for row in components if row.get("passed"))
    synced_count = sum(1 for row in components if row.get("tracker_synced"))
    return {
        "run_id": run_id,
        "commit": bool(commit),
        "project_root": str(root),
        "started_at": _now_iso(),
        "total": len(components),
        "passed_count": passed_count,
        "failed_count": len(components) - passed_count,
        "synced_count": synced_count,
        "all_passed": passed_count == len(components) and len(components) > 0,
        "all_hashes_unchanged": all(bool(row.get("hashes_unchanged")) for row in components),
        "components": components,
    }
