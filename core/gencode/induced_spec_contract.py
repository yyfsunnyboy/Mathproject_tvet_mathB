"""Required-field contract for V3 component induced specs."""

from __future__ import annotations

from typing import Any

from core.gencode.answer_schema_registry import resolve_answer_schema_key

REQUIRED_INDUCED_SPEC_FIELDS = (
    "component_id",
    "skill_id",
    "domain",
    "domain_operation",
    "problem_type_id",
    "answer_schema_key",
    "presentation_mode",
    "checker_key",
)

ALLOWED_FALLBACK_STATUSES = frozenset({"needs_human_review", "unsupported"})


class InducedSpecContractError(ValueError):
    """Raised when an induced spec lacks mandatory routing fields."""


def migrate_induced_spec_payload(spec: dict[str, Any]) -> dict[str, Any]:
    """Deterministically enrich legacy induced specs; never silently guess schema."""
    migrated = dict(spec or {})
    if migrated.get("classification_status") in ALLOWED_FALLBACK_STATUSES:
        return migrated

    domain_operation = str(
        migrated.get("domain_operation")
        or migrated.get("line_type")
        or migrated.get("target_task")
        or ""
    ).strip()
    problem_type_id = str(
        migrated.get("problem_type_id")
        or migrated.get("target_task")
        or domain_operation
        or ""
    ).strip()
    if domain_operation and not migrated.get("domain_operation"):
        migrated["domain_operation"] = domain_operation
    elif problem_type_id and not migrated.get("domain_operation"):
        migrated["domain_operation"] = problem_type_id
    if problem_type_id and not migrated.get("problem_type_id"):
        migrated["problem_type_id"] = problem_type_id

    if not migrated.get("answer_schema_key"):
        resolved = resolve_answer_schema_key(
            domain_operation=domain_operation,
            problem_type_id=problem_type_id,
            task_type=str(migrated.get("line_type") or "").strip() or None,
        )
        if resolved:
            migrated["answer_schema_key"] = resolved
        else:
            migrated["classification_status"] = "needs_human_review"
            migrated.setdefault(
                "classification_blockers",
                ["answer_schema_key_unresolved"],
            )

    if not migrated.get("checker_key"):
        answer_contract = migrated.get("answer_contract")
        if isinstance(answer_contract, dict) and answer_contract.get("checker_key"):
            migrated["checker_key"] = answer_contract["checker_key"]

    if not migrated.get("domain"):
        skill_key = str(migrated.get("skill_id") or "").strip()
        if skill_key:
            try:
                from core.registry.taxonomy_registry import get_fixed_domain_key

                migrated["fixed_domain_key"] = get_fixed_domain_key(skill_key)
                migrated["domain"] = str(migrated["fixed_domain_key"]).split(".", 1)[0]
            except Exception:
                migrated["classification_status"] = "needs_human_review"
                migrated.setdefault("classification_blockers", ["fixed_domain_key_unresolved"])
        else:
            migrated["classification_status"] = "needs_human_review"
            migrated.setdefault("classification_blockers", ["fixed_domain_key_unresolved"])

    if not migrated.get("component_id") and migrated.get("textbook_example_id") is not None:
        migrated["component_id"] = f"src_{int(migrated['textbook_example_id'])}"

    return migrated


def validate_induced_spec_contract(
    spec: dict[str, Any],
    *,
    allow_fallback_status: bool = True,
) -> list[str]:
    """Return blocker messages; empty list means contract satisfied."""
    migrated = migrate_induced_spec_payload(spec)
    blockers: list[str] = []

    status = str(migrated.get("classification_status") or "").strip()
    if allow_fallback_status and status in ALLOWED_FALLBACK_STATUSES:
        return blockers

    for field in REQUIRED_INDUCED_SPEC_FIELDS:
        value = migrated.get(field)
        if value is None or str(value).strip() == "":
            blockers.append(f"missing_induced_spec_field:{field}")

    schema_key = str(migrated.get("answer_schema_key") or "").strip()
    if schema_key and schema_key not in (
        "needs_human_review",
        "unsupported",
    ):
        from core.gencode.answer_schema_registry import ANSWER_SCHEMAS

        if schema_key not in ANSWER_SCHEMAS:
            blockers.append(f"unknown_answer_schema_key:{schema_key}")

    return blockers


def assert_induced_spec_contract(spec: dict[str, Any]) -> dict[str, Any]:
    """Migrate and raise when mandatory induced spec fields are missing."""
    migrated = migrate_induced_spec_payload(spec)
    blockers = validate_induced_spec_contract(migrated)
    if blockers:
        raise InducedSpecContractError("; ".join(blockers))
    return migrated
