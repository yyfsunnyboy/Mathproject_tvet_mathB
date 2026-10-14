from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_SubSection_4_5_1'
GENERATOR_KEYS = ['src_12221', 'src_12222', 'src_12223', 'src_12224', 'src_12238', 'src_12265']
GENERATOR_SPECS = [{'textbook_example_id': 12221, 'component_id': 'src_12221', 'generator_key': 'src_12221', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'common_log_table_lookup', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'common_log_table_lookup', 'checker_key': 'multi_part', 'display_order': 12221, 'source_order': 12221, 'sampling_weight': 10.0}, {'textbook_example_id': 12222, 'component_id': 'src_12222', 'generator_key': 'src_12222', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'in_class_practice', 'line_type': 'common_log_table_lookup', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'common_log_table_lookup', 'checker_key': 'multi_part', 'display_order': 12222, 'source_order': 12222, 'sampling_weight': 10.0}, {'textbook_example_id': 12223, 'component_id': 'src_12223', 'generator_key': 'src_12223', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'common_log_table_lookup', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'common_log_table_lookup', 'checker_key': 'multi_part', 'display_order': 12223, 'source_order': 12223, 'sampling_weight': 10.0}, {'textbook_example_id': 12224, 'component_id': 'src_12224', 'generator_key': 'src_12224', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'in_class_practice', 'line_type': 'common_log_table_lookup', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'common_log_table_lookup', 'checker_key': 'multi_part', 'display_order': 12224, 'source_order': 12224, 'sampling_weight': 10.0}, {'textbook_example_id': 12238, 'component_id': 'src_12238', 'generator_key': 'src_12238', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_exercise', 'line_type': 'common_log_table_lookup', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'common_log_table_lookup', 'checker_key': 'multi_part', 'display_order': 12238, 'source_order': 12238, 'sampling_weight': 10.0}, {'textbook_example_id': 12265, 'component_id': 'src_12265', 'generator_key': 'src_12265', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'self_assessment', 'line_type': 'common_log_given_approx_eval', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'common_log_given_approx_eval', 'checker_key': 'expression', 'display_order': 12265, 'source_order': 12265, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12221': 'components/src_12221/generate.py', 'src_12222': 'components/src_12222/generate.py', 'src_12223': 'components/src_12223/generate.py', 'src_12224': 'components/src_12224/generate.py', 'src_12238': 'components/src_12238/generate.py', 'src_12265': 'components/src_12265/generate.py'}
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
