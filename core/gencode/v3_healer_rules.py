# -*- coding: utf-8 -*-
"""V3-scoped repair rules ported from the Aggressive Healer v2 research stack.

RETIRED FROM V3 (see ``core.gencode.v3_healer_adapter``); physical deletion pending.

Only rules that are independent of the Math16 research dataset (task_id,
cell_id, condition, frozen oracle payload, research Ops API SSOT) are
executable here.  Every other research rule is registered as a disabled
candidate so callers get an explicit ABSTAIN reason instead of silence.

Rules are pure ``code -> RuleProposal`` functions: no I/O, no evaluator, no
expected answer, at most one deterministic candidate per call.
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

RESEARCH_REPOSITORY = "yyfsunnyboy/MathProject_AST_Research_HealerBoundary"
RESEARCH_COMMIT = "f499a7472a739666fb3ba54e806bfc85f71eba75"
RESEARCH_LICENSE = "MIT (declared in source README.md; no LICENSE file at research commit)"
RESEARCH_PC_FROZEN_MANIFEST_SHA256 = "4b45ec08784146b567b01ae5f46d561d76cf10209df7b50f5eedd87d396853e5"
RESEARCH_PC_FINAL_AGGREGATE_SHA256 = "1d5ecbc4a21f9985e38f418adbeba41672c757668c4a05f83e40dc97d59ec128"
RESEARCH_TIER_MAPPING_MANIFEST = {
    "path": "docs/experiments/manifests/math16_healer_rule_id_tier_mapping_v1.json",
    "git_blob_sha1": "24533d1d3500cf96ccfb7ce463f40c38c1e742a7",
}
V3_RULESET_VERSION = "v3.healer.rules.1"

FAILURE_SYNTAX = "syntax_error"
FAILURE_NAME = "name_error"

SCOPE_INSERT_CLOSING_DELIMITER = "insert_single_closing_delimiter"
SCOPE_REPLACE_FULLWIDTH = "replace_fullwidth_syntax_punctuation"
SCOPE_INSERT_PASS_LINE = "insert_single_pass_line"
SCOPE_INSERT_STDLIB_IMPORT = "insert_single_stdlib_import_line"
SCOPE_NONE = "none"

MAX_ERROR_LINE_LENGTH = 2000

FULLWIDTH_PUNCT_MAP: dict[str, str] = {
    "\uff0c": ",",
    "\uff1a": ":",
    "\uff1b": ";",
    "\uff08": "(",
    "\uff09": ")",
    "\uff3b": "[",
    "\uff3d": "]",
    "\uff5b": "{",
    "\uff5d": "}",
}

STDLIB_IMPORT_MAP: dict[str, str] = {
    "Fraction": "from fractions import Fraction",
    "Decimal": "from decimal import Decimal",
    "defaultdict": "from collections import defaultdict",
    "Counter": "from collections import Counter",
    "deque": "from collections import deque",
}

_A3_ALLOWED_SUITE_OWNERS = frozenset({"if", "elif", "else", "for", "try", "except", "finally", "with"})


@dataclass(frozen=True)
class RuleProposal:
    rule_id: str
    applied: bool
    source_out: str
    edit_scope: str = SCOPE_NONE
    reason: str = ""
    candidate_count: int = 0
    evidence: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuleProvenance:
    source_path: str
    git_blob_sha1: str
    research_status: str
    research_evidence: str = ""


@dataclass(frozen=True)
class V3HealerRuleSpec:
    rule_id: str
    research_tier: str
    layer_role: str
    v3_status: str  # "executable" | "disabled_candidate"
    trigger: str
    eligibility: tuple[str, ...]
    contract_prerequisites: tuple[str, ...]
    edit_scope: str
    forbidden_semantics: tuple[str, ...]
    validation_requirements: tuple[str, ...]
    abstain_conditions: tuple[str, ...]
    provenance: RuleProvenance
    v3_adaptations: tuple[str, ...] = ()
    disabled_reason: str = ""
    apply: Callable[[str, Mapping[str, Any]], RuleProposal] | None = None

    @property
    def executable(self) -> bool:
        return self.v3_status == "executable" and self.apply is not None

    def describe(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "research_tier": self.research_tier,
            "layer_role": self.layer_role,
            "v3_status": self.v3_status,
            "trigger": self.trigger,
            "eligibility": list(self.eligibility),
            "contract_prerequisites": list(self.contract_prerequisites),
            "edit_scope": self.edit_scope,
            "forbidden_semantics": list(self.forbidden_semantics),
            "validation_requirements": list(self.validation_requirements),
            "abstain_conditions": list(self.abstain_conditions),
            "v3_adaptations": list(self.v3_adaptations),
            "disabled_reason": self.disabled_reason,
            "provenance": {
                "repository": RESEARCH_REPOSITORY,
                "commit": RESEARCH_COMMIT,
                "source_path": self.provenance.source_path,
                "git_blob_sha1": self.provenance.git_blob_sha1,
                "research_status": self.provenance.research_status,
                "research_evidence": self.provenance.research_evidence,
            },
        }


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def parse_error(code: str) -> SyntaxError | None:
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return exc
    return None


def is_parseable(code: str) -> bool:
    return parse_error(code) is None


def ast_equivalence_key(code: str) -> str:
    return ast.dump(ast.parse(code))


def split_line_comment(line: str) -> tuple[str, str]:
    """Split a physical line into (code_part, comment_part) respecting quotes."""
    in_single = in_double = in_triple_single = in_triple_double = False
    idx = 0
    n = len(line)
    while idx < n:
        if line[idx : idx + 3] == "'''":
            if not in_double and not in_triple_double:
                in_triple_single = not in_triple_single
            idx += 3
            continue
        if line[idx : idx + 3] == '"""':
            if not in_single and not in_triple_single:
                in_triple_double = not in_triple_double
            idx += 3
            continue
        ch = line[idx]
        if ch == "\\" and idx + 1 < n:
            idx += 2
            continue
        if ch == "'" and not in_double and not in_triple_double:
            in_single = not in_single
        elif ch == '"' and not in_single and not in_triple_single:
            in_double = not in_double
        elif ch == "#" and not (in_single or in_double or in_triple_single or in_triple_double):
            return line[:idx], line[idx:]
        idx += 1
    return line, ""


