"""Regression guard: Phase 1 must not load or expose RAG runtime."""
from __future__ import annotations

import sys

from app import create_app


RETIRED_ROUTES = {
    "/api/rag_search",
    "/api/rag_chat",
    "/api/adaptive/adv_rag_search",
    "/api/adaptive/adv_rag_chat",
    "/api/adaptive/rag_hint",
}


def test_rag_runtime_is_not_loaded_or_registered():
    app = create_app()
    routes = {rule.rule for rule in app.url_map.iter_rules()}

    assert RETIRED_ROUTES.isdisjoint(routes)
    assert "core.rag_engine" not in sys.modules
    assert "core.advanced_rag_engine" not in sys.modules
    assert "core.adaptive.rag_hint_engine" not in sys.modules


def test_phase1_practice_routes_remain_registered():
    app = create_app()
    routes = {rule.rule: rule.endpoint for rule in app.url_map.iter_rules()}

    assert routes["/adaptive_practice"] == "practice.adaptive_practice_page"
    assert "/api/adaptive/submit_and_get_next" in routes
    assert "/api/practice/ai-check-handwriting" in routes
    assert "/teacher_dashboard" in routes
    assert "/review-demo" in routes
