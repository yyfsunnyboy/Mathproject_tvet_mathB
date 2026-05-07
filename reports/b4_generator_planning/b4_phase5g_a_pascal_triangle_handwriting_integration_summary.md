# Phase 5G-A Pascal Triangle Handwriting Integration Summary

## 1) 本階段目的
- 將 B4 Chapter 1 的「巴斯卡三角形」技能導入既有 `/practice` 手寫作答與 AI 判斷流程。
- 入口仍使用 dashboard 技能卡片，不新增新練習頁。

## 2) 為什麼巴斯卡三角形不走 int-answer
- 巴斯卡列舉與二項式展開屬於多項內容（係數、次方、符號、項次），單一整數答案無法完整判斷學習品質。
- 因此改走 `answer_type=handwriting` + `grading_mode=ai_judged_free_response`，沿用樹狀圖已驗證流程。

## 3) 支援 variants
- `pascal_row_listing`
- `pascal_binomial_expansion`

## 4) 題目 payload 設計
- 新增 `core/vocational_math_b4/free_response/pascal_triangle_judge.py`。
- 提供 `build_pascal_triangle_payload(variant, index)` 與：
  - `problem_type_id=pascal_triangle_handwriting`
  - `skill_id=vh_數學B4_PascalTriangle`
  - `answer_type=handwriting`
  - `grading_mode=ai_judged_free_response`
  - `variant`
  - `question_text`
  - `n`
  - `expected_row`
  - `expected_terms`
  - `expected_expansion`
- `/get_next_question` 使用 `pascal_triangle_index` 輪替題型，不走 deterministic int-answer generator。

## 5) Handwriting AI rubric
- 在 `/analyze_handwriting` 新增 `problem_type=pascal_triangle_handwriting` 分支。
- Prompt 內容包含：`question_text`、`expected_row`、`expected_terms`、`expected_expansion` 與四級判定：
  - `correct`
  - `partial`
  - `incorrect`
  - `needs_review`
- 回傳格式與既有 handwriting response 相容（含 `handwriting_status`、`handwriting_analysis`、`correct`、`next_question`）。

## 6) 修改檔案
- `core/vocational_math_b4/free_response/pascal_triangle_judge.py`
- `core/routes/practice.py`
- `core/routes/analysis.py`
- `templates/dashboard.html`
- `templates/index.html`
- `tests/test_phase5g_a_pascal_triangle_handwriting_flow.py`

## 7) 測試結果
- 已新增 Phase 5G-A 專屬測試檔，並執行指定測試指令（結果見本次執行輸出）。

## 8) Runtime 邊界
- 不改 `check_answer` 的 deterministic int-answer 主流程。
- 不改 `/api/adaptive/submit_and_get_next`。
- 不改 deterministic allowlist。
- 不改 B4 deterministic `question_router`。
- 不改 coverage matrix。

## 9) Known limitations
- 完整展開式的手寫辨識仍可能受筆跡影響，實務上仍建議教師抽查。
- 第一版不處理複雜 `$(ax+b)^n`（如 `$(3x+2)^4`）。
- 第一版不處理巴斯卡三角形推導證明題（僅列舉列與基本二項式展開）。
