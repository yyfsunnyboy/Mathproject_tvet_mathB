# B4 Chapter 2 Phase 6C Postcheck：P0 Deterministic Closure

## 0. Scope and Guardrails

本輪為 Phase 6C P0 Deterministic 的 closure / postcheck，**只新增文件**，不做任何 implementation。

明確聲明：

| 項目 | 確認 |
|---|---|
| 未新增任何題型 | ✅ |
| 未修改 production code | ✅ |
| 未修改 tests | ✅ |
| 未修改 routes | ✅ |
| 未修改 templates | ✅ |
| 未修改 generators | ✅ |
| 未修改 validators | ✅ |
| 未修改 database | ✅ |
| 未修改 coverage matrix | ✅ |
| 未修改 adaptive scoring / mastery / APR / remediation | ✅ |
| 未啟動 Phase 6D / 6E / 6F | ✅ |

新增文件：
- `reports/b4_generator_planning/b4_phase6c_postcheck_chap2_p0_deterministic_closure.md`（本報告）
- `docs/系統SOP/B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md`（追加 frontend double-encoding guard + changelog v0.1.1）

---

## 1. Completed Phase 6C Scope

### 1.1 已完成 Problem Types

| phase | problem_type | skill_id | answer_type | checker | runtime status |
|---|---|---|---|---|---|
| 6C-1 | `classical_probability_fraction` | `vh_數學B4_ProbabilityDefinition` | `rational_fraction` | `check_rational_answer` flexible | **MANUAL_SMOKE_PASSED** |
| 6C-1 | `complement_probability` | `vh_數學B4_ProbabilityProperties` | `rational_fraction` | `check_rational_answer` flexible | **MANUAL_SMOKE_PASSED** |
| 6C-1 | `sample_space_count_numeric` | `vh_數學B4_SampleSpaceAndEvents` | `integer` | `check_integer_answer` strict | **MANUAL_SMOKE_PASSED** |
| 6C-2 | `union_intersection_probability` | `vh_數學B4_ProbabilityProperties` | `rational_fraction` | `check_rational_answer` flexible | **MANUAL_SMOKE_PASSED** |
| 6C-2 | `dice_coin_probability_count` | `vh_數學B4_ProbabilityDefinition` | `rational_fraction` | `check_rational_answer` flexible | **MANUAL_SMOKE_PASSED** |

### 1.2 Sub-phases 彙整

| sub-phase | 說明 | 狀態 |
|---|---|---|
| Phase 6C-1 | 初始 3 個 deterministic 題型 + generators + checker + router + allowlist + tests | MANUAL_SMOKE_PASSED |
| Phase 6C-1R | `/practice` route integration、URL decode、generator branch、check_answer interceptor | MANUAL_SMOKE_PASSED |
| Phase 6C-1R2 | legacy skills module fallback fix（`import skills.<skill_id>` 防護） | MANUAL_SMOKE_PASSED |
| Phase 6C-1V | `sample_space_count_numeric` 情境輪轉（variety / seed coverage tuning） | MANUAL_SMOKE_PASSED |
| Phase 6C-2 | 新增 2 個 deterministic 題型 + allowlist 擴充 + router 擴充 + tests | MANUAL_SMOKE_PASSED |
| Phase 6C-2R | frontend double-encoding fix（`getSkillId()` 加 `decodeURIComponent()`） | MANUAL_SMOKE_PASSED |

---

## 2. Runtime Smoke Gate Result

### 2.1 最終 Smoke Gate 結果

