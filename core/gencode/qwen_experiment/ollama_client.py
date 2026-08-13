# -*- coding: utf-8 -*-
"""Ollama-only client for Qwen Gencode experiment (no Gemini fallback)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config import Config

from core.gencode.qwen_experiment.constants import (
    DEFAULT_MODEL_PRESET,
    DEFAULT_OLLAMA_BASE,
    DEFAULT_TIMEOUT_SECONDS,
)


class OllamaUnavailableError(RuntimeError):
    """Raised when Ollama or the required model is unavailable."""


@dataclass(frozen=True)
class OllamaCallResult:
    text: str
    raw: dict[str, Any]
    thinking: str = ""


def resolve_preset(preset_key: str = DEFAULT_MODEL_PRESET) -> dict[str, Any]:
    key = str(preset_key or DEFAULT_MODEL_PRESET).strip()
    presets = getattr(Config, "CODER_PRESETS", {}) or {}
    if key not in presets:
        raise OllamaUnavailableError(f"unknown_model_preset:{key}")
    cfg = dict(presets[key])
    if str(cfg.get("provider", "")).lower() != "local":
        raise OllamaUnavailableError(f"preset_not_local:{key}")
    model = str(cfg.get("model") or "").strip()
    if not model:
        raise OllamaUnavailableError(f"preset_missing_model:{key}")
    return cfg


def _http_json(
    method: str,
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: float = 30.0,
    opener: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers=headers, method=method.upper())
    open_fn = opener or urlopen
    try:
        with open_fn(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else str(exc)
        raise OllamaUnavailableError(f"ollama_http_error:{exc.code}:{detail[:300]}") from exc
    except URLError as exc:
        raise OllamaUnavailableError(f"ollama_unreachable:{exc.reason}") from exc
    except TimeoutError as exc:
        raise OllamaUnavailableError(f"ollama_timeout:{timeout}") from exc
    try:
        parsed = json.loads(body) if body.strip() else {}
    except json.JSONDecodeError as exc:
        raise OllamaUnavailableError(f"ollama_invalid_json:{body[:200]}") from exc
    return parsed if isinstance(parsed, dict) else {"raw": parsed}


class OllamaExperimentClient:
    """Direct Ollama HTTP client. Never falls back to Gemini or get_ai_client."""

    def __init__(
        self,
        *,
        preset_key: str = DEFAULT_MODEL_PRESET,
        base_url: str = DEFAULT_OLLAMA_BASE,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        opener: Callable[..., Any] | None = None,
        skip_availability_check: bool = False,
    ) -> None:
        self.preset_key = str(preset_key or DEFAULT_MODEL_PRESET).strip()
        self.cfg = resolve_preset(self.preset_key)
        self.model = str(self.cfg["model"])
        self.base_url = str(base_url or DEFAULT_OLLAMA_BASE).rstrip("/")
        self.timeout = float(timeout if timeout is not None else DEFAULT_TIMEOUT_SECONDS)
        self._opener = opener
        self.temperature = float(self.cfg.get("temperature", 0.1))
        self.max_tokens = int(self.cfg.get("max_tokens", 2048) or 2048)
        extra = self.cfg.get("extra_body") if isinstance(self.cfg.get("extra_body"), dict) else {}
        self.num_ctx = int(extra.get("num_ctx", 8192) or 8192)
        self.extra_options = dict(extra)
        if not skip_availability_check:
            self.ensure_available()

    def tags_url(self) -> str:
        return f"{self.base_url}/api/tags"

    def chat_url(self) -> str:
        return f"{self.base_url}/api/chat"

    def ensure_available(self) -> dict[str, Any]:
        tags = _http_json("GET", self.tags_url(), timeout=min(30.0, self.timeout), opener=self._opener)
        models = tags.get("models") if isinstance(tags.get("models"), list) else []
        names: list[str] = []
        for item in models:
            if isinstance(item, dict):
                name = str(item.get("name") or item.get("model") or "").strip()
                if name:
                    names.append(name)
        if not names:
            raise OllamaUnavailableError("ollama_no_models_listed")
        target = self.model
        aliases = {target, target.split(":")[0], f"{target}:latest"}
        matched = False
        for name in names:
            base = name.split(":")[0]
            if name in aliases or base == target.split(":")[0] or name.startswith(target):
                matched = True
                break
        if not matched:
            raise OllamaUnavailableError(
                f"ollama_model_missing:{target};available={names[:20]}"
            )
        return {"ok": True, "model": target, "available_count": len(names)}

    def generate(self, prompt: str) -> OllamaCallResult:
        options = {
            "temperature": self.temperature,
            "num_predict": self.max_tokens,
            "num_ctx": self.num_ctx,
        }
        for key in ("top_k", "top_p", "repeat_penalty", "num_gpu", "num_thread", "keep_alive"):
            if key in self.extra_options:
                options[key] = self.extra_options[key]
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [{"role": "user", "content": str(prompt or "")}],
            "options": options,
        }
        raw = _http_json(
            "POST",
            self.chat_url(),
            payload=payload,
            timeout=self.timeout,
            opener=self._opener,
        )
        message = raw.get("message") if isinstance(raw.get("message"), dict) else {}
        text = str(message.get("content") or raw.get("response") or "")
        thinking = str(message.get("thinking") or raw.get("thinking") or "")
        if not text.strip() and thinking.strip():
            # Prefer explicit content; if empty, do not treat thinking as code.
            text = ""
        return OllamaCallResult(text=text, raw=raw, thinking=thinking)

    def model_snapshot_fields(self) -> dict[str, Any]:
        return {
            "provider": "ollama",
            "model": self.model,
            "preset_key": self.preset_key,
            "endpoint_type": "ollama_http",
            "endpoint": self.base_url,
            "temperature": self.temperature,
            "num_ctx": self.num_ctx,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
        }
