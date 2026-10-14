from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B2_SubSection_4_1_2'
GENERATOR_KEYS = ['src_11832', 'src_11833', 'src_11834', 'src_11835', 'src_11836', 'src_11837', 'src_11838', 'src_11839', 'src_11840', 'src_11845', 'src_11846', 'src_11847', 'src_11848', 'src_11849', 'src_11876', 'src_11888', 'src_11889', 'src_11892', 'src_11893']
GENERATOR_SPECS = [{'textbook_example_id': 11832, 'component_id': 'src_11832', 'generator_key': 'src_11832', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'identify_center_radius_from_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_general', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11832, 'source_order': 11832, 'sampling_weight': 10.0}, {'textbook_example_id': 11833, 'component_id': 'src_11833', 'generator_key': 'src_11833', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'identify_center_radius_from_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_general', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11833, 'source_order': 11833, 'sampling_weight': 10.0}, {'textbook_example_id': 11834, 'component_id': 'src_11834', 'generator_key': 'src_11834', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'identify_center_radius_from_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_general', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11834, 'source_order': 11834, 'sampling_weight': 10.0}, {'textbook_example_id': 11835, 'component_id': 'src_11835', 'generator_key': 'src_11835', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'identify_center_radius_from_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_general', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11835, 'source_order': 11835, 'sampling_weight': 10.0}, {'textbook_example_id': 11836, 'component_id': 'src_11836', 'generator_key': 'src_11836', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_circle_parameter_range', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_parameter_range', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11836, 'source_order': 11836, 'sampling_weight': 10.0}, {'textbook_example_id': 11837, 'component_id': 'src_11837', 'generator_key': 'src_11837', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_circle_parameter_range', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_parameter_range', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11837, 'source_order': 11837, 'sampling_weight': 10.0}, {'textbook_example_id': 11838, 'component_id': 'src_11838', 'generator_key': 'src_11838', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'circle_through_three_points', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_through_three_points', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11838, 'source_order': 11838, 'sampling_weight': 10.0}, {'textbook_example_id': 11839, 'component_id': 'src_11839', 'generator_key': 'src_11839', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'circle_through_three_points', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_through_three_points', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11839, 'source_order': 11839, 'sampling_weight': 10.0}, {'textbook_example_id': 11840, 'component_id': 'src_11840', 'generator_key': 'src_11840', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'circle_center_on_axis_area', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'circle_center_on_axis_area', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11840, 'source_order': 11840, 'sampling_weight': 10.0}, {'textbook_example_id': 11845, 'component_id': 'src_11845', 'generator_key': 'src_11845', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'identify_center_radius_from_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_general', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11845, 'source_order': 11845, 'sampling_weight': 10.0}, {'textbook_example_id': 11846, 'component_id': 'src_11846', 'generator_key': 'src_11846', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'classify_general_circle_graph', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_general_circle_graph', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11846, 'source_order': 11846, 'sampling_weight': 10.0}, {'textbook_example_id': 11847, 'component_id': 'src_11847', 'generator_key': 'src_11847', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_circle_parameter_range', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_parameter_range', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11847, 'source_order': 11847, 'sampling_weight': 10.0}, {'textbook_example_id': 11848, 'component_id': 'src_11848', 'generator_key': 'src_11848', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'circle_through_three_points', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_through_three_points', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11848, 'source_order': 11848, 'sampling_weight': 10.0}, {'textbook_example_id': 11849, 'component_id': 'src_11849', 'generator_key': 'src_11849', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'translate_and_scale_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'translate_and_scale_circle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11849, 'source_order': 11849, 'sampling_weight': 10.0}, {'textbook_example_id': 11876, 'component_id': 'src_11876', 'generator_key': 'src_11876', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'evaluate_center_radius_expression', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'evaluate_center_radius_expression', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11876, 'source_order': 11876, 'sampling_weight': 10.0}, {'textbook_example_id': 11888, 'component_id': 'src_11888', 'generator_key': 'src_11888', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'compute_circle_area_from_general', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_circle_area_from_general', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11888, 'source_order': 11888, 'sampling_weight': 10.0}, {'textbook_example_id': 11889, 'component_id': 'src_11889', 'generator_key': 'src_11889', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'identify_circle_from_product_form', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'identify_circle_from_product_form', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11889, 'source_order': 11889, 'sampling_weight': 10.0}, {'textbook_example_id': 11892, 'component_id': 'src_11892', 'generator_key': 'src_11892', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'circle_through_three_points', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_through_three_points', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11892, 'source_order': 11892, 'sampling_weight': 10.0}, {'textbook_example_id': 11893, 'component_id': 'src_11893', 'generator_key': 'src_11893', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'solve_circle_parameter_range_mcq', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'solve_circle_parameter_range_mcq', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11893, 'source_order': 11893, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_11832': 'components/src_11832/generate.py', 'src_11833': 'components/src_11833/generate.py', 'src_11834': 'components/src_11834/generate.py', 'src_11835': 'components/src_11835/generate.py', 'src_11836': 'components/src_11836/generate.py', 'src_11837': 'components/src_11837/generate.py', 'src_11838': 'components/src_11838/generate.py', 'src_11839': 'components/src_11839/generate.py', 'src_11840': 'components/src_11840/generate.py', 'src_11845': 'components/src_11845/generate.py', 'src_11846': 'components/src_11846/generate.py', 'src_11847': 'components/src_11847/generate.py', 'src_11848': 'components/src_11848/generate.py', 'src_11849': 'components/src_11849/generate.py', 'src_11876': 'components/src_11876/generate.py', 'src_11888': 'components/src_11888/generate.py', 'src_11889': 'components/src_11889/generate.py', 'src_11892': 'components/src_11892/generate.py', 'src_11893': 'components/src_11893/generate.py'}
_V3_ROOT = Path(__file__).resolve().parent
_RR_CURSOR = 0
_SHUFFLED_CYCLE = None


def _component_sampling_weight(component_id: str) -> float:
    for row in GENERATOR_SPECS:
        if isinstance(row, dict) and str(row.get("component_id") or "") == component_id:
            return float(row.get("sampling_weight", 1) or 1)
    return 1.0


def _ordered_generator_keys() -> list[str]:
    specs_by_id = {
        str(row.get("component_id") or ""): row
        for row in GENERATOR_SPECS
        if isinstance(row, dict) and str(row.get("component_id") or "")
    }
    return sorted(
        GENERATOR_KEYS,
        key=lambda key: (
            int((specs_by_id.get(key) or {}).get("display_order", 0)),
            int((specs_by_id.get(key) or {}).get("textbook_example_id", 0)),
            key,
        ),
    )


def _load_component_module(component_id: str, module_filename: str) -> Any:
    path = _V3_ROOT / "components" / component_id / module_filename
    module_name = f"v3_{SKILL_ID}_{component_id}_{module_filename.replace('.py', '')}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"component_module_not_found:{component_id}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pick_component_id(
    seed: int | None = None,
    component_id: str | None = None,
) -> str:
    if component_id and component_id in _COMPONENT_DISPATCH:
        return component_id
    ordered_keys = _ordered_generator_keys()
    if not ordered_keys:
        raise RuntimeError("generator_keys_empty")
    
    import math
    from functools import reduce
    
    raw_weights = []
    for key in ordered_keys:
        w = int(_component_sampling_weight(key) or 1)
        raw_weights.append(max(1, w))
        
    g = reduce(math.gcd, raw_weights) if raw_weights else 1
    normalized_weights = [w // g for w in raw_weights]
    
    cycle = []
    for key, w in zip(ordered_keys, normalized_weights):
        cycle.extend([key] * w)

    if seed is None:
        global _RR_CURSOR, _SHUFFLED_CYCLE
        if _SHUFFLED_CYCLE is None or _RR_CURSOR >= len(_SHUFFLED_CYCLE):
            import random
            _SHUFFLED_CYCLE = list(cycle)
            random.shuffle(_SHUFFLED_CYCLE)
            _RR_CURSOR = 0
        picked = _SHUFFLED_CYCLE[_RR_CURSOR]
        _RR_CURSOR += 1
        return picked
    else:
        import random
        cycle_len = len(cycle)
        cycle_seed = int(seed) // cycle_len
        shuffled = list(cycle)
        random.Random(cycle_seed).shuffle(shuffled)
        return shuffled[int(seed) % cycle_len]



def _spec_for_component(component_id: str) -> dict[str, Any]:
    for row in GENERATOR_SPECS:
        if isinstance(row, dict) and str(row.get("component_id") or "") == component_id:
            return dict(row)
    return {}


def _minimal_answer_contract(payload: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    embedded = payload.get("answer_contract")
    if isinstance(embedded, dict) and embedded.get("answer_type"):
        return dict(embedded)
    presentation_mode = str(
        payload.get("presentation_mode")
        or spec.get("presentation_mode")
        or (payload.get("metadata") or {}).get("presentation_mode")
        or "short_answer"
    ).strip()
    answer_type = str(
        payload.get("answer_type")
        or spec.get("answer_type")
        or (payload.get("metadata") or {}).get("answer_type")
        or ("single_choice" if presentation_mode == "single_choice" else "expression")
    ).strip()
    semantic_answer = str(
        payload.get("semantic_answer")
        or (payload.get("metadata") or {}).get("semantic_answer")
        or payload.get("display_answer")
        or payload.get("correct_answer")
        or ""
    ).strip()
    if presentation_mode == "single_choice":
        return {
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence": "choice_label",
            "semantic_answer": semantic_answer,
        }
    return {
        "presentation_mode": "short_answer",
        "answer_type": answer_type,
        "checker": "linear_equation_equivalent_checker",
        "checker_key": "linear_equation_equivalent_checker",
        "answer_equivalence": "linear_equation_equivalent",
        "equivalence": "linear_equation_equivalent",
        "semantic_answer": semantic_answer,
    }


def _merge_generator_spec(payload: dict[str, Any], component_id: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return payload
    spec = _spec_for_component(component_id)
    out = dict(payload)
    merge_keys = (
        "textbook_example_id",
        "component_id",
        "generator_key",
        "presentation_mode",
        "problem_type_id",
        "source_kind",
        "line_type",
        "display_order",
        "source_order",
        "sampling_weight",
    )
    for key in merge_keys:
        if spec.get(key) is not None:
            out[key] = spec[key]
    out.setdefault("component_id", component_id)
    out.setdefault("generator_key", component_id)
    meta = dict(out.get("metadata") or {}) if isinstance(out.get("metadata"), dict) else {}
    for key in (
        "textbook_example_id",
        "component_id",
        "presentation_mode",
        "answer_type",
        "problem_type_id",
        "source_kind",
        "line_type",
        "semantic_answer",
    ):
        if out.get(key) is not None:
            meta.setdefault(key, out.get(key))
        elif spec.get(key) is not None:
            meta.setdefault(key, spec.get(key))
    if out.get("semantic_answer") is not None:
        meta.setdefault("semantic_answer", out.get("semantic_answer"))
    out["metadata"] = meta
    if not isinstance(out.get("answer_contract"), dict) or not out.get("answer_contract"):
        out["answer_contract"] = _minimal_answer_contract(out, spec)
    if out["answer_contract"].get("checker"):
        out["checker"] = out["answer_contract"].get("checker")
        out.setdefault("checker_type", out["answer_contract"].get("checker"))
    if out["answer_contract"].get("answer_equivalence"):
        out["equivalence"] = out["answer_contract"].get("answer_equivalence")
    return out


def generate(
    level: int = 1,
    seed: int | None = None,
    component_id: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    picked = _pick_component_id(seed=seed, component_id=component_id)
    module = _load_component_module(picked, "generate.py")
    generate_fn = getattr(module, "generate", None)
    if not callable(generate_fn):
        raise RuntimeError(f"component_generate_missing:{picked}")
    payload = generate_fn(level=level, seed=seed, component_id=picked, **kwargs)
    if isinstance(payload, dict):
        if not payload.get("component_id"):
            payload["component_id"] = picked
        return _merge_generator_spec(payload, picked)
    return payload


def check(
    user_answer: Any,
    correct_answer: Any,
    question_payload: dict[str, Any] | None = None,
) -> Any:
    payload = dict(question_payload or {})
    component_id = str(payload.get("component_id") or "")
    if component_id and component_id in _COMPONENT_DISPATCH:
        module = _load_component_module(component_id, "generate.py")
        check_fn = getattr(module, "check", None)
        if callable(check_fn):
            return check_fn(user_answer, correct_answer, payload)
    from core.gencode.runtime_skill_wrapper import check_answer

    return check_answer(user_answer, correct_answer, payload=payload)


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    payload = dict(question_payload or {})
    component_id = str(payload.get("component_id") or "")
    if component_id and component_id in _COMPONENT_DISPATCH:
        module = _load_component_module(component_id, "get_hint.py")
        hint_fn = getattr(module, "get_hint", None)
        if callable(hint_fn):
            from inspect import signature

            parameters = signature(hint_fn).parameters
            if "stage" in parameters and "question_payload" not in parameters:
                return str(hint_fn(payload, stage=step) or "")
            return str(hint_fn(step, payload) or "")
    return ""
