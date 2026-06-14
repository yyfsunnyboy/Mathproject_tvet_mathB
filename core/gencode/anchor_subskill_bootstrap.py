# -*- coding: utf-8 -*-
"""Bootstrap Phase 1 candidates for anchor subskills with registered slots but zero source examples."""

from __future__ import annotations

from typing import Any

from core.gencode.answer_contract_bridge import legacy_fields_from_answer_contract
from core.gencode.answer_contract_policy import (
    checker_selection_reason,
    infer_answer_contract_from_problem_context,
)
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.classifier_proposal import detect_answer_shape
from core.gencode.generator_contract_schema import enrich_spec_generator_contract
from core.gencode.problem_type_spec import get_template_slot
from core.gencode.slot_generators import SLOT_REGISTRY, TARGET_TASK_GENERATOR_REGISTRY
from core.gencode.task_families import task_family_for_task
from core.gencode.template_slot_resolver import TASK_FAMILY_TO_SLOT

# Anchor tasks that share a slot with another task; skip when the primary is already induced.
_ANCHOR_TASK_SLOT_ALIASES: dict[str, str] = {
    "interpret_quadratic_inequality_solution_set": "solve_quadratic_inequality",
}

_BOOTSTRAP_ANSWER_FORMAT_HINT: dict[str, str] = {
    "solve_quadratic_inequality_special_cases": "text_short",
    "solve_quadratic_inequality_parameter_range": "interval",
    "reverse_quadratic_inequality_coefficients": "integer",
    "applied_quadratic_inequality_problem": "interval",
}


def _task_has_registered_generator(target_task: str, slot: str) -> bool:
    task = str(target_task or "").strip()
    if task in TARGET_TASK_GENERATOR_REGISTRY:
        return True
    resolved_slot = str(slot or task or "").strip()
    return bool(resolved_slot and resolved_slot in SLOT_REGISTRY)


def _bootstrap_problem_type_id(target_task: str, answer_format_hint: str) -> str:
    task = str(target_task or "").strip()
    hint = str(answer_format_hint or "").strip()
    if hint == "integer" and not task.startswith("integer_"):
        return f"integer_{task}"
    if hint == "text_short" and not task.startswith("text_short_"):
        return f"text_short_{task}"
    return task


def _build_anchor_bootstrap_spec(
    skill_id: str,
    target_task: str,
    *,
    existing_ids: set[str],
) -> dict[str, Any] | None:
    from core.gencode.problem_type_canonicalizer import enrich_spec_with_canonicalization

    task = str(target_task or "").strip()
    if not task:
        return None
    math_objects = ["quadratic_inequality"]
    slot = TASK_FAMILY_TO_SLOT.get(task, task)
    if not _task_has_registered_generator(task, slot):
        return None

    task_family = task_family_for_task(task)
    ac = infer_answer_contract_from_problem_context(
        answer_type="short_answer",
        target_task=task,
        task_family=task_family,
        math_objects=math_objects,
        cluster_features=[],
        has_choices=False,
    )
    hint = _BOOTSTRAP_ANSWER_FORMAT_HINT.get(task, "")
    pt_id = _bootstrap_problem_type_id(task, hint)
    suffix = 2
    original = pt_id
    while pt_id in existing_ids:
        pt_id = f"{original}_{suffix}"
        suffix += 1
    existing_ids.add(pt_id)

    generator_contract: dict[str, Any] = {
        "template_families": [task],
        "parameter_slots": {"seed": "integer", "difficulty": "easy"},
        "randomization_rules": {"shuffle_choices": False},
        "avoid_llm_freeform_math": True,
        "use_domain_functions": True,
        "derivation_steps_required": True,
    }
    if slot:
        generator_contract["template_slots"] = {"stem": slot}

    display_name = f"{task} / anchor bootstrap"
    spec = enrich_spec_generator_contract(
        {
            "problem_type_id": pt_id,
            "skill_id": skill_id,
            "target_task": task,
            "task_family": task_family,
            "display_name": display_name,
            "answer_format_hint": hint or None,
            "source_example_ids": [],
            "answer_contract": ac,
            "stem_contract": {
                "stem_must_not_embed_choices": True,
                "allowed_math_objects": math_objects,
                "required_math_objects": math_objects,
                "forbidden_patterns": [r"\(A\)", r"\(B\)", r"\(C\)", r"\(D\)"],
            },
            "dependency_contract": {
                "givens_must_be_used": True,
                "target_answer_must_depend_on_givens": True,
                "variables_in_conditions_must_appear_in_target": False,
            },
            "semantic_contract": {
                "reasoning_type": [task],
                "reject_if": [
                    "unused_condition",
                    "ambiguous_answer",
                    "answer_not_derivable",
                ],
            },
            "generator_contract": generator_contract,
            "validator_contract": {
                "static_checks": ["answer_contract_checks"],
                "semantic_checks": ["givens_to_target_dependency"],
                "runtime_smoke_count": 30,
            },
            "spec_source": "anchor_slot_bootstrap",
            "grouping_reason": "anchor_subskill_bootstrap_zero_source",
            "feature_signature": ["anchor_slot_bootstrap", task],
        }
    )
    return enrich_spec_with_canonicalization(spec)


