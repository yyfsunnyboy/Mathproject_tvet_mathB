# B4 Chapter 2 Phase 6C-2：Second Deterministic Probability Batch Summary

## 0. Scope and Guardrails

本輪為 Phase 6C-2，只新增 2 個 deterministic problem_type：
- `union_intersection_probability`
- `dice_coin_probability_count`

明確聲明：
- ✅ 只修改本輪允許的必要檔案
- ❌ 未修改 database
- ❌ 未修改 coverage matrix
- ❌ 未修改 adaptive scoring / mastery / APR / remediation
- ❌ 未修改 templates
- ❌ 未大改 /practice route
- ❌ 未動 Chap1 allowlist
- ❌ 未啟動 Phase 6D / 6E / 6F
- ❌ 未新增 fake skill generator
- ❌ 未處理 handwriting / free-response 題型
- ❌ 未加入 listing 題型 (sample_space_listing / event_set_listing / subset_listing)
- ❌ 未處理 BasicConceptsOfSets / ConditionalProbability / IndependentEvents
- ❌ 未處理 MathematicalExpectation / expectation 題型
- ❌ 未處理 image-related 題

---

## 1. Files Changed

| 動作 | 檔案 | 說明 |
|---|---|---|
| **修改** | `core/vocational_math_b4/generators/chap2_probability_basic.py` | 追加 2 個 generator 函式（docstring 更新 + EOF 追加） |
| **修改** | `core/vocational_math_b4/adaptive/b4_chapter2_phase6c1_allowlist.py` | 擴展 allowed problem_types frozenset（6C-1 保留，6C-2 追加） |
| **修改** | `core/vocational_math_b4/services/question_router.py` | 擴展 `_CHAP2_PHASE6C1_REGISTRY`（新增 2 個 entry），更新 docstring |
| **修改** | `tests/test_b4_chap2_phase6c1_probability_basic.py` | 修復 3 個因 registry 擴展而失效的既有測試（加 `problem_type_id` pin） |
| **修改** | `tests/test_b4_chap2_phase6c1r_practice_route_integration.py` | 修復 2 個因 registry 擴展而失效的既有測試（加 `problem_type_id` pin） |
| **新增** | `tests/test_b4_chap2_phase6c2_probability_second_batch.py` | Phase 6C-2 新測試（含 6C-1 regression） |
| **新增** | `reports/b4_generator_planning/b4_phase6c2_second_deterministic_probability_summary.md` | 本報告 |

**未修改：**
- `core/routes/practice.py`（6C-1R 的 is_b4_chapter2_phase6c1_deterministic_skill 判斷已包含新 skills）
- `core/vocational_math_b4/domain/b4_validators.py`（checker 完全重用）
- `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`
- 所有 templates / database

---

## 2. Implemented Problem Types

### A. `union_intersection_probability`

| 項目 | 說明 |
|---|---|
| skill_id | `vh_數學B4_ProbabilityProperties` |
| generator | `union_intersection_probability()` in `chap2_probability_basic.py` |
| generator_key | `b4.chap2.union_intersection_probability` |
| answer_type | `rational_fraction` |
| canonical answer | 最簡分數字串，例如 `"3/5"` |
| checker | `check_rational_answer` flexible（重用 6C-1，無修改） |

**Sub-types：**
- `ask_union`：given P(A),P(B),P(A∩B)，求 P(A∪B)
- `ask_intersection`：given P(A∪B),P(A),P(B)，求 P(A∩B)

**數學約束（生成器強制）：**
- 0 ≤ c ≤ min(a,b)（P(A∩B) ≤ P(A), P(A∩B) ≤ P(B)）
- P(A∪B) = (a+b-c)/D ≤ 1
- P(A∪B) ≥ P(A), P(A∪B) ≥ P(B)
- answer ≠ P(A), answer ≠ P(B)（避免平凡情境）

**禁止：** 三事件容斥、條件機率、圖像題、文氏圖

---

### B. `dice_coin_probability_count`

| 項目 | 說明 |
|---|---|
| skill_id | `vh_數學B4_ProbabilityDefinition` |
| generator | `dice_coin_probability_count()` in `chap2_probability_basic.py` |
| generator_key | `b4.chap2.dice_coin_probability_count` |
| answer_type | `rational_fraction` |
| canonical answer | 最簡分數字串，例如 `"1/6"` |
| checker | `check_rational_answer` flexible（重用 6C-1，無修改） |

