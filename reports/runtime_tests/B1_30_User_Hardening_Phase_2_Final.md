# B1 30-User Hardening Phase 2 Final

Date: 2026-09-13 (Asia/Taipei)

## Result

PASS. Tests used isolated SQLite databases and exactly one Waitress process per measured run. No commit or push was performed. Gencode, B2, and B4 were not changed by this phase.

## Runtime changes

- Vocational dashboard recent-attempt metadata and class/teacher data now use bulk queries.
- Measured dashboard context SQL statements: 167 before-path simulation, 7 optimized.
- A gradable `/check_answer` now stages Progress and PracticeAttempt together and commits once. Focused instrumentation asserts one DB commit per submit.
- Adaptive catalog and manifest loads use thread-safe path + `(mtime_ns, size)` caches. Returned values are deep copies; manifest writes invalidate the cache.
- AI entry points release the Flask-SQLAlchemy request session immediately before external model waits. Tests assert zero checked-out connections and no active transaction at the model call.
- Added reproducible B1 load DB preparation, one-process Waitress runner, and Locust normal/burst scenarios. The load scenario uses all 23 published B1 skills and selects deterministic non-drawing components.

## 30 users, normal student flow, 10 minutes

Source: `b1_phase2_normal_10m_20260913_1715_stats.csv`

| Metric | Result |
|---|---:|
| Requests | 35,132 |
| Failures / 5xx / timeouts | 0 / 0 / 0 |
| Aggregate p50 / p95 | 9 ms / 22 ms |
| Dashboard p50 / p95 | 11 ms / 29 ms |
| Get question p50 / p95 | 9 ms / 23 ms |
| Practice page p50 / p95 | 7 ms / 17 ms |
| Submit p50 / p95 | 7 ms / 16 ms |
| Submit requests | 8,775 |
| sqlite_locked / pool_timeout | 0 / 0 |
| Missing writes | 0 |
| Duplicate write groups | 0 |

The isolated normal-run database ended with 17,537 PracticeAttempt rows and `SUM(Progress.questions_solved)=17,537`, including the preceding full-duration correctness run. All question UIDs are non-null and unique per student.

## 30 users, near-simultaneous submit

Source: `b1_phase2_burst_20260913_stats.csv`

| Metric | Result |
|---|---:|
| Requests | 150 |
| Submit requests | 30 |
| Failures / 5xx / timeouts | 0 / 0 / 0 |
| Aggregate p50 / p95 | 170 ms / 860 ms |
| Submit p50 / p95 | 150 ms / 210 ms |
| sqlite_locked / pool_timeout | 0 / 0 |
| PracticeAttempt writes | 30 |
| Progress questions solved | 30 |
| Missing / duplicate writes | 0 / 0 |

## Verification

- Focused Phase 2 and production hardening: 12 passed.
- B1 23-skill production/runtime regression: 238 passed.
- `git diff --check`: passed (line-ending warnings only).