def _candidate_from_bootstrap_spec(
    spec: dict[str, Any],
    *,
    fallback_subskill_id: str,
) -> dict[str, Any]:
    from core.gencode.problem_type_canonicalizer import (
        evaluate_typed_prefix_readiness,
        is_phase3_packaging_allowed,
    )
    from core.gencode.spec_phase1_merge import slot_generator_readiness
    from core.gencode.task_families import answer_contract_supports_task

    pt = str(spec.get("problem_type_id", "")).strip()
    ac_proposal = dict(spec.get("answer_contract", {}) if isinstance(spec.get("answer_contract"), dict) else {})
    legacy = legacy_fields_from_answer_contract(ac_proposal)
    checker_cap = validate_answer_contract_capability(ac_proposal)
    ac_proposal.update(
        {
            "checker_key": legacy["checker_key"],
            "equivalence_type": legacy["equivalence_type"],
            "answer_shape": legacy.get("answer_shape", ""),
            "selected_checker": legacy.get("selected_checker", legacy["checker_key"]),
            "checker_capability_status": checker_cap.get("checker_capability_status", "ok"),
            "checker_contract_blockers": checker_cap.get("checker_contract_blockers", []),
            "checker_contract_warnings": checker_cap.get("checker_contract_warnings", []),
            "stem_contract": spec.get("stem_contract"),
            "dependency_contract": spec.get("dependency_contract"),
            "semantic_contract": spec.get("semantic_contract"),
            "generator_contract": spec.get("generator_contract"),
            "validator_contract": spec.get("validator_contract"),
        }
    )
    answer_shape = str(ac_proposal.get("answer_shape", "")).strip() or detect_answer_shape(ac_proposal)
    readiness, usable_for_phase3, canonical_blockers = evaluate_typed_prefix_readiness(spec)
    if readiness not in {"runtime_ready", "runtime_ready_with_warning"}:
        legacy_readiness = slot_generator_readiness(spec)
        if legacy_readiness in {"runtime_ready", "runtime_ready_with_warning"}:
            readiness = legacy_readiness
            usable_for_phase3 = True
    contract_ok, contract_blockers = answer_contract_supports_task(spec)
    if canonical_blockers:
        contract_blockers = sorted(set(list(contract_blockers) + list(canonical_blockers)))
    if checker_cap.get("checker_capability_status") == "blocked":
        readiness = "answer_contract_not_supported"
        usable_for_phase3 = False
    elif not contract_ok:
        readiness = "answer_contract_not_supported"
        usable_for_phase3 = False
    if not is_phase3_packaging_allowed(readiness, usable_for_phase3):
        usable_for_phase3 = False

    cand_target = str(spec.get("target_task", "")).strip()
    cand_family = str(spec.get("task_family", "")).strip() or task_family_for_task(cand_target)
    return {
        "problem_type_id": pt,
        "proposed_problem_type_id": pt,
        "display_name": spec.get("display_name", ""),
        "matched_example_ids": [],
        "matched_example_count": 0,
        "unmatched_example_ids": [],
        "representative_example_id": None,
        "structural_features": [answer_shape] if answer_shape else [],
        "answer_contract_proposal": ac_proposal,
        "checker_key_proposal": legacy["checker_key"],
        "equivalence_type_proposal": legacy["equivalence_type"],
        "answer_shape": answer_shape,
        "answer_semantics": str(ac_proposal.get("answer_semantics", ac_proposal.get("answer_shape", ""))),
        "presentation_mode": str(ac_proposal.get("presentation_mode", "short_answer")),
        "source_has_choices": bool(ac_proposal.get("source_has_choices")),
        "selected_checker": str(ac_proposal.get("selected_checker", legacy["checker_key"])),
        "checker_selection_reason": str(
            ac_proposal.get("checker_selection_reason")
            or checker_selection_reason(
                answer_type=str(ac_proposal.get("answer_type", "")),
                target_task=cand_target,
                task_family=cand_family,
                has_choices=bool(ac_proposal.get("source_has_choices")),
                answer_shape=str(ac_proposal.get("answer_shape", "")),
            )
        ),
        "confidence": "medium",
        "promote_recommendation": "recommend_promote_for_that_candidate",
        "promote_blockers": [] if usable_for_phase3 else ["anchor_bootstrap_not_runtime_ready"],
        "risk_flags": ["anchor_slot_bootstrap_zero_source"],
        "checker_contract_warnings": checker_cap.get("checker_contract_warnings", []),
        "spec_source": "anchor_slot_bootstrap",
        "grouping_reason": spec.get("grouping_reason", ""),
        "feature_signature": spec.get("feature_signature", []),
        "problem_type_spec_draft": spec,
        "generator_readiness": readiness,
        "usable_for_phase3": usable_for_phase3,
        "template_slot": get_template_slot(spec) or spec.get("_resolved_template_slot", ""),
        "canonical_base_problem_type_id": spec.get("canonical_base_problem_type_id", ""),
        "value_type_prefix": spec.get("value_type_prefix", ""),
        "subskill_id": cand_target or fallback_subskill_id,
    }


