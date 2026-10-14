from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_SubSection_2_1_1'
GENERATOR_KEYS = ['src_11971', 'src_11972', 'src_11973', 'src_11974', 'src_11975', 'src_11976', 'src_11977', 'src_11978', 'src_11987', 'src_11988', 'src_11989', 'src_11990', 'src_11991', 'src_11992', 'src_11995', 'src_11996', 'src_12022', 'src_12032', 'src_12033', 'src_12034']
GENERATOR_SPECS = [{'textbook_example_id': 11971, 'component_id': 'src_11971', 'generator_key': 'src_11971', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'linear_solve_isolated', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'linear_solve_isolated', 'checker_key': 'multi_part_answer_checker', 'display_order': 11971, 'source_order': 11971, 'sampling_weight': 10.0}, {'textbook_example_id': 11972, 'component_id': 'src_11972', 'generator_key': 'src_11972', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'linear_solve_isolated', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'linear_solve_isolated', 'checker_key': 'multi_part_answer_checker', 'display_order': 11972, 'source_order': 11972, 'sampling_weight': 10.0}, {'textbook_example_id': 11973, 'component_id': 'src_11973', 'generator_key': 'src_11973', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'linear_solve_general', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'linear_solve_general', 'checker_key': 'multi_part_answer_checker', 'display_order': 11973, 'source_order': 11973, 'sampling_weight': 10.0}, {'textbook_example_id': 11974, 'component_id': 'src_11974', 'generator_key': 'src_11974', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'linear_solve_general', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'linear_solve_general', 'checker_key': 'multi_part_answer_checker', 'display_order': 11974, 'source_order': 11974, 'sampling_weight': 10.0}, {'textbook_example_id': 11975, 'component_id': 'src_11975', 'generator_key': 'src_11975', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'linear_word_unit_total', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'linear_word_unit_total', 'checker_key': 'expression_checker', 'display_order': 11975, 'source_order': 11975, 'sampling_weight': 10.0}, {'textbook_example_id': 11976, 'component_id': 'src_11976', 'generator_key': 'src_11976', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'linear_word_unit_total', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'linear_word_unit_total', 'checker_key': 'expression_checker', 'display_order': 11976, 'source_order': 11976, 'sampling_weight': 10.0}, {'textbook_example_id': 11977, 'component_id': 'src_11977', 'generator_key': 'src_11977', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'linear_word_two_conditions', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'linear_word_two_conditions', 'checker_key': 'multi_part_answer_checker', 'display_order': 11977, 'source_order': 11977, 'sampling_weight': 10.0}, {'textbook_example_id': 11978, 'component_id': 'src_11978', 'generator_key': 'src_11978', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'linear_word_two_conditions', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'linear_word_two_conditions', 'checker_key': 'multi_part_answer_checker', 'display_order': 11978, 'source_order': 11978, 'sampling_weight': 10.0}, {'textbook_example_id': 11987, 'component_id': 'src_11987', 'generator_key': 'src_11987', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'linear_solve_isolated', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'linear_solve_isolated', 'checker_key': 'multi_part_answer_checker', 'display_order': 11987, 'source_order': 11987, 'sampling_weight': 10.0}, {'textbook_example_id': 11988, 'component_id': 'src_11988', 'generator_key': 'src_11988', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'linear_solve_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'linear_solve_general', 'checker_key': 'expression_checker', 'display_order': 11988, 'source_order': 11988, 'sampling_weight': 10.0}, {'textbook_example_id': 11989, 'component_id': 'src_11989', 'generator_key': 'src_11989', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'linear_solve_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'linear_solve_general', 'checker_key': 'expression_checker', 'display_order': 11989, 'source_order': 11989, 'sampling_weight': 10.0}, {'textbook_example_id': 11990, 'component_id': 'src_11990', 'generator_key': 'src_11990', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'linear_word_ratio_sum', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'linear_word_ratio_sum', 'checker_key': 'multi_part_answer_checker', 'display_order': 11990, 'source_order': 11990, 'sampling_weight': 10.0}, {'textbook_example_id': 11991, 'component_id': 'src_11991', 'generator_key': 'src_11991', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'linear_word_three_shares', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'linear_word_three_shares', 'checker_key': 'multi_part_answer_checker', 'display_order': 11991, 'source_order': 11991, 'sampling_weight': 10.0}, {'textbook_example_id': 11992, 'component_id': 'src_11992', 'generator_key': 'src_11992', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'linear_word_two_conditions', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'linear_word_two_conditions', 'checker_key': 'multi_part_answer_checker', 'display_order': 11992, 'source_order': 11992, 'sampling_weight': 10.0}, {'textbook_example_id': 11995, 'component_id': 'src_11995', 'generator_key': 'src_11995', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'linear_word_markup', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'linear_word_markup', 'checker_key': 'expression_checker', 'display_order': 11995, 'source_order': 11995, 'sampling_weight': 10.0}, {'textbook_example_id': 11996, 'component_id': 'src_11996', 'generator_key': 'src_11996', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'linear_word_two_plans', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'linear_word_two_plans', 'checker_key': 'expression_checker', 'display_order': 11996, 'source_order': 11996, 'sampling_weight': 10.0}, {'textbook_example_id': 12022, 'component_id': 'src_12022', 'generator_key': 'src_12022', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'linear_solve_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'linear_solve_general', 'checker_key': 'expression_checker', 'display_order': 12022, 'source_order': 12022, 'sampling_weight': 10.0}, {'textbook_example_id': 12032, 'component_id': 'src_12032', 'generator_key': 'src_12032', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'linear_solve_general', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'linear_solve_general', 'checker_key': 'single_choice_checker', 'display_order': 12032, 'source_order': 12032, 'sampling_weight': 10.0}, {'textbook_example_id': 12033, 'component_id': 'src_12033', 'generator_key': 'src_12033', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'linear_word_class_share', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'linear_word_class_share', 'checker_key': 'single_choice_checker', 'display_order': 12033, 'source_order': 12033, 'sampling_weight': 10.0}, {'textbook_example_id': 12034, 'component_id': 'src_12034', 'generator_key': 'src_12034', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'linear_word_markup', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'linear_word_markup', 'checker_key': 'single_choice_checker', 'display_order': 12034, 'source_order': 12034, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_11971': 'components/src_11971/generate.py', 'src_11972': 'components/src_11972/generate.py', 'src_11973': 'components/src_11973/generate.py', 'src_11974': 'components/src_11974/generate.py', 'src_11975': 'components/src_11975/generate.py', 'src_11976': 'components/src_11976/generate.py', 'src_11977': 'components/src_11977/generate.py', 'src_11978': 'components/src_11978/generate.py', 'src_11987': 'components/src_11987/generate.py', 'src_11988': 'components/src_11988/generate.py', 'src_11989': 'components/src_11989/generate.py', 'src_11990': 'components/src_11990/generate.py', 'src_11991': 'components/src_11991/generate.py', 'src_11992': 'components/src_11992/generate.py', 'src_11995': 'components/src_11995/generate.py', 'src_11996': 'components/src_11996/generate.py', 'src_12022': 'components/src_12022/generate.py', 'src_12032': 'components/src_12032/generate.py', 'src_12033': 'components/src_12033/generate.py', 'src_12034': 'components/src_12034/generate.py'}
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
