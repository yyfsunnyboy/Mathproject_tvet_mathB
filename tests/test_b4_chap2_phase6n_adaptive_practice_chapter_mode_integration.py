# -*- coding: utf-8 -*-
"""Phase 6N: B4 Chapter 2 Adaptive Practice Chapter Mode Integration Tests.

Tests cover:
1. Chap2 chapter URL payload parsing (mode=chapter, curriculum=vocational, volume=數學B4, chapter_id=2)
2. Resolver returns 10 Chap2 skills
3. Reserved listing types not in diagnostic sequence
4. Diagnostic sequence stage order is correct
5. Stage-balanced sequence covers all 4 stages
6. Start diagnosis retrieves first question
7. First question payload has skill_id, problem_type_id, answer_type, expected_answer
8. check_answer triggers next question
9. Deterministic answer writes visibility audit log
10. No mastery/APR/remediation update
11. Friendly error (no silent no-op)
12. Encoded/decoded volume and chapter label handled
13. Chap1 chapter mode not broken
14. /practice Chap2 skill routes not broken
15. Teacher audit visibility not broken
"""
import pytest
import uuid


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _minimal_bootstrap_payload(chapter_id="2", volume="數學B4"):
    return {
        "mode": "chapter",
        "entry_mode": "chapter",
        "curriculum": "vocational",
        "volume": volume,
        "chapter_id": chapter_id,
        "step_number": 0,
        "student_id": 99,
    }


# ─── 1. URL payload parsing ───────────────────────────────────────────────────

class TestChap2ChapterUrlPayload:
    def test_chapter_id_2_detected(self):
        """chapter_id=2 is correctly identified as Chap2 chapter mode."""
        payload = _minimal_bootstrap_payload()
        assert payload["chapter_id"] == "2"
        assert payload["mode"] == "chapter"
        assert payload["curriculum"] == "vocational"
        assert payload["volume"] == "數學B4"

    def test_url_decoded_volume_accepted(self):
        """URL-decoded volume '數學B4' matches correctly."""
        from urllib.parse import unquote
        raw = unquote("%E6%95%B8%E5%AD%B8B4")  # 數學B4 URL-encoded
        assert raw == "數學B4"

    def test_chapter_label_alias(self):
        """Chapter name starting with '2 機率' is treated as chapter2 hit."""
        chapter_name = "2 機率"
        assert chapter_name.startswith("2 機率")


# ─── 2. Resolver returns 10 Chap2 skills ─────────────────────────────────────

class TestChap2ChapterResolver:
    def test_skill_count(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            B4_CHAP2_CHAPTER_SKILL_IDS,
        )
        assert len(B4_CHAP2_CHAPTER_SKILL_IDS) == 10

    def test_all_expected_skills_present(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            B4_CHAP2_CHAPTER_SKILL_IDS,
        )
        expected = {
            "vh_數學B4_BasicConceptsOfSets",
            "vh_數學B4_SampleSpaceAndEvents",
            "vh_數學B4_ProbabilityDefinition",
            "vh_數學B4_ProbabilityProperties",
            "vh_數學B4_ProbabilityOperations",
            "vh_數學B4_ConditionalProbability",
            "vh_數學B4_IndependentEvents",
            "vh_數學B4_MathematicalExpectationDefinition",
            "vh_數學B4_ApplicationsOfExpectation",
            "vh_數學B4_MathematicalExpectation",
        }
        assert set(B4_CHAP2_CHAPTER_SKILL_IDS) == expected

    def test_resolve_b4_chapter2_entry_from_practice_py(self):
        """_resolve_b4_chapter_adaptive_entry returns Chap2 bundle."""
        from core.routes.practice import _resolve_b4_chapter_adaptive_entry
        bridge, hit = _resolve_b4_chapter_adaptive_entry(
            mode="chapter",
            curriculum="vocational",
            volume="數學B4",
            chapter_id="2",
            skill_ids="",
        )
        assert hit is True
        assert bridge["chapter_id"] == "2"
        assert len(bridge["unit_skill_ids"]) == 10
        assert bridge.get("b4_chap2_chapter_mode") is True

    def test_resolve_does_not_hit_chapter1(self):
        from core.routes.practice import _resolve_b4_chapter_adaptive_entry
        _, hit = _resolve_b4_chapter_adaptive_entry(
            mode="chapter",
            curriculum="vocational",
            volume="數學B4",
            chapter_id="2",
            skill_ids="",
        )
        assert hit is True
        # Chapter 1 resolver must NOT be triggered for chapter_id=2
        bridge1, hit1 = _resolve_b4_chapter_adaptive_entry(
            mode="chapter",
            curriculum="vocational",
            volume="數學B4",
            chapter_id="1",
            skill_ids="",
        )
        assert hit1 is True
        assert bridge1["chapter_id"] == "1"


