from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "simplify_exponent_expressions"
TEXTBOOK_EXAMPLE_ID = 12367
DEFAULT_COMPONENT_ID = "src_12367" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_RealExponentsAndLaws"
FIXED_DOMAIN_KEY = "algebra.exponent_laws"
DOMAIN_OPERATION = "simplify_exponent_expressions"


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

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '10'], ['sqrt', ['n', '2']]], ['pow', ['n', '100'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '2']]], ['n', '2']]]], ['pow', ['pow', ['n', '3'], ['sqrt', ['n', '2']]], ['jux', ['n', '2'], ['sqrt', ['n', '2']]]], ['mul', ['pow', ['n', '3/2'], ['jux', ['n', '2'], ['sqrt', ['n', '3']]]], ['pow', ['n', '2/3'], ['sqrt', ['n', '12']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '2'], ['sqrt', ['n', '3']]], ['pow', ['n', '4'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '3']]], ['n', '2']]]], ['pow', ['pow', ['n', '5'], ['sqrt', ['n', '5']]], ['jux', ['n', '2'], ['sqrt', ['n', '5']]]], ['mul', ['pow', ['n', '5/3'], ['jux', ['n', '2'], ['sqrt', ['n', '2']]]], ['pow', ['n', '3/5'], ['sqrt', ['n', '8']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '5'], ['sqrt', ['n', '5']]], ['pow', ['n', '25'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '5']]], ['n', '2']]]], ['pow', ['pow', ['n', '7'], ['sqrt', ['n', '2']]], ['jux', ['n', '2'], ['sqrt', ['n', '2']]]], ['mul', ['pow', ['n', '3/2'], ['jux', ['n', '2'], ['sqrt', ['n', '5']]]], ['pow', ['n', '2/3'], ['sqrt', ['n', '20']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '3'], ['sqrt', ['n', '7']]], ['pow', ['n', '9'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '7']]], ['n', '2']]]], ['pow', ['pow', ['n', '7'], ['sqrt', ['n', '5']]], ['jux', ['n', '1'], ['sqrt', ['n', '5']]]], ['mul', ['pow', ['n', '2/3'], ['jux', ['n', '2'], ['sqrt', ['n', '2']]]], ['pow', ['n', '3/2'], ['sqrt', ['n', '8']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '10'], ['sqrt', ['n', '5']]], ['pow', ['n', '100'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '5']]], ['n', '2']]]], ['pow', ['pow', ['n', '5'], ['sqrt', ['n', '2']]], ['jux', ['n', '3'], ['sqrt', ['n', '2']]]], ['mul', ['pow', ['n', '2/3'], ['jux', ['n', '2'], ['sqrt', ['n', '2']]]], ['pow', ['n', '3/2'], ['sqrt', ['n', '8']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '3'], ['sqrt', ['n', '7']]], ['pow', ['n', '9'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '7']]], ['n', '2']]]], ['pow', ['pow', ['n', '7'], ['sqrt', ['n', '2']]], ['jux', ['n', '3'], ['sqrt', ['n', '2']]]], ['mul', ['pow', ['n', '5/3'], ['jux', ['n', '3'], ['sqrt', ['n', '5']]]], ['pow', ['n', '3/5'], ['sqrt', ['n', '45']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '2'], ['sqrt', ['n', '5']]], ['pow', ['n', '4'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '5']]], ['n', '2']]]], ['pow', ['pow', ['n', '5'], ['sqrt', ['n', '5']]], ['jux', ['n', '3'], ['sqrt', ['n', '5']]]], ['mul', ['pow', ['n', '5/3'], ['jux', ['n', '2'], ['sqrt', ['n', '5']]]], ['pow', ['n', '3/5'], ['sqrt', ['n', '20']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '2'], ['sqrt', ['n', '3']]], ['pow', ['n', '4'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '3']]], ['n', '2']]]], ['pow', ['pow', ['n', '5'], ['sqrt', ['n', '2']]], ['jux', ['n', '1'], ['sqrt', ['n', '2']]]], ['mul', ['pow', ['n', '4/3'], ['jux', ['n', '2'], ['sqrt', ['n', '3']]]], ['pow', ['n', '3/4'], ['sqrt', ['n', '12']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '10'], ['sqrt', ['n', '6']]], ['pow', ['n', '100'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '6']]], ['n', '2']]]], ['pow', ['pow', ['n', '7'], ['sqrt', ['n', '5']]], ['jux', ['n', '1'], ['sqrt', ['n', '5']]]], ['mul', ['pow', ['n', '5/3'], ['jux', ['n', '2'], ['sqrt', ['n', '3']]]], ['pow', ['n', '3/5'], ['sqrt', ['n', '12']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '10'], ['sqrt', ['n', '6']]], ['pow', ['n', '100'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '6']]], ['n', '2']]]], ['pow', ['pow', ['n', '7'], ['sqrt', ['n', '3']]], ['jux', ['n', '3'], ['sqrt', ['n', '3']]]], ['mul', ['pow', ['n', '2/3'], ['jux', ['n', '2'], ['sqrt', ['n', '3']]]], ['pow', ['n', '3/2'], ['sqrt', ['n', '12']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '10'], ['sqrt', ['n', '7']]], ['pow', ['n', '100'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '7']]], ['n', '2']]]], ['pow', ['pow', ['n', '3'], ['sqrt', ['n', '5']]], ['jux', ['n', '1'], ['sqrt', ['n', '5']]]], ['mul', ['pow', ['n', '3/2'], ['jux', ['n', '3'], ['sqrt', ['n', '2']]]], ['pow', ['n', '2/3'], ['sqrt', ['n', '18']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '5'], ['sqrt', ['n', '5']]], ['pow', ['n', '25'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '5']]], ['n', '2']]]], ['pow', ['pow', ['n', '3'], ['sqrt', ['n', '5']]], ['jux', ['n', '1'], ['sqrt', ['n', '5']]]], ['mul', ['pow', ['n', '3/2'], ['jux', ['n', '2'], ['sqrt', ['n', '3']]]], ['pow', ['n', '2/3'], ['sqrt', ['n', '12']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '10'], ['sqrt', ['n', '2']]], ['pow', ['n', '100'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '2']]], ['n', '2']]]], ['pow', ['pow', ['n', '3'], ['sqrt', ['n', '5']]], ['jux', ['n', '1'], ['sqrt', ['n', '5']]]], ['mul', ['pow', ['n', '4/3'], ['jux', ['n', '2'], ['sqrt', ['n', '2']]]], ['pow', ['n', '3/4'], ['sqrt', ['n', '8']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '3'], ['sqrt', ['n', '6']]], ['pow', ['n', '9'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '6']]], ['n', '2']]]], ['pow', ['pow', ['n', '3'], ['sqrt', ['n', '5']]], ['jux', ['n', '1'], ['sqrt', ['n', '5']]]], ['mul', ['pow', ['n', '4/3'], ['jux', ['n', '2'], ['sqrt', ['n', '3']]]], ['pow', ['n', '3/4'], ['sqrt', ['n', '12']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '10'], ['sqrt', ['n', '3']]], ['pow', ['n', '100'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '3']]], ['n', '2']]]], ['pow', ['pow', ['n', '7'], ['sqrt', ['n', '2']]], ['jux', ['n', '3'], ['sqrt', ['n', '2']]]], ['mul', ['pow', ['n', '4/3'], ['jux', ['n', '3'], ['sqrt', ['n', '5']]]], ['pow', ['n', '3/4'], ['sqrt', ['n', '45']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '10'], ['sqrt', ['n', '2']]], ['pow', ['n', '100'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '2']]], ['n', '2']]]], ['pow', ['pow', ['n', '7'], ['sqrt', ['n', '5']]], ['jux', ['n', '3'], ['sqrt', ['n', '5']]]], ['mul', ['pow', ['n', '4/3'], ['jux', ['n', '3'], ['sqrt', ['n', '2']]]], ['pow', ['n', '3/4'], ['sqrt', ['n', '18']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '3'], ['sqrt', ['n', '3']]], ['pow', ['n', '9'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '3']]], ['n', '2']]]], ['pow', ['pow', ['n', '3'], ['sqrt', ['n', '5']]], ['jux', ['n', '2'], ['sqrt', ['n', '5']]]], ['mul', ['pow', ['n', '3/2'], ['jux', ['n', '2'], ['sqrt', ['n', '2']]]], ['pow', ['n', '2/3'], ['sqrt', ['n', '8']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '3'], ['sqrt', ['n', '6']]], ['pow', ['n', '9'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '6']]], ['n', '2']]]], ['pow', ['pow', ['n', '3'], ['sqrt', ['n', '2']]], ['jux', ['n', '1'], ['sqrt', ['n', '2']]]], ['mul', ['pow', ['n', '4/3'], ['jux', ['n', '2'], ['sqrt', ['n', '2']]]], ['pow', ['n', '3/4'], ['sqrt', ['n', '8']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '5'], ['sqrt', ['n', '7']]], ['pow', ['n', '25'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '7']]], ['n', '2']]]], ['pow', ['pow', ['n', '3'], ['sqrt', ['n', '3']]], ['jux', ['n', '2'], ['sqrt', ['n', '3']]]], ['mul', ['pow', ['n', '2/3'], ['jux', ['n', '3'], ['sqrt', ['n', '2']]]], ['pow', ['n', '3/2'], ['sqrt', ['n', '18']]]]]}, {'stem': '利用指數律，求下列各式的值：', 'items': [['mul', ['pow', ['n', '10'], ['sqrt', ['n', '5']]], ['pow', ['n', '100'], ['div', ['sub', ['n', '1'], ['sqrt', ['n', '5']]], ['n', '2']]]], ['pow', ['pow', ['n', '5'], ['sqrt', ['n', '2']]], ['jux', ['n', '1'], ['sqrt', ['n', '2']]]], ['mul', ['pow', ['n', '5/3'], ['jux', ['n', '2'], ['sqrt', ['n', '2']]]], ['pow', ['n', '3/5'], ['sqrt', ['n', '8']]]]]}]}}), seed)
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
