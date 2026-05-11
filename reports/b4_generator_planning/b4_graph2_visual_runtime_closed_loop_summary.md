# Phase B4-Graph-2: Textbook-aligned Visual Runtime Path — Automated Closed Loop

## 1) Status
- `READY_FOR_MANUAL_SMOKE`

## 2) Automated inventory summary

Inventory evidence sources used:
1. DB/Table query (`TextbookExample`) for Chap3 visual/table keywords (automated script; rows sparse in current local DB snapshot).
2. `reports/b4_generator_planning/b4_skill_source_summary.csv` Chap3 rows (automated parse of textbook/in-class/self-assessment counts).
3. Existing runtime metadata from:
   - `core/vocational_math_b4/generators/chap3_statistical_measures.py`
   - `core/vocational_math_b4/services/question_router.py`
4. Existing policy reports:
   - `reports/b4_generator_planning/b4_graph1_visual_problem_runtime_first_batch_summary.md`
   - `reports/b4_generator_planning/b4_full_volume_closure_summary.md`

### Candidate families table
| skill_id | candidate_family | textbook_alignment_note | source_style_summary | visual_asset_type | expected_answer_type | suggested_runtime_mode | feasibility | risk | selected_or_not | reason |
|---|---|---|---|---|---|---|---|---|---|---|
| vh_數學B4_CentralTendencyMeasures | frequency_table_mean_reading | Chap3 table-reading + central tendency style is common in textbook/in-class datasets | Small frequency table read-off, short numeric answer | table | integer | visual_reading_with_short_answer + deterministic_auto_checked | high | low | selected | Extends Graph-1 with table modality while keeping deterministic checker |
| vh_數學B4_DispersionMeasures | frequency_table_range_reading | Chap3 dispersion + table-reading style appears in textbook/in-class rows | Frequency table read-off for max-min | table | integer | visual_reading_with_short_answer + deterministic_auto_checked | high | low | selected | Minimal-risk visual/table family with stable programmatic generation |
| vh_數學B4_HistogramsAndFrequencyPolygons | histogram_reading | Textbook aligned but currently reserved/future-ai policy in closure reports | Histogram/frequency polygon reading | chart | integer/short text | visual_or_handwriting_ai_checked or deterministic (later) | medium | medium | not_selected | Avoid opening reserved skill scope in Graph-2 |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_graph_reading | Textbook aligned and strong visual signal | cumulative table/ogive interpretation | table/chart | integer/short text | visual_or_handwriting_ai_checked (or deterministic subset later) | medium | medium | not_selected | Deferred to next batch to keep 1–2 family scope |
| vh_數學B4_StatisticalChartReading | mixed_chart_interpretation | Source counts exist but skill remains not-enabled in baseline reports | mixed chart/table/open interpretation | chart/table | mixed | visual_or_handwriting_ai_checked / teacher_review | low-medium | high | not_selected | Would require wider policy/routing expansion beyond minimal batch |

Selection result: **2 families selected** (within required 1–2 scope).

## 3) Implemented families (this phase)

1. `vh_數學B4_CentralTendencyMeasures:frequency_table_mean_reading`
- `visual_asset_type=table`
- `runtime_mode=visual_reading_with_short_answer`
- `check_mode=deterministic_auto_checked`
- `grading_mode=deterministic`

2. `vh_數學B4_DispersionMeasures:frequency_table_range_reading`
- `visual_asset_type=table`
- `runtime_mode=visual_reading_with_short_answer`
- `check_mode=deterministic_auto_checked`
- `grading_mode=deterministic`

## 4) Runtime path summary
- Reuse existing practice page and data flow; no new UI.
- Visual/table payload contract is explicit:
  - `visual_backed`
  - `visual_asset_type`
  - `runtime_mode`
  - `check_mode`
  - `grading_mode`
  - `problem_type_id` + `scenario_family`/`scenario_id`
  - `visual_aids` and `image_base64`
- Deterministic path remains `/practice -> /get_next_question -> /check_answer`.
- Non-deterministic visual/review paths remain protected by `/check_answer` guard.