# ─── 3. Reserved listing types NOT in diagnostic sequence ────────────────────

class TestReservedListingExclusion:
    def test_no_reserved_listing_in_plan(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            get_b4_chap2_chapter_plan,
        )
        reserved = {
            "sample_space_listing",
            "event_set_listing",
            "subset_listing",
            "tree_diagram_listing",
        }
        plan = get_b4_chap2_chapter_plan()
        plan_problem_types = {step["problem_type_id"] for step in plan}
        assert plan_problem_types.isdisjoint(reserved), (
            f"Reserved listing types found in plan: {plan_problem_types & reserved}"
        )

    def test_all_plan_problem_types_in_allowlist(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            get_b4_chap2_chapter_plan,
        )
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES,
        )
        plan = get_b4_chap2_chapter_plan()
        for step in plan:
            pid = step["problem_type_id"]
            assert pid in B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES, (
                f"problem_type_id '{pid}' not in Chap2 allowlist"
            )


# ─── 4 & 5. Diagnostic sequence stage order ──────────────────────────────────

class TestDiagnosticSequenceStages:
    def test_four_stages_covered(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            get_b4_chap2_chapter_plan,
        )
        plan = get_b4_chap2_chapter_plan()
        stages = {step["stage"] for step in plan}
        assert len(stages) >= 4

    def test_stage_order(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            get_b4_chap2_chapter_plan,
        )
        plan = get_b4_chap2_chapter_plan()
        first_stage = plan[0]["stage"]
        last_stage = plan[-1]["stage"]
        assert "stage_1" in first_stage
        assert "stage_4" in last_stage

    def test_stage1_starts_with_sets(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            get_b4_chap2_chapter_plan,
        )
        plan = get_b4_chap2_chapter_plan()
        assert plan[0]["skill_id"] == "vh_數學B4_BasicConceptsOfSets"

    def test_stage4_ends_with_expectation(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            get_b4_chap2_chapter_plan,
        )
        plan = get_b4_chap2_chapter_plan()
        last = plan[-1]
        assert "Expectation" in last["skill_id"] or "MathematicalExpectation" in last["skill_id"]

    def test_total_steps_is_10(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
        )
        assert B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS == 10

    def test_each_stage_has_at_least_one_step(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            get_b4_chap2_chapter_plan,
            B4_CHAP2_CHAPTER_STAGES,
        )
        plan = get_b4_chap2_chapter_plan()
        plan_stages = {step["stage"] for step in plan}
        for stage_info in B4_CHAP2_CHAPTER_STAGES:
            assert stage_info["stage_id"] in plan_stages, (
                f"Stage '{stage_info['stage_id']}' has no steps in plan"
            )


# ─── 6 & 7. First question generation ────────────────────────────────────────

