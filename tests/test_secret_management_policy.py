from __future__ import annotations

import os

import pytest

from core.ai_settings import SETTING_GEMINI_API_KEY, set_system_setting_value
from core.ai_wrapper import resolve_gemini_api_key
from core.secret_policy import (
    REDACTED_SECRET_VALUE,
    redact_system_settings_records,
    should_skip_system_setting_restore,
)


def test_backup_redacts_gemini_key_without_leaking_value():
    secret = "AIzaRegressionSecretMustNotAppear123456"
    rows = redact_system_settings_records([
        {"key": SETTING_GEMINI_API_KEY, "value": secret, "description": "legacy"},
        {"key": "ai_mode", "value": "cloud"},
    ])
    assert rows[0]["value"] == REDACTED_SECRET_VALUE
    assert secret not in repr(rows)
    assert rows[1]["value"] == "cloud"


def test_runtime_key_ignores_legacy_database_and_uses_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaEnvironmentOnly123456789012345678")
    key, source = resolve_gemini_api_key()
    assert key == os.environ["GEMINI_API_KEY"]
    assert source == "env"


def test_secret_setting_cannot_be_persisted():
    with pytest.raises(ValueError, match="environment-managed"):
        set_system_setting_value(SETTING_GEMINI_API_KEY, "AIzaRegressionSecretMustNotPersist")


def test_restore_policy_ignores_secret_fields_for_job_reports_and_database_writes():
    assert should_skip_system_setting_restore(SETTING_GEMINI_API_KEY) is True
    assert should_skip_system_setting_restore("provider_access_token") is True
    assert should_skip_system_setting_restore("ai_mode") is False
