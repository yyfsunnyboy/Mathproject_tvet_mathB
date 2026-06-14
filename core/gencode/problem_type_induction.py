from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from core.gencode.answer_contract_bridge import legacy_fields_from_answer_contract
from core.gencode.answer_contract_policy import (
    checker_selection_reason,
    infer_answer_contract_from_problem_context,
    is_coordinate_pair_semantic,
    is_quadratic_rational_scalar_semantic,
    _answers_suggest_rational,
    _answers_suggest_numeric_only,
    presentation_mode_for_features,
)
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.classifier_proposal import detect_answer_shape
from core.gencode.classification_policy import (
    apply_final_classification_to_features,
    build_classification_diagnostic,
    build_classified_example_feature,
    uses_ai_first_classification,
)
from core.gencode.source_structure_context import (
    classification_sort_key,
    enrich_examples_with_structure_context,
    update_structure_report,
)
from core.gencode.example_feature_extractor import extract_example_feature, extract_example_feature_rule_only
from core.gencode.example_feature_extractor import _detect_math_objects
from core.gencode.generator_contract_schema import enrich_spec_generator_contract
from core.gencode.pipeline_policy import evaluate_pipeline_gates
from core.gencode.problem_type_spec import get_template_slot, list_problem_types_for_skill
from core.gencode.main_skill_anchor import build_main_skill_anchor
from core.gencode.semantic_alignment import (
    apply_alignment_gate_to_candidates,
    build_source_example_alignment_report,
    evaluate_semantic_alignment,
    evaluate_source_example_alignment,
    extract_skill_terms,
    load_skill_metadata_from_db,
    merge_alignment_into_gates,
)
from core.gencode.task_families import DIVISION_POINT_COORDINATES_FAMILY
from core.gencode.induction_source_policy import (
    annotate_features_with_induction_tier,
    split_induction_source_features,
)
from core.gencode.phase1_anchor_contract import phase1_enforcement_assertion_block
from core.gencode.spec_phase1_merge import slot_generator_readiness
from core.gencode.answer_contract_gate import apply_runtime_gate_to_candidate
from core.gencode.task_families import (
    QUADRATIC_INEQUALITY_FAMILY,
    QUADRATIC_INEQUALITY_TASKS,
    SOLVE_UNKNOWN_COORDINATE_TASKS,
    answer_contract_supports_task,
    task_family_for_task,
)


def _load_human_confirmed_rulepack(skill_id: str) -> dict[str, Any] | None:
    """Source Skill Binding Supremacy §7: load human_confirmed rule pack for a skill.

    Returns the rule pack entry dict if one with ``classifier_source: human_confirmed``
    exists for *skill_id*, otherwise returns None.
    """
    import yaml
    from pathlib import Path

    rulepack_path = Path(__file__).resolve().parents[2] / "configs" / "gencode" / "classifiers" / "phase1_rule_packs.yaml"
    if not rulepack_path.exists():
        return None
    try:
        with rulepack_path.open("r", encoding="utf-8") as fh:
            root = yaml.safe_load(fh) or []
    except Exception:
        return None
    if not isinstance(root, list):
        return None
    sid = str(skill_id or "").strip()
    for item in root:
        if not isinstance(item, dict):
            continue
        if str(item.get("skill_id", "")).strip() == sid:
            if str(item.get("classifier_source", "")).strip() == "human_confirmed":
                return item
    return None