**三種情境：**
| context | 說明 |
|---|---|
| `single_die_property` | 擲一顆骰子，偶數/奇數/大小於某數 等 9 種條件 |
| `two_dice_sum` | 擲兩顆骰子，點數和為指定目標值 |
| `coin_exact_heads` | 擲 n 枚硬幣（n=2,3,4），恰好 k 次正面 |

**禁止：** image-related、列出樣本空間、條件機率、獨立事件正式題型

---

## 3. Router / Allowlist Changes

### `_CHAP2_PHASE6C1_REGISTRY` 更新

```
vh_數學B4_ProbabilityDefinition:
  [KEPT]  classical_probability_fraction   (6C-1)
  [NEW]   dice_coin_probability_count      (6C-2)

vh_數學B4_ProbabilityProperties:
  [KEPT]  complement_probability            (6C-1)
  [NEW]   union_intersection_probability    (6C-2)

vh_數學B4_SampleSpaceAndEvents:
  [KEPT]  sample_space_count_numeric        (6C-1)
```

### `B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES` 更新

| problem_type | phase |
|---|---|
| `classical_probability_fraction` | 6C-1 kept |
| `complement_probability` | 6C-1 kept |
| `sample_space_count_numeric` | 6C-1 kept |
| `union_intersection_probability` | **6C-2 new** |
| `dice_coin_probability_count` | **6C-2 new** |

Allowlist size: **5** (was 3).

**仍不開放（確認）：**

| skill | status |
|---|---|
| `vh_數學B4_BasicConceptsOfSets` | blocked (not_enabled) |
| `vh_數學B4_ConditionalProbability` | blocked (not_enabled) |
| `vh_數學B4_IndependentEvents` | blocked (not_enabled) |
| `vh_數學B4_ProbabilityOperations` | blocked (not_enabled) |
| `vh_數學B4_MathematicalExpectationDefinition` | blocked (not_enabled) |
| `vh_數學B4_ApplicationsOfExpectation` | blocked (not_enabled) |
| `vh_數學B4_MathematicalExpectation` | blocked (not_enabled) |

---

## 4. Checker Reuse Summary

Phase 6C-2 完全重用 `b4_validators.py` 的現有 checker，**未修改 checker 程式碼**：

| checker | 用途 | 模式 |
|---|---|---|
| `check_rational_answer` | union_intersection + dice_coin 答題批改 | flexible（decimal+percentage+LaTeX 等值均接受） |
| `check_integer_answer` | sample_space_count（6C-1 回歸確認） | strict |
| `check_probability_range` | 由 check_rational_answer 內部呼叫 | 共通層 |

---

## 5. Tests Run

```
python -m pytest \
  tests/test_b4_chap2_phase6c2_probability_second_batch.py \
  tests/test_b4_chap2_phase6c1_probability_basic.py \
  tests/test_b4_chap2_phase6c1r_practice_route_integration.py \
  tests/test_b4_chapter1_adaptive_allowlist.py \
  --tb=short -q
```

**結果：250 passed in 0.26s**

| Test Suite | 測試數 | 狀態 |
|---|---|---|
| Phase 6C-2 新測試 | 82 | ✅ PASSED |
| Phase 6C-1 原測試 | 95 | ✅ PASSED (3 tests updated to pin pid) |
| Phase 6C-1R Route 測試 | 73 | ✅ PASSED (2 tests updated to pin pid) |
| Chap1 Allowlist / Router 回歸 | 8 | ✅ PASSED |

**已知 test 更新說明（非 bug）：**

舊測試 `test_p0_skills_generate_correctly`、`test_multi_seed_smoke`（6C-1）和 `test_generate_and_validate_p0_skills`（6C-1R）在 registry 只有 1 entry 時，`generate_for_chap2_skill(skill_id=..., seed=N)` 固定返回同一題型。6C-2 registry 擴展後有 2 entries，seed 路由可能選到新 entry。解法：加 `problem_type_id=expected_pid` pin 參數。此為正確行為，非回歸。

---

## 6. Manual Smoke Checklist

啟動 Flask app 後，依 SOP 測試：

### 6.1 URL decode + skill bypass

```
GET /practice?skill=vh_數學B4_ProbabilityProperties
GET /practice?skill=vh_%E6%95%B8%E5%AD%B8B4_ProbabilityProperties
GET /practice?skill=vh_數學B4_ProbabilityDefinition
GET /practice?skill=vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition
```

預期：進入練習頁，無「技能不存在」錯誤。

### 6.2 /get_next_question