def bootstrap_anchor_subskill_candidates(
    skill_id: str,
    main_skill_anchor: dict[str, Any],
    induced_specs: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    existing_ids: set[str],
    *,
    fallback_subskill_id: str = "same_as_main_skill",
) -> dict[str, Any]:
    """Add induced specs + candidates for anchor subskills missing from source clustering."""
    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else {}
    expected = [
        str(t).strip()
        for t in (anchor.get("expected_subskill_candidates") or [])
        if str(t).strip() and not str(t).endswith("_family")
    ]
    observed_tasks = {
        str(s.get("target_task", "")).strip()
        for s in induced_specs
        if isinstance(s, dict) and str(s.get("target_task", "")).strip()
    }
    observed_slots = {
        str(get_template_slot(s) or s.get("_resolved_template_slot") or "").strip()
        for s in induced_specs
        if isinstance(s, dict)
    }
    candidate_ids = {
        str(c.get("problem_type_id", "")).strip()
        for c in candidates
        if isinstance(c, dict) and str(c.get("problem_type_id", "")).strip()
    }

    bootstrapped: list[str] = []
    skipped: list[dict[str, str]] = []

    for task in expected:
        if task in observed_tasks:
            skipped.append({"task": task, "reason": "already_induced_from_source"})
            continue
        alias = _ANCHOR_TASK_SLOT_ALIASES.get(task, "")
        if alias and alias in observed_tasks:
            skipped.append({"task": task, "reason": f"slot_alias_covered_by:{alias}"})
            continue
        slot = TASK_FAMILY_TO_SLOT.get(task, task)
        if slot and slot in observed_slots and task not in observed_slots:
            skipped.append({"task": task, "reason": f"slot_already_covered:{slot}"})
            continue
        if task in candidate_ids:
            skipped.append({"task": task, "reason": "already_in_candidates"})
            continue

        spec = _build_anchor_bootstrap_spec(skill_id, task, existing_ids=existing_ids)
        if spec is None:
            skipped.append({"task": task, "reason": "no_registered_slot_generator"})
            continue

        pt = str(spec.get("problem_type_id", "")).strip()
        if pt in candidate_ids:
            skipped.append({"task": task, "reason": "duplicate_problem_type_id"})
            continue

        induced_specs.append(spec)
        observed_tasks.add(task)
        resolved_slot = str(get_template_slot(spec) or spec.get("_resolved_template_slot") or slot or "").strip()
        if resolved_slot:
            observed_slots.add(resolved_slot)

        candidate = _candidate_from_bootstrap_spec(spec, fallback_subskill_id=fallback_subskill_id)
        candidates.append(candidate)
        candidate_ids.add(pt)
        bootstrapped.append(task)

    return {
        "bootstrapped_tasks": bootstrapped,
        "bootstrapped_count": len(bootstrapped),
        "skipped_tasks": skipped,
    }
