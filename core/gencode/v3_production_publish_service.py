"""Production publish lifecycle for a single gated V3 skill."""

from __future__ import annotations

import importlib.util
import os
import py_compile
import shutil
import sqlite3
import sys
import uuid
from pathlib import Path
from typing import Any

from core.gencode.pipeline_state import utc_timestamp
from core.gencode.skill_wrapper_compiler import (
    _fetch_verified_components,
    _is_path_under,
    assert_safe_project_root,
    compile_and_double_write_skill,
    rollback_v3_to_v2_facade,
)

V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS: frozenset[str] = frozenset({
    "vh_數學B1_PointSlopeForm",
    "vh_數學B1_HorizontalAndVerticalLineEquations",
    "vh_數學B1_SlopeInterceptForm",
    "vh_數學B1_InterceptForm",
})

V3_VARIATION_REQUIRED_SKILLS: frozenset[str] = frozenset()

# Backward-compatible alias for existing test imports
ALLOWED_PRODUCTION_SKILL_ID = "vh_數學B1_PointSlopeForm"


def assert_safe_staging_root(staging_root: str, project_root: Path) -> Path:
    """Validate an isolated staging root for compile and smoke."""
    if not str(staging_root or "").strip():
        raise ValueError("unsafe_staging_root")

    staging_path = Path(os.path.abspath(os.path.normpath(staging_root)))
    project_path = Path(os.path.abspath(os.path.normpath(str(project_root))))
    if staging_path == project_path:
        raise ValueError("unsafe_staging_root")

    for blocked_parent in (project_path / "skills", project_path / "agent_skills_v3"):
        if _is_path_under(staging_path, blocked_parent):
            raise ValueError("unsafe_staging_root")

    return staging_path


def _sync_dryrun_components_to_v3_house(staging_path: Path, skill_id: str) -> None:
    dryrun_components = staging_path / skill_id / "components"
    v3_components = staging_path / "agent_skills_v3" / skill_id / "components"
    if not dryrun_components.exists():
        return
    v3_components.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(dryrun_components, v3_components, dirs_exist_ok=True)


def _backup_facade_before_overwrite(facade_path: Path) -> bool:
    backup_path = facade_path.with_suffix(f"{facade_path.suffix}.bak")
    if facade_path.exists() and not backup_path.exists():
        backup_path.write_text(facade_path.read_text(encoding="utf-8"), encoding="utf-8")
        return True
    return False


def _promote_staging_to_production(
    staging_path: Path,
    project_path: Path,
    skill_id: str,
) -> dict[str, object]:
    staging_facade = staging_path / "skills" / f"{skill_id}.py"
    production_facade = project_path / "skills" / f"{skill_id}.py"
    if not staging_facade.exists():
        raise FileNotFoundError(f"staging thin facade missing: {staging_facade}")

    production_facade.parent.mkdir(parents=True, exist_ok=True)
    backup_created = _backup_facade_before_overwrite(production_facade)
    production_facade.write_text(staging_facade.read_text(encoding="utf-8"), encoding="utf-8")

    staging_v3_skill = staging_path / "agent_skills_v3" / skill_id
    production_v3_skill = project_path / "agent_skills_v3" / skill_id
    v3_promoted = False
    if staging_v3_skill.exists():
        if production_v3_skill.exists():
            shutil.rmtree(production_v3_skill)
        shutil.copytree(staging_v3_skill, production_v3_skill)
        v3_promoted = True

    return {
        "backup_created": backup_created,
        "thin_facade_path": str(production_facade.resolve()),
        "v3_skill_dir": str(production_v3_skill.resolve()) if v3_promoted else None,
        "v3_promoted": v3_promoted,
    }


def _load_facade_module(thin_facade_path: Path):
    module_name = f"v3_publish_smoke_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, thin_facade_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load facade module: {thin_facade_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    return module


def run_v3_smoke(root: Path, skill_id: str) -> None:
    """Static compile and dynamic dispatch smoke for one skill root."""
    thin_facade_path = root / "skills" / f"{skill_id}.py"
    new_house_path = root / "agent_skills_v3" / skill_id / "__init__.py"
    components_dir = root / "agent_skills_v3" / skill_id / "components"

    py_compile.compile(str(thin_facade_path), doraise=True)
    py_compile.compile(str(new_house_path), doraise=True)
    if components_dir.exists():
        for py_file in components_dir.rglob("*.py"):
            py_compile.compile(str(py_file), doraise=True)

    facade = _load_facade_module(thin_facade_path)
    payload = facade.generate(seed=42)
    if not isinstance(payload, dict):
        raise RuntimeError("generate must return dict")
    facade.check("mock answer", "mock answer", question_payload=payload)
    hint = facade.get_hint(1, question_payload=payload)
    if not isinstance(hint, str):
        raise RuntimeError("get_hint must return str")