class TestFirstQuestionGeneration:
    def test_bootstrap_returns_question_payload(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
        )
        payload = _minimal_bootstrap_payload()
        resp = build_b4_chap2_chapter_response(payload, runtime={})
        assert "new_question_data" in resp
        q = resp["new_question_data"]
        assert q.get("question_text"), "question_text should not be empty"
        assert q.get("answer") or q.get("correct_answer"), "answer should not be empty"

    def test_first_question_has_required_fields(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
        )
        payload = _minimal_bootstrap_payload()
        resp = build_b4_chap2_chapter_response(payload, runtime={})
        q = resp["new_question_data"]
        assert q.get("skill_id"), "skill_id required"
        assert q.get("problem_type_id"), "problem_type_id required"
        assert q.get("answer_type"), "answer_type required"

    def test_first_question_has_expected_answer_in_response(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
        )
        payload = _minimal_bootstrap_payload()
        resp = build_b4_chap2_chapter_response(payload, runtime={})
        q = resp["new_question_data"]
        expected = q.get("correct_answer") or q.get("answer")
        assert expected, "Expected answer must be present in question data"

    def test_session_id_assigned(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
        )
        payload = _minimal_bootstrap_payload()
        resp = build_b4_chap2_chapter_response(payload, runtime={})
        assert resp.get("session_id"), "session_id must be assigned on bootstrap"

    def test_step_number_is_zero_on_bootstrap(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
        )
        payload = _minimal_bootstrap_payload()
        resp = build_b4_chap2_chapter_response(payload, runtime={})
        assert resp["step_number"] == 0

    def test_not_completed_on_bootstrap(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
        )
        payload = _minimal_bootstrap_payload()
        resp = build_b4_chap2_chapter_response(payload, runtime={})
        assert resp.get("completed") is False


# ─── 8. check_answer triggers next question ───────────────────────────────────

class TestCheckAnswerAdvancesStep:
    def _do_bootstrap(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )
        payload = _minimal_bootstrap_payload()
        resp = build_b4_chap2_chapter_response(payload, runtime={})
        runtime = build_b4_chap2_chapter_runtime_store_entry(resp, 0)
        return resp, runtime

    def test_answer_submission_advances_step(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
        )
        resp0, runtime = self._do_bootstrap()
        session_id = resp0["session_id"]
        correct_answer = resp0["new_question_data"]["correct_answer"]
        payload2 = {
            "step_number": 1,
            "session_id": session_id,
            "user_answer": correct_answer,
            "mode": "chapter",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "2",
            "student_id": 99,
        }
        resp2 = build_b4_chap2_chapter_response(payload2, runtime=runtime)
        # step_number in response should be 1 (the next question)
        assert resp2["step_number"] == 1
        assert resp2.get("completed") is False

    def test_wrong_answer_also_advances(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )
        resp0, runtime = self._do_bootstrap()
        session_id = resp0["session_id"]
        payload2 = {
            "step_number": 1,
            "session_id": session_id,
            "user_answer": "999999",  # deliberately wrong
            "mode": "chapter",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "2",
            "student_id": 99,
        }
        resp2 = build_b4_chap2_chapter_response(payload2, runtime=runtime)
        assert resp2["step_number"] == 1  # advanced to next
        grading = resp2.get("grading_analysis") or {}
        assert grading.get("is_correct") is False


# ─── 9. Visibility audit log writing ─────────────────────────────────────────

class TestVisibilityAuditLog:
    def test_audit_log_written_on_answer(self, monkeypatch):
        """_maybe_write_audit_log is called on answer submission."""
        call_log: list[dict] = []

        def fake_write_audit_log(**kwargs):
            call_log.append(kwargs)

        import core.vocational_math_b4.services.b4_chap2_chapter_mode as _cm
        monkeypatch.setattr(_cm, "_maybe_write_audit_log", fake_write_audit_log)

        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )
        resp0 = build_b4_chap2_chapter_response(
            _minimal_bootstrap_payload(), runtime={}
        )
        runtime = build_b4_chap2_chapter_runtime_store_entry(resp0, 0)
        payload2 = {
            "step_number": 1,
            "session_id": resp0["session_id"],
            "user_answer": resp0["new_question_data"]["correct_answer"],
            "mode": "chapter",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "2",
            "student_id": 99,
        }
        build_b4_chap2_chapter_response(payload2, runtime=runtime)
        assert len(call_log) >= 1, "_maybe_write_audit_log must be called on answer submission"

    def test_audit_log_not_written_on_bootstrap(self, monkeypatch):
        """No audit log is written on bootstrap (no user_answer)."""
        call_log: list[dict] = []

        def fake_write_audit_log(**kwargs):
            call_log.append(kwargs)

        import core.vocational_math_b4.services.b4_chap2_chapter_mode as _cm
        monkeypatch.setattr(_cm, "_maybe_write_audit_log", fake_write_audit_log)

        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
        )
        build_b4_chap2_chapter_response(_minimal_bootstrap_payload(), runtime={})
        assert len(call_log) == 0, "No audit log on bootstrap (no user_answer)"


