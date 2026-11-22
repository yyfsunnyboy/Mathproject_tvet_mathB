# -*- coding: utf-8 -*-
"""B1-only: rewrite facade/package Registry from on-disk component metadata.

Does NOT rebuild generate.py. Backs up existing facade/package first.
Blocked publish eligibility (domain evidence) is bypassed intentionally for
local contract repair when verified components already exist on disk.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.gencode.skill_wrapper_compiler import (
    _render_component_manifest,
    _render_new_house_init_py,
    _render_thin_facade_py,
)

P0_SKILLS = (
    "vh_數學B1_QuadraticFunctionGraph",
    "vh_數學B1_QuadraticInequalityAndFactoring",
    "vh_數學B1_FunctionConcept",
    "vh_數學B1_QuadraticInequalitySolution",
    "vh_數學B1_VertexFormOfQuadraticFunction",
    "vh_數學B1_CompletingTheSquare",
    "vh_數學B1_QuadraticFunctionExtremum",
)


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot_load:{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _specs_from_disk(skill_id: str) -> tuple[list[str], list[dict[str, Any]]]:
    components_dir = ROOT / "agent_skills_v3" / skill_id / "components"
    if not components_dir.is_dir():
        raise RuntimeError(f"missing_components_dir:{skill_id}")
    specs: list[dict[str, Any]] = []
    for child in sorted(components_dir.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            continue
        generate_py = child / "generate.py"
        metadata_py = child / "metadata.py"
        if not generate_py.is_file() or not metadata_py.is_file():
            continue
        meta = _load_module(metadata_py, f"_meta_{skill_id}_{child.name}")
        component_id = str(getattr(meta, "COMPONENT_ID", child.name) or child.name).strip()
        problem_type_id = str(getattr(meta, "PROBLEM_TYPE_ID", "") or "").strip()
        if not problem_type_id:
            raise RuntimeError(f"missing_problem_type_id:{skill_id}:{component_id}")
        textbook_example_id = int(getattr(meta, "TEXTBOOK_EXAMPLE_ID", 0) or 0)
        av = getattr(meta, "ANSWER_VERIFICATION_TYPE", {}) or {}
        if not isinstance(av, dict):
            av = {}
        presentation_mode = str(getattr(meta, "PRESENTATION_MODE", "") or "short_answer")
        answer_type = str(
            getattr(meta, "ANSWER_TYPE", None)
            or getattr(meta, "ANSWER_VALUE_TYPE", None)
            or av.get("answer_type")
            or "text_short"
        )
        specs.append(
            {
                "textbook_example_id": textbook_example_id,
                "component_id": component_id,
                "generator_key": component_id,
                "presentation_mode": presentation_mode,
                "response_mode": str(getattr(meta, "RESPONSE_MODE", None) or presentation_mode),
                "interaction_type": str(getattr(meta, "INTERACTION_TYPE", None) or presentation_mode),
                "source_kind": str(getattr(meta, "SOURCE_KIND", None) or "example"),
                "line_type": str(getattr(meta, "DOMAIN_OPERATION", None) or problem_type_id),
                "answer_type": answer_type,
                "answer_value_type": str(getattr(meta, "ANSWER_VALUE_TYPE", None) or answer_type),
                "problem_type_id": problem_type_id,
                "checker_key": av.get("checker_key"),
                "equivalence_type": av.get("equivalence_type"),
                "display_order": textbook_example_id,
                "source_order": textbook_example_id,
                "sampling_weight": float(getattr(meta, "ORDER_WEIGHT", 10) or 10),
                "generator_readiness": str(getattr(meta, "GENERATOR_READINESS", "runtime_ready")),
            }
        )
    if not specs:
        raise RuntimeError(f"no_disk_components:{skill_id}")
    specs.sort(
        key=lambda row: (
            int(row.get("display_order") or 0),
            int(row.get("textbook_example_id") or 0),
            str(row.get("component_id") or ""),
        )
    )
    keys = [str(row["component_id"]) for row in specs]
    return keys, specs


def _backup(path: Path, backup_root: Path) -> str | None:
    if not path.exists():
        return None
    rel = path.relative_to(ROOT)
    dest = backup_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if path.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(path, dest)
    else:
        shutil.copy2(path, dest)
    return str(dest)


def repair_skill(skill_id: str, backup_root: Path) -> dict[str, Any]:
    keys, specs = _specs_from_disk(skill_id)
    package_dir = ROOT / "agent_skills_v3" / skill_id
    package_init = package_dir / "__init__.py"
    facade = ROOT / "skills" / f"{skill_id}.py"
    manifest = package_dir / "component_manifest.json"

    backups = {
        "facade": _backup(facade, backup_root),
        "package_init": _backup(package_init, backup_root),
        "manifest": _backup(manifest, backup_root),
    }

    package_dir.mkdir(parents=True, exist_ok=True)
    package_init.write_text(
        _render_new_house_init_py(skill_id=skill_id, generator_keys=keys, generator_specs=specs),
        encoding="utf-8",
    )
    facade.write_text(
        _render_thin_facade_py(skill_id=skill_id, generator_keys=keys, generator_specs=specs),
        encoding="utf-8",
    )
    manifest.write_text(
        json.dumps(
            _render_component_manifest(skill_id=skill_id, generator_specs=specs),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "skill_id": skill_id,
        "component_count": len(keys),
        "generator_keys": keys,
        "problem_type_ids": sorted({str(s["problem_type_id"]) for s in specs}),
        "backups": backups,
        "facade": str(facade),
        "package_init": str(package_init),
    }


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = ROOT / "reports" / "gencode_rebuild_backup" / f"b1_registry_repair_{stamp}"
    backup_root.mkdir(parents=True, exist_ok=True)
    results = []
    for skill_id in P0_SKILLS:
        result = repair_skill(skill_id, backup_root)
        results.append(result)
        print(
            "REPAIRED",
            skill_id,
            "components",
            result["component_count"],
            "types",
            len(result["problem_type_ids"]),
        )
    out = backup_root / "repair_summary.json"
    out.write_text(json.dumps({"backup_root": str(backup_root), "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("summary", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
