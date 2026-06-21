# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from flask import Flask


@pytest.fixture
def flask_app() -> Flask:
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


class _RawConn:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True

    def commit(self) -> None:
        pass


def _route_func(admin_route):
    return getattr(admin_route.admin_example_v3_details, "__wrapped__", admin_route.admin_example_v3_details)


def _unwrapped(view):
    return getattr(view, "__wrapped__", view)


def _patch_v3_details_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    *,
    is_admin: bool = True,
    example=None,
    tracker_status=None,
    file_status=None,
):
    from core.routes import admin as admin_route
    from core.gencode.services import gencode_status_query_service as status_service

    raw_conn = _RawConn()
    monkeypatch.setattr(admin_route, "current_user", SimpleNamespace(is_admin=is_admin))
    monkeypatch.setattr(
        admin_route,
        "db",
        SimpleNamespace(
            session=SimpleNamespace(get=lambda _model, _id: example),
            engine=SimpleNamespace(raw_connection=lambda: raw_conn),
        ),
    )
    monkeypatch.setattr(
        status_service,
        "get_gencode_status_for_examples",
        lambda _conn, ids: {ids[0]: tracker_status or {}},
    )
    monkeypatch.setattr(
        status_service,
        "inspect_gencode_files",
        lambda **_kwargs: file_status or {
            "dryrun_generate_exists": False,
            "production_generate_exists": False,
        },
    )
    monkeypatch.setattr(admin_route, "_resolve_admin_project_root", lambda: Path("E:/project"))
    return admin_route, raw_conn


def test_v3_details_success_returns_json_200(flask_app: Flask, monkeypatch: pytest.MonkeyPatch):
    admin_route, _raw_conn = _patch_v3_details_dependencies(
        monkeypatch,
        example=SimpleNamespace(skill_id="vh_test_skill"),
        tracker_status={
            "status": "draft_written",
            "component_id": "src_1001",
            "induced_spec_payload": json.dumps({
                "presentation_mode": "single_choice",
                "problem_type_id": "linear_equation",
                "answer_contract": {"answer_type": "single_choice"},
                "integrity_gate_passed": True,
                "integrity_gate_version": "v1",
                "integrity_gate_blockers": [],
            }),
            "updated_at": "2026-06-20 12:00:00",
            "error_log": None,
        },
        file_status={"dryrun_generate_exists": True, "production_generate_exists": False},
    )

    with flask_app.app_context():
        response, status = _route_func(admin_route)(1001)

    payload = response.get_json()
    assert status == 200
    assert response.content_type.startswith("application/json")
    assert payload["status"] == "success"
    assert payload["textbook_example_id"] == 1001
    assert payload["component_id"] == "src_1001"
    assert payload["presentation_mode"] == "single_choice"
    assert payload["answer_type"] == "single_choice"
    assert payload["dryrun_generate_exists"] is True


def test_v3_details_missing_example_returns_json_404(flask_app: Flask, monkeypatch: pytest.MonkeyPatch):
    admin_route, _raw_conn = _patch_v3_details_dependencies(monkeypatch, example=None)

    with flask_app.app_context():
        response, status = _route_func(admin_route)(404)

    payload = response.get_json()
    assert status == 404
    assert payload == {
        "status": "failed",
        "reason": "textbook_example_not_found",
        "details": "textbook_example_not_found",
        "textbook_example_id": 404,
    }


def test_v3_details_non_admin_returns_json_403(flask_app: Flask, monkeypatch: pytest.MonkeyPatch):
    admin_route, _raw_conn = _patch_v3_details_dependencies(
        monkeypatch,
        is_admin=False,
        example=SimpleNamespace(skill_id="vh_test_skill"),
    )

    with flask_app.app_context():
        response, status = _route_func(admin_route)(1001)

    payload = response.get_json()
    assert status == 403
    assert payload["status"] == "failed"
    assert payload["reason"] == "forbidden"
    assert response.content_type.startswith("application/json")


