from pathlib import Path

from config import Config
from core.ai_settings import get_effective_model_config, normalize_google_model_id


ROOT = Path(__file__).resolve().parents[1]


def test_normalize_google_model_id_legacy_and_31_models():
    assert normalize_google_model_id("gemini-3.1-flash") == "gemini-3.1-flash-lite-preview"
    assert normalize_google_model_id("Gemini 3.1 Flash-Lite") == "gemini-3.1-flash-lite-preview"
    assert normalize_google_model_id("gemini-3.1-flash-lite") == "gemini-3.1-flash-lite-preview"
    assert normalize_google_model_id("gemini-3.1-flash-lite-preview") == "gemini-3.1-flash-lite-preview"
    assert normalize_google_model_id("Gemini 3 Flash") == "gemini-3-flash-preview"
    assert normalize_google_model_id("Gemini 3 Flash Preview") == "gemini-3-flash-preview"
    assert normalize_google_model_id("gemini-3-flash") == "gemini-3-flash-preview"
    assert normalize_google_model_id("gemini-3-flash-preview") == "gemini-3-flash-preview"
    assert normalize_google_model_id("Gemini 2.5 Flash") == "gemini-2.5-flash"


def test_config_google_model_ids_and_default():
    assert Config.DEFAULT_CLOUD_MODEL == "gemini-3.1-flash-lite-preview"
    assert Config.DEFAULT_OCR_JSON_MODEL == "gemini-3.1-flash-lite-preview"
    assert Config.DEFAULT_SELF_ASSESSMENT_IMPORT_MODEL == "gemini-3.1-flash-lite-preview"
    assert Config.DEFAULT_TEXTBOOK_IMPORT_MODEL == "gemini-3-flash-preview"
    assert Config.DEFAULT_STABLE_FALLBACK_MODEL == "gemini-2.5-flash"
    assert Config.SUPPORTED_CLOUD_MODELS == [
        "gemini-3.1-flash-lite-preview",
        "gemini-3-flash-preview",
        "gemini-2.5-flash",
    ]
    assert Config.CODER_PRESETS["gemini-3.1-flash-lite-preview"]["model"] == "gemini-3.1-flash-lite-preview"
    assert Config.CODER_PRESETS["gemini-3-flash-preview"]["model"] == "gemini-3-flash-preview"


def test_ai_prompt_settings_ui_model_options():
    html = (ROOT / "templates" / "ai_prompt_settings.html").read_text(encoding="utf-8")
    assert 'value="{{ model.value }}"' in html
    assert "gemini-3.1-flash-lite-preview" in html
    for model_id in ("gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-flash"):
        assert model_id in Config.SUPPORTED_CLOUD_MODELS
    assert "gemini-3.1-flash" not in Config.SUPPORTED_CLOUD_MODELS
    assert "gemini-3.1-flash-lite" not in Config.SUPPORTED_CLOUD_MODELS
    assert "gemini-3.1-pro" not in Config.SUPPORTED_CLOUD_MODELS
    assert "gemini-3.1-flash-001" not in Config.SUPPORTED_CLOUD_MODELS


def test_api_key_test_uses_selected_model_id_not_label():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "normalize_google_model_id(model_input or Config.DEFAULT_CLOUD_MODEL)" in source
    assert "GenerativeModel(model_name)" in source
    assert "SETTING_AI_CLOUD_MODEL, model_name" in source
    assert '"model_not_found"' in source
    assert '"api_key_invalid"' in source


def test_runtime_status_returns_model_id_field():
    source = (ROOT / "core" / "routes" / "practice.py").read_text(encoding="utf-8")
    assert '"tutor_model": tutor_model' in source
    assert '"architect_model": architect_model' in source
    assert '"vision_analyzer_model": vision_model' in source
    assert "get_google_model_label(tutor_model)" in source


def test_textbook_importer_uses_runtime_gemini_model_not_old_default():
    analyzer = (ROOT / "core" / "ai_analyzer.py").read_text(encoding="utf-8")
    processor = (ROOT / "core" / "textbook_processor.py").read_text(encoding="utf-8")
    assert 'or "gemini-3.1-flash-lite-preview"' in analyzer
    assert 'get_model("architect")' in processor
    assert Config.MODEL_ROLES["architect"]["model"] == "gemini-3-flash-preview"
    assert "gemini-3.1-flash" not in processor
    assert "gemini-2.5-flash" not in processor


def test_get_model_architect_follows_db_global_selected_model(monkeypatch):
    monkeypatch.setattr(
        "core.ai_settings.get_ai_settings_snapshot",
        lambda: {
            "ai_global_strategy": "cloud_first",
            "ai_default_provider": "google",
            "ai_model_roles": {},
            "ai_rag_naive_threshold": 0.35,
            "ai_enable_tutor_response": True,
            "ai_enable_high_precision_vision": False,
            "ai_cloud_model": "gemini-3-flash-preview",
        },
    )
    cfg = get_effective_model_config("architect")
    assert cfg["model"] == "gemini-3-flash-preview"


def test_get_model_vision_follows_db_global_selected_model(monkeypatch):
    monkeypatch.setattr(
        "core.ai_settings.get_ai_settings_snapshot",
        lambda: {
            "ai_global_strategy": "cloud_first",
            "ai_default_provider": "google",
            "ai_model_roles": {},
            "ai_rag_naive_threshold": 0.35,
            "ai_enable_tutor_response": True,
            "ai_enable_high_precision_vision": False,
            "ai_cloud_model": "gemini-3-flash-preview",
        },
    )
    cfg = get_effective_model_config("vision_analyzer")
    assert cfg["model"] == "gemini-3-flash-preview"


def test_role_override_still_beats_db_global_selected_model(monkeypatch):
    monkeypatch.setattr(
        "core.ai_settings.get_ai_settings_snapshot",
        lambda: {
            "ai_global_strategy": "cloud_first",
            "ai_default_provider": "google",
            "ai_model_roles": {"architect": "gemini-3.1-flash-lite-preview"},
            "ai_rag_naive_threshold": 0.35,
            "ai_enable_tutor_response": True,
            "ai_enable_high_precision_vision": False,
            "ai_cloud_model": "gemini-3-flash-preview",
        },
    )
    cfg = get_effective_model_config("architect")
    assert cfg["model"] == "gemini-3.1-flash-lite-preview"


def test_without_db_selected_model_falls_back_to_config_role_default(monkeypatch):
    monkeypatch.setattr(
        "core.ai_settings.get_ai_settings_snapshot",
        lambda: {
            "ai_global_strategy": "cloud_first",
            "ai_default_provider": "google",
            "ai_model_roles": {},
            "ai_rag_naive_threshold": 0.35,
            "ai_enable_tutor_response": True,
            "ai_enable_high_precision_vision": False,
            "ai_cloud_model": "",
        },
    )
    cfg = get_effective_model_config("architect")
    assert cfg["model"] == Config.MODEL_ROLES["architect"]["model"]
