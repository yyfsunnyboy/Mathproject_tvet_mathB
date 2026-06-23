"""Shared V3 fixed-domain capability resolution."""

from __future__ import annotations

import importlib
from dataclasses import asdict, dataclass
from typing import Any

from core.gencode.answer_schema_registry import resolve_answer_schema_key
from core.gencode.skill_fixed_domain_authority import FixedDomainContext
from core.gencode.v3_error_codes import (
    DOMAIN_FUNCTION_MISSING,
    DOMAIN_MODULE_MISSING,
    DOMAIN_OPERATION_MISSING,
)


@dataclass(frozen=True)
class DomainCapabilityResult:
    fixed_domain_key: str
    requested_capability: str
    domain_operation: str
    function_name: str
    function_exists: bool
    operation_registered: bool
    answer_schema_key: str
    checker_key: str
    required_validation_facts: tuple[str, ...]
    visual_requirements: tuple[str, ...]
    capability_status: str
    domain_module: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["required_validation_facts"] = list(self.required_validation_facts)
        data["visual_requirements"] = list(self.visual_requirements)
        return data


def resolve_domain_capability(
    *,
    skill_id: str,
    fixed_domain_key: str,
    normalized_classification: dict[str, Any],
    source_example: dict[str, Any] | None = None,
    domain_context: FixedDomainContext | None = None,
) -> DomainCapabilityResult:
    """Resolve operation/function readiness inside the fixed routing domain only."""
    ctx = domain_context
    requested = str(
        normalized_classification.get("requested_capability")
        or normalized_classification.get("domain_operation")
        or normalized_classification.get("selected_operation")
        or normalized_classification.get("problem_type_id")
        or ""
    ).strip()
    operation = str(
        normalized_classification.get("domain_operation")
        or normalized_classification.get("selected_operation")
        or requested
    ).strip()
    allowed = tuple(ctx.allowed_operations if ctx else normalized_classification.get("allowed_operations") or ())
    operation_registered = bool(operation and operation in allowed)

    module_path = str(ctx.domain_module if ctx else normalized_classification.get("domain_module") or "").strip()
    function_name = str(
        normalized_classification.get("function_name")
        or (ctx.entrypoint if ctx else normalized_classification.get("entrypoint"))
        or ""
    ).strip()
    function_exists = False
    module_missing = False
    if module_path:
        try:
            module = importlib.import_module(module_path)
            function_exists = bool(function_name and callable(getattr(module, function_name, None)))
        except ModuleNotFoundError:
            module_missing = True
    else:
        module_missing = True

    answer_schema_key = str(
        normalized_classification.get("answer_schema_key")
        or resolve_answer_schema_key(domain_operation=operation, problem_type_id=operation)
        or ""
    )
    checker_key = str(normalized_classification.get("checker_key") or "")
    if not checker_key:
        checker_key = "choice_label_checker" if "choice" in operation else "integer_checker"

    if module_missing:
        status = DOMAIN_MODULE_MISSING
    elif not operation_registered:
        status = DOMAIN_OPERATION_MISSING
    elif not function_exists:
        status = DOMAIN_FUNCTION_MISSING
    else:
        status = "ready"

    return DomainCapabilityResult(
        fixed_domain_key=str(fixed_domain_key or "").strip(),
        requested_capability=requested,
        domain_operation=operation,
        function_name=function_name,
        function_exists=function_exists,
        operation_registered=operation_registered,
        answer_schema_key=answer_schema_key,
        checker_key=checker_key,
        required_validation_facts=tuple(normalized_classification.get("required_validation_facts") or ()),
        visual_requirements=tuple(normalized_classification.get("visual_requirements") or ()),
        capability_status=status,
        domain_module=module_path,
    )
