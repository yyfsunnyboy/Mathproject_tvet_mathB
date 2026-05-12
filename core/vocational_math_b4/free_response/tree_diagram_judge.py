# -*- coding: utf-8 -*-
"""Rule-based text judge prototype for B4 tree diagram listing answers.

This module is intentionally isolated from deterministic int-answer runtime.
"""

from __future__ import annotations

import re
from collections import Counter
from itertools import product
from typing import Any


PROBLEM_TYPE_ID = "tree_diagram_listing"
GRADING_MODE = "ai_judged_free_response"

FIXED_STAGE_BINARY_TREE_PATHS: tuple[str, ...] = (
    "正正正",
    "正正反",
    "正反正",
    "正反反",
    "反正正",
    "反正反",
    "反反正",
    "反反反",
)

EARLY_STOPPING_GAME_PATHS: tuple[str, ...] = (
    "甲甲",
    "甲乙甲",
    "甲乙乙",
    "乙甲甲",
    "乙甲乙",
    "乙乙",
)

EARLY_STOPPING_FIXED_THREE_ROUND_PATHS: tuple[str, ...] = (
    "甲甲甲",
    "甲甲乙",
    "甲乙甲",
    "甲乙乙",
    "乙甲甲",
    "乙甲乙",
    "乙乙甲",
    "乙乙乙",
)


FIXED_STAGE_BINARY_TREE_PARAM_SETS: tuple[tuple[list[str], int], ...] = (
    (["正", "反"], 3),
    (["成", "敗"], 2),
    (["紅", "藍"], 3),
    (["甲", "乙"], 3),
    (["成", "敗"], 3),
    (["紅", "藍"], 2),
)

EARLY_STOPPING_GAME_LABEL_SETS: tuple[list[str], ...] = (
    ["甲", "乙"],
    ["紅", "藍"],
    ["A", "B"],
)


def _pick_indexed(items: tuple[Any, ...], *, seed: int | None = None, index: int | None = None) -> Any:
    if index is not None:
        return items[index % len(items)]
    if seed is not None:
        return items[seed % len(items)]
    return items[0]


def _binary_paths(labels: list[str], stages: int) -> list[str]:
    return ["".join(path) for path in product(labels, repeat=stages)]


def _early_stopping_paths(labels: list[str]) -> list[str]:
    first, second = labels
    return [
        first + first,
        first + second + first,
        first + second + second,
        second + first + first,
        second + first + second,
        second + second,
    ]


def _fixed_stage_question_text(labels: list[str], stages: int) -> str:
    first, second = labels
    stage_text = "兩" if stages == 2 else "三"
    if labels == ["正", "反"]:
        return f"投擲一枚均勻硬幣連續{stage_text}次，試用樹狀圖或完整列舉方式描述所有可能情形。"
    if labels == ["成", "敗"]:
        return f"某實驗每次結果可能為成功或失敗，連續進行{stage_text}次，試用樹狀圖或完整列舉方式描述所有可能情形。"
    return f"每次從{first}、{second}兩種結果中出現一種，連續進行{stage_text}次，試用樹狀圖或完整列舉方式描述所有可能情形。"


def _early_stopping_question_text(labels: list[str]) -> str:
    first, second = labels
    return f"{first}、{second}兩隊比賽，每場沒有平手，先贏兩場者勝。試問共有多少種勝負情形？請用樹狀圖或完整列舉方式描述所有可能情形。"


