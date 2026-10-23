from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_TangentLinesOfACircle'
GENERATOR_KEYS = ['src_12500', 'src_12501', 'src_12502', 'src_12503', 'src_12504', 'src_12505', 'src_12506', 'src_12507', 'src_12508', 'src_12509', 'src_12510', 'src_12511', 'src_12512', 'src_12514', 'src_12516']
GENERATOR_SPECS = [{'textbook_example_id': 12500, 'component_id': 'src_12500', 'generator_key': 'src_12500', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'equation', 'answer_value_type': 'equation', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_equation_equivalent_checker', 'equivalence_type': None, 'display_order': 12500, 'source_order': 12500, 'sampling_weight': 10.0}, {'textbook_example_id': 12501, 'component_id': 'src_12501', 'generator_key': 'src_12501', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12501, 'source_order': 12501, 'sampling_weight': 10.0}, {'textbook_example_id': 12502, 'component_id': 'src_12502', 'generator_key': 'src_12502', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12502, 'source_order': 12502, 'sampling_weight': 10.0}, {'textbook_example_id': 12503, 'component_id': 'src_12503', 'generator_key': 'src_12503', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_circle_tangent_scenarios', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_tangent_scenarios', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12503, 'source_order': 12503, 'sampling_weight': 10.0}, {'textbook_example_id': 12504, 'component_id': 'src_12504', 'generator_key': 'src_12504', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_circle_from_tangent_point', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_from_tangent_point', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12504, 'source_order': 12504, 'sampling_weight': 10.0}, {'textbook_example_id': 12505, 'component_id': 'src_12505', 'generator_key': 'src_12505', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12505, 'source_order': 12505, 'sampling_weight': 10.0}, {'textbook_example_id': 12506, 'component_id': 'src_12506', 'generator_key': 'src_12506', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12506, 'source_order': 12506, 'sampling_weight': 10.0}, {'textbook_example_id': 12507, 'component_id': 'src_12507', 'generator_key': 'src_12507', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_circle_tangent_scenarios', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_tangent_scenarios', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12507, 'source_order': 12507, 'sampling_weight': 10.0}, {'textbook_example_id': 12508, 'component_id': 'src_12508', 'generator_key': 'src_12508', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_circle_line_statement_truth', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_circle_line_statement_truth', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12508, 'source_order': 12508, 'sampling_weight': 10.0}, {'textbook_example_id': 12509, 'component_id': 'src_12509', 'generator_key': 'src_12509', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12509, 'source_order': 12509, 'sampling_weight': 10.0}, {'textbook_example_id': 12510, 'component_id': 'src_12510', 'generator_key': 'src_12510', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'equation', 'answer_value_type': 'equation', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_equation_equivalent_checker', 'equivalence_type': None, 'display_order': 12510, 'source_order': 12510, 'sampling_weight': 10.0}, {'textbook_example_id': 12511, 'component_id': 'src_12511', 'generator_key': 'src_12511', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'write_circle_tangent_lines', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'write_circle_tangent_lines', 'checker_key': 'linear_relation_set_checker', 'equivalence_type': None, 'display_order': 12511, 'source_order': 12511, 'sampling_weight': 10.0}, {'textbook_example_id': 12512, 'component_id': 'src_12512', 'generator_key': 'src_12512', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_circle_line_parameter', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'solve_circle_line_parameter', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12512, 'source_order': 12512, 'sampling_weight': 10.0}, {'textbook_example_id': 12514, 'component_id': 'src_12514', 'generator_key': 'src_12514', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_circle_tangent_scenarios', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_circle_tangent_scenarios', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12514, 'source_order': 12514, 'sampling_weight': 10.0}, {'textbook_example_id': 12516, 'component_id': 'src_12516', 'generator_key': 'src_12516', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_circle_tangent_scenarios', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_circle_tangent_scenarios', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12516, 'source_order': 12516, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12500': 'components/src_12500/generate.py', 'src_12501': 'components/src_12501/generate.py', 'src_12502': 'components/src_12502/generate.py', 'src_12503': 'components/src_12503/generate.py', 'src_12504': 'components/src_12504/generate.py', 'src_12505': 'components/src_12505/generate.py', 'src_12506': 'components/src_12506/generate.py', 'src_12507': 'components/src_12507/generate.py', 'src_12508': 'components/src_12508/generate.py', 'src_12509': 'components/src_12509/generate.py', 'src_12510': 'components/src_12510/generate.py', 'src_12511': 'components/src_12511/generate.py', 'src_12512': 'components/src_12512/generate.py', 'src_12514': 'components/src_12514/generate.py', 'src_12516': 'components/src_12516/generate.py'}
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
