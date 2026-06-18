from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B1_InterceptForm'
GENERATOR_KEYS = ['src_4547', 'src_4548', 'src_4555', 'src_4558', 'src_4559', 'src_4564', 'src_4604']
GENERATOR_SPECS = [{'textbook_example_id': 4547, 'component_id': 'src_4547', 'generator_key': 'src_4547', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4547', 'line_type': 'intercept_form_equation_and_triangle_area', 'answer_type': 'multi_part', 'problem_type_id': 'intercept_form_equation_and_triangle_area', 'display_order': 4547, 'source_order': 4547, 'sampling_weight': 10.0}, {'textbook_example_id': 4548, 'component_id': 'src_4548', 'generator_key': 'src_4548', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4548', 'line_type': 'intercept_form_from_intercept_sum_and_slope', 'answer_type': 'expression', 'problem_type_id': 'intercept_form_from_intercept_sum_and_slope', 'display_order': 4548, 'source_order': 4548, 'sampling_weight': 10.0}, {'textbook_example_id': 4555, 'component_id': 'src_4555', 'generator_key': 'src_4555', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4555', 'line_type': 'intercept_form_equation_and_triangle_area', 'answer_type': 'multi_part', 'problem_type_id': 'intercept_form_equation_and_triangle_area', 'display_order': 4555, 'source_order': 4555, 'sampling_weight': 10.0}, {'textbook_example_id': 4558, 'component_id': 'src_4558', 'generator_key': 'src_4558', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4558', 'line_type': 'triangle_area_bisector_line_equation', 'answer_type': 'linear_equation', 'problem_type_id': 'triangle_area_bisector_line_equation', 'display_order': 4558, 'source_order': 4558, 'sampling_weight': 10.0}, {'textbook_example_id': 4559, 'component_id': 'src_4559', 'generator_key': 'src_4559', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4559', 'line_type': 'parabola_secant_parallel_line_choice', 'answer_type': 'single_choice', 'problem_type_id': 'parabola_secant_parallel_line_choice', 'display_order': 4559, 'source_order': 4559, 'sampling_weight': 10.0}, {'textbook_example_id': 4564, 'component_id': 'src_4564', 'generator_key': 'src_4564', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4564', 'line_type': 'intercept_form_equation_and_triangle_area', 'answer_type': 'multi_part', 'problem_type_id': 'intercept_form_equation_and_triangle_area', 'display_order': 4564, 'source_order': 4564, 'sampling_weight': 10.0}, {'textbook_example_id': 4604, 'component_id': 'src_4604', 'generator_key': 'src_4604', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4604', 'line_type': 'intercept_form_triangle_area', 'answer_type': 'single_choice', 'problem_type_id': 'intercept_form_triangle_area', 'display_order': 4604, 'source_order': 4604, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_4547': 'components/src_4547/generate.py', 'src_4548': 'components/src_4548/generate.py', 'src_4555': 'components/src_4555/generate.py', 'src_4558': 'components/src_4558/generate.py', 'src_4559': 'components/src_4559/generate.py', 'src_4564': 'components/src_4564/generate.py', 'src_4604': 'components/src_4604/generate.py'}
_V3_ROOT = Path(__file__).resolve().parent
_RR_CURSOR = 0


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
    if seed is None:
        global _RR_CURSOR
        picked = ordered_keys[_RR_CURSOR % len(ordered_keys)]
        _RR_CURSOR += 1
        return picked
    import random

    weights = [_component_sampling_weight(key) for key in ordered_keys]
    return random.Random(seed).choices(ordered_keys, weights=weights, k=1)[0]


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
