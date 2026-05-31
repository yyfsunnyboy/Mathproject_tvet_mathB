# -*- coding: utf-8 -*-
"""Shared Gencode AI client resolution (aligned with pipeline bootstrap)."""

from __future__ import annotations

import logging
from typing import Any

from config import Config
from core.ai_settings import get_ai_settings_snapshot, get_effective_model_config
from core.ai_wrapper import GoogleAIClient, get_ai_client, resolve_gemini_api_key

logger = logging.getLogger(__name__)

DEFAULT_SEMANTIC_ROLES = ("classifier", "architect", "tutor", "default")


def _cloud_preset_from_snapshot(snapshot: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    cloud_key = str(snapshot.get("ai_cloud_model", "") or "").strip()
    if cloud_key and cloud_key in Config.CODER_PRESETS:
        cfg = dict(Config.CODER_PRESETS[cloud_key])
        if str(cfg.get("provider", "")).lower() in ("google", "gemini"):
            return cloud_key, cfg
    for fallback in (
        str(getattr(Config, "DEFAULT_CLOUD_MODEL", "") or ""),
        str(getattr(Config, "DEFAULT_GOOGLE_MODEL", "") or ""),
        "gemini-3.1-flash-lite-preview",
    ):
        key = fallback.strip()
        if key and key in Config.CODER_PRESETS:
            cfg = dict(Config.CODER_PRESETS[key])
            if str(cfg.get("provider", "")).lower() in ("google", "gemini"):
                return key, cfg
    return None


def resolve_gencode_ai_client(
    preferred_roles: list[str] | tuple[str, ...] | None = None,
) -> tuple[Any | None, dict[str, Any]]:
    """
  Resolve a Google Gemini client using the same config chain as other AI features:
  SystemSetting / current_app.config / Config / os.environ for API key;
  get_effective_model_config for provider/model per role.
    """
    roles = list(preferred_roles or DEFAULT_SEMANTIC_ROLES)
    snapshot = get_ai_settings_snapshot()
    mode = str(snapshot.get("ai_global_strategy", "unknown"))
    api_key, key_source = resolve_gemini_api_key()
    has_api_key = bool(str(api_key or "").strip())
    last_meta: dict[str, Any] = {
        "role": "",
        "mode": mode,
        "provider": "",
        "model": "",
        "source": "",
        "api_key_source": key_source or "",
        "has_api_key": has_api_key,
        "endpoint": "",
        "failure_reason": "",
        "error_type": "",
    }

    if not has_api_key:
        last_meta["failure_reason"] = "missing_api_key"
        last_meta["error_type"] = "missing_api_key"
        return None, last_meta

    for role in roles:
        cfg = get_effective_model_config(role)
        provider = str(cfg.get("provider", "local")).lower()
        model = str(cfg.get("model", "") or "").strip()
        source = str(cfg.get("_resolved_source", "unknown"))
        meta: dict[str, Any] = {
            "role": role,
            "mode": mode,
            "provider": provider,
            "model": model,
            "source": source,
            "api_key_source": key_source or "",
            "has_api_key": has_api_key,
            "endpoint": "google_api" if provider in ("google", "gemini") else "local_api",
            "failure_reason": "",
            "error_type": "",
        }
        if provider in ("google", "gemini"):
            if not model:
                meta["failure_reason"] = "model_not_configured"
                meta["error_type"] = "model_not_configured"
                last_meta = meta
                continue
            try:
                client = GoogleAIClient(
                    model,
                    temperature=float(cfg.get("temperature", 0.2)),
                    max_tokens=cfg.get("max_tokens", 8192),
                    safety_settings=cfg.get("safety_settings"),
                    api_key=api_key,
                )
                meta["provider"] = "google"
                meta["endpoint"] = "google_api"
                return client, meta
            except Exception as ex:
                meta["failure_reason"] = str(ex)
                meta["error_type"] = "ai_wrapper_error"
                last_meta = meta
                continue

        try:
            client = get_ai_client(role=role)
            actual = "google" if "GoogleAIClient" in type(client).__name__ else "local"
            if actual == "google":
                meta["provider"] = "google"
                meta["endpoint"] = "google_api"
                meta["model"] = str(getattr(client, "model_name", model) or model)
                return client, meta
            meta["failure_reason"] = f"role={role} resolved to local provider"
            meta["error_type"] = "provider_not_configured"
            last_meta = meta
        except Exception as ex:
            meta["failure_reason"] = str(ex)
            meta["error_type"] = "ai_wrapper_error"
            last_meta = meta

    cloud = _cloud_preset_from_snapshot(snapshot)
    if cloud and has_api_key:
        preset_key, cfg = cloud
        model = str(cfg.get("model", "") or preset_key).strip()
        try:
            client = GoogleAIClient(
                model,
                temperature=float(cfg.get("temperature", 0.2)),
                max_tokens=cfg.get("max_tokens", 8192),
                safety_settings=cfg.get("safety_settings"),
                api_key=api_key,
            )
            return client, {
                "role": "cloud_fallback",
                "mode": mode,
                "provider": "google",
                "model": model,
                "source": f"cloud_preset:{preset_key}",
                "api_key_source": key_source or "",
                "has_api_key": True,
                "endpoint": "google_api",
                "failure_reason": "",
                "error_type": "",
            }
        except Exception as ex:
            last_meta = {
                "role": "cloud_fallback",
                "mode": mode,
                "provider": "google",
                "model": model,
                "source": f"cloud_preset:{preset_key}",
                "api_key_source": key_source or "",
                "has_api_key": True,
                "endpoint": "google_api",
                "failure_reason": str(ex),
                "error_type": "ai_wrapper_error",
            }

    if not last_meta.get("error_type"):
        last_meta["error_type"] = "provider_not_configured"
        if not last_meta.get("failure_reason"):
            last_meta["failure_reason"] = "no_google_role_configured"
    return None, last_meta


def log_ai_semantic_classifier(
    *,
    skill_id: str = "",
    example_id: Any = "",
    provider: str = "",
    model: str = "",
    has_api_key: bool = False,
    status: str = "unavailable",
    error_type: str = "",
    error_message: str = "",
) -> None:
    line = (
        "[AI SEMANTIC CLASSIFIER] skill_id=%s example_id=%s provider=%s model=%s "
        "has_api_key=%s status=%s error_type=%s error_message=%s"
    )
    args = (
        skill_id or "",
        example_id or "",
        provider or "",
        model or "",
        "true" if has_api_key else "false",
        status or "",
        error_type or "",
        (error_message or "")[:500],
    )
    try:
        from flask import current_app, has_app_context

        if has_app_context():
            current_app.logger.info(line, *args)
            return
    except Exception:
        pass
    logger.info(line, *args)
