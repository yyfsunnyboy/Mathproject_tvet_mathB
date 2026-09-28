from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_SubSection_4_1_2'
GENERATOR_KEYS = ['src_12129', 'src_12130', 'src_12137', 'src_12138', 'src_12139']
GENERATOR_SPECS = [{'textbook_example_id': 12129, 'component_id': 'src_12129', 'generator_key': 'src_12129', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'exp_integer_exponent_simplify', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_integer_exponent_simplify', 'checker_key': 'multi_part', 'display_order': 12129, 'source_order': 12129, 'sampling_weight': 10.0}, {'textbook_example_id': 12130, 'component_id': 'src_12130', 'generator_key': 'src_12130', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'in_class_practice', 'line_type': 'exp_integer_exponent_simplify', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_integer_exponent_simplify', 'checker_key': 'multi_part', 'display_order': 12130, 'source_order': 12130, 'sampling_weight': 10.0}, {'textbook_example_id': 12137, 'component_id': 'src_12137', 'generator_key': 'src_12137', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_exercise', 'line_type': 'exp_fill_integer_exponent', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_fill_integer_exponent', 'checker_key': 'multi_part', 'display_order': 12137, 'source_order': 12137, 'sampling_weight': 10.0}, {'textbook_example_id': 12138, 'component_id': 'src_12138', 'generator_key': 'src_12138', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_exercise', 'line_type': 'exp_zero_negative_eval', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_zero_negative_eval', 'checker_key': 'multi_part', 'display_order': 12138, 'source_order': 12138, 'sampling_weight': 10.0}, {'textbook_example_id': 12139, 'component_id': 'src_12139', 'generator_key': 'src_12139', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_exercise', 'line_type': 'exp_integer_exponent_simplify', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_integer_exponent_simplify', 'checker_key': 'multi_part', 'display_order': 12139, 'source_order': 12139, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12129': 'components/src_12129/generate.py', 'src_12130': 'components/src_12130/generate.py', 'src_12137': 'components/src_12137/generate.py', 'src_12138': 'components/src_12138/generate.py', 'src_12139': 'components/src_12139/generate.py'}
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
