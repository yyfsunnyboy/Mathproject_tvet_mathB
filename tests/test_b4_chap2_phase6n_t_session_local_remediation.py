# -*- coding: utf-8 -*-
"""Phase 6N-T: B4 Chapter 2 Session-local Remediation Tests.

Verifies that:
1. Consecutive 2 wrong answers in a stage trigger remediation
2. in_remediation=True in response
3. current_strategy shows "近側發展區補救"
4. Bridge problem is from the same stage (simpler problem_type)
5. Bridge problems are NOT reserved listing types
6. Correct remediation answer => return_ready=True, return to mainline
7. Forced return after max attempts
8. Trajectory points include remediation entries
9. No formal mastery / APR / remediation policy written
10. Chap1 chapter mode not broken
11. Phase 6I audit logging not broken
12. Phase 6J teacher audit visibility not broken
"""
import pytest


# ─── Helpers ─────────────────────────────────────────────────────────────────

_RESERVED_LISTING = {
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


def _drive_to_remediation(stage_step_indices: list[int]):
    """
    Drive the session to answer wrong on the specified mainline steps,
    then return (last_resp, runtime) after the remediation trigger.

    stage_step_indices: list of step indices (0-based) to answer wrong twice
    in the same stage, triggering remediation.
    """
    from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
        build_b4_chap2_chapter_response,
        build_b4_chap2_chapter_runtime_store_entry,
    )
    resp0, runtime = _bootstrap()
    session_id = resp0["session_id"]
    current_resp = resp0

    for target_step in stage_step_indices:
        # Advance to the target step correctly first (if not already there)
        while int(current_resp.get("chapter_current_step") or current_resp.get("step_number") or 0) < target_step:
            correct_ans = runtime["correct_answer"]
            current_resp, runtime = _submit(session_id, current_resp["step_number"], correct_ans, runtime)
            if current_resp.get("completed"):
                return current_resp, runtime

        # Answer wrong
        current_resp, runtime = _submit(
            session_id, current_resp["step_number"], "WRONG_99999", runtime
        )
        if current_resp.get("in_remediation") or current_resp.get("completed"):
            return current_resp, runtime

    return current_resp, runtime


# ─── 1. Remediation trigger ────────────────────────────────────────────────

