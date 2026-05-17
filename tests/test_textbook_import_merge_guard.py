from core.textbook_processor import (
    _is_low_value_import_field,
    score_problem_text_quality,
    should_replace_problem_text,
)


def test_existing_latex_beats_incoming_placeholder():
    existing = "試求 \\(|x|<3\\)"
    incoming = "[FORMULA_IMAGE_1] < 3"
    replace, existing_q, incoming_q = should_replace_problem_text(existing, incoming)
    assert replace is False
    assert existing_q["score"] > incoming_q["score"]


def test_incoming_latex_beats_existing_placeholder():
    existing = "[FORMULA_IMAGE_1] < 3"
    incoming = "試求 \\(|x|<3\\)"
    replace, existing_q, incoming_q = should_replace_problem_text(existing, incoming)
    assert replace is True
    assert incoming_q["score"] > existing_q["score"]


def test_formula_asset_metadata_can_merge_without_problem_text_replacement():
    existing = "試求 \\(|x|<3\\)"
    incoming = "[FORMULA_IMAGE_1] < 3"
    replace, _, _ = should_replace_problem_text(existing, incoming)
    incoming_notes = {"formula_assets": [{"placeholder_token": "[FORMULA_IMAGE_1]"}]}
    assert replace is False
    assert incoming_notes["formula_assets"]


def test_blank_or_ellipsis_answer_is_low_value():
    assert _is_low_value_import_field("")
    assert _is_low_value_import_field("略")
    assert not _is_low_value_import_field("\\(x=1\\)")


def test_placeholder_only_scores_low():
    q = score_problem_text_quality("[FORMULA_MISSING]")
    assert q["only_placeholder"] is True
    assert q["score"] < 0
