# Phase B4-Graph-3: Histogram Visual Runtime Path — Textbook-aligned Automated Closed Loop

## 1. Status
- `AUTO_VISUAL_SMOKE_PASSED`

## 2. Inventory summary (automated, compact)

Evidence sources:
1. `reports/b4_generator_planning/b4_skill_source_summary.csv` (Chap3 visual/chart-related rows)
2. `reports/b4_generator_planning/b4_data_quality_review.md` and Phase7A/7E/7G reports
3. Current generator/router/allowlist metadata in `chap3_statistical_measures.py`, `question_router.py`, `b4_chapter3_phase7b_allowlist.py`

### Candidate families table
| skill_id | candidate_family | textbook_alignment_note | source_style_summary | visual_asset_type | expected_answer_type | suggested_runtime_mode | feasibility | risk | selected_or_not | reason |
|---|---|---|---|---|---|---|---|---|---|---|
| vh_數學B4_HistogramsAndFrequencyPolygons | histogram_reading | Chap3 3-2 直方圖題型在課本/隨堂有代表性資料點 | 看圖讀值/讀總數，短答整數 | histogram | integer | visual_reading_with_short_answer + deterministic_auto_checked | high | medium | selected | 單 family 可穩定生成、可 deterministic 判分、最貼近本輪目標 |
| vh_數學B4_HistogramsAndFrequencyPolygons | frequency_polygon_reading | 同技能但偏折線圖/混合圖 | 需更多圖像語義與題型分流 | chart | integer/mixed | visual_or_handwriting_ai_checked (later) | medium | medium-high | not_selected | 本輪只做 1 family，避免同批擴張 |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_graph_reading | 課本有累積圖，但歷史報告多標示 answer 可驗證性不足 | 多為累積折線圖判讀/反推 | chart/table | mixed | visual_or_handwriting_ai_checked (later) | medium-low | high | not_selected | 先避免累積圖反推與多步推論複雜度 |
| vh_數學B4_StatisticalChartReading | mixed_chart_interpretation | 多來自 self_assessment，歷史報告列為保留 | 多圖混合判讀，題型分散 | chart/table | mixed | teacher_review / ai_checked (later) | low-medium | high | not_selected | 超出本輪 deterministic short-answer 範圍 |

Selection rule applied: **only 1 family selected**.

## 3. Implemented family
- skill_id: `vh_數學B4_HistogramsAndFrequencyPolygons`
- family/problem_type: `histogram_reading`
- visual_asset_type: `histogram`
- runtime_mode: `visual_reading_with_short_answer`
- check_mode: `deterministic_auto_checked`
- grading_mode: `deterministic`

## 4. Textbook alignment summary (no long quote)
- 依 Chap3 統計資料整理的直方圖題風格，優先實作「看圖直接讀值/求總數」的短答型問題。
- 避免本輪進入「要求學生作圖」或「多步開放式判讀」，保持與 Graph-1/Graph-2 同樣可驗證的 deterministic 規格。

## 5. Runtime path summary
- Reuse existing practice page/runtime path; no new UI.
- Payload contract explicitly includes:
  - `visual_backed=true`
  - `visual_asset_type=histogram`
  - `runtime_mode=visual_reading_with_short_answer`
  - `check_mode=deterministic_auto_checked`
  - `grading_mode=deterministic`
  - `problem_type_id=histogram_reading`
  - `scenario_family/scenario_id`
  - `visual_aids` and `image_base64`
- Student-facing texts are localized Chinese (question/explanation/chart metadata).

## 6. Changed files
- `core/vocational_math_b4/generators/chap3_statistical_measures.py`
- `core/vocational_math_b4/services/question_router.py`
- `core/vocational_math_b4/adaptive/b4_chapter3_phase7b_allowlist.py`
- `tests/test_b4_graph3_histogram_runtime_closed_loop.py`
- `reports/b4_generator_planning/b4_graph3_histogram_runtime_closed_loop_summary.md`

