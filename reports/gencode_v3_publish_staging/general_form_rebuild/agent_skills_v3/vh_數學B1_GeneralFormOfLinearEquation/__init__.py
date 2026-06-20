from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B1_GeneralFormOfLinearEquation'
GENERATOR_KEYS = ['src_4565', 'src_4566', 'src_4567', 'src_4572', 'src_4573', 'src_4574', 'src_4581', 'src_4582', 'src_4585', 'src_4592', 'src_4593', 'src_4594', 'src_4595', 'src_4596', 'src_4597', 'src_4598', 'src_4599']
GENERATOR_SPECS = [{'textbook_example_id': 4565, 'component_id': 'src_4565', 'generator_key': 'src_4565', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4565', 'line_type': 'slope_from_general_or_intercept_form', 'answer_type': 'numeric_or_undefined', 'problem_type_id': 'slope_from_general_or_intercept_form', 'display_order': 4565, 'source_order': 4565, 'sampling_weight': 10.0}, {'textbook_example_id': 4566, 'component_id': 'src_4566', 'generator_key': 'src_4566', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4566', 'line_type': 'line_through_point_parallel_to_line', 'answer_type': 'linear_equation', 'problem_type_id': 'line_through_point_parallel_to_line', 'display_order': 4566, 'source_order': 4566, 'sampling_weight': 10.0}, {'textbook_example_id': 4567, 'component_id': 'src_4567', 'generator_key': 'src_4567', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4567', 'line_type': 'line_through_point_perpendicular_to_line', 'answer_type': 'linear_equation', 'problem_type_id': 'line_through_point_perpendicular_to_line', 'display_order': 4567, 'source_order': 4567, 'sampling_weight': 10.0}, {'textbook_example_id': 4572, 'component_id': 'src_4572', 'generator_key': 'src_4572', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4572', 'line_type': 'slope_of_horizontal_or_vertical_line', 'answer_type': 'numeric_or_undefined', 'problem_type_id': 'slope_of_horizontal_or_vertical_line', 'display_order': 4572, 'source_order': 4572, 'sampling_weight': 10.0}, {'textbook_example_id': 4573, 'component_id': 'src_4573', 'generator_key': 'src_4573', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4573', 'line_type': 'line_through_point_parallel_to_line', 'answer_type': 'linear_equation', 'problem_type_id': 'line_through_point_parallel_to_line', 'display_order': 4573, 'source_order': 4573, 'sampling_weight': 10.0}, {'textbook_example_id': 4574, 'component_id': 'src_4574', 'generator_key': 'src_4574', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4574', 'line_type': 'line_through_point_perpendicular_to_line', 'answer_type': 'linear_equation', 'problem_type_id': 'line_through_point_perpendicular_to_line', 'display_order': 4574, 'source_order': 4574, 'sampling_weight': 10.0}, {'textbook_example_id': 4581, 'component_id': 'src_4581', 'generator_key': 'src_4581', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4581', 'line_type': 'slope_from_general_form', 'answer_type': 'numeric_or_undefined', 'problem_type_id': 'slope_from_general_form', 'display_order': 4581, 'source_order': 4581, 'sampling_weight': 10.0}, {'textbook_example_id': 4582, 'component_id': 'src_4582', 'generator_key': 'src_4582', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4582', 'line_type': 'line_through_point_parallel_to_line', 'answer_type': 'linear_equation', 'problem_type_id': 'line_through_point_parallel_to_line', 'display_order': 4582, 'source_order': 4582, 'sampling_weight': 10.0}, {'textbook_example_id': 4585, 'component_id': 'src_4585', 'generator_key': 'src_4585', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4585', 'line_type': 'line_through_point_perpendicular_to_line', 'answer_type': 'linear_equation', 'problem_type_id': 'line_through_point_perpendicular_to_line', 'display_order': 4585, 'source_order': 4585, 'sampling_weight': 10.0}, {'textbook_example_id': 4592, 'component_id': 'src_4592', 'generator_key': 'src_4592', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4592', 'line_type': 'parallel_line_slope', 'answer_type': 'numeric_or_undefined', 'problem_type_id': 'parallel_line_slope', 'display_order': 4592, 'source_order': 4592, 'sampling_weight': 10.0}, {'textbook_example_id': 4593, 'component_id': 'src_4593', 'generator_key': 'src_4593', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4593', 'line_type': 'perpendicular_condition_parameter', 'answer_type': 'rational', 'problem_type_id': 'perpendicular_condition_parameter', 'display_order': 4593, 'source_order': 4593, 'sampling_weight': 10.0}, {'textbook_example_id': 4594, 'component_id': 'src_4594', 'generator_key': 'src_4594', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4594', 'line_type': 'line_through_point_perpendicular_to_line', 'answer_type': 'linear_equation', 'problem_type_id': 'line_through_point_perpendicular_to_line', 'display_order': 4594, 'source_order': 4594, 'sampling_weight': 10.0}, {'textbook_example_id': 4595, 'component_id': 'src_4595', 'generator_key': 'src_4595', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4595', 'line_type': 'compare_line_slopes', 'answer_type': 'single_choice', 'problem_type_id': 'compare_line_slopes', 'display_order': 4595, 'source_order': 4595, 'sampling_weight': 10.0}, {'textbook_example_id': 4596, 'component_id': 'src_4596', 'generator_key': 'src_4596', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4596', 'line_type': 'perpendicular_line_slope', 'answer_type': 'numeric_or_undefined', 'problem_type_id': 'perpendicular_line_slope', 'display_order': 4596, 'source_order': 4596, 'sampling_weight': 10.0}, {'textbook_example_id': 4597, 'component_id': 'src_4597', 'generator_key': 'src_4597', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4597', 'line_type': 'line_through_intersection_parallel_to_line', 'answer_type': 'linear_equation', 'problem_type_id': 'line_through_intersection_parallel_to_line', 'display_order': 4597, 'source_order': 4597, 'sampling_weight': 10.0}, {'textbook_example_id': 4598, 'component_id': 'src_4598', 'generator_key': 'src_4598', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4598', 'line_type': 'line_through_point_perpendicular_to_line', 'answer_type': 'linear_equation', 'problem_type_id': 'line_through_point_perpendicular_to_line', 'display_order': 4598, 'source_order': 4598, 'sampling_weight': 10.0}, {'textbook_example_id': 4599, 'component_id': 'src_4599', 'generator_key': 'src_4599', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4599', 'line_type': 'perpendicular_bisector_application', 'answer_type': 'linear_equation', 'problem_type_id': 'perpendicular_bisector_application', 'display_order': 4599, 'source_order': 4599, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_4565': 'components/src_4565/generate.py', 'src_4566': 'components/src_4566/generate.py', 'src_4567': 'components/src_4567/generate.py', 'src_4572': 'components/src_4572/generate.py', 'src_4573': 'components/src_4573/generate.py', 'src_4574': 'components/src_4574/generate.py', 'src_4581': 'components/src_4581/generate.py', 'src_4582': 'components/src_4582/generate.py', 'src_4585': 'components/src_4585/generate.py', 'src_4592': 'components/src_4592/generate.py', 'src_4593': 'components/src_4593/generate.py', 'src_4594': 'components/src_4594/generate.py', 'src_4595': 'components/src_4595/generate.py', 'src_4596': 'components/src_4596/generate.py', 'src_4597': 'components/src_4597/generate.py', 'src_4598': 'components/src_4598/generate.py', 'src_4599': 'components/src_4599/generate.py'}
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
