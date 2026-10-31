from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_DefinitionOfClassicalProbability'
GENERATOR_KEYS = ['src_12860', 'src_12861', 'src_12862', 'src_12863', 'src_12864', 'src_12865', 'src_12866', 'src_12867', 'src_12868', 'src_12869', 'src_12870', 'src_12871', 'src_12872', 'src_12873', 'src_12874', 'src_12875', 'src_12876', 'src_12877', 'src_12878', 'src_12879', 'src_12880', 'src_12881', 'src_12882', 'src_12883', 'src_12884']
GENERATOR_SPECS = [{'textbook_example_id': 12860, 'component_id': 'src_12860', 'generator_key': 'src_12860', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'uniform_draw_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'uniform_draw_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12860, 'source_order': 12860, 'sampling_weight': 10.0}, {'textbook_example_id': 12861, 'component_id': 'src_12861', 'generator_key': 'src_12861', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'coin_count_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coin_count_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12861, 'source_order': 12861, 'sampling_weight': 10.0}, {'textbook_example_id': 12862, 'component_id': 'src_12862', 'generator_key': 'src_12862', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'coin_count_probability', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'coin_count_probability', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12862, 'source_order': 12862, 'sampling_weight': 10.0}, {'textbook_example_id': 12863, 'component_id': 'src_12863', 'generator_key': 'src_12863', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'dice_count_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'dice_count_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12863, 'source_order': 12863, 'sampling_weight': 10.0}, {'textbook_example_id': 12864, 'component_id': 'src_12864', 'generator_key': 'src_12864', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'urn_draw_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'urn_draw_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12864, 'source_order': 12864, 'sampling_weight': 10.0}, {'textbook_example_id': 12865, 'component_id': 'src_12865', 'generator_key': 'src_12865', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'dice_count_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'dice_count_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12865, 'source_order': 12865, 'sampling_weight': 10.0}, {'textbook_example_id': 12866, 'component_id': 'src_12866', 'generator_key': 'src_12866', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'uniform_draw_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'uniform_draw_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12866, 'source_order': 12866, 'sampling_weight': 10.0}, {'textbook_example_id': 12867, 'component_id': 'src_12867', 'generator_key': 'src_12867', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'replacement_count_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'replacement_count_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12867, 'source_order': 12867, 'sampling_weight': 10.0}, {'textbook_example_id': 12868, 'component_id': 'src_12868', 'generator_key': 'src_12868', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'coin_count_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coin_count_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12868, 'source_order': 12868, 'sampling_weight': 10.0}, {'textbook_example_id': 12869, 'component_id': 'src_12869', 'generator_key': 'src_12869', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'dice_count_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'dice_count_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12869, 'source_order': 12869, 'sampling_weight': 10.0}, {'textbook_example_id': 12870, 'component_id': 'src_12870', 'generator_key': 'src_12870', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'urn_draw_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'urn_draw_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12870, 'source_order': 12870, 'sampling_weight': 10.0}, {'textbook_example_id': 12871, 'component_id': 'src_12871', 'generator_key': 'src_12871', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'dice_count_probability', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'dice_count_probability', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12871, 'source_order': 12871, 'sampling_weight': 10.0}, {'textbook_example_id': 12872, 'component_id': 'src_12872', 'generator_key': 'src_12872', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'classical_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'classical_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12872, 'source_order': 12872, 'sampling_weight': 10.0}, {'textbook_example_id': 12873, 'component_id': 'src_12873', 'generator_key': 'src_12873', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'classical_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'classical_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12873, 'source_order': 12873, 'sampling_weight': 10.0}, {'textbook_example_id': 12874, 'component_id': 'src_12874', 'generator_key': 'src_12874', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'classical_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'classical_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12874, 'source_order': 12874, 'sampling_weight': 10.0}, {'textbook_example_id': 12875, 'component_id': 'src_12875', 'generator_key': 'src_12875', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'dice_count_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'dice_count_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12875, 'source_order': 12875, 'sampling_weight': 10.0}, {'textbook_example_id': 12876, 'component_id': 'src_12876', 'generator_key': 'src_12876', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'dice_count_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'dice_count_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12876, 'source_order': 12876, 'sampling_weight': 10.0}, {'textbook_example_id': 12877, 'component_id': 'src_12877', 'generator_key': 'src_12877', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'urn_draw_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'urn_draw_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12877, 'source_order': 12877, 'sampling_weight': 10.0}, {'textbook_example_id': 12878, 'component_id': 'src_12878', 'generator_key': 'src_12878', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'urn_draw_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'urn_draw_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12878, 'source_order': 12878, 'sampling_weight': 10.0}, {'textbook_example_id': 12879, 'component_id': 'src_12879', 'generator_key': 'src_12879', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'uniform_draw_probability', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'uniform_draw_probability', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12879, 'source_order': 12879, 'sampling_weight': 10.0}, {'textbook_example_id': 12880, 'component_id': 'src_12880', 'generator_key': 'src_12880', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'urn_draw_probability', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'urn_draw_probability', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12880, 'source_order': 12880, 'sampling_weight': 10.0}, {'textbook_example_id': 12881, 'component_id': 'src_12881', 'generator_key': 'src_12881', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'dice_count_probability', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'dice_count_probability', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12881, 'source_order': 12881, 'sampling_weight': 10.0}, {'textbook_example_id': 12882, 'component_id': 'src_12882', 'generator_key': 'src_12882', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'urn_draw_probability', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'urn_draw_probability', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12882, 'source_order': 12882, 'sampling_weight': 10.0}, {'textbook_example_id': 12883, 'component_id': 'src_12883', 'generator_key': 'src_12883', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'password_guess', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'password_guess', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12883, 'source_order': 12883, 'sampling_weight': 10.0}, {'textbook_example_id': 12884, 'component_id': 'src_12884', 'generator_key': 'src_12884', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_urn_count', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_urn_count', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12884, 'source_order': 12884, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12860': 'components/src_12860/generate.py', 'src_12861': 'components/src_12861/generate.py', 'src_12862': 'components/src_12862/generate.py', 'src_12863': 'components/src_12863/generate.py', 'src_12864': 'components/src_12864/generate.py', 'src_12865': 'components/src_12865/generate.py', 'src_12866': 'components/src_12866/generate.py', 'src_12867': 'components/src_12867/generate.py', 'src_12868': 'components/src_12868/generate.py', 'src_12869': 'components/src_12869/generate.py', 'src_12870': 'components/src_12870/generate.py', 'src_12871': 'components/src_12871/generate.py', 'src_12872': 'components/src_12872/generate.py', 'src_12873': 'components/src_12873/generate.py', 'src_12874': 'components/src_12874/generate.py', 'src_12875': 'components/src_12875/generate.py', 'src_12876': 'components/src_12876/generate.py', 'src_12877': 'components/src_12877/generate.py', 'src_12878': 'components/src_12878/generate.py', 'src_12879': 'components/src_12879/generate.py', 'src_12880': 'components/src_12880/generate.py', 'src_12881': 'components/src_12881/generate.py', 'src_12882': 'components/src_12882/generate.py', 'src_12883': 'components/src_12883/generate.py', 'src_12884': 'components/src_12884/generate.py'}
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
