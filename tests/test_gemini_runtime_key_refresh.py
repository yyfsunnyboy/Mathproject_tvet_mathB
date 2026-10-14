from __future__ import annotations

from flask import Flask

import core.ai_analyzer as analyzer
from core.ai_wrapper import resolve_gemini_api_key
from core.env_secrets import update_gemini_api_key


class _FakeModel:
    def __init__(self, model_name, configured_key):
        self.model_name = model_name
        self.configured_key = configured_key


def test_saved_key_is_immediately_resolved_for_test_vision_and_tutor(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    old_key = "AIzaOldRuntimeCredential123456789000"
    new_key = "AIzaNewRuntimeCredential123456789999"
    configured = {"key": None}
    built = []

    monkeypatch.setattr(analyzer, "gemini_model", None)
    monkeypatch.setattr(analyzer, "gemini_chat", None)
    monkeypatch.setattr(analyzer, "gemini_model_name", None)
    monkeypatch.setattr(analyzer, "gemini_key_fingerprint", None)
    monkeypatch.setattr(analyzer.genai, "configure", lambda api_key: configured.update(key=api_key))

    def build_model(model_name):
        model = _FakeModel(model_name, configured["key"])
        built.append(model)
        return model

    monkeypatch.setattr(analyzer.genai, "GenerativeModel", build_model)
    monkeypatch.setattr("core.ai_settings.apply_ai_runtime_settings", lambda: None)
    monkeypatch.setattr(
        "core.ai_settings.get_effective_model_config",
        lambda role: {"provider": "google", "model": "gemini-3.1-flash-lite-preview"},
    )

    app = Flask(__name__)
    app.config["TESTING"] = True
    with app.app_context():
        update_gemini_api_key(old_key, env_path=env_path)
        old_tutor = analyzer.get_model("tutor")
        assert old_tutor.configured_key == old_key

        # This is the same persistence operation used after /test_api_key succeeds.
        update_gemini_api_key(new_key, env_path=env_path)
        tested_key, tested_source = resolve_gemini_api_key()
        assert (tested_key, tested_source) == (new_key, "env")

        vision = analyzer.get_model("vision_analyzer")
        tutor = analyzer.get_model("tutor")

    assert vision.configured_key == new_key
    assert tutor.configured_key == new_key
    assert vision is tutor
    assert vision is not old_tutor
    assert len(built) == 2


def test_same_key_does_not_rebuild_but_changed_key_invalidates_cached_model(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    configured = {"key": None}
    built = []

    monkeypatch.setattr(analyzer, "gemini_model", None)
    monkeypatch.setattr(analyzer, "gemini_chat", None)
    monkeypatch.setattr(analyzer, "gemini_model_name", None)
    monkeypatch.setattr(analyzer, "gemini_key_fingerprint", None)
    monkeypatch.setattr(analyzer.genai, "configure", lambda api_key: configured.update(key=api_key))
    monkeypatch.setattr(
        analyzer.genai,
        "GenerativeModel",
        lambda model_name: built.append(_FakeModel(model_name, configured["key"])) or built[-1],
    )
    monkeypatch.setattr("core.ai_settings.apply_ai_runtime_settings", lambda: None)
    monkeypatch.setattr(
        "core.ai_settings.get_effective_model_config",
        lambda role: {"provider": "google", "model": "gemini-3.1-flash-lite-preview"},
    )

    app = Flask(__name__)
    with app.app_context():
        update_gemini_api_key("AIzaFirstRuntimeCredential1234567890", env_path=env_path)
        first = analyzer.get_model("tutor")
        assert analyzer.get_model("vision_analyzer") is first

        update_gemini_api_key("AIzaSecondRuntimeCredential123456789", env_path=env_path)
        second = analyzer.get_model("tutor")

    assert second is not first
    assert len(built) == 2
