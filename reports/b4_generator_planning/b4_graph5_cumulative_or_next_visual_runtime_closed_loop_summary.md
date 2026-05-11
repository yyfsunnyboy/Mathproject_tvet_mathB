# Phase B4-Graph-5: Cumulative Frequency Graph / Next Visual Candidate - Autonomous Fidelity-Gated Closed Loop

## 1. Final status
- `BLOCKED`

## 2. Candidate inventory table

| candidate_rank | skill_id | candidate_family | source_type | source_section | source_skill_or_title | observed_question_style | visual_asset_type | expected_answer_type | suggested_runtime_mode | fidelity_decision | feasibility | risk | selected_or_not | reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_graph_reading | textbook_example / in_class_practice / basic_exercise | 3-2 | 例題與練習（累積次數折線圖） | 依累積圖做區間與人數推估，多為多步判讀，且來源常註記 needs_review | cumulative_frequency_graph | integer/mixed | visual_reading_with_short_answer (candidate only) | partially_aligned | medium | high | not_selected | source style可見讀圖，但 evidence 不足以達 aligned deterministic gate。 |
| 2 | vh_數學B4_StatisticalChartReading | mixed_chart_interpretation | self_assessment | 3-2 | 自我評量圖表判讀 | 混合圖型判讀，答案證據穩定性不足 | mixed_chart | mixed | review_mode / future_ai_checked | rejected | low-medium | high | not_selected | 非單一穩定 deterministic short-answer pattern。 |
| 3 | vh_數學B4_HistogramsAndFrequencyPolygons | frequency_polygon_reading | textbook_example / textbook_practice | 3-2 | 例題2、基礎題3 等 | 以次數分配表作圖（直方圖+折線圖）為主 | frequency_polygon | mixed | future_ai_checked / teacher_review | rejected | low | high | not_selected | 作圖題為主，不可為 runtime 方便硬改為讀圖短答（Graph-4已封存 BLOCKED）。 |

## 3. Textbook fidelity evidence table

| source_type | source_section | source_skill_or_title | observed_question_style | matched_runtime_pattern | fidelity_decision | reason |
|---|---|---|---|---|---|---|
| textbook_example | 3-2 | vh_數學B4_CumulativeFrequencyTablesAndGraphs（例題） | 依累積折線圖回答不及格/區間人數，常含多步反推 | cumulative_graph_reading_multi_step | partially_aligned | 可讀圖但證據多標 needs_review，且 deterministic answer contract 不穩。 |
| textbook_practice | 3-2 | vh_數學B4_CumulativeFrequencyTablesAndGraphs（練習） | 完成累積次數表或依圖反推 | cumulative_table_or_graph_completion | rejected | 含填表/反推，非穩定短答 deterministic pattern。 |
| self_assessment | 3-2 | vh_數學B4_StatisticalChartReading（自評題） | 混合圖型判讀 | mixed_chart_interpretation | rejected | 圖型混合與答案證據不穩，非本輪可放行 family。 |
| textbook_example | 3-2 | vh_數學B4_HistogramsAndFrequencyPolygons（例題2） | 由表作圖（直方圖+次數分配折線圖） | frequency_polygon_drawing | rejected | 作圖題，不是讀圖短答；不可改寫放行。 |

## 4. Selected candidate or blocking result

- No candidate satisfied aligned release criteria.
- Blocking table:

| blocked_candidate | blocked_reason | rejected_source_summary | why_not_runtime_ready |
|---|---|---|---|
| cumulative_frequency_graph_reading | no aligned source under deterministic short-answer standard | 來源多為 needs_review，且常含多步反推/補表依賴 | deterministic answer contract、source fidelity 與可驗證性不足 |
| mixed_chart_interpretation | no aligned deterministic pattern | 自評題多為混合圖型判讀 | answer style不穩、風險高、偏review/AI判讀 |
| frequency_polygon_reading | already blocked by Graph-4 reconciliation | 課本主型為作圖 | fidelity gate明確禁止硬改寫成讀圖短答 |

## 5. Confirmation for BLOCKED outcome

- No runtime family released in Graph-5.
- No production code changes were introduced for Graph-5 runtime.
- No synthetic-only family accepted.
- No runtime sample artifacts exported for Graph-5.

## 6. Tests and regressions

- `pytest -q tests/test_b4_graph5_cumulative_or_next_visual_runtime_closed_loop.py -> 6 passed`
- `pytest -q tests/test_b4_graph4_frequency_polygon_runtime_closed_loop.py -> 4 passed`
- `pytest -q tests/test_b4_graph3_histogram_runtime_closed_loop.py -> 10 passed`
- `pytest -q tests/test_b4_graph2_visual_runtime_closed_loop.py -> 14 passed`
- `pytest -q tests/test_b4_graph1_visual_runtime_first_batch.py -> 8 passed`
- `pytest -q tests/test_b4_chap3_phase7d_dispersion_measures_runtime_ready.py::test_get_next_question_and_check_answer -> 1 passed`

## 7. Closed-loop repair log

- Iteration 1: Built candidate inventory and fidelity table; gate verdict remained no aligned release candidate.
- Iteration 2: Added Graph-5 blocked-gate tests and verified no runtime opening.
- Iteration 3: Reran full required regressions to ensure Graph-1/2/3/4 and Chap3 deterministic spot remained green.

## 8. Known limitations

- Current Chap3 visual/table sources for cumulative graph and mixed chart are not stable aligned deterministic-short-answer evidence.
- Releasing cumulative graph runtime now would violate textbook fidelity gate precedence.

## 9. Next suggested candidate (not implemented in this round)

- `vh_數學B4_CumulativeFrequencyTablesAndGraphs:cumulative_frequency_graph_reading` after new aligned source curation:
  - isolate single-step read-off patterns,
  - prove deterministic answer contract,
  - update fidelity table to aligned before any runtime release.
