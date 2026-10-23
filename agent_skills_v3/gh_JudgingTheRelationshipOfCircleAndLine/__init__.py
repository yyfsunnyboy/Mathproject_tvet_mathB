from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_JudgingTheRelationshipOfCircleAndLine'
GENERATOR_KEYS = ['src_12481', 'src_12482', 'src_12483', 'src_12484', 'src_12485', 'src_12486', 'src_12487', 'src_12488', 'src_12489', 'src_12490', 'src_12491', 'src_12492', 'src_12493', 'src_12494', 'src_12495', 'src_12496', 'src_12497', 'src_12498', 'src_12499', 'src_12513', 'src_12515']
GENERATOR_SPECS = [{'textbook_example_id': 12481, 'component_id': 'src_12481', 'generator_key': 'src_12481', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'classify_circle_line_relations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_circle_line_relations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12481, 'source_order': 12481, 'sampling_weight': 10.0}, {'textbook_example_id': 12482, 'component_id': 'src_12482', 'generator_key': 'src_12482', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_circle_line_parameter', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'solve_circle_line_parameter', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12482, 'source_order': 12482, 'sampling_weight': 10.0}, {'textbook_example_id': 12483, 'component_id': 'src_12483', 'generator_key': 'src_12483', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'classify_circle_line_relations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_circle_line_relations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12483, 'source_order': 12483, 'sampling_weight': 10.0}, {'textbook_example_id': 12484, 'component_id': 'src_12484', 'generator_key': 'src_12484', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_chord_and_distance', 'answer_type': 'numeric_or_radical', 'answer_value_type': 'numeric_or_radical', 'problem_type_id': 'solve_chord_and_distance', 'checker_key': 'expression_equivalence_checker', 'equivalence_type': None, 'display_order': 12484, 'source_order': 12484, 'sampling_weight': 10.0}, {'textbook_example_id': 12485, 'component_id': 'src_12485', 'generator_key': 'src_12485', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_circle_line_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_line_parameter', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12485, 'source_order': 12485, 'sampling_weight': 10.0}, {'textbook_example_id': 12486, 'component_id': 'src_12486', 'generator_key': 'src_12486', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'classify_circle_line_relations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_circle_line_relations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12486, 'source_order': 12486, 'sampling_weight': 10.0}, {'textbook_example_id': 12487, 'component_id': 'src_12487', 'generator_key': 'src_12487', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_circle_line_parameter', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'solve_circle_line_parameter', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12487, 'source_order': 12487, 'sampling_weight': 10.0}, {'textbook_example_id': 12488, 'component_id': 'src_12488', 'generator_key': 'src_12488', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'quiz', 'line_type': 'classify_circle_line_relations', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'classify_circle_line_relations', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12488, 'source_order': 12488, 'sampling_weight': 10.0}, {'textbook_example_id': 12489, 'component_id': 'src_12489', 'generator_key': 'src_12489', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_circle_line_parameter', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'solve_circle_line_parameter', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12489, 'source_order': 12489, 'sampling_weight': 10.0}, {'textbook_example_id': 12490, 'component_id': 'src_12490', 'generator_key': 'src_12490', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12490, 'source_order': 12490, 'sampling_weight': 10.0}, {'textbook_example_id': 12491, 'component_id': 'src_12491', 'generator_key': 'src_12491', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_circle_line_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_circle_line_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12491, 'source_order': 12491, 'sampling_weight': 10.0}, {'textbook_example_id': 12492, 'component_id': 'src_12492', 'generator_key': 'src_12492', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_circle_line_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_circle_line_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12492, 'source_order': 12492, 'sampling_weight': 10.0}, {'textbook_example_id': 12493, 'component_id': 'src_12493', 'generator_key': 'src_12493', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_circle_line_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_circle_line_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12493, 'source_order': 12493, 'sampling_weight': 10.0}, {'textbook_example_id': 12494, 'component_id': 'src_12494', 'generator_key': 'src_12494', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_circle_line_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_circle_line_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12494, 'source_order': 12494, 'sampling_weight': 10.0}, {'textbook_example_id': 12495, 'component_id': 'src_12495', 'generator_key': 'src_12495', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'classify_circle_line_relations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'classify_circle_line_relations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12495, 'source_order': 12495, 'sampling_weight': 10.0}, {'textbook_example_id': 12496, 'component_id': 'src_12496', 'generator_key': 'src_12496', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_circle_line_parameter', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'solve_circle_line_parameter', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12496, 'source_order': 12496, 'sampling_weight': 10.0}, {'textbook_example_id': 12497, 'component_id': 'src_12497', 'generator_key': 'src_12497', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'classify_circle_line_relations', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'classify_circle_line_relations', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12497, 'source_order': 12497, 'sampling_weight': 10.0}, {'textbook_example_id': 12498, 'component_id': 'src_12498', 'generator_key': 'src_12498', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_circle_line_parameter', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'solve_circle_line_parameter', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12498, 'source_order': 12498, 'sampling_weight': 10.0}, {'textbook_example_id': 12499, 'component_id': 'src_12499', 'generator_key': 'src_12499', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_chord_and_distance', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_chord_and_distance', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12499, 'source_order': 12499, 'sampling_weight': 10.0}, {'textbook_example_id': 12513, 'component_id': 'src_12513', 'generator_key': 'src_12513', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_circle_line_parameter', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_line_parameter', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12513, 'source_order': 12513, 'sampling_weight': 10.0}, {'textbook_example_id': 12515, 'component_id': 'src_12515', 'generator_key': 'src_12515', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_chord_and_distance', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_chord_and_distance', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12515, 'source_order': 12515, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12481': 'components/src_12481/generate.py', 'src_12482': 'components/src_12482/generate.py', 'src_12483': 'components/src_12483/generate.py', 'src_12484': 'components/src_12484/generate.py', 'src_12485': 'components/src_12485/generate.py', 'src_12486': 'components/src_12486/generate.py', 'src_12487': 'components/src_12487/generate.py', 'src_12488': 'components/src_12488/generate.py', 'src_12489': 'components/src_12489/generate.py', 'src_12490': 'components/src_12490/generate.py', 'src_12491': 'components/src_12491/generate.py', 'src_12492': 'components/src_12492/generate.py', 'src_12493': 'components/src_12493/generate.py', 'src_12494': 'components/src_12494/generate.py', 'src_12495': 'components/src_12495/generate.py', 'src_12496': 'components/src_12496/generate.py', 'src_12497': 'components/src_12497/generate.py', 'src_12498': 'components/src_12498/generate.py', 'src_12499': 'components/src_12499/generate.py', 'src_12513': 'components/src_12513/generate.py', 'src_12515': 'components/src_12515/generate.py'}
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
