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

## 8.2 Adaptive Practice Chapter Mode Entry and UI State Contract

### 8.2.1 Chapter mode entry link must be verified

若某章節已完成 deterministic runtime-ready coverage，dashboard / curriculum view 的「單元練習」連結必須導向 chapter mode：

`/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=<chapter_id>&learning_mode=teaching&practice_kind=unit_practice`

不得導向：

`/adaptive_practice?mode=single&skill_ids=<chapter label>`

例如 Chap2「2 機率」應導向：

`/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=2&learning_mode=teaching&practice_kind=unit_practice`

### 8.2.2 Start diagnosis must not be silent no-op

adaptive_practice chapter mode 按「開始診斷」後，必須驗證：

- 可產生第一題
- 題目屬於該章 deterministic allowlist / diagnostic sequence
- 可送答案
- 可批改
- 可進下一題
- 若失敗，必須顯示 friendly error，不得 silent no-op

### 8.2.3 UI state must update, not only question flow

runtime smoke 不得只驗證「有題目」。
還必須確認前端 UI state 有更新：

- step_number / completed_steps
- total_steps
- progress_percent
- display_mastery_percent 或本次診斷顯示用 mastery
- current_stage / current_skill
- next_skill / next_problem_type
- session_correct_count
- session_attempt_count
- session_correct_rate
- trajectory_points 或等價動態軌跡資料

若此階段尚未接正式 mastery / APR，必須明確區分：

- display_mastery_percent：session-local UI display only
- formal mastery / APR：不得被本階段修改，除非另有 scoring policy phase 核准

### 8.2.4 Chapter mode should reuse existing chapter pattern

新增章節接入 adaptive_practice 時，應優先沿用已存在的 chapter mode pattern，例如 Chap1：

- chapter mode bootstrap
- curriculum / volume / chapter_id parsing
- chapter-specific allowlist / resolver
- diagnostic sequence
- get_next_question / check_answer integration
- audit logging

不得為每章重寫一套完全平行的 adaptive engine。

### 8.2.5 Runtime smoke gate must include chapter mode checks

每個章節接入 adaptive_practice chapter mode 時，manual smoke / automated tests 至少包含：

1. dashboard 單元練習連結正確
2. chapter mode URL 可進入
3. 開始診斷有第一題
4. 答題後可批改
5. 可進下一題
6. progress / mastery display 不停在 0%
7. trajectory / roadmap 有更新
8. 不出現 silent no-op
9. 不出現 JS uncaught error
10. 不破壞既有章節 chapter mode
11. 不修改正式 mastery / APR / remediation，除非本 phase 明確允許

### 8.2.6 Completion status rule

若 chapter mode 已能出題與批改，但 UI progress / trajectory / mastery display 未更新，狀態不得標為 `MANUAL_SMOKE_PASSED`。

應標為：

`NEEDS_UI_STATE_REPAIR`

## 8.3 Runtime-Ready 定義與階段性驗收

不是「能出題、能批改」就算 runtime-ready。一個 skill 要達到 runtime-ready 必須滿足以下三大原則：

1. **Skill-level textbook coverage（確實盤點題型覆蓋度）**：該 skill 在資料庫題庫與課本 evidence 中出現過的主要題型，都必須被確實盤點並納入 generator 實作範圍。
2. **Automated scenario diversity check（自動化多樣性防護）**：generator 必須具備實質的題幹與情境變化，不能只換數字。且必須透過自動化測試 (automated tests) 驗證多 seed 下的 scenario 多樣性，不能依賴 manual smoke 去抓「題型太單調」的問題。
3. **Chapter-level manual smoke（推遲人工驗收時機）**：不再於單一或少數技能完成時就要求 manual smoke。必須等「該章節的全部技能」都完成 runtime-ready 後，才進行少量的最終人工驗收（Chapter-level manual smoke），以降低反覆測試成本。

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
- v0.1.3：新增 Adaptive Practice Chapter Mode Entry and UI State Contract。要求章節單元練習連結必須使用 chapter mode，開始診斷不得 silent no-op，且 runtime smoke 必須驗證 progress / display mastery / trajectory / session state 更新；若只出題但 UI 狀態不更新，應標記 NEEDS_UI_STATE_REPAIR。
- v0.1.5：新增 Section 8.3 Runtime-Ready 定義與階段性驗收。明確定義 runtime-ready 必須包含 skill-level textbook coverage 與 automated scenario diversity check，並將 manual smoke 的執行時機延後至 chapter-level 全部技能完成後。

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


