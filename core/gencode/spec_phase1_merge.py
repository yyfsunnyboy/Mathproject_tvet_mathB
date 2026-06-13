from __future__ import annotations

from collections import defaultdict
from typing import Any

from core.gencode.problem_type_spec import (
    get_answer_contract,
    get_dependency_contract,
    get_generator_contract,
    get_semantic_contract,
    get_stem_contract,
    get_template_slot,
    list_problem_types_for_skill,
)
from core.gencode.slot_generators import SLOT_REGISTRY
from core.gencode.classifier_proposal import detect_answer_shape
from core.gencode.pipeline_policy import evaluate_pipeline_gates
from core.gencode.answer_contract_gate import apply_runtime_gate_to_candidate

_EQUIVALENCE_MAP = {
    "exact_text": "exact_string",
    "string_equivalence": "exact_string",
    "numeric_equal": "numeric_exact",
    "numeric_equivalence": "numeric_exact",
    "fraction_equal": "rational_equivalent",
    "algebraic_equivalent": "algebraic_equivalent",
    "expression_equivalence": "algebraic_equivalent",
    "set_equal": "unordered_solution_set",
    "interval_equivalence": "interval_set",
    "inequality_solution_equivalence": "interval_set",
}

_CHECKER_MAP = {
    "single_choice": ("choice_label_checker", "choice_label"),
    "short_answer": ("text_checker", "exact_string"),
    "multi_choice": ("choice_label_checker", "choice_label"),
    "numeric": ("integer_checker", "numeric_exact"),
    "fraction": ("fraction_checker", "rational_equivalent"),
    "expression": ("expression_equivalence_checker", "algebraic_equivalent"),
    "ordered_pair": ("coordinate_pair_checker", "coordinate_pair_equivalence"),
    "coordinate_pair": ("coordinate_pair_checker", "coordinate_pair_equivalence"),
}


def spec_to_answer_contract_proposal(spec: dict[str, Any]) -> dict[str, Any]:
    ac = get_answer_contract(spec)
    answer_type = str(ac.get("answer_type", "")).strip()
    equivalence = str(ac.get("answer_equivalence") or ac.get("equivalence_type") or "").strip()
    answer_shape = str(ac.get("answer_shape", "")).strip()
    checker_key = str(ac.get("checker") or ac.get("checker_key") or "").strip()
    if checker_key:
        eq_default = equivalence
    else:
        checker_key, eq_default = _CHECKER_MAP.get(answer_type, ("text_checker", "exact_string"))
    return {
        "answer_type": answer_type,
        "answer_shape": answer_shape,
        "equivalence_type": _EQUIVALENCE_MAP.get(equivalence, eq_default),
        "checker_key": checker_key,
        "order_matters": answer_type not in {"set", "multi_choice"},
        "accepted_format_notes": [],
        "canonical_answer_schema": answer_type,
        "stem_contract": get_stem_contract(spec),
        "dependency_contract": get_dependency_contract(spec),
        "semantic_contract": get_semantic_contract(spec),
        "generator_contract": get_generator_contract(spec),
        "validator_contract": spec.get("validator_contract") if isinstance(spec.get("validator_contract"), dict) else {},
    }


def slot_generator_readiness(spec: dict[str, Any]) -> str:
    from core.gencode.checker_registry import validate_answer_contract_capability
    from core.gencode.problem_type_canonicalizer import (
        READINESS_CONTRACT_SLOT_MISMATCH,
        evaluate_typed_prefix_readiness,
    )
    from core.gencode.task_families import answer_contract_supports_task

    # Typed-prefix canonicalization: resolve slot + answer_contract before readiness.
    readiness, usable, blockers = evaluate_typed_prefix_readiness(spec)
    if readiness == READINESS_CONTRACT_SLOT_MISMATCH:
        return readiness
    if usable and readiness in {"runtime_ready", "runtime_ready_with_warning"}:
        return readiness

    ac = get_answer_contract(spec)
    cap = validate_answer_contract_capability(ac)
    if cap.get("checker_capability_status") == "blocked":
        return "answer_contract_not_supported"
    contract_ok, _ = answer_contract_supports_task(spec)
    if not contract_ok:
        return "answer_contract_not_supported"
    slot = get_template_slot(spec)
    target_task = str(spec.get("target_task", "")).strip()
    checker = str(ac.get("checker") or ac.get("checker_key") or "").strip()
    equivalence = str(ac.get("answer_equivalence", "")).strip()
    answer_shape = str(ac.get("answer_shape", "")).strip()
    if (
        not slot
        and target_task in {"evaluate_function_value", "interpret_function_notation"}
        and str(ac.get("answer_type", "")).strip() in {"numeric", "short_answer"}
        and checker == "numeric_checker"
        and equivalence in {"numeric_equal", "numeric_equivalence"}
        and answer_shape in {"", "scalar"}
        and "function_value_numeric" in SLOT_REGISTRY
    ):
        return "runtime_ready"
    if slot and slot in SLOT_REGISTRY:
        return "runtime_ready"
    ac = get_answer_contract(spec)
    at = str(ac.get("answer_type", "")).strip()
    if at in {"single_choice", "short_answer"}:
        return "runtime_ready"
    if slot:
        return "pending_template"
    return readiness if readiness != "runtime_ready" else "generator_not_ready"


