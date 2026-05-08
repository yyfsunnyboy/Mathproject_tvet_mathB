# B4 Chapter 2 Phase 6C-2R：Practice Smoke Regression Fix Summary

## 1. 根因 (Root Cause)

### 錯誤現象

/practice 頁面按「下一題」時出現：

```
技能 vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition 不存在或未啟用
技能 vh_%E6%95%B8%E5%AD%B8B4_SampleSpaceAndEvents 不存在或未啟用
```

### 根因分析

**雙重 encode（double-encoding）問題。**

**問題鏈：**

```
1. 瀏覽器 URL：
   /practice/vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition
   （encoded）

2. Flask backend practice() 收到路徑參數後已 _url_unquote →
   skill_id = "vh_數學B4_ProbabilityDefinition"（已 decoded）
   → 渲染 index.html，skill_id 傳入 template 為 decoded

3. 但 window.location.pathname 仍是原始 URL：
   /practice/vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition

4. 前端 getSkillId() 從 pathname.split('/') 取最後一段：
   pathParts[last] = "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition"
   → 取到的是 encoded 字串，未 decode

5. params.set('skill', "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition")
   → URLSearchParams.set() 再次 percent-encode '%' 為 '%25'
   → 傳給 server：vh_%2525E6%2525958%25...（二次 encode）

6. 後端 _url_unquote() 只解一層：
   → 得到 vh_%E6%95%B8%E5%AD%B8B4_... （仍 encoded！）

7. is_b4_chapter2_phase6c1_deterministic_skill() 判斷失敗
   → DB lookup → 404：技能 vh_%E6%95%B8... 不存在
```

**為何 6C-1R 時正常：**

6C-1R 修了 `/practice` page 的 URL decode，頁面可以正常進入，但 6C-1R 測試並未覆蓋「在 encoded URL 下按下一題」的 JS 路徑 — 當時的 manual smoke 使用的可能是 decoded URL。

**6C-2 是否覆蓋 6C-1R2 修正：** 否。6C-2 未動 `practice.py`，後端 `_url_unquote` 仍在（line 754）。問題根源在前端 JS，6C-2 亦未動 `index.html`。

---

## 2. 修改檔案

| 動作 | 檔案 | 說明 |
|---|---|---|
| **修改** | `templates/index.html` | `getSkillId()` 函式追加 `decodeURIComponent()`，防止二次 encode |
| **新增** | `tests/test_b4_chap2_phase6c2r_practice_smoke_regression.py` | Phase 6C-2R 回歸測試 |
| **新增** | `reports/b4_generator_planning/b4_phase6c2r_practice_smoke_regression_summary.md` | 本報告 |

**未修改：**
- `core/routes/practice.py`（`_url_unquote` 已在正確位置，不動）
- `core/vocational_math_b4/generators/chap2_probability_basic.py`
- `core/vocational_math_b4/adaptive/b4_chapter2_phase6c1_allowlist.py`
- `core/vocational_math_b4/services/question_router.py`
- database、coverage matrix、Chap1 allowlist

---

## 3. 修正方式

### 修改：`templates/index.html` — `getSkillId()` 函式

**Before：**
```javascript
function getSkillId() {
    if (PRACTICE_MODE === 'similar_practice' && similarPracticeState.skillId) {
        return similarPracticeState.skillId;
    }
    const querySkill = new URLSearchParams(window.location.search).get('skill');
    if (querySkill) return querySkill;
    const pathParts = window.location.pathname.split('/');
    const skillIdFromPath = pathParts[pathParts.length - 1];
    return skillIdFromPath || '{{ skill_id }}' || 'remainder';
}
```

**After：**
```javascript
function getSkillId() {
    if (PRACTICE_MODE === 'similar_practice' && similarPracticeState.skillId) {
        return similarPracticeState.skillId;
    }
    // Phase 6C-2R: decodeURIComponent() prevents double-encoding.
    // URLSearchParams.set() will percent-encode the value again, so we must
    // decode %-encoded segments first (e.g. vh_%E6%95%B8... → vh_數學B4_...).
    const rawQuerySkill = new URLSearchParams(window.location.search).get('skill');
    if (rawQuerySkill) {
        try { return decodeURIComponent(rawQuerySkill); } catch(e) { return rawQuerySkill; }
    }
    const pathParts = window.location.pathname.split('/');
    const rawSkillIdFromPath = pathParts[pathParts.length - 1];
    const skillIdFromPath = rawSkillIdFromPath
        ? (function() { try { return decodeURIComponent(rawSkillIdFromPath); } catch(e) { return rawSkillIdFromPath; } })()
        : '';
    return skillIdFromPath || '{{ skill_id }}' || 'remainder';
}
```

**設計說明：**
- `try/catch` 包裹 `decodeURIComponent()`，防止 malformed URI 拋出 `URIError`
- 如果 decode 失敗（例如 `%ZZ` 之類），安全 fallback 到原始字串，讓 backend 再次嘗試 decode
- 對已 decoded 的 skill_id（純 ASCII/CJK，無 `%`）`decodeURIComponent()` 是 idempotent
- Backend `_url_unquote` 保持不動，`URLSearchParams.set(decoded_cjk)` → server 收到 single-encoded → `_url_unquote` → plain

**修正後的鏈：**

```
1. URL: /practice/vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition
2. pathParts[last] = "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition"
3. decodeURIComponent() → "vh_數學B4_ProbabilityDefinition"（plain）
4. params.set('skill', "vh_數學B4_ProbabilityDefinition")
   → URLSearchParams encodes CJK → "skill=vh_%E6%95%B8%E5%AD%B8B4_..."（single-encoded）
5. 後端 _url_unquote() → "vh_數學B4_ProbabilityDefinition"（correct）
6. is_b4_chapter2_phase6c1_deterministic_skill() → True ✅
7. generate_for_chap2_skill() → payload ✅
```

