# Phase 5B-Fix-B Summary: Start Diagnosis Payload Bridge

## 問題現象（Blocking）
- 入口頁可正常開啟：`/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=1`
- 後端已有解析到：
  - `resolved_target_skill_count=13`
  - `starter_skill=vh_數學B4_AdditionPrinciple`
- 但按「開始診斷」後，`POST /api/adaptive/submit_and_get_next` 回 `400`。

## 根因判斷
- 前端 chapter entry payload 與 adaptive runtime `submit_and_get_next` 可接受模式語意不一致。
- `mode=chapter` 直接送入 runtime 容易觸發 `ValueError -> 400`。
- 同時首題啟動 payload 需要顯式攜帶 chapter bridge 欄位（bootstrap pool / starter / chapter context）以避免落入缺欄位或錯誤語意。

## 本次修正範圍（僅 payload bridge）
- 未修改 B4 generators。
- 未修改 coverage matrix。
- 未修改 question router。
- 未修改 adaptive policy。
- 未修改前端版面（僅 JS payload bridge）。

## 變更檔案
- `templates/adaptive_practice_v2.html`
- `core/routes/adaptive_api.py`
- `core/routes/practice.py`（僅補注入 `starter_skill_id`）
- `tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`

## 修正內容

### 1) Template 安全序列化與 payload 組裝
在 `adaptive_practice_v2.html` 確認/補齊注入：
- `mode`（`adaptiveEntryMode`）
- `curriculum`
- `volume`
- `chapter_id`
- `unit_skill_ids`（完整 allowlist）
- `bootstrap_unit_skill_ids`（首題 starter pool）
- `starter_skill_id`

Start diagnosis（`bootstrapBtn`）在 B4 chapter-mode 時，payload 攜帶：
- `target_skill_ids` / `skill_ids`: `bootstrap_unit_skill_ids`
- `unit_skill_ids`: 完整 B4 Chapter 1 allowlist
- `starter_skill_id`
- `curriculum`
- `volume`
- `chapter_id`
- `learning_mode: "main"`
- `entry_mode: "chapter"`
- `mode`: runtime 可接受模式（`teaching`）

並新增：
- `console.log("[Phase5B-FixB] start diagnosis payload", bootstrapPayload)`

### 2) adaptive API 最小橋接（chapter -> runtime mode）
在 `core/routes/adaptive_api.py`：
- 若偵測 `mode=chapter + vocational + 數學B4 + chapter_id=1`：
  - 保留 chapter context（`entry_mode=chapter`）
  - 將 runtime `mode` 正規化為 `teaching`
  - 缺省補 `learning_mode=main`

並在 `400`（`ValueError`）回應新增 debug：
- `received_keys`
- `missing_fields`

### 3) practice route 注入 starter 欄位
在 `core/routes/practice.py` 將 `starter_skill_id` 額外注入模板，以便前端顯式組 payload。

## 測試更新
- 更新 `tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`：
  1. 驗證 chapter entry render 內容包含 `bootstrapUnitSkillIds` / `starterSkillId`
  2. 模擬 chapter start diagnosis POST（含 bootstrap/allowlist/context 欄位）不再 400，且可回傳 allowlisted skill

## QA 指令與結果
- `python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`
  - 結果：`6 passed, 9 warnings`

## 結論
- 本次僅修「開始診斷 payload bridge」，已解除 chapter-mode 入口的 blocking 400。
- chapter context 與 starter/allowlist 欄位已完整傳遞，且後端 400 訊息已可回報 `received_keys/missing_fields` 方便追蹤。
