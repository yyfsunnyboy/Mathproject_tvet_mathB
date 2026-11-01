from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "die_payout_expectation"
TEXTBOOK_EXAMPLE_ID = 12903
DEFAULT_COMPONENT_ID = "src_12903" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MathematicalExpectation"
FIXED_DOMAIN_KEY = "discrete.mathematical_expectation"
DOMAIN_OPERATION = "die_payout_expectation"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['die_payout_expectation'], 'domain_operation': 'die_payout_expectation', 'problem_type_id': 'die_payout_expectation', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'style': 'linear', 'coef': 10, 'payouts': [10, 20, 30, 40, 50, 60]}, {'style': 'linear', 'coef': 55, 'payouts': [55, 110, 165, 220, 275, 330]}, {'style': 'linear', 'coef': 14, 'payouts': [14, 28, 42, 56, 70, 84]}, {'style': 'linear', 'coef': 19, 'payouts': [19, 38, 57, 76, 95, 114]}, {'style': 'linear', 'coef': 47, 'payouts': [47, 94, 141, 188, 235, 282]}, {'style': 'linear', 'coef': 30, 'payouts': [30, 60, 90, 120, 150, 180]}, {'style': 'linear', 'coef': 57, 'payouts': [57, 114, 171, 228, 285, 342]}, {'style': 'linear', 'coef': 29, 'payouts': [29, 58, 87, 116, 145, 174]}, {'style': 'linear', 'coef': 53, 'payouts': [53, 106, 159, 212, 265, 318]}, {'style': 'linear', 'coef': 21, 'payouts': [21, 42, 63, 84, 105, 126]}, {'style': 'linear', 'coef': 32, 'payouts': [32, 64, 96, 128, 160, 192]}, {'style': 'linear', 'coef': 35, 'payouts': [35, 70, 105, 140, 175, 210]}, {'style': 'linear', 'coef': 24, 'payouts': [24, 48, 72, 96, 120, 144]}, {'style': 'linear', 'coef': 3, 'payouts': [3, 6, 9, 12, 15, 18]}, {'style': 'linear', 'coef': 34, 'payouts': [34, 68, 102, 136, 170, 204]}, {'style': 'linear', 'coef': 4, 'payouts': [4, 8, 12, 16, 20, 24]}, {'style': 'linear', 'coef': 26, 'payouts': [26, 52, 78, 104, 130, 156]}, {'style': 'linear', 'coef': 12, 'payouts': [12, 24, 36, 48, 60, 72]}, {'style': 'linear', 'coef': 52, 'payouts': [52, 104, 156, 208, 260, 312]}, {'style': 'linear', 'coef': 60, 'payouts': [60, 120, 180, 240, 300, 360]}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['die_payout_expectation'], 'domain_operation': 'die_payout_expectation', 'problem_type_id': 'die_payout_expectation', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'style': 'linear', 'coef': 10, 'payouts': [10, 20, 30, 40, 50, 60]}, {'style': 'linear', 'coef': 55, 'payouts': [55, 110, 165, 220, 275, 330]}, {'style': 'linear', 'coef': 14, 'payouts': [14, 28, 42, 56, 70, 84]}, {'style': 'linear', 'coef': 19, 'payouts': [19, 38, 57, 76, 95, 114]}, {'style': 'linear', 'coef': 47, 'payouts': [47, 94, 141, 188, 235, 282]}, {'style': 'linear', 'coef': 30, 'payouts': [30, 60, 90, 120, 150, 180]}, {'style': 'linear', 'coef': 57, 'payouts': [57, 114, 171, 228, 285, 342]}, {'style': 'linear', 'coef': 29, 'payouts': [29, 58, 87, 116, 145, 174]}, {'style': 'linear', 'coef': 53, 'payouts': [53, 106, 159, 212, 265, 318]}, {'style': 'linear', 'coef': 21, 'payouts': [21, 42, 63, 84, 105, 126]}, {'style': 'linear', 'coef': 32, 'payouts': [32, 64, 96, 128, 160, 192]}, {'style': 'linear', 'coef': 35, 'payouts': [35, 70, 105, 140, 175, 210]}, {'style': 'linear', 'coef': 24, 'payouts': [24, 48, 72, 96, 120, 144]}, {'style': 'linear', 'coef': 3, 'payouts': [3, 6, 9, 12, 15, 18]}, {'style': 'linear', 'coef': 34, 'payouts': [34, 68, 102, 136, 170, 204]}, {'style': 'linear', 'coef': 4, 'payouts': [4, 8, 12, 16, 20, 24]}, {'style': 'linear', 'coef': 26, 'payouts': [26, 52, 78, 104, 130, 156]}, {'style': 'linear', 'coef': 12, 'payouts': [12, 24, 36, 48, 60, 72]}, {'style': 'linear', 'coef': 52, 'payouts': [52, 104, 156, 208, 260, 312]}, {'style': 'linear', 'coef': 60, 'payouts': [60, 120, 180, 240, 300, 360]}]}}, 'problem_type_id': 'die_payout_expectation', 'required_capabilities': ['die_payout_expectation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'style': 'linear', 'coef': 10, 'payouts': [10, 20, 30, 40, 50, 60]}, {'style': 'linear', 'coef': 55, 'payouts': [55, 110, 165, 220, 275, 330]}, {'style': 'linear', 'coef': 14, 'payouts': [14, 28, 42, 56, 70, 84]}, {'style': 'linear', 'coef': 19, 'payouts': [19, 38, 57, 76, 95, 114]}, {'style': 'linear', 'coef': 47, 'payouts': [47, 94, 141, 188, 235, 282]}, {'style': 'linear', 'coef': 30, 'payouts': [30, 60, 90, 120, 150, 180]}, {'style': 'linear', 'coef': 57, 'payouts': [57, 114, 171, 228, 285, 342]}, {'style': 'linear', 'coef': 29, 'payouts': [29, 58, 87, 116, 145, 174]}, {'style': 'linear', 'coef': 53, 'payouts': [53, 106, 159, 212, 265, 318]}, {'style': 'linear', 'coef': 21, 'payouts': [21, 42, 63, 84, 105, 126]}, {'style': 'linear', 'coef': 32, 'payouts': [32, 64, 96, 128, 160, 192]}, {'style': 'linear', 'coef': 35, 'payouts': [35, 70, 105, 140, 175, 210]}, {'style': 'linear', 'coef': 24, 'payouts': [24, 48, 72, 96, 120, 144]}, {'style': 'linear', 'coef': 3, 'payouts': [3, 6, 9, 12, 15, 18]}, {'style': 'linear', 'coef': 34, 'payouts': [34, 68, 102, 136, 170, 204]}, {'style': 'linear', 'coef': 4, 'payouts': [4, 8, 12, 16, 20, 24]}, {'style': 'linear', 'coef': 26, 'payouts': [26, 52, 78, 104, 130, 156]}, {'style': 'linear', 'coef': 12, 'payouts': [12, 24, 36, 48, 60, 72]}, {'style': 'linear', 'coef': 52, 'payouts': [52, 104, 156, 208, 260, 312]}, {'style': 'linear', 'coef': 60, 'payouts': [60, 120, 180, 240, 300, 360]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MathematicalExpectation', 'fixed_domain_key': 'discrete.mathematical_expectation', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['die_payout_expectation'], 'matched_capabilities': ['die_payout_expectation'], 'selected_operation': 'die_payout_expectation', 'registry_revision': 'promoted-a714bd66521e', 'domain_module': 'core.domain.promoted.mathematical_expectation.mathematical_expectation_domain', 'entrypoint': 'build_mathematical_expectation_matrix', 'allowed_operations': ['coin_payout_expectation', 'decision_by_expectation', 'die_payout_expectation', 'expectation_claim', 'insurance_expectation', 'lottery_expectation', 'multiple_choice_guess_expectation', 'prize_ball_expectation', 'single_die_game', 'two_dice_match_game', 'urn_draw_expectation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MathematicalExpectation'}), seed)
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
