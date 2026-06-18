"""Admin-only V3 dry-run action service."""

from __future__ import annotations

import importlib.util
import py_compile
import sqlite3
from pathlib import Path
from typing import Any

from core.gencode.pipeline_orchestrator import (
    V3_PRODUCTION_PUBLISH_ENABLED,
    _load_v3_taxonomy_mvp_scope,
    run_gencode_phase2_raw,
)
from core.gencode.schema.gencode_component_tracker_inspection import (
    ensure_gencode_component_tracker_table,
)
from core.gencode.services.component_tracker_service import (
    assert_textbook_example_skill,
    derive_component_id,
    save_tracker_record,
    update_status,
)
from core.gencode.services.v3_skill_coverage_service import (
    build_coverage_warnings,
    get_v3_skill_component_coverage,
)


def _fetch_textbook_example_ids_for_skill(
    conn: sqlite3.Connection,
    skill_id: str,
) -> list[int]:
    rows = conn.execute(
        """
        SELECT id
        FROM textbook_examples
        WHERE skill_id = ?
        ORDER BY id ASC
        """,
        (str(skill_id or "").strip(),),
    ).fetchall()
    return [int(row[0] if not hasattr(row, "keys") else row["id"]) for row in rows]


_UNSUPPORTED_ERROR_CODES = frozenset(
    {
        "unsupported_task_type",
        "unsupported_domain",
        "unsupported_checker",
        "unsupported_answer_contract",
        "unsupported_choices_generator",
        "presentation_inference_failed",
    }
)


def _assert_admin_v3_dryrun_skill_allowed(skill_id: str) -> None:
    """Allow admin batch dryrun for any concrete skill; keep outline rows inert."""
    skill_key = str(skill_id or "").strip()
    if not skill_key:
        raise ValueError("missing_skill_id")
    if skill_key.startswith("outline_"):
        raise ValueError("outline_skill_not_supported_for_v3_dryrun")


def _classify_dryrun_error(exc: Exception) -> str:
    message = f"{exc.__class__.__name__}:{exc}"
    lowered = message.lower()
    if "unsupported_task_type" in lowered:
        return "unsupported_task_type"
    if "unsupported_domain" in lowered:
        return "unsupported_domain"
    if "unsupported_checker" in lowered:
        return "unsupported_checker"
    if "unsupported_answer_contract" in lowered:
        return "unsupported_answer_contract"
    if "unsupported_choices_generator" in lowered:
        return "unsupported_choices_generator"
    if "presentation" in lowered and ("infer" in lowered or "inference" in lowered):
        return "presentation_inference_failed"
    if "choice" in lowered:
        return "unsupported_choices_generator"
    if "answer_contract" in lowered or "answer contract" in lowered:
        return "unsupported_answer_contract"
    if "checker" in lowered or "check_answer" in lowered:
        return "unsupported_checker"
    if "domain" in lowered or "adapter" in lowered:
        return "unsupported_domain"
    if "v3_shadow_bridge_not_executed" in lowered or "shadow_bridge" in lowered:
        return "unsupported_task_type"
    if "task_type" in lowered or "problem_type" in lowered or "unsupported" in lowered:
        return "unsupported_task_type"
    return "failed"


def _record_failed_example(
    conn: sqlite3.Connection,
    *,
    textbook_example_id: int,
    skill_id: str,
    error_code: str,
    exc: Exception,
) -> None:
    error_log = f"{error_code}: {exc.__class__.__name__}: {exc}"
    try:
        save_tracker_record(
            conn,
            textbook_example_id=textbook_example_id,
            skill_id=skill_id,
            gencode_status="failed",
            induced_spec_payload={"error_code": error_code},
            gencode_error_log=error_log,
        )
    except Exception:
        # Preserve the batch response even if an existing inconsistent row blocks the upsert.
        pass