| smoke gate item | 結果 |
|---|---|
| `/practice` entry（decoded skill） | ✅ passed |
| `/practice` entry（encoded skill） | ✅ passed |
| `/get_next_question`（decoded skill） | ✅ passed |
| `/get_next_question`（encoded skill） | ✅ passed |
| `/check_answer`（rational：fraction/decimal/percentage） | ✅ passed |
| `/check_answer`（integer：strict，`36.0` / `36%` rejected） | ✅ passed |
| URL encoded skill_id decode | ✅ passed |
| decoded skill_id passthrough | ✅ passed |
| frontend double-encoding regression | ✅ passed |
| unsupported Chap2 skill guard（422，`Chap2 skill not enabled`） | ✅ passed |
| handwriting reserved problem_type blocked（`sample_space_listing` / `event_set_listing` / `subset_listing`） | ✅ passed |
| legacy skills module fallback avoided | ✅ passed |
| Chap1 regression | ✅ passed |

### 2.2 重要教訓：Frontend Double-Encoding

**根因：**

`templates/index.html` 的 `getSkillId()` 函式從 `window.location.pathname.split('/')` 取 path segment。當瀏覽器 URL 為：

```
/practice/vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition
```

取到的 `pathParts[last]` 為 **encoded 字串**：`vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition`

接著 `URLSearchParams.set('skill', ...)` 會把 `%` 二次 encode 成 `%25`，傳給 server：

```
/get_next_question?skill=vh_%2525E6%2525958...
```

後端 `_url_unquote()` 只解一層，得到：

```
vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition  （仍 encoded！）
```

`is_b4_chapter2_phase6c1_deterministic_skill()` 判斷失敗 → DB lookup → 404。

**修正：**

在 `getSkillId()` 中，path segment 先 `decodeURIComponent()`，再由 `URLSearchParams.set()` 送出（single-encoded）→ backend `_url_unquote()` 正確還原：

```javascript
// 修正後的 path 取法
const rawSkillIdFromPath = pathParts[pathParts.length - 1];
const skillIdFromPath = rawSkillIdFromPath
    ? (function() { try { return decodeURIComponent(rawSkillIdFromPath); } catch(e) { return rawSkillIdFromPath; } })()
    : '';
```

**設計安全性：**
- `try/catch` 防止 `URIError`（malformed URI 如 `%ZZ`）
- 對已 decoded 字串（純 CJK / ASCII）`decodeURIComponent()` idempotent，無副作用
- Backend `_url_unquote()` 不需改動

**SOP 補記：**

此問題屬於 **frontend double-encoding**，在後端 URL decode 修正後仍可能發生，因此 Runtime Smoke Gate SOP 已在 v0.1.1 補入 `frontend double-encoding guard`（見 SOP Section 6.1）。

---

## 3. Tests Summary

| Phase | 測試執行 | 測試數量 | 狀態 | 來源 |
|---|---|---|---|---|
| Phase 6C-1 generator/checker/router/allowlist | `test_b4_chap2_phase6c1_probability_basic.py` | **95 passed** | ✅ | b4_phase6c1_deterministic_probability_minimal_summary.md |
| Phase 6C-1R route integration | `test_b4_chap2_phase6c1r_practice_route_integration.py` | **73 passed** | ✅ | b4_phase6c1r_practice_route_smoke_fix_summary.md |
| Phase 6C-1R2 next_question integration | `test_b4_chap2_phase6c1r2_practice_next_question_integration.py` | 含於 203 passed 中 | ✅ | b4_phase6c1r2_legacy_skill_fallback_fix_summary.md |
| Phase 6C-2 second batch + regression | 4 suites combined | **250 passed** | ✅ | b4_phase6c2_second_deterministic_probability_summary.md |
| Phase 6C-2R double-encoding regression | 5 suites combined | **337 passed** | ✅ | b4_phase6c2r_practice_smoke_regression_summary.md |
| Chap1 regression | `test_b4_chapter1_adaptive_allowlist.py` | **8 passed**（每次） | ✅ | 每個 phase 均執行 |
| **Final combined run** | 5 suites | **337 passed in 0.24s** | ✅ | Phase 6C-2R |

