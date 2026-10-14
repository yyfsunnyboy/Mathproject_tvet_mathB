from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_PlainHeading_3_2_4'
GENERATOR_KEYS = ['src_12072', 'src_12073', 'src_12079', 'src_12080', 'src_12084', 'src_12085', 'src_12108', 'src_12109']
GENERATOR_SPECS = [{'textbook_example_id': 12072, 'component_id': 'src_12072', 'generator_key': 'src_12072', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'same_side_test', 'answer_type': 'short_answer', 'answer_value_type': 'short_answer', 'problem_type_id': 'same_side_test', 'checker_key': 'short_answer', 'display_order': 12072, 'source_order': 12072, 'sampling_weight': 10.0}, {'textbook_example_id': 12073, 'component_id': 'src_12073', 'generator_key': 'src_12073', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'same_side_parameter', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'same_side_parameter', 'checker_key': 'inequality', 'display_order': 12073, 'source_order': 12073, 'sampling_weight': 10.0}, {'textbook_example_id': 12079, 'component_id': 'src_12079', 'generator_key': 'src_12079', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'same_side_test', 'answer_type': 'short_answer', 'answer_value_type': 'short_answer', 'problem_type_id': 'same_side_test', 'checker_key': 'short_answer', 'display_order': 12079, 'source_order': 12079, 'sampling_weight': 10.0}, {'textbook_example_id': 12080, 'component_id': 'src_12080', 'generator_key': 'src_12080', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'same_side_parameter', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'same_side_parameter', 'checker_key': 'inequality', 'display_order': 12080, 'source_order': 12080, 'sampling_weight': 10.0}, {'textbook_example_id': 12084, 'component_id': 'src_12084', 'generator_key': 'src_12084', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'same_side_test', 'answer_type': 'short_answer', 'answer_value_type': 'short_answer', 'problem_type_id': 'same_side_test', 'checker_key': 'short_answer', 'display_order': 12084, 'source_order': 12084, 'sampling_weight': 10.0}, {'textbook_example_id': 12085, 'component_id': 'src_12085', 'generator_key': 'src_12085', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'same_side_parameter', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'same_side_parameter', 'checker_key': 'inequality', 'display_order': 12085, 'source_order': 12085, 'sampling_weight': 10.0}, {'textbook_example_id': 12108, 'component_id': 'src_12108', 'generator_key': 'src_12108', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'same_side_test', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'same_side_test', 'checker_key': 'single_choice', 'display_order': 12108, 'source_order': 12108, 'sampling_weight': 10.0}, {'textbook_example_id': 12109, 'component_id': 'src_12109', 'generator_key': 'src_12109', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'same_side_parameter', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'same_side_parameter', 'checker_key': 'single_choice', 'display_order': 12109, 'source_order': 12109, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12072': 'components/src_12072/generate.py', 'src_12073': 'components/src_12073/generate.py', 'src_12079': 'components/src_12079/generate.py', 'src_12080': 'components/src_12080/generate.py', 'src_12084': 'components/src_12084/generate.py', 'src_12085': 'components/src_12085/generate.py', 'src_12108': 'components/src_12108/generate.py', 'src_12109': 'components/src_12109/generate.py'}
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
