"""Canonical Gencode V3 error codes and compatibility helpers."""

from __future__ import annotations

from typing import Any

DOMAIN_BINDING_MISSING = "DOMAIN_BINDING_MISSING"
DOMAIN_MODULE_MISSING = "DOMAIN_MODULE_MISSING"
DOMAIN_OPERATION_MISSING = "DOMAIN_OPERATION_MISSING"
DOMAIN_FUNCTION_MISSING = "DOMAIN_FUNCTION_MISSING"
DOMAIN_FUNCTION_EXTENSION_PENDING = "DOMAIN_FUNCTION_EXTENSION_PENDING"
DOMAIN_FUNCTION_EXTENSION_FAILED = "DOMAIN_FUNCTION_EXTENSION_FAILED"
DOMAIN_FUNCTION_TEST_FAILED = "DOMAIN_FUNCTION_TEST_FAILED"
SHADOW_BRIDGE_NOT_EXECUTED = "SHADOW_BRIDGE_NOT_EXECUTED"
SHADOW_BRIDGE_FAILED = "SHADOW_BRIDGE_FAILED"
COMPONENT_GENERATION_FAILED = "COMPONENT_GENERATION_FAILED"
COMPONENT_COMPILE_FAILED = "COMPONENT_COMPILE_FAILED"
COMPONENT_SMOKE_FAILED = "COMPONENT_SMOKE_FAILED"
COMPONENT_VERIFICATION_FAILED = "COMPONENT_VERIFICATION_FAILED"
PACKAGING_FAILED = "PACKAGING_FAILED"
UNSUPPORTED_TASK_TYPE = "UNSUPPORTED_TASK_TYPE"

# New Gencode V3 Domain Resolution error codes
DOMAIN_OVERRIDE_NOT_FOUND = "DOMAIN_OVERRIDE_NOT_FOUND"
DOMAIN_CAPABILITY_PARTIAL = "DOMAIN_CAPABILITY_PARTIAL"
DOMAIN_CAPABILITY_UNRESOLVED = "DOMAIN_CAPABILITY_UNRESOLVED"
DOMAIN_CAPABILITY_AMBIGUOUS = "DOMAIN_CAPABILITY_AMBIGUOUS"
DOMAIN_BINDING_CONFLICT = "DOMAIN_BINDING_CONFLICT"
DOMAIN_EVIDENCE_INCOMPLETE = "DOMAIN_EVIDENCE_INCOMPLETE"
DOMAIN_CAPABILITY_MISSING = "domain_capability_missing"
DOMAIN_PROVIDER_MISSING = "DOMAIN_PROVIDER_MISSING"
DOMAIN_ADAPTER_FAILED = "DOMAIN_ADAPTER_FAILED"
CHOICE_CONTRACT_INCOMPLETE = "CHOICE_CONTRACT_INCOMPLETE"


RECOVERABLE_DOMAIN_CODES = frozenset(
    {
        DOMAIN_OPERATION_MISSING,
        DOMAIN_FUNCTION_MISSING,
        DOMAIN_FUNCTION_EXTENSION_PENDING,
    }
)

PIPELINE_DEFECT_CODES = frozenset({SHADOW_BRIDGE_NOT_EXECUTED, SHADOW_BRIDGE_FAILED})

UNSUPPORTED_FINAL_CODES = frozenset({UNSUPPORTED_TASK_TYPE})

LEGACY_ERROR_CODE_MAP = {
    "skill_domain_not_registered": DOMAIN_BINDING_MISSING,
    "unsupported_domain_operation": DOMAIN_FUNCTION_MISSING,
    "domain_operation_not_allowed": DOMAIN_OPERATION_MISSING,
    "fixed_domain_violation": DOMAIN_OPERATION_MISSING,
    "v3_shadow_bridge_not_executed": SHADOW_BRIDGE_NOT_EXECUTED,
}


class V3PipelineError(RuntimeError):
    """Structured V3 pipeline error that keeps responsibility and code intact."""

    def __init__(self, code: str, message: str = "", *, details: dict[str, Any] | None = None):
        self.code = canonical_error_code(code)
        self.details = dict(details or {})
        super().__init__(message or self.code)


