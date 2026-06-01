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

    # Standard list of single-item data defects & non-fatal structural alarms
    SINGLE_ITEM_DEFECT_TOKENS = [
        "small_number_source_quality_reject",
        "single_broken_latex",
        "registry_rule_needs_review",
        "alignment_score_below_recommended_threshold",
        "small_number_missing_answer",
        "single_problem_type_pending",
        "enrichment_examples_excluded",
        "future_ai_judged_exists",
        "source_bank_only_exists",
        "contextual_application_exists",
        "runtime_ready_candidate_pending",
        "ocr_noise",
        "rulepack",
        "rule_pack",
        "rule-pack",
        "alignment_score",
        "consecutive_same_template",
        "consecutive_same_template_variant",
        "diversity",
        "same_template",
        "template_variant",
        "low_source",
        "insufficient_examples",
        "small_number",
        "broken_latex",
        "needs_review",
        "excluded",
        "pending",
    ]

    # 1. Classify risk flags and identify fatal vs non-fatal
    fatal_risks: list[str] = []
    non_fatal_alarms: list[str] = []

    for x in candidates:
        r_flags = x.get("risk_flags") or []
        for r in r_flags:
            r_str = str(r).strip()
            r_lower = r_str.lower()
            if not r_str:
                continue

            is_single_item = any(tok in r_lower for tok in SINGLE_ITEM_DEFECT_TOKENS)

            if is_single_item:
                if r_str not in non_fatal_alarms:
                    non_fatal_alarms.append(r_str)
            elif "fatal" in r_lower or "crypto" in r_lower or "safety" in r_lower:
                if r_str not in fatal_risks:
                    fatal_risks.append(r_str)
            else:
                # Other non-fatal warnings/risks
                if r_str not in non_fatal_alarms:
                    non_fatal_alarms.append(r_str)

    if semantic_alignment_blocked:
        if "semantic_alignment_blocked" not in non_fatal_alarms:
            non_fatal_alarms.append("semantic_alignment_blocked")

    # Helper function to check if a candidate represents a valid, structurally non-contradictory ProblemTypeSpec
    def is_valid_spec(x: dict[str, Any]) -> bool:
        pt_id = str(x.get("problem_type_id", "")).strip()
        shape = str(x.get("answer_shape", "")).strip()
        contract = x.get("answer_contract_proposal")
        checker = str(x.get("checker_key_proposal", "")).strip()
        eq = str(x.get("equivalence_type_proposal", "")).strip()

        # Check if empty/unknown
        if pt_id in {"", "unknown"}:
            return False
        if shape in {"", "unknown_answer_shape"}:
            return False
        if not isinstance(contract, dict) or not contract:
            return False
        if not checker:
            return False
        if not eq:
            return False

        # Check if contradictory or fatal
        r_flags = x.get("risk_flags") or []
        for r in r_flags:
            r_str = str(r).lower()
            if "contradictory" in r_str or "conflict" in r_str:
                return False

            if "fatal" in r_str or "crypto" in r_str or "safety" in r_str:
                is_single_item = any(tok in r_str for tok in SINGLE_ITEM_DEFECT_TOKENS)
                if not is_single_item:
                    return False
        return True

    # 2. Core Sufficiency Gate Overrides
    valid_specs = [x for x in candidates if is_valid_spec(x)]
    classifier_ok = source_examples_count >= 1 and len(valid_specs) >= 1

    low_source = any(int(x.get("matched_example_count", 0)) < min_examples_runtime_ready for x in valid_specs) if valid_specs else True

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

    runtime_foundation = classifier_ok
    fatal_risk = bool(fatal_risks)

    runtime_allowed = (
        runtime_foundation
        and checker_smoke_passed
        and dynamic_sampling_passed
        and contract_tests_passed
        and (not fatal_risk)
    )

    runtime_blockers: list[str] = []
    if not runtime_foundation:
        runtime_blockers.append("blocked_insufficient_examples")
    if runtime_foundation and not checker_smoke_passed:
        runtime_blockers.append("runtime_smoke_failed")
    if runtime_foundation and not dynamic_sampling_passed:
        runtime_blockers.append("dynamic_sampling_failed")
    if runtime_foundation and not contract_tests_passed:
        runtime_blockers.append("contract_tests_failed")
    if fatal_risk:
        runtime_blockers.append("fatal_risk")

    runtime_status = "runtime_ready_allowed" if runtime_allowed else "blocked_insufficient_examples"
    if fatal_risk:
        runtime_status = "blocked_fatal_risk"

    # Exception Review Demotion
    exception_reasons: list[str] = []
    if source_examples_count < 1:
        exception_reasons.append("no_source_examples")

    for r in fatal_risks:
        exception_reasons.append(r)

    if not valid_specs and source_examples_count >= 1:
        unknown_shape = any(str(x.get("answer_shape", "")).strip() in {"", "unknown_answer_shape"} for x in candidates)
        unknown_problem_type = any(str(x.get("problem_type_id", "")).strip() in {"", "unknown"} for x in candidates)
        missing_checker = any(not str(x.get("checker_key_proposal", "")).strip() for x in candidates)
        missing_eq = any(not str(x.get("equivalence_type_proposal", "")).strip() for x in candidates)
        missing_contract = any(not isinstance(x.get("answer_contract_proposal"), dict) or not x.get("answer_contract_proposal") for x in candidates)
        contradictory = any("contradictory" in str(r).lower() for x in candidates for r in (x.get("risk_flags") or []))

        if unknown_shape:
            exception_reasons.append("unknown_answer_shape")
        if contradictory:
            exception_reasons.append("contradictory_answer_question")
        if missing_checker:
            exception_reasons.append("checker_key_missing_and_cannot_infer")
        if unknown_problem_type:
            exception_reasons.append("candidate_problem_type_unknown")
        if missing_eq:
            exception_reasons.append("equivalence_type_missing")
        if missing_contract:
            exception_reasons.append("answer_contract_missing")

    if runtime_foundation and not checker_smoke_passed:
        exception_reasons.append("runtime_smoke_failed")

    # Trigger required = True if source_examples_count < 1 or fatal crypto/execution safety risk is explicitly flagged
    fatal_crypto_or_safety = False
    for r in fatal_risks:
        r_lower = r.lower()
        if "crypto" in r_lower or "safety" in r_lower or "fatal" in r_lower:
            fatal_crypto_or_safety = True
            break

    exception_required = (source_examples_count < 1) or fatal_crypto_or_safety

    classifier_warnings = []
    if classifier_ok and low_source:
        classifier_warnings.append("insufficient_examples")
    classifier_warnings.extend(non_fatal_alarms)

    generator_warnings = []
    if classifier_ok and low_source:
        generator_warnings.append("low_source_examples")
    generator_warnings.extend(non_fatal_alarms)

    return {
        "classifier_gate": {
            "status": classifier_status,
            "allowed": classifier_ok,
            "warnings": classifier_warnings,
        },
        "generator_draft_gate": {
            "status": generator_status,
            "allowed": classifier_ok,
            "warnings": generator_warnings,
        },
        "runtime_ready_gate": {
            "status": runtime_status,
            "allowed": runtime_allowed,
            "blockers": runtime_blockers,
            "warnings": non_fatal_alarms,
        },
        "exception_review_gate": {
            "required": exception_required,
            "reasons": exception_reasons,
        },
    }
