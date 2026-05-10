# B4 Phase 6N — Chap2 Adaptive Practice Chapter Mode Integration
## Runtime-Ready Summary

**Phase:** 6N  
**Date:** 2026-05-10  
**Status:** ✅ READY_FOR_MANUAL_SMOKE  
**Scope:** B4 Chapter 2 (機率) — Chapter Mode Adaptive Practice Integration

---

## 1. Scope and Guardrails

### 目標
讓以下 URL 可正常運作：
```
/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=2&learning_mode=teaching&practice_kind=unit_practice
```

按「開始診斷」後進入 Chap2 deterministic diagnostic flow：
- 產生第一題 ✅
- 可送答案 ✅
- 可批改 ✅
- 可進下一題 ✅
- 可寫入 visibility audit log ✅
- 不改正式 mastery / APR / remediation policy ✅

### 硬性限制（均遵守）
| 項目 | 狀態 |
|------|------|
| 不修改 adaptive scoring / mastery / APR / remediation | ✅ 遵守 |
| 不啟動 PPO / AKT 正式 scoring 寫入 | ✅ 遵守 |
| 不新增題型 | ✅ 遵守 |
| 不修改 generators | ✅ 遵守 |
| 不修改 validators | ✅ 遵守 |
| 不修改 DB schema | ✅ 遵守 |
| 不破壞 Chap1 chapter mode | ✅ 遵守 |
| 不破壞 /practice | ✅ 遵守 |
| 不破壞 teacher audit visibility | ✅ 遵守 |
| 不啟動下一章 | ✅ 遵守 |
| reserved listing problem_types 保持 blocked | ✅ 遵守 |

---

## 2. Root Cause of Chap2 Start Diagnosis No-Op

Chap2 之前無法從 `/adaptive_practice?...chapter_id=2...` 啟動，根本原因如下：

1. **`_resolve_b4_chapter_adaptive_entry`** (practice.py) 的 chapter detection 只有 `chapter_id == "1"` 分支，chapter_id=2 直接 return `({}, False)` → template 注入 `unit_skill_ids=[]`
2. **`adaptive_submit_and_get_next`** (adaptive_api.py) 的 `is_b4_chapter_entry` 判斷只有 `b4_chapter1_hit`，chapter_id=2 進入 `submit_and_get_next(session_engine)` → session engine 找不到 Chap2 catalog entries → `ValueError: No catalog entries available`
3. **session_engine.py** 的 `filter_catalog_entries_for_b4_chapter1_deterministic_adaptive` 會把所有不在 `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST` 的 B4 技能過濾掉，Chap2 skills 全部被擋掉
4. Template JS 的 `isB4Chapter1Mode` 只識別 `chapter_id === "1"`，無 Chap2 相對應邏輯

---

## 3. Files Changed

### 新增
| 檔案 | 說明 |
|------|------|
| `core/vocational_math_b4/services/b4_chap2_chapter_mode.py` | Chap2 chapter mode 輕量級 handler：診斷計劃、resolver、answer checker、audit 寫入 |
| `tests/test_b4_chap2_phase6n_adaptive_practice_chapter_mode_integration.py` | 44 項整合測試 |
| `reports/b4_generator_planning/b4_phase6n_chap2_adaptive_practice_chapter_mode_runtime_ready_summary.md` | 本報告 |

### 修改
| 檔案 | 修改內容 |
|------|----------|
| `core/routes/practice.py` | 1) 匯入 `B4_CHAP2_CHAPTER_SKILL_IDS` / `B4_CHAP2_CHAPTER_DIAGNOSTIC_TOTAL_STEPS`；2) `_resolve_b4_chapter_adaptive_entry` 加入 chapter_id="2" 分支 |
| `core/routes/adaptive_api.py` | 1) 匯入 `build_b4_chap2_chapter_response` / `build_b4_chap2_chapter_runtime_store_entry`；2) `adaptive_submit_and_get_next` 加入 `is_b4_chapter2_entry` 分支 |
| `templates/adaptive_practice_v2.html` | 加入 `isB4Chapter2Mode` JS 變數；更新 bootstrap click handler；更新 `runtimeMode` 判斷 |

### 未修改（故意）
- `core/adaptive/session_engine.py` — 不需改動
- `core/vocational_math_b4/adaptive/b4_chapter2_phase6c1_allowlist.py` — 現有 allowlist 沿用
- `core/vocational_math_b4/services/question_router.py` — 沿用 `generate_for_chap2_skill`
- `core/vocational_math_b4/services/b4_chap2_visibility_audit.py` — 沿用 audit 函式
- 所有 generators / validators

---

## 4. Chap1 Pattern Reused

| Chap1 設施 | Chap2 沿用方式 |
|-----------|---------------|
| `_resolve_b4_chapter_adaptive_entry` | 同一函式，加 elif 分支 |
| `adaptive_submit_and_get_next` 端點 | 同一端點，加 is_b4_chapter2_entry 分支 |
| Runtime store (`adaptive_runtime` session) | 同一 store 結構，加 chap2 extra fields |
| `_response_for_frontend` (隱藏 correct_answer) | 同一函式，Chap2 response 通過同一 sanitizer |
| `isB4Chapter1Mode` JS 模式 | 加入平行的 `isB4Chapter2Mode` |
| Bootstrap click handler pattern | 加 `if (isB4Chapter2Mode)` 分支 |