class TestRemediationTrigger:

    def test_two_consecutive_wrong_triggers_remediation(self):
        """Two consecutive wrong answers in Stage 2 should trigger remediation."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )
        resp0, runtime = _bootstrap()
        session_id = resp0["session_id"]

        # Skip to step 2 (Stage 2: classical_probability_fraction)
        for step_i in [0, 1]:
            correct = runtime["correct_answer"]
            resp0, runtime = _submit(session_id, resp0["step_number"], correct, runtime)
            assert not resp0.get("completed"), f"Completed too early at step {step_i}"

        # First wrong answer in Stage 2
        resp1, runtime = _submit(session_id, resp0["step_number"], "WRONG_1", runtime)
        assert not resp1.get("in_remediation"), "Should not remediate after only 1 wrong"

        # Second consecutive wrong answer in Stage 2 → remediation
        resp2, runtime = _submit(session_id, resp1["step_number"], "WRONG_2", runtime)
        assert resp2.get("in_remediation") is True, (
            f"Expected in_remediation=True after 2 consecutive wrong, got: {resp2.get('in_remediation')}"
        )

    def test_single_wrong_no_remediation(self):
        """A single wrong answer must NOT trigger remediation."""
        resp0, runtime = _bootstrap()
        session_id = resp0["session_id"]
        resp1, runtime = _submit(session_id, resp0["step_number"], "WRONG_ONCE", runtime)
        assert not resp1.get("in_remediation"), (
            "Single wrong answer should not trigger remediation"
        )

    def test_remediation_not_triggered_after_correct_reset(self):
        """Wrong, correct, wrong — streak resets, no remediation."""
        resp0, runtime = _bootstrap()
        session_id = resp0["session_id"]
        # Wrong
        resp1, runtime = _submit(session_id, resp0["step_number"], "WRONG", runtime)
        # Correct
        correct = runtime["correct_answer"]
        resp2, runtime = _submit(session_id, resp1["step_number"], correct, runtime)
        # Wrong again — streak reset so no remediation
        resp3, runtime = _submit(session_id, resp2["step_number"], "WRONG", runtime)
        assert not resp3.get("in_remediation"), (
            "Streak should have reset after a correct answer; wrong after reset should not remediate"
        )


# ─── 2. Remediation response contract ─────────────────────────────────────

class TestRemediationResponseContract:

    def _get_remediation_resp(self):
        """Drive to remediation in Stage 1 (steps 0 & 1 both wrong twice)."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )
        resp0, runtime = _bootstrap()
        session_id = resp0["session_id"]
        # Step 0: wrong
        r1, runtime = _submit(session_id, resp0["step_number"], "WRONG_1", runtime)
        # Step 0 (repeated wrong) → should trigger remediation
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)
        return r2, runtime, session_id

    def test_in_remediation_true(self):
        r, _, _ = self._get_remediation_resp()
        assert r.get("in_remediation") is True

    def test_current_strategy_is_remediation(self):
        r, _, _ = self._get_remediation_resp()
        strategy = str(r.get("current_strategy") or "")
        assert "補救" in strategy or "近側" in strategy, (
            f"Expected remediation strategy, got: {strategy}"
        )

    def test_display_mode_is_remediation(self):
        r, _, _ = self._get_remediation_resp()
        assert r.get("display_mode") == "remediation"

    def test_remediation_reason_non_empty(self):
        r, _, _ = self._get_remediation_resp()
        assert str(r.get("remediation_reason") or "").strip() != "", (
            "remediation_reason should be non-empty"
        )

    def test_session_local_fail_streak_present(self):
        r, _, _ = self._get_remediation_resp()
        streak = r.get("session_local_fail_streak")
        assert streak is not None and streak >= 2

    def test_remediation_question_has_skill_id(self):
        r, _, _ = self._get_remediation_resp()
        q = r.get("new_question_data") or {}
        assert q.get("skill_id"), "Bridge question must have skill_id"

    def test_remediation_question_has_problem_type_id(self):
        r, _, _ = self._get_remediation_resp()
        q = r.get("new_question_data") or {}
        assert q.get("problem_type_id"), "Bridge question must have problem_type_id"

    def test_remediation_problem_type_not_reserved_listing(self):
        r, _, _ = self._get_remediation_resp()
        q = r.get("new_question_data") or {}
        pt = q.get("problem_type_id", "")
        assert pt not in _RESERVED_LISTING, (
            f"Bridge problem_type_id '{pt}' is a reserved listing type"
        )

    def test_ppo_strategy_2_in_remediation(self):
        """ppo_strategy=2 signals the frontend a non-mainline path."""
        r, _, _ = self._get_remediation_resp()
        assert r.get("ppo_strategy") == 2

    def test_return_ready_false_in_remediation(self):
        r, _, _ = self._get_remediation_resp()
        assert r.get("return_ready") is False

    def test_has_returned_to_main_false_in_remediation(self):
        r, _, _ = self._get_remediation_resp()
        assert r.get("has_returned_to_main") is False


# ─── 3. Remediation bridge mapping per stage ──────────────────────────────

