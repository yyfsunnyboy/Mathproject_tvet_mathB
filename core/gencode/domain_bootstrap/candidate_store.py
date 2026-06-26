# -*- coding: utf-8 -*-
"""Isolated persistence for domain bootstrap sessions and artifacts."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from core.gencode.domain_bootstrap.models import BootstrapSession, DomainGapReport

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BOOTSTRAP_ROOT = PROJECT_ROOT / "reports" / "domain_bootstrap"
DEFAULT_CANDIDATE_ROOT = PROJECT_ROOT / "agent_domains_candidate"


class CandidateStore:
    """File-backed store for gap reports and bootstrap sessions."""

    def __init__(
        self,
        *,
        bootstrap_root: str | Path | None = None,
        candidate_root: str | Path | None = None,
    ) -> None:
        self.bootstrap_root = Path(bootstrap_root or DEFAULT_BOOTSTRAP_ROOT)
        self.candidate_root = Path(candidate_root or DEFAULT_CANDIDATE_ROOT)

    def gap_dir(self, gap_id: str) -> Path:
        return self.bootstrap_root / str(gap_id)

    def candidate_dir(self, gap_id: str) -> Path:
        return self.candidate_root / str(gap_id)

    def gap_report_path(self, gap_id: str) -> Path:
        return self.gap_dir(gap_id) / "gap_report.json"

    def session_path(self, gap_id: str) -> Path:
        return self.gap_dir(gap_id) / "bootstrap_session.json"

    def save_gap_report(self, report: DomainGapReport) -> Path:
        path = self.gap_report_path(report.gap_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def load_gap_report(self, gap_id: str) -> DomainGapReport | None:
        path = self.gap_report_path(gap_id)
        if not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return DomainGapReport(**data) if isinstance(data, dict) else None

    def save_session(self, session: BootstrapSession) -> Path:
        path = self.session_path(session.gap_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(session.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def load_session(self, gap_id: str) -> BootstrapSession | None:
        path = self.session_path(gap_id)
        if not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return BootstrapSession.from_dict(data) if isinstance(data, dict) else None

    def ensure_candidate_workspace(self, gap_id: str) -> Path:
        path = self.candidate_dir(gap_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_candidate_file(self, gap_id: str, relative_path: str, content: str) -> Path:
        workspace = self.ensure_candidate_workspace(gap_id)
        target = workspace / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def read_candidate_file(self, gap_id: str, relative_path: str) -> str:
        target = self.candidate_dir(gap_id) / relative_path
        return target.read_text(encoding="utf-8")

    def candidate_file_exists(self, gap_id: str, relative_path: str) -> bool:
        return (self.candidate_dir(gap_id) / relative_path).is_file()

    def write_json(self, gap_id: str, relative_path: str, payload: dict[str, Any]) -> Path:
        return self.write_candidate_file(
            gap_id,
            relative_path,
            json.dumps(payload, ensure_ascii=False, indent=2),
        )

    def rollback_candidate_workspace(self, gap_id: str) -> None:
        path = self.candidate_dir(gap_id)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
