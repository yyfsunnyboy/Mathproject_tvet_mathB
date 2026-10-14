from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B1_PolynomialArithmeticOperations'
GENERATOR_KEYS = ['src_4612', 'src_4613', 'src_4614', 'src_4615', 'src_4616', 'src_4617', 'src_4622', 'src_4623', 'src_4624', 'src_4625', 'src_4626', 'src_4627', 'src_4633', 'src_4634', 'src_4635', 'src_4636', 'src_4637', 'src_4706']
GENERATOR_SPECS = [{'textbook_example_id': 4612, 'component_id': 'src_4612', 'generator_key': 'src_4612', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_add_sub', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_add_sub', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4612, 'source_order': 4612, 'sampling_weight': 10.0}, {'textbook_example_id': 4613, 'component_id': 'src_4613', 'generator_key': 'src_4613', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_product_term_coefficient', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_product_term_coefficient', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4613, 'source_order': 4613, 'sampling_weight': 10.0}, {'textbook_example_id': 4614, 'component_id': 'src_4614', 'generator_key': 'src_4614', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_long_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_long_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4614, 'source_order': 4614, 'sampling_weight': 10.0}, {'textbook_example_id': 4615, 'component_id': 'src_4615', 'generator_key': 'src_4615', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_long_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_long_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4615, 'source_order': 4615, 'sampling_weight': 10.0}, {'textbook_example_id': 4616, 'component_id': 'src_4616', 'generator_key': 'src_4616', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_synthetic_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_synthetic_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4616, 'source_order': 4616, 'sampling_weight': 10.0}, {'textbook_example_id': 4617, 'component_id': 'src_4617', 'generator_key': 'src_4617', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_shifted_basis_eval', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_shifted_basis_eval', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4617, 'source_order': 4617, 'sampling_weight': 10.0}, {'textbook_example_id': 4622, 'component_id': 'src_4622', 'generator_key': 'src_4622', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_add_sub', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_add_sub', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4622, 'source_order': 4622, 'sampling_weight': 10.0}, {'textbook_example_id': 4623, 'component_id': 'src_4623', 'generator_key': 'src_4623', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_multiply', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_multiply', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4623, 'source_order': 4623, 'sampling_weight': 10.0}, {'textbook_example_id': 4624, 'component_id': 'src_4624', 'generator_key': 'src_4624', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_product_term_coefficient', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_product_term_coefficient', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4624, 'source_order': 4624, 'sampling_weight': 10.0}, {'textbook_example_id': 4625, 'component_id': 'src_4625', 'generator_key': 'src_4625', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_long_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_long_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4625, 'source_order': 4625, 'sampling_weight': 10.0}, {'textbook_example_id': 4626, 'component_id': 'src_4626', 'generator_key': 'src_4626', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_synthetic_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_synthetic_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4626, 'source_order': 4626, 'sampling_weight': 10.0}, {'textbook_example_id': 4627, 'component_id': 'src_4627', 'generator_key': 'src_4627', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_remainder_param_solve', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_remainder_param_solve', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4627, 'source_order': 4627, 'sampling_weight': 10.0}, {'textbook_example_id': 4633, 'component_id': 'src_4633', 'generator_key': 'src_4633', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_add_sub', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_add_sub', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4633, 'source_order': 4633, 'sampling_weight': 10.0}, {'textbook_example_id': 4634, 'component_id': 'src_4634', 'generator_key': 'src_4634', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_multiply', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_multiply', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4634, 'source_order': 4634, 'sampling_weight': 10.0}, {'textbook_example_id': 4635, 'component_id': 'src_4635', 'generator_key': 'src_4635', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_product_term_coefficient', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_product_term_coefficient', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4635, 'source_order': 4635, 'sampling_weight': 10.0}, {'textbook_example_id': 4636, 'component_id': 'src_4636', 'generator_key': 'src_4636', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_long_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_long_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4636, 'source_order': 4636, 'sampling_weight': 10.0}, {'textbook_example_id': 4637, 'component_id': 'src_4637', 'generator_key': 'src_4637', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_synthetic_division', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_synthetic_division', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4637, 'source_order': 4637, 'sampling_weight': 10.0}, {'textbook_example_id': 4706, 'component_id': 'src_4706', 'generator_key': 'src_4706', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'polynomial_product_term_coefficient', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_product_term_coefficient', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4706, 'source_order': 4706, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_4612': 'components/src_4612/generate.py', 'src_4613': 'components/src_4613/generate.py', 'src_4614': 'components/src_4614/generate.py', 'src_4615': 'components/src_4615/generate.py', 'src_4616': 'components/src_4616/generate.py', 'src_4617': 'components/src_4617/generate.py', 'src_4622': 'components/src_4622/generate.py', 'src_4623': 'components/src_4623/generate.py', 'src_4624': 'components/src_4624/generate.py', 'src_4625': 'components/src_4625/generate.py', 'src_4626': 'components/src_4626/generate.py', 'src_4627': 'components/src_4627/generate.py', 'src_4633': 'components/src_4633/generate.py', 'src_4634': 'components/src_4634/generate.py', 'src_4635': 'components/src_4635/generate.py', 'src_4636': 'components/src_4636/generate.py', 'src_4637': 'components/src_4637/generate.py', 'src_4706': 'components/src_4706/generate.py'}
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