def _newline_of(line: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return ""


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


def _abstain(rule_id: str, code: str, reason: str, **evidence: Any) -> RuleProposal:
    return RuleProposal(rule_id=rule_id, applied=False, source_out=code, reason=reason, evidence=evidence)


def _closing_insert_classes(
    code: str,
    lineno: int,
    chars: tuple[str, ...],
) -> dict[str, dict[str, Any]]:
    """Enumerate single closing-delimiter inserts on one line, grouped by AST equivalence.

    Two byte positions that yield the same AST (e.g. before/after a space) are
    the same repair; distinct ASTs are distinct repairs and make the site ambiguous.
    """
    lines = code.splitlines(keepends=True)
    err_line = lines[lineno - 1]
    nl = _newline_of(err_line)
    body = err_line[: len(err_line) - len(nl)] if nl else err_line
    code_part, comment_part = split_line_comment(body)
    classes: dict[str, dict[str, Any]] = {}
    for pos in range(len(code_part) + 1):
        for ch in chars:
            trial_lines = list(lines)
            trial_lines[lineno - 1] = code_part[:pos] + ch + code_part[pos:] + comment_part + nl
            trial = "".join(trial_lines)
            if not is_parseable(trial):
                continue
            key = ast_equivalence_key(trial)
            classes.setdefault(
                key,
                {"lineno": lineno, "pos": pos, "delimiter_char": ch, "fixed_source": trial, "positions": []},
            )["positions"].append(pos)
    return classes


def string_or_comment_mask(code: str) -> list[bool] | None:
    """Per-character mask of STRING / COMMENT / f-string token spans; None if untokenizable."""
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except (tokenize.TokenError, SyntaxError, IndentationError):
        return None
    protected_types = {tokenize.STRING, tokenize.COMMENT}
    for name in ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END", "TSTRING_START", "TSTRING_MIDDLE", "TSTRING_END"):
        tok_type = getattr(tokenize, name, None)
        if tok_type is not None:
            protected_types.add(tok_type)
    lines = code.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    mask = [False] * len(code)
    for tok in tokens:
        if tok.type not in protected_types:
            continue
        (sr, sc), (er, ec) = tok.start, tok.end
        if sr - 1 >= len(offsets) or er - 1 >= len(offsets):
            continue
        start = offsets[sr - 1] + sc
        end = offsets[er - 1] + ec
        for i in range(max(0, start), min(len(code), end)):
            mask[i] = True
    return mask


# ---------------------------------------------------------------------------
# Tier A — L1_CLOSE_UNBALANCED_PARENTHESIS
# ---------------------------------------------------------------------------

RULE_A_L1_PAREN = "L1_CLOSE_UNBALANCED_PARENTHESIS"


def apply_a_l1_close_unbalanced_parenthesis(code: str, context: Mapping[str, Any]) -> RuleProposal:
    exc = parse_error(code)
    if exc is None:
        return _abstain(RULE_A_L1_PAREN, code, "source_already_parses")
    if not str(exc.msg or "").startswith("'(' was never closed"):
        return _abstain(RULE_A_L1_PAREN, code, "syntax_error_not_unclosed_paren", parse_error=str(exc.msg))
    if not re.search(r"^\s*def\s+generate\s*\(", code, re.MULTILINE):
        return _abstain(RULE_A_L1_PAREN, code, "generate_entry_point_missing")
    lines = code.splitlines(keepends=True)
    lineno = exc.lineno
    if not lineno or lineno < 1 or lineno > len(lines):
        return _abstain(RULE_A_L1_PAREN, code, "line_number_out_of_bounds")
    if len(lines[lineno - 1]) > MAX_ERROR_LINE_LENGTH:
        return _abstain(RULE_A_L1_PAREN, code, "error_line_too_long")

    def _append_paren(index: int) -> str:
        target = lines[index]
        nl = _newline_of(target)
        trial_lines = list(lines)
        trial_lines[index] = target[: len(target) - len(nl)] + ")" + nl
        return "".join(trial_lines)

    trial = _append_paren(lineno - 1)
    if not is_parseable(trial):
        return _abstain(RULE_A_L1_PAREN, code, "trial_fix_still_fails_parse")
    for i, line in enumerate(lines):
        if i == lineno - 1 or not line.strip():
            continue
        if is_parseable(_append_paren(i)):
            return _abstain(RULE_A_L1_PAREN, code, "multiple_possible_repair_lines_exist", other_line=i + 1)
    classes = _closing_insert_classes(code, lineno, (")",))
    if len(classes) != 1:
        return RuleProposal(
            rule_id=RULE_A_L1_PAREN,
            applied=False,
            source_out=code,
            reason=f"ambiguous_intra_line_paren_positions_{len(classes)}",
            candidate_count=len(classes),
        )
    if ast_equivalence_key(trial) not in classes:
        return _abstain(RULE_A_L1_PAREN, code, "end_of_line_fix_not_in_unique_class")
    return RuleProposal(
        rule_id=RULE_A_L1_PAREN,
        applied=True,
        source_out=trial,
        edit_scope=SCOPE_INSERT_CLOSING_DELIMITER,
        reason="fixed_unbalanced_parenthesis_at_line_end",
        candidate_count=1,
        evidence={"lineno": lineno, "parse_error": str(exc.msg)},
    )


# ---------------------------------------------------------------------------
# Tier B1 — core.normalize_fullwidth_python_punctuation
# ---------------------------------------------------------------------------

RULE_B1_FULLWIDTH = "core.normalize_fullwidth_python_punctuation"


def normalize_fullwidth_python_punctuation(code: str) -> str:
    """Replace mapped fullwidth punctuation outside string/comment tokens; fail-closed."""
    if not code:
        return code
    mask = string_or_comment_mask(code)
    if mask is None:
        return code
    chars = list(code)
    changed = False
    for i, ch in enumerate(chars):
        if ch in FULLWIDTH_PUNCT_MAP and not mask[i]:
            chars[i] = FULLWIDTH_PUNCT_MAP[ch]
            changed = True
    if not changed:
        return code
    healed = "".join(chars)
    return healed if is_parseable(healed) else code


def apply_b1_fullwidth(code: str, context: Mapping[str, Any]) -> RuleProposal:
    if not code:
        return _abstain(RULE_B1_FULLWIDTH, code, "empty_source_noop")
    if is_parseable(code):
        return _abstain(RULE_B1_FULLWIDTH, code, "source_already_parses")
    healed = normalize_fullwidth_python_punctuation(code)
    if healed == code:
        return _abstain(RULE_B1_FULLWIDTH, code, "no_unprotected_mapped_or_fail_closed")
    if len(healed) != len(code):
        return _abstain(RULE_B1_FULLWIDTH, code, "unexpected_length_change")
    mapped = sum(1 for a, b in zip(code, healed) if a != b)
    return RuleProposal(
        rule_id=RULE_B1_FULLWIDTH,
        applied=True,
        source_out=healed,
        edit_scope=SCOPE_REPLACE_FULLWIDTH,
        reason="fullwidth_syntax_punctuation_normalized",
        candidate_count=1,
        evidence={"mapped_char_count": mapped},
    )


# ---------------------------------------------------------------------------
# Tier B2 — TIER_A_UNIQUE_MISSING_DELIMITER_REPAIR_V1
# ---------------------------------------------------------------------------

RULE_B2_DELIMITER = "TIER_A_UNIQUE_MISSING_DELIMITER_REPAIR_V1"
_DELIMITER_ERR_RE = re.compile(r"never closed|unmatched|unexpected EOF|EOF while parsing", re.IGNORECASE)
_EMPTY_SUITE_ERR_RE = re.compile(r"expected an indented block|IndentationError", re.IGNORECASE)


def apply_b2_unique_missing_delimiter(code: str, context: Mapping[str, Any]) -> RuleProposal:
    exc = parse_error(code)
    if exc is None:
        return _abstain(RULE_B2_DELIMITER, code, "source_already_parses")
    msg = str(exc.msg or "")
    if not exc.lineno:
        return _abstain(RULE_B2_DELIMITER, code, "missing_line_number", parse_error=msg)
    if _EMPTY_SUITE_ERR_RE.search(msg) or not _DELIMITER_ERR_RE.search(msg):
        return _abstain(RULE_B2_DELIMITER, code, "syntax_error_not_delimiter", parse_error=msg)
    lines = code.splitlines(keepends=True)
    if exc.lineno > len(lines):
        return _abstain(RULE_B2_DELIMITER, code, "line_number_out_of_bounds")
    if len(lines[exc.lineno - 1]) > MAX_ERROR_LINE_LENGTH:
        return _abstain(RULE_B2_DELIMITER, code, "error_line_too_long")
    classes = _closing_insert_classes(code, exc.lineno, (")", "]", "}"))
    if not classes:
        return _abstain(RULE_B2_DELIMITER, code, "no_unique_closing_insert", parse_error=msg)
    if len(classes) > 1:
        return RuleProposal(
            rule_id=RULE_B2_DELIMITER,
            applied=False,
            source_out=code,
            reason=f"ambiguous_closing_inserts_count_{len(classes)}",
            candidate_count=len(classes),
            evidence={"parse_error": msg},
        )
    cand = next(iter(classes.values()))
    return RuleProposal(
        rule_id=RULE_B2_DELIMITER,
        applied=True,
        source_out=cand["fixed_source"],
        edit_scope=SCOPE_INSERT_CLOSING_DELIMITER,
        reason="single_closing_delimiter_insert",
        candidate_count=1,
        evidence={
            "lineno": cand["lineno"],
            "pos": cand["pos"],
            "delimiter_char": cand["delimiter_char"],
            "ast_equivalent_positions": list(cand["positions"]),
            "parse_error": msg,
        },
    )


# ---------------------------------------------------------------------------
# Tier B3 — TIER_A_EMPTY_SUITE_INSERT_PASS_V1
# ---------------------------------------------------------------------------

RULE_B3_EMPTY_SUITE = "TIER_A_EMPTY_SUITE_INSERT_PASS_V1"
_HEADER_RE = re.compile(
    r"^([ \t]*)(if|elif|else|for|while|try|except|finally|with|def|class|match|case)\b.*:$"
)


def _find_empty_suite_sites(code: str) -> list[dict[str, Any]]:
    lines = code.splitlines(keepends=True)
    sites: list[dict[str, Any]] = []
    for i, raw in enumerate(lines):
        logical = raw.rstrip("\r\n")
        match = _HEADER_RE.match(split_line_comment(logical)[0].rstrip())
        if not match:
            continue
        header_indent = _indent_width(logical)
        j = i + 1
        saw_exec = False
        comment_indent = None
        while j < len(lines):
            suite_logical = lines[j].rstrip("\r\n")
            if not suite_logical.strip():
                j += 1
                continue
            suite_indent = _indent_width(suite_logical)
            if suite_indent <= header_indent:
                break
            if suite_logical.strip().startswith("#"):
                if comment_indent is None:
                    comment_indent = suite_indent
                j += 1
                continue
            saw_exec = True
            break
        if saw_exec:
            continue
        sites.append(
            {
                "header_index": i,
                "header_lineno": i + 1,
                "suite_owner_kind": match.group(2),
                "comment_only_suite": comment_indent is not None,
                "suite_indent": comment_indent if comment_indent is not None else header_indent + 4,
            }
        )
    return sites


def apply_b3_empty_suite_insert_pass(code: str, context: Mapping[str, Any]) -> RuleProposal:
    exc = parse_error(code)
    if exc is None:
        return _abstain(RULE_B3_EMPTY_SUITE, code, "source_already_parses")
    msg = str(exc.msg or "").lower()
    if "indented block" not in msg:
        return _abstain(RULE_B3_EMPTY_SUITE, code, "syntax_error_not_empty_suite", parse_error=str(exc.msg))
    sites = _find_empty_suite_sites(code)
    if not sites:
        return _abstain(RULE_B3_EMPTY_SUITE, code, "no_empty_suite_site")
    if len(sites) > 1:
        return RuleProposal(
            rule_id=RULE_B3_EMPTY_SUITE,
            applied=False,
            source_out=code,
            reason=f"ambiguous_empty_suites_count_{len(sites)}",
            candidate_count=len(sites),
        )
    site = sites[0]
    if site["suite_owner_kind"] not in _A3_ALLOWED_SUITE_OWNERS:
        return _abstain(
            RULE_B3_EMPTY_SUITE,
            code,
            f"suite_owner_not_allowed_in_v3:{site['suite_owner_kind']}",
        )
    if not site["comment_only_suite"]:
        return _abstain(RULE_B3_EMPTY_SUITE, code, "suite_not_explicitly_comment_only_possible_misindented_body")
    lines = code.splitlines(keepends=True)
    idx = int(site["header_index"])
    nl = _newline_of(lines[idx]) or "\n"
    fixed = "".join(lines[: idx + 1] + [" " * int(site["suite_indent"]) + "pass" + nl] + lines[idx + 1 :])
    if not is_parseable(fixed):
        return _abstain(RULE_B3_EMPTY_SUITE, code, "empty_suite_insert_pass_still_unparseable")
    return RuleProposal(
        rule_id=RULE_B3_EMPTY_SUITE,
        applied=True,
        source_out=fixed,
        edit_scope=SCOPE_INSERT_PASS_LINE,
        reason="single_empty_suite_insert_pass",
        candidate_count=1,
        evidence={
            "header_lineno": site["header_lineno"],
            "insert_lineno": site["header_lineno"] + 1,
            "suite_owner_kind": site["suite_owner_kind"],
        },
    )


# ---------------------------------------------------------------------------
# Tier B4 — TIER_A_UNIQUE_IMPORT_BINDING_REPAIR_V1
# ---------------------------------------------------------------------------

RULE_B4_IMPORT = "TIER_A_UNIQUE_IMPORT_BINDING_REPAIR_V1"


def _collect_bound_names(tree: ast.AST) -> set[str]:
    bound: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            bound.add(node.name)
            args = node.args
            for arg in args.args + args.posonlyargs + args.kwonlyargs:
                bound.add(arg.arg)
            if args.vararg:
                bound.add(args.vararg.arg)
            if args.kwarg:
                bound.add(args.kwarg.arg)
        elif isinstance(node, ast.ClassDef):
            bound.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            bound.add(node.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                bound.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    bound.add(alias.asname or alias.name)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            bound.update(node.names)
    return bound


def _import_insert_index(tree: ast.Module) -> int:
    """0-based physical line index after the module docstring and any __future__ imports."""
    end_line = 0
    for i, node in enumerate(tree.body):
        is_docstring = (
            i == 0
            and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
        is_future = isinstance(node, ast.ImportFrom) and node.module == "__future__"
        if is_docstring or is_future:
            end_line = int(getattr(node, "end_lineno", node.lineno))
            continue
        break
    return end_line


def apply_b4_unique_import_binding(code: str, context: Mapping[str, Any]) -> RuleProposal:
    import builtins

    exc = parse_error(code)
    if exc is not None:
        return _abstain(RULE_B4_IMPORT, code, "source_not_parseable")
    name_error_name = str(context.get("name_error_name") or "").strip()
    if not name_error_name:
        return _abstain(RULE_B4_IMPORT, code, "no_runtime_name_error_evidence")
    tree = ast.parse(code)
    bound = _collect_bound_names(tree) | set(dir(builtins))
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    missing = sorted(used - bound)
    repairable = [n for n in missing if n in STDLIB_IMPORT_MAP]
    if not missing:
        return _abstain(RULE_B4_IMPORT, code, "no_unique_stdlib_binding_gap")
    if len(repairable) != 1 or len(missing) != 1:
        return _abstain(
            RULE_B4_IMPORT,
            code,
            "non_unique_or_unmapped_binding_gaps",
            missing=missing,
        )
    name = repairable[0]
    if name != name_error_name:
        return _abstain(RULE_B4_IMPORT, code, "runtime_name_error_does_not_match_static_gap", missing=missing)
    stmt = STDLIB_IMPORT_MAP[name]
    if stmt in code:
        return _abstain(RULE_B4_IMPORT, code, "equivalent_binding_already_present")
    lines = code.splitlines(keepends=True)
    idx = _import_insert_index(tree)
    nl = _newline_of(lines[0]) if lines else "\n"
    nl = nl or "\n"
    fixed = "".join(lines[:idx] + [stmt + nl] + lines[idx:])
    try:
        compile(fixed, "<v3_healer_b4>", "exec")
    except SyntaxError:
        return _abstain(RULE_B4_IMPORT, code, "import_insert_not_compilable")
    return RuleProposal(
        rule_id=RULE_B4_IMPORT,
        applied=True,
        source_out=fixed,
        edit_scope=SCOPE_INSERT_STDLIB_IMPORT,
        reason="single_import_binding_insert",
        candidate_count=1,
        evidence={"missing_name": name, "binding_stmt": stmt, "insert_lineno": idx + 1},
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_FINALS = "agent_tools/finals_rebuild"
_COMMON_FORBIDDEN = (
    "string_literal_content",
    "numeric_literal_value",
    "answer_or_correct_answer_expression",
    "answer_contract_or_checker_binding",
    "domain_function_or_operation_selection",
    "delete_or_comment_out_code_line",
)
_COMMON_VALIDATION = (
    "patch_scope_verifier",
    "protected_answer_line_guard",
    "python_compile",
    "isolated_component_execution_seed_42",
    "deterministic_replay_seed_42",
    "component_payload_validator_multi_seed",
    "answer_contract_capability",
    "shared_checker_positive_and_negative_probe",
    "source_isomorphism_when_required",
    "idempotence_recheck",
    "full_v3_gate_rerun_in_pipeline",
    "publish_eligibility_human_review_blocker",
)
_V3_COMPONENT_CONTRACT = (
    "component_id == src_{textbook_example_id}",
    "skill_id / fixed_domain_key / domain_operation present",
    "generate.py identity constants match contract",
)


def _disabled(
    rule_id: str,
    tier: str,
    role: str,
    path: str,
    blob: str,
    research_status: str,
    reason: str,
    trigger: str,
    prerequisites: tuple[str, ...],
) -> V3HealerRuleSpec:
    return V3HealerRuleSpec(
        rule_id=rule_id,
        research_tier=tier,
        layer_role=role,
        v3_status="disabled_candidate",
        trigger=trigger,
        eligibility=(),
        contract_prerequisites=prerequisites,
        edit_scope=SCOPE_NONE,
        forbidden_semantics=_COMMON_FORBIDDEN,
        validation_requirements=_COMMON_VALIDATION,
        abstain_conditions=("always_abstain_until_v3_contract_and_independent_validation_exist",),
        provenance=RuleProvenance(source_path=path, git_blob_sha1=blob, research_status=research_status),
        disabled_reason=reason,
    )


RULE_SPECS: tuple[V3HealerRuleSpec, ...] = (
    V3HealerRuleSpec(
        rule_id=RULE_A_L1_PAREN,
        research_tier="Tier A",
        layer_role="frozen_conservative_base",
        v3_status="executable",
        trigger="SyntaxError message starts with \"'(' was never closed\"",
        eligibility=(FAILURE_SYNTAX,),
        contract_prerequisites=_V3_COMPONENT_CONTRACT,
        edit_scope=SCOPE_INSERT_CLOSING_DELIMITER,
        forbidden_semantics=_COMMON_FORBIDDEN,
        validation_requirements=_COMMON_VALIDATION,
        abstain_conditions=(
            "source_already_parses",
            "generate_entry_point_missing",
            "trial_fix_still_fails_parse",
            "multiple_possible_repair_lines_exist",
            "ambiguous_intra_line_paren_positions (V3)",
            "error_line_too_long",
        ),
        provenance=RuleProvenance(
            source_path=f"{_FINALS}/ce115_research_healer_rules_l1_paren_close.py",
            git_blob_sha1="898bc583094c9603c6e0dba216f3d39da44b21a4",
            research_status="production_ready (Pilot-02 frozen Tier A)",
            research_evidence="Tier A anchor: Qwen4B 79/320 -> 85/320, verified rescue 6 (all six Tier A rules)",
        ),
        v3_adaptations=(
            "uses SyntaxError.msg instead of str(exc) (research check '(' in str(exc) is always true)",
            "requires intra-line AST-equivalence uniqueness; ambiguous paren positions abstain",
            "no evaluator re-run inside the rule",
        ),
        apply=apply_a_l1_close_unbalanced_parenthesis,
    ),
    V3HealerRuleSpec(
        rule_id=RULE_B1_FULLWIDTH,
        research_tier="Tier B",
        layer_role="safe_structural_extension",
        v3_status="executable",
        trigger="SyntaxError and mapped fullwidth punctuation outside string/comment tokens",
        eligibility=(FAILURE_SYNTAX,),
        contract_prerequisites=_V3_COMPONENT_CONTRACT,
        edit_scope=SCOPE_REPLACE_FULLWIDTH,
        forbidden_semantics=_COMMON_FORBIDDEN + ("fullwidth_text_inside_question_strings",),
        validation_requirements=_COMMON_VALIDATION,
        abstain_conditions=(
            "source_already_parses (V3: identifiers may legally contain some fullwidth glyphs)",
            "tokenize_failed",
            "result_not_parseable",
            "unexpected_length_change",
        ),
        provenance=RuleProvenance(
            source_path=f"{_FINALS}/core_adapter.py + {_FINALS}/aggressive_healer_tier_a/rule_a1_fullwidth.py",
            git_blob_sha1="4893618fa369a37b02afc264ae7fe019e92c5f81 / 1850eb5d760c25c2e2914bcf71c8a42e42ca1e42",
            research_status="implemented; C2 Tier B development replay 86/320 frozen, 85/320 corrected (+0 corrected)",
        ),
        v3_adaptations=("only runs on unparseable source", "t-string tokens also protected"),
        apply=apply_b1_fullwidth,
    ),
    V3HealerRuleSpec(
        rule_id=RULE_B2_DELIMITER,
        research_tier="Tier B",
        layer_role="safe_structural_extension",
        v3_status="executable",
        trigger="SyntaxError delimiter message (never closed / unexpected EOF) on a known line",
        eligibility=(FAILURE_SYNTAX,),
        contract_prerequisites=_V3_COMPONENT_CONTRACT,
        edit_scope=SCOPE_INSERT_CLOSING_DELIMITER,
        forbidden_semantics=_COMMON_FORBIDDEN,
        validation_requirements=_COMMON_VALIDATION,
        abstain_conditions=(
            "syntax_error_not_delimiter",
            "no_unique_closing_insert",
            "ambiguous_closing_inserts (more than one AST-distinct repair)",
            "error_line_too_long",
        ),
        provenance=RuleProvenance(
            source_path=f"{_FINALS}/aggressive_healer_tier_a/rule_a2_delimiter.py",
            git_blob_sha1="506f6afc0a91762aee5071c2378a5d6165ebe09b",
            research_status="implemented; Tier B (safe structural)",
        ),
        v3_adaptations=(
            "uniqueness is computed over AST-equivalence classes; whitespace-only position variants are one repair",
            "uses SyntaxError.msg",
        ),
        apply=apply_b2_unique_missing_delimiter,
    ),
    V3HealerRuleSpec(
        rule_id=RULE_B3_EMPTY_SUITE,
        research_tier="Tier B",
        layer_role="safe_structural_extension",
        v3_status="executable",
        trigger="SyntaxError 'expected an indented block' with exactly one empty suite",
        eligibility=(FAILURE_SYNTAX,),
        contract_prerequisites=_V3_COMPONENT_CONTRACT,
        edit_scope=SCOPE_INSERT_PASS_LINE,
        forbidden_semantics=_COMMON_FORBIDDEN + ("placeholder_function_body", "while_loop_body"),
        validation_requirements=_COMMON_VALIDATION,
        abstain_conditions=(
            "ambiguous_empty_suites",
            "suite_owner_not_allowed_in_v3 (def/class/while/match/case)",
            "suite_not_explicitly_comment_only (possible mis-indented body => math semantic drift)",
        ),
        provenance=RuleProvenance(
            source_path=f"{_FINALS}/aggressive_healer_tier_a/rule_a3_empty_suite.py",
            git_blob_sha1="3b88dd2563a01f41ecc4add688d3ea6a530cdc06",
            research_status="implemented; Tier B (safe structural)",
        ),
        v3_adaptations=(
            "research version also fills a mis-indented loop body with pass, silently changing math; V3 requires a comment-only suite",
            "def/class bodies excluded (no placeholder generate())",
            "while bodies excluded (no infinite loop)",
        ),
        apply=apply_b3_empty_suite_insert_pass,
    ),
    V3HealerRuleSpec(
        rule_id=RULE_B4_IMPORT,
        research_tier="Tier B",
        layer_role="safe_structural_extension",
        v3_status="executable",
        trigger="runtime NameError for exactly one statically unbound stdlib name",
        eligibility=(FAILURE_NAME,),
        contract_prerequisites=_V3_COMPONENT_CONTRACT,
        edit_scope=SCOPE_INSERT_STDLIB_IMPORT,
        forbidden_semantics=_COMMON_FORBIDDEN + ("domain_module_imports",),
        validation_requirements=_COMMON_VALIDATION,
        abstain_conditions=(
            "source_not_parseable",
            "no_runtime_name_error_evidence",
            "non_unique_or_unmapped_binding_gaps",
            "runtime_name_error_does_not_match_static_gap",
        ),
        provenance=RuleProvenance(
            source_path=f"{_FINALS}/aggressive_healer_tier_a/rule_a4_import_binding.py",
            git_blob_sha1="7b04e3b95c50ba2bfb5d2b04b4c71da5fece1a55",
            research_status="implemented; Tier B (safe structural)",
        ),
        v3_adaptations=(
            "inserts after module docstring AND __future__ imports (research version breaks compile() on V3 templates)",
            "requires the runtime NameError name to equal the unique static gap",
            "accepts only when compile() succeeds",
        ),
        apply=apply_b4_unique_import_binding,
    ),
    _disabled(
        "L1_CLOSE_UNBALANCED_DELIMITER_EXTENDED", "Tier A", "frozen_conservative_base",
        f"{_FINALS}/ce115_research_healer_rules_l1_delimiter_extended.py",
        "40b3d0c9bd273a07dcbb7bf718cbdea8f5959841", "experimental; PRODUCTION_APPROVED=False",
        "research-experimental; enumerates delimiter deletions and rebuilds source with '\\n'.join (drops CRLF/trailing newline); covered by B2",
        "SyntaxError near a delimiter", (),
    ),
    _disabled(
        "L1_PROSE_RESIDUE_NARROW", "Tier A", "frozen_conservative_base",
        f"{_FINALS}/ce115_research_healer_rules_l1_prose_narrow.py",
        "98b0594b17866519441d9f27c69066104e541caa", "experimental; PRODUCTION_APPROVED=False",
        "comments out / truncates code at the SyntaxError line, which V3 forbids (no deletion of failing lines)",
        "SyntaxError caused by prose residue", (),
    ),
    _disabled(
        "L2_SINGLE_KEY_ORACLE_PAYLOAD_WRAP", "Tier A", "frozen_conservative_base",
        f"{_FINALS}/ce115_research_healer_rules_l2.py",
        "7cd65171db79165d2531052be3f01c534656ecde", "production allowlist (Math16)",
        "rewrites the Math16 oracle_payload return field; V3 components have no oracle_payload and the Answer Oracle must not be touched",
        "Math16 return dict missing oracle_payload wrap", ("math16_frozen_oracle_payload",),
    ),
    _disabled(
        "L2_KWARGS_EMPTY_BAG_INLINE_UNIQUE_PARAM", "Tier A", "frozen_conservative_base",
        f"{_FINALS}/ce115_research_healer_rules_l2_kwargs_bag_inline.py",
        "ec28d7e709ab5b1839911259f3bd7802e145716f", "production allowlist (Math16)",
        "eligibility depends on Math16 frozen parameter names (decide_eligibility reads oracle_payload); V3 parameters come from Domain constraints",
        "Math16 kwargs bag referencing frozen parameter", ("math16_frozen_oracle_payload",),
    ),
    _disabled(
        "L2_CORRECT_ANSWER_JSON_DUMPS_UNWRAP", "Tier A", "frozen_conservative_base",
        f"{_FINALS}/ce115_research_healer_rules_l2_json_dumps_unwrap.py",
        "65fc1956215af29897e4029d4e6b16d03cada62c", "production allowlist (Math16)",
        "rewrites the correct_answer expression; forbidden for V3 (answer semantics)",
        "correct_answer wrapped in json.dumps", (),
    ),
    _disabled(
        "TIER_B_EXPLICIT_DOMAIN_METHOD_BINDING_REPAIR_V1", "Tier C1", "contract_aware_repair_candidate",
        "scripts/run_math16_c2_c3_tier_c1_qwen9b_v1.py",
        "f76e482d7b2ef3c4eb7099e1cfdf4522c29fadd6", "development replay (Math16 contract matrix)",
        "renames research Ops methods using math16_ab2d_task_contract_matrix_v1; V3 operations are dispatched via the Domain registry with no equivalent method-alias contract",
        "AttributeError on research *Ops method", ("v3_operation_alias_contract",),
    ),
    _disabled(
        "TIER_B_DOMAIN_SIGNATURE_FORM_REPAIR_V1", "Tier C2", "contract_aware_repair_candidate",
        f"{_FINALS}/aggressive_healer_tier_c2/rule_default_optional_cleanup.py",
        "ded0a68cb9c05b80a28e88d81eb30eed1968ad12", "development replay (Math16)",
        "imports research core.prompts.domain_function_library Ops classes and DOMAIN_API_SSOT; no V3 signature contract",
        "Ops call with redundant default/optional args", ("v3_domain_signature_contract",),
    ),
    _disabled(
        "TIER_D_OPS_SHADOW_REMOVAL_V1", "Tier D", "failure_gated_risk_accepting_repair",
        f"{_FINALS}/aggressive_healer_tier_d/rule_d1_ops_shadow_removal.py",
        "25d94807dfb09763d1e41dced29f9adb841a572b", "development (Tier D separate ledger)",
        "risk-accepting deletion of model-defined Ops classes; research Ops names only",
        "model-defined class shadows runtime Ops", ("v3_independent_validation_for_risk_accepting_rules",),
    ),
    _disabled(
        "TIER_D_DUPLICATE_DEFINITION_SELECTION_V1", "Tier D", "failure_gated_risk_accepting_repair",
        f"{_FINALS}/aggressive_healer_tier_d/rule_d2_duplicate_definition_selection.py",
        "f60f82651c13cb0cdc3d000b60ebc7b6ac3f27ba", "development (Tier D separate ledger)",
        "drops one of two definitions via a weighted ranking; may discard the mathematically correct body",
        "duplicate same-scope definitions", ("v3_independent_validation_for_risk_accepting_rules",),
    ),
    _disabled(
        "TIER_D_SYNTAX_RESIDUE_QUARANTINE_V1", "Tier D", "failure_gated_risk_accepting_repair",
        f"{_FINALS}/aggressive_healer_tier_d/rule_d3_syntax_residue_quarantine.py",
        "71221d9c1c96483d7698e7779e64fa38d7cb2f45", "development (Tier D separate ledger)",
        "comments out trailing code after generate(); equivalent to deleting failing lines, forbidden in V3",
        "trailing residue after generate()", ("v3_independent_validation_for_risk_accepting_rules",),
    ),
    _disabled(
        "TIER_D_RANKED_DOMAIN_METHOD_BINDING_V1", "Tier D", "failure_gated_risk_accepting_repair",
        f"{_FINALS}/aggressive_healer_tier_d/rule_d5_ranked_domain_method_binding.py",
        "526bf648c9c350c073e829aeab694b5dfb792026", "development (Tier D separate ledger)",
        "ranked rename of Ops methods using the Math16 contract matrix; changes which mathematical operation runs",
        "AttributeError on research *Ops method", ("v3_operation_alias_contract", "v3_independent_validation_for_risk_accepting_rules"),
    ),
    _disabled(
        "PC-R01_ANSWER_SOURCE_REWIRE_V2", "PC (Contract-Aware v2)", "proof_carrying_contract_aware",
        f"{_FINALS}/aggressive_healer_contract_v2/rules/pc_r01_answer_source_rewire.py",
        "37aee12dbb40538acc5bc89966db9ae23fd2c0c7", "frozen v2.0.0; 3 verified rescues (Math16)",
        "rewires answer fields; contract clause is hard-coded per Math16 task_id; affects answer semantics",
        "answer field not sourced from contract formatter", ("answer_source_rewire",),
    ),
    _disabled(
        "PC-R02_OPERAND_ORDER_RESTORE_V2", "PC (Contract-Aware v2)", "proof_carrying_contract_aware",
        f"{_FINALS}/aggressive_healer_contract_v2/rules/pc_r02_operand_order.py",
        "0dc624cb8d3950dd66ed2ccc381e00b338e7a99c", "frozen v2.0.0; 2 verified rescues (Math16)",
        "swaps operands per a Math16-only clause (FractionOps.sub); changes mathematical result",
        "operand order differs from full-plan clause", ("operand_order_constraints", "full_plan_constraints"),
    ),
    _disabled(
        "PC-R03_DOMAIN_API_NORMALIZE_V2", "PC (Contract-Aware v2)", "proof_carrying_contract_aware",
        f"{_FINALS}/aggressive_healer_contract_v2/rules/pc_r03_domain_api_normalize.py",
        "2b8ed820566502768b338dec94f1b6adb81d86a0", "frozen v2.0.0; 1 verified rescue (Math16)",
        "allowed_methods come from research DOMAIN_API_SSOT; V3 has no equivalent allowed-method contract for generate.py",
        "illegal *Ops class/method", ("allowed_methods", "api_signatures"),
    ),
    _disabled(
        "PC-R04_UNIQUE_PROCESS_WIRING_V2", "PC (Contract-Aware v2)", "proof_carrying_contract_aware",
        f"{_FINALS}/aggressive_healer_contract_v2/rules/pc_r04_unique_process_wiring.py",
        "ca3703f081c781cd6ed3bf667a67ccb7bd6a48a4", "frozen v2.0.0; 0 accepts (abstain scaffolding)",
        "inserts a missing full-plan API step from Math16 TASK_SCAFFOLDS_V2; no V3 full-plan contract",
        "exactly one missing required call", ("full_plan_constraints",),
    ),
)

RULES_BY_ID: dict[str, V3HealerRuleSpec] = {spec.rule_id: spec for spec in RULE_SPECS}
EXECUTABLE_RULE_ORDER: tuple[str, ...] = tuple(spec.rule_id for spec in RULE_SPECS if spec.executable)
DISABLED_RULE_IDS: tuple[str, ...] = tuple(spec.rule_id for spec in RULE_SPECS if not spec.executable)


def describe_ruleset() -> dict[str, Any]:
    return {
        "ruleset_version": V3_RULESET_VERSION,
        "research_repository": RESEARCH_REPOSITORY,
        "research_commit": RESEARCH_COMMIT,
        "research_license": RESEARCH_LICENSE,
        "research_pc_frozen_manifest_sha256": RESEARCH_PC_FROZEN_MANIFEST_SHA256,
        "research_pc_final_aggregate_sha256": RESEARCH_PC_FINAL_AGGREGATE_SHA256,
        "research_tier_mapping_manifest": dict(RESEARCH_TIER_MAPPING_MANIFEST),
        "executable_rule_order": list(EXECUTABLE_RULE_ORDER),
        "rules": [spec.describe() for spec in RULE_SPECS],
    }
