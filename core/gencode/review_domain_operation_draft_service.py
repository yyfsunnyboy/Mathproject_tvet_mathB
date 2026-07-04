"""Build review-only Domain operation drafts from approved capability proposals."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROPOSAL_ROOT = PROJECT_ROOT / "reports" / "domain_capability_proposals"
DEFAULT_DRAFT_ROOT = PROJECT_ROOT / "reports" / "domain_operation_drafts"

_PROPOSAL_ID_PATTERN = re.compile(r"^capability_[a-z0-9]+$")


def _configured_root(
    explicit_root: str | Path | None,
    environment_name: str,
    default_root: Path,
) -> Path:
    configured = str(os.environ.get(environment_name) or "").strip()
    return Path(explicit_root or configured or default_root)


def _canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid_json_object:{path}")
    return payload


def _candidate_for_domain(
    proposal: dict[str, Any],
    target_domain: str,
) -> dict[str, Any]:
    for candidate in proposal.get("candidate_domains") or []:
        if isinstance(candidate, dict) and candidate.get("domain_key") == target_domain:
            return candidate
    return {}


def _build_draft(
    proposal: dict[str, Any],
    *,
    proposal_hash: str,
    revision: int,
) -> dict[str, Any]:
    capabilities = [
        str(value).strip()
        for value in proposal.get("required_capabilities") or []
        if str(value or "").strip()
    ]
    capability = capabilities[0] if capabilities else str(proposal.get("missing_operation") or "")
    target_domain = str(proposal.get("best_reuse_domain") or "").strip()
    operation_name = str(proposal.get("missing_operation") or capability).strip()
    if not capability or not target_domain or not operation_name:
        raise ValueError("approved_proposal_missing_draft_inputs")

    candidate = _candidate_for_domain(proposal, target_domain)
    domain_module = str(candidate.get("domain_module") or "").strip()
    implementation_target = (
        domain_module.replace(".", "/") + ".py"
        if domain_module
        else f"core/domain/{target_domain.replace('.', '/')}_domain.py"
    )
    operation_signature = (
        f"build_{operation_name}_matrix(*, seed: int | None = None, "
        f"constraints: dict[str, object] | None = None) -> dict[str, object]"
    )

    return {
        "draft_schema": "review_domain_operation_draft.v1",
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": proposal_hash,
        "revision": revision,
        "capability": capability,
        "target_domain": target_domain,
        "recommendation": proposal.get("recommended_action"),
        "operation_name": operation_name,
        "operation_signature": operation_signature,
        "input_schema": {
            "type": "object",
            "required": ["source_topology"],
            "properties": {
                "source_topology": {"type": "object"},
                "constraints": {"type": "object"},
                "seed": {"type": ["integer", "null"]},
            },
            "additionalProperties": False,
        },
        "output_schema": {
            "type": "object",
            "required": [
                "question",
                "answer",
                "semantic_answer",
                "answer_type",
                "presentation_mode",
                "topology_tags",
            ],
            "properties": {
                "question": {"type": "string"},
                "answer": {},
                "semantic_answer": {},
                "answer_type": {"type": "string"},
                "presentation_mode": {"type": "string"},
                "topology_tags": {"type": "array", "items": {"type": "string"}},
                "choices": {"type": "array"},
                "visual_spec": {"type": ["object", "null"]},
            },
        },
        "mathematical_invariants": [
            "generated givens determine the requested quantities",
            "semantic_answer and displayed answer represent the same mathematical result",
            "all derived values remain consistent with the generated givens",
            "source topology, answer schema, and presentation mode are preserved",
        ],
        "validation_rules": [
            "validate input and output against the draft schemas",
            "validate every declared mathematical invariant",
            "validate source-fidelity against the originating source topology",
            "validate a unique correct choice when choices are present",
            "reject visual metadata that cannot be rendered consistently",
        ],
        "source_example_ids": sorted(
            set(int(value) for value in proposal.get("source_example_ids") or [])
        ),
        "registry_patch_preview": {
            "apply": False,
            "target_file": "core/registry/domain_operation_registry.py",
            "target_domain": target_domain,
            "operation": {
                "operation_key": operation_name,
                "handler": operation_name,
                "provided_capabilities": capabilities or [capability],
            },
        },
        "implementation_file_preview": {
            "apply": False,
            "target_file": implementation_target,
            "operation_signature": operation_signature,
            "body": "raise NotImplementedError('review-only operation draft')",
        },
        "test_file_preview": {
            "apply": False,
            "target_file": f"tests/domain/test_{operation_name}.py",
            "required_cases": [
                "schema contract",
                "mathematical invariants",
                "source topology fidelity",
                "deterministic seeded generation",
            ],
        },
        "status": "draft",
        "production_publish_allowed": False,
        "tracker_status_change": None,
    }


def build_review_domain_operation_draft(
    proposal_id: str,
    *,
    proposal_root: str | Path | None = None,
    draft_root: str | Path | None = None,
    stable_proposal_hash: str | None = None,
) -> dict[str, Any]:
    """Create or reuse a review-only draft revision for an approved proposal.

    Args:
        proposal_id: The proposal ID (must match ``capability_<alphanum>`` pattern).
        proposal_root: Optional override for the proposals directory.
        draft_root: Optional override for the drafts directory.
        stable_proposal_hash: Pre-computed stable hash of the proposal's content
            (excluding volatile fields such as ``reviewed_at``, ``proposal_hash``,
            ``status``, etc.).  When provided, the function uses this value directly
            instead of hashing the full on-disk proposal dict.  This allows callers
            to ensure revision idempotency without modifying the proposal file.
            When *not* provided the function falls back to hashing the full proposal
            dict (legacy behaviour, requires ``status == "approved"`` on disk).
    """
    normalized_id = str(proposal_id or "").strip()
    if not _PROPOSAL_ID_PATTERN.fullmatch(normalized_id):
        raise ValueError("invalid_capability_proposal_id")

    proposals = _configured_root(
        proposal_root,
        "DOMAIN_CAPABILITY_PROPOSAL_ROOT",
        DEFAULT_PROPOSAL_ROOT,
    )
    proposal_path = proposals / f"{normalized_id}.json"
    if not proposal_path.is_file():
        raise FileNotFoundError(f"capability_proposal_not_found:{normalized_id}")

    proposal = _load_json(proposal_path)
    if proposal.get("proposal_id") != normalized_id:
        raise ValueError("capability_proposal_id_mismatch")

    if stable_proposal_hash is not None:
        # Caller has pre-computed a stable hash from content-only fields.
        # No disk mutation required; skip the status check (caller handles approval).
        proposal_hash = stable_proposal_hash
    else:
        # Legacy path: require status == "approved" and hash the full dict.
        status = str(proposal.get("status") or "").strip()
        if status != "approved":
            raise ValueError(f"capability_proposal_not_approved:{status or 'missing'}")
        proposal_hash = _canonical_hash(proposal)

    drafts = _configured_root(
        draft_root,
        "DOMAIN_OPERATION_DRAFT_ROOT",
        DEFAULT_DRAFT_ROOT,
    )
    proposal_draft_root = drafts / normalized_id
    index_path = proposal_draft_root / "revisions.json"
    index = (
        _load_json(index_path)
        if index_path.is_file()
        else {
            "draft_index_schema": "review_domain_operation_draft_index.v1",
            "proposal_id": normalized_id,
            "revisions": [],
        }
    )
    revisions = list(index.get("revisions") or [])
    for entry in revisions:
        if entry.get("proposal_hash") != proposal_hash:
            continue
        artifact_path = proposal_draft_root / str(entry["artifact"])
        if artifact_path.is_file():
            draft = _load_json(artifact_path)
            return {
                **draft,
                "artifact_path": str(artifact_path),
                "index_path": str(index_path),
                "reused_revision": True,
            }

    revision = max((int(entry.get("revision") or 0) for entry in revisions), default=0) + 1
    revision_dir = proposal_draft_root / f"revision_{revision:04d}"
    artifact_path = revision_dir / "domain_operation_draft.json"
    draft = _build_draft(proposal, proposal_hash=proposal_hash, revision=revision)

    revision_dir.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(draft, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    revisions.append(
        {
            "revision": revision,
            "proposal_hash": proposal_hash,
            "artifact": str(artifact_path.relative_to(proposal_draft_root)),
        }
    )
    index["revisions"] = revisions
    proposal_draft_root.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {
        **draft,
        "artifact_path": str(artifact_path),
        "index_path": str(index_path),
        "reused_revision": False,
    }
