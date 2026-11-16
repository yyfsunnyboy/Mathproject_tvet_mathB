# Known Issues / Technical Debt

## CartesianCoordinateSystem skill-local `check()` 字串比對

- 位置：`skills/vh_數學B1_CartesianCoordinateSystemEstablishment.py` 的 skill-local `check()`
- 現象：仍存在 skill-local 字串比對，未走共用數學等價 checker
- 範圍：不屬於共用 checker 層；與 B1 Chapter 3 無關
- 本輪：不處理、不順手修
- 狀態：deferred

runtime wrapper `check_answer` 在 contract 指向象限 checker 時仍走共用路徑。未對齊的是 skill 本體 `check()`。

## 教材原題 Fallback 與教師預覽的 IMPLEMENTATION_GAP

- 來源：2026-11-03 第二冊 Unit 8 唯讀查核；規範見 [Lean SOP](./SOP_Gencode_V3_Lean.md) §0.2、§6.1，流程見 [PipelineFlow](./SOP_Gencode_AgentSkillV3_PipelineFlow.md) §6.2。
- 狀態：open。以下通用機制均未實作，報告中不得寫成已完成；補實作需另案授權，並依 Impact-Based Testing 驗證。2026-11-03 Unit 8 P0-A／P0-B 只做個案處理，見表中實例欄。

| 缺口 | 現況（位置） | 實例 |
| --- | --- | --- |
| 原題缺必要圖片或資訊時標記不可用 | `_select_textbook_example_for_skill` 不檢查 Stage 1 封板或 required visual（`core/routes/practice.py`） | Unit 8 隨堂練習 10（id 12930）「承例題9」沒有綁定長條圖仍出題。P0-A 已於 2026-11-03 在正式 DB 單筆補綁 12926 長條圖（備份 `backups/math2_unit8_fallback_repair/20261103_233740/`）；重新匯入會遺失 |
| 未登錄原題明確標記不可用或未評分 | 不在 `configs/fixed_textbook_practice.json`、也不在 `UNGRADED_SELF_STUDY_SKILLS` 的原題以空答案出題；送出回傳「模組載入錯誤」（不寫紀錄） | Unit 8 全部 35 題。P0-B 已將其四個 Skill 列入 `UNGRADED_NO_VERIFIED_ANSWER_SKILLS`：5001 已驗收送出為未評分、無模組錯誤，5000 待重啟載入；其他未登錄 Skill 仍受影響 |
| 單次練習的學生層級重複控制 | 只有 session 內依 id 循環（`current_textbook_example_id`）；沒有學生層級持久紀錄，一輪後或重新登入即重複 | — |
| Generator 執行失敗時退回原題 | 重試用盡回傳 `_question_delivery_failure_response`，不退回原題 | — |
| 未發布即可供教師預覽 | `/admin/textbook-examples/<id>/v3-preview` 僅限 admin，需 tracker `verified`、`reports/gencode_v3_dryrun` 產物與已註冊 Domain；`/admin/domain-bootstrap/gaps/<gap_id>/preview` 僅限自動 Bootstrap gap，回傳 JSON 樣本，無呈現、圖形或 Checker 試答 | Unit 8 revision_0004 無法在未 Promotion 時預覽 |
