from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "prize_ball_expectation"
TEXTBOOK_EXAMPLE_ID = 12911
DEFAULT_COMPONENT_ID = "src_12911" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MathematicalExpectation"
FIXED_DOMAIN_KEY = "discrete.mathematical_expectation"
DOMAIN_OPERATION = "prize_ball_expectation"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['prize_ball_expectation'], 'domain_operation': 'prize_ball_expectation', 'problem_type_id': 'prize_ball_expectation', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'values': [1000, 2000, 3000, 7200], 'choice_offsets': [-500, -300, 0, 200, 500]}, {'values': [1500, 2500, 6000, 8000, 9500], 'choice_offsets': [200, -800, 0, -300, 800]}, {'values': [4000, 6500, 7000, 8500], 'choice_offsets': [-500, 800, 0, -200, -800]}, {'values': [500, 1500, 4000, 6000], 'choice_offsets': [500, -200, -500, -300, 0]}, {'values': [6500, 8500, 9000], 'choice_offsets': [-500, 300, 200, 0, -200]}, {'values': [1500, 3000, 5000, 6500, 7000], 'choice_offsets': [-500, 800, -300, 0, -800]}, {'values': [500, 1500, 3000, 3500, 5500], 'choice_offsets': [-800, 200, 800, 0, -300]}, {'values': [1500, 2000, 7000], 'choice_offsets': [-800, -500, 800, 200, 0]}, {'values': [500, 2500, 3000, 4500], 'choice_offsets': [-300, -500, -800, 0, 200]}, {'values': [2000, 5000, 5500, 9000, 9500], 'choice_offsets': [-300, 0, -800, 200, -500]}, {'values': [2000, 2500, 6000], 'choice_offsets': [500, 800, -500, 0, 200]}, {'values': [1500, 3000, 4500, 8500, 9500], 'choice_offsets': [-500, -200, 0, 500, 800]}, {'values': [1000, 3000, 4000, 8000], 'choice_offsets': [800, -300, 0, 300, -800]}, {'values': [1000, 3000, 4500, 9500], 'choice_offsets': [0, -800, 200, 800, -300]}, {'values': [500, 4500, 5500, 6500, 7500], 'choice_offsets': [200, -300, -800, -200, 0]}, {'values': [500, 3500, 4000, 5000, 8000], 'choice_offsets': [-800, -500, -300, 800, 0]}, {'values': [2000, 3500, 6000, 7000, 9500], 'choice_offsets': [500, 0, -300, -200, -500]}, {'values': [1000, 2500, 4000, 6500], 'choice_offsets': [200, 0, 300, -500, -800]}, {'values': [1000, 3000, 3500, 6000], 'choice_offsets': [-500, 300, -200, 0, 200]}, {'values': [1000, 1500, 6000, 6500, 8000], 'choice_offsets': [800, 0, -200, 500, 200]}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['prize_ball_expectation'], 'domain_operation': 'prize_ball_expectation', 'problem_type_id': 'prize_ball_expectation', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'values': [1000, 2000, 3000, 7200], 'choice_offsets': [-500, -300, 0, 200, 500]}, {'values': [1500, 2500, 6000, 8000, 9500], 'choice_offsets': [200, -800, 0, -300, 800]}, {'values': [4000, 6500, 7000, 8500], 'choice_offsets': [-500, 800, 0, -200, -800]}, {'values': [500, 1500, 4000, 6000], 'choice_offsets': [500, -200, -500, -300, 0]}, {'values': [6500, 8500, 9000], 'choice_offsets': [-500, 300, 200, 0, -200]}, {'values': [1500, 3000, 5000, 6500, 7000], 'choice_offsets': [-500, 800, -300, 0, -800]}, {'values': [500, 1500, 3000, 3500, 5500], 'choice_offsets': [-800, 200, 800, 0, -300]}, {'values': [1500, 2000, 7000], 'choice_offsets': [-800, -500, 800, 200, 0]}, {'values': [500, 2500, 3000, 4500], 'choice_offsets': [-300, -500, -800, 0, 200]}, {'values': [2000, 5000, 5500, 9000, 9500], 'choice_offsets': [-300, 0, -800, 200, -500]}, {'values': [2000, 2500, 6000], 'choice_offsets': [500, 800, -500, 0, 200]}, {'values': [1500, 3000, 4500, 8500, 9500], 'choice_offsets': [-500, -200, 0, 500, 800]}, {'values': [1000, 3000, 4000, 8000], 'choice_offsets': [800, -300, 0, 300, -800]}, {'values': [1000, 3000, 4500, 9500], 'choice_offsets': [0, -800, 200, 800, -300]}, {'values': [500, 4500, 5500, 6500, 7500], 'choice_offsets': [200, -300, -800, -200, 0]}, {'values': [500, 3500, 4000, 5000, 8000], 'choice_offsets': [-800, -500, -300, 800, 0]}, {'values': [2000, 3500, 6000, 7000, 9500], 'choice_offsets': [500, 0, -300, -200, -500]}, {'values': [1000, 2500, 4000, 6500], 'choice_offsets': [200, 0, 300, -500, -800]}, {'values': [1000, 3000, 3500, 6000], 'choice_offsets': [-500, 300, -200, 0, 200]}, {'values': [1000, 1500, 6000, 6500, 8000], 'choice_offsets': [800, 0, -200, 500, 200]}]}}, 'problem_type_id': 'prize_ball_expectation', 'required_capabilities': ['prize_ball_expectation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'values': [1000, 2000, 3000, 7200], 'choice_offsets': [-500, -300, 0, 200, 500]}, {'values': [1500, 2500, 6000, 8000, 9500], 'choice_offsets': [200, -800, 0, -300, 800]}, {'values': [4000, 6500, 7000, 8500], 'choice_offsets': [-500, 800, 0, -200, -800]}, {'values': [500, 1500, 4000, 6000], 'choice_offsets': [500, -200, -500, -300, 0]}, {'values': [6500, 8500, 9000], 'choice_offsets': [-500, 300, 200, 0, -200]}, {'values': [1500, 3000, 5000, 6500, 7000], 'choice_offsets': [-500, 800, -300, 0, -800]}, {'values': [500, 1500, 3000, 3500, 5500], 'choice_offsets': [-800, 200, 800, 0, -300]}, {'values': [1500, 2000, 7000], 'choice_offsets': [-800, -500, 800, 200, 0]}, {'values': [500, 2500, 3000, 4500], 'choice_offsets': [-300, -500, -800, 0, 200]}, {'values': [2000, 5000, 5500, 9000, 9500], 'choice_offsets': [-300, 0, -800, 200, -500]}, {'values': [2000, 2500, 6000], 'choice_offsets': [500, 800, -500, 0, 200]}, {'values': [1500, 3000, 4500, 8500, 9500], 'choice_offsets': [-500, -200, 0, 500, 800]}, {'values': [1000, 3000, 4000, 8000], 'choice_offsets': [800, -300, 0, 300, -800]}, {'values': [1000, 3000, 4500, 9500], 'choice_offsets': [0, -800, 200, 800, -300]}, {'values': [500, 4500, 5500, 6500, 7500], 'choice_offsets': [200, -300, -800, -200, 0]}, {'values': [500, 3500, 4000, 5000, 8000], 'choice_offsets': [-800, -500, -300, 800, 0]}, {'values': [2000, 3500, 6000, 7000, 9500], 'choice_offsets': [500, 0, -300, -200, -500]}, {'values': [1000, 2500, 4000, 6500], 'choice_offsets': [200, 0, 300, -500, -800]}, {'values': [1000, 3000, 3500, 6000], 'choice_offsets': [-500, 300, -200, 0, 200]}, {'values': [1000, 1500, 6000, 6500, 8000], 'choice_offsets': [800, 0, -200, 500, 200]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MathematicalExpectation', 'fixed_domain_key': 'discrete.mathematical_expectation', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['prize_ball_expectation'], 'matched_capabilities': ['prize_ball_expectation'], 'selected_operation': 'prize_ball_expectation', 'registry_revision': 'promoted-a714bd66521e', 'domain_module': 'core.domain.promoted.mathematical_expectation.mathematical_expectation_domain', 'entrypoint': 'build_mathematical_expectation_matrix', 'allowed_operations': ['coin_payout_expectation', 'decision_by_expectation', 'die_payout_expectation', 'expectation_claim', 'insurance_expectation', 'lottery_expectation', 'multiple_choice_guess_expectation', 'prize_ball_expectation', 'single_die_game', 'two_dice_match_game', 'urn_draw_expectation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MathematicalExpectation'}), seed)
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
