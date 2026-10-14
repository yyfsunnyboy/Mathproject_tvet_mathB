from __future__ import annotations

from core.gencode.answer_grading import (
    attach_correct_answer_feedback,
    build_correct_answer_display,
)
from pathlib import Path


def _question(answer_type: str, canonical, **extra):
    contract = {"answer_type": answer_type, "canonical_answer": canonical}
    contract.update(extra.pop("contract", {}))
    return {"skill_id": "test_skill", "answer_contract": contract, **extra}


def test_correct_submit_does_not_reveal_answer():
    result = attach_correct_answer_feedback({"correct": True}, _question("short_answer", r"\frac{1}{2}"))
    assert result["all_correct"] is True
    assert "correct_answer_display" not in result


def test_short_answer_wrong_returns_canonical_display():
    result = attach_correct_answer_feedback({"correct": False}, _question("short_answer", r"\frac{1}{2}"))
    assert result["correct_answer_display"]["value"] == r"\frac{1}{2}"


def test_single_choice_returns_label_and_semantic_option_text():
    current = _question("single_choice", r"\sin\theta=1", choices=["0", r"\sin\theta=1", "-1"])
    display = build_correct_answer_display(current)
    assert display == {"answer_type": "single_choice", "label": "B", "option_text": r"\sin\theta=1"}


def test_multi_part_and_table_fill_return_labeled_items():
    parts = [
        {"key": "a", "label": "(1)", "expected_answer": "2"},
        {"key": "b", "label": "(2)", "expected_answer": r"\pi"},
    ]
    multi = build_correct_answer_display(_question("multi_part", {"a": "2", "b": r"\pi"}, contract={"parts": parts}))
    table = build_correct_answer_display(_question("table_fill", {"a": "2", "b": r"\pi"}, contract={"parts": parts}))
    assert multi["items"] == table["items"]
    assert multi["items"][1] == {"key": "b", "label": "(2)", "value": r"\pi"}


def test_required_form_failure_has_explicit_feedback_and_canonical_format():
    current = _question(
        "short_answer",
        r"\frac{\sqrt{2}}{2}",
        contract={"required_form": "simplified_trig_value"},
    )
    result = attach_correct_answer_feedback(
        {"correct": False, "required_form_failed": True}, current
    )
    assert result["mathematically_equivalent"] is True
    assert result["required_form_valid"] is False
    assert "格式不符合要求" in result["required_form_feedback"]
    assert result["correct_answer_display"]["value"] == r"\frac{\sqrt{2}}{2}"


def test_drawing_only_exposes_existing_reference_or_rubric():
    no_reference = build_correct_answer_display(_question("drawing", None))
    with_rubric = build_correct_answer_display(
        _question("drawing", None, contract={"rubric": "端點與方向皆正確"})
    )
    assert no_reference is None
    assert with_rubric == {"answer_type": "drawing", "reference": None, "rubric": "端點與方向皆正確"}


def test_shared_frontend_renderer_wraps_raw_latex_and_typesets_mathjax():
    source = Path("static/js/correct_answer_feedback.js").read_text(encoding="utf-8")
    assert "function mathText" in source
    assert "MathJax.typesetPromise" in source
    assert "mathText(item.value)" in source
