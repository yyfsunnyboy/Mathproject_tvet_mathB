# -*- coding: utf-8 -*-
"""LocalAIClient Ollama thinking/visible-text parsing (no live model calls)."""

from __future__ import annotations

import json
from unittest import mock

import requests

from core.ai_wrapper import (
    LocalAIClient,
    OllamaGenerateResponse,
    extract_ollama_visible_and_thinking,
)


class _HttpResp:
    def __init__(self, payload: dict, status: int = 200):
        self.status_code = status
        self._payload = payload
        self.text = json.dumps(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP {self.status_code}", response=self)


def test_extract_generate_thinking_and_visible_content():
    visible, thinking = extract_ollama_visible_and_thinking(
        {"response": '{"ok": true}', "thinking": "reasoned privately"},
        chat=False,
    )
    assert visible == '{"ok": true}'
    assert "reasoned" in thinking


def test_extract_generate_empty_response_does_not_use_thinking():
    visible, thinking = extract_ollama_visible_and_thinking(
        {"response": "", "thinking": '{"skill_id": "should_not_promote"}'},
        chat=False,
    )
    assert visible == ""
    assert "should_not_promote" in thinking


def test_extract_think_tags_leave_final_content():
    visible, thinking = extract_ollama_visible_and_thinking(
        {"response": "<think>scratch</think>\n{\"a\": 1}"},
        chat=False,
    )
    assert visible == '{"a": 1}'
    assert "scratch" in thinking
    assert "<think>" not in visible


def test_extract_chat_content_and_thinking():
    visible, thinking = extract_ollama_visible_and_thinking(
        {"message": {"content": "final", "thinking": "chain"}},
        chat=True,
    )
    assert visible == "final"
    assert thinking == "chain"


def test_local_generate_thinking_with_content(monkeypatch):
    client = LocalAIClient("qwen3.5:9b")
    payload = {"response": '{"ok": true}', "thinking": "why", "prompt_eval_count": 3, "eval_count": 5}

    def fake_post(url, **kwargs):
        assert url.endswith("/api/generate")
        return _HttpResp(payload)

    monkeypatch.setattr("requests.post", fake_post)
    resp = client.generate_content("hello")
    assert isinstance(resp, OllamaGenerateResponse)
    assert resp.text == '{"ok": true}'
    assert resp.thinking == "why"
    assert resp.empty_model_output is False
    assert resp.http_ok is True


def test_local_generate_http200_empty_text(monkeypatch):
    client = LocalAIClient("qwen3.5:9b")

    def fake_post(url, **kwargs):
        return _HttpResp({"response": "", "thinking": "only thinking"})

    monkeypatch.setattr("requests.post", fake_post)
    resp = client.generate_content("hello")
    assert resp.text == ""
    assert resp.empty_model_output is True
    assert "only thinking" not in resp.text
    assert resp.thinking == "only thinking"
    assert resp.http_ok is True


def test_local_chat_fallback_parses_message_content(monkeypatch):
    client = LocalAIClient("qwen3.5:9b")
    calls = []

    def fake_post(url, **kwargs):
        calls.append(url)
        if str(url).endswith("/api/generate"):
            return _HttpResp({}, status=404)
        return _HttpResp({"message": {"content": "chat-visible", "thinking": "chat-think"}})

    monkeypatch.setattr("requests.post", fake_post)
    resp = client.generate_content("hello")
    assert any(str(u).endswith("/api/chat") for u in calls)
    assert resp.text == "chat-visible"
    assert resp.thinking == "chat-think"
    assert resp.empty_model_output is False


def test_ollama_response_str_is_visible_text_only():
    resp = OllamaGenerateResponse("", thinking="secret-thinking")
    assert str(resp) == ""
    assert resp.empty_model_output is True
    assert "secret-thinking" not in str(resp)


def test_local_generate_default_omits_think(monkeypatch):
    captured = []

    def fake_post(url, **kwargs):
        captured.append(kwargs.get("json") or {})
        return _HttpResp({"response": "ok"})

    monkeypatch.setattr("requests.post", fake_post)
    LocalAIClient("qwen3.5:9b").generate_content("hello")
    assert captured
    assert "think" not in captured[0]
    assert "think" not in (captured[0].get("options") or {})


def test_local_generate_think_false_is_top_level(monkeypatch):
    captured = []

    def fake_post(url, **kwargs):
        captured.append(kwargs.get("json") or {})
        return _HttpResp({"response": '{"status":"ok"}'})

    monkeypatch.setattr("requests.post", fake_post)
    resp = LocalAIClient("qwen3.5:9b").generate_content("hello", think=False)
    assert captured[0]["think"] is False
    assert "think" not in (captured[0].get("options") or {})
    assert resp.text == '{"status":"ok"}'


def test_local_chat_fallback_passes_think_false(monkeypatch):
    captured = []

    def fake_post(url, **kwargs):
        captured.append((str(url), kwargs.get("json") or {}))
        if str(url).endswith("/api/generate"):
            return _HttpResp({}, status=404)
        return _HttpResp({"message": {"content": "chat-ok"}})

    monkeypatch.setattr("requests.post", fake_post)
    resp = LocalAIClient("qwen3.5:9b").generate_content("hello", think=False)
    assert captured[0][0].endswith("/api/generate")
    assert captured[0][1]["think"] is False
    assert captured[1][0].endswith("/api/chat")
    assert captured[1][1]["think"] is False
    assert "think" not in (captured[1][1].get("options") or {})
    assert resp.text == "chat-ok"


def test_local_vision_chat_passes_think_false(monkeypatch, tmp_path):
    img = tmp_path / "tiny.png"
    img.write_bytes(b"\x89PNG\r\n")
    captured = []

    def fake_post(url, **kwargs):
        captured.append((str(url), kwargs.get("json") or {}))
        return _HttpResp({"message": {"content": "{}"}})

    monkeypatch.setattr("requests.post", fake_post)
    resp = LocalAIClient("qwen3.5:9b").generate_content("hello", image_path=str(img), think=False)
    assert captured[0][0].endswith("/api/chat")
    assert captured[0][1]["think"] is False
    assert "think" not in (captured[0][1].get("options") or {})
    assert resp.text == "{}"
