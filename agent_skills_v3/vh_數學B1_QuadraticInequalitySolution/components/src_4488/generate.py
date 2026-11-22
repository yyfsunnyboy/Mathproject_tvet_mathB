from __future__ import annotations

from typing import Any

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.slot_generators import generate_from_problem_type_spec

SKILL_ID = 'vh_數學B1_QuadraticInequalitySolution'
PROBLEM_TYPE_ID = 'integer_applied_quadratic_inequality_problem'
TEXTBOOK_EXAMPLE_ID = 4488
DEFAULT_COMPONENT_ID = 'src_4488'
PRESENTATION_MODE = 'short_answer'
ANSWER_TYPE = 'integer'


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    spec = load_problem_type_spec(SKILL_ID, PROBLEM_TYPE_ID, prefer="auto")
    if not isinstance(spec, dict):
        raise RuntimeError(f"missing_problem_type_spec:{PROBLEM_TYPE_ID}")
    spec = dict(spec)
    spec['presentation_variant'] = 'min_integer_profit'
    ac = dict(spec.get('answer_contract') or {})
    ac['answer_type'] = 'integer'
    ac['presentation_mode'] = 'short_answer'
    for stale in (
        'checker_selection_reason',
        'answer_semantics',
        'answer_shape',
        'answer_format_hint',
        'answer_format_example',
        'selected_checker',
    ):
        ac.pop(stale, None)
    if ANSWER_TYPE == 'integer':
        ac['checker'] = 'integer_checker'
        ac['checker_key'] = 'integer_checker'
        ac['equivalence_type'] = 'numeric_exact'
        ac['answer_equivalence'] = 'numeric_exact'
        ac['accepted_formats'] = ['41', '12']
        ac['answer_format_example'] = '41'
    elif ANSWER_TYPE == 'text_short':
        ac['checker'] = 'text_short_checker'
        ac['checker_key'] = 'text_short_checker'
        ac['equivalence_type'] = 'exact_string'
        ac['answer_equivalence'] = 'exact_string'
        ac['accepted_formats'] = ['10,11']
        ac['answer_format_example'] = '10,11'
    spec['answer_contract'] = ac
    spec['answer_format_hint'] = ANSWER_TYPE
    payload = generate_from_problem_type_spec(SKILL_ID, spec, seed=seed)
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    if component_id:
        payload["component_id"] = component_id
    payload["textbook_example_id"] = TEXTBOOK_EXAMPLE_ID
    payload["seed"] = seed
    payload.setdefault("problem_type_id", PROBLEM_TYPE_ID)
    payload.setdefault("presentation_mode", PRESENTATION_MODE)
    payload.setdefault("answer_type", ANSWER_TYPE)
    return payload
