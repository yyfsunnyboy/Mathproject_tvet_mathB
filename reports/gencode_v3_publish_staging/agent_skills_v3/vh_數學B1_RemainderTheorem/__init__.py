from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B1_RemainderTheorem'
GENERATOR_KEYS = ['src_4638', 'src_4639', 'src_4640', 'src_4641', 'src_4642', 'src_4643', 'src_4644', 'src_4645', 'src_4656', 'src_4657', 'src_4658', 'src_4659', 'src_4664', 'src_4665', 'src_4666', 'src_4667', 'src_4668', 'src_4669', 'src_4670', 'src_4722']
GENERATOR_SPECS = [{'textbook_example_id': 4638, 'component_id': 'src_4638', 'generator_key': 'src_4638', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4638, 'source_order': 4638, 'sampling_weight': 10.0}, {'textbook_example_id': 4639, 'component_id': 'src_4639', 'generator_key': 'src_4639', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4639, 'source_order': 4639, 'sampling_weight': 10.0}, {'textbook_example_id': 4640, 'component_id': 'src_4640', 'generator_key': 'src_4640', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4640, 'source_order': 4640, 'sampling_weight': 10.0}, {'textbook_example_id': 4641, 'component_id': 'src_4641', 'generator_key': 'src_4641', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4641, 'source_order': 4641, 'sampling_weight': 10.0}, {'textbook_example_id': 4642, 'component_id': 'src_4642', 'generator_key': 'src_4642', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4642, 'source_order': 4642, 'sampling_weight': 10.0}, {'textbook_example_id': 4643, 'component_id': 'src_4643', 'generator_key': 'src_4643', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4643, 'source_order': 4643, 'sampling_weight': 10.0}, {'textbook_example_id': 4644, 'component_id': 'src_4644', 'generator_key': 'src_4644', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4644, 'source_order': 4644, 'sampling_weight': 10.0}, {'textbook_example_id': 4645, 'component_id': 'src_4645', 'generator_key': 'src_4645', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4645, 'source_order': 4645, 'sampling_weight': 10.0}, {'textbook_example_id': 4656, 'component_id': 'src_4656', 'generator_key': 'src_4656', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4656, 'source_order': 4656, 'sampling_weight': 10.0}, {'textbook_example_id': 4657, 'component_id': 'src_4657', 'generator_key': 'src_4657', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4657, 'source_order': 4657, 'sampling_weight': 10.0}, {'textbook_example_id': 4658, 'component_id': 'src_4658', 'generator_key': 'src_4658', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4658, 'source_order': 4658, 'sampling_weight': 10.0}, {'textbook_example_id': 4659, 'component_id': 'src_4659', 'generator_key': 'src_4659', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4659, 'source_order': 4659, 'sampling_weight': 10.0}, {'textbook_example_id': 4664, 'component_id': 'src_4664', 'generator_key': 'src_4664', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4664, 'source_order': 4664, 'sampling_weight': 10.0}, {'textbook_example_id': 4665, 'component_id': 'src_4665', 'generator_key': 'src_4665', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4665, 'source_order': 4665, 'sampling_weight': 10.0}, {'textbook_example_id': 4666, 'component_id': 'src_4666', 'generator_key': 'src_4666', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4666, 'source_order': 4666, 'sampling_weight': 10.0}, {'textbook_example_id': 4667, 'component_id': 'src_4667', 'generator_key': 'src_4667', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4667, 'source_order': 4667, 'sampling_weight': 10.0}, {'textbook_example_id': 4668, 'component_id': 'src_4668', 'generator_key': 'src_4668', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4668, 'source_order': 4668, 'sampling_weight': 10.0}, {'textbook_example_id': 4669, 'component_id': 'src_4669', 'generator_key': 'src_4669', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4669, 'source_order': 4669, 'sampling_weight': 10.0}, {'textbook_example_id': 4670, 'component_id': 'src_4670', 'generator_key': 'src_4670', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4670, 'source_order': 4670, 'sampling_weight': 10.0}, {'textbook_example_id': 4722, 'component_id': 'src_4722', 'generator_key': 'src_4722', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'remainder_theorem_evaluate', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'remainder_theorem_evaluate', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4722, 'source_order': 4722, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_4638': 'components/src_4638/generate.py', 'src_4639': 'components/src_4639/generate.py', 'src_4640': 'components/src_4640/generate.py', 'src_4641': 'components/src_4641/generate.py', 'src_4642': 'components/src_4642/generate.py', 'src_4643': 'components/src_4643/generate.py', 'src_4644': 'components/src_4644/generate.py', 'src_4645': 'components/src_4645/generate.py', 'src_4656': 'components/src_4656/generate.py', 'src_4657': 'components/src_4657/generate.py', 'src_4658': 'components/src_4658/generate.py', 'src_4659': 'components/src_4659/generate.py', 'src_4664': 'components/src_4664/generate.py', 'src_4665': 'components/src_4665/generate.py', 'src_4666': 'components/src_4666/generate.py', 'src_4667': 'components/src_4667/generate.py', 'src_4668': 'components/src_4668/generate.py', 'src_4669': 'components/src_4669/generate.py', 'src_4670': 'components/src_4670/generate.py', 'src_4722': 'components/src_4722/generate.py'}
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