TREE_DIAGRAM_DIVERSITY_SCENARIOS: tuple[dict[str, Any], ...] = (
    {
        "scenario_family": "binary_three_trials",
        "scenario_id": "coin_toss_three_times",
        "context_signature": "coin_3_trials",
        "outcome_set_signature": "H_T",
        "question_text": "投擲一枚均勻硬幣連續三次，請用樹狀圖或完整列舉方式寫出所有可能結果，並寫出總數。",
        "stage_options": [["正", "反"], ["正", "反"], ["正", "反"]],
    },
    {
        "scenario_family": "binary_two_trials",
        "scenario_id": "coin_toss_two_times",
        "context_signature": "coin_2_trials",
        "outcome_set_signature": "H_T",
        "question_text": "投擲一枚均勻硬幣連續兩次，請用樹狀圖或完整列舉方式列出所有可能結果，並寫出總數。",
        "stage_options": [["正", "反"], ["正", "反"]],
    },
    {
        "scenario_family": "binary_three_trials",
        "scenario_id": "two_color_three_draws_with_replacement",
        "context_signature": "red_blue_with_replacement_3",
        "outcome_set_signature": "red_blue",
        "question_text": "袋中只有紅、藍兩球，每次抽一球後放回，連續抽三次。請用樹狀圖或完整列舉方式列出所有可能結果。",
        "stage_options": [["紅", "藍"], ["紅", "藍"], ["紅", "藍"]],
    },
    {
        "scenario_family": "binary_two_trials",
        "scenario_id": "binary_outcome_two_trials",
        "context_signature": "success_failure_2",
        "outcome_set_signature": "success_failure",
        "question_text": "某實驗每次結果可能為成功或失敗，連續進行兩次。請用樹狀圖或完整列舉方式列出所有可能結果。",
        "stage_options": [["成", "敗"], ["成", "敗"]],
    },
    {
        "scenario_family": "product_rule_two_stage",
        "scenario_id": "meal_choice_two_stage",
        "context_signature": "meal_drink_2x3",
        "outcome_set_signature": "meal2_drink3",
        "question_text": "午餐先選主餐（2 種）再選飲料（3 種），請用樹狀圖或完整列舉方式列出所有搭配。",
        "stage_options": [["主甲", "主乙"], ["飲甲", "飲乙", "飲丙"]],
    },
    {
        "scenario_family": "product_rule_two_stage",
        "scenario_id": "clothing_choice_two_stage_2x2",
        "context_signature": "clothing_2x2",
        "outcome_set_signature": "top2_bottom2",
        "question_text": "穿搭先選上衣（2 種）再選褲子（2 種），請用樹狀圖或完整列舉方式列出所有搭配。",
        "stage_options": [["上甲", "上乙"], ["下甲", "下乙"]],
    },
    {
        "scenario_family": "product_rule_two_stage",
        "scenario_id": "clothing_choice_two_stage_2x3",
        "context_signature": "clothing_2x3",
        "outcome_set_signature": "top2_bottom3",
        "question_text": "穿搭先選上衣（2 種）再選褲子（3 種），請用樹狀圖或完整列舉方式列出所有搭配。",
        "stage_options": [["上甲", "上乙"], ["下甲", "下乙", "下丙"]],
    },
    {
        "scenario_family": "product_rule_two_stage",
        "scenario_id": "route_choice_two_stage",
        "context_signature": "route_2x3",
        "outcome_set_signature": "route2_route3",
        "question_text": "從甲地到乙地有 2 條路，乙地到丙地有 3 條路。請用樹狀圖或完整列舉方式列出所有路線。",
        "stage_options": [["甲路", "乙路"], ["一線", "二線", "三線"]],
    },
    {
        "scenario_family": "product_rule_two_stage",
        "scenario_id": "digit_or_code_two_stage",
        "context_signature": "code_3x2",
        "outcome_set_signature": "digit3_symbol2",
        "question_text": "代碼第一位可選 1、2、3，第二位可選 A、B。請用樹狀圖或完整列舉方式列出所有代碼。",
        "stage_options": [["1", "2", "3"], ["A", "B"]],
    },
    {
        "scenario_family": "mixed_outcome_two_stage",
        "scenario_id": "dice_coin_combination",
        "context_signature": "coin1_dice1",
        "outcome_set_signature": "coin2_dice6",
        "question_text": "擲硬幣一次再擲骰子一次，請用樹狀圖或完整列舉方式列出所有可能結果。",
        "stage_options": [["正", "反"], ["1", "2", "3", "4", "5", "6"]],
    },
    {
        "scenario_family": "best_of_three_binary_match",
        "scenario_id": "win_two_games_best_of_three_named_teams",
        "context_signature": "best_of_three_named",
        "outcome_set_signature": "two_teams",
        "question_text": "兩隊比賽每場無平手，先贏兩場者勝。請用樹狀圖或完整列舉方式列出所有可能比賽進程。",
        "stage_options": [["甲勝", "乙勝"], ["甲勝", "乙勝"], ["甲勝", "乙勝"]],
    },
    {
        "scenario_family": "best_of_three_binary_match",
        "scenario_id": "win_two_games_best_of_three_ab_teams",
        "context_signature": "best_of_three_ab",
        "outcome_set_signature": "two_teams",
        "question_text": "A、B 兩隊比賽每場無平手，先贏兩場者勝。請用樹狀圖或完整列舉方式列出所有可能比賽進程。",
        "stage_options": [["A勝", "B勝"], ["A勝", "B勝"], ["A勝", "B勝"]],
    },
)


