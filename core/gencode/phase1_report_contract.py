# -*- coding: utf-8 -*-
from typing import Any
from core.gencode.sop_policy import ALLOWED_SKILL_LEVEL_BLOCKERS, DISALLOWED_SKILL_BLOCK_PROMOTIONS

ANSWER_TYPES = [
    "choice", "integer", "rational", "numeric", "expression", "interval", "set", 
    "ordered_tuple", "unordered_tuple", "coordinate_pair", "ordered_pair", "matrix", "boolean", "text_short",
    "free_response", "drawing", "handwriting"
]
EQUIVALENCE_TYPES = [
    "choice_label", "numeric_exact", "rational_equivalent", "decimal_tolerance", 
    "percentage_equivalent", "algebraic_equivalent", "equation_equivalent", 
    "interval_set", "unordered_solution_set", "ordered_tuple_exact", 
    "unordered_tuple_equivalent", "matrix_exact", "exact_string", 
    "case_insensitive_string", "manual_review_or_ai_judged"
]
CHECKER_KEYS = [
    "choice_label_checker", "integer_checker", "rational_checker", "decimal_tolerance_checker", 
    "percentage_checker", "expression_checker", "equation_checker", "interval_checker", 
    "set_checker", "tuple_checker", "matrix_checker", "text_short_checker", 
    "manual_review_checker", "ai_judged_checker"
]

def _has_coordinate_pair_semantics(payload: dict[str, Any]) -> bool:
    semantic_values = {
        str(payload.get("answer_shape", "")).strip(),
        str(payload.get("semantic_answer_shape", "")).strip(),
        str(payload.get("answer_semantics", "")).strip(),
        str(payload.get("semantics", "")).strip(),
    }
    math_objects = set(payload.get("math_objects") or [])
    stem = payload.get("stem_contract") if isinstance(payload.get("stem_contract"), dict) else {}
    math_objects.update(stem.get("allowed_math_objects") or [])
    math_objects.update(stem.get("required_math_objects") or [])
    return "coordinate_pair" in semantic_values or "coordinate_pair" in math_objects


