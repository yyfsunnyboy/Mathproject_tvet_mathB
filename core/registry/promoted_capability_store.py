"""Data-driven store for human-reviewed capabilities promoted into production.

The store is the only persisted source for promoted domains.  At import time
``domain_operation_registry`` registers promoted domain specs and
``taxonomy_registry`` merges promoted skill bindings; statically declared
domains and skill bindings always win over promoted entries.

Entries are written exclusively by
``core.gencode.reviewed_capability_promotion.promote_reviewed_workspace``.
"""

from __future__ import annotations

import copy
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROMOTED_STORE = PROJECT_ROOT / "configs" / "gencode_promoted_capabilities.json"
STORE_SCHEMA = "promoted_capability_store.v1"


def store_path(path: str | Path | None = None) -> Path:
    return Path(path) if path else DEFAULT_PROMOTED_STORE


def load_store(path: str | Path | None = None) -> dict[str, Any]:
    target = store_path(path)
    if not target.is_file():
        return {"schema": STORE_SCHEMA, "domains": {}}
    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != STORE_SCHEMA:
        raise ValueError(f"promoted_store_schema_invalid:{target}")
    domains = payload.get("domains")
    if not isinstance(domains, dict):
        raise ValueError(f"promoted_store_domains_invalid:{target}")
    return payload


