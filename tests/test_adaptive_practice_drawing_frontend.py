from __future__ import annotations

from pathlib import Path


TEMPLATE = Path("templates/adaptive_practice_v2.html")
STANDARD_TEMPLATE = Path("templates/index.html")


def _function_body(source: str, name: str) -> str:
    marker = f"function {name}"
    start = source.index(marker)
    brace = source.index("{", start)
    depth = 0
    for idx in range(brace, len(source)):
        char = source[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[brace : idx + 1]
    raise AssertionError(f"function body not found: {name}")


def _async_function_body(source: str, name: str) -> str:
    marker = f"async function {name}"
    start = source.index(marker)
    brace = source.index("{", start)
    depth = 0
    for idx in range(brace, len(source)):
        char = source[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[brace : idx + 1]
    raise AssertionError(f"async function body not found: {name}")


def test_drawing_frontend_guard_uses_contract_fields():
    source = TEMPLATE.read_text(encoding="utf-8")
    body = _function_body(source, "isDrawingQuestion")

    assert 'contract.checker_key === "free_response_drawing_checker"' in body
    assert 'contract.checker === "free_response_drawing_checker"' in body
    assert 'contract.answer_type === "drawing"' in body
    assert 'contract.answer_shape === "drawing"' in body


def test_drawing_ai_check_uses_check_answer_not_handwriting_endpoint():
    source = TEMPLATE.read_text(encoding="utf-8")
    analyze_body = _async_function_body(source, "analyzeHandwriting")
    drawing_branch = analyze_body.split('if (isCurrentDrawingQuestion()) {', 1)[1].split("return;", 1)[0]

    assert 'submitDrawingAnswer("ai_check")' in drawing_branch
    assert "/api/practice/ai-check-handwriting" not in drawing_branch
    assert "/analyze_handwriting" not in drawing_branch


def test_drawing_submit_payload_does_not_send_expected_answer_or_spec():
    source = TEMPLATE.read_text(encoding="utf-8")
    body = _async_function_body(source, "submitDrawingAnswer")

    assert 'fetch("/check_answer"' in body
    assert "composite_image_data_url" in body
    assert "student_strokes_image_data_url" in body
    assert "image_data_url" in body
    assert "question_uid" in body
    assert "skill_id" in body
    assert "expected_answer" not in body
    assert "expected_drawing_spec" not in body


def test_standard_practice_drawing_ai_check_uses_check_answer_before_handwriting():
    source = STANDARD_TEMPLATE.read_text(encoding="utf-8")
    guard_body = _function_body(source, "isDrawingQuestion")
    payload_body = _function_body(source, "buildDrawingCheckAnswerPayload")
    helper_body = _function_body(source, "submitDrawingAnswerFromCanvas")
    ai_body = _function_body(source, "setupAIButton")

    assert "contract.checker_key === 'free_response_drawing_checker'" in guard_body
    assert "contract.answer_type === 'drawing'" in guard_body
    assert "contract.answer_shape === 'drawing'" in guard_body
    assert "Boolean(q.expected_drawing_spec)" in guard_body
    assert "fetch('/check_answer'" in helper_body
    assert "composite_image_data_url" in payload_body
    assert "student_strokes_image_data_url" in payload_body
    assert "image_data_url" in payload_body
    assert "question_uid" in payload_body
    assert "skill_id" in payload_body
    assert "expected_answer" not in payload_body
    assert "expected_drawing_spec" not in payload_body

    drawing_dispatch = ai_body.index("submitDrawingAnswerFromCanvas('ai-check-button')")
    handwriting_dispatch = ai_body.index("fetch('/analyze_handwriting'")
    assert drawing_dispatch < handwriting_dispatch


def test_standard_practice_submit_button_uses_drawing_dispatch():
    source = STANDARD_TEMPLATE.read_text(encoding="utf-8")
    submit_body = _function_body(source, "setupSubmit")
    drawing_dispatch = submit_body.index("submitDrawingAnswerFromCanvas('submit-button')")
    normal_dispatch = submit_body.index("fetch('/check_answer'")

    assert drawing_dispatch < normal_dispatch


def test_practice_templates_have_dual_canvas_and_ui_contract_helpers():
    adaptive = TEMPLATE.read_text(encoding="utf-8")
    standard = STANDARD_TEMPLATE.read_text(encoding="utf-8")

    for source in (adaptive, standard):
        assert "drawing-background-canvas" in source
        assert "buildCompositeCanvas" in source
        assert "resolveDrawingUiContract" in source
        assert "applyDrawingUiContract" in source
        assert "normal_submit_enabled" in source
        assert "text_input_enabled" in source

    # Check is_correct === true and handleCorrectAnswer hook in standard template
    assert "isCorrectVal === true" in standard
    assert "handleCorrectAnswer()" in standard
    assert "consecutiveWrongs++" in standard

    # Check is_correctVal !== null and handleCorrectAnswer hook in adaptive template
    assert "isCorrectVal !== null" in adaptive
    assert "handleCorrectAnswer(" in adaptive


def test_ui_contract_dispatch_logic_and_guards():
    adaptive = TEMPLATE.read_text(encoding="utf-8")
    standard = STANDARD_TEMPLATE.read_text(encoding="utf-8")

    # Verify ui_contract key checks
    for source in (adaptive, standard):
        assert "ai_check_required" in source
        assert "canvas_required" in source

    # Verify guards in AI button click handlers
    assert "ui.ai_check_required !== true" in adaptive
    assert "ui.ai_check_required !== true" in standard

    # Verify expected_answer removal from handwriting analysis payload in standard template
    ai_body = _function_body(standard, "setupAIButton")
    assert "expected_answer" not in ai_body
    assert "correct_answer" not in ai_body
