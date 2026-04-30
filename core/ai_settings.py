# -*- coding: utf-8 -*-
"""AI settings helpers for admin control center and runtime model resolution."""

from __future__ import annotations

import json
from typing import Any

from flask import current_app, has_app_context

from config import Config

AI_ROLE_KEYS = ("architect", "coder", "tutor", "vision_analyzer", "classifier", "default")

SETTING_AI_GLOBAL_STRATEGY = "ai_global_strategy"
SETTING_AI_DEFAULT_PROVIDER = "ai_default_provider"
SETTING_AI_MODEL_ROLES = "ai_model_roles"
SETTING_AI_RAG_NAIVE_THRESHOLD = "ai_rag_naive_threshold"
SETTING_AI_ENABLE_TUTOR_RESPONSE = "ai_enable_tutor_response"
SETTING_AI_ENABLE_HIGH_PRECISION_VISION = "ai_enable_high_precision_vision"
SETTING_AI_CLOUD_MODEL = "ai_cloud_model"
SETTING_GEMINI_API_KEY = "ai_gemini_api_key"

DEFAULT_AI_GLOBAL_STRATEGY = "hybrid_balanced"
DEFAULT_AI_DEFAULT_PROVIDER = str(getattr(Config, "DEFAULT_PROVIDER", "local") or "local").lower()
DEFAULT_AI_RAG_NAIVE_THRESHOLD = float(getattr(Config, "ADVANCED_RAG_NAIVE_THRESHOLD", 0.35))
DEFAULT_AI_ENABLE_TUTOR_RESPONSE = True
DEFAULT_AI_ENABLE_HIGH_PRECISION_VISION = False
DEFAULT_AI_CLOUD_MODEL = str(getattr(Config, "DEFAULT_CLOUD_MODEL", "gemini-3.1-flash-lite-preview") or "gemini-3.1-flash-lite-preview")
SUPPORTED_CLOUD_MODELS = tuple(getattr(Config, "SUPPORTED_CLOUD_MODELS", [DEFAULT_AI_CLOUD_MODEL]))


