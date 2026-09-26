from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B3_SubSection_1_1_5'
GENERATOR_KEYS = ['src_11908', 'src_11909', 'src_11910', 'src_11911', 'src_11912', 'src_11919', 'src_11920', 'src_11921', 'src_11964', 'src_11965', 'src_11967', 'src_11968']
GENERATOR_SPECS = [{'textbook_example_id': 11908, 'component_id': 'src_11908', 'generator_key': 'src_11908', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'arithmetic_series_sum_given', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_sum_given', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11908, 'source_order': 11908, 'sampling_weight': 10.0}, {'textbook_example_id': 11909, 'component_id': 'src_11909', 'generator_key': 'src_11909', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'arithmetic_series_sum_given', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_sum_given', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11909, 'source_order': 11909, 'sampling_weight': 10.0}, {'textbook_example_id': 11910, 'component_id': 'src_11910', 'generator_key': 'src_11910', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'arithmetic_series_recover_param', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_recover_param', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11910, 'source_order': 11910, 'sampling_weight': 10.0}, {'textbook_example_id': 11911, 'component_id': 'src_11911', 'generator_key': 'src_11911', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'arithmetic_series_recover_param', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_recover_param', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11911, 'source_order': 11911, 'sampling_weight': 10.0}, {'textbook_example_id': 11912, 'component_id': 'src_11912', 'generator_key': 'src_11912', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'arithmetic_odd_count_mid_total', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'arithmetic_odd_count_mid_total', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11912, 'source_order': 11912, 'sampling_weight': 10.0}, {'textbook_example_id': 11919, 'component_id': 'src_11919', 'generator_key': 'src_11919', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'arithmetic_series_sum_given', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_sum_given', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11919, 'source_order': 11919, 'sampling_weight': 10.0}, {'textbook_example_id': 11920, 'component_id': 'src_11920', 'generator_key': 'src_11920', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'arithmetic_series_from_two_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_from_two_terms', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11920, 'source_order': 11920, 'sampling_weight': 10.0}, {'textbook_example_id': 11921, 'component_id': 'src_11921', 'generator_key': 'src_11921', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'exercise', 'line_type': 'arithmetic_index_and_total_sum', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'arithmetic_index_and_total_sum', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 11921, 'source_order': 11921, 'sampling_weight': 10.0}, {'textbook_example_id': 11964, 'component_id': 'src_11964', 'generator_key': 'src_11964', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'arithmetic_series_from_two_terms', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'arithmetic_series_from_two_terms', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11964, 'source_order': 11964, 'sampling_weight': 10.0}, {'textbook_example_id': 11965, 'component_id': 'src_11965', 'generator_key': 'src_11965', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'arithmetic_series_sum_given', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_sum_given', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11965, 'source_order': 11965, 'sampling_weight': 10.0}, {'textbook_example_id': 11967, 'component_id': 'src_11967', 'generator_key': 'src_11967', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'arithmetic_series_recover_param', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_recover_param', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11967, 'source_order': 11967, 'sampling_weight': 10.0}, {'textbook_example_id': 11968, 'component_id': 'src_11968', 'generator_key': 'src_11968', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'arithmetic_sum_multiples_range', 'answer_type': 'single_choice', 'answer_value_type': 'single_choice', 'problem_type_id': 'arithmetic_sum_multiples_range', 'checker_key': 'single_choice_checker', 'equivalence_type': None, 'display_order': 11968, 'source_order': 11968, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_11908': 'components/src_11908/generate.py', 'src_11909': 'components/src_11909/generate.py', 'src_11910': 'components/src_11910/generate.py', 'src_11911': 'components/src_11911/generate.py', 'src_11912': 'components/src_11912/generate.py', 'src_11919': 'components/src_11919/generate.py', 'src_11920': 'components/src_11920/generate.py', 'src_11921': 'components/src_11921/generate.py', 'src_11964': 'components/src_11964/generate.py', 'src_11965': 'components/src_11965/generate.py', 'src_11967': 'components/src_11967/generate.py', 'src_11968': 'components/src_11968/generate.py'}
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
