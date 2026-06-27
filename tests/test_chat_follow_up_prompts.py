# -*- coding: utf-8 -*-
"""Unit tests for /chat_ai follow-up prompt normalization."""

from core.ai_analyzer import (
    build_generic_follow_up_fallback,
    diversify_follow_up_prompts,
    normalize_follow_up_prompts,
)


def _assert_valid_prompts(prompts, user_question=""):
    assert isinstance(prompts, list)
    assert len(prompts) == 3
    joined = " ".join(prompts)
    assert "【觀察】" not in joined
    assert "【聯想】" not in joined
    assert "【執行】" not in joined
    assert "問題1 (" not in joined
    assert "是否成立" not in joined
    assert "驗算「" not in joined
    for p in prompts:
        assert p.strip()
        assert p.strip().lower() != user_question.strip().lower()


def test_normalize_accepts_llm_prompts():
    user_q = "這題怎麼開始？"
    llm = [
        "為什麼要先確認母體和樣本？",
        "題目說的抽樣方式是指哪一種？",
        "如果把樣本當成母體會怎樣？",
    ]
    out = normalize_follow_up_prompts(llm, user_question=user_q)
    _assert_valid_prompts(out, user_question=user_q)
    assert out == llm


def test_normalize_rejects_legacy_templates():
    legacy = [
        "問題1 (【觀察】：先看「這題」，哪個條件最容易被忽略？)",
        "問題2 (【聯想】：這題和哪個公式或性質最直接相關？為什麼？)",
        "問題3 (【執行】：請用 1 步驗算「這題」是否成立。)",
    ]
    out = normalize_follow_up_prompts(legacy, user_question="這題怎麼算？")
    assert out == build_generic_follow_up_fallback()


def test_normalize_filters_duplicate_user_question():
    user_q = "為什麼要用四分位數？"
    llm = [
        user_q,
        "排序後中間那兩個數要怎麼看？",
        "全距和四分位距差在哪？",
    ]
    out = normalize_follow_up_prompts(llm, user_question=user_q)
    assert len(out) == 3
    assert user_q not in out


def test_diversify_uses_generic_when_same_as_last_turn():
    llm = [
        "為什麼兩個累積次數要相減？",
        "圖上 60 分對應的是哪個累積次數？",
        "把以上累積當成以下累積會錯在哪？",
    ]
    first = diversify_follow_up_prompts(llm, [], user_question="怎麼讀圖？", turn_index=0)
    second = diversify_follow_up_prompts(llm, first, user_question="怎麼讀圖？", turn_index=1)
    assert second == build_generic_follow_up_fallback(variant=2)
    _assert_valid_prompts(second)


def test_sampling_question_scenario():
    """抽樣題：追問應涉及母體、樣本及抽樣方式。"""
    llm = [
        "為什麼調查時不能只看樣本就當成全部？",
        "題目裡的母體和樣本分別指哪些對象？",
        "把便利抽樣當成隨機抽樣會有什麼問題？",
    ]
    out = normalize_follow_up_prompts(
        llm,
        user_question="這題的母體是什麼？",
        question_context="某校調查 200 名學生的通勤方式，全校共 1200 人。",
    )
    _assert_valid_prompts(out, user_question="這題的母體是什麼？")
    text = " ".join(out)
    assert any(k in text for k in ("母體", "樣本", "抽樣"))


def test_cumulative_frequency_scenario():
    """累積次數圖：追問應涉及兩個累積次數相減及圖表讀值。"""
    llm = [
        "為什麼要用兩個累積次數相減？",
        "圖上 50 分到 60 分這段該讀哪兩個點？",
        "把以上累積次數當成以下累積次數會算錯什麼？",
    ]
    out = normalize_follow_up_prompts(
        llm,
        user_question="60 分有多少人？",
        question_context="以下為數學成績的累積次數折線圖。",
    )
    _assert_valid_prompts(out, user_question="60 分有多少人？")
    text = " ".join(out)
    assert any(k in text for k in ("累積", "相減", "圖"))


def test_range_iqr_scenario():
    """全距與四分位距：追問應涉及排序、全距及四分位數位置。"""
    llm = [
        "為什麼算四分位距前要先排序？",
        "Q1 和 Q3 在 9 個數據裡各在哪個位置？",
        "把全距和四分位距混用會怎樣？",
    ]
    out = normalize_follow_up_prompts(
        llm,
        user_question="這組數據的全距是多少？",
        question_context="數據：12, 15, 18, 20, 22, 25, 28, 30, 35",
    )
    _assert_valid_prompts(out, user_question="這組數據的全距是多少？")
    text = " ".join(out)
    assert any(k in text for k in ("排序", "全距", "四分位"))
