from __future__ import annotations

import logging
import random
from typing import Any

from core.gencode.answer_payload import answer_type_family
from core.gencode.division_point_slot_engine import DIVISION_POINT_SLOT, is_division_point_target_task
from core.gencode.problem_type_spec import get_answer_contract, get_generator_contract, get_template_slot

logger = logging.getLogger(__name__)

# Map Phase 1 target_task / template_family names to registered slot generators.
TASK_FAMILY_TO_SLOT: dict[str, str] = {
    "classify_quadrant": "symbolic_quadrant",
    "choose_possible_coordinate": "axis_distance_choice",
    "choose_correct_statement": "symbolic_quadrant_statement_choice",
    "compute_numeric": "point_quadrant",
    "read_graph": "point_quadrant_choice",
    "read_table": "point_quadrant_choice",
    "solve_unknown_coordinate_from_two_point_distance": "two_point_distance_solution_set",
    "compute_distance_between_two_points": "two_point_distance_compute",
    "compute_internal_division_point_coordinates": DIVISION_POINT_SLOT,
    "compute_centroid_coordinates": DIVISION_POINT_SLOT,
    "compute_midpoint_coordinates": DIVISION_POINT_SLOT,
    "solve_point_from_section_ratio": DIVISION_POINT_SLOT,
    "compute_triangle_median_line": "linear_triangle_median_compute",
    "evaluate_function_value": "function_value_numeric",
    "interpret_function_notation": "linear_function_two_point_choice",
    "contextual_application": "linear_function_contextual_word_problem",
    "word_problem": "linear_function_contextual_word_problem",
    "quadratic_graph_vertex_axis_choice": "quadratic_graph_vertex_axis_choice",
    "quadratic_graph_translation_fill_blank": "quadratic_graph_translation_fill_blank",
    "quadratic_graph_translation_short_answer": "quadratic_graph_translation_short_answer",
    "quadratic_vertex_form_properties": "quadratic_vertex_form_properties",
    "quadratic_standard_to_vertex_properties": "quadratic_standard_to_vertex_properties",
}

SLOT_COMPATIBLE_FAMILIES: dict[str, frozenset[str]] = {
    "point_quadrant": frozenset({"classification", "short_answer"}),
    "point_quadrant_choice": frozenset({"single_choice"}),
    "symbolic_quadrant": frozenset({"classification", "short_answer"}),
    "symbolic_quadrant_choice": frozenset({"single_choice"}),
    "two_point_distance_solution_set": frozenset({"solution_set"}),
    "two_point_distance_compute": frozenset({"numeric_or_radical", "numeric"}),
    DIVISION_POINT_SLOT: frozenset({"ordered_pair", "coordinate_pair", "single_choice"}),
    "linear_triangle_median_compute": frozenset({"numeric", "numeric_or_radical", "expression", "short_answer"}),
    "function_value_numeric": frozenset({"numeric", "short_answer"}),
    "linear_function_two_point_choice": frozenset({"single_choice"}),
    "linear_function_contextual_word_problem": frozenset({"numeric", "expression", "short_answer"}),
    "quadratic_graph_vertex_axis_choice": frozenset({"single_choice"}),
    "quadratic_graph_translation_fill_blank": frozenset({"text_short", "short_answer"}),
    "quadratic_graph_translation_short_answer": frozenset({"text_short", "short_answer"}),
    "quadratic_vertex_form_properties": frozenset({"single_choice", "text_short", "short_answer"}),
    "quadratic_standard_to_vertex_properties": frozenset({"single_choice", "text_short", "short_answer"}),
}

_QUADRATIC_GRAPH_TARGET_TASKS = frozenset(
    {
        "quadratic_graph_vertex_axis_choice",
        "quadratic_graph_translation_fill_blank",
        "quadratic_graph_translation_short_answer",
        "quadratic_vertex_form_properties",
        "quadratic_standard_to_vertex_properties",
    }
)


def _is_quadratic_graph_spec(problem_type_spec: dict[str, Any]) -> bool:
    skill_id = str(problem_type_spec.get("skill_id", "")).strip().lower()
    pt = str(problem_type_spec.get("problem_type_id", "")).strip().lower()
    target_task = str(problem_type_spec.get("target_task", "")).strip().lower()
    if "quadraticfunctiongraph" in skill_id or "quadratic" in pt or target_task in _QUADRATIC_GRAPH_TARGET_TASKS:
        return True
    gc = get_generator_contract(problem_type_spec)
    families = gc.get("template_families") if isinstance(gc.get("template_families"), list) else []
    joined = " ".join(str(f).strip().lower() for f in families if str(f).strip())
    return "quadratic" in joined