---

## 4. 測試結果

```
python -m pytest \
  tests/test_b4_chap2_phase6c2r_practice_smoke_regression.py \
  tests/test_b4_chap2_phase6c2_probability_second_batch.py \
  tests/test_b4_chap2_phase6c1_probability_basic.py \
  tests/test_b4_chap2_phase6c1r_practice_route_integration.py \
  tests/test_b4_chapter1_adaptive_allowlist.py \
  --tb=short -q
```

**結果：337 passed in 0.24s**

| Suite | 測試數 | 狀態 |
|---|---|---|
| Phase 6C-2R 新回歸測試 | 87 | ✅ PASSED |
| Phase 6C-2 完整測試 | 82 | ✅ PASSED |
| Phase 6C-1 原測試 | 95 | ✅ PASSED |
| Phase 6C-1R Route 測試 | 73 | ✅ PASSED |
| Chap1 Allowlist / Router 回歸 | 8 | ✅ PASSED |

---

## 5. Manual Smoke Checklist

啟動 Flask app，執行以下手動測試：

### 5.1 Encoded URL 進入 /practice（必測）

```
GET /practice/vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition
GET /practice/vh_%E6%95%B8%E5%AD%B8B4_ProbabilityProperties
GET /practice/vh_%E6%95%B8%E5%AD%B8B4_SampleSpaceAndEvents
```

預期：正常進入練習頁，頁面標題非 `未知技能`，無 404。

### 5.2 按「下一題」（必測，根因修正點）

在上述三個 encoded URL 的頁面，點「下一題」：

預期：
- 正常出現題目
- 不出現「技能 vh_%E6%95%B8... 不存在或未啟用」
- `question_text` 包含正確的機率題目

### 5.3 /get_next_question 直接 API 測試

```
GET /get_next_question?skill=vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition
GET /get_next_question?skill=vh_%E6%95%B8%E5%AD%B8B4_ProbabilityProperties
GET /get_next_question?skill=vh_%E6%95%B8%E5%AD%B8B4_SampleSpaceAndEvents
GET /get_next_question?skill=vh_數學B4_ProbabilityDefinition
GET /get_next_question?skill=vh_數學B4_ProbabilityProperties
GET /get_next_question?skill=vh_數學B4_SampleSpaceAndEvents
```

預期：HTTP 200，`new_question_text` 非空，`answer_type` ∈ {`rational_fraction`, `integer`}。

### 5.4 6C-2 新題型確認

```
GET /get_next_question?skill=vh_數學B4_ProbabilityProperties&problem_type=union_intersection_probability
GET /get_next_question?skill=vh_數學B4_ProbabilityDefinition&problem_type=dice_coin_probability_count
```

預期：
- union：題目含 P(A∪B) 或 P(A∩B)
- dice_coin：題目含骰子/硬幣語境

### 5.5 Blocked skills 正確回錯誤（encoded 後也正確）

```
GET /get_next_question?skill=vh_數學B4_BasicConceptsOfSets
GET /get_next_question?skill=vh_%E6%95%B8%E5%AD%B8B4_BasicConceptsOfSets
GET /get_next_question?skill=vh_數學B4_ConditionalProbability
GET /get_next_question?skill=vh_數學B4_IndependentEvents
```

預期：HTTP 422，`error` = `Chap2 skill not enabled in Phase 6C-1`，**不**出現 encoded skill_id，**不**出現 `No module named`。

### 5.6 Handwriting listing blocked

```
GET /get_next_question?skill=vh_數學B4_SampleSpaceAndEvents&problem_type=sample_space_listing
```

預期：HTTP 422，`error` 含 `handwriting reserved`。

### 5.7 /check_answer 答題驗證

先取一道 ProbabilityDefinition 題，再分別送：
- `1/3` → 依題目決定正確/錯誤
- `2/6` → 等值 unreduced，若 correct_answer=1/3 則正確
- `0.5` → 若 correct_answer=1/2 則正確
- `50%` → 若 correct_answer=1/2 則正確
- `36.0`（integer 題）→ 應為錯誤
- `36%`（integer 題）→ 應為錯誤
- `36`（integer 題）→ 應為正確

### 5.8 Chap1 不受影響

```
GET /get_next_question?skill=vh_數學B4_AdditionPrinciple
```

預期：HTTP 200，正常出題。

---

## 6. Final Confirmation

| 項目 | 確認 |
|---|---|
| 是否只修 6C-2 smoke regression | ✅ 是 |
| 是否新增 Phase 6D 題型 | ✅ 否 |
| 是否處理 BasicConceptsOfSets | ✅ 否（維持 422 gate） |
| 是否加入 handwriting/free-response | ✅ 否 |
| 是否修改 database | ✅ 否 |
| 是否修改 coverage matrix | ✅ 否 |
| 是否修改 adaptive scoring / mastery / APR / remediation | ✅ 否 |
| 是否修改 templates | ✅ 是（限 index.html `getSkillId()` 加 `decodeURIComponent()`） |
| 是否啟動 Phase 6D | ✅ 否 |
| templates 修改是否必要 | ✅ 是（根因就在前端 JS 的 double-encoding） |
| 後端 practice.py `_url_unquote` 是否修改 | ✅ 否（已正確，保留） |

---

*Phase 6C-2R 完成。狀態：**READY_FOR_MANUAL_SMOKE**。*

*下一輪：Manual smoke 驗證後，若通過，可開始 Phase 6D 規劃。*
