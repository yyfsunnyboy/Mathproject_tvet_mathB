from __future__ import annotations

import importlib.util
import random
from pathlib import Path
from typing import Any

_COMMON_PATH = Path(__file__).resolve().parents[1] / "_poll_common.py"
_spec = importlib.util.spec_from_file_location("poll_common", _COMMON_PATH)
_common = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_common)

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "single_choice"
PROBLEM_TYPE_ID = "poll_support_from_interval"
TEXTBOOK_EXAMPLE_ID = 3861
DEFAULT_COMPONENT_ID = "src_3861"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed if seed is not None else TEXTBOOK_EXAMPLE_ID)
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID)
    params = _common.generate_poll_params(rng)

    p = float(params["support_percent"])
    e = float(params["margin_percent"])
    lower = float(params["lower_bound"])
    upper = float(params["upper_bound"])
    decimals = int(params["decimals"])

    option_specs = _common.build_support_choice_options(p, e, lower, upper, decimals, rng)
    choices, answer_label, correct_text = _common.build_shuffled_choices(option_specs, rng)

    interval_text = _common.format_interval(lower, upper, decimals)
    question_text = (
        f"某次民意調查{_common.CONFIDENCE_PHRASE}，\n"
        f"所得支持度的可能範圍為 {interval_text}。\n"
        "此次調查所得到的支持度 p 為多少？"
    )
    midpoint = _common.round_value((lower + upper) / 2, decimals)
    lo_text = _common.format_number(lower, decimals)
    hi_text = _common.format_number(upper, decimals)
    mid_text = _common.format_number(midpoint, decimals)
    explanation = (
        f"{_common.CONFIDENCE_PHRASE}為題目背景資訊，本題計算不需使用 {_common.CONFIDENCE_LEVEL_PERCENT}%。\n"
        "支持度 p 為信賴區間的中點，只需使用已給的可能範圍上下限：\n"
        f"p = ({lo_text} + {hi_text}) ÷ 2 = {mid_text}%，也就是 {correct_text}。\n"
        f"故正確答案為 ({answer_label})。"
    )

    givens = {
        "support_percent": p,
        "margin_percent": e,
        "lower_bound": lower,
        "upper_bound": upper,
        "decimals": decimals,
        "confidence_level_percent": _common.CONFIDENCE_LEVEL_PERCENT,
    }
    validation_facts = dict(givens)
    validation_facts["correct_option_text"] = correct_text

    return _common.build_single_choice_payload(
        component_id=component_id,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID,
        problem_type_id=PROBLEM_TYPE_ID,
        source_kind="quiz",
        question_text=question_text,
        explanation=explanation,
        choices=choices,
        answer_label=answer_label,
        display_answer=correct_text,
        seed=seed,
        validation_facts=validation_facts,
        givens=givens,
    )