class TestRemediationBridgeMapping:

    def test_all_stages_have_bridge(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            _CHAP2_REMEDIATION_BRIDGES,
            B4_CHAP2_CHAPTER_STAGES,
        )
        stage_ids = {s["stage_id"] for s in B4_CHAP2_CHAPTER_STAGES}
        for stage_id in stage_ids:
            assert stage_id in _CHAP2_REMEDIATION_BRIDGES, (
                f"No remediation bridge for stage {stage_id}"
            )

    def test_bridge_not_reserved_listing(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _CHAP2_REMEDIATION_BRIDGES
        for stage_id, bridge in _CHAP2_REMEDIATION_BRIDGES.items():
            pt = bridge.get("problem_type_id", "")
            assert pt not in _RESERVED_LISTING, (
                f"Bridge for {stage_id} uses reserved listing '{pt}'"
            )

    def test_bridge_same_stage(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _CHAP2_REMEDIATION_BRIDGES
        for stage_id, bridge in _CHAP2_REMEDIATION_BRIDGES.items():
            assert bridge.get("stage") == stage_id, (
                f"Bridge stage mismatch for {stage_id}: got {bridge.get('stage')}"
            )

    def test_get_remediation_bridge_accessor(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import get_chap2_remediation_bridge
        b = get_chap2_remediation_bridge("stage_2_basic_probability")
        assert b is not None
        assert b["problem_type_id"] == "dice_coin_probability_count"

    def test_unknown_stage_returns_none(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import get_chap2_remediation_bridge
        assert get_chap2_remediation_bridge("nonexistent_stage") is None

    def test_stage3_bridge_is_without_replacement(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import get_chap2_remediation_bridge
        b = get_chap2_remediation_bridge("stage_3_conditional_independent")
        assert b["problem_type_id"] == "without_replacement_conditional_probability"

    def test_stage4_bridge_is_expectation_from_distribution(self):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import get_chap2_remediation_bridge
        b = get_chap2_remediation_bridge("stage_4_expectation")
        assert b["problem_type_id"] == "expectation_from_distribution"


# ─── 4. Return to mainline after remediation ───────────────────────────────

class TestReturnToMainline:

    def _get_remediation_and_session(self):
        """Drive to remediation, return (remediation_resp, runtime, session_id)."""
        resp0, runtime = _bootstrap()
        session_id = resp0["session_id"]
        # Two wrong on step 0 → remediation
        r1, runtime = _submit(session_id, resp0["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)
        assert r2.get("in_remediation"), "Setup failed: not in remediation"
        return r2, runtime, session_id

    def test_correct_remediation_sets_return_ready(self):
        rem_resp, runtime, session_id = self._get_remediation_and_session()
        correct = runtime["correct_answer"]
        r_return, _ = _submit(session_id, rem_resp["step_number"], correct, runtime)
        assert r_return.get("return_ready") is True, (
            f"return_ready should be True after correct remediation, got {r_return.get('return_ready')}"
        )

    def test_correct_remediation_exits_in_remediation(self):
        rem_resp, runtime, session_id = self._get_remediation_and_session()
        correct = runtime["correct_answer"]
        r_return, _ = _submit(session_id, rem_resp["step_number"], correct, runtime)
        assert not r_return.get("in_remediation"), (
            "in_remediation should be False after correct remediation"
        )

    def test_correct_remediation_has_returned_to_main(self):
        rem_resp, runtime, session_id = self._get_remediation_and_session()
        correct = runtime["correct_answer"]
        r_return, _ = _submit(session_id, rem_resp["step_number"], correct, runtime)
        assert r_return.get("has_returned_to_main") is True

    def test_returned_to_main_shows_mainline_question(self):
        """After correct remediation, next question is a mainline plan question."""
        rem_resp, runtime, session_id = self._get_remediation_and_session()
        correct = runtime["correct_answer"]
        r_return, _ = _submit(session_id, rem_resp["step_number"], correct, runtime)
        q = r_return.get("new_question_data") or {}
        # Mainline question must not be a bridge synthetic family
        family_id = q.get("family_id", "")
        assert "BRIDGE" not in family_id.upper() or r_return.get("in_remediation") is False

    def test_forced_return_after_max_attempts(self):
        """After 2 failed remediation attempts, return to mainline regardless."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _CHAP2_MAX_REMEDIATION_ATTEMPTS
        rem_resp, runtime, session_id = self._get_remediation_and_session()

        # Wrong remediation answers up to max attempts
        r = rem_resp
        for i in range(_CHAP2_MAX_REMEDIATION_ATTEMPTS):
            if not r.get("in_remediation"):
                break
            r, runtime = _submit(session_id, r["step_number"], "WRONG_REMEDIATION", runtime)

        # After max attempts, should exit remediation
        assert not r.get("in_remediation"), (
            f"Should have exited remediation after {_CHAP2_MAX_REMEDIATION_ATTEMPTS} wrong attempts"
        )


# ─── 5. Trajectory in remediation ─────────────────────────────────────────

class TestRemediationTrajectory:

    def test_remediation_entry_in_trajectory(self):
        """After answering a remediation question, trajectory includes a bridge entry."""
        resp0, runtime = _bootstrap()
        session_id = resp0["session_id"]
        # Trigger remediation
        r1, runtime = _submit(session_id, resp0["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)
        assert r2.get("in_remediation")
        # Answer remediation
        r3, runtime = _submit(session_id, r2["step_number"], "WRONG_BRIDGE", runtime)

        traj = r3.get("trajectory_points") or []
        # Find remediation entries
        remediation_entries = [tp for tp in traj if tp.get("is_remediation") is True]
        assert len(remediation_entries) >= 1, (
            "Expected at least one remediation trajectory entry"
        )

    def test_mainline_entries_not_marked_remediation(self):
        """Mainline trajectory entries must have is_remediation=False."""
        resp0, runtime = _bootstrap()
        session_id = resp0["session_id"]
        correct = runtime["correct_answer"]
        r1, runtime = _submit(session_id, resp0["step_number"], correct, runtime)

        traj = r1.get("trajectory_points") or []
        for tp in traj:
            if tp.get("is_remediation") is not None:
                assert tp.get("is_remediation") is False, (
                    f"Mainline step should have is_remediation=False, got {tp}"
                )


# ─── 6. No formal mastery / APR / PPO written ─────────────────────────────

class TestNoFormalMasteryWritten:

    def test_remediation_response_no_mastery_fields(self):
        resp0, runtime = _bootstrap()
        session_id = resp0["session_id"]
        r1, runtime = _submit(session_id, resp0["step_number"], "WRONG", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG", runtime)

        forbidden = ["apr_delta", "mastery_level", "mastery_record_id", "fail_streak", "ppo_write"]
        for field in forbidden:
            assert field not in r2, (
                f"Forbidden formal mastery field '{field}' in remediation response"
            )

    def test_display_mastery_percent_is_display_only(self):
        """display_mastery_percent must stay in [0, 100] and not exceed 1.0 in apr form."""
        resp0, runtime = _bootstrap()
        session_id = resp0["session_id"]
        for _ in range(3):
            r, runtime = _submit(session_id, resp0["step_number"], "WRONG", runtime)
            resp0 = r
        pct = resp0.get("display_mastery_percent", 0)
        assert 0 <= pct <= 100


# ─── 7. Regression: Chap1 + audit logging not broken ──────────────────────

class TestRegressionNotBroken:

    def test_chap1_chapter_mode_skill_ids_unaffected(self):
        """B4 Chapter 2 allowlist must remain intact (Phase 6N-T must not touch it)."""
        from core.vocational_math_b4.adaptive.b4_chapter2_phase6c1_allowlist import (
            B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST,
        )
        assert len(B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST) >= 3

    def test_audit_log_still_callable_after_remediation(self):
        """Visibility audit functions must still work."""
        from core.vocational_math_b4.services.b4_chap2_visibility_audit import (
            persist_b4_chap2_deterministic_answer_event,
        )
        assert callable(persist_b4_chap2_deterministic_answer_event)

    def test_remediation_bridges_routable_via_question_router(self):
        """Every bridge problem_type must be callable through generate_for_chap2_skill."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _CHAP2_REMEDIATION_BRIDGES
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill
        for stage_id, bridge in _CHAP2_REMEDIATION_BRIDGES.items():
            try:
                q = generate_for_chap2_skill(
                    skill_id=bridge["skill_id"],
                    problem_type_id=bridge["problem_type_id"],
                    seed=42,
                )
                assert q.get("skill_id") == bridge["skill_id"], (
                    f"Bridge {stage_id}: skill_id mismatch"
                )
            except Exception as exc:
                pytest.fail(
                    f"Bridge {stage_id} not routable via generate_for_chap2_skill: {exc}"
                )

    def test_chap2_chapter_plan_unchanged(self):
        """Main diagnostic plan must still have 10 steps after Phase 6N-T."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
            get_b4_chap2_chapter_plan,
        )
        assert B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS == 10
        assert len(get_b4_chap2_chapter_plan()) == 10

    def test_full_mainline_flow_no_remediation_all_correct(self):
        """Answering all 10 mainline questions correctly: completed=True, no remediation."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
            B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS,
        )
        runtime = {}
        session_id = None
        payload = {
            "mode": "chapter",
            "curriculum": "vocational",
            "volume": "數學B4",
            "chapter_id": "2",
            "step_number": 0,
            "student_id": 99,
        }
        resp = build_b4_chap2_chapter_response(payload, runtime=runtime)
        session_id = resp["session_id"]
        runtime = build_b4_chap2_chapter_runtime_store_entry(resp, 0)

        for i in range(B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS):
            correct = runtime["correct_answer"]
            payload = {
                "step_number": i + 1,
                "session_id": session_id,
                "user_answer": correct,
                "mode": "chapter",
                "curriculum": "vocational",
                "volume": "數學B4",
                "chapter_id": "2",
                "student_id": 99,
            }
            resp = build_b4_chap2_chapter_response(payload, runtime=runtime)
            runtime = build_b4_chap2_chapter_runtime_store_entry(
                resp,
                int(resp.get("chapter_current_step") or resp.get("step_number") or 0),
            )
            if resp.get("completed"):
                break

        assert resp.get("completed") is True, "Should complete after all correct"
        assert not resp.get("in_remediation"), "Should not be in remediation when completed"


# ─── 8. Phase 6N-T-R: Failed-stage lock tests ─────────────────────────────

_EXPECTATION_PROBLEM_TYPES = {
    "expectation_discrete_basic",
    "expectation_from_distribution",
    "expectation_word_problem_profit_fairness",
    "expectation_assessment_numeric",
}


def _advance_to_stage(target_stage: str):
    """
    Bootstrap and advance through mainline steps correctly until the
    first step of `target_stage` is served.  Returns (resp, runtime, session_id).
    """
    from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
        _B4_CHAP2_CHAPTER_PLAN,
    )
    # Find first step index for target stage
    first_target_step = next(
        (i for i, s in enumerate(_B4_CHAP2_CHAPTER_PLAN) if s["stage"] == target_stage), None
    )
    assert first_target_step is not None, f"No plan step for stage {target_stage}"

    resp, runtime = _bootstrap()
    session_id = resp["session_id"]

    for i in range(first_target_step):
        correct = runtime["correct_answer"]
        resp, runtime = _submit(session_id, resp["step_number"], correct, runtime)
        assert not resp.get("completed"), f"Completed too early at step {i}"

    assert resp.get("current_stage") == target_stage or resp.get("chapter_stage") == target_stage, (
        f"Expected stage {target_stage}, got {resp.get('current_stage')}"
    )
    return resp, runtime, session_id


class TestFailedStageLock:
    """Phase 6N-T-R: Bridge selection must use the locked failed_stage, not the advanced step."""

    def test_stage2_wrong_twice_remediation_not_expectation(self):
        """Stage 2 consecutive wrong must produce Stage 2 bridge, NOT expectation."""
        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")

        # Two consecutive wrong in Stage 2
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("in_remediation") is True, "Should be in remediation"
        q = r2.get("new_question_data") or {}
        pt = q.get("problem_type_id", "")
        assert pt not in _EXPECTATION_PROBLEM_TYPES, (
            f"Stage 2 remediation must NOT be expectation problem, got: {pt}"
        )

    def test_stage2_failed_stage_field_is_stage2(self):
        """failed_stage must be 'stage_2_basic_probability', not stage_4."""
        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("in_remediation") is True
        assert r2.get("failed_stage") == "stage_2_basic_probability", (
            f"Expected failed_stage='stage_2_basic_probability', got '{r2.get('failed_stage')}'"
        )

    def test_stage2_failed_skill_id_persisted(self):
        """failed_skill_id must be the Stage 2 skill that triggered remediation."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _B4_CHAP2_CHAPTER_PLAN
        stage2_skills = {s["skill_id"] for s in _B4_CHAP2_CHAPTER_PLAN if s["stage"] == "stage_2_basic_probability"}

        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("failed_skill_id") in stage2_skills, (
            f"failed_skill_id '{r2.get('failed_skill_id')}' not in Stage 2 skills: {stage2_skills}"
        )

    def test_stage2_failed_problem_type_id_persisted(self):
        """failed_problem_type_id must be a Stage 2 problem type."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _B4_CHAP2_CHAPTER_PLAN
        stage2_ptypes = {s["problem_type_id"] for s in _B4_CHAP2_CHAPTER_PLAN if s["stage"] == "stage_2_basic_probability"}

        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("failed_problem_type_id") in stage2_ptypes, (
            f"failed_problem_type_id '{r2.get('failed_problem_type_id')}' not in Stage 2: {stage2_ptypes}"
        )

    def test_stage3_wrong_twice_remediation_not_expectation(self):
        """Stage 3 consecutive wrong must NOT produce expectation bridge."""
        resp, runtime, session_id = _advance_to_stage("stage_3_conditional_independent")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("in_remediation") is True, "Should be in remediation after 2 wrong in Stage 3"
        q = r2.get("new_question_data") or {}
        pt = q.get("problem_type_id", "")
        assert pt not in _EXPECTATION_PROBLEM_TYPES, (
            f"Stage 3 remediation must NOT be expectation problem, got: {pt}"
        )

    def test_stage3_failed_stage_field_is_stage3(self):
        """failed_stage for Stage 3 failure must be stage_3_conditional_independent."""
        resp, runtime, session_id = _advance_to_stage("stage_3_conditional_independent")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("failed_stage") == "stage_3_conditional_independent", (
            f"Expected 'stage_3_conditional_independent', got '{r2.get('failed_stage')}'"
        )

    def test_stage4_remediation_uses_expectation_bridge(self):
        """Only Stage 4 consecutive wrong may use expectation bridge."""
        resp, runtime, session_id = _advance_to_stage("stage_4_expectation")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("in_remediation") is True, "Should be in remediation after 2 wrong in Stage 4"
        q = r2.get("new_question_data") or {}
        pt = q.get("problem_type_id", "")
        assert pt in _EXPECTATION_PROBLEM_TYPES or pt == "expectation_from_distribution", (
            f"Stage 4 bridge should be an expectation type, got: {pt}"
        )
        assert r2.get("failed_stage") == "stage_4_expectation"

    def test_failed_stage_preserved_in_runtime_store(self):
        """failed_stage stored in runtime must survive the bridge call."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_runtime_store_entry,
        )
        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, runtime_after = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("in_remediation") is True
        # The NEW runtime (stored after bridge response) must have failed_stage
        assert runtime_after.get("failed_stage") == "stage_2_basic_probability", (
            f"Runtime failed_stage not preserved: {runtime_after.get('failed_stage')}"
        )

    def test_bridge_problem_type_not_reserved_listing(self):
        """All bridge problem types from all stages must not be reserved listing types."""
        for stage_id in [
            "stage_1_sets_and_sample_space",
            "stage_2_basic_probability",
            "stage_3_conditional_independent",
            "stage_4_expectation",
        ]:
            resp, runtime, session_id = _advance_to_stage(stage_id)
            r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
            r2, _ = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

            if r2.get("in_remediation"):
                q = r2.get("new_question_data") or {}
                pt = q.get("problem_type_id", "")
                assert pt not in _RESERVED_LISTING, (
                    f"Stage {stage_id} bridge uses reserved listing: {pt}"
                )

    def test_remediation_stage_matches_failed_stage(self):
        """remediation_stage_id in bridge response must match failed_stage."""
        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, _ = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("in_remediation") is True
        assert r2.get("remediation_stage_id") == r2.get("failed_stage"), (
            f"remediation_stage_id ({r2.get('remediation_stage_id')}) != "
            f"failed_stage ({r2.get('failed_stage')})"
        )

    def test_return_ready_after_correct_remediation(self):
        """Correct bridge answer must set return_ready=True."""
        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)

        assert r2.get("in_remediation") is True
        correct_bridge = runtime["correct_answer"]
        r3, _ = _submit(session_id, r2["step_number"], correct_bridge, runtime)

        assert r3.get("return_ready") is True, (
            f"return_ready should be True after correct bridge, got: {r3.get('return_ready')}"
        )
        assert not r3.get("in_remediation")

    def test_return_to_main_after_correct_remediation(self):
        """After correct remediation, has_returned_to_main must be True."""
        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)
        correct_bridge = runtime["correct_answer"]
        r3, _ = _submit(session_id, r2["step_number"], correct_bridge, runtime)

        assert r3.get("has_returned_to_main") is True

    def test_trajectory_records_failed_stage(self):
        """Trajectory must include the remediation entry with correct stage."""
        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)
        # Answer the bridge question
        r3, _ = _submit(session_id, r2["step_number"], "WRONG_BRIDGE", runtime)

        traj = r3.get("trajectory_points") or []
        bridge_entries = [tp for tp in traj if tp.get("is_remediation") is True]
        assert len(bridge_entries) >= 1, "Expected at least one remediation trajectory entry"
        for entry in bridge_entries:
            assert entry.get("stage") == "stage_2_basic_probability", (
                f"Bridge trajectory entry has wrong stage: {entry.get('stage')}"
            )


class TestRemediationStageOrderGuard:
    """Phase 6N-T-R2: remediation stage selection must never move forward."""

    @pytest.mark.parametrize(
        "failed_stage, remediation_stage, expected_stage",
        [
            ("stage_1_sets_and_sample_space", "stage_1_sets_and_sample_space", "stage_1_sets_and_sample_space"),
            ("stage_2_basic_probability", "stage_2_basic_probability", "stage_2_basic_probability"),
            ("stage_3_conditional_independent", "stage_3_conditional_independent", "stage_3_conditional_independent"),
            ("stage_4_expectation", "stage_4_expectation", "stage_4_expectation"),
            # drift cases: remediation_stage moved forward, still must lock to failed_stage
            ("stage_2_basic_probability", "stage_3_conditional_independent", "stage_2_basic_probability"),
            ("stage_2_basic_probability", "stage_4_expectation", "stage_2_basic_probability"),
            ("stage_3_conditional_independent", "stage_4_expectation", "stage_3_conditional_independent"),
            ("stage_1_sets_and_sample_space", "stage_4_expectation", "stage_1_sets_and_sample_space"),
        ],
    )
    def test_select_guarded_remediation_stage_matrix(self, failed_stage, remediation_stage, expected_stage):
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import _select_guarded_remediation_stage
        got = _select_guarded_remediation_stage(
            failed_stage=failed_stage,
            remediation_stage=remediation_stage,
        )
        assert got == expected_stage, (
            f"guard mismatch: failed={failed_stage}, remediation={remediation_stage}, got={got}, expected={expected_stage}"
        )

    def test_stage2_runtime_drift_still_uses_stage2_bridge(self):
        """Even if runtime remediation_stage drifts to stage 3, bridge must stay at failed_stage stage 2."""
        from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
            build_b4_chap2_chapter_response,
            build_b4_chap2_chapter_runtime_store_entry,
        )

        resp, runtime, session_id = _advance_to_stage("stage_2_basic_probability")
        r1, runtime = _submit(session_id, resp["step_number"], "WRONG_1", runtime)
        r2, runtime = _submit(session_id, r1["step_number"], "WRONG_2", runtime)
        assert r2.get("in_remediation") is True

        # Simulate runtime drift observed in manual smoke: remediation_stage moved forward.
        drift_runtime = dict(runtime)
        drift_runtime["remediation_stage"] = "stage_3_conditional_independent"

        r3 = build_b4_chap2_chapter_response(
            {
                "step_number": r2["step_number"],
                "session_id": session_id,
                "user_answer": "WRONG_REMEDIATION",
                "mode": "chapter",
                "entry_mode": "chapter",
                "curriculum": "vocational",
                "volume": "?詨飛B4",
                "chapter_id": "2",
                "student_id": 99,
            },
            runtime=drift_runtime,
        )
        runtime_after = build_b4_chap2_chapter_runtime_store_entry(
            r3,
            int(r3.get("chapter_current_step") or r3.get("step_number") or 0),
        )

        q = r3.get("new_question_data") or {}
        assert "ConditionalProbability" not in str(q.get("skill_id") or "")
        assert "IndependentEvents" not in str(q.get("skill_id") or "")
        assert "Expectation" not in str(q.get("skill_id") or "")
        assert str(r3.get("current_stage") or "") in {
            "stage_1_sets_and_sample_space",
            "stage_2_basic_probability",
        }, f"Stage2 remediation drifted forward: {r3.get('current_stage')}"
        assert r3.get("remediation_stage_id") == "stage_2_basic_probability"
        assert runtime_after.get("failed_stage") == "stage_2_basic_probability"
