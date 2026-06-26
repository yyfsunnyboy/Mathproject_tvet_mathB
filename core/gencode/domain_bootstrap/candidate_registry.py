# -*- coding: utf-8 -*-
"""Verified bootstrap candidate provider overlay (not production registry)."""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_VERIFIED_STORE = PROJECT_ROOT / "reports" / "domain_bootstrap" / "verified_candidates.json"

_lock = threading.Lock()
_verified_providers: dict[str, dict[str, Any]] = {}


@dataclass(frozen=True)
class VerifiedCandidateProvider:
    domain_key: str
    domain_module: str
    entrypoint: str
    capabilities: frozenset[str]
    allowed_operations: tuple[str, ...]
    gap_id: str
    artifact_hash: str
    registry_revision: str

    def to_provider_dict(self) -> dict[str, Any]:
        return {
            "domain_module": self.domain_module,
            "entrypoint": self.entrypoint,
            "capabilities": sorted(self.capabilities),
            "allowed_operations": list(self.allowed_operations),
            "bootstrap_gap_id": self.gap_id,
            "artifact_hash": self.artifact_hash,
            "registry_revision": self.registry_revision,
            "resolution_source": "bootstrap_verified_candidate",
        }


def _store_path(path: str | Path | None = None) -> Path:
    return Path(path or DEFAULT_VERIFIED_STORE)


def _load_store(path: Path) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _save_store(path: Path, payload: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def list_verified_bootstrap_providers() -> dict[str, dict[str, Any]]:
    with _lock:
        return {key: dict(value) for key, value in _verified_providers.items()}


def get_verified_bootstrap_provider(domain_key: str) -> dict[str, Any] | None:
    with _lock:
        row = _verified_providers.get(str(domain_key or "").strip())
        return dict(row) if isinstance(row, dict) else None


def register_verified_candidate(provider: VerifiedCandidateProvider, *, store_path: str | Path | None = None) -> None:
    with _lock:
        _verified_providers[provider.domain_key] = provider.to_provider_dict()
        path = _store_path(store_path)
        payload = _load_store(path)
        payload[provider.domain_key] = provider.to_provider_dict()
        _save_store(path, payload)


def unregister_verified_candidate(domain_key: str, *, store_path: str | Path | None = None) -> None:
    with _lock:
        _verified_providers.pop(str(domain_key or "").strip(), None)
        path = _store_path(store_path)
        payload = _load_store(path)
        payload.pop(str(domain_key or "").strip(), None)
        _save_store(path, payload)


def load_verified_candidates_from_disk(*, store_path: str | Path | None = None) -> None:
    path = _store_path(store_path)
    payload = _load_store(path)
    with _lock:
        _verified_providers.clear()
        _verified_providers.update({k: dict(v) for k, v in payload.items() if isinstance(v, dict)})


def merge_bootstrap_providers(base_providers: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    merged = dict(base_providers)
    merged.update(list_verified_bootstrap_providers())
    return merged
