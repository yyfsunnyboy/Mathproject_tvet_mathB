from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_CountingPrinciples'
GENERATOR_KEYS = ['src_12749', 'src_12750', 'src_12751', 'src_12752', 'src_12753', 'src_12754', 'src_12755', 'src_12756', 'src_12757', 'src_12758', 'src_12759', 'src_12760', 'src_12761', 'src_12762', 'src_12765', 'src_12768', 'src_12769', 'src_12770', 'src_12771', 'src_12772', 'src_12773']
GENERATOR_SPECS = [{'textbook_example_id': 12749, 'component_id': 'src_12749', 'generator_key': 'src_12749', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'race_outcomes', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'race_outcomes', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12749, 'source_order': 12749, 'sampling_weight': 10.0}, {'textbook_example_id': 12750, 'component_id': 'src_12750', 'generator_key': 'src_12750', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'choice_product', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'choice_product', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12750, 'source_order': 12750, 'sampling_weight': 10.0}, {'textbook_example_id': 12751, 'component_id': 'src_12751', 'generator_key': 'src_12751', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'divisor_counting', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'divisor_counting', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12751, 'source_order': 12751, 'sampling_weight': 10.0}, {'textbook_example_id': 12752, 'component_id': 'src_12752', 'generator_key': 'src_12752', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'at_least_one_pairing', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'at_least_one_pairing', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12752, 'source_order': 12752, 'sampling_weight': 10.0}, {'textbook_example_id': 12753, 'component_id': 'src_12753', 'generator_key': 'src_12753', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'two_set_counting', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'two_set_counting', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12753, 'source_order': 12753, 'sampling_weight': 10.0}, {'textbook_example_id': 12754, 'component_id': 'src_12754', 'generator_key': 'src_12754', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'three_set_counting', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'three_set_counting', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12754, 'source_order': 12754, 'sampling_weight': 10.0}, {'textbook_example_id': 12755, 'component_id': 'src_12755', 'generator_key': 'src_12755', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'coin_payment', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'coin_payment', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12755, 'source_order': 12755, 'sampling_weight': 10.0}, {'textbook_example_id': 12756, 'component_id': 'src_12756', 'generator_key': 'src_12756', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'graph_paths', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'graph_paths', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12756, 'source_order': 12756, 'sampling_weight': 10.0}, {'textbook_example_id': 12757, 'component_id': 'src_12757', 'generator_key': 'src_12757', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'dice_sum_multiples', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'dice_sum_multiples', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12757, 'source_order': 12757, 'sampling_weight': 10.0}, {'textbook_example_id': 12758, 'component_id': 'src_12758', 'generator_key': 'src_12758', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'choice_product', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'choice_product', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12758, 'source_order': 12758, 'sampling_weight': 10.0}, {'textbook_example_id': 12759, 'component_id': 'src_12759', 'generator_key': 'src_12759', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'divisor_counting', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'divisor_counting', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12759, 'source_order': 12759, 'sampling_weight': 10.0}, {'textbook_example_id': 12760, 'component_id': 'src_12760', 'generator_key': 'src_12760', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'ordered_at_least_one', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'ordered_at_least_one', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12760, 'source_order': 12760, 'sampling_weight': 10.0}, {'textbook_example_id': 12761, 'component_id': 'src_12761', 'generator_key': 'src_12761', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'two_set_counting', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'two_set_counting', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12761, 'source_order': 12761, 'sampling_weight': 10.0}, {'textbook_example_id': 12762, 'component_id': 'src_12762', 'generator_key': 'src_12762', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'multiples_counting', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'multiples_counting', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12762, 'source_order': 12762, 'sampling_weight': 10.0}, {'textbook_example_id': 12765, 'component_id': 'src_12765', 'generator_key': 'src_12765', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'region_pairs_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'region_pairs_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12765, 'source_order': 12765, 'sampling_weight': 10.0}, {'textbook_example_id': 12768, 'component_id': 'src_12768', 'generator_key': 'src_12768', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'coin_toss_sequences', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'coin_toss_sequences', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12768, 'source_order': 12768, 'sampling_weight': 10.0}, {'textbook_example_id': 12769, 'component_id': 'src_12769', 'generator_key': 'src_12769', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'grade_selection', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'grade_selection', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12769, 'source_order': 12769, 'sampling_weight': 10.0}, {'textbook_example_id': 12770, 'component_id': 'src_12770', 'generator_key': 'src_12770', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'two_set_counting', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'two_set_counting', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12770, 'source_order': 12770, 'sampling_weight': 10.0}, {'textbook_example_id': 12771, 'component_id': 'src_12771', 'generator_key': 'src_12771', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'three_set_counting', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'three_set_counting', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12771, 'source_order': 12771, 'sampling_weight': 10.0}, {'textbook_example_id': 12772, 'component_id': 'src_12772', 'generator_key': 'src_12772', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'two_set_counting', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'two_set_counting', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12772, 'source_order': 12772, 'sampling_weight': 10.0}, {'textbook_example_id': 12773, 'component_id': 'src_12773', 'generator_key': 'src_12773', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'tiling_count', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'tiling_count', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12773, 'source_order': 12773, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12749': 'components/src_12749/generate.py', 'src_12750': 'components/src_12750/generate.py', 'src_12751': 'components/src_12751/generate.py', 'src_12752': 'components/src_12752/generate.py', 'src_12753': 'components/src_12753/generate.py', 'src_12754': 'components/src_12754/generate.py', 'src_12755': 'components/src_12755/generate.py', 'src_12756': 'components/src_12756/generate.py', 'src_12757': 'components/src_12757/generate.py', 'src_12758': 'components/src_12758/generate.py', 'src_12759': 'components/src_12759/generate.py', 'src_12760': 'components/src_12760/generate.py', 'src_12761': 'components/src_12761/generate.py', 'src_12762': 'components/src_12762/generate.py', 'src_12765': 'components/src_12765/generate.py', 'src_12768': 'components/src_12768/generate.py', 'src_12769': 'components/src_12769/generate.py', 'src_12770': 'components/src_12770/generate.py', 'src_12771': 'components/src_12771/generate.py', 'src_12772': 'components/src_12772/generate.py', 'src_12773': 'components/src_12773/generate.py'}
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
