"""L1 Healer Rule: Prose Residue Narrow.

This rule targets思維鏈 Prose residues in two narrow subcategories:
- Subclass A: Standalone prose block of 1-N lines.
- Subclass B: End-of-line prose residue.
Ensures strict uniqueness constraint and single-location safety.
"""

from __future__ import annotations

import ast
import re
from typing import Any, Mapping

RULE_ID = "L1_PROSE_RESIDUE_NARROW"
LAYER = "L1"
PRIORITY = 98
STATUS = "experimental"
PRODUCTION_APPROVED = False

def is_pseudocode_label(line: str) -> bool:
    """Check if line is a pseudocode label like 'inner_parenthesis:'."""
    stripped = line.strip()
    if stripped.endswith(":") and not any(k in stripped for k in ["if", "else", "elif", "try", "except", "finally", "for", "while", "with", "def", "class"]):
        return True
    return False

def analyze_l1_prose_narrow(source: str) -> dict[str, Any]:
    res = {
        "applicable": False,
        "triggered": False,
        "reason": "initialized",
        "guards": {}
    }
    
    # Precondition 1: Source must fail to compile
    try:
        ast.parse(source)
        res["reason"] = "source_already_parses"
        return res
    except SyntaxError as exc:
        err_msg = str(exc)
        line_num = exc.lineno
        
    if not line_num:
        res["reason"] = "no_line_number_in_syntax_error"
        return res
        
    lines = source.splitlines()
    if line_num < 1 or line_num > len(lines):
        res["reason"] = "invalid_line_number"
        return res
        
    err_line = lines[line_num - 1]
    res["applicable"] = True
    
    # Precondition 2: Must contain def generate entry point
    if not re.search(r"^\s*def\s+generate\s*\(", source, re.MULTILINE):
        res["reason"] = "generate_entry_point_missing"
        return res

    blacklist_keywords = ["return", "def", "class", "import"]
    valid_candidates = []

    # --- Subclass A: Standalone Prose Block (continuous 1-N lines) ---
    # We explore continuous ranges [start, end] around line_num (from -3 lines to +3 lines)
    min_idx = max(0, line_num - 4)
    max_idx = min(len(lines), line_num + 3)
    
    for start in range(min_idx, line_num):
        for end in range(line_num, max_idx + 1):
            candidate_lines = lines[start:end]
            
            # Constraints:
            # 1. No empty block
            if not candidate_lines:
                continue
            # 2. None of the lines contain blacklist keywords
            if any(any(k in l for k in blacklist_keywords) for l in candidate_lines):
                continue
            # 3. None of the lines are pseudocode labels
            if any(is_pseudocode_label(l) for l in candidate_lines):
                continue
                
            # Trial repair: comment out this block
            trial_lines = list(lines)
            for idx in range(start, end):
                # Preserving indentation, comment out the line
                indent = len(trial_lines[idx]) - len(trial_lines[idx].lstrip())
                trial_lines[idx] = " " * indent + "# " + trial_lines[idx].lstrip()
                
            trial_source = "\n".join(trial_lines)
            try:
                ast.parse(trial_source)
                # Single-location Guard: replacing this block with a single 'pass' must parse cleanly
                guard_lines = list(lines)
                indent = len(lines[start]) - len(lines[start].lstrip())
                # Replace whole block with a single pass
                guard_lines[start:end] = [" " * indent + "pass"]
                guard_source = "\n".join(guard_lines)
                ast.parse(guard_source)
                
                valid_candidates.append({
                    "subclass": "A",
                    "fixed_source": trial_source,
                    "target_range": (start + 1, end),
                    "repair_type": f"comment_block_{start+1}_to_{end}"
                })
            except SyntaxError:
                pass

    # --- Subclass B: End-of-line Prose Residue ---
    # We truncate the err_line at different character positions
    # err_line_stripped for pos loop
    for pos in range(len(err_line) + 1):
        prefix = err_line[:pos]
        suffix = err_line[pos:]
        
        # Constraints:
        # 1. prefix must not be completely empty/whitespace (must have statement)
        if not prefix.strip():
            continue
        # 2. suffix must not contain blacklist keywords
        if any(k in suffix for k in blacklist_keywords):
            continue
        # 3. suffix must not be a pseudocode label
        if is_pseudocode_label(suffix):
            continue
            
        # Trial repair: replace err_line with prefix
        trial_lines = list(lines)
        trial_lines[line_num - 1] = prefix
        trial_source = "\n".join(trial_lines)
        try:
            ast.parse(trial_source)
            # Single-location Guard: replacing this line with pass must parse cleanly
            guard_lines = list(lines)
            indent = len(err_line) - len(err_line.lstrip())
            guard_lines[line_num - 1] = " " * indent + "pass"
            guard_source = "\n".join(guard_lines)
            ast.parse(guard_source)
            
            valid_candidates.append({
                "subclass": "B",
                "fixed_source": trial_source,
                "target_range": (line_num, line_num),
                "repair_type": f"truncate_line_at_{pos}"
            })
        except SyntaxError:
            pass

    # Strict Uniqueness Constraint
    if len(valid_candidates) == 0:
        res["reason"] = "no_prose_repair_candidate_passed_ast_parse"
        return res
    elif len(valid_candidates) > 1:
        res["reason"] = f"multiple_prose_candidates_passed_parse_count_{len(valid_candidates)}"
        return res
        
    best_cand = valid_candidates[0]
    res["triggered"] = True
    res["reason"] = "all_transform_guards_ready"
    res["guards"] = {
        "fixed_source": best_cand["fixed_source"],
        "fix_line": best_cand["target_range"][0],
        "repair_type": best_cand["repair_type"],
        "subclass": best_cand["subclass"],
        "parse_error": err_msg
    }
    return res

