from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "coin_payout_expectation"
TEXTBOOK_EXAMPLE_ID = 12894
DEFAULT_COMPONENT_ID = "src_12894" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MathematicalExpectation"
FIXED_DOMAIN_KEY = "discrete.mathematical_expectation"
DOMAIN_OPERATION = "coin_payout_expectation"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['coin_payout_expectation'], 'domain_operation': 'coin_payout_expectation', 'problem_type_id': 'coin_payout_expectation', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'n': 3, 'scenarios': [[-100, 5, 10, 15], [-60, 5, 10, 15]]}, {'n': 4, 'scenarios': [[-120, 5, 10, 15, 20], [-100, 5, 10, 15, 20]]}, {'n': 4, 'scenarios': [[-180, 10, 20, 30, 40], [-20, 10, 20, 30, 40]]}, {'n': 3, 'scenarios': [[-200, 20, 40, 60], [-80, 20, 40, 60]]}, {'n': 2, 'scenarios': [[-200, 10, 20], [-120, 10, 20]]}, {'n': 2, 'scenarios': [[-160, 20, 40], [-20, 20, 40]]}, {'n': 4, 'scenarios': [[-100, 10, 20, 30, 40], [-80, 10, 20, 30, 40]]}, {'n': 3, 'scenarios': [[-120, 20, 40, 60], [-160, 20, 40, 60]]}, {'n': 2, 'scenarios': [[-180, 5, 10], [-200, 5, 10]]}, {'n': 2, 'scenarios': [[-40, 20, 40], [-200, 20, 40]]}, {'n': 2, 'scenarios': [[-120, 20, 40], [-200, 20, 40]]}, {'n': 2, 'scenarios': [[-200, 10, 20], [-100, 10, 20]]}, {'n': 3, 'scenarios': [[-40, 20, 40, 60], [-120, 20, 40, 60]]}, {'n': 4, 'scenarios': [[-20, 20, 40, 60, 80], [-160, 20, 40, 60, 80]]}, {'n': 2, 'scenarios': [[-40, 5, 10], [-160, 5, 10]]}, {'n': 4, 'scenarios': [[-100, 20, 40, 60, 80], [-140, 20, 40, 60, 80]]}, {'n': 3, 'scenarios': [[-80, 5, 10, 15], [-100, 5, 10, 15]]}, {'n': 4, 'scenarios': [[-120, 5, 10, 15, 20], [-160, 5, 10, 15, 20]]}, {'n': 2, 'scenarios': [[-120, 10, 20], [-20, 10, 20]]}, {'n': 2, 'scenarios': [[-200, 5, 10], [-100, 5, 10]]}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['coin_payout_expectation'], 'domain_operation': 'coin_payout_expectation', 'problem_type_id': 'coin_payout_expectation', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'n': 3, 'scenarios': [[-100, 5, 10, 15], [-60, 5, 10, 15]]}, {'n': 4, 'scenarios': [[-120, 5, 10, 15, 20], [-100, 5, 10, 15, 20]]}, {'n': 4, 'scenarios': [[-180, 10, 20, 30, 40], [-20, 10, 20, 30, 40]]}, {'n': 3, 'scenarios': [[-200, 20, 40, 60], [-80, 20, 40, 60]]}, {'n': 2, 'scenarios': [[-200, 10, 20], [-120, 10, 20]]}, {'n': 2, 'scenarios': [[-160, 20, 40], [-20, 20, 40]]}, {'n': 4, 'scenarios': [[-100, 10, 20, 30, 40], [-80, 10, 20, 30, 40]]}, {'n': 3, 'scenarios': [[-120, 20, 40, 60], [-160, 20, 40, 60]]}, {'n': 2, 'scenarios': [[-180, 5, 10], [-200, 5, 10]]}, {'n': 2, 'scenarios': [[-40, 20, 40], [-200, 20, 40]]}, {'n': 2, 'scenarios': [[-120, 20, 40], [-200, 20, 40]]}, {'n': 2, 'scenarios': [[-200, 10, 20], [-100, 10, 20]]}, {'n': 3, 'scenarios': [[-40, 20, 40, 60], [-120, 20, 40, 60]]}, {'n': 4, 'scenarios': [[-20, 20, 40, 60, 80], [-160, 20, 40, 60, 80]]}, {'n': 2, 'scenarios': [[-40, 5, 10], [-160, 5, 10]]}, {'n': 4, 'scenarios': [[-100, 20, 40, 60, 80], [-140, 20, 40, 60, 80]]}, {'n': 3, 'scenarios': [[-80, 5, 10, 15], [-100, 5, 10, 15]]}, {'n': 4, 'scenarios': [[-120, 5, 10, 15, 20], [-160, 5, 10, 15, 20]]}, {'n': 2, 'scenarios': [[-120, 10, 20], [-20, 10, 20]]}, {'n': 2, 'scenarios': [[-200, 5, 10], [-100, 5, 10]]}]}}, 'problem_type_id': 'coin_payout_expectation', 'required_capabilities': ['coin_payout_expectation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'n': 3, 'scenarios': [[-100, 5, 10, 15], [-60, 5, 10, 15]]}, {'n': 4, 'scenarios': [[-120, 5, 10, 15, 20], [-100, 5, 10, 15, 20]]}, {'n': 4, 'scenarios': [[-180, 10, 20, 30, 40], [-20, 10, 20, 30, 40]]}, {'n': 3, 'scenarios': [[-200, 20, 40, 60], [-80, 20, 40, 60]]}, {'n': 2, 'scenarios': [[-200, 10, 20], [-120, 10, 20]]}, {'n': 2, 'scenarios': [[-160, 20, 40], [-20, 20, 40]]}, {'n': 4, 'scenarios': [[-100, 10, 20, 30, 40], [-80, 10, 20, 30, 40]]}, {'n': 3, 'scenarios': [[-120, 20, 40, 60], [-160, 20, 40, 60]]}, {'n': 2, 'scenarios': [[-180, 5, 10], [-200, 5, 10]]}, {'n': 2, 'scenarios': [[-40, 20, 40], [-200, 20, 40]]}, {'n': 2, 'scenarios': [[-120, 20, 40], [-200, 20, 40]]}, {'n': 2, 'scenarios': [[-200, 10, 20], [-100, 10, 20]]}, {'n': 3, 'scenarios': [[-40, 20, 40, 60], [-120, 20, 40, 60]]}, {'n': 4, 'scenarios': [[-20, 20, 40, 60, 80], [-160, 20, 40, 60, 80]]}, {'n': 2, 'scenarios': [[-40, 5, 10], [-160, 5, 10]]}, {'n': 4, 'scenarios': [[-100, 20, 40, 60, 80], [-140, 20, 40, 60, 80]]}, {'n': 3, 'scenarios': [[-80, 5, 10, 15], [-100, 5, 10, 15]]}, {'n': 4, 'scenarios': [[-120, 5, 10, 15, 20], [-160, 5, 10, 15, 20]]}, {'n': 2, 'scenarios': [[-120, 10, 20], [-20, 10, 20]]}, {'n': 2, 'scenarios': [[-200, 5, 10], [-100, 5, 10]]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MathematicalExpectation', 'fixed_domain_key': 'discrete.mathematical_expectation', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['coin_payout_expectation'], 'matched_capabilities': ['coin_payout_expectation'], 'selected_operation': 'coin_payout_expectation', 'registry_revision': 'promoted-a714bd66521e', 'domain_module': 'core.domain.promoted.mathematical_expectation.mathematical_expectation_domain', 'entrypoint': 'build_mathematical_expectation_matrix', 'allowed_operations': ['coin_payout_expectation', 'decision_by_expectation', 'die_payout_expectation', 'expectation_claim', 'insurance_expectation', 'lottery_expectation', 'multiple_choice_guess_expectation', 'prize_ball_expectation', 'single_die_game', 'two_dice_match_game', 'urn_draw_expectation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MathematicalExpectation'}), seed)
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
