# -*- coding: utf-8 -*-
"""Answer-format example suffix is omitted only when the stem already states a
format that structurally covers it; everything uncertain keeps the original."""
from __future__ import annotations

import importlib

from core.gencode.answer_format_hint import (
    QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE,
    build_answer_format_suffix_for_stem,
    stem_states_answer_format,
)
from core.gencode.scenario_pool_manager import append_answer_format_suffix
from core.gencode.slot_generators import _reinforce_slot_question_text

TRANSLATION_STEM = "相較於 $y=3x^2$，拋物線 $y=3(x+2)^2+4$ 如何平移？請用「向左 2、向上 3」的格式作答。"
TEXT_SHORT_AC = {"answer_type": "text_short", "checker": "text_short_checker", "checker_key": "text_short_checker"}
INTEGER_AC = {"answer_type": "integer", "checker": "integer_checker", "checker_key": "integer_checker"}


def _finalize(stem: str, ac: dict) -> dict:
    payload = {"question_text": stem, "question": stem, "choices": [], "answer_contract": dict(ac)}
    return append_answer_format_suffix(payload, {"answer_contract": dict(ac)})


def test_translation_stem_with_stated_format_drops_duplicate_example() -> None:
    out = _finalize(TRANSLATION_STEM, TEXT_SHORT_AC)
    assert out["question_text"] == TRANSLATION_STEM
    assert out["question"] == TRANSLATION_STEM
    assert "答案範例" not in out["question_text"]
    assert out["metadata"]["answer_format_suffix_suppressed"] == "stem_states_answer_format"
    assert out["answer_contract"] == TEXT_SHORT_AC


def test_vertex_form_template_in_stem_covers_vertex_example() -> None:
    assert stem_states_answer_format("請用配方法，將 $y=-x^2+2x+3$ 改寫為 $a(x+m)^2+n$／頂點式。", "$2(x-2)^2+3$")
    assert stem_states_answer_format("把二次式 $y=x^2+6x+13$ 化成頂點式 $a(x-h)^2+k$。", "$2(x-2)^2+3$")


def test_uncertain_cases_keep_example() -> None:
    # Bare numeric examples never count as covered by a stated word format.
    assert not stem_states_answer_format(TRANSLATION_STEM, "5")
    # Structure mismatch: factorization example vs vertex-form template.
    assert not stem_states_answer_format("將 $x^2+x-6$ 改寫為 $a(x+m)^2+n$。", "(x-2)(x+3)")
    # No explicit format statement in the stem.
    assert not stem_states_answer_format("求 $p+q$ 的值。", "-3/4")
    assert not stem_states_answer_format("解不等式 $x^2-2x-3<0$。", QUADRATIC_INEQUALITY_UNIFIED_HINT_EXAMPLE)
    # Solving with a method is not an answer format.
    assert not stem_states_answer_format("請用配方法求頂點。", "$2(x-2)^2+3$")


def test_kept_example_joins_stem_without_extra_line() -> None:
    stem = "已知二次函數 $y=x^2+px+q$ 的圖形最低點為 $(2,-1)$，求 $p+q$ 的值。"
    out = _finalize(stem, INTEGER_AC)
    assert out["question_text"] == stem + "（答案範例：5）"
    assert "\n" not in out["question_text"]
    assert "answer_format_suffix_suppressed" not in out["metadata"]


def test_math_constraints_are_never_touched() -> None:
    stem = "放出 $120$ 公尺長的線，仰角為 $65^\\circ$，試求高度（四捨五入到小數點後第 3 位）。"
    out = _finalize(stem, INTEGER_AC)
    assert out["question_text"].startswith(stem)
    assert "四捨五入到小數點後第 3 位" in out["question_text"]


def test_linear_equation_hint_unchanged() -> None:
    ac = {"answer_type": "equation", "answer_shape": "linear_equation",
          "checker": "linear_equation_equivalent_checker"}
    suffix, reason = build_answer_format_suffix_for_stem(ac, "求過點 $(1,2)$ 且斜率為 $3$ 的直線方程式。")
    assert suffix.startswith("（") and "例如" in suffix
    assert reason == ""


def test_short_stem_gets_no_generic_padding_sentence() -> None:
    spec = {"semantic_contract": {"required_concepts": ["十字交乘法"]}}
    stem = "利用十字交乘法分解：$x^2+5x+6$"
    out = _reinforce_slot_question_text({"question_text": stem}, spec)
    assert out["question_text"] == stem
    missing = _reinforce_slot_question_text({"question_text": "分解 $x^2+5x+6$"}, spec)
    assert missing["question_text"] == "分解 $x^2+5x+6$ 解題時請運用十字交乘法。"


def test_runtime_translation_questions_are_single_paragraph_and_gradable() -> None:
    mod = importlib.import_module("skills.vh_數學B1_QuadraticFunctionGraph")
    seen = 0
    for seed in range(60):
        q = mod.generate(level=1, seed=seed)
        if "translation_fill_blank" not in str(q.get("problem_type_id") or ""):
            continue
        seen += 1
        qt = str(q.get("question_text") or "")
        assert "的格式作答" in qt
        assert "答案範例" not in qt
        assert "\n" not in qt
        ans = q.get("correct_answer") or q.get("answer")
        assert bool(mod.check(ans, ans, question_payload=q)) is True
    assert seen >= 2
