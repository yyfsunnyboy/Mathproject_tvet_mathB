from __future__ import annotations

import random
from typing import Any

from core.domain.statistics.frequency_distribution_domain import build_frequency_distribution_table_matrix

PRESENTATION_MODE = "single_choice"
ANSWER_TYPE = "choice_label"
PROBLEM_TYPE_ID = "histogram_distribution_update"
TEXTBOOK_EXAMPLE_ID = 3829
SKILL_ID = "vh_數學B4_HistogramsAndFrequencyPolygons"
DEFAULT_COMPONENT_ID = "src_3829"

HEIGHT_BINS = ["100~105", "105~110", "110~115", "115~120", "120~125"]
BIN_BOUNDS = [(100, 105), (105, 110), (110, 115), (115, 120), (120, 125)]


def _values_in_bin(bin_label: str) -> list[int]:
    idx = HEIGHT_BINS.index(bin_label)
    lo, hi = BIN_BOUNDS[idx]
    return list(range(lo, hi))


def _option_text(out_bin: str, in_bin: str, out_delta: int, in_delta: int) -> str:
    out_word = "加" if out_delta > 0 else "減"
    in_word = "加" if in_delta > 0 else "減"
    return f"{out_bin}組次數{out_word}{abs(out_delta)}，{in_bin}組次數{in_word}{abs(in_delta)}"


def _adjacent_bins(bin_label: str) -> list[str]:
    idx = HEIGHT_BINS.index(bin_label)
    neighbors: list[str] = []
    if idx > 0:
        neighbors.append(HEIGHT_BINS[idx - 1])
    if idx < len(HEIGHT_BINS) - 1:
        neighbors.append(HEIGHT_BINS[idx + 1])
    return neighbors