def _enumerate_stage_paths(stage_options: list[list[str]]) -> list[str]:
    return ["、".join(path) for path in product(*stage_options)]


def build_tree_diagram_listing_payload(
    variant: str = "early_stopping_game",
    seed: int | None = None,
    index: int | None = None,
) -> dict[str, Any]:
    normalized_variant = str(variant or "").strip()
    if normalized_variant == "fixed_stage_binary_tree":
        # Keep old indexed behavior for compatibility with existing tests.
        if index is None or index < len(FIXED_STAGE_BINARY_TREE_PARAM_SETS):
            labels, stages = _pick_indexed(FIXED_STAGE_BINARY_TREE_PARAM_SETS, seed=seed, index=index)
            expected_paths = _binary_paths(labels, stages)
            scenario_id = "fixed_stage_binary_tree_legacy"
            scenario_family = "binary_fixed_stage_legacy"
            branch_counts = [len(labels)] * stages
            parameter_signature = f"legacy_fixed_stage:labels={'-'.join(labels)},stages={stages}"
            outcome_set_signature = f"{labels[0]}_{labels[1]}"
            context_signature = "legacy_fixed_stage_binary"
            question_text = _fixed_stage_question_text(labels, stages)
        else:
            scenario = TREE_DIAGRAM_DIVERSITY_SCENARIOS[index % len(TREE_DIAGRAM_DIVERSITY_SCENARIOS)]
            stage_options = [list(s) for s in scenario.get("stage_options", [])]
            expected_paths = _enumerate_stage_paths(stage_options)
            stages = len(stage_options)
            labels = stage_options[0] if stage_options else []
            scenario_id = str(scenario.get("scenario_id", "tree_diagram_scenario"))
            scenario_family = str(scenario.get("scenario_family", "tree_diagram_counting"))
            outcome_set_signature = str(scenario.get("outcome_set_signature", ""))
            context_signature = str(scenario.get("context_signature", ""))
            branch_counts = [len(s) for s in stage_options]
            parameter_signature = (
                f"tree:{scenario_id}:depth={stages}:branches={','.join(str(v) for v in branch_counts)}:"
                f"context={context_signature}:outcomes={outcome_set_signature}"
            )
            question_text = str(scenario.get("question_text", "請用樹狀圖或完整列舉方式寫出所有可能情形。"))
        return {
            "problem_type_id": PROBLEM_TYPE_ID,
            "grading_mode": GRADING_MODE,
            "variant": normalized_variant,
            "question_text": question_text,
            "expected_count": len(expected_paths),
            "expected_paths": expected_paths,
            "path_labels": labels,
            "stages": stages,
            "scenario_family": scenario_family,
            "scenario_id": scenario_id,
            "parameter_signature": parameter_signature,
            "outcome_set_signature": outcome_set_signature,
            "tree_depth": stages,
            "branch_counts": branch_counts,
            "context_signature": context_signature,
            "expected_answer_schema": {
                "type": "tree_or_listing",
                "expected_count": len(expected_paths),
                "tree_depth": stages,
                "branch_counts": branch_counts,
            },
            "rubric": [
                "是否列出所有可能情形",
                "是否沒有重複或遺漏",
                "是否分支層次合理",
                "若題目要求總數，是否給出正確總數",
            ],
            "textbook_alignment_note": "維持樹狀圖/完整列舉課本骨架，透過情境與參數做可控變化。",
            "accept_text_listing": True,
            "accept_handwriting_tree": False,
            "requires_listing_or_tree": True,
        }
    if normalized_variant == "early_stopping_game":
        labels = _pick_indexed(EARLY_STOPPING_GAME_LABEL_SETS, seed=seed, index=index)
        expected_paths = _early_stopping_paths(labels)
        # 移除壞掉的亂碼判斷
        scenario_id = "win_two_games_best_of_three_ab_teams"
        return {
            "problem_type_id": PROBLEM_TYPE_ID,
            "grading_mode": GRADING_MODE,
            "variant": normalized_variant,
            "question_text": _early_stopping_question_text(labels),
            "expected_count": len(expected_paths),
            "expected_paths": expected_paths,
            "path_labels": labels,
            "stopping_rule": "first_to_2_wins",
            "scenario_family": "best_of_three_binary_match",
            "scenario_id": scenario_id,
            "parameter_signature": f"best_of_three:labels={'-'.join(labels)}",
            "outcome_set_signature": "two_teams",
            "tree_depth": 3,
            "branch_counts": [2, 2, 2],
            "context_signature": "sports_match",
            "expected_answer_schema": {
                "type": "tree_or_listing",
                "expected_count": len(expected_paths),
                "tree_depth": 3,
                "branch_counts": [2, 2, 2],
                "stopping_rule": "first_to_2_wins",
            },
            "rubric": [
                "是否列出所有可能情形",
                "是否沒有重複或遺漏",
                "是否分支層次合理",
                "是否正確處理先贏兩場即停止",
            ],
            "textbook_alignment_note": "維持先贏兩場的樹狀圖列舉骨架，不以隊伍名稱替換當作有效多樣性。",
            "accept_text_listing": True,
            "accept_handwriting_tree": False,
            "requires_listing_or_tree": True,
        }
    raise ValueError(f"Unsupported tree diagram variant: {variant}")