def publish_single_v3_skill_to_production(
    *,
    conn: sqlite3.Connection,
    skill_id: str,
    project_root: str,
    staging_root: str,
) -> dict[str, object]:
    """Publish one gated skill through staging smoke, promote, and production smoke."""
    skill_key = str(skill_id or "").strip()
    if skill_key not in V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS:
        raise ValueError("production_publish_not_allowed_for_skill")

    project_path = assert_safe_project_root(project_root)
    staging_path = assert_safe_staging_root(staging_root, project_path)

    verified_components = _fetch_verified_components(conn, skill_key)
    if not verified_components:
        raise ValueError("no_verified_components")

    compile_result = compile_and_double_write_skill(conn, skill_key, str(staging_path))
    _sync_dryrun_components_to_v3_house(staging_path, skill_key)

    from core.gencode.v3_component_spec_validator import (
        assert_generator_specs_metadata_consistent,
    )

    generator_specs = compile_result.get("generator_specs")
    if isinstance(generator_specs, list):
        assert_generator_specs_metadata_consistent(
            sandbox_root=str(staging_path),
            skill_id=skill_key,
            generator_specs=generator_specs,
        )

    try:
        run_v3_smoke(staging_path, skill_key)
    except Exception as exc:
        raise ValueError(f"staging_smoke_failed: {exc}") from exc

    # Variation Audit Gate check before promotion
    try:
        from core.gencode.services.v3_variation_audit_service import audit_skill_variation
        variation_report = audit_skill_variation(
            skill_id=skill_key,
            source="staging",
            staging_root=str(staging_path),
            conn=conn,
        )
    except Exception as exc:
        raise ValueError(f"variation_audit_failed: {exc}") from exc

    is_first_publish = not (project_path / "skills" / f"{skill_key}.py").exists()
    is_variation_required = skill_key in V3_VARIATION_REQUIRED_SKILLS
    has_static = variation_report.get("static_count", 0) > 0

    if is_variation_required and has_static:
        raise ValueError(
            f"production_publish_blocked: variation gate failed due to static components. "
            f"Warnings: {variation_report.get('variation_warning')}"
        )

    overall_status = "production_published"
    if has_static:
        if is_first_publish or not is_variation_required:
            overall_status = "runtime_ready_with_variation_warning"

    promote_result = _promote_staging_to_production(staging_path, project_path, skill_key)

    try:
        run_v3_smoke(project_path, skill_key)
    except Exception as exc:
        rollback_result = rollback_v3_to_v2_facade(
            skill_key,
            str(project_path),
            trusted_project_root=True,
        )
        return {
            "status": "rolled_back_after_failed_production_smoke",
            "skill_id": skill_key,
            "project_root": str(project_path),
            "staging_root": str(staging_path),
            "component_count": compile_result.get("component_count", 0),
            "smoke_status": "failed",
            "staging_smoke_status": "passed",
            "production_smoke_error": str(exc),
            "promote": promote_result,
            "rollback": rollback_result,
            "timestamp": utc_timestamp(),
            "variation_status": variation_report.get("status"),
            "dynamic_count": variation_report.get("dynamic_count", 0),
            "static_count": variation_report.get("static_count", 0),
            "partially_dynamic_count": variation_report.get("partially_dynamic_count", 0),
            "variation_warning": variation_report.get("variation_warning", ""),
            "variation_status_by_component": variation_report.get("variation_status_by_component", {}),
        }

    return {
        "status": overall_status,
        "skill_id": skill_key,
        "project_root": str(project_path),
        "staging_root": str(staging_path),
        "component_count": compile_result.get("component_count", 0),
        "smoke_status": "passed",
        "staging_smoke_status": "passed",
        "production_smoke_status": "passed",
        "compile": compile_result,
        "promote": promote_result,
        "timestamp": utc_timestamp(),
        "variation_status": variation_report.get("status"),
        "dynamic_count": variation_report.get("dynamic_count", 0),
        "static_count": variation_report.get("static_count", 0),
        "partially_dynamic_count": variation_report.get("partially_dynamic_count", 0),
        "variation_warning": variation_report.get("variation_warning", ""),
        "variation_status_by_component": variation_report.get("variation_status_by_component", {}),
    }
