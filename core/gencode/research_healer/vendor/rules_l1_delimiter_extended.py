"""L1 Healer Rule: Close/Delete Unbalanced Delimiters (Extended).

This rule extends delimiter matching by enumerating all insertion/deletion
locations for parenthesized delimiters ((), {}, []) within the target error line,
enforcing a strict Unique Repair Constraint under a Single-location Guard.
"""

from __future__ import annotations

import ast
import re
from typing import Any, Mapping

RULE_ID = "L1_CLOSE_UNBALANCED_DELIMITER_EXTENDED"
LAYER = "L1"
PRIORITY = 95
STATUS = "experimental"
PRODUCTION_APPROVED = False

def split_comment(line: str) -> tuple[str, str]:
    """Split a line into (code_part, comment_part) by finding unquoted '#'."""
    in_single = False
    in_double = False
    in_triple_single = False
    in_triple_double = False
    
    idx = 0
    n = len(line)
    while idx < n:
        if idx + 2 < n and line[idx:idx+3] == "'''":
            if not in_double and not in_triple_double:
                in_triple_single = not in_triple_single
            idx += 3
            continue
        if idx + 2 < n and line[idx:idx+3] == '"""':
            if not in_single and not in_triple_single:
                in_triple_double = not in_triple_double
            idx += 3
            continue
        
        char = line[idx]
        if char == "\\" and idx + 1 < n:
            # Skip escaped character
            idx += 2
            continue
            
        if char == "'" and not in_double and not in_triple_double:
            in_single = not in_single
        elif char == '"' and not in_single and not in_triple_single:
            in_double = not in_double
        elif char == '#' and not in_single and not in_double and not in_triple_single and not in_triple_double:
            return line[:idx], line[idx:]
        idx += 1
    return line, ""

def analyze_l1_delimiter_extended(source: str) -> dict[str, Any]:
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
    
    # Check if this is the Special Case: Dict Unclosed Brace '{'
    is_dict_unclosed = False
    if "never closed" in err_msg.lower() and "{" in err_msg.lower():
        is_dict_unclosed = True
    elif "never closed" in err_msg.lower() and err_line.strip().endswith("{"):
        is_dict_unclosed = True

    # Precondition 2: Single-location Guard (bypass for dict unclosed brace)
    if not is_dict_unclosed:
        temp_lines = list(lines)
        # Replace the target line with a syntactically neutral 'pass' to preserve indentation blocks
        indent = len(err_line) - len(err_line.lstrip())
        temp_lines[line_num - 1] = " " * indent + "pass"
        commented_source = "\n".join(temp_lines)
        try:
            ast.parse(commented_source)
        except SyntaxError:
            res["reason"] = "commented_out_source_still_fails_parse_multiple_errors"
            return res

    # Precondition 3: Must contain def generate entry point
    if not re.search(r"^\s*def\s+generate\s*\(", source, re.MULTILINE):
        res["reason"] = "generate_entry_point_missing"
        return res

    # Delimiters we attempt to balance
    delimiters = "()[]{}"
    
    # Unique Repair Enumeration
    valid_candidates = []

    if is_dict_unclosed:
        # Get base indentation of the error line
        base_indent = len(err_line) - len(err_line.lstrip())
        
        # We attempt inserting '}' at the end of the error line
        # and at the end of any subsequent lines belonging to the same block (larger indentation)
        # up until we hit a line with equal or smaller indentation.
        target_lines_to_try = [line_num]
        
        for idx in range(line_num, len(lines)):
            l = lines[idx]
            if not l.strip():
                continue
            l_indent = len(l) - len(l.lstrip())
            if l_indent <= base_indent:
                break
            target_lines_to_try.append(idx + 1)
            
        for t_line in target_lines_to_try:
            t_line_content = lines[t_line - 1]
            code_part, comment_part = split_comment(t_line_content)
            
            # Insert '}' at the end of the code part (before comment)
            trial_line = code_part.rstrip() + "}" + comment_part
            
            trial_lines = list(lines)
            trial_lines[t_line - 1] = trial_line
            trial_source = "\n".join(trial_lines)
            try:
                ast.parse(trial_source)
                valid_candidates.append({
                    "type": f"insert_dict_brace_line_{t_line}",
                    "fixed_source": trial_source,
                    "fix_line": t_line
                })
            except SyntaxError:
                pass
    else:
        # General Case: Enumerate all possible insertion/deletion points in err_line (excluding comments)
        code_part, comment_part = split_comment(err_line)
        
        # 1. Insertion Trials
        for pos in range(len(code_part) + 1):
            for char in delimiters:
                trial_code = code_part[:pos] + char + code_part[pos:]
                trial_line = trial_code + comment_part
                lines_copy = list(lines)
                lines_copy[line_num - 1] = trial_line
                trial_source = "\n".join(lines_copy)
                try:
                    ast.parse(trial_source)
                    valid_candidates.append({
                        "type": f"insert_{char}",
                        "fixed_source": trial_source,
                        "fix_line": line_num,
                        "pos": pos
                    })
                except SyntaxError:
                    pass
                    
        # 2. Deletion Trials
        for pos in range(len(code_part)):
            if code_part[pos] in delimiters:
                trial_code = code_part[:pos] + code_part[pos+1:]
                trial_line = trial_code + comment_part
                lines_copy = list(lines)
                lines_copy[line_num - 1] = trial_line
                trial_source = "\n".join(lines_copy)
                try:
                    ast.parse(trial_source)
                    valid_candidates.append({
                        "type": f"delete_{code_part[pos]}",
                        "fixed_source": trial_source,
                        "fix_line": line_num,
                        "pos": pos
                    })
                except SyntaxError:
                    pass

    # Unique Repair Constraint check
    if len(valid_candidates) == 0:
        res["reason"] = "no_repair_candidate_passed_ast_parse"
        return res
    elif len(valid_candidates) > 1:
        res["reason"] = f"multiple_repair_candidates_passed_parse_count_{len(valid_candidates)}"
        return res
        
    best_cand = valid_candidates[0]
    res["triggered"] = True
    res["reason"] = "all_transform_guards_ready"
    res["guards"] = {
        "fixed_source": best_cand["fixed_source"],
        "fix_line": best_cand["fix_line"],
        "repair_type": best_cand["type"],
        "parse_error": err_msg
    }
    return res

