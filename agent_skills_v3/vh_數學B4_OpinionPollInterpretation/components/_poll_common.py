from __future__ import annotations

import random
from typing import Any

SKILL_ID = "vh_數學B4_OpinionPollInterpretation"
CONFIDENCE_LEVEL_PERCENT = 95
CONFIDENCE_PHRASE = "在 95% 的信心水準下"

UI_CONTRACT: dict[str, Any] = {
    "response_mode": "choice",
    "text_input_enabled": False,
    "normal_submit_enabled": True,
    "ai_check_required": False,
    "canvas_required": False,
    "allow_image_upload": False,
    "allow_text_answer": False,
}


def round_value(val: float, decimals: int) -> float:
    return round(val, decimals)


def format_number(val: float, decimals: int) -> str:
    rounded = round_value(val, decimals)
    if decimals == 0:
        return str(int(rounded))
    return f"{rounded:.{decimals}f}"


def format_percent(val: float, decimals: int) -> str:
    return f"{format_number(val, decimals)}%"


def format_interval(lo: float, hi: float, decimals: int) -> str:
    return f"{format_number(lo, decimals)}%～{format_number(hi, decimals)}%"


def valid_interval(lo: float, hi: float) -> bool:
    return 0 <= lo < hi <= 100


def generate_sample_size(rng: random.Random) -> int:
    return rng.choice([850, 900, 960, 1000, 1050, 1080, 1100, 1150, 1200])


def generate_poll_params(rng: random.Random) -> dict[str, Any]:
    decimals = rng.choice([0, 1, 2])
    scale = 10 ** decimals
    for _ in range(200):
        e_scaled = rng.randint(1, 12 * scale)
        p_min_scaled = e_scaled + scale
        p_max_scaled = 100 * scale - e_scaled
        if p_min_scaled > p_max_scaled:
            continue
        p_scaled = rng.randint(p_min_scaled, p_max_scaled)
        p = p_scaled / scale
        e = e_scaled / scale
        lower = round_value(p - e, decimals)
        upper = round_value(p + e, decimals)
        if not (0 < e < p and lower >= 0 and upper <= 100 and lower < upper):
            continue
        return {
            "support_percent": p,
            "margin_percent": e,
            "lower_bound": lower,
            "upper_bound": upper,
            "decimals": decimals,
            "sample_size": generate_sample_size(rng),
            "confidence_level_percent": CONFIDENCE_LEVEL_PERCENT,
        }
    return {
        "support_percent": 55.0,
        "margin_percent": 3.0,
        "lower_bound": 52.0,
        "upper_bound": 58.0,
        "decimals": 0,
        "sample_size": 1100,
        "confidence_level_percent": CONFIDENCE_LEVEL_PERCENT,
    }


def _append_interval_option(
    options: list[tuple[str, bool]],
    seen: set[str],
    lo: float,
    hi: float,
    is_correct: bool,
    decimals: int,
) -> None:
    lo_r = round_value(lo, decimals)
    hi_r = round_value(hi, decimals)
    if not valid_interval(lo_r, hi_r):
        return
    text = format_interval(lo_r, hi_r, decimals)
    if text in seen:
        return
    seen.add(text)
    options.append((text, is_correct))


def build_interval_choice_options(
    p: float,
    e: float,
    lower: float,
    upper: float,
    decimals: int,
    rng: random.Random,
) -> list[tuple[str, bool]]:
    options: list[tuple[str, bool]] = []
    seen: set[str] = set()
    candidate_pairs = [
        (lower, upper, True),
        (p + e, p + 2 * e, False),
        (p - 2 * e, p - e, False),
        (p - 2 * e, p + 2 * e, False),
        (0, lower, False),
        (upper, min(100, upper + e), False),
        (max(0, lower - e), lower, False),
        (upper, min(100, upper + 2 * e), False),
        (max(0, p - 3 * e), max(0, p - e), False),
        (min(100, p + e), min(100, p + 3 * e), False),
        (max(0, lower - 2 * e), max(0, lower - e), False),
        (min(100, upper + e), min(100, upper + 2 * e), False),
    ]
    for lo, hi, is_correct in candidate_pairs:
        if len(options) >= 4:
            break
        _append_interval_option(options, seen, lo, hi, is_correct, decimals)

    attempts = 0
    while len(options) < 4 and attempts < 100:
        attempts += 1
        shift = (attempts % 7 + 1) * max(e, 0.1)
        lo_r = round_value(max(0, lower - shift), decimals)
        hi_r = round_value(min(100, lo_r + e), decimals)
        if not valid_interval(lo_r, hi_r):
            lo_r = round_value(max(0, min(100, upper) - e), decimals)
            hi_r = round_value(min(100, upper + shift), decimals)
        _append_interval_option(options, seen, lo_r, hi_r, False, decimals)

    if not any(flag for _, flag in options):
        raise ValueError("interval_options_missing_correct")
    if len(options) < 4:
        raise ValueError("interval_options_insufficient")
    correct = next(text for text, flag in options if flag)
    distractors = [text for text, flag in options if not flag][:3]
    return [(correct, True)] + [(text, False) for text in distractors]


