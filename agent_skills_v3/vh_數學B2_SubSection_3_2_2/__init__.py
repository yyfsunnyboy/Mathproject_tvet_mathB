from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B2_SubSection_3_2_2'
GENERATOR_KEYS = ['src_11762', 'src_11763', 'src_11764', 'src_11765', 'src_11766', 'src_11767', 'src_11776', 'src_11777', 'src_11778', 'src_11779', 'src_11780', 'src_11807', 'src_11808', 'src_11819', 'src_11821']
GENERATOR_SPECS = [{'textbook_example_id': 11762, 'component_id': 'src_11762', 'generator_key': 'src_11762', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_vector_sum_difference', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_sum_difference', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11762, 'source_order': 11762, 'sampling_weight': 10.0}, {'textbook_example_id': 11763, 'component_id': 'src_11763', 'generator_key': 'src_11763', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_vector_sum_difference', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_sum_difference', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11763, 'source_order': 11763, 'sampling_weight': 10.0}, {'textbook_example_id': 11764, 'component_id': 'src_11764', 'generator_key': 'src_11764', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_point_vectors_linear_combination', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_point_vectors_linear_combination', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11764, 'source_order': 11764, 'sampling_weight': 10.0}, {'textbook_example_id': 11765, 'component_id': 'src_11765', 'generator_key': 'src_11765', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_point_vectors_linear_combination', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_point_vectors_linear_combination', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11765, 'source_order': 11765, 'sampling_weight': 10.0}, {'textbook_example_id': 11766, 'component_id': 'src_11766', 'generator_key': 'src_11766', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_triangle_chain_and_perimeter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_triangle_chain_and_perimeter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11766, 'source_order': 11766, 'sampling_weight': 10.0}, {'textbook_example_id': 11767, 'component_id': 'src_11767', 'generator_key': 'src_11767', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'compute_triangle_chain_and_perimeter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_triangle_chain_and_perimeter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11767, 'source_order': 11767, 'sampling_weight': 10.0}, {'textbook_example_id': 11776, 'component_id': 'src_11776', 'generator_key': 'src_11776', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_parallelogram_fourth_vertex', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_parallelogram_fourth_vertex', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11776, 'source_order': 11776, 'sampling_weight': 10.0}, {'textbook_example_id': 11777, 'component_id': 'src_11777', 'generator_key': 'src_11777', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_vector_sum_difference', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_sum_difference', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11777, 'source_order': 11777, 'sampling_weight': 10.0}, {'textbook_example_id': 11778, 'component_id': 'src_11778', 'generator_key': 'src_11778', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_point_vectors_linear_combination', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_point_vectors_linear_combination', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11778, 'source_order': 11778, 'sampling_weight': 10.0}, {'textbook_example_id': 11779, 'component_id': 'src_11779', 'generator_key': 'src_11779', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_triangle_chain_and_perimeter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_triangle_chain_and_perimeter', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11779, 'source_order': 11779, 'sampling_weight': 10.0}, {'textbook_example_id': 11780, 'component_id': 'src_11780', 'generator_key': 'src_11780', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_vector_linear_combination', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_linear_combination', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11780, 'source_order': 11780, 'sampling_weight': 10.0}, {'textbook_example_id': 11807, 'component_id': 'src_11807', 'generator_key': 'src_11807', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'compute_vector_sum_difference', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_sum_difference', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11807, 'source_order': 11807, 'sampling_weight': 10.0}, {'textbook_example_id': 11808, 'component_id': 'src_11808', 'generator_key': 'src_11808', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'compute_vector_linear_combination', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'compute_vector_linear_combination', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 11808, 'source_order': 11808, 'sampling_weight': 10.0}, {'textbook_example_id': 11819, 'component_id': 'src_11819', 'generator_key': 'src_11819', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_vector_sum_difference', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'compute_vector_sum_difference', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11819, 'source_order': 11819, 'sampling_weight': 10.0}, {'textbook_example_id': 11821, 'component_id': 'src_11821', 'generator_key': 'src_11821', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'test', 'line_type': 'compute_chain_closure_vector_mcq', 'answer_type': 'choice', 'answer_value_type': 'choice', 'problem_type_id': 'compute_chain_closure_vector_mcq', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 11821, 'source_order': 11821, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_11762': 'components/src_11762/generate.py', 'src_11763': 'components/src_11763/generate.py', 'src_11764': 'components/src_11764/generate.py', 'src_11765': 'components/src_11765/generate.py', 'src_11766': 'components/src_11766/generate.py', 'src_11767': 'components/src_11767/generate.py', 'src_11776': 'components/src_11776/generate.py', 'src_11777': 'components/src_11777/generate.py', 'src_11778': 'components/src_11778/generate.py', 'src_11779': 'components/src_11779/generate.py', 'src_11780': 'components/src_11780/generate.py', 'src_11807': 'components/src_11807/generate.py', 'src_11808': 'components/src_11808/generate.py', 'src_11819': 'components/src_11819/generate.py', 'src_11821': 'components/src_11821/generate.py'}
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
