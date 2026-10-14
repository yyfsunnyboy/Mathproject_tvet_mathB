from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_SubSection_4_1_1'
GENERATOR_KEYS = ['src_12127', 'src_12128', 'src_12136', 'src_12145', 'src_12248']
GENERATOR_SPECS = [{'textbook_example_id': 12127, 'component_id': 'src_12127', 'generator_key': 'src_12127', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'exp_integer_power_eval', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_integer_power_eval', 'checker_key': 'multi_part', 'display_order': 12127, 'source_order': 12127, 'sampling_weight': 10.0}, {'textbook_example_id': 12128, 'component_id': 'src_12128', 'generator_key': 'src_12128', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'in_class_practice', 'line_type': 'exp_integer_power_eval', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_integer_power_eval', 'checker_key': 'multi_part', 'display_order': 12128, 'source_order': 12128, 'sampling_weight': 10.0}, {'textbook_example_id': 12136, 'component_id': 'src_12136', 'generator_key': 'src_12136', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_exercise', 'line_type': 'exp_integer_power_eval', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'exp_integer_power_eval', 'checker_key': 'multi_part', 'display_order': 12136, 'source_order': 12136, 'sampling_weight': 10.0}, {'textbook_example_id': 12145, 'component_id': 'src_12145', 'generator_key': 'src_12145', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'advanced_exercise', 'line_type': 'exp_prime_factor_exponent', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'exp_prime_factor_exponent', 'checker_key': 'expression', 'display_order': 12145, 'source_order': 12145, 'sampling_weight': 10.0}, {'textbook_example_id': 12248, 'component_id': 'src_12248', 'generator_key': 'src_12248', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'exp_law_product_choice', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'exp_law_product_choice', 'checker_key': 'single_choice', 'display_order': 12248, 'source_order': 12248, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12127': 'components/src_12127/generate.py', 'src_12128': 'components/src_12128/generate.py', 'src_12136': 'components/src_12136/generate.py', 'src_12145': 'components/src_12145/generate.py', 'src_12248': 'components/src_12248/generate.py'}
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
