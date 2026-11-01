"""L1 draft rule (PAUSED — not on production allowlist).

Rule id: L1_COMMENT_ONLY_IF_INSERT_PASS

Status
------
Experimental / draft only. Removed from production ``RULE_ALLOWLIST`` after
external audit. Must not be described as safe, semantic-preserving, or
approved for formal commit.

Fixture ``fail_exact_ab2d_l1`` is exploratory parse-only evidence, not a
production repair-to-pass claim.

When explicitly enabled for research probes, inserts ``pass`` into a unique
comment-only ``if`` suite that currently fails to parse.
"""

from __future__ import annotations

import ast
import re
from typing import Any, Mapping

RULE_ID = "L1_COMMENT_ONLY_IF_INSERT_PASS"
LAYER = "L1"
# Draft priority only; not used by production allowlist.
PRIORITY = 50
PRODUCTION_APPROVED = False
STATUS = "paused_experimental_draft"

_IF_HEADER_RE = re.compile(r"^([ \t]*)if\b[^:\n]*:\s*(#.*)?$")
_ELIF_HEADER_RE = re.compile(r"^([ \t]*)elif\b")


def _indent_width(line: str) -> int:
    width = 0
    for ch in line:
        if ch == " ":
            width += 1
        elif ch == "\t":
            width += 4
        else:
            break
    return width


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def _is_comment_only(line: str) -> bool:
    return line.strip().startswith("#")


def _split_lines(source: str) -> list[str]:
    return source.splitlines(keepends=True)


def _newline_of(line: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return "\n"


def _detect_parse_error(source: str) -> str | None:
    try:
        ast.parse(source)
    except SyntaxError as exc:
        return str(exc)
    return None


def _find_comment_only_if_sites(source: str) -> list[dict[str, Any]]:
    lines = _split_lines(source)
    sites: list[dict[str, Any]] = []
    i = 0
    while i < len(lines):
        logical = lines[i].rstrip("\r\n")
        if _ELIF_HEADER_RE.match(logical):
            i += 1
            continue
        match = _IF_HEADER_RE.match(logical)
        if not match:
            i += 1
            continue

        if_indent = _indent_width(logical)
        j = i + 1
        suite_lines = 0
        comment_lines = 0
        while j < len(lines):
            suite_logical = lines[j].rstrip("\r\n")
            if _is_blank(suite_logical):
                suite_lines += 1
                j += 1
                continue
            suite_indent = _indent_width(suite_logical)
            if suite_indent <= if_indent:
                break
            if _is_comment_only(suite_logical):
                suite_lines += 1
                comment_lines += 1
                j += 1
                continue
            suite_lines = -1
            break

        if suite_lines < 0:
            i += 1
            continue
        if j < len(lines):
            next_logical = lines[j].rstrip("\r\n")
            if not _is_blank(next_logical) and _indent_width(next_logical) > if_indent:
                i += 1
                continue

        suite_indent = if_indent + 4
        for k in range(i + 1, j):
            cand = lines[k].rstrip("\r\n")
            if _is_comment_only(cand):
                suite_indent = _indent_width(cand)
                break

        sites.append(
            {
                "if_lineno": i + 1,
                "if_line_index": i,
                "suite_end_index": j,
                "insert_after_index": i,
                "if_indent": if_indent,
                "suite_indent": suite_indent,
                "comment_lines": comment_lines,
                "suite_span_lines": j - (i + 1),
            }
        )
        i += 1
    return sites


def analyze_l1_comment_only_if(source: str) -> dict[str, Any]:
    parse_error = _detect_parse_error(source)
    sites = _find_comment_only_if_sites(source)
    guards: dict[str, Any] = {
        "parse_error_present": parse_error is not None,
        "parse_error": parse_error,
        "comment_only_if_site_count": len(sites),
        "unique_comment_only_if": len(sites) == 1,
        "suite_only_blank_or_comment": False,
        "next_stmt_dedented_or_eof": False,
        "insert_pass_parses": False,
        "production_approved": PRODUCTION_APPROVED,
        "site": None,
    }

    if parse_error is None:
        return {
            "guards": guards,
            "applicable": False,
            "triggered": False,
            "reason": "source_already_parses",
        }

    if len(sites) != 1:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": "comment_only_if_not_unique_or_absent",
        }

    site = sites[0]
    guards["site"] = {
        "if_lineno": site["if_lineno"],
        "suite_indent": site["suite_indent"],
        "comment_lines": site["comment_lines"],
    }
    guards["suite_only_blank_or_comment"] = True
    guards["next_stmt_dedented_or_eof"] = True

    trial = _insert_pass(source, site)
    trial_err = _detect_parse_error(trial)
    guards["insert_pass_parses"] = trial_err is None
    if trial_err is not None:
        return {
            "guards": guards,
            "applicable": True,
            "triggered": False,
            "reason": f"insert_pass_still_unparseable:{trial_err}",
            "site": site,
        }

    return {
        "guards": guards,
        "applicable": True,
        "triggered": True,
        "reason": "all_transform_guards_ready",
        "site": site,
    }


