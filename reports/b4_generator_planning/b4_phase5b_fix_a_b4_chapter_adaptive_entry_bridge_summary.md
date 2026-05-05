# Phase 5B-Fix-A Summary: B4 Chapter Adaptive Entry Bridge

## Root Cause
- `dashboard` 章節卡片「1 排列組合」的「單元練習」連結使用舊語意：
  - `/adaptive_practice?mode=single&skill_ids=1+排列組合`
- 其中 `skill_ids` 被塞入章節顯示文字（`1 排列組合`），不是有效 `skill_id`。
- `adaptive_practice_v2` 啟動時會把 `skill_id` 送到 `/api/adaptive/submit_and_get_next`，導致 runtime 無法正確對應 adaptive catalog，造成 400。

## Preferred URL
- 已對齊為：
  - `/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=1`

## Expected Product Flow
- 學生在 `數學B4 -> 1 排列組合` 點選「單元練習」。
- 前端以 chapter-mode 進入 adaptive 頁面。
- chapter bridge 將 Chapter 1 解析到 `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST`。
- 首題 bootstrap 先使用基礎 starter 子池；之後回到完整 allowlist 池做既有 adaptive progression/remediation。
- 回傳 generator-backed deterministic 題目，且不曝露排除題型。

## Files Inspected
- `templates/dashboard.html`
- `core/routes/practice.py`
- `templates/adaptive_practice_v2.html`
- `core/adaptive/session_engine.py`
- `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`

## Files Changed
- `templates/dashboard.html`
  - B4 Chapter 1 卡片的「單元練習」改走 chapter-mode URL（其餘維持舊邏輯）。
- `core/routes/practice.py`
  - 新增 `_resolve_b4_chapter_adaptive_entry(...)` 橋接。
  - 支援 `mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=1` 解析。
  - 安全相容舊 URL：`mode=single&skill_ids=1 排列組合`。
  - 傳遞 `unit_skill_ids`（完整池）、`bootstrap_unit_skill_ids`（starter 子池）、`starter_skill_id` 到前端模板。
  - 新增除錯 log：raw query params、mode、curriculum/volume/chapter_id、compat path、resolved count、starter skill。
- `templates/adaptive_practice_v2.html`
  - base payload 新增 chapter context 與 `unit_skill_ids`。
  - `bootstrap` 第一次送出時改用 `bootstrap_unit_skill_ids`（基礎 starter 子池）。
  - 後續作答沿用完整 `unit_skill_ids`，保留既有 adaptive 行為。
  - 新增前端 console debug 訊息（章節橋接與解析結果）。
- `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`
  - 新增 `B4_CHAPTER_1_ADAPTIVE_STARTER_SKILL_ORDER`。
  - 新增 `starter_b4_candidates(...)`，提供 deterministic 首題 starter 子池。
- `tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`（新增）
  - 覆蓋 dashboard link、chapter resolver、首題 allowlist、排除題型阻擋、舊網址相容、non-B4 不變。

## Before Behavior
- `數學B4 -> 1 排列組合 -> 單元練習` 進入舊 URL。
- 「開始診斷」送出 payload 含非合法 skill 語意，導致 `/api/adaptive/submit_and_get_next` 回 400。

## After Behavior
- 章節卡片連結改為 chapter-mode URL。
- chapter bridge 會把 B4 Chapter 1 解析為 deterministic allowlist 池。
- 首題從基礎 starter 池選取（避免一開始落在 advanced-only 深題）。
- 後續回到完整 allowlist 池，維持既有 progression/remediation。
- excluded problem types (`binomial_expansion_basic`, `tree_diagram_listing`, `pascal_triangle_derivation`) 仍被阻擋。
- non-B4 流程不變。

## QA Commands and Results
- `python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`
  - Result: `6 passed, 9 warnings`
- `python -m pytest -q tests/test_phase4f_main_d_real_smoke_retry_alignment.py tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`
  - Result: `11 passed, 14 warnings`

## Backward Compatibility
- 已實作（safe + minimal）：
  - `/adaptive_practice?mode=single&skill_ids=1+排列組合`
  - 會被橋接為 B4 Chapter 1 chapter-mode 入口語意。
- 同時 dashboard 已切到新 URL，舊路徑僅保留相容。

## Manual Browser Smoke
- 本次 patch 以自動化測試驗證完成。
- 尚未於本回合執行實際瀏覽器手動點擊驗證（若需，我可下一步提供手動 smoke checklist 與預期畫面/Network 檢查點）。
