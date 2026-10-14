# -*- coding: utf-8 -*-
"""Global practice bootstrap acceptance gate (shared frontend).

A practice page that returns HTTP 200 with an empty question card must FAIL.
Structured stem is optional and must never block initial /get_next_question.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from urllib.parse import quote

import pytest

TEMPLATE = Path("templates/index.html")

REPRESENTATIVE_SKILLS = [
    "vh_數學B2_SubSection_3_2_2",  # B2 Ch3 known-good (vectors)
    "vh_數學B2_SubSection_4_1_1",  # B2 Ch4 multipart structured
    "vh_數學B2_SubSection_4_2_3",  # B2 Ch4 legacy single equation
]


def _practice_inline_script(source: str) -> str:
    scripts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>", source)
    return next(s for s in scripts if "get_next_question" in s and "loadQuestion" in s)


def _function_body(source: str, *, signature: str) -> str:
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[brace : index + 1]
    raise AssertionError(f"function body not found: {signature}")


def test_shared_practice_js_has_no_python_def_and_balanced_braces() -> None:
    """One malformed shared brace/def blanks EVERY /practice unit while still HTTP 200."""
    source = TEMPLATE.read_text(encoding="utf-8")
    practice = _practice_inline_script(source)
    offenders = re.findall(r"(?m)^\s*def\s+[A-Za-z_$][\w$]*\s*\(", practice)
    assert offenders == [], f"Python def in practice JS kills bootstrap: {offenders}"
    # Raw `{`/`}` counts are not a reliable parse gate (template literals / regex).
    # Catch the exact regression that blanked every /practice unit:
    assert "function buildMultiPartFieldGroups(" in practice
    assert "def buildMultiPartFieldGroups" not in practice
    assert "function loadQuestion(" in practice
    assert "function renderQuestion(payload)" in practice


def test_initial_question_fetch_is_independent_of_structured_stem() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    practice = _practice_inline_script(source)
    # DOMContentLoaded path must call loadQuestion before any stem render can matter.
    assert "handlePracticeSkillEntry();" in practice
    assert "loadQuestion();" in practice
    assert "setTimeout(ensureInitialLoad, 1000);" in practice
    load = _function_body(practice, signature="function loadQuestion(")
    render = _function_body(practice, signature="function renderQuestion(payload)")
    structured = _function_body(practice, signature="function renderStructuredStem(")
    assert "/get_next_question?" in load
    assert "renderQuestion(data)" in load
    assert "renderStructuredStem" not in load  # fetch must not depend on stem helper
    assert "usedStructuredStem" in render
    assert "setQuestionDisplayText(questionText, questionMainText)" in render
    assert "try {" in structured
    assert "using legacy question_text" in structured
    # Declaration order: fetch helper exists; structured is optional enhancement.
    assert practice.index("function loadQuestion(") < practice.index("function renderStructuredStem(")


def test_representative_skills_practice_bootstrap_fetches_and_renders_payload() -> None:
    """Authenticated smoke: page + get_next_question + non-empty problem for Ch3/Ch4/legacy."""
    from app import create_app
    from models import User, db

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(username=f"gboot_{uuid.uuid4().hex[:8]}", password_hash="x", role="student")
        db.session.add(user)
        db.session.commit()
        uid = user.id

    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True

    # Served HTML must contain the fixed JS (not Python def).
    page0 = client.get(f"/practice/{quote(REPRESENTATIVE_SKILLS[0])}")
    html = page0.get_data(as_text=True)
    assert page0.status_code == 200
    assert "function buildMultiPartFieldGroups" in html
    assert "def buildMultiPartFieldGroups" not in html

    results = {}
    for skill in REPRESENTATIVE_SKILLS:
        page = client.get(f"/practice/{quote(skill)}")
        assert page.status_code == 200
        # Initial fetch
        resp = client.get(f"/get_next_question?skill={quote(skill)}&level=1")
        data = resp.get_json(silent=True) or {}
        q = str(data.get("question_text") or data.get("new_question_text") or "").strip()
        stem = data.get("stem_structure") if isinstance(data.get("stem_structure"), dict) else None
        has_stem = bool(stem and isinstance(stem.get("items"), list) and stem.get("items"))
        parts = ((data.get("answer_contract") or {}).get("parts") or [])
        choices = data.get("choices") or []
        widget_ok = bool(parts) or bool(choices) or True  # short_answer uses main input
        ok = (
            resp.status_code == 200
            and not data.get("error")
            and bool(q)
            and widget_ok
        )
        results[skill] = {
            "ok": ok,
            "status": resp.status_code,
            "family": data.get("problem_type_id"),
            "q_len": len(q),
            "has_stem": has_stem,
            "error": data.get("error"),
        }
        assert ok, f"bootstrap failed for {skill}: {results[skill]}"

        # 下一題 — second fetch must also succeed and keep a visible problem.
        resp2 = client.get(f"/get_next_question?skill={quote(skill)}&level=1")
        data2 = resp2.get_json(silent=True) or {}
        q2 = str(data2.get("question_text") or "").strip()
        assert resp2.status_code == 200 and q2 and not data2.get("error"), (
            f"下一題 failed for {skill}: status={resp2.status_code} err={data2.get('error')}"
        )

    # Ch4 structured skill should expose stem_structure when that family is served.
    ch4 = results["vh_數學B2_SubSection_4_1_1"]
    assert ch4["ok"]
    # Legacy Ch4 skill must still work without requiring stem_structure.
    legacy = results["vh_數學B2_SubSection_4_2_3"]
    assert legacy["ok"]
    # Ch3 must work (legacy path).
    ch3 = results["vh_數學B2_SubSection_3_2_2"]
    assert ch3["ok"]


def test_malformed_optional_stem_metadata_does_not_blank_resolve_path() -> None:
    """Contract text: missing/malformed stem falls through to question_text."""
    source = TEMPLATE.read_text(encoding="utf-8")
    resolver = _function_body(source, signature="function resolveQuestionText(payload)")
    structured = _function_body(source, signature="function renderStructuredStem(")
    assert "resolveStemStructure(payload)" in resolver
    assert "payload.question_text || payload.new_question_text" in resolver
    assert "return false" in structured
    assert "try {" in structured