def canonicalize_and_complete(
    at: str,
    eq: str,
    checker: str,
    question_text: str = "",
    *,
    problem_type_id: str = "",
    coordinate_pair_semantic: bool = False,
) -> tuple[str, str, str]:
    """
    Universally cleans, canonicalizes legacy tokens, and completes checkers/equivalence types.
    """
    at = str(at or "").strip()
    eq = str(eq or "").strip()
    checker = str(checker or "").strip()

    if at == "single_choice":
        at = "choice"
    elif at == "short_answer":
        at = "text_short"
    if problem_type_id and eq == str(problem_type_id).strip():
        eq = ""
    if coordinate_pair_semantic and at not in {"choice", "single_choice"}:
        at = "ordered_tuple"
        eq = "ordered_tuple_exact"
        checker = "tuple_checker"
    
    # 1. Mapping Canonicalization (Legacy Remap)
    if eq in ["numeric_equivalence", "numeric_equal", "numeric_exact_equivalence"]:
        eq = "numeric_exact"
    elif eq in ["string_equivalence", "exact_text", "exact_string_equivalence"]:
        eq = "exact_string"
    elif eq == "fraction_equal":
        eq = "rational_equivalent"
    elif eq == "set_equal":
        eq = "unordered_solution_set"
    elif eq == "expression_equivalence":
        eq = "algebraic_equivalent"
        
    if checker in ["text_checker", "string_checker"]:
        checker = "text_short_checker"
        
    # Check for fractions to dynamically prefer rational over integer
    has_fraction = "frac" in question_text or "/" in question_text
    
    if at in ["float", "number", "numeric", "integer"]:
        if has_fraction:
            at = "rational"
        else:
            at = "integer"
            
    # 2. Generic Contract Completion (Pre-防御 Layer)
    if at in ["numeric", "integer"]:
        if not eq or eq not in EQUIVALENCE_TYPES:
            eq = "numeric_exact"
        if not checker or checker not in CHECKER_KEYS:
            checker = "integer_checker"
    elif at == "rational":
        if not eq or eq not in EQUIVALENCE_TYPES:
            eq = "rational_equivalent"
        if not checker or checker not in CHECKER_KEYS:
            checker = "rational_checker"
    elif at == "expression":
        if not eq or eq not in EQUIVALENCE_TYPES:
            eq = "algebraic_equivalent"
        if not checker or checker not in CHECKER_KEYS:
            checker = "expression_checker"
    elif at == "choice":
        eq = "choice_label"
        checker = "choice_label_checker"
    elif at == "set":
        if not eq or eq not in EQUIVALENCE_TYPES:
            eq = "unordered_solution_set"
        if not checker or checker not in CHECKER_KEYS:
            checker = "set_checker"
    elif at == "interval":
        if not eq or eq not in EQUIVALENCE_TYPES:
            eq = "interval_set"
        if not checker or checker not in CHECKER_KEYS:
            checker = "interval_checker"
    elif at in ["ordered_tuple", "unordered_tuple", "coordinate_pair", "ordered_pair"]:
        at = "ordered_tuple" if at in {"coordinate_pair", "ordered_pair"} else at
        if not eq or eq not in EQUIVALENCE_TYPES:
            eq = "ordered_tuple_exact" if at == "ordered_tuple" else "unordered_tuple_equivalent"
        if not checker or checker not in CHECKER_KEYS:
            checker = "tuple_checker"
    elif at == "matrix":
        if not eq or eq not in EQUIVALENCE_TYPES:
            eq = "matrix_exact"
        if not checker or checker not in CHECKER_KEYS:
            checker = "matrix_checker"
            
    # 3. Delete text_checker leaks for purely mathematical deterministic evaluations
    is_pure_math = at in ["integer", "rational", "numeric", "expression", "interval", "set", "ordered_tuple", "unordered_tuple", "matrix"]
    if is_pure_math:
        if checker in ["text_short_checker", "text_checker", "manual_review_checker", ""]:
            if at in ["integer", "numeric"]:
                checker = "integer_checker"
                eq = "numeric_exact"
            elif at == "rational":
                checker = "rational_checker"
                eq = "rational_equivalent"
            elif at == "expression":
                checker = "expression_checker"
                eq = "algebraic_equivalent"
            elif at == "set":
                checker = "set_checker"
                eq = "unordered_solution_set"
            elif at == "interval":
                checker = "interval_checker"
                eq = "interval_set"
            elif at in ["ordered_tuple", "unordered_tuple"]:
                checker = "tuple_checker"
                eq = "ordered_tuple_exact" if at == "ordered_tuple" else "unordered_tuple_equivalent"
            elif at == "matrix":
                checker = "matrix_checker"
                eq = "matrix_exact"
                
        if eq in ["exact_string", "case_insensitive_string", ""]:
            if at in ["integer", "numeric"]:
                eq = "numeric_exact"
            elif at == "rational":
                eq = "rational_equivalent"
            elif at == "expression":
                eq = "algebraic_equivalent"
            elif at == "set":
                eq = "unordered_solution_set"
            elif at == "interval":
                eq = "interval_set"
            elif at in ["ordered_tuple", "unordered_tuple"]:
                eq = "ordered_tuple_exact" if at == "ordered_tuple" else "unordered_tuple_equivalent"
            elif at == "matrix":
                eq = "matrix_exact"
                
    # Final strict Whitelist overrides
    if at not in ANSWER_TYPES:
        at = "expression"
    if eq not in EQUIVALENCE_TYPES:
        eq = "algebraic_equivalent"
    if checker not in CHECKER_KEYS:
        checker = "expression_checker"
        
    return at, eq, checker

