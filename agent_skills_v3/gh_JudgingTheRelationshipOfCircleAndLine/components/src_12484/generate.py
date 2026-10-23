from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "numeric_or_radical"
PROBLEM_TYPE_ID = "solve_chord_and_distance"
TEXTBOOK_EXAMPLE_ID = 12484
DEFAULT_COMPONENT_ID = "src_12484" if TEXTBOOK_EXAMPLE_ID else ""
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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.circle_line_relations', 'required_capabilities': ['solve_chord_and_distance'], 'domain_operation': 'solve_chord_and_distance', 'problem_type_id': 'solve_chord_and_distance', 'presentation_mode': 'short_answer', 'answer_type': 'numeric_or_radical', 'generation_constraints': {'variants': [{'circle': {'center': [2, 3], 'r2': 25}, 'line': [3, -4, 21], 'asks': ['chord']}, {'circle': {'center': [0, -1], 'r2': 23}, 'line': [3, -4, 6], 'asks': ['chord']}, {'circle': {'center': [-4, -1], 'r2': 27}, 'line': [8, 15, 132], 'asks': ['chord']}, {'circle': {'center': [2, 0], 'r2': 22}, 'line': [15, -8, -13], 'asks': ['chord']}, {'circle': {'center': [-3, -3], 'r2': 53}, 'line': [4, 3, 46], 'asks': ['chord']}, {'circle': {'center': [0, -2], 'r2': 26}, 'line': [12, 5, 62], 'asks': ['chord']}, {'circle': {'center': [-1, 1], 'r2': 8}, 'line': [15, -8, 40], 'asks': ['chord']}, {'circle': {'center': [1, 2], 'r2': 23}, 'line': [3, -4, 25], 'asks': ['chord']}, {'circle': {'center': [2, 0], 'r2': 23}, 'line': [5, -12, -23], 'asks': ['chord']}, {'circle': {'center': [-4, 4], 'r2': 9}, 'line': [5, 12, -54], 'asks': ['chord']}, {'circle': {'center': [3, 3], 'r2': 52}, 'line': [12, 5, -116], 'asks': ['chord']}, {'circle': {'center': [-2, 2], 'r2': 33}, 'line': [8, -15, 12], 'asks': ['chord']}, {'circle': {'center': [-3, -1], 'r2': 35}, 'line': [4, 3, 40], 'asks': ['chord']}, {'circle': {'center': [-2, 0], 'r2': 7}, 'line': [5, -12, 36], 'asks': ['chord']}, {'circle': {'center': [-2, 4], 'r2': 54}, 'line': [4, -3, -5], 'asks': ['chord']}, {'circle': {'center': [4, 0], 'r2': 50}, 'line': [15, 8, 25], 'asks': ['chord']}, {'circle': {'center': [1, -2], 'r2': 36}, 'line': [3, -4, -31], 'asks': ['chord']}, {'circle': {'center': [0, 2], 'r2': 14}, 'line': [3, 4, -18], 'asks': ['chord']}, {'circle': {'center': [-4, 2], 'r2': 23}, 'line': [12, 5, 25], 'asks': ['chord']}, {'circle': {'center': [0, 0], 'r2': 33}, 'line': [12, -5, -65], 'asks': ['chord']}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.circle_line_relations', 'required_capabilities': ['solve_chord_and_distance'], 'domain_operation': 'solve_chord_and_distance', 'problem_type_id': 'solve_chord_and_distance', 'presentation_mode': 'short_answer', 'answer_type': 'numeric_or_radical', 'generation_constraints': {'variants': [{'circle': {'center': [2, 3], 'r2': 25}, 'line': [3, -4, 21], 'asks': ['chord']}, {'circle': {'center': [0, -1], 'r2': 23}, 'line': [3, -4, 6], 'asks': ['chord']}, {'circle': {'center': [-4, -1], 'r2': 27}, 'line': [8, 15, 132], 'asks': ['chord']}, {'circle': {'center': [2, 0], 'r2': 22}, 'line': [15, -8, -13], 'asks': ['chord']}, {'circle': {'center': [-3, -3], 'r2': 53}, 'line': [4, 3, 46], 'asks': ['chord']}, {'circle': {'center': [0, -2], 'r2': 26}, 'line': [12, 5, 62], 'asks': ['chord']}, {'circle': {'center': [-1, 1], 'r2': 8}, 'line': [15, -8, 40], 'asks': ['chord']}, {'circle': {'center': [1, 2], 'r2': 23}, 'line': [3, -4, 25], 'asks': ['chord']}, {'circle': {'center': [2, 0], 'r2': 23}, 'line': [5, -12, -23], 'asks': ['chord']}, {'circle': {'center': [-4, 4], 'r2': 9}, 'line': [5, 12, -54], 'asks': ['chord']}, {'circle': {'center': [3, 3], 'r2': 52}, 'line': [12, 5, -116], 'asks': ['chord']}, {'circle': {'center': [-2, 2], 'r2': 33}, 'line': [8, -15, 12], 'asks': ['chord']}, {'circle': {'center': [-3, -1], 'r2': 35}, 'line': [4, 3, 40], 'asks': ['chord']}, {'circle': {'center': [-2, 0], 'r2': 7}, 'line': [5, -12, 36], 'asks': ['chord']}, {'circle': {'center': [-2, 4], 'r2': 54}, 'line': [4, -3, -5], 'asks': ['chord']}, {'circle': {'center': [4, 0], 'r2': 50}, 'line': [15, 8, 25], 'asks': ['chord']}, {'circle': {'center': [1, -2], 'r2': 36}, 'line': [3, -4, -31], 'asks': ['chord']}, {'circle': {'center': [0, 2], 'r2': 14}, 'line': [3, 4, -18], 'asks': ['chord']}, {'circle': {'center': [-4, 2], 'r2': 23}, 'line': [12, 5, 25], 'asks': ['chord']}, {'circle': {'center': [0, 0], 'r2': 33}, 'line': [12, -5, -65], 'asks': ['chord']}]}}, 'problem_type_id': 'solve_chord_and_distance', 'required_capabilities': ['solve_chord_and_distance'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'circle': {'center': [2, 3], 'r2': 25}, 'line': [3, -4, 21], 'asks': ['chord']}, {'circle': {'center': [0, -1], 'r2': 23}, 'line': [3, -4, 6], 'asks': ['chord']}, {'circle': {'center': [-4, -1], 'r2': 27}, 'line': [8, 15, 132], 'asks': ['chord']}, {'circle': {'center': [2, 0], 'r2': 22}, 'line': [15, -8, -13], 'asks': ['chord']}, {'circle': {'center': [-3, -3], 'r2': 53}, 'line': [4, 3, 46], 'asks': ['chord']}, {'circle': {'center': [0, -2], 'r2': 26}, 'line': [12, 5, 62], 'asks': ['chord']}, {'circle': {'center': [-1, 1], 'r2': 8}, 'line': [15, -8, 40], 'asks': ['chord']}, {'circle': {'center': [1, 2], 'r2': 23}, 'line': [3, -4, 25], 'asks': ['chord']}, {'circle': {'center': [2, 0], 'r2': 23}, 'line': [5, -12, -23], 'asks': ['chord']}, {'circle': {'center': [-4, 4], 'r2': 9}, 'line': [5, 12, -54], 'asks': ['chord']}, {'circle': {'center': [3, 3], 'r2': 52}, 'line': [12, 5, -116], 'asks': ['chord']}, {'circle': {'center': [-2, 2], 'r2': 33}, 'line': [8, -15, 12], 'asks': ['chord']}, {'circle': {'center': [-3, -1], 'r2': 35}, 'line': [4, 3, 40], 'asks': ['chord']}, {'circle': {'center': [-2, 0], 'r2': 7}, 'line': [5, -12, 36], 'asks': ['chord']}, {'circle': {'center': [-2, 4], 'r2': 54}, 'line': [4, -3, -5], 'asks': ['chord']}, {'circle': {'center': [4, 0], 'r2': 50}, 'line': [15, 8, 25], 'asks': ['chord']}, {'circle': {'center': [1, -2], 'r2': 36}, 'line': [3, -4, -31], 'asks': ['chord']}, {'circle': {'center': [0, 2], 'r2': 14}, 'line': [3, 4, -18], 'asks': ['chord']}, {'circle': {'center': [-4, 2], 'r2': 23}, 'line': [12, 5, 25], 'asks': ['chord']}, {'circle': {'center': [0, 0], 'r2': 33}, 'line': [12, -5, -65], 'asks': ['chord']}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_JudgingTheRelationshipOfCircleAndLine', 'fixed_domain_key': 'analytic_geometry.circle_line_relations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_chord_and_distance'], 'matched_capabilities': ['solve_chord_and_distance'], 'selected_operation': 'solve_chord_and_distance', 'registry_revision': 'promoted-fee773daa80d', 'domain_module': 'core.domain.promoted.analytic_geometry_circle_lines.circle_line_domain', 'entrypoint': 'build_circle_line_relations_matrix', 'allowed_operations': ['classify_circle_line_relations', 'evaluate_circle_line_statement_truth', 'solve_chord_and_distance', 'solve_circle_line_parameter', 'write_circle_tangent_lines'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_JudgingTheRelationshipOfCircleAndLine'}), seed)
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
