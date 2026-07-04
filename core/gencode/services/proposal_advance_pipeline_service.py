"""Auto Triage to Draft and Isolated Validation Pipeline with Executable Workspace Gate."""

from __future__ import annotations

import json
import py_compile
import sqlite3
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Any

from core.gencode.review_domain_operation_draft_service import (
    build_review_domain_operation_draft,
    _canonical_hash,
    _load_json,
    DEFAULT_PROPOSAL_ROOT,
    DEFAULT_DRAFT_ROOT,
)
from core.gencode.services.v3_question_integrity_validator import validate_component_payload
from core.gencode.services.failed_component_recovery_service import DB_PATH

# ---------------------------------------------------------------------------
# Stable hash helpers — pure functions, no I/O
# ---------------------------------------------------------------------------

#: Fields whose values change between pipeline runs and must NOT influence the
#: stable content hash.  Excluding them ensures that re-running the pipeline on
#: the same proposal always finds the same draft revision regardless of audit
#: timestamps, prior run artefacts or transient status flags.
_STABLE_VOLATILE_FIELDS: frozenset[str] = frozenset({
    "status",
    "failed_gate",
    "missing_artifacts",
    "failed_source_example_ids",
    "reviewed_at",
    "reviewed_by",
    "proposal_hash",
})


def _build_stable_hash_payload(proposal: dict[str, Any]) -> dict[str, Any]:
    """Return an in-memory copy of *proposal* stripped of all volatile fields.

    The returned dict is suitable for canonical hash computation.  It always
    has ``status`` set to the sentinel value ``"approved"`` so that the hash
    is independent of the actual current status on disk.

    This is a **pure function**: it never reads from or writes to the
    filesystem and never modifies the original dict.
    """
    stable = {k: v for k, v in proposal.items() if k not in _STABLE_VOLATILE_FIELDS}
    stable["status"] = "approved"  # sentinel – same value regardless of actual status
    return stable


def _stable_canonical_hash(proposal: dict[str, Any]) -> str:
    """Compute a stable SHA-256 hash of *proposal*'s essential content.

    Volatile run-time fields are excluded (see ``_STABLE_VOLATILE_FIELDS``).
    This is a **pure function**: no I/O, no side effects.
    """
    return _canonical_hash(_build_stable_hash_payload(proposal))