def run_admin_v3_dryrun_for_skill(
    conn: sqlite3.Connection,
    skill_id: str,
    *,
    smoke: bool = False,
    verify: bool = False,
    force: bool = False,
    limit: int | None = None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    seed: int | None = None,
) -> dict[str, object]:
    """Run V3 dryrun for all textbook examples under one skill."""
    ensure_gencode_component_tracker_table(conn)

    skill_key = str(skill_id or "").strip()
    if not skill_key:
        raise ValueError("missing_skill_id")
    _assert_admin_v3_dryrun_skill_allowed(skill_key)

    example_ids = _fetch_textbook_example_ids_for_skill(conn, skill_key)
    if limit is not None:
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            raise ValueError("invalid_limit")
        example_ids = example_ids[:limit]

    results: list[dict[str, object]] = []
    processed_count = 0
    skipped_verified_count = 0
    success_count = 0
    failed_count = 0
    unsupported_count = 0

    for textbook_example_id in example_ids:
        component_id = derive_component_id(textbook_example_id)
        tracker = _fetch_tracker_for_example(conn, textbook_example_id)
        tracker_status = str((tracker or {}).get("gencode_status") or "").strip()

        if tracker_status == "verified" and not force:
            skipped_verified_count += 1
            results.append(
                {
                    "textbook_example_id": textbook_example_id,
                    "status": "skipped_verified",
                    "component_id": component_id,
                    "message": "verified tracker row kept",
                }
            )
            continue

        processed_count += 1
        try:
            dryrun_result = run_admin_v3_dryrun_for_example(
                conn=conn,
                textbook_example_id=textbook_example_id,
                skill_id=skill_key,
                dryrun_base_dir=dryrun_base_dir,
                seed=seed,
                allow_non_mvp_skill=True,
            )
            entry_status = "processed"
            message = str(dryrun_result.get("status") or "draft_written")

            if smoke:
                smoke_result = run_admin_v3_smoke_for_example(
                    conn=conn,
                    textbook_example_id=textbook_example_id,
                    skill_id=skill_key,
                    dryrun_base_dir=dryrun_base_dir,
                    seed=seed if seed is not None else 42,
                )
                message = str(smoke_result.get("status") or "smoke_passed")
                if verify:
                    verify_result = mark_admin_v3_example_verified(
                        conn=conn,
                        textbook_example_id=textbook_example_id,
                        skill_id=skill_key,
                    )
                    message = str(verify_result.get("status") or "verified")

            success_count += 1
            results.append(
                {
                    "textbook_example_id": textbook_example_id,
                    "status": entry_status,
                    "component_id": str(dryrun_result.get("component_id") or component_id),
                    "message": message,
                }
            )
        except Exception as exc:
            error_code = _classify_dryrun_error(exc)
            if error_code in _UNSUPPORTED_ERROR_CODES:
                unsupported_count += 1
            _record_failed_example(
                conn,
                textbook_example_id=textbook_example_id,
                skill_id=skill_key,
                error_code=error_code,
                exc=exc,
            )
            failed_count += 1
            results.append(
                {
                    "textbook_example_id": textbook_example_id,
                    "status": "failed",
                    "component_id": component_id,
                    "error_code": error_code,
                    "message": f"{exc.__class__.__name__}:{exc}",
                }
            )

    coverage = get_v3_skill_component_coverage(conn, skill_key)
    verified_count = int(coverage.get("verified_count") or 0)
    missing_tracker_count = int(coverage.get("missing_tracker_count") or 0)

    variation_report = {}
    if failed_count == 0 and verified_count > 0:
        from core.gencode.services.v3_variation_audit_service import audit_skill_variation
        try:
            variation_report = audit_skill_variation(
                skill_id=skill_key,
                source="dryrun",
                conn=conn,
            )
        except Exception:
            pass

    return {
        "success": failed_count == 0,
        "skill_id": skill_key,
        "total_examples": len(example_ids),
        "processed_count": processed_count,
        "skipped_verified_count": skipped_verified_count,
        "success_count": success_count,
        "failed_count": failed_count,
        "unsupported_count": unsupported_count,
        "verified_count": verified_count,
        "missing_tracker_count": missing_tracker_count,
        "publish_ready": bool(coverage.get("publish_ready")),
        "results": results,
        "per_example_results": results,
        "coverage": coverage,
        "variation_checked": bool(variation_report),
        "dynamic_count": variation_report.get("dynamic_count", 0),
        "static_count": variation_report.get("static_count", 0),
        "partially_dynamic_count": variation_report.get("partially_dynamic_count", 0),
        "insufficient_sample_count": variation_report.get("insufficient_sample_count", 0),
        "variation_status_by_component": variation_report.get("variation_status_by_component", {}),
    }