def _build_distractors(
    out_bin: str,
    in_bin: str,
    correct_text: str,
    rng: random.Random,
) -> list[str]:
    reversed_text = _option_text(out_bin, in_bin, +1, -1)

    wrong_out_neighbors = _adjacent_bins(out_bin)
    wrong_out = rng.choice(wrong_out_neighbors) if wrong_out_neighbors else out_bin
    adjacent_out_text = _option_text(wrong_out, in_bin, -1, +1)

    wrong_in_candidates = [b for b in _adjacent_bins(in_bin) if b != out_bin]
    if not wrong_in_candidates:
        wrong_in_candidates = [b for b in _adjacent_bins(in_bin)] or [in_bin]
    wrong_in = rng.choice(wrong_in_candidates)
    mixed_text = _option_text(out_bin, wrong_in, -1, +1)

    pool = [reversed_text, adjacent_out_text, mixed_text]
    unique: list[str] = []
    seen = {correct_text}
    for text in pool:
        if text not in seen:
            seen.add(text)
            unique.append(text)

    while len(unique) < 3:
        alt_out = rng.choice(HEIGHT_BINS)
        alt_in = rng.choice([b for b in HEIGHT_BINS if b != alt_out])
        alt_text = _option_text(alt_out, alt_in, rng.choice([-1, 1]), rng.choice([-1, 1]))
        if alt_text not in seen:
            seen.add(alt_text)
            unique.append(alt_text)

    return unique[:3]


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    rng = random.Random(seed if seed is not None else TEXTBOOK_EXAMPLE_ID)
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID)

    matrix = build_frequency_distribution_table_matrix(
        seed=seed,
        domain_operation="histogram_distribution_update",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={},
    )
    givens = dict(matrix.get("givens") or {})
    freq_map = dict(givens.get("frequency_map") or {})
    height_bins = list(givens.get("categories") or HEIGHT_BINS)

    eligible_out = [b for b in height_bins if int(freq_map.get(b, 0)) >= 2]
    if not eligible_out:
        eligible_out = [height_bins[min(3, len(height_bins) - 1)]]
    out_bin = rng.choice(eligible_out)
    in_candidates = [b for b in height_bins if b != out_bin]
    in_bin = rng.choice(in_candidates)

    trans_out_val = rng.choice(_values_in_bin(out_bin))
    trans_in_val = rng.choice(_values_in_bin(in_bin))

    correct_text = _option_text(out_bin, in_bin, -1, +1)
    distractor_texts = _build_distractors(out_bin, in_bin, correct_text, rng)

    options_pool = [{"text": correct_text, "is_correct": True}]
    for text in distractor_texts:
        options_pool.append({"text": text, "is_correct": False})

    rng.shuffle(options_pool)

    labels = ["A", "B", "C", "D"]
    choices: list[dict[str, str]] = []
    answer_label = "A"
    for label, opt in zip(labels, options_pool):
        choices.append({"key": label, "label": label, "text": opt["text"]})
        if opt["is_correct"]:
            answer_label = label

    question_text = (
        "下圖為某幼兒園班上25位小朋友身高分布之直方圖。"
        f"今班上轉出一位身高{trans_out_val}公分的小朋友，"
        f"轉入一位身高{trans_in_val}公分的小朋友，"
        "下列何者正確描述受影響組距及其次數變化？"
    )

    init_map = freq_map
    final_map = dict(init_map)
    final_map[out_bin] = int(init_map.get(out_bin, 0)) - 1
    final_map[in_bin] = int(init_map.get(in_bin, 0)) + 1

    explanation = (
        f"1. 轉出一位身高 {trans_out_val} 公分的小朋友，屬於 {out_bin} 組，"
        f"因此該組人數減少 1 人（{init_map[out_bin]} -> {final_map[out_bin]} 人）。\n"
        f"2. 轉入一位身高 {trans_in_val} 公分的小朋友，屬於 {in_bin} 組，"
        f"因此該組人數增加 1 人（{init_map[in_bin]} -> {final_map[in_bin]} 人）。\n"
        "3. 其餘各組人數不變。\n"
        f"故正確答案為 ({answer_label})。"
    )

    validation_facts = dict(matrix.get("validation_facts") or {})
    validation_facts.update(
        {
            "trans_out_val": trans_out_val,
            "trans_in_val": trans_in_val,
            "out_bin": out_bin,
            "in_bin": in_bin,
            "correct_option_text": correct_text,
        }
    )

    ui_contract = {
        "response_mode": "choice",
        "text_input_enabled": False,
        "normal_submit_enabled": True,
        "ai_check_required": False,
        "canvas_required": True,
        "allow_image_upload": False,
        "allow_text_answer": False,
    }

    image_base64 = matrix.get("image_base64") or ""
    visual_aids = matrix.get("visual_aids") or []
    visual_spec = matrix.get("visual_spec") or {}

    return {
        "skill_id": SKILL_ID,
        "component_id": component_id,
        "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
        "problem_type_id": PROBLEM_TYPE_ID,
        "domain_operation": PROBLEM_TYPE_ID,
        "source_kind": "example",
        "question_type": "single_choice",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
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
        "display_answer": correct_text,
        "checker_key": "choice_label_checker",
        "equivalence_type": "choice_label",
        "answer_contract": {
            "presentation_mode": PRESENTATION_MODE,
            "answer_type": ANSWER_TYPE,
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence": "choice_label",
            "semantic_answer": answer_label,
            "ui_contract": ui_contract,
        },
        "metadata": {
            "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
            "component_id": component_id,
            "presentation_mode": PRESENTATION_MODE,
            "answer_type": ANSWER_TYPE,
            "problem_type_id": PROBLEM_TYPE_ID,
            "source_kind": "example",
            "semantic_answer": answer_label,
            "question_type": "single_choice",
        },
        "math_core": {
            "givens": givens,
            "raw_givens": givens,
            "target": correct_text,
            "math_objects": ["frequency_table", "histogram"],
            "derivation": explanation.split("\n"),
            "validation_facts": validation_facts,
        },
        "visual_spec": visual_spec,
        "visual_aids": visual_aids,
        "image_base64": image_base64,
        "validation_facts": validation_facts,
        "generator_key": component_id or DEFAULT_COMPONENT_ID,
    }
