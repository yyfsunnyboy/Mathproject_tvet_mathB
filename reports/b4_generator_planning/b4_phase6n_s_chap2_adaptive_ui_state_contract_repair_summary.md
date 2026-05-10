# Phase 6N-S：Chap2 Adaptive UI State Contract Repair

## Summary

| 欄位 | 值 |
|------|----|
| Phase | 6N-S |
| 狀態 | READY_FOR_MANUAL_SMOKE |
| 關聯 Phase | 6N（Chap2 Chapter Mode Integration）、6N-R（Dashboard Link Repair） |
| 變更檔案數 | 3 |
| 新測試數 | 17（TestChap2UIStateContract） |
| 總測試通過 | 1017 passed（regression 累計） |

---

## 1. Failure Symptom（手動測試失敗現象）

在 `/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=2&learning_mode=teaching&practice_kind=unit_practice` 頁面：

- 按「開始診斷」→ 可正確出第一題 ✅
- 送出答案 → 後端 `/api/adaptive/submit_and_get_next` 正常推進步驟 ✅
- **但前端 UI 靜止不動：**
  - APR 環（掌握度圓環）永遠顯示 **0%**
  - 動態精熟軌跡圖（trajectoryBox）條寬度全部 **0%**
  - 本單元學習導航（navProgressBox）顯示「**推估中（0 / 6）**」，進度條寬度 **0%**
  - 題號 / step 顯示正常（有更新），但掌握度相關的所有數值停滯

---

## 2. Root Cause（根本原因）

經定點檢查 `adaptive_practice_v2.html`，確認三個獨立問題：

### 問題 A：`current_apr` 固定為 0.0

`b4_chap2_chapter_mode.py` 的 response 中：
```python
"current_apr": 0.0,  # 固定值，從不更新
```

前端 `updateOverview` 讀取 `response.current_apr`，`Number(0.0 || 0)` → **0%**。  
前端 `renderTrajectory` 的軌跡條寬度 = `item.current_apr * 100 = 0`。

### 問題 B：`POLY_MAINLINE_SEQUENCE` 不含 Chap2 family 代碼

`updateMainlineProgressBox` 使用 `POLY_MAINLINE_SEQUENCE = ["F1", "F2", "F5", "F11", "F9", "F10"]`（多項式主線），  
Chap2 的 `target_family_id` 為 `B4C2_SYN_01` 至 `B4C2_SYN_10`，全部不在序列中。

`currentIndexRaw === -1` → `completedLike === false` → 訊息為：
```
📍 學習進度：推估中（0 / 6）
```
此訊息**不含百分比數字** → `updateNavProgressBarFromText` 正則 `(\d+(?:\.\d+)?)\s*%` 無法匹配 → **進度條寬度 0%**。

### 問題 C：缺少 session-local 計數器欄位

前端無法取得：
- `completed_steps`、`total_steps`、`progress_percent`
- `session_correct_count`、`session_attempt_count`、`session_correct_rate`
- `display_mastery_percent`
- `trajectory_points`
- `next_skill_id`、`next_problem_type_id`

---

## 3. Files Changed

| 檔案 | 變更類型 | 說明 |
|------|---------|------|
| `core/vocational_math_b4/services/b4_chap2_chapter_mode.py` | 修改 | 加入 `_compute_display_apr`、`_build_trajectory_points`；更新 `build_b4_chap2_chapter_response` 計算並回傳 UI state 欄位；更新 `build_b4_chap2_chapter_runtime_store_entry` 持久化計數器 |
| `templates/adaptive_practice_v2.html` | 修改 | 新增 `isB4Chapter2Mode` branch in `updateMainlineProgressBox`；在 `renderQuestion` 儲存 Chap2 session-local state |
| `tests/test_b4_chap2_phase6n_adaptive_practice_chapter_mode_integration.py` | 修改 | 新增 `TestChap2UIStateContract` class（17 tests） |

---

## 4. Chap1 Payload Pattern Reused

| Chap1 pattern | Chap2 mapping |
|---------------|---------------|
| `current_apr` (0-1 real mastery) | `current_apr` = display-only APR formula（不寫 DB） |
| `ppo_strategy` | 固定 `1`（無 PPO routing 邏輯） |
| `frustration_index` | 固定 `0` |
| `demo_route_msg` 含 `%` | Chap2 訊息含「掌握度 X%」→ `updateNavProgressBarFromText` 正常讀取 |
| `state.history` push by `renderQuestion` | 沿用，但需 `current_apr > 0` 才有視覺效果 |

---

## 5. Chap2 UI State Payload Summary

### `build_b4_chap2_chapter_response` 新增欄位

| 欄位 | 說明 |
|------|------|
| `current_apr` | `_compute_display_apr(step_index, correct_count, attempt_count)` 計算，不寫 DB |
| `completed_steps` | 本次診斷已送答題數（= `attempt_count`） |
| `total_steps` | 固定 10 |
| `progress_percent` | `step_index / 10 * 100`（%） |
| `session_correct_count` | 累計答對數 |
| `session_attempt_count` | 累計送答數 |
| `session_correct_rate` | `correct / max(1, attempt)` |
| `display_mastery_percent` | `round(current_apr * 100)`，display-only |
| `current_stage` / `current_stage_label` | 當前 stage id / label |
| `current_skill_id` / `current_problem_type_id` | 當前題目 skill/type |
| `next_skill_id` / `next_problem_type_id` | 下一步 skill/type |
| `trajectory_points` | 已答步驟的 trajectory 列表（session-local） |

### `_compute_display_apr` 公式

```
display_apr = 0.5 × (step_index / total_steps)
            + 0.5 × (correct_count / max(1, attempt_count))
```

