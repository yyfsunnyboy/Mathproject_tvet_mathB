# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
from copy import deepcopy
from pathlib import Path
from threading import RLock

from .schema import CatalogEntry


DEFAULT_CATALOG_PATH = Path(__file__).resolve().parents[2] / "docs" / "自適應實作" / "skill_breakpoint_catalog.csv"
_CATALOG_CACHE: dict[Path, tuple[tuple[int, int], tuple[CatalogEntry, ...]]] = {}
_CATALOG_CACHE_LOCK = RLock()


def _file_signature(path: Path) -> tuple[int, int]:
    stat = path.stat()
    return stat.st_mtime_ns, stat.st_size


def _read_rows(path: Path) -> list[dict[str, str]]:
    last_error = None
    for encoding in ("utf-8-sig", "utf-8", "cp950"):
        try:
            with path.open("r", encoding=encoding, newline="") as fh:
                reader = csv.DictReader(fh)
                return [dict(row) for row in reader]
        except Exception as exc:  # pragma: no cover
            last_error = exc
    raise RuntimeError(f"Failed to read catalog {path}: {last_error}")


def load_catalog(path: str | Path | None = None) -> list[CatalogEntry]:
    catalog_path = (Path(path) if path else DEFAULT_CATALOG_PATH).resolve()
    if not catalog_path.exists():
        raise FileNotFoundError(f"Catalog file not found: {catalog_path}")

    signature = _file_signature(catalog_path)
    with _CATALOG_CACHE_LOCK:
        cached = _CATALOG_CACHE.get(catalog_path)
        if cached is not None and cached[0] == signature:
            return deepcopy(list(cached[1]))
        rows = _read_rows(catalog_path)
        entries = tuple(CatalogEntry.from_row(row) for row in rows)
        _CATALOG_CACHE[catalog_path] = (signature, entries)
        return deepcopy(list(entries))


def build_family_index(path: str | Path | None = None) -> dict[str, CatalogEntry]:
    entries = load_catalog(path)
    return {f"{entry.skill_id}:{entry.family_id}": entry for entry in entries}
