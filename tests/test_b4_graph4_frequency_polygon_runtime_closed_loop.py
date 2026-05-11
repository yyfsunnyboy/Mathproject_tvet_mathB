from __future__ import annotations

import re
from pathlib import Path

import pytest

from core.vocational_math_b4.services.question_router import generate_for_chap3_skill


REPORT_PATH = Path(
    "reports/b4_generator_planning/b4_graph4_frequency_polygon_runtime_closed_loop_summary.md"
)
TARGET_SKILL = "vh_數學B4_HistogramsAndFrequencyPolygons"


def _report_text() -> str:
    return REPORT_PATH.read_text(encoding="utf-8")


def test_textbook_fidelity_evidence_table_exists() -> None:
    text = _report_text()
    assert "Textbook fidelity evidence" in text
    assert "Final Textbook Fidelity Reconciliation" in text
    assert "source_type" in text
    assert "source_section" in text
    assert "observed_question_style" in text
    assert "matched_runtime_pattern" in text
    assert "fidelity_decision" in text


def test_selected_pattern_must_come_from_aligned_source() -> None:
    text = _report_text()
    aligned_rows = re.findall(r"\|[^\n]*\|\s*aligned\s*\|[^\n]*", text)
    polygon_pattern_rows = re.findall(
        r"\|[^\n]*frequency_polygon_[^\n]*\|\s*(aligned|partially_aligned|rejected)\s*\|[^\n]*",
        text,
    )
    assert polygon_pattern_rows, "frequency_polygon runtime pattern rows missing in fidelity table"

    if not aligned_rows:
        assert "## 1. Status" in text
        assert "`BLOCKED`" in text
    else:
        assert any(decision == "aligned" for decision in polygon_pattern_rows)


def test_no_synthetic_only_pass_claim() -> None:
    text = _report_text().lower()
    bad_claim = (
        ("synthetic only" in text or "自行設計" in text or "no textbook source" in text)
        and "auto_visual_smoke_passed" in text
    )
    assert bad_claim is False


def test_blocked_means_runtime_not_opened() -> None:
    text = _report_text()
    if "`BLOCKED`" not in text:
        pytest.skip("This gate only applies when report status is BLOCKED.")

    with pytest.raises(ValueError):
        generate_for_chap3_skill(
            skill_id=TARGET_SKILL,
            problem_type_id="frequency_polygon_reading",
            seed=11,
            level=1,
        )