## Visual / Handwriting / Review 題型的自動化驗收原則

### Runtime mode 分流
B4 題型需分三類，且 route/checker 必須明確分流：

1. `deterministic_auto_checked`
- 適用：純數值、分數、選擇題、可機器批改題型。
- 驗收：必須通過 `/practice -> /get_next_question -> /check_answer`。

2. `visual_or_handwriting_ai_checked`
- 適用：圖形、長條圖、折線圖、樹狀圖、數線、表格、手寫過程。
- 要求：
  - 題目可進 `practice` 頁。
  - payload 必須帶 `visual_backed`、`visual_asset_type`、`runtime_mode`、`check_mode`、`grading_mode` metadata。
  - 不可硬塞進一般 deterministic checker。
  - 當 `check_mode` 屬於 `ai_judged_free_response` / `visual_ai_checked` / `handwriting_ai_checked` / `review_mode` 時，`/check_answer` 必須 guard，回傳需使用 AI 檢查或教師覆核的 friendly response。

3. `teacher_review` / `visibility_only`
- 適用：開放式解釋、抽樣設計、民調解讀、完整手寫證明。
- 要求：可出題、可呈現、可蒐集學生作答；不要求 deterministic 判分。

### 自動化測試優先
每一批 visual / handwriting 題型完成時，必須先有 automated tests，再進 manual smoke。

最低測試應包含：

1. generator payload test
- `question payload` 含 `visual_backed`
- `visual_aids` 或 `image_base64` 存在
- `runtime_mode` / `check_mode` / `grading_mode` 正確
- `answer` 格式符合題型

2. router test
- 指定 `skill` 可抽到新增 family
- `problem_type` / `scenario_family` / `visual_asset_type` 可被觀察到

3. practice route test
- `/get_next_question` 可回 visual-backed 題
- 前端必需欄位不缺失
- encoded / decoded `skill_id` 正常

4. check_answer guard test
- `deterministic_auto_checked` 題可正常判對 / 判錯
- `ai_judged_free_response` / `visual_ai_checked` / `handwriting_ai_checked` / `review_mode` 不可誤走 deterministic checker
- 應回傳 friendly response

5. regression test
- 舊 Chap1 / Chap2 / Chap3 deterministic runtime-ready 題型不得壞掉
- 既有 handwriting payload 路徑不得壞掉

### Scenario diversity 自動化
visual 題型不得只換數字。測試需檢查至少下列欄位之一：
- `scenario_id`
- `scenario_family`
- `problem_type`
- `visual_asset_type`
- `question pattern`

若同一 skill 底下有多個圖形 family，應逐批加入，不得一次大改全部。

### Manual smoke 後移
manual smoke 只在 automated tests 通過後進行。
manual smoke 只做少量代表性視覺確認，例如每個新 family 2~3 題。

manual smoke 檢查項目：
- practice 頁可進入
- 圖形 / 表格正常顯示
- 題目文字自然
- 短答 / 手寫 / 上傳 / AI 檢查 UI 不衝突
- deterministic 題判分正常
- review / AI checked 題不誤判

### Small repair 原則
若 manual smoke 發現問題：
1. 不得只靠人工反覆測
2. 必須先新增或補強 automated regression test
3. 再做最小 code repair
4. 再跑相關 tests
5. 更新 report

### Report 狀態標準
每一批 visual runtime path report 必須標示其中一種狀態：
- `BLOCKED`
- `READY_FOR_MANUAL_SMOKE`
- `MANUAL_SMOKE_PASSED`
- `ACCEPTED_WITH_KNOWN_LIMITATIONS`

若只有 planning report，沒有 runtime code 與 tests，不得標示 `READY_FOR_MANUAL_SMOKE`。

### Phase B4-Graph-1 範例
Phase B4-Graph-1：

- report path:
  `reports/b4_generator_planning/b4_graph1_visual_problem_runtime_first_batch_summary.md`

- 已完成 family：
  - `vh_數學B4_CentralTendencyMeasures:chart_mode_bar_reading`
  - `vh_數學B4_DispersionMeasures:chart_range_line_reading`

- 狀態：
  `MANUAL_SMOKE_PASSED`

此案例代表：
- `visual_reading_with_short_answer` 可作為 B4 圖形題第一條 runtime path
- 圖形題可先採「看圖短答」方式進入 runtime
- 不必一開始就完成自由手繪 AI 批改
- 但 metadata、route、checker guard、tests 必須先齊備
