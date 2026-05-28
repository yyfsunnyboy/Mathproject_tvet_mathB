from __future__ import annotations

import random
from typing import Any

from core.gencode.problem_type_spec import get_generator_contract, get_template_slot

# Map Phase 1 target_task / template_family names to registered slot generators.
TASK_FAMILY_TO_SLOT: dict[str, str] = {
    "classify_quadrant": "symbolic_quadrant",
    "choose_possible_coordinate": "axis_distance_choice",
    "choose_correct_statement": "symbolic_quadrant_statement_choice",
    "compute_numeric": "point_quadrant",
    "read_graph": "point_quadrant_choice",
    "read_table": "point_quadrant_choice",
}


def resolve_template_slot(problem_type_spec: dict[str, Any], seed: int | None = None) -> str:
    """Pick slot from template_families when multiple families are induced for one problem_type."""
    gc = get_generator_contract(problem_type_spec)
    families = gc.get("template_families")
    if isinstance(families, list):
        usable = [str(f).strip() for f in families if str(f).strip()]
        if len(usable) > 1:
            rng = random.Random(seed)
            family = usable[rng.randrange(len(usable))]
            slot = TASK_FAMILY_TO_SLOT.get(family, "")
            if slot:
                return slot
    slots = gc.get("template_slots")
    if isinstance(slots, dict):
        stem = str(slots.get("stem", "")).strip()
        if stem:
            return stem
    return get_template_slot(problem_type_spec)
