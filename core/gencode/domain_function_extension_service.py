"""V3 Domain Function Extension gap recording.

This service intentionally does not write speculative code. When a fixed domain
already has an approved canonical function the caller proceeds; otherwise the
gap is recorded with a recoverable V3 error code for human or generator-assisted
domain extension.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from core.gencode.domain_capability_service import DomainCapabilityResult
from core.gencode.v3_error_codes import DOMAIN_FUNCTION_EXTENSION_PENDING, V3PipelineError


@dataclass(frozen=True)
class DomainFunctionGap:
    skill_id: str
    example_id: int | None
    fixed_domain_key: str
    requested_capability: str
    proposed_domain_operation: str
    proposed_function_name: str
    input_contract: dict[str, Any]
    output_contract: dict[str, Any]
    answer_schema_key: str
    mathematical_invariants: tuple[str, ...]
    edge_cases: tuple[str, ...]
    related_example_ids: tuple[int, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["mathematical_invariants"] = list(self.mathematical_invariants)
        data["edge_cases"] = list(self.edge_cases)
        data["related_example_ids"] = list(self.related_example_ids)
        return data


def build_capability_gap_record(
    *,
    skill_id: str,
    example_id: int | None,
    capability: DomainCapabilityResult,
    source_example: dict[str, Any] | None = None,
) -> DomainFunctionGap:
    source = source_example or {}
    return DomainFunctionGap(
        skill_id=str(skill_id or "").strip(),
        example_id=example_id,
        fixed_domain_key=capability.fixed_domain_key,
        requested_capability=capability.requested_capability,
        proposed_domain_operation=capability.domain_operation,
        proposed_function_name=capability.function_name,
        input_contract={
            "source_fields": sorted(str(k) for k in source.keys()),
            "domain_operation": capability.domain_operation,
        },
        output_contract={
            "shape": "Full Matrix Dictionary",
            "required_fields": [
                "givens",
                "answer",
                "distractors",
                "explanation_steps",
                "validation_facts",
                "visual_spec",
            ],
        },
        answer_schema_key=capability.answer_schema_key,
        mathematical_invariants=(
            "answer correctness",
            "distractor uniqueness",
            "exact numeric types",
        ),
        edge_cases=("empty source", "invalid seed", "boundary values"),
        related_example_ids=tuple([example_id] if isinstance(example_id, int) else []),
    )


def extend_domain_function_for_capability(
    *,
    skill_id: str,
    example_id: int | None,
    capability: DomainCapabilityResult,
    source_example: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record a recoverable domain-function gap and stop component generation."""
    gap = build_capability_gap_record(
        skill_id=skill_id,
        example_id=example_id,
        capability=capability,
        source_example=source_example,
    )
    raise V3PipelineError(
        DOMAIN_FUNCTION_EXTENSION_PENDING,
        f"{DOMAIN_FUNCTION_EXTENSION_PENDING}:{capability.domain_operation}",
        details={"capability_gap": gap.to_dict()},
    )