def _normalize_digits(text: str) -> str:
    table = str.maketrans("０１２３４５６７８９", "0123456789")
    return text.translate(table)


def _extract_count_mentions(text: str) -> list[int]:
    normalized = _normalize_digits(text)
    return [int(match) for match in re.findall(r"\d+", normalized)]


def parse_tree_diagram_text_answer(answer_text: str, path_labels: list[str]) -> dict[str, Any]:
    text = str(answer_text or "")
    labels = [str(label) for label in path_labels if str(label)]
    label_set = set(labels)
    raw_count_mentions = _extract_count_mentions(text)
    if not text.strip() or not labels:
        return {
            "detected_paths": [],
            "duplicated_paths": [],
            "count_only_answer": bool(raw_count_mentions),
            "raw_count_mentions": raw_count_mentions,
        }

    chunks: list[str] = []
    current: list[str] = []
    for char in text:
        if char in label_set:
            current.append(char)
        else:
            if current:
                chunks.append("".join(current))
                current = []
    if current:
        chunks.append("".join(current))

    paths: list[str] = []
    for chunk in chunks:
        if len(chunk) in {2, 3}:
            paths.append(chunk)
        elif len(chunk) > 3:
            # Fallback for answers pasted without separators. Keep non-overlapping triples
            # because current supported variants only use binary labels and length 2/3 paths.
            step = 3
            for idx in range(0, len(chunk), step):
                candidate = chunk[idx : idx + step]
                if len(candidate) in {2, 3}:
                    paths.append(candidate)

    counts = Counter(paths)
    detected_paths = list(dict.fromkeys(paths))
    duplicated_paths = [path for path, count in counts.items() if count > 1]
    return {
        "detected_paths": detected_paths,
        "duplicated_paths": duplicated_paths,
        "count_only_answer": bool(raw_count_mentions and not detected_paths),
        "raw_count_mentions": raw_count_mentions,
    }


def _ordered_difference(left: list[str], right: set[str]) -> list[str]:
    return [item for item in left if item not in right]


def _confidence_for(status: str, score: float, *, has_paths: bool) -> float:
    if status == "correct":
        return 0.98
    if status == "needs_review":
        return 0.25
    if has_paths:
        return max(0.55, min(0.9, 0.55 + score * 0.35))
    return 0.65