def run_admin_v3_dryrun_for_example(
    *,
    conn: sqlite3.Connection,
    textbook_example_id: int,
    skill_id: str,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    seed: int | None = None,
    allow_non_mvp_skill: bool = False,
) -> dict[str, object]:
    """Run one admin-triggered V3 shadow-bridge dryrun for a textbook example."""
    ensure_gencode_component_tracker_table(conn)

    skill_key = str(skill_id or "").strip()
    if not skill_key:
        raise ValueError("missing_skill_id")
    _assert_admin_v3_dryrun_skill_allowed(skill_key)
    if not isinstance(textbook_example_id, int) or isinstance(textbook_example_id, bool):
        raise ValueError("invalid_textbook_example_id")

    # Administrative ownership guard: textbook example must belong to this skill.
    assert_textbook_example_skill(
        conn,
        textbook_example_id=textbook_example_id,
        skill_id=skill_key,
    )

    if not allow_non_mvp_skill:
        mvp_scope = _load_v3_taxonomy_mvp_scope("configs/gencode_taxonomy/k12_component_taxonomy.yaml")
        if skill_key not in mvp_scope:
            raise ValueError("skill_not_in_v3_mvp_scope")

    # Hard safety lock: admin dryrun must never run with publish flag enabled.
    if bool(V3_PRODUCTION_PUBLISH_ENABLED):
        raise ValueError("unsafe_production_publish_flag_enabled")

    phase2_kwargs: dict[str, Any] = {
        "dry_run": True,
        "v3_textbook_example_id": textbook_example_id,
        "v3_conn": conn,
        "v3_dryrun_base_dir": dryrun_base_dir,
    }
    if seed is not None:
        phase2_kwargs["seed"] = seed
    try:
        phase2_result = run_gencode_phase2_raw(
            skill_key,
            **phase2_kwargs,
        )
    except TypeError:
        # Backward-compatible path when run_gencode_phase2_raw has no seed parameter.
        phase2_kwargs.pop("seed", None)
        phase2_result = run_gencode_phase2_raw(
            skill_key,
            **phase2_kwargs,
        )
    if str(phase2_result.get("phase_status", "")).strip() != "V3_SHADOW_BRIDGE":
        raise ValueError("v3_shadow_bridge_not_executed")
    if str(phase2_result.get("tracker_status", "")).strip() != "draft_written":
        raise ValueError("v3_shadow_bridge_not_executed")

    component_id = derive_component_id(textbook_example_id)
    dryrun_root = Path(str(dryrun_base_dir or "").strip())
    if not dryrun_root.is_absolute():
        dryrun_root = Path(__file__).resolve().parents[3] / dryrun_root
    component_dir = dryrun_root / skill_key / "components" / component_id

    return {
        "status": "draft_written",
        "skill_id": skill_key,
        "textbook_example_id": textbook_example_id,
        "component_id": component_id,
        "dryrun_component_dir": str(component_dir.resolve()),
    }


def _fetch_tracker_for_example(
    conn: sqlite3.Connection,
    textbook_example_id: int,
) -> dict[str, object] | None:
    row = conn.execute(
        """
        SELECT textbook_example_id, skill_id, component_id, gencode_status, gencode_error_log, updated_at
        FROM gencode_component_tracker
        WHERE textbook_example_id = ?
        """,
        (textbook_example_id,),
    ).fetchone()
    if row is None:
        return None
    if hasattr(row, "keys"):
        return {
            "textbook_example_id": row["textbook_example_id"],
            "skill_id": row["skill_id"],
            "component_id": row["component_id"],
            "gencode_status": row["gencode_status"],
            "gencode_error_log": row["gencode_error_log"],
            "updated_at": row["updated_at"],
        }
    return {
        "textbook_example_id": row[0],
        "skill_id": row[1],
        "component_id": row[2],
        "gencode_status": row[3],
        "gencode_error_log": row[4],
        "updated_at": row[5],
    }


