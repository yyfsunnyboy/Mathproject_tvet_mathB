# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import tempfile
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any

from .schema import ManifestEntry


DEFAULT_MANIFEST_PATH = Path(__file__).resolve().parents[2] / "docs" / "自適應實作" / "skill_manifest.json"
_MANIFEST_CACHE: dict[Path, tuple[tuple[int, int], tuple[ManifestEntry, ...]]] = {}
_MANIFEST_CACHE_LOCK = RLock()


def _file_signature(path: Path) -> tuple[int, int]:
    stat = path.stat()
    return stat.st_mtime_ns, stat.st_size


def ensure_manifest(path: str | Path | None = None) -> Path:
    manifest_path = Path(path) if path else DEFAULT_MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if not manifest_path.exists():
        manifest_path.write_text("[]\n", encoding="utf-8")
    return manifest_path


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding="utf-8") as tmp:
        json.dump(payload, tmp, ensure_ascii=False, indent=2)
        tmp.write("\n")
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def load_manifest(path: str | Path | None = None) -> list[ManifestEntry]:
    manifest_path = ensure_manifest(path).resolve()
    signature = _file_signature(manifest_path)
    with _MANIFEST_CACHE_LOCK:
        cached = _MANIFEST_CACHE.get(manifest_path)
        if cached is not None and cached[0] == signature:
            return deepcopy(list(cached[1]))
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("Manifest root must be a JSON array")
        entries = tuple(ManifestEntry.from_dict(item) for item in raw)
        _MANIFEST_CACHE[manifest_path] = (signature, entries)
        return deepcopy(list(entries))


def save_manifest(entries: list[ManifestEntry], path: str | Path | None = None) -> None:
    manifest_path = ensure_manifest(path).resolve()
    with _MANIFEST_CACHE_LOCK:
        _atomic_write_json(manifest_path, [entry.to_dict() for entry in entries])
        _MANIFEST_CACHE.pop(manifest_path, None)


def register_manifest_entry(entry_payload: dict[str, Any], path: str | Path | None = None) -> ManifestEntry:
    entry = ManifestEntry.from_dict(entry_payload)
    entries = load_manifest(path)

    # Upsert by composite key: skill_id + family_id.
    upserted = False
    for idx, current in enumerate(entries):
        if current.manifest_key == entry.manifest_key:
            entries[idx] = entry
            upserted = True
            break
    if not upserted:
        entries.append(entry)

    save_manifest(entries, path)
    return entry


def resolve_script_path(family_id: str, path: str | Path | None = None, skill_id: str | None = None) -> str | None:
    key = family_id.strip()
    entries = load_manifest(path)
    if skill_id:
        skill_key = skill_id.strip()
        for entry in entries:
            if entry.skill_id == skill_key and entry.family_id == key:
                return entry.script_path
    for entry in entries:
        if entry.family_id == key:
            return entry.script_path
    return None
