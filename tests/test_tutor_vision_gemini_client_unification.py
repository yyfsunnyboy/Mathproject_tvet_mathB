from __future__ import annotations

import logging
from pathlib import Path
from types import SimpleNamespace

import core.ai_wrapper as wrapper


ROOT = Path(__file__).resolve().parents[1]


class _FakeGenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.models = object()


def _google_role_config(role):
    return {
        "provider": "google",
        "model": "vision-model" if role == "vision_analyzer" else "tutor-model",
        "temperature": 0.1,
        "max_tokens": 128,
    }


def test_tutor_and_vision_use_same_factory_resolver_and_fingerprint(monkeypatch, caplog):
    key = "AIza" + "UnifiedCredentialLifecycle" + "1234"
    monkeypatch.setattr(wrapper, "HAS_NEW_SDK", True)
    monkeypatch.setattr(wrapper, "new_genai", SimpleNamespace(Client=_FakeGenAIClient))
    monkeypatch.setattr(wrapper, "resolve_gemini_api_key", lambda: (key, "env"))
    monkeypatch.setattr(wrapper, "get_effective_model_config", _google_role_config)

    with caplog.at_level(logging.INFO, logger=wrapper.__name__):
        tutor = wrapper.get_ai_client("tutor")
        vision = wrapper.get_ai_client("vision_analyzer")

    assert type(tutor) is type(vision) is wrapper.GoogleAIClient
    assert tutor.api_key == vision.api_key == key
    traces = [record.message for record in caplog.records if "[AI RUNTIME]" in record.message]
    assert len(traces) == 2
    assert "role=tutor" in traces[0]
    assert "role=vision_analyzer" in traces[1]
    tutor_fingerprint = traces[0].split("key_fingerprint=", 1)[1].split()[0]
    vision_fingerprint = traces[1].split("key_fingerprint=", 1)[1].split()[0]
    assert tutor_fingerprint == vision_fingerprint
    assert key not in "\n".join(traces)


def test_key_change_refreshes_both_roles_without_cached_client(monkeypatch):
    active = {"key": "AIza" + "FirstUnifiedCredential" + "1111"}
    monkeypatch.setattr(wrapper, "HAS_NEW_SDK", True)
    monkeypatch.setattr(wrapper, "new_genai", SimpleNamespace(Client=_FakeGenAIClient))
    monkeypatch.setattr(wrapper, "resolve_gemini_api_key", lambda: (active["key"], "env"))
    monkeypatch.setattr(wrapper, "get_effective_model_config", _google_role_config)

    old_tutor = wrapper.get_ai_client("tutor")
    old_vision = wrapper.get_ai_client("vision_analyzer")
    active["key"] = "AIza" + "SecondUnifiedCredential" + "2222"
    new_tutor = wrapper.get_ai_client("tutor")
    new_vision = wrapper.get_ai_client("vision_analyzer")

    assert old_tutor.api_key == old_vision.api_key
    assert new_tutor.api_key == new_vision.api_key == active["key"]
    assert new_tutor is not old_tutor
    assert new_vision is not old_vision


def test_handwriting_path_has_no_legacy_upload_or_direct_model():
    analyzer = (ROOT / "core" / "ai_analyzer.py").read_text(encoding="utf-8")
    start = analyzer.index("def analyze(")
    end = analyzer.index("def identify_skills_from_problem", start)
    body = analyzer[start:end]
    assert 'get_ai_client(role="vision_analyzer")' in body
    assert "genai.upload_file" not in body
    assert "get_model()" not in body


def test_handwriting_route_does_not_pass_a_second_credential_source():
    route = (ROOT / "core" / "routes" / "adaptive_api.py").read_text(encoding="utf-8")
    start = route.index("def _call_ai_handwriting_checker")
    end = route.index("@practice_bp.route", start)
    body = route[start:end]
    assert "resolve_gemini_api_key" not in body
    assert "api_key=None" in body
