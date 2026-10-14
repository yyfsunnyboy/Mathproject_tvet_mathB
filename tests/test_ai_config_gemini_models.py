from pathlib import Path

import pytest

from config import Config
from core.ai_settings import get_active_ai_model, get_effective_model_config, normalize_google_model_id


ROOT = Path(__file__).resolve().parents[1]
LITE = "gemini-3.5-flash-lite"
FLASH = "gemini-3.8-flash"


def _snapshot(model=LITE):
    return {
        "ai_global_strategy": "cloud_first",
        "ai_default_provider": "google",
        "ai_model_roles": {},
        "ai_enable_tutor_response": True,
        "ai_enable_high_precision_vision": False,
        "ai_cloud_model": model,
    }


def test_production_model_allowlist_and_default():
    assert Config.SUPPORTED_CLOUD_MODELS == [LITE, FLASH]
    assert Config.DEFAULT_CLOUD_MODEL == LITE
    assert Config.DEFAULT_OCR_JSON_MODEL == LITE
    assert Config.DEFAULT_TEXTBOOK_IMPORT_MODEL == LITE
    assert Config.DEFAULT_STABLE_FALLBACK_MODEL == LITE
    assert Config.CODER_PRESETS[LITE]["model"] == LITE
    assert Config.CODER_PRESETS[FLASH]["model"] == FLASH


@pytest.mark.parametrize("legacy", ["gemini-2.5-flash", "gemini-3-flash-preview", "gemini-3-flash", "gemini-3.1-flash-lite"])
def test_legacy_models_normalize_to_default(legacy):
    assert normalize_google_model_id(legacy, allow_fallback=True) == LITE
    with pytest.raises(ValueError):
        normalize_google_model_id(legacy)


def test_only_allowlisted_model_ids_are_accepted():
    assert normalize_google_model_id(LITE) == LITE
    assert normalize_google_model_id("Gemini 3.8 Flash") == FLASH
    with pytest.raises(ValueError):
        normalize_google_model_id("not-a-model")


def test_settings_ui_has_only_two_production_options():
    html = (ROOT / "templates" / "ai_prompt_settings.html").read_text(encoding="utf-8")
    assert 'value="{{ model.value }}"' in html
    assert Config.GOOGLE_GEMINI_MODELS[LITE]["label"] == "Gemini 3.5 Flash-Lite"
    assert Config.GOOGLE_GEMINI_MODELS[FLASH]["label"] == "Gemini 3.8 Flash"
    assert "gemini-3-flash-preview" not in html
    assert "gemini-2.5-flash" not in html


def test_test_and_save_handler_is_defined_and_posts_model_ids():
    html = (ROOT / "templates" / "ai_prompt_settings.html").read_text(encoding="utf-8")
    assert 'onclick="testAndSaveMode()"' in html
    assert "async function testAndSaveMode()" in html
    assert 'fetch("/test_api_key"' in html
    assert "cloud_model: cloudModel" in html
    assert 'fetch("/admin/ai_prompt_settings/update"' in html
    assert "finally {\n                btn.innerHTML = originalBtnText;\n                btn.disabled = false;" in html
    assert "Gemini API 連線成功，設定已儲存" in html


@pytest.mark.parametrize("selected", [LITE, FLASH])
def test_google_roles_share_the_active_model(monkeypatch, selected):
    monkeypatch.setattr("core.ai_settings.get_ai_settings_snapshot", lambda: _snapshot(selected))
    for role in ("architect", "tutor", "vision_analyzer", "classifier", "default"):
        cfg = get_effective_model_config(role)
        assert cfg["provider"] == "google"
        assert cfg["model"] == selected


def test_active_model_normalizes_legacy_persisted_setting(monkeypatch):
    monkeypatch.setattr("core.ai_settings._get_system_setting_value", lambda _key: "gemini-2.5-flash")
    assert get_active_ai_model() == LITE


def test_google_role_override_cannot_bypass_active_model(monkeypatch):
    snapshot = _snapshot(FLASH)
    snapshot["ai_model_roles"] = {"tutor": LITE}
    monkeypatch.setattr("core.ai_settings.get_ai_settings_snapshot", lambda: snapshot)
    assert get_effective_model_config("tutor")["model"] == FLASH


def test_api_key_test_validates_model_and_uses_resolver():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "normalize_google_model_id(model_input or Config.DEFAULT_CLOUD_MODEL)" in source
    assert "GenerativeModel(model_name)" in source
    assert '"unsupported_model"' in source


def test_direct_gemini_call_sites_use_active_model_resolver():
    analyzer = (ROOT / "core" / "ai_analyzer.py").read_text(encoding="utf-8")
    practice = (ROOT / "core" / "routes" / "practice.py").read_text(encoding="utf-8")
    assert "runtime_model = get_active_ai_model()" in analyzer
    assert "GenerativeModel(get_active_ai_model())" in practice


def test_no_cross_model_escalation_in_runtime_client():
    wrapper = (ROOT / "core" / "ai_wrapper.py").read_text(encoding="utf-8")
    retry_body = wrapper[wrapper.index("def call_ai_with_retry"):]
    assert FLASH not in retry_body
    assert "fallback=local" not in wrapper
    assert "never silently change" in wrapper