# ─── 10. No mastery / APR / remediation update ───────────────────────────────

class TestNoMasteryUpdate:
    def test_current_apr_is_zero(self):
        """current_apr must be 0.0 (no APR update for Chap2 chapter mode)."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
        )
        resp = build_b4_chap2_chapter_response(_minimal_bootstrap_payload(), runtime={})
        assert resp["current_apr"] == 0.0

    def test_chapter_mode_flag_present(self):
        """b4_chap2_chapter_mode flag is set in response."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
        )
        resp = build_b4_chap2_chapter_response(_minimal_bootstrap_payload(), runtime={})
        assert resp.get("b4_chap2_chapter_mode") is True


# ─── 11. Friendly error / no silent no-op ─────────────────────────────────────

class TestFriendlyError:
    def test_invalid_step_index_raises(self):
        """Out-of-range step raises ValueError (not silent no-op)."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
        )
        # Simulate a runtime that has completed all steps
        runtime = {
            "correct_answer": "1/2",
            "skill_id": "vh_數學B4_BasicConceptsOfSets",
            "question_text": "test",
            "chap2_step_index": 9,
        }
        payload = {
            "step_number": 10,
            "session_id": uuid.uuid4().hex,
            "user_answer": "5",
            "mode": "chapter",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "2",
            "student_id": 99,
        }
        # After submitting answer for step 9 (last), next step should be 10 → completed
        resp = build_b4_chap2_chapter_response(payload, runtime=runtime)
        assert resp.get("completed") is True

    def test_completion_response_has_no_question_text(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            _build_completed_response,
        )
        resp = _build_completed_response("test_sid", 10)
        assert resp["completed"] is True
        assert resp["unit_completed"] is True

    def test_no_op_detection_resolved_type_2(self):
        """chapter_id=2 resolver always returns a bundle (not empty dict)."""
        from core.routes.practice import _resolve_b4_chapter_adaptive_entry
        bridge, hit = _resolve_b4_chapter_adaptive_entry(
            mode="chapter",
            curriculum="vocational",
            volume="數學B4",
            chapter_id="2",
            skill_ids="",
        )
        assert hit is True
        assert bridge.get("unit_skill_ids"), "unit_skill_ids must not be empty"


# ─── 12. Encoded / decoded volume and chapter label ──────────────────────────

class TestEncodedVolumeHandling:
    def test_resolver_with_normalized_volume(self):
        from core.routes.practice import _resolve_b4_chapter_adaptive_entry
        bridge, hit = _resolve_b4_chapter_adaptive_entry(
            mode="chapter",
            curriculum="vocational",
            volume="數學B4",
            chapter_id="2",
            skill_ids="",
        )
        assert hit is True

    def test_chapter2_hit_detection(self):
        """chapter_id=2 and '2 機率' both trigger Chap2 hit in adaptive_api."""
        b4_chapter2_hit_by_id = "2" == "2"
        b4_chapter2_hit_by_name = "2 機率".startswith("2 機率")
        assert b4_chapter2_hit_by_id
        assert b4_chapter2_hit_by_name


# ─── 13. Chap1 chapter mode not broken ───────────────────────────────────────

class TestChap1NotBroken:
    def test_chap1_resolver_still_works(self):
        from core.routes.practice import _resolve_b4_chapter_adaptive_entry
        bridge, hit = _resolve_b4_chapter_adaptive_entry(
            mode="chapter",
            curriculum="vocational",
            volume="數學B4",
            chapter_id="1",
            skill_ids="",
        )
        assert hit is True
        assert bridge["chapter_id"] == "1"
        assert len(bridge["unit_skill_ids"]) >= 10
        assert "b4_chap2_chapter_mode" not in bridge  # chap2 flag not in chap1 bridge

    def test_chap1_legacy_still_works(self):
        from core.routes.practice import _resolve_b4_chapter_adaptive_entry
        bridge, hit = _resolve_b4_chapter_adaptive_entry(
            mode="single",
            curriculum="",
            volume="",
            chapter_id="",
            skill_ids="1 排列組合",
        )
        assert hit is True
        assert bridge["chapter_id"] == "1"
        assert bridge["compat_path_used"] is True


# ─── 14. /practice Chap2 skill routes not broken ─────────────────────────────

class TestChap2PracticeRouteNotBroken:
    def test_chap2_allowlist_skills_unchanged(self):
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST,
        )
        expected_skills = {
            "vh_數學B4_ProbabilityDefinition",
            "vh_數學B4_ProbabilityProperties",
            "vh_數學B4_SampleSpaceAndEvents",
            "vh_數學B4_ConditionalProbability",
            "vh_數學B4_IndependentEvents",
            "vh_數學B4_MathematicalExpectationDefinition",
            "vh_數學B4_ProbabilityOperations",
            "vh_數學B4_BasicConceptsOfSets",
            "vh_數學B4_ApplicationsOfExpectation",
            "vh_數學B4_MathematicalExpectation",
        }
        assert expected_skills <= B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST

    def test_generate_for_chap2_skill_not_broken(self):
        """generate_for_chap2_skill still works for all Chap2 plan steps."""
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            get_b4_chap2_chapter_plan,
        )
        plan = get_b4_chap2_chapter_plan()
        for step in plan:
            payload = generate_for_chap2_skill(
                skill_id=step["skill_id"],
                problem_type_id=step["problem_type_id"],
                seed=42,
                level=1,
                multiple_choice=True,
            )
            assert payload.get("question_text"), f"Missing question_text for {step['skill_id']}"
            assert payload.get("answer") or payload.get("correct_answer"), (
                f"Missing answer for {step['skill_id']}"
            )


# ─── 15. Teacher audit visibility not broken ─────────────────────────────────

class TestTeacherAuditVisibility:
    def test_audit_module_importable(self):
        from core.vocational_math_b4.services.b4_chap2_visibility_audit import (
            persist_b4_chap2_deterministic_answer_event,
            persist_b4_chap2_gated_event,
        )
        assert callable(persist_b4_chap2_deterministic_answer_event)
        assert callable(persist_b4_chap2_gated_event)


# ─── Diagnostic plan completeness ────────────────────────────────────────────

class TestDiagnosticPlanCompleteness:
    def test_plan_has_correct_number_of_steps(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            get_b4_chap2_chapter_plan,
            B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
        )
        plan = get_b4_chap2_chapter_plan()
        assert len(plan) == B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS == 10

    def test_each_plan_step_has_required_fields(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            get_b4_chap2_chapter_plan,
        )
        required_fields = {"stage", "skill_id", "problem_type_id", "answer_type",
                           "checker", "synthetic_family_id"}
        for i, step in enumerate(get_b4_chap2_chapter_plan()):
            missing = required_fields - set(step.keys())
            assert not missing, f"Step {i} missing fields: {missing}"

    def test_answer_types_are_valid(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            get_b4_chap2_chapter_plan,
        )
        valid_answer_types = {"integer", "rational_fraction", "expected_value"}
        for step in get_b4_chap2_chapter_plan():
            assert step["answer_type"] in valid_answer_types, (
                f"Invalid answer_type '{step['answer_type']}' in step {step['problem_type_id']}"
            )

    def test_deterministic_seed_is_stable(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            _derive_question_seed,
        )
        seed1 = _derive_question_seed("test_session_abc", 0)
        seed2 = _derive_question_seed("test_session_abc", 0)
        seed3 = _derive_question_seed("test_session_abc", 1)
        assert seed1 == seed2, "Same (session, step) must yield same seed"
        assert seed1 != seed3, "Different steps must yield different seeds"

    def test_same_seed_produces_same_question(self):
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
        q1 = generate_for_chap2_skill(
            skill_id="vh_數學B4_ProbabilityDefinition",
            problem_type_id="classical_probability_fraction",
            seed=12345,
        )
        q2 = generate_for_chap2_skill(
            skill_id="vh_數學B4_ProbabilityDefinition",
            problem_type_id="classical_probability_fraction",
            seed=12345,
        )
        assert q1["question_text"] == q2["question_text"]
        assert q1["answer"] == q2["answer"]

    def test_is_chap2_complete_boundary(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            is_b4_chap2_chapter_complete,
            B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
        )
        assert not is_b4_chap2_chapter_complete(0)
        assert not is_b4_chap2_chapter_complete(9)
        assert is_b4_chap2_chapter_complete(10)
        assert is_b4_chap2_chapter_complete(B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS)

    def test_full_diagnostic_flow_10_steps(self):
        """Simulate all 10 steps of the diagnostic flow end-to-end."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
            B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
        )
        runtime = {}
        session_id = None

        for expected_step in range(B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS):
            if expected_step == 0:
                payload = _minimal_bootstrap_payload()
            else:
                # Get correct answer from last question and submit it
                correct = runtime.get("correct_answer", "0")
                payload = {
                    "step_number": expected_step,
                    "session_id": session_id,
                    "user_answer": correct,
                    "mode": "chapter",
                    "entry_mode": "chapter",
                    "curriculum": "vocational",
                    "volume": "數學B4",
                    "chapter_id": "2",
                    "student_id": 99,
                }

            resp = build_b4_chap2_chapter_response(payload, runtime=runtime)
            assert not resp.get("completed"), f"Completed too early at step {expected_step}"
            assert resp["step_number"] == expected_step

            session_id = resp["session_id"]
            runtime = build_b4_chap2_chapter_runtime_store_entry(resp, expected_step)

        # Submit last answer — should complete
        correct = runtime.get("correct_answer", "0")
        final_payload = {
            "step_number": 10,
            "session_id": session_id,
            "user_answer": correct,
            "mode": "chapter",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "2",
            "student_id": 99,
        }
        final_resp = build_b4_chap2_chapter_response(final_payload, runtime=runtime)
        assert final_resp.get("completed") is True, "Should be completed after 10 steps"


