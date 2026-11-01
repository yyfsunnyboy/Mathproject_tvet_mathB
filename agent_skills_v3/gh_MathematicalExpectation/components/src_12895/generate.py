from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "insurance_expectation"
TEXTBOOK_EXAMPLE_ID = 12895
DEFAULT_COMPONENT_ID = "src_12895" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_MathematicalExpectation"
FIXED_DOMAIN_KEY = "discrete.mathematical_expectation"
DOMAIN_OPERATION = "insurance_expectation"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['insurance_expectation'], 'domain_operation': 'insurance_expectation', 'problem_type_id': 'insurance_expectation', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'age': 50, 'stated_prob': '0.9998', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 2400}, {'age': 45, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 6000}, {'age': 50, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 3000}, {'age': 40, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 3600}, {'age': 45, 'stated_prob': '0.9998', 'prob_kind': 'survive', 'payout': 5000000, 'ask': 'profit', 'premium': 2400}, {'age': 40, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 4000}, {'age': 50, 'stated_prob': '0.9995', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 1500}, {'age': 40, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 3600}, {'age': 50, 'stated_prob': '0.9992', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 8000}, {'age': 45, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 3600}, {'age': 60, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 6000}, {'age': 40, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 5000000, 'ask': 'profit', 'premium': 4000}, {'age': 45, 'stated_prob': '0.9998', 'prob_kind': 'survive', 'payout': 5000000, 'ask': 'profit', 'premium': 1800}, {'age': 55, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 1800}, {'age': 60, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 5000000, 'ask': 'profit', 'premium': 3600}, {'age': 60, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 5000}, {'age': 55, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 1500}, {'age': 40, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 1800}, {'age': 60, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 3600}, {'age': 45, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 3600}]}}, 'phase1_classification': {'fixed_domain_key': 'discrete.mathematical_expectation', 'required_capabilities': ['insurance_expectation'], 'domain_operation': 'insurance_expectation', 'problem_type_id': 'insurance_expectation', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'age': 50, 'stated_prob': '0.9998', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 2400}, {'age': 45, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 6000}, {'age': 50, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 3000}, {'age': 40, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 3600}, {'age': 45, 'stated_prob': '0.9998', 'prob_kind': 'survive', 'payout': 5000000, 'ask': 'profit', 'premium': 2400}, {'age': 40, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 4000}, {'age': 50, 'stated_prob': '0.9995', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 1500}, {'age': 40, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 3600}, {'age': 50, 'stated_prob': '0.9992', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 8000}, {'age': 45, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 3600}, {'age': 60, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 6000}, {'age': 40, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 5000000, 'ask': 'profit', 'premium': 4000}, {'age': 45, 'stated_prob': '0.9998', 'prob_kind': 'survive', 'payout': 5000000, 'ask': 'profit', 'premium': 1800}, {'age': 55, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 1800}, {'age': 60, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 5000000, 'ask': 'profit', 'premium': 3600}, {'age': 60, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 5000}, {'age': 55, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 1500}, {'age': 40, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 1800}, {'age': 60, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 3600}, {'age': 45, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 3600}]}}, 'problem_type_id': 'insurance_expectation', 'required_capabilities': ['insurance_expectation'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'age': 50, 'stated_prob': '0.9998', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 2400}, {'age': 45, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 6000}, {'age': 50, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 3000}, {'age': 40, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 3600}, {'age': 45, 'stated_prob': '0.9998', 'prob_kind': 'survive', 'payout': 5000000, 'ask': 'profit', 'premium': 2400}, {'age': 40, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 4000}, {'age': 50, 'stated_prob': '0.9995', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 1500}, {'age': 40, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 3600}, {'age': 50, 'stated_prob': '0.9992', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 8000}, {'age': 45, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 3600}, {'age': 60, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 6000}, {'age': 40, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 5000000, 'ask': 'profit', 'premium': 4000}, {'age': 45, 'stated_prob': '0.9998', 'prob_kind': 'survive', 'payout': 5000000, 'ask': 'profit', 'premium': 1800}, {'age': 55, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 1800}, {'age': 60, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 5000000, 'ask': 'profit', 'premium': 3600}, {'age': 60, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 3000000, 'ask': 'profit', 'premium': 5000}, {'age': 55, 'stated_prob': '0.999', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 1500}, {'age': 40, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 1800}, {'age': 60, 'stated_prob': '0.9985', 'prob_kind': 'survive', 'payout': 1000000, 'ask': 'profit', 'premium': 3600}, {'age': 45, 'stated_prob': '0.9996', 'prob_kind': 'survive', 'payout': 2000000, 'ask': 'profit', 'premium': 3600}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_MathematicalExpectation', 'fixed_domain_key': 'discrete.mathematical_expectation', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['insurance_expectation'], 'matched_capabilities': ['insurance_expectation'], 'selected_operation': 'insurance_expectation', 'registry_revision': 'promoted-a714bd66521e', 'domain_module': 'core.domain.promoted.mathematical_expectation.mathematical_expectation_domain', 'entrypoint': 'build_mathematical_expectation_matrix', 'allowed_operations': ['coin_payout_expectation', 'decision_by_expectation', 'die_payout_expectation', 'expectation_claim', 'insurance_expectation', 'lottery_expectation', 'multiple_choice_guess_expectation', 'prize_ball_expectation', 'single_die_game', 'two_dice_match_game', 'urn_draw_expectation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_MathematicalExpectation'}), seed)
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
