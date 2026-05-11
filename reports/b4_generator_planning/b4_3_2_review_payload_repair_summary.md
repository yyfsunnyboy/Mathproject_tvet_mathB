# B4 3-2 Review Payload Repair Summary

## 1. 問題描述

本輪聚焦 3-2 兩個學生端體驗問題：

- `vh_數學B4_StatisticalChartReading` 在學生端出現「skill not enabled」生硬錯誤，不符合 visibility/review 路徑。
- `vh_數學B4_CumulativeFrequencyTablesAndGraphs` 題幹要求「依下表補齊」，但 payload 未穩定提供可作答的表格結構。

## 2. 修正策略

- 僅調整 Chap3 review/visibility payload 與 route guard 文案，不修改 3-1 三技能邊界。
- 保持 B4 mode-aware 覆蓋架構不變，不新增 skill、不改 runtime allowlist 計數。

## 3. StatisticalChartReading route / UX 修正

- 移除 `practice.py` 中對 `vh_數學B4_StatisticalChartReading` 的「必填 problem_type 否則 422」限制。
- `/get_next_question` 回傳時新增 `message` 欄位；`statistical_chart_reading_visibility_shell` 內建中文 friendly message：
  - 「此技能屬於統計圖表判讀與教師覆核題，請依題目圖表作答，系統將保留作答供 AI/Review 檢查或教師覆核。」
- `/check_answer` 在 `review_mode` 下對此 skill 回傳 friendly guard，不走 deterministic 比對。

## 4. CumulativeFrequencyTablesAndGraphs 表格 payload 修正

- 保持 review 路徑（非 deterministic）：
  - `runtime_mode=visual_or_handwriting_ai_checked`
  - `check_mode=review_mode`
  - `grading_mode=teacher_review`
- 針對補表題補齊可視化 payload：
  - 新增 `table_title=累積次數分配表`
  - 新增 `table` 規格（`headers`、`rows`）
  - 保留 `visual_aids`（table）
  - 新增 `image_base64`（表格圖片）
- 表格欄位改為：
  - `headers = ["組別", "次數", "累積次數"]`
  - `rows` 至少 4 列，待填欄位使用 `"□"`。
- 補齊：
  - `answer_input_type=free_response_or_handwriting`
  - `expected_answer_schema.minimum_rows / required_points`
  - 中文 `explanation`（由上而下累加）
  - `source_style_summary`、`textbook_alignment_note`
- `/check_answer` 對此 skill 回傳：
  - 「此題需要補表與說明，請使用 AI/Review 檢查或教師覆核。」

## 5. 修改檔案

- `core/vocational_math_b4/generators/chap3_statistical_measures.py`
- `core/routes/practice.py`
- `tests/test_b4_3_2_review_payload_repair.py`
- `reports/b4_generator_planning/b4_3_2_review_payload_repair_summary.md`

## 6. 新增測試

- `tests/test_b4_3_2_review_payload_repair.py`
  - StatisticalChartReading friendly route + review guard
  - CumulativeFrequencyTablesAndGraphs table/visual payload + review guard
  - localization（題幹/訊息/表格 metadata）

## 7. 測試結果

- `pytest -q tests/test_b4_3_2_review_payload_repair.py` → **3 passed**
- `pytest -q tests/test_b4_3_1_conceptual_skill_boundary_repair.py` → **8 passed**
- `pytest -q tests/test_b4_fullruntime_remaining_skills_mode_aware_paths.py` → **15 passed**
- `pytest -q tests/test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py` → **15 passed**
- `pytest -q tests/test_b4_final_mode_aware_runtime_coverage_recount.py` → **8 passed**

## 8. Coverage 影響與最終狀態

- B4 final coverage 計數不變：
  - `40/40 mode-aware runtime coverage`
  - `unknown_or_no_runtime_count = 0`
- 本輪為 review payload/UX 修補，不變更 canonical skill 集合與 coverage gate。

`READY_FOR_RECHECK`
