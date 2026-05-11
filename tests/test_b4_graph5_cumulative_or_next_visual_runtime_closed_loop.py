from __future__ import annotations

from pathlib import Path

import pytest

from core.vocational_math_b4.services.question_router import generate_for_chap3_skill


REPORT_PATH = Path(
    "reports/b4_generator_planning/b4_graph5_cumulative_or_next_visual_runtime_closed_loop_summary.md"
)
SKILL_CUM = "vh_數學B4_CumulativeFrequencyTablesAndGraphs"
SKILL_STAT = "vh_數學B4_StatisticalChartReading"


def _report_text() -> str:
    return REPORT_PATH.read_text(encoding="utf-8")


def test_candidate_inventory_and_fidelity_tables_exist() -> None:
    text = _report_text()
    assert "Candidate inventory table" in text
    assert "Textbook fidelity evidence table" in text
    assert "candidate_rank" in text
    assert "fidelity_decision" in text


def test_blocked_status_when_no_aligned_release_candidate() -> None:
    text = _report_text()
    assert "## 1. Final status" in text
    assert "`BLOCKED`" in text
    assert "No candidate satisfied aligned release criteria." in text


def test_rejected_candidates_have_reasons_and_no_synthetic_pass() -> None:
    text = _report_text().lower()
    assert "blocked_candidate" in text
    assert "blocked_reason" in text
    assert "rejected_source_summary" in text
    assert "why_not_runtime_ready" in text
    assert "synthetic-only family accepted" in text
    assert "auto_visual_smoke_passed" not in text


def test_no_runtime_release_router_remains_closed() -> None:
    with pytest.raises(ValueError):
        generate_for_chap3_skill(
            skill_id=SKILL_CUM,
            problem_type_id="cumulative_frequency_graph_reading",
            seed=11,
            level=1,
        )

    with pytest.raises(ValueError):
        generate_for_chap3_skill(
            skill_id=SKILL_STAT,
            problem_type_id="mixed_chart_interpretation",
            seed=11,
            level=1,
        )


def test_no_runtime_sample_artifacts_exported_for_graph5() -> None:
    sample_dir = Path("reports/b4_generator_planning/graph5_samples")
    assert not sample_dir.exists()


def test_blocked_confirmation_explicit() -> None:
    text = _report_text()
    assert "No runtime family released in Graph-5." in text
    assert "No production code changes were introduced for Graph-5 runtime." in text