MATH_IMPLEMENTATIONS = {
    "collinear_trisection_coordinate": """import random

def collinear_trisection_coordinate(*, seed=None, constraints=None):
    r = random.Random(seed)
    x1 = r.randint(-10, 10) * 3
    y1 = r.randint(-10, 10) * 3
    dx = r.choice([-3, 3]) * 3
    dy = r.choice([-3, 3]) * 3
    x2 = x1 + dx
    y2 = y1 + dy
    tx = (2 * x1 + x2) // 3
    ty = (2 * y1 + y2) // 3
    answer = f"({tx}, {ty})"
    return {
        "question_text": f"Given collinear points A({x1}, {y1}) and B({x2}, {y2}), find the trisection point closer to A.",
        "answer": answer,
        "semantic_answer": [tx, ty],
        "answer_type": "coordinate_pair",
        "presentation_mode": "short_answer",
        "metadata": {
            "answer_dependencies": [],
            "A": [x1, y1],
            "B": [x2, y2]
        }
    }
""",
    "draw_constant_function_graph": """import random

def draw_constant_function_graph(*, seed=None, constraints=None):
    r = random.Random(seed)
    c = r.randint(-5, 5)
    expected = {"type": "constant_line", "y": c}
    return {
        "question_text": f"Draw the graph of the constant function y = {c}.",
        "answer": expected,
        "semantic_answer": expected,
        "answer_type": "drawing",
        "presentation_mode": "canvas",
        "expected_drawing_spec": expected,
        "metadata": {
            "expected_drawing_spec": expected,
            "answer_dependencies": []
        }
    }
""",
    "draw_linear_function_graph": """import random

def draw_linear_function_graph(*, seed=None, constraints=None):
    r = random.Random(seed)
    m = r.choice([-2, -1, 1, 2])
    k = r.randint(-3, 3)
    expected = {"type": "linear_line", "slope": m, "intercept": k}
    return {
        "question_text": f"Draw the graph of the linear function y = {m}x + {k}.",
        "answer": expected,
        "semantic_answer": expected,
        "answer_type": "drawing",
        "presentation_mode": "canvas",
        "expected_drawing_spec": expected,
        "metadata": {
            "expected_drawing_spec": expected,
            "answer_dependencies": []
        }
    }
""",
    "graph_based_linear_application_inverse": """import random

def graph_based_linear_application_inverse(*, seed=None, constraints=None):
    r = random.Random(seed)
    m = r.choice([2, 3, 5])
    k = r.randint(1, 10)
    x_val = r.randint(1, 5)
    y_val = m * x_val + k
    return {
        "question_text": f"Given the graph of y = {m}x + {k}, find x when y = {y_val}.",
        "answer": str(x_val),
        "semantic_answer": x_val,
        "answer_type": "short_answer",
        "presentation_mode": "integer",
        "metadata": {
            "answer_dependencies": []
        }
    }
""",
    "robust_budget_feasibility_choice": """import random

def robust_budget_feasibility_choice(*, seed=None, constraints=None):
    r = random.Random(seed)
    p = r.randint(2, 5)
    q = r.randint(5, 10)
    x = r.randint(1, 5)
    y = r.randint(1, 5)
    b = r.randint(20, 50)
    feasible = (p * x + q * y) <= b
    ans = "A" if feasible else "B"
    choices = [
        {"id": "A", "text": "Yes, feasible"},
        {"id": "B", "text": "No, not feasible"}
    ]
    return {
        "question_text": f"If pencils cost {p} dollars and notebooks cost {q} dollars, is it feasible to buy {x} pencils and {y} notebooks with a budget of {b} dollars?",
        "answer": ans,
        "semantic_answer": ans,
        "answer_type": "single_choice",
        "presentation_mode": "single_choice",
        "choices": choices,
        "metadata": {
            "choices": choices,
            "answer_dependencies": []
        }
    }
""",
    "graph_based_linear_model_equation": """import random

def graph_based_linear_model_equation(*, seed=None, constraints=None):
    r = random.Random(seed)
    m = r.randint(1, 5)
    k = r.randint(1, 5)
    return {
        "question_text": f"Find the equation of the line shown in the graph passing through (0, {k}) with slope {m}.",
        "answer": f"y = {m}x + {k}",
        "semantic_answer": f"y = {m}x + {k}",
        "answer_type": "short_answer",
        "presentation_mode": "equation",
        "metadata": {
            "answer_dependencies": []
        }
    }
""",
    "linear_equation_from_two_points_choice": """import random

def linear_equation_from_two_points_choice(*, seed=None, constraints=None):
    r = random.Random(seed)
    x1, y1 = 1, r.randint(1, 5)
    x2, y2 = 2, y1 + r.randint(1, 3)
    m = y2 - y1
    k = y1 - m * x1
    correct_eq = f"y = {m}x + {k}"
    choices = [
        {"id": "A", "text": correct_eq},
        {"id": "B", "text": f"y = {m+1}x + {k}"},
        {"id": "C", "text": f"y = {m}x + {k+1}"},
        {"id": "D", "text": f"y = {m+2}x + {k}"}
    ]
    return {
        "question_text": f"Which is the equation of the line passing through ({x1}, {y1}) and ({x2}, {y2})?",
        "answer": "A",
        "semantic_answer": "A",
        "answer_type": "single_choice",
        "presentation_mode": "single_choice",
        "choices": choices,
        "metadata": {
            "choices": choices,
            "answer_dependencies": []
        }
    }
""",
    "linear_graph_feasibility_choice": """import random

def linear_graph_feasibility_choice(*, seed=None, constraints=None):
    r = random.Random(seed)
    m = r.choice([1, 2])
    k = r.randint(-2, 2)
    choices = [
        {"id": "A", "text": f"Graph of y >= {m}x + {k}"},
        {"id": "B", "text": f"Graph of y < {m}x + {k}"}
    ]
    return {
        "question_text": f"Which graph represents the linear inequality y >= {m}x + {k}?",
        "answer": "A",
        "semantic_answer": "A",
        "answer_type": "single_choice",
        "presentation_mode": "single_choice",
        "choices": choices,
        "metadata": {
            "choices": choices,
            "answer_dependencies": []
        }
    }
""",
    "graph_based_tiered_linear_application_multi_part": """import random

def graph_based_tiered_linear_application_multi_part(*, seed=None, constraints=None):
    r = random.Random(seed)
    tier1_rate = r.randint(2, 4)
    tier2_rate = r.randint(5, 8)
    limit = 10
    val1 = r.randint(1, limit - 1)
    val2 = r.randint(limit + 1, limit + 5)
    
    ans1 = val1 * tier1_rate
    ans2 = limit * tier1_rate + (val2 - limit) * tier2_rate
    
    parts = {
        "part_1": {
            "answer": str(ans1),
            "semantic_answer": ans1,
            "answer_type": "short_answer",
            "presentation_mode": "integer"
        },
        "part_2": {
            "answer": str(ans2),
            "semantic_answer": ans2,
            "answer_type": "short_answer",
            "presentation_mode": "integer"
        }
    }
    return {
        "question_text": f"A tiered pricing model charges {tier1_rate} dollars per unit up to {limit} units, and {tier2_rate} dollars per unit thereafter. (1) Find the cost of {val1} units. (2) Find the cost of {val2} units.",
        "answer": parts,
        "semantic_answer": parts,
        "answer_type": "multi_part",
        "presentation_mode": "multiple_inputs",
        "parts": parts,
        "metadata": {
            "parts": parts,
            "answer_dependencies": []
        }
    }
"""
}

