from __future__ import annotations

import json
import re
from pathlib import Path


REPORT_PATH = Path(
    "reports/b4_generator_planning/b4_final_mode_aware_runtime_coverage_recount.md"
)
SKILL_SOURCE_CSV = Path("reports/b4_generator_planning/b4_skill_source_summary.csv")


def _read_report() -> str:
    return REPORT_PATH.read_text(encoding="utf-8")


def _extract_snapshot() -> dict:
    text = _read_report()
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    assert m, "Machine-readable Snapshot JSON block not found."
    return json.loads(m.group(1))


def _canonical_skill_ids() -> list[str]:
    lines = SKILL_SOURCE_CSV.read_text(encoding="utf-8").strip().splitlines()
    return [ln.split(",")[0] for ln in lines[1:] if ln.strip()]


def _matrix_rows_for_skills() -> dict[str, str]:
    text = _read_report()
    rows: dict[str, str] = {}
    for line in text.splitlines():
        if "| vh_數學B4_" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 7:
            continue
        skill_id = parts[3]
        category = parts[5]
        if skill_id.startswith("vh_數學B4_"):
            rows[skill_id] = category
    return rows


def test_report_exists() -> None:
    assert REPORT_PATH.exists()


def test_total_b4_skills_is_40() -> None:
    snap = _extract_snapshot()
    assert snap["total_b4_skills"] == 40


def test_primary_category_sum_is_40() -> None:
    snap = _extract_snapshot()
    assert snap["sum_primary_categories"] == 40


def test_unknown_or_no_runtime_is_zero() -> None:
    snap = _extract_snapshot()
    assert snap["unknown_or_no_runtime_count"] == 0


def test_all_40_skills_have_primary_category() -> None:
    canonical = set(_canonical_skill_ids())
    matrix = _matrix_rows_for_skills()
    assert len(canonical) == 40
    assert canonical.issubset(set(matrix.keys()))
    assert len(matrix) >= 40


def test_histograms_and_frequency_polygons_is_partial_runtime() -> None:
    matrix = _matrix_rows_for_skills()
    assert matrix.get("vh_數學B4_HistogramsAndFrequencyPolygons") == "PARTIAL_RUNTIME"


def test_graph4_graph5_blocked_items_not_counted_as_unknown() -> None:
    snap = _extract_snapshot()
    blocked = set(snap["blocked_items"])
    assert {"frequency_polygon_reading", "cumulative_frequency_graph_reading", "mixed_chart_interpretation"}.issubset(blocked)
    assert snap["unknown_or_no_runtime_count"] == 0


def test_fullruntime1_and_fullruntime2_evidence_present() -> None:
    text = _read_report()
    assert "test_b4_fullruntime_remaining_skills_mode_aware_paths.py" in text
    assert "test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py" in text
