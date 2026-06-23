"""Skill-Fixed Domain Authority — deterministic routing gates for Gencode V3."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from core.registry.taxonomy_registry import (
    SkillDomainNotRegisteredError,
    get_allowed_operations,
    get_fixed_domain_key,
    get_registry_revision,
    resolve_domain_for_skill,
)
from core.gencode.v3_error_codes import (
    DOMAIN_BINDING_MISSING,
    DOMAIN_FUNCTION_MISSING,
    DOMAIN_OPERATION_MISSING,
)

logger = logging.getLogger(__name__)

# Routing blocker codes (also used as tracker gencode_status where applicable).
SKILL_DOMAIN_NOT_REGISTERED = DOMAIN_BINDING_MISSING
DOMAIN_OPERATION_NOT_ALLOWED = "domain_operation_not_allowed"
UNSUPPORTED_DOMAIN_OPERATION = "unsupported_domain_operation"
FIXED_DOMAIN_VIOLATION = "fixed_domain_violation"
OPERATION_CONTRACT_MISMATCH = "operation_contract_mismatch"

AI_IGNORED_ROUTING_FIELDS = frozenset(
    {
        "domain_key",
        "domain_family",
        "recommended_skill",
        "nearest_template",
        "domain",
        "fixed_domain_key",
    }
)


class SkillFixedDomainError(ValueError):
    """Base error for skill-fixed domain authority violations."""

    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = str(code)
        self.details = dict(details or {})


@dataclass(frozen=True)
class FixedDomainContext:
    skill_id: str
    fixed_domain_key: str
    allowed_operations: tuple[str, ...]
    registry_revision: str
    domain_module: str
    entrypoint: str
    curriculum_profile: str


def resolve_fixed_domain_context(skill_id: str) -> FixedDomainContext:
    """Resolve authoritative fixed-domain context for a skill."""
    key = str(skill_id or "").strip()
    try:
        routing = resolve_domain_for_skill(key)
    except KeyError as exc:
        raise SkillFixedDomainError(
            SKILL_DOMAIN_NOT_REGISTERED,
            f"{DOMAIN_BINDING_MISSING}: {key!r}",
            details={"skill_id": key},
        ) from exc

    fixed_domain_key = get_fixed_domain_key(key)
    allowed = tuple(get_allowed_operations(fixed_domain_key, skill_id=key))
    if not allowed:
        raise SkillFixedDomainError(
            UNSUPPORTED_DOMAIN_OPERATION,
            f"no_allowed_operations_for_domain: {fixed_domain_key!r}",
            details={"skill_id": key, "fixed_domain_key": fixed_domain_key},
        )

    return FixedDomainContext(
        skill_id=key,
        fixed_domain_key=fixed_domain_key,
        allowed_operations=allowed,
        registry_revision=get_registry_revision(key),
        domain_module=str(routing.get("domain_module") or ""),
        entrypoint=str(routing.get("entrypoint") or ""),
        curriculum_profile=str(
            routing.get("default_curriculum_profile")
            or routing.get("curriculum_profile")
            or "vocational_high_b"
        ),
    )


def strip_ai_routing_fields(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove AI-suggested routing fields that must not influence dispatch."""
    cleaned = dict(payload or {})
    for field in AI_IGNORED_ROUTING_FIELDS:
        cleaned.pop(field, None)
    return cleaned


def assert_operation_allowed(
    *,
    skill_id: str,
    fixed_domain_key: str,
    selected_operation: str,
    allowed_operations: list[str] | tuple[str, ...] | None = None,
) -> str:
    """Hard gate: selected_operation must be in allowed_operations whitelist."""
    op = str(selected_operation or "").strip()
    if not op:
        raise SkillFixedDomainError(
            DOMAIN_OPERATION_NOT_ALLOWED,
            "domain_operation_not_allowed: empty operation",
            details={
                "skill_id": skill_id,
                "fixed_domain_key": fixed_domain_key,
                "selected_operation": op,
            },
        )

    whitelist = tuple(allowed_operations or get_allowed_operations(fixed_domain_key, skill_id=skill_id))
    if op not in whitelist:
        raise SkillFixedDomainError(
            DOMAIN_OPERATION_NOT_ALLOWED,
            f"domain_operation_not_allowed: {op!r} not in {list(whitelist)!r}",
            details={
                "skill_id": skill_id,
                "fixed_domain_key": fixed_domain_key,
                "selected_operation": op,
                "allowed_operations": list(whitelist),
            },
        )
    return op


