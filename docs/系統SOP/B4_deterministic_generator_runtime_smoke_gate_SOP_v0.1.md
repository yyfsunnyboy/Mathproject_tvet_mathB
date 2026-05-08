# B4 Deterministic Generator Runtime Smoke Gate SOP v0.1

## 1. SOP 目的

本 SOP 用來補強 B4 deterministic 題型的 implementation phase 驗收標準，避免只靠 generator/checker/router 單元測試就宣告完成。

重點：
- 避免「generator tests passed，但學生端不能用」。
- 避免中文 `skill_id` URL encoding/decoding 導致 runtime 失敗。
- 避免 fallback 到 legacy `skills.<skill_id>` import。
- 避免 handwriting/free-response 題型誤入 deterministic runtime。
- 建立每一批 deterministic 題型固定的 runtime smoke gate。

## 2. 適用範圍

適用於：
- B4 Chapter 1 以後所有 deterministic 題型 batch。
- Chap2 Phase 6C 之後所有 deterministic implementation phase。
- 未來 B1/B2/B3/B4 或其他冊別，只要沿用相同 vocational runtime 架構，皆可參考。

不適用於：
- handwriting AI-judged 題型。
- free-response 題型。
- manual review 題型。
- 純文件 phase（inventory/taxonomy/validator plan）。

## 3. 核心原則

1. implementation phase 完成標準不是 generator tests passed。
2. 必須確認 `/practice` 可進入。
3. 必須確認 `/get_next_question` 可取得題目。
4. 必須確認 `/check_answer` 可批改。
5. 必須測 URL encoded 與 decoded `skill_id`。
6. 必須測 unsupported skill 不得 fallback legacy import。
7. 必須測 handwriting reserved 題型 blocked。
8. 必須跑前一章/前一批 regression tests。
9. smoke 未通過，不得進下一批題型。

## 4. Deterministic Batch 必備交付物

每一批 deterministic implementation 至少交付：
1. generator
2. checker/validator
3. router registry
4. deterministic allowlist
5. `/practice` route integration
6. `/get_next_question` integration
7. `/check_answer` integration
8. tests
9. manual smoke checklist
10. phase summary report

狀態規範：
- 若只完成 generator/checker/router，未完成 `/practice` runtime integration，狀態只能是 `PARTIAL_RUNTIME_READY`。
- 若 manual smoke 尚未執行，狀態只能是 `READY_FOR_MANUAL_SMOKE`。

## 5. Runtime Smoke Gate Checklist

### 5.1 `/practice` entry

每個新 skill 必測：
- decoded：`/practice?skill=vh_數學B4_...`
- encoded：`/practice?skill=vh_%E6%95%B8%E5%AD%B8B4_...`

預期：
- 不出現「技能不存在或未啟用」。
- 不出現 `No module named 'skills.vh_數學B4_...'`。
- 可正常進入練習頁。

### 5.2 `/get_next_question`

每個新 `problem_type` 必測：
- 可取得題目。
- `question_text` 非空。
- `answer` 非空。
- `answer_type` 正確。
- `problem_type_id` 正確。
- 不得是 `handwriting`。
- 不得是 `ai_judged_free_response`。
- 不含 `[FORMULA_MISSING]`。
- 不含 `[BLANK]`。
- 不含未填 placeholder。

### 5.3 `/check_answer`

每個 checker 必測：
- canonical answer 正確。
- accepted equivalent answer 正確。
- wrong answer 錯誤。
- invalid format 錯誤。
- edge case 錯誤或 clear error。

機率題例：
- `1/2` correct
- `2/4` correct
- `0.5` correct
- `50%` correct
- `3/4` incorrect
- `5/4` invalid or incorrect
- `1/0` invalid or incorrect

整數題例：
- `36` correct
- ` 36 ` correct
- `３６` correct（若支援全形）
- `36.0` incorrect
- `36%` incorrect
- `-36` incorrect（除非明確允許）

### 5.4 unsupported skill guard

對同章但未開放 skill 必測：
- 回 clear error（例如 `ChapN skill not enabled in current phase`）。
- 不得 fallback 到 `No module named 'skills.vh_數學B4_...'`。

### 5.5 handwriting reserved guard

對 reserved `problem_type` 必測：
- `sample_space_listing`
- `event_set_listing`
- `subset_listing`
- `tree_diagram_listing`
- `pascal_triangle_handwriting`

預期：
- deterministic route blocked。
- 不進 deterministic allowlist。
- 不更新 mastery/APR/fail_streak/remediation。

## 6. URL Encoding 規則

- 所有 route 接收 `skill_id` 時，必須同時處理 encoded 與 decoded 形式。
- 中文 `skill_id` decode 必須採 idempotent 方式（例如 `urllib.parse.unquote`）。
- decode 不得破壞已 decoded 值。
- 測試必須同時涵蓋 encoded/decoded。

