# -*- coding: utf-8 -*-
"""Promote bootstrap candidate to verified provider with rollback."""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Any

from core.gencode.domain_bootstrap.candidate_registry import (
    VerifiedCandidateProvider,
    register_verified_candidate,
    unregister_verified_candidate,
)
from core.gencode.domain_bootstrap.candidate_store import CandidateStore
from core.gencode.domain_bootstrap.models import DomainGapReport
from core.gencode.domain_bootstrap.validation_runner import validate_candidate_domain

PROJECT_ROOT = Path(__file__).resolve().parents[3]
VERIFIED_DOMAIN_ROOT = PROJECT_ROOT / "agent_domains_verified"


class PromotionError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


def promote_candidate_to_verified(
    *,
    store: CandidateStore,
    gap_report: DomainGapReport,
    artifact_hash: str,
    teacher_approved: bool,
    registry_store_path: str | Path | None = None,
) -> dict[str, Any]:
    if not teacher_approved:
        raise PromotionError("teacher_not_approved", "teacher approval required")

    validation = validate_candidate_domain(store=store, gap_report=gap_report)
    if not validation.get("passed"):
        raise PromotionError(
            "candidate_validation_failed",
            "candidate gate not passed",
            details={"blockers": validation.get("blockers")},
        )

    gap_id = gap_report.gap_id
    manifest = json.loads(store.read_candidate_file(gap_id, "domain_manifest.json"))
    domain_key = str(manifest.get("domain_key") or "")
    operation_key = str((manifest.get("operations") or [""])[0])
    registry_revision = f"bootstrap-{uuid.uuid4().hex[:12]}"

    target_dir = VERIFIED_DOMAIN_ROOT / gap_id
    backup_dir = VERIFIED_DOMAIN_ROOT / f"{gap_id}.rollback"
    promoted = False
    registered_domain_key = ""

    try:
        if backup_dir.exists():
            shutil.rmtree(backup_dir, ignore_errors=True)
        if target_dir.exists():
            shutil.copytree(target_dir, backup_dir)
            shutil.rmtree(target_dir, ignore_errors=True)

        shutil.copytree(store.candidate_dir(gap_id), target_dir)
        provider = VerifiedCandidateProvider(
            domain_key=domain_key,
            domain_module=f"agent_domains_verified.{gap_id}.domain_module",
            entrypoint=str(manifest.get("entrypoint") or "build_fixture_matrix"),
            capabilities=frozenset(manifest.get("capabilities") or []),
            allowed_operations=(operation_key,),
            gap_id=gap_id,
            artifact_hash=artifact_hash,
            registry_revision=registry_revision,
        )
        register_verified_candidate(provider, store_path=registry_store_path)
        promoted = True
        registered_domain_key = domain_key
    except Exception as exc:
        if promoted and registered_domain_key:
            unregister_verified_candidate(registered_domain_key, store_path=registry_store_path)
        if backup_dir.exists():
            if target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)
            shutil.copytree(backup_dir, target_dir)
        raise PromotionError("promotion_failed", str(exc)) from exc

    return {
        "promoted": True,
        "domain_key": domain_key,
        "registry_revision": registry_revision,
        "artifact_hash": artifact_hash,
        "verified_path": str(target_dir),
    }


def rollback_promotion(domain_key: str, *, registry_store_path: str | Path | None = None) -> None:
    unregister_verified_candidate(domain_key, store_path=registry_store_path)
