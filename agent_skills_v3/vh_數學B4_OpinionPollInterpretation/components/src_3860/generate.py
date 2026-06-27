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
PROBLEM_TYPE_ID = "poll_interval_from_support_and_margin"
TEXTBOOK_EXAMPLE_ID = 3860
DEFAULT_COMPONENT_ID = "src_3860"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed if seed is not None else TEXTBOOK_EXAMPLE_ID)
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID)
    params = _common.generate_poll_params(rng)

    p = float(params["support_percent"])
    e = float(params["margin_percent"])
    lower = float(params["lower_bound"])
    upper = float(params["upper_bound"])
    decimals = int(params["decimals"])

    option_specs = _common.build_interval_choice_options(p, e, lower, upper, decimals, rng)
    choices, answer_label, correct_text = _common.build_shuffled_choices(option_specs, rng)

    p_text = _common.format_number(p, decimals)
    e_text = _common.format_number(e, decimals)
    sample_size = int(params.get("sample_size") or 1100)
    question_text = (
        f"某次民意調查成功訪問 {sample_size} 位選民。\n"
        f"{_common.CONFIDENCE_PHRASE}，有 {p_text}% 的選民表示支持，"
        f"抽樣誤差為 ±{e_text} 個百分點。\n"
        "下列何者為支持度的可能範圍？"
    )
    explanation = (
        f"{_common.CONFIDENCE_PHRASE}為題目背景資訊，本題計算不需使用 {_common.CONFIDENCE_LEVEL_PERCENT}% 或樣本數。\n"
        f"支持度可能範圍只需使用支持度 {p_text}% 與抽樣誤差 {e_text} 個百分點：\n"
        f"{p_text}% − {e_text}% = {_common.format_number(lower, decimals)}%，"
        f"{p_text}% + {e_text}% = {_common.format_number(upper, decimals)}%。\n"
        f"故可能範圍為 {correct_text}，正確答案為 ({answer_label})。"
    )

    givens = {
        "support_percent": p,
        "margin_percent": e,
        "lower_bound": lower,
        "upper_bound": upper,
        "decimals": decimals,
        "sample_size": sample_size,
        "confidence_level_percent": _common.CONFIDENCE_LEVEL_PERCENT,
    }
    validation_facts = dict(givens)
    validation_facts["correct_option_text"] = correct_text

    return _common.build_single_choice_payload(
        component_id=component_id,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID,
        problem_type_id=PROBLEM_TYPE_ID,
        source_kind="example",
        question_text=question_text,
        explanation=explanation,
        choices=choices,
        answer_label=answer_label,
        display_answer=correct_text,
        seed=seed,
        validation_facts=validation_facts,
        givens=givens,
    )
