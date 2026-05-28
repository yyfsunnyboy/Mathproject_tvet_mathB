from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from core.gencode.answer_contract_bridge import legacy_fields_from_answer_contract
from core.gencode.classifier_proposal import detect_answer_shape
from core.gencode.example_feature_extractor import extract_example_feature
from core.gencode.pipeline_policy import evaluate_pipeline_gates
from core.gencode.problem_type_spec import get_template_slot, list_problem_types_for_skill
from core.gencode.spec_phase1_merge import slot_generator_readiness

_DISPLAY_NAME = {
    ("short_answer", "classify_quadrant"): "象限判斷短答",
    ("single_choice", "choose_correct_statement"): "象限敘述選擇",
    ("single_choice", "choose_possible_coordinate"): "座標選擇",
}


def _primary_math_objects(math_objects: list[str]) -> tuple[str, ...]:
    priority = [
        "axis_distance",
        "symbolic_condition",
        "coordinate_point",
        "expression",
        "probability_context",
        "combinatorics_context",
        "statistics_context",
        "graph",
        "table",
    ]
    ordered = [m for m in priority if m in math_objects]
    for m in math_objects:
        if m not in ordered:
            ordered.append(m)
    return tuple(ordered[:2]) if ordered else tuple()


def _feature_signature(feat: dict[str, Any]) -> tuple[Any, ...]:
    return (
        str(feat.get("answer_type", "")).strip(),
        str(feat.get("target_task", "")).strip(),
        tuple(feat.get("reasoning_type", []) if isinstance(feat.get("reasoning_type"), list) else []),
        _primary_math_objects(list(feat.get("math_objects", []) or [])),
    )


def _compatible_target_tasks(tasks: set[str]) -> bool:
    if len(tasks) <= 1:
        return True
    choice_like = {"choose_correct_statement", "choose_possible_coordinate", "classify_quadrant"}
    if tasks.issubset(choice_like):
        return True
    return False


