from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B2_SubSection_4_1_1'
GENERATOR_KEYS = ['src_11826', 'src_11827', 'src_11828', 'src_11829', 'src_11830', 'src_11831', 'src_11841', 'src_11842', 'src_11843', 'src_11844', 'src_11850', 'src_11877', 'src_11886', 'src_11887', 'src_11890', 'src_11891']
GENERATOR_SPECS = [{'textbook_example_id': 11826, 'component_id': 'src_11826', 'generator_key': 'src_11826', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'identify_center_radius_from_standard', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_standard', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11826, 'source_order': 11826, 'sampling_weight': 10.0}, {'textbook_example_id': 11827, 'component_id': 'src_11827', 'generator_key': 'src_11827', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'identify_center_radius_from_standard', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_standard', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11827, 'source_order': 11827, 'sampling_weight': 10.0}, {'textbook_example_id': 11828, 'component_id': 'src_11828', 'generator_key': 'src_11828', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'interpret_circular_locus_equation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'interpret_circular_locus_equation', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11828, 'source_order': 11828, 'sampling_weight': 10.0}, {'textbook_example_id': 11829, 'component_id': 'src_11829', 'generator_key': 'src_11829', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'write_circle_equations_from_conditions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_equations_from_conditions', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11829, 'source_order': 11829, 'sampling_weight': 10.0}, {'textbook_example_id': 11830, 'component_id': 'src_11830', 'generator_key': 'src_11830', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'circle_from_diameter_endpoints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_from_diameter_endpoints', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11830, 'source_order': 11830, 'sampling_weight': 10.0}, {'textbook_example_id': 11831, 'component_id': 'src_11831', 'generator_key': 'src_11831', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'circle_from_diameter_endpoints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_from_diameter_endpoints', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11831, 'source_order': 11831, 'sampling_weight': 10.0}, {'textbook_example_id': 11841, 'component_id': 'src_11841', 'generator_key': 'src_11841', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'identify_center_radius_from_standard', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'identify_center_radius_from_standard', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11841, 'source_order': 11841, 'sampling_weight': 10.0}, {'textbook_example_id': 11842, 'component_id': 'src_11842', 'generator_key': 'src_11842', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_equations_from_conditions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_equations_from_conditions', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11842, 'source_order': 11842, 'sampling_weight': 10.0}, {'textbook_example_id': 11843, 'component_id': 'src_11843', 'generator_key': 'src_11843', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'circle_equal_radius_at_origin', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_equal_radius_at_origin', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11843, 'source_order': 11843, 'sampling_weight': 10.0}, {'textbook_example_id': 11844, 'component_id': 'src_11844', 'generator_key': 'src_11844', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'circle_from_diameter_endpoints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_from_diameter_endpoints', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11844, 'source_order': 11844, 'sampling_weight': 10.0}, {'textbook_example_id': 11850, 'component_id': 'src_11850', 'generator_key': 'src_11850', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'translate_and_scale_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'translate_and_scale_circle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11850, 'source_order': 11850, 'sampling_weight': 10.0}, {'textbook_example_id': 11877, 'component_id': 'src_11877', 'generator_key': 'src_11877', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'translate_and_scale_circle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'translate_and_scale_circle', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11877, 'source_order': 11877, 'sampling_weight': 10.0}, {'textbook_example_id': 11886, 'component_id': 'src_11886', 'generator_key': 'src_11886', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'circle_origin_through_lines_intersection', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'circle_origin_through_lines_intersection', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11886, 'source_order': 11886, 'sampling_weight': 10.0}, {'textbook_example_id': 11887, 'component_id': 'src_11887', 'generator_key': 'src_11887', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'circle_same_center_scaled_area', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'circle_same_center_scaled_area', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11887, 'source_order': 11887, 'sampling_weight': 10.0}, {'textbook_example_id': 11890, 'component_id': 'src_11890', 'generator_key': 'src_11890', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'circle_center_tangent_to_line', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'circle_center_tangent_to_line', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11890, 'source_order': 11890, 'sampling_weight': 10.0}, {'textbook_example_id': 11891, 'component_id': 'src_11891', 'generator_key': 'src_11891', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'circle_from_diameter_endpoints', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'circle_from_diameter_endpoints', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11891, 'source_order': 11891, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_11826': 'components/src_11826/generate.py', 'src_11827': 'components/src_11827/generate.py', 'src_11828': 'components/src_11828/generate.py', 'src_11829': 'components/src_11829/generate.py', 'src_11830': 'components/src_11830/generate.py', 'src_11831': 'components/src_11831/generate.py', 'src_11841': 'components/src_11841/generate.py', 'src_11842': 'components/src_11842/generate.py', 'src_11843': 'components/src_11843/generate.py', 'src_11844': 'components/src_11844/generate.py', 'src_11850': 'components/src_11850/generate.py', 'src_11877': 'components/src_11877/generate.py', 'src_11886': 'components/src_11886/generate.py', 'src_11887': 'components/src_11887/generate.py', 'src_11890': 'components/src_11890/generate.py', 'src_11891': 'components/src_11891/generate.py'}
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
