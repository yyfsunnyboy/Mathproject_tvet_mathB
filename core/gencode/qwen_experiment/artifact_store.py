# -*- coding: utf-8 -*-
"""Artifact store for isolated Qwen Gencode experiment jobs."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from core.gencode.qwen_experiment.constants import DEFAULT_OUTPUT_ROOT

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def utc_now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def sha256_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_output_root(output_root: str | Path | None = None) -> Path:
    raw = str(output_root or DEFAULT_OUTPUT_ROOT).strip() or DEFAULT_OUTPUT_ROOT
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    resolved = path.resolve()
    # Safety: must stay under project reports/gencode_qwen_dryrun (or pytest temp override).
    reports = (PROJECT_ROOT / "reports").resolve()
    under_reports = reports == resolved or reports in resolved.parents
    if under_reports:
        if "gencode_qwen_dryrun" not in resolved.parts:
            resolved = (reports / "gencode_qwen_dryrun").resolve()
        return resolved
    # Allow absolute temp dirs only when they already contain the experiment namespace.
    if "gencode_qwen_dryrun" in resolved.parts:
        return resolved
    raise ValueError(f"output_root_outside_reports:{resolved}")


def make_job_id(example_id: int, seed: int, started_at: str | None = None) -> str:
    stamp = (started_at or utc_now_iso()).replace(":", "").replace("-", "")
    stamp = re.sub(r"[^0-9T]", "", stamp)[:15]
    return f"ex{int(example_id)}_s{int(seed)}_{stamp}"


class ArtifactStore:
    def __init__(self, job_dir: Path) -> None:
        self.job_dir = Path(job_dir)
        self.job_dir.mkdir(parents=True, exist_ok=True)
        self.components_dir = self.job_dir / "components"
        self.components_dir.mkdir(parents=True, exist_ok=True)

    def path(self, name: str) -> Path:
        return self.job_dir / name

    def write_text(self, name: str, content: str) -> Path:
        path = self.path(name)
        path.write_text(str(content), encoding="utf-8")
        return path

    def write_json(self, name: str, payload: dict[str, Any] | list[Any]) -> Path:
        path = self.path(name)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def read_json(self, name: str) -> dict[str, Any] | None:
        path = self.path(name)
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
        return data if isinstance(data, dict) else None

    def exists(self, name: str) -> bool:
        return self.path(name).is_file()

    def write_component_file(self, component_id: str, filename: str, content: str) -> Path:
        comp_dir = self.components_dir / str(component_id)
        comp_dir.mkdir(parents=True, exist_ok=True)
        path = comp_dir / filename
        # Boundary: only under this job's components dir.
        if self.job_dir.resolve() not in path.resolve().parents:
            raise PermissionError(f"artifact_boundary_violation:{path}")
        path.write_text(str(content), encoding="utf-8")
        return path

    def collect_artifact_hashes(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for path in sorted(self.job_dir.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(self.job_dir).as_posix()
            digest = sha256_file(path)
            if digest:
                out[rel] = digest
        return out
