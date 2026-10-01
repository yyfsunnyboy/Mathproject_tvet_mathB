"""Regression guard: retired AKT adaptive-review routes must not return."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def isolated_app(tmp_path: Path, monkeypatch):
    import config

    db_path = tmp_path / "legacy_route_guard.db"
    monkeypatch.setattr(config.Config, "SQLALCHEMY_DATABASE_URI", f"sqlite:///{db_path.as_posix()}")
    from app import create_app

    app = create_app()
    app.config.update(TESTING=True)
    return app


def test_legacy_adaptive_review_is_absent_and_current_flow_remains(isolated_app):
    rules = {rule.rule: rule.endpoint for rule in isolated_app.url_map.iter_rules()}

    assert "/adaptive-review" not in rules
    assert not any(path.startswith("/api/adaptive-review") for path in rules)
    assert rules["/adaptive_practice"] == "practice.adaptive_practice_page"
    assert "/api/adaptive/submit_and_get_next" in rules

    client = isolated_app.test_client()
    assert client.get("/adaptive-review").status_code == 404
