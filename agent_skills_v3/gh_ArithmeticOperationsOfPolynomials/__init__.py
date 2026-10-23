from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_ArithmeticOperationsOfPolynomials'
GENERATOR_KEYS = ['src_12520', 'src_12521', 'src_12522', 'src_12523', 'src_12524', 'src_12525', 'src_12526', 'src_12527', 'src_12528', 'src_12529', 'src_12530', 'src_12531', 'src_12532', 'src_12533', 'src_12534', 'src_12535', 'src_12536', 'src_12537']
GENERATOR_SPECS = [{'textbook_example_id': 12520, 'component_id': 'src_12520', 'generator_key': 'src_12520', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12520, 'source_order': 12520, 'sampling_weight': 10.0}, {'textbook_example_id': 12521, 'component_id': 'src_12521', 'generator_key': 'src_12521', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12521, 'source_order': 12521, 'sampling_weight': 10.0}, {'textbook_example_id': 12522, 'component_id': 'src_12522', 'generator_key': 'src_12522', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_polynomial_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12522, 'source_order': 12522, 'sampling_weight': 10.0}, {'textbook_example_id': 12523, 'component_id': 'src_12523', 'generator_key': 'src_12523', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12523, 'source_order': 12523, 'sampling_weight': 10.0}, {'textbook_example_id': 12524, 'component_id': 'src_12524', 'generator_key': 'src_12524', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'taylor_shift_expansion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'taylor_shift_expansion', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12524, 'source_order': 12524, 'sampling_weight': 10.0}, {'textbook_example_id': 12525, 'component_id': 'src_12525', 'generator_key': 'src_12525', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_polynomial_values', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12525, 'source_order': 12525, 'sampling_weight': 10.0}, {'textbook_example_id': 12526, 'component_id': 'src_12526', 'generator_key': 'src_12526', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12526, 'source_order': 12526, 'sampling_weight': 10.0}, {'textbook_example_id': 12527, 'component_id': 'src_12527', 'generator_key': 'src_12527', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12527, 'source_order': 12527, 'sampling_weight': 10.0}, {'textbook_example_id': 12528, 'component_id': 'src_12528', 'generator_key': 'src_12528', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_polynomial_statements', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'evaluate_polynomial_statements', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12528, 'source_order': 12528, 'sampling_weight': 10.0}, {'textbook_example_id': 12529, 'component_id': 'src_12529', 'generator_key': 'src_12529', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_polynomial_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12529, 'source_order': 12529, 'sampling_weight': 10.0}, {'textbook_example_id': 12530, 'component_id': 'src_12530', 'generator_key': 'src_12530', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12530, 'source_order': 12530, 'sampling_weight': 10.0}, {'textbook_example_id': 12531, 'component_id': 'src_12531', 'generator_key': 'src_12531', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'taylor_shift_expansion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'taylor_shift_expansion', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12531, 'source_order': 12531, 'sampling_weight': 10.0}, {'textbook_example_id': 12532, 'component_id': 'src_12532', 'generator_key': 'src_12532', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12532, 'source_order': 12532, 'sampling_weight': 10.0}, {'textbook_example_id': 12533, 'component_id': 'src_12533', 'generator_key': 'src_12533', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_polynomial_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12533, 'source_order': 12533, 'sampling_weight': 10.0}, {'textbook_example_id': 12534, 'component_id': 'src_12534', 'generator_key': 'src_12534', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_arithmetic_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_arithmetic_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12534, 'source_order': 12534, 'sampling_weight': 10.0}, {'textbook_example_id': 12535, 'component_id': 'src_12535', 'generator_key': 'src_12535', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_divisor_from_quotient_remainder', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_divisor_from_quotient_remainder', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12535, 'source_order': 12535, 'sampling_weight': 10.0}, {'textbook_example_id': 12536, 'component_id': 'src_12536', 'generator_key': 'src_12536', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_values', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'evaluate_polynomial_values', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12536, 'source_order': 12536, 'sampling_weight': 10.0}, {'textbook_example_id': 12537, 'component_id': 'src_12537', 'generator_key': 'src_12537', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'taylor_shift_expansion', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'taylor_shift_expansion', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12537, 'source_order': 12537, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12520': 'components/src_12520/generate.py', 'src_12521': 'components/src_12521/generate.py', 'src_12522': 'components/src_12522/generate.py', 'src_12523': 'components/src_12523/generate.py', 'src_12524': 'components/src_12524/generate.py', 'src_12525': 'components/src_12525/generate.py', 'src_12526': 'components/src_12526/generate.py', 'src_12527': 'components/src_12527/generate.py', 'src_12528': 'components/src_12528/generate.py', 'src_12529': 'components/src_12529/generate.py', 'src_12530': 'components/src_12530/generate.py', 'src_12531': 'components/src_12531/generate.py', 'src_12532': 'components/src_12532/generate.py', 'src_12533': 'components/src_12533/generate.py', 'src_12534': 'components/src_12534/generate.py', 'src_12535': 'components/src_12535/generate.py', 'src_12536': 'components/src_12536/generate.py', 'src_12537': 'components/src_12537/generate.py'}
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
