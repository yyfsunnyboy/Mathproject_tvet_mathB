# B4 Phase 5B-Fix-E1 Summary: Wire Existing B4-to-B4 Remediation Bridge

## Root Cause
- B4 Chapter 1 deterministic adaptive flow had allowlisted/generator-ready skills, but repeated-wrong remediation routing still depended on generic non-B4 retrieval paths.
- In repeated wrong scenarios, routing often stayed on `stay`, producing empty/irrelevant `mapping_candidates` and no viable remediation skill switch for B4 teaching practice.

## Inventory Report Finding Used
- Based on `reports/b4_generator_planning/b4_phase5b_b4_subskill_remediation_inventory_from_yaml.md`, formal B4 YAML subskill ontology is not present yet.
- Existing in-code bridge `B4_CHAPTER_1_REMEDIATION_BRIDGE` already exists and is suitable for minimal pilot bridge routing in E1.

## Existing Bridge Mapping Summary
- Mapping source: `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`
- Bridge keys: all B4 Chapter 1 deterministic allowlisted skill IDs.
- Bridge values: prerequisite B4 Chapter 1 deterministic allowlisted target skills only.
- Guardrails verified in tests:
  - targets are in `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST`
  - targets are not in `B4_MANUAL_REVIEW_OR_UNAVAILABLE_SKILL_IDS`
  - excluded problem types remain blocked by payload validator

## Files Inspected
- `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`
- `core/adaptive/session_engine.py`
- `tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`
- `reports/b4_generator_planning/b4_phase5b_b4_subskill_remediation_inventory_from_yaml.md`

## Files Changed
- `core/adaptive/session_engine.py`
- `tests/test_phase5b_fix_e1_b4_remediation_bridge.py`
- `reports/b4_generator_planning/b4_phase5b_fix_e1_b4_to_b4_remediation_bridge_summary.md`

## B4-only Override Rule (Implemented)
- Scope is strictly B4 Chapter 1 teaching + `unit_practice` path.
- When all are true:
  - not already in remediation
  - bridge candidates exist from `B4_CHAPTER_1_REMEDIATION_BRIDGE`
  - route action came out as `stay`
  - repeated-failure threshold hit:
    - `fail_streak >= 2` OR
    - `consecutive_wrong_on_family >= 2` OR
    - `frustration_index >= 3`
- Then:
  - force `remediation_review_ready = True`
  - force route to remediation
  - select first viable B4 bridge candidate
  - persist remediation target skill as `routing_session.remediation_skill_id`
  - force remediation subskill marker `b4_chapter1_bridge_remediation`
  - constrain remediation question selection to selected B4 target skill ID

## Logging Added
- Tag: `[Phase5B-FixE1][b4_remediation_bridge]`
- Fields logged:
  - `current_b4_skill_id`
  - `current_family_id`
  - `fail_streak`
  - `consecutive_wrong_on_family`
  - `frustration_index`
  - `candidates`
  - `selected_remediation_skill`
  - `reason`
  - `override_applied`

## QA Commands / Result
- Commands to run:
  - `python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`
  - `python -m pytest -q tests/test_phase5b_fix_e1_b4_remediation_bridge.py`
- Result: to be executed in local environment after patch application.

## Manual Browser Smoke Recommendation
- Open B4 Chapter 1 teaching/unit practice.
- Trigger repeated wrong on a mapped skill (e.g. `vh_數學B4_BinomialTheorem`).
- Verify response and UI state include remediation indicators:
  - `post_mode=remediation` or `in_remediation=true`
  - `remediation_skill=<B4 target skill>`
  - `remediation_subskill=b4_chapter1_bridge_remediation`
  - `route_action=remediate`
- Verify next question skill ID matches mapped bridge target.

## Deferred Scope Note
- Formal B4 YAML ontology design and integration is intentionally deferred to **Phase 5B-Fix-E2**.
