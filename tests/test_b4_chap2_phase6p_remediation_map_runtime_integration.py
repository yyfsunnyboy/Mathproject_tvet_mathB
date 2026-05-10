# -*- coding: utf-8 -*-
"""Phase 6P: Chap2 remediation map runtime integration tests."""

from __future__ import annotations

import pytest


_RESERVED = {
    "sample_space_listing",
    "event_set_listing",
    "subset_listing",
    "tree_diagram_listing",
}


def _bootstrap():
    from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
        build_b4_chap2_chapter_response,
        build_b4_chap2_chapter_runtime_store_entry,
    )
    payload = {
        "mode": "chapter",
        "entry_mode": "chapter",
        "curriculum": "vocational",
        "volume": "數學B4",
        "chapter_id": "2",
        "step_number": 0,
        "student_id": 99,
    }
    resp = build_b4_chap2_chapter_response(payload, runtime={})
    runtime = build_b4_chap2_chapter_runtime_store_entry(resp, 0)
    return resp, runtime


def _submit(session_id, step_number, user_answer, runtime):
    from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
        build_b4_chap2_chapter_response,
        build_b4_chap2_chapter_runtime_store_entry,
    )
    payload = {
        "step_number": step_number,
        "session_id": session_id,
        "user_answer": user_answer,
        "mode": "chapter",
        "entry_mode": "chapter",
        "curriculum": "vocational",
        "volume": "數學B4",
        "chapter_id": "2",
        "student_id": 99,
    }
    resp = build_b4_chap2_chapter_response(payload, runtime=runtime)
    new_runtime = build_b4_chap2_chapter_runtime_store_entry(
        resp,
        int(resp.get("chapter_current_step") or resp.get("step_number") or 0),
    )
    return resp, new_runtime


def _advance_to_stage(target_stage: str):
    from core.vocational_math_b4.services.b4_chap2_chapter_mode import _B4_CHAP2_CHAPTER_PLAN

    first_target_step = next(i for i, s in enumerate(_B4_CHAP2_CHAPTER_PLAN) if s["stage"] == target_stage)
    resp, runtime = _bootstrap()
    session_id = resp["session_id"]
    for _ in range(first_target_step):
        resp, runtime = _submit(session_id, resp["step_number"], runtime["correct_answer"], runtime)
    return resp, runtime, session_id


