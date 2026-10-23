from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_RemainderTheorem'
GENERATOR_KEYS = ['src_12518', 'src_12525', 'src_12536', 'src_12538', 'src_12539', 'src_12540', 'src_12541', 'src_12542', 'src_12543', 'src_12544', 'src_12545', 'src_12546', 'src_12547', 'src_12548', 'src_12549']
GENERATOR_SPECS = [{'textbook_example_id': 12518, 'component_id': 'src_12518', 'generator_key': 'src_12518', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_polynomial_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12518, 'source_order': 12518, 'sampling_weight': 10.0}, {'textbook_example_id': 12525, 'component_id': 'src_12525', 'generator_key': 'src_12525', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_values', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_polynomial_values', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12525, 'source_order': 12525, 'sampling_weight': 10.0}, {'textbook_example_id': 12536, 'component_id': 'src_12536', 'generator_key': 'src_12536', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_values', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'evaluate_polynomial_values', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12536, 'source_order': 12536, 'sampling_weight': 10.0}, {'textbook_example_id': 12538, 'component_id': 'src_12538', 'generator_key': 'src_12538', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_values', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'evaluate_polynomial_values', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12538, 'source_order': 12538, 'sampling_weight': 10.0}, {'textbook_example_id': 12539, 'component_id': 'src_12539', 'generator_key': 'src_12539', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_remainder_from_conditions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_remainder_from_conditions', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12539, 'source_order': 12539, 'sampling_weight': 10.0}, {'textbook_example_id': 12540, 'component_id': 'src_12540', 'generator_key': 'src_12540', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_polynomial_values', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'evaluate_polynomial_values', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12540, 'source_order': 12540, 'sampling_weight': 10.0}, {'textbook_example_id': 12541, 'component_id': 'src_12541', 'generator_key': 'src_12541', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_polynomial_values', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'evaluate_polynomial_values', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12541, 'source_order': 12541, 'sampling_weight': 10.0}, {'textbook_example_id': 12542, 'component_id': 'src_12542', 'generator_key': 'src_12542', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_remainder_from_conditions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_remainder_from_conditions', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12542, 'source_order': 12542, 'sampling_weight': 10.0}, {'textbook_example_id': 12543, 'component_id': 'src_12543', 'generator_key': 'src_12543', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_polynomial_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12543, 'source_order': 12543, 'sampling_weight': 10.0}, {'textbook_example_id': 12544, 'component_id': 'src_12544', 'generator_key': 'src_12544', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_polynomial_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12544, 'source_order': 12544, 'sampling_weight': 10.0}, {'textbook_example_id': 12545, 'component_id': 'src_12545', 'generator_key': 'src_12545', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_remainder_from_conditions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_remainder_from_conditions', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12545, 'source_order': 12545, 'sampling_weight': 10.0}, {'textbook_example_id': 12546, 'component_id': 'src_12546', 'generator_key': 'src_12546', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_polynomial_statements', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'evaluate_polynomial_statements', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12546, 'source_order': 12546, 'sampling_weight': 10.0}, {'textbook_example_id': 12547, 'component_id': 'src_12547', 'generator_key': 'src_12547', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_remainder_from_conditions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_remainder_from_conditions', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12547, 'source_order': 12547, 'sampling_weight': 10.0}, {'textbook_example_id': 12548, 'component_id': 'src_12548', 'generator_key': 'src_12548', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_polynomial_from_remainder_congruences', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_from_remainder_congruences', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12548, 'source_order': 12548, 'sampling_weight': 10.0}, {'textbook_example_id': 12549, 'component_id': 'src_12549', 'generator_key': 'src_12549', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_remainder_with_linear_part', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_remainder_with_linear_part', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12549, 'source_order': 12549, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12518': 'components/src_12518/generate.py', 'src_12525': 'components/src_12525/generate.py', 'src_12536': 'components/src_12536/generate.py', 'src_12538': 'components/src_12538/generate.py', 'src_12539': 'components/src_12539/generate.py', 'src_12540': 'components/src_12540/generate.py', 'src_12541': 'components/src_12541/generate.py', 'src_12542': 'components/src_12542/generate.py', 'src_12543': 'components/src_12543/generate.py', 'src_12544': 'components/src_12544/generate.py', 'src_12545': 'components/src_12545/generate.py', 'src_12546': 'components/src_12546/generate.py', 'src_12547': 'components/src_12547/generate.py', 'src_12548': 'components/src_12548/generate.py', 'src_12549': 'components/src_12549/generate.py'}
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
