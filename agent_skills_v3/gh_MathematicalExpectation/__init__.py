from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_MathematicalExpectation'
GENERATOR_KEYS = ['src_12891', 'src_12892', 'src_12893', 'src_12894', 'src_12895', 'src_12896', 'src_12897', 'src_12898', 'src_12899', 'src_12900', 'src_12901', 'src_12902', 'src_12903', 'src_12904', 'src_12905', 'src_12906', 'src_12907', 'src_12908', 'src_12909', 'src_12910', 'src_12911']
GENERATOR_SPECS = [{'textbook_example_id': 12891, 'component_id': 'src_12891', 'generator_key': 'src_12891', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'die_payout_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'die_payout_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12891, 'source_order': 12891, 'sampling_weight': 10.0}, {'textbook_example_id': 12892, 'component_id': 'src_12892', 'generator_key': 'src_12892', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'urn_draw_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'urn_draw_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12892, 'source_order': 12892, 'sampling_weight': 10.0}, {'textbook_example_id': 12893, 'component_id': 'src_12893', 'generator_key': 'src_12893', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'urn_draw_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'urn_draw_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12893, 'source_order': 12893, 'sampling_weight': 10.0}, {'textbook_example_id': 12894, 'component_id': 'src_12894', 'generator_key': 'src_12894', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'coin_payout_expectation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'coin_payout_expectation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12894, 'source_order': 12894, 'sampling_weight': 10.0}, {'textbook_example_id': 12895, 'component_id': 'src_12895', 'generator_key': 'src_12895', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'insurance_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'insurance_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12895, 'source_order': 12895, 'sampling_weight': 10.0}, {'textbook_example_id': 12896, 'component_id': 'src_12896', 'generator_key': 'src_12896', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'coin_payout_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'coin_payout_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12896, 'source_order': 12896, 'sampling_weight': 10.0}, {'textbook_example_id': 12897, 'component_id': 'src_12897', 'generator_key': 'src_12897', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'urn_draw_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'urn_draw_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12897, 'source_order': 12897, 'sampling_weight': 10.0}, {'textbook_example_id': 12898, 'component_id': 'src_12898', 'generator_key': 'src_12898', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'urn_draw_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'urn_draw_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12898, 'source_order': 12898, 'sampling_weight': 10.0}, {'textbook_example_id': 12899, 'component_id': 'src_12899', 'generator_key': 'src_12899', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'two_dice_match_game', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'two_dice_match_game', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12899, 'source_order': 12899, 'sampling_weight': 10.0}, {'textbook_example_id': 12900, 'component_id': 'src_12900', 'generator_key': 'src_12900', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'quiz', 'line_type': 'decision_by_expectation', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'decision_by_expectation', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12900, 'source_order': 12900, 'sampling_weight': 10.0}, {'textbook_example_id': 12901, 'component_id': 'src_12901', 'generator_key': 'src_12901', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'expectation_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'expectation_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12901, 'source_order': 12901, 'sampling_weight': 10.0}, {'textbook_example_id': 12902, 'component_id': 'src_12902', 'generator_key': 'src_12902', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'expectation_claim', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'expectation_claim', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12902, 'source_order': 12902, 'sampling_weight': 10.0}, {'textbook_example_id': 12903, 'component_id': 'src_12903', 'generator_key': 'src_12903', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'die_payout_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'die_payout_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12903, 'source_order': 12903, 'sampling_weight': 10.0}, {'textbook_example_id': 12904, 'component_id': 'src_12904', 'generator_key': 'src_12904', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'urn_draw_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'urn_draw_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12904, 'source_order': 12904, 'sampling_weight': 10.0}, {'textbook_example_id': 12905, 'component_id': 'src_12905', 'generator_key': 'src_12905', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'urn_draw_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'urn_draw_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12905, 'source_order': 12905, 'sampling_weight': 10.0}, {'textbook_example_id': 12906, 'component_id': 'src_12906', 'generator_key': 'src_12906', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'urn_draw_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'urn_draw_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12906, 'source_order': 12906, 'sampling_weight': 10.0}, {'textbook_example_id': 12907, 'component_id': 'src_12907', 'generator_key': 'src_12907', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'single_die_game', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'single_die_game', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12907, 'source_order': 12907, 'sampling_weight': 10.0}, {'textbook_example_id': 12908, 'component_id': 'src_12908', 'generator_key': 'src_12908', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'insurance_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'insurance_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12908, 'source_order': 12908, 'sampling_weight': 10.0}, {'textbook_example_id': 12909, 'component_id': 'src_12909', 'generator_key': 'src_12909', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'multiple_choice_guess_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'multiple_choice_guess_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12909, 'source_order': 12909, 'sampling_weight': 10.0}, {'textbook_example_id': 12910, 'component_id': 'src_12910', 'generator_key': 'src_12910', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'lottery_expectation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'lottery_expectation', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12910, 'source_order': 12910, 'sampling_weight': 10.0}, {'textbook_example_id': 12911, 'component_id': 'src_12911', 'generator_key': 'src_12911', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'prize_ball_expectation', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'prize_ball_expectation', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12911, 'source_order': 12911, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12891': 'components/src_12891/generate.py', 'src_12892': 'components/src_12892/generate.py', 'src_12893': 'components/src_12893/generate.py', 'src_12894': 'components/src_12894/generate.py', 'src_12895': 'components/src_12895/generate.py', 'src_12896': 'components/src_12896/generate.py', 'src_12897': 'components/src_12897/generate.py', 'src_12898': 'components/src_12898/generate.py', 'src_12899': 'components/src_12899/generate.py', 'src_12900': 'components/src_12900/generate.py', 'src_12901': 'components/src_12901/generate.py', 'src_12902': 'components/src_12902/generate.py', 'src_12903': 'components/src_12903/generate.py', 'src_12904': 'components/src_12904/generate.py', 'src_12905': 'components/src_12905/generate.py', 'src_12906': 'components/src_12906/generate.py', 'src_12907': 'components/src_12907/generate.py', 'src_12908': 'components/src_12908/generate.py', 'src_12909': 'components/src_12909/generate.py', 'src_12910': 'components/src_12910/generate.py', 'src_12911': 'components/src_12911/generate.py'}
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
