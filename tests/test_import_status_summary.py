# -*- coding: utf-8 -*-
from __future__ import annotations

from core.data_importer import _append_import_final_status
from core.session_safety import summarize_import_result


def test_import_final_status_completed_when_no_failures_or_warnings():
    lines = []

    status = _append_import_final_status(
        lines,
        row_stats={"skills_info": {"failed": 0}},
        warning_count=0,
    )

    assert status == "completed"
    assert "final_status: completed" in lines


def test_import_final_status_completed_with_warnings_for_orphans():
    lines = []

    status = _append_import_final_status(
        lines,
        row_stats={"skill_curriculum": {"failed": 0}},
        warning_count=24,
        orphan_skill_curriculum_count=24,
    )

    assert status == "completed_with_warnings"
    assert "final_status: completed_with_warnings" in lines
    assert "warning_count: 24" in lines
    assert "orphan_skill_curriculum_count: 24" in lines


def test_import_final_status_failed_for_row_failures():
    lines = []

    status = _append_import_final_status(
        lines,
        row_stats={"skills_info": {"failed": 1}},
        warning_count=0,
    )

    assert status == "failed"
    assert "final_status: failed" in lines


def test_import_final_status_failed_for_fatal_exception():
    lines = []

    status = _append_import_final_status(
        lines,
        fatal_error_count=1,
        fatal_reason="fatal_exception",
    )

    assert status == "failed"
    assert "fatal_errors: 1" in lines
    assert "final_status_reason: fatal_exception" in lines


def test_failed_zero_table_lines_do_not_count_as_errors():
    message = "\n".join(
        [
            "Table skills_info: source_rows=2, imported=2, failed=0, skipped=0",
            "Table skill_curriculum: source_rows=3, imported=3, failed=0, skipped=0",
            "final_status: completed",
            "warning_count: 0",
            "fatal_errors: 0",
            "orphan_skill_curriculum_count: 0",
        ]
    )

    summary = summarize_import_result((True, message))

    assert summary["status"] == "completed"
    assert summary["failed_rows"] == 0
    assert summary["error_count"] == 0
    assert summary["warning_count"] == 0


def test_orphan_rows_with_no_failed_rows_are_completed_with_warnings():
    message = "\n".join(
        [
            "Table skills_info: source_rows=468, imported=468, failed=0, skipped=0",
            "Table skill_curriculum: source_rows=507, imported=507, failed=0, skipped=0",
            "orphan skill_curriculum rows: 24",
            "WARNING: orphan skill_curriculum rows: 24",
            "final_status: completed_with_warnings",
            "final_status_reason: post_import_warnings",
            "warning_count: 24",
            "fatal_errors: 0",
            "orphan_skill_curriculum_count: 24",
        ]
    )

    summary = summarize_import_result((True, message))

    assert summary["status"] == "completed_with_warnings"
    assert summary["success"] is True
    assert summary["failed_rows"] == 0
    assert summary["error_count"] == 0
    assert summary["warning_count"] == 24
    assert summary["orphan_skill_curriculum_count"] == 24


def test_legacy_failed_success_flag_with_only_orphans_is_reclassified_as_warning():
    message = "\n".join(
        [
            "Table skills_info: source_rows=468, imported=468, failed=0, skipped=0",
            "Table skill_curriculum: source_rows=507, imported=507, failed=0, skipped=0",
            "orphan skill_curriculum rows: 24",
        ]
    )

    summary = summarize_import_result((False, message))

    assert summary["status"] == "completed_with_warnings"
    assert summary["success"] is True
    assert summary["error_count"] == 0
    assert summary["warning_count"] == 24


def test_row_failed_rows_are_failed_and_counted_as_errors():
    message = "\n".join(
        [
            "Table skills_info: source_rows=2, imported=1, failed=1, skipped=0",
            "final_status: failed",
            "final_status_reason: row_import_failures",
            "warning_count: 0",
            "fatal_errors: 0",
        ]
    )

    summary = summarize_import_result((False, message))

    assert summary["status"] == "failed"
    assert summary["success"] is False
    assert summary["failed_rows"] == 1
    assert summary["error_count"] == 1


def test_fatal_exception_is_failed():
    message = "\n".join(
        [
            "匯入失敗: boom",
            "final_status: failed",
            "final_status_reason: fatal_exception",
            "warning_count: 0",
            "fatal_errors: 1",
        ]
    )

    summary = summarize_import_result((False, message))

    assert summary["status"] == "failed"
    assert summary["success"] is False
    assert summary["fatal_errors"] == 1
    assert summary["error_count"] == 1
