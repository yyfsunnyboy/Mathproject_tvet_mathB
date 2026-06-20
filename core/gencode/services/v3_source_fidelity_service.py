"""V3 Source Semantic Fidelity Gate Service."""

from __future__ import annotations
from typing import Any


def verify_source_fidelity(
    classification: dict[str, Any],
    component_metadata: dict[str, Any],
    *,
    question_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify that the generated component metadata is faithful to the source's
    semantic classification, and optionally validate the question payload via
    the integrity gate.

    Args:
        classification: Output of the semantic classifier.
        component_metadata: Dict containing PROBLEM_TYPE_ID, PRESENTATION_MODE,
            ANSWER_TYPE keys (from the generated metadata.py).
        question_payload: Optional — if provided, the raw payload returned by
            generate(seed=42) is passed through validate_component_payload().
            Blockers are surfaced as fidelity errors with the prefix
            "integrity_gate_blocker:".  When None, the function behaves
            identically to the original implementation (backward compatible).
    """
    errors: list[str] = []

    # 1. problem_type_id match
    expected_type = classification.get("problem_type_id")
    actual_type = component_metadata.get("PROBLEM_TYPE_ID")
    if actual_type != expected_type:
        errors.append(f"problem_type_id mismatch: got {actual_type!r}, expected {expected_type!r}")

    # 2. presentation_mode match
    expected_mode = classification.get("presentation_mode")
    actual_mode = component_metadata.get("PRESENTATION_MODE")
    if actual_mode != expected_mode:
        errors.append(f"presentation_mode mismatch: got {actual_mode!r}, expected {expected_mode!r}")

    # 3. answer_type match
    expected_ans = classification.get("answer_type")
    actual_ans = component_metadata.get("ANSWER_TYPE")
    if actual_ans != expected_ans:
        errors.append(f"answer_type mismatch: got {actual_ans!r}, expected {expected_ans!r}")

    # 4. Prevent generic fallback leakage
    if (
        actual_type == "write_line_equation_from_point_slope"
        and expected_type != "write_line_equation_from_point_slope"
    ):
        errors.append("Fidelity violation: component leaked default point-slope fallback")

    # 5. Optional payload integrity check (no-op when question_payload is None)
    integrity_gate_passed: bool | None = None
    integrity_gate_blockers: list[str] = []
    if question_payload is not None:
        from core.gencode.services.v3_question_integrity_validator import validate_component_payload
        integrity_result = validate_component_payload(question_payload)
        integrity_gate_passed = integrity_result["passed"]
        integrity_gate_blockers = integrity_result["blockers"]
        for blocker in integrity_gate_blockers:
            errors.append(f"integrity_gate_blocker:{blocker}")

    result: dict[str, Any] = {
        "fidelity_passed": len(errors) == 0,
        "errors": errors,
    }
    if question_payload is not None:
        result["integrity_gate_passed"] = integrity_gate_passed
        result["integrity_gate_blockers"] = integrity_gate_blockers
    return result
