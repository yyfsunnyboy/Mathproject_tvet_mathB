from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_OperationsOfRadicalsAndFractions'
GENERATOR_KEYS = ['src_12302', 'src_12303', 'src_12304', 'src_12305', 'src_12306', 'src_12307', 'src_12308', 'src_12309', 'src_12310', 'src_12311', 'src_12312', 'src_12313', 'src_12314', 'src_12315', 'src_12316', 'src_12317', 'src_12318', 'src_12319', 'src_12320', 'src_12321']
GENERATOR_SPECS = [{'textbook_example_id': 12302, 'component_id': 'src_12302', 'generator_key': 'src_12302', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'simplify_radical_fraction_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_radical_fraction_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12302, 'source_order': 12302, 'sampling_weight': 10.0}, {'textbook_example_id': 12303, 'component_id': 'src_12303', 'generator_key': 'src_12303', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'order_radical_numbers', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'order_radical_numbers', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12303, 'source_order': 12303, 'sampling_weight': 10.0}, {'textbook_example_id': 12304, 'component_id': 'src_12304', 'generator_key': 'src_12304', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'evaluate_time_dilation_relations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_time_dilation_relations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12304, 'source_order': 12304, 'sampling_weight': 10.0}, {'textbook_example_id': 12305, 'component_id': 'src_12305', 'generator_key': 'src_12305', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'denest_square_roots', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'denest_square_roots', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12305, 'source_order': 12305, 'sampling_weight': 10.0}, {'textbook_example_id': 12306, 'component_id': 'src_12306', 'generator_key': 'src_12306', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_integer_fraction_part_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_integer_fraction_part_expression', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12306, 'source_order': 12306, 'sampling_weight': 10.0}, {'textbook_example_id': 12307, 'component_id': 'src_12307', 'generator_key': 'src_12307', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'optimize_by_am_gm', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'optimize_by_am_gm', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12307, 'source_order': 12307, 'sampling_weight': 10.0}, {'textbook_example_id': 12308, 'component_id': 'src_12308', 'generator_key': 'src_12308', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'simplify_radical_fraction_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_radical_fraction_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12308, 'source_order': 12308, 'sampling_weight': 10.0}, {'textbook_example_id': 12309, 'component_id': 'src_12309', 'generator_key': 'src_12309', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'simplify_radical_fraction_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_radical_fraction_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12309, 'source_order': 12309, 'sampling_weight': 10.0}, {'textbook_example_id': 12310, 'component_id': 'src_12310', 'generator_key': 'src_12310', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'order_radical_numbers', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'order_radical_numbers', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12310, 'source_order': 12310, 'sampling_weight': 10.0}, {'textbook_example_id': 12311, 'component_id': 'src_12311', 'generator_key': 'src_12311', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_time_dilation_relations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_time_dilation_relations', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12311, 'source_order': 12311, 'sampling_weight': 10.0}, {'textbook_example_id': 12312, 'component_id': 'src_12312', 'generator_key': 'src_12312', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'denest_square_roots', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'denest_square_roots', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12312, 'source_order': 12312, 'sampling_weight': 10.0}, {'textbook_example_id': 12313, 'component_id': 'src_12313', 'generator_key': 'src_12313', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'evaluate_integer_fraction_part_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_integer_fraction_part_expression', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12313, 'source_order': 12313, 'sampling_weight': 10.0}, {'textbook_example_id': 12314, 'component_id': 'src_12314', 'generator_key': 'src_12314', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'optimize_by_am_gm', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'optimize_by_am_gm', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12314, 'source_order': 12314, 'sampling_weight': 10.0}, {'textbook_example_id': 12315, 'component_id': 'src_12315', 'generator_key': 'src_12315', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'simplify_radical_fraction_expressions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'simplify_radical_fraction_expressions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12315, 'source_order': 12315, 'sampling_weight': 10.0}, {'textbook_example_id': 12316, 'component_id': 'src_12316', 'generator_key': 'src_12316', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'nearest_integer_from_radical_relation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'nearest_integer_from_radical_relation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12316, 'source_order': 12316, 'sampling_weight': 10.0}, {'textbook_example_id': 12317, 'component_id': 'src_12317', 'generator_key': 'src_12317', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'denest_square_roots', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'denest_square_roots', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12317, 'source_order': 12317, 'sampling_weight': 10.0}, {'textbook_example_id': 12318, 'component_id': 'src_12318', 'generator_key': 'src_12318', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'denest_square_roots', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'denest_square_roots', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12318, 'source_order': 12318, 'sampling_weight': 10.0}, {'textbook_example_id': 12319, 'component_id': 'src_12319', 'generator_key': 'src_12319', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_integer_fraction_part_expression', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'evaluate_integer_fraction_part_expression', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12319, 'source_order': 12319, 'sampling_weight': 10.0}, {'textbook_example_id': 12320, 'component_id': 'src_12320', 'generator_key': 'src_12320', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'optimize_by_am_gm', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'optimize_by_am_gm', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12320, 'source_order': 12320, 'sampling_weight': 10.0}, {'textbook_example_id': 12321, 'component_id': 'src_12321', 'generator_key': 'src_12321', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'optimize_by_am_gm', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'optimize_by_am_gm', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12321, 'source_order': 12321, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12302': 'components/src_12302/generate.py', 'src_12303': 'components/src_12303/generate.py', 'src_12304': 'components/src_12304/generate.py', 'src_12305': 'components/src_12305/generate.py', 'src_12306': 'components/src_12306/generate.py', 'src_12307': 'components/src_12307/generate.py', 'src_12308': 'components/src_12308/generate.py', 'src_12309': 'components/src_12309/generate.py', 'src_12310': 'components/src_12310/generate.py', 'src_12311': 'components/src_12311/generate.py', 'src_12312': 'components/src_12312/generate.py', 'src_12313': 'components/src_12313/generate.py', 'src_12314': 'components/src_12314/generate.py', 'src_12315': 'components/src_12315/generate.py', 'src_12316': 'components/src_12316/generate.py', 'src_12317': 'components/src_12317/generate.py', 'src_12318': 'components/src_12318/generate.py', 'src_12319': 'components/src_12319/generate.py', 'src_12320': 'components/src_12320/generate.py', 'src_12321': 'components/src_12321/generate.py'}
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
