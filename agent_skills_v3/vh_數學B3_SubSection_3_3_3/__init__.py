from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_SubSection_3_3_3'
GENERATOR_KEYS = ['src_12090', 'src_12091', 'src_12103', 'src_12114', 'src_12116', 'src_12126']
GENERATOR_SPECS = [{'textbook_example_id': 12090, 'component_id': 'src_12090', 'generator_key': 'src_12090', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_extrema', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'lp_extrema', 'checker_key': 'multi_part', 'display_order': 12090, 'source_order': 12090, 'sampling_weight': 10.0}, {'textbook_example_id': 12091, 'component_id': 'src_12091', 'generator_key': 'src_12091', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_extrema', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'lp_extrema', 'checker_key': 'multi_part', 'display_order': 12091, 'source_order': 12091, 'sampling_weight': 10.0}, {'textbook_example_id': 12103, 'component_id': 'src_12103', 'generator_key': 'src_12103', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'textbook_example', 'line_type': 'lp_extrema', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'lp_extrema', 'checker_key': 'multi_part', 'display_order': 12103, 'source_order': 12103, 'sampling_weight': 10.0}, {'textbook_example_id': 12114, 'component_id': 'src_12114', 'generator_key': 'src_12114', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'self_assessment', 'line_type': 'lp_extrema', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'lp_extrema', 'checker_key': 'multi_part', 'display_order': 12114, 'source_order': 12114, 'sampling_weight': 10.0}, {'textbook_example_id': 12116, 'component_id': 'src_12116', 'generator_key': 'src_12116', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'self_assessment', 'line_type': 'lp_extrema', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'lp_extrema', 'checker_key': 'multi_part', 'display_order': 12116, 'source_order': 12116, 'sampling_weight': 10.0}, {'textbook_example_id': 12126, 'component_id': 'src_12126', 'generator_key': 'src_12126', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'self_assessment', 'line_type': 'lp_extrema', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'lp_extrema', 'checker_key': 'single_choice', 'display_order': 12126, 'source_order': 12126, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12090': 'components/src_12090/generate.py', 'src_12091': 'components/src_12091/generate.py', 'src_12103': 'components/src_12103/generate.py', 'src_12114': 'components/src_12114/generate.py', 'src_12116': 'components/src_12116/generate.py', 'src_12126': 'components/src_12126/generate.py'}
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
