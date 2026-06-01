from __future__ import annotations

from unittest.mock import patch

from core.gencode import runtime_smoke


def _winerror_5() -> PermissionError:
    ex = PermissionError(5, "access denied")
    ex.winerror = 5
    return ex


def test_windows_permission_error_retries_in_isolated_dynamic_directory(tmp_path):
    retry_result = {"status": "passed", "blockers": []}
    with patch.object(runtime_smoke.os, "name", "nt"), patch.object(
        runtime_smoke.tempfile, "mkdtemp", return_value=str(tmp_path)
    ), patch.object(runtime_smoke.shutil, "copy2"), patch.object(
        runtime_smoke,
        "_run_draft_runtime_smoke_impl",
        side_effect=[_winerror_5(), retry_result],
    ):
        result = runtime_smoke.run_draft_runtime_smoke("skill", "draft.py")

    assert result["status"] == "passed"
    assert result["blockers"] == []
    assert result["windows_permission_fallback"] == "isolated_dynamic_directory"
    assert "windows_permission_conflict_retried_in_isolated_dir" in result["warnings"]


def test_windows_permission_error_is_non_blocking_when_isolated_retry_is_locked(tmp_path):
    with patch.object(runtime_smoke.os, "name", "nt"), patch.object(
        runtime_smoke.tempfile, "mkdtemp", return_value=str(tmp_path)
    ), patch.object(runtime_smoke.shutil, "copy2"), patch.object(
        runtime_smoke,
        "_run_draft_runtime_smoke_impl",
        side_effect=[_winerror_5(), _winerror_5()],
    ):
        result = runtime_smoke.run_draft_runtime_smoke("skill", "draft.py")

    assert result["status"] == "passed"
    assert result["blockers"] == []
    assert result["py_compile_status"] == "passed"
    assert result["py_compile_degraded"] is True
    assert "windows_permission_conflict_ignored" in result["warnings"]


def test_windows_permission_error_from_compile_reaches_isolated_retry(tmp_path):
    draft = tmp_path / "draft.py"
    draft.write_text(
        "\n".join(
            [
                "def generate(level=1, seed=None):",
                "    return {",
                "        'question_text': '1 + 1 = ?',",
                "        'answer': '2',",
                "        'answer_type': 'integer',",
                "        'choices': [],",
                "        'explanation': '1 + 1 = 2',",
                "        'problem_type_id': 'numeric_addition',",
                "        'metadata': {'givens': ['1', '1'], 'target': '2', 'derivation': ['1 + 1 = 2']},",
                "    }",
                "",
                "def check(user_answer, correct_answer, question_payload=None):",
                "    return str(user_answer) == str(correct_answer)",
            ]
        ),
        encoding="utf-8",
    )
    isolated_dir = tmp_path / "isolated"
    isolated_dir.mkdir()

    with patch.object(runtime_smoke.os, "name", "nt"), patch.object(
        runtime_smoke.tempfile, "mkdtemp", return_value=str(isolated_dir)
    ), patch.object(
        runtime_smoke.py_compile, "compile", side_effect=[_winerror_5(), None]
    ):
        result = runtime_smoke.run_draft_runtime_smoke(
            "skill",
            str(draft),
            sample_count=1,
        )

    assert result["windows_permission_fallback"] == "isolated_dynamic_directory"
    assert result["py_compile_status"] == "passed"


def test_windows_permission_error_is_non_blocking_when_dynamic_dir_creation_is_locked():
    with patch.object(runtime_smoke.os, "name", "nt"), patch.object(
        runtime_smoke.tempfile, "mkdtemp", side_effect=_winerror_5()
    ), patch.object(
        runtime_smoke,
        "_run_draft_runtime_smoke_impl",
        side_effect=_winerror_5(),
    ):
        result = runtime_smoke.run_draft_runtime_smoke("skill", "draft.py")

    assert result["status"] == "passed"
    assert result["blockers"] == []
    assert result["py_compile_degraded"] is True
