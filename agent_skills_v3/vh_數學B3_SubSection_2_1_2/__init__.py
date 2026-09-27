from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_SubSection_2_1_2'
GENERATOR_KEYS = ['src_11979', 'src_11980', 'src_11981', 'src_11982', 'src_11986', 'src_11993', 'src_11994', 'src_12035', 'src_12036', 'src_12037', 'src_12038']
GENERATOR_SPECS = [{'textbook_example_id': 11979, 'component_id': 'src_11979', 'generator_key': 'src_11979', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'inequality_solve', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'inequality_solve', 'checker_key': 'multi_part_answer_checker', 'display_order': 11979, 'source_order': 11979, 'sampling_weight': 10.0}, {'textbook_example_id': 11980, 'component_id': 'src_11980', 'generator_key': 'src_11980', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'inequality_solve', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'inequality_solve', 'checker_key': 'multi_part_answer_checker', 'display_order': 11980, 'source_order': 11980, 'sampling_weight': 10.0}, {'textbook_example_id': 11981, 'component_id': 'src_11981', 'generator_key': 'src_11981', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'inequality_word_minimum', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'inequality_word_minimum', 'checker_key': 'expression_checker', 'display_order': 11981, 'source_order': 11981, 'sampling_weight': 10.0}, {'textbook_example_id': 11982, 'component_id': 'src_11982', 'generator_key': 'src_11982', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'inequality_word_minimum', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'inequality_word_minimum', 'checker_key': 'expression_checker', 'display_order': 11982, 'source_order': 11982, 'sampling_weight': 10.0}, {'textbook_example_id': 11986, 'component_id': 'src_11986', 'generator_key': 'src_11986', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'inequality_bmi_bound', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'inequality_bmi_bound', 'checker_key': 'single_choice_checker', 'display_order': 11986, 'source_order': 11986, 'sampling_weight': 10.0}, {'textbook_example_id': 11993, 'component_id': 'src_11993', 'generator_key': 'src_11993', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'inequality_solve', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'inequality_solve', 'checker_key': 'multi_part_answer_checker', 'display_order': 11993, 'source_order': 11993, 'sampling_weight': 10.0}, {'textbook_example_id': 11994, 'component_id': 'src_11994', 'generator_key': 'src_11994', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'inequality_word_minimum', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'inequality_word_minimum', 'checker_key': 'expression_checker', 'display_order': 11994, 'source_order': 11994, 'sampling_weight': 10.0}, {'textbook_example_id': 12035, 'component_id': 'src_12035', 'generator_key': 'src_12035', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'inequality_solve', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'inequality_solve', 'checker_key': 'single_choice_checker', 'display_order': 12035, 'source_order': 12035, 'sampling_weight': 10.0}, {'textbook_example_id': 12036, 'component_id': 'src_12036', 'generator_key': 'src_12036', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'inequality_solve', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'inequality_solve', 'checker_key': 'single_choice_checker', 'display_order': 12036, 'source_order': 12036, 'sampling_weight': 10.0}, {'textbook_example_id': 12037, 'component_id': 'src_12037', 'generator_key': 'src_12037', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'inequality_solve', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'inequality_solve', 'checker_key': 'single_choice_checker', 'display_order': 12037, 'source_order': 12037, 'sampling_weight': 10.0}, {'textbook_example_id': 12038, 'component_id': 'src_12038', 'generator_key': 'src_12038', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'inequality_word_minimum', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'inequality_word_minimum', 'checker_key': 'single_choice_checker', 'display_order': 12038, 'source_order': 12038, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_11979': 'components/src_11979/generate.py', 'src_11980': 'components/src_11980/generate.py', 'src_11981': 'components/src_11981/generate.py', 'src_11982': 'components/src_11982/generate.py', 'src_11986': 'components/src_11986/generate.py', 'src_11993': 'components/src_11993/generate.py', 'src_11994': 'components/src_11994/generate.py', 'src_12035': 'components/src_12035/generate.py', 'src_12036': 'components/src_12036/generate.py', 'src_12037': 'components/src_12037/generate.py', 'src_12038': 'components/src_12038/generate.py'}
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
