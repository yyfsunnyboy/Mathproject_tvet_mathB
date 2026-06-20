# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import uuid
import time
from pathlib import Path
from types import SimpleNamespace
import pytest
from flask import Flask

from models import TextbookExample, SkillInfo, User
from core.gencode.services.v3_component_preview_service import (
    resolve_preview_component,
    generate_component_preview,
)

# Standard stubs for generate.py
STUB_GENERATE_SHORT_ANSWER = """\
def generate(seed=42):
    return {
        "question_text": f"What is 1 + 1? (seed={seed})",
        "choices": [],
        "answer_contract": {
            "answer_type": "short_answer",
            "checker_key": "exact_match",
        },
        "correct_answer": "2",
        "metadata": {"problem_type_id": "addition_test"}
    }
"""

STUB_GENERATE_MULTIPLE_CHOICE = """\
def generate(seed=42):
    return {
        "question_text": "Choose the largest number:",
        "choices": ["A. 1", "B. 5", "C. 3", "D. 2"],
        "answer_contract": {
            "answer_type": "multiple_choice",
        },
        "correct_answer": "B",
        "metadata": {"problem_type_id": "max_test"}
    }
}
"""

STUB_GENERATE_TIMEOUT = """\
import time
def generate(seed=42):
    # Loop infinitely to trigger timeout
    while True:
        time.sleep(0.1)
"""

STUB_GENERATE_EXCEPTION = """\
def generate(seed=42):
    raise ZeroDivisionError("division by zero test")
"""


class MockEngine:
    def raw_connection(self):
        return SimpleNamespace(close=lambda: None)


def _write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def mock_flask_app() -> Flask:
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


# ══════════════════════════════════════════════════════════════════════════════
# 1. Component Resolution Tests
# ══════════════════════════════════════════════════════════════════════════════

