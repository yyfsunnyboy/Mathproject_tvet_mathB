# Phase 5B-Fix-C: Backend B4 Chapter Bootstrap 400 Fix Summary

## 問題描述
- 前端 Phase 5B-FixB payload 已正確（`mode=teaching`, `entry_mode=chapter`, `step_number=0`, starter/full allowlist 均存在）。
- 但 `POST /api/adaptive/submit_and_get_next` 仍回 400。

## 本次修正範圍
- 只調整 `core/routes/adaptive_api.py` 的 `adaptive_submit_and_get_next` payload bridge / 400 診斷輸出。
- 未修改：
  - B4 generators
  - coverage matrix
  - question router
  - adaptive policy
  - frontend 版面

## 400 路徑盤點（此 endpoint）
- `adaptive_api.py` 本端 400：
  - 只有 `except ValueError as exc: return jsonify(...), 400`
- 該 `ValueError` 來源主要是 `session_engine.submit_and_get_next(payload)` 丟出，例如：
  - `No catalog entries available for the requested adaptive scope`

## Fix-C 核心調整

### 1) 明確 B4 chapter bootstrap 偵測
條件：
- `entry_mode == "chapter"` **或** `mode == "chapter"`
- `curriculum == "vocational"`
- `volume == "數學B4"`
- `chapter_id == "1"`
- `step_number == 0`
- `session_id` 空值

### 2) bootstrap 路徑不走提交答案語意
在偵測為 bootstrap 時：
- 移除/忽略 `session_id`, `user_answer`, `is_correct`, `answer_feedback`
- 保留 runtime：
  - `mode = "teaching"`
  - `entry_mode = "chapter"`
  - `learning_mode = "main"`（缺省補）

### 3) payload 正規化（薄適配）
- `skill_id` 若缺，回填 `starter_skill_id`
- 將 `target_skill_ids` / `skill_ids` / `unit_skill_ids` 正規化為 `list[str]`
- 若 `unit_skill_ids` 缺，從 `target_skill_ids` 或 `skill_ids` 回填
- 若 `target_skill_ids` 缺，從 `skill_ids` 或 `unit_skill_ids` 回填
- 若 `skill_ids` 缺，從 `target_skill_ids` 或 `unit_skill_ids` 回填

### 4) 新增 bootstrap debug log
- 新增 log：
  - `[Phase5B-FixC][b4_chapter_bootstrap] detected ...`
  - 包含 `mode/entry_mode/step_number/session_id/skill_id/target_skill_ids_count/unit_skill_ids_count/received_keys`

### 5) 擴充 400 response 診斷欄位
目前 400 JSON 會包含：
- `error`
- `missing_fields`
- `received_keys`
- `mode`
- `entry_mode`
- `step_number`
- `skill_id`
- `target_skill_ids_count`
- `unit_skill_ids_count`
- `internal_exception_type`
- `internal_exception_message`

## 測試調整
- 更新 `tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`
  - bootstrap API 測試改為模擬實際瀏覽器 payload（`mode=teaching`, `entry_mode=chapter`）
  - 斷言 API 回 200、非 400

## QA
- 指令：
  - `python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`
- 結果：
  - `6 passed, 9 warnings`

## 結論
- Fix-C 已在 backend 端補齊 B4 chapter bootstrap 的判斷與 payload 適配，避免首題啟動被誤判為答題提交流程導致 400。
- 非 B4 流程保持不變（測試仍通過）。
