# -*- coding: utf-8 -*-
"""Package and publish the sealed Math B2 1-2 V3 components without DB writes."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

from core.gencode.b2_12_component_specs import COMPONENT_SPECS
from core.gencode.schema.gencode_component_tracker_inspection import (
    ensure_gencode_component_tracker_table,
)
from core.gencode.skill_fixed_domain_authority import get_confirmed_skill_binding
from core.gencode.skill_wrapper_compiler import compile_and_double_write_skill
from core.gencode.v3_production_publish_service import (
    _sync_staging_v3_component_sources,
    run_v3_smoke,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_COMPONENTS = {
    "vh_數學B2_RatioAndRatioValue": 2,
    "vh_數學B2_TrigonometricFunctionsOfAcuteAngles": 10,
    "vh_數學B2_TrigonometricValuesOfSpecialAngles": 6,
    "vh_數學B2_CalculatingFunctionValuesUsingCalculator": 2,
    "vh_數學B2_FundamentalTrigonometricIdentities": 10,
}

# Phase 2 keeps these verified source components, but Phase 3 must not publish
# or expose them through a runtime skill wrapper.
RUNTIME_EXCLUDED_EXAMPLE_IDS = frozenset({11575})


def _load_generate(example_id: int, skill_id: str) -> Any:
    path = (
        PROJECT_ROOT / "agent_skills_v3" / skill_id
        / "components" / f"src_{example_id}" / "generate.py"
    )
    module_spec = importlib.util.spec_from_file_location(f"b2_12_phase3_{example_id}", path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"component_import_failed:src_{example_id}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.generate


def _tracker_snapshot() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    ensure_gencode_component_tracker_table(conn)
    for example_id, component in sorted(COMPONENT_SPECS.items()):
        if example_id in RUNTIME_EXCLUDED_EXAMPLE_IDS:
            continue
        skill_id = str(component["skill_id"])
        operation = str(component["operation"])
        payload = _load_generate(example_id, skill_id)(seed=0, component_id=f"src_{example_id}")
        binding = get_confirmed_skill_binding(skill_id) or {}
        spec = {
            "skill_id": skill_id,
            "textbook_example_id": example_id,
            "component_id": f"src_{example_id}",
            "source_kind": payload.get("source_kind"),
            "fixed_domain_key": binding.get("fixed_domain_key"),
            "domain_module": binding.get("domain_module"),
            "entrypoint": binding.get("entrypoint"),
            "binding_status": "confirmed",
            "resolution_source": "confirmed_binding",
            "registry_revision": binding.get("registry_revision"),
            "domain_operation": operation,
            "selected_operation": operation,
            "problem_type_id": operation,
            "line_type": operation,
            "presentation_mode": payload.get("presentation_mode"),
            "response_mode": payload.get("answer_type"),
            "interaction_type": payload.get("answer_type"),
            "answer_type": payload.get("answer_type"),
            "checker_key": payload.get("checker_key"),
            "equivalence_type": payload.get("equivalence_type"),
            "answer_contract": payload.get("answer_contract"),
            "integrity_gate_passed": True,
            "integrity_gate_version": "v1",
            "choice_contract_valid": True,
            "display_order": example_id,
            "source_order": example_id,
            "sampling_weight": 1,
        }
        if payload.get("presentation_mode") == "single_choice":
            spec.update({
                "choices": payload.get("choices"),
                "answer": payload.get("correct_answer"),
            })
        conn.execute(
            """
            INSERT INTO gencode_component_tracker
                (textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload)
            VALUES (?, ?, ?, 'verified', ?)
            """,
            (example_id, skill_id, f"src_{example_id}", json.dumps(spec, ensure_ascii=False)),
        )
    conn.commit()
    return conn


def _atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.b2_12_phase3.tmp")
    shutil.copy2(source, temporary)
    os.replace(temporary, destination)


def _prune_runtime_exclusions(staging_root: Path, skill_id: str) -> list[str]:
    """Remove preserved Phase 2 sources from this isolated publish package only."""
    removed: list[str] = []
    components_root = staging_root / "agent_skills_v3" / skill_id / "components"
    for example_id in sorted(RUNTIME_EXCLUDED_EXAMPLE_IDS):
        spec = COMPONENT_SPECS.get(example_id) or {}
        if spec.get("skill_id") != skill_id:
            continue
        component_id = f"src_{example_id}"
        component_path = components_root / component_id
        if component_path.is_dir():
            shutil.rmtree(component_path)
            removed.append(component_id)
    return removed


def package_and_publish() -> dict[str, Any]:
    staging_parent = PROJECT_ROOT / "reports" / "gencode_v3_publish_staging"
    staging_parent.mkdir(parents=True, exist_ok=True)
    staging_root = Path(tempfile.mkdtemp(prefix="b2_12_phase3_", dir=staging_parent))
    conn = _tracker_snapshot()
    results: dict[str, Any] = {}
    try:
        # Gate the whole requested section before any production artifact is written.
        for skill_id, expected_count in SKILL_COMPONENTS.items():
            compiled = compile_and_double_write_skill(conn, skill_id, str(staging_root))
            synced = _sync_staging_v3_component_sources(
                staging_root, skill_id, project_path=PROJECT_ROOT
            )
            removed = _prune_runtime_exclusions(staging_root, skill_id)
            synced_count = int(synced["component_count"]) - len(removed)
            if compiled["component_count"] != expected_count:
                raise RuntimeError(f"wrapper_count_mismatch:{skill_id}")
            if synced_count != expected_count:
                raise RuntimeError(f"component_sync_count_mismatch:{skill_id}")
            run_v3_smoke(staging_root, skill_id)
            results[skill_id] = {
                "wrapper_components": expected_count,
                "published": 0,
                "staging_smoke": "passed",
                "production_smoke": "pending",
            }

        # All five staging packages passed; publishing may now begin.
        for skill_id, expected_count in SKILL_COMPONENTS.items():
            stage_skill = staging_root / "agent_skills_v3" / skill_id
            production_skill = PROJECT_ROOT / "agent_skills_v3" / skill_id
            _atomic_copy(stage_skill / "__init__.py", production_skill / "__init__.py")
            _atomic_copy(
                stage_skill / "component_manifest.json",
                production_skill / "component_manifest.json",
            )
            _atomic_copy(
                staging_root / "skills" / f"{skill_id}.py",
                PROJECT_ROOT / "skills" / f"{skill_id}.py",
            )
            run_v3_smoke(PROJECT_ROOT, skill_id)
            results[skill_id]["published"] = expected_count
            results[skill_id]["production_smoke"] = "passed"
    finally:
        conn.close()
    return {
        "status": "published",
        "staging_root": str(staging_root),
        "skills": results,
        "component_total": sum(SKILL_COMPONENTS.values()),
        "production_db_written": False,
    }


if __name__ == "__main__":
    print(json.dumps(package_and_publish(), ensure_ascii=False, indent=2))
