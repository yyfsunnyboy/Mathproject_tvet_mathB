from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "lottery_expectation"
TEXTBOOK_EXAMPLE_ID = 12910
DEFAULT_COMPONENT_ID = "src_12910" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MathematicalExpectation"
FIXED_DOMAIN_KEY = "discrete.mathematical_expectation"
DOMAIN_OPERATION = "lottery_expectation"


def _materialize_generation_constraints(raw_constraints: dict[str, Any], seed: int | None) -> dict[str, Any]:
    constraints = deepcopy(raw_constraints)
    generation_constraints = constraints.pop("generation_constraints", None)
    if generation_constraints is None:
        return constraints
    if not isinstance(generation_constraints, dict):
        raise ValueError("generation_constraints must be a dict")
    variants = generation_constraints.get("variants")
    if not isinstance(variants, list) or not variants:
        raise ValueError("generation_constraints.variants must be a non-empty list")
    index = 0 if seed is None else int(seed) % len(variants)
    selected = variants[index]
    if not isinstance(selected, dict):
        raise ValueError("generation_constraints variant must be a dict")
    selected_constraints = selected.get("constraints", selected)
    if not isinstance(selected_constraints, dict):
        raise ValueError("generation_constraints variant constraints must be a dict")
    forbidden = {"answer", "correct_answer", "canonical_answer", "answer_contract", "checker", "checker_key"}
    if forbidden & set(selected_constraints):
        raise ValueError("generation_constraints must not define answer or checker authority")
    constraints.update(deepcopy(selected_constraints))
    return constraints


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    resolution = resolve_domain_authority(SKILL_ID, selected_operation=DOMAIN_OPERATION)
    if (
        resolution.binding_status != "confirmed"
        or resolution.fixed_domain_key != FIXED_DOMAIN_KEY
        or resolution.selected_operation != DOMAIN_OPERATION
    ):
        raise RuntimeError(
            "domain_binding_mismatch:"
            f"{resolution.binding_status}:{resolution.fixed_domain_key}:{resolution.selected_operation}"
        )

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['lottery_expectation'], 'domain_operation': 'lottery_expectation', 'problem_type_id': 'lottery_expectation', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'total': 1000000, 'prizes': [[10000000, 1], [5000000, 2], [1000000, 5], [100000, 20], [10000, 100], [1000, 1000]]}, {'total': 500000, 'prizes': [[5000000, 2], [1000000, 3], [50000, 10], [10000, 200]]}, {'total': 100000, 'prizes': [[1000000, 1], [500000, 5], [100000, 100], [10000, 200]]}, {'total': 100000, 'prizes': [[5000000, 3], [500000, 10], [50000, 20], [10000, 500]]}, {'total': 1000000, 'prizes': [[1000000, 3], [500000, 10], [50000, 20], [10000, 50], [5000, 500]]}, {'total': 200000, 'prizes': [[1000000, 2], [500000, 3], [10000, 5], [5000, 20], [1000, 500]]}, {'total': 2000000, 'prizes': [[10000000, 2], [500000, 100], [100000, 200], [10000, 500], [1000, 1000]]}, {'total': 1000000, 'prizes': [[10000000, 2], [5000000, 3], [500000, 200], [100000, 1000]]}, {'total': 2000000, 'prizes': [[10000000, 2], [1000000, 50], [100000, 100], [50000, 500]]}, {'total': 500000, 'prizes': [[500000, 5], [100000, 100], [50000, 200], [10000, 500]]}, {'total': 200000, 'prizes': [[1000000, 5], [100000, 50], [10000, 500]]}, {'total': 100000, 'prizes': [[5000000, 1], [100000, 2], [50000, 200], [10000, 1000]]}, {'total': 100000, 'prizes': [[10000000, 1], [50000, 3], [10000, 200], [1000, 1000]]}, {'total': 500000, 'prizes': [[1000000, 1], [500000, 10], [50000, 100], [5000, 1000]]}, {'total': 100000, 'prizes': [[5000000, 1], [1000000, 2], [50000, 10], [5000, 20], [2000, 1000]]}, {'total': 1000000, 'prizes': [[10000000, 10], [50000, 50], [5000, 500]]}, {'total': 100000, 'prizes': [[100000, 5], [10000, 10], [5000, 50]]}, {'total': 500000, 'prizes': [[5000000, 10], [1000000, 50], [100000, 100], [2000, 1000]]}, {'total': 2000000, 'prizes': [[100000, 2], [50000, 3], [2000, 5], [1000, 10]]}, {'total': 2000000, 'prizes': [[10000000, 2], [1000000, 50], [100000, 100], [10000, 500], [2000, 1000]]}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['lottery_expectation'], 'domain_operation': 'lottery_expectation', 'problem_type_id': 'lottery_expectation', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'total': 1000000, 'prizes': [[10000000, 1], [5000000, 2], [1000000, 5], [100000, 20], [10000, 100], [1000, 1000]]}, {'total': 500000, 'prizes': [[5000000, 2], [1000000, 3], [50000, 10], [10000, 200]]}, {'total': 100000, 'prizes': [[1000000, 1], [500000, 5], [100000, 100], [10000, 200]]}, {'total': 100000, 'prizes': [[5000000, 3], [500000, 10], [50000, 20], [10000, 500]]}, {'total': 1000000, 'prizes': [[1000000, 3], [500000, 10], [50000, 20], [10000, 50], [5000, 500]]}, {'total': 200000, 'prizes': [[1000000, 2], [500000, 3], [10000, 5], [5000, 20], [1000, 500]]}, {'total': 2000000, 'prizes': [[10000000, 2], [500000, 100], [100000, 200], [10000, 500], [1000, 1000]]}, {'total': 1000000, 'prizes': [[10000000, 2], [5000000, 3], [500000, 200], [100000, 1000]]}, {'total': 2000000, 'prizes': [[10000000, 2], [1000000, 50], [100000, 100], [50000, 500]]}, {'total': 500000, 'prizes': [[500000, 5], [100000, 100], [50000, 200], [10000, 500]]}, {'total': 200000, 'prizes': [[1000000, 5], [100000, 50], [10000, 500]]}, {'total': 100000, 'prizes': [[5000000, 1], [100000, 2], [50000, 200], [10000, 1000]]}, {'total': 100000, 'prizes': [[10000000, 1], [50000, 3], [10000, 200], [1000, 1000]]}, {'total': 500000, 'prizes': [[1000000, 1], [500000, 10], [50000, 100], [5000, 1000]]}, {'total': 100000, 'prizes': [[5000000, 1], [1000000, 2], [50000, 10], [5000, 20], [2000, 1000]]}, {'total': 1000000, 'prizes': [[10000000, 10], [50000, 50], [5000, 500]]}, {'total': 100000, 'prizes': [[100000, 5], [10000, 10], [5000, 50]]}, {'total': 500000, 'prizes': [[5000000, 10], [1000000, 50], [100000, 100], [2000, 1000]]}, {'total': 2000000, 'prizes': [[100000, 2], [50000, 3], [2000, 5], [1000, 10]]}, {'total': 2000000, 'prizes': [[10000000, 2], [1000000, 50], [100000, 100], [10000, 500], [2000, 1000]]}]}}, 'problem_type_id': 'lottery_expectation', 'required_capabilities': ['lottery_expectation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'total': 1000000, 'prizes': [[10000000, 1], [5000000, 2], [1000000, 5], [100000, 20], [10000, 100], [1000, 1000]]}, {'total': 500000, 'prizes': [[5000000, 2], [1000000, 3], [50000, 10], [10000, 200]]}, {'total': 100000, 'prizes': [[1000000, 1], [500000, 5], [100000, 100], [10000, 200]]}, {'total': 100000, 'prizes': [[5000000, 3], [500000, 10], [50000, 20], [10000, 500]]}, {'total': 1000000, 'prizes': [[1000000, 3], [500000, 10], [50000, 20], [10000, 50], [5000, 500]]}, {'total': 200000, 'prizes': [[1000000, 2], [500000, 3], [10000, 5], [5000, 20], [1000, 500]]}, {'total': 2000000, 'prizes': [[10000000, 2], [500000, 100], [100000, 200], [10000, 500], [1000, 1000]]}, {'total': 1000000, 'prizes': [[10000000, 2], [5000000, 3], [500000, 200], [100000, 1000]]}, {'total': 2000000, 'prizes': [[10000000, 2], [1000000, 50], [100000, 100], [50000, 500]]}, {'total': 500000, 'prizes': [[500000, 5], [100000, 100], [50000, 200], [10000, 500]]}, {'total': 200000, 'prizes': [[1000000, 5], [100000, 50], [10000, 500]]}, {'total': 100000, 'prizes': [[5000000, 1], [100000, 2], [50000, 200], [10000, 1000]]}, {'total': 100000, 'prizes': [[10000000, 1], [50000, 3], [10000, 200], [1000, 1000]]}, {'total': 500000, 'prizes': [[1000000, 1], [500000, 10], [50000, 100], [5000, 1000]]}, {'total': 100000, 'prizes': [[5000000, 1], [1000000, 2], [50000, 10], [5000, 20], [2000, 1000]]}, {'total': 1000000, 'prizes': [[10000000, 10], [50000, 50], [5000, 500]]}, {'total': 100000, 'prizes': [[100000, 5], [10000, 10], [5000, 50]]}, {'total': 500000, 'prizes': [[5000000, 10], [1000000, 50], [100000, 100], [2000, 1000]]}, {'total': 2000000, 'prizes': [[100000, 2], [50000, 3], [2000, 5], [1000, 10]]}, {'total': 2000000, 'prizes': [[10000000, 2], [1000000, 50], [100000, 100], [10000, 500], [2000, 1000]]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MathematicalExpectation', 'fixed_domain_key': 'discrete.mathematical_expectation', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['lottery_expectation'], 'matched_capabilities': ['lottery_expectation'], 'selected_operation': 'lottery_expectation', 'registry_revision': 'promoted-a714bd66521e', 'domain_module': 'core.domain.promoted.mathematical_expectation.mathematical_expectation_domain', 'entrypoint': 'build_mathematical_expectation_matrix', 'allowed_operations': ['coin_payout_expectation', 'decision_by_expectation', 'die_payout_expectation', 'expectation_claim', 'insurance_expectation', 'lottery_expectation', 'multiple_choice_guess_expectation', 'prize_ball_expectation', 'single_die_game', 'two_dice_match_game', 'urn_draw_expectation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MathematicalExpectation'}), seed)
    constraints["skill_id"] = SKILL_ID
    _matrix, payload = dispatch_registered_operation(
        resolution.fixed_domain_key,
        DOMAIN_OPERATION,
        seed=seed,
        constraints=constraints,
    )
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    if component_id:
        payload["component_id"] = component_id
    payload["skill_id"] = SKILL_ID
    payload["textbook_example_id"] = TEXTBOOK_EXAMPLE_ID
    payload["domain_resolution"] = {
        "fixed_domain_key": resolution.fixed_domain_key,
        "resolution_source": resolution.resolution_source,
        "binding_status": resolution.binding_status,
        "selected_operation": resolution.selected_operation,
        "registry_revision": resolution.registry_revision,
    }
    payload["seed"] = seed
    return payload
