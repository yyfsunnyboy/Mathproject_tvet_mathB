# B4 Choice Payload Rendering Repair Summary

## 1. 問題描述

學生端出現 blocking bug：題幹要求「請輸入選項代號」，但畫面沒有顯示任何選項，導致無法作答。

## 2. Root Cause（實查）

- **主因：route contract 缺漏。**
  - `core/routes/practice.py` 的 `/get_next_question` 回傳 JSON 未包含 `choices`，導致前端拿不到選項資料。
- **次因：template 未渲染 choices。**
  - `templates/index.html` 只有渲染 `new_question_text`，未針對 `choices` 顯示選項區塊。
- **相容性缺口：choice alias。**
  - deterministic choice 題原答案多為 `1/2/3/4`，但未統一處理 `A/B/C/D` 輸入別名。

## 3. 修正策略（small repair）

- 不改 B4 coverage 架構、不新增大型 UI。
- 僅補齊 choice payload 全鏈路契約：
  - 後端 route 回傳 `choices`
  - 前端最小渲染 `choices`
  - checker 支援 `A/B/C/D` 與 `1/2/3/4` 等價輸入

## 4. Choice Payload Contract

- 本輪採用 **方案 B（list of strings）**，例如：
  - `choices = ["1. ...", "2. ...", "3. ...", "4. ..."]`
- 每題 deterministic choice 路徑維持：
  - `question_text`
  - `answer`
  - `choices`
  - `explanation`
  - `answer_input_type="choice"`（equivalent to choice mode）
- checker alias：
  - 若正解為 `1`，可接受輸入 `1` / `A` / `a`（其餘類推）

## 5. 修改檔案

- `core/routes/practice.py`
  - `/get_next_question` 回傳新增 `choices`、`choices_display`
  - `/check_answer` 新增 choice alias 正規化（A→1, B→2...）
- `templates/index.html`
  - 新增 `#question-choices` 顯示區
  - 新增 `renderChoices(...)` 渲染邏輯
  - `loadQuestion()` 收到 payload 後渲染 choices

## 6. 新增 Tests

- `tests/test_b4_choice_payload_rendering_repair.py`
  - generator choice contract（StatisticalBasicConcepts）
  - SamplingMethods choice contract（四種抽樣方法選項）
  - route response choices 保留測試
  - check_answer alias（A/a/1）測試
  - frontend rendering safety contract（choices/choices_display；非 choice 路徑不受影響）

## 7. 測試結果

- `pytest -q tests/test_b4_choice_payload_rendering_repair.py` → **6 passed**
- `pytest -q tests/test_b4_3_1_conceptual_skill_boundary_repair.py` → **8 passed**
- `pytest -q tests/test_b4_fullruntime_remaining_skills_mode_aware_paths.py` → **15 passed**
- `pytest -q tests/test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py` → **15 passed**
- `pytest -q tests/test_b4_final_mode_aware_runtime_coverage_recount.py` → **8 passed**

## 8. 是否影響 B4 Final Coverage Count

- 不影響。
- `40/40 mode-aware runtime coverage` 維持不變。
- `unknown_or_no_runtime_count = 0` 維持不變。

## 9. Final Status

`READY_FOR_RECHECK`
