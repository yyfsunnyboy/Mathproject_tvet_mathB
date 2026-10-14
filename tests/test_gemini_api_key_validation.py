from __future__ import annotations

from pathlib import Path

from core.ai_wrapper import sanitize_secret_text


ROOT = Path(__file__).resolve().parents[1]


def test_route_requires_real_google_call_before_save():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    call_at = source.index('model.generate_content("1+1=?")')
    save_at = source.index("update_gemini_api_key(submitted_key)", call_at)
    invalidate_at = source.index("invalidate_gemini_client_cache()", save_at)
    assert call_at < save_at < invalidate_at


def test_invalid_key_response_is_failure_and_non_200():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert 'error_type, status, message = "api_key_invalid", 401' in source
    assert '"success": False' in source
    assert '"ok": False' in source
    assert '}), status' in source


def test_failed_replacement_restores_saved_key_and_cannot_save():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    exception_at = source.index("except Exception as e:", source.index("def test_api_key"))
    failure_path = source[exception_at:source.index("@app.route('/debug/session_key_status')")]
    assert "resolve_gemini_api_key()" in failure_path
    assert "genai.configure(api_key=saved_key)" in failure_path
    assert "update_gemini_api_key(submitted_key)" not in failure_path


def test_frontend_requires_http_success_and_explicit_success_contract():
    html = (ROOT / "templates" / "ai_prompt_settings.html").read_text(encoding="utf-8")
    guard = "!testRes.ok || testData.success !== true || testData.ok !== true"
    guard_at = html.index(guard)
    update_at = html.index('fetch("/admin/ai_prompt_settings/update"', guard_at)
    assert guard_at < update_at


def test_error_redaction_hides_complete_key_in_plain_text_and_query_url():
    secret = "AIza" + "ValidationSecret1234567890" + "LAST"
    raw = f"API_KEY_INVALID https://example.test/path?key={secret}&x=1 submitted={secret}"
    safe = sanitize_secret_text(raw, [secret])
    assert secret not in safe
    assert "?key=***LAST" in safe
    assert "submitted=***LAST" in safe


def test_validation_errors_are_distinct():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    for error_type in ("api_key_invalid", "permission_denied", "quota_exceeded", "model_not_found"):
        assert f'"{error_type}"' in source
