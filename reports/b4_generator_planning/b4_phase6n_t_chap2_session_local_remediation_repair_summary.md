# Phase 6N-T：Chap2 Adaptive Practice Session-local Remediation Integration

## Summary

| 欄位 | 值 |
|------|----|
| Phase | 6N-T |
| 狀態 | READY_FOR_MANUAL_SMOKE |
| 關聯 Phase | 6N-S（UI State Contract）、6N（Chapter Mode）、6N-R（Dashboard Link） |
| 變更檔案數 | 3 |
| 新測試數 | 35（test_b4_chap2_phase6n_t_session_local_remediation.py） |
| 總測試通過 | 1052 passed（regression 累計） |

---

## 1. Failure Symptom（手動測試失敗現象）

Chap2 chapter mode adaptive practice 頁面：

- 學生連續答錯時，系統直接推進到下一道主線題
- **不會進入補救 / 近側發展區分支**
- 診斷流程對各種學習狀況均無分支，缺乏真實自適應能力
- APR 環可正確下降，但沒有對應的補救行為回應

---

## 2. Root Cause（根本原因）

Phase 6N 的 `build_b4_chap2_chapter_response` 僅實作**固定線性序列**：
- 每次答題後，`step_index = last_plan_step_index + 1`，直接推進主線
- 無 `stage_fail_streak` 追蹤機制
- 無 remediation trigger 條件
- 無 bridge question 路由

Chap1 的補救邏輯位於正式 `session_engine.py`（PPO policy），屬正式 mastery/APR 更新機制，無法在不改 engine 的情況下直接複製。因此 Phase 6N-T 在 Chap2 lightweight handler 內實作獨立的 **session-local remediation**。

---

## 3. Chap1 Pattern Reused

| Chap1 概念 | Phase 6N-T 對應實作 |
|-----------|---------------------|
| `fail_streak` 累計 | `stage_fail_streak` dict，per-stage 計數 |
| remediation trigger | `stage_fail_streak[stage] >= 2` |
| bridge question | `_CHAP2_REMEDIATION_BRIDGES` per-stage 映射 |
| `return_ready` flag | 補救答對後 `return_ready=True` |
| `has_returned_to_main` | 返回主線後設 True，`state.hasReturnedToMain` |
| `in_remediation` response field | 沿用 Chap1 `_response_for_frontend` 映射的 `in_remediation` key |
| `display_mode = "remediation"` | Chap2 branch 讀取此值更新 UI |

---

## 4. Files Changed

| 檔案 | 變更類型 | 說明 |
|------|---------|------|
| `core/vocational_math_b4/services/b4_chap2_chapter_mode.py` | 修改 | 新增 `_CHAP2_REMEDIATION_BRIDGES`、`_CHAP2_FAIL_STREAK_THRESHOLD`、`_derive_remediation_seed`、`get_chap2_remediation_bridge`；重寫 `build_b4_chap2_chapter_response` 補救分支；更新 `build_b4_chap2_chapter_runtime_store_entry` 持久化補救狀態 |
| `templates/adaptive_practice_v2.html` | 修改 | `updateMainlineProgressBox` Chap2 branch 加入 remediation 顯示；`renderQuestion` 加入 `state.chap2InRemediation`、`state.chap2ReturnReady`、`state.chap2HasReturnedToMain`、`state.isRemediationActive`、`state.displayMode` 更新 |
| `tests/test_b4_chap2_phase6n_t_session_local_remediation.py` | 新增 | 35 tests（見下方） |

---

## 5. Session-local Remediation Policy

### 觸發條件

```
stage_fail_streak[stage_id] >= 2
AND is_answer_submission
AND NOT in_remediation
AND bridge available for this stage
AND NOT all mainline steps complete
```

### 補救流程

```
1. in_remediation = True
2. remediation_stage = current_stage_id
3. remediation_attempt = 0
4. resume_step_index = mainline_step_index（待返回的主線步驟）
5. 呼叫 bridge 的 generate_for_chap2_skill
6. 若補救答對：
   → return_ready = True
   → in_remediation = False
   → has_returned_to_main = True
   → stage_fail_streak[stage] = 0（重置）
   → 返回 mainline step resume_step_index
7. 若補救答錯：
   → remediation_attempt += 1
   → 若 attempt >= _CHAP2_MAX_REMEDIATION_ATTEMPTS (=2)：
     強制返回主線（has_returned_to_main=True）
   → 否則繼續補救（同 bridge，不同 seed）
```

**保證無限迴圈防止：`_CHAP2_MAX_REMEDIATION_ATTEMPTS = 2`**

### Remediation Bridge 映射

| Stage | Bridge skill_id | Bridge problem_type_id |
|-------|----------------|----------------------|
| stage_1_sets_and_sample_space | vh_數學B4_BasicConceptsOfSets | inclusion_exclusion_count |
| stage_2_basic_probability | vh_數學B4_ProbabilityDefinition | dice_coin_probability_count |
| stage_3_conditional_independent | vh_數學B4_ConditionalProbability | without_replacement_conditional_probability |
| stage_4_expectation | vh_數學B4_MathematicalExpectationDefinition | expectation_from_distribution |