def _resolve_quadratic_graph_slot(problem_type_spec: dict[str, Any]) -> str:
    target_task = str(problem_type_spec.get("target_task", "")).strip()
    if target_task in _QUADRATIC_GRAPH_TARGET_TASKS:
        return TASK_FAMILY_TO_SLOT.get(target_task, "")
    pt = str(problem_type_spec.get("problem_type_id", "")).strip().lower()
    if "translation_fill_blank" in pt:
        return "quadratic_graph_translation_fill_blank"
    if "translation_short_answer" in pt:
        return "quadratic_graph_translation_short_answer"
    if "standard_to_vertex" in pt:
        return "quadratic_standard_to_vertex_properties"
    if "vertex_form" in pt:
        return "quadratic_vertex_form_properties"
    return "quadratic_graph_vertex_axis_choice"


def _resolve_function_family_slot(problem_type_spec: dict[str, Any], family: str) -> str:
    """Contract-aware slot for function-value task families (data-driven, not skill-specific)."""
    task = str(family or problem_type_spec.get("target_task", "")).strip()
    if task not in {"evaluate_function_value", "interpret_function_notation", "contextual_application", "word_problem"}:
        return ""
    ac = get_answer_contract(problem_type_spec)
    gc = get_generator_contract(problem_type_spec)
    answer_type = str(ac.get("answer_type", "")).strip()
    checker = str(ac.get("checker") or ac.get("checker_key") or "").strip()
    pt_key = str(problem_type_spec.get("problem_type_id", "")).strip().lower()
    if task == "interpret_function_notation":
        mapped = TASK_FAMILY_TO_SLOT.get("interpret_function_notation", "")
        if mapped and _slot_compatible_with_contract(mapped, problem_type_spec):
            return mapped
    application_requested = task in {"contextual_application", "word_problem"} or (
        task == "evaluate_function_value"
        and (
            bool(gc.get("contextual_application"))
            or "application" in pt_key
            or "word_problem" in pt_key
            or pt_key.startswith("expression_evaluate_function_value")
        )
        and (answer_type == "expression" or checker == "expression_checker")
    )
    if application_requested:
        mapped = TASK_FAMILY_TO_SLOT.get("contextual_application", "")
        if mapped and _slot_compatible_with_contract(mapped, problem_type_spec):
            return mapped
    mapped = TASK_FAMILY_TO_SLOT.get("evaluate_function_value", "")
    if mapped and _slot_compatible_with_contract(mapped, problem_type_spec):
        return mapped
    return ""


def _infer_slot_from_answer_contract(problem_type_spec: dict[str, Any]) -> str:
    family = answer_type_family(str(get_answer_contract(problem_type_spec).get("answer_type", "")))
    if family == "solution_set":
        return "two_point_distance_solution_set"
    if family in {"numeric_or_radical", "numeric"}:
        gc = get_generator_contract(problem_type_spec)
        families = gc.get("template_families") if isinstance(gc.get("template_families"), list) else []
        joined = " ".join(str(f) for f in families)
        if "compute_distance" in joined or "distance" in joined:
            return "two_point_distance_compute"
    return ""


def _slot_compatible_with_contract(slot: str, problem_type_spec: dict[str, Any]) -> bool:
    slot_name = str(slot or "").strip()
    if not slot_name:
        return False
    family = answer_type_family(str(get_answer_contract(problem_type_spec).get("answer_type", "")))
    allowed = SLOT_COMPATIBLE_FAMILIES.get(slot_name)
    if allowed is None:
        return True
    return family in allowed


def _slot_rng(seed: int | None, problem_type_id: str) -> random.Random:
    if seed is None:
        return random.Random()
    return random.Random(f"{seed}|template_slot|{problem_type_id}")