class TestMapCoverage:
    def test_runtime_map_covers_17_problem_types(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _CHAP2_REMEDIATION_MAP

        assert len(_CHAP2_REMEDIATION_MAP) == 17

    @pytest.mark.parametrize(
        "problem_type_id",
        [
            "set_operation_count",
            "inclusion_exclusion_count",
            "sample_space_count_numeric",
            "classical_probability_fraction",
            "dice_coin_probability_count",
            "complement_probability",
            "union_intersection_probability",
            "event_operation_probability",
            "probability_algebra_mixed",
            "conditional_probability_basic",
            "without_replacement_conditional_probability",
            "independent_joint_probability",
            "independent_at_least_one_probability",
            "expectation_discrete_basic",
            "expectation_from_distribution",
            "expectation_word_problem_profit_fairness",
            "expectation_assessment_numeric",
        ],
    )
    def test_each_problem_type_has_candidates(self, problem_type_id):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _CHAP2_REMEDIATION_MAP

        row = _CHAP2_REMEDIATION_MAP[problem_type_id]
        assert len(list(row.get("remediation_candidates") or [])) >= 1

    def test_reserved_never_in_map_candidates(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _CHAP2_REMEDIATION_MAP

        for row in _CHAP2_REMEDIATION_MAP.values():
            for pid in list(row.get("remediation_candidates") or []):
                assert pid not in _RESERVED

    def test_candidates_in_allowlist_or_stage_fallback_path(self):
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES,
        )
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _CHAP2_REMEDIATION_MAP

        for row in _CHAP2_REMEDIATION_MAP.values():
            for pid in list(row.get("remediation_candidates") or []):
                assert pid in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES


class TestSelectionPolicy:
    def test_probability_algebra_mixed_candidates_no_conditional_or_expectation(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _CHAP2_REMEDIATION_MAP

        cands = list(_CHAP2_REMEDIATION_MAP["probability_algebra_mixed"]["remediation_candidates"])
        assert "complement_probability" in cands
        assert "union_intersection_probability" in cands
        assert "event_operation_probability" in cands
        forbidden = {"conditional_probability_basic", "without_replacement_conditional_probability"}
        assert forbidden.isdisjoint(set(cands))
        assert all("expectation" not in c for c in cands)

    def test_conditional_basic_candidates_include_classical_and_sample_space(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _CHAP2_REMEDIATION_MAP

        cands = set(_CHAP2_REMEDIATION_MAP["conditional_probability_basic"]["remediation_candidates"])
        assert "classical_probability_fraction" in cands
        assert "sample_space_count_numeric" in cands

    def test_independent_at_least_one_candidates_include_complement_and_joint(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _CHAP2_REMEDIATION_MAP

        cands = set(_CHAP2_REMEDIATION_MAP["independent_at_least_one_probability"]["remediation_candidates"])
        assert "complement_probability" in cands
        assert "independent_joint_probability" in cands

    def test_expectation_word_problem_candidates_include_expected_prereqs(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _CHAP2_REMEDIATION_MAP

        cands = set(_CHAP2_REMEDIATION_MAP["expectation_word_problem_profit_fairness"]["remediation_candidates"])
        assert "expectation_discrete_basic" in cands
        assert "expectation_from_distribution" in cands
        assert "classical_probability_fraction" in cands


class TestRuntimeSelectionAndGuard:
    def test_stage2_wrong_never_selects_stage3_or_stage4(self):
        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, _ = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("in_remediation") is True
        sel = str(r2.get("selected_remediation_problem_type_id") or "")
        assert "conditional" not in sel
        assert "independent" not in sel
        assert "expectation" not in sel

    def test_stage3_wrong_never_selects_stage4(self):
        resp, runtime, session_id = _advance_to_stage("stage_3_conditional_independent")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, _ = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("in_remediation") is True
        sel = str(r2.get("selected_remediation_problem_type_id") or "")
        assert "expectation" not in sel

    def test_stage4_may_select_expectation(self):
        resp, runtime, session_id = _advance_to_stage("stage_4_expectation")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, _ = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("in_remediation") is True
        sel = str(r2.get("selected_remediation_problem_type_id") or "")
        assert sel != ""

    def test_remediation_source_is_map_or_stage_fallback(self):
        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, _ = _submit(session_id, r1["step_number"], "WRONG_2", runtime)
        assert r2.get("remediation_source") in {"problem_type_map", "stage_fallback"}
        assert isinstance(r2.get("remediation_candidates_considered"), list)

    def test_map_candidate_unavailable_fallback_respects_stage_guard(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _select_remediation_target

        # unknown problem_type forces stage fallback; for Stage2 it must not return Stage3/4
        selected, source, _ = _select_remediation_target(
            failed_problem_type_id="__unknown__",
            failed_stage="stage_2_basic_probability",
            remediation_stage="stage_2_basic_probability",
        )
        assert source == "stage_fallback"
        assert selected is not None
        assert selected["stage"] in {"stage_1_sets_and_sample_space", "stage_2_basic_probability"}

    def test_return_ready_can_return_mainline(self):
        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("in_remediation") is True
        correct = runtime["correct_answer"]
        r3, _ = _submit(session_id, r2["step_number"], correct, runtime)
        assert r3.get("return_ready") is True
        assert r3.get("has_returned_to_main") is True
        assert not r3.get("in_remediation")


class TestNoFormalPolicyWritesAndRegressions:
    def test_no_formal_mastery_apr_ppo_akt_fields(self):
        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, _ = _submit(session_id, r1["step_number"], "WRONG_2", runtime)
        forbidden = {"apr_delta", "mastery_level", "mastery_record_id", "ppo_write", "akt_update"}
        assert forbidden.isdisjoint(set(r2.keys()))

    def test_phase6i_audit_logging_callable(self):
        from core.vocational_math_b4.services.b4_chap2_visibility_audit import (
            persist_b4_chap2_deterministic_answer_event,
        )
        assert callable(persist_b4_chap2_deterministic_answer_event)

    def test_phase6j_teacher_visibility_routes_exist(self):
        from app import app

        urls = {r.rule for r in app.url_map.iter_rules()}
        assert "/teacher/b4-chap2-audit" in urls
        assert "/api/teacher/b4-chap2-audit" in urls

    def test_chap1_mode_not_broken(self):
        from core.routes.practice import _resolve_b4_chapter_adaptive_entry

        bridge, hit = _resolve_b4_chapter_adaptive_entry(
            mode="chapter",
            curriculum="vocational",
            volume="數學B4",
            chapter_id="1",
            skill_ids="",
        )
        assert hit is True
        assert bridge.get("chapter_id") == "1"
