from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_SubSection_2_2_4'
GENERATOR_KEYS = ['src_12007', 'src_12008', 'src_12009', 'src_12010', 'src_12011', 'src_12017', 'src_12018', 'src_12019', 'src_12021', 'src_12026', 'src_12027', 'src_12031', 'src_12040', 'src_12041']
GENERATOR_SPECS = [{'textbook_example_id': 12007, 'component_id': 'src_12007', 'generator_key': 'src_12007', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_vieta_expressions', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_vieta_expressions', 'checker_key': 'multi_part_answer_checker', 'display_order': 12007, 'source_order': 12007, 'sampling_weight': 10.0}, {'textbook_example_id': 12008, 'component_id': 'src_12008', 'generator_key': 'src_12008', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'quadratic_vieta_expressions', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_vieta_expressions', 'checker_key': 'multi_part_answer_checker', 'display_order': 12008, 'source_order': 12008, 'sampling_weight': 10.0}, {'textbook_example_id': 12009, 'component_id': 'src_12009', 'generator_key': 'src_12009', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_vieta_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_vieta_parameter', 'checker_key': 'expression_checker', 'display_order': 12009, 'source_order': 12009, 'sampling_weight': 10.0}, {'textbook_example_id': 12010, 'component_id': 'src_12010', 'generator_key': 'src_12010', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'quadratic_vieta_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_vieta_parameter', 'checker_key': 'expression_checker', 'display_order': 12010, 'source_order': 12010, 'sampling_weight': 10.0}, {'textbook_example_id': 12011, 'component_id': 'src_12011', 'generator_key': 'src_12011', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'quadratic_vieta_parameter', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'quadratic_vieta_parameter', 'checker_key': 'single_choice_checker', 'display_order': 12011, 'source_order': 12011, 'sampling_weight': 10.0}, {'textbook_example_id': 12017, 'component_id': 'src_12017', 'generator_key': 'src_12017', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'quadratic_vieta_expressions', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'quadratic_vieta_expressions', 'checker_key': 'multi_part_answer_checker', 'display_order': 12017, 'source_order': 12017, 'sampling_weight': 10.0}, {'textbook_example_id': 12018, 'component_id': 'src_12018', 'generator_key': 'src_12018', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'quadratic_vieta_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_vieta_parameter', 'checker_key': 'expression_checker', 'display_order': 12018, 'source_order': 12018, 'sampling_weight': 10.0}, {'textbook_example_id': 12019, 'component_id': 'src_12019', 'generator_key': 'src_12019', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'quadratic_vieta_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_vieta_parameter', 'checker_key': 'expression_checker', 'display_order': 12019, 'source_order': 12019, 'sampling_weight': 10.0}, {'textbook_example_id': 12021, 'component_id': 'src_12021', 'generator_key': 'src_12021', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'quadratic_build_from_symmetric', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_build_from_symmetric', 'checker_key': 'expression_checker', 'display_order': 12021, 'source_order': 12021, 'sampling_weight': 10.0}, {'textbook_example_id': 12026, 'component_id': 'src_12026', 'generator_key': 'src_12026', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'quadratic_vieta_expressions', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'quadratic_vieta_expressions', 'checker_key': 'single_choice_checker', 'display_order': 12026, 'source_order': 12026, 'sampling_weight': 10.0}, {'textbook_example_id': 12027, 'component_id': 'src_12027', 'generator_key': 'src_12027', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'quadratic_vieta_expressions', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'quadratic_vieta_expressions', 'checker_key': 'single_choice_checker', 'display_order': 12027, 'source_order': 12027, 'sampling_weight': 10.0}, {'textbook_example_id': 12031, 'component_id': 'src_12031', 'generator_key': 'src_12031', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'quadratic_vieta_expressions', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'quadratic_vieta_expressions', 'checker_key': 'single_choice_checker', 'display_order': 12031, 'source_order': 12031, 'sampling_weight': 10.0}, {'textbook_example_id': 12040, 'component_id': 'src_12040', 'generator_key': 'src_12040', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'quadratic_vieta_expressions', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'quadratic_vieta_expressions', 'checker_key': 'single_choice_checker', 'display_order': 12040, 'source_order': 12040, 'sampling_weight': 10.0}, {'textbook_example_id': 12041, 'component_id': 'src_12041', 'generator_key': 'src_12041', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'quadratic_vieta_parameter', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'quadratic_vieta_parameter', 'checker_key': 'single_choice_checker', 'display_order': 12041, 'source_order': 12041, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12007': 'components/src_12007/generate.py', 'src_12008': 'components/src_12008/generate.py', 'src_12009': 'components/src_12009/generate.py', 'src_12010': 'components/src_12010/generate.py', 'src_12011': 'components/src_12011/generate.py', 'src_12017': 'components/src_12017/generate.py', 'src_12018': 'components/src_12018/generate.py', 'src_12019': 'components/src_12019/generate.py', 'src_12021': 'components/src_12021/generate.py', 'src_12026': 'components/src_12026/generate.py', 'src_12027': 'components/src_12027/generate.py', 'src_12031': 'components/src_12031/generate.py', 'src_12040': 'components/src_12040/generate.py', 'src_12041': 'components/src_12041/generate.py'}
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
