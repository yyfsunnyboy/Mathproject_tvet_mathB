from __future__ import annotations

from collections import Counter
from urllib.parse import quote

from app import create_app


PUBLISHED_B4_V3_SKILL = "vh_數學B4_FrequencyDistributionTableConstruction"
B4_LEGACY_ONLY_SKILL = "vh_數學B4_SamplingSurvey"


def _logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "1"
        sess["_fresh"] = True
    return client


def test_get_next_question_prefers_published_v3_over_b4_phase7b_router(monkeypatch):
    import core.routes.practice as practice_route

    def fail_b4_router(**kwargs):
        raise AssertionError("B4 Phase7B router must not run when a published V3 facade is available")

    monkeypatch.setattr(practice_route, "generate_for_chap3_skill", fail_b4_router)

    client = _logged_client()
    counts: Counter[str] = Counter()
    legacy_count = 0
    no_component_count = 0
    problem_types: set[str] = set()
    module_files: set[str] = set()

    for _ in range(12):
        resp = client.get(f"/get_next_question?skill={quote(PUBLISHED_B4_V3_SKILL)}&level=1")
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["route_mode"] == "v3"
        assert payload["route_source"] == "gencode_wrapper"
        assert payload["wrapper_loaded"] is True
        assert payload["legacy_fallback_used"] is False
        module_files.add(payload["module_file"])
        if payload.get("route_source") == "legacy":
            legacy_count += 1
        component_id = payload.get("component_id")
        if not component_id:
            no_component_count += 1
        else:
            counts[component_id] += 1
        problem_types.add(payload.get("problem_type_id"))

    assert all(counts[f"src_{eid}"] > 0 for eid in range(3822, 3826))
    assert legacy_count == 0
    assert no_component_count == 0
    assert "frequency_table_single_bin_count" not in problem_types
    assert problem_types == {"frequency_table_construction_review"}
    assert any(path.endswith(f"skills\\{PUBLISHED_B4_V3_SKILL}.py") for path in module_files)


def test_b4_phase7b_legacy_only_skill_still_routes_to_legacy():
    client = _logged_client()
    resp = client.get(f"/get_next_question?skill={quote(B4_LEGACY_ONLY_SKILL)}&level=1&gen_seed=3")
    assert resp.status_code == 200
    payload = resp.get_json()

    assert payload["route_mode"] == "b4_phase7b"
    assert payload["route_source"] == "legacy"
    assert payload["legacy_fallback_used"] is True
    assert payload["legacy_fallback_reason"] == "v3_facade_missing"
    assert payload.get("component_id") in (None, "")
    assert payload.get("problem_type_id")
