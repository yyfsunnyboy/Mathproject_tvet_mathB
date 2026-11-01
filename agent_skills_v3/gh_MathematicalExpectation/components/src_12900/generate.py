from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "decision_by_expectation"
TEXTBOOK_EXAMPLE_ID = 12900
DEFAULT_COMPONENT_ID = "src_12900" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MathematicalExpectation"
FIXED_DOMAIN_KEY = "discrete.mathematical_expectation"
DOMAIN_OPERATION = "decision_by_expectation"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['decision_by_expectation'], 'domain_operation': 'decision_by_expectation', 'problem_type_id': 'decision_by_expectation', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[40, 15, -10], [55, 10, -30]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.3', '0.5', '0.2'], 'profits': [[38, 14, -17], [73, 12, -15]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.3', '0.5', '0.2'], 'profits': [[58, 6, -13], [68, 2, -32]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[38, 23, -20], [41, 16, -26]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[28, 12, -6], [47, 3, -30]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[27, 15, -6], [52, 5, -33]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.2', '0.6', '0.2'], 'profits': [[52, 6, -5], [54, 15, -33]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[39, 10, -20], [59, 3, -22]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.5', '0.3', '0.2'], 'profits': [[35, 12, -5], [43, 15, -34]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[50, 23, -9], [68, 10, -21]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[36, 22, -8], [41, 6, -19]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[33, 18, -20], [69, 15, -19]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[28, 5, -14], [34, 12, -36]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[22, 25, -7], [53, 17, -31]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.3', '0.4', '0.3'], 'profits': [[36, 14, -9], [32, 3, -34]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[49, 15, -10], [75, 0, -33]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[56, 14, -11], [58, 16, -19]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[42, 24, -17], [37, 4, -27]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[52, 22, -14], [65, 6, -31]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[23, 6, -14], [31, 19, -38]]}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['decision_by_expectation'], 'domain_operation': 'decision_by_expectation', 'problem_type_id': 'decision_by_expectation', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[40, 15, -10], [55, 10, -30]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.3', '0.5', '0.2'], 'profits': [[38, 14, -17], [73, 12, -15]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.3', '0.5', '0.2'], 'profits': [[58, 6, -13], [68, 2, -32]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[38, 23, -20], [41, 16, -26]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[28, 12, -6], [47, 3, -30]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[27, 15, -6], [52, 5, -33]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.2', '0.6', '0.2'], 'profits': [[52, 6, -5], [54, 15, -33]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[39, 10, -20], [59, 3, -22]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.5', '0.3', '0.2'], 'profits': [[35, 12, -5], [43, 15, -34]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[50, 23, -9], [68, 10, -21]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[36, 22, -8], [41, 6, -19]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[33, 18, -20], [69, 15, -19]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[28, 5, -14], [34, 12, -36]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[22, 25, -7], [53, 17, -31]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.3', '0.4', '0.3'], 'profits': [[36, 14, -9], [32, 3, -34]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[49, 15, -10], [75, 0, -33]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[56, 14, -11], [58, 16, -19]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[42, 24, -17], [37, 4, -27]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[52, 22, -14], [65, 6, -31]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[23, 6, -14], [31, 19, -38]]}]}}, 'problem_type_id': 'decision_by_expectation', 'required_capabilities': ['decision_by_expectation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[40, 15, -10], [55, 10, -30]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.3', '0.5', '0.2'], 'profits': [[38, 14, -17], [73, 12, -15]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.3', '0.5', '0.2'], 'profits': [[58, 6, -13], [68, 2, -32]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[38, 23, -20], [41, 16, -26]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[28, 12, -6], [47, 3, -30]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[27, 15, -6], [52, 5, -33]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.2', '0.6', '0.2'], 'profits': [[52, 6, -5], [54, 15, -33]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[39, 10, -20], [59, 3, -22]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.5', '0.3', '0.2'], 'profits': [[35, 12, -5], [43, 15, -34]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[50, 23, -9], [68, 10, -21]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[36, 22, -8], [41, 6, -19]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[33, 18, -20], [69, 15, -19]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[28, 5, -14], [34, 12, -36]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[22, 25, -7], [53, 17, -31]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.3', '0.4', '0.3'], 'profits': [[36, 14, -9], [32, 3, -34]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[49, 15, -10], [75, 0, -33]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.6', '0.3', '0.1'], 'profits': [[56, 14, -11], [58, 16, -19]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.4', '0.5', '0.1'], 'profits': [[42, 24, -17], [37, 4, -27]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[52, 22, -14], [65, 6, -31]]}, {'states': ['成長', '持平', '衰退'], 'probs': ['0.25', '0.5', '0.25'], 'profits': [[23, 6, -14], [31, 19, -38]]}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MathematicalExpectation', 'fixed_domain_key': 'discrete.mathematical_expectation', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['decision_by_expectation'], 'matched_capabilities': ['decision_by_expectation'], 'selected_operation': 'decision_by_expectation', 'registry_revision': 'promoted-a714bd66521e', 'domain_module': 'core.domain.promoted.mathematical_expectation.mathematical_expectation_domain', 'entrypoint': 'build_mathematical_expectation_matrix', 'allowed_operations': ['coin_payout_expectation', 'decision_by_expectation', 'die_payout_expectation', 'expectation_claim', 'insurance_expectation', 'lottery_expectation', 'multiple_choice_guess_expectation', 'prize_ball_expectation', 'single_die_game', 'two_dice_match_game', 'urn_draw_expectation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MathematicalExpectation'}), seed)
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