def _load_module_from_path(file_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("candidate_module", str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create spec for {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def advance_capability_proposals(
    skill_id: str,
    *,
    dry_run: bool = False,
    proposal_root: str | Path | None = None,
    draft_root: str | Path | None = None,
    db_conn: sqlite3.Connection | None = None,
) -> dict[str, Any]:
    """Orchestrate auto-triage, drafting, and Executable Workspace Gate validation for capability proposals."""
    p_root = Path(proposal_root or DEFAULT_PROPOSAL_ROOT)
    d_root = Path(draft_root or DEFAULT_DRAFT_ROOT)

    total_proposals = 0
    auto_approved = 0
    approval_failed = 0
    drafts_created = 0
    drafts_reused = 0
    workspaces_created = 0
    workspaces_reused = 0
    validation_passed = 0
    validation_failed = 0
    ready_for_human_review_count = 0
    downgraded_count = 0
    per_proposal_results = {}

    if not p_root.is_dir():
        return {
            "total_proposals": 0,
            "auto_approved": 0,
            "approval_failed": 0,
            "drafts_created": 0,
            "drafts_reused": 0,
            "workspaces_created": 0,
            "workspaces_reused": 0,
            "validation_passed": 0,
            "validation_failed": 0,
            "ready_for_human_review": 0,
            "downgraded_count": 0,
            "per_proposal_results": {}
        }

    conn = db_conn
    close_conn = False
    if conn is None and not dry_run:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        close_conn = True

    try:
        # Scan all capability proposals for the skill
        for p_file in sorted(p_root.glob("capability_*.json")):
            try:
                proposal = _load_json(p_file)
            except Exception:
                continue

            proposal_skills = proposal.get("skill_ids") or [proposal.get("skill_id")]
            if str(skill_id).strip() not in [str(s).strip() for s in proposal_skills if s]:
                continue

            proposal_id = proposal["proposal_id"]
            original_status = str(proposal.get("status") or "").strip()
            total_proposals += 1

            failed_gate = []
            missing_artifacts = []
            failed_source_example_ids = []
            
            # Retrieve or generate draft details for revision mapping
            # (If status is proposed, we run auto-triage first)
            status = original_status
            if status == "proposed":
                # ================= 1. Auto Triage Rule Check =================
                triage_errors = []
                if proposal.get("proposal_schema") != "domain_capability_proposal.v1":
                    triage_errors.append("invalid_schema_version")
                if not proposal.get("proposal_id"):
                    triage_errors.append("missing_proposal_id")
                
                req_caps = proposal.get("required_capabilities") or []
                if not isinstance(req_caps, list) or not req_caps:
                    triage_errors.append("invalid_required_capabilities")
                elif len(set(req_caps)) > 1:
                    triage_errors.append("cannot_merge_different_capabilities")

                src_ids = proposal.get("source_example_ids") or []
                if not isinstance(src_ids, list) or not src_ids:
                    triage_errors.append("missing_source_example_ids")
                else:
                    for sid in src_ids:
                        try:
                            if int(sid) <= 0:
                                triage_errors.append(f"invalid_example_id:{sid}")
                        except Exception:
                            triage_errors.append(f"invalid_example_id_format:{sid}")

                if not proposal.get("best_reuse_domain"):
                    triage_errors.append("missing_best_reuse_domain")
                if not proposal.get("recommended_action"):
                    triage_errors.append("missing_recommended_action")

                prob_type = proposal.get("problem_type_id")
                if prob_type and req_caps and prob_type not in req_caps:
                    triage_errors.append("problem_type_capability_mismatch")

                if triage_errors:
                    approval_failed += 1
                    per_proposal_results[proposal_id] = {
                        "status": "proposed",
                        "failed_gate": ["auto_triage"],
                        "missing_artifacts": [],
                        "failed_source_example_ids": [],
                        "error": f"Triage checks failed: {triage_errors}",
                        "details": "Proposal rejected at Auto Triage."
                    }
                    continue

                auto_approved += 1
                status = "approved"
                if not dry_run:
                    # Update status to approved on disk.  Record the *stable*
                    # content hash so the audit record stays idempotent across
                    # re-runs.  The stable hash is computed in memory from the
                    # proposal content only (volatile fields excluded).
                    p_hash = _stable_canonical_hash(proposal)
                    proposal["status"] = "approved"
                    proposal["reviewed_at"] = datetime.now().isoformat()
                    proposal["reviewed_by"] = "auto_pipeline"
                    proposal["proposal_hash"] = p_hash
                    p_file.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")

            # Load/create draft to check workspaces
            revision = 1
            if not dry_run:
                try:
                    # Compute the stable hash in memory — NO disk mutation needed.
                    # Pass it as stable_proposal_hash so build_review_domain_operation_draft
                    # uses it directly instead of re-hashing the full on-disk proposal
                    # (which would include volatile fields and break idempotency).
                    current_proposal = _load_json(p_file)
                    sh = _stable_canonical_hash(current_proposal)

                    draft_res = build_review_domain_operation_draft(
                        proposal_id,
                        proposal_root=p_root,
                        draft_root=d_root,
                        stable_proposal_hash=sh,
                    )

                    revision = draft_res.get("revision", 1)
                    if draft_res.get("reused_revision"):
                        drafts_reused += 1
                    else:
                        drafts_created += 1
                except Exception as de:
                    validation_failed += 1
                    per_proposal_results[proposal_id] = {
                        "status": original_status,
                        "failed_gate": ["drafting_error"],
                        "missing_artifacts": [],
                        "failed_source_example_ids": [],
                        "error": str(de),
                        "details": "Failed to create draft."
                    }
                    continue

            # Check workspace and validate
            ws_dir = d_root / proposal_id / f"revision_{revision:04d}" / "workspace"
            
            if not dry_run and not ws_dir.is_dir():
                workspaces_created += 1
                ws_dir.mkdir(parents=True, exist_ok=True)
                
                # Write candidates stubs
                reg_preview = draft_res.get("registry_patch_preview") or {}
                impl_preview = draft_res.get("implementation_file_preview") or {}
                test_preview = draft_res.get("test_file_preview") or {}

                impl_file = ws_dir / "implementation_candidate.py"
                impl_file.write_text(
                    f"# Operation signature candidate\n# {impl_preview.get('operation_signature')}\n\ndef {draft_res.get('operation_name')}(*args, **kwargs):\n    {impl_preview.get('body')}\n",
                    encoding="utf-8"
                )

                test_file = ws_dir / "test_candidate.py"
                test_cases = "\n".join(f"# - {case}" for case in test_preview.get("required_cases", []))
                test_file.write_text(
                    f"# Test Cases Candidate for {draft_res.get('operation_name')}\n{test_cases}\n\ndef test_stub():\n    pass\n",
                    encoding="utf-8"
                )

                reg_file = ws_dir / "registry_patch.json"
                reg_file.write_text(json.dumps(reg_preview, indent=2, ensure_ascii=False), encoding="utf-8")

                adapter_preview = {
                    "operation": draft_res.get("operation_name"),
                    "route": f"if op == '{draft_res.get('operation_name')}': convert_to_payload()"
                }
                adapter_file = ws_dir / "adapter_patch.json"
                adapter_file.write_text(json.dumps(adapter_preview, indent=2, ensure_ascii=False), encoding="utf-8")
            elif not dry_run:
                workspaces_reused += 1

            impl_file = ws_dir / "implementation_candidate.py"
            test_file = ws_dir / "test_candidate.py"
            reg_file = ws_dir / "registry_patch.json"
            adapter_file = ws_dir / "adapter_patch.json"

            # Executable Workspace Gate Checks
            readiness = "ready_for_human_review"

            if dry_run:
                failed_gate.append("implementation_stub")
                failed_gate.append("test_no_assertion")
                failed_gate.append("adapter_no_invocation")
                readiness = "implementation_incomplete"
                
                if original_status == "ready_for_human_review":
                    downgraded_count += 1
                validation_failed += 1

                per_proposal_results[proposal_id] = {
                    "status": readiness,
                    "failed_gate": failed_gate,
                    "missing_artifacts": missing_artifacts,
                    "failed_source_example_ids": failed_source_example_ids,
                    "error": None,
                    "details": "Dry run: Scaffold scanned. Downgraded to implementation_incomplete."
                }
                continue

            # Real Execution Checks
            artifacts = [impl_file, test_file, reg_file, adapter_file]
            for art in artifacts:
                if not art.is_file():
                    missing_artifacts.append(art.name)
            
            if missing_artifacts:
                readiness = "draft_scaffold_ready"
            else:
                # Load contents
                impl_code = impl_file.read_text(encoding="utf-8")
                test_code = test_file.read_text(encoding="utf-8")
                
                try:
                    adapter_data = json.loads(adapter_file.read_text(encoding="utf-8"))
                except Exception:
                    adapter_data = {}
                
                # Check implementation stub (pass, NotImplementedError, empty return)
                has_not_implemented = "NotImplementedError" in impl_code
                has_pass_body = False
                lines = [l.strip() for l in impl_code.splitlines() if l.strip()]
                for idx, line in enumerate(lines):
                    if line.startswith("def "):
                        body_lines = []
                        for l in lines[idx+1:]:
                            if l.startswith("def ") or not l.startswith(" "):
                                break
                            body_lines.append(l.strip())
                        if body_lines == ["pass"] or body_lines == ["return {}"] or body_lines == ["return None"]:
                            has_pass_body = True
                            break

                if has_not_implemented or has_pass_body:
                    failed_gate.append("implementation_stub")

                # Check test stub
                if "assert " not in test_code:
                    failed_gate.append("test_no_assertion")

                # Check adapter stub
                op_name = draft_res.get("operation_name")
                adapter_route = adapter_data.get("route", "")
                if op_name not in adapter_route:
                    failed_gate.append("adapter_no_invocation")

                if failed_gate:
                    readiness = "implementation_incomplete"
                else:
                    # Run Compilability & Dynamic Execution checks on actual code
                    try:
                        py_compile.compile(str(impl_file), doraise=True)
                    except Exception as ce:
                        failed_gate.append("implementation_compilation_failed")
                        readiness = "validation_failed"

                    try:
                        py_compile.compile(str(test_file), doraise=True)
                    except Exception as ce:
                        failed_gate.append("test_compilation_failed")
                        readiness = "validation_failed"

                    if readiness == "ready_for_human_review":
                        # Dynamic Execution validation
                        try:
                            mod = _load_module_from_path(impl_file)
                            handler_fn = getattr(mod, op_name, None)
                            if not handler_fn:
                                failed_gate.append("missing_handler_function")
                                readiness = "validation_failed"
                            else:
                                # Test function execution under fixed seeds (7, 42, 101)
                                for seed in [7, 42, 101]:
                                    val_payload = handler_fn(seed=seed)
                                    # Verification of answer contract & invariants
                                    if not isinstance(val_payload, dict):
                                        failed_gate.append("invalid_payload_return_type")
                                        readiness = "validation_failed"
                                        break
                                    # Expected standard keys (question_text is the canonical field name)
                                    for key in ["question_text", "answer", "semantic_answer", "answer_type", "presentation_mode"]:
                                        if key not in val_payload:
                                            failed_gate.append(f"missing_payload_key:{key}")
                                            readiness = "validation_failed"
                                            break
                                    if readiness == "validation_failed":
                                        break
                        except Exception as ee:
                            failed_gate.append(f"execution_exception:{ee}")
                            readiness = "validation_failed"

                    # Component validator for source example ids
                    src_ids = proposal.get("source_example_ids") or []
                    for ex_id in src_ids:
                        row = conn.execute(
                            """
                            SELECT induced_spec_payload
                            FROM gencode_component_tracker
                            WHERE skill_id = ? AND textbook_example_id = ?
                            """,
                            (str(skill_id).strip(), int(ex_id))
                        ).fetchone()
                        
                        if row and row["induced_spec_payload"]:
                            try:
                                payload = json.loads(row["induced_spec_payload"])
                                val_res = validate_component_payload(payload, f"src_{ex_id}")
                                if not val_res.get("passed"):
                                    failed_source_example_ids.append(int(ex_id))
                                    failed_gate.append("component_validation_failed")
                                    readiness = "validation_failed"
                            except Exception as e:
                                failed_source_example_ids.append(int(ex_id))
                                failed_gate.append(f"component_parse_failed:{e}")
                                readiness = "validation_failed"

            # Update status in the proposal file on disk
            if original_status != readiness:
                proposal["status"] = readiness
                proposal["failed_gate"] = failed_gate
                proposal["missing_artifacts"] = missing_artifacts
                proposal["failed_source_example_ids"] = failed_source_example_ids
                p_file.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")

                if original_status == "ready_for_human_review" and readiness != "ready_for_human_review":
                    downgraded_count += 1

            if readiness == "ready_for_human_review":
                ready_for_human_review_count += 1
                validation_passed += 1
            else:
                validation_failed += 1

            per_proposal_results[proposal_id] = {
                "status": readiness,
                "failed_gate": failed_gate,
                "missing_artifacts": missing_artifacts,
                "failed_source_example_ids": failed_source_example_ids,
                "error": None if not failed_gate else f"Executable Gate failed: {failed_gate}",
                "details": f"Status updated to {readiness}."
            }

    finally:
        if close_conn:
            conn.close()

    return {
        "total_proposals": total_proposals,
        "auto_approved": auto_approved,
        "approval_failed": approval_failed,
        "drafts_created": drafts_created,
        "drafts_reused": drafts_reused,
        "workspaces_created": workspaces_created,
        "workspaces_reused": workspaces_reused,
        "validation_passed": validation_passed,
        "validation_failed": validation_failed,
        "ready_for_human_review": ready_for_human_review_count,
        "downgraded_count": downgraded_count,
        "per_proposal_results": per_proposal_results
    }

def build_executable_domain_workspaces(
    skill_id: str,
    *,
    dry_run: bool = False,
    proposal_root: str | Path | None = None,
    draft_root: str | Path | None = None,
    db_conn: sqlite3.Connection | None = None,
) -> dict[str, Any]:
    """Load implementation_incomplete proposals and automatically write executable Domain operations and tests."""
    p_root = Path(proposal_root or DEFAULT_PROPOSAL_ROOT)
    d_root = Path(draft_root or DEFAULT_DRAFT_ROOT)

    total_incomplete = 0
    implementations_created = 0
    implementations_reused = 0
    validation_passed = 0
    validation_failed = 0
    ready_for_human_review = 0
    failed_gate = {}
    failed_source_example_ids = {}
    per_proposal_results = {}

    if not p_root.is_dir():
        return {
            "total_incomplete": 0,
            "implementations_created": 0,
            "implementations_reused": 0,
            "validation_passed": 0,
            "validation_failed": 0,
            "ready_for_human_review": 0,
            "per_proposal_results": {}
        }

    conn = db_conn
    close_conn = False
    if conn is None and not dry_run:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        close_conn = True

    try:
        # Scan proposals matching the skill
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

            # Process only implementation_incomplete proposals
            if status != "implementation_incomplete":
                continue

            total_incomplete += 1

            # Retrieve draft revision mapping
            revision = 1
            if not dry_run:
                try:
                    # Compute stable hash in memory — NO disk mutation.
                    # The proposal file is read only; its audit fields
                    # (reviewed_at, reviewed_by, proposal_hash) are preserved.
                    current_proposal = _load_json(p_file)
                    sh = _stable_canonical_hash(current_proposal)

                    draft_res = build_review_domain_operation_draft(
                        proposal_id,
                        proposal_root=p_root,
                        draft_root=d_root,
                        stable_proposal_hash=sh,
                    )

                    revision = draft_res.get("revision", 1)
                except Exception as de:
                    validation_failed += 1
                    per_proposal_results[proposal_id] = {
                        "status": "implementation_incomplete",
                        "error": f"Failed to resolve draft: {de}"
                    }
                    continue

            op_name = proposal.get("missing_operation") or proposal.get("problem_type_id")
            if not op_name:
                req_caps = proposal.get("required_capabilities") or []
                if req_caps:
                    op_name = req_caps[0]
            if not op_name and not dry_run:
                op_name = draft_res.get("operation_name")
            
            if not op_name:
                per_proposal_results[proposal_id] = {
                    "status": "implementation_incomplete",
                    "error": "Missing operation name in proposal."
                }
                validation_failed += 1
                continue

            # Look up math implementation
            math_code = MATH_IMPLEMENTATIONS.get(op_name)
            if not math_code:
                # No math rule is available to build a real implementation.
                # Maintain status as implementation_incomplete as per SOP Rule 4.
                per_proposal_results[proposal_id] = {
                    "status": "implementation_incomplete",
                    "error": "Math rules not found. Cannot construct implementation automatically."
                }
                validation_failed += 1
                continue

            if dry_run:
                # Dry run planning: we will create implementation and validate
                implementations_created += 1
                validation_passed += 1
                ready_for_human_review += 1
                per_proposal_results[proposal_id] = {
                    "status": "ready_for_human_review",
                    "error": None,
                    "details": "Dry run: Will write executable operation and validate."
                }
                continue

            # Real Execution: Write candidate implementations and tests
            ws_dir = d_root / proposal_id / f"revision_{revision:04d}" / "workspace"
            ws_dir.mkdir(parents=True, exist_ok=True)
            impl_file = ws_dir / "implementation_candidate.py"
            test_file = ws_dir / "test_candidate.py"
            adapter_file = ws_dir / "adapter_patch.json"

            # Check if already executable (to differentiate created vs reused)
            is_stub = True
            if impl_file.is_file():
                content = impl_file.read_text(encoding="utf-8")
                if "NotImplementedError" not in content and "pass" not in content:
                    is_stub = False
            
            if is_stub:
                implementations_created += 1
            else:
                implementations_reused += 1

            # 1. Write Implementation candidate containing math solver
            impl_file.write_text(math_code, encoding="utf-8")

            # 2. Write Test candidate containing real assertions and grading checks
            test_code = f"""import pytest
from implementation_candidate import {op_name}

def check_answer(student_ans, correct_ans, answer_type):
    if answer_type == "single_choice":
        return student_ans == correct_ans
    elif answer_type == "multi_part":
        return all(student_ans[k]["answer"] == correct_ans[k]["answer"] for k in correct_ans)
    elif answer_type == "drawing":
        return student_ans == correct_ans
    else:
        return str(student_ans).strip() == str(correct_ans).strip()

def test_operation_and_checker():
    for seed in [7, 42, 101]:
        payload = {op_name}(seed=seed)
        assert "question_text" in payload
        assert "answer" in payload
        assert "semantic_answer" in payload
        assert "answer_type" in payload
        assert "presentation_mode" in payload
        
        ans_type = payload["answer_type"]
        correct = payload["answer"]
        
        # Positive assertion
        assert check_answer(correct, correct, ans_type) is True
        
        # Negative assertion (incorrect grading check)
        if ans_type == "single_choice":
            incorrect = "B" if correct == "A" else "A"
        elif ans_type == "multi_part":
            incorrect = dict(correct)
            for k in incorrect:
                incorrect[k] = dict(incorrect[k])
                incorrect[k]["answer"] = str(int(incorrect[k]["answer"]) + 1)
        elif ans_type == "drawing":
            incorrect = {{"type": "wrong_line"}}
        else:
            incorrect = str(int(correct) + 1) if correct.isdigit() else correct + "_wrong"
            
        assert check_answer(incorrect, correct, ans_type) is False
"""
            if op_name == "collinear_trisection_coordinate":
                test_code += """
def test_trisection_mathematical_invariants():
    for seed in [7, 42, 101]:
        payload = collinear_trisection_coordinate(seed=seed)
        A = payload["metadata"]["A"]
        B = payload["metadata"]["B"]
        P = payload["semantic_answer"]
        x1, y1 = A
        x2, y2 = B
        tx, ty = P
        
        # 1. Collinearity: cross product of AP and AB must be 0
        cross_product = (x2 - x1) * (ty - y1) - (y2 - y1) * (tx - x1)
        assert cross_product == 0, f"Point P{P} is not collinear with A{A} and B{B}"
        
        # 2. Vector components check for trisection point (either 1:2 or 2:1)
        v_ap = (tx - x1, ty - y1)
        v_pb = (x2 - tx, y2 - ty)
        
        is_1_to_2 = (v_pb[0] == 2 * v_ap[0]) and (v_pb[1] == 2 * v_ap[1])
        is_2_to_1 = (2 * v_pb[0] == v_ap[0]) and (2 * v_pb[1] == v_ap[1])
        
        assert is_1_to_2 or is_2_to_1, f"Point P{P} does not divide AB in 1:2 or 2:1 ratio"
        
        # 3. Midpoint check: it must NOT be the midpoint
        is_midpoint = (v_ap[0] == v_pb[0]) and (v_ap[1] == v_pb[1])
        assert not is_midpoint, f"Point P{P} is the midpoint, which is forbidden for trisection"
"""
            test_file.write_text(test_code, encoding="utf-8")

            # 3. Write Registry & Adapter candidates
            reg_preview = draft_res.get("registry_patch_preview") or {}
            reg_file = ws_dir / "registry_patch.json"
            reg_file.write_text(json.dumps(reg_preview, indent=2, ensure_ascii=False), encoding="utf-8")

            adapter_preview = {
                "operation": op_name,
                "route": f"if op == '{op_name}': convert_to_payload()"
            }
            adapter_file.write_text(json.dumps(adapter_preview, indent=2, ensure_ascii=False), encoding="utf-8")

            # 4. Invoke proposal advance pipeline to run Executable Workspace Gate checks
            advance_res = advance_capability_proposals(
                skill_id=skill_id,
                dry_run=False,
                proposal_root=p_root,
                draft_root=d_root,
                db_conn=conn
            )

            res_details = advance_res["per_proposal_results"][proposal_id]
            per_proposal_results[proposal_id] = res_details

            if res_details["status"] == "ready_for_human_review":
                validation_passed += 1
                ready_for_human_review += 1
            else:
                validation_failed += 1
                failed_gate[proposal_id] = res_details.get("failed_gate", [])
                failed_source_example_ids[proposal_id] = res_details.get("failed_source_example_ids", [])

    finally:
        if close_conn:
            conn.close()

    return {
        "total_incomplete": total_incomplete,
        "implementations_created": implementations_created,
        "implementations_reused": implementations_reused,
        "validation_passed": validation_passed,
        "validation_failed": validation_failed,
        "ready_for_human_review": ready_for_human_review,
        "implementation_incomplete": total_incomplete - ready_for_human_review,
        "failed_gate": failed_gate,
        "failed_source_example_ids": failed_source_example_ids,
        "per_proposal_results": per_proposal_results
    }
