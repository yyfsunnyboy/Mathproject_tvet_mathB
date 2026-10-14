from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_PlainHeading_3_2_2'
GENERATOR_KEYS = ['src_12065', 'src_12124']
GENERATOR_SPECS = [{'textbook_example_id': 12065, 'component_id': 'src_12065', 'generator_key': 'src_12065', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'exam_practice', 'line_type': 'integer_feasible_choice', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'integer_feasible_choice', 'checker_key': 'single_choice', 'display_order': 12065, 'source_order': 12065, 'sampling_weight': 10.0}, {'textbook_example_id': 12124, 'component_id': 'src_12124', 'generator_key': 'src_12124', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'self_assessment', 'line_type': 'integer_feasible_count', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'integer_feasible_count', 'checker_key': 'expression', 'display_order': 12124, 'source_order': 12124, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12065': 'components/src_12065/generate.py', 'src_12124': 'components/src_12124/generate.py'}
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
