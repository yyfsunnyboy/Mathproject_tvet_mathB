# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path

SOP_POLICY_VERSION = "v0.2"

REQUIRED_SOP_PATHS = [
    Path("docs") / "系統SOP" / "Gencode_AgentSkillV2整合" / "Gencode與AgentSkillV2整合總體設計_v0.2.md",
    Path("docs") / "系統SOP" / "Gencode_AgentSkillV2整合" / "AgentSkillV2_ProblemType規格包設計_v0.2.md",
    Path("docs") / "系統SOP" / "Gencode_AgentSkillV2整合" / "AnswerContract_EquivalenceType_Gate_v0.2.md"
]

ALLOWED_SKILL_LEVEL_BLOCKERS = {
    "no_usable_core_examples",
    "no_problem_type_spec_formed",
    "majority_core_examples_out_of_skill_scope",
    "skill_section_curriculum_mismatch",
    "systemic_answer_contract_failure",
    "runtime_generation_safety_risk",
    "required_sop_fields_missing"
}

DISALLOWED_SKILL_BLOCK_PROMOTIONS = {
    "small_number_source_quality_reject",
    "small_number_missing_answer",
    "single_broken_latex",
    "registry_rule_needs_review",
    "single_problem_type_pending",
    "enrichment_examples_excluded",
    "future_ai_judged_exists",
    "source_bank_only_exists",
    "contextual_application_exists",
    "runtime_ready_candidate_pending"
}

def validate_sop_preflight(project_root: str) -> dict:
    """
    Checks that all required SOP files exist, are readable,
    and have no severe mojibake.
    """
    root = Path(project_root)
    preflight_status = "PASS"
    required_sop_files = []
    errors = []
    
    # 3. General Mojibake Scanner Guard (Strictly flags replacement  without false positives)
    mojibake_patterns = [
        r'\uFFFD',          # Unicode replacement character ()
        r'\uFFFD[A-Z\d]',   # Corruption sequence
    ]
    
    for rel_path in REQUIRED_SOP_PATHS:
        full_path = root / rel_path
        exists = full_path.exists()
        readable = False
        mojibake_detected = False
        
        if exists:
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                readable = True
                
                # Scan for mojibake
                for pattern in mojibake_patterns:
                    if re.search(pattern, content):
                        mojibake_detected = True
                        errors.append(f"Mojibake detected in {rel_path.as_posix()} with pattern: {pattern}")
                        break
            except Exception as e:
                errors.append(f"Failed to read {rel_path.as_posix()}: {str(e)}")
        else:
            errors.append(f"SOP file missing: {rel_path.as_posix()}")
            
        required_sop_files.append({
            "path": rel_path.as_posix(),
            "exists": exists,
            "readable": readable,
            "mojibake_detected": mojibake_detected
        })
        
    if errors or any(not f["exists"] or not f["readable"] or f["mojibake_detected"] for f in required_sop_files):
        preflight_status = "FAIL"
        
    return {
        "sop_policy_version": SOP_POLICY_VERSION,
        "sop_preflight_status": preflight_status,
        "required_sop_files": required_sop_files,
        "errors": errors
    }

def build_sop_reference(project_root: str) -> dict:
    """
    Returns reference metadata to be included in reports if preflight passes.
    """
    preflight = validate_sop_preflight(project_root)
    return {
        "sop_policy_version": SOP_POLICY_VERSION,
        "highest_sop": (Path("docs") / "系統SOP" / "Gencode_AgentSkillV2整合" / "Gencode與AgentSkillV2整合總體設計_v0.2.md").as_posix(),
        "required_sop_files": preflight["required_sop_files"],
        "sop_preflight_status": preflight["sop_preflight_status"]
    }

def validate_skill_level_blockers(blockers, core_example_count: int = 0, has_valid_spec: bool = False) -> dict:
    """
    Ensures that none of the skill-level blockers violate SOP rules.
    Disallowed or unknown blockers trigger FAIL and a gate violation flag.
    """
    blocker_set = set(blockers or [])
    invalid_skill_level_blockers = []
    warnings = []
    
    # 2. Universal Core Sufficiency Gate Logic
    for b in blocker_set:
        is_disallowed = (
            b in DISALLOWED_SKILL_BLOCK_PROMOTIONS or
            b not in ALLOWED_SKILL_LEVEL_BLOCKERS or
            any(tok in b for tok in ["source_quality_reject", "broken_latex", "missing_answer", "needs_review"])
        )
        if is_disallowed:
            warnings.append(f"disallowed_blocker_demoted_to_warning:{b}")
            invalid_skill_level_blockers.append(b)
            
    sop_gate_status = "PASS"
    sop_violation = False
    
    if invalid_skill_level_blockers:
        sop_gate_status = "FAIL"
        sop_violation = True
        
    # Enforce the absolute minimum core check
    if core_example_count >= 2 and has_valid_spec:
        sop_gate_status = "PASS"
        sop_violation = False
        invalid_skill_level_blockers = []
        
    return {
        "sop_gate_status": sop_gate_status,
        "invalid_skill_level_blockers": invalid_skill_level_blockers,
        "allowed_skill_level_blockers": list(ALLOWED_SKILL_LEVEL_BLOCKERS),
        "sop_violation": sop_violation,
        "warnings": warnings
    }
