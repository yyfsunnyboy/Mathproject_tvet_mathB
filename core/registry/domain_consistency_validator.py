"""Domain operation registry consistency validator.

Checks that the registry, taxonomy, domain handlers and runtime are mutually
consistent.  Call validate_domain_operation_registry() at application startup
or in the test suite.  Any inconsistency raises DomainRegistryInconsistentError
so the problem is surfaced immediately — not when a user clicks "regenerate".

Conditions checked
------------------
1. registry declares operation, but domain module cannot be imported
2. registry declares operation, but domain entrypoint is not callable
3. registry declares operation, but OperationSpec.handler is empty
4. taxonomy DOMAIN_ALLOWED_OPERATIONS disagrees with registry (drift)
5. DOMAIN_PROVIDERS disagrees with registry (drift)
6. YAML allowed_types contains operations absent from the registry
7. unknown operation passes through undetected (always raises)
"""

from __future__ import annotations

import importlib
import logging
from typing import Any

logger = logging.getLogger(__name__)

DOMAIN_REGISTRY_INCONSISTENT = "DOMAIN_OPERATION_REGISTRY_INCONSISTENT"


class DomainRegistryInconsistentError(RuntimeError):
    """Raised when registry consistency check fails.

    Attributes
    ----------
    findings : list[dict]
        Each dict has keys: code, domain_key, operation (optional),
        missing_layers, detail.
    """

    def __init__(self, findings: list[dict[str, Any]]) -> None:
        self.findings = findings
        lines = [f"[{DOMAIN_REGISTRY_INCONSISTENT}] {len(findings)} issue(s):"]
        for f in findings:
            op = f.get("operation", "")
            layers = ", ".join(f.get("missing_layers") or [])
            lines.append(
                f"  domain_key={f.get('domain_key')}  operation={op}  "
                f"missing_layers=[{layers}]  detail={f.get('detail', '')}"
            )
        super().__init__("\n".join(lines))


def validate_domain_operation_registry(*, raise_on_failure: bool = True) -> list[dict[str, Any]]:
    """Run all consistency checks and return list of findings.

    Parameters
    ----------
    raise_on_failure:
        If True (default) raise DomainRegistryInconsistentError when any
        finding is detected.  Set to False to collect findings without
        raising (useful for reporting).

    Returns
    -------
    list[dict]
        Empty list if fully consistent.
    """
    from core.registry.domain_operation_registry import (
        _REGISTRY,
        check_registry_consistency,
    )
    from core.registry.taxonomy_registry import DOMAIN_ALLOWED_OPERATIONS, SKILL_TO_DOMAIN
    from core.gencode.skill_fixed_domain_authority import DOMAIN_PROVIDERS

    findings: list[dict[str, Any]] = []

    # ── 1–3: registry internal consistency (module/entrypoint/handler) ────────
    findings.extend(check_registry_consistency())

    # ── 4: taxonomy drift ─────────────────────────────────────────────────────
    for dk, registry_ops in _REGISTRY.items():
        taxonomy_ops = set(DOMAIN_ALLOWED_OPERATIONS.get(dk) or [])
        registry_op_set = set(registry_ops.allowed_operations)
        extra_in_taxonomy = taxonomy_ops - registry_op_set
        missing_in_taxonomy = registry_op_set - taxonomy_ops
        if extra_in_taxonomy:
            findings.append({
                "code": DOMAIN_REGISTRY_INCONSISTENT,
                "domain_key": dk,
                "missing_layers": ["taxonomy_sync"],
                "detail": (
                    f"DOMAIN_ALLOWED_OPERATIONS has ops not in registry: {sorted(extra_in_taxonomy)}"
                ),
            })
        if missing_in_taxonomy:
            findings.append({
                "code": DOMAIN_REGISTRY_INCONSISTENT,
                "domain_key": dk,
                "missing_layers": ["taxonomy_sync"],
                "detail": (
                    f"registry has ops missing from DOMAIN_ALLOWED_OPERATIONS: {sorted(missing_in_taxonomy)}"
                ),
            })

    # ── 5: DOMAIN_PROVIDERS drift ─────────────────────────────────────────────
    for dk, prov in DOMAIN_PROVIDERS.items():
        registry_spec = _REGISTRY.get(dk)
        if registry_spec is None:
            findings.append({
                "code": DOMAIN_REGISTRY_INCONSISTENT,
                "domain_key": dk,
                "missing_layers": ["registry"],
                "detail": f"DOMAIN_PROVIDERS has {dk!r} but it is not in domain_operation_registry",
            })
            continue
        prov_ops = set(prov.get("allowed_operations") or [])
        registry_op_set = set(registry_spec.allowed_operations)
        extra = prov_ops - registry_op_set
        missing = registry_op_set - prov_ops
        if extra:
            findings.append({
                "code": DOMAIN_REGISTRY_INCONSISTENT,
                "domain_key": dk,
                "missing_layers": ["providers_sync"],
                "detail": f"DOMAIN_PROVIDERS has ops not in registry: {sorted(extra)}",
            })
        if missing:
            findings.append({
                "code": DOMAIN_REGISTRY_INCONSISTENT,
                "domain_key": dk,
                "missing_layers": ["providers_sync"],
                "detail": f"registry has ops missing from DOMAIN_PROVIDERS: {sorted(missing)}",
            })

    # ── 6: YAML allowed_types must be a subset of registry ───────────────────
    for skill_id, routing in SKILL_TO_DOMAIN.items():
        yaml_types: list[str] = list(
            routing.get("allowed_types") or routing.get("allowed_operations") or []
        )
        if not yaml_types:
            continue
        fixed_dk = str(
            routing.get("fixed_domain_key")
            or routing.get("fixed_domain_key")
            or ""
        ).strip()
        if not fixed_dk:
            continue
        registry_spec = _REGISTRY.get(fixed_dk)
        if registry_spec is None:
            continue
        registry_op_set = set(registry_spec.allowed_operations)
        rogue = [op for op in yaml_types if op not in registry_op_set]
        if rogue:
            findings.append({
                "code": DOMAIN_REGISTRY_INCONSISTENT,
                "domain_key": fixed_dk,
                "missing_layers": ["yaml_allowed_types"],
                "detail": (
                    f"skill {skill_id!r} YAML allowed_types contains ops "
                    f"absent from registry: {rogue}"
                ),
            })

    if findings and raise_on_failure:
        raise DomainRegistryInconsistentError(findings)

    return findings
