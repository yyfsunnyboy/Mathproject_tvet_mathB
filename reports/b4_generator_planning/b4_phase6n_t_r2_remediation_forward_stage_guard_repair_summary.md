# Phase 6N-T-R2: Chap2 Remediation Forward-stage Guard Repair Summary

## Status
- READY_FOR_MANUAL_SMOKE

## Scope
- Phase: 6N-T-R2
- Target: Chap2 session-local remediation target selection only
- Guardrail: remediation target must never move to any stage after failed_stage

## Failure Symptom
- In `stage_2_basic_probability`, after consecutive wrong answers, remediation could surface a Stage 3 skill (`ConditionalProbability`) under state drift scenarios.
- This violates stage-prerequisite direction for Chap2 remediation.

## Root Cause
- Existing logic already introduced `failed_stage` lock, but lacked an explicit strict stage-order guard.
- Bridge stage selection could rely on state fields without validating stage rank ceiling.
- Under runtime drift (`remediation_stage` moved forward), selection needed a hard non-forward constraint.

## Minimal Patch

### 1) Strict stage order guard added
File:
- `core/vocational_math_b4/services/b4_chap2_chapter_mode.py`

Changes:
- Added canonical stage order map:
  - `stage_1_sets_and_sample_space = 1`
  - `stage_2_basic_probability = 2`
  - `stage_3_conditional_independent = 3`
  - `stage_4_expectation = 4`
- Added helper:
  - `_stage_rank(stage_id)`
  - `_select_guarded_remediation_stage(failed_stage, remediation_stage)`
- Enforced selection rule:
  - remediation bridge stage must be `<= failed_stage` ceiling
  - if drift/inconsistency occurs, fall back to nearest available prior/equal stage
  - never select a forward stage

### 2) Applied guard on both remediation paths
File:
- `core/vocational_math_b4/services/b4_chap2_chapter_mode.py`

Changes:
- Remediation grading path now uses guarded bridge stage (not raw `remediation_stage`).
- Remediation serving path now uses guarded bridge stage for bridge generation.
- Response fields (`current_stage`, `chapter_stage`, `remediation_stage_id`) align with guarded stage.
- `frustration_index` / streak reset bind to guarded stage key.

### 3) Added stage-order matrix tests
File:
- `tests/test_b4_chap2_phase6n_t_session_local_remediation.py`

New coverage:
- `TestRemediationStageOrderGuard`
- Matrix assertions for strict guard behavior across normal and drift combinations.
- Drift simulation case:
  - `failed_stage=stage_2_basic_probability`
  - forced runtime drift `remediation_stage=stage_3_conditional_independent`
  - verifies remediation still serves Stage 2 bridge (`dice_coin_probability_count` / ProbabilityDefinition).

## Files Touched
- `core/vocational_math_b4/services/b4_chap2_chapter_mode.py`
- `tests/test_b4_chap2_phase6n_t_session_local_remediation.py`

## Regression / Verification

Executed:
- `C:\Python314\python.exe -m pytest -q tests/test_b4_chap2_phase6n_t_session_local_remediation.py`
  - 57 passed
- `C:\Python314\python.exe -m pytest -q tests/test_b4_chap2_phase6n_adaptive_practice_chapter_mode_integration.py`
  - 61 passed

## Guardrail Compliance
- No formal mastery writes changed
- No APR/PPO/AKT policy changes
- No generator / validator changes
- No DB schema changes
- No coverage matrix changes
- No Chap1 chapter mode changes
- No `/practice` route contract changes
- No teacher audit visibility changes

## Runtime Impact
- Chap2 session-local remediation now has hard forward-stage prevention.
- Remediation target candidates are constrained to failed_stage or earlier only.
- Stage 2 failures cannot escalate remediation target to Stage 3/4 under drift.

## Final
- READY_FOR_MANUAL_SMOKE