def judge_tree_diagram_text_answer(payload: dict[str, Any], answer_text: str) -> dict[str, Any]:
    expected_paths = [str(path) for path in (payload.get("expected_paths") or []) if str(path)]
    expected_set = set(expected_paths)
    expected_count = int(payload.get("expected_count") or len(expected_paths))
    variant = str(payload.get("variant") or "").strip()
    parsed = parse_tree_diagram_text_answer(answer_text, list(payload.get("path_labels") or []))
    detected_paths = list(parsed.get("detected_paths") or [])
    detected_set = set(detected_paths)
    duplicated_paths = list(parsed.get("duplicated_paths") or [])
    missing_paths = _ordered_difference(expected_paths, detected_set)
    extra_paths = _ordered_difference(detected_paths, expected_set)
    matched_expected_count = len(expected_set & detected_set)
    count_only_answer = bool(parsed.get("count_only_answer", False))

    status = "needs_review"
    main_issue = ""
    feedback = ""
    score = 0.0

    if not str(answer_text or "").strip():
        status = "needs_review"
        main_issue = "答案空白，無法判斷是否完成列舉。"
        feedback = "請用文字列出所有可能情形；本階段尚未處理手寫或圖片答案。"
    elif count_only_answer:
        status = "partial"
        score = 0.4 if expected_count in set(parsed.get("raw_count_mentions") or []) else 0.25
        main_issue = "只寫總數，未用樹狀圖或完整列舉。"
        feedback = "你寫出了總數，但題目要求用樹狀圖或完整列舉描述所有情形，因此還需要列出每一種可能結果。"
    elif not detected_paths:
        status = "needs_review"
        main_issue = "無法從文字中可靠解析出路徑。"
        feedback = "請用頓號、逗號或換行列出每一種可能情形。"
    else:
        score = matched_expected_count / expected_count if expected_count else 0.0
        labels = [str(label) for label in (payload.get("path_labels") or []) if str(label)]
        early_stop_overrun_paths = {
            path
            for path in detected_paths
            if variant == "early_stopping_game"
            and len(labels) == 2
            and len(path) == 3
            and (path.startswith(labels[0] * 2) or path.startswith(labels[1] * 2))
        }
        fixed_three_error = bool(early_stop_overrun_paths)
        if fixed_three_error:
            status = "incorrect" if score < 0.75 else "partial"
            main_issue = "未理解「先贏兩場即停止」，列出了不應繼續比賽的路徑。"
            examples = "、".join(list(early_stop_overrun_paths)[:2])
            feedback = f"你似乎把比賽固定列成三場，但題目規定先贏兩場就結束，因此像{examples}這類路徑不應列入。"
        elif not missing_paths and not extra_paths:
            status = "correct"
            score = 1.0
            main_issue = "列舉完整。"
            feedback = "列舉完整，且符合題目規則。"
            if duplicated_paths:
                status = "partial"
                score = 0.9
                main_issue = "列舉完整但有重複項。"
                feedback = f"你的主要列舉完整，但重複列出了：{'、'.join(duplicated_paths)}。"
        elif matched_expected_count > 0 and matched_expected_count >= len(extra_paths):
            status = "partial"
            score = max(0.1, min(0.95, score))
            if missing_paths:
                main_issue = f"列舉不完整，少了：{'、'.join(missing_paths)}。"
                if variant == "early_stopping_game":
                    feedback = f"你的列舉方向正確，但少了：{'、'.join(missing_paths)}。請檢查前兩場一勝一敗時，第三場仍可能由任一隊獲勝。"
                else:
                    feedback = f"你的列舉方向正確，但少了：{'、'.join(missing_paths)}。請逐層檢查每次正、反兩種分支。"
            else:
                main_issue = "有額外或重複路徑。"
                feedback = "你的主要方向接近正確，但出現額外或重複的路徑，請重新檢查每一條終止路徑。"
        else:
            status = "incorrect"
            score = min(score, 0.45)
            main_issue = "列舉路徑多數不符合題目規則。"
            feedback = "目前列出的路徑與題目規則差距較大，請先確認每一階段可能結果與停止條件。"

    score = round(float(max(0.0, min(1.0, score))), 3)
    return {
        "status": status,
        "score": score,
        "expected_count": expected_count,
        "detected_count": len(detected_paths),
        "expected_paths": expected_paths,
        "detected_paths": detected_paths,
        "missing_paths": missing_paths,
        "extra_paths": extra_paths,
        "duplicated_paths": duplicated_paths,
        "count_only_answer": count_only_answer,
        "main_issue": main_issue,
        "feedback": feedback,
        "teacher_review_needed": status == "needs_review",
        "confidence": _confidence_for(status, score, has_paths=bool(detected_paths)),
    }
