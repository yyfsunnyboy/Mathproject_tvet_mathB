# -*- coding: utf-8 -*-
import sqlite3
import time
from unittest import mock

import pytest

from core.gencode.services.gencode_status_query_service import (
    build_admin_skills_gencode_status_map,
)


def test_status_map_does_not_audit_variation_by_default():
    conn = sqlite3.connect(":memory:")

    with mock.patch(
        "core.gencode.services.v3_skill_coverage_service.get_v3_skills_component_coverage_batch"
    ) as mock_batch_coverage, mock.patch(
        "core.gencode.services.v3_variation_audit_service.audit_skill_variation"
    ) as mock_audit:
        mock_batch_coverage.return_value = {
            "dummy_skill_1": {
                "skill_id": "dummy_skill_1",
                "verified_count": 1,
                "total_examples": 1,
                "failed_count": 0,
                "unsupported_count": 0,
                "publish_ready": True,
                "examples": [],
            }
        }

        res = build_admin_skills_gencode_status_map(conn, ["dummy_skill_1"])

        mock_audit.assert_not_called()
        assert "dummy_skill_1" in res
        assert res["dummy_skill_1"]["verified_count"] == 1


def test_status_map_batch_completes_quickly_for_many_skills():
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
    skill_ids = [f"skill_{idx}" for idx in range(120)]
    for skill_id in skill_ids:
        conn.execute(
            "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
            (int(skill_id.split("_")[1]), skill_id),
        )
    conn.commit()

    started = time.time()
    result = build_admin_skills_gencode_status_map(conn, skill_ids)
    elapsed = time.time() - started

    assert len(result) == len(skill_ids)
    assert elapsed < 2.0, f"batch status map too slow: {elapsed:.3f}s for {len(skill_ids)} skills"


@pytest.mark.parametrize(
    "audit_variation,should_call_full_view",
    [(False, False), (True, True)],
)
def test_status_map_audit_variation_switches_to_full_view(audit_variation, should_call_full_view):
    conn = sqlite3.connect(":memory:")
    with mock.patch(
        "core.gencode.services.gencode_status_query_service.build_admin_skill_gencode_status_view"
    ) as mock_full_view, mock.patch(
        "core.gencode.services.gencode_status_query_service._build_skill_list_gencode_status_view"
    ) as mock_list_view, mock.patch(
        "core.gencode.services.v3_skill_coverage_service.get_v3_skills_component_coverage_batch"
    ) as mock_batch_coverage, mock.patch(
        "core.gencode.services.gencode_status_query_service._fetch_batch_tracker_rows_for_skills"
    ) as mock_batch_tracker, mock.patch(
        "core.gencode.services.gencode_status_query_service._batch_inspect_skill_production_files"
    ) as mock_batch_prod:
        mock_full_view.return_value = {"status": "verified"}
        mock_list_view.return_value = {"status": "not_created"}
        mock_batch_coverage.return_value = {"skill_a": {"total_examples": 0, "verified_count": 0, "failed_count": 0, "unsupported_count": 0, "publish_ready": False, "examples": []}}
        mock_batch_tracker.return_value = {"skill_a": []}
        mock_batch_prod.return_value = {"skill_a": {"production_wrapper_exists": False, "v3_package_exists": False, "generator_specs_count": 0, "production_component_count": 0}}

        build_admin_skills_gencode_status_map(
            conn,
            ["skill_a"],
            audit_variation=audit_variation,
        )

        if should_call_full_view:
            mock_full_view.assert_called_once()
            mock_list_view.assert_not_called()
        else:
            mock_list_view.assert_called_once()
            mock_full_view.assert_not_called()