例子：
- encoded：`vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition`
- decoded：`vh_數學B4_ProbabilityDefinition`

## 7. Legacy skills module fallback 防護

若題型使用 `core/vocational_math_b4/generators` 與 `question_router` 新架構，runtime 不得嘗試：

`import skills.<skill_id>`

對 ChapN deterministic allowlist 內 skill：
- 先檢查 allowlist/router registry。
- 必須走新 generator route。
- 不得 fallback legacy module import。

對 ChapN 未開放 skill：
- 必須回 clear error。
- 不得 fallback legacy module import。

## 8. Allowlist 與 Problem Type 邊界

- allowlist 盡量以 `skill + problem_type` 為邊界。
- 若系統仍是 skill-level route，也必須在 skill 內限制 allowed `problem_type`。
- 不得因開放某 skill 就讓該 skill 全部 `problem_type` 進 deterministic runtime。
- handwriting/free-response `problem_type` 必須 hard excluded。

## 8.1 Skill Availability / Not-Enabled UX Rule

### 8.1.1 未開放 skill 是正常狀態，不是系統錯誤

若某個 skill 尚未被 deterministic allowlist 開放，runtime 應回傳清楚、**中性**的訊息，讓學生與教師理解「此能力尚未開放自動出題」，而非「系統壞掉」。

建議對外文案（可擇一或並列中英）：

- 此技能尚未開放自動出題
- This skill is not enabled in the current deterministic runtime

**不得**在學生端／教師端顯示**過期或內部** phase 名稱，例如：

- `Phase 6C-1`
- `Phase 6D`
- `Phase 6E`

phase 名稱屬工程內部流程標籤，不適合作為使用者可讀錯誤訊息；Chap2 已完成 6C／6D／6E／6F deterministic mainline 後，更不得沿用舊 phase 字串造成誤解。

### 8.1.2 錯誤訊息不得暴露內部實作細節

學生端／教師端**不得**出現下列內容：

- `No module named 'skills.vh_數學B4_...'`
- `Chap2 skill not enabled in Phase 6C-1`（或任何含具體 phase 代號的未開放訊息）
- raw Python `import` error、完整 traceback
- **encoded** `skill_id` 原文（例如 `vh_%E6%95%B8...`）
- **double-encoded** `skill_id`（例如 `vh_%2525E6...`）

應改為 **clear error**（語意對應即可，實作可先中英並列）：

- `此技能尚未開放自動出題`
- `Chap2 skill not enabled in current deterministic runtime`
- `This skill is reserved for handwriting/free-response review`（適用於僅保留給手寫／開放式流程者）

### 8.1.3 已開放／未開放／reserved 三種狀態需分離

runtime 或 UI 應能區分下列三類，避免混用為「系統錯誤」：

1. **enabled deterministic skill**
   - 可進入 `/practice`
   - 可透過 `/get_next_question` 出題
   - 可透過 `/check_answer` 批改

2. **not-yet-enabled skill**
   - 尚未開放自動出題（中性狀態）
   - **不得** fallback 到 legacy `import skills.<skill_id>`
   - **不得**被呈現為後端例外或「技能不存在」等系統故障語氣

3. **reserved handwriting / free-response `problem_type`**
   - 不進 deterministic allowlist
   - 不更新 mastery／APR／fail_streak／remediation（依既定政策）
   - 可標記為 future AI-judged／deferred_teacher_review

### 8.1.4 UI 建議

若技能列表包含尚未開放的 skill，建議優先：

- 將該項設為 **disabled**，或
- 顯示「尚未開放自動出題」
- 顯示「保留為手寫／開放式題型」（若屬 reserved 路線）
- 學生點擊後顯示**友善、中性**說明，而非技術錯誤

目標：避免學生誤以為整站或練習功能故障。

### 8.1.5 smoke gate 必測

每個 deterministic batch 的 runtime smoke **須額外**驗證：

- 已開放 skill：正常進入練習並出題、批改
- **同章未開放 skill**：回傳 **clear not-enabled** 訊息（不含過期 phase、不含 legacy import 字樣、不含 encoded／double-encoded `skill_id`）
- handwriting reserved `problem_type`：回傳 **reserved／blocked** 類 clear 訊息
- **不出現** legacy import error
- **不出現**過期或內部 phase 名稱
- **不出現** raw traceback 或將 URL 編碼串直接貼給使用者

## 9. 測試要求

每個 deterministic implementation phase 必須包含：
1. generator tests
2. checker tests
3. router/allowlist boundary tests
4. route integration tests
5. encoded/decoded `skill_id` tests
6. unsupported skill no legacy import tests
7. handwriting reserved blocked tests
8. previous phase regression tests
9. previous chapter regression tests（若相關）