> **最終組合跑法：**
> ```
> python -m pytest \
>   tests/test_b4_chap2_phase6c2r_practice_smoke_regression.py \
>   tests/test_b4_chap2_phase6c2_probability_second_batch.py \
>   tests/test_b4_chap2_phase6c1_probability_basic.py \
>   tests/test_b4_chap2_phase6c1r_practice_route_integration.py \
>   tests/test_b4_chapter1_adaptive_allowlist.py \
>   --tb=short -q
> ```
> 結果：**337 passed in 0.24s**

最終人工 smoke：**全部通過**（Phase 6C-2R manual smoke，2026-05-08）。

---

## 4. Files Changed Across Phase 6C

### 4.1 Production Code

| 檔案 | 動作 | 涉及 Phase |
|---|---|---|
| `core/vocational_math_b4/generators/chap2_probability_basic.py` | **新增**（6C-1），**修改追加**（6C-1V variety tuning、6C-2 新增 2 generators） | 6C-1, 6C-1V, 6C-2 |
| `core/vocational_math_b4/domain/b4_validators.py` | **修改追加**（新增 `check_rational_answer`、`check_integer_answer`、`check_probability_range`） | 6C-1 |
| `core/vocational_math_b4/services/question_router.py` | **修改追加**（新增 `_CHAP2_PHASE6C1_REGISTRY`、`generate_for_chap2_skill`；6C-2 擴充 registry） | 6C-1, 6C-2 |
| `core/vocational_math_b4/adaptive/b4_chapter2_phase6c1_allowlist.py` | **新增**（6C-1）；**修改**（6C-2 擴充 allowed_problem_types frozenset） | 6C-1, 6C-2 |
| `core/routes/practice.py` | **修改**（URL decode、skill_info bypass、generator branch、check_answer interceptor、legacy import guard） | 6C-1R, 6C-1R2 |
| `templates/index.html` | **修改**（`getSkillId()` 加 `decodeURIComponent()`） | 6C-2R |

### 4.2 Tests

| 檔案 | 動作 | 涉及 Phase |
|---|---|---|
| `tests/test_b4_chap2_phase6c1_probability_basic.py` | **新增**（6C-1）；**修改**（6C-2 後 pin problem_type_id） | 6C-1, 6C-2 |
| `tests/test_b4_chap2_phase6c1r_practice_route_integration.py` | **新增**（6C-1R）；**修改**（6C-2 後 pin problem_type_id） | 6C-1R, 6C-2 |
| `tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py` | **新增**（6C-1R2） | 6C-1R2 |
| `tests/test_b4_chap2_phase6c2_probability_second_batch.py` | **新增**（6C-2） | 6C-2 |
| `tests/test_b4_chap2_phase6c2r_practice_smoke_regression.py` | **新增**（6C-2R） | 6C-2R |

### 4.3 Reports

| 檔案 | Phase |
|---|---|
| `reports/b4_generator_planning/b4_phase6a_chap2_problem_type_taxonomy.md` | 6A |
| `reports/b4_generator_planning/b4_phase6b_probability_validator_plan.md` | 6B |
| `reports/b4_generator_planning/b4_phase6c1_deterministic_probability_minimal_summary.md` | 6C-1 |
| `reports/b4_generator_planning/b4_phase6c1r_practice_route_smoke_fix_summary.md` | 6C-1R |
| `reports/b4_generator_planning/b4_phase6c1r2_legacy_skill_fallback_fix_summary.md` | 6C-1R2 |
| `reports/b4_generator_planning/b4_phase6c1v_sample_space_variety_summary.md` | 6C-1V |
| `reports/b4_generator_planning/b4_phase6c2_second_deterministic_probability_summary.md` | 6C-2 |
| `reports/b4_generator_planning/b4_phase6c2r_practice_smoke_regression_summary.md` | 6C-2R |
| `reports/b4_generator_planning/b4_phase6c_postcheck_chap2_p0_deterministic_closure.md` | **6C Postcheck（本報告）** |

### 4.4 SOP

