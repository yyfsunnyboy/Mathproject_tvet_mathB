from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_SubSection_2_2_2'
GENERATOR_KEYS = ['src_11997', 'src_11998', 'src_11999', 'src_12000', 'src_12001', 'src_12002', 'src_12012', 'src_12013', 'src_12014', 'src_12015', 'src_12023', 'src_12025', 'src_12039']
GENERATOR_SPECS = [{'textbook_example_id': 11997, 'component_id': 'src_11997', 'generator_key': 'src_11997', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_integer_roots', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_integer_roots', 'checker_key': 'multi_part_answer_checker', 'display_order': 11997, 'source_order': 11997, 'sampling_weight': 10.0}, {'textbook_example_id': 11998, 'component_id': 'src_11998', 'generator_key': 'src_11998', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'quadratic_integer_roots', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_integer_roots', 'checker_key': 'multi_part_answer_checker', 'display_order': 11998, 'source_order': 11998, 'sampling_weight': 10.0}, {'textbook_example_id': 11999, 'component_id': 'src_11999', 'generator_key': 'src_11999', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_projectile_time', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_projectile_time', 'checker_key': 'expression_checker', 'display_order': 11999, 'source_order': 11999, 'sampling_weight': 10.0}, {'textbook_example_id': 12000, 'component_id': 'src_12000', 'generator_key': 'src_12000', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'quadratic_projectile_time', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_projectile_time', 'checker_key': 'expression_checker', 'display_order': 12000, 'source_order': 12000, 'sampling_weight': 10.0}, {'textbook_example_id': 12001, 'component_id': 'src_12001', 'generator_key': 'src_12001', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_formula_exact', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_formula_exact', 'checker_key': 'multi_part_answer_checker', 'display_order': 12001, 'source_order': 12001, 'sampling_weight': 10.0}, {'textbook_example_id': 12002, 'component_id': 'src_12002', 'generator_key': 'src_12002', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'quadratic_formula_exact', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_formula_exact', 'checker_key': 'multi_part_answer_checker', 'display_order': 12002, 'source_order': 12002, 'sampling_weight': 10.0}, {'textbook_example_id': 12012, 'component_id': 'src_12012', 'generator_key': 'src_12012', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'quadratic_integer_roots', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_integer_roots', 'checker_key': 'multi_part_answer_checker', 'display_order': 12012, 'source_order': 12012, 'sampling_weight': 10.0}, {'textbook_example_id': 12013, 'component_id': 'src_12013', 'generator_key': 'src_12013', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'quadratic_right_triangle_side_relation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_right_triangle_side_relation', 'checker_key': 'expression_checker', 'display_order': 12013, 'source_order': 12013, 'sampling_weight': 10.0}, {'textbook_example_id': 12014, 'component_id': 'src_12014', 'generator_key': 'src_12014', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'quadratic_word_pair_count', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_word_pair_count', 'checker_key': 'expression_checker', 'display_order': 12014, 'source_order': 12014, 'sampling_weight': 10.0}, {'textbook_example_id': 12015, 'component_id': 'src_12015', 'generator_key': 'src_12015', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'quadratic_formula_exact', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_formula_exact', 'checker_key': 'multi_part_answer_checker', 'display_order': 12015, 'source_order': 12015, 'sampling_weight': 10.0}, {'textbook_example_id': 12023, 'component_id': 'src_12023', 'generator_key': 'src_12023', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'quadratic_integer_roots', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'quadratic_integer_roots', 'checker_key': 'single_choice_checker', 'display_order': 12023, 'source_order': 12023, 'sampling_weight': 10.0}, {'textbook_example_id': 12025, 'component_id': 'src_12025', 'generator_key': 'src_12025', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'quadratic_word_pythagoras', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'quadratic_word_pythagoras', 'checker_key': 'single_choice_checker', 'display_order': 12025, 'source_order': 12025, 'sampling_weight': 10.0}, {'textbook_example_id': 12039, 'component_id': 'src_12039', 'generator_key': 'src_12039', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'quadratic_integer_roots', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'quadratic_integer_roots', 'checker_key': 'single_choice_checker', 'display_order': 12039, 'source_order': 12039, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_11997': 'components/src_11997/generate.py', 'src_11998': 'components/src_11998/generate.py', 'src_11999': 'components/src_11999/generate.py', 'src_12000': 'components/src_12000/generate.py', 'src_12001': 'components/src_12001/generate.py', 'src_12002': 'components/src_12002/generate.py', 'src_12012': 'components/src_12012/generate.py', 'src_12013': 'components/src_12013/generate.py', 'src_12014': 'components/src_12014/generate.py', 'src_12015': 'components/src_12015/generate.py', 'src_12023': 'components/src_12023/generate.py', 'src_12025': 'components/src_12025/generate.py', 'src_12039': 'components/src_12039/generate.py'}
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
