"""Classify V3 pipeline failures by repair responsibility layer."""

from __future__ import annotations

from collections import Counter
from typing import Any

FAILURE_LAYER_COMPONENT = "component_local_failure"
FAILURE_LAYER_DOMAIN = "domain_operation_failure"
FAILURE_LAYER_SHARED = "shared_contract_failure"
FAILURE_LAYER_PACKAGING = "packaging_failure"

_SHARED_CONTRACT_MARKERS = (
    "answer_schema_mismatch",
    "answer_schema_unknown",
    "missing_induced_spec_field",
    "unknown_answer_schema_key",
    "matrix['answer'] missing required fields",
    "shared_contract",
    "schema registry",
)

_DOMAIN_OPERATION_MARKERS = (
    "unsupported line_type",
    "unsupported_line_equation_task_type",
    "required_line_task_slot_missing",
    "domain_operation_failure",
    "distance formula",
)

_PACKAGING_MARKERS = (
    "manifest",
    "dispatch",
    "wrapper",
    "generator_spec_metadata_inconsistent",
    "packaging_failure",
    "compile_v3",
)


def classify_failure_message(message: str) -> str:
    """Map one error message to a responsibility layer."""
    lowered = str(message or "").lower()
    if any(marker in lowered for marker in _PACKAGING_MARKERS):
        return FAILURE_LAYER_PACKAGING
    if any(marker in lowered for marker in _SHARED_CONTRACT_MARKERS):
        return FAILURE_LAYER_SHARED
    if any(marker in lowered for marker in _DOMAIN_OPERATION_MARKERS):
        return FAILURE_LAYER_DOMAIN
    return FAILURE_LAYER_COMPONENT


def classify_batch_failures(failures: list[dict[str, Any]]) -> dict[str, Any]:
    """Detect shared-contract blockers when multiple components share identical errors."""
    messages = [
        str(item.get("error") or item.get("message") or item.get("gencode_error_log") or "")
        for item in failures
    ]
    normalized = [msg.strip() for msg in messages if msg.strip()]
    counts = Counter(normalized)
    dominant_message, dominant_count = ("", 0)
    if counts:
        dominant_message, dominant_count = counts.most_common(1)[0]

    shared_contract = (
        dominant_count >= 2
        and classify_failure_message(dominant_message) == FAILURE_LAYER_SHARED
    )
    layer = (
        FAILURE_LAYER_SHARED
        if shared_contract
        else classify_failure_message(dominant_message)
    )
    return {
        "failure_layer": layer,
        "shared_contract_failure": shared_contract,
        "dominant_error": dominant_message,
        "dominant_error_count": dominant_count,
        "component_failure_count": len(normalized),
        "should_skip_component_repair": shared_contract,
    }