| 檔案 | 動作 |
|---|---|
| `docs/系統SOP/B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md` | **追加**：Section 6.1 frontend double-encoding guard + changelog v0.1.1 |

### 4.5 未修改（保護範圍確認）

- `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py` — 未動
- 所有 Chap1 generator — 未動
- database — 未動
- coverage matrix — 未動
- adaptive scoring / mastery / APR / remediation — 未動
- 其他 routes — 未動

---

## 5. Guardrail Confirmation

| 項目 | 狀態 |
|---|---|
| `sample_space_listing` blocked | ✅ hard excluded in `B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES` |
| `event_set_listing` blocked | ✅ hard excluded |
| `subset_listing` blocked | ✅ hard excluded |
| `BasicConceptsOfSets` 未開放 | ✅ 在 `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS` |
| `ConditionalProbability` 未開放 | ✅ 在 `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS` |
| `IndependentEvents` 未開放 | ✅ 在 `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS` |
| `MathematicalExpectation*` 未開放 | ✅ 在 `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS` |
| handwriting / free-response 未進 deterministic allowlist | ✅ |
| adaptive scoring / mastery / APR / remediation 未修改 | ✅ |
| database 未修改 | ✅ |
| coverage matrix 未修改 | ✅ |
| Chap1 allowlist 未被破壞（size 仍 13） | ✅ |
| Chap2 P0 skills 不在 Chap1 allowlist | ✅ 測試確認無 overlap |

---

## 6. Known Limitations

| # | 限制 | 說明 | 建議處理 Phase |
|---|---|---|---|
| L1 | `set_operation_count` 未處理 | 集合計數，牽涉 `BasicConceptsOfSets` | Phase 6C-3 或 6D-alt |
| L2 | `inclusion_exclusion_count` 未處理 | 同上 | Phase 6C-3 或 6D-alt |
| L3 | `conditional_probability_basic` 未處理 | 條件機率 P(B\|A) | Phase 6D |
| L4 | `without_replacement_conditional_probability` 未處理 | 不放回條件機率 | Phase 6D |
| L5 | `independent_events_definition` 未處理 | 獨立事件定義判斷 | Phase 6E |
| L6 | `expected_value_discrete` 未處理 | 數學期望值 E(X) | Phase 6F |
| L7 | handwriting listing 題型未接入 scoring | `sample_space_listing` / `event_set_listing` / `subset_listing` 保留給 AI-judged 評分流程 | Phase 6G（handwriting phase） |
| L8 | Chap2 deterministic result 未接 adaptive scoring | mastery / APR / fail_streak 尚未整合 Chap2 deterministic 答題結果 | 另開 phase |
| L9 | DB `textbook_examples` 87 題 `needs_review` 未處理 | 本輪 generator 使用獨立參數化生成，不依賴 DB 題目 | 另開 DB 清理 phase |
| L10 | image-related 題仍排除 | Phase 6A inventory 確認有 2 題 image-related，目前不生成 | 另開 Phase |
| L11 | `classical_probability_fraction` 情境仍偏簡（integer_range 僅奇/偶） | 未來可擴充更多情境（因數、倍數、質數等） | Phase 6C 擴充或 6D+ |
| L12 | union 參數全用同分母 D | `union_intersection_probability` 使用單一分母，題目較規則 | Phase 6C-3 引入不同分母 |
| L13 | dice_coin coin n 限 2..4 | n>4 超出 Level 1 難度，目前排除 | Phase 6D Level 2 擴充 |
| L14 | `BasicConceptsOfSets` 開放路線未確定 | 開放前須先確認 allowlist + route guard 策略 | 優先於 Phase 6C-3 |

---

## 7. SOP Update Note

已更新 `docs/系統SOP/B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md`，追加：

- **Section 6.1**（插入在既有 Section 6 之後）：Frontend double-encoding guard
- **Changelog v0.1.1**

