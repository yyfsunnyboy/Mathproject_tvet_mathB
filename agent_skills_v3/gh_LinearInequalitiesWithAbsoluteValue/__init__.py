from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_LinearInequalitiesWithAbsoluteValue'
GENERATOR_KEYS = ['src_1033', 'src_1034', 'src_1035', 'src_1036', 'src_1037', 'src_1040', 'src_1044', 'src_1045', 'src_1046', 'src_1048', 'src_1049', 'src_12331', 'src_12332', 'src_12333']
GENERATOR_SPECS = [{'textbook_example_id': 1033, 'component_id': 'src_1033', 'generator_key': 'src_1033', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1033, 'source_order': 1033, 'sampling_weight': 10.0}, {'textbook_example_id': 1034, 'component_id': 'src_1034', 'generator_key': 'src_1034', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1034, 'source_order': 1034, 'sampling_weight': 10.0}, {'textbook_example_id': 1035, 'component_id': 'src_1035', 'generator_key': 'src_1035', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1035, 'source_order': 1035, 'sampling_weight': 10.0}, {'textbook_example_id': 1036, 'component_id': 'src_1036', 'generator_key': 'src_1036', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'inequality_solution', 'answer_value_type': 'inequality_solution', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 1036, 'source_order': 1036, 'sampling_weight': 10.0}, {'textbook_example_id': 1037, 'component_id': 'src_1037', 'generator_key': 'src_1037', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'recover_absolute_value_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recover_absolute_value_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1037, 'source_order': 1037, 'sampling_weight': 10.0}, {'textbook_example_id': 1040, 'component_id': 'src_1040', 'generator_key': 'src_1040', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_absolute_value_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_absolute_value_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 1040, 'source_order': 1040, 'sampling_weight': 10.0}, {'textbook_example_id': 1044, 'component_id': 'src_1044', 'generator_key': 'src_1044', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1044, 'source_order': 1044, 'sampling_weight': 10.0}, {'textbook_example_id': 1045, 'component_id': 'src_1045', 'generator_key': 'src_1045', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1045, 'source_order': 1045, 'sampling_weight': 10.0}, {'textbook_example_id': 1046, 'component_id': 'src_1046', 'generator_key': 'src_1046', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'recover_absolute_value_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recover_absolute_value_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1046, 'source_order': 1046, 'sampling_weight': 10.0}, {'textbook_example_id': 1048, 'component_id': 'src_1048', 'generator_key': 'src_1048', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'recover_absolute_value_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recover_absolute_value_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1048, 'source_order': 1048, 'sampling_weight': 10.0}, {'textbook_example_id': 1049, 'component_id': 'src_1049', 'generator_key': 'src_1049', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'recover_absolute_value_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'recover_absolute_value_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 1049, 'source_order': 1049, 'sampling_weight': 10.0}, {'textbook_example_id': 12331, 'component_id': 'src_12331', 'generator_key': 'src_12331', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12331, 'source_order': 12331, 'sampling_weight': 10.0}, {'textbook_example_id': 12332, 'component_id': 'src_12332', 'generator_key': 'src_12332', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_absolute_value_inequalities', 'answer_type': 'inequality_solution', 'answer_value_type': 'inequality_solution', 'problem_type_id': 'solve_absolute_value_inequalities', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12332, 'source_order': 12332, 'sampling_weight': 10.0}, {'textbook_example_id': 12333, 'component_id': 'src_12333', 'generator_key': 'src_12333', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_tolerance_range_application', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_tolerance_range_application', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12333, 'source_order': 12333, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_1033': 'components/src_1033/generate.py', 'src_1034': 'components/src_1034/generate.py', 'src_1035': 'components/src_1035/generate.py', 'src_1036': 'components/src_1036/generate.py', 'src_1037': 'components/src_1037/generate.py', 'src_1040': 'components/src_1040/generate.py', 'src_1044': 'components/src_1044/generate.py', 'src_1045': 'components/src_1045/generate.py', 'src_1046': 'components/src_1046/generate.py', 'src_1048': 'components/src_1048/generate.py', 'src_1049': 'components/src_1049/generate.py', 'src_12331': 'components/src_12331/generate.py', 'src_12332': 'components/src_12332/generate.py', 'src_12333': 'components/src_12333/generate.py'}
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