_DISPLAY_NAME = {
    ("short_answer", "classify_quadrant"): "象限判斷短答",
    ("short_answer", "solve_unknown_coordinate_from_two_point_distance"): "兩點距離反求座標",
    ("short_answer", "compute_distance_between_two_points"): "兩點距離計算",
    ("short_answer", "compute_centroid_coordinates"): "三角形重心坐標",
    ("short_answer", "compute_midpoint_coordinates"): "兩點中點坐標",
    ("short_answer", "compute_internal_division_point_coordinates"): "內分點坐標",
    ("short_answer", "compute_external_division_point_coordinates"): "外分點坐標",
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


def _cluster_answer_type_key(feat: dict[str, Any]) -> str:
    """Strategy A: MCQ presentation splits from ordered_pair short-answer clusters."""
    at = str(feat.get("answer_type", "")).strip()
    if at in {"ordered_pair", "coordinate_pair"} and feat.get("has_choices"):
        return "single_choice"
    return at


def _presentation_mode_for_feature(feat: dict[str, Any]) -> str:
    at = str(feat.get("answer_type", "")).strip()
    if at == "single_choice" or feat.get("has_choices"):
        return "single_choice"
    return "short_answer"


def _feature_signature(feat: dict[str, Any]) -> tuple[Any, ...]:
    return (
        _cluster_answer_type_key(feat),
        str(feat.get("target_task", "")).strip(),
        _presentation_mode_for_feature(feat),
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
        by_answer[_cluster_answer_type_key(f)].append(f)

    clusters: list[dict[str, Any]] = []
    for answer_type, group in sorted(by_answer.items()):
        group = [g for g in group if isinstance(g, dict) and not g.get("source_quality_reject")]
        if not group:
            continue
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


def _slugify_problem_type_id(
    answer_type: str,
    target_task: str,
    math_objects: tuple[str, ...],
    *,
    presentation_mode: str = "",
) -> str:
    parts = [answer_type]
    if target_task:
        parts.append(target_task)
    if presentation_mode and presentation_mode not in {answer_type, ""}:
        parts.append(presentation_mode)
    for m in math_objects[:2]:
        parts.append(m.replace("_context", ""))
    base = "_".join(p for p in parts if p)
    base = re.sub(r"_+", "_", base).strip("_")
    return base[:80] or f"{answer_type}_general"


def _canonical_problem_type_base(answer_type: str, target_task: str, presentation_mode: str = "") -> str:
    task = str(target_task or "").strip()
    if is_quadratic_rational_scalar_semantic(target_task=task) and str(presentation_mode or "").strip() != "single_choice":
        if str(answer_type or "").strip() == "rational":
            return f"rational_{task}"
        if str(answer_type or "").strip() == "integer":
            return f"integer_{task}"
        return task
    if task in {"compute_midpoint_coordinates", "compute_centroid_coordinates"}:
        mode = str(presentation_mode or "").strip()
        if mode in {"single_choice", "short_answer"}:
            return f"{mode}_{task}"
        return f"{answer_type}_{task}"
    if task:
        mode = str(presentation_mode or "").strip()
        if mode:
            return f"{answer_type}_{task}_{mode}"
        return f"{answer_type}_{task}"
    return ""


def _strip_value_prefix_for_semantic_problem_type(
    problem_type_id: str,
    *,
    target_task: str = "",
    presentation_mode: str = "",
    math_objects: list[str] | None = None,
) -> str:
    pt = str(problem_type_id or "").strip()
    if pt.startswith(("integer_", "rational_")):
        return pt
    task = str(target_task or "").strip()
    mode = str(presentation_mode or "").strip()
    value_prefixes = ("integer_", "numeric_", "rational_")
    base = pt
    for prefix in value_prefixes:
        if base.startswith(prefix):
            base = base[len(prefix):]
            break
    if base == pt:
        return pt
    if is_quadratic_rational_scalar_semantic(
        problem_type_id=base,
        target_task=task,
        math_objects=math_objects,
    ):
        return base
    if mode == "single_choice" and (
        task == "quadratic_graph_vertex_axis_choice"
        or base == "quadratic_graph_vertex_axis_choice"
    ):
        return base
    return pt


def _infer_template_slot(answer_type: str, target_task: str, math_objects: list[str]) -> str:
    if target_task == "quadratic_vertex_form_translation_to_new_function":
        return "quadratic_vertex_form_translation_to_new_function"
    if target_task == "compute_quadratic_vertex":
        return "quadratic_vertex_extremum_rational"
    if target_task == "quadratic_vertex_or_parameter_computation":
        return "quadratic_vertex_or_parameter_computation"
    if target_task == "quadratic_graph_translation_fill_blank":
        return "quadratic_graph_translation_fill_blank"
    if target_task == "quadratic_vertex_form_properties":
        return "quadratic_vertex_form_properties"
    if target_task == "quadratic_standard_to_vertex_properties":
        return "quadratic_standard_to_vertex_properties"
    if target_task in {"factor_quadratic_by_cross_multiplication", "solve_quadratic_by_factoring"}:
        return "factor_quadratic_by_cross_multiplication"
    if target_task in {"solve_quadratic_inequality", "interpret_quadratic_inequality_solution_set"}:
        return "solve_quadratic_inequality"
    if target_task == "solve_quadratic_inequality_special_cases":
        return "solve_quadratic_inequality_special_cases"
    if target_task == "solve_quadratic_inequality_parameter_range":
        return "solve_quadratic_inequality_parameter_range"
    if target_task == "reverse_quadratic_inequality_coefficients":
        return "reverse_quadratic_inequality_coefficients"
    if target_task == "applied_quadratic_inequality_problem":
        return "applied_quadratic_inequality_problem"
    if target_task == "interpret_function_notation":
        if answer_type == "single_choice":
            return "linear_function_two_point_choice"
        return "function_value_numeric"
    if target_task in {"contextual_application", "word_problem"}:
        return "linear_function_contextual_word_problem"
    if target_task == "evaluate_function_value" and answer_type in {"numeric", "short_answer"}:
        return "function_value_numeric"
    if target_task == "evaluate_function_value" and answer_type == "expression":
        return "linear_function_contextual_word_problem"
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


def _build_answer_contract(
    answer_type: str,
    cluster_features: list[dict[str, Any]] | None = None,
    *,
    target_task: str = "",
    task_family: str = "",
    math_objects: list[str] | None = None,
) -> dict[str, Any]:
    features = cluster_features or []
    has_choices = any(f.get("has_choices") for f in features if isinstance(f, dict))
    tasks = {str(f.get("target_task", "")).strip() for f in features if isinstance(f, dict)}
    resolved_task = str(target_task or (next(iter(tasks)) if len(tasks) == 1 else "")).strip()
    mos = list(math_objects or [])
    for f in features:
        if isinstance(f, dict):
            for m in f.get("math_objects", []) or []:
                if m not in mos:
                    mos.append(m)
    return infer_answer_contract_from_problem_context(
        answer_type=answer_type,
        target_task=resolved_task,
        task_family=task_family,
        math_objects=mos,
        cluster_features=features,
        has_choices=has_choices,
    )


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
    target_task = tasks[0] if len(tasks) == 1 else ("multi_task" if tasks else "")
    if not target_task and not tasks:
        target_task = "needs_review"
    presentation_mode = presentation_mode_for_features(answer_type, features)
    pt_id = _slugify_problem_type_id(
        answer_type,
        target_task if target_task not in {"multi_task", "needs_review", ""} else (tasks[0] if tasks else "needs_review"),
        primary_math,
        presentation_mode=presentation_mode if presentation_mode != answer_type else "",
    )
    resolved_target_task = target_task if target_task != "multi_task" else (tasks[0] if tasks else "")
    canonical = _canonical_problem_type_base(answer_type, resolved_target_task, presentation_mode=presentation_mode)
    if canonical:
        pt_id = canonical
        
    has_fallback = any("fallback_application" in str(f.get("problem_type_id", "")) for f in features)
    proxy_ids = sorted(
        {
            str(f.get("proxy_problem_type_id", "")).strip()
            for f in features
            if str(f.get("proxy_problem_type_id", "")).strip()
        }
    )
    if len(proxy_ids) == 1:
        pt_id = proxy_ids[0]
        canonical = ""
        has_fallback = True
    if has_fallback:
        pt_id = pt_id if len(proxy_ids) == 1 else f"{answer_type}_{resolved_target_task}_fallback_application"

    pt_id = _strip_value_prefix_for_semantic_problem_type(
        pt_id,
        target_task=resolved_target_task,
        presentation_mode=presentation_mode,
        math_objects=math_union,
    )
        
    suffix = 2
    original = pt_id
    if canonical:
        # Canonical ids should be stable across runs and can reuse existing catalog ids.
        pass
    else:
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
    slot = _infer_template_slot(answer_type, resolved_target_task, math_union)
    from core.gencode.division_point_slot_engine import DIVISION_POINT_SLOT, is_division_point_target_task

    if is_division_point_target_task(resolved_target_task):
        slot = DIVISION_POINT_SLOT
    task_family = task_family_for_task(resolved_target_task)
    ac = _build_answer_contract(
        answer_type,
        features,
        target_task=resolved_target_task,
        task_family=task_family,
        math_objects=math_union,
    )
    legacy = legacy_fields_from_answer_contract(ac)
    checker_key = str(legacy.get("checker_key", ac.get("checker_key", ac.get("checker", "")))).strip()
    cluster_has_rational_answers = _answers_suggest_rational(features)
    cluster_has_integer_only_answers = _answers_suggest_numeric_only(features)
    if resolved_target_task in {"compute_quadratic_vertex", "quadratic_vertex_or_parameter_computation"}:
        if cluster_has_rational_answers and not str(pt_id or "").startswith("rational_"):
            pt_id = f"rational_{resolved_target_task}"
        elif (
            checker_key == "integer_checker"
            and cluster_has_integer_only_answers
            and not cluster_has_rational_answers
            and not str(pt_id or "").startswith("integer_")
        ):
            pt_id = f"integer_{resolved_target_task}"

    # ── Infer answer_format_hint from Phase 1 cluster evidence ───────────────
    from core.gencode.answer_format_hint import (
        HINT_UNKNOWN,
        HINT_CHOICE,
        HINT_RATIONAL,
        infer_answer_format_hint,
        infer_answer_format_hint_from_answers,
        _HINT_TO_CONTRACT,
    )
    # Priority: source_has_choices flag → answer text samples → answer_type
    has_choices_in_cluster = any(
        f.get("has_choices") for f in features if isinstance(f, dict)
    )
    if has_choices_in_cluster:
        inferred_hint = HINT_CHOICE
    else:
        sample_answers: list[str] = [
            str(f.get("answer") or f.get("source_answer") or "").strip()
            for f in features if isinstance(f, dict)
            if str(f.get("answer") or f.get("source_answer") or "").strip()
        ]
        if cluster_has_rational_answers and resolved_target_task in {
            "compute_quadratic_vertex",
            "quadratic_vertex_or_parameter_computation",
        }:
            inferred_hint = HINT_RATIONAL
        elif is_quadratic_rational_scalar_semantic(
            problem_type_id=pt_id,
            target_task=resolved_target_task,
            task_family=task_family,
            math_objects=math_union,
        ) and not str(pt_id or "").strip().lower().startswith(("integer_", "rational_")):
            inferred_hint = HINT_RATIONAL
        elif str(pt_id or "").strip().lower().startswith("rational_"):
            inferred_hint = HINT_RATIONAL
        elif str(pt_id or "").strip().lower().startswith("integer_"):
            from core.gencode.answer_format_hint import HINT_INTEGER

            inferred_hint = HINT_INTEGER
        else:
            inferred_hint = infer_answer_format_hint_from_answers(sample_answers) if sample_answers \
                else infer_answer_format_hint({"answer_contract": ac})
    # Set answer_format_hint on ac so enrich_spec_with_canonicalization can use it
    if inferred_hint and inferred_hint != HINT_UNKNOWN:
        ac["source_has_choices"] = has_choices_in_cluster
        hint_template = _HINT_TO_CONTRACT.get(inferred_hint, {})
        if "answer_fields" in hint_template:
            ac["answer_fields"] = hint_template["answer_fields"]
        if "answer_separator" in hint_template:
            ac["answer_separator"] = hint_template["answer_separator"]
    elif has_choices_in_cluster:
        ac["source_has_choices"] = True
        inferred_hint = HINT_CHOICE
    # ─────────────────────────────────────────────────────────────────────────
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
    for f in features:
        sc = f.get("semantic_classification") if isinstance(f.get("semantic_classification"), dict) else {}
        scoped_gc = sc.get("selected_generator_contract")
        if isinstance(scoped_gc, dict) and scoped_gc:
            generator_contract = {**generator_contract, **scoped_gc}
            param_schema = sc.get("parameter_schema")
            if isinstance(param_schema, dict) and param_schema:
                generator_contract["parameter_schema"] = param_schema
            break
            
    if has_fallback:
        generator_contract["contextual_application"] = True
        
    if slot:
        generator_contract["template_slots"] = {"stem": slot}

    spec = enrich_spec_generator_contract(
        {
        "problem_type_id": pt_id,
        "skill_id": skill_id,
        "target_task": resolved_target_task,
        "task_family": task_family,
        "display_name": display_name,
        "answer_format_hint": inferred_hint if inferred_hint != HINT_UNKNOWN else None,
        "answer_fields": ac.get("answer_fields") or None,
        "answer_separator": ac.get("answer_separator") or None,
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
    )
    from core.gencode.problem_type_canonicalizer import enrich_spec_with_canonicalization

    spec = enrich_spec_with_canonicalization(spec)
    ac = spec.get("answer_contract") if isinstance(spec.get("answer_contract"), dict) else ac
    legacy = legacy_fields_from_answer_contract(ac)
    # Mark spec as canonicalized so _reinforce_canonical_answer_contract won't overwrite.
    # (canonical_base_problem_type_id is set by enrich_spec_with_canonicalization)
    return spec, legacy


def _cluster_contract_canonical_key(cluster: dict[str, Any]) -> tuple[Any, ...]:
    features: list[dict[str, Any]] = list(cluster.get("features") or [])
    answer_type = str(cluster.get("answer_type", "")).strip()
    tasks = sorted(
        {
            str(f.get("target_task", "")).strip()
            for f in features
            if isinstance(f, dict) and str(f.get("target_task", "")).strip()
        }
    )
    target_task = tasks[0] if len(tasks) == 1 else ("multi_task" if tasks else "")
    resolved_target_task = target_task if target_task != "multi_task" else (tasks[0] if tasks else "")
    presentation_mode = presentation_mode_for_features(answer_type, features)
    task_family = task_family_for_task(resolved_target_task)
    ac = _build_answer_contract(
        answer_type,
        features,
        target_task=resolved_target_task,
        task_family=task_family,
    )
    legacy = legacy_fields_from_answer_contract(ac)
    answer_shape = str(legacy.get("answer_shape", "")).strip() or detect_answer_shape(ac)
    template_families = tuple(tasks if len(tasks) > 1 else ([target_task] if target_task else []))
    return (
        resolved_target_task,
        answer_type,
        presentation_mode,
        str(legacy.get("checker_key", "")).strip(),
        str(legacy.get("equivalence_type", "")).strip(),
        answer_shape,
        template_families,
    )


def _canonicalize_induction_clusters(clusters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged_by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    ordered_keys: list[tuple[Any, ...]] = []
    for cluster in clusters:
        if not isinstance(cluster, dict):
            continue
        key = _cluster_contract_canonical_key(cluster)
        if key not in merged_by_key:
            merged_by_key[key] = {
                "answer_type": cluster.get("answer_type"),
                "features": list(cluster.get("features") or []),
                "signature": cluster.get("signature"),
                "merge_reason": cluster.get("merge_reason", ""),
            }
            ordered_keys.append(key)
            continue
        existing = merged_by_key[key]
        combined = list(existing.get("features") or []) + list(cluster.get("features") or [])
        by_exid: dict[Any, dict[str, Any]] = {}
        for f in combined:
            if not isinstance(f, dict):
                continue
            exid = f.get("source_example_id")
            if exid is None:
                exid = id(f)
            by_exid[exid] = f
        existing["features"] = list(by_exid.values())
        existing["merge_reason"] = "merged_by_canonical_contract"
        existing["signature"] = ("canonical_contract_merge", key[0], key[1], key[2])
    return [merged_by_key[k] for k in ordered_keys]


def _synthesize_orphan_problem_type_id(feat: dict[str, Any]) -> str:
    """Assign a deterministic problem_type_id for examples excluded from clustering."""
    if not isinstance(feat, dict):
        return ""
    target = str(feat.get("target_task", "")).strip()
    sem = feat.get("semantic_classification") if isinstance(feat.get("semantic_classification"), dict) else {}
    if not target or target in {"unknown", "needs_review", "same_as_main_skill"}:
        target = str(sem.get("final_target_task", "")).strip() or target
    if not target or target in {"unknown", "needs_review", "same_as_main_skill"}:
        return ""
    ans_type = _cluster_answer_type_key(feat)
    presentation = _presentation_mode_for_feature(feat)
    math_objs = list(feat.get("math_objects", []) or [])
    primary_math = _primary_math_objects(math_objs)
    canonical = _canonical_problem_type_base(ans_type, target, presentation_mode=presentation)
    pt_id = canonical or _slugify_problem_type_id(
        ans_type,
        target,
        primary_math,
        presentation_mode=presentation if presentation != ans_type else "",
    )
    if str(ac_checker := str(feat.get("checker_key", feat.get("checker", ""))).strip()) == "integer_checker":
        if not pt_id.startswith("integer_") and not _answers_suggest_rational([feat]):
            pt_id = f"integer_{target}"
    elif _answers_suggest_rational([feat]) and not pt_id.startswith("rational_"):
        if is_quadratic_rational_scalar_semantic(target_task=target, math_objects=math_objs):
            pt_id = f"rational_{target}"
    elif ans_type == "integer" and not pt_id.startswith("integer_"):
        if is_quadratic_rational_scalar_semantic(target_task=target, math_objects=math_objs) and not _answers_suggest_rational([feat]):
            pt_id = f"integer_{target}"
    return pt_id


def merge_unclassified_low_confidence_examples(
    features_for_induction: list[dict[str, Any]],
    excluded_source_examples: list[dict[str, Any]],
    features: list[dict[str, Any]],
    skill_id: str,
    main_skill_anchor: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    SOP v0.2: Rescues core examples that are classified as unclassified_low_confidence.
    Assigns them a fallback problem type ID format: [semantics_signature]_fallback_application.
    Appends them to features_for_induction.
    """
    still_excluded = []
    feat_by_id = {f.get("source_example_id"): f for f in features if isinstance(f.get("source_example_id"), int)}

    for row in excluded_source_examples:
        ex_id = row.get("example_id")
        reason = row.get("exclude_reason")
        is_core = row.get("induction_tier") == "core" or row.get("included_in_core_induction")

        if reason == "unclassified_low_confidence" and is_core and isinstance(ex_id, int) and ex_id in feat_by_id:
            feat = feat_by_id[ex_id]
            expected_families = set((main_skill_anchor or {}).get("expected_task_families") or [])
            observed_task = str(feat.get("target_task", "")).strip()
            if observed_task in QUADRATIC_INEQUALITY_TASKS:
                fallback_task = observed_task
            elif QUADRATIC_INEQUALITY_FAMILY in expected_families:
                text = str(feat.get("question_text") or feat.get("problem_text") or "")
                mos = feat.get("math_objects") if isinstance(feat.get("math_objects"), list) else []
                if "factoring_expression" in mos or re.search(r"十字交乘|因式分解", text, re.I):
                    fallback_task = "factor_quadratic_by_cross_multiplication"
                elif "inequality" in mos or re.search(r"不等式|inequality|[<>≤≥]", text, re.I):
                    fallback_task = "solve_quadratic_inequality"
                else:
                    fallback_task = "factor_quadratic_by_cross_multiplication"
            else:
                fallback_subskill = (main_skill_anchor.get("fallback_subskill") or {}) if isinstance(main_skill_anchor, dict) else {}
                fallback_task = fallback_subskill.get("subskill_id", "evaluate_function_value")
                if not fallback_task or fallback_task == "same_as_main_skill":
                    fallback_task = "evaluate_function_value"

            feat["target_task"] = fallback_task
            feat["target"] = fallback_task
            if not feat.get("task_family"):
                feat["task_family"] = task_family_for_task(fallback_task) or "function_concept_family"

            if isinstance(feat.get("semantic_classification"), dict):
                sc = feat["semantic_classification"]
                sc["final_target_task"] = fallback_task
                sc["final_task_family"] = feat["task_family"]
                sc["candidate_source"] = "fallback_application"
                sc["classifier_source"] = "fallback_application_induct"
                sc["requires_human_action"] = False

            ans_type = _cluster_answer_type_key(feat)
            sig_base = f"{ans_type}_{fallback_task}"
            if fallback_task in QUADRATIC_INEQUALITY_TASKS:
                fallback_pt_id = f"expression_{fallback_task}"
            else:
                fallback_pt_id = f"{sig_base}_fallback_application"
            feat["problem_type_id"] = fallback_pt_id
            feat["included_in_core_induction"] = True
            feat["induction_tier"] = "core"
            feat["source_quality_reject"] = False

            row["included_in_phase1"] = True
            row["aligned_with_skill"] = True
            row["exclude_reason"] = ""
            row["alignment_kind"] = "fallback_application"
            row["requires_human_action"] = False

            features_for_induction.append(feat)
        else:
            still_excluded.append(row)

    return features_for_induction, still_excluded


def _observed_target_task_for_clause45(
    feat: dict[str, Any],
    row: dict[str, Any],
    main_skill_anchor: dict[str, Any],
) -> str:
    sc = feat.get("semantic_classification") if isinstance(feat.get("semantic_classification"), dict) else {}
    fallback_subskill = (main_skill_anchor.get("fallback_subskill") or {}) if isinstance(main_skill_anchor, dict) else {}
    candidates = (
        sc.get("final_target_task"),
        feat.get("target_task"),
        row.get("target_task"),
        sc.get("rule_target_task"),
        sc.get("ai_target_task"),
        fallback_subskill.get("subskill_id"),
    )
    for candidate in candidates:
        task = str(candidate or "").strip()
        if task and task not in {"unknown", "needs_review", "same_as_main_skill", "compute_numeric"}:
            return task
    feat_task = str(feat.get("target_task", "")).strip()
    if feat_task in QUADRATIC_INEQUALITY_TASKS:
        return feat_task
    expected_families = set((main_skill_anchor or {}).get("expected_task_families") or [])
    if QUADRATIC_INEQUALITY_FAMILY in expected_families:
        mos = feat.get("math_objects") if isinstance(feat.get("math_objects"), list) else []
        text = str(feat.get("question_text") or feat.get("problem_text") or "")
        if "factoring_expression" in mos or re.search(r"十字交乘|因式分解", text, re.I):
            return "factor_quadratic_by_cross_multiplication"
        if "inequality" in mos or re.search(r"不等式|inequality|[<>≤≥]", text, re.I):
            return "solve_quadratic_inequality"
    return "contextual_application"


def apply_clause45_unclassified_exception_escalation(
    features_for_induction: list[dict[str, Any]],
    excluded_source_examples: list[dict[str, Any]],
    features: list[dict[str, Any]],
    *,
    main_skill_anchor: dict[str, Any],
    induction_source_report: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    core_example_count = int(induction_source_report.get("core_example_count", 0) or 0)
    if core_example_count <= 0 or features_for_induction:
        return features_for_induction, excluded_source_examples, {}

    feat_by_id = {f.get("source_example_id"): f for f in features if isinstance(f, dict) and isinstance(f.get("source_example_id"), int)}
    core_low_confidence_rows = [
        row
        for row in excluded_source_examples
        if isinstance(row, dict)
        and row.get("exclude_reason") == "unclassified_low_confidence"
        and (row.get("induction_tier") == "core" or row.get("included_in_core_induction") or row.get("example_id") in feat_by_id)
        and isinstance(row.get("example_id"), int)
        and row.get("example_id") in feat_by_id
    ]
    if not core_low_confidence_rows:
        return features_for_induction, excluded_source_examples, {}

    rescued_ids: set[int] = set()
    observed_tasks: list[str] = []
    # Source Skill Binding Supremacy §6: when scope is locked, generic fallback
    # tasks must NOT be promoted as usable Phase 3 problem types.
    scope_locked = bool((main_skill_anchor or {}).get("source_skill_scope_locked", False))
    _GENERIC_FALLBACK_TASKS = frozenset({
        "contextual_application", "generic_numeric", "generic_numeric_family",
        "fallback_contextual_application", "compute_numeric",
    })
    for row in core_low_confidence_rows:
        ex_id = row.get("example_id")
        feat = feat_by_id.get(ex_id)
        if not isinstance(feat, dict):
            continue
        observed_task = _observed_target_task_for_clause45(feat, row, main_skill_anchor)
        observed_tasks.append(observed_task)
        task_family = task_family_for_task(observed_task) or str(feat.get("task_family", "")).strip()

        # Source Skill Binding Supremacy §6: if scope is locked and the resolved
        # task is a generic fallback, produce skill_scoped_unresolved_problem_type
        # instead so Phase 3 cannot use it as a real generator.
        if scope_locked and (observed_task in _GENERIC_FALLBACK_TASKS or observed_task == "contextual_application"):
            proxy_problem_type_id = "skill_scoped_unresolved_problem_type"
            feat["generator_readiness"] = "pending_problem_type_induction"
            feat["usable_for_phase3"] = False
            feat["needs_rule_pack_or_slot_registration"] = True
        else:
            proxy_problem_type_id = re.sub(r"_+", "_", f"fallback_{observed_task}").strip("_")

        feat["target_task"] = observed_task
        feat["target"] = observed_task
        feat["task_family"] = task_family
        feat["problem_type_id"] = proxy_problem_type_id
        feat["proxy_problem_type_id"] = proxy_problem_type_id
        feat["included_in_core_induction"] = True
        feat["induction_tier"] = "core"
        feat["source_quality_reject"] = False

        sc = feat.get("semantic_classification") if isinstance(feat.get("semantic_classification"), dict) else {}
        if not isinstance(sc, dict):
            sc = {}
            feat["semantic_classification"] = sc
        sc["final_target_task"] = observed_task
        sc["final_task_family"] = task_family
        sc["candidate_source"] = "clause45_fallback_proxy"
        sc["classifier_source"] = "clause45_unclassified_exception"
        sc["requires_human_action"] = False

        row["target_task"] = observed_task
        row["task_family"] = task_family
        row["included_in_phase1"] = True
        row["aligned_with_skill"] = True
        row["exclude_reason"] = ""
        row["alignment_kind"] = "clause45_fallback_proxy"
        row["requires_human_action"] = False

        features_for_induction.append(feat)
        rescued_ids.add(int(ex_id))

    if not rescued_ids:
        return features_for_induction, excluded_source_examples, {}

    still_excluded = [
        row
        for row in excluded_source_examples
        if not (isinstance(row, dict) and isinstance(row.get("example_id"), int) and int(row.get("example_id")) in rescued_ids)
    ]
    task_counts = Counter(observed_tasks)
    # Determine whether any rescued examples were demoted to skill_scoped_unresolved.
    unresolved_ids = {
        int(feat_by_id[row.get("example_id")].get("source_example_id", row.get("example_id")))
        for row in core_low_confidence_rows
        if isinstance(row, dict)
        and isinstance(row.get("example_id"), int)
        and row.get("example_id") in feat_by_id
        and feat_by_id[row.get("example_id")].get("problem_type_id") == "skill_scoped_unresolved_problem_type"
    } if scope_locked else set()
    report = {
        "clause45_escalation_applied": True,
        "clause45_rescued_example_ids": sorted(rescued_ids),
        "clause45_observed_target_task_distribution": dict(task_counts),
        "clause45_proxy_problem_type_ids": sorted({f"fallback_{task}" for task in task_counts if task}),
        "clause45_source_skill_scope_locked": scope_locked,
        "clause45_skill_scoped_unresolved_example_ids": sorted(unresolved_ids),
    }
    return features_for_induction, still_excluded, report


def _spec_in_expected_families(spec: dict[str, Any], expected_families: set[str]) -> bool:
    if not expected_families:
        return True
    fam = str(spec.get("task_family", "")).strip() or task_family_for_task(str(spec.get("target_task", "")))
    return fam in expected_families


COMBINATORICS_PROBABILITY_KEYWORDS = ("排列", "組合", "機率")
COMBINATORICS_PROBABILITY_DIAGNOSIS_TAGS = (
    "p_c_confusion",
    "sample_space_error",
    "double_counting",
    "denominator_error",
)


def _inject_combinatorics_probability_diagnosis_tags(induced: dict[str, Any], skill_id: str) -> None:
    """SOP v0.3.2 條款 3.6：語意關鍵字驅動之高職數B四大經典診斷標籤剛性注入。"""
    sid_str = str(skill_id or "").strip()
    is_combinatorics_or_prob = any(k in sid_str for k in COMBINATORICS_PROBABILITY_KEYWORDS)
    if not is_combinatorics_or_prob:
        return

    diagnosis_tags = list(COMBINATORICS_PROBABILITY_DIAGNOSIS_TAGS)

    # 1. 注入頂層屬性（保持大字典向後相容）
    induced["diagnosis_tags"] = diagnosis_tags

    # 2. 注入 subskills 子技能明細（不改變 subskills 原本的字串清單結構）
    if isinstance(induced.get("subskills"), list):
        induced.setdefault("subskills_detail", [])
        for sub in induced["subskills"]:
            sub_id = str(sub).strip()
            if not sub_id:
                continue
            induced["subskills_detail"].append(
                {
                    "subskill_id": sub_id,
                    "diagnosis_tags": diagnosis_tags,
                }
            )

    # 3. 注入每題分類候選，為 RAG 補救提供每題特徵
    if isinstance(induced.get("per_example_classification"), list):
        for row in induced["per_example_classification"]:
            if isinstance(row, dict):
                row["diagnosis_tag_candidates"] = diagnosis_tags


def induce_problem_types_from_examples(
    skill_id: str,
    examples: list[dict[str, Any]],
    *,
    spec_mode: str = "ai_first_induce_from_sources",
    main_skill_anchor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    skill_metadata = load_skill_metadata_from_db(skill_id)
    if isinstance(main_skill_anchor, dict) and str(main_skill_anchor.get("skill_id", "")).strip() == str(skill_id).strip():
        anchor = dict(main_skill_anchor)
    else:
        anchor = build_main_skill_anchor(skill_id, skill_metadata)
    anchor["classification_mandate"] = phase1_enforcement_assertion_block(anchor, include_anchor_fields=False)
    main_skill_anchor = anchor
    # Source Skill Binding Supremacy §7: check for human_confirmed rule pack.
    human_confirmed_pack = _load_human_confirmed_rulepack(skill_id)
    human_confirmed_rule_pack_applied = False
    if human_confirmed_pack is not None:
        human_confirmed_rule_pack_applied = True
        # If single_primary_problem_type flag set, pin spec_mode to rule-first
        # so AI cannot overwrite the human_confirmed classification.
        if human_confirmed_pack.get("single_primary_problem_type"):
            spec_mode = "rule_first_induce_from_sources"
    expected_families = set(main_skill_anchor.get("expected_task_families") or [])
    expected_subskills = {
        t
        for t in (main_skill_anchor.get("expected_subskill_candidates") or [])
        if t and not str(t).endswith("_family")
    }
    fallback_subskill = (main_skill_anchor.get("fallback_subskill") or {}) if isinstance(main_skill_anchor, dict) else {}
    fallback_subskill_id = str(fallback_subskill.get("subskill_id", "same_as_main_skill")).strip() or "same_as_main_skill"
    enriched_examples, structure_report = enrich_examples_with_structure_context(
        [ex for ex in examples if isinstance(ex, dict)]
    )
    enriched_examples.sort(key=classification_sort_key)
    semantic_classifications: list[dict[str, Any]] = []
    ai_semantic_status = "not_used"
    features: list[dict[str, Any]] = []
    classifications_by_id: dict[int, dict[str, Any]] = {}
    for ex in enriched_examples:
        if uses_ai_first_classification(spec_mode):
            feat, trace = build_classified_example_feature(
                ex,
                main_skill_anchor,
                spec_mode=spec_mode,
                classifications_by_id=classifications_by_id,
            )
            semantic_classifications.append({"example_id": feat.get("source_example_id"), **trace})
        else:
            feat, trace = build_classified_example_feature(
                ex,
                main_skill_anchor,
                spec_mode="rule_first_induce_from_sources",
                classifications_by_id=classifications_by_id,
            )
            semantic_classifications.append({"example_id": feat.get("source_example_id"), **trace})
        features.append(feat)
    structure_report = update_structure_report(structure_report, classifications=semantic_classifications)
    if uses_ai_first_classification(spec_mode):
        invalid_resp = sum(
            1
            for t in semantic_classifications
            if str(t.get("classifier_source", "")) == "ai_invalid_response_needs_review"
            or str(t.get("ai_semantic_status", "")) == "invalid_response"
        )
        unavailable = sum(1 for t in semantic_classifications if t.get("classifier_source") == "rule_fallback_ai_unavailable")
        if invalid_resp == len(semantic_classifications) and semantic_classifications:
            ai_semantic_status = "invalid_response"
        elif unavailable == len(semantic_classifications) and semantic_classifications:
            ai_semantic_status = "unavailable"
        elif invalid_resp and unavailable:
            ai_semantic_status = "partial_invalid_and_unavailable"
        elif invalid_resp:
            ai_semantic_status = "partial_invalid_response"
        elif unavailable:
            ai_semantic_status = "partial_unavailable"
        else:
            ai_semantic_status = "ok"
    features = apply_final_classification_to_features(features)
    # Recompute math_objects after final task is chosen to avoid stale rule-only objects.
    for feat in features:
        if not isinstance(feat, dict):
            continue
        txt = str(feat.get("question_text", "")).strip()
        task = str(feat.get("target_task", "")).strip()
        if txt and task:
            feat["math_objects"] = _detect_math_objects(txt, task)
    features = annotate_features_with_induction_tier(features, examples=examples)
    _core_features, induction_source_report = split_induction_source_features(features, examples=examples)
    rejected_source_examples: list[dict[str, Any]] = []
    source_quality_issues: list[dict[str, Any]] = []
    for f in features:
        if not isinstance(f, dict):
            continue
        if not f.get("source_quality_reject"):
            continue
        rejected_source_examples.append(
            {
                "example_id": f.get("source_example_id"),
                "reason": "source_quality_reject",
                "issues": list(f.get("source_quality_issues") or []),
            }
        )
        source_quality_issues.append(
            {
                "example_id": f.get("source_example_id"),
                "issues": list(f.get("source_quality_issues") or []),
            }
        )
    features_for_induction, excluded_source_examples = build_source_example_alignment_report(
        skill_id,
        skill_metadata,
        features,
        examples=examples,
        main_skill_anchor=main_skill_anchor,
    )
    clause45_report: dict[str, Any] = {}
    features_for_induction, excluded_source_examples, clause45_report = apply_clause45_unclassified_exception_escalation(
        features_for_induction,
        excluded_source_examples,
        features,
        main_skill_anchor=main_skill_anchor,
        induction_source_report=induction_source_report,
    )
    features_for_induction, excluded_source_examples = merge_unclassified_low_confidence_examples(
        features_for_induction,
        excluded_source_examples,
        features,
        skill_id,
        main_skill_anchor,
    )
    # Candidate-only examples (composite exercises) are tracked separately and must not pollute fallback buckets.
    candidate_only_examples = [
        f for f in features_for_induction
        if isinstance(f, dict) and bool(f.get("candidate_only"))
    ]
    stable_features_for_clusters = [
        f for f in features_for_induction
        if isinstance(f, dict) and not bool(f.get("candidate_only"))
    ]
    clusters = _canonicalize_induction_clusters(_cluster_features(stable_features_for_clusters))
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
        from core.gencode.problem_type_canonicalizer import (
            is_phase3_packaging_allowed,
            evaluate_typed_prefix_readiness,
        )
        readiness, usable_for_phase3, canonical_blockers = evaluate_typed_prefix_readiness(spec)
        if readiness != "runtime_ready" and readiness != "runtime_ready_with_warning":
            # Fallback to legacy readiness for non-canonicalizable paths
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
        # Source Skill Binding Supremacy §9: block Phase 3 for unresolved/generic fallback types.
        _UNRESOLVED_PT_PREFIXES = (
            "skill_scoped_unresolved",
            "pending_problem_type_induction",
        )
        _GENERIC_FALLBACK_PT_SUBSTRINGS = (
            "fallback_contextual_application",
            "contextual_application",
            "generic_numeric_family",
        )
        if any(pt.startswith(p) for p in _UNRESOLVED_PT_PREFIXES):
            readiness = "pending_problem_type_induction"
        elif bool(main_skill_anchor.get("source_skill_scope_locked")) and any(
            s in pt for s in _GENERIC_FALLBACK_PT_SUBSTRINGS
        ):
            readiness = "blocked_by_unresolved_skill_scoped_problem_type"
            usable_for_phase3 = False
        if not is_phase3_packaging_allowed(readiness, usable_for_phase3):
            usable_for_phase3 = False
        cand_target = str(spec.get("target_task", "")).strip()
        cand_family = str(spec.get("task_family", "")).strip() or task_family_for_task(cand_target)
        subskill_risk: list[str] = []
        if (
            expected_subskills
            and cand_target
            and cand_target not in expected_subskills
            and cand_family in expected_families
        ):
            scope = str(main_skill_anchor.get("skill_anchor_scope", "")).strip()
            if scope in {"medium", "broad"}:
                subskill_risk.append("same_family_extension")
            else:
                subskill_risk.append("subskill_mismatch_warning")
        coord_sem = is_coordinate_pair_semantic(
            answer_type=str(ac_proposal.get("answer_type", "")),
            target_task=cand_target,
            task_family=cand_family,
            answer_shape=str(ac_proposal.get("answer_shape", "")),
        )
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
                "answer_semantics": str(ac_proposal.get("answer_semantics", ac_proposal.get("answer_shape", ""))),
                "presentation_mode": str(
                    ac_proposal.get(
                        "presentation_mode",
                        presentation_mode_for_features(str(cluster.get("answer_type", "")), list(cluster.get("features") or [])),
                    )
                ),
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
                "coordinate_pair_presentation_note": (
                    "此來源為選擇題呈現，但語意答案為坐標對；已依 presentation_mode 拆分 problem_type。"
                    if coord_sem
                    and ac_proposal.get("source_has_choices")
                    and str(ac_proposal.get("presentation_mode", "")) == "single_choice"
                    else ""
                ),
                "confidence": "high",
                "promote_recommendation": "recommend_promote_for_that_candidate",
                "promote_blockers": [],
                "risk_flags": sorted(
                    set(
                        list(contract_blockers)
                        + list(checker_cap.get("checker_contract_blockers", []) or [])
                        + subskill_risk
                    )
                )
                if not contract_ok or checker_cap.get("checker_capability_status") == "blocked" or subskill_risk
                else [],
                "checker_contract_warnings": checker_cap.get("checker_contract_warnings", []),
                "spec_source": "phase1_induced_draft",
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
        )

    from core.gencode.anchor_subskill_bootstrap import bootstrap_anchor_subskill_candidates

    anchor_bootstrap_report = bootstrap_anchor_subskill_candidates(
        skill_id,
        main_skill_anchor,
        induced_specs,
        candidates,
        existing_ids,
        fallback_subskill_id=fallback_subskill_id,
    )

    # Source Skill Binding Supremacy / ProblemType Bridge §3–§4:
    # If any induced candidate is a bridge primary, expand it to runtime variants.
    coverage_floor_suggestions: list[dict[str, Any]] = []
    candidate_ids = {str(c.get("problem_type_id", "")).strip() for c in candidates if isinstance(c, dict)}
    observed_quadratic_tasks = {
        str(f.get("target_task", "")).strip()
        for f in features_for_induction
        if isinstance(f, dict)
        and task_family_for_task(str(f.get("target_task", ""))) == "quadratic_function_graph_family"
    }
    standard_vertex_evidence = [
        f for f in features_for_induction
        if isinstance(f, dict)
        and task_family_for_task(str(f.get("target_task", ""))) == "quadratic_function_graph_family"
        and re.search(r"x\}\^\{2\}|x\^2|ax\^2|px\+q|bx\+c", str(f.get("question_text", "")))
        and ("quadratic_vertex_form" in list(f.get("math_objects") or []) or "頂點" in str(f.get("question_text", "")))
    ]
    if (
        "quadratic_standard_to_vertex_properties" not in candidate_ids
        and observed_quadratic_tasks
        and standard_vertex_evidence
    ):
        pt = "quadratic_standard_to_vertex_properties"
        ex_ids = sorted(
            {
                int(f.get("source_example_id"))
                for f in standard_vertex_evidence
                if isinstance(f.get("source_example_id"), int)
            }
        )
        coverage_floor_suggestions.append(
            {
                "problem_type_id": pt,
                "target_task": pt,
                "reason": "quadratic_vertex_form_coverage_floor",
                "suggestion_only": True,
                "candidate_only": True,
                "requires_human_action": True,
                "phase3_include": False,
                "usable_for_phase3": False,
                "matched_example_ids": ex_ids,
                "matched_example_count": len(ex_ids),
                "notes": "coverage_floor may suggest missing coverage, but source evidence did not classify this problem_type directly",
            }
        )
        spec = {
            "problem_type_id": pt,
            "skill_id": skill_id,
            "display_name": "quadratic / standard to vertex properties",
            "target_task": pt,
            "task_family": task_family_for_task(pt),
            "source_example_ids": ex_ids,
            "answer_contract": {
                "answer_type": "single_choice",
                "answer_shape": "single_choice",
                "answer_semantics": "choice_label",
                "answer_equivalence": "choice_label",
                "equivalence_type": "choice_label",
                "checker": "choice_label_checker",
                "checker_key": "choice_label_checker",
                "presentation_mode": "single_choice",
                "choices_required": True,
                "choice_count": 4,
                "correct_choice_count": 1,
                "frontend_render_choices": True,
            },
            "stem_contract": {
                "stem_must_not_embed_choices": True,
                "required_math_objects": ["quadratic_equation"],
                "allowed_math_objects": ["quadratic_equation", "quadratic_vertex_form", "quadratic_vertex", "quadratic_axis"],
                "forbidden_patterns": [r"\(A\)", r"\(B\)", r"\(C\)", r"\(D\)"],
            },
            "dependency_contract": {
                "givens_must_be_used": True,
                "target_answer_must_depend_on_givens": True,
                "variables_in_conditions_must_appear_in_target": False,
            },
            "semantic_contract": {
                "reasoning_type": ["quadratic_standard_to_vertex_properties"],
                "required_concepts": ["quadratic_vertex_form"],
            },
            "generator_contract": {
                "template_slots": {"stem": "quadratic_standard_to_vertex_properties"},
                "template_families": [pt],
                "derivation_steps_required": True,
                "avoid_llm_freeform_math": True,
            },
            "validator_contract": {"runtime_smoke_count": 30},
            "grouping_reason": "quadratic_vertex_form_coverage_floor",
            "feature_signature": ["single_choice", pt],
            "spec_source": "phase1_induced_draft",
            "generator_readiness": "runtime_ready",
            "usable_for_phase3": False,
            "candidate_only": True,
            "requires_human_action": True,
            "phase3_include": False,
        }

    from core.gencode.problem_type_bridge import (
        BRIDGE_MISSING,
        expand_primary_to_runtime_variants,
        is_bridge_primary,
    )
    expanded_candidates: list[dict[str, Any]] = []
    bridge_expanded_pts: set[str] = set()
    for cand in candidates:
        pt_id = str(cand.get("problem_type_id", "")).strip()
        if is_bridge_primary(pt_id):
            source_ex_ids = [
                int(eid) for eid in (cand.get("matched_example_ids") or [])
                if isinstance(eid, int)
            ]
            variants, status = expand_primary_to_runtime_variants(skill_id, pt_id, source_ex_ids)
            if status == "ok" and variants:
                bridge_expanded_pts.add(pt_id)
                for v in variants:
                    v["source_candidate"] = cand
                    v["confidence"] = "high"
                    v["promote_recommendation"] = "recommend_promote_for_that_candidate"
                    v["promote_blockers"] = []
                    v["risk_flags"] = []
                    v["template_slot"] = v.get("generator_contract", {}).get("template_slots", {}).get("stem", "")
                    v["subskill_id"] = v.get("target_task", fallback_subskill_id)
                    expanded_candidates.append(v)
            else:
                # Bridge missing — mark as blocked, do NOT fallback to contextual_application
                blocked_cand = dict(cand)
                blocked_cand["generator_readiness"] = BRIDGE_MISSING
                blocked_cand["usable_for_phase3"] = False
                blocked_cand["risk_flags"] = sorted(
                    set(list(blocked_cand.get("risk_flags", []) or []) + [BRIDGE_MISSING])
                )
                blocked_cand["promote_blockers"] = sorted(
                    set(list(blocked_cand.get("promote_blockers", []) or []) + [BRIDGE_MISSING])
                )
                expanded_candidates.append(blocked_cand)
        else:
            expanded_candidates.append(cand)
    candidates = expanded_candidates

    non_runtime_supported_problem_type_ids = {
        str(c.get("problem_type_id", "")).strip()
        for c in candidates
        if isinstance(c, dict) and str(c.get("generator_readiness", "")).strip() != "runtime_ready"
    }
    candidate_only_problem_type_example_ids = {
        int(ex_id)
        for ex_id, pt in cluster_by_ex.items()
        if isinstance(ex_id, int) and str(pt).strip() in non_runtime_supported_problem_type_ids
    }

    for f in features:
        ex_id = f.get("source_example_id")
        pt = cluster_by_ex.get(ex_id, "unknown")
        if pt == "unknown":
            synthesized = _synthesize_orphan_problem_type_id(f)
            if synthesized:
                pt = synthesized
        sem = f.get("semantic_classification") if isinstance(f.get("semantic_classification"), dict) else {}
        risk_flags = ["stem_embeds_choices"] if f.get("stem_embeds_choices") else []
        if sem.get("classifier_source") == "ai_overrode_rule":
            risk_flags.append("ai_overrode_rule")
        if sem.get("classifier_source") == "ai_rule_conflict_review":
            risk_flags.append("ai_rule_conflict_review")
        if sem.get("source_mapping_warning"):
            risk_flags.append(str(sem["source_mapping_warning"]))
        if sem.get("requires_human_action"):
            risk_flags.append("requires_human_action")
        subskill_id = str(f.get("target_task", "")).strip() or fallback_subskill_id
        if bool(f.get("candidate_only")):
            subskill_id = fallback_subskill_id
            if "candidate_only" not in risk_flags:
                risk_flags.append("candidate_only")
        if isinstance(ex_id, int) and ex_id in candidate_only_problem_type_example_ids and str(f.get("target_task", "")).strip():
            if "candidate_only_problem_type" not in risk_flags:
                risk_flags.append("candidate_only_problem_type")
        per_example.append(
            {
                "example_id": ex_id,
                "detected_problem_type_id": pt,
                "example_feature": f,
                "answer_shape": f.get("answer_shape", ""),
                "classification_confidence": "high" if pt != "unknown" else "low",
                "classification_reason": str(f.get("classifier_source", "feature_signature_induction")),
                "risk_flags": risk_flags,
                "semantic_classification": sem,
                "subskill_id": subskill_id,
                "classification_source": str(sem.get("classifier_source", "")).strip() or str(f.get("classifier_source", "")).strip(),
            }
        )

    expected_family_relaxation_report: dict[str, Any] = {}
    if expected_families:
        unfiltered_induced_specs = list(induced_specs)
        unfiltered_candidates = list(candidates)
        induced_specs = [s for s in induced_specs if _spec_in_expected_families(s, expected_families)]
        candidates = [c for c in candidates if _spec_in_expected_families(c.get("problem_type_spec_draft", c), expected_families)]
        valid_core_tasks = [
            str(f.get("target_task", "")).strip()
            for f in stable_features_for_clusters
            if isinstance(f, dict)
            and str(f.get("induction_tier", "core")).strip() == "core"
            and not f.get("source_quality_reject")
            and str(f.get("target_task", "")).strip()
            and str(f.get("target_task", "")).strip() not in {"unknown", "needs_review"}
        ]
        task_counts = Counter(valid_core_tasks)
        uniform_task = task_counts.most_common(1)[0][0] if task_counts and task_counts.most_common(1)[0][1] == len(valid_core_tasks) else ""
        if uniform_task and unfiltered_candidates and not candidates:
            induced_specs = unfiltered_induced_specs
            candidates = unfiltered_candidates
            expected_family_relaxation_report = {
                "expected_family_relaxation_applied": True,
                "expected_family_relaxation_reason": "uniform_core_target_task_distribution",
                "expected_family_relaxation_target_task": uniform_task,
            }

    candidates = [apply_runtime_gate_to_candidate(c) for c in candidates if isinstance(c, dict)]

    semantic_alignment = evaluate_semantic_alignment(
        skill_id,
        skill_metadata=skill_metadata,
        source_features=features,
        candidate_specs=induced_specs,
        main_skill_anchor=main_skill_anchor,
        ai_semantic_status=ai_semantic_status,
        examples=examples,
        induction_source_report=induction_source_report,
    )
    if not features_for_induction and features:
        semantic_alignment = dict(semantic_alignment)
        semantic_alignment["decision"] = "block"
        blockers = list(semantic_alignment.get("blockers", []) or [])
        if int(induction_source_report.get("enrichment_example_count", 0) or 0) > 0:
            if "low_core_source_examples" not in blockers:
                blockers.append("low_core_source_examples")
            blockers = [
                b
                for b in blockers
                if b not in {"source_examples_mismatch", "majority_needs_review"}
            ]
        elif "source_examples_mismatch" not in blockers:
            blockers.append("source_examples_mismatch")
        semantic_alignment["blockers"] = sorted(set(blockers))

    candidates = apply_alignment_gate_to_candidates(candidates, semantic_alignment)

    gates = evaluate_pipeline_gates(
        candidates,
        source_examples_count=len(examples),
        checker_smoke_passed=False,
        dynamic_sampling_passed=False,
        contract_tests_passed=True,
        semantic_alignment_blocked=semantic_alignment.get("decision") == "block",
    )
    gates = merge_alignment_into_gates(gates, semantic_alignment)
    ex_gate = gates.get("exception_review_gate", {}) if isinstance(gates.get("exception_review_gate"), dict) else {}
    ex_reasons = [r for r in (ex_gate.get("reasons") or []) if str(r) not in {"runtime_smoke_failed", "dynamic_sampling_failed"}]
    if semantic_alignment.get("examples_outside_expected_family") and ai_semantic_status != "unavailable":
        ex_reasons.extend(["mixed_source_families", "requires_human_action"])
    if semantic_alignment.get("same_family_subskill_mismatch_examples"):
        ex_reasons.append("same_family_subskill_mismatch")
        if str(main_skill_anchor.get("skill_anchor_scope", "")).strip() == "narrow":
            ex_reasons.append("requires_human_action")
    ex_gate["reasons"] = sorted(set(ex_reasons))
    ex_gate["required"] = bool(ex_reasons)
    gates["exception_review_gate"] = ex_gate

    requires_human_action = bool(
        semantic_alignment.get("same_family_subskill_mismatch_examples")
        and str(main_skill_anchor.get("skill_anchor_scope", "")).strip() == "narrow"
    ) or any(
        isinstance(t, dict) and t.get("requires_human_action")
        for t in semantic_classifications
    ) or bool(structure_report.get("structure_mismatch_examples"))

    alignment_score = min(
        float(semantic_alignment.get("skill_source_score", 0.0)),
        float(semantic_alignment.get("skill_problem_type_score", 0.0)),
    )
    skill_terms = extract_skill_terms(skill_id, skill_metadata)
    source_example_alignment: list[dict[str, Any]] = []
    classification_diagnostics: list[dict[str, Any]] = []
    align_by_id: dict[int, dict[str, Any]] = {}
    for feat in features:
        if not isinstance(feat, dict):
            continue
        row = evaluate_source_example_alignment(skill_terms, feat, main_skill_anchor=main_skill_anchor)
        row["skill_id"] = skill_id
        row["title_stem_preview"] = str(feat.get("question_text", ""))[:80]
        source_example_alignment.append(row)
        ex_id = feat.get("source_example_id")
        if isinstance(ex_id, int):
            align_by_id[ex_id] = row
        trace = feat.get("semantic_classification") if isinstance(feat.get("semantic_classification"), dict) else {}
        classification_diagnostics.append(
            build_classification_diagnostic(
                feat,
                trace,
                main_skill_anchor,
                ai_semantic_status=ai_semantic_status,
                alignment_row=row,
            )
        )
    for row in per_example:
        if not isinstance(row, dict):
            continue
        ex_id = row.get("example_id")
        if isinstance(ex_id, int) and isinstance(align_by_id.get(ex_id), dict):
            row["induction_eligibility"] = str(align_by_id[ex_id].get("induction_eligibility", "")).strip()
        else:
            row["induction_eligibility"] = "unknown"

    semantic_mismatch_examples = [
        x for x in source_example_alignment
        if isinstance(x, dict)
        and str(x.get("alignment_kind", "")).strip() in {"needs_review", "outsider_candidate_warning"}
        and (
            str(x.get("task_family", "")).strip()
            and str(x.get("task_family", "")).strip() not in set(main_skill_anchor.get("expected_task_families") or [])
        )
    ]
    same_family_extension_examples = [
        x for x in source_example_alignment
        if isinstance(x, dict) and str(x.get("alignment_kind", "")).strip() == "same_family_extension"
    ]
    section_scope_subskill_extension_examples = [
        x for x in source_example_alignment
        if isinstance(x, dict) and str(x.get("alignment_kind", "")).strip() == "section_scope_subskill_extension"
    ]
    same_as_main_skill_examples = [
        {"example_id": x.get("example_id"), "reason": "fallback_subskill"}
        for x in per_example
        if isinstance(x, dict)
        and str(x.get("subskill_id", "")).strip() == fallback_subskill_id
        and "candidate_only" not in (x.get("risk_flags") or [])
        and "candidate_only_problem_type" not in (x.get("risk_flags") or [])
    ]
    inherited_from_previous_context_examples = [
        {
            "example_id": d.get("example_id"),
            "linked_example_id": d.get("linked_example_id"),
            "reason": "linked_example_consistent_boost",
        }
        for d in classification_diagnostics
        if isinstance(d, dict) and "linked_example_consistent_boost" in str(d.get("confidence_adjustment_reason", ""))
    ]
    low_source_examples = [
        {"problem_type_id": c.get("problem_type_id"), "matched_example_count": c.get("matched_example_count")}
        for c in candidates
        if isinstance(c, dict) and int(c.get("matched_example_count", 0) or 0) < 3
    ]
    candidate_only_problem_types = [
        {"example_id": f.get("source_example_id"), "subskill_id": fallback_subskill_id, "reason": "candidate_only_source"}
        for f in candidate_only_examples
        if isinstance(f, dict)
    ]
    candidate_only_problem_types.extend(
        [
            {"example_id": x.get("example_id"), "problem_type_id": x.get("detected_problem_type_id"), "reason": "runtime_not_supported"}
            for x in per_example
            if isinstance(x, dict) and "candidate_only_problem_type" in (x.get("risk_flags") or [])
        ]
    )
    subskills = sorted(
        {
            str(x.get("subskill_id", "")).strip()
            for x in per_example
            if isinstance(x, dict) and str(x.get("subskill_id", "")).strip()
        }
        | {fallback_subskill_id}
    )

    induced: dict[str, Any] = {
        "skill_id": skill_id,
        "main_skill_anchor": main_skill_anchor,
        "spec_mode": spec_mode,
        "semantic_classifications": semantic_classifications,
        "classification_diagnostics": classification_diagnostics,
        "ai_semantic_status": ai_semantic_status,
        "ai_semantic_unavailable_reason": next(
            (
                str(d.get("ai_unavailable_reason", "")).strip()
                for d in classification_diagnostics
                if str(d.get("ai_unavailable_reason", "")).strip()
            ),
            "",
        ),
        "ai_invalid_response_reason": next(
            (
                str(d.get("ai_invalid_response_reason", "")).strip()
                for d in classification_diagnostics
                if str(d.get("ai_invalid_response_reason", "")).strip()
            ),
            "",
        ),
        "source_structure_report": structure_report,
        "source_type_distribution": structure_report.get("source_type_distribution", {}),
        "example_practice_link_map": structure_report.get("example_practice_link_map", []),
        "structure_mismatch_examples": structure_report.get("structure_mismatch_examples", []),
        "same_section_family_distribution": structure_report.get("same_section_family_distribution", {}),
        "example_features": features,
        "semantic_alignment": semantic_alignment,
        "source_alignment_status": semantic_alignment.get("decision", "pass"),
        "skill_problem_type_alignment_status": semantic_alignment.get("decision", "pass"),
        "alignment_score": alignment_score,
        "alignment_warnings": list(semantic_alignment.get("warnings", []) or []),
        "alignment_blockers": list(semantic_alignment.get("blockers", []) or []),
        "source_family_distribution": semantic_alignment.get("source_family_distribution", {}),
        "candidate_problem_type_families": semantic_alignment.get("candidate_problem_type_families", []),
        "expected_skill_families": semantic_alignment.get("expected_skill_families", []),
        "expected_subskill_candidates": semantic_alignment.get(
            "expected_subskill_candidates",
            main_skill_anchor.get("expected_subskill_candidates", []),
        ),
        "observed_target_task_distribution": semantic_alignment.get("observed_target_task_distribution", {}),
        "same_family_subskill_mismatch_examples": semantic_alignment.get(
            "same_family_subskill_mismatch_examples", []
        ),
        "examples_outside_expected_subskills": semantic_alignment.get("examples_outside_expected_subskills", []),
        "suggested_action": semantic_alignment.get("suggested_action", ""),
        "requires_human_action": requires_human_action,
        "excluded_source_examples": excluded_source_examples,
        "rejected_source_examples": rejected_source_examples,
        "source_quality_issues": source_quality_issues,
        "semantic_mismatch_examples": semantic_mismatch_examples,
        "suspected_wrong_skill_examples": semantic_alignment.get("examples_outside_expected_family", []),
        "same_family_extension_examples": same_family_extension_examples,
        "section_scope_subskill_extension_examples": section_scope_subskill_extension_examples,
        "same_as_main_skill_examples": same_as_main_skill_examples,
        "inherited_from_previous_context_examples": inherited_from_previous_context_examples,
        "low_source_examples": low_source_examples,
        "coverage_floor_suggestions": coverage_floor_suggestions,
        "anchor_subskill_bootstrap": anchor_bootstrap_report,
        "candidate_only_problem_types": candidate_only_problem_types,
        "candidate_only_count": len(candidate_only_problem_types),
        "same_as_main_skill_count": len(same_as_main_skill_examples),
        "rule_only_classification_count": sum(
            1
            for x in per_example
            if isinstance(x, dict)
            and str(x.get("classification_source", "")).strip() in {"rule_only", "registry_rule"}
        ),
        "hybrid_resolved_count": sum(1 for x in per_example if isinstance(x, dict) and str(x.get("classification_source", "")).strip() == "hybrid_resolved"),
        "subskills": subskills,
        "fallback_subskill_used": any(str(s) == fallback_subskill_id for s in subskills),
        "source_belongs_to_current_skill_by_default_count": len(features) - len(semantic_alignment.get("source_quality_reject_examples", [])),
        "induction_source_selection": induction_source_report,
        "skipped_enrichment_examples": induction_source_report.get("skipped_enrichment_examples", []),
        "future_ai_judged_candidates": induction_source_report.get("future_ai_judged_candidates", []),
        "contextual_application_sources": induction_source_report.get("contextual_application_sources", []),
        **clause45_report,
        **expected_family_relaxation_report,
        "core_example_count": induction_source_report.get("core_example_count", 0),
        "enrichment_example_count": induction_source_report.get("enrichment_example_count", 0),
        "source_example_alignment": source_example_alignment,
        "induction_clusters": [
            {
                "grouping_reason": c.get("merge_reason"),
                "feature_signature": list(c.get("signature", ())),
                "source_example_ids": sorted(
                    {int(f.get("source_example_id")) for f in c.get("features", []) if isinstance(f.get("source_example_id"), int)}
                ),
                "answer_type": c.get("answer_type"),
                "presentation_mode": presentation_mode_for_features(
                    str(c.get("answer_type", "")),
                    list(c.get("features") or []),
                ),
                "source_has_choices": any(
                    f.get("has_choices") for f in (c.get("features") or []) if isinstance(f, dict)
                ),
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
        # Source Skill Binding Supremacy §3/§7 fields.
        "source_skill_scope_locked": bool(main_skill_anchor.get("source_skill_scope_locked", True)),
        "source_skill_id": str(main_skill_anchor.get("source_skill_id", skill_id)),
        "classification_scope": str(main_skill_anchor.get("classification_scope", "within_current_skill")),
        "skill_mapping_authority": str(main_skill_anchor.get("skill_mapping_authority", "textbook_examples.skill_id")),
        "human_confirmed_rule_pack_applied": human_confirmed_rule_pack_applied,
        "matched_registered_yaml_rule_pack": str(human_confirmed_pack.get("rule_pack_id", "")) if human_confirmed_pack else "",
        "ai_classification_overridden_by_human_confirmed_rule_pack": human_confirmed_rule_pack_applied,
    }
    _inject_combinatorics_probability_diagnosis_tags(induced, skill_id)
    return induced


def apply_spec_mode(
    skill_id: str,
    induced: dict[str, Any],
    legacy_auto_review: dict[str, Any],
    entries: list[dict[str, Any]],
    spec_mode: str,
) -> dict[str, Any]:
    mode = str(spec_mode or "ai_first_induce_from_sources").strip()
    curated = list_problem_types_for_skill(skill_id)
    induce_modes = {
        "induce_from_sources",
        "ai_first_induce_from_sources",
        "rule_first_induce_from_sources",
        "hybrid_ai_rule_validate",
    }

    if mode in induce_modes or not curated:
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


def _build_quadratic_coverage_floor_suggestions(
    *,
    skill_id: str,
    features_for_induction: list[dict[str, Any]],
    candidate_ids: set[str],
) -> list[dict[str, Any]]:
    """Suggest, but never promote, unobserved quadratic coverage-floor types."""
    observed_quadratic_tasks = {
        str(f.get("target_task", "")).strip()
        for f in features_for_induction
        if isinstance(f, dict)
        and task_family_for_task(str(f.get("target_task", ""))) == "quadratic_function_graph_family"
    }
    standard_vertex_evidence = [
        f for f in features_for_induction
        if isinstance(f, dict)
        and task_family_for_task(str(f.get("target_task", ""))) == "quadratic_function_graph_family"
        and re.search(r"x\}\^\{2\}|x\^2|ax\^2|px\+q|bx\+c", str(f.get("question_text", "")))
        and ("quadratic_vertex_form" in list(f.get("math_objects") or []) or "??" in str(f.get("question_text", "")))
    ]
    pt = "quadratic_standard_to_vertex_properties"
    if pt in candidate_ids or not observed_quadratic_tasks or not standard_vertex_evidence:
        return []
    ex_ids = sorted(
        {
            int(f.get("source_example_id"))
            for f in standard_vertex_evidence
            if isinstance(f.get("source_example_id"), int)
        }
    )
    return [
        {
            "skill_id": skill_id,
            "problem_type_id": pt,
            "target_task": pt,
            "reason": "quadratic_vertex_form_coverage_floor",
            "suggestion_only": True,
            "candidate_only": True,
            "requires_human_action": True,
            "phase3_include": False,
            "usable_for_phase3": False,
            "matched_example_ids": ex_ids,
            "matched_example_count": len(ex_ids),
            "notes": "coverage_floor may suggest missing coverage, but source evidence did not classify this problem_type directly",
        }
    ]
