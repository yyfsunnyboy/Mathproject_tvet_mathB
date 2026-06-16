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
from core.gencode.services.component_tracker_service import (
    assert_textbook_example_skill,
    derive_component_id,
    update_status,
)


def run_admin_v3_dryrun_for_example(
    *,
    conn: sqlite3.Connection,
    textbook_example_id: int,
    skill_id: str,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    seed: int | None = None,
) -> dict[str, object]:
    """Run one admin-triggered V3 shadow-bridge dryrun for a textbook example."""
    skill_key = str(skill_id or "").strip()
    if not skill_key:
        raise ValueError("missing_skill_id")
    if not isinstance(textbook_example_id, int) or isinstance(textbook_example_id, bool):
        raise ValueError("invalid_textbook_example_id")

    # Administrative ownership guard: textbook example must belong to this skill.
    assert_textbook_example_skill(
        conn,
        textbook_example_id=textbook_example_id,
        skill_id=skill_key,
    )

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
