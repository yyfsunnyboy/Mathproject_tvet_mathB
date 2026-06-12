# -*- coding: utf-8 -*-
"""
tests/gencode/test_generated_question_format_validator.py
==========================================================
全域題目格式驗證器單元測試

涵蓋：
  - 中文題幹通過 (TC-01)
  - 英文題幹失敗 localization_violation (TC-02)
  - LaTeX 未閉合 latex_unbalanced (TC-03)
  - code fence 失敗 markdown_code_fence_detected (TC-04)
  - x^2 未包 LaTeX formula_not_wrapped (TC-05)
  - x=-2 純文字通過 (TC-06)
  - choices 重複 choices_duplicate (TC-07)
  - 答案超出 choices 範圍 answer_not_in_choices (TC-08)
  - LaTeX 非法分隔符 latex_delimiter_not_allowed (TC-09)
  - 空公式 latex_empty_formula (TC-10)
  - 空 payload 不報錯 (TC-11)
  - 無 choices 的選擇題 choices_missing (TC-12)
  - $...$ 正確包裹後不誤報 formula_not_wrapped (TC-13)
  - metadata.givens.text 中的 code fence (TC-14)
"""
import pytest

from core.gencode.generated_question_format_validator import (
    validate_generated_question_format,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _run(payload: dict) -> list[str]:
    return validate_generated_question_format(payload)


def _assert_blocker(result: list[str], blocker: str) -> None:
    assert blocker in result, (
        f"Expected blocker {blocker!r} in result, got: {result}"
    )


def _assert_no_blocker(result: list[str], blocker: str) -> None:
    assert blocker not in result, (
        f"Blocker {blocker!r} should NOT appear in result, got: {result}"
    )


def _assert_clean(result: list[str]) -> None:
    assert result == [], f"Expected no blockers, got: {result}"


# ─────────────────────────────────────────────────────────────────────────────
# TC-01: 中文題幹，LaTeX 正確包裹 → 全通過
# ─────────────────────────────────────────────────────────────────────────────

def test_tc01_chinese_question_passes():
    """正常繁體中文題幹，公式已包裹，不應有任何 blocker。"""
    payload = {
        "question_text": "已知 $y=x^2+1$，求 x=2 時的 y 值。",
        "answer": "5",
        "answer_type": "short_answer",
        "choices": [],
        "explanation": "將 x=2 代入 $y=x^2+1$，得 $y=4+1=5$。",
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    _assert_clean(_run(payload))


# ─────────────────────────────────────────────────────────────────────────────
# TC-02: 英文題幹 → localization_violation
# ─────────────────────────────────────────────────────────────────────────────

def test_tc02_english_question_localization_violation():
    """整句英文題幹應觸發 localization_violation。"""
    payload = {
        "question_text": "Given y=x^2+1, find the value of y when x=2.",
        "answer": "5",
        "answer_type": "short_answer",
        "choices": [],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_blocker(result, "localization_violation")


# ─────────────────────────────────────────────────────────────────────────────
# TC-03: LaTeX 未閉合 → latex_unbalanced
# ─────────────────────────────────────────────────────────────────────────────

def test_tc03_latex_unbalanced():
    """$...$ 未閉合（奇數個 $）應觸發 latex_unbalanced。"""
    payload = {
        "question_text": "已知 $y=x^2+1，求 x=2 時的 y 值。",
        "answer": "5",
        "answer_type": "short_answer",
        "choices": [],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_blocker(result, "latex_unbalanced")


# ─────────────────────────────────────────────────────────────────────────────
# TC-04: Markdown code fence → markdown_code_fence_detected
# ─────────────────────────────────────────────────────────────────────────────

def test_tc04_code_fence_detected():
    """含有 ```python 的 question_text 應觸發 markdown_code_fence_detected。"""
    payload = {
        "question_text": "請參考以下程式碼：\n```python\ny = x**2 + 1\n```\n求 x=2 時的 y 值。",
        "answer": "5",
        "answer_type": "short_answer",
        "choices": [],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_blocker(result, "markdown_code_fence_detected")


# ─────────────────────────────────────────────────────────────────────────────
# TC-05: x^2 未包 LaTeX → formula_not_wrapped
# ─────────────────────────────────────────────────────────────────────────────

def test_tc05_formula_not_wrapped():
    """question_text 中的 x^2 未在 $...$ 內，應觸發 formula_not_wrapped。"""
    payload = {
        "question_text": "已知 y=x^2+1，求 x=2 時的 y 值。",
        "answer": "5",
        "answer_type": "short_answer",
        "choices": [],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_blocker(result, "formula_not_wrapped")


# ─────────────────────────────────────────────────────────────────────────────
# TC-06: x=-2 純文字 → 不觸發 formula_not_wrapped
# ─────────────────────────────────────────────────────────────────────────────

def test_tc06_simple_assignment_passes():
    """若 x=-2 純文字，不應觸發 formula_not_wrapped。"""
    payload = {
        "question_text": "若 x=-2，求 x+3 的值。",
        "answer": "1",
        "answer_type": "short_answer",
        "choices": [],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_no_blocker(result, "formula_not_wrapped")
    _assert_no_blocker(result, "localization_violation")
    _assert_no_blocker(result, "latex_unbalanced")


# ─────────────────────────────────────────────────────────────────────────────
# TC-07: choices 重複 → choices_duplicate
# ─────────────────────────────────────────────────────────────────────────────

def test_tc07_choices_duplicate():
    """choices 有重複文字應觸發 choices_duplicate。"""
    payload = {
        "question_text": "計算 $2+3$ 的值。",
        "answer": "A",
        "answer_type": "single_choice",
        "choices": ["1", "1", "2", "3"],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_blocker(result, "choices_duplicate")


# ─────────────────────────────────────────────────────────────────────────────
# TC-08: 答案標籤超出 choices 範圍 → answer_not_in_choices
# ─────────────────────────────────────────────────────────────────────────────

def test_tc08_answer_not_in_choices():
    """answer = 'E'，但 choices 只有 4 項（A-D），應觸發 answer_not_in_choices。"""
    payload = {
        "question_text": "下列哪個選項正確？",
        "answer": "E",
        "answer_type": "single_choice",
        "choices": ["甲", "乙", "丙", "丁"],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_blocker(result, "answer_not_in_choices")


# ─────────────────────────────────────────────────────────────────────────────
# TC-09: \( \) 非法 LaTeX 分隔符 → latex_delimiter_not_allowed
# ─────────────────────────────────────────────────────────────────────────────

def test_tc09_bad_latex_delimiter():
    r"""使用 \( \) 而非 $...$ 應觸發 latex_delimiter_not_allowed。"""
    payload = {
        "question_text": r"已知 \(y=x^2+1\)，求 x=2 時的 y 值。",
        "answer": "5",
        "answer_type": "short_answer",
        "choices": [],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_blocker(result, "latex_delimiter_not_allowed")


# ─────────────────────────────────────────────────────────────────────────────
# TC-10: 空公式 $  $ → latex_empty_formula
# ─────────────────────────────────────────────────────────────────────────────

def test_tc10_empty_latex_formula():
    """出現 $ <空白> $ 應觸發 latex_empty_formula。"""
    payload = {
        "question_text": "若 $  $ 代入公式，求解。",
        "answer": "0",
        "answer_type": "short_answer",
        "choices": [],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_blocker(result, "latex_empty_formula")


# ─────────────────────────────────────────────────────────────────────────────
# TC-11: 空 payload → 回傳空 list，不丟 exception
# ─────────────────────────────────────────────────────────────────────────────

def test_tc11_empty_payload_no_exception():
    """空 payload 應回傳空 list，不丟任何 exception。"""
    assert validate_generated_question_format({}) == []
    assert validate_generated_question_format(None) == []  # type: ignore[arg-type]


# ─────────────────────────────────────────────────────────────────────────────
# TC-12: 選擇題但 choices 為空 → choices_missing
# ─────────────────────────────────────────────────────────────────────────────

def test_tc12_choices_missing():
    """answer_type=single_choice 但 choices 為空應觸發 choices_missing。"""
    payload = {
        "question_text": "下列何者正確？",
        "answer": "A",
        "answer_type": "single_choice",
        "choices": [],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_blocker(result, "choices_missing")


# ─────────────────────────────────────────────────────────────────────────────
# TC-13: 公式已正確包裹 $...$ → 不誤報 formula_not_wrapped
# ─────────────────────────────────────────────────────────────────────────────

def test_tc13_formula_properly_wrapped_no_false_positive():
    """$y=x^2+4x+3$ 已包裹，不應觸發 formula_not_wrapped。"""
    payload = {
        "question_text": "求二次函數 $y=x^2+4x+3$ 的頂點坐標。",
        "answer": "(-2, -1)",
        "answer_type": "short_answer",
        "choices": [],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_no_blocker(result, "formula_not_wrapped")
    _assert_no_blocker(result, "latex_unbalanced")


# ─────────────────────────────────────────────────────────────────────────────
# TC-14: metadata.givens[].text 含 code fence → markdown_code_fence_detected
# ─────────────────────────────────────────────────────────────────────────────

def test_tc14_code_fence_in_metadata_givens():
    """code fence 藏在 metadata.givens[].text 也應被偵測到。"""
    payload = {
        "question_text": "根據以下條件求解。",
        "answer": "5",
        "answer_type": "short_answer",
        "choices": [],
        "metadata": {
            "givens": [
                {"type": "expr", "text": "```\ny = x^2\n```"},
            ],
            "target": {},
            "derivation": [],
        },
    }
    result = _run(payload)
    _assert_blocker(result, "markdown_code_fence_detected")


# ─────────────────────────────────────────────────────────────────────────────
# TC-15: \frac 出現在 $...$ 外 → formula_not_wrapped
# ─────────────────────────────────────────────────────────────────────────────

def test_tc15_frac_outside_latex():
    r"""\\frac 出現在 $...$ 外應觸發 formula_not_wrapped。"""
    payload = {
        "question_text": r"計算 \frac{1}{2} + \frac{1}{3} 的值。",
        "answer": "5/6",
        "answer_type": "short_answer",
        "choices": [],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_blocker(result, "formula_not_wrapped")


# ─────────────────────────────────────────────────────────────────────────────
# TC-16: answer_type 在 problem_type_id 中隱含選擇題 → 也做 choices 結構檢查
# ─────────────────────────────────────────────────────────────────────────────

def test_tc16_choice_type_inferred_from_problem_type_id():
    """即使 answer_type 未設，problem_type_id 以 single_choice_ 開頭也應做 choices 檢查。"""
    payload = {
        "question_text": "下列何者正確？",
        "answer": "A",
        "answer_type": "",
        "problem_type_id": "single_choice_quadrant_classification",
        "choices": [],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_blocker(result, "choices_missing")


# ─────────────────────────────────────────────────────────────────────────────
# TC-17: choices 全為 A/B/C/D 標籤純文字，答案 B 在範圍內 → 全通過
# ─────────────────────────────────────────────────────────────────────────────

def test_tc17_valid_choice_answer_in_range():
    """answer='B'，choices 有 4 項，不應觸發 answer_not_in_choices。"""
    payload = {
        "question_text": "若 $x=2$，則 $x^2$ 等於多少？",
        "answer": "B",
        "answer_type": "single_choice",
        "choices": ["1", "4", "6", "8"],
        "metadata": {"givens": [], "target": {}, "derivation": []},
    }
    result = _run(payload)
    _assert_no_blocker(result, "answer_not_in_choices")
    _assert_no_blocker(result, "choices_missing")
    _assert_no_blocker(result, "choices_duplicate")
