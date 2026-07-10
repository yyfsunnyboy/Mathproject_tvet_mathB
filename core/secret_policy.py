"""Central policy for credentials that must never enter persistent artifacts."""

from __future__ import annotations

from typing import Iterable


SECRET_SETTING_KEYS = frozenset({"ai_gemini_api_key"})
SECRET_KEY_MARKERS = ("api_key", "apikey", "secret", "token", "password", "credential")
REDACTED_SECRET_VALUE = "[REDACTED]"


def is_secret_setting_key(value: object) -> bool:
    key = str(value or "").strip().lower()
    return key in SECRET_SETTING_KEYS or any(marker in key for marker in SECRET_KEY_MARKERS)


def should_skip_system_setting_restore(key: object) -> bool:
    """Environment-managed settings must never be restored from a workbook."""
    return is_secret_setting_key(key)


def redact_system_settings_records(records: Iterable[dict]) -> list[dict]:
    """Return export-safe copies; secret settings retain identity but not values."""
    safe = []
    for record in records:
        row = dict(record)
        if is_secret_setting_key(row.get("key")):
            row["value"] = REDACTED_SECRET_VALUE
            if "description" in row:
                row["description"] = "Secret excluded from backup; configure via environment."
        safe.append(row)
    return safe
