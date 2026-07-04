"""Capability Proposal Approval Gate service."""

from __future__ import annotations

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

from core.gencode.review_domain_operation_draft_service import DEFAULT_PROPOSAL_ROOT, _load_json

PROJECT_ROOT = Path("c:/Python/Mathproject_tvet_mathB")

def _canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

def review_capability_proposals(
    skill_id: str,
    decisions: dict[str, str],
    *,
    dry_run: bool = False,
    proposal_root: str | Path | None = None,
) -> dict[str, Any]:
    """Apply human review decisions to proposed capability proposals.
    
    decisions format: { "proposal_id": "approve" | "reject" | "hold" }
    """
    p_root = Path(proposal_root or DEFAULT_PROPOSAL_ROOT)

    total_pending = 0
    approved = 0
    rejected = 0
    held = 0
    unchanged = 0
    failed = 0
    per_proposal_results = {}

    if not p_root.is_dir():
        return {
            "total_pending": 0,
            "approved": 0,
            "rejected": 0,
            "held": 0,
            "unchanged": 0,
            "failed": 0,
            "per_proposal_results": {}
        }

    for p_file in sorted(p_root.glob("capability_*.json")):
        try:
            proposal = _load_json(p_file)
        except Exception:
            continue

        proposal_skills = proposal.get("skill_ids") or [proposal.get("skill_id")]
        if str(skill_id).strip() not in [str(s).strip() for s in proposal_skills if s]:
            continue

        proposal_id = proposal["proposal_id"]
        status = str(proposal.get("status") or "").strip()

        if status == "proposed":
            total_pending += 1
        
        decision = decisions.get(proposal_id)
        
        if not decision:
            unchanged += 1
            per_proposal_results[proposal_id] = {
                "status": "unchanged",
                "error": None,
                "details": f"No decision specified. Status remains {status!r}."
            }
            continue

        # Idempotency check: already reviewed cannot be overwritten
        if status in ["approved", "rejected"]:
            unchanged += 1
            per_proposal_results[proposal_id] = {
                "status": "unchanged",
                "error": None,
                "details": f"Proposal is already {status!r}. Cannot re-review."
            }
            continue

        if decision == "hold":
            held += 1
            per_proposal_results[proposal_id] = {
                "status": "held",
                "error": None,
                "details": "Held in proposed state."
            }
            continue

        elif decision == "reject":
            if dry_run:
                rejected += 1
                per_proposal_results[proposal_id] = {
                    "status": "rejected",
                    "error": None,
                    "details": "Planned rejection."
                }
                continue

            try:
                proposal["status"] = "rejected"
                proposal["rejected_reason"] = "Reviewed decision: reject"
                proposal["reviewed_at"] = datetime.now().isoformat()
                proposal["reviewed_by"] = "human_reviewer"
                
                p_file.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")
                rejected += 1
                per_proposal_results[proposal_id] = {
                    "status": "rejected",
                    "error": None,
                    "details": "Successfully updated status to rejected."
                }
            except Exception as e:
                failed += 1
                per_proposal_results[proposal_id] = {
                    "status": "failed",
                    "error": str(e),
                    "details": "Failed to write rejection."
                }

        elif decision == "approve":
            # 1. Validation schema checks
            missing_fields = []
            for field in ["proposal_id", "required_capabilities", "source_example_ids", "best_reuse_domain", "recommended_action"]:
                if not proposal.get(field):
                    missing_fields.append(field)
            if proposal.get("proposal_schema") != "domain_capability_proposal.v1":
                missing_fields.append("proposal_schema_mismatch")

            if missing_fields:
                failed += 1
                per_proposal_results[proposal_id] = {
                    "status": "failed",
                    "error": f"Schema Validation Failed: Missing/invalid fields: {missing_fields}",
                    "details": "Cannot approve invalid proposal."
                }
                continue

            if dry_run:
                approved += 1
                per_proposal_results[proposal_id] = {
                    "status": "approved",
                    "error": None,
                    "details": "Planned approval."
                }
                continue

            try:
                # Store hash before updating metadata
                p_hash = _canonical_hash(proposal)
                
                proposal["status"] = "approved"
                proposal["reviewed_at"] = datetime.now().isoformat()
                proposal["reviewed_by"] = "human_reviewer"
                proposal["proposal_hash"] = p_hash
                
                p_file.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")
                approved += 1
                per_proposal_results[proposal_id] = {
                    "status": "approved",
                    "error": None,
                    "details": "Successfully updated status to approved."
                }
            except Exception as e:
                failed += 1
                per_proposal_results[proposal_id] = {
                    "status": "failed",
                    "error": str(e),
                    "details": "Failed to write approval."
                }
        else:
            failed += 1
            per_proposal_results[proposal_id] = {
                "status": "failed",
                "error": f"Unknown decision: {decision!r}",
                "details": "Skipped."
            }

    return {
        "total_pending": total_pending,
        "approved": approved,
        "rejected": rejected,
        "held": held,
        "unchanged": unchanged,
        "failed": failed,
        "per_proposal_results": per_proposal_results
    }