> 追加內容只在 SOP 末尾插入小節，**未重寫既有任何 section**。

### Frontend double-encoding guard（摘要）

若 B4 practice page 以 path-based URL（`/practice/<skill_id>`）開啟，且 `skill_id` 含 CJK（如 `vh_%E6%95%B8%E5%AD%B8B4_...`），前端 `getSkillId()` 從 `window.location.pathname` 取得的 path segment 仍是 **encoded** 字串。

若直接交給 `URLSearchParams.set()`，`%` 會被二次 encode 成 `%25`，導致 server 收到雙重 encode 的 skill_id，`_url_unquote()` 解一層後仍是 encoded，allowlist 判斷失敗。

**修正規則：** 每個從 pathname 或 querystring 取出的 skill_id，在進 `URLSearchParams.set()` 前，一律先 `decodeURIComponent()`（try/catch 防 URIError）。

---

## 8. Recommended Next Phase

### 建議：Phase 6D — Conditional Probability Minimal Batch

**理由：**

- Chap2 P0 deterministic probability 已完整 closure
- 條件機率是 Chap2 主線的自然延伸
- 不建議跳去 expectation（數學結構複雜）或 handwriting listing（需 AI-judged scoring）

**建議 scope：**

| problem_type | skill_id | 說明 |
|---|---|---|
| `conditional_probability_basic` | `vh_數學B4_ConditionalProbability` | P(B\|A) = P(A∩B)/P(A)，給定 P(A)、P(A∩B) 求 P(B\|A) |
| `without_replacement_conditional_probability` | `vh_數學B4_ConditionalProbability` | 不放回抽樣條件機率（球袋、撲克牌等） |

**前提：**

1. Phase 6C Postcheck 宣告完成
2. 未來 smoke gate SOP 必須沿用（含 frontend double-encoding guard）

---

### 替代方案：Phase 6C-3 — Set Count Batch

**scope：**

| problem_type | skill_id | 說明 |
|---|---|---|
| `set_operation_count` | `vh_數學B4_BasicConceptsOfSets` | 集合元素個數計算 |
| `inclusion_exclusion_count` | `vh_數學B4_BasicConceptsOfSets` | 排容原理 \|A∪B\| = \|A\| + \|B\| - \|A∩B\| |

**前提：**

- `BasicConceptsOfSets` 目前在 `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS`
- 若選此路線，須先明確處理 `BasicConceptsOfSets` 的 allowlist 邊界與 route guard
- 不建議在 Phase 6D 之前直接啟動，除非 BasicConceptsOfSets 的 scope 已明確界定

---

## 9. Final Confirmation

| 項目 | 確認 |
|---|---|
| 是否只新增 closure report | ✅ 是 |
| 是否更新 SOP | ✅ 是（只追加 frontend double-encoding guard + changelog v0.1.1，未重寫） |
| 是否修改 production code | ✅ 否 |
| 是否修改 tests | ✅ 否 |
| 是否修改 routes | ✅ 否 |
| 是否修改 templates | ✅ 否 |
| 是否修改 generators | ✅ 否 |
| 是否修改 validators | ✅ 否 |
| 是否修改 database | ✅ 否 |
| 是否修改 coverage matrix | ✅ 否 |
| 是否新增 allowlist | ✅ 否 |
| 是否加入 handwriting/free-response 題型 | ✅ 否 |
| 是否修改 adaptive scoring / mastery / APR / remediation | ✅ 否 |
| 是否啟動 Phase 6D / 6E / 6F | ✅ 否 |

---

*Phase 6C P0 Deterministic Closure 完成。*

*狀態：**CLOSED**。*

*Phase 6C-1 + 6C-1R + 6C-1R2 + 6C-1V + 6C-2 + 6C-2R 全部 MANUAL_SMOKE_PASSED。*

*可進入下一 phase 規劃（建議 Phase 6D：Conditional Probability Minimal Batch）。*
