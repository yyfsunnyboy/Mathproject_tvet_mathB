"""Shared final-answer disclosure guard: symbolic equivalence across question types."""

from __future__ import annotations

import pytest

from core.ai_tutor_disclosure import REDACTION_TEXT, find_answer_disclosure, redact_answer_disclosure
from core.ai_tutor_pedagogy import (
    enforce_teaching_round_disclosure,
    full_solution_allowed,
    teaching_round_block,
    tutor_intent_block,
)


@pytest.mark.parametrize("answer,reply", [
    # line equation: rearranged / scaled forms
    ("y=\\frac{2}{3}x-5", "整理後得到 $3y=2x-15$。"),
    ("y=\\frac{2}{3}x-5", "所以 $y=\\frac{2x}{3}-5$。"),
    ("y=\\frac{2}{3}x-5", "移項得 $2x-3y-15=0$。"),
    # numeric solution
    ("x=4", "所以 $x=4$。"),
    ("x=4", "答案是 4。"),
    # inequality, including flipped direction
    ("x \\ge 3", "所以 $x \\ge 3$。"),
    ("x \\ge 3", "所以 $3 \\le x$。"),
    # multi-part answers need every part
    ("x=4 或 x=10", "所以 x=4 或 x=10。"),
    # coordinate
    ("(1,7)", "中點是 $P(1,7)$。"),
    # choice
    ("C", "答案是 (C)。"),
    # probability fraction, reduced or not
    ("\\frac{1}{2}", "機率 $P=\\frac{3}{6}$。"),
    # polynomial expression
    ("x^2+5x+6", "展開後得 $x^2+5x+6$。"),
    # radical value
    ("5\\sqrt{2}", "$OP=\\sqrt{50}=5\\sqrt{2}$。"),
])
def test_equivalent_final_answers_are_detected(answer, reply):
    finding = find_answer_disclosure(reply, answer)
    assert finding.disclosed, (answer, reply)
    redacted = redact_answer_disclosure(reply, finding)
    assert REDACTION_TEXT in redacted or " ?" in redacted


@pytest.mark.parametrize("answer,reply", [
    # general formulas and partial substitution are teaching, not disclosure
    ("y=\\frac{2}{3}x-5", "斜截式是 $y=mx+b$，$m$ 是斜率、$b$ 是 y 截距。"),
    ("y=\\frac{2}{3}x-5", "把斜率代入得 $y=\\frac{2}{3}x+b$，再想想 $b$ 是多少。"),
    ("5\\sqrt{2}", "代入距離公式 $OP=\\sqrt{1^2+7^2}$，先算根號裡面。"),
    ("x=4", "兩邊同減 3 得 $2x=8$，下一步兩邊同除以 2。"),
    # only one part of a two-part answer
    ("x=4 或 x=10", "其中一個解是 x=4，另一個請你自己算。"),
    # wrong inequality direction
    ("x \\ge 3", "注意不是 $x \\le 3$。"),
    # bare number without an answer marker
    ("x=4", "第 4 行的移項要再看一次。"),
    ("C", "先比較選項 A 與 B 的差別。"),
])
def test_formulas_and_partial_steps_are_not_disclosure(answer, reply):
    assert not find_answer_disclosure(reply, answer).disclosed, (answer, reply)


def test_students_own_correct_answer_may_be_affirmed():
    reply = "你的 $y=\\frac{2}{3}x-5$ 正確，這就是答案。"
    assert find_answer_disclosure(reply, "y=\\frac{2}{3}x-5").disclosed
    assert not find_answer_disclosure(reply, "y=\\frac{2}{3}x-5", student_work="3y = 2x - 15").disclosed


def test_sequence_rubric_detects_full_row_only():
    items = ["1", "4", "6", "4", "1"]
    assert find_answer_disclosure("第 4 列是 1, 4, 6, 4, 1。", "", answer_items=items).disclosed
    assert not find_answer_disclosure("第 4 列開頭是 1, 4, 6。", "", answer_items=items).disclosed


def test_redaction_keeps_the_teaching_text():
    reply = "先把 $-5$ 移到右邊。\n所以 $y=\\frac{2}{3}x-5$。"
    finding = find_answer_disclosure(reply, "y=\\frac{2}{3}x-5")
    redacted = redact_answer_disclosure(reply, finding)
    assert "先把 $-5$ 移到右邊" in redacted
    assert "\\frac{2}{3}x-5" not in redacted


def test_unparseable_proof_answers_are_only_literal():
    # Capability boundary: paraphrased proofs are left to the prompt-level policy.
    assert find_answer_disclosure("所以△ABC≅△DEF", "△ABC≅△DEF").disclosed
    assert not find_answer_disclosure("用 SAS 可以說明兩個三角形的關係", "△ABC≅△DEF").disclosed


# --- teaching-round policy -------------------------------------------------

def test_full_solution_only_from_round_three_on_request():
    assert not full_solution_allowed(1, "full_solution")
    assert not full_solution_allowed(2, "full_solution")
    assert full_solution_allowed(3, "full_solution")
    assert full_solution_allowed(5, "full_solution")
    assert not full_solution_allowed(3, "next_step")


def test_round_block_states_round_and_disclosure():
    first = teaching_round_block(1, "check_work")
    assert "第 1 輪" in first and "不允許" in first
    early = tutor_intent_block("直接告訴我答案", 2)
    assert "第 2 輪" in early and "完整解答從第 3 輪起才提供" in early
    assert "依步驟寫出完整解答" not in early
    late = tutor_intent_block("直接告訴我答案", 3)
    assert "允許：學生已明確要求完整解答" in late


@pytest.mark.parametrize("round_no,intent,kept", [
    (1, "full_solution", False),
    (2, "full_solution", False),
    (3, "next_step", False),
    (3, "full_solution", True),
])
def test_enforcement_follows_round(round_no, intent, kept):
    reply = "整理得 $3y=2x-15$，所以 $y=\\frac{2}{3}x-5$。"
    out, redacted = enforce_teaching_round_disclosure(
        reply, correct_answer="y=\\frac{2}{3}x-5", teaching_round=round_no, intent=intent,
    )
    assert (out == reply) is kept
    assert redacted is (not kept)
