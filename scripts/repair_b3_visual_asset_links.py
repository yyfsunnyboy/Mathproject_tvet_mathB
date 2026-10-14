"""Restore B3 textbook visual linkage from the committed manifest.

Updates only ``textbook_examples.notes["image_assets"]``. Problem text,
answers, skill identity, and source fields stay untouched. Running twice does
not duplicate an asset that is already present.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_DB = ROOT / "instance" / "kumon_math.db"
DEFAULT_MANIFEST = ROOT / "configs" / "b3_visual_asset_links.json"
_PROTECTED_COLUMNS = (
    "problem_text",
    "correct_answer",
    "skill_id",
    "source_section",
    "source_curriculum",
    "source_volume",
    "source_chapter",
    "source_description",
)


def load_manifest(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    links = payload.get("links") if isinstance(payload, dict) else payload
    if not isinstance(links, list) or not links:
        raise ValueError(f"visual link manifest is empty: {path}")
    return links


def _asset_path(asset: dict[str, Any]) -> str:
    path = str(asset.get("path") or asset.get("asset_path") or "").replace("\\", "/")
    if not path or path.startswith("/") or ":" in path[:3]:
        raise ValueError(f"asset path must be project-relative: {path!r}")
    return path


def repair_b3_visual_asset_links(
    conn: sqlite3.Connection,
    links: list[dict[str, Any]],
    *,
    project_root: Path,
    apply: bool,
) -> dict[str, int]:
    created = 0
    unchanged = 0
    for item in links:
        example_id = int(item["textbook_example_id"])
        expected_skill = str(item.get("skill_id") or "")
        assets = item.get("image_assets") or []
        if not isinstance(assets, list) or not assets:
            raise ValueError(f"example {example_id} has no image_assets")
        for asset in assets:
            rel = _asset_path(asset)
            if not (project_root / rel).is_file():
                raise ValueError(f"missing visual file for example {example_id}: {rel}")

        columns = ", ".join(("notes",) + _PROTECTED_COLUMNS)
        row = conn.execute(
            f"SELECT {columns} FROM textbook_examples WHERE id = ?",
            (example_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"textbook example {example_id} is missing")
        protected_before = tuple(row[name] for name in _PROTECTED_COLUMNS)
        if expected_skill and str(row["skill_id"]) != expected_skill:
            raise ValueError(
                f"example {example_id} skill_id {row['skill_id']!r} does not match manifest"
            )
        notes_raw = row["notes"]
        notes = json.loads(notes_raw) if notes_raw else {}
        if not isinstance(notes, dict):
            raise ValueError(f"example {example_id} notes is not an object")
        existing = notes.get("image_assets") or []
        if existing == assets:
            unchanged += 1
            continue
        notes["image_assets"] = assets
        if apply:
            conn.execute(
                "UPDATE textbook_examples SET notes = ? WHERE id = ?",
                (json.dumps(notes, ensure_ascii=False), example_id),
            )
            after = conn.execute(
                f"SELECT {', '.join(_PROTECTED_COLUMNS)} FROM textbook_examples WHERE id = ?",
                (example_id,),
            ).fetchone()
            protected_after = tuple(after[name] for name in _PROTECTED_COLUMNS)
            if protected_after != protected_before:
                raise RuntimeError(f"protected columns changed for example {example_id}")
        created += 1
    if apply:
        conn.commit()
    return {"created": created, "unchanged": unchanged}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--apply", action="store_true", help="write notes.image_assets")
    args = parser.parse_args()
    links = load_manifest(args.manifest)
    uri = f"file:{args.db}?mode={'rw' if args.apply else 'ro'}"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        result = repair_b3_visual_asset_links(
            conn,
            links,
            project_root=ROOT,
            apply=args.apply,
        )
    finally:
        conn.close()
    mode = "applied" if args.apply else "dry-run"
    print(f"{mode} created={result['created']} unchanged={result['unchanged']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