def test_v3_details_missing_tracker_still_returns_json(flask_app: Flask, monkeypatch: pytest.MonkeyPatch):
    admin_route, _raw_conn = _patch_v3_details_dependencies(
        monkeypatch,
        example=SimpleNamespace(skill_id="vh_test_skill"),
        tracker_status={},
    )

    with flask_app.app_context():
        response, status = _route_func(admin_route)(1002)

    payload = response.get_json()
    assert status == 200
    assert payload["status"] == "success"
    assert payload["gencode_status"] == "not_created"
    assert payload["component_id"] == "src_1002"


def test_v3_details_invalid_induced_spec_payload_warns_without_html_500(
    flask_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
):
    admin_route, _raw_conn = _patch_v3_details_dependencies(
        monkeypatch,
        example=SimpleNamespace(skill_id="vh_test_skill"),
        tracker_status={
            "status": "draft_written",
            "component_id": "src_1003",
            "induced_spec_payload": "{bad json",
        },
    )

    with flask_app.app_context():
        response, status = _route_func(admin_route)(1003)

    payload = response.get_json()
    assert status == 200
    assert payload["status"] == "success"
    assert payload["warnings"][0]["reason"] == "invalid_induced_spec_payload_json"
    assert payload["warnings"][0]["raw_preview"] == "{bad json"


def test_v3_details_datetime_is_serialized(flask_app: Flask, monkeypatch: pytest.MonkeyPatch):
    updated_at = datetime(2026, 6, 20, 13, 14, 15)
    admin_route, _raw_conn = _patch_v3_details_dependencies(
        monkeypatch,
        example=SimpleNamespace(skill_id="vh_test_skill"),
        tracker_status={
            "status": "draft_written",
            "component_id": "src_1004",
            "updated_at": updated_at,
        },
    )

    with flask_app.app_context():
        response, status = _route_func(admin_route)(1004)

    payload = response.get_json()
    assert status == 200
    assert payload["updated_at"] == "2026-06-20T13:14:15"


def test_v3_details_exception_returns_json_500(flask_app: Flask, monkeypatch: pytest.MonkeyPatch):
    from core.routes import admin as admin_route

    monkeypatch.setattr(admin_route, "current_user", SimpleNamespace(is_admin=True))
    monkeypatch.setattr(
        admin_route,
        "db",
        SimpleNamespace(session=SimpleNamespace(get=lambda _model, _id: (_ for _ in ()).throw(RuntimeError("boom")))),
    )

    with flask_app.app_context():
        response, status = _route_func(admin_route)(1005)

    payload = response.get_json()
    assert status == 500
    assert payload == {
        "status": "failed",
        "reason": "v3_details_error",
        "details": "boom",
        "textbook_example_id": 1005,
    }


def test_template_v3_details_url_matches_route_contract():
    template = Path("templates/admin_examples.html").read_text(encoding="utf-8")
    admin_py = Path("core/routes/admin.py").read_text(encoding="utf-8")

    assert "/admin/textbook-examples/${exampleId}/v3-details" in template
    assert "@core_bp.route('/admin/textbook-examples/<int:textbook_example_id>/v3-details', methods=['GET'])" in admin_py
    assert "def admin_example_v3_details(textbook_example_id: int)" in admin_py


def test_template_does_not_assume_v3_details_response_is_json():
    template = Path("templates/admin_examples.html").read_text(encoding="utf-8")

    assert "response.headers.get('content-type')" in template
    assert "response.text()" in template
    assert "non-JSON response" in template
    details_fetch = template.split("fetch(`/admin/textbook-examples/${exampleId}/v3-details`)")[1].split(".then(data =>", 1)[0]
    assert "response.json()" in details_fetch
    assert "content-type" in details_fetch


