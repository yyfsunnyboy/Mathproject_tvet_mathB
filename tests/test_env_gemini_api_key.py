from __future__ import annotations

import os

from dotenv import load_dotenv

from core.env_secrets import update_gemini_api_key
from core.secret_policy import redact_system_settings_records
from core.ai_wrapper import sanitize_secret_text


def test_save_preserves_other_variables_and_deduplicates_key(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text("KEEP_ME=yes\nGEMINI_API_KEY=old\nGEMINI_API_KEY=older\n", encoding="utf-8")
    secret = "AIzaFocusedRegressionSecret1234567890"
    update_gemini_api_key(secret, env_path=env_path)
    text = env_path.read_text(encoding="utf-8")
    assert "KEEP_ME=yes" in text
    assert text.count("GEMINI_API_KEY=") == 1
    assert f"GEMINI_API_KEY={secret}" in text
    assert os.environ["GEMINI_API_KEY"] == secret


def test_blank_does_not_overwrite_and_clear_removes_key(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text("OTHER=value\nGEMINI_API_KEY=existing\n", encoding="utf-8")
    # The HTTP layer treats a blank submission as no save; verify file remains intact.
    assert env_path.read_text(encoding="utf-8").splitlines()[-1] == "GEMINI_API_KEY=existing"
    update_gemini_api_key(None, env_path=env_path)
    assert env_path.read_text(encoding="utf-8") == "OTHER=value\n"
    assert "GEMINI_API_KEY" not in os.environ


def test_restart_loads_saved_key_and_backup_redaction_never_contains_it(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    secret = "AIzaRestartRegressionSecret1234567890"
    update_gemini_api_key(secret, env_path=env_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    load_dotenv(env_path, override=True)
    assert os.environ["GEMINI_API_KEY"] == secret
    backup_rows = redact_system_settings_records([{"key": "ai_gemini_api_key", "value": secret}])
    assert secret not in repr(backup_rows)


def test_log_or_response_text_redacts_submitted_key():
    secret = "AIzaLogResponseRegressionSecret1234567890"
    safe_text = sanitize_secret_text(f"provider rejected {secret}", [secret])
    assert secret not in safe_text
