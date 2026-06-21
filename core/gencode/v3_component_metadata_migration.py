"""Rebuild V3 component metadata.py from authoritative generator specs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.v3_component_scaffold_builder import _build_metadata_py


def _payload_from_generator_spec(spec: dict[str, Any]) -> dict[str, Any]:
    problem_type_id = str(spec.get("problem_type_id") or "").strip()
    if not problem_type_id:
        raise ValueError(f"missing_problem_type_id:{spec.get('component_id')}")
    payload = dict(spec)
    payload["target_task"] = problem_type_id
    payload["problem_type_id"] = problem_type_id
    payload.setdefault("template_slot", problem_type_id)
    payload.setdefault("source_kind", spec.get("source_kind") or spec.get("component_id"))
    return payload


def rebuild_component_metadata_from_generator_spec(
    *,
    skill_id: str,
    component_dir: str | Path,
    generator_spec: dict[str, Any],
    domain_meta: dict[str, Any],
    write: bool = True,
) -> dict[str, Any]:
    """Rebuild one metadata.py from a generator spec without touching runtime logic."""
    component_path = Path(component_dir)
    component_id = str(generator_spec.get("component_id") or "").strip()
    if not component_id:
        raise ValueError("missing_component_id")
    if component_path.name != component_id:
        raise ValueError(
            f"component_dir_identity_mismatch: expected={component_id!r} actual={component_path.name!r}"
        )
    metadata_path = component_path / "metadata.py"
    before = metadata_path.read_text(encoding="utf-8") if metadata_path.is_file() else ""
    payload_meta = _payload_from_generator_spec(generator_spec)
    rebuilt = _build_metadata_py(
        skill_id=skill_id,
        component_id=component_id,
        source_kind=str(payload_meta.get("source_kind") or component_id),
        order_weight=int(payload_meta.get("sampling_weight") or payload_meta.get("source_order") or 10),
        difficulty_level=str(payload_meta.get("difficulty_level") or "easy"),
        domain_meta=domain_meta,
        payload_meta=payload_meta,
        textbook_example_id=int(payload_meta.get("textbook_example_id") or 0),
    )
    changed = before != rebuilt
    if write and changed:
        metadata_path.write_text(rebuilt, encoding="utf-8")
    return {
        "component_id": component_id,
        "metadata_path": str(metadata_path),
        "changed": changed,
        "written": bool(write and changed),
    }


def rebuild_component_metadata_from_generator_specs(
    *,
    sandbox_root: str | Path,
    skill_id: str,
    generator_specs: list[dict[str, Any]],
    domain_meta: dict[str, Any],
    write: bool = True,
) -> dict[str, Any]:
    """Rebuild all component metadata files under a dryrun/staging root."""
    root = Path(sandbox_root)
    skill_key = str(skill_id or "").strip()
    component_roots = [
        root / skill_key / "components",
        root / "agent_skills_v3" / skill_key / "components",
    ]
    results: list[dict[str, Any]] = []
    for spec in generator_specs:
        component_id = str(spec.get("component_id") or "").strip()
        if not component_id:
            continue
        component_dirs = [base / component_id for base in component_roots if (base / component_id).is_dir()]
        if not component_dirs:
            results.append({
                "component_id": component_id,
                "changed": False,
                "written": False,
                "error": "component_dir_missing",
            })
            continue
        for component_dir in component_dirs:
            results.append(
                rebuild_component_metadata_from_generator_spec(
                    skill_id=skill_key,
                    component_dir=component_dir,
                    generator_spec=spec,
                    domain_meta=domain_meta,
                    write=write,
                )
            )
    return {
        "skill_id": skill_key,
        "total": len(results),
        "changed": sum(1 for row in results if row.get("changed")),
        "written": sum(1 for row in results if row.get("written")),
        "errors": [row for row in results if row.get("error")],
        "components": results,
    }