def test_drawer_uses_two_delegated_v3_buttons_and_click_safe_overlay():
    template = Path("templates/admin_examples.html").read_text(encoding="utf-8")
    final_drawer_renderer = template.split("function renderV3DrawerDetails(data, skillId)", 1)[1].split("async function refreshV3DrawerDetails", 1)[0]

    assert ".v3-drawer-backdrop" in template
    assert "z-index: 1999;" in template
    assert ".v3-drawer" in template
    assert "z-index: 2000;" in template
    assert "pointer-events: auto;" in template
    assert "data-v3-action=\"regenerate\"" in final_drawer_renderer
    assert "data-v3-action=\"sample\"" in final_drawer_renderer
    assert "Smoke" not in final_drawer_renderer
    assert "verified" not in final_drawer_renderer
    assert 'document.addEventListener(\'click\', function(event)' in template
    assert 'event.target.closest("[data-v3-action=\'regenerate\']")' in template
    assert 'event.target.closest("[data-v3-action=\'sample\']")' in template


def test_drawer_regenerate_button_disabled_and_badge_refreshed_after_completion():
    template = Path("templates/admin_examples.html").read_text(encoding="utf-8")

    assert "button.disabled = true" in template
    assert "生成與驗證中..." in template
    assert "await refreshV3DrawerDetails(exampleId, skillId)" in template
    assert "updateV3Badge(exampleId, data)" in template
    assert "此例題已重新生成並驗證通過。" in template


def test_sample_display_contract_includes_three_fixed_seeds_and_required_fields():
    template = Path("templates/admin_examples.html").read_text(encoding="utf-8")
    admin_py = Path("core/routes/admin.py").read_text(encoding="utf-8")

    assert "seeds = [7, 42, 101]" in admin_py
    assert '"problem_type_id": problem_type_id' in admin_py
    for field in [
        "question_text",
        "choices",
        "answer",
        "semantic_answer",
        "problem_type_id",
        "checker",
        "integrity_result",
    ]:
        assert field in template


def test_v3_regenerate_auto_flow_success_returns_verified(
    flask_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
):
    from core.routes import admin as admin_route
    from core.gencode.services import admin_gencode_action_service as action_service

    calls: list[str] = []
    raw_conn = _RawConn()
    monkeypatch.setattr(admin_route, "current_user", SimpleNamespace(is_admin=True))
    monkeypatch.setattr(
        admin_route,
        "db",
        SimpleNamespace(
            session=SimpleNamespace(get=lambda _model, _id: SimpleNamespace(skill_id="vh_test_skill")),
            engine=SimpleNamespace(raw_connection=lambda: raw_conn),
        ),
    )
    monkeypatch.setattr(admin_route, "_resolve_admin_project_root", lambda: Path("E:/project"))
    monkeypatch.setattr(
        action_service,
        "run_admin_v3_dryrun_for_example",
        lambda **_kwargs: calls.append("dryrun") or {
            "status": "draft_written",
            "component_id": "src_1001",
        },
    )
    monkeypatch.setattr(
        admin_route,
        "_run_admin_v3_integrity_gate_for_example",
        lambda **_kwargs: calls.append("smoke_integrity") or {
            "status": "success",
            "textbook_example_id": 1001,
            "skill_id": "vh_test_skill",
            "component_id": "src_1001",
            "gencode_status": "verified",
            "integrity_gate_passed": True,
            "integrity_gate_version": "v1",
        },
    )

    with flask_app.app_context():
        response, status = _unwrapped(admin_route.admin_example_v3_regenerate)(1001)

    payload = response.get_json()
    assert status == 200
    assert payload["status"] == "success"
    assert payload["gencode_status"] == "verified"
    assert payload["integrity_gate_passed"] is True
    assert payload["integrity_gate_version"] == "v1"
    assert calls == ["dryrun", "smoke_integrity"]


