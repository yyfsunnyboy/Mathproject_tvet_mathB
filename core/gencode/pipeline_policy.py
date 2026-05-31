from __future__ import annotations

from typing import Any


def evaluate_pipeline_gates(
    candidate_problem_types: list[dict[str, Any]],
    *,
    source_examples_count: int,
    checker_smoke_passed: bool = False,
    dynamic_sampling_passed: bool = False,
    contract_tests_passed: bool = False,
    min_examples_runtime_ready: int = 3,
    semantic_alignment_blocked: bool = False,
) -> dict[str, Any]:
    candidates = [x for x in candidate_problem_types if isinstance(x, dict)]
    fatal_risk = any(any("fatal" in str(r).lower() for r in (x.get("risk_flags") or [])) for x in candidates)
    unknown_shape = any(str(x.get("answer_shape", "")).strip() in {"", "unknown_answer_shape"} for x in candidates)
    unknown_problem_type = any(str(x.get("problem_type_id", "")).strip() in {"", "unknown"} for x in candidates)
    missing_checker = any(not str(x.get("checker_key_proposal", "")).strip() for x in candidates)
    missing_eq = any(not str(x.get("equivalence_type_proposal", "")).strip() for x in candidates)
    missing_contract = any(not isinstance(x.get("answer_contract_proposal"), dict) or not x.get("answer_contract_proposal") for x in candidates)
    contradictory = any("contradictory" in str(r).lower() for x in candidates for r in (x.get("risk_flags") or []))

    classifier_ok = (
        source_examples_count >= 1
        and bool(candidates)
        and (not unknown_problem_type)
        and (not unknown_shape)
        and (not missing_contract)
        and (not missing_checker)
        and (not missing_eq)
        and (not fatal_risk)
    )
    low_source = any(int(x.get("matched_example_count", 0)) < min_examples_runtime_ready for x in candidates)
    classifier_status = "classifier_blocked"
    if classifier_ok and low_source:
        classifier_status = "classifier_auto_pending_promote_with_warning"
    elif classifier_ok:
        classifier_status = "classifier_auto_pending_promote"

    generator_status = "generator_draft_blocked"
    if classifier_ok and low_source:
        generator_status = "generator_draft_allowed_with_low_source_warning"
    elif classifier_ok:
        generator_status = "generator_draft_allowed"

    runtime_foundation = classifier_ok and all(int(x.get("matched_example_count", 0)) >= min_examples_runtime_ready for x in candidates)
    runtime_allowed = (
        runtime_foundation
        and checker_smoke_passed
        and dynamic_sampling_passed
        and contract_tests_passed
        and (not fatal_risk)
        and (not semantic_alignment_blocked)
    )
    runtime_status = "runtime_ready_allowed" if runtime_allowed else "blocked_insufficient_examples"
    runtime_blockers: list[str] = []
    if semantic_alignment_blocked:
        runtime_blockers.append("semantic_alignment_blocked")
    if not runtime_foundation:
        runtime_blockers.append("blocked_insufficient_examples")
    if runtime_foundation and not checker_smoke_passed:
        runtime_blockers.append("runtime_smoke_failed")
    if runtime_foundation and not dynamic_sampling_passed:
        runtime_blockers.append("dynamic_sampling_failed")
    if runtime_foundation and not contract_tests_passed:
        runtime_blockers.append("contract_tests_failed")
    if fatal_risk:
        runtime_status = "blocked_fatal_risk"
        runtime_blockers.append("fatal_risk")

    exception_reasons: list[str] = []
    if semantic_alignment_blocked:
        exception_reasons.append("semantic_alignment_blocked")
    if fatal_risk:
        exception_reasons.append("fatal_risk")
    if source_examples_count < 1:
        exception_reasons.append("no_source_examples")
    if unknown_shape:
        exception_reasons.append("unknown_answer_shape")
    if contradictory:
        exception_reasons.append("contradictory_answer_question")
    if missing_checker:
        exception_reasons.append("checker_key_missing_and_cannot_infer")
    if unknown_problem_type:
        exception_reasons.append("candidate_problem_type_unknown")
    if runtime_foundation and not checker_smoke_passed:
        exception_reasons.append("runtime_smoke_failed")
    if any("fake_diversity_fatal" in str(r) for x in candidates for r in (x.get("risk_flags") or [])):
        exception_reasons.append("duplicate_or_fake_diversity_fatal")
    if any(str(x.get("answer_shape", "")) == "manual_review_or_free_response" for x in candidates):
        exception_reasons.append("manual_review_or_free_response_requires_exception_review")

    return {
        "classifier_gate": {
            "status": classifier_status,
            "allowed": classifier_ok,
            "warnings": ["insufficient_examples"] if (classifier_ok and low_source) else [],
        },
        "generator_draft_gate": {
            "status": generator_status,
            "allowed": classifier_ok,
            "warnings": ["low_source_examples"] if (classifier_ok and low_source) else [],
        },
        "runtime_ready_gate": {
            "status": runtime_status,
            "allowed": runtime_allowed,
            "blockers": runtime_blockers,
        },
        "exception_review_gate": {
            "required": bool(exception_reasons),
            "reasons": exception_reasons,
        },
    }
