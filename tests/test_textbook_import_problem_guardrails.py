from core.textbook_processor import (
    _is_question_start_text,
    build_docx_question_formula_context,
    classify_practice_source_bucket,
    classify_non_question_block,
    normalize_fill_blank_artifacts,
    normalize_permutation_combination_notation,
    repair_missing_single_variable_text,
    segment_question_block_text,
    validate_problem_block_purity,
)


def test_summary_bucket_basic_and_advanced_count_as_chapter_exercise():
    assert classify_practice_source_bucket("basic_exercise") == "chapter_exercise"
    assert classify_practice_source_bucket("advanced_exercise") == "chapter_exercise"


def test_block_boundary_error_marked_on_subsection_heading_inside_problem():
    p = {
        "problem_text": "試求答案。\n1-1.3乘法原理\n若已知臺北到臺中有3條路線",
        "skill_id": "vh_mathb4_AdditionPrinciple",
    }
    out = validate_problem_block_purity(p)
    assert out.get("needs_review") is True
    assert out.get("block_boundary_error") is True
    assert out.get("skill_boundary_mismatch") is True


def test_formula_missing_marked_when_placeholder_present_and_stem_not_readable():
    p = {"problem_text": "[FORMULA_MISSING]\n[BLOCK_IMAGE]"}
    out = validate_problem_block_purity(p)
    assert out.get("needs_review") is True
    assert out.get("formula_missing") is True


def test_repair_missing_single_variable_when_unique_symbol_n():
    text = "設 為正整數，試求下列各式之 值：(1) n! = 120 (2) \\frac{n!}{(n-2)!} = 42"
    fixed, meta = repair_missing_single_variable_text(text)
    assert "設 n 為正整數" in fixed
    assert "之 n 值" in fixed
    assert meta.get("applied") is True
    assert meta.get("symbol") == "n"


def test_repair_missing_single_variable_rejects_multiple_candidates():
    text = "設 為正整數，試求下列各式之 值：(1) n! = 120 (2) x! = 24"
    fixed, meta = repair_missing_single_variable_text(text)
    assert fixed == text
    assert meta.get("applied") is False
    assert meta.get("reason") == "non_unique_candidate_variable"


def test_question_formula_context_stops_on_structural_boundary():
    blocks = [
        {"type": "paragraph", "text": "例題1 試求答案", "block_index": 1},
        {"type": "paragraph", "text": "由上面的例題得知...", "block_index": 2},
        {"type": "paragraph", "text": "1-1.3乘法原理", "block_index": 3},
        {"type": "paragraph", "text": "若已知臺北到臺中有3條路線", "block_index": 4},
    ]
    ctx = build_docx_question_formula_context(blocks)
    text = ctx.get("例題1", "")
    assert "由上面的例題得知" in text
    assert "1-1.3乘法原理" not in text
    assert "若已知臺北到臺中有3條路線" not in text


def test_fill_blank_instruction_is_semanticized():
    text = "試填入下列各式□之值"
    fixed, meta = normalize_fill_blank_artifacts(text)
    assert fixed == "試填入下列各式空格之值"
    assert meta.get("changed") is True


def test_fill_blank_symbols_normalized_to_blank_token():
    text = "□ × □ × □ = □"
    fixed, _ = normalize_fill_blank_artifacts(text)
    assert fixed == "[BLANK] × [BLANK] × [BLANK] = [BLANK]"


def test_blank_only_not_formula_missing():
    p = {"problem_text": "[BLANK] × [BLANK] = [BLANK]"}
    out = validate_problem_block_purity(p)
    assert out.get("formula_missing") is None
    assert out.get("needs_review") is None


def test_blank_sets_fill_blank_metadata():
    p = {"problem_text": "[BLANK] × [BLANK] = [BLANK]"}
    out = validate_problem_block_purity(p)
    assert out.get("has_answer_blank") is True
    assert out.get("question_format") == "fill_blank"


def test_permutation_unicode_notation_normalized():
    text = "⁷P₃"
    fixed, meta = normalize_permutation_combination_notation(text)
    assert fixed == "P^{7}_{3}"
    assert meta.get("changed") is True


def test_permutation_already_normalized_not_broken():
    text = "P^{7}_{3}"
    fixed, meta = normalize_permutation_combination_notation(text)
    assert fixed == text
    assert meta.get("changed") is False


def test_formula_missing_still_flagged_even_with_blank():
    p = {"problem_text": "[BLANK]\n[FORMULA_MISSING]"}
    out = validate_problem_block_purity(p)
    assert out.get("formula_missing") is True
    assert out.get("needs_review") is True


def test_question_segmentation_stops_at_next_subsection_boundary():
    text = (
        "例題2 試求答案\n"
        "這是題目內容\n"
        "1-1.3乘法原理\n"
        "若已知臺北到臺中有3條路線"
    )
    seg, meta = segment_question_block_text(text, question_title="例題2")
    assert "1-1.3乘法原理" not in seg
    assert "若已知臺北到臺中有3條路線" not in seg
    assert meta.get("changed") is True


def test_explanation_sentence_not_detected_as_question_start():
    assert _is_question_start_text("由上面的例題得知...") is False


def test_concept_explanation_classified_as_non_question():
    kind = classify_non_question_block("由上面的例題得知，利用公式可得，因此...")
    assert kind == "concept_explanation"


def test_figure_caption_not_treated_as_question_block():
    kind = classify_non_question_block("▲圖5 ▲圖6")
    assert kind == "figure_caption"
    seg, _ = segment_question_block_text("例題2 試求答案\n▲圖5\n▲圖6", question_title="例題2")
    assert "▲圖5" not in seg
    assert "▲圖6" not in seg