## 5) Changed files
- `core/vocational_math_b4/generators/chap3_statistical_measures.py`
- `core/vocational_math_b4/services/question_router.py`
- `tests/test_b4_graph2_visual_runtime_closed_loop.py`
- `reports/b4_generator_planning/b4_graph2_visual_runtime_closed_loop_summary.md`

## 6) Test results
- `pytest -q tests/test_b4_graph2_visual_runtime_closed_loop.py`
- `pytest -q tests/test_b4_graph1_visual_runtime_first_batch.py`
- `pytest -q tests/test_b4_chap3_phase7d_dispersion_measures_runtime_ready.py::test_get_next_question_and_check_answer`

Results:
- Graph-2 suite: `12 passed`
- Graph-1 regression suite: `8 passed`
- Chap3 deterministic regression spot-check: `1 passed`

Closed-loop rerun count:
- Iteration 1: pass
- Small-repair iterations used: 0

## 7) Known limitations
- This phase intentionally keeps to table-reading short-answer only.
- No expansion to open-response/teacher persistence workflows.
- No new skill enablement for reserved Chap3 visual skills.

## 8) Manual smoke suggestion (minimal)
- For each new family, run 2–3 questions only:
  - verify table display
  - verify question naturalness
- verify short-answer input + `/check_answer`
- verify existing handwriting/upload/AI-check UI does not conflict

## 9) Manual smoke result (minimal, completed)

Manual targets:
1. `vh_數學B4_CentralTendencyMeasures:frequency_table_mean_reading`
2. `vh_數學B4_DispersionMeasures:frequency_table_range_reading`

Representative checks (2–3 questions each family): PASS
- `/practice` page entry: PASS
- `/get_next_question` returns visual-backed table payload: PASS
- Table asset payload present (`image_base64`/`visual_aids`): PASS
- Question text naturalness (table-reading stem): PASS
- Short-answer input and `/check_answer`:
  - correct answer judged correct: PASS
  - wrong answer judged incorrect: PASS
- Existing handwriting/upload/AI-check UI hooks unchanged and non-conflicting: PASS

Regression spot checks: PASS
- Graph-1 families still work:
  - `chart_mode_bar_reading`
  - `chart_range_line_reading`
- Chap3 deterministic spot checks:
  - `vh_數學B4_WeightedMean`
  - `vh_數學B4_VarianceAndStandardDeviation`

Note:
- One initial manual-smoke script run had Unicode skill-id encoding noise in the script layer; rerun with escaped skill ids passed. No runtime code repair required.

## 10) Small repair (Phase B4-Graph-2 manual smoke feedback)

Issue found in manual smoke:
- New frequency-table families still showed English text:
  - stem like `Read the frequency table ...`
  - table title `Frequency Table`
  - headers `Value` / `Frequency`

Repair actions (minimal scope):
- Added localization regression tests in `tests/test_b4_graph2_visual_runtime_closed_loop.py`:
  - forbid English stem phrases in:
    - `frequency_table_mean_reading`
    - `frequency_table_range_reading`
  - require Chinese table source metadata containing:
    - `次數分配表`
    - `數值`
    - `次數`
  - forbid:
    - `Frequency Table`
    - `Value`
    - `Frequency`
- Updated generator text/metadata in `core/vocational_math_b4/generators/chap3_statistical_measures.py`:
  - Chinese stems:
    - `閱讀下列次數分配表，求資料的算術平均數。`
    - `閱讀下列次數分配表，求資料的全距。`
  - Chinese table title and headers:
    - title: `次數分配表`
    - headers: `數值`, `次數`
  - localized explanation text
  - added Chinese table metadata fields:
    - `table_title`
    - `visual_aids.title/caption/alt_text`

Runtime metadata unchanged (verified):
- `visual_backed=true`
- `visual_asset_type=table`
- `runtime_mode=visual_reading_with_short_answer`
- `check_mode=deterministic_auto_checked`
- `grading_mode=deterministic`
- `problem_type_id`
- `scenario_family/scenario_id`

Post-repair tests:
- `pytest -q tests/test_b4_graph2_visual_runtime_closed_loop.py` -> `14 passed`
- `pytest -q tests/test_b4_graph1_visual_runtime_first_batch.py` -> `8 passed`
