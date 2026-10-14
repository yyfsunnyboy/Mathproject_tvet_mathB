# -*- coding: utf-8 -*-
"""Classify textbook examples for V3 build: eligible / intentional skip / needs capability."""

from __future__ import annotations

import json
from typing import Any


DISPOSITION_RESOLVABLE = "resolvable"
DISPOSITION_INTENTIONAL_SKIP = "intentional_skip"
DISPOSITION_NEEDS_CAPABILITY = "needs_capability"


def _parse_payload(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if raw is None:
        return {}
    text = str(raw).strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def is_intentional_skip_signal(
    *,
    reason: str = "",
    classification_source: str = "",
    error_log: str = "",
    payload: dict[str, Any] | None = None,
) -> bool:
    """True when Phase1 explicitly blocked the example as non-runtime (intentional skip)."""
    src = str(classification_source or "").strip()
    if src == "phase1_rule_pack_blocked":
        return True

    payload = payload or {}
    nested = payload.get("phase1_classification")
    if isinstance(nested, dict):
        nested_src = str(nested.get("classification_source") or "").strip()
        if nested_src == "phase1_rule_pack_blocked":
            return True
        nested_reason = str(nested.get("reason") or "")
        if nested_reason.startswith("BLOCKED:"):
            return True
        if nested.get("runtime_candidate") is False:
            return True

    preflight = payload.get("phase1_preflight")
    if isinstance(preflight, dict):
        if str(preflight.get("reason") or "").startswith("BLOCKED:"):
            return True

    for text in (reason, error_log, str(payload.get("reason") or "")):
        if str(text).startswith("BLOCKED:") or "BLOCKED:" in str(text):
            return True
    if payload.get("runtime_candidate") is False:
        return True
    if payload.get("intentional_skip") is True:
        return True
    return False


def disposition_from_phase1_probe(probe: dict[str, Any]) -> dict[str, Any]:
    """Map a Phase1 probe result into a build disposition."""
    example_id = int(probe.get("textbook_example_id") or 0)
    if probe.get("resolvable"):
        return {
            "textbook_example_id": example_id,
            "disposition": DISPOSITION_RESOLVABLE,
            "reason": "",
            "problem_type_id": str(probe.get("problem_type_id") or ""),
            "suggested_domain": "",
        }

    reason = str(probe.get("reason") or "").strip()
    source = str(probe.get("classification_source") or "").strip()
    if is_intentional_skip_signal(reason=reason, classification_source=source):
        return {
            "textbook_example_id": example_id,
            "disposition": DISPOSITION_INTENTIONAL_SKIP,
            "reason": reason or "intentional_skip",
            "problem_type_id": "",
            "suggested_domain": "",
        }

    return {
        "textbook_example_id": example_id,
        "disposition": DISPOSITION_NEEDS_CAPABILITY,
        "reason": reason or "unresolved_example",
        "problem_type_id": str(probe.get("problem_type_id") or ""),
        "suggested_domain": str(probe.get("suggested_domain") or probe.get("domain_key") or ""),
    }


def disposition_from_tracker_row(tracker: dict[str, Any] | None, example_id: int) -> str | None:
    """
    Infer disposition from an existing tracker row when Phase1 is not re-run.

    Returns None when tracker evidence is insufficient.
    """
    if not tracker:
        return None
    status = str(tracker.get("gencode_status") or "").strip()
    if status == "verified":
        return DISPOSITION_RESOLVABLE
    if status != "needs_human_review":
        return None

    payload = _parse_payload(tracker.get("induced_spec_payload"))
    error_log = str(tracker.get("gencode_error_log") or "")
    if is_intentional_skip_signal(error_log=error_log, payload=payload):
        return DISPOSITION_INTENTIONAL_SKIP
    return None


def summarize_dispositions(items: list[dict[str, Any]]) -> dict[str, Any]:
    resolvable: list[int] = []
    intentional_skip: list[dict[str, Any]] = []
    needs_capability: list[dict[str, Any]] = []
    for item in items:
        disposition = str(item.get("disposition") or "")
        eid = int(item.get("textbook_example_id") or 0)
        if disposition == DISPOSITION_RESOLVABLE:
            resolvable.append(eid)
        elif disposition == DISPOSITION_INTENTIONAL_SKIP:
            intentional_skip.append(
                {
                    "example_id": eid,
                    "reason": str(item.get("reason") or "intentional_skip"),
                }
            )
        elif disposition == DISPOSITION_NEEDS_CAPABILITY:
            needs_capability.append(
                {
                    "example_id": eid,
                    "reason": str(item.get("reason") or "needs_capability"),
                    "suggested_domain": str(item.get("suggested_domain") or ""),
                    "detected_pattern": str(item.get("problem_type_id") or ""),
                }
            )
    example_count = len(items)
    skip_count = len(intentional_skip)
    eligible_count = max(0, example_count - skip_count)
    return {
        "example_count": example_count,
        "eligible_count": eligible_count,
        "resolvable_ids": resolvable,
        "resolvable_count": len(resolvable),
        "skip_count": skip_count,
        "skip_examples": intentional_skip,
        "needs_capability_count": len(needs_capability),
        "needs_capability_examples": needs_capability,
        "intentional_skip_ids": [int(x["example_id"]) for x in intentional_skip],
        "needs_capability_ids": [int(x["example_id"]) for x in needs_capability],
    }
