from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B2_SubSection_1_4_4'
GENERATOR_KEYS = ['src_11663', 'src_11664', 'src_11665', 'src_11666', 'src_11667', 'src_11668', 'src_11669', 'src_11670', 'src_11671', 'src_11672', 'src_11673', 'src_11674', 'src_11675']
GENERATOR_SPECS = [{'textbook_example_id': 11663, 'component_id': 'src_11663', 'generator_key': 'src_11663', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'example', 'line_type': 'calculate_trig_period_from_argument_scale', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'calculate_trig_period_from_argument_scale', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 9, 'source_order': 9, 'sampling_weight': 1.0}, {'textbook_example_id': 11664, 'component_id': 'src_11664', 'generator_key': 'src_11664', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'calculate_trig_period_from_argument_scale', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'calculate_trig_period_from_argument_scale', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 10, 'source_order': 10, 'sampling_weight': 1.0}, {'textbook_example_id': 11665, 'component_id': 'src_11665', 'generator_key': 'src_11665', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'classify_trig_expression_sign_change', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'classify_trig_expression_sign_change', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 11, 'source_order': 11, 'sampling_weight': 1.0}, {'textbook_example_id': 11666, 'component_id': 'src_11666', 'generator_key': 'src_11666', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'compare_trig_values_by_monotonicity', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compare_trig_values_by_monotonicity', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 12, 'source_order': 12, 'sampling_weight': 1.0}, {'textbook_example_id': 11667, 'component_id': 'src_11667', 'generator_key': 'src_11667', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'exercise', 'line_type': 'classify_trig_equation_feasibility', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'classify_trig_equation_feasibility', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label', 'display_order': 13, 'source_order': 13, 'sampling_weight': 1.0}, {'textbook_example_id': 11668, 'component_id': 'src_11668', 'generator_key': 'src_11668', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'solve_trig_value_quadratic_constraint', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_trig_value_quadratic_constraint', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 14, 'source_order': 14, 'sampling_weight': 1.0}, {'textbook_example_id': 11669, 'component_id': 'src_11669', 'generator_key': 'src_11669', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'analyze_affine_transformed_trig_graph', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_affine_transformed_trig_graph', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 15, 'source_order': 15, 'sampling_weight': 1.0}, {'textbook_example_id': 11670, 'component_id': 'src_11670', 'generator_key': 'src_11670', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'analyze_affine_transformed_trig_graph', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_affine_transformed_trig_graph', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 16, 'source_order': 16, 'sampling_weight': 1.0}, {'textbook_example_id': 11671, 'component_id': 'src_11671', 'generator_key': 'src_11671', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'analyze_tangent_absolute_graph_period', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_tangent_absolute_graph_period', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 17, 'source_order': 17, 'sampling_weight': 1.0}, {'textbook_example_id': 11672, 'component_id': 'src_11672', 'generator_key': 'src_11672', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'calculate_trig_period_from_argument_scale', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'calculate_trig_period_from_argument_scale', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 18, 'source_order': 18, 'sampling_weight': 1.0}, {'textbook_example_id': 11673, 'component_id': 'src_11673', 'generator_key': 'src_11673', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'evaluate_trig_decimal', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_trig_decimal', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 19, 'source_order': 19, 'sampling_weight': 1.0}, {'textbook_example_id': 11674, 'component_id': 'src_11674', 'generator_key': 'src_11674', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'count_sine_cosine_intersections', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'count_sine_cosine_intersections', 'checker_key': 'expression_checker', 'equivalence_type': 'algebraic_equivalent', 'display_order': 20, 'source_order': 20, 'sampling_weight': 1.0}, {'textbook_example_id': 11675, 'component_id': 'src_11675', 'generator_key': 'src_11675', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multi_part', 'interaction_type': 'multi_part', 'source_kind': 'exercise', 'line_type': 'analyze_affine_transformed_trig_graph', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'analyze_affine_transformed_trig_graph', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 21, 'source_order': 21, 'sampling_weight': 1.0}]
_COMPONENT_DISPATCH = {'src_11663': 'components/src_11663/generate.py', 'src_11664': 'components/src_11664/generate.py', 'src_11665': 'components/src_11665/generate.py', 'src_11666': 'components/src_11666/generate.py', 'src_11667': 'components/src_11667/generate.py', 'src_11668': 'components/src_11668/generate.py', 'src_11669': 'components/src_11669/generate.py', 'src_11670': 'components/src_11670/generate.py', 'src_11671': 'components/src_11671/generate.py', 'src_11672': 'components/src_11672/generate.py', 'src_11673': 'components/src_11673/generate.py', 'src_11674': 'components/src_11674/generate.py', 'src_11675': 'components/src_11675/generate.py'}
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
