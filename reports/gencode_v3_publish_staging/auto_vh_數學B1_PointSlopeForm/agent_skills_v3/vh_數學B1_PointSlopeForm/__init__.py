from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'vh_數學B1_PointSlopeForm'
GENERATOR_KEYS = ['src_4540', 'src_4541', 'src_4542', 'src_4543', 'src_4546', 'src_4549', 'src_4550', 'src_4551', 'src_4552', 'src_4556', 'src_4557', 'src_4560', 'src_4561', 'src_4606']
GENERATOR_SPECS = [{'textbook_example_id': 4540, 'component_id': 'src_4540', 'generator_key': 'src_4540', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4540', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4540, 'source_order': 4540, 'sampling_weight': 10.0}, {'textbook_example_id': 4541, 'component_id': 'src_4541', 'generator_key': 'src_4541', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4541', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4541, 'source_order': 4541, 'sampling_weight': 10.0}, {'textbook_example_id': 4542, 'component_id': 'src_4542', 'generator_key': 'src_4542', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4542', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4542, 'source_order': 4542, 'sampling_weight': 10.0}, {'textbook_example_id': 4543, 'component_id': 'src_4543', 'generator_key': 'src_4543', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4543', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4543, 'source_order': 4543, 'sampling_weight': 10.0}, {'textbook_example_id': 4546, 'component_id': 'src_4546', 'generator_key': 'src_4546', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4546', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4546, 'source_order': 4546, 'sampling_weight': 10.0}, {'textbook_example_id': 4549, 'component_id': 'src_4549', 'generator_key': 'src_4549', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4549', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4549, 'source_order': 4549, 'sampling_weight': 10.0}, {'textbook_example_id': 4550, 'component_id': 'src_4550', 'generator_key': 'src_4550', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4550', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4550, 'source_order': 4550, 'sampling_weight': 10.0}, {'textbook_example_id': 4551, 'component_id': 'src_4551', 'generator_key': 'src_4551', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4551', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4551, 'source_order': 4551, 'sampling_weight': 10.0}, {'textbook_example_id': 4552, 'component_id': 'src_4552', 'generator_key': 'src_4552', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4552', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4552, 'source_order': 4552, 'sampling_weight': 10.0}, {'textbook_example_id': 4556, 'component_id': 'src_4556', 'generator_key': 'src_4556', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4556', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4556, 'source_order': 4556, 'sampling_weight': 10.0}, {'textbook_example_id': 4557, 'component_id': 'src_4557', 'generator_key': 'src_4557', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4557', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4557, 'source_order': 4557, 'sampling_weight': 10.0}, {'textbook_example_id': 4560, 'component_id': 'src_4560', 'generator_key': 'src_4560', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4560', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4560, 'source_order': 4560, 'sampling_weight': 10.0}, {'textbook_example_id': 4561, 'component_id': 'src_4561', 'generator_key': 'src_4561', 'presentation_mode': 'short_answer', 'source_kind': 'ex_4561', 'line_type': 'point_slope', 'answer_type': 'expression', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4561, 'source_order': 4561, 'sampling_weight': 10.0}, {'textbook_example_id': 4606, 'component_id': 'src_4606', 'generator_key': 'src_4606', 'presentation_mode': 'single_choice', 'source_kind': 'ex_4606', 'line_type': 'point_slope', 'answer_type': 'single_choice', 'problem_type_id': 'write_line_equation_from_point_slope', 'display_order': 4606, 'source_order': 4606, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_4540': 'components/src_4540/generate.py', 'src_4541': 'components/src_4541/generate.py', 'src_4542': 'components/src_4542/generate.py', 'src_4543': 'components/src_4543/generate.py', 'src_4546': 'components/src_4546/generate.py', 'src_4549': 'components/src_4549/generate.py', 'src_4550': 'components/src_4550/generate.py', 'src_4551': 'components/src_4551/generate.py', 'src_4552': 'components/src_4552/generate.py', 'src_4556': 'components/src_4556/generate.py', 'src_4557': 'components/src_4557/generate.py', 'src_4560': 'components/src_4560/generate.py', 'src_4561': 'components/src_4561/generate.py', 'src_4606': 'components/src_4606/generate.py'}
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
