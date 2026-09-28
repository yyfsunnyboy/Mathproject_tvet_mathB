from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_SubSection_3_3_4'
GENERATOR_KEYS = ['src_12092', 'src_12093', 'src_12094', 'src_12095', 'src_12096', 'src_12105', 'src_12106', 'src_12115', 'src_12125']
GENERATOR_SPECS = [{'textbook_example_id': 12092, 'component_id': 'src_12092', 'generator_key': 'src_12092', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'lp_application', 'checker_key': 'expression', 'display_order': 12092, 'source_order': 12092, 'sampling_weight': 10.0}, {'textbook_example_id': 12093, 'component_id': 'src_12093', 'generator_key': 'src_12093', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'lp_application', 'checker_key': 'expression', 'display_order': 12093, 'source_order': 12093, 'sampling_weight': 10.0}, {'textbook_example_id': 12094, 'component_id': 'src_12094', 'generator_key': 'src_12094', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'lp_application', 'checker_key': 'expression', 'display_order': 12094, 'source_order': 12094, 'sampling_weight': 10.0}, {'textbook_example_id': 12095, 'component_id': 'src_12095', 'generator_key': 'src_12095', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'lp_application', 'checker_key': 'expression', 'display_order': 12095, 'source_order': 12095, 'sampling_weight': 10.0}, {'textbook_example_id': 12096, 'component_id': 'src_12096', 'generator_key': 'src_12096', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'exam_practice', 'line_type': 'lp_application', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'lp_application', 'checker_key': 'single_choice', 'display_order': 12096, 'source_order': 12096, 'sampling_weight': 10.0}, {'textbook_example_id': 12105, 'component_id': 'src_12105', 'generator_key': 'src_12105', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'lp_application', 'checker_key': 'expression', 'display_order': 12105, 'source_order': 12105, 'sampling_weight': 10.0}, {'textbook_example_id': 12106, 'component_id': 'src_12106', 'generator_key': 'src_12106', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'lp_application', 'checker_key': 'expression', 'display_order': 12106, 'source_order': 12106, 'sampling_weight': 10.0}, {'textbook_example_id': 12115, 'component_id': 'src_12115', 'generator_key': 'src_12115', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'constraint_system_choice', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'constraint_system_choice', 'checker_key': 'single_choice', 'display_order': 12115, 'source_order': 12115, 'sampling_weight': 10.0}, {'textbook_example_id': 12125, 'component_id': 'src_12125', 'generator_key': 'src_12125', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'constraint_system_choice', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'constraint_system_choice', 'checker_key': 'single_choice', 'display_order': 12125, 'source_order': 12125, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12092': 'components/src_12092/generate.py', 'src_12093': 'components/src_12093/generate.py', 'src_12094': 'components/src_12094/generate.py', 'src_12095': 'components/src_12095/generate.py', 'src_12096': 'components/src_12096/generate.py', 'src_12105': 'components/src_12105/generate.py', 'src_12106': 'components/src_12106/generate.py', 'src_12115': 'components/src_12115/generate.py', 'src_12125': 'components/src_12125/generate.py'}
_V3_ROOT = Path(__file__).resolve().parent


def _load_component_module(component_id: str, module_filename: str) -> Any:
    path = _V3_ROOT / "components" / component_id / module_filename
    spec = importlib.util.spec_from_file_location(f"v3_{SKILL_ID}_{component_id}_{module_filename}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"component_module_not_found:{component_id}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate(level: int = 1, seed: int | None = None, component_id: str | None = None, **kwargs: Any) -> dict[str, Any]:
    picked = component_id or kwargs.get("component_id") or GENERATOR_KEYS[0]
    module = _load_component_module(str(picked), "generate.py")
    payload = module.generate(level=level, seed=seed, component_id=picked, **kwargs)
    if isinstance(payload, dict):
        payload["component_id"] = picked
        payload.setdefault("skill_id", SKILL_ID)
    return payload


def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> Any:
    from core.gencode.runtime_skill_wrapper import check_answer
    return check_answer(user_answer, correct_answer, payload=dict(question_payload or {}))


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    payload = dict(question_payload or {})
    component_id = str(payload.get("component_id") or "")
    if component_id in _COMPONENT_DISPATCH:
        module = _load_component_module(component_id, "get_hint.py")
        return str(module.get_hint(step, payload) or "")
    return ""