## 7. Tests run
- `pytest -q tests/test_b4_graph3_histogram_runtime_closed_loop.py`
- `pytest -q tests/test_b4_graph2_visual_runtime_closed_loop.py`
- `pytest -q tests/test_b4_graph1_visual_runtime_first_batch.py`
- `pytest -q tests/test_b4_chap3_phase7d_dispersion_measures_runtime_ready.py::test_get_next_question_and_check_answer`

Results:
- Graph-3 suite: `9 passed`
- Graph-2 regression: `14 passed`
- Graph-1 regression: `8 passed`
- Chap3 deterministic spot: `1 passed`

## 8. Localization result
- 題幹中文：是
- 圖表標題中文：是（直方圖）
- 軸標籤中文：是（分數區間 / 人數）
- explanation 中文：是
- 英文殘留（student-facing template words）：未檢出

## 9. Closed-loop repair log
- Iteration 1 failed on `/get_next_question` for histogram skill with `Chap3 skill not enabled` (allowlist encoding/normalization mismatch path).
- Small repair applied (minimal):
  - file: `core/vocational_math_b4/adaptive/b4_chapter3_phase7b_allowlist.py`
  - change: robust fallback match for `skill_id.endswith("HistogramsAndFrequencyPolygons")` in:
    - `is_b4_chapter3_phase7b_deterministic_skill`
    - `is_b4_chapter3_skill_not_enabled`
- Iteration 2 rerun: all required suites passed.

## 10. Known limitations
- 本輪只開 `histogram_reading` 單 family，不含 frequency polygon/cumulative graph。
- 題型仍屬短答判讀；未涵蓋畫圖或開放式統計解釋。

## 11. Manual smoke suggestion (next step)
- 僅需 `histogram_reading` 2–3 題代表性檢查：
  - 圖形顯示正常
  - 中文化無殘留英文
  - 短答輸入與正錯判斷正確
  - 手寫/上傳/AI檢查 UI 不衝突

## 12. Automated visual sample smoke result (agent-side)

Target family:
- `vh_數學B4_HistogramsAndFrequencyPolygons:histogram_reading`

Automated sample count: `3` (seeds 3/11/19), PASS
- `/practice` page entry: PASS
- `/get_next_question` histogram visual-backed payload: PASS
- Histogram asset payload present (`image_base64`/`visual_aids`): PASS
- Chart title / axis labels / question stem / explanation in Chinese: PASS
- Question style aligns with textbook-like histogram read-off/total-count tasks: PASS
- Short-answer input and `/check_answer`:
  - correct answer judged correct: PASS
  - wrong answer judged incorrect: PASS
- Existing handwriting/upload/AI-check UI hooks non-conflicting: PASS

Regression spot checks: PASS
- Graph-1:
  - `chart_mode_bar_reading`
  - `chart_range_line_reading`
- Graph-2:
  - `frequency_table_mean_reading`
  - `frequency_table_range_reading`
- Chap3 deterministic:
  - `vh_數學B4_WeightedMean`
  - `vh_數學B4_VarianceAndStandardDeviation`

Sample artifacts (auto-exported):
- `reports/b4_generator_planning/graph3_samples/graph3_histogram_sample_01.png`
- `reports/b4_generator_planning/graph3_samples/graph3_histogram_sample_02.png`
- `reports/b4_generator_planning/graph3_samples/graph3_histogram_sample_03.png`

Localization result:
- 題幹中文：PASS
- 圖表標題中文：PASS
- x/y 軸標籤中文：PASS
- explanation 中文：PASS
- 英文殘留關鍵詞（Histogram/Frequency/Read the histogram/interval/count/total frequency）：未檢出

check_answer result:
- 正確答案判對：PASS
- 錯誤答案判錯：PASS

Policy note:
- 本 phase 改採 automated visual sample smoke first，不再要求使用者執行人工連按檢查；人工僅保留給疑難案例或抽樣覆核。