def _insert_pass(source: str, site: Mapping[str, Any]) -> str:
    lines = _split_lines(source)
    idx = int(site["insert_after_index"])
    header = lines[idx]
    nl = _newline_of(header)
    indent = " " * int(site["suite_indent"])
    pass_line = f"{indent}pass{nl}"
    new_lines = lines[: idx + 1] + [pass_line] + lines[idx + 1 :]
    return "".join(new_lines)


def is_applicable(source: str, context: Mapping[str, Any]) -> tuple[bool, Mapping[str, Any], str]:
    analysis = analyze_l1_comment_only_if(source)
    return bool(analysis["applicable"]), dict(analysis["guards"]), str(analysis["reason"])


def is_triggered(source: str, context: Mapping[str, Any]) -> tuple[bool, str]:
    analysis = analyze_l1_comment_only_if(source)
    if not analysis["applicable"]:
        return False, str(analysis["reason"])
    return bool(analysis["triggered"]), str(analysis["reason"])


def apply(source: str, context: Mapping[str, Any]) -> tuple[str, Mapping[str, Any], str]:
    analysis = analyze_l1_comment_only_if(source)
    validation: dict[str, Any] = {
        "rule_id": RULE_ID,
        "production_approved": PRODUCTION_APPROVED,
        "status": STATUS,
        "full_repair_to_pass_claimed": False,
        "semantic_preserving_claimed": False,
        "repair_scope": "exploratory_parse_only",
    }
    if not analysis.get("triggered"):
        return source, validation, f"apply_skipped:{analysis['reason']}"

    site = analysis["site"]
    before_err = _detect_parse_error(source)
    new_source = _insert_pass(source, site)
    after_err = _detect_parse_error(new_source)
    validation.update(
        {
            "before_parse_error": before_err,
            "after_parse_error": after_err,
            "ast_parse_success": after_err is None,
            "inserted_pass_lineno": int(site["if_lineno"]) + 1,
            "suite_indent": int(site["suite_indent"]),
        }
    )
    if after_err is not None:
        return source, validation, "insert_pass_failed_parse_abort"

    task = context.get("task")
    frozen = context.get("frozen")
    if isinstance(task, Mapping) and isinstance(frozen, Mapping):
        from core.gencode.research_healer.vendor.evaluator_unavailable import classify_response

        outcome, _code, details = classify_response(
            new_source,
            {"oracle_payload": dict(frozen)},
            dict(task),
        )
        validation["evaluator_outcome"] = outcome
        validation["evaluator_rerun"] = True
        validation["evaluator_details_keys"] = sorted(details.keys())
        validation["next_layer_status"] = outcome
    else:
        validation["evaluator_rerun"] = False

    return new_source, validation, "inserted_pass_into_comment_only_if_suite"