---

## 5. Chap2 Chapter Resolver Summary

URL 參數 → resolver 解析 → skill bundle：

```
mode=chapter + curriculum=vocational + volume=數學B4 + chapter_id=2
→ _resolve_b4_chapter_adaptive_entry returns:
  {
    "entry_mode": "chapter",
    "unit_name": "單元練習：2 機率",
    "unit_skill_ids": [10 Chap2 skills in curriculum order],
    "bootstrap_unit_skill_ids": [same],
    "starter_skill_id": "vh_數學B4_BasicConceptsOfSets",
    "chapter_id": "2",
    "b4_chap2_chapter_mode": True,
    "diagnostic_total_steps": 10,
  }
```

**10 個 Chap2 skills（課本順序）：**
1. `vh_數學B4_BasicConceptsOfSets`
2. `vh_數學B4_SampleSpaceAndEvents`
3. `vh_數學B4_ProbabilityDefinition`
4. `vh_數學B4_ProbabilityProperties`
5. `vh_數學B4_ProbabilityOperations`
6. `vh_數學B4_ConditionalProbability`
7. `vh_數學B4_IndependentEvents`
8. `vh_數學B4_MathematicalExpectationDefinition`
9. `vh_數學B4_ApplicationsOfExpectation`
10. `vh_數學B4_MathematicalExpectation`

---

## 6. Diagnostic Sequence Policy

**策略：** Deterministic stage-balanced 10 題診斷

| Step | Stage | Skill | Problem Type | Answer Type |
|------|-------|-------|--------------|-------------|
| 0 | Stage 1：集合與樣本空間 | BasicConceptsOfSets | set_operation_count | integer |
| 1 | Stage 1：集合與樣本空間 | SampleSpaceAndEvents | sample_space_count_numeric | integer |
| 2 | Stage 2：基本機率與運算 | ProbabilityDefinition | classical_probability_fraction | rational_fraction |
| 3 | Stage 2：基本機率與運算 | ProbabilityProperties | complement_probability | rational_fraction |
| 4 | Stage 2：基本機率與運算 | ProbabilityOperations | event_operation_probability | rational_fraction |
| 5 | Stage 3：條件機率與獨立事件 | ConditionalProbability | conditional_probability_basic | rational_fraction |
| 6 | Stage 3：條件機率與獨立事件 | IndependentEvents | independent_joint_probability | rational_fraction |
| 7 | Stage 4：數學期望值 | MathematicalExpectationDefinition | expectation_discrete_basic | expected_value |
| 8 | Stage 4：數學期望值 | ApplicationsOfExpectation | expectation_word_problem_profit_fairness | expected_value |
| 9 | Stage 4：數學期望值 | MathematicalExpectation | expectation_assessment_numeric | expected_value |

**選題機制：** 完全 deterministic，seed = `SHA256(session_id :: step_index)[:8]`，確保每個 session 可重現。

**保留禁止題型（從未出現）：**
- `sample_space_listing`
- `event_set_listing`
- `subset_listing`
- `tree_diagram_listing`

---

## 7. Runtime Integration Summary

### Bootstrap 流程（step=0）
1. Frontend → `POST /api/adaptive/submit_and_get_next` (step_number=0, chapter_id=2)
2. `adaptive_submit_and_get_next` 識別 `is_b4_chapter2_entry=True`
3. 呼叫 `build_b4_chap2_chapter_response(payload, runtime={})`
4. 建立新 session_id，從 plan[0] 產生 BasicConceptsOfSets 題目
5. 回傳 question payload → frontend `renderQuestion(data)`

### 答題流程（step=N）
1. Frontend → `POST /api/adaptive/submit_and_get_next` (session_id, step_number=N, user_answer)
2. `is_b4_chapter2_entry=True` → `build_b4_chap2_chapter_response(payload, runtime=runtime_store[session_id])`
3. `_check_answer_for_plan_step` 使用對應 checker（integer/rational/expected_value）
4. `_maybe_write_audit_log` 寫入 B4Chap2VisibilityAuditLog
5. 從 plan[N+1] 產生下一題，回傳 grading_analysis + next question

### 完成流程（step=10）
1. 所有 10 步完成後回傳 `completed=True, unit_completed=True`
2. Frontend 顯示診斷完成畫面

---

## 8. Visibility Audit Behavior

- **觸發時機：** 每次 `user_answer` 提交後（非 bootstrap）
- **呼叫函式：** `_maybe_write_audit_log` → `persist_b4_chap2_deterministic_answer_event`
- **記錄欄位：** skill_id, problem_type_id, answer_type, expected_answer, user_answer, is_correct, checker_name
- **不影響：** mastery, APR, remediation policy
- **靜默錯誤處理：** audit 失敗不影響主流程

