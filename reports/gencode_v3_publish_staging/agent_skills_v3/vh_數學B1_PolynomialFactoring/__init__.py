from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B1_PolynomialFactoring'
GENERATOR_KEYS = ['src_4671', 'src_4672', 'src_4673', 'src_4674', 'src_4675', 'src_4681', 'src_4682', 'src_4683', 'src_4684', 'src_4685', 'src_4694', 'src_4695', 'src_4696', 'src_4697', 'src_4701', 'src_4713', 'src_4714', 'src_4715']
GENERATOR_SPECS = [{'textbook_example_id': 4671, 'component_id': 'src_4671', 'generator_key': 'src_4671', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4671, 'source_order': 4671, 'sampling_weight': 10.0}, {'textbook_example_id': 4672, 'component_id': 'src_4672', 'generator_key': 'src_4672', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4672, 'source_order': 4672, 'sampling_weight': 10.0}, {'textbook_example_id': 4673, 'component_id': 'src_4673', 'generator_key': 'src_4673', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4673, 'source_order': 4673, 'sampling_weight': 10.0}, {'textbook_example_id': 4674, 'component_id': 'src_4674', 'generator_key': 'src_4674', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4674, 'source_order': 4674, 'sampling_weight': 10.0}, {'textbook_example_id': 4675, 'component_id': 'src_4675', 'generator_key': 'src_4675', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4675, 'source_order': 4675, 'sampling_weight': 10.0}, {'textbook_example_id': 4681, 'component_id': 'src_4681', 'generator_key': 'src_4681', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4681, 'source_order': 4681, 'sampling_weight': 10.0}, {'textbook_example_id': 4682, 'component_id': 'src_4682', 'generator_key': 'src_4682', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4682, 'source_order': 4682, 'sampling_weight': 10.0}, {'textbook_example_id': 4683, 'component_id': 'src_4683', 'generator_key': 'src_4683', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4683, 'source_order': 4683, 'sampling_weight': 10.0}, {'textbook_example_id': 4684, 'component_id': 'src_4684', 'generator_key': 'src_4684', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4684, 'source_order': 4684, 'sampling_weight': 10.0}, {'textbook_example_id': 4685, 'component_id': 'src_4685', 'generator_key': 'src_4685', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4685, 'source_order': 4685, 'sampling_weight': 10.0}, {'textbook_example_id': 4694, 'component_id': 'src_4694', 'generator_key': 'src_4694', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4694, 'source_order': 4694, 'sampling_weight': 10.0}, {'textbook_example_id': 4695, 'component_id': 'src_4695', 'generator_key': 'src_4695', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4695, 'source_order': 4695, 'sampling_weight': 10.0}, {'textbook_example_id': 4696, 'component_id': 'src_4696', 'generator_key': 'src_4696', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4696, 'source_order': 4696, 'sampling_weight': 10.0}, {'textbook_example_id': 4697, 'component_id': 'src_4697', 'generator_key': 'src_4697', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4697, 'source_order': 4697, 'sampling_weight': 10.0}, {'textbook_example_id': 4701, 'component_id': 'src_4701', 'generator_key': 'src_4701', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4701, 'source_order': 4701, 'sampling_weight': 10.0}, {'textbook_example_id': 4713, 'component_id': 'src_4713', 'generator_key': 'src_4713', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4713, 'source_order': 4713, 'sampling_weight': 10.0}, {'textbook_example_id': 4714, 'component_id': 'src_4714', 'generator_key': 'src_4714', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4714, 'source_order': 4714, 'sampling_weight': 10.0}, {'textbook_example_id': 4715, 'component_id': 'src_4715', 'generator_key': 'src_4715', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'test', 'line_type': 'polynomial_factoring', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_factoring', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 4715, 'source_order': 4715, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_4671': 'components/src_4671/generate.py', 'src_4672': 'components/src_4672/generate.py', 'src_4673': 'components/src_4673/generate.py', 'src_4674': 'components/src_4674/generate.py', 'src_4675': 'components/src_4675/generate.py', 'src_4681': 'components/src_4681/generate.py', 'src_4682': 'components/src_4682/generate.py', 'src_4683': 'components/src_4683/generate.py', 'src_4684': 'components/src_4684/generate.py', 'src_4685': 'components/src_4685/generate.py', 'src_4694': 'components/src_4694/generate.py', 'src_4695': 'components/src_4695/generate.py', 'src_4696': 'components/src_4696/generate.py', 'src_4697': 'components/src_4697/generate.py', 'src_4701': 'components/src_4701/generate.py', 'src_4713': 'components/src_4713/generate.py', 'src_4714': 'components/src_4714/generate.py', 'src_4715': 'components/src_4715/generate.py'}
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
