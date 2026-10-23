from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "solve_chord_and_distance"
TEXTBOOK_EXAMPLE_ID = 12515
DEFAULT_COMPONENT_ID = "src_12515" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_JudgingTheRelationshipOfCircleAndLine"
FIXED_DOMAIN_KEY = "analytic_geometry.circle_line_relations"
DOMAIN_OPERATION = "solve_chord_and_distance"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.circle_line_relations', 'required_capabilities': ['solve_chord_and_distance'], 'domain_operation': 'solve_chord_and_distance', 'problem_type_id': 'solve_chord_and_distance', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'circle': {'center': [1, 2], 'r2': 9}, 'point': [2, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-2, -2], 'r2': 18}, 'point': [-4, -2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [2, 3], 'r2': 26}, 'point': [5, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-1, -1], 'r2': 17}, 'point': [-2, 1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, -2], 'r2': 10}, 'point': [3, -1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [0, -1], 'r2': 17}, 'point': [-3, 1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [0, 2], 'r2': 13}, 'point': [-1, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [2, 3], 'r2': 10}, 'point': [3, 1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [2, 2], 'r2': 19}, 'point': [4, 2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, 3], 'r2': 7}, 'point': [3, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [2, -1], 'r2': 28}, 'point': [4, 2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [0, -2], 'r2': 10}, 'point': [0, -1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [4, -1], 'r2': 23}, 'point': [1, -3], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-3, 2], 'r2': 20}, 'point': [-5, 3], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, 4], 'r2': 11}, 'point': [3, 2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, -1], 'r2': 19}, 'point': [5, 2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-1, 4], 'r2': 13}, 'point': [1, 5], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-2, 2], 'r2': 26}, 'point': [1, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [0, 3], 'r2': 7}, 'point': [1, 1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, -4], 'r2': 18}, 'point': [4, -5], 'asks': ['shortest_chord', 'shortest_chord_line']}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.circle_line_relations', 'required_capabilities': ['solve_chord_and_distance'], 'domain_operation': 'solve_chord_and_distance', 'problem_type_id': 'solve_chord_and_distance', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'circle': {'center': [1, 2], 'r2': 9}, 'point': [2, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-2, -2], 'r2': 18}, 'point': [-4, -2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [2, 3], 'r2': 26}, 'point': [5, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-1, -1], 'r2': 17}, 'point': [-2, 1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, -2], 'r2': 10}, 'point': [3, -1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [0, -1], 'r2': 17}, 'point': [-3, 1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [0, 2], 'r2': 13}, 'point': [-1, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [2, 3], 'r2': 10}, 'point': [3, 1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [2, 2], 'r2': 19}, 'point': [4, 2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, 3], 'r2': 7}, 'point': [3, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [2, -1], 'r2': 28}, 'point': [4, 2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [0, -2], 'r2': 10}, 'point': [0, -1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [4, -1], 'r2': 23}, 'point': [1, -3], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-3, 2], 'r2': 20}, 'point': [-5, 3], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, 4], 'r2': 11}, 'point': [3, 2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, -1], 'r2': 19}, 'point': [5, 2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-1, 4], 'r2': 13}, 'point': [1, 5], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-2, 2], 'r2': 26}, 'point': [1, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [0, 3], 'r2': 7}, 'point': [1, 1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, -4], 'r2': 18}, 'point': [4, -5], 'asks': ['shortest_chord', 'shortest_chord_line']}]}}, 'problem_type_id': 'solve_chord_and_distance', 'required_capabilities': ['solve_chord_and_distance'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'circle': {'center': [1, 2], 'r2': 9}, 'point': [2, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-2, -2], 'r2': 18}, 'point': [-4, -2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [2, 3], 'r2': 26}, 'point': [5, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-1, -1], 'r2': 17}, 'point': [-2, 1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, -2], 'r2': 10}, 'point': [3, -1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [0, -1], 'r2': 17}, 'point': [-3, 1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [0, 2], 'r2': 13}, 'point': [-1, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [2, 3], 'r2': 10}, 'point': [3, 1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [2, 2], 'r2': 19}, 'point': [4, 2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, 3], 'r2': 7}, 'point': [3, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [2, -1], 'r2': 28}, 'point': [4, 2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [0, -2], 'r2': 10}, 'point': [0, -1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [4, -1], 'r2': 23}, 'point': [1, -3], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-3, 2], 'r2': 20}, 'point': [-5, 3], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, 4], 'r2': 11}, 'point': [3, 2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, -1], 'r2': 19}, 'point': [5, 2], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-1, 4], 'r2': 13}, 'point': [1, 5], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [-2, 2], 'r2': 26}, 'point': [1, 4], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [0, 3], 'r2': 7}, 'point': [1, 1], 'asks': ['shortest_chord', 'shortest_chord_line']}, {'circle': {'center': [3, -4], 'r2': 18}, 'point': [4, -5], 'asks': ['shortest_chord', 'shortest_chord_line']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_JudgingTheRelationshipOfCircleAndLine', 'fixed_domain_key': 'analytic_geometry.circle_line_relations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_chord_and_distance'], 'matched_capabilities': ['solve_chord_and_distance'], 'selected_operation': 'solve_chord_and_distance', 'registry_revision': 'promoted-fee773daa80d', 'domain_module': 'core.domain.promoted.analytic_geometry_circle_lines.circle_line_domain', 'entrypoint': 'build_circle_line_relations_matrix', 'allowed_operations': ['classify_circle_line_relations', 'evaluate_circle_line_statement_truth', 'solve_chord_and_distance', 'solve_circle_line_parameter', 'write_circle_tangent_lines'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_JudgingTheRelationshipOfCircleAndLine'}), seed)
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
