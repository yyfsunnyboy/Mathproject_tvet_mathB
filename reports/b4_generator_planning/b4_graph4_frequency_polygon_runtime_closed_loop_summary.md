# Phase B4-Graph-4: Frequency Polygon Visual Runtime Path - Textbook Fidelity Gate

## 1. Status
- `BLOCKED`

## 2. Inventory summary (automated, compact)

Evidence sources:
1. `reports/b4_generator_planning/b4_skill_source_summary.csv`
2. `reports/b4_generator_planning/b4_skill_example_sequence.md`
3. `reports/b4_generator_planning/b4_data_quality_review.md`
4. `reports/b4_generator_planning/b4_phase7a_chap3_textbook_evidence_skill_inventory_plan.md`
5. Existing Graph-1/Graph-2/Graph-3 reports and current Chap3 generator/router/allowlist metadata

### Candidate families table
| skill_id | candidate_family | textbook_alignment_note | source_style_summary | visual_asset_type | expected_answer_type | suggested_runtime_mode | feasibility | risk | selected_or_not | reason |
|---|---|---|---|---|---|---|---|---|---|---|
| vh_數學B4_HistogramsAndFrequencyPolygons | frequency_polygon_reading | Chap3 3-2 source style is primarily draw-from-table. | Main style is drawing histogram/frequency polygon, not read-off short answer. | frequency_polygon | mixed | future_ai_checked / teacher_review | low | high | selected_for_gate_only | Evaluated by fidelity gate only; not released to deterministic runtime. |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_graph_reading | 3-2 has cumulative graph reading, but high needs_review and mixed validation evidence. | Cumulative line chart read-off and reverse inference. | cumulative_frequency_graph | integer/mixed | future_ai_checked | medium | high | not_selected | Out of Graph-4 single-family scope. |
| vh_數學B4_StatisticalChartReading | mixed_chart_interpretation | Mostly self-assessment mixed chart interpretation. | Multi-chart interpretation with less stable answer evidence. | mixed_chart | mixed | review_mode | low-medium | high | not_selected | Out of Graph-4 scope and not deterministic-ready. |

Selection rule applied: **only 1 family was evaluated for release (`frequency_polygon_reading`)**.

## 3. Textbook fidelity evidence

### Textbook fidelity evidence table
| source_type | source_section | source_skill_or_title | observed_question_style | matched_runtime_pattern | fidelity_decision | reason |
|---|---|---|---|---|---|---|
| textbook_example | 3-2 | vh_數學B4_HistogramsAndFrequencyPolygons / 例題 2 | 依次數分配表畫直方圖與次數分配折線圖 | frequency_polygon_drawing | rejected | Drawing task; not read-off short-answer. |
| textbook_practice | 3-2 | vh_數學B4_HistogramsAndFrequencyPolygons / 基礎題 3 | 給定分組資料後畫圖 | frequency_polygon_drawing | rejected | Requires drawing workflow; not deterministic read-off short-answer. |
| self_assessment | 3-2 | vh_數學B4_StatisticalChartReading / 自我評量 5-7 | 依累積折線圖判讀區間或人數 | cumulative_graph_reading | partially_aligned | Different skill/graph type and mostly needs_review sources. |

Textbook fidelity decision:
- `frequency_polygon_read_single_group`: no aligned source found.
- `frequency_polygon_total_count`: no aligned source found.
- Without aligned pattern, `frequency_polygon_reading` cannot be released.

## 4. Runtime decision
- Do not open `vh_數學B4_HistogramsAndFrequencyPolygons:frequency_polygon_reading` in runtime registry.
- Do not add Graph-4 deterministic visual payload release in this phase.
- Keep frequency polygon as future `ai_checked` / `teacher_review` track until aligned evidence exists.

## 5. Textbook alignment note
- source_style_summary: Chapter 3-2 frequency polygon materials are mainly drawing-oriented.
- textbook_alignment_note: This phase follows fidelity gate priority and does not rewrite drawing tasks into read-off short-answer only to satisfy runtime.

## 6. Files changed (Graph-4 gate only)
- `tests/test_b4_graph4_frequency_polygon_runtime_closed_loop.py`
- `reports/b4_generator_planning/b4_graph4_frequency_polygon_runtime_closed_loop_summary.md`

## 7. Tests run
- `pytest -q tests/test_b4_graph4_frequency_polygon_runtime_closed_loop.py -> 4 passed`
- `pytest -q tests/test_b4_graph3_histogram_runtime_closed_loop.py -> 10 passed`
- `pytest -q tests/test_b4_graph2_visual_runtime_closed_loop.py -> 14 passed`
- `pytest -q tests/test_b4_graph1_visual_runtime_first_batch.py -> 8 passed`
- `pytest -q tests/test_b4_chap3_phase7d_dispersion_measures_runtime_ready.py::test_get_next_question_and_check_answer -> 1 passed`

## 8. Localization note
- No new Graph-4 runtime payload was released in this reconciliation.
- Graph-1/2/3 regressions remained green, so existing localization behavior was not regressed.

## 9. Closed-loop repair log
- Iteration 1: Runtime-first attempt existed previously, but fidelity gate evidence remained insufficient.
- Iteration 2: Reconciled to evidence-first decision and retained BLOCKED status.

## 10. Not handled this round
- `frequency_polygon_drawing`: drawing-type tasks, reserved for AI/teacher review.
- `cumulative_frequency_graph_reading`: not in Graph-4 single-family scope.
- `mixed_chart_interpretation`: mixed-chart/open interpretation outside deterministic scope.

## 11. Known limitations
- No aligned textbook evidence for frequency polygon read-off short-answer patterns in current corpus.
- Runtime success alone cannot override textbook fidelity gate.

## 12. Next-step recommendation
- Keep `BLOCKED` until aligned read-off source evidence is found.
- If future evidence appears, run a new Graph-4 closed loop with aligned-source checks first.

## 13. Final Textbook Fidelity Reconciliation

1. 第二次 runtime pattern 是否有直接對應課本/題庫中的 aligned source：**否**。
2. aligned source 是什麼：目前無 aligned source；可追溯 source 全為 `rejected` 或 `partially_aligned`（見上表）。
3. 該 source 是讀圖短答還是作圖題：主證據是**作圖題**；次證據是累積圖判讀，非本輪目標 skill pattern。
4. 如果是作圖題，是否允許改寫成讀圖短答：**不允許**（若僅為 runtime 方便改寫，判定不合格）。
5. 第二次 `AUTO_VISUAL_SMOKE_PASSED` 是否應保留：**不保留**。
6. 最終狀態：**`BLOCKED`**。

Reconciliation conclusion:
- Textbook fidelity gate takes precedence over runtime success, tests passed, and sample artifacts.
- No new aligned evidence was added to overturn the first BLOCKED decision, so Graph-4 remains blocked and runtime opening is not retained.
