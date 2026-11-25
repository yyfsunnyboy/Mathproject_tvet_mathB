# -*- coding: utf-8 -*-
"""Handwriting AI-check must not auto-mark assisted; tutor paths still do."""

from __future__ import annotations

import inspect
from pathlib import Path

from core.practice_type_mastery import (
    clear_question_assisted,
    mark_question_assisted,
    question_was_assisted,
)
from core.routes import adaptive_api, analysis
from core.skill_card_mastery import (
    build_skill_card_mastery,
    is_known_empty_shell_skill,
)


def test_ai_check_handwriting_source_does_not_mark_assisted() -> None:
    src = inspect.getsource(adaptive_api.ai_check_handwriting)
    assert "mark_question_assisted" not in src


def test_tutor_paths_still_mark_assisted() -> None:
    # analyze_handwriting is the diagnostic path after wrong check_answer
    analyze_src = inspect.getsource(analysis.analyze_handwriting)
    assert "mark_question_assisted" in analyze_src
    # chat route source (name may vary) must keep assisted marking
    src_file = Path(analysis.__file__).read_text(encoding="utf-8")
    assert "mark_question_assisted" in src_file
    assert src_file.count("mark_question_assisted") >= 2


def test_record_type_attempt_assisted_blocks_mastered(app_ctx_isolated_db=None) -> None:
    # Lightweight session stub
    class _S(dict):
        modified = False

    sess = _S()
    uid = "q-independent-1"
    assert question_was_assisted(sess, uid) is False
    mark_question_assisted(sess, uid)
    assert question_was_assisted(sess, uid) is True
    clear_question_assisted(sess, uid)
    assert question_was_assisted(sess, uid) is False


def test_subsection332_is_known_empty_shell() -> None:
    assert is_known_empty_shell_skill("vh_數學B1_SubSection332")
    assert not is_known_empty_shell_skill("vh_數學B1_RationalEquation")


def test_subsection332_card_not_alarm_binding_and_practice_disabled() -> None:
    from app import create_app

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        cards = build_skill_card_mastery(
            student_id=None,
            skill_ids=["vh_數學B1_SubSection332", "vh_數學B1_RationalEquation"],
        )
        shell = cards["vh_數學B1_SubSection332"]
        assert shell["binding_issue"] is True
        assert shell["binding_issue_code"] == "empty_shell_no_runtime"
        assert "教材參考題綁定異常" not in str(shell.get("binding_issue_label") or "")
        assert shell.get("practice_enabled") is False
