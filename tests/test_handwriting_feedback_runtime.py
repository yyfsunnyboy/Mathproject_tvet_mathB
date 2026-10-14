from core.routes.analysis import (
    _handwriting_rule_based_reply,
    _handwriting_second_stage_compliance_flags,
)


def test_short_socratic_reply_passes_without_fixed_labels():
    reply = "你已經想到答案可能在兩邊，方向是對的。這兩個條件要同時成立，還是只要一個成立？"

    flags = _handwriting_second_stage_compliance_flags(
        reply,
        "incorrect",
        "x > 19 or x < -19",
    )

    assert flags["compliance_ok"] is True
    assert "錯誤提示" not in reply
    assert "具體下一步" not in reply


def test_complete_answer_leak_is_still_rejected_for_short_answer():
    flags = _handwriting_second_stage_compliance_flags(
        "你已經找到關鍵了。正確答案是 19，再看看題目問什麼？",
        "incorrect",
        "19",
    )

    assert flags["compliance_ok"] is False
    assert flags["gives_final_answer"] is True
    assert "gave_final_answer" in flags["reject_reasons"]


def test_authoritative_correct_reply_cannot_continue_correction():
    accepted = _handwriting_second_stage_compliance_flags("答對了，你抓到重點了！", "correct", "19")
    rejected = _handwriting_second_stage_compliance_flags("答對了，但這裡需要修正。", "correct", "19")

    assert accepted["compliance_ok"] is True
    assert rejected["compliance_ok"] is False
    assert "correct_status_continues_correction" in rejected["reject_reasons"]


def test_fallback_is_plain_language_without_internal_labels_or_error_marks():
    reply = _handwriting_rule_based_reply(
        {
            "status": "incorrect",
            "recognized_expression": "x > 19, x < -19",
            "error_mechanism": "notation_error",
            "family_label_zh": "一般題型",
        }
    )

    assert len(reply.splitlines()) <= 3
    assert reply.endswith("？")
    for forbidden in (
        "一般題型",
        "式子格式或記號不完整",
        "式子結構",
        "表示方式",
        "依題意化簡",
        "✘",
        "❌",
        "X",
    ):
        assert forbidden not in reply


def test_partially_correct_fallback_starts_with_affirmation():
    reply = _handwriting_rule_based_reply(
        {
            "status": "partially_correct",
            "recognized_expression": "2x + 3x = 6x",
            "error_mechanism": "combine_error",
        }
    )

    assert reply.splitlines()[0] == "你前面的方向是對的。"
    assert len(reply.splitlines()) == 3
