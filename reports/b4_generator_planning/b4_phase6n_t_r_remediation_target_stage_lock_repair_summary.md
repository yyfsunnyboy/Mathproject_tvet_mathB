# Phase 6N-T-R：Chap2 Remediation Target Stage Lock Repair

## Summary

| 欄位 | 值 |
|------|----|
| Phase | 6N-T-R |
| 狀態 | READY_FOR_MANUAL_SMOKE |
| 關聯 Phase | 6N-T（Session-local Remediation）、6N-S（UI State）、6N（Chapter Mode） |
| 變更檔案數 | 2 |
| 新增測試數 | 13（TestFailedStageLock） |
| 總測試通過 | 1065 passed（regression 累計） |

---

## 1. Failure Symptom（手動測試失敗現象）

在 Stage 2（基本機率與運算）連續答錯後：

- 補救題可能出現期望值問題（Stage 4）
- 前端顯示「目前補救 expectation_from_distribution」，語境與機率完全不符
- 學生看到「機率連錯，卻要做期望值補救」

---

## 2. Root Cause（根本原因）

Phase 6N-T 的補救觸發路徑正確，但在持久化 `remediation_stage` 時存在設計缺陷：

```python
# 舊寫法（有潛在問題）
"remediation_stage": str(
    response.get("remediation_stage_id") or response.get("current_stage") or ""
) if in_remediation else "",
```

`current_stage` 在 remediation bridge response 中代表「補救用的 bridge stage」，在 mainline response 中代表「下一道主線題的 stage」。當 fallback 到 `current_stage` 時，若 bridge response 的 `current_stage` 與 mainline 的 `current_stage` 混淆，就可能用錯 stage 來選 bridge。

更根本的問題：**沒有明確的 `failed_stage` 欄位**，補救觸發時的目標 stage 只靠 `remediation_stage` 間接傳遞，沒有明確保存「是哪一道主線題觸發了補救」。

---

## 3. Files Changed

| 檔案 | 變更類型 | 說明 |
|------|---------|------|
| `core/vocational_math_b4/services/b4_chap2_chapter_mode.py` | 修改 | 加入 `failed_stage`, `failed_skill_id`, `failed_problem_type_id` 明確鎖定機制；bridge 選取改用 `bridge_stage_key = failed_stage or remediation_stage`；runtime store 明確儲存三個 failed fields；`remediation_stage` 改用 `remediation_stage_id`（不再 fallback `current_stage`） |
| `tests/test_b4_chap2_phase6n_t_session_local_remediation.py` | 修改 | 新增 `TestFailedStageLock`（13 tests）驗證 stage 隔離 |

---

## 4. Failed-Stage Lock Design

### 觸發時明確保存

```python
if remediation_trigger_condition:
    in_remediation = True
    remediation_stage = current_stage_id      # 同上，保留相容
    # Phase 6N-T-R: 明確鎖定 failed stage
    failed_stage = current_stage_id           # NEVER 由 current_step 覆蓋
    failed_skill_id = last_plan_step.get("skill_id", "")
    failed_problem_type_id = last_plan_step.get("problem_type_id", "")
```

### Bridge 選取改用 `failed_stage`

```python
# 舊：可能用到 current_stage（advanced step 的 stage）
bridge = _CHAP2_REMEDIATION_BRIDGES.get(remediation_stage, {})

# 新：明確用 failed_stage（觸發時鎖定的 stage）
bridge_stage_key = failed_stage or remediation_stage
bridge = _CHAP2_REMEDIATION_BRIDGES.get(bridge_stage_key, {})
```

### Runtime Store 改用 `remediation_stage_id`（不再 fallback `current_stage`）

```python
# 舊：
"remediation_stage": str(response.get("remediation_stage_id") or response.get("current_stage") or "")

# 新：
"remediation_stage": str(response.get("remediation_stage_id") or "") if in_remediation else "",
```

### Response 新增明確欄位

| 欄位 | 說明 |
|------|------|
| `failed_stage` | 觸發補救時的主線 stage id，不受後續 step 推進影響 |
| `failed_skill_id` | 觸發補救時的主線 skill_id |
| `failed_problem_type_id` | 觸發補救時的主線 problem_type_id |

---

## 5. Remediation Target Mapping（保證 Stage 隔離）

| 失敗 Stage | Bridge | 絕不使用 |
|-----------|--------|---------|
| stage_1_sets_and_sample_space | `inclusion_exclusion_count` | 非集合相關 |
| stage_2_basic_probability | `dice_coin_probability_count` | **絕不用 expectation** |
| stage_3_conditional_independent | `without_replacement_conditional_probability` | **絕不用 expectation** |
| stage_4_expectation | `expectation_from_distribution` | 才允許期望值 |

---

## 6. Tests Run

| 測試集 | 數量 | 結果 |
|--------|------|------|
| `TestFailedStageLock`（Stage 2 → 非 expectation, Stage 3 → 非 expectation, Stage 4 → expectation, failed_stage 持久化, runtime 保留, trajectory）| 13 | ✅ 全部通過 |
| `TestRemediationTrigger` + `TestRemediationResponseContract` + `TestReturnToMainline`（6N-T 原有） | 22 | ✅ |
| Phase 6N（chapter mode integration） | 61 | ✅ |
| Phase 6I（audit logging） | 4 | ✅ |
| Phase 6G-0（skill availability） | 30 | ✅ |
| Phase 6K + 6C1/C2/D/E/F（generators） | 662 | ✅ |

---

## 7. Regression Result

累計通過：**1065 tests passed，0 failed**

---

## 8. Manual Smoke Checklist

- [ ] 在 Stage 2（步驟 2~4：ProbabilityDefinition / ProbabilityProperties / ProbabilityOperations）連續答錯 2 題
  - [ ] 補救題為機率相關（dice_coin_probability_count），不是期望值
  - [ ] response 含 `failed_stage: "stage_2_basic_probability"`
  - [ ] 前端顯示「目前針對基本機率與運算進行補救」
- [ ] 在 Stage 3（步驟 5~6：ConditionalProbability / IndependentEvents）連續答錯 2 題
  - [ ] 補救題為條件機率（without_replacement_conditional_probability），不是期望值
  - [ ] response 含 `failed_stage: "stage_3_conditional_independent"`
- [ ] 在 Stage 4（步驟 7~9：期望值相關）連續答錯 2 題
  - [ ] 補救題為 `expectation_from_distribution`（Stage 4 才允許用期望值補救）
- [ ] 補救答對 → `return_ready=True`，返回主線
- [ ] Chap1 chapter mode 不受影響
- [ ] Teacher audit log 正常記錄補救題

---

## 9. Final Confirmation

| 項目 | 確認 |
|------|------|
| 是否只修 Chap2 remediation target stage lock | ✅ 是 |
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
