from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_Combination'
GENERATOR_KEYS = ['src_12812', 'src_12813', 'src_12814', 'src_12815', 'src_12816', 'src_12817', 'src_12818', 'src_12819', 'src_12820', 'src_12821', 'src_12822', 'src_12823', 'src_12824', 'src_12825', 'src_12826', 'src_12827', 'src_12828', 'src_12829', 'src_12830', 'src_12831', 'src_12832', 'src_12833']
GENERATOR_SPECS = [{'textbook_example_id': 12812, 'component_id': 'src_12812', 'generator_key': 'src_12812', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'combination_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'combination_evaluate', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12812, 'source_order': 12812, 'sampling_weight': 10.0}, {'textbook_example_id': 12813, 'component_id': 'src_12813', 'generator_key': 'src_12813', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'select_with_members', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'select_with_members', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12813, 'source_order': 12813, 'sampling_weight': 10.0}, {'textbook_example_id': 12814, 'component_id': 'src_12814', 'generator_key': 'src_12814', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'mixed_group_ordered', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'mixed_group_ordered', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12814, 'source_order': 12814, 'sampling_weight': 10.0}, {'textbook_example_id': 12815, 'component_id': 'src_12815', 'generator_key': 'src_12815', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'group_partition', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'group_partition', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12815, 'source_order': 12815, 'sampling_weight': 10.0}, {'textbook_example_id': 12816, 'component_id': 'src_12816', 'generator_key': 'src_12816', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'group_partition', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'group_partition', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12816, 'source_order': 12816, 'sampling_weight': 10.0}, {'textbook_example_id': 12817, 'component_id': 'src_12817', 'generator_key': 'src_12817', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'combination_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'combination_evaluate', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12817, 'source_order': 12817, 'sampling_weight': 10.0}, {'textbook_example_id': 12818, 'component_id': 'src_12818', 'generator_key': 'src_12818', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'select_with_members', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'select_with_members', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12818, 'source_order': 12818, 'sampling_weight': 10.0}, {'textbook_example_id': 12819, 'component_id': 'src_12819', 'generator_key': 'src_12819', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'mixed_group_ordered', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'mixed_group_ordered', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12819, 'source_order': 12819, 'sampling_weight': 10.0}, {'textbook_example_id': 12820, 'component_id': 'src_12820', 'generator_key': 'src_12820', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'group_partition', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'group_partition', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12820, 'source_order': 12820, 'sampling_weight': 10.0}, {'textbook_example_id': 12821, 'component_id': 'src_12821', 'generator_key': 'src_12821', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'group_partition', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'group_partition', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12821, 'source_order': 12821, 'sampling_weight': 10.0}, {'textbook_example_id': 12822, 'component_id': 'src_12822', 'generator_key': 'src_12822', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'combination_identity_select', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'combination_identity_select', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12822, 'source_order': 12822, 'sampling_weight': 10.0}, {'textbook_example_id': 12823, 'component_id': 'src_12823', 'generator_key': 'src_12823', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'combination_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'combination_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12823, 'source_order': 12823, 'sampling_weight': 10.0}, {'textbook_example_id': 12824, 'component_id': 'src_12824', 'generator_key': 'src_12824', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'combination_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'combination_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12824, 'source_order': 12824, 'sampling_weight': 10.0}, {'textbook_example_id': 12825, 'component_id': 'src_12825', 'generator_key': 'src_12825', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'combination_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'combination_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12825, 'source_order': 12825, 'sampling_weight': 10.0}, {'textbook_example_id': 12826, 'component_id': 'src_12826', 'generator_key': 'src_12826', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'pair_count', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'pair_count', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12826, 'source_order': 12826, 'sampling_weight': 10.0}, {'textbook_example_id': 12827, 'component_id': 'src_12827', 'generator_key': 'src_12827', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'sequential_selection', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'sequential_selection', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12827, 'source_order': 12827, 'sampling_weight': 10.0}, {'textbook_example_id': 12828, 'component_id': 'src_12828', 'generator_key': 'src_12828', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'gender_committee', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'gender_committee', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12828, 'source_order': 12828, 'sampling_weight': 10.0}, {'textbook_example_id': 12829, 'component_id': 'src_12829', 'generator_key': 'src_12829', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'paired_group_assignment', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'paired_group_assignment', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12829, 'source_order': 12829, 'sampling_weight': 10.0}, {'textbook_example_id': 12830, 'component_id': 'src_12830', 'generator_key': 'src_12830', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'surjective_distribution', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'surjective_distribution', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12830, 'source_order': 12830, 'sampling_weight': 10.0}, {'textbook_example_id': 12831, 'component_id': 'src_12831', 'generator_key': 'src_12831', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'pair_count', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'pair_count', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12831, 'source_order': 12831, 'sampling_weight': 10.0}, {'textbook_example_id': 12832, 'component_id': 'src_12832', 'generator_key': 'src_12832', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'parity_sum_selection', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'parity_sum_selection', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12832, 'source_order': 12832, 'sampling_weight': 10.0}, {'textbook_example_id': 12833, 'component_id': 'src_12833', 'generator_key': 'src_12833', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'multiset_select_arrange', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'multiset_select_arrange', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12833, 'source_order': 12833, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12812': 'components/src_12812/generate.py', 'src_12813': 'components/src_12813/generate.py', 'src_12814': 'components/src_12814/generate.py', 'src_12815': 'components/src_12815/generate.py', 'src_12816': 'components/src_12816/generate.py', 'src_12817': 'components/src_12817/generate.py', 'src_12818': 'components/src_12818/generate.py', 'src_12819': 'components/src_12819/generate.py', 'src_12820': 'components/src_12820/generate.py', 'src_12821': 'components/src_12821/generate.py', 'src_12822': 'components/src_12822/generate.py', 'src_12823': 'components/src_12823/generate.py', 'src_12824': 'components/src_12824/generate.py', 'src_12825': 'components/src_12825/generate.py', 'src_12826': 'components/src_12826/generate.py', 'src_12827': 'components/src_12827/generate.py', 'src_12828': 'components/src_12828/generate.py', 'src_12829': 'components/src_12829/generate.py', 'src_12830': 'components/src_12830/generate.py', 'src_12831': 'components/src_12831/generate.py', 'src_12832': 'components/src_12832/generate.py', 'src_12833': 'components/src_12833/generate.py'}
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
