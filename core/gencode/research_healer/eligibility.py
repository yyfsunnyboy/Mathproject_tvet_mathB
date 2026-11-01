# -*- coding: utf-8 -*-
"""V3 eligibility / safety matrix for the research healer rules.

A research rule may only enter ``V3_PRODUCTION_ALLOWLIST`` after a V3
compatibility and safety proof on real V3 AI Python samples.  No rule has
such a proof yet, so the allowlist is empty and every research rule is
evaluated in probe mode only (its output is never handed to the pipeline).
"""

from __future__ import annotations

from dataclasses import dataclass

STATUS_ENABLED = "ENABLED"
STATUS_DISABLED = "DISABLED"

TIER_PREFLIGHT = "V3 Preflight"
TIER_RESEARCH_L1 = "Research L1"
TIER_RESEARCH_L2 = "Research L2"

PREFLIGHT_FENCE_RULE_ID = "V3_PREFLIGHT_UNIQUE_MARKDOWN_FENCE_EXTRACT"


@dataclass(frozen=True)
class RuleEligibility:
    rule_id: str
    tier: str
    research_status: str
    research_production_approved: bool
    v3_status: str
    edit_kind: str
    v3_risks: tuple[str, ...]
    reason: str


RULE_ELIGIBILITY: tuple[RuleEligibility, ...] = (
    RuleEligibility(
        rule_id=PREFLIGHT_FENCE_RULE_ID,
        tier=TIER_PREFLIGHT,
        research_status="v3_native",
        research_production_approved=False,
        v3_status=STATUS_ENABLED,
        edit_kind="extract the single fenced code block verbatim",
        v3_risks=(),
        reason=(
            "output is a verbatim substring of the AI response; no code character is "
            "added, removed or reordered, so math and control flow cannot change"
        ),
    ),
    RuleEligibility(
        rule_id="L1_CLOSE_UNBALANCED_PARENTHESIS",
        tier=TIER_RESEARCH_L1,
        research_status="production_ready",
        research_production_approved=True,
        v3_status=STATUS_DISABLED,
        edit_kind="append ')' at the end of the reported line",
        v3_risks=("math_grouping_change", "requires_generate_entrypoint"),
        reason=(
            "uniqueness is only checked across line ends, not across positions inside the "
            "line, so 'x = (a + b * c' may become '(a + b * c)' instead of '(a + b) * c'; "
            "parse success does not prove the intended grouping"
        ),
    ),
    RuleEligibility(
        rule_id="L1_CLOSE_UNBALANCED_DELIMITER_EXTENDED",
        tier=TIER_RESEARCH_L1,
        research_status="experimental",
        research_production_approved=False,
        v3_status=STATUS_DISABLED,
        edit_kind="insert or delete one of ()[]{} in the error line",
        v3_risks=("math_grouping_change", "valid_code_deletion", "research_experimental"),
        reason="may delete a delimiter or regroup an expression; experimental in research",
    ),
    RuleEligibility(
        rule_id="L1_PROSE_RESIDUE_NARROW",
        tier=TIER_RESEARCH_L1,
        research_status="experimental",
        research_production_approved=False,
        v3_status=STATUS_DISABLED,
        edit_kind="comment out lines or truncate the error line",
        v3_risks=("valid_code_deletion", "math_expression_truncation", "research_experimental"),
        reason="truncation can remove part of a formula; experimental in research",
    ),
    RuleEligibility(
        rule_id="L1_COMMENT_ONLY_IF_INSERT_PASS",
        tier=TIER_RESEARCH_L1,
        research_status="paused_experimental_draft",
        research_production_approved=False,
        v3_status=STATUS_DISABLED,
        edit_kind="insert 'pass' into an if block that only holds comments",
        v3_risks=("control_flow_change", "research_paused"),
        reason="changes the body of an if statement; paused in research",
    ),
    RuleEligibility(
        rule_id="L2_SINGLE_KEY_ORACLE_PAYLOAD_WRAP",
        tier=TIER_RESEARCH_L2,
        research_status="production_approved",
        research_production_approved=True,
        v3_status=STATUS_DISABLED,
        edit_kind="wrap oracle_payload scalar from frozen oracle values",
        v3_risks=("reads_oracle_values", "answer_contract_shape_change", "ce115_contract_only"),
        reason="reads frozen oracle values and rewrites the CE115 return contract; V3 has no oracle_payload",
    ),
    RuleEligibility(
        rule_id="L2_KWARGS_EMPTY_BAG_INLINE_UNIQUE_PARAM",
        tier=TIER_RESEARCH_L2,
        research_status="production_approved",
        research_production_approved=True,
        v3_status=STATUS_DISABLED,
        edit_kind="inline frozen parameter literals over an empty kwargs bag",
        v3_risks=("injects_values", "ce115_contract_only"),
        reason="injects literal values from the research frozen bag; forbidden in V3",
    ),
    RuleEligibility(
        rule_id="L2_CORRECT_ANSWER_JSON_DUMPS_UNWRAP",
        tier=TIER_RESEARCH_L2,
        research_status="production_approved",
        research_production_approved=True,
        v3_status=STATUS_DISABLED,
        edit_kind="remove json.dumps around correct_answer",
        v3_risks=("modifies_correct_answer", "answer_contract_shape_change", "ce115_contract_only"),
        reason="changes the correct_answer expression; V3 Answer Contract must not be rewritten",
    ),
)

ELIGIBILITY_BY_ID: dict[str, RuleEligibility] = {r.rule_id: r for r in RULE_ELIGIBILITY}

RESEARCH_RULE_IDS: tuple[str, ...] = tuple(r.rule_id for r in RULE_ELIGIBILITY if r.tier != TIER_PREFLIGHT)

V3_PRODUCTION_ALLOWLIST: tuple[str, ...] = tuple(
    r.rule_id for r in RULE_ELIGIBILITY if r.tier != TIER_PREFLIGHT and r.v3_status == STATUS_ENABLED
)
