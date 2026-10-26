from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_Sequence'
GENERATOR_KEYS = ['src_12667', 'src_12668', 'src_12669', 'src_12670', 'src_12671', 'src_12672', 'src_12673', 'src_12674', 'src_12675', 'src_12676', 'src_12677', 'src_12678', 'src_12679', 'src_12680', 'src_12681', 'src_12682', 'src_12683', 'src_12684', 'src_12685']
GENERATOR_SPECS = [{'textbook_example_id': 12667, 'component_id': 'src_12667', 'generator_key': 'src_12667', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'sequence_terms_from_formula', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'sequence_terms_from_formula', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12667, 'source_order': 12667, 'sampling_weight': 10.0}, {'textbook_example_id': 12668, 'component_id': 'src_12668', 'generator_key': 'src_12668', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'figure_path_pattern', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'figure_path_pattern', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12668, 'source_order': 12668, 'sampling_weight': 10.0}, {'textbook_example_id': 12669, 'component_id': 'src_12669', 'generator_key': 'src_12669', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'geometric_from_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_from_terms', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12669, 'source_order': 12669, 'sampling_weight': 10.0}, {'textbook_example_id': 12670, 'component_id': 'src_12670', 'generator_key': 'src_12670', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_from_relations', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'geometric_from_relations', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12670, 'source_order': 12670, 'sampling_weight': 10.0}, {'textbook_example_id': 12671, 'component_id': 'src_12671', 'generator_key': 'src_12671', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'progression_three_numbers', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'progression_three_numbers', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12671, 'source_order': 12671, 'sampling_weight': 10.0}, {'textbook_example_id': 12672, 'component_id': 'src_12672', 'generator_key': 'src_12672', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'sequence_terms_from_formula', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'sequence_terms_from_formula', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12672, 'source_order': 12672, 'sampling_weight': 10.0}, {'textbook_example_id': 12673, 'component_id': 'src_12673', 'generator_key': 'src_12673', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'finger_counting_cycle', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'finger_counting_cycle', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12673, 'source_order': 12673, 'sampling_weight': 10.0}, {'textbook_example_id': 12674, 'component_id': 'src_12674', 'generator_key': 'src_12674', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'geometric_from_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_from_terms', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12674, 'source_order': 12674, 'sampling_weight': 10.0}, {'textbook_example_id': 12675, 'component_id': 'src_12675', 'generator_key': 'src_12675', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'geometric_from_relations', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'geometric_from_relations', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12675, 'source_order': 12675, 'sampling_weight': 10.0}, {'textbook_example_id': 12676, 'component_id': 'src_12676', 'generator_key': 'src_12676', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'progression_three_numbers', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'progression_three_numbers', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12676, 'source_order': 12676, 'sampling_weight': 10.0}, {'textbook_example_id': 12677, 'component_id': 'src_12677', 'generator_key': 'src_12677', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'sequence_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'sequence_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12677, 'source_order': 12677, 'sampling_weight': 10.0}, {'textbook_example_id': 12678, 'component_id': 'src_12678', 'generator_key': 'src_12678', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'sequence_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'sequence_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12678, 'source_order': 12678, 'sampling_weight': 10.0}, {'textbook_example_id': 12679, 'component_id': 'src_12679', 'generator_key': 'src_12679', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'sequence_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'sequence_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12679, 'source_order': 12679, 'sampling_weight': 10.0}, {'textbook_example_id': 12680, 'component_id': 'src_12680', 'generator_key': 'src_12680', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'sequence_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'sequence_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12680, 'source_order': 12680, 'sampling_weight': 10.0}, {'textbook_example_id': 12681, 'component_id': 'src_12681', 'generator_key': 'src_12681', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'arithmetic_from_terms', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'arithmetic_from_terms', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12681, 'source_order': 12681, 'sampling_weight': 10.0}, {'textbook_example_id': 12682, 'component_id': 'src_12682', 'generator_key': 'src_12682', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'geometric_from_relations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'geometric_from_relations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12682, 'source_order': 12682, 'sampling_weight': 10.0}, {'textbook_example_id': 12683, 'component_id': 'src_12683', 'generator_key': 'src_12683', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'geometric_from_relations', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'geometric_from_relations', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12683, 'source_order': 12683, 'sampling_weight': 10.0}, {'textbook_example_id': 12684, 'component_id': 'src_12684', 'generator_key': 'src_12684', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'progression_three_numbers', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'progression_three_numbers', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12684, 'source_order': 12684, 'sampling_weight': 10.0}, {'textbook_example_id': 12685, 'component_id': 'src_12685', 'generator_key': 'src_12685', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'progression_three_numbers', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'progression_three_numbers', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12685, 'source_order': 12685, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12667': 'components/src_12667/generate.py', 'src_12668': 'components/src_12668/generate.py', 'src_12669': 'components/src_12669/generate.py', 'src_12670': 'components/src_12670/generate.py', 'src_12671': 'components/src_12671/generate.py', 'src_12672': 'components/src_12672/generate.py', 'src_12673': 'components/src_12673/generate.py', 'src_12674': 'components/src_12674/generate.py', 'src_12675': 'components/src_12675/generate.py', 'src_12676': 'components/src_12676/generate.py', 'src_12677': 'components/src_12677/generate.py', 'src_12678': 'components/src_12678/generate.py', 'src_12679': 'components/src_12679/generate.py', 'src_12680': 'components/src_12680/generate.py', 'src_12681': 'components/src_12681/generate.py', 'src_12682': 'components/src_12682/generate.py', 'src_12683': 'components/src_12683/generate.py', 'src_12684': 'components/src_12684/generate.py', 'src_12685': 'components/src_12685/generate.py'}
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
