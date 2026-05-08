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
