from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "evaluate_circle_line_statement_truth"
TEXTBOOK_EXAMPLE_ID = 12493
DEFAULT_COMPONENT_ID = "src_12493" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_JudgingTheRelationshipOfCircleAndLine"
FIXED_DOMAIN_KEY = "analytic_geometry.circle_line_relations"
DOMAIN_OPERATION = "evaluate_circle_line_statement_truth"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.circle_line_relations', 'required_capabilities': ['evaluate_circle_line_statement_truth'], 'domain_operation': 'evaluate_circle_line_statement_truth', 'problem_type_id': 'evaluate_circle_line_statement_truth', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'statement': {'kind': 'tangent_to_both_axes', 'center': [2, -2], 'r2': 4}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-8, -5], 'r2': 25}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-2, -1], 'r2': 1}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [1, 4], 'r2': 1}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-3, -6], 'r2': 9}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [4, 4], 'r2': 16}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [9, 6], 'r2': 36}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [6, -8], 'r2': 36}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-5, -5], 'r2': 25}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-4, -4], 'r2': 16}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-1, 1], 'r2': 1}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [6, 8], 'r2': 36}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-4, 4], 'r2': 16}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [2, -4], 'r2': 4}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [1, 1], 'r2': 1}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-7, -5], 'r2': 25}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-6, -6], 'r2': 36}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-8, 5], 'r2': 25}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-3, 5], 'r2': 9}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-2, -5], 'r2': 4}}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.circle_line_relations', 'required_capabilities': ['evaluate_circle_line_statement_truth'], 'domain_operation': 'evaluate_circle_line_statement_truth', 'problem_type_id': 'evaluate_circle_line_statement_truth', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'statement': {'kind': 'tangent_to_both_axes', 'center': [2, -2], 'r2': 4}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-8, -5], 'r2': 25}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-2, -1], 'r2': 1}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [1, 4], 'r2': 1}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-3, -6], 'r2': 9}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [4, 4], 'r2': 16}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [9, 6], 'r2': 36}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [6, -8], 'r2': 36}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-5, -5], 'r2': 25}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-4, -4], 'r2': 16}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-1, 1], 'r2': 1}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [6, 8], 'r2': 36}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-4, 4], 'r2': 16}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [2, -4], 'r2': 4}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [1, 1], 'r2': 1}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-7, -5], 'r2': 25}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-6, -6], 'r2': 36}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-8, 5], 'r2': 25}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-3, 5], 'r2': 9}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-2, -5], 'r2': 4}}]}}, 'problem_type_id': 'evaluate_circle_line_statement_truth', 'required_capabilities': ['evaluate_circle_line_statement_truth'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'statement': {'kind': 'tangent_to_both_axes', 'center': [2, -2], 'r2': 4}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-8, -5], 'r2': 25}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-2, -1], 'r2': 1}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [1, 4], 'r2': 1}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-3, -6], 'r2': 9}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [4, 4], 'r2': 16}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [9, 6], 'r2': 36}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [6, -8], 'r2': 36}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-5, -5], 'r2': 25}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-4, -4], 'r2': 16}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-1, 1], 'r2': 1}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [6, 8], 'r2': 36}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-4, 4], 'r2': 16}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [2, -4], 'r2': 4}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [1, 1], 'r2': 1}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-7, -5], 'r2': 25}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-6, -6], 'r2': 36}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-8, 5], 'r2': 25}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-3, 5], 'r2': 9}}, {'statement': {'kind': 'tangent_to_both_axes', 'center': [-2, -5], 'r2': 4}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_JudgingTheRelationshipOfCircleAndLine', 'fixed_domain_key': 'analytic_geometry.circle_line_relations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['evaluate_circle_line_statement_truth'], 'matched_capabilities': ['evaluate_circle_line_statement_truth'], 'selected_operation': 'evaluate_circle_line_statement_truth', 'registry_revision': 'promoted-fee773daa80d', 'domain_module': 'core.domain.promoted.analytic_geometry_circle_lines.circle_line_domain', 'entrypoint': 'build_circle_line_relations_matrix', 'allowed_operations': ['classify_circle_line_relations', 'evaluate_circle_line_statement_truth', 'solve_chord_and_distance', 'solve_circle_line_parameter', 'write_circle_tangent_lines'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_JudgingTheRelationshipOfCircleAndLine'}), seed)
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
