# -*- coding: utf-8 -*-
from typing import Any

def validate_problem_type_grouping_contract(report: dict[str, Any]) -> dict[str, Any]:
    """
    Enforces grouping consistency on candidate problem types.
    Ensures that different target tasks and answer types are not merged,
    and splits mixed candidate groups into distinct candidate problem types.
    """
    candidates = report.get("candidate_problem_types", []) or []
    per_example = report.get("per_example_classification", []) or report.get("source_classifications", []) or []
    
    # 1. Map example classifications by example_id
    examples_by_id = {}
    for row in per_example:
        if not isinstance(row, dict):
            continue
        feat = row.get("example_feature", {}) if isinstance(row.get("example_feature"), dict) else {}
        eid = row.get("example_id")
        if eid is None:
            eid = feat.get("source_example_id")
        if eid is None:
            continue
            
        # 2. Enforce Rule-Pack Classification Authority
        clf_src = str(row.get("classifier_source", feat.get("classifier_source", ""))).strip()
        if "rule" in clf_src or "registry" in clf_src:
            has_severe_error = False
            for k in ["severe_ocr_noise", "broken_latex", "missing_answer"]:
                if bool(row.get(k, feat.get(k, False))):
                    has_severe_error = True
                    break
            
            if not has_severe_error:
                row["requires_human_action"] = False
                if "example_feature" in row and isinstance(row["example_feature"], dict):
                    row["example_feature"]["requires_human_action"] = False
            
        task = str(row.get("target_task", feat.get("target_task", "unknown"))).strip()
        final_task = str(row.get("final_target_task", feat.get("final_target_task", task))).strip()
        family = str(row.get("task_family", feat.get("task_family", "unknown"))).strip()
        final_family = str(row.get("final_task_family", feat.get("final_task_family", family))).strip()
        
        at = str(row.get("answer_type", feat.get("answer_type", "unknown"))).strip()
        eq = str(row.get("equivalence_type", feat.get("equivalence_type", ""))).strip()
        checker = str(row.get("checker_key", feat.get("checker_key", ""))).strip()
        pres = str(row.get("presentation_mode", feat.get("presentation_mode", ""))).strip()
        
        examples_by_id[eid] = {
            "example_id": eid,
            "target_task": final_task,
            "task_family": final_family,
            "answer_type": at,
            "equivalence_type": eq,
            "checker_key": checker,
            "presentation_mode": pres,
        }

    warnings = []
    violations = []
    normalized_fields = {}
    new_candidates = []
    has_mixed_group = False
    
    # 2. Inspect each candidate
    for candidate in candidates:
        if not isinstance(candidate, dict):
            new_candidates.append(candidate)
            continue
            
        pt_id = str(candidate.get("problem_type_id", "")).strip()
        matched_ids = candidate.get("matched_example_ids", []) or []
        
        # 1. Implement Generic Self-Pollution Guard at Loop Header
        eq_prop = candidate.get("equivalence_type_proposal")
        if eq_prop == pt_id:
            candidate["equivalence_type_proposal"] = ""
            warnings.append(f"pollution_cleanup:{pt_id}:equivalence_type_proposal_cleared")
            if isinstance(candidate.get("answer_contract_proposal"), dict):
                candidate["answer_contract_proposal"]["equivalence_type"] = ""
                candidate["answer_contract_proposal"]["answer_equivalence"] = ""
        
        # Check if the pt_id itself has semantic mixture (e.g. numeric and short_answer)
        is_mixed_id = False
        if "numeric" in pt_id and "interpret_function_notation" in pt_id:
            is_mixed_id = True
        elif "numeric" in pt_id and ("short_answer" in pt_id or "choice" in pt_id or "string" in pt_id):
            if "evaluate_function_value" not in pt_id:
                is_mixed_id = True
                
        if is_mixed_id:
            has_mixed_group = True
            violations.append(f"semantic_mixture_in_problem_type_id:{pt_id}")
            
        # Group matched examples by target_task and answer_type
        subgroups = {}
        for ex_id in matched_ids:
            ex_info = examples_by_id.get(ex_id, {})
            task = ex_info.get("target_task", "unknown")
            at = ex_info.get("answer_type", "unknown")
            family = ex_info.get("task_family", "unknown")
            eq = ex_info.get("equivalence_type", "")
            checker = ex_info.get("checker_key", "")
            pres = ex_info.get("presentation_mode", "")
            
            key = (task, at, family, eq, checker, pres)
            if key not in subgroups:
                subgroups[key] = []
            subgroups[key].append(ex_id)
            
        if len(subgroups) > 1:
            has_mixed_group = True
            warnings.append(f"mixed_group_split_required:{pt_id}")
            
        # 3. Implement Generic Signature-Based Splitting
        for idx, (key, sub_matched_ids) in enumerate(sorted(subgroups.items()), start=1):
            task, at, family, eq, checker, pres = key
            
            # Slugify new problem type ID: {normalized_answer_type}_{normalized_target_task}
            parts = []
            if at and at != "unknown":
                parts.append(at)
            else:
                parts.append("unclassified")
            
            if task and task != "unknown":
                parts.append(task)
                
            new_pt_id = "_".join(parts)
            
            if pres and pres != "unknown":
                # Avoid redundant presentation mode if it's already in parts or similar to at
                if pres != at and not (at == "choice" and pres == "single_choice") and not (at == "short_answer" and pres == "short_answer"):
                    new_pt_id = f"{new_pt_id}_{pres}"
            
            # Clone and update candidate fields
            new_cand = dict(candidate)
            new_cand.update({
                "problem_type_id": new_pt_id,
                "proposed_problem_type_id": new_pt_id,
                "display_name": f"{at} / {task}" if task else at,
                "matched_example_ids": sub_matched_ids,
                "matched_example_count": len(sub_matched_ids),
                "representative_example_id": sub_matched_ids[0] if sub_matched_ids else None,
                "unmatched_example_ids": [x for x in candidate.get("unmatched_example_ids", []) if x not in sub_matched_ids],
            })
            
            # Update answer_contract_proposal if present
            ac = dict(candidate.get("answer_contract_proposal", {}))
            ac.update({
                "answer_type": at,
                "checker_key": checker,
                "checker": checker,
                "equivalence_type": eq,
                "answer_equivalence": eq,
                "presentation_mode": pres,
            })
            new_cand["answer_contract_proposal"] = ac
            new_cand["checker_key_proposal"] = checker
            new_cand["equivalence_type_proposal"] = eq
            
            new_candidates.append(new_cand)

    normalized_fields["candidate_problem_types"] = new_candidates
    normalized_fields["proposal_items"] = new_candidates
    
    # 4. Sync candidate counts cleanly
    normalized_fields["candidate_problem_type_count"] = len(new_candidates)
    
    # 3. Decision / Atomic consistency
    if has_mixed_group:
        status = "FAIL"
        normalized_fields["ok"] = False
        normalized_fields["phase_status"] = "GROUPING_CONTRACT_FAIL"
        normalized_fields["suggested_action"] = "Please review and split mixed problem type groups."
    else:
        status = "PASS"
        
    return {
        "problem_type_grouping_contract_status": status,
        "problem_type_grouping_contract_warnings": warnings,
        "problem_type_grouping_contract_violations": violations,
        "normalized_fields": normalized_fields,
    }
