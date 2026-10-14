from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_SubSection_3_1_3'
GENERATOR_KEYS = ['src_12048', 'src_12049', 'src_12050', 'src_12051', 'src_12052', 'src_12053', 'src_12054', 'src_12059', 'src_12060', 'src_12061', 'src_12064', 'src_12122', 'src_12123']
GENERATOR_SPECS = [{'textbook_example_id': 12048, 'component_id': 'src_12048', 'generator_key': 'src_12048', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'line_slope_pair', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'line_slope_pair', 'checker_key': 'multi_part', 'display_order': 12048, 'source_order': 12048, 'sampling_weight': 10.0}, {'textbook_example_id': 12049, 'component_id': 'src_12049', 'generator_key': 'src_12049', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'line_slope_pair', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'line_slope_pair', 'checker_key': 'multi_part', 'display_order': 12049, 'source_order': 12049, 'sampling_weight': 10.0}, {'textbook_example_id': 12050, 'component_id': 'src_12050', 'generator_key': 'src_12050', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'textbook_example', 'line_type': 'line_pair_relation', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'line_pair_relation', 'checker_key': 'single_choice', 'display_order': 12050, 'source_order': 12050, 'sampling_weight': 10.0}, {'textbook_example_id': 12051, 'component_id': 'src_12051', 'generator_key': 'src_12051', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'textbook_example', 'line_type': 'line_pair_relation', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'line_pair_relation', 'checker_key': 'single_choice', 'display_order': 12051, 'source_order': 12051, 'sampling_weight': 10.0}, {'textbook_example_id': 12052, 'component_id': 'src_12052', 'generator_key': 'src_12052', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'system_parameter_unique', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'system_parameter_unique', 'checker_key': 'inequality', 'display_order': 12052, 'source_order': 12052, 'sampling_weight': 10.0}, {'textbook_example_id': 12053, 'component_id': 'src_12053', 'generator_key': 'src_12053', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'system_parameter_unique', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'system_parameter_unique', 'checker_key': 'inequality', 'display_order': 12053, 'source_order': 12053, 'sampling_weight': 10.0}, {'textbook_example_id': 12054, 'component_id': 'src_12054', 'generator_key': 'src_12054', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'exam_practice', 'line_type': 'system_dependent_value', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'system_dependent_value', 'checker_key': 'single_choice', 'display_order': 12054, 'source_order': 12054, 'sampling_weight': 10.0}, {'textbook_example_id': 12059, 'component_id': 'src_12059', 'generator_key': 'src_12059', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'line_slope_pair', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'line_slope_pair', 'checker_key': 'multi_part', 'display_order': 12059, 'source_order': 12059, 'sampling_weight': 10.0}, {'textbook_example_id': 12060, 'component_id': 'src_12060', 'generator_key': 'src_12060', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'textbook_example', 'line_type': 'line_pair_relation', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'line_pair_relation', 'checker_key': 'single_choice', 'display_order': 12060, 'source_order': 12060, 'sampling_weight': 10.0}, {'textbook_example_id': 12061, 'component_id': 'src_12061', 'generator_key': 'src_12061', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'system_parameter_unique', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'system_parameter_unique', 'checker_key': 'inequality', 'display_order': 12061, 'source_order': 12061, 'sampling_weight': 10.0}, {'textbook_example_id': 12064, 'component_id': 'src_12064', 'generator_key': 'src_12064', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'advanced_exercise', 'line_type': 'system_parameter_cases', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'system_parameter_cases', 'checker_key': 'multi_part', 'display_order': 12064, 'source_order': 12064, 'sampling_weight': 10.0}, {'textbook_example_id': 12122, 'component_id': 'src_12122', 'generator_key': 'src_12122', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'self_assessment', 'line_type': 'system_parameter_unique', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'system_parameter_unique', 'checker_key': 'inequality', 'display_order': 12122, 'source_order': 12122, 'sampling_weight': 10.0}, {'textbook_example_id': 12123, 'component_id': 'src_12123', 'generator_key': 'src_12123', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'system_parameter_unique', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'system_parameter_unique', 'checker_key': 'single_choice', 'display_order': 12123, 'source_order': 12123, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12048': 'components/src_12048/generate.py', 'src_12049': 'components/src_12049/generate.py', 'src_12050': 'components/src_12050/generate.py', 'src_12051': 'components/src_12051/generate.py', 'src_12052': 'components/src_12052/generate.py', 'src_12053': 'components/src_12053/generate.py', 'src_12054': 'components/src_12054/generate.py', 'src_12059': 'components/src_12059/generate.py', 'src_12060': 'components/src_12060/generate.py', 'src_12061': 'components/src_12061/generate.py', 'src_12064': 'components/src_12064/generate.py', 'src_12122': 'components/src_12122/generate.py', 'src_12123': 'components/src_12123/generate.py'}
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