def remap_legacy_fields(cand: dict[str, Any]) -> dict[str, Any]:
    """
    Cleans and canonicalizes legacy fields in a candidate to standard Gencode Whitelist tokens.
    """
    ac = dict(cand.get("answer_contract_proposal", {}))
    
    at = str(ac.get("answer_type", cand.get("answer_type", "expression"))).strip()
    eq = str(ac.get("equivalence_type", cand.get("equivalence_type", ac.get("answer_equivalence", "")))).strip()
    checker = str(ac.get("checker_key", cand.get("checker_key", ac.get("checker", "")))).strip()
    
    pt_id = str(cand.get("problem_type_id", "")).strip()
    draft = dict(cand.get("problem_type_spec_draft")) if isinstance(cand.get("problem_type_spec_draft"), dict) else {}
    coordinate_pair_semantic = _has_coordinate_pair_semantics(ac) or _has_coordinate_pair_semantics(draft)
    at, eq, checker = canonicalize_and_complete(
        at,
        eq,
        checker,
        problem_type_id=pt_id,
        coordinate_pair_semantic=coordinate_pair_semantic,
    )
    
    ac.update({
        "answer_type": at,
        "equivalence_type": eq,
        "answer_equivalence": eq,
        "checker_key": checker,
        "checker": checker,
    })
    
    cand["answer_contract_proposal"] = ac
    cand["answer_type"] = at
    cand["equivalence_type_proposal"] = eq
    cand["checker_key_proposal"] = checker
    
    # Re-slugify problem_type_id to match standard whitelisted tokens
    draft_pt_id = str(draft.get("problem_type_id", "")).strip()
    if pt_id.startswith("expression_") and draft_pt_id and draft_pt_id != pt_id:
        pt_id = draft_pt_id
    if pt_id:
        pt_id = pt_id.replace("numeric_", f"{at}_").replace("_numeric", f"_{at}")
        if not coordinate_pair_semantic:
            pt_id = pt_id.replace("short_answer", "expression")
        cand["problem_type_id"] = pt_id
        cand["proposed_problem_type_id"] = pt_id
    if draft:
        draft_ac = dict(draft.get("answer_contract")) if isinstance(draft.get("answer_contract"), dict) else {}
        draft_ac.update(
            {
                "answer_type": at,
                "equivalence_type": eq,
                "answer_equivalence": eq,
                "checker_key": checker,
                "checker": checker,
            }
        )
        draft["answer_contract"] = draft_ac
        if pt_id:
            draft["problem_type_id"] = pt_id
        cand["problem_type_spec_draft"] = draft

    owned_flags = {
        "missing_answer_contract_problem_type",
        "missing_checker_key_problem_type",
        "invalid_equivalence_type_problem_type",
    }
    cand["promote_blockers"] = [x for x in (cand.get("promote_blockers", []) or []) if x not in owned_flags]
    cand["risk_flags"] = [x for x in (cand.get("risk_flags", []) or []) if x not in owned_flags]
        
    return cand

