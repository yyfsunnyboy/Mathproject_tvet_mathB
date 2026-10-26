"""Admin textbook table: a fixed textbook row is shown as practisable fixed practice, never as a GenCode state (shared logic, no per-row cases)."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "instance" / "kumon_math.db"
sys.path.insert(0, str(ROOT))

from core.gencode.services import gencode_status_query_service as S  # noqa: E402


def test_resolver_distinguishes_the_four_states_from_the_gencode_status():
    assert S.resolve_example_practice_status("published", None)["key"] == "dynamic_published"
    assert S.resolve_example_practice_status("published", "graded")["key"] == "dynamic_published"  # a published generator stays the primary state
    assert S.resolve_example_practice_status("not_generated", "graded")["key"] == "fixed_graded"
    assert S.resolve_example_practice_status("failed", "ungraded")["key"] == "fixed_ungraded"
    assert S.resolve_example_practice_status("not_generated", None)["key"] == "none"
    labels = {k: v["label"] for k, v in S.PRACTICE_STATUS.items()}
    assert len(set(labels.values())) == 4 and labels["fixed_graded"] != labels["dynamic_published"]


def test_fixed_rows_never_take_a_gencode_label_or_badge():
    teacher = S._teacher_status_payload("not_generated")
    for mode in ("graded", "ungraded"):
        shown = S.example_display_status(teacher, S.resolve_example_practice_status("not_generated", mode))
        assert "固定教材" in shown["label"] and shown["badge_class"] not in ("teacher-v3-published", "teacher-v3-generated-not-packaged")
        assert shown["label"] not in {v["label"] for v in S.TEACHER_V3_STATUS.values()}
    # everything else keeps its GenCode badge
    assert S.example_display_status(teacher, S.resolve_example_practice_status("not_generated", None)) == teacher
    published = S._teacher_status_payload("published")
    assert S.example_display_status(published, S.resolve_example_practice_status("published", "graded")) == published


@pytest.mark.skipif(not PROD.exists(), reason="formal database not present")
def test_status_map_for_the_unit2_rows_on_a_read_only_connection():
    con = sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)
    try:
        examples = [(12719, "gh_Series"), (12727, "gh_Series"), (12731, "gh_CommonSeriesSummationFormulas"), (12735, "gh_CommonSeriesSummationFormulas"),
                    (12707, "gh_Series"), (12732, "gh_CommonSeriesSummationFormulas")]
        status = S.build_admin_examples_gencode_status_map(con, examples, project_root=str(ROOT))
    finally:
        con.close()
    keys = {i: status[i]["practice_status"]["key"] for i, _ in examples}
    assert keys[12719] == keys[12727] == "fixed_graded" and keys[12731] == keys[12735] == "fixed_ungraded"
    assert keys[12707] == keys[12732] == "dynamic_published"  # the generated rows of the same skills are untouched
    for rid in (12719, 12727, 12731, 12735):  # the GenCode side still says what it always said: no verified/published component
        assert status[rid]["teacher_status"]["status_key"] == "not_generated" and status[rid]["status"] != "verified"
        assert "固定教材" in status[rid]["display_status"]["label"]
    assert status[12707]["display_status"]["status_key"] == "published"