禁止的 reserved listing 不在任何 bridge 中：`sample_space_listing`、`event_set_listing`、`subset_listing`、`tree_diagram_listing` 均排除。

---

## 6. UI State Payload Summary

### 補救時 response 新增欄位

| 欄位 | 值 |
|------|----|
| `in_remediation` | `True` |
| `return_ready` | `False`（補救中） / `True`（補救成功後） |
| `has_returned_to_main` | `False`（補救中） / `True`（返回後） |
| `remediation_reason` | 例："連續答錯 2 題（基本機率與運算），進入近側發展區補救" |
| `remediation_stage_id` | 補救中的 stage id |
| `remediation_attempt` | 當前補救嘗試次數（0-indexed） |
| `stage_fail_streak` | dict：{stage_id: consecutive_wrong_count} |
| `session_local_fail_streak` | 當前 stage 的連續錯誤數 |
| `current_strategy` | "近側發展區補救" / "主線診斷" / "返回主線" |
| `display_mode` | "remediation" / "mainline" |
| `ppo_strategy` | `2`（補救中） / `1`（主線） |

### 前端狀態映射（`renderQuestion` Chap2 branch）

```javascript
state.chap2InRemediation = Boolean(response.in_remediation);
state.chap2ReturnReady = Boolean(response.return_ready);
state.chap2HasReturnedToMain = Boolean(response.has_returned_to_main);
state.chap2LocalFailStreak = Number(response.session_local_fail_streak);
state.chap2CurrentStrategy = String(response.current_strategy);
state.isRemediationActive = response.in_remediation;
state.displayMode = response.in_remediation ? "remediation" : "mainline";
```

### 學習導航顯示（`updateMainlineProgressBox` Chap2 branch）

- **補救中：** `⚠ 近側發展區補救中：{stageName}` + 連續答錯數
- **補救完成返回：** `✅ 補救完成，返回主線：{stageName}`
- **主線中：** `📍 診斷進度：X%`（同 Phase 6N-S）

---

## 7. Tests Run

| 測試集 | 數量 | 結果 |
|--------|------|------|
| `TestRemediationTrigger`（2 wrong→trigger, 1 wrong→no trigger, streak reset） | 3 | ✅ |
| `TestRemediationResponseContract`（in_remediation, strategy, reason, bridge, ppo） | 11 | ✅ |
| `TestRemediationBridgeMapping`（all stages, not reserved, same stage, router） | 7 | ✅ |
| `TestReturnToMainline`（correct→return_ready, forced return after max） | 5 | ✅ |
| `TestRemediationTrajectory`（bridge entry, mainline not marked） | 2 | ✅ |
| `TestNoFormalMasteryWritten`（no mastery fields, display only） | 2 | ✅ |
| `TestRegressionNotBroken`（allowlist, audit, router, plan, all-correct flow） | 5 | ✅ |

---

## 8. Regression Result

累計通過：**1052 tests passed，0 failed**

| 測試群組 | 通過 |
|---------|------|
| Phase 6N-T（新增） | 35 |
| Phase 6N（integration） | 61 |
| Phase 6I（audit logging） | 4 |
| Phase 6G-0（skill availability） | 30 |
| Phase 6N-R（dashboard link） | 22 |
| Phase 6K remaining skill coverage | ~120 |
| Phase 6C1/C2/D/E/F/K（generators） | 739 |

---

## 9. Manual Smoke Checklist

- [ ] 開啟 `/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=2&learning_mode=teaching&practice_kind=unit_practice`
- [ ] 按「開始診斷」→ 第一題出現（Stage 1）
- [ ] 連續答錯 2 題：
  - [ ] 學習導航顯示「⚠ 近側發展區補救中：集合與樣本空間」
  - [ ] 題目變成 bridge problem（`inclusion_exclusion_count`）
  - [ ] `current_strategy` = "近側發展區補救"
  - [ ] APR 環降低但不歸零
- [ ] 補救題答對：
  - [ ] 顯示「✅ 補救完成，返回主線」
  - [ ] 下一題回主線
- [ ] 補救題連答錯 2 次：
  - [ ] 強制返回主線（`has_returned_to_main=True`）
  - [ ] 不無限循環
- [ ] Chap1 chapter mode 不受影響
- [ ] Teacher audit visibility log 補救題也有記錄

---

## 10. Final Confirmation

| 項目 | 確認 |
|------|------|
| 是否只修 Chap2 session-local remediation | ✅ 是 |
| 是否修改正式 mastery | ✅ 否 |
| 是否修改 APR / PPO | ✅ 否 |
| 是否修改正式 remediation policy | ✅ 否 |
| 是否新增題型 | ✅ 否 |
| 是否修改 generators / validators | ✅ 否 |
| 是否修改 DB schema | ✅ 否 |
| 是否破壞 Chap1 chapter mode | ✅ 否 |
| 是否破壞 /practice | ✅ 否 |
| 是否破壞 teacher audit visibility | ✅ 否 |
| 是否啟動下一 phase | ✅ 否 |

**完成狀態：READY_FOR_MANUAL_SMOKE**