def test_resolve_preview_component_prioritizes_verified_dryrun(mock_flask_app: Flask, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("core.gencode.services.v3_component_preview_service.resolve_admin_project_root", lambda _app: tmp_path)
    
    example = SimpleNamespace(id=4565, skill_id="vh_test_skill")
    skill_info = SimpleNamespace(skill_ch_name="測試技能")
    
    # Mock database session query/get
    def mock_get(model, ident):
        if model == TextbookExample:
            return example
        if model == SkillInfo:
            return skill_info
        return None
        
    monkeypatch.setattr(
        "core.gencode.services.v3_component_preview_service.db",
        SimpleNamespace(
            session=SimpleNamespace(get=mock_get),
            engine=MockEngine()
        )
    )
    
    # Mock tracker row - status is 'verified'
    tracker_row = {
        "component_id": "src_4565",
        "gencode_status": "verified",
        "induced_spec_payload": None,
        "updated_at": "2026-06-20 12:00:00"
    }
    monkeypatch.setattr(
        "core.gencode.services.v3_component_preview_service._fetch_tracker_row",
        lambda *args, **kwargs: tracker_row
    )
    
    # Setup files: both dryrun and prod exist
    dryrun_file = tmp_path / "reports" / "gencode_v3_dryrun" / "vh_test_skill" / "components" / "src_4565" / "generate.py"
    prod_file = tmp_path / "agent_skills_v3" / "vh_test_skill" / "components" / "src_4565" / "generate.py"
    
    _write_file(dryrun_file, STUB_GENERATE_SHORT_ANSWER)
    _write_file(prod_file, STUB_GENERATE_SHORT_ANSWER + "\n# different content to trigger hash mismatch")
    
    with mock_flask_app.app_context():
        res = resolve_preview_component(4565)
        
    assert res["textbook_example_id"] == 4565
    assert res["artifact_source"] == "dryrun"
    assert res["artifact_path"] == str(dryrun_file)
    assert res["production_contains_latest"] is False


def test_resolve_preview_component_falls_back_to_production(mock_flask_app: Flask, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("core.gencode.services.v3_component_preview_service.resolve_admin_project_root", lambda _app: tmp_path)
    
    example = SimpleNamespace(id=4565, skill_id="vh_test_skill")
    skill_info = SimpleNamespace(skill_ch_name="測試技能")
    
    def mock_get(model, ident):
        if model == TextbookExample:
            return example
        if model == SkillInfo:
            return skill_info
        return None
        
    monkeypatch.setattr(
        "core.gencode.services.v3_component_preview_service.db",
        SimpleNamespace(
            session=SimpleNamespace(get=mock_get),
            engine=MockEngine()
        )
    )
    
    # Tracker says status is 'failed' (not verified)
    tracker_row = {
        "component_id": "src_4565",
        "gencode_status": "failed",
        "induced_spec_payload": None,
        "updated_at": "2026-06-20 12:00:00"
    }
    monkeypatch.setattr(
        "core.gencode.services.v3_component_preview_service._fetch_tracker_row",
        lambda *args, **kwargs: tracker_row
    )
    
    # Setup files: both dryrun and prod exist
    dryrun_file = tmp_path / "reports" / "gencode_v3_dryrun" / "vh_test_skill" / "components" / "src_4565" / "generate.py"
    prod_file = tmp_path / "agent_skills_v3" / "vh_test_skill" / "components" / "src_4565" / "generate.py"
    
    _write_file(dryrun_file, STUB_GENERATE_SHORT_ANSWER)
    _write_file(prod_file, STUB_GENERATE_SHORT_ANSWER)
    
    with mock_flask_app.app_context():
        res = resolve_preview_component(4565)
        
    # Since tracker status is failed, it fallbacks to production
    assert res["artifact_source"] == "production"
    assert res["artifact_path"] == str(prod_file)


# ══════════════════════════════════════════════════════════════════════════════
# 2. Generation Timeout and Exception Handling Tests
# ══════════════════════════════════════════════════════════════════════════════

def test_generate_component_preview_success(mock_flask_app: Flask, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("core.gencode.services.v3_component_preview_service.resolve_admin_project_root", lambda _app: tmp_path)
    
    example = SimpleNamespace(id=4565, skill_id="vh_test_skill")
    skill_info = SimpleNamespace(skill_ch_name="測試技能")
    
    def mock_get(model, ident):
        if model == TextbookExample:
            return example
        if model == SkillInfo:
            return skill_info
        return None
        
    monkeypatch.setattr(
        "core.gencode.services.v3_component_preview_service.db",
        SimpleNamespace(
            session=SimpleNamespace(get=mock_get),
            engine=MockEngine()
        )
    )
    monkeypatch.setattr(
        "core.gencode.services.v3_component_preview_service._fetch_tracker_row",
        lambda *args, **kwargs: None
    )
    
    prod_file = tmp_path / "agent_skills_v3" / "vh_test_skill" / "components" / "src_4565" / "generate.py"
    _write_file(prod_file, STUB_GENERATE_SHORT_ANSWER)
    
    with mock_flask_app.app_context():
        res = generate_component_preview(4565, seed=123)
        
    assert res["success"] is True
    assert res["example_id"] == 4565
    assert "What is 1 + 1? (seed=123)" in res["question"]["question_text"]
    assert res["question"]["answer"] == "2"
    assert res["question"]["choices"] == []


def test_generate_component_preview_timeout_enforces_limit(mock_flask_app: Flask, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("core.gencode.services.v3_component_preview_service.resolve_admin_project_root", lambda _app: tmp_path)
    
    example = SimpleNamespace(id=4565, skill_id="vh_test_skill")
    skill_info = SimpleNamespace(skill_ch_name="測試技能")
    
    def mock_get(model, ident):
        if model == TextbookExample:
            return example
        if model == SkillInfo:
            return skill_info
        return None
        
    monkeypatch.setattr(
        "core.gencode.services.v3_component_preview_service.db",
        SimpleNamespace(
            session=SimpleNamespace(get=mock_get),
            engine=MockEngine()
        )
    )
    monkeypatch.setattr(
        "core.gencode.services.v3_component_preview_service._fetch_tracker_row",
        lambda *args, **kwargs: None
    )
    
    prod_file = tmp_path / "agent_skills_v3" / "vh_test_skill" / "components" / "src_4565" / "generate.py"
    _write_file(prod_file, STUB_GENERATE_TIMEOUT)
    
    with mock_flask_app.app_context():
        with pytest.raises(TimeoutError):
            generate_component_preview(4565, seed=42, timeout_seconds=0.2)


def test_generate_component_preview_handles_exceptions(mock_flask_app: Flask, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("core.gencode.services.v3_component_preview_service.resolve_admin_project_root", lambda _app: tmp_path)
    
    example = SimpleNamespace(id=4565, skill_id="vh_test_skill")
    skill_info = SimpleNamespace(skill_ch_name="測試技能")
    
    def mock_get(model, ident):
        if model == TextbookExample:
            return example
        if model == SkillInfo:
            return skill_info
        return None
        
    monkeypatch.setattr(
        "core.gencode.services.v3_component_preview_service.db",
        SimpleNamespace(
            session=SimpleNamespace(get=mock_get),
            engine=MockEngine()
        )
    )
    monkeypatch.setattr(
        "core.gencode.services.v3_component_preview_service._fetch_tracker_row",
        lambda *args, **kwargs: None
    )
    
    prod_file = tmp_path / "agent_skills_v3" / "vh_test_skill" / "components" / "src_4565" / "generate.py"
    _write_file(prod_file, STUB_GENERATE_EXCEPTION)
    
    with mock_flask_app.app_context():
        with pytest.raises(ZeroDivisionError):
            generate_component_preview(4565, seed=42)


# ══════════════════════════════════════════════════════════════════════════════
# 3. Route Registration and Endpoint Interaction Integration
# ══════════════════════════════════════════════════════════════════════════════

def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _make_formal_app_with_temp_db(tmp_path: Path):
    import config as _cfg
    from app import create_app
    from models import db, User
    
    db_path = tmp_path / f"formal_preview_{uuid.uuid4().hex[:8]}.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    app = create_app()
    app.config.update(TESTING=True)
    return app, db, User, prev_uri, _cfg


def test_preview_routes_registered_and_auth_enforced(tmp_path: Path):
    app, db_instance, UserClass, prev_uri, cfg = _make_formal_app_with_temp_db(tmp_path)
    try:
        # Route registration checks
        rules = {str(rule): rule for rule in app.url_map.iter_rules()}
        assert "/admin/textbook-examples/<int:id>/v3-preview" in rules
        assert "/admin/textbook-examples/<int:id>/v3-preview/generate" in rules

        # 403 verification for anonymous / non-admin
        client = app.test_client()
        resp_get = client.get("/admin/textbook-examples/4565/v3-preview")
        assert resp_get.status_code == 302 or resp_get.status_code == 401 or resp_get.status_code == 403
    finally:
        cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri


def test_preview_routes_nonexistent_returns_404(tmp_path: Path):
    app, db_instance, UserClass, prev_uri, cfg = _make_formal_app_with_temp_db(tmp_path)
    try:
        with app.app_context():
            admin = UserClass(
                username=f"admin_{uuid.uuid4().hex[:8]}",
                password_hash="x",
                role="admin",
            )
            db_instance.session.add(admin)
            db_instance.session.commit()
            admin_id = admin.id

        client = app.test_client()
        _login(client, admin_id)

        # example ID 999999 doesn't exist
        resp_get = client.get("/admin/textbook-examples/999999/v3-preview")
        assert resp_get.status_code == 404

        resp_post = client.post("/admin/textbook-examples/999999/v3-preview/generate")
        assert resp_post.status_code == 404
        assert resp_post.get_json()["success"] is False
        assert resp_post.get_json()["error_code"] == "example_not_found"
    finally:
        cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
