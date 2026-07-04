"""Capability Proposal Draft Orchestrator service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.gencode.review_domain_operation_draft_service import (
    build_review_domain_operation_draft,
    _canonical_hash,
    _load_json,
    DEFAULT_PROPOSAL_ROOT,
    DEFAULT_DRAFT_ROOT,
)

PROJECT_ROOT = Path("c:/Python/Mathproject_tvet_mathB")

def build_pending_domain_drafts(
    skill_id: str,
    *,
    dry_run: bool = False,
    proposal_root: str | Path | None = None,
    draft_root: str | Path | None = None,
) -> dict[str, Any]:
    """Scan and process approved capability proposals for a skill, creating operation drafts."""
    p_root = Path(proposal_root or DEFAULT_PROPOSAL_ROOT)
    d_root = Path(draft_root or DEFAULT_DRAFT_ROOT)

    total_proposals = 0
    approved_pending = 0
    skipped_unapproved = 0
    drafts_created = 0
    drafts_reused = 0
    drafts_failed = 0
    per_proposal_results = {}

    if not p_root.is_dir():
        return {
            "total_proposals": 0,
            "approved_pending": 0,
            "skipped_unapproved": 0,
            "drafts_created": 0,
            "drafts_reused": 0,
            "drafts_failed": 0,
            "per_proposal_results": {}
        }

    # Find all JSON proposal files
    for p_file in sorted(p_root.glob("capability_*.json")):
        try:
            proposal = _load_json(p_file)
        except Exception:
            continue

        # Check if proposal is for this skill
        proposal_skills = proposal.get("skill_ids") or [proposal.get("skill_id")]
        if str(skill_id).strip() not in [str(s).strip() for s in proposal_skills if s]:
            continue

        total_proposals += 1
        proposal_id = proposal["proposal_id"]
        status = str(proposal.get("status") or "").strip()

        if status != "approved":
            skipped_unapproved += 1
            per_proposal_results[proposal_id] = {
                "status": "skipped_unapproved",
                "error": None,
                "details": f"Proposal status is {status!r}. Skipped."
            }
            continue

        approved_pending += 1
        proposal_hash = _canonical_hash(proposal)
        
        # Check index for existing revision
        proposal_draft_root = d_root / proposal_id
        index_path = proposal_draft_root / "revisions.json"
        
        reused = False
        if index_path.is_file():
            try:
                index = _load_json(index_path)
                revisions = list(index.get("revisions") or [])
                for entry in revisions:
                    if entry.get("proposal_hash") == proposal_hash:
                        artifact_path = proposal_draft_root / str(entry["artifact"])
                        if artifact_path.is_file():
                            reused = True
                            break
            except Exception:
                pass

        if dry_run:
            if reused:
                drafts_reused += 1
                per_proposal_results[proposal_id] = {
                    "status": "reused",
                    "error": None,
                    "details": f"Planned reuse of existing draft for hash {proposal_hash[:8]}."
                }
            else:
                drafts_created += 1
                per_proposal_results[proposal_id] = {
                    "status": "created",
                    "error": None,
                    "details": f"Planned creation of new draft revision for hash {proposal_hash[:8]}."
                }
            continue

        # Actual execution
        try:
            res = build_review_domain_operation_draft(
                proposal_id,
                proposal_root=p_root,
                draft_root=d_root
            )
            is_reused = res.get("reused_revision", False)
            if is_reused:
                drafts_reused += 1
                per_proposal_results[proposal_id] = {
                    "status": "reused",
                    "error": None,
                    "details": f"Reused existing draft revision {res.get('revision')}."
                }
            else:
                drafts_created += 1
                per_proposal_results[proposal_id] = {
                    "status": "created",
                    "error": None,
                    "details": f"Created new draft revision {res.get('revision')}."
                }
        except Exception as e:
            drafts_failed += 1
            per_proposal_results[proposal_id] = {
                "status": "failed",
                "error": str(e),
                "details": "Failed to build review domain operation draft."
            }

    return {
        "total_proposals": total_proposals,
        "approved_pending": approved_pending,
        "skipped_unapproved": skipped_unapproved,
        "drafts_created": drafts_created,
        "drafts_reused": drafts_reused,
        "drafts_failed": drafts_failed,
        "per_proposal_results": per_proposal_results
    }