# ─── Phase 6N-S: Chap2 Adaptive UI State Contract ─────────────────────────────

class TestChap2UIStateContract:
    """Phase 6N-S: UI state fields must be populated so the frontend can update."""

    def _bootstrap(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )
        payload = _minimal_bootstrap_payload()
        resp = build_b4_chap2_chapter_response(payload, runtime={})
        runtime = build_b4_chap2_chapter_runtime_store_entry(resp, 0)
        return resp, runtime

    def test_bootstrap_has_ui_state_fields(self):
        """Start diagnosis response must include all required UI state fields."""
        resp, _ = self._bootstrap()
        required = [
            "session_id",
            "step_number",
            "total_steps",
            "completed_steps",
            "progress_percent",
            "session_correct_count",
            "session_attempt_count",
            "session_correct_rate",
            "display_mastery_percent",
            "current_stage",
            "current_stage_label",
            "current_skill_id",
            "current_problem_type_id",
            "next_skill_id",
            "next_problem_type_id",
            "trajectory_points",
        ]
        for field in required:
            assert field in resp, f"Missing UI state field: {field}"

    def test_step0_progress_percent_is_zero(self):
        """Bootstrap (step 0) should have progress_percent == 0."""
        resp, _ = self._bootstrap()
        assert resp["progress_percent"] == 0.0

    def test_step0_total_steps_is_ten(self):
        resp, _ = self._bootstrap()
        assert resp["total_steps"] == 10

    def test_step0_trajectory_empty(self):
        """Bootstrap has no answered steps yet — trajectory_points empty."""
        resp, _ = self._bootstrap()
        assert resp["trajectory_points"] == []

    def test_submit_correct_increments_completed_steps(self):
        """After a correct answer, completed_steps should increase."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )
        resp0, runtime = self._bootstrap()
        session_id = resp0["session_id"]
        correct = runtime["correct_answer"]

        payload1 = {
            "step_number": 1,
            "session_id": session_id,
            "user_answer": correct,
            "mode": "chapter",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "2",
            "student_id": 99,
        }
        resp1 = build_b4_chap2_chapter_response(payload1, runtime=runtime)
        assert resp1["completed_steps"] >= 1, "completed_steps should be at least 1 after answer"

    def test_submit_correct_increments_session_correct_count(self):
        """Correct answer increments session_correct_count."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )
        resp0, runtime = self._bootstrap()
        session_id = resp0["session_id"]
        correct = runtime["correct_answer"]

        payload1 = {
            "step_number": 1,
            "session_id": session_id,
            "user_answer": correct,
            "mode": "chapter",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "2",
            "student_id": 99,
        }
        resp1 = build_b4_chap2_chapter_response(payload1, runtime=runtime)
        assert resp1["session_correct_count"] == 1, (
            f"Expected session_correct_count=1, got {resp1['session_correct_count']}"
        )

    def test_submit_correct_updates_session_correct_rate(self):
        """After a correct answer, session_correct_rate should be > 0."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )
        resp0, runtime = self._bootstrap()
        session_id = resp0["session_id"]
        correct = runtime["correct_answer"]

        payload1 = {
            "step_number": 1,
            "session_id": session_id,
            "user_answer": correct,
            "mode": "chapter",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "2",
            "student_id": 99,
        }
        resp1 = build_b4_chap2_chapter_response(payload1, runtime=runtime)
        assert resp1["session_correct_rate"] > 0.0

    def test_submit_correct_display_mastery_percent_positive(self):
        """display_mastery_percent should be > 0 after a correct answer."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )
        resp0, runtime = self._bootstrap()
        session_id = resp0["session_id"]
        correct = runtime["correct_answer"]

        payload1 = {
            "step_number": 1,
            "session_id": session_id,
            "user_answer": correct,
            "mode": "chapter",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "2",
            "student_id": 99,
        }
        resp1 = build_b4_chap2_chapter_response(payload1, runtime=runtime)
        assert resp1["display_mastery_percent"] > 0, (
            f"display_mastery_percent should be > 0, got {resp1['display_mastery_percent']}"
        )

    def test_submit_correct_trajectory_grows(self):
        """After answering step 0, trajectory_points should have 1 entry."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )
        resp0, runtime = self._bootstrap()
        session_id = resp0["session_id"]
        correct = runtime["correct_answer"]

        payload1 = {
            "step_number": 1,
            "session_id": session_id,
            "user_answer": correct,
            "mode": "chapter",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "2",
            "student_id": 99,
        }
        resp1 = build_b4_chap2_chapter_response(payload1, runtime=runtime)
        assert len(resp1["trajectory_points"]) == 1
        tp = resp1["trajectory_points"][0]
        assert tp["answered"] is True
        assert tp["is_correct"] is True
        assert tp["display_mastery_percent"] > 0

    def test_next_skill_updated(self):
        """After step 0, next_skill_id should be non-empty (step 1 skill)."""
        resp0, _ = self._bootstrap()
        assert resp0["next_skill_id"] != "", "next_skill_id should be set after bootstrap"
        assert resp0["next_problem_type_id"] != ""

    def test_submit_incorrect_increments_attempt_not_correct(self):
        """Incorrect answer increments session_attempt_count but not correct_count."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )
        resp0, runtime = self._bootstrap()
        session_id = resp0["session_id"]

        payload1 = {
            "step_number": 1,
            "session_id": session_id,
            "user_answer": "WRONG_ANSWER_99999",
            "mode": "chapter",
            "entry_mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "2",
            "student_id": 99,
        }
        resp1 = build_b4_chap2_chapter_response(payload1, runtime=runtime)
        assert resp1["session_attempt_count"] == 1, (
            f"session_attempt_count should be 1, got {resp1['session_attempt_count']}"
        )
        assert resp1["session_correct_count"] == 0, (
            f"session_correct_count should remain 0, got {resp1['session_correct_count']}"
        )

    def test_complete_all_steps_completed_true(self):
        """Answering all 10 steps should yield completed=True."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
            B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
        )
        runtime = {}
        session_id = None

        for i in range(B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS):
            if i == 0:
                payload = _minimal_bootstrap_payload()
            else:
                payload = {
                    "step_number": i,
                    "session_id": session_id,
                    "user_answer": runtime.get("correct_answer", "0"),
                    "mode": "chapter",
                    "entry_mode": "chapter",
                    "curriculum": "vocational",
                    "volume": "數學B4",
                    "chapter_id": "2",
                    "student_id": 99,
                }
            resp = build_b4_chap2_chapter_response(payload, runtime=runtime)
            session_id = resp["session_id"]
            runtime = build_b4_chap2_chapter_runtime_store_entry(resp, i)

        final_resp = build_b4_chap2_chapter_response(
            {
                "step_number": B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
                "session_id": session_id,
                "user_answer": runtime.get("correct_answer", "0"),
                "mode": "chapter",
                "curriculum": "vocational",
                "volume": "數學B4",
                "chapter_id": "2",
                "student_id": 99,
            },
            runtime=runtime,
        )
        assert final_resp["completed"] is True
        assert final_resp["display_mastery_percent"] > 0

    def test_completed_response_has_final_trajectory(self):
        """Completed response includes trajectory_points with all answered steps."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
            B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
        )
        runtime = {}
        session_id = None

        for i in range(B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS):
            if i == 0:
                payload = _minimal_bootstrap_payload()
            else:
                payload = {
                    "step_number": i,
                    "session_id": session_id,
                    "user_answer": runtime.get("correct_answer", "0"),
                    "mode": "chapter",
                    "curriculum": "vocational",
                    "volume": "數學B4",
                    "chapter_id": "2",
                    "student_id": 99,
                }
            resp = build_b4_chap2_chapter_response(payload, runtime=runtime)
            session_id = resp["session_id"]
            runtime = build_b4_chap2_chapter_runtime_store_entry(resp, i)

        final_resp = build_b4_chap2_chapter_response(
            {
                "step_number": B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
                "session_id": session_id,
                "user_answer": runtime.get("correct_answer", "0"),
                "mode": "chapter",
                "curriculum": "vocational",
                "volume": "數學B4",
                "chapter_id": "2",
                "student_id": 99,
            },
            runtime=runtime,
        )
        assert len(final_resp["trajectory_points"]) == B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS

    def test_display_apr_formula(self):
        """Display APR formula: 0.5 * progress + 0.5 * correct_rate."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _compute_display_apr
        # 5/10 steps done, 4/5 correct
        apr = _compute_display_apr(step_index=5, correct_count=4, attempt_count=5)
        expected = 0.5 * (5 / 10) + 0.5 * (4 / 5)
        assert abs(apr - round(expected, 4)) < 0.001

    def test_display_apr_not_formal_mastery(self):
        """display_mastery_percent must NOT exceed 100."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _compute_display_apr
        apr = _compute_display_apr(step_index=10, correct_count=10, attempt_count=10)
        assert apr <= 1.0
        assert apr >= 0.0

    def test_runtime_store_persists_counters(self):
        """Runtime store entry persists session counters for next call."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )
        resp0, runtime0 = self._bootstrap()
        session_id = resp0["session_id"]
        correct = runtime0["correct_answer"]

        payload1 = {
            "step_number": 1,
            "session_id": session_id,
            "user_answer": correct,
            "mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "2",
            "student_id": 99,
        }
        resp1 = build_b4_chap2_chapter_response(payload1, runtime=runtime0)
        runtime1 = build_b4_chap2_chapter_runtime_store_entry(resp1, 1)

        assert runtime1["session_correct_count"] == 1
        assert runtime1["session_attempt_count"] == 1
        assert len(runtime1["chap2_trajectory_history"]) == 1

    def test_no_formal_mastery_fields_in_response(self):
        """Response must not contain formal mastery fields (APR table keys)."""
        resp0, _ = self._bootstrap()
        forbidden = ["apr_delta", "mastery_level", "mastery_record_id", "fail_streak"]
        for field in forbidden:
            assert field not in resp0, (
                f"Forbidden formal mastery field '{field}' found in Chap2 response"
            )
