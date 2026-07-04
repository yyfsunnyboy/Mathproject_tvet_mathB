from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B1_LinearFunction'
GENERATOR_KEYS = ['src_4424', 'src_4425', 'src_4426', 'src_4433', 'src_4434', 'src_4441', 'src_4442', 'src_4444', 'src_4445', 'src_4446', 'src_4448', 'src_4449', 'src_4500', 'src_4515', 'src_4516']
GENERATOR_SPECS = [{'textbook_example_id': 4424, 'component_id': 'src_4424', 'generator_key': 'src_4424', 'presentation_mode': 'graph_multi_part', 'response_mode': 'graph_multi_part', 'interaction_type': 'graph_multi_part', 'source_kind': 'example', 'line_type': 'graph_intercepts_and_linear_equation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_intercepts_and_linear_equation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 4424, 'source_order': 4424, 'sampling_weight': 10.0}, {'textbook_example_id': 4425, 'component_id': 'src_4425', 'generator_key': 'src_4425', 'presentation_mode': 'graph_multi_part', 'response_mode': 'graph_multi_part', 'interaction_type': 'graph_multi_part', 'source_kind': 'example', 'line_type': 'graph_based_tiered_linear_application_multi_part', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_based_tiered_linear_application_multi_part', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 4425, 'source_order': 4425, 'sampling_weight': 10.0}, {'textbook_example_id': 4426, 'component_id': 'src_4426', 'generator_key': 'src_4426', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'collinear_trisection_coordinate', 'answer_type': 'coordinate_pair', 'answer_value_type': 'coordinate_pair', 'problem_type_id': 'collinear_trisection_coordinate', 'checker_key': 'coordinate_pair_checker', 'equivalence_type': None, 'display_order': 4426, 'source_order': 4426, 'sampling_weight': 10.0}, {'textbook_example_id': 4433, 'component_id': 'src_4433', 'generator_key': 'src_4433', 'presentation_mode': 'canvas', 'response_mode': 'canvas', 'interaction_type': 'canvas', 'source_kind': 'example', 'line_type': 'draw_constant_function_graph', 'answer_type': 'drawing', 'answer_value_type': 'drawing', 'problem_type_id': 'draw_constant_function_graph', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': None, 'display_order': 4433, 'source_order': 4433, 'sampling_weight': 10.0}, {'textbook_example_id': 4434, 'component_id': 'src_4434', 'generator_key': 'src_4434', 'presentation_mode': 'canvas', 'response_mode': 'canvas', 'interaction_type': 'canvas', 'source_kind': 'example', 'line_type': 'draw_linear_function_graph', 'answer_type': 'drawing', 'answer_value_type': 'drawing', 'problem_type_id': 'draw_linear_function_graph', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': None, 'display_order': 4434, 'source_order': 4434, 'sampling_weight': 10.0}, {'textbook_example_id': 4441, 'component_id': 'src_4441', 'generator_key': 'src_4441', 'presentation_mode': 'graph_multi_part', 'response_mode': 'graph_multi_part', 'interaction_type': 'graph_multi_part', 'source_kind': 'quiz', 'line_type': 'graph_intercepts_and_linear_equation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_intercepts_and_linear_equation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 4441, 'source_order': 4441, 'sampling_weight': 10.0}, {'textbook_example_id': 4442, 'component_id': 'src_4442', 'generator_key': 'src_4442', 'presentation_mode': 'graph_short_answer', 'response_mode': 'graph_short_answer', 'interaction_type': 'graph_short_answer', 'source_kind': 'quiz', 'line_type': 'graph_based_linear_application_inverse', 'answer_type': 'numeric', 'answer_value_type': 'numeric', 'problem_type_id': 'graph_based_linear_application_inverse', 'checker_key': 'numeric_checker', 'equivalence_type': None, 'display_order': 4442, 'source_order': 4442, 'sampling_weight': 10.0}, {'textbook_example_id': 4444, 'component_id': 'src_4444', 'generator_key': 'src_4444', 'presentation_mode': 'graph_multi_part', 'response_mode': 'graph_multi_part', 'interaction_type': 'graph_multi_part', 'source_kind': 'example', 'line_type': 'graph_intercepts_and_linear_equation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_intercepts_and_linear_equation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 4444, 'source_order': 4444, 'sampling_weight': 10.0}, {'textbook_example_id': 4445, 'component_id': 'src_4445', 'generator_key': 'src_4445', 'presentation_mode': 'graph_multi_part', 'response_mode': 'graph_multi_part', 'interaction_type': 'graph_multi_part', 'source_kind': 'example', 'line_type': 'graph_based_tiered_linear_application_multi_part', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_based_tiered_linear_application_multi_part', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 4445, 'source_order': 4445, 'sampling_weight': 10.0}, {'textbook_example_id': 4446, 'component_id': 'src_4446', 'generator_key': 'src_4446', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'robust_budget_feasibility_choice', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'robust_budget_feasibility_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 4446, 'source_order': 4446, 'sampling_weight': 10.0}, {'textbook_example_id': 4448, 'component_id': 'src_4448', 'generator_key': 'src_4448', 'presentation_mode': 'canvas', 'response_mode': 'canvas', 'interaction_type': 'canvas', 'source_kind': 'quiz', 'line_type': 'draw_constant_function_graph', 'answer_type': 'drawing', 'answer_value_type': 'drawing', 'problem_type_id': 'draw_constant_function_graph', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': None, 'display_order': 4448, 'source_order': 4448, 'sampling_weight': 10.0}, {'textbook_example_id': 4449, 'component_id': 'src_4449', 'generator_key': 'src_4449', 'presentation_mode': 'canvas', 'response_mode': 'canvas', 'interaction_type': 'canvas', 'source_kind': 'quiz', 'line_type': 'draw_linear_function_graph', 'answer_type': 'drawing', 'answer_value_type': 'drawing', 'problem_type_id': 'draw_linear_function_graph', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': None, 'display_order': 4449, 'source_order': 4449, 'sampling_weight': 10.0}, {'textbook_example_id': 4500, 'component_id': 'src_4500', 'generator_key': 'src_4500', 'presentation_mode': 'graph_single_choice', 'response_mode': 'graph_single_choice', 'interaction_type': 'graph_single_choice', 'source_kind': 'test', 'line_type': 'graph_based_linear_model_equation', 'answer_type': 'single_choice', 'answer_value_type': 'choice', 'problem_type_id': 'graph_based_linear_model_equation', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 4500, 'source_order': 4500, 'sampling_weight': 10.0}, {'textbook_example_id': 4515, 'component_id': 'src_4515', 'generator_key': 'src_4515', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'linear_equation_from_two_points_choice', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'linear_equation_from_two_points_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 4515, 'source_order': 4515, 'sampling_weight': 10.0}, {'textbook_example_id': 4516, 'component_id': 'src_4516', 'generator_key': 'src_4516', 'presentation_mode': 'graph_single_choice', 'response_mode': 'graph_single_choice', 'interaction_type': 'graph_single_choice', 'source_kind': 'test', 'line_type': 'linear_graph_feasibility_choice', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'linear_graph_feasibility_choice', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 4516, 'source_order': 4516, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_4424': 'components/src_4424/generate.py', 'src_4425': 'components/src_4425/generate.py', 'src_4426': 'components/src_4426/generate.py', 'src_4433': 'components/src_4433/generate.py', 'src_4434': 'components/src_4434/generate.py', 'src_4441': 'components/src_4441/generate.py', 'src_4442': 'components/src_4442/generate.py', 'src_4444': 'components/src_4444/generate.py', 'src_4445': 'components/src_4445/generate.py', 'src_4446': 'components/src_4446/generate.py', 'src_4448': 'components/src_4448/generate.py', 'src_4449': 'components/src_4449/generate.py', 'src_4500': 'components/src_4500/generate.py', 'src_4515': 'components/src_4515/generate.py', 'src_4516': 'components/src_4516/generate.py'}
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
        "answer_type",
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
            return str(hint_fn(step, payload) or "")
    return ""