def _safe_json_loads(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _parse_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in ("true", "1", "yes", "on"):
        return True
    if text in ("false", "0", "no", "off"):
        return False
    return default


def _parse_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_provider(provider: Any) -> str:
    p = str(provider or "").strip().lower()
    return p if p in ("local", "google") else DEFAULT_AI_DEFAULT_PROVIDER


def _normalize_strategy(strategy: Any) -> str:
    s = str(strategy or "").strip().lower()
    if s in ("local_first", "cloud_first", "hybrid_balanced"):
        return s
    return DEFAULT_AI_GLOBAL_STRATEGY


def _log_warning(message: str) -> None:
    if has_app_context():
        current_app.logger.warning(message)


def normalize_google_model_id(model: Any, *, allow_fallback: bool = False) -> str:
    raw = str(model or "").strip()
    key = raw.lower()
    aliases = {
        "gemini 3.1 flash": "gemini-3.1-flash-lite-preview",
        "gemini-3.1-flash": "gemini-3.1-flash-lite-preview",
        "gemini 3.1 flash-lite": "gemini-3.1-flash-lite-preview",
        "gemini 3.1 flash lite": "gemini-3.1-flash-lite-preview",
        "gemini-3.1-flash-lite": "gemini-3.1-flash-lite-preview",
        "gemini-3.1-flash-lite-preview": "gemini-3.1-flash-lite-preview",
        "gemini 3 flash": "gemini-3-flash-preview",
        "gemini 3 flash preview": "gemini-3-flash-preview",
        "gemini 3.0 flash": "gemini-3-flash-preview",
        "gemini 3.0 flash preview": "gemini-3-flash-preview",
        "gemini-3-flash": "gemini-3-flash-preview",
        "gemini-3-flash-preview": "gemini-3-flash-preview",
        "gemini 3.1 flash stable": "gemini-3.1-flash-lite-preview",
        "gemini-3.1-flash-001": "gemini-3.1-flash-lite-preview",
        "gemini 3.1 pro": "gemini-3.1-flash-lite-preview",
        "gemini-3.1-pro": "gemini-3.1-flash-lite-preview",
        "gemini 2.5 flash": "gemini-2.5-flash",
        "gemini-2.5-flash": "gemini-2.5-flash",
    }
    normalized = aliases.get(key)
    if normalized and normalized in SUPPORTED_CLOUD_MODELS:
        if key in {
            "gemini-3.1-flash",
            "gemini 3.1 flash",
            "gemini-3.1-flash-lite",
            "gemini-3.1-flash-001",
            "gemini-3.1-pro",
        }:
            _log_warning(
                f"[AI CONFIG] Deprecated/unsupported model {raw} normalized to {normalized}"
            )
        return normalized

    message = f"Unknown or unsupported Gemini model id: {raw or '<empty>'}"
    _log_warning(f"[AI MODEL] {message}")
    if allow_fallback:
        _log_warning(f"[AI MODEL] Falling back to DEFAULT_CLOUD_MODEL={DEFAULT_AI_CLOUD_MODEL}")
        return DEFAULT_AI_CLOUD_MODEL
    raise ValueError(message)


def get_google_model_options() -> list[dict[str, Any]]:
    models = getattr(Config, "GOOGLE_GEMINI_MODELS", {})
    options: list[dict[str, Any]] = []
    for model_id in SUPPORTED_CLOUD_MODELS:
        meta = dict(models.get(model_id, {}))
        if meta.get("enabled", True) is False:
            continue
        options.append(
            {
                "id": model_id,
                "value": model_id,
                "label": meta.get("label", model_id),
                "provider": meta.get("provider", "google"),
                "tier": meta.get("tier", ""),
                "legacy": bool(meta.get("legacy", False)),
                "recommended_for": meta.get("recommended_for", []),
            }
        )
    return options


def get_google_model_label(model: Any) -> str:
    try:
        model_id = normalize_google_model_id(model)
    except ValueError:
        return str(model or "")
    return getattr(Config, "GOOGLE_GEMINI_MODELS", {}).get(model_id, {}).get("label", model_id)


def _normalize_cloud_model(model_name: Any) -> str:
    model = str(model_name or "").strip()
    return normalize_google_model_id(model, allow_fallback=True)


def _get_system_setting_value(key: str) -> str | None:
    if not has_app_context():
        return None
    from models import SystemSetting

    row = SystemSetting.query.filter_by(key=key).first()
    return row.value if row else None


def set_system_setting_value(key: str, value: Any, description: str = "") -> None:
    """Upsert one SystemSetting row. Caller controls commit/rollback."""
    from models import SystemSetting

    text_value = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    row = SystemSetting.query.filter_by(key=key).first()
    if row:
        row.value = text_value
        if description:
            row.description = description
    else:
        row = SystemSetting(key=key, value=text_value, description=description)
        from models import db

        db.session.add(row)


def get_available_model_presets() -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for key, cfg in Config.CODER_PRESETS.items():
        options.append(
            {
                "key": key,
                "provider": cfg.get("provider", ""),
                "model": cfg.get("model", ""),
                "description": cfg.get("description", ""),
            }
        )
    return options


def _config_role_to_preset_key(role: str) -> str | None:
    cfg = Config.MODEL_ROLES.get(role) or Config.MODEL_ROLES.get("default")
    if not isinstance(cfg, dict):
        return None
    provider = cfg.get("provider")
    model = cfg.get("model")
    for key, preset in Config.CODER_PRESETS.items():
        if preset.get("provider") == provider and preset.get("model") == model:
            return key
    return None


def _fallback_preset_for_provider(role: str, provider: str) -> str | None:
    provider = _normalize_provider(provider)
    local_pref = {
        "coder": "qwen3-8b",
        "tutor": "qwen3-8b",
        "vision_analyzer": "qwen3-vl-8b",
        "classifier": "qwen2.5-3b",
        "default": "qwen2.5-3b",
    }
    cloud_model = _normalize_cloud_model(_get_system_setting_value(SETTING_AI_CLOUD_MODEL))
    selected_cloud_key = cloud_model
    if selected_cloud_key not in Config.CODER_PRESETS:
        selected_cloud_key = DEFAULT_AI_CLOUD_MODEL
    cloud_pref = {
        "coder": selected_cloud_key,
        "tutor": selected_cloud_key,
        "vision_analyzer": selected_cloud_key,
        "classifier": selected_cloud_key,
        "default": selected_cloud_key,
    }

    if provider == "google":
        key = cloud_pref.get(role, DEFAULT_AI_CLOUD_MODEL)
        if key in Config.CODER_PRESETS:
            return key
    else:
        key = local_pref.get(role, local_pref["default"])
        if key in Config.CODER_PRESETS:
            return key

    for k, cfg in Config.CODER_PRESETS.items():
        if str(cfg.get("provider", "")).lower() == provider:
            return k
    return None


def get_ai_settings_snapshot() -> dict[str, Any]:
    model_roles_raw = _get_system_setting_value(SETTING_AI_MODEL_ROLES)
    role_overrides = _safe_json_loads(model_roles_raw)

    sanitized_roles: dict[str, str] = {}
    for role in AI_ROLE_KEYS:
        chosen = role_overrides.get(role)
        if isinstance(chosen, str) and chosen in Config.CODER_PRESETS:
            sanitized_roles[role] = chosen

    strategy = _normalize_strategy(_get_system_setting_value(SETTING_AI_GLOBAL_STRATEGY))
    default_provider = _normalize_provider(_get_system_setting_value(SETTING_AI_DEFAULT_PROVIDER))
    rag_threshold = _parse_float(
        _get_system_setting_value(SETTING_AI_RAG_NAIVE_THRESHOLD),
        DEFAULT_AI_RAG_NAIVE_THRESHOLD,
    )
    enable_tutor = _parse_bool(
        _get_system_setting_value(SETTING_AI_ENABLE_TUTOR_RESPONSE),
        DEFAULT_AI_ENABLE_TUTOR_RESPONSE,
    )
    enable_vision = _parse_bool(
        _get_system_setting_value(SETTING_AI_ENABLE_HIGH_PRECISION_VISION),
        DEFAULT_AI_ENABLE_HIGH_PRECISION_VISION,
    )
    cloud_model = _normalize_cloud_model(_get_system_setting_value(SETTING_AI_CLOUD_MODEL))

    return {
        "ai_global_strategy": strategy,
        "ai_default_provider": default_provider,
        "ai_model_roles": sanitized_roles,
        "ai_rag_naive_threshold": rag_threshold,
        "ai_enable_tutor_response": enable_tutor,
        "ai_enable_high_precision_vision": enable_vision,
        "ai_cloud_model": cloud_model,
    }


def _resolve_role_preset_from_strategy(role: str, strategy: str, default_provider: str) -> str | None:
    if strategy == "local_first":
        return _fallback_preset_for_provider(role, "local")
    if strategy == "cloud_first":
        return _fallback_preset_for_provider(role, "google")

    # hybrid_balanced:
    if strategy == "hybrid_balanced" and role == "tutor":
        # Hybrid 模式下，tutor 必須是 Gemini
        return _fallback_preset_for_provider(role, "google")

    # keep current config tendency first, then provider fallback
    cfg_key = _config_role_to_preset_key(role)
    if cfg_key and cfg_key in Config.CODER_PRESETS:
        return cfg_key
    return _fallback_preset_for_provider(role, default_provider)


def get_effective_model_config(role: str) -> dict[str, Any]:
    normalized_role = role if role in AI_ROLE_KEYS else "default"
    settings = get_ai_settings_snapshot()
    ai_mode = settings.get("ai_global_strategy", "unknown")
    role_overrides = settings.get("ai_model_roles", {})
    selected_cloud_model = str(settings.get("ai_cloud_model", DEFAULT_AI_CLOUD_MODEL)).strip()

    preset_key = None
    source = "unknown"

    # Step 1: role-specific DB override
    override = role_overrides.get(normalized_role)
    if override in Config.CODER_PRESETS:
        preset_key = override
        source = "db_role_override"

    # Step 2: global DB selected cloud model (for all cloud-oriented roles)
    if not preset_key:
        should_use_cloud_selection = (
            ai_mode == "cloud_first"
            or (ai_mode == "hybrid_balanced" and normalized_role in ("tutor", "architect", "vision_analyzer", "classifier", "default"))
        )
        if should_use_cloud_selection and selected_cloud_model in Config.CODER_PRESETS:
            cloud_cfg = Config.CODER_PRESETS.get(selected_cloud_model, {})
            if str(cloud_cfg.get("provider", "")).lower() == "google":
                preset_key = selected_cloud_model
                source = "db_global_selected_model"

    # Step 3: role-specific config default
    if not preset_key:
        cfg_key = _config_role_to_preset_key(normalized_role)
        if cfg_key in Config.CODER_PRESETS:
            preset_key = cfg_key
            source = "config_role_default"

    # Step 4: global config default (DEFAULT_CLOUD_MODEL)
    if not preset_key:
        global_cfg_key = _normalize_cloud_model(getattr(Config, "DEFAULT_CLOUD_MODEL", DEFAULT_AI_CLOUD_MODEL))
        if global_cfg_key in Config.CODER_PRESETS:
            preset_key = global_cfg_key
            source = "config_global_default"

    # Step 5: hard fallback
    if not preset_key:
        stable_fallback = _normalize_cloud_model(getattr(Config, "DEFAULT_STABLE_FALLBACK_MODEL", "gemini-2.5-flash"))
        if stable_fallback in Config.CODER_PRESETS:
            preset_key = stable_fallback
            source = "hard_fallback"
        else:
            preset_key = next(iter(Config.CODER_PRESETS.keys()), None)
            source = "hard_fallback"

    if preset_key and preset_key in Config.CODER_PRESETS:
        cfg = dict(Config.CODER_PRESETS[preset_key])
        cfg["preset_key"] = preset_key
        
        provider = cfg.get("provider", "unknown")
        model_name = cfg.get("model", "unknown")
        
        if has_app_context():
            current_app.logger.info(
                f"[AI CONFIG RESOLVE] role={role} mode={ai_mode} source={source} "
                f"provider={provider} model={model_name}"
            )
            
        return cfg

    # Extreme fallback
    base = Config.MODEL_ROLES.get(role) or Config.MODEL_ROLES.get("default") or {}
    
    if has_app_context():
        current_app.logger.info(
            f"[AI CONFIG RESOLVE] role={role} mode={ai_mode} source=extreme_fallback "
            f"provider={base.get('provider', 'unknown')} model={base.get('model', 'unknown')}"
        )
        
    return dict(base)


def apply_ai_runtime_settings() -> None:
    """Load DB settings into current Flask app config for runtime usage."""
    if not has_app_context():
        return

    snapshot = get_ai_settings_snapshot()
    current_app.config["ADVANCED_RAG_NAIVE_THRESHOLD"] = snapshot["ai_rag_naive_threshold"]
    current_app.config["AI_GLOBAL_STRATEGY"] = snapshot["ai_global_strategy"]
    current_app.config["AI_DEFAULT_PROVIDER"] = snapshot["ai_default_provider"]
    current_app.config["AI_ENABLE_TUTOR_RESPONSE"] = snapshot["ai_enable_tutor_response"]
    current_app.config["AI_ENABLE_HIGH_PRECISION_VISION"] = snapshot["ai_enable_high_precision_vision"]
    current_app.config["AI_CLOUD_MODEL"] = snapshot["ai_cloud_model"]
