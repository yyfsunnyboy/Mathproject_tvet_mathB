# Known Issues / Technical Debt

## CartesianCoordinateSystem skill-local `check()` 字串比對

- 位置：`skills/vh_數學B1_CartesianCoordinateSystemEstablishment.py` 的 skill-local `check()`
- 現象：仍存在 skill-local 字串比對，未走共用數學等價 checker
- 範圍：不屬於共用 checker 層；與 B1 Chapter 3 無關
- 本輪：不處理、不順手修
- 狀態：deferred

runtime wrapper `check_answer` 在 contract 指向象限 checker 時仍走共用路徑。未對齊的是 skill 本體 `check()`。

## 第二冊 Unit 9 二維數據分析：Stage 1 修復後殘留項

- 來源：2026-11-18 Unit 9 Stage 1 最小修復，證據見 `reports/gh_math2_unit9_stage1/`。
- 狀態：open，不阻擋 Stage 1 重新匯入。

| 項目 | 現況 | 影響與處理 |
| --- | --- | --- |
| MathType OLE #57、#63 轉換失敗 | DOCX 段落 116、119（「乙 相關係數」說明文字，PDF p5 的 \((x_i',y_i')\) 與 \(r=\frac{x_1'y_1'+\cdots+x_n'y_n'}{n}\)）；DSMT6 帶 prime 裝飾符號，`list index out of range` | 匯入只存題目列，這兩段不進題庫，也不會顯示在題目頁。未擴修 converter；若日後匯入或顯示課文說明，必須先修 |
| 跨題依賴（已於 2026-11-18 接上消費端） | 隨堂練習7 題幹「承例題6」，notes 有 `source_dependency` | 共用解析器 `core/textbook_source_dependency.py`。原題練習帶入例題6 前置資料且不自動判分。GenCode V3 生成題須自含資料。練7 的已驗證答案仍缺 |
| GenCode V3（2026-11-18 已正式發布） | Domain `statistics.bivariate_descriptive`，Bundle `.../affe15e1/revision_0001` | **Published**：21 components（Correlation 11 + Regression 10）。**DEFERRED 原題** 5 題（12947/12948/12954/12960/12963）固定 ungraded。備份 `backups/math2_unit9_bivariate_statistics/20261118_231904/`。Flask 5001 已受控重啟。Stage1 `pending_final_acceptance` 未改 |

## 教材跨題依賴（承例題N）解析

- 來源：2026-11-18。解析器為 `core/textbook_source_dependency.py`，測試見 `tests/test_textbook_source_dependency.py` 與 `tests/test_gh_math2_unit9_source_dependency_practice.py`。
- 解析規則：
  - 依賴線索有三種：notes 的 `source_dependency`、題幹的「承例題N」，以及 `linked_example`。只有 `linked_example`、沒有前兩種時，視為一般相關例題，不帶入任何資料。
  - 被引用的例題只在同一 curriculum、volume、chapter 內依標題尋找。
  - 帶入的內容只取到第一個「(1)」之前的前置資料，不改寫 DB 題幹。
  - 前置資料出現圖形線索時，必須有已核可的圖片，否則阻擋。
- 阻擋條件：找不到例題、例題重複、例題邊界不確定（單一題且沒有小題）、前置資料沒有數據、必要圖缺失、標題衝突、DB 查詢失敗。阻擋的題目在原題輪替中跳過；直接指定時回傳 409 `TEXTBOOK_EXAMPLE_NOT_STANDALONE`；V3 Phase 1 回傳 unresolved `SOURCE_DEPENDENCY_UNRESOLVED:*`。
- 狀態：open。

| 項目 | 現況 | 處理 |
| --- | --- | --- |
| 單一題例題的邊界需人工確認 | 數學1 單元3 練6（12350）、單元6 練6（12461）、數學4A 舊列（2782）的例題沒有小題，無法安全切出前置資料，現在已被阻擋、不再出題 | 需要由教師標記前置資料範圍的機制；未建立前維持阻擋 |
| 依賴題的答案驗證 | 帶入前置資料的原題全部不自動判分，除非 `fixed_textbook_practice.json` 已有驗證過的答案 | 需要建立答案核對流程；不得把答案硬編進 Checker |
| 已發布的直線 adapter 會輸出「承例題 11：」 | 數學1 單元5 的 `line_equations_adapter` 沿用原例題設定，因為它的 spec 沒有 `source_dependency`，不受 gate 影響 | 若日後以 V3 重建 12424，自含性 gate 會擋下，必須改成自含題幹 |
| 「承上題」 | 數學2 單元11（1564）屬於題內引用，不解析 | 如有跨列需求另案處理 |

## 教材原題 Fallback 與教師預覽的 IMPLEMENTATION_GAP

- 來源：2026-11-03 第二冊 Unit 8 唯讀查核；規範見 [Lean SOP](./SOP_Gencode_V3_Lean.md) §0.2、§6.1，流程見 [PipelineFlow](./SOP_Gencode_AgentSkillV3_PipelineFlow.md) §6.2。
- 狀態：open。以下通用機制均未實作，報告中不得寫成已完成；補實作需另案授權，並依 Impact-Based Testing 驗證。2026-11-03 Unit 8 P0-A／P0-B 只做個案處理，見表中實例欄。

| 缺口 | 現況（位置） | 實例 |
| --- | --- | --- |
| 原題缺必要圖片或資訊時標記不可用 | `_select_textbook_example_for_skill` 不檢查 Stage 1 封板或 required visual（`core/routes/practice.py`） | Unit 8 隨堂練習 10（id 12930）「承例題9」沒有綁定長條圖仍出題。P0-A 已於 2026-11-03 在正式 DB 單筆補綁 12926 長條圖（備份 `backups/math2_unit8_fallback_repair/20261103_233740/`）；重新匯入會遺失。2026-11-18 起，承例題類的題目改由跨題依賴解析器帶入例題的前置資料與圖片，缺圖就阻擋；其他類型缺少必要圖片的檢查仍未實作 |
| 未登錄原題明確標記不可用或未評分 | 不在 `configs/fixed_textbook_practice.json`、也不在 `UNGRADED_SELF_STUDY_SKILLS` 的原題以空答案出題；送出回傳「模組載入錯誤」（不寫紀錄） | Unit 8 全部 35 題。P0-B 已將其四個 Skill 列入 `UNGRADED_NO_VERIFIED_ANSWER_SKILLS`：5001 已驗收送出為未評分、無模組錯誤，5000 待重啟載入；其他未登錄 Skill 仍受影響 |
| 單次練習的學生層級重複控制 | 只有 session 內依 id 循環（`current_textbook_example_id`）；沒有學生層級持久紀錄，一輪後或重新登入即重複 | — |
| Generator 執行失敗時退回原題 | 重試用盡回傳 `_question_delivery_failure_response`，不退回原題 | — |
| 未發布即可供教師預覽 | `/admin/textbook-examples/<id>/v3-preview` 僅限 admin，需 tracker `verified`、`reports/gencode_v3_dryrun` 產物與已註冊 Domain；`/admin/domain-bootstrap/gaps/<gap_id>/preview` 僅限自動 Bootstrap gap，回傳 JSON 樣本，無呈現、圖形或 Checker 試答 | Unit 8 revision_0004 無法在未 Promotion 時預覽 |