def assert_template_dispatch(
    *,
    skill_id: str,
    fixed_domain_key: str,
    template_domain_key: str,
    template_operation_key: str,
    allowed_operations: list[str] | tuple[str, ...] | None = None,
) -> None:
    """Validate template slot domain/operation before dispatch."""
    if str(template_domain_key or "").strip() != str(fixed_domain_key or "").strip():
        raise SkillFixedDomainError(
            FIXED_DOMAIN_VIOLATION,
            f"fixed_domain_violation: template domain {template_domain_key!r} != {fixed_domain_key!r}",
            details={
                "skill_id": skill_id,
                "fixed_domain_key": fixed_domain_key,
                "template_domain_key": template_domain_key,
                "template_operation_key": template_operation_key,
            },
        )
    assert_operation_allowed(
        skill_id=skill_id,
        fixed_domain_key=fixed_domain_key,
        selected_operation=template_operation_key,
        allowed_operations=allowed_operations,
    )


def build_classifier_taxonomy_entry(ctx: FixedDomainContext) -> dict[str, Any]:
    """Taxonomy entry passed to semantic classifier — AI cannot override domain."""
    return {
        "skill_id": ctx.skill_id,
        "fixed_domain_key": ctx.fixed_domain_key,
        "allowed_operations": list(ctx.allowed_operations),
        "allowed_types": list(ctx.allowed_operations),
        "registry_revision": ctx.registry_revision,
    }


def normalize_ai_classification(
    classification: dict[str, Any],
    ctx: FixedDomainContext,
) -> dict[str, Any]:
    """Normalize AI/deterministic classification output under fixed domain authority."""
    cleaned = strip_ai_routing_fields(classification)
    selected = str(
        cleaned.get("selected_operation")
        or cleaned.get("domain_operation")
        or cleaned.get("problem_type_id")
        or ""
    ).strip()
    if selected:
        assert_operation_allowed(
            skill_id=ctx.skill_id,
            fixed_domain_key=ctx.fixed_domain_key,
            selected_operation=selected,
            allowed_operations=ctx.allowed_operations,
        )
    normalized = {
        **cleaned,
        "skill_id": ctx.skill_id,
        "fixed_domain_key": ctx.fixed_domain_key,
        "registry_revision": ctx.registry_revision,
        "selected_operation": selected or cleaned.get("selected_operation"),
        "domain_operation": selected or cleaned.get("domain_operation"),
    }
    if selected and not normalized.get("problem_type_id"):
        normalized["problem_type_id"] = selected
    return normalized


def log_dispatch_event(
    *,
    phase: str,
    skill_id: str,
    component_id: str = "",
    example_id: int | None = None,
    fixed_domain_key: str = "",
    selected_operation: str = "",
    problem_type_id: str = "",
    template_slot: str = "",
    template_domain_key: str = "",
    seed: int | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Structured dispatch log — required fields for audit trail."""
    record = {
        "phase": str(phase or "").strip(),
        "skill_id": str(skill_id or "").strip(),
        "component_id": str(component_id or "").strip(),
        "example_id": example_id,
        "fixed_domain_key": str(fixed_domain_key or "").strip(),
        "selected_operation": str(selected_operation or "").strip(),
        "problem_type_id": str(problem_type_id or "").strip(),
        "template_slot": str(template_slot or "").strip(),
        "template_domain_key": str(template_domain_key or "").strip(),
        "seed": seed,
    }
    if extra:
        record.update(extra)
    logger.info("[GENCODE_DISPATCH] %s", json.dumps(record, ensure_ascii=False, default=str))


def validate_publish_component_record(
    *,
    skill_id: str,
    component_skill_id: str,
    component_fixed_domain_key: str,
    component_operation: str,
    component_status: str,
    registry_skill_id: str | None = None,
) -> list[str]:
    """Return publish blockers for a single component; empty means eligible."""
    blockers: list[str] = []
    skill_key = str(skill_id or "").strip()
    if str(component_skill_id or "").strip() != skill_key:
        blockers.append("publish_skill_id_mismatch")
    try:
        ctx = resolve_fixed_domain_context(skill_key)
    except SkillFixedDomainError as exc:
        blockers.append(exc.code)
        return blockers

    if str(component_fixed_domain_key or "").strip():
        if str(component_fixed_domain_key or "").strip() != ctx.fixed_domain_key:
            blockers.append(FIXED_DOMAIN_VIOLATION)

    op = str(component_operation or "").strip()
    if op and op not in ctx.allowed_operations:
        blockers.append(DOMAIN_OPERATION_NOT_ALLOWED)

    status = str(component_status or "").strip()
    if status in {
        UNSUPPORTED_DOMAIN_OPERATION,
        FIXED_DOMAIN_VIOLATION,
        DOMAIN_OPERATION_NOT_ALLOWED,
        "needs_human_review",
    }:
        blockers.append(f"non_publishable_status:{status}")
    if status != "verified":
        blockers.append("component_not_verified")

    return blockers