def is_applicable(source: str, context: Mapping[str, Any] | None = None) -> tuple[bool, Mapping[str, Any], str]:
    ctx = dict(context or {})
    analysis = analyze_l1_prose_narrow(source)
    ctx["l1_prose_analysis"] = analysis
    return analysis["applicable"], ctx, analysis["reason"]

def is_triggered(source: str, context: Mapping[str, Any] | None = None) -> tuple[bool, str]:
    ctx = dict(context or {})
    analysis = ctx.get("l1_prose_analysis") or analyze_l1_prose_narrow(source)
    return analysis["triggered"], analysis["reason"]

def apply(source: str, context: Mapping[str, Any] | None = None) -> tuple[str, Mapping[str, Any], str]:
    ctx = dict(context or {})
    analysis = ctx.get("l1_prose_analysis") or analyze_l1_prose_narrow(source)
    validation: dict[str, Any] = {
        "rule_id": RULE_ID,
        "production_approved": PRODUCTION_APPROVED,
        "status": STATUS,
        "full_repair_to_pass_claimed": True,
        "semantic_preserving_claimed": True,
        "repair_scope": "syntax_error_prose_residue",
    }
    
    if not analysis.get("triggered"):
        return source, validation, f"apply_skipped:{analysis['reason']}"
        
    fixed_source = analysis["guards"]["fixed_source"]
    validation.update({
        "before_parse_error": analysis["guards"]["parse_error"],
        "after_parse_error": None,
        "ast_parse_success": True,
        "fixed_lineno": analysis["guards"]["fix_line"],
        "repair_type": analysis["guards"]["repair_type"],
        "subclass": analysis["guards"]["subclass"]
    })
    
    task = ctx.get("task")
    frozen = ctx.get("frozen")
    if isinstance(task, Mapping) and isinstance(frozen, Mapping):
        from core.gencode.research_healer.vendor.evaluator_unavailable import classify_response

        outcome, _code, details = classify_response(
            fixed_source,
            {"oracle_payload": dict(frozen)},
            dict(task),
        )
        validation["evaluator_outcome"] = outcome
        validation["evaluator_rerun"] = True
        validation["evaluator_details_keys"] = sorted(details.keys())
        validation["next_layer_status"] = outcome
    else:
        validation["evaluator_rerun"] = False

    return fixed_source, validation, f"fixed_prose_residue_by_{analysis['guards']['repair_type']}"
