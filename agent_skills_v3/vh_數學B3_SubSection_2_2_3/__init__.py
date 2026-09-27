from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_SubSection_2_2_3'
GENERATOR_KEYS = ['src_12003', 'src_12004', 'src_12005', 'src_12006', 'src_12016', 'src_12020', 'src_12028', 'src_12029', 'src_12030']
GENERATOR_SPECS = [{'textbook_example_id': 12003, 'component_id': 'src_12003', 'generator_key': 'src_12003', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_root_count', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_root_count', 'checker_key': 'multi_part_answer_checker', 'display_order': 12003, 'source_order': 12003, 'sampling_weight': 10.0}, {'textbook_example_id': 12004, 'component_id': 'src_12004', 'generator_key': 'src_12004', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'quadratic_root_count', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_root_count', 'checker_key': 'multi_part_answer_checker', 'display_order': 12004, 'source_order': 12004, 'sampling_weight': 10.0}, {'textbook_example_id': 12005, 'component_id': 'src_12005', 'generator_key': 'src_12005', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_parameter_equal_roots', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_parameter_equal_roots', 'checker_key': 'expression_checker', 'display_order': 12005, 'source_order': 12005, 'sampling_weight': 10.0}, {'textbook_example_id': 12006, 'component_id': 'src_12006', 'generator_key': 'src_12006', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'quadratic_parameter_no_real', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_parameter_no_real', 'checker_key': 'expression_checker', 'display_order': 12006, 'source_order': 12006, 'sampling_weight': 10.0}, {'textbook_example_id': 12016, 'component_id': 'src_12016', 'generator_key': 'src_12016', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'quadratic_root_count', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_root_count', 'checker_key': 'multi_part_answer_checker', 'display_order': 12016, 'source_order': 12016, 'sampling_weight': 10.0}, {'textbook_example_id': 12020, 'component_id': 'src_12020', 'generator_key': 'src_12020', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'quadratic_parameter_no_real', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_parameter_no_real', 'checker_key': 'expression_checker', 'display_order': 12020, 'source_order': 12020, 'sampling_weight': 10.0}, {'textbook_example_id': 12028, 'component_id': 'src_12028', 'generator_key': 'src_12028', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'quadratic_parameter_equal_roots', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'quadratic_parameter_equal_roots', 'checker_key': 'single_choice_checker', 'display_order': 12028, 'source_order': 12028, 'sampling_weight': 10.0}, {'textbook_example_id': 12029, 'component_id': 'src_12029', 'generator_key': 'src_12029', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'quadratic_parameter_no_real', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_parameter_no_real', 'checker_key': 'expression_checker', 'display_order': 12029, 'source_order': 12029, 'sampling_weight': 10.0}, {'textbook_example_id': 12030, 'component_id': 'src_12030', 'generator_key': 'src_12030', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'quadratic_parameter_two_distinct', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'quadratic_parameter_two_distinct', 'checker_key': 'single_choice_checker', 'display_order': 12030, 'source_order': 12030, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12003': 'components/src_12003/generate.py', 'src_12004': 'components/src_12004/generate.py', 'src_12005': 'components/src_12005/generate.py', 'src_12006': 'components/src_12006/generate.py', 'src_12016': 'components/src_12016/generate.py', 'src_12020': 'components/src_12020/generate.py', 'src_12028': 'components/src_12028/generate.py', 'src_12029': 'components/src_12029/generate.py', 'src_12030': 'components/src_12030/generate.py'}
_V3_ROOT = Path(__file__).resolve().parent
_RR_CURSOR = 0
_SHUFFLED_CYCLE = None


def _component_sampling_weight(component_id: str) -> float:
    for row in GENERATOR_SPECS:
        if str(row.get("component_id") or "") == component_id:
            return float(row.get("sampling_weight", 1) or 1)
    return 1.0


def _ordered_generator_keys() -> list[str]:
    specs_by_id = {str(row.get("component_id") or ""): row for row in GENERATOR_SPECS}
    return sorted(GENERATOR_KEYS, key=lambda key: (int((specs_by_id.get(key) or {}).get("display_order", 0)), key))


def _load_component_module(component_id: str, module_filename: str) -> Any:
    path = _V3_ROOT / "components" / component_id / module_filename
    module_name = f"v3_{SKILL_ID}_{component_id}_{module_filename.replace('.py', '')}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"component_module_not_found:{component_id}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pick_component_id(seed: int | None = None, component_id: str | None = None) -> str:
    if component_id and component_id in _COMPONENT_DISPATCH:
        return component_id
    ordered = _ordered_generator_keys()
    if seed is None:
        global _RR_CURSOR, _SHUFFLED_CYCLE
        import random
        if _SHUFFLED_CYCLE is None or _RR_CURSOR >= len(_SHUFFLED_CYCLE):
            _SHUFFLED_CYCLE = list(ordered)
            random.shuffle(_SHUFFLED_CYCLE)
            _RR_CURSOR = 0
        picked = _SHUFFLED_CYCLE[_RR_CURSOR]
        _RR_CURSOR += 1
        return picked
    return ordered[int(seed) % len(ordered)]


def generate(level: int = 1, seed: int | None = None, component_id: str | None = None, **kwargs: Any) -> dict[str, Any]:
    picked = _pick_component_id(seed=seed, component_id=component_id or kwargs.get("component_id"))
    module = _load_component_module(picked, "generate.py")
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
