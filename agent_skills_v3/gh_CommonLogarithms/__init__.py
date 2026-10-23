from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_CommonLogarithms'
GENERATOR_KEYS = ['src_12385', 'src_12386', 'src_12387', 'src_12388', 'src_12389', 'src_12390', 'src_12391', 'src_12392', 'src_12393', 'src_12394', 'src_12395', 'src_12396', 'src_12397', 'src_12398', 'src_12399', 'src_12400', 'src_12401', 'src_12402']
GENERATOR_SPECS = [{'textbook_example_id': 12385, 'component_id': 'src_12385', 'generator_key': 'src_12385', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_common_logarithm_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_common_logarithm_items', 'checker_key': None, 'equivalence_type': None, 'display_order': 12385, 'source_order': 12385, 'sampling_weight': 1.0}, {'textbook_example_id': 12386, 'component_id': 'src_12386', 'generator_key': 'src_12386', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_common_logarithm_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_common_logarithm_items', 'checker_key': None, 'equivalence_type': None, 'display_order': 12386, 'source_order': 12386, 'sampling_weight': 1.0}, {'textbook_example_id': 12387, 'component_id': 'src_12387', 'generator_key': 'src_12387', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12387, 'source_order': 12387, 'sampling_weight': 1.0}, {'textbook_example_id': 12388, 'component_id': 'src_12388', 'generator_key': 'src_12388', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'approximate_common_logarithm', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'approximate_common_logarithm', 'checker_key': None, 'equivalence_type': None, 'display_order': 12388, 'source_order': 12388, 'sampling_weight': 1.0}, {'textbook_example_id': 12389, 'component_id': 'src_12389', 'generator_key': 'src_12389', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'count_digits_of_integer_power', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'count_digits_of_integer_power', 'checker_key': None, 'equivalence_type': None, 'display_order': 12389, 'source_order': 12389, 'sampling_weight': 1.0}, {'textbook_example_id': 12390, 'component_id': 'src_12390', 'generator_key': 'src_12390', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'evaluate_common_logarithm_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_common_logarithm_items', 'checker_key': None, 'equivalence_type': None, 'display_order': 12390, 'source_order': 12390, 'sampling_weight': 1.0}, {'textbook_example_id': 12391, 'component_id': 'src_12391', 'generator_key': 'src_12391', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'evaluate_common_logarithm_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_common_logarithm_items', 'checker_key': None, 'equivalence_type': None, 'display_order': 12391, 'source_order': 12391, 'sampling_weight': 1.0}, {'textbook_example_id': 12392, 'component_id': 'src_12392', 'generator_key': 'src_12392', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12392, 'source_order': 12392, 'sampling_weight': 1.0}, {'textbook_example_id': 12393, 'component_id': 'src_12393', 'generator_key': 'src_12393', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'count_digits_of_integer_power', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'count_digits_of_integer_power', 'checker_key': None, 'equivalence_type': None, 'display_order': 12393, 'source_order': 12393, 'sampling_weight': 1.0}, {'textbook_example_id': 12394, 'component_id': 'src_12394', 'generator_key': 'src_12394', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_number_property_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_number_property_statements', 'checker_key': None, 'equivalence_type': None, 'display_order': 12394, 'source_order': 12394, 'sampling_weight': 1.0}, {'textbook_example_id': 12395, 'component_id': 'src_12395', 'generator_key': 'src_12395', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_exponent_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_exponent_statement_truth', 'checker_key': None, 'equivalence_type': None, 'display_order': 12395, 'source_order': 12395, 'sampling_weight': 1.0}, {'textbook_example_id': 12396, 'component_id': 'src_12396', 'generator_key': 'src_12396', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_exponent_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_exponent_statement_truth', 'checker_key': None, 'equivalence_type': None, 'display_order': 12396, 'source_order': 12396, 'sampling_weight': 1.0}, {'textbook_example_id': 12397, 'component_id': 'src_12397', 'generator_key': 'src_12397', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_number_property_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_number_property_statements', 'checker_key': None, 'equivalence_type': None, 'display_order': 12397, 'source_order': 12397, 'sampling_weight': 1.0}, {'textbook_example_id': 12398, 'component_id': 'src_12398', 'generator_key': 'src_12398', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_common_logarithm_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_common_logarithm_items', 'checker_key': None, 'equivalence_type': None, 'display_order': 12398, 'source_order': 12398, 'sampling_weight': 1.0}, {'textbook_example_id': 12399, 'component_id': 'src_12399', 'generator_key': 'src_12399', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_conditional_exponent_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_conditional_exponent_values', 'checker_key': None, 'equivalence_type': None, 'display_order': 12399, 'source_order': 12399, 'sampling_weight': 1.0}, {'textbook_example_id': 12400, 'component_id': 'src_12400', 'generator_key': 'src_12400', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_power_of_ten_exponent', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_power_of_ten_exponent', 'checker_key': None, 'equivalence_type': None, 'display_order': 12400, 'source_order': 12400, 'sampling_weight': 1.0}, {'textbook_example_id': 12401, 'component_id': 'src_12401', 'generator_key': 'src_12401', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_power_of_ten_exponent', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_power_of_ten_exponent', 'checker_key': None, 'equivalence_type': None, 'display_order': 12401, 'source_order': 12401, 'sampling_weight': 1.0}, {'textbook_example_id': 12402, 'component_id': 'src_12402', 'generator_key': 'src_12402', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'select_nearest_model_value', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'select_nearest_model_value', 'checker_key': None, 'equivalence_type': None, 'display_order': 12402, 'source_order': 12402, 'sampling_weight': 1.0}]
_COMPONENT_DISPATCH = {'src_12385': 'components/src_12385/generate.py', 'src_12386': 'components/src_12386/generate.py', 'src_12387': 'components/src_12387/generate.py', 'src_12388': 'components/src_12388/generate.py', 'src_12389': 'components/src_12389/generate.py', 'src_12390': 'components/src_12390/generate.py', 'src_12391': 'components/src_12391/generate.py', 'src_12392': 'components/src_12392/generate.py', 'src_12393': 'components/src_12393/generate.py', 'src_12394': 'components/src_12394/generate.py', 'src_12395': 'components/src_12395/generate.py', 'src_12396': 'components/src_12396/generate.py', 'src_12397': 'components/src_12397/generate.py', 'src_12398': 'components/src_12398/generate.py', 'src_12399': 'components/src_12399/generate.py', 'src_12400': 'components/src_12400/generate.py', 'src_12401': 'components/src_12401/generate.py', 'src_12402': 'components/src_12402/generate.py'}
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
