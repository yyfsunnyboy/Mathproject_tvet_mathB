# -*- coding: utf-8 -*-
"""Safe JSON extraction for Gemini / AI responses (LaTeX backslashes, fenced blocks)."""

from __future__ import annotations

import json
import re
from typing import Any

_PREVIEW_LEN = 400


def sanitize_gemini_json_text(raw: str) -> str:
    """Repair common Gemini JSON issues: fences, prose wrappers, unescaped LaTeX backslashes."""
    if raw is None:
        return ""
    text = str(raw).strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    latex_commands = (
        "binom|frac|times|cdot|sum|prod|sqrt|left|right|over|overline|underline|"
        "vec|hat|bar|lim|to|infty|sin|cos|tan|cot|sec|csc|log|ln|"
        "alpha|beta|gamma|delta|theta|lambda|mu|pi|sigma|omega|phi|rho|tau|"
        "Delta|Sigma"
    )
    text = re.sub(rf"(?<!\\)\\(?=(?:{latex_commands})\b|[()\[\]{{}}])", r"\\\\", text)
    text = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r"\\\\", text)
    return text


def extract_json_object_text(raw: str) -> str:
    text = str(raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no_json_object")
    return text[start : end + 1]


def safe_load_gemini_json(raw: str) -> dict[str, Any]:
    """Parse AI JSON; sanitize LaTeX escapes on failure."""
    raw_text = str(raw or "").strip()
    if not raw_text:
        raise ValueError("empty_ai_response")
    if raw_text.lower().startswith("error:"):
        raise ValueError(f"provider_response_error:{raw_text[:200]}")
    snippet = extract_json_object_text(raw_text)
    fixed = sanitize_gemini_json_text(raw_text)
    try:
        parsed = json.loads(snippet)
        if isinstance(parsed, dict):
            return parsed
        raise ValueError("json_root_not_object")
    except json.JSONDecodeError:
        parsed = json.loads(fixed)
        if isinstance(parsed, dict):
            return parsed
        raise ValueError("json_root_not_object")


def parse_ai_semantic_json(raw: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Parse classifier JSON with diagnostics.
    Returns (parsed_dict, diagnostics).
    """
    raw_text = str(raw or "").strip()
    diag: dict[str, Any] = {
        "raw_response_preview": raw_text[:_PREVIEW_LEN],
        "sanitized_response_preview": "",
        "parser_error": "",
        "failed_stage": "",
    }
    if not raw_text:
        diag["parser_error"] = "empty_ai_response"
        diag["failed_stage"] = "ai_json_parse"
        raise ValueError("empty_ai_response")
    try:
        sanitized = sanitize_gemini_json_text(raw_text)
        diag["sanitized_response_preview"] = sanitized[:_PREVIEW_LEN]
        parsed = safe_load_gemini_json(raw_text)
        if not isinstance(parsed, dict):
            diag["parser_error"] = "json_root_not_object"
            diag["failed_stage"] = "ai_json_parse"
            raise ValueError("json_root_not_object")
        return parsed, diag
    except json.JSONDecodeError as ex:
        diag["parser_error"] = str(ex)
        diag["failed_stage"] = "ai_json_parse"
        raise
    except ValueError as ex:
        diag["parser_error"] = str(ex)
        diag["failed_stage"] = "ai_json_parse"
        raise
