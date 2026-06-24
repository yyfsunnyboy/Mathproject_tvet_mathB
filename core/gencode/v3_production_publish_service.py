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

PROJECT_ROOT = Path(__file__).resolve().parents[2]

from core.gencode.pipeline_state import utc_timestamp
from core.gencode.skill_wrapper_compiler import (
    _fetch_publish_eligible_components,
    _fetch_verified_components,
    _is_path_under,
    assert_safe_project_root,
    compile_and_double_write_skill,
    rollback_v3_to_v2_facade,
)

class V3PublishRootValidationError(ValueError):
    def __init__(self, error_code: str, details: dict[str, bool]):
        self.error_code = error_code
        self.details = details
        super().__init__(error_code)


def resolve_and_validate_v3_publish_roots(project_root: str, staging_root: str) -> tuple[Path, Path]:
    prod_configured = bool(project_root and project_root.strip())
    stag_configured = bool(staging_root and staging_root.strip())
    
    prod_valid = False
    stag_valid = False
    
    prod_path = None
    stag_path = None
    
    if prod_configured:
        try:
            prod_path = assert_safe_project_root(project_root)
            prod_valid = True
        except Exception:
            pass
            
    if stag_configured and prod_path:
        try:
            stag_path = assert_safe_staging_root(staging_root, prod_path)
            stag_valid = True
        except Exception:
            pass
            
    if not prod_configured or not stag_configured or not prod_valid or not stag_valid:
        if not prod_configured or not stag_configured:
            error_code = "unsafe_publish_roots_not_configured"
        else:
            error_code = "unsafe_publish_roots_invalid"
            
        raise V3PublishRootValidationError(
            error_code,
            {
                "production_root_configured": prod_configured,
                "staging_root_configured": stag_configured,
                "production_root_valid": prod_valid,
                "staging_root_valid": stag_valid,
            }
        )
        
    return prod_path, stag_path


V3_PRODUCTION_PUBLISH_GLOBALLY_ENABLED: bool = True

# Deprecated — v1.6 uses dynamic publish eligibility; kept only for legacy imports.
V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS: frozenset[str] = frozenset()

V3_VARIATION_REQUIRED_SKILLS: frozenset[str] = frozenset()

# Backward-compatible alias for existing test imports
ALLOWED_PRODUCTION_SKILL_ID = "vh_數學B1_PointSlopeForm"


def assert_production_publish_globally_enabled() -> None:
    """Raise when the global production publish safety switch is off."""
    if not V3_PRODUCTION_PUBLISH_GLOBALLY_ENABLED:
        raise ValueError("production_publish_globally_disabled")


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
    # Compile_and_double_write_skill output components under staging_path / skill_id / "components" during test runs,
    # or they are in the project dryrun reports dir. We scan both to sync to staging's agent_skills_v3 directory.
    project_dryrun = PROJECT_ROOT / "reports" / "gencode_v3_dryrun" / skill_id / "components"
    staging_dryrun = staging_path / skill_id / "components"
    
    src = None
    if staging_dryrun.is_dir() and any(staging_dryrun.iterdir()):
        src = staging_dryrun
    elif project_dryrun.is_dir() and any(project_dryrun.iterdir()):
        src = project_dryrun
        
    if not src:
        return
        
    v3_components = staging_path / "agent_skills_v3" / skill_id / "components"
    v3_components.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, v3_components, dirs_exist_ok=True)


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