def is_applicable(source: str, context: Mapping[str, Any] | None = None) -> tuple[bool, Mapping[str, Any], str]:
    ctx = dict(context or {})
    analysis = analyze_l1_delimiter_extended(source)
    ctx["l1_delimiter_analysis"] = analysis
    return analysis["applicable"], ctx, analysis["reason"]

def is_triggered(source: str, context: Mapping[str, Any] | None = None) -> tuple[bool, str]:
    ctx = dict(context or {})
    analysis = ctx.get("l1_delimiter_analysis") or analyze_l1_delimiter_extended(source)
    return analysis["triggered"], analysis["reason"]

def apply(source: str, context: Mapping[str, Any] | None = None) -> tuple[str, Mapping[str, Any], str]:
    ctx = dict(context or {})
    analysis = ctx.get("l1_delimiter_analysis") or analyze_l1_delimiter_extended(source)
    validation: dict[str, Any] = {
        "rule_id": RULE_ID,
        "production_approved": PRODUCTION_APPROVED,
        "status": STATUS,
        "full_repair_to_pass_claimed": True,
        "semantic_preserving_claimed": True,
        "repair_scope": "syntax_error_unbalanced_delimiter",
    }
    
    if not analysis.get("triggered"):
        return source, validation, f"apply_skipped:{analysis['reason']}"
        
    fixed_source = analysis["guards"]["fixed_source"]
    validation.update({
        "before_parse_error": analysis["guards"]["parse_error"],
        "after_parse_error": None,
        "ast_parse_success": True,
        "fixed_lineno": analysis["guards"]["fix_line"],
        "repair_type": analysis["guards"]["repair_type"]
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

    return fixed_source, validation, f"fixed_unbalanced_delimiter_by_{analysis['guards']['repair_type']}"
