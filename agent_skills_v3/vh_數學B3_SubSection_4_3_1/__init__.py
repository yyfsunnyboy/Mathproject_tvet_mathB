from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_SubSection_4_3_1'
GENERATOR_KEYS = ['src_12171', 'src_12172', 'src_12188', 'src_12250']
GENERATOR_SPECS = [{'textbook_example_id': 12171, 'component_id': 'src_12171', 'generator_key': 'src_12171', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'log_definition_eval', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'log_definition_eval', 'checker_key': 'multi_part', 'display_order': 12171, 'source_order': 12171, 'sampling_weight': 10.0}, {'textbook_example_id': 12172, 'component_id': 'src_12172', 'generator_key': 'src_12172', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'in_class_practice', 'line_type': 'log_definition_eval', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'log_definition_eval', 'checker_key': 'multi_part', 'display_order': 12172, 'source_order': 12172, 'sampling_weight': 10.0}, {'textbook_example_id': 12188, 'component_id': 'src_12188', 'generator_key': 'src_12188', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_exercise', 'line_type': 'log_domain_validity_choice', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'log_domain_validity_choice', 'checker_key': 'multi_part', 'display_order': 12188, 'source_order': 12188, 'sampling_weight': 10.0}, {'textbook_example_id': 12250, 'component_id': 'src_12250', 'generator_key': 'src_12250', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'log_domain_validity_choice', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'log_domain_validity_choice', 'checker_key': 'single_choice', 'display_order': 12250, 'source_order': 12250, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12171': 'components/src_12171/generate.py', 'src_12172': 'components/src_12172/generate.py', 'src_12188': 'components/src_12188/generate.py', 'src_12250': 'components/src_12250/generate.py'}
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
