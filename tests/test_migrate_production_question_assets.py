import hashlib
import json
import sqlite3
from pathlib import Path

import scripts.migrate_production_question_assets as migration


def _notes(*, notes_anchor: str, asset_anchor: str) -> str:
    return json.dumps(
        {
            "question_anchor": {"anchor_id": notes_anchor},
            "image_assets": [
                {
                    "visual_classification": "required",
                    "match_score": 0.98,
                    "needs_crop_review": False,
                    "source_page": 7,
                    "bbox": [1, 2, 3, 4],
                    "sha256": "a" * 64,
                    "path": "uploads/question_assets/figure.png",
                    "question_anchor": asset_anchor,
                }
            ],
        }
    )


def test_inventory_requires_asset_to_match_sealed_question_identity() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE textbook_examples "
        "(id INTEGER, source_volume TEXT, source_section TEXT, notes TEXT)"
    )
    connection.executemany(
        "INSERT INTO textbook_examples VALUES (?, ?, ?, ?)",
        [
            (1, "數學B2", "1-4", _notes(notes_anchor="sealed-1", asset_anchor="sealed-1")),
            (2, "數學B2", "1-4", _notes(notes_anchor="sealed-2", asset_anchor="other")),
        ],
    )

    assert [row["example_id"] for row in migration._inventory(connection)] == [1]


def test_rebuild_rejects_source_without_audited_pdf_identity(
    tmp_path: Path, monkeypatch
) -> None:
    pdf = tmp_path / "source.pdf"
    pdf.write_bytes(b"pdf")
    monkeypatch.setattr(migration, "_source_pdf", lambda _volume, _section: pdf)
    monkeypatch.setattr(migration, "ROOT", tmp_path)
    entry = {
        "volume": "數學B9",
        "section": "9-9",
        "asset": {
            "path": "uploads/question_assets/missing.png",
            "sha256": hashlib.sha256(b"old crop").hexdigest(),
            "source_page": 1,
            "bbox": [1, 2, 3, 4],
        },
    }

    source, rebuilt, metadata, error = migration._verified_bytes(entry)

    assert source is None
    assert rebuilt is False
    assert metadata is None
    assert error == "authoritative_source_pdf_identity_missing"
