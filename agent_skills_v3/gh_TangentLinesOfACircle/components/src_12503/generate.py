from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "multi_part"
PROBLEM_TYPE_ID = "solve_circle_tangent_scenarios"
TEXTBOOK_EXAMPLE_ID = 12503
DEFAULT_COMPONENT_ID = "src_12503" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_TangentLinesOfACircle"
FIXED_DOMAIN_KEY = "analytic_geometry.circle_line_relations"
DOMAIN_OPERATION = "solve_circle_tangent_scenarios"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'analytic_geometry.circle_line_relations', 'required_capabilities': ['solve_circle_tangent_scenarios'], 'domain_operation': 'solve_circle_tangent_scenarios', 'problem_type_id': 'solve_circle_tangent_scenarios', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'scenario': 'building_view', 'center_y': 6, 'point': [6, 10]}, {'scenario': 'building_view', 'center_y': 2, 'point': [4, 4]}, {'scenario': 'building_view', 'center_y': 3, 'point': [3, 6]}, {'scenario': 'building_view', 'center_y': 6, 'point': [6, 13]}, {'scenario': 'building_view', 'center_y': 2, 'point': [2, 9]}, {'scenario': 'building_view', 'center_y': 8, 'point': [8, 9]}, {'scenario': 'building_view', 'center_y': 5, 'point': [5, 12]}, {'scenario': 'building_view', 'center_y': 5, 'point': [5, 7]}, {'scenario': 'building_view', 'center_y': 4, 'point': [4, 11]}, {'scenario': 'building_view', 'center_y': 6, 'point': [1, 12]}, {'scenario': 'building_view', 'center_y': 8, 'point': [8, 10]}, {'scenario': 'building_view', 'center_y': 3, 'point': [7, 6]}, {'scenario': 'building_view', 'center_y': 5, 'point': [8, 10]}, {'scenario': 'building_view', 'center_y': 3, 'point': [3, 10]}, {'scenario': 'building_view', 'center_y': 2, 'point': [2, 4]}, {'scenario': 'building_view', 'center_y': 2, 'point': [10, 7]}, {'scenario': 'building_view', 'center_y': 7, 'point': [7, 11]}, {'scenario': 'building_view', 'center_y': 2, 'point': [8, 4]}, {'scenario': 'building_view', 'center_y': 2, 'point': [5, 4]}, {'scenario': 'building_view', 'center_y': 2, 'point': [10, 4]}]}}, 'phase1_classification': {'fixed_domain_key': 'analytic_geometry.circle_line_relations', 'required_capabilities': ['solve_circle_tangent_scenarios'], 'domain_operation': 'solve_circle_tangent_scenarios', 'problem_type_id': 'solve_circle_tangent_scenarios', 'presentation_mode': 'multiple_inputs', 'answer_type': 'multi_part', 'generation_constraints': {'variants': [{'scenario': 'building_view', 'center_y': 6, 'point': [6, 10]}, {'scenario': 'building_view', 'center_y': 2, 'point': [4, 4]}, {'scenario': 'building_view', 'center_y': 3, 'point': [3, 6]}, {'scenario': 'building_view', 'center_y': 6, 'point': [6, 13]}, {'scenario': 'building_view', 'center_y': 2, 'point': [2, 9]}, {'scenario': 'building_view', 'center_y': 8, 'point': [8, 9]}, {'scenario': 'building_view', 'center_y': 5, 'point': [5, 12]}, {'scenario': 'building_view', 'center_y': 5, 'point': [5, 7]}, {'scenario': 'building_view', 'center_y': 4, 'point': [4, 11]}, {'scenario': 'building_view', 'center_y': 6, 'point': [1, 12]}, {'scenario': 'building_view', 'center_y': 8, 'point': [8, 10]}, {'scenario': 'building_view', 'center_y': 3, 'point': [7, 6]}, {'scenario': 'building_view', 'center_y': 5, 'point': [8, 10]}, {'scenario': 'building_view', 'center_y': 3, 'point': [3, 10]}, {'scenario': 'building_view', 'center_y': 2, 'point': [2, 4]}, {'scenario': 'building_view', 'center_y': 2, 'point': [10, 7]}, {'scenario': 'building_view', 'center_y': 7, 'point': [7, 11]}, {'scenario': 'building_view', 'center_y': 2, 'point': [8, 4]}, {'scenario': 'building_view', 'center_y': 2, 'point': [5, 4]}, {'scenario': 'building_view', 'center_y': 2, 'point': [10, 4]}]}}, 'problem_type_id': 'solve_circle_tangent_scenarios', 'required_capabilities': ['solve_circle_tangent_scenarios'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'multiple_inputs', 'answer_contract': {}, 'generation_constraints': {'variants': [{'scenario': 'building_view', 'center_y': 6, 'point': [6, 10]}, {'scenario': 'building_view', 'center_y': 2, 'point': [4, 4]}, {'scenario': 'building_view', 'center_y': 3, 'point': [3, 6]}, {'scenario': 'building_view', 'center_y': 6, 'point': [6, 13]}, {'scenario': 'building_view', 'center_y': 2, 'point': [2, 9]}, {'scenario': 'building_view', 'center_y': 8, 'point': [8, 9]}, {'scenario': 'building_view', 'center_y': 5, 'point': [5, 12]}, {'scenario': 'building_view', 'center_y': 5, 'point': [5, 7]}, {'scenario': 'building_view', 'center_y': 4, 'point': [4, 11]}, {'scenario': 'building_view', 'center_y': 6, 'point': [1, 12]}, {'scenario': 'building_view', 'center_y': 8, 'point': [8, 10]}, {'scenario': 'building_view', 'center_y': 3, 'point': [7, 6]}, {'scenario': 'building_view', 'center_y': 5, 'point': [8, 10]}, {'scenario': 'building_view', 'center_y': 3, 'point': [3, 10]}, {'scenario': 'building_view', 'center_y': 2, 'point': [2, 4]}, {'scenario': 'building_view', 'center_y': 2, 'point': [10, 7]}, {'scenario': 'building_view', 'center_y': 7, 'point': [7, 11]}, {'scenario': 'building_view', 'center_y': 2, 'point': [8, 4]}, {'scenario': 'building_view', 'center_y': 2, 'point': [5, 4]}, {'scenario': 'building_view', 'center_y': 2, 'point': [10, 4]}]}, 'exact_task_operation': '', 'source_choices': [{'key': 'A', 'label': 'A', 'text': '，圓弧形大廈從正面看過去，其輪廓由圓弧形與一段底座組成。圖'}, {'key': 'B', 'label': 'B', 'text': '為某一圓弧形大廈的輪廓畫在坐標平面上之設計圖，其中 \\(M\\left(0,6\\right)\\) 為圓心，弦 \\({\\overline{ AB }}\\) 為圓弧形大廈的底座。\n已知從x軸正向上一點Q仰望圖'}, {'key': 'B', 'label': 'B', 'text': '的圓弧形大廈所能看到的最高點為 \\(P\\left(6,10\\right)\\)，試回答下列問題：\n(1)直線 \\(PQ\\) 斜率為＿＿＿＿＿＿＿。\n(2)試求直線PQ的方程式。\n(3)試求Q點的坐標'}], 'domain_resolution': {'skill_id': 'gh_TangentLinesOfACircle', 'fixed_domain_key': 'analytic_geometry.circle_line_relations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['solve_circle_tangent_scenarios'], 'matched_capabilities': ['solve_circle_tangent_scenarios'], 'selected_operation': 'solve_circle_tangent_scenarios', 'registry_revision': 'promoted-fee773daa80d', 'domain_module': 'core.domain.promoted.analytic_geometry_circle_lines.circle_line_domain', 'entrypoint': 'build_circle_line_relations_matrix', 'allowed_operations': ['evaluate_circle_line_statement_truth', 'solve_circle_from_tangent_point', 'solve_circle_line_parameter', 'solve_circle_tangent_scenarios', 'write_circle_tangent_lines'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_TangentLinesOfACircle'}), seed)
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
