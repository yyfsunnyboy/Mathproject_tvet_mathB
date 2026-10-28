from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_LinearPermutation'
GENERATOR_KEYS = ['src_12774', 'src_12775', 'src_12776', 'src_12777', 'src_12778', 'src_12779', 'src_12780', 'src_12781', 'src_12782', 'src_12783', 'src_12784', 'src_12785', 'src_12786', 'src_12787', 'src_12788', 'src_12789', 'src_12790', 'src_12791', 'src_12792']
GENERATOR_SPECS = [{'textbook_example_id': 12774, 'component_id': 'src_12774', 'generator_key': 'src_12774', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'selected_arrangement', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'selected_arrangement', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12774, 'source_order': 12774, 'sampling_weight': 10.0}, {'textbook_example_id': 12775, 'component_id': 'src_12775', 'generator_key': 'src_12775', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'selected_arrangement', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'selected_arrangement', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12775, 'source_order': 12775, 'sampling_weight': 10.0}, {'textbook_example_id': 12776, 'component_id': 'src_12776', 'generator_key': 'src_12776', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'distinct_digit_numbers', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'distinct_digit_numbers', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12776, 'source_order': 12776, 'sampling_weight': 10.0}, {'textbook_example_id': 12777, 'component_id': 'src_12777', 'generator_key': 'src_12777', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'adjacent_separated', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'adjacent_separated', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12777, 'source_order': 12777, 'sampling_weight': 10.0}, {'textbook_example_id': 12778, 'component_id': 'src_12778', 'generator_key': 'src_12778', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'restricted_assignment', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'restricted_assignment', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12778, 'source_order': 12778, 'sampling_weight': 10.0}, {'textbook_example_id': 12779, 'component_id': 'src_12779', 'generator_key': 'src_12779', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'selected_arrangement', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'selected_arrangement', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12779, 'source_order': 12779, 'sampling_weight': 10.0}, {'textbook_example_id': 12780, 'component_id': 'src_12780', 'generator_key': 'src_12780', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'selected_arrangement', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'selected_arrangement', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12780, 'source_order': 12780, 'sampling_weight': 10.0}, {'textbook_example_id': 12781, 'component_id': 'src_12781', 'generator_key': 'src_12781', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'restricted_assignment', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'restricted_assignment', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12781, 'source_order': 12781, 'sampling_weight': 10.0}, {'textbook_example_id': 12782, 'component_id': 'src_12782', 'generator_key': 'src_12782', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'two_group_line', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'two_group_line', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12782, 'source_order': 12782, 'sampling_weight': 10.0}, {'textbook_example_id': 12783, 'component_id': 'src_12783', 'generator_key': 'src_12783', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'restricted_assignment', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'restricted_assignment', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12783, 'source_order': 12783, 'sampling_weight': 10.0}, {'textbook_example_id': 12784, 'component_id': 'src_12784', 'generator_key': 'src_12784', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'counting_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'counting_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12784, 'source_order': 12784, 'sampling_weight': 10.0}, {'textbook_example_id': 12785, 'component_id': 'src_12785', 'generator_key': 'src_12785', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'counting_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'counting_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12785, 'source_order': 12785, 'sampling_weight': 10.0}, {'textbook_example_id': 12786, 'component_id': 'src_12786', 'generator_key': 'src_12786', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'selected_arrangement', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'selected_arrangement', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12786, 'source_order': 12786, 'sampling_weight': 10.0}, {'textbook_example_id': 12787, 'component_id': 'src_12787', 'generator_key': 'src_12787', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'distinct_digit_numbers', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'distinct_digit_numbers', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12787, 'source_order': 12787, 'sampling_weight': 10.0}, {'textbook_example_id': 12788, 'component_id': 'src_12788', 'generator_key': 'src_12788', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'restricted_assignment', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'restricted_assignment', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12788, 'source_order': 12788, 'sampling_weight': 10.0}, {'textbook_example_id': 12789, 'component_id': 'src_12789', 'generator_key': 'src_12789', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'ends_from_group', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'ends_from_group', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12789, 'source_order': 12789, 'sampling_weight': 10.0}, {'textbook_example_id': 12790, 'component_id': 'src_12790', 'generator_key': 'src_12790', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'ends_and_block', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'ends_and_block', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12790, 'source_order': 12790, 'sampling_weight': 10.0}, {'textbook_example_id': 12791, 'component_id': 'src_12791', 'generator_key': 'src_12791', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'fixed_order_insertion', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'fixed_order_insertion', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12791, 'source_order': 12791, 'sampling_weight': 10.0}, {'textbook_example_id': 12792, 'component_id': 'src_12792', 'generator_key': 'src_12792', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'relative_order_three', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'relative_order_three', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12792, 'source_order': 12792, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12774': 'components/src_12774/generate.py', 'src_12775': 'components/src_12775/generate.py', 'src_12776': 'components/src_12776/generate.py', 'src_12777': 'components/src_12777/generate.py', 'src_12778': 'components/src_12778/generate.py', 'src_12779': 'components/src_12779/generate.py', 'src_12780': 'components/src_12780/generate.py', 'src_12781': 'components/src_12781/generate.py', 'src_12782': 'components/src_12782/generate.py', 'src_12783': 'components/src_12783/generate.py', 'src_12784': 'components/src_12784/generate.py', 'src_12785': 'components/src_12785/generate.py', 'src_12786': 'components/src_12786/generate.py', 'src_12787': 'components/src_12787/generate.py', 'src_12788': 'components/src_12788/generate.py', 'src_12789': 'components/src_12789/generate.py', 'src_12790': 'components/src_12790/generate.py', 'src_12791': 'components/src_12791/generate.py', 'src_12792': 'components/src_12792/generate.py'}
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
