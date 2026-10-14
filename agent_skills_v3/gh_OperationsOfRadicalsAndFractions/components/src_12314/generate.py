from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "rational"
PROBLEM_TYPE_ID = "optimize_by_am_gm"
TEXTBOOK_EXAMPLE_ID = 12314
DEFAULT_COMPONENT_ID = "src_12314" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_OperationsOfRadicalsAndFractions"
FIXED_DOMAIN_KEY = "algebra.radical_operations"
DOMAIN_OPERATION = "optimize_by_am_gm"


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

    constraints = _materialize_generation_constraints(dict({'v3_induced_spec': {'fixed_domain_key': 'algebra.radical_operations', 'required_capabilities': ['radical_operations'], 'domain_operation': 'optimize_by_am_gm', 'problem_type_id': 'optimize_by_am_gm', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 8, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 5, 'product': 5, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 6, 'product': 150, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 5, 'product': 80, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 6, 'product': 216, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 50, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 3, 'product': 75, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 6, 'product': 54, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 32, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 4, 'product': 100, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 5, 'product': 20, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 72, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 4, 'product': 144, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 3, 'product': 3, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 4, 'product': 4, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 5, 'product': 45, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 4, 'product': 64, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 3, 'product': 12, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 2, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 6, 'product': 6, 'context': 'positive_pair'}}]}}, 'phase1_classification': {'fixed_domain_key': 'algebra.radical_operations', 'required_capabilities': ['radical_operations'], 'domain_operation': 'optimize_by_am_gm', 'problem_type_id': 'optimize_by_am_gm', 'presentation_mode': 'short_answer', 'answer_type': 'rational', 'generation_constraints': {'variants': [{'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 8, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 5, 'product': 5, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 6, 'product': 150, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 5, 'product': 80, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 6, 'product': 216, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 50, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 3, 'product': 75, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 6, 'product': 54, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 32, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 4, 'product': 100, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 5, 'product': 20, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 72, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 4, 'product': 144, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 3, 'product': 3, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 4, 'product': 4, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 5, 'product': 45, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 4, 'product': 64, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 3, 'product': 12, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 2, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 6, 'product': 6, 'context': 'positive_pair'}}]}}, 'problem_type_id': 'optimize_by_am_gm', 'required_capabilities': ['radical_operations'], 'classification_source': '', 'source_hash': '', 'presentation_mode': 'short_answer', 'answer_contract': {}, 'generation_constraints': {'variants': [{'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 8, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 5, 'product': 5, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 6, 'product': 150, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 5, 'product': 80, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 6, 'product': 216, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 50, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 3, 'product': 75, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 6, 'product': 54, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 32, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 4, 'product': 100, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 5, 'product': 20, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 72, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 4, 'product': 144, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 3, 'product': 3, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 4, 'product': 4, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 5, 'product': 45, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 4, 'product': 64, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 3, 'product': 12, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 2, 'product': 2, 'context': 'positive_pair'}}, {'problem': {'kind': 'min_linear_sum_fixed_product', 'p': 1, 'q': 6, 'product': 6, 'context': 'positive_pair'}}]}, 'exact_task_operation': '', 'domain_resolution': {'skill_id': 'gh_OperationsOfRadicalsAndFractions', 'fixed_domain_key': 'algebra.radical_operations', 'resolution_source': 'confirmed_binding', 'binding_status': 'confirmed', 'required_capabilities': [], 'matched_capabilities': [], 'selected_operation': 'optimize_by_am_gm', 'registry_revision': 'promoted-285211635de3', 'domain_module': 'core.domain.promoted.algebra_radical_operations.radical_operations_domain', 'entrypoint': 'build_radical_operations_matrix', 'allowed_operations': ['simplify_radical_fraction_expressions', 'denest_square_roots', 'evaluate_integer_fraction_part_expression', 'order_radical_numbers', 'evaluate_time_dilation_relations', 'optimize_by_am_gm', 'nearest_integer_from_radical_relation'], 'curriculum_profile': 'general_high'}, 'skill_id': 'gh_OperationsOfRadicalsAndFractions'}), seed)
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
