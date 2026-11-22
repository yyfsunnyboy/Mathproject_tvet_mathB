# -*- coding: utf-8 -*-
"""Shared static inventory of GenCode V3 Generator problem types per skill.

Counts are derived from production Registry evidence only:
  skills/{skill_id}.py facade + agent_skills_v3/{skill_id}/ package.

Four quantities are intentionally separated:
  - generator_impl_count: distinct component generate.py implementations
  - usable_problem_type_count: deduped runtime-selectable problem_type_id values
  - textbook_example_count / eligible_example_count: textbook coverage (optional callers)
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]

_BLOCKED_READINESS = frozenset({"blocked", "disabled", "pending", "not_ready"})
_PT_SUFFIX = re.compile(r"_\d+$")
_UNKNOWN = object()


def normalize_problem_type_id(problem_type_id: str) -> str:
    """Strip trailing numeric variant suffix (_1, _2); keep semantic suffixes."""
    return _PT_SUFFIX.sub("", str(problem_type_id or "").strip())


def is_outline_skill(skill_id: str, category: str | None = None) -> bool:
    sid = str(skill_id or "").strip()
    if sid.startswith("outline_"):
        return True
    cat = str(category or "").strip().lower()
    return cat == "outline"


def format_problem_type_count_display(count: int | None) -> str:
    """Admin table label: 'N 種', '0 種', or '—' when unknown."""
    if count is None:
        return "—"
    return f"{int(count)} 種"


def _resolve_root(project_root: str | Path | None) -> Path:
    if project_root is not None and str(project_root).strip():
        return Path(project_root)
    return PROJECT_ROOT


def _read_assign_list(path: Path, name: str) -> list[Any] | None:
    """Parse a module-level list assignment via AST. None = unreadable/missing."""
    if not path.is_file():
        return None
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig", errors="replace"))
    except Exception:
        return _UNKNOWN  # type: ignore[return-value]
    for node in tree.body:
        if not (
            isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
        ):
            continue
        try:
            value = ast.literal_eval(node.value)
        except Exception:
            return _UNKNOWN  # type: ignore[return-value]
        if not isinstance(value, list):
            return _UNKNOWN  # type: ignore[return-value]
        return value
    return []


def _read_assign_str(path: Path, name: str) -> str | None:
    if not path.is_file():
        return None
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig", errors="replace"))
    except Exception:
        return None
    for node in tree.body:
        if not (
            isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
        ):
            continue
        try:
            value = ast.literal_eval(node.value)
        except Exception:
            return None
        return str(value) if value is not None else None
    return None


def _is_runtime_ready(row: dict[str, Any]) -> bool:
    readiness = str(row.get("generator_readiness", "runtime_ready")).strip().lower()
    return readiness not in _BLOCKED_READINESS


def _spec_rows(raw: list[Any] | None | object) -> list[dict[str, Any]] | None:
    if raw is _UNKNOWN:
        return None
    if raw is None:
        return []
    return [row for row in raw if isinstance(row, dict)]


def _key_set(raw: list[Any] | None | object) -> set[str] | None:
    if raw is _UNKNOWN:
        return None
    if raw is None:
        return set()
    out: set[str] = set()
    for item in raw:
        text = str(item or "").strip()
        if text:
            out.add(text)
    return out


def _family_id_from_row(row: dict[str, Any]) -> str:
    for key in ("family_id", "math_family", "line_type"):
        value = str(row.get(key) or "").strip()
        if value:
            return value
    return ""


def _component_generate_path(package_dir: Path, component_id: str) -> Path:
    return package_dir / "components" / component_id / "generate.py"


def inventory_skill_generator_problem_types(
    skill_id: str,
    *,
    project_root: str | Path | None = None,
    production_base_dir: str = "agent_skills_v3",
    category: str | None = None,
) -> dict[str, Any]:
    """Static inventory for one skill. Does not execute generators."""
    skill_key = str(skill_id or "").strip()
    root = _resolve_root(project_root)
    package_dir = root / production_base_dir / skill_key
    facade_path = root / "skills" / f"{skill_key}.py"
    package_init = package_dir / "__init__.py"

    base: dict[str, Any] = {
        "skill_id": skill_key,
        "is_outline": is_outline_skill(skill_key, category),
        "facade_path": str(facade_path),
        "package_init_path": str(package_init),
        "facade_exists": facade_path.is_file(),
        "package_exists": package_init.is_file(),
        "generator_impl_count": 0,
        "registered_generator_count": 0,
        "usable_problem_type_count": 0,
        "defined_problem_type_count": 0,
        "not_runtime_problem_type_count": 0,
        "family_count": 0,
        "usable_problem_type_ids": [],
        "defined_problem_type_ids": [],
        "not_runtime_problem_type_ids": [],
        "family_ids": [],
        "unknown_problem_type_rows": 0,
        "count_confidence": "known",
        "display_count": 0,
        "display_label": "0 種",
        "health": "PASS",
        "anomalies": [],
        "health_layers": {
            "static_registry": "PASS",
            "runtime_usable_types": 0,
            "checker_verified": None,
            "promotion_gate": None,
            "student_acceptance": None,
            "note": (
                "static_registry only; checker/promotion/student layers require separate evidence"
            ),
        },
        "evidence": {
            "facade": str(facade_path) if facade_path.is_file() else None,
            "package": str(package_init) if package_init.is_file() else None,
            "type_identity": "problem_type_id",
            "runtime_selection": "GENERATOR_SPECS + GENERATOR_KEYS + components/*/generate.py",
        },
    }

    if not skill_key:
        base["count_confidence"] = "unknown"
        base["usable_problem_type_count"] = None
        base["display_count"] = None
        base["display_label"] = "—"
        base["health"] = "UNKNOWN"
        base["anomalies"].append("empty_skill_id")
        return base

    if base["is_outline"]:
        base["health"] = "PASS"
        base["anomalies"].append("outline_skill_excluded_from_executable_types")
        base["display_label"] = "0 種"
        base["health_layers"]["static_registry"] = "PASS"
        base["health_layers"]["runtime_usable_types"] = 0
        base["health_layers"]["note"] = "outline excluded from executable usable-type counts"
        return base

    facade_specs_raw = _read_assign_list(facade_path, "GENERATOR_SPECS") if facade_path.is_file() else None
    facade_keys_raw = _read_assign_list(facade_path, "GENERATOR_KEYS") if facade_path.is_file() else None
    package_specs_raw = _read_assign_list(package_init, "GENERATOR_SPECS") if package_init.is_file() else None
    package_keys_raw = _read_assign_list(package_init, "GENERATOR_KEYS") if package_init.is_file() else None

    facade_specs = _spec_rows(facade_specs_raw)
    package_specs = _spec_rows(package_specs_raw)
    facade_keys = _key_set(facade_keys_raw)
    package_keys = _key_set(package_keys_raw)

    # Some published facades build GENERATOR_SPECS dynamically (non-literal). In that
    # case AST cannot read specs; fall back to package literals when keys are still
    # statically readable so admin counts are not forced to "—".
    if facade_path.is_file() and facade_specs is None and package_specs is not None and facade_keys is not None:
        facade_specs = []
        base["anomalies"].append("facade_generator_specs_not_literal_using_package")
    if package_init.is_file() and package_specs is None and facade_specs is not None and package_keys is not None:
        package_specs = list(facade_specs)
        base["anomalies"].append("package_generator_specs_not_literal_using_facade")

    if (
        (facade_path.is_file() and (facade_specs is None or facade_keys is None))
        or (package_init.is_file() and (package_specs is None or package_keys is None))
    ):
        # Still unreadable on a side that exists → cannot confidently count.
        if facade_specs is None and package_specs is None:
            base["count_confidence"] = "unknown"
            base["usable_problem_type_count"] = None
            base["display_count"] = None
            base["display_label"] = "—"
            base["health"] = "UNKNOWN"
            base["anomalies"].append("generator_metadata_unreadable")
            return base
        # One side totally missing metadata lists.
        if facade_keys is None or package_keys is None:
            base["count_confidence"] = "unknown"
            base["usable_problem_type_count"] = None
            base["display_count"] = None
            base["display_label"] = "—"
            base["health"] = "UNKNOWN"
            base["anomalies"].append("generator_keys_unreadable")
            return base

    facade_specs = facade_specs or []
    package_specs = package_specs or []
    facade_keys = facade_keys or set()
    package_keys = package_keys or set()

    facade_skill_id = _read_assign_str(facade_path, "SKILL_ID") if facade_path.is_file() else None
    package_skill_id = _read_assign_str(package_init, "SKILL_ID") if package_init.is_file() else None
    if facade_skill_id and facade_skill_id != skill_key:
        base["anomalies"].append(f"facade_skill_id_mismatch:{facade_skill_id}")
    if package_skill_id and package_skill_id != skill_key:
        base["anomalies"].append(f"package_skill_id_mismatch:{package_skill_id}")

    # Implementations on disk (actual generate.py files).
    impl_ids: set[str] = set()
    components_dir = package_dir / "components"
    if components_dir.is_dir():
        for child in components_dir.iterdir():
            if child.is_dir() and (child / "generate.py").is_file():
                impl_ids.add(child.name)
    base["generator_impl_count"] = len(impl_ids)

    # Prefer facade registry for runtime (skills/*.py is what practice loads).
    # If facade SPECS were non-literal, package SPECS become the type-identity source
    # while facade KEYS still gate runtime selectability.
    facade_specs_usable_as_primary = bool(facade_path.is_file()) and bool(facade_specs)
    primary_specs = facade_specs if facade_specs_usable_as_primary else package_specs
    primary_keys = facade_keys if facade_path.is_file() else package_keys
    if facade_path.is_file() and package_init.is_file():
        # Runtime-selectable requires agreement between facade and package keys.
        selectable_keys = facade_keys & package_keys
    elif facade_path.is_file():
        selectable_keys = set(facade_keys)
        base["anomalies"].append("package_missing_facade_only")
    elif package_init.is_file():
        selectable_keys = set()
        base["anomalies"].append("facade_missing_package_only_not_runtime")
    else:
        selectable_keys = set()

    defined_by_norm: dict[str, str] = {}
    usable_by_norm: dict[str, str] = {}
    not_runtime_by_norm: dict[str, str] = {}
    family_ids: set[str] = set()
    unknown_rows = 0
    registered_components: set[str] = set()

    def _is_v3_component_id(component_id: str) -> bool:
        cid = str(component_id or "").strip()
        return bool(cid) and (cid.startswith("src_") or cid.startswith("cmp_"))

    for row in primary_specs:
        component_id = str(row.get("component_id") or row.get("generator_key") or "").strip()
        raw_pt = str(row.get("problem_type_id") or "").strip()
        family = _family_id_from_row(row)
        if family:
            family_ids.add(family)
        if _is_v3_component_id(component_id):
            registered_components.add(component_id)

        if not raw_pt or raw_pt.upper() == "UNKNOWN":
            unknown_rows += 1
            continue

        norm = normalize_problem_type_id(raw_pt) or raw_pt
        defined_by_norm.setdefault(norm, raw_pt)

        ready = _is_runtime_ready(row)
        if _is_v3_component_id(component_id):
            generate_ok = _component_generate_path(package_dir, component_id).is_file()
            in_keys = component_id in selectable_keys
            # When facade+package both exist, also require the same component in package specs.
            in_package_specs = True
            if facade_path.is_file() and package_init.is_file() and package_specs:
                in_package_specs = any(
                    str(p.get("component_id") or "").strip() == component_id for p in package_specs
                )
            if generate_ok and in_keys and ready and in_package_specs:
                usable_by_norm.setdefault(norm, raw_pt)
            else:
                not_runtime_by_norm.setdefault(norm, raw_pt)
            continue

        # Legacy / bootstrap facade path: problem_type_id declared without V3 component_id.
        # Runtime can still select via generate_for_skill / adapter when facade exists.
        if ready and facade_path.is_file():
            usable_by_norm.setdefault(norm, raw_pt)
            base["evidence"]["legacy_problem_type_registry"] = True
        else:
            not_runtime_by_norm.setdefault(norm, raw_pt)

    # Types only present on the other side (package vs facade) still count as defined/not-runtime.
    secondary_specs = package_specs if primary_specs is facade_specs else facade_specs
    for row in secondary_specs:
        raw_pt = str(row.get("problem_type_id") or "").strip()
        family = _family_id_from_row(row)
        if family:
            family_ids.add(family)
        if not raw_pt or raw_pt.upper() == "UNKNOWN":
            unknown_rows += 1
            continue
        norm = normalize_problem_type_id(raw_pt) or raw_pt
        defined_by_norm.setdefault(norm, raw_pt)
        if norm not in usable_by_norm:
            not_runtime_by_norm.setdefault(norm, raw_pt)

    # A type that became usable should not remain in not_runtime.
    for norm in usable_by_norm:
        not_runtime_by_norm.pop(norm, None)

    if primary_keys:
        base["registered_generator_count"] = len(registered_components & primary_keys)
    else:
        base["registered_generator_count"] = len(registered_components)

    base["defined_problem_type_ids"] = sorted(defined_by_norm.values())
    base["usable_problem_type_ids"] = sorted(usable_by_norm.values())
    base["not_runtime_problem_type_ids"] = sorted(not_runtime_by_norm.values())
    base["defined_problem_type_count"] = len(defined_by_norm)
    base["usable_problem_type_count"] = len(usable_by_norm)
    base["not_runtime_problem_type_count"] = len(not_runtime_by_norm)
    base["family_ids"] = sorted(family_ids)
    base["family_count"] = len(family_ids)
    base["unknown_problem_type_rows"] = unknown_rows
    base["display_count"] = base["usable_problem_type_count"]
    base["display_label"] = format_problem_type_count_display(base["usable_problem_type_count"])

    if unknown_rows and not usable_by_norm and not defined_by_norm:
        base["count_confidence"] = "unknown"
        base["usable_problem_type_count"] = None
        base["display_count"] = None
        base["display_label"] = "—"
        base["health"] = "UNKNOWN"
        base["anomalies"].append("problem_type_id_unrecognizable")
        return base

    # health here = static Registry / usable-type inventory only.
    # It is NOT Runtime smoke, Checker acceptance, Promotion Gate, or student QA.
    if not facade_path.is_file() and not package_init.is_file():
        base["anomalies"].append("no_generator_artifacts")
        base["health"] = "WARN"
    elif base["generator_impl_count"] > 0 and base["usable_problem_type_count"] == 0:
        base["health"] = "WARN"
        base["anomalies"].append("generators_exist_but_not_runtime_selectable")
    elif facade_path.is_file() and not package_init.is_file():
        base["health"] = "WARN"
    elif package_init.is_file() and not facade_path.is_file():
        base["health"] = "WARN"
    elif base["anomalies"]:
        base["health"] = "WARN"
    else:
        base["health"] = "PASS"

    if any("skill_id_mismatch" in a for a in base["anomalies"]):
        base["health"] = "FAIL"

    # Orphan implementations not registered in primary keys.
    orphan_impls = sorted(impl_ids - (primary_keys or set()))
    if orphan_impls:
        base["anomalies"].append(f"unregistered_generate_py:{','.join(orphan_impls[:8])}")
        if base["health"] == "PASS":
            base["health"] = "WARN"

    missing_impls = sorted((primary_keys or set()) - impl_ids)
    if missing_impls:
        base["anomalies"].append(f"registered_without_generate_py:{','.join(missing_impls[:8])}")
        if base["health"] == "PASS":
            base["health"] = "WARN"

    # Executable skills with zero usable types must not be counted as healthy PASS.
    if (
        not base["is_outline"]
        and base.get("usable_problem_type_count") == 0
        and base["health"] == "PASS"
    ):
        base["health"] = "WARN"
        base["anomalies"].append("executable_skill_with_zero_usable_types")

    base["health_layers"] = {
        "static_registry": base["health"],
        "runtime_usable_types": int(base["usable_problem_type_count"] or 0)
        if base.get("usable_problem_type_count") is not None
        else None,
        "checker_verified": None,
        "promotion_gate": None,
        "student_acceptance": None,
        "note": (
            "static_registry only; checker/promotion/student layers require separate evidence"
        ),
    }

    return base


def build_generator_problem_type_count_map(
    skill_ids: list[str],
    *,
    project_root: str | Path | None = None,
    production_base_dir: str = "agent_skills_v3",
    categories: dict[str, str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Batch inventory keyed by skill_id for admin list pages."""
    categories = categories or {}
    out: dict[str, dict[str, Any]] = {}
    for skill_id in skill_ids:
        key = str(skill_id or "").strip()
        if not key or key in out:
            continue
        out[key] = inventory_skill_generator_problem_types(
            key,
            project_root=project_root,
            production_base_dir=production_base_dir,
            category=categories.get(key),
        )
    return out
