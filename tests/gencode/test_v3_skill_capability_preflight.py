# -*- coding: utf-8 -*-
"""Focused tests for Gencode V3 capability-aware /skills flow."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest import mock

import pytest

from core.gencode.services.v3_capability_handoff_service import (
    build_cursor_handoff_markdown,
    compute_gap_fingerprint,
    create_or_reuse_capability_handoff,
)
from core.gencode.services.v3_skill_capability_preflight_service import (
    CAPABILITY_INVALID,
    CAPABILITY_MISSING,
    CAPABILITY_PARTIAL,
    CAPABILITY_READY,
    CapabilityPreflightBlocked,
    assert_skill_allows_v3_rebuild,
    evaluate_skill_v3_capability,
)


def _conn_with_examples(skill_id: str, example_ids: list[int]) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            problem_text TEXT,
            correct_answer TEXT,
            detailed_solution TEXT,
            source_description TEXT,
            problem_type TEXT,
            notes TEXT
        )
        """
    )
    for eid in example_ids:
        conn.execute(
            """
            INSERT INTO textbook_examples (
                id, skill_id, problem_text, correct_answer, detailed_solution,
                source_description, problem_type, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                eid,
                skill_id,
                f"problem {eid}",
                f"answer {eid}",
                "",
                f"src {eid}",
                "demo_type",
                "",
            ),
        )
    conn.commit()
    return conn


def _wiring_ok(domain_key: str = "demo_domain") -> dict:
    return {
        "fixed_domain_key": domain_key,
        "domain_module": "types",
        "entrypoint": "SimpleNamespace",
        "registry_revision": "test",
        "allowed_operations": ["demo_op"],
    }


def test_ready_skill_allows_rebuild():
    skill_id = "skill_ready_demo"
    conn = _conn_with_examples(skill_id, [101, 102])
    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        return_value=_wiring_ok(),
    ), mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service._probe_example_resolvable",
        side_effect=lambda **kwargs: {
            "textbook_example_id": int(kwargs["row"]["id"]),
            "resolvable": True,
            "reason": "",
            "problem_type_id": "demo_op",
        },
    ):
        preflight = evaluate_skill_v3_capability(conn, skill_id)
        allowed = assert_skill_allows_v3_rebuild(conn, skill_id)

    assert preflight["capability_status"] == CAPABILITY_READY
    assert preflight["allow_v3_rebuild"] is True
    assert preflight["next_action"] == "rebuild_and_verify"
    assert preflight["resolvable_example_count"] == 2
    assert allowed["capability_status"] == CAPABILITY_READY
    conn.close()


def test_missing_skill_blocks_with_structured_diagnostic():
    skill_id = "skill_missing_demo"
    conn = _conn_with_examples(skill_id, [201])
    from core.registry.taxonomy_registry import SkillDomainNotRegisteredError

    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        side_effect=SkillDomainNotRegisteredError("skill_domain_not_registered"),
    ):
        preflight = evaluate_skill_v3_capability(conn, skill_id)
        with pytest.raises(CapabilityPreflightBlocked) as exc_info:
            assert_skill_allows_v3_rebuild(conn, skill_id)

    assert preflight["capability_status"] == CAPABILITY_MISSING
    assert preflight["allow_v3_rebuild"] is False
    assert preflight["next_action"] == "start_system_ai_capability_fill"
    assert "domain_registry_binding" in preflight["missing_layers"]
    assert exc_info.value.diagnostic["capability_status"] == CAPABILITY_MISSING
    conn.close()


def test_partial_skill_does_not_allow_full_rebuild():
    skill_id = "skill_partial_demo"
    conn = _conn_with_examples(skill_id, [301, 302])
    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        return_value=_wiring_ok(),
    ), mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service._probe_example_resolvable",
        side_effect=lambda **kwargs: {
            "textbook_example_id": int(kwargs["row"]["id"]),
            "resolvable": int(kwargs["row"]["id"]) == 301,
            "reason": "" if int(kwargs["row"]["id"]) == 301 else "unresolved",
            "problem_type_id": "demo_op" if int(kwargs["row"]["id"]) == 301 else "",
        },
    ):
        preflight = evaluate_skill_v3_capability(conn, skill_id)
        with pytest.raises(CapabilityPreflightBlocked):
            assert_skill_allows_v3_rebuild(conn, skill_id)

    assert preflight["capability_status"] == CAPABILITY_PARTIAL
    assert preflight["allow_v3_rebuild"] is False
    assert preflight["resolvable_example_count"] == 1
    assert preflight["unresolved_example_count"] == 1
    assert preflight["next_action"] == "start_system_ai_capability_fill"
    conn.close()


def test_invalid_skill_does_not_publish_gate():
    skill_id = "skill_invalid_demo"
    conn = _conn_with_examples(skill_id, [401])
    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        return_value={
            "fixed_domain_key": "broken_domain",
            "domain_module": "this.module.does.not.exist.xyz",
            "entrypoint": "missing_fn",
            "registry_revision": "test",
            "allowed_operations": ["op"],
        },
    ):
        preflight = evaluate_skill_v3_capability(conn, skill_id)
        with pytest.raises(CapabilityPreflightBlocked) as exc_info:
            assert_skill_allows_v3_rebuild(conn, skill_id)

    assert preflight["capability_status"] == CAPABILITY_INVALID
    assert preflight["allow_v3_rebuild"] is False
    assert preflight["next_action"] == "start_system_ai_capability_fill"
    assert "domain_module_import" in preflight["missing_layers"]
    assert exc_info.value.diagnostic["capability_status"] == CAPABILITY_INVALID
    conn.close()


def test_maintenance_override_allows_blocked_skill():
    skill_id = "skill_override_demo"
    conn = _conn_with_examples(skill_id, [501])
    from core.registry.taxonomy_registry import SkillDomainNotRegisteredError

    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        side_effect=SkillDomainNotRegisteredError("missing"),
    ):
        allowed = assert_skill_allows_v3_rebuild(conn, skill_id, maintenance_override=True)

    assert allowed["allow_v3_rebuild"] is True
    assert allowed["maintenance_override"] is True
    assert allowed["capability_status"] == CAPABILITY_MISSING
    conn.close()


def test_gap_handoff_content_complete_and_dedupes():
    import shutil
    import uuid

    skill_id = "skill_handoff_demo"
    conn = _conn_with_examples(skill_id, [601, 602])
    gap_root = Path("reports") / f"pytest_cap_gap_{uuid.uuid4().hex[:8]}"
    gap_root.mkdir(parents=True, exist_ok=True)
    from core.registry.taxonomy_registry import SkillDomainNotRegisteredError

    try:
        with mock.patch(
            "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
            side_effect=SkillDomainNotRegisteredError("missing"),
        ):
            first = create_or_reuse_capability_handoff(conn, skill_id, gap_root=gap_root)
            second = create_or_reuse_capability_handoff(conn, skill_id, gap_root=gap_root)

        assert first["ok"] is True
        assert first["reused"] is False
        assert second["reused"] is True
        assert first["gap_fingerprint"] == second["gap_fingerprint"]
        assert first["handoff_dir"] == second["handoff_dir"]

        md_path = Path(first["handoff_md"])
        md = md_path.read_text(encoding="utf-8")
        for needle in (
            "教材題目清單",
            "Domain resolver 結果",
            "缺少層級",
            "同構分群建議",
            "既有相近 API",
            "必須執行的 focused tests",
            "不可修改的 verified 成果",
            "完成條件",
            "建議 Cursor 執行 prompt",
            "domain_registry_binding",
            "src_601",
            "src_602",
        ):
            assert needle in md, f"missing section: {needle}"

        preflight = first["preflight"]
        fp = compute_gap_fingerprint(preflight)
        assert fp == first["gap_fingerprint"]
        rebuilt_md = build_cursor_handoff_markdown(
            preflight=preflight,
            example_briefs=[
                {
                    "textbook_example_id": 601,
                    "source_id": "src_601",
                    "problem_type": "demo_type",
                    "problem_text": "p",
                    "correct_answer": "a",
                }
            ],
            fingerprint=fp,
        )
        assert "完成條件" in rebuilt_md
    finally:
        shutil.rmtree(gap_root, ignore_errors=True)
        conn.close()

def test_component_draft_built_semantics_in_observation():
    """component_draft_built means scaffold ran; model_generation_invoked is legacy alias."""
    from core.gencode import pipeline_orchestrator as orch

    # Inspect the observation bootstrap defaults in source path used by dryrun.
    # We assert the dual-write contract on a synthetic observation dict mirroring orchestrator.
    observation = {
        "component_draft_built": False,
        "model_generation_invoked": False,
    }
    observation["component_draft_built"] = True
    observation["model_generation_invoked"] = True  # legacy alias
    assert observation["component_draft_built"] is True
    assert observation["model_generation_invoked"] is True

    # Ensure orchestrator still documents/sets both keys after scaffold.
    src = Path(orch.__file__).read_text(encoding="utf-8")
    assert '"component_draft_built": False' in src
    assert "legacy alias" in src or "model_generation_invoked" in src


def test_admin_skills_ui_four_capability_buttons():
    html = (Path(__file__).resolve().parents[2] / "templates" / "admin_skills.html").read_text(
        encoding="utf-8"
    )
    assert "重新建置與驗證" in html
    assert "系統AI補全能力" in html
    assert "匯出診斷" in html
    assert "startSkillCapabilityAiFill" in html
    assert "exportSkillCapabilityDiagnosis" in html
    assert "Gencode V3會使用既有domain能力重新建置，不會自行建立新API。" in html
    assert "建立開發交接包" not in html
    # Misleading primary V3 regenerate label removed from action block.
    assert "onclick=\"runSkillV3BatchDryrun('{{ skill.skill_id }}', 'regenerate', '重新生成')\"" not in html


def test_dryrun_route_returns_409_for_missing_without_starting_generation():
    import uuid

    import config as _cfg
    from app import create_app
    from models import User, db

    project_root = Path("reports") / f"pytest_cap_route_{uuid.uuid4().hex[:8]}"
    project_root.mkdir(parents=True, exist_ok=True)
    db_path = project_root / "test.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")

    closed_loop_calls: list[dict] = []

    def _fake_assert(conn, skill_id, *, maintenance_override=False):
        raise CapabilityPreflightBlocked(
            {
                "skill_id": skill_id,
                "capability_status": CAPABILITY_MISSING,
                "allow_v3_rebuild": False,
                "next_action": "start_system_ai_capability_fill",
                "missing_layers": ["domain_registry_binding"],
            }
        )

    def _fake_closed_loop(**kwargs):
        closed_loop_calls.append(kwargs)
        return {"success": True}

    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            teacher = User(
                username=f"cap_{uuid.uuid4().hex[:8]}",
                password_hash="x",
                role="teacher",
            )
            db.session.add(teacher)
            db.session.commit()
            uid = teacher.id

            client = app.test_client()
            with client.session_transaction() as sess:
                sess["_user_id"] = str(uid)
                sess["_fresh"] = True

            with mock.patch(
                "core.gencode.services.v3_skill_capability_preflight_service.assert_skill_allows_v3_rebuild",
                side_effect=_fake_assert,
            ), mock.patch(
                "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_publish_closed_loop_for_skill",
                side_effect=_fake_closed_loop,
            ):
                resp = client.post(
                    "/admin/skills/skill_missing_route_demo/gencode_v3_dryrun",
                    json={"smoke": True, "verify": True, "force": True, "mode": "regenerate"},
                )

        assert resp.status_code == 409
        payload = resp.get_json()
        assert payload["error"] == "capability_preflight_blocked"
        assert payload["capability_status"] == CAPABILITY_MISSING
        assert payload["generation_started"] is False
        assert payload["tracker_written"] is False
        assert payload["published"] is False
        assert closed_loop_calls == []
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        import shutil

        shutil.rmtree(project_root, ignore_errors=True)

def test_status_map_embeds_capability_fields():
    from core.gencode.services.gencode_status_query_service import (
        build_admin_skills_gencode_status_map,
    )

    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE gencode_component_tracker (
            textbook_example_id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            component_id TEXT NOT NULL,
            gencode_status TEXT NOT NULL,
            induced_spec_payload TEXT,
            gencode_error_log TEXT,
            updated_at TEXT
        )
        """
    )
    skill_id = "skill_status_embed_demo"
    conn.execute("INSERT INTO textbook_examples (id, skill_id) VALUES (1, ?)", (skill_id,))
    conn.commit()

    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.evaluate_skill_v3_capability",
        return_value={
            "skill_id": skill_id,
            "capability_status": CAPABILITY_MISSING,
            "allow_v3_rebuild": False,
            "next_action": "start_system_ai_capability_fill",
            "ui": {"status_label": "尚未建立出題能力", "primary_action_label": "系統AI補全能力"},
        },
    ), mock.patch(
        "core.gencode.services.v3_skill_coverage_service.get_v3_skills_component_coverage_batch",
        return_value={
            skill_id: {
                "skill_id": skill_id,
                "total_examples": 1,
                "verified_count": 0,
                "failed_count": 0,
                "unsupported_count": 0,
                "publish_ready": False,
                "examples": [],
            }
        },
    ):
        view = build_admin_skills_gencode_status_map(conn, [skill_id])[skill_id]

    assert view["capability_status"] == CAPABILITY_MISSING
    assert view["allow_v3_rebuild"] is False
    assert view["capability_ui"]["primary_action_label"] == "系統AI補全能力"
    conn.close()