def test_v3_regenerate_auto_flow_failure_writes_failed_tracker(
    flask_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
):
    from core.routes import admin as admin_route
    from core.gencode.services import admin_gencode_action_service as action_service
    from core.gencode.services import component_tracker_service as tracker_service

    saved: list[dict[str, object]] = []
    raw_conn = _RawConn()
    monkeypatch.setattr(admin_route, "current_user", SimpleNamespace(is_admin=True))
    monkeypatch.setattr(
        admin_route,
        "db",
        SimpleNamespace(
            session=SimpleNamespace(get=lambda _model, _id: SimpleNamespace(skill_id="vh_test_skill")),
            engine=SimpleNamespace(raw_connection=lambda: raw_conn),
        ),
    )
    monkeypatch.setattr(
        action_service,
        "run_admin_v3_dryrun_for_example",
        lambda **_kwargs: {"status": "draft_written", "component_id": "src_1002"},
    )
    monkeypatch.setattr(
        admin_route,
        "_run_admin_v3_integrity_gate_for_example",
        lambda **_kwargs: (_ for _ in ()).throw(ValueError("integrity_validation_failed")),
    )
    monkeypatch.setattr(
        tracker_service,
        "_fetch_tracker_row",
        lambda _conn, textbook_example_id: {
            "component_id": "src_1002",
            "induced_spec_payload": "{}",
        },
    )
    monkeypatch.setattr(tracker_service, "derive_component_id", lambda _id: "src_1002")
    monkeypatch.setattr(
        tracker_service,
        "save_tracker_record",
        lambda *args, **kwargs: saved.append(kwargs) or kwargs,
    )

    with flask_app.app_context():
        response, status = _unwrapped(admin_route.admin_example_v3_regenerate)(1002)

    payload = response.get_json()
    assert status == 200
    assert payload["status"] == "failed"
    assert payload["component_id"] == "src_1002"
    assert payload["blockers"] == ["integrity_validation_failed"]
    assert saved
    assert saved[-1]["gencode_status"] == "failed"
    assert saved[-1]["gencode_error_log"] == "integrity_validation_failed"


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _make_formal_app_with_temp_db(tmp_path: Path):
    import config as _cfg
    from app import create_app
    from models import User, db

    db_path = tmp_path / f"formal_v3_details_{uuid.uuid4().hex[:8]}.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    app = create_app()
    app.config.update(TESTING=True)
    return app, db, User, prev_uri, _cfg


def test_formal_app_url_map_registers_v3_textbook_example_routes(tmp_path: Path):
    app, _db, _User, prev_uri, cfg = _make_formal_app_with_temp_db(tmp_path)
    try:
        routes = {str(rule): rule for rule in app.url_map.iter_rules()}

        assert "/admin/textbook-examples/<int:textbook_example_id>/v3-details" in routes
        assert "/admin/textbook-examples/<int:textbook_example_id>/v3-regenerate" in routes
        assert "/admin/textbook-examples/<int:textbook_example_id>/v3-smoke" in routes
        assert "/admin/textbook-examples/<int:textbook_example_id>/v3-sample" in routes

        assert "GET" in routes["/admin/textbook-examples/<int:textbook_example_id>/v3-details"].methods
        assert "POST" in routes["/admin/textbook-examples/<int:textbook_example_id>/v3-regenerate"].methods
        assert "POST" in routes["/admin/textbook-examples/<int:textbook_example_id>/v3-smoke"].methods
        assert "GET" in routes["/admin/textbook-examples/<int:textbook_example_id>/v3-sample"].methods
    finally:
        cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri


def test_formal_app_v3_details_client_never_returns_default_html_404(tmp_path: Path):
    app, db, User, prev_uri, cfg = _make_formal_app_with_temp_db(tmp_path)
    try:
        with app.app_context():
            admin = User(
                username=f"admin_{uuid.uuid4().hex[:8]}",
                password_hash="x",
                role="admin",
            )
            db.session.add(admin)
            db.session.commit()
            admin_id = admin.id

        client = app.test_client()
        _login(client, admin_id)
        response = client.get("/admin/textbook-examples/4565/v3-details")

        assert response.status_code == 404
        assert response.content_type.startswith("application/json")
        assert response.get_json() == {
            "status": "failed",
            "reason": "textbook_example_not_found",
            "details": "textbook_example_not_found",
            "textbook_example_id": 4565,
        }
        assert not response.get_data(as_text=True).lstrip().startswith("<!doctype html>")
    finally:
        cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
