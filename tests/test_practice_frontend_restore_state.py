from __future__ import annotations

from pathlib import Path


TEMPLATE = Path("templates/index.html")


def _function_body(source: str, name: str) -> str:
    marker = f"function {name}"
    start = source.index(marker)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[brace : index + 1]
    raise AssertionError(f"function body not found: {name}")


def test_level_display_prefers_level_then_current_level_then_safe_fallback() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    resolver = _function_body(source, "resolvePracticeResponseLevel")
    loader = _function_body(source, "loadQuestion")

    assert "source.level ?? source.current_level ?? existingLevel ?? 1" in resolver
    assert "selectedLevel = responseLevel" in loader
    assert "`等級：${responseLevel}`" in loader
    assert "`等級：${data.current_level}`" not in source


def test_latest_response_replaces_all_question_identity_and_contract_fields() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    normalizer = _function_body(source, "normalizeLatestQuestionResponse")
    snapshot = _function_body(source, "snapshotPracticeQuestion")
    loader = _function_body(source, "loadQuestion")

    for expected in (
        "question_text: questionTextValue",
        "new_question_text: questionTextValue",
        "question_uid: String(response.question_uid ?? '')",
        "answer_contract: answerContract",
        "current_level: responseLevel",
        "level: responseLevel",
    ):
        assert expected in normalizer
    assert "new_question_text: questionTextValue" in snapshot
    assert "current_level: responseLevel" in snapshot
    assert "level: responseLevel" in snapshot
    assert loader.index("data = normalizeLatestQuestionResponse(data)") < loader.index("applyCurrentQuestion(data)")
    assert loader.index("applyCurrentQuestion(data)") < loader.index("renderQuestion(data)")


def test_question_text_fallback_is_canonicalized_before_render() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    resolver = _function_body(source, "resolveQuestionText")
    normalizer = _function_body(source, "normalizeLatestQuestionResponse")

    assert "payload.question_text || payload.new_question_text" in resolver
    assert "const questionTextValue = resolveQuestionText(response)" in normalizer
    assert "question_text: questionTextValue" in normalizer
    assert "new_question_text: questionTextValue" in normalizer


def test_skill_entry_and_each_load_clear_old_question_state() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    entry = _function_body(source, "handlePracticeSkillEntry")
    reset = _function_body(source, "resetPracticeQuestionDisplay")
    loader = _function_body(source, "loadQuestion")

    assert "clearSkillPracticeStorage(activeSkill)" in entry
    assert "currentQuestion = null" in reset
    assert "isInitialQuestionLoaded = false" in reset
    assert "window.currentProblemTypeId = ''" in reset
    assert "window.currentExpectedAnswer = ''" in reset
    assert "clearSkillPracticeStorage(skill)" in loader
