# B4 Phase 4F Main-D — Real Smoke + Retry Alignment Summary

## 1) Files inspected

- `core/adaptive/session_engine.py`
- `core/routes/adaptive_api.py`
- `core/routes/practice.py`
- `tests/test_phase4f_main_c_adaptive_v2_allowlist.py`
- `tests/test_phase4f_main_b_adaptive_e2e_smoke.py`
- `tests/test_phase4f_main_a_adaptive_generator_first.py`
- `tests/test_b4_chapter1_adaptive_allowlist.py`
- `tests/test_adaptive_m2_api.py`
- `tests/test_vocational_math_b4_question_router_registry_canonical.py`

## 2) Files changed

- `core/adaptive/session_engine.py`
  - Added B4 validator-reject audit capture at generator-layer finalize stage.
  - Added bounded B4 retry alignment in `submit_and_get_next`:
    - trigger condition: B4 allowlisted flow + first generated payload ends at `catalog_fallback` with validator-reject audits.
    - retry behavior: attempt other allowlisted B4 catalog candidates before final fallback.
    - retry bound: max 2 alternate candidates.
    - preserve final safety net: `catalog_fallback` + `_ensure_safe_question_payload`.
  - Added retry audit emission into `new_question_data.adaptive_audit.b4_retry_attempts`.
- `tests/test_phase4f_main_d_real_smoke_retry_alignment.py` (new)
  - Added Main-D smoke and retry-alignment tests.

## 3) Real DB / app smoke coverage

Implemented in `tests/test_phase4f_main_d_real_smoke_retry_alignment.py`:

- `test_main_d_real_app_smoke_b4_route_not_blocked_by_empty_db_and_submit_answer`
  - Verifies B4 allowlisted route can still generate question when DB textbook pool is empty (`recommend_question -> None`).
  - Verifies answer submission path (`/check_answer`) still works with generated payload.
  - Verifies adaptive audit fields are present.

## 4) Frontend smoke coverage

Implemented lightweight route/app-context smoke in:

- `test_main_d_frontend_route_smoke_pages_and_adaptive_endpoint`
  - Verifies page route load (`/adaptive_practice`) returns 200.
  - Verifies adaptive endpoint (`/api/adaptive/submit_and_get_next`) returns valid payload and no route/template missing error.

## 5) Retry behavior design (Main-D)

### Trigger

- Only in B4 allowlisted adaptive flow.
- First generation attempt results in `catalog_fallback` **and** carries validator reject audits (`adaptive_audit.reject_audits`).

### Action

- Before accepting fallback, iterate through other allowlisted B4 entries from current filtered catalog scope.
- Retry with alternate entries (max 2 attempts) via existing `_generate_question_payload`.

### Termination

- If any retry succeeds with non-`catalog_fallback` source, accept that payload.
- If all retries fail, retain existing `catalog_fallback`/safe payload chain as final safety net.

### Observability

- Append audit trail to `new_question_data.adaptive_audit.b4_retry_attempts`:
  - rejected attempt(s) with reason and reject detail.
  - accepted retry marker when success occurs.

## 6) QA commands run

Executed:

- `python -m pytest -q tests/test_phase4f_main_d_real_smoke_retry_alignment.py`
- `python -m pytest -q tests/test_phase4f_main_d_real_smoke_retry_alignment.py tests/test_phase4f_main_c_adaptive_v2_allowlist.py tests/test_phase4f_main_b_adaptive_e2e_smoke.py tests/test_phase4f_main_a_adaptive_generator_first.py tests/test_b4_chapter1_adaptive_allowlist.py tests/test_vocational_math_b4_question_router_registry_canonical.py`

Environment setup needed during run:

- Installed missing runtime deps in active Python env:
  - `pyyaml`
  - `google-api-core`
  - `google-generativeai`
  - plus bulk requirements installation attempt (`python -m pip install -r requirements.txt`), then targeted installs.

## 7) Results

- Main-D dedicated test file:
  - `5 passed`.
- Combined regression set:
  - `58 passed, 27 warnings` (exit code `0`).

## 8) Known limitations

- Current test runtime includes heavy Advanced RAG initialization and external model loading, which increases test wall-time and log volume.
- There are existing warnings (deprecated `google.generativeai`, tokenizer deprecation, torch checkpoint warning), but no test failures.

## 9) Final recommendation (Phase 4F closure vs Main-E)

- **Recommendation:** Phase 4F-Main-D passes the requested regression gate and is ready for Phase 4F closure.
- Next step can proceed to Main-E, with warnings tracked as technical-debt cleanup (non-blocking).