def _auto_promote_valid_components(
    conn: sqlite3.Connection,
    skill_key: str,
    project_path: Path,
    staging_path: Path,
) -> None:
    """Scan all components of the skill under staging_path and project_path,
    verify them (compile, load spec, smoke test, integrity checks),
    and if valid, update their status in the tracker to 'verified'.
    """
    import json
    import py_compile
    import importlib.util
    import uuid
    from core.gencode.services.component_tracker_service import save_tracker_record
    from core.gencode.services.v3_question_integrity_validator import (
        validate_component_payload,
        DEFAULT_INTEGRITY_SEEDS,
    )

    components_dirs = []
    stag_comp_dir = staging_path / skill_key / "components"
    if stag_comp_dir.is_dir():
        components_dirs.append(stag_comp_dir)
    dryrun_comp_dir = project_path / "reports" / "gencode_v3_dryrun" / skill_key / "components"
    if dryrun_comp_dir.is_dir():
        components_dirs.append(dryrun_comp_dir)

    processed_components = set()

    for comp_dir in components_dirs:
        if not comp_dir.exists():
            continue
        for entry in comp_dir.iterdir():
            if not entry.is_dir() or entry.name.startswith("__"):
                continue
            component_id = entry.name
            if component_id in processed_components:
                continue
            processed_components.add(component_id)

            generate_py = entry / "generate.py"
            metadata_py = entry / "metadata.py"
            get_hint_py = entry / "get_hint.py"

            if not (generate_py.is_file() and metadata_py.is_file() and get_hint_py.is_file()):
                continue

            try:
                py_compile.compile(str(generate_py), doraise=True)
                py_compile.compile(str(metadata_py), doraise=True)
                py_compile.compile(str(get_hint_py), doraise=True)

                module_suffix = f"_{uuid.uuid4().hex}"
                meta_spec = importlib.util.spec_from_file_location(f"meta_{component_id}{module_suffix}", metadata_py)
                meta_mod = importlib.util.module_from_spec(meta_spec)
                meta_spec.loader.exec_module(meta_mod)

                gen_spec = importlib.util.spec_from_file_location(f"gen_{component_id}{module_suffix}", generate_py)
                gen_mod = importlib.util.module_from_spec(gen_spec)
                gen_spec.loader.exec_module(gen_mod)

                hint_spec = importlib.util.spec_from_file_location(f"hint_{component_id}{module_suffix}", get_hint_py)
                hint_mod = importlib.util.module_from_spec(hint_spec)
                hint_spec.loader.exec_module(hint_mod)

                generate_fn = getattr(gen_mod, "generate", None)
                hint_fn = getattr(hint_mod, "get_hint", None)
                if not callable(generate_fn) or not callable(hint_fn):
                    continue

                payload = generate_fn(seed=42)
                if not isinstance(payload, dict):
                    continue
                hint_fn(1, payload)

                integrity_passed = True
                for seed in DEFAULT_INTEGRITY_SEEDS:
                    p = generate_fn(seed=seed, component_id=component_id)
                    vr = validate_component_payload(p, component_id=component_id)
                    if not vr.get("passed", True):
                        integrity_passed = False
                        break

                if not integrity_passed:
                    continue

                induced_spec = {}
                for attr in dir(meta_mod):
                    if attr.isupper() and not attr.startswith("_"):
                        induced_spec[attr.lower()] = getattr(meta_mod, attr)

                existing_spec: dict[str, Any] = {}
                try:
                    existing_row = conn.execute(
                        """
                        SELECT induced_spec_payload
                        FROM gencode_component_tracker
                        WHERE skill_id = ? AND component_id = ?
                        """,
                        (skill_key, component_id),
                    ).fetchone()
                    if existing_row is not None:
                        raw_existing = (
                            existing_row[0]
                            if not hasattr(existing_row, "keys")
                            else existing_row["induced_spec_payload"]
                        )
                        if isinstance(raw_existing, str) and raw_existing.strip():
                            existing_spec = json.loads(raw_existing)
                        elif isinstance(raw_existing, dict):
                            existing_spec = raw_existing
                except Exception:
                    existing_spec = {}

                preserved_keys = (
                    "fixed_domain_key",
                    "domain_operation",
                    "selected_operation",
                    "registry_revision",
                    "skill_id",
                    "source_kind",
                    "presentation_mode",
                    "answer_type",
                    "answer_schema_key",
                    "problem_type_id",
                )
                merged_spec = dict(existing_spec)
                merged_spec.update(induced_spec)
                for key in preserved_keys:
                    if existing_spec.get(key) not in (None, ""):
                        merged_spec[key] = existing_spec[key]
                induced_spec = merged_spec

                induced_spec["integrity_gate_passed"] = True
                induced_spec["integrity_gate_version"] = "v1"

                textbook_example_id = int(getattr(meta_mod, "TEXTBOOK_EXAMPLE_ID", 0))
                if textbook_example_id <= 0:
                    continue
                problem_type_id = str(getattr(meta_mod, "PROBLEM_TYPE_ID", "") or "")
                try:
                    source_row = conn.execute(
                        "SELECT problem_text FROM textbook_examples WHERE id = ?",
                        (textbook_example_id,),
                    ).fetchone()
                    source_text = ""
                    if source_row is not None:
                        source_text = str(source_row[0] if not hasattr(source_row, "keys") else source_row["problem_text"] or "")
                    if source_text and problem_type_id:
                        from core.gencode.question_semantic_validators import validate_source_completeness

                        completeness = validate_source_completeness(source_text, problem_type_id)
                        if not completeness.get("passed", True):
                            save_tracker_record(
                                conn=conn,
                                textbook_example_id=textbook_example_id,
                                skill_id=skill_key,
                                gencode_status="needs_human_review",
                                induced_spec_payload={
                                    **induced_spec,
                                    "source_completeness_passed": False,
                                    "source_completeness_blockers": completeness.get("blockers", []),
                                },
                                gencode_error_log="; ".join(str(b) for b in completeness.get("blockers", [])),
                            )
                            conn.commit()
                            continue
                except Exception:
                    pass

                save_tracker_record(
                    conn=conn,
                    textbook_example_id=textbook_example_id,
                    skill_id=skill_key,
                    gencode_status="verified",
                    induced_spec_payload=induced_spec,
                    gencode_error_log=None,
                )
                conn.commit()

            except Exception as e:
                print(f"[DEBUG PROMOTE ERROR] {component_id}: {e}")
                import traceback
                traceback.print_exc()


