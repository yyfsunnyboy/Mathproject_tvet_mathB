# -*- coding: utf-8 -*-
"""Regression: practice-page bootstrap must not die on optional stem_structure."""

from __future__ import annotations

import re
from pathlib import Path

TEMPLATE = Path("templates/index.html")


def _function_body(source: str, name: str, *, signature: str | None = None) -> str:
    marker = signature or f"function {name}("
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


def test_practice_inline_script_has_no_python_def_functions() -> None:
    """A stray ``def foo() {`` kills the whole practice script (blank question)."""
    source = TEMPLATE.read_text(encoding="utf-8")
    scripts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>", source)
    practice = next(s for s in scripts if "get_next_question" in s and "loadQuestion" in s)
    offenders = re.findall(r"(?m)^\s*def\s+[A-Za-z_$][\w$]*\s*\(", practice)
    assert offenders == [], f"Python def in practice JS: {offenders}"


def test_initial_bootstrap_fetches_before_structured_stem() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    # DOMContentLoaded still kicks loadQuestion independently of stem helpers.
    assert "handlePracticeSkillEntry();" in source
    assert "loadQuestion();" in source
    assert "setTimeout(ensureInitialLoad, 1000);" in source
    load = _function_body(source, "loadQuestion")
    assert "/get_next_question?" in load
    assert "renderQuestion(data)" in load
    # Structured stem is only inside renderQuestion — after payload exists.
    render = _function_body(source, "renderQuestion", signature="function renderQuestion(payload)")
    assert "resolveQuestionText(payload)" in render
    assert "renderStructuredStem" in render
    assert source.index("function loadQuestion") < source.index("function renderStructuredStem")
    assert source.index("fetch(`/get_next_question?") < source.index("function renderStructuredStem")


def test_structured_stem_is_optional_with_legacy_fallback() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    render = _function_body(source, "renderQuestion", signature="function renderQuestion(payload)")
    structured = _function_body(source, "renderStructuredStem")
    assert "usedStructuredStem" in render
    assert "setQuestionDisplayText(questionText, questionMainText)" in render
    assert "return false" in structured
    assert "using legacy question_text" in structured
    # Missing/malformed optional metadata must not throw past bootstrap.
    assert "try {" in structured
    assert "try {" in render


def test_resolve_question_text_prefers_stem_then_legacy() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    resolver = _function_body(source, "resolveQuestionText")
    assert "resolveStemStructure(payload)" in resolver
    assert "payload.question_text || payload.new_question_text" in resolver
    assert "stem.items" in resolver