def _append_value_option(
    options: list[tuple[str, bool]],
    seen: set[str],
    val: float,
    is_correct: bool,
    decimals: int,
) -> None:
    text = format_percent(round_value(val, decimals), decimals)
    if text in seen:
        return
    seen.add(text)
    options.append((text, is_correct))


def build_support_choice_options(
    p: float,
    e: float,
    lower: float,
    upper: float,
    decimals: int,
    rng: random.Random,
) -> list[tuple[str, bool]]:
    midpoint = round_value((lower + upper) / 2, decimals)
    width = round_value(upper - lower, decimals)
    half_width = round_value(width / 2, decimals)
    bound_val = lower if rng.random() < 0.5 else upper
    if round_value(bound_val, decimals) == midpoint:
        bound_val = upper if bound_val == lower else lower

    options: list[tuple[str, bool]] = []
    seen: set[str] = set()
    candidate_values = [
        (midpoint, True),
        (width, False),
        (half_width, False),
        (bound_val, False),
        (lower, False),
        (upper, False),
        (p + e, False),
        (max(0, p - e), False),
        (p + 2 * e, False),
        (max(0, p - 2 * e), False),
    ]
    for val, is_correct in candidate_values:
        if len(options) >= 4:
            break
        _append_value_option(options, seen, val, is_correct, decimals)

    attempts = 0
    while len(options) < 4 and attempts < 100:
        attempts += 1
        delta = (attempts % 5 + 1) * max(e / 2, 0.5)
        sign = 1 if attempts % 2 else -1
        val = round_value(min(100, max(0, p + sign * delta)), decimals)
        _append_value_option(options, seen, val, False, decimals)

    if not any(flag for _, flag in options):
        raise ValueError("support_options_missing_correct")
    if len(options) < 4:
        raise ValueError("support_options_insufficient")
    correct = next(text for text, flag in options if flag)
    distractors = [text for text, flag in options if not flag][:3]
    return [(correct, True)] + [(text, False) for text in distractors]


def build_shuffled_choices(
    option_specs: list[tuple[str, bool]],
    rng: random.Random,
) -> tuple[list[dict[str, str]], str, str]:
    specs = list(option_specs)
    rng.shuffle(specs)
    labels = ["A", "B", "C", "D"]
    choices: list[dict[str, str]] = []
    answer_label = "A"
    correct_text = ""
    for label, (text, is_correct) in zip(labels, specs):
        choices.append({"key": label, "label": label, "text": text})
        if is_correct:
            answer_label = label
            correct_text = text
    return choices, answer_label, correct_text


def build_single_choice_payload(
    *,
    component_id: str,
    textbook_example_id: int,
    problem_type_id: str,
    source_kind: str,
    question_text: str,
    explanation: str,
    choices: list[dict[str, str]],
    answer_label: str,
    display_answer: str,
    seed: int | None,
    validation_facts: dict[str, Any],
    givens: dict[str, Any],
) -> dict[str, Any]:
    answer_contract = {
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "answer_equivalence": "choice_label",
        "equivalence": "choice_label",
        "semantic_answer": answer_label,
        "ui_contract": dict(UI_CONTRACT),
    }
    return {
        "skill_id": SKILL_ID,
        "component_id": component_id,
        "textbook_example_id": textbook_example_id,
        "problem_type_id": problem_type_id,
        "domain_operation": problem_type_id,
        "source_kind": source_kind,
        "question_type": "single_choice",
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "interaction_type": "single_choice",
        "auto_checkable": True,
        "grading_mode": "auto",
        "question_text": question_text,
        "explanation": explanation,
        "seed": seed,
        "choices": choices,
        "options": [c["text"] for c in choices],
        "answer": answer_label,
        "correct_answer": answer_label,
        "display_answer": display_answer,
        "checker_key": "choice_label_checker",
        "equivalence_type": "choice_label",
        "answer_contract": answer_contract,
        "metadata": {
            "textbook_example_id": textbook_example_id,
            "component_id": component_id,
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "problem_type_id": problem_type_id,
            "source_kind": source_kind,
            "semantic_answer": answer_label,
            "question_type": "single_choice",
            "givens": givens,
        },
        "math_core": {
            "givens": givens,
            "raw_givens": givens,
            "target": display_answer,
            "math_objects": ["poll_support", "margin_of_error", "confidence_interval"],
            "derivation": [line for line in explanation.split("\n") if line.strip()],
            "validation_facts": validation_facts,
        },
        "validation_facts": validation_facts,
        "generator_key": component_id,
    }