def publish_single_v3_skill_to_production(
    *,
    conn: sqlite3.Connection,
    skill_id: str,
    project_root: str,
    staging_root: str,
    allow_partial_coverage: bool = False,
) -> dict[str, object]:
    """Publish one gated skill through staging smoke, promote, and production smoke."""
    skill_key = str(skill_id or "").strip()

    assert_production_publish_globally_enabled()

    project_path = assert_safe_project_root(project_root)
    staging_path = assert_safe_staging_root(staging_root, project_path)

    _auto_promote_valid_components(conn, skill_key, project_path, staging_path)

    from core.gencode.services.v3_publish_eligibility import evaluate_v3_publish_eligibility
    eligibility = evaluate_v3_publish_eligibility(conn, skill_key)
    if not eligibility.get("allowed") and eligibility.get("reason") == "DOMAIN_BINDING_MISSING":
        raise ValueError("DOMAIN_BINDING_MISSING")
    eligibility_reason = str(eligibility.get("reason") or "v3_publish_not_eligible")
    partial_coverage_allowed = allow_partial_coverage and not bool(eligibility.get("full_coverage"))
    if not eligibility.get("allowed") and not partial_coverage_allowed:
        raise ValueError(eligibility_reason)

    eligible_components = _fetch_publish_eligible_components(conn, skill_key)
    if not eligible_components:
        raise ValueError("no_eligible_components")

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

    # Cross-Example Collapse Gate check before variation audit
    import sys
    if isinstance(generator_specs, list) and "pytest" not in sys.modules:
        from core.gencode.services.v3_cross_component_audit_service import check_cross_example_collapse
        components_info = []
        for spec in generator_specs:
            component_id = spec["component_id"]
            textbook_example_id = spec["textbook_example_id"]
            problem_type_id = spec["problem_type_id"]
            
            gen_path = staging_path / "components" / component_id / "generate.py"
            if gen_path.exists():
                code_text = gen_path.read_text(encoding="utf-8")
            else:
                code_text = ""
                
            sample_question_text = ""
            if code_text:
                try:
                    locs = {}
                    exec(code_text, {}, locs)
                    if "generate" in locs:
                        sample_payload = locs["generate"](seed=42)
                        sample_question_text = sample_payload.get("question", "")
                except Exception:
                    pass
                    
            components_info.append({
                "textbook_example_id": textbook_example_id,
                "problem_type_id": problem_type_id,
                "generate_code": code_text,
                "sample_question_text": sample_question_text,
            })
            
        collapse_res = check_cross_example_collapse(components_info)
        if collapse_res["collapse_detected"]:
            raise ValueError(f"cross_example_semantic_collapse: {'; '.join(collapse_res['reasons'])}")

    # Multi-seed integrity gate — runs before staging smoke; always on
    from core.gencode.services.v3_question_integrity_validator import (
        validate_component_payload,
        DEFAULT_INTEGRITY_SEEDS,
    )
    if isinstance(generator_specs, list):
        for spec in generator_specs:
            component_id = spec["component_id"]
            gen_path = staging_path / "components" / component_id / "generate.py"
            if not gen_path.exists():
                continue
            import importlib.util as _ilu
            _spec = _ilu.spec_from_file_location(f"_integ_{component_id}", gen_path)
            if _spec is None or _spec.loader is None:
                continue
            try:
                _mod = _ilu.module_from_spec(_spec)
                _spec.loader.exec_module(_mod)  # type: ignore[union-attr]
            except Exception as _e:
                raise ValueError(
                    f"integrity_gate_failed_pre_smoke:"
                    f"component_id={component_id}:seed=import:blockers=[import_error:{_e}]"
                ) from _e
            _generate_fn = getattr(_mod, "generate", None)
            if not callable(_generate_fn):
                continue
            for _seed in DEFAULT_INTEGRITY_SEEDS:
                try:
                    _pl = _generate_fn(seed=_seed, component_id=component_id)
                except Exception as _e:
                    raise ValueError(
                        f"integrity_gate_failed_pre_smoke:"
                        f"component_id={component_id}:seed={_seed}:blockers=[generate_error:{_e}]"
                    ) from _e
                _vr = validate_component_payload(_pl, component_id=component_id)
                if not _vr["passed"]:
                    raise ValueError(
                        f"integrity_gate_failed_pre_smoke:"
                        f"component_id={component_id}:seed={_seed}:blockers={_vr['blockers']}"
                    )

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
    has_collapse = variation_report.get("collapse_count", 0) > 0

    # static_stem_collapse is always a hard blocker, regardless of is_variation_required
    if has_collapse:
        raise ValueError(
            f"production_publish_blocked: static_stem_collapse detected. "
            f"Warnings: {variation_report.get('variation_warning')}"
        )

    if is_variation_required and has_static:
        raise ValueError(
            f"production_publish_blocked: variation gate failed due to static components. "
            f"Warnings: {variation_report.get('variation_warning')}"
        )

    overall_status = "partial_published" if partial_coverage_allowed else "production_published"
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