```
GET /get_next_question?skill=vh_數學B4_ProbabilityProperties&problem_type=union_intersection_probability
GET /get_next_question?skill=vh_數學B4_ProbabilityDefinition&problem_type=dice_coin_probability_count
GET /get_next_question?skill=vh_%E6%95%B8%E5%AD%B8B4_ProbabilityProperties
GET /get_next_question?skill=vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition
```

預期：
- HTTP 200
- `question_text` 含 P(A∪B) 或 P(A∩B)（聯集）/骰子幣題情境
- `answer_type` = `rational_fraction`
- 無 handwriting / ai_judged 欄位

### 6.3 /check_answer（union_intersection）

```
POST /check_answer
{"answer": "3/5"}                 → 正確（若 correct_answer = 3/5）
{"answer": "6/10"}               → 正確（等值 unreduced）
{"answer": "0.6"}                → 正確（等值 decimal）
{"answer": "60%"}                → 正確（等值 percentage）
{"answer": "1/2"}                → 錯誤
```

### 6.4 /check_answer（dice_coin）

```
POST /check_answer
{"answer": "1/6"}                → 正確（若 correct_answer = 1/6）
{"answer": "3/18"}               → 正確（等值 unreduced）
{"answer": "1/4"}                → 錯誤
```

### 6.5 handwriting listing 仍 blocked

```
GET /get_next_question?skill=vh_數學B4_SampleSpaceAndEvents&problem_type=sample_space_listing
```

預期：HTTP 422，錯誤訊息含「handwriting reserved」。

### 6.6 未開放技能仍 blocked

```
GET /get_next_question?skill=vh_數學B4_BasicConceptsOfSets
GET /get_next_question?skill=vh_數學B4_ConditionalProbability
```

預期：HTTP 404「技能不存在或未啟用」（不 fallback 到 legacy module）。

**Manual smoke 狀態：⏳ PENDING（等待人工執行）**

---

## 7. Risks / Known Limitations

| # | 風險 | 說明 | 建議 |
|---|---|---|---|
| R1 | union 參數全用同分母 D | 生成器使用單一分母，題目參數較規則 | 可在 6C-3 引入不同分母版本，豐富題目多樣性 |
| R2 | dice_coin coin_exact_heads n=2..4 限制 | n>4 組合爆炸，超出 Level 1 難度 | 可在 6D 開放 n=5,6 的 Level 2/3 題型 |
| R3 | two_dice_sum difficulty ≤ 1 只選 target∈{6,7,8} | 其他 target 在 Level 1 不出現 | 可依課程需求在 6C-3 放開 |
| R4 | checker infinite decimal | `1/6` 的 decimal repr 為無限循環，不可直接傳入 check_rational_answer | 已在 test 中避免；production checker 使用 Fraction 精確比對，此問題不影響 runtime |

---

## 8. Final Confirmation

| 項目 | 狀態 |
|---|---|
| 是否只處理 2 個 problem_type | ✅ 是（union_intersection_probability + dice_coin_probability_count） |
| 是否新增 Phase 6C-2 題型以外內容 | ✅ 否 |
| 是否修改 production code | ✅ 是，限 `chap2_probability_basic.py`、`question_router.py`、`b4_chapter2_phase6c1_allowlist.py`（必要最小修改） |
| 是否修改 tests | ✅ 是，限本輪測試 + 必要 pin 修正既有 6C-1/6C-1R 測試 |
| 是否修改 routes | ✅ 否（`practice.py` 未動；`is_b4_chapter2_phase6c1_deterministic_skill` 已覆蓋新 skills） |
| 是否修改 templates | ✅ 否 |
| 是否修改 generators | ✅ 是，限 `chap2_probability_basic.py` 追加（Phase 6C-1 generator 函式未改動） |
| 是否修改 database | ✅ 否 |
| 是否修改 coverage matrix | ✅ 否 |
| 是否新增 / 修改 deterministic allowlist | ✅ 是，只限 6C-2 兩題 + 保留 6C-1（allowlist size 3→5） |
| 是否加入 handwriting/free-response 題型 | ✅ 否 |
| 是否處理 BasicConceptsOfSets | ✅ 否 |
| 是否修改 adaptive scoring / mastery / APR / remediation | ✅ 否 |
| 是否啟動 Phase 6D / 6E / 6F | ✅ 否 |

---

*Phase 6C-2 完成。停在此處，等待人工 smoke。*
*狀態：READY_FOR_MANUAL_SMOKE*
