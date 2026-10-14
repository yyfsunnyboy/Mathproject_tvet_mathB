"""B3 visual linkage can be rebuilt from the committed manifest."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from scripts.repair_b3_visual_asset_links import (
    load_manifest,
    repair_b3_visual_asset_links,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "configs" / "b3_visual_asset_links.json"


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT,
            source_curriculum TEXT,
            source_volume TEXT,
            source_chapter TEXT,
            source_section TEXT,
            source_description TEXT,
            problem_text TEXT,
            correct_answer TEXT,
            notes TEXT
        )
        """
    )
    return conn


def test_repair_creates_missing_link_once_and_preserves_question_fields():
    links = load_manifest(MANIFEST)
    target = links[0]
    conn = _conn()
    conn.execute(
        """
        INSERT INTO textbook_examples (
            id, skill_id, source_curriculum, source_volume, source_chapter,
            source_section, source_description, problem_text, correct_answer, notes
        ) VALUES (?, ?, 'vocational', '數學B3', 'ch3', '3-3', '例2', '題幹', '答案', ?)
        """,
        (target["textbook_example_id"], target["skill_id"], json.dumps({"kept": True})),
    )
    first = repair_b3_visual_asset_links(conn, [target], project_root=ROOT, apply=True)
    second = repair_b3_visual_asset_links(conn, [target], project_root=ROOT, apply=True)
    row = conn.execute(
        "SELECT problem_text, correct_answer, skill_id, source_section, notes FROM textbook_examples WHERE id = ?",
        (target["textbook_example_id"],),
    ).fetchone()
    notes = json.loads(row["notes"])
    assert first == {"created": 1, "unchanged": 0}
    assert second == {"created": 0, "unchanged": 1}
    assert notes["kept"] is True
    assert notes["image_assets"] == target["image_assets"]
    assert len(notes["image_assets"]) == 1
    assert row["problem_text"] == "題幹"
    assert row["correct_answer"] == "答案"
    assert row["skill_id"] == target["skill_id"]
    assert row["source_section"] == "3-3"
    for asset in notes["image_assets"]:
        path = str(asset["path"])
        assert not Path(path).is_absolute()
        assert (ROOT / path).is_file()
