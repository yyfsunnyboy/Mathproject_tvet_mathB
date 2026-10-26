from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_Series'
GENERATOR_KEYS = ['src_12707', 'src_12708', 'src_12709', 'src_12710', 'src_12711', 'src_12712', 'src_12713', 'src_12714', 'src_12715', 'src_12716', 'src_12717', 'src_12718', 'src_12720', 'src_12721', 'src_12722', 'src_12723', 'src_12724', 'src_12725', 'src_12726', 'src_12728', 'src_12729', 'src_12730', 'src_12739', 'src_12743']
GENERATOR_SPECS = [{'textbook_example_id': 12707, 'component_id': 'src_12707', 'generator_key': 'src_12707', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'arithmetic_series_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12707, 'source_order': 12707, 'sampling_weight': 10.0}, {'textbook_example_id': 12708, 'component_id': 'src_12708', 'generator_key': 'src_12708', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'arithmetic_series_relation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_relation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12708, 'source_order': 12708, 'sampling_weight': 10.0}, {'textbook_example_id': 12709, 'component_id': 'src_12709', 'generator_key': 'src_12709', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'fish_rows', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'fish_rows', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12709, 'source_order': 12709, 'sampling_weight': 10.0}, {'textbook_example_id': 12710, 'component_id': 'src_12710', 'generator_key': 'src_12710', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'geometric_series_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_series_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12710, 'source_order': 12710, 'sampling_weight': 10.0}, {'textbook_example_id': 12711, 'component_id': 'src_12711', 'generator_key': 'src_12711', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_series_relation', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'geometric_series_relation', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12711, 'source_order': 12711, 'sampling_weight': 10.0}, {'textbook_example_id': 12712, 'component_id': 'src_12712', 'generator_key': 'src_12712', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_series_relation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'geometric_series_relation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12712, 'source_order': 12712, 'sampling_weight': 10.0}, {'textbook_example_id': 12713, 'component_id': 'src_12713', 'generator_key': 'src_12713', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'partial_sum_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'partial_sum_terms', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12713, 'source_order': 12713, 'sampling_weight': 10.0}, {'textbook_example_id': 12714, 'component_id': 'src_12714', 'generator_key': 'src_12714', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'arithmetic_series_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12714, 'source_order': 12714, 'sampling_weight': 10.0}, {'textbook_example_id': 12715, 'component_id': 'src_12715', 'generator_key': 'src_12715', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'arithmetic_series_relation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_relation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12715, 'source_order': 12715, 'sampling_weight': 10.0}, {'textbook_example_id': 12716, 'component_id': 'src_12716', 'generator_key': 'src_12716', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'arithmetic_series_relation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'arithmetic_series_relation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12716, 'source_order': 12716, 'sampling_weight': 10.0}, {'textbook_example_id': 12717, 'component_id': 'src_12717', 'generator_key': 'src_12717', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'geometric_series_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_series_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12717, 'source_order': 12717, 'sampling_weight': 10.0}, {'textbook_example_id': 12718, 'component_id': 'src_12718', 'generator_key': 'src_12718', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'geometric_series_relation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'geometric_series_relation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12718, 'source_order': 12718, 'sampling_weight': 10.0}, {'textbook_example_id': 12720, 'component_id': 'src_12720', 'generator_key': 'src_12720', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'partial_sum_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'partial_sum_terms', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12720, 'source_order': 12720, 'sampling_weight': 10.0}, {'textbook_example_id': 12721, 'component_id': 'src_12721', 'generator_key': 'src_12721', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'series_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'series_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12721, 'source_order': 12721, 'sampling_weight': 10.0}, {'textbook_example_id': 12722, 'component_id': 'src_12722', 'generator_key': 'src_12722', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'arithmetic_series_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_series_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12722, 'source_order': 12722, 'sampling_weight': 10.0}, {'textbook_example_id': 12723, 'component_id': 'src_12723', 'generator_key': 'src_12723', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'arithmetic_series_relation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'arithmetic_series_relation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12723, 'source_order': 12723, 'sampling_weight': 10.0}, {'textbook_example_id': 12724, 'component_id': 'src_12724', 'generator_key': 'src_12724', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'arithmetic_series_relation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'arithmetic_series_relation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12724, 'source_order': 12724, 'sampling_weight': 10.0}, {'textbook_example_id': 12725, 'component_id': 'src_12725', 'generator_key': 'src_12725', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'geometric_series_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_series_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12725, 'source_order': 12725, 'sampling_weight': 10.0}, {'textbook_example_id': 12726, 'component_id': 'src_12726', 'generator_key': 'src_12726', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'geometric_series_relation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_series_relation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12726, 'source_order': 12726, 'sampling_weight': 10.0}, {'textbook_example_id': 12728, 'component_id': 'src_12728', 'generator_key': 'src_12728', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'partial_sum_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'partial_sum_terms', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12728, 'source_order': 12728, 'sampling_weight': 10.0}, {'textbook_example_id': 12729, 'component_id': 'src_12729', 'generator_key': 'src_12729', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'arithmetic_series_relation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'arithmetic_series_relation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12729, 'source_order': 12729, 'sampling_weight': 10.0}, {'textbook_example_id': 12730, 'component_id': 'src_12730', 'generator_key': 'src_12730', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_series_relation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'geometric_series_relation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12730, 'source_order': 12730, 'sampling_weight': 10.0}, {'textbook_example_id': 12739, 'component_id': 'src_12739', 'generator_key': 'src_12739', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'series_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'series_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12739, 'source_order': 12739, 'sampling_weight': 10.0}, {'textbook_example_id': 12743, 'component_id': 'src_12743', 'generator_key': 'src_12743', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'geometric_series_relation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_series_relation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12743, 'source_order': 12743, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12707': 'components/src_12707/generate.py', 'src_12708': 'components/src_12708/generate.py', 'src_12709': 'components/src_12709/generate.py', 'src_12710': 'components/src_12710/generate.py', 'src_12711': 'components/src_12711/generate.py', 'src_12712': 'components/src_12712/generate.py', 'src_12713': 'components/src_12713/generate.py', 'src_12714': 'components/src_12714/generate.py', 'src_12715': 'components/src_12715/generate.py', 'src_12716': 'components/src_12716/generate.py', 'src_12717': 'components/src_12717/generate.py', 'src_12718': 'components/src_12718/generate.py', 'src_12720': 'components/src_12720/generate.py', 'src_12721': 'components/src_12721/generate.py', 'src_12722': 'components/src_12722/generate.py', 'src_12723': 'components/src_12723/generate.py', 'src_12724': 'components/src_12724/generate.py', 'src_12725': 'components/src_12725/generate.py', 'src_12726': 'components/src_12726/generate.py', 'src_12728': 'components/src_12728/generate.py', 'src_12729': 'components/src_12729/generate.py', 'src_12730': 'components/src_12730/generate.py', 'src_12739': 'components/src_12739/generate.py', 'src_12743': 'components/src_12743/generate.py'}
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
