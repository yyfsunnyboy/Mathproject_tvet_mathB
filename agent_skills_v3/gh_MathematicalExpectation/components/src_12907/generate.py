from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "single_die_game"
TEXTBOOK_EXAMPLE_ID = 12907
DEFAULT_COMPONENT_ID = "src_12907" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MathematicalExpectation"
FIXED_DOMAIN_KEY = "discrete.mathematical_expectation"
DOMAIN_OPERATION = "single_die_game"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['single_die_game'], 'domain_operation': 'single_die_game', 'problem_type_id': 'single_die_game', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'win_set': 'prime', 'multiplier': 3, 'fee': 4}, {'win_set': 'prime', 'multiplier': 2, 'fee': 7}, {'win_set': 'even', 'multiplier': 5, 'fee': 6}, {'win_set': 'odd', 'multiplier': 3, 'fee': 2}, {'win_set': 'odd', 'multiplier': 2, 'fee': 9}, {'win_set': 'odd', 'multiplier': 4, 'fee': 8}, {'win_set': 'even', 'multiplier': 4, 'fee': 9}, {'win_set': 'even', 'multiplier': 2, 'fee': 6}, {'win_set': 'high', 'multiplier': 2, 'fee': 2}, {'win_set': 'prime', 'multiplier': 5, 'fee': 4}, {'win_set': 'prime', 'multiplier': 5, 'fee': 8}, {'win_set': 'high', 'multiplier': 5, 'fee': 8}, {'win_set': 'prime', 'multiplier': 3, 'fee': 1}, {'win_set': 'high', 'multiplier': 4, 'fee': 2}, {'win_set': 'high', 'multiplier': 3, 'fee': 9}, {'win_set': 'prime', 'multiplier': 5, 'fee': 7}, {'win_set': 'odd', 'multiplier': 4, 'fee': 4}, {'win_set': 'odd', 'multiplier': 5, 'fee': 7}, {'win_set': 'odd', 'multiplier': 5, 'fee': 9}, {'win_set': 'even', 'multiplier': 5, 'fee': 2}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['single_die_game'], 'domain_operation': 'single_die_game', 'problem_type_id': 'single_die_game', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'win_set': 'prime', 'multiplier': 3, 'fee': 4}, {'win_set': 'prime', 'multiplier': 2, 'fee': 7}, {'win_set': 'even', 'multiplier': 5, 'fee': 6}, {'win_set': 'odd', 'multiplier': 3, 'fee': 2}, {'win_set': 'odd', 'multiplier': 2, 'fee': 9}, {'win_set': 'odd', 'multiplier': 4, 'fee': 8}, {'win_set': 'even', 'multiplier': 4, 'fee': 9}, {'win_set': 'even', 'multiplier': 2, 'fee': 6}, {'win_set': 'high', 'multiplier': 2, 'fee': 2}, {'win_set': 'prime', 'multiplier': 5, 'fee': 4}, {'win_set': 'prime', 'multiplier': 5, 'fee': 8}, {'win_set': 'high', 'multiplier': 5, 'fee': 8}, {'win_set': 'prime', 'multiplier': 3, 'fee': 1}, {'win_set': 'high', 'multiplier': 4, 'fee': 2}, {'win_set': 'high', 'multiplier': 3, 'fee': 9}, {'win_set': 'prime', 'multiplier': 5, 'fee': 7}, {'win_set': 'odd', 'multiplier': 4, 'fee': 4}, {'win_set': 'odd', 'multiplier': 5, 'fee': 7}, {'win_set': 'odd', 'multiplier': 5, 'fee': 9}, {'win_set': 'even', 'multiplier': 5, 'fee': 2}]}}, 'problem_type_id': 'single_die_game', 'required_capabilities': ['single_die_game'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'win_set': 'prime', 'multiplier': 3, 'fee': 4}, {'win_set': 'prime', 'multiplier': 2, 'fee': 7}, {'win_set': 'even', 'multiplier': 5, 'fee': 6}, {'win_set': 'odd', 'multiplier': 3, 'fee': 2}, {'win_set': 'odd', 'multiplier': 2, 'fee': 9}, {'win_set': 'odd', 'multiplier': 4, 'fee': 8}, {'win_set': 'even', 'multiplier': 4, 'fee': 9}, {'win_set': 'even', 'multiplier': 2, 'fee': 6}, {'win_set': 'high', 'multiplier': 2, 'fee': 2}, {'win_set': 'prime', 'multiplier': 5, 'fee': 4}, {'win_set': 'prime', 'multiplier': 5, 'fee': 8}, {'win_set': 'high', 'multiplier': 5, 'fee': 8}, {'win_set': 'prime', 'multiplier': 3, 'fee': 1}, {'win_set': 'high', 'multiplier': 4, 'fee': 2}, {'win_set': 'high', 'multiplier': 3, 'fee': 9}, {'win_set': 'prime', 'multiplier': 5, 'fee': 7}, {'win_set': 'odd', 'multiplier': 4, 'fee': 4}, {'win_set': 'odd', 'multiplier': 5, 'fee': 7}, {'win_set': 'odd', 'multiplier': 5, 'fee': 9}, {'win_set': 'even', 'multiplier': 5, 'fee': 2}]}, 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '當乙擲出的點數為質數時，甲須付給乙該點數 \\(3\\) 倍的金額'}, {'key': 'B', 'label': 'B', 'text': '當出現其他點數時，乙須付給甲該點數的金額。\n回答以下問題。\n(1)\t玩此遊戲一次，求乙所得金額的期望值。\n(2)\t若玩此遊戲之前乙要先付給甲 \\(4\\) 元現金，則這個遊戲公平嗎？'}], 'domain_resolution': {'skill_id': 'gh_MathematicalExpectation', 'fixed_domain_key': 'discrete.mathematical_expectation', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['single_die_game'], 'matched_capabilities': ['single_die_game'], 'selected_operation': 'single_die_game', 'registry_revision': 'promoted-a714bd66521e', 'domain_module': 'core.domain.promoted.mathematical_expectation.mathematical_expectation_domain', 'entrypoint': 'build_mathematical_expectation_matrix', 'allowed_operations': ['coin_payout_expectation', 'decision_by_expectation', 'die_payout_expectation', 'expectation_claim', 'insurance_expectation', 'lottery_expectation', 'multiple_choice_guess_expectation', 'prize_ball_expectation', 'single_die_game', 'two_dice_match_game', 'urn_draw_expectation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MathematicalExpectation'}), seed)
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
