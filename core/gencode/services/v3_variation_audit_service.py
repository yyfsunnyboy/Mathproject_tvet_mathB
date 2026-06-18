# -*- coding: utf-8 -*-
"""Generic V3 Variation Audit Service for auditing generator variations."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def extract_parameter_signature(payload: dict[str, Any]) -> str:
    """Extract a parameter signature from the payload to detect mathematical property variation."""
    meta = payload.get("metadata", {}) or {}
    domain_payload = payload.get("domain_payload", {}) or {}
    parameters = payload.get("parameters", {}) or {}
    constraints = payload.get("constraints", {}) or {}
    
    sig_parts = []
    
    # 1. Try to extract from structured domain metadata
    has_structured = False
    for d in (parameters, constraints, domain_payload, meta):
        if isinstance(d, dict) and d:
            for k in sorted(d.keys()):
                # Exclude trivial keys like component_id, textbook_example_id in signature if we want true math values
                if k in ("component_id", "textbook_example_id", "seed"):
                    continue
                has_structured = True
                sig_parts.append(f"{k}:{d[k]}")
                
    if payload.get("semantic_answer"):
        sig_parts.append(f"semantic_answer:{payload['semantic_answer']}")
        
    if has_structured and sig_parts:
        sig_str = "|".join(sig_parts)
        return hashlib.sha256(sig_str.encode("utf-8")).hexdigest()[:16]
        
    # 2. Fallback normalization strategy: extract numbers, coordinates, and equations from question text and answer keys
    q_text = payload.get("question_text", "")
    c_ans = payload.get("correct_answer", "")
    choices = payload.get("choices") or []
    
    fallback_parts = []
    if payload.get("semantic_answer"):
        fallback_parts.append(f"semantic_answer:{payload['semantic_answer']}")
        
    # Normalize question text slightly and extract numbers/fractions
    # Matches decimals, negatives, fractions, and LaTeX fractions
    numbers = re.findall(r"-?\d+(?:\.\d+)?|\\frac\{-?\d+\}\{-?\d+\}|\d+/\d+", q_text)
    if numbers:
        fallback_parts.append(f"q_nums:{sorted(numbers)}")
        
    # Correct answer serialization
    if isinstance(c_ans, dict):
        ans_items = []
        for k in sorted(c_ans.keys()):
            ans_items.append(f"{k}:{c_ans[k]}")
        fallback_parts.append(f"ans_dict:{ans_items}")
    else:
        fallback_parts.append(f"ans_val:{c_ans}")
        
    # Choices text values
    if choices:
        choice_vals = sorted([str(ch.get("text", "")) for ch in choices if isinstance(ch, dict)])
        fallback_parts.append(f"choices:{choice_vals}")
        
    fallback_str = "|".join(fallback_parts)
    return hashlib.sha256(fallback_str.encode("utf-8")).hexdigest()[:16]


def _load_module_directly(file_path: Path, module_name: str = "temp_module"):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for: {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit_skill_variation(
    skill_id: str,
    sample_size: int = 200,
    min_samples_per_component: int = 5,
    seeds: list[int] | None = None,
    source: str = "production",
    project_root: str | None = None,
    staging_root: str | None = None,
    conn: sqlite3.Connection | None = None,
) -> dict[str, Any]:
    """Audit the parameter variation for a skill across all verified components."""
    skill_key = str(skill_id or "").strip()
    if not skill_key:
        raise ValueError("missing_skill_id")
        
    root_path = Path(project_root or PROJECT_ROOT).resolve()
    
    # 1. Fetch verified components from tracker to know what needs to be verified
    close_conn_later = False
    if conn is None:
        db_path = root_path / "instance" / "kumon_math.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        close_conn_later = True
        
    try:
        rows = conn.execute(
            """SELECT textbook_example_id, component_id 
               FROM gencode_component_tracker 
               WHERE skill_id = ? AND gencode_status = 'verified'
               ORDER BY textbook_example_id""",
            (skill_key,),
        ).fetchall()
    finally:
        if close_conn_later:
            conn.close()
            
    if not rows:
        return {
            "status": "no_components",
            "skill_id": skill_key,
            "components_checked": 0,
            "dynamic_count": 0,
            "static_count": 0,
            "partially_dynamic_count": 0,
            "insufficient_sample_count": 0,
            "variation_status_by_component": {},
            "variation_warning": "No verified components found in tracker.",
        }
        
    # Standard seed list
    if not seeds:
        seeds = list(range(1, sample_size + 1))
        
    component_results: dict[str, dict[str, Any]] = {}
    
    from core.gencode.runtime_skill_wrapper import check_answer
    
    # For each verified component, run audit
    for row in rows:
        if hasattr(row, "keys") or isinstance(row, sqlite3.Row):
            comp_id = str(row["component_id"])
            ex_id = int(row["textbook_example_id"])
        else:
            ex_id = int(row[0])
            comp_id = str(row[1])
        
        # Determine component's generate.py path based on source
        if source == "dryrun":
            comp_dir = root_path / "reports" / "gencode_v3_dryrun" / skill_key / "components" / comp_id
        elif source == "production":
            comp_dir = root_path / "agent_skills_v3" / skill_key / "components" / comp_id
        elif source == "staging":
            if not staging_root:
                raise ValueError("staging_root must be provided when source is staging")
            comp_dir = Path(staging_root) / "agent_skills_v3" / skill_key / "components" / comp_id
        else:
            raise ValueError(f"Unsupported source type: {source}")
            
        generate_py = comp_dir / "generate.py"
        
        if not generate_py.is_file():
            # If the file doesn't exist, we classify it as insufficient/missing
            component_results[comp_id] = {
                "component_id": comp_id,
                "textbook_example_id": ex_id,
                "generated_count": 0,
                "unique_question_text_count": 0,
                "unique_correct_answer_count": 0,
                "unique_display_answer_count": 0,
                "unique_choices_signature_count": 0,
                "unique_semantic_answer_count": 0,
                "unique_parameter_signature_count": 0,
                "variation_status": "insufficient_sample",
            }
            continue
            
        try:
            comp_mod = _load_module_directly(generate_py, f"audit_mod_{comp_id}")
        except Exception as e:
            # If it fails to load, count it as unsafe/failed
            component_results[comp_id] = {
                "component_id": comp_id,
                "textbook_example_id": ex_id,
                "generated_count": 0,
                "unique_question_text_count": 0,
                "unique_correct_answer_count": 0,
                "unique_display_answer_count": 0,
                "unique_choices_signature_count": 0,
                "unique_semantic_answer_count": 0,
                "unique_parameter_signature_count": 0,
                "variation_status": "unsafe_dynamic",
                "error": f"ImportError: {e}",
            }
            continue
            
        payloads = []
        has_error = False
        error_msg = ""
        
        # Generate min_samples_per_component or more to audit variation
        num_seeds = max(len(seeds), min_samples_per_component)
        for s in seeds[:num_seeds]:
            try:
                # Generate question
                pld = comp_mod.generate(seed=s, component_id=comp_id)
                
                # Basic correctness validation
                q_text = pld.get("question_text")
                c_ans = pld.get("correct_answer")
                ans_contract = pld.get("answer_contract") or {}
                pres_mode = pld.get("presentation_mode")
                
                # 1. Question checks
                if not q_text or c_ans is None or not ans_contract or not pres_mode:
                    has_error = True
                    error_msg = "Missing required keys in payload"
                    
                # 2. Self check (grading correct answer)
                correct_check = check_answer(c_ans, c_ans, payload=pld)
                if not correct_check:
                    has_error = True
                    error_msg = "Grader self-check failed on correct answer"
                    
                # 3. Single choice checks
                if pres_mode == "single_choice":
                    choices = pld.get("choices") or []
                    if len(choices) != 4:
                        has_error = True
                        error_msg = f"Single choice must have 4 choices, got {len(choices)}"
                    elif len(set(c.get("text") for c in choices if isinstance(c, dict))) != 4:
                        has_error = True
                        error_msg = "Duplicate choice options detected"
                    elif c_ans not in ("A", "B", "C", "D"):
                        has_error = True
                        error_msg = f"Correct answer label must be A/B/C/D, got {c_ans}"
                    else:
                        # Check incorrect choice does not pass
                        wrong_label = "B" if c_ans != "B" else "A"
                        wrong_check = check_answer(wrong_label, c_ans, payload=pld)
                        if wrong_check:
                            has_error = True
                            error_msg = f"Grader graded incorrect choice label '{wrong_label}' as correct"
                            
                pld["_param_sig"] = extract_parameter_signature(pld)
                pld["_choices_sig"] = hashlib.sha256(
                    json.dumps(pld.get("choices") or [], ensure_ascii=False).encode("utf-8")
                ).hexdigest()[:16]
                
                payloads.append(pld)
            except Exception as e:
                has_error = True
                error_msg = f"Exception: {e}"
                
        # Calculate stats
        generated_count = len(payloads)
        
        if generated_count < min_samples_per_component:
            var_status = "insufficient_sample"
        elif has_error:
            var_status = "unsafe_dynamic"
        else:
            unique_q = len(set(p["question_text"] for p in payloads))
            unique_c = len(set(json.dumps(p["correct_answer"], ensure_ascii=False) for p in payloads))
            unique_d = len(set(json.dumps(p.get("display_answer"), ensure_ascii=False) for p in payloads))
            unique_choices = len(set(p["_choices_sig"] for p in payloads))
            unique_semantic = len(set(str(p.get("semantic_answer") or "") for p in payloads))
            unique_sigs = len(set(p["_param_sig"] for p in payloads))
            
            # Classification rules:
            if unique_q > 1 and unique_c > 1 and unique_sigs > 1:
                var_status = "dynamic"
            elif unique_q == 1 and unique_c == 1 and unique_sigs == 1:
                var_status = "static"
            else:
                var_status = "partially_dynamic"
                
        if generated_count > 0 and not has_error:
            unique_q = len(set(p["question_text"] for p in payloads))
            unique_c = len(set(json.dumps(p["correct_answer"], ensure_ascii=False) for p in payloads))
            unique_d = len(set(json.dumps(p.get("display_answer"), ensure_ascii=False) for p in payloads))
            unique_choices = len(set(p["_choices_sig"] for p in payloads))
            unique_semantic = len(set(str(p.get("semantic_answer") or "") for p in payloads))
            unique_sigs = len(set(p["_param_sig"] for p in payloads))
        else:
            unique_q = unique_c = unique_d = unique_choices = unique_semantic = unique_sigs = 0
            
        component_results[comp_id] = {
            "component_id": comp_id,
            "textbook_example_id": ex_id,
            "generated_count": generated_count,
            "unique_question_text_count": unique_q,
            "unique_correct_answer_count": unique_c,
            "unique_display_answer_count": unique_d,
            "unique_choices_signature_count": unique_choices,
            "unique_semantic_answer_count": unique_semantic,
            "unique_parameter_signature_count": unique_sigs,
            "variation_status": var_status,
            **({"error": error_msg} if has_error else {}),
        }
        
    # Calculate summary metrics
    total_comps = len(component_results)
    dynamic_count = sum(1 for c in component_results.values() if c["variation_status"] == "dynamic")
    static_count = sum(1 for c in component_results.values() if c["variation_status"] == "static")
    partial_count = sum(1 for c in component_results.values() if c["variation_status"] == "partially_dynamic")
    insufficient_count = sum(1 for c in component_results.values() if c["variation_status"] == "insufficient_sample")
    unsafe_count = sum(1 for c in component_results.values() if c["variation_status"] == "unsafe_dynamic")
    
    # Skill-level status logic
    if total_comps == 0:
        overall_status = "no_components"
    elif unsafe_count > 0:
        overall_status = "unsafe_dynamic"
    elif dynamic_count == total_comps:
        overall_status = "dynamic"
    elif static_count == total_comps:
        overall_status = "static_only"
    else:
        overall_status = "runtime_ready_with_variation_warning"
        
    # Build a warnings list if there are static components
    warnings = []
    if static_count > 0:
        static_ids = [c["component_id"] for c in component_results.values() if c["variation_status"] == "static"]
        warnings.append(f"Static components detected: {', '.join(static_ids)}")
        
    return {
        "status": overall_status,
        "skill_id": skill_key,
        "components_checked": total_comps,
        "dynamic_count": dynamic_count,
        "static_count": static_count,
        "partially_dynamic_count": partial_count,
        "insufficient_sample_count": insufficient_count,
        "unsafe_dynamic_count": unsafe_count,
        "variation_status_by_component": component_results,
        "variation_warnings": warnings,
        "variation_warning": "; ".join(warnings) if warnings else "",
    }
