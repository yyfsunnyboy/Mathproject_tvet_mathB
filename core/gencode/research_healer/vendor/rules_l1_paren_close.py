"""L1 rule to repair unclosed parenthesis syntax error.

Rule id: L1_CLOSE_UNBALANCED_PARENTHESIS
"""

from __future__ import annotations

import ast
import re
from typing import Any, Mapping

RULE_ID = "L1_CLOSE_UNBALANCED_PARENTHESIS"
LAYER = "L1"
PRIORITY = 90
PRODUCTION_APPROVED = True
STATUS = "production_ready"

def _detect_parse_error(source: str) -> tuple[str | None, int | None]:
    try:
        ast.parse(source)
    except SyntaxError as exc:
        return str(exc), exc.lineno
    return None, None

def analyze_l1_paren_close(source: str) -> dict[str, Any]:
    err, lineno = _detect_parse_error(source)
    guards = {
        "parse_error_present": err is not None,
        "parse_error": err,
        "unbalanced_paren_error": err is not None and "was never closed" in err and "(" in err,
        "single_generate": False,
        "fix_parses": False,
        "fix_line": None,
        "fixed_source": None,
        "unique_trigger_verified": False,
    }

    if err is None:
        return {
            "guards": guards,
            "applicable": False,
            "triggered": False,
            "reason": "source_already_parses",
        }

    # Safeguard: Ensure def generate entry point is present
    if not re.search(r"def\s+generate\s*\(", source):
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "generate_entry_point_missing",
        }
    guards["single_generate"] = True

    if not guards["unbalanced_paren_error"]:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "syntax_error_not_unclosed_paren",
        }

    if lineno is None:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "missing_line_number",
        }

    lines = source.splitlines(keepends=True)
    if lineno > len(lines) or lineno <= 0:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "line_number_out_of_bounds",
        }

    # Attempt to fix the source by adding ')' at the end of the error line
    target_line = lines[lineno - 1]
    nl = "\n"
    if target_line.endswith("\r\n"):
        nl = "\r\n"
    
    stripped = target_line.rstrip("\r\n")
    fixed_line = stripped + ")" + nl
    
    trial_lines = list(lines)
    trial_lines[lineno - 1] = fixed_line
    trial_source = "".join(trial_lines)

    trial_err, _ = _detect_parse_error(trial_source)
    if trial_err is not None:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": f"trial_fix_still_fails_parse:{trial_err}",
        }

    # Strict check: Verify this line is the UNIQUE trigger and repair point
    # We verify that attempting to fix ANY other line in the file does NOT make it compile
    other_lines_parsable = False
    for i in range(len(lines)):
        if i == lineno - 1:
            continue
        # Skip purely blank lines to keep it fast
        if not lines[i].strip():
            continue
        
        alt_lines = list(lines)
        alt_target = alt_lines[i]
        alt_nl = "\n"
        if alt_target.endswith("\r\n"):
            alt_nl = "\r\n"
        alt_fixed = alt_target.rstrip("\r\n") + ")" + alt_nl
        alt_lines[i] = alt_fixed
        alt_source = "".join(alt_lines)
        
        alt_err, _ = _detect_parse_error(alt_source)
        if alt_err is None:
            # We found another line where adding ')' also makes it compile!
            # This violates uniqueness of the trigger line.
            other_lines_parsable = True
            break

    if other_lines_parsable:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "multiple_possible_repair_lines_exist",
        }

    guards["fix_parses"] = True
    guards["fix_line"] = lineno
    guards["fixed_source"] = trial_source
    guards["unique_trigger_verified"] = True

    return {
        "guards": guards,
        "applicable": True,
        "triggered": True,
        "reason": "all_transform_guards_ready",
    }

def is_applicable(source: str, context: Mapping[str, Any]) -> tuple[bool, Mapping[str, Any], str]:
    analysis = analyze_l1_paren_close(source)
    return bool(analysis["applicable"]), dict(analysis["guards"]), str(analysis["reason"])

def is_triggered(source: str, context: Mapping[str, Any]) -> tuple[bool, str]:
    analysis = analyze_l1_paren_close(source)
    if not analysis["applicable"]:
        return False, str(analysis["reason"])
    return bool(analysis["triggered"]), str(analysis["reason"])

def apply(source: str, context: Mapping[str, Any]) -> tuple[str, Mapping[str, Any], str]:
    analysis = analyze_l1_paren_close(source)
    validation: dict[str, Any] = {
        "rule_id": RULE_ID,
        "production_approved": PRODUCTION_APPROVED,
        "status": STATUS,
        "full_repair_to_pass_claimed": True,
        "semantic_preserving_claimed": True,
        "repair_scope": "syntax_error_unclosed_paren",
    }
    if not analysis.get("triggered"):
        return source, validation, f"apply_skipped:{analysis['reason']}"

    fixed_source = analysis["guards"]["fixed_source"]
    validation.update({
        "before_parse_error": analysis["guards"]["parse_error"],
        "after_parse_error": None,
        "ast_parse_success": True,
        "fixed_lineno": analysis["guards"]["fix_line"],
    })

    # Trigger re-evaluation if task and frozen parameters are provided in context
    task = context.get("task")
    frozen = context.get("frozen")
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

    return fixed_source, validation, "fixed_unbalanced_parenthesis_at_line_end"
