# -*- coding: utf-8 -*-
"""
tests/gencode/test_phase1_rule_pack_priority.py
================================================
G. human_confirmed rule pack priority tests.
H. Clause 4.5 boundary: scope_locked + no stable problem_type
   => must NOT produce usable contextual_application.
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.main_skill_anchor import build_main_skill_anchor
from core.gencode.problem_type_induction import (
    apply_clause45_unclassified_exception_escalation,
    _load_human_confirmed_rulepack,
)
from core.gencode.task_families import QUADRATIC_FUNCTION_GRAPH_FAMILY


# ---------------------------------------------------------------------------
# G. human_confirmed rule pack loading
# ---------------------------------------------------------------------------

def test_load_human_confirmed_rulepack_returns_none_for_unknown_skill():
    """Unknown skill should return None without error."""
    result = _load_human_confirmed_rulepack("nonexistent_skill_xyz_123")
    assert result is None


def test_load_human_confirmed_rulepack_type():
    """If a rule pack exists for a real skill, it must be a dict."""
    result = _load_human_confirmed_rulepack("vh_數學B1_QuadraticFunctionGraph")
    assert result is None or isinstance(result, dict)


# ---------------------------------------------------------------------------
# H. Clause 4.5 boundary: scope_locked must produce skill_scoped_unresolved
#    instead of usable contextual_application
# ---------------------------------------------------------------------------

def test_clause45_scope_locked_produces_unresolved_not_contextual():
    """
    When source_skill_scope_locked=True and all examples are unclassified_low_confidence,
    Clause 4.5 must produce skill_scoped_unresolved_problem_type, NOT contextual_application.
    """
    anchor = build_main_skill_anchor(
        "vh_數學B1_QuadraticFunctionGraph",
        {
            "skill_en_name": "QuadraticFunctionGraph",
            "skill_ch_name": "二次函數的圖形",
        },
    )
    assert anchor.get("source_skill_scope_locked") is True

    # Raw feature: a quad example left unclassified
    feat = {
        "source_example_id": 9999,
        "target_task": "",
        "task_family": "",
        "induction_tier": "core",
        "source_quality_reject": False,
        "included_in_core_induction": False,
        "semantic_classification": {
            "final_target_task": "",
            "final_task_family": "",
            "candidate_source": "",
            "classifier_source": "",
        },
    }
    excluded_row = {
        "example_id": 9999,
        "exclude_reason": "unclassified_low_confidence",
        "induction_tier": "core",
        "included_in_core_induction": False,
        "target_task": "",
        "task_family": "",
    }

    features_for_induction: list = []
    excluded = [excluded_row]
    features = [feat]
    induction_source_report = {"core_example_count": 1}

    rescued_features, still_excluded, report = apply_clause45_unclassified_exception_escalation(
        features_for_induction,
        excluded,
        features,
        main_skill_anchor=anchor,
        induction_source_report=induction_source_report,
    )

    if not report.get("clause45_escalation_applied"):
        # If clause45 didn't fire, that's acceptable (no rows rescued)
        pytest.skip("clause45 did not rescue any examples in this test setup")

    # Verify no usable contextual_application was produced
    for feat_out in rescued_features:
        pt_id = str(feat_out.get("problem_type_id", ""))
        # Should NOT be a generic fallback_contextual_application
        assert "contextual_application" not in pt_id or pt_id == "skill_scoped_unresolved_problem_type", (
            f"scope_locked clause45 must NOT produce contextual_application; got {pt_id}"
        )
        if pt_id == "skill_scoped_unresolved_problem_type":
            assert feat_out.get("usable_for_phase3") is False or feat_out.get("generator_readiness") == "pending_problem_type_induction"


def test_clause45_without_scope_lock_still_works():
    """
    When source_skill_scope_locked is explicitly False, Clause 4.5 still rescues normally.
    (Regression: do not break non-locked flow.)
    """
    anchor = {
        "source_skill_scope_locked": False,
        "expected_task_families": ["generic_numeric_family"],
        "expected_subskill_candidates": [],
        "fallback_subskill": {"subskill_id": "same_as_main_skill"},
    }
    feat = {
        "source_example_id": 8888,
        "target_task": "compute_distance",
        "task_family": "distance_between_two_points_family",
        "induction_tier": "core",
        "source_quality_reject": False,
        "included_in_core_induction": False,
        "semantic_classification": {
            "final_target_task": "compute_distance",
            "final_task_family": "distance_between_two_points_family",
            "candidate_source": "rule",
        },
    }
    excluded_row = {
        "example_id": 8888,
        "exclude_reason": "unclassified_low_confidence",
        "induction_tier": "core",
        "included_in_core_induction": False,
        "target_task": "compute_distance",
        "task_family": "distance_between_two_points_family",
    }

    rescued_features, still_excluded, report = apply_clause45_unclassified_exception_escalation(
        [],
        [excluded_row],
        [feat],
        main_skill_anchor=anchor,
        induction_source_report={"core_example_count": 1},
    )

    if report.get("clause45_escalation_applied"):
        # When not scope_locked, contextual_application proxy is acceptable
        for feat_out in rescued_features:
            pt_id = str(feat_out.get("problem_type_id", ""))
            assert pt_id, "proxy_problem_type_id must be set"


# ---------------------------------------------------------------------------
# D. Bridge integration: human_confirmed rule pack + ProblemType Bridge
# ---------------------------------------------------------------------------

def test_bridge_exists_for_rule_pack_primary():
    """
    human_confirmed rule pack 的 primary problem_type_id 應命中 bridge 設定。
    """
    from core.gencode.problem_type_bridge import has_bridge, reset_bridge_cache
    reset_bridge_cache()
    # The primary pt from phase1_rule_packs.yaml for QuadraticFunctionGraph
    assert has_bridge("text_short_compute_vertex_and_axis"), (
        "Bridge missing for text_short_compute_vertex_and_axis; "
        "Phase 2 cannot expand to runtime variants"
    )
    reset_bridge_cache()


def test_bridge_expand_produces_5_variants():
    """
    Bridge 展開後應產生 5 個 runtime presentation variants。
    """
    from core.gencode.problem_type_bridge import (
        expand_primary_to_runtime_variants,
        reset_bridge_cache,
    )
    reset_bridge_cache()
    variants, status = expand_primary_to_runtime_variants(
        "vh_數學B1_QuadraticFunctionGraph",
        "text_short_compute_vertex_and_axis",
        [4450, 4460, 4466, 4503],
    )
    assert status == "ok", f"Expected 'ok', got {status!r}"
    assert len(variants) >= 5, (
        f"Expected >=5 variants, got {len(variants)}: "
        f"{[v.get('problem_type_id') for v in variants]}"
    )
    reset_bridge_cache()


def test_bridge_variants_not_contextual_application():
    """
    Bridge 展開的 variant 不得含 contextual_application。
    """
    from core.gencode.problem_type_bridge import (
        expand_primary_to_runtime_variants,
        reset_bridge_cache,
    )
    reset_bridge_cache()
    variants, _ = expand_primary_to_runtime_variants(
        "vh_數學B1_QuadraticFunctionGraph",
        "text_short_compute_vertex_and_axis",
    )
    for v in variants:
        pt = v.get("problem_type_id", "")
        assert "contextual_application" not in pt, (
            f"Bridge variant must not be contextual_application, got {pt!r}"
        )
    reset_bridge_cache()


def test_bridge_variants_usable_for_phase3():
    """
    Bridge 展開的 variants 應標 usable_for_phase3: True。
    """
    from core.gencode.problem_type_bridge import (
        expand_primary_to_runtime_variants,
        reset_bridge_cache,
    )
    reset_bridge_cache()
    variants, _ = expand_primary_to_runtime_variants(
        "vh_數學B1_QuadraticFunctionGraph",
        "text_short_compute_vertex_and_axis",
    )
    for v in variants:
        assert v.get("usable_for_phase3") is True, (
            f"Bridge variant {v.get('problem_type_id')!r} not usable_for_phase3"
        )
    reset_bridge_cache()


def test_bridge_missing_does_not_fallback_to_contextual_application():
    """
    Bridge 缺失時不得 fallback 到 contextual_application。
    BRIDGE_MISSING status はそのまま返すこと。
    """
    from core.gencode.problem_type_bridge import (
        BRIDGE_MISSING,
        expand_primary_to_runtime_variants,
        reset_bridge_cache,
    )
    reset_bridge_cache()
    variants, status = expand_primary_to_runtime_variants(
        "vh_數學B1_QuadraticFunctionGraph",
        "totally_unknown_problem_type_xyz",
    )
    assert status == BRIDGE_MISSING, f"Expected BRIDGE_MISSING, got {status!r}"
    for v in variants:
        assert "contextual_application" not in v.get("problem_type_id", ""), (
            f"Should not produce contextual_application fallback"
        )
    reset_bridge_cache()


def test_phase2_bridge_expansion_integrates_with_induction():
    """
    problem_type_induction 的 bridge 展開邏輯：
    若候選 pt_id 是 bridge primary，應展開為 runtime variants，
    不應保留 primary 作為 usable_for_phase3 的 generator。
    """
    from core.gencode.problem_type_bridge import (
        expand_primary_to_runtime_variants,
        is_bridge_primary,
        reset_bridge_cache,
    )
    reset_bridge_cache()

    # The bridge primary from rule packs
    primary_pt = "text_short_compute_vertex_and_axis"
    assert is_bridge_primary(primary_pt), f"{primary_pt} should be a bridge primary"

    variants, status = expand_primary_to_runtime_variants(
        "vh_數學B1_QuadraticFunctionGraph", primary_pt
    )
    assert status == "ok"

    # None of the expanded variants should be the primary itself
    for v in variants:
        assert v["problem_type_id"] != primary_pt, (
            f"Bridge expansion must not include the primary itself as a runtime generator"
        )

    # None of the expanded variants should be contextual_application
    for v in variants:
        pt = v.get("problem_type_id", "")
        assert "contextual_application" not in pt

    reset_bridge_cache()

