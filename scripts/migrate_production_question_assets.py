"""Migrate gated QUESTION_REQUIRED textbook visuals into Git deployment assets.

The default mode is read-only. ``--apply`` materializes verified files below
``static/question_assets`` and updates existing TextbookExample.notes paths in
one database transaction. It never publishes helpful, solution, or decorative
assets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.question_image_assets import production_question_asset_relpath
from core.textbook_pdf_visual import crop_pdf_bbox
from core.textbook_b2_11 import B2_11_PDF_SHA256
from core.textbook_b2_12 import B2_12_PDF_SHA256
from core.textbook_importer_v3_storage import resolve_project_textbook_source_pair


DEFAULT_DB = ROOT / "instance" / "kumon_math.db"
OLD_ROOT = "uploads/question_assets/"
REQUIRED_CLASSES = {"required", "question_required"}
MIN_SOURCE_FIDELITY_SCORE = 0.90
AUDITED_SOURCE_SHA256 = {
    ("數學B2", "1-1"): B2_11_PDF_SHA256,
    ("數學B2", "1-2"): B2_12_PDF_SHA256,
    # Source pair resolved from the canonical project-local source directory.
    # This authenticates the PDF bytes; page/bbox remain the sealed per-asset mapping.
    ("數學B2", "1-4"): "02f79bcec5f482aa6af27b44fed6ec32ef70a79420408b82a3c10fb5b33f6e1a",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_pair(volume: str, section: str) -> tuple[Path, Path] | None:
    return resolve_project_textbook_source_pair(
        ROOT,
        "vocational",
        volume,
        section,
    )


def _source_pdf(volume: str, section: str) -> Path | None:
    pair = _source_pair(volume, section)
    return pair[1] if pair else None


def _eligible(asset: dict[str, Any]) -> bool:
    classification = str(
        asset.get("visual_classification") or asset.get("image_description") or ""
    ).strip().lower()
    try:
        score = float(asset.get("match_score") or 0.0)
    except (TypeError, ValueError):
        return False
    return bool(
        classification in REQUIRED_CLASSES
        and score >= MIN_SOURCE_FIDELITY_SCORE
        and not asset.get("needs_crop_review")
        and asset.get("source_page")
        and asset.get("bbox")
        and asset.get("sha256")
        and str(asset.get("path") or "").replace("\\", "/").startswith(OLD_ROOT)
    )


def _inventory(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT id, source_volume, source_section, notes "
        "FROM textbook_examples WHERE notes LIKE ? ORDER BY id",
        (f"%{OLD_ROOT}%",),
    ).fetchall()
    inventory: list[dict[str, Any]] = []
    for example_id, volume, section, raw_notes in rows:
        try:
            notes = json.loads(raw_notes or "{}")
        except (TypeError, json.JSONDecodeError):
            continue
        assets = notes.get("image_assets")
        if not isinstance(assets, list):
            continue
        question_anchor = notes.get("question_anchor")
        sealed_anchor_id = str(
            question_anchor.get("anchor_id")
            if isinstance(question_anchor, dict)
            else ""
        ).strip()
        for index, asset in enumerate(assets):
            if (
                isinstance(asset, dict)
                and _eligible(asset)
                and sealed_anchor_id
                and str(asset.get("question_anchor") or "").strip()
                == sealed_anchor_id
            ):
                inventory.append(
                    {
                        "example_id": int(example_id),
                        "volume": str(volume or ""),
                        "section": str(section or ""),
                        "notes": notes,
                        "asset_index": index,
                        "asset": asset,
                    }
                )
    return inventory


def _section_code(section: str) -> str:
    match = re.search(r"(\d+\s*-\s*\d+)", str(section or ""))
    return match.group(1).replace(" ", "") if match else ""


def _verified_bytes(
    entry: dict[str, Any],
) -> tuple[Path | None, bool, dict[str, Any] | None, str | None]:
    asset = entry["asset"]
    expected_sha = str(asset["sha256"]).lower()
    pdf = _source_pdf(entry["volume"], entry["section"])
    audited_sha = AUDITED_SOURCE_SHA256.get(
        (entry["volume"], _section_code(entry["section"]))
    )
    if pdf is not None and pdf.is_file() and audited_sha:
        actual_source_sha = _sha256(pdf)
        if actual_source_sha != audited_sha:
            return None, False, None, "authoritative_source_pdf_sha256_mismatch"
        with tempfile.TemporaryDirectory(prefix="question_asset_migration_") as temp_dir:
            candidate = Path(temp_dir) / "candidate.png"
            image_meta = crop_pdf_bbox(
                pdf,
                int(asset["source_page"]),
                list(asset["bbox"]),
                candidate,
                dpi=int(asset.get("dpi") or 200),
            )
            with tempfile.NamedTemporaryFile(
                prefix="verified_question_asset_", suffix=".png", delete=False
            ) as handle:
                retained = Path(handle.name)
            shutil.copy2(candidate, retained)
        return retained, True, image_meta, None

    old_path = ROOT / str(asset["path"])
    if old_path.is_file() and _sha256(old_path) == expected_sha:
        return old_path, False, None, None
    if pdf is None or not pdf.is_file():
        return None, False, None, "authoritative_source_pdf_missing"
    return None, False, None, "authoritative_source_pdf_identity_missing"


def migrate(*, db_path: Path = DEFAULT_DB, apply: bool = False) -> dict[str, Any]:
    connection = sqlite3.connect(str(db_path))
    try:
        inventory = _inventory(connection)
        result: dict[str, Any] = {
            "mode": "apply" if apply else "dry_run",
            "production_assets_found": len(inventory),
            "rebuilt": 0,
            "migrated": 0,
            "failed": [],
        }
        if not apply:
            result["would_migrate"] = sum(
                1 for row in inventory if (ROOT / str(row["asset"]["path"])).is_file()
                or _source_pdf(row["volume"], row["section"])
            )
            return result

        notes_by_id: dict[int, dict[str, Any]] = {}
        temporary_files: list[Path] = []
        for entry in inventory:
            source, rebuilt, image_meta, error = _verified_bytes(entry)
            if error or source is None:
                result["failed"].append(
                    {"example_id": entry["example_id"], "error": error or "unknown"}
                )
                continue
            if rebuilt:
                temporary_files.append(source)
                result["rebuilt"] += 1

            old_path = str(entry["asset"]["path"])
            new_rel = production_question_asset_relpath(old_path)
            if not new_rel:
                result["failed"].append(
                    {"example_id": entry["example_id"], "error": "invalid_destination"}
                )
                continue
            destination = ROOT / new_rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            expected_destination_sha = str(
                (image_meta or {}).get("sha256") or entry["asset"]["sha256"]
            ).lower()
            if _sha256(destination) != expected_destination_sha:
                destination.unlink(missing_ok=True)
                result["failed"].append(
                    {"example_id": entry["example_id"], "error": "destination_sha256_mismatch"}
                )
                continue

            notes = notes_by_id.setdefault(entry["example_id"], entry["notes"])
            migrated_asset = notes["image_assets"][entry["asset_index"]]
            migrated_asset["path"] = new_rel
            migrated_asset["display_path"] = new_rel
            if image_meta:
                for key in ("width", "height", "file_size", "sha256", "dpi"):
                    migrated_asset[key] = image_meta.get(key)
            result["migrated"] += 1

        try:
            for example_id, notes in notes_by_id.items():
                connection.execute(
                    "UPDATE textbook_examples SET notes = ? WHERE id = ?",
                    (json.dumps(notes, ensure_ascii=False), example_id),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            for path in temporary_files:
                path.unlink(missing_ok=True)
        return result
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    print(json.dumps(migrate(db_path=args.db, apply=args.apply), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