- `step_index / total_steps`：進度比（走了幾題）
- `correct_count / attempt_count`：正確率
- 不寫 DB，不影響正式 mastery / APR / fail_streak

### Trajectory point 結構

```json
{
  "step_index": 2,
  "stage": "stage2",
  "skill_id": "vh_數學B4_ProbabilityDefinition",
  "problem_type_id": "classical_probability_fraction",
  "answered": true,
  "is_correct": true,
  "display_apr": 0.55,
  "progress_percent": 30.0,
  "display_mastery_percent": 55
}
```

### `build_b4_chap2_chapter_runtime_store_entry` 新增持久化欄位

```python
"session_correct_count": int(...),
"session_attempt_count": int(...),
"chap2_trajectory_history": list(...),
```
確保跨 request 累計計數器不遺失。

---

## 6. Frontend Mapping Summary

### `updateMainlineProgressBox` — Chap2 branch

```javascript
if (isB4Chapter2Mode) {
  const totalSteps = Number(state.chap2TotalSteps || 10);
  const currentStep = Number(state.stepNumber || 0);
  const masteryPct = Number(state.chap2DisplayMasteryPercent || 0);
  const stageName = String(state.chap2StageLabel || "待判定");
  const progressPct = (currentStep / totalSteps * 100).toFixed(1);
  let msg = `📍 診斷進度：${progressPct}%（${currentStep} / ${totalSteps} 題）`;
  msg += `\n\n目前位置：${stageName}`;
  msg += `\n掌握度：${masteryPct}%`;
  setTextWithFlash(boxId, msg);
  updateNavProgressBarFromText(msg);  // ← 可正確讀取 "XX.X%" 更新進度條
  return;
}
```

### `renderQuestion` — Chap2 state 儲存

```javascript
if (isB4Chapter2Mode) {
  state.chap2TotalSteps = Number(response.total_steps || 10);
  state.chap2CompletedSteps = Number(response.completed_steps || 0);
  state.chap2StageLabel = String(response.current_stage_label || ...);
  state.chap2NextSkillId = String(response.next_skill_id || "");
  state.chap2NextProblemTypeId = String(response.next_problem_type_id || "");
  state.chap2DisplayMasteryPercent = Number(response.display_mastery_percent || 0);
  state.chap2CorrectCount = Number(response.session_correct_count || 0);
  state.chap2AttemptCount = Number(response.session_attempt_count || 0);
}
```

### APR 環（`current_apr`）

`updateOverview` 直接讀 `response.current_apr`（0–1）。  
Chap2 現在回傳真實 display APR → APR 環隨答題更新。

### 動態精熟軌跡圖（`renderTrajectory`）

`renderQuestion` 在 line 2255 push `state.history`:
```javascript
state.history.push({ step_number, current_apr, ppo_strategy, ... });
```
現在 `current_apr > 0` → 軌跡條寬度 `Math.max(4, Math.round(item.current_apr * 100))` 正確顯示。

---

## 7. Tests Run

| 測試集 | 數量 | 結果 |
|--------|------|------|
| `TestChap2UIStateContract`（新增 Phase 6N-S） | 17 | ✅ 全部通過 |
| `TestChap2ChapterUrlPayload` / `TestChap2ChapterResolver` / ... | 44 | ✅ 全部通過 |
| Phase 6I Audit Logging | 4 | ✅ |
| Phase 6G-0 Skill Availability | 30 | ✅ |
| Phase 6N-R Dashboard Link | 22 | ✅ |
| Phase 6K Remaining Skill Coverage | ~120 | ✅ |
| Phase 6C1 / 6C2 / 6D / 6E / 6F | ~498 | ✅ |

---

## 8. Regression Result

累計通過：**1017 tests passed，0 failed**

---

## 9. Manual Smoke Checklist

- [ ] 開啟 `/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=2&learning_mode=teaching&practice_kind=unit_practice`
- [ ] 按「開始診斷」→ 第一題正確出現
- [ ] 送出正確答案後：
  - [ ] APR 環（掌握度圓環）從 0% 跳到 > 0%
  - [ ] `本單元學習導航` 進度條從 0% 更新
  - [ ] 軌跡圖（trajectoryBox）出現第一條，寬度 > 4%
  - [ ] step number 從 0 → 1
  - [ ] 掌握度百分比數字更新
- [ ] 送出錯誤答案：
  - [ ] APR 環更新（較低但仍有進度比例）
  - [ ] session_correct_rate 反映錯誤
- [ ] 答完全部 10 題後：
  - [ ] 顯示完成訊息
  - [ ] APR 環顯示最終診斷掌握度
- [ ] Chap1 chapter mode 不破壞：`/adaptive_practice?...&chapter_id=1` 正常
- [ ] Teacher audit visibility log 不受影響

---

## 10. Final Confirmation

| 項目 | 確認 |
|------|------|
| 是否只修 Chap2 adaptive UI state | ✅ 是 |
| 是否修改正式 mastery | ✅ 否 |
| 是否修改 APR policy | ✅ 否 |
| 是否修改 fail_streak policy | ✅ 否 |
| 是否觸發 remediation | ✅ 否 |
| 是否修改 DB schema | ✅ 否 |
| 是否新增題型 | ✅ 否 |
| 是否修改 generators / validators | ✅ 否 |
| 是否破壞 Chap1 chapter mode | ✅ 否 |
| 是否破壞 /practice | ✅ 否 |
| 是否破壞 teacher audit visibility | ✅ 否 |
| 是否啟動下一 phase | ✅ 否 |

**完成狀態：READY_FOR_MANUAL_SMOKE**