def merge_phase1_with_problem_type_specs(
    skill_id: str,
    auto_review: dict[str, Any],
    entries: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """When JSON specs exist for skill_id, they define the candidate problem_type list."""
    specs = list_problem_types_for_skill(skill_id)
    if not specs:
        return None

    spec_pt_ids = {str(s.get("problem_type_id", "")).strip() for s in specs}
    per_example = auto_review.get("per_example_classification", []) if isinstance(auto_review.get("per_example_classification"), list) else []
    evidence_groups: dict[str, list[int]] = defaultdict(list)
    for row in per_example:
        if not isinstance(row, dict):
            continue
        exid = row.get("example_id")
        if not isinstance(exid, int):
            continue
        pt = str(row.get("detected_problem_type_id", "")).strip()
        if pt in spec_pt_ids:
            evidence_groups[pt].append(exid)

    all_example_ids = sorted(
        {
            int(e.get("example_id"))
            for e in entries
            if isinstance(e, dict) and isinstance(e.get("example_id"), int)
        }
    )
    candidates: list[dict[str, Any]] = []
    for spec in specs:
        pt = str(spec.get("problem_type_id", "")).strip()
        if not pt:
            continue
        contract = spec_to_answer_contract_proposal(spec)
        matched_ids = sorted(set(evidence_groups.get(pt, [])))
        readiness = slot_generator_readiness(spec)
        answer_shape = detect_answer_shape(contract)
        blockers: list[str] = []
        if readiness == "pending_template":
            blockers.append("slot_generator_not_registered")
        elif readiness == "generator_not_ready":
            blockers.append("generator_not_ready")
        promote = "recommend_promote_for_that_candidate" if readiness == "runtime_ready" else "conservative_hold_for_that_candidate"
        candidates.append(
            {
                "problem_type_id": pt,
                "proposed_problem_type_id": pt,
                "display_name": str(spec.get("display_name", "")).strip(),
                "matched_example_ids": matched_ids,
                "matched_example_count": len(matched_ids),
                "unmatched_example_ids": [x for x in all_example_ids if x not in matched_ids],
                "representative_example_id": matched_ids[0] if matched_ids else None,
                "structural_features": [answer_shape] if answer_shape else [],
                "answer_contract_proposal": contract,
                "checker_key_proposal": str(contract.get("checker_key", "")),
                "equivalence_type_proposal": str(contract.get("equivalence_type", "")),
                "answer_shape": answer_shape,
                "confidence": "high",
                "promote_recommendation": promote,
                "promote_blockers": blockers,
                "risk_flags": [],
                "spec_source": "problem_type_specs.v1.json",
                "generator_readiness": readiness,
                "template_slot": get_template_slot(spec),
            }
        )
        candidates[-1] = apply_runtime_gate_to_candidate(candidates[-1])

    out = dict(auto_review)
    out["candidate_problem_types"] = candidates
    out["proposal_items"] = candidates
    out["split_or_merge_recommendation"] = "spec_defined_problem_types"
    out["problem_type_spec_first"] = True
    out["spec_defined_problem_type_ids"] = sorted(spec_pt_ids)
    gates = evaluate_pipeline_gates(
        candidates,
        source_examples_count=len(entries),
        checker_smoke_passed=False,
        dynamic_sampling_passed=False,
        contract_tests_passed=False,
    )
    out.update(gates)
    out["next_action"] = "spec_defined_types_ready_for_phase2"
    return out