def _load_module_from_file(file_path: Path):
    module_name = f"admin_v3_smoke_{file_path.stem}_{abs(hash(str(file_path)))}"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module_load_failed:{file_path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_admin_v3_smoke_for_example(
    *,
    conn,
    textbook_example_id: int,
    skill_id: str,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    seed: int | None = 42,
) -> dict[str, object]:
    """Run smoke test against one dryrun component and advance tracker status."""
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

    tracker = _fetch_tracker_for_example(conn, textbook_example_id)
    if tracker is None:
        raise ValueError("invalid_status_for_smoke")
    status = str(tracker.get("gencode_status", "")).strip()
    if status not in {"draft_written", "failed"}:
        raise ValueError("invalid_status_for_smoke")

    component_id = str(tracker.get("component_id") or "").strip()
    if not component_id:
        raise ValueError("missing_component_id")

    dryrun_root = Path(str(dryrun_base_dir or "").strip())
    if not dryrun_root.is_absolute():
        dryrun_root = Path(__file__).resolve().parents[3] / dryrun_root
    component_dir = dryrun_root / skill_key / "components" / component_id

    required_files = {
        "metadata.py": component_dir / "metadata.py",
        "generate.py": component_dir / "generate.py",
        "get_hint.py": component_dir / "get_hint.py",
    }
    missing_files = [name for name, path in required_files.items() if not path.is_file()]
    if missing_files:
        update_status(
            conn,
            textbook_example_id=textbook_example_id,
            skill_id=skill_key,
            gencode_status="failed",
            gencode_error_log=f"missing_files:{','.join(missing_files)}",
        )
        raise ValueError("dryrun_component_missing_files")

    try:
        for target_path in required_files.values():
            py_compile.compile(str(target_path), doraise=True)

        generate_module = _load_module_from_file(required_files["generate.py"])
        hint_module = _load_module_from_file(required_files["get_hint.py"])

        generate_fn = getattr(generate_module, "generate", None)
        if not callable(generate_fn):
            raise RuntimeError("missing_generate_function")
        payload = generate_fn(seed=seed)
        if not isinstance(payload, dict):
            payload = {}

        hint_fn = getattr(hint_module, "get_hint", None)
        if not callable(hint_fn):
            raise RuntimeError("missing_get_hint_function")
        hint_fn(1, payload)
    except Exception as exc:
        update_status(
            conn,
            textbook_example_id=textbook_example_id,
            skill_id=skill_key,
            gencode_status="failed",
            gencode_error_log=f"{exc.__class__.__name__}:{exc}",
        )
        raise ValueError("dryrun_smoke_failed") from exc

    updated = update_status(
        conn,
        textbook_example_id=textbook_example_id,
        skill_id=skill_key,
        gencode_status="smoke_passed",
        gencode_error_log=None,
    )
    return {
        "status": "smoke_passed",
        "skill_id": skill_key,
        "textbook_example_id": textbook_example_id,
        "component_id": component_id,
        "tracker_updated_at": updated.get("updated_at"),
    }


def mark_admin_v3_example_verified(
    *,
    conn,
    textbook_example_id: int,
    skill_id: str,
) -> dict[str, object]:
    """Advance tracker status from smoke_passed to verified."""
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
    tracker = _fetch_tracker_for_example(conn, textbook_example_id)
    if tracker is None:
        raise ValueError("tracker_record_not_found")

    status = str(tracker.get("gencode_status") or "").strip()
    if status != "smoke_passed":
        raise ValueError("invalid_status_for_verify")

    component_id = str(tracker.get("component_id") or "").strip()
    if not component_id:
        raise ValueError("missing_component_id")

    updated = update_status(
        conn,
        textbook_example_id=textbook_example_id,
        skill_id=skill_key,
        gencode_status="verified",
        gencode_error_log=None,
    )
    return {
        "status": "verified",
        "skill_id": skill_key,
        "textbook_example_id": textbook_example_id,
        "component_id": component_id,
        "tracker_updated_at": updated.get("updated_at"),
    }


def _count_verified_components_for_skill(conn: sqlite3.Connection, skill_id: str) -> int:
    row = conn.execute(
        """
        SELECT COUNT(*) AS verified_count
        FROM gencode_component_tracker
        WHERE skill_id = ? AND gencode_status = 'verified'
        """,
        (str(skill_id or "").strip(),),
    ).fetchone()
    if row is None:
        return 0
    if hasattr(row, "keys"):
        return int(row["verified_count"])
    return int(row[0])


def run_admin_v3_publish_for_skill(
    *,
    conn,
    skill_id: str,
    project_root: str,
    staging_root: str,
    force_publish: bool = False,
    strict_coverage: bool = False,
) -> dict[str, object]:
    """Publish one admin-gated V3 skill through the production publish service."""
    if force_publish is not True:
        raise ValueError("production_publish_requires_force_publish")

    ensure_gencode_component_tracker_table(conn)

    from core.gencode.v3_production_publish_service import V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS

    skill_key = str(skill_id or "").strip()
    if skill_key not in V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS:
        raise ValueError("production_publish_not_allowed_for_skill")

    coverage = get_v3_skill_component_coverage(conn, skill_key)
    warnings = build_coverage_warnings(coverage)

    if strict_coverage and not bool(coverage.get("publish_ready")):
        raise ValueError("v3_coverage_incomplete_for_strict_publish")

    verified_component_count = _count_verified_components_for_skill(conn, skill_key)
    if verified_component_count < 1:
        raise ValueError("no_verified_components")

    from core.gencode.v3_production_publish_service import publish_single_v3_skill_to_production

    publish_result = publish_single_v3_skill_to_production(
        conn=conn,
        skill_id=skill_key,
        project_root=project_root,
        staging_root=staging_root,
    )
    status = str(publish_result.get("status", "")).strip()
    component_count = publish_result.get("component_count", 0)

    return {
        "status": status,
        "skill_id": skill_key,
        "verified_component_count": verified_component_count,
        "component_count": component_count,
        "coverage": coverage,
        "warnings": warnings,
        "project_root": publish_result.get("project_root"),
        "staging_root": publish_result.get("staging_root"),
        "smoke_status": publish_result.get("smoke_status"),
        "staging_smoke_status": publish_result.get("staging_smoke_status"),
        "production_smoke_status": publish_result.get("production_smoke_status"),
        "compile": publish_result.get("compile"),
        "promote": publish_result.get("promote"),
        "rollback": publish_result.get("rollback"),
        "production_smoke_error": publish_result.get("production_smoke_error"),
        "timestamp": publish_result.get("timestamp"),
        "publish": publish_result,
    }
