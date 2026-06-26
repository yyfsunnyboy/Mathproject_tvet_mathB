# -*- coding: utf-8 -*-
"""Deterministic candidate domain scaffold builder."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from core.gencode.domain_bootstrap.candidate_store import CandidateStore
from core.gencode.domain_bootstrap.models import DomainGapReport

ABSTRACT_FIXTURE_CAPABILITY = "fixture_abstract_numeric_computation"
ABSTRACT_FAIL_CAPABILITY = "fixture_abstract_unhealable_gap"


def _domain_key_for_gap(gap_report: DomainGapReport) -> str:
    primary = (gap_report.missing_capabilities or gap_report.required_capabilities or ["unknown"])[0]
    safe = "".join(ch if ch.isalnum() else "_" for ch in primary.lower()).strip("_")
    return f"candidate.{safe}"


def build_candidate_scaffold(
    *,
    store: CandidateStore,
    gap_report: DomainGapReport,
    deliberately_broken: bool = False,
) -> dict[str, Any]:
    gap_id = gap_report.gap_id
    workspace = store.ensure_candidate_workspace(gap_id)
    domain_key = _domain_key_for_gap(gap_report)
    operation_key = f"compute_{domain_key.split('.')[-1]}"
    capabilities = list(gap_report.missing_capabilities or gap_report.required_capabilities or [ABSTRACT_FIXTURE_CAPABILITY])

    oracle_mode = "broken" if deliberately_broken else "valid"
    manifest = {
        "domain_key": domain_key,
        "domain_module": "domain_module",
        "entrypoint": "build_fixture_matrix",
        "capabilities": capabilities,
        "operations": [operation_key],
        "gap_id": gap_id,
        "oracle_mode": oracle_mode,
    }
    store.write_json(gap_id, "domain_manifest.json", manifest)

    domain_module = f'''# -*- coding: utf-8 -*-
"""Candidate domain module — isolated bootstrap artifact."""

from __future__ import annotations

from typing import Any


def build_fixture_matrix(
    *,
    seed: int,
    domain_operation: str,
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    constraints = dict(constraints or {{}})
    values = list(constraints.get("values") or [2, 3, 5])
    total = sum(int(v) for v in values)
    return {{
        "domain_operation": domain_operation,
        "seed": seed,
        "givens": {{"values": values}},
        "answer": total,
        "semantic_answer": total,
        "question_text": f"已知資料為 {{', '.join(str(v) for v in values)}}，求總和。",
        "presentation_mode": "short_answer",
        "answer_type": "integer",
        "checker": "integer_checker",
        "metadata": {{
            "givens": {{"values": values}},
            "target": "sum",
            "derivation": ["sum(values)"],
        }},
    }}
'''
    store.write_candidate_file(gap_id, "domain_module.py", domain_module)

    oracle = f'''# -*- coding: utf-8 -*-
"""Independent mathematical oracle — must not import domain_module."""

from __future__ import annotations

from typing import Any

ORACLE_MODE = "{oracle_mode}"


def oracle_verify_matrix(matrix: dict[str, Any]) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    values = ((matrix.get("givens") or {{}}).get("values") or [])
    if not values:
        blockers.append("oracle_missing_values")
    try:
        expected = sum(int(v) for v in values)
    except Exception:
        blockers.append("oracle_invalid_values")
        return False, blockers
    answer = matrix.get("answer")
    if ORACLE_MODE == "broken":
        blockers.append("oracle_intentionally_broken")
        return False, blockers
    if answer != expected:
        blockers.append("oracle_answer_mismatch")
    return len(blockers) == 0, blockers
'''
    store.write_candidate_file(gap_id, "oracle.py", oracle)

    adapter = {
        "operation_key": operation_key,
        "answer_contract": {
            "answer_type": "integer",
            "checker_key": "integer_checker",
            "presentation_mode": "short_answer",
        },
        "ui_contract": {"presentation_mode": "short_answer"},
    }
    store.write_json(gap_id, "matrix_adapter_draft.json", adapter)

    preview_samples = []
    for seed in (7, 42, 101):
        preview_samples.append(
            {
                "seed": seed,
                "question_text": f"fixture preview seed={seed}",
                "answer": 10,
                "hint": "將所有數值相加。",
            }
        )
    store.write_json(gap_id, "preview_samples.json", {"samples": preview_samples})

    report = {
        "gap_id": gap_id,
        "domain_key": domain_key,
        "operation_key": operation_key,
        "capabilities": capabilities,
        "artifact_paths": [
            "domain_manifest.json",
            "domain_module.py",
            "oracle.py",
            "matrix_adapter_draft.json",
            "preview_samples.json",
        ],
    }
    store.write_json(gap_id, "bootstrap_report.json", report)

    digest = hashlib.sha256(
        json.dumps(manifest, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return {
        "gap_id": gap_id,
        "workspace": str(workspace),
        "domain_key": domain_key,
        "operation_key": operation_key,
        "artifact_hash": digest,
        "manifest": manifest,
    }