---

## 9. Tests Run

| 測試文件 | 通過數 |
|---------|--------|
| `test_b4_chap2_phase6n_adaptive_practice_chapter_mode_integration.py` | 44 |
| `test_b4_chap2_phase6k_remaining_skill_coverage.py` | (Phase 6K regression) |
| `test_b4_chap2_phase6c1_probability_basic.py` | (Phase 6C-1 regression) |
| `test_b4_chap2_phase6c2_probability_second_batch.py` | (Phase 6C-2 regression) |
| `test_b4_chap2_phase6g0_skill_availability_ux.py` | (Phase 6G-0 regression) |
| `test_b4_chap2_phase6i_visibility_audit_logging.py` | (Phase 6I regression) |
| `test_b4_chap2_phase6f_expected_value.py` | (Phase 6F regression) |
| `test_b4_chap2_phase6c1r_practice_route_integration.py` | (route regression) |
| `test_b4_chap2_phase6c1r2_practice_next_question_integration.py` | (route regression) |
| `test_b4_chap2_phase6c2r_practice_smoke_regression.py` | (regression) |
| `test_b4_chap2_phase6d_conditional_probability.py` | (Phase 6D regression) |
| `test_b4_chap2_phase6e_independent_events.py` | (Phase 6E regression) |

**合計（三個批次）：** 359 + 94 + 481 + 44 = **978 passed, 0 failed**

---

## 10. Regression Result

| 批次 | 測試數 | 結果 |
|------|--------|------|
| Phase 6K + 6C-1 + 6C-2 | 359 | ✅ 全部通過 |
| Phase 6G-0 + 6I + 6F | 94 | ✅ 全部通過 |
| Route integration (6C-1R, 6C-1R2, 6C-2R, 6D, 6E) | 481 | ✅ 全部通過 |
| Phase 6N new tests | 44 | ✅ 全部通過 |

---

## 11. Manual Smoke Checklist

### URL Entry
- [ ] 瀏覽器開啟 `/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=2&learning_mode=teaching&practice_kind=unit_practice`
- [ ] 頁面標題顯示「單元練習：2 機率」
- [ ] 「開始診斷」按鈕可見

### Bootstrap Flow
- [ ] 按「開始診斷」 → 不出現 silent no-op
- [ ] 第一題出現（BasicConceptsOfSets, set_operation_count）
- [ ] 題目有選項（multiple_choice=True）
- [ ] JS console 無 uncaught error
- [ ] 無「Phase 6C-1」或「No module named skills」等錯誤文字外洩

### Answer Submission
- [ ] 輸入任意答案 → 批改結果出現（正確/錯誤）
- [ ] 進入下一題（stage 前進）
- [ ] 共 10 題後出現「診斷完成」訊息

### Stage Progression
- [ ] Step 0-1：stage_1 — 集合與樣本空間
- [ ] Step 2-4：stage_2 — 基本機率與運算
- [ ] Step 5-6：stage_3 — 條件機率與獨立事件
- [ ] Step 7-9：stage_4 — 數學期望值

### Chap1 Regression
- [ ] `/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=1&...` 仍正常運作
- [ ] Chap1「開始診斷」不受 Chap2 修改影響

### /practice Regression
- [ ] `/practice?skill=vh_數學B4_ProbabilityDefinition&problem_type=classical_probability_fraction` 仍正常
- [ ] teacher audit log 頁面仍可正常顯示

---

## 12. Known Limitations

1. **Chap2 chapter mode 不做正式 mastery/APR 更新** — 本輪設計決策，符合 Phase 6N 範圍
2. **診斷只有固定 10 題一種序列** — 無動態 PPO 決策；後續可由 Phase 6L 的 adaptive scoring policy 接替
3. **答錯不重試** — 診斷繼續前進，錯誤記錄在 audit log
4. **session_engine.py 未改動** — Chap2 繞過 session engine 使用獨立 handler；如需完整 PPO 路由須另立 phase
5. **teacher audit `/b4_chap2_teacher_audit`** — 寫入機制相同（`persist_b4_chap2_deterministic_answer_event`），但 source_phase 標記為 `b4_chap2_phase6i`（沿用現有值）

---

## 13. Final Confirmation

| 問題 | 答案 |
|------|------|
| 是否讓 Chap2 chapter mode URL 可開始診斷 | ✅ 是 |
| 是否沿用 Chap1 chapter mode pattern | ✅ 是（同端點、同 runtime store、同 template） |
| 是否新增題型 | ❌ 否 |
| 是否修改 adaptive scoring / mastery / APR / remediation | ❌ 否 |
| 是否修改 DB schema | ❌ 否 |
| 是否破壞 Chap1 chapter mode | ❌ 否（測試確認） |
| 是否破壞 /practice | ❌ 否（481 route tests passed） |
| 是否保留 reserved listing blocked | ✅ 是（plan 不含 sample_space_listing 等 4 種） |
| 是否啟動下一 phase | ❌ 否 |

---

**完成狀態：READY_FOR_MANUAL_SMOKE**