def infer_registered_task_token(problem_type_spec: dict[str, Any]) -> str:
    """Recover a registered task token from a normalized problem_type_id."""
    pt = str(problem_type_spec.get("problem_type_id", "")).strip().lower()
    if not pt:
        return ""
    matches = [task for task in TASK_FAMILY_TO_SLOT if task.lower() in pt]
    if not matches:
        return ""
    return max(matches, key=len)


def resolve_template_slot(problem_type_spec: dict[str, Any], seed: int | None = None) -> str:
    """Pick slot from template_families when multiple families are induced for one problem_type."""
    pt = str(problem_type_spec.get("problem_type_id", "")).strip()
    target_task = str(problem_type_spec.get("target_task", "")).strip()
    if _is_quadratic_graph_spec(problem_type_spec):
        slot = _resolve_quadratic_graph_slot(problem_type_spec)
        if slot:
            logger.info(
                "[GENCODE DISPATCH] template_slot problem_type_id=%s selected_slot=%s selection_strategy=quadratic_domain_guard",
                pt,
                slot,
            )
            return slot
    inferred_target_task = infer_registered_task_token(problem_type_spec)
    if target_task not in TASK_FAMILY_TO_SLOT and inferred_target_task:
        target_task = inferred_target_task
        logger.info(
            "[GENCODE DISPATCH] recovered_target_task problem_type_id=%s target_task=%s selection_strategy=problem_type_id_token",
            pt,
            target_task,
        )
    if is_division_point_target_task(target_task):
        slot = TASK_FAMILY_TO_SLOT.get(target_task, DIVISION_POINT_SLOT)
        logger.info(
            "[GENCODE DISPATCH] template_slot problem_type_id=%s selected_slot=%s selection_strategy=target_task",
            pt,
            slot,
        )
        return slot
    if target_task == "compute_triangle_median_line":
        slot = TASK_FAMILY_TO_SLOT[target_task]
        logger.info(
            "[GENCODE DISPATCH] template_slot problem_type_id=%s selected_slot=%s selection_strategy=target_task",
            pt,
            slot,
        )
        return slot
    gc = get_generator_contract(problem_type_spec)
    families = gc.get("template_families")
    strategy = "template_slots.stem"
    selected_slot = ""
    if isinstance(families, list):
        usable = [str(f).strip() for f in families if str(f).strip()]
        if len(usable) > 1:
            rng = _slot_rng(seed, pt)
            family = usable[rng.randrange(len(usable))]
            slot = _resolve_function_family_slot(problem_type_spec, family) or TASK_FAMILY_TO_SLOT.get(family, "")
            if slot:
                strategy = "template_families.uniform_random"
                selected_slot = slot
                logger.info(
                    "[GENCODE DISPATCH] template_slot problem_type_id=%s selected_slot=%s selection_strategy=%s family=%s",
                    pt,
                    selected_slot,
                    strategy,
                    family,
                )
                return selected_slot
        elif len(usable) == 1:
            slot = _resolve_function_family_slot(problem_type_spec, usable[0]) or TASK_FAMILY_TO_SLOT.get(usable[0], "")
            if slot:
                strategy = "template_families.single"
                selected_slot = slot
                logger.info(
                    "[GENCODE DISPATCH] template_slot problem_type_id=%s selected_slot=%s selection_strategy=%s family=%s",
                    pt,
                    selected_slot,
                    strategy,
                    usable[0],
                )
                return selected_slot
    slots = gc.get("template_slots")
    if isinstance(slots, dict):
        stem = str(slots.get("stem", "")).strip()
        if stem and _slot_compatible_with_contract(stem, problem_type_spec):
            selected_slot = stem
            logger.info(
                "[GENCODE DISPATCH] template_slot problem_type_id=%s selected_slot=%s selection_strategy=%s",
                pt,
                selected_slot,
                strategy,
            )
            return selected_slot
        if stem:
            inferred = _infer_slot_from_answer_contract(problem_type_spec)
            if inferred:
                logger.info(
                    "[GENCODE DISPATCH] template_slot problem_type_id=%s selected_slot=%s selection_strategy=answer_contract_inferred rejected_stem=%s",
                    pt,
                    inferred,
                    stem,
                )
                return inferred
    selected_slot = get_template_slot(problem_type_spec)
    logger.info(
        "[GENCODE DISPATCH] template_slot problem_type_id=%s selected_slot=%s selection_strategy=fallback_template_slot",
        pt,
        selected_slot,
    )
    return selected_slot