def canonical_error_code(code: str) -> str:
    key = str(code or "").strip()
    if not key:
        return COMPONENT_GENERATION_FAILED
    if key in LEGACY_ERROR_CODE_MAP:
        return LEGACY_ERROR_CODE_MAP[key]
    lowered = key.lower()
    if lowered in LEGACY_ERROR_CODE_MAP:
        return LEGACY_ERROR_CODE_MAP[lowered]
    upper = key.upper()
    known = {
        DOMAIN_BINDING_MISSING,
        DOMAIN_MODULE_MISSING,
        DOMAIN_OPERATION_MISSING,
        DOMAIN_FUNCTION_MISSING,
        DOMAIN_FUNCTION_EXTENSION_PENDING,
        DOMAIN_FUNCTION_EXTENSION_FAILED,
        DOMAIN_FUNCTION_TEST_FAILED,
        SHADOW_BRIDGE_NOT_EXECUTED,
        SHADOW_BRIDGE_FAILED,
        COMPONENT_GENERATION_FAILED,
        COMPONENT_COMPILE_FAILED,
        COMPONENT_SMOKE_FAILED,
        COMPONENT_VERIFICATION_FAILED,
        PACKAGING_FAILED,
        UNSUPPORTED_TASK_TYPE,
        DOMAIN_OVERRIDE_NOT_FOUND,
        DOMAIN_CAPABILITY_PARTIAL,
        DOMAIN_CAPABILITY_UNRESOLVED,
        DOMAIN_CAPABILITY_AMBIGUOUS,
        DOMAIN_BINDING_CONFLICT,
        DOMAIN_EVIDENCE_INCOMPLETE,
        DOMAIN_CAPABILITY_MISSING,
        DOMAIN_PROVIDER_MISSING,
        DOMAIN_ADAPTER_FAILED,
        CHOICE_CONTRACT_INCOMPLETE,
    }
    return upper if upper in known else key


def error_code_from_message(message: str) -> str:
    lowered = str(message or "").lower()
    if "domain_capability_ambiguous" in lowered:
        return DOMAIN_CAPABILITY_AMBIGUOUS
    if "domain_capability_partial" in lowered:
        return DOMAIN_CAPABILITY_PARTIAL
    if "domain_capability_unresolved" in lowered:
        return DOMAIN_CAPABILITY_UNRESOLVED
    if "domain_binding_conflict" in lowered:
        return DOMAIN_BINDING_CONFLICT
    if "domain_evidence_incomplete" in lowered:
        return DOMAIN_EVIDENCE_INCOMPLETE
    if "choice_contract_incomplete" in lowered:
        return CHOICE_CONTRACT_INCOMPLETE
    for legacy, canonical in LEGACY_ERROR_CODE_MAP.items():
        if legacy in lowered:
            return canonical
    if "domain_binding" in lowered or "not_registered" in lowered:
        return DOMAIN_BINDING_MISSING
    if "domain_module" in lowered or "no module named" in lowered:
        return DOMAIN_MODULE_MISSING
    if "domain_function_test" in lowered:
        return DOMAIN_FUNCTION_TEST_FAILED
    if "domain_function" in lowered or "entrypoint" in lowered:
        return DOMAIN_FUNCTION_MISSING
    if "domain_operation" in lowered or "operation" in lowered:
        return DOMAIN_OPERATION_MISSING
    if "shadow_bridge" in lowered:
        return SHADOW_BRIDGE_NOT_EXECUTED
    if "compile" in lowered:
        return COMPONENT_COMPILE_FAILED
    if "smoke" in lowered:
        return COMPONENT_SMOKE_FAILED
    if "verification" in lowered or "integrity" in lowered:
        return COMPONENT_VERIFICATION_FAILED
    if "unsupported_task_type" in lowered:
        return UNSUPPORTED_TASK_TYPE
    return COMPONENT_GENERATION_FAILED


def is_unsupported_final_error(code: str) -> bool:
    return canonical_error_code(code) in UNSUPPORTED_FINAL_CODES


def is_domain_gap_error(code: str) -> bool:
    return canonical_error_code(code) in {
        DOMAIN_OPERATION_MISSING,
        DOMAIN_FUNCTION_MISSING,
        DOMAIN_FUNCTION_EXTENSION_PENDING,
        DOMAIN_FUNCTION_EXTENSION_FAILED,
        DOMAIN_FUNCTION_TEST_FAILED,
        DOMAIN_CAPABILITY_PARTIAL,
        DOMAIN_CAPABILITY_UNRESOLVED,
    }


def is_pipeline_failure_error(code: str) -> bool:
    return canonical_error_code(code) in PIPELINE_DEFECT_CODES
