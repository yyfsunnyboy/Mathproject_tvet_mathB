from __future__ import annotations

import logging
import random
from typing import Any

from core.gencode.answer_payload import answer_type_family
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
}

SLOT_COMPATIBLE_FAMILIES: dict[str, frozenset[str]] = {
    "point_quadrant": frozenset({"classification", "short_answer"}),
    "point_quadrant_choice": frozenset({"single_choice"}),
    "symbolic_quadrant": frozenset({"classification", "short_answer"}),
    "symbolic_quadrant_choice": frozenset({"single_choice"}),
    "two_point_distance_solution_set": frozenset({"solution_set"}),
    "two_point_distance_compute": frozenset({"numeric_or_radical", "numeric"}),
}


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


def resolve_template_slot(problem_type_spec: dict[str, Any], seed: int | None = None) -> str:
    """Pick slot from template_families when multiple families are induced for one problem_type."""
    pt = str(problem_type_spec.get("problem_type_id", "")).strip()
    gc = get_generator_contract(problem_type_spec)
    families = gc.get("template_families")
    strategy = "template_slots.stem"
    selected_slot = ""
    if isinstance(families, list):
        usable = [str(f).strip() for f in families if str(f).strip()]
        if len(usable) > 1:
            rng = _slot_rng(seed, pt)
            family = usable[rng.randrange(len(usable))]
            slot = TASK_FAMILY_TO_SLOT.get(family, "")
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
            slot = TASK_FAMILY_TO_SLOT.get(usable[0], "")
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
