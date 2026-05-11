# Phase B4-Graph-1: B4 Graphical Problem Runtime Path — Inventory + First Runtime-ready Batch

## 1. Scope and guardrails
- 本輪採最小增量：沿用既有 `/practice`（`templates/index.html`）與 `NumberLine/手寫區/AI檢查` 呈現模式。
- 不新增平行頁面、不改 adaptive scoring / APR / PPO / session_engine / DB schema。
- 先做 inventory，再落地第一批 `visual_reading_with_short_answer` runtime-ready family。

## 2. Inventory (B4 graphical/handwriting families)

### A. visual_reading_with_short_answer (first batch target)
- `vh_數學B4_CentralTendencyMeasures:chart_mode_bar_reading`（看長條圖讀值，短答整數）
- `vh_數學B4_DispersionMeasures:chart_range_line_reading`（看折線圖求全距，短答整數）
- 選擇理由：可保留圖形載體，同時維持 deterministic short-answer checker，風險最低。

### B. visual_reading_with_choice_or_structured_answer
- `vh_數學B4_StatisticalChartReading` 相關 chart/table interpretation（目前仍 not-enabled）
- `vh_數學B4_CumulativeFrequencyTablesAndGraphs` 結構化圖表判讀子題（尚需更完整題型契約）

### C. handwriting_or_drawing_ai_checked
- `vh_數學B4_TreeDiagramCounting:tree_diagram_listing`（既有 handwriting + AI judged）
- `vh_數學B4_PascalTriangle:pascal_triangle_handwriting`（既有 handwriting + AI judged）

### D. teacher_review_only (current)
- 需要自由畫圖/開放式敘述且不適合 strict deterministic 的統計圖表構作題（暫維持 review/future_ai_judged）

## 3. First runtime-ready batch implemented
- `vh_數學B4_CentralTendencyMeasures:chart_mode_bar_reading`
- `vh_數學B4_DispersionMeasures:chart_range_line_reading`

以上皆為 `visual-backed + short-answer integer`，且直接走 deterministic checker。

## 4. Runtime path design summary
- 新增 payload/runtime metadata：
  - `visual_backed`
  - `visual_asset_type`
  - `runtime_mode`
  - `check_mode`
  - `grading_mode`
- 本輪命名對應：
  - deterministic 題型：`check_mode=deterministic_auto_checked`
  - AI/手寫題型：沿用既有 `grading_mode=ai_judged_free_response`
- `/check_answer` 新增保護：
  - 若 `check_mode/grading_mode` 屬於 `ai_judged_free_response | visual_ai_checked | handwriting_ai_checked | review_mode`，直接回傳「請使用 AI 檢查」，避免誤走 deterministic path。

## 5. UI contract alignment (reuse existing NumberLine/practice style)
- 沿用 `templates/index.html`，不新增新頁。
- 現有元素維持：
  - 題目文字區
  - 圖像顯示（`image_base64`/`visual_aids`）
  - 輸入框
  - 手寫區（canvas）
  - 圖片上傳
  - AI 檢查按鈕
- 視覺題僅透過 payload 注入圖片/圖表資訊，不改外觀主結構。

## 6. Automated tests

### Added
- `tests/test_b4_graph1_visual_runtime_first_batch.py`
  - 第一批 visual family 可生成
  - payload 帶 visual/check/runtime metadata
  - `/get_next_question` 可回傳 visual-backed payload
  - `/check_answer` 可正確判分（deterministic short-answer）
  - AI/review mode 不誤走 deterministic checker
  - practice 頁面仍具既有視覺題必要元素（題文/圖像/輸入/手寫/上傳/AI檢查）
  - not-enabled skill UX 不退化
  - scenario diversity（非單一模板）檢查

### Regression checks run
- `tests/test_b4_chap3_phase7d_dispersion_measures_runtime_ready.py::test_get_next_question_and_check_answer`
- `tests/test_phase5f_d_free_response_practice_route.py::test_tree_diagram_get_next_question_uses_handwriting_payload_without_skill_module`

### Result
- 新增測試：`8 passed`
- 回歸抽測：`2 passed`

## 7. Changed files
- `core/vocational_math_b4/generators/chap3_statistical_measures.py`
- `core/vocational_math_b4/services/question_router.py`
- `core/routes/practice.py`
- `tests/test_b4_graph1_visual_runtime_first_batch.py`

## 8. Known limitations
- 本輪僅完成「看圖短答 + deterministic」第一批，尚未進入自由手繪批改與教師覆核持久化。
- 圖表題仍以 runtime payload + 既有 UI 呈現，未擴充更細緻圖表互動控件。
- Chap3 其餘 reserved/future_ai_judged 圖形 family 仍保持既有 not-enabled/reserved 策略。

## 9. SOP patch
- 無必要 SOP 補丁（本輪以既有 SOP 與既有 visual/handwriting runtime 模式落地）。

## 10. Manual smoke (minimal) result

### Target families
- `vh_數學B4_CentralTendencyMeasures:chart_mode_bar_reading`
- `vh_數學B4_DispersionMeasures:chart_range_line_reading`

### Checklist outcome
- `/practice` page entry: PASS
- `/get_next_question` visual-backed payload: PASS
- chart render payload (`image_base64` present): PASS
- short-answer input + deterministic `/check_answer`: PASS
- existing handwriting/upload/AI-check UI hooks no conflict: PASS
- non-deterministic visual/review mode guard to 「請使用 AI 檢查」: PASS
- Chap1/Chap2/Chap3 deterministic regression sanity: PASS
- manual-smoke passed families:
  - `vh_數學B4_CentralTendencyMeasures:chart_mode_bar_reading`
  - `vh_數學B4_DispersionMeasures:chart_range_line_reading`

### Notes
- Smoke run used URL-encoded skill ids to avoid shell encoding side effects.
- No runtime code defect found in this smoke round; no patch required.
- Known note (non-blocking): for `CentralTendencyMeasures:chart_mode_bar_reading`, if a tied highest frequency is generated, generator/checker should explicitly allow multi-answer equivalence, or add a constraint to avoid tied modes in later tightening. This does not block this phase pass.

## 11. Next minimal visual family suggestion (proposal only)
- `vh_數學B4_CentralTendencyMeasures`: chart median/mean read-off short-answer variant (visual-backed deterministic)
- `vh_數學B4_DispersionMeasures`: chart min/max direct read short-answer variant (visual-backed deterministic)

## 12. Status
- `MANUAL_SMOKE_PASSED`