測試結果必須寫入 phase summary report。

## 10. 狀態命名規則

- `PLANNING_ONLY`：只做 inventory/taxonomy/validator plan。
- `GENERATOR_READY`：generator/checker unit tests 通過，尚未 route integration。
- `RUNTIME_READY`：`/practice`、`/get_next_question`、`/check_answer` tests 通過。
- `READY_FOR_MANUAL_SMOKE`：automated route tests 通過，尚未人工 smoke。
- `MANUAL_SMOKE_PASSED`：人工 smoke 通過，可進下一批。
- `BLOCKED`：任一 gate 未通過，不得進下一 phase。

強制規則：
- 未達 `MANUAL_SMOKE_PASSED`，不得進下一 deterministic batch。

## 11. Phase Summary Report 必備欄位

每個 deterministic implementation summary report 必須包含：
1. scope and guardrails
2. implemented problem_types
3. files changed
4. generator summary
5. checker summary
6. router/allowlist summary
7. `/practice` route integration summary
8. `/check_answer` integration summary
9. tests run
10. manual smoke result
11. unsupported skill behavior
12. handwriting reserved behavior
13. known limitations
14. final confirmation
15. next phase recommendation

## 12. 與既有 SOP 的關係

本 SOP 為補丁文件，補強：
- `docs/系統SOP/教材匯入與技能生成SOP_v0.1.md`
- `docs/系統SOP/AI閉環開發與驗收SOP_v0.1.md`

它不取代既有 SOP，而是補強 deterministic generator implementation phase 的 runtime smoke gate。

## 13. Changelog

- v0.1：由 Chap2 Phase 6C-1 / 6C-1R / 6C-1R2 經驗整理而成，補強 runtime smoke gate、URL decode、legacy fallback guard、handwriting reserved guard。
- v0.1.1：加入 Section 6.1 frontend double-encoding guard，源自 Chap2 Phase 6C-2R manual smoke regression（2026-05-08）。
- v0.1.2：新增 Section 8.1 Skill Availability / Not-Enabled UX Rule，要求未開放 skill 回傳中性 clear error，不得顯示過期 phase 名稱、legacy import error、encoded／double-encoded skill_id，並要求 UI／smoke 區分 enabled／not-yet-enabled／reserved 三種狀態。

## 6.1 Frontend Double-Encoding Guard（v0.1.1 追加）

### 問題背景

後端 `_url_unquote()` 正確後，仍可能發生前端 double-encoding。

當 practice page 以 path-based URL（`/practice/<skill_id>`）開啟，且 `skill_id` 含 CJK 字元（如 `vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition`）：

1. `window.location.pathname.split('/')` 取到的 path segment 仍是 **encoded** 字串
2. 直接傳入 `URLSearchParams.set('skill', encoded_string)` 時，`%` 被再次 encode 成 `%25`
3. server 收到雙重 encoded skill_id：`vh_%2525E6%2525958...`
4. `_url_unquote()` 解一層後仍是 encoded → allowlist 判斷失敗 → 404

### 修正規則

每個從 `window.location.pathname` 或 `window.location.search` 取出的 skill_id，在進 `URLSearchParams.set()` 或任何 API 呼叫前，**一律先 `decodeURIComponent()`**：

```javascript
// 安全寫法（try/catch 防 URIError on malformed %-sequence）
function safeDecodeSkillId(raw) {
    try { return decodeURIComponent(raw); }
    catch(e) { return raw; }  // fallback: pass as-is, let backend handle
}
```

`decodeURIComponent()` 對已 decoded 的純 ASCII/CJK 字串是 idempotent，不會破壞正常值。

### Smoke Gate 補充測試項目

從 v0.1.1 起，每批 deterministic 題型的 manual smoke 必須涵蓋：

- **path-based encoded URL entry**：`/practice/vh_%E6%95%B8%E5%AD%B8B4_<SkillId>` 進入後，按「下一題」能正常出題
- **query-based encoded URL**：`/practice?skill=vh_%E6%95%B8%E5%AD%B8B4_<SkillId>` 同上
- 確認前端 `getSkillId()` 或等效函式已加 `decodeURIComponent()`
- 開發者工具 Network tab 確認：`/get_next_question?skill=` 後的值為 **single-encoded** 或 decoded，不含 `%25`

### 根源確認

此問題在 Phase 6C-2R 發現並修正：

- **修正位置**：`templates/index.html` → `getSkillId()` 函式（line ~3000）
- **修正日期**：2026-05-08
- **修正方式**：path/query 取出後先 `decodeURIComponent()`
- **後端保持不動**：`_url_unquote()` 已在 `practice.py` 各 route 正確位置，不需修改