def validate_phase1_report_contract(report: dict[str, Any]) -> dict[str, Any]:
    """
    Enforces SOP v0.2 consistency guidelines on Phase 1 reports.
    Performs data alignment, aggregates scores safely, filters disallowed blockers,
    and returns normalized_fields, warnings, and violations.
    """
    violations = []
    warnings = []
    normalized_fields = {}
    
    # 1. Load data collections safely
    per_example = report.get("per_example_classification", []) or report.get("source_classifications", []) or []
    per_example = [dict(x) for x in per_example if isinstance(x, dict)]
    
    rejected_source_examples = list(report.get("rejected_source_examples", []) or [])
    source_quality_reject_examples = list(report.get("source_quality_reject_examples", []) or [])
    
    # Track examples that are source_quality_reject
    found_reject_ids = set()
    for row in per_example:
        feat = row.get("example_feature", {}) if isinstance(row.get("example_feature"), dict) else {}
        
        eid = row.get("example_id")
        if eid is None:
            eid = feat.get("source_example_id")
        if eid is None:
            continue
            
        issue_type = str(row.get("issue_type", feat.get("issue_type", ""))).strip()
        exclude_reason = str(row.get("exclude_reason", feat.get("exclude_reason", ""))).strip()
        quality_status = str(row.get("source_quality_status", feat.get("source_quality_status", ""))).strip()
        quality_reject = bool(row.get("source_quality_reject", feat.get("source_quality_reject", False)))
        
        is_sq_reject = (
            issue_type == "source_quality_reject" or
            exclude_reason == "source_quality_reject" or
            quality_status == "rejected" or
            quality_reject
        )
        
        if is_sq_reject:
            if isinstance(eid, dict):
                eid = eid.get("example_id")
            if eid is not None:
                try:
                    found_reject_ids.add(int(eid))
                except (TypeError, ValueError):
                    found_reject_ids.add(eid)
                
    # 2. Source Quality Consistency Checks
    sq_rejects_ids = []
    for x in source_quality_reject_examples:
        if isinstance(x, dict):
            eid = x.get("example_id")
            if eid is not None:
                sq_rejects_ids.append(eid)
        else:
            sq_rejects_ids.append(x)

    for rid in found_reject_ids:
        if rid not in sq_rejects_ids:
            sq_rejects_ids.append(rid)
            warnings.append(f"source_quality_reject_examples_normalized:{rid}")
            
    # rejected_source_examples vs source_quality_reject_examples check
    if rejected_source_examples and not sq_rejects_ids and found_reject_ids:
        sq_rejects_ids = list(found_reject_ids)
        warnings.append("source_quality_reject_examples_normalized_from_found")
        
    for rid in rejected_source_examples:
        actual_id = rid
        if isinstance(rid, dict):
            actual_id = rid.get("example_id")
        if actual_id in {None, "unknown", "", "(unknown)"}:
            warnings.append("unknown_rejected_source_example_id")
            
    # Clean up sq_rejects_ids to ensure all are hashable and sortable
    hashable_sq_rejects = []
    for x in sq_rejects_ids:
        if x in {None, "unknown", "", "(unknown)"}:
            continue
        try:
            if isinstance(x, str) and x.isdigit():
                hashable_sq_rejects.append(int(x))
            elif isinstance(x, dict):
                eid = x.get("example_id")
                if eid is not None:
                    hashable_sq_rejects.append(int(eid) if str(eid).isdigit() else eid)
            else:
                hashable_sq_rejects.append(x)
        except Exception:
            hashable_sq_rejects.append(str(x))
            
    normalized_fields["source_quality_reject_examples"] = sorted(list(set(hashable_sq_rejects)))
    
    # 3. Alignment Aggregate Consistency Checks
    expected_tasks = set(report.get("expected_subskill_candidates", []))
    expected_families = set(report.get("expected_skill_families", []))
    
    usable_core_scores = []
    per_example_normalized = []
    
    for row in per_example:
        row_copy = dict(row)
        feat = row_copy.get("example_feature", {}) if isinstance(row_copy.get("example_feature"), dict) else {}
        
        eid = row_copy.get("example_id")
        if eid is None:
            eid = feat.get("source_example_id")
            
        final_task = str(row_copy.get("final_target_task", row_copy.get("target_task", feat.get("target_task", "")))).strip()
        final_family = str(row_copy.get("final_task_family", row_copy.get("task_family", feat.get("task_family", "")))).strip()
        quality_status = str(row_copy.get("source_quality_status", feat.get("source_quality_status", ""))).strip()
        included_core = bool(row_copy.get("included_in_core_induction", feat.get("included_in_core_induction", False)))
        
        # 3.1 Universal Canonicalization and Contract Completion
        at = str(row_copy.get("answer_type", feat.get("answer_type", "expression"))).strip()
        eq = str(row_copy.get("equivalence_type", feat.get("equivalence_type", row_copy.get("equivalence", feat.get("equivalence", ""))))).strip()
        checker = str(row_copy.get("checker_key", feat.get("checker_key", row_copy.get("checker", feat.get("checker", ""))))).strip()
        question_text = str(feat.get("question_text", "")).strip()
        
        coordinate_pair_semantic = _has_coordinate_pair_semantics(row_copy) or _has_coordinate_pair_semantics(feat)
        at, eq, checker = canonicalize_and_complete(
            at,
            eq,
            checker,
            question_text,
            problem_type_id=str(row_copy.get("detected_problem_type_id", "")).strip(),
            coordinate_pair_semantic=coordinate_pair_semantic,
        )
        
        row_copy["answer_type"] = at
        row_copy["equivalence_type"] = eq
        row_copy["checker_key"] = checker
        
        if isinstance(row_copy.get("example_feature"), dict):
            row_copy["example_feature"]["answer_type"] = at
            row_copy["example_feature"]["equivalence_type"] = eq
            row_copy["example_feature"]["equivalence"] = eq
            row_copy["example_feature"]["checker_key"] = checker
            row_copy["example_feature"]["checker"] = checker
            
        row_score = float(row_copy.get("alignment_score", feat.get("alignment_score", 0.0)) or 0.0)
        
        if included_core and final_task in expected_tasks and final_family in expected_families and quality_status != "rejected":
            if row_score == 0.0:
                row_score = 0.8
                if "alignment_score" in row_copy:
                    row_copy["alignment_score"] = 0.8
                if "alignment_score" in feat:
                    feat["alignment_score"] = 0.8
                    row_copy["example_feature"] = feat
                if "alignment_score" not in row_copy and "alignment_score" not in feat:
                    row_copy["alignment_score"] = 0.8
                warnings.append(f"per_example_alignment_score_corrected:{eid}")
                
        per_example_normalized.append(row_copy)
        
        # Aggregate scores (exclude rejects and non-core induction)
        is_reject = (
            quality_status == "rejected" or
            row_copy.get("source_quality_reject", feat.get("source_quality_reject", False)) or
            row_copy.get("exclude_reason", feat.get("exclude_reason", "")) == "source_quality_reject"
        )
        is_enrichment = (
            row_copy.get("induction_tier", feat.get("induction_tier", "")) == "enrichment" or
            row_copy.get("exclude_reason", feat.get("exclude_reason", "")) == "enrichment_not_core_induction"
        )
        
        if not is_reject and not is_enrichment and included_core:
            usable_core_scores.append(row_score)
            
    normalized_fields["per_example_classification"] = per_example_normalized
    normalized_fields["source_classifications"] = per_example_normalized
    
    # Calculate aggregate alignment score
    agg_score = float(report.get("alignment_score", 0.0) or 0.0)
    if usable_core_scores:
        avg_score = round(sum(usable_core_scores) / len(usable_core_scores), 4)
    else:
        avg_score = agg_score
        
    if avg_score > 0.0 and agg_score == 0.0:
        agg_score = avg_score
        normalized_fields["alignment_score"] = agg_score
        normalized_fields["skill_source_score"] = agg_score
        warnings.append("aggregate_alignment_score_normalized")
    else:
        normalized_fields["alignment_score"] = agg_score
        
    # If alignment score is low but no allowed blockers exist, status must be warn, not block
    align_status = str(report.get("source_alignment_status", "pass")).strip()
    align_blockers = list(report.get("alignment_blockers", []) or [])
    
    allowed_align_blockers = [b for b in align_blockers if b in ALLOWED_SKILL_LEVEL_BLOCKERS]
    if align_status == "block" and not allowed_align_blockers:
        normalized_fields["source_alignment_status"] = "warn"
        normalized_fields["alignment_blockers"] = []
        warnings.append("source_alignment_status_blocked_demoted_to_warn")
    else:
        normalized_fields["source_alignment_status"] = align_status
        normalized_fields["alignment_blockers"] = align_blockers
 
    # 4. Gate Layer Consistency Checks
    align_blockers = list(normalized_fields.get("alignment_blockers", align_blockers))
    ex_gate = report.get("exception_review_gate", {}) or {}
    ex_reasons = list(ex_gate.get("reasons", []) or [])
    
    all_blockers = set(align_blockers) | set(ex_reasons)
    invalid_blockers = []
    
    for b in all_blockers:
        is_disallowed = (
            b in DISALLOWED_SKILL_BLOCK_PROMOTIONS or
            b not in ALLOWED_SKILL_LEVEL_BLOCKERS or
            "source_quality_reject" in b or
            "broken_latex" in b or
            "missing_answer" in b or
            "pending_template" in b
        )
        if is_disallowed:
            invalid_blockers.append(b)
            
    sop_gate_violation = bool(report.get("sop_gate_violation", False))
    sop_gate_status = str(report.get("sop_gate_status", "PASS")).strip()
    
    if invalid_blockers:
        violations.extend(invalid_blockers)
        sop_gate_violation = True
        sop_gate_status = "FAIL"
        
        align_blockers = [b for b in align_blockers if b not in invalid_blockers]
        ex_reasons = [r for r in ex_reasons if r not in invalid_blockers]
        
        normalized_fields["alignment_blockers"] = align_blockers
        normalized_fields["exception_review_gate"] = {
            "required": bool(ex_reasons),
            "reasons": ex_reasons
        }
        
        align_warns = list(report.get("alignment_warnings", []) or [])
        for ib in invalid_blockers:
            warnings.append(f"report_contract_warning:disallowed_blocker_demoted:{ib}")
            if ib not in align_warns:
                align_warns.append(f"disallowed_blocker_promoted_to_warning:{ib}")
        normalized_fields["alignment_warnings"] = align_warns
        
    normalized_fields["sop_gate_status"] = sop_gate_status
    normalized_fields["sop_gate_violation"] = sop_gate_violation
    normalized_fields["invalid_skill_level_blockers"] = list(set(report.get("invalid_skill_level_blockers", []) or []) | set(invalid_blockers))
    
    # 5. Candidate Problem Types Consistency & Whitelist Canonicalization
    candidates = report.get("candidate_problem_types", []) or []
    cand_count = int(report.get("candidate_problem_type_count", 0) or 0)
    
    normalized_candidates = []
    for cand in candidates:
        if not isinstance(cand, dict):
            normalized_candidates.append(cand)
            continue
        cleaned_cand = remap_legacy_fields(dict(cand))
        normalized_candidates.append(cleaned_cand)
        
    normalized_fields["candidate_problem_types"] = normalized_candidates
    normalized_fields["proposal_items"] = normalized_candidates
    
    if normalized_candidates and cand_count == 0:
        cand_count = len(normalized_candidates)
        normalized_fields["candidate_problem_type_count"] = cand_count
        warnings.append("candidate_problem_type_count_synchronized")
    else:
        normalized_fields["candidate_problem_type_count"] = cand_count
        
    # If candidate count > 0 and skill level blockers is empty, final status must NOT be blocked
    final_blockers = set(normalized_fields.get("alignment_blockers", align_blockers)) | set(normalized_fields.get("exception_review_gate", {}).get("reasons", ex_reasons))
    
    phase_status = str(report.get("phase_status", "")).strip()
    if cand_count > 0 and not final_blockers:
        if "blocked" in phase_status.lower() or phase_status == "SOP_PREFLIGHT_FAIL":
            if phase_status != "SOP_PREFLIGHT_FAIL":
                normalized_fields["phase_status"] = "phase1_completed"
                normalized_fields["ok"] = True
                warnings.append("phase_status_normalized_to_completed")
                
    # Final Contract Status Decision
    if violations:
        contract_status = "FAIL"
    elif warnings:
        contract_status = "PASS_WITH_WARNINGS"
    else:
        contract_status = "PASS"
        
    return {
        "report_contract_status": contract_status,
        "report_contract_violations": violations,
        "report_contract_warnings": warnings,
        "normalized_fields": normalized_fields
    }
