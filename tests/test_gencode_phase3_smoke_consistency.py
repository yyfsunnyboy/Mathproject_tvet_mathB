from __future__ import annotations

from core.gencode.runtime_smoke import run_draft_runtime_smoke


def test_empty_generate_marks_runtime_smoke_failed(tmp_path):
    draft = tmp_path / "draft_skill.py"
    draft.write_text(
        """
def generate(level=1, seed=None, **kwargs):
    return {}

def check(user_answer, correct_answer):
    return False
""",
        encoding="utf-8",
    )
    raw = run_draft_runtime_smoke("test_skill", str(draft))
    assert raw["status"] == "failed"
    assert "runtime_smoke_empty_output" in raw["blockers"]


def test_publish_check_status_matches_raw_blockers(tmp_path, monkeypatch):
    draft = tmp_path / "draft_skill.py"
    draft.write_text(
        """
def generate(level=1, seed=None, **kwargs):
    return None

def check(user_answer, correct_answer):
    return False
""",
        encoding="utf-8",
    )
    from core.gencode.pipeline_orchestrator import _run_gencode_publish_check_for_draft

    pc = _run_gencode_publish_check_for_draft("test_skill", str(draft))
    assert pc["runtime_smoke_status"] == "failed"
    assert pc["runtime_smoke_raw"]["status"] == "failed"
    assert pc["runtime_smoke_status"] != "passed"
    assert "runtime_smoke_empty_output" in pc["blockers"] or "runtime_smoke_failed" in pc["blockers"]