def serialize_store(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_store_atomic(path: str | Path | None, payload: dict[str, Any]) -> None:
    target = store_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.tmp")
    tmp.write_bytes(serialize_store(payload))
    os.replace(tmp, target)


def build_domain_spec(domain_key: str, entry: dict[str, Any]):
    from core.registry.domain_operation_registry import DomainCapabilitySpec, OperationSpec

    operations = {}
    for op_key, op in entry["operations"].items():
        operations[op_key] = OperationSpec(
            operation_key=op_key,
            handler=str(op["handler"]),
            payload_adapter=op.get("payload_adapter") or None,
            validator=op.get("validator") or None,
            supported_answer_types=tuple(op.get("supported_answer_types") or ()),
            supported_presentation_modes=tuple(op.get("supported_presentation_modes") or ("short_answer",)),
            runtime_contract=op.get("runtime_contract") or None,
            provided_capabilities=tuple(op.get("provided_capabilities") or (op_key,)),
        )
    return DomainCapabilitySpec(
        domain_key=domain_key,
        domain_module=str(entry["domain_module"]),
        entrypoint=str(entry["entrypoint"]),
        capabilities=frozenset(entry.get("capabilities") or ()),
        operations=operations,
    )


def build_skill_binding(domain_key: str, entry: dict[str, Any], skill_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    binding = entry["skill_bindings"][skill_id]
    operations = list(binding.get("allowed_operations") or entry["operations"].keys())
    curriculum = str(binding.get("default_curriculum_profile") or "")
    routing = {
        "fixed_domain_key": domain_key,
        "domain_module": str(entry["domain_module"]),
        "entrypoint": str(entry["entrypoint"]),
        "default_curriculum_profile": curriculum,
        "allowed_types": operations,
        "promoted_capability": True,
    }
    profile = {
        "fixed_domain_key": domain_key,
        "domain": domain_key.split(".", 1)[0],
        "curriculum_profile": curriculum,
        "registry_revision": str(entry["registry_revision"]),
    }
    return routing, profile


def is_static_skill_binding(skill_id: str) -> bool:
    from core.registry import taxonomy_registry

    routing = taxonomy_registry.SKILL_TO_DOMAIN.get(skill_id)
    return isinstance(routing, dict) and not routing.get("promoted_capability")


# --- import-time loaders -----------------------------------------------------


def register_promoted_domain_specs(path: str | Path | None = None) -> list[str]:
    """Register promoted domains into domain_operation_registry (static domains win)."""
    from core.registry import domain_operation_registry as registry

    try:
        domains = load_store(path)["domains"]
    except Exception:
        logger.exception("promoted capability store unreadable; promoted domains skipped")
        return []
    registered: list[str] = []
    for domain_key, entry in sorted(domains.items()):
        if domain_key in registry._REGISTRY:
            logger.error("promoted domain %s conflicts with a static domain; skipped", domain_key)
            continue
        try:
            registry.register_domain_spec(build_domain_spec(domain_key, entry))
        except Exception:
            logger.exception("promoted domain %s invalid; skipped", domain_key)
            continue
        registered.append(domain_key)
    return registered


def promoted_skill_bindings(
    path: str | Path | None = None,
    *,
    existing_skills: set[str] | frozenset[str] = frozenset(),
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Return (SKILL_TO_DOMAIN rows, SKILL_DOMAIN_PROFILE rows) for promoted, registered domains."""
    from core.registry.domain_operation_registry import get_domain_spec

    try:
        domains = load_store(path)["domains"]
    except Exception:
        logger.exception("promoted capability store unreadable; promoted bindings skipped")
        return {}, {}
    routing_rows: dict[str, dict[str, Any]] = {}
    profile_rows: dict[str, dict[str, Any]] = {}
    for domain_key, entry in sorted(domains.items()):
        spec = get_domain_spec(domain_key)
        if spec is None or spec.domain_module != entry.get("domain_module"):
            continue
        for skill_id in sorted(entry.get("skill_bindings") or {}):
            if skill_id in existing_skills or skill_id in routing_rows:
                logger.error("promoted binding for %s conflicts with an existing binding; skipped", skill_id)
                continue
            routing_rows[skill_id], profile_rows[skill_id] = build_skill_binding(domain_key, entry, skill_id)
    return routing_rows, profile_rows


# --- live runtime application (used inside a promotion transaction) ----------


def _runtime_modules():
    from core.gencode import skill_fixed_domain_authority as authority
    from core.registry import domain_operation_registry as registry
    from core.registry import taxonomy_registry as taxonomy

    return registry, taxonomy, authority


def snapshot_runtime_state(domain_key: str, skill_ids: list[str] | set[str], package_import: str) -> dict[str, Any]:
    registry, taxonomy, authority = _runtime_modules()
    missing = object()

    def _grab(mapping: dict[str, Any], key: str) -> Any:
        value = mapping.get(key, missing)
        return missing if value is missing else copy.deepcopy(value)

    return {
        "_missing": missing,
        "domain_key": domain_key,
        "skill_ids": sorted(set(skill_ids)),
        "registry": registry._REGISTRY.get(domain_key, missing),
        "allowed": _grab(taxonomy.DOMAIN_ALLOWED_OPERATIONS, domain_key),
        "provider": _grab(authority.DOMAIN_PROVIDERS, domain_key),
        "routing": {skill: _grab(taxonomy.SKILL_TO_DOMAIN, skill) for skill in set(skill_ids)},
        "profile": {skill: _grab(taxonomy.SKILL_DOMAIN_PROFILE, skill) for skill in set(skill_ids)},
        "modules": {
            name: module
            for name, module in sys.modules.items()
            if name == package_import or name.startswith(package_import + ".")
        },
        "package_import": package_import,
    }


def restore_runtime_state(snapshot: dict[str, Any]) -> None:
    registry, taxonomy, authority = _runtime_modules()
    missing = snapshot["_missing"]
    domain_key = snapshot["domain_key"]

    def _put(mapping: dict[str, Any], key: str, value: Any) -> None:
        if value is missing:
            mapping.pop(key, None)
        else:
            mapping[key] = value

    _put(registry._REGISTRY, domain_key, snapshot["registry"])
    _put(taxonomy.DOMAIN_ALLOWED_OPERATIONS, domain_key, snapshot["allowed"])
    _put(authority.DOMAIN_PROVIDERS, domain_key, snapshot["provider"])
    for skill, value in snapshot["routing"].items():
        _put(taxonomy.SKILL_TO_DOMAIN, skill, value)
    for skill, value in snapshot["profile"].items():
        _put(taxonomy.SKILL_DOMAIN_PROFILE, skill, value)
    purge_package_modules(snapshot["package_import"])
    sys.modules.update(snapshot["modules"])


def purge_package_modules(package_import: str) -> None:
    for name in [n for n in sys.modules if n == package_import or n.startswith(package_import + ".")]:
        sys.modules.pop(name, None)


def remove_promoted_entry(domain_key: str, entry: dict[str, Any] | None) -> None:
    registry, taxonomy, authority = _runtime_modules()
    registry._REGISTRY.pop(domain_key, None)
    taxonomy.DOMAIN_ALLOWED_OPERATIONS.pop(domain_key, None)
    authority.DOMAIN_PROVIDERS.pop(domain_key, None)
    for skill_id in (entry or {}).get("skill_bindings") or {}:
        routing = taxonomy.SKILL_TO_DOMAIN.get(skill_id)
        if isinstance(routing, dict) and routing.get("promoted_capability"):
            taxonomy.SKILL_TO_DOMAIN.pop(skill_id, None)
            taxonomy.SKILL_DOMAIN_PROFILE.pop(skill_id, None)


def apply_promoted_entry(domain_key: str, entry: dict[str, Any]) -> None:
    registry, taxonomy, authority = _runtime_modules()
    spec = build_domain_spec(domain_key, entry)
    registry.register_domain_spec(spec)
    taxonomy.DOMAIN_ALLOWED_OPERATIONS[domain_key] = list(spec.allowed_operations)
    authority.DOMAIN_PROVIDERS[domain_key] = {
        "domain_module": spec.domain_module,
        "entrypoint": spec.entrypoint,
        "capabilities": spec.capabilities,
        "allowed_operations": spec.allowed_operations,
    }
    for skill_id in entry.get("skill_bindings") or {}:
        routing, profile = build_skill_binding(domain_key, entry, skill_id)
        taxonomy.SKILL_TO_DOMAIN[skill_id] = routing
        taxonomy.SKILL_DOMAIN_PROFILE[skill_id] = profile
