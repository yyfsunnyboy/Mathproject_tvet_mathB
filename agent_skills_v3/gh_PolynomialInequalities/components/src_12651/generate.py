from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "polynomial_statements"
TEXTBOOK_EXAMPLE_ID = 12651
DEFAULT_COMPONENT_ID = "src_12651" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_PolynomialInequalities"
FIXED_DOMAIN_KEY = "inequality.polynomial"
DOMAIN_OPERATION = "polynomial_statements"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'inequality.polynomial', 'required_capabilities': ['polynomial_statements'], 'domain_operation': 'polynomial_statements', 'problem_type_id': 'polynomial_statements', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-2, 0]}, 'rel': '>', 'right': {'poly': [3]}}, 'claim': 'x>-3/2'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '<=', 'right': {'poly': [3]}}, 'claim': 'x>=3/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-5, 0]}, 'rel': '<=', 'right': {'poly': [4]}}, 'claim': 'x>=-4/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '<', 'right': {'poly': [5]}}, 'claim': 'x>5/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '<', 'right': {'poly': [5]}}, 'claim': 'x<5/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-4, 0]}, 'rel': '>=', 'right': {'poly': [-3]}}, 'claim': 'x<=3/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [1, 0]}, 'rel': '>=', 'right': {'poly': [6]}}, 'claim': 'x<=6'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [3, 0]}, 'rel': '<=', 'right': {'poly': [9]}}, 'claim': 'x<=3'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [5, 0]}, 'rel': '<', 'right': {'poly': [2]}}, 'claim': 'x>2/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-5, 0]}, 'rel': '<', 'right': {'poly': [-8]}}, 'claim': 'x>8/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [3, 0]}, 'rel': '<=', 'right': {'poly': [6]}}, 'claim': 'x>=2'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [5, 0]}, 'rel': '<=', 'right': {'poly': [-4]}}, 'claim': 'x>=-4/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [3, 0]}, 'rel': '>', 'right': {'poly': [9]}}, 'claim': 'x<3'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [5, 0]}, 'rel': '>=', 'right': {'poly': [9]}}, 'claim': 'x<=9/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [1, 0]}, 'rel': '>=', 'right': {'poly': [-4]}}, 'claim': 'x>=-4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '>', 'right': {'poly': [-6]}}, 'claim': 'x<-3/2'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-2, 0]}, 'rel': '>', 'right': {'poly': [2]}}, 'claim': 'x>-1'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '>', 'right': {'poly': [-9]}}, 'claim': 'x<-9/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-1, 0]}, 'rel': '>=', 'right': {'poly': [-4]}}, 'claim': 'x<=4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '>', 'right': {'poly': [8]}}, 'claim': 'x<2'}], 'mode': 'truth'}]}}, 'phase1_classification': {'fixed_domain_key': 'inequality.polynomial', 'required_capabilities': ['polynomial_statements'], 'domain_operation': 'polynomial_statements', 'problem_type_id': 'polynomial_statements', 'presentation_mode': 'single_choice', 'answer_type': 'single_choice', 'generation_constraints': {'variants': [{'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-2, 0]}, 'rel': '>', 'right': {'poly': [3]}}, 'claim': 'x>-3/2'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '<=', 'right': {'poly': [3]}}, 'claim': 'x>=3/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-5, 0]}, 'rel': '<=', 'right': {'poly': [4]}}, 'claim': 'x>=-4/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '<', 'right': {'poly': [5]}}, 'claim': 'x>5/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '<', 'right': {'poly': [5]}}, 'claim': 'x<5/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-4, 0]}, 'rel': '>=', 'right': {'poly': [-3]}}, 'claim': 'x<=3/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [1, 0]}, 'rel': '>=', 'right': {'poly': [6]}}, 'claim': 'x<=6'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [3, 0]}, 'rel': '<=', 'right': {'poly': [9]}}, 'claim': 'x<=3'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [5, 0]}, 'rel': '<', 'right': {'poly': [2]}}, 'claim': 'x>2/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-5, 0]}, 'rel': '<', 'right': {'poly': [-8]}}, 'claim': 'x>8/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [3, 0]}, 'rel': '<=', 'right': {'poly': [6]}}, 'claim': 'x>=2'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [5, 0]}, 'rel': '<=', 'right': {'poly': [-4]}}, 'claim': 'x>=-4/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [3, 0]}, 'rel': '>', 'right': {'poly': [9]}}, 'claim': 'x<3'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [5, 0]}, 'rel': '>=', 'right': {'poly': [9]}}, 'claim': 'x<=9/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [1, 0]}, 'rel': '>=', 'right': {'poly': [-4]}}, 'claim': 'x>=-4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '>', 'right': {'poly': [-6]}}, 'claim': 'x<-3/2'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-2, 0]}, 'rel': '>', 'right': {'poly': [2]}}, 'claim': 'x>-1'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '>', 'right': {'poly': [-9]}}, 'claim': 'x<-9/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-1, 0]}, 'rel': '>=', 'right': {'poly': [-4]}}, 'claim': 'x<=4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '>', 'right': {'poly': [8]}}, 'claim': 'x<2'}], 'mode': 'truth'}]}}, 'problem_type_id': 'polynomial_statements', 'required_capabilities': ['polynomial_statements'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'single_choice', 'answer_contract': {}, 'generation_constraints': {'variants': [{'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-2, 0]}, 'rel': '>', 'right': {'poly': [3]}}, 'claim': 'x>-3/2'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '<=', 'right': {'poly': [3]}}, 'claim': 'x>=3/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-5, 0]}, 'rel': '<=', 'right': {'poly': [4]}}, 'claim': 'x>=-4/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '<', 'right': {'poly': [5]}}, 'claim': 'x>5/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '<', 'right': {'poly': [5]}}, 'claim': 'x<5/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-4, 0]}, 'rel': '>=', 'right': {'poly': [-3]}}, 'claim': 'x<=3/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [1, 0]}, 'rel': '>=', 'right': {'poly': [6]}}, 'claim': 'x<=6'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [3, 0]}, 'rel': '<=', 'right': {'poly': [9]}}, 'claim': 'x<=3'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [5, 0]}, 'rel': '<', 'right': {'poly': [2]}}, 'claim': 'x>2/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-5, 0]}, 'rel': '<', 'right': {'poly': [-8]}}, 'claim': 'x>8/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [3, 0]}, 'rel': '<=', 'right': {'poly': [6]}}, 'claim': 'x>=2'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [5, 0]}, 'rel': '<=', 'right': {'poly': [-4]}}, 'claim': 'x>=-4/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [3, 0]}, 'rel': '>', 'right': {'poly': [9]}}, 'claim': 'x<3'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [5, 0]}, 'rel': '>=', 'right': {'poly': [9]}}, 'claim': 'x<=9/5'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [1, 0]}, 'rel': '>=', 'right': {'poly': [-4]}}, 'claim': 'x>=-4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '>', 'right': {'poly': [-6]}}, 'claim': 'x<-3/2'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-2, 0]}, 'rel': '>', 'right': {'poly': [2]}}, 'claim': 'x>-1'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '>', 'right': {'poly': [-9]}}, 'claim': 'x<-9/4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [-1, 0]}, 'rel': '>=', 'right': {'poly': [-4]}}, 'claim': 'x<=4'}], 'mode': 'truth'}, {'subject': {}, 'statements': [{'kind': 'solution_claim', 'ineq': {'left': {'poly': [4, 0]}, 'rel': '>', 'right': {'poly': [8]}}, 'claim': 'x<2'}], 'mode': 'truth'}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_PolynomialInequalities', 'fixed_domain_key': 'inequality.polynomial', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': ['polynomial_statements'], 'matched_capabilities': ['polynomial_statements'], 'selected_operation': 'polynomial_statements', 'registry_revision': 'promoted-ce51ac7b8c4c', 'domain_module': 'core.domain.promoted.polynomial_inequality.polynomial_inequality_domain', 'entrypoint': 'build_polynomial_inequality_matrix', 'allowed_operations': ['polynomial_applications', 'polynomial_inequality_parameters', 'polynomial_statements', 'solve_polynomial_inequality'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_PolynomialInequalities'}), seed)
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