def _cluster_features(features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_answer: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for f in features:
        by_answer[str(f.get("answer_type", "")).strip()].append(f)

    clusters: list[dict[str, Any]] = []
    for answer_type, group in sorted(by_answer.items()):
        sub: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
        for f in group:
            sig = _feature_signature(f)
            sub[sig].append(f)

        if len(sub) == 1:
            for sig, items in sub.items():
                clusters.append({"answer_type": answer_type, "features": items, "signature": sig, "merge_reason": "single_signature_group"})
            continue

        quadrant_short = answer_type == "short_answer" and all(
            str(f.get("target_task", "")).strip() == "classify_quadrant" for f in group
        )
        if quadrant_short and len(sub) > 1:
            clusters.append(
                {
                    "answer_type": answer_type,
                    "features": group,
                    "signature": ("merged_short_answer_quadrant", answer_type),
                    "merge_reason": "merged_short_answer_quadrant_sign_reasoning",
                }
            )
            continue

        tasks = {str(f.get("target_task", "")).strip() for f in group}
        if _compatible_target_tasks(tasks) and answer_type == "single_choice":
            clusters.append(
                {
                    "answer_type": answer_type,
                    "features": group,
                    "signature": ("merged_single_choice", answer_type, tuple(sorted(tasks))),
                    "merge_reason": "merged_compatible_single_choice_tasks_with_template_families",
                }
            )
            continue

        for sig, items in sub.items():
            clusters.append(
                {
                    "answer_type": answer_type,
                    "features": items,
                    "signature": sig,
                    "merge_reason": "split_by_feature_signature",
                }
            )
    return clusters


def _slugify_problem_type_id(answer_type: str, target_task: str, math_objects: tuple[str, ...]) -> str:
    parts = [answer_type]
    if target_task:
        parts.append(target_task)
    for m in math_objects[:2]:
        parts.append(m.replace("_context", ""))
    base = "_".join(p for p in parts if p)
    base = re.sub(r"_+", "_", base).strip("_")
    return base[:80] or f"{answer_type}_general"


def _infer_template_slot(answer_type: str, target_task: str, math_objects: list[str]) -> str:
    if answer_type == "short_answer":
        if "symbolic_condition" in math_objects:
            return "symbolic_quadrant"
        if "coordinate_point" in math_objects:
            return "point_quadrant"
        return "point_quadrant"
    if answer_type == "single_choice":
        if target_task == "choose_possible_coordinate" or "axis_distance" in math_objects:
            return "axis_distance_choice"
        if target_task == "choose_correct_statement":
            return "symbolic_quadrant_statement_choice"
        if "symbolic_condition" in math_objects:
            return "symbolic_quadrant_choice"
        return "point_quadrant_choice"
    return ""


def _build_answer_contract(answer_type: str) -> dict[str, Any]:
    if answer_type == "single_choice":
        return {
            "answer_type": "single_choice",
            "choices_required": True,
            "choice_count": 4,
            "correct_choice_count": 1,
            "answer_equivalence": "choice_label",
            "frontend_render_choices": True,
        }
    if answer_type == "numeric":
        return {
            "answer_type": "numeric",
            "choices_required": False,
            "choice_count": None,
            "correct_choice_count": None,
            "answer_equivalence": "numeric_equal",
            "frontend_render_choices": False,
        }
    return {
        "answer_type": "short_answer",
        "choices_required": False,
        "choice_count": None,
        "correct_choice_count": None,
        "answer_equivalence": "exact_text",
        "frontend_render_choices": False,
    }


def _build_problem_type_spec_draft(skill_id: str, cluster: dict[str, Any], existing_ids: set[str]) -> dict[str, Any]:
    features: list[dict[str, Any]] = list(cluster.get("features") or [])
    answer_type = str(cluster.get("answer_type", "")).strip()
    tasks = sorted({str(f.get("target_task", "")).strip() for f in features if str(f.get("target_task", "")).strip()})
    math_union: list[str] = []
    for f in features:
        for m in f.get("math_objects", []) or []:
            if m not in math_union:
                math_union.append(m)
    primary_math = _primary_math_objects(math_union)
    target_task = tasks[0] if len(tasks) == 1 else "multi_task"
    pt_id = _slugify_problem_type_id(answer_type, target_task if target_task != "multi_task" else tasks[0], primary_math)
    suffix = 2
    original = pt_id
    while pt_id in existing_ids:
        pt_id = f"{original}_{suffix}"
        suffix += 1
    existing_ids.add(pt_id)

    reasoning_union: list[str] = []
    for f in features:
        for r in f.get("reasoning_type", []) or []:
            if r not in reasoning_union:
                reasoning_union.append(r)

    template_families = tasks if len(tasks) > 1 else [target_task]
    slot = _infer_template_slot(answer_type, target_task if target_task != "multi_task" else (tasks[0] if tasks else ""), math_union)
    ac = _build_answer_contract(answer_type)
    legacy = legacy_fields_from_answer_contract(ac)
    display_key = (answer_type, tasks[0] if tasks else target_task)
    display_name = _DISPLAY_NAME.get(display_key, f"{answer_type} / {target_task}")

    generator_contract: dict[str, Any] = {
        "template_families": template_families,
        "parameter_slots": {"seed": "integer", "difficulty": "easy"},
        "randomization_rules": {"shuffle_choices": answer_type == "single_choice"},
        "avoid_llm_freeform_math": True,
        "use_domain_functions": True,
        "derivation_steps_required": True,
    }
    if slot:
        generator_contract["template_slots"] = {"stem": slot}

    spec = {
        "problem_type_id": pt_id,
        "skill_id": skill_id,
        "display_name": display_name,
        "source_example_ids": sorted(
            {int(f.get("source_example_id")) for f in features if isinstance(f.get("source_example_id"), int)}
        ),
        "answer_contract": ac,
        "stem_contract": {
            "stem_must_not_embed_choices": True,
            "allowed_math_objects": math_union,
            "required_math_objects": list(primary_math),
            "forbidden_patterns": ["\\(A\\)", "\\(B\\)", "\\(C\\)", "\\(D\\)"],
        },
        "dependency_contract": {
            "givens_must_be_used": True,
            "target_answer_must_depend_on_givens": True,
            "variables_in_conditions_must_appear_in_target": "symbolic_condition" in math_union,
        },
        "semantic_contract": {
            "reasoning_type": reasoning_union,
            "reject_if": [
                "unused_condition",
                "ambiguous_answer",
                "answer_not_derivable",
                "duplicated_choices",
                "no_correct_choice",
                "multiple_correct_choices_when_single_choice",
            ],
        },
        "generator_contract": generator_contract,
        "validator_contract": {
            "static_checks": ["answer_contract_checks", "choices_policy"],
            "semantic_checks": ["givens_to_target_dependency"],
            "runtime_smoke_count": 30,
        },
        "spec_source": "phase1_induced_draft",
        "grouping_reason": str(cluster.get("merge_reason", "")),
        "feature_signature": list(cluster.get("signature", ())),
    }
    return spec, legacy


def induce_problem_types_from_examples(skill_id: str, examples: list[dict[str, Any]]) -> dict[str, Any]:
    features = [extract_example_feature(ex) for ex in examples if isinstance(ex, dict)]
    clusters = _cluster_features(features)
    existing_ids = {str(s.get("problem_type_id", "")).strip() for s in list_problem_types_for_skill(skill_id)}
    induced_specs: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    per_example: list[dict[str, Any]] = []

    cluster_by_ex: dict[int, str] = {}
    for cluster in clusters:
        spec, legacy = _build_problem_type_spec_draft(skill_id, cluster, existing_ids)
        induced_specs.append(spec)
        pt = spec["problem_type_id"]
        ex_ids = spec.get("source_example_ids", [])
        for ex_id in ex_ids:
            if isinstance(ex_id, int):
                cluster_by_ex[ex_id] = pt
        ac_proposal = dict(spec.get("answer_contract", {}))
        ac_proposal.update(
            {
                "checker_key": legacy["checker_key"],
                "equivalence_type": legacy["equivalence_type"],
                "stem_contract": spec.get("stem_contract"),
                "dependency_contract": spec.get("dependency_contract"),
                "semantic_contract": spec.get("semantic_contract"),
                "generator_contract": spec.get("generator_contract"),
                "validator_contract": spec.get("validator_contract"),
            }
        )
        answer_shape = detect_answer_shape(ac_proposal)
        readiness = slot_generator_readiness(spec)
        candidates.append(
            {
                "problem_type_id": pt,
                "proposed_problem_type_id": pt,
                "display_name": spec.get("display_name", ""),
                "matched_example_ids": ex_ids,
                "matched_example_count": len(ex_ids),
                "unmatched_example_ids": [],
                "representative_example_id": ex_ids[0] if ex_ids else None,
                "structural_features": [answer_shape],
                "answer_contract_proposal": ac_proposal,
                "checker_key_proposal": legacy["checker_key"],
                "equivalence_type_proposal": legacy["equivalence_type"],
                "answer_shape": answer_shape,
                "confidence": "high",
                "promote_recommendation": "recommend_promote_for_that_candidate",
                "promote_blockers": [],
                "risk_flags": [],
                "spec_source": "phase1_induced_draft",
                "grouping_reason": spec.get("grouping_reason", ""),
                "feature_signature": spec.get("feature_signature", []),
                "problem_type_spec_draft": spec,
                "generator_readiness": readiness,
                "template_slot": get_template_slot(spec),
            }
        )

    for f in features:
        ex_id = f.get("source_example_id")
        pt = cluster_by_ex.get(ex_id, "unknown")
        per_example.append(
            {
                "example_id": ex_id,
                "detected_problem_type_id": pt,
                "example_feature": f,
                "answer_shape": f.get("answer_shape", ""),
                "classification_confidence": "high" if pt != "unknown" else "low",
                "classification_reason": "feature_signature_induction",
                "risk_flags": ["stem_embeds_choices"] if f.get("stem_embeds_choices") else [],
            }
        )

    gates = evaluate_pipeline_gates(
        candidates,
        source_examples_count=len(examples),
        checker_smoke_passed=False,
        dynamic_sampling_passed=False,
        contract_tests_passed=True,
    )
    ex_gate = gates.get("exception_review_gate", {}) if isinstance(gates.get("exception_review_gate"), dict) else {}
    ex_reasons = [r for r in (ex_gate.get("reasons") or []) if str(r) not in {"runtime_smoke_failed", "dynamic_sampling_failed"}]
    ex_gate["reasons"] = ex_reasons
    ex_gate["required"] = bool(ex_reasons)
    gates["exception_review_gate"] = ex_gate

    return {
        "skill_id": skill_id,
        "spec_mode": "induce_from_sources",
        "example_features": features,
        "induction_clusters": [
            {
                "grouping_reason": c.get("merge_reason"),
                "feature_signature": list(c.get("signature", ())),
                "source_example_ids": sorted(
                    {int(f.get("source_example_id")) for f in c.get("features", []) if isinstance(f.get("source_example_id"), int)}
                ),
                "answer_type": c.get("answer_type"),
            }
            for c in clusters
        ],
        "induced_problem_type_specs": induced_specs,
        "candidate_problem_types": candidates,
        "per_example_classification": per_example,
        "split_or_merge_recommendation": "induced_from_source_features",
        "problem_type_spec_first": True,
        "spec_defined_problem_type_ids": [s["problem_type_id"] for s in induced_specs],
        **gates,
        "next_action": "phase2_generate_from_induced_specs",
    }


def apply_spec_mode(
    skill_id: str,
    induced: dict[str, Any],
    legacy_auto_review: dict[str, Any],
    entries: list[dict[str, Any]],
    spec_mode: str,
) -> dict[str, Any]:
    mode = str(spec_mode or "induce_from_sources").strip()
    curated = list_problem_types_for_skill(skill_id)

    if mode == "induce_from_sources" or not curated:
        out = dict(induced)
        out["spec_mode"] = mode
        out["curated_specs_available"] = bool(curated)
        return out

    if mode == "curated_first":
        from core.gencode.spec_phase1_merge import merge_phase1_with_problem_type_specs

        merged = merge_phase1_with_problem_type_specs(skill_id, legacy_auto_review, entries)
        if merged:
            merged["spec_mode"] = mode
            merged["induction_comparison"] = {"induced_count": len(induced.get("candidate_problem_types", []))}
            return merged
        out = dict(induced)
        out["spec_mode"] = mode
        return out

    # hybrid: induced primary, annotate curated diff
    out = dict(induced)
    out["spec_mode"] = mode
    out["curated_specs_available"] = bool(curated)
    curated_ids = {str(s.get("problem_type_id", "")) for s in curated}
    induced_ids = {str(c.get("problem_type_id", "")) for c in induced.get("candidate_problem_types", []) if isinstance(c, dict)}
    out["hybrid_diff"] = {
        "only_in_curated": sorted(curated_ids - induced_ids),
        "only_in_induced": sorted(induced_ids - curated_ids),
        "overlap": sorted(curated_ids & induced_ids),
    }
    return out
