# B1 Skill 完成鼓勵 MsgBox 報告

**日期**：2026-11-22  
**範圍**：僅 B1 題型掌握制完成互動  
**狀態**：實作完成，等待人工驗收

---

## 1. 原本自動跳轉發生的位置與觸發原因

- 位置：`templates/index.html` → `handleCorrectAnswer()` → `PracticeCorrectAnswerFlow` 的 `onConfirm`。
- 行為：答對後先顯示成功 MsgBox，按「確定」後 **`setTimeout(loadQuestion, 500)` 自動載入下一題**。
- 原因：共用正確作答流程把「答對」等同「繼續下一題」，沒有 Skill 完成閘門，也沒有「下一單元」選擇。
- 本輪改動後：B1 在 `skill_just_completed` 時**不再自動 `loadQuestion`**，改顯示完成鼓勵 MsgBox。

## 2. 修改後 MsgBox 的觸發條件

後端 `build_skill_completion_payload` 同時滿足：

1. B1 題型掌握制 Skill  
2. 本次答題前 `was_complete_before = false`  
3. 答題交易 **已成功 commit** 且 mastery 寫入已嘗試  
4. 寫入後 `X = Y` 且 `Y > 0`  

才回傳 `skill_just_completed = true`。

前端另要求 `progress_mode === 'problem_type_mastery'`，並以 `question_uid` 去重，避免同一筆提交重複彈出。

不觸發：答錯、同型重複答對、AI 提示後未獨立驗證、已完成後重練、儲存失敗、頁面重整（無 check_answer 轉換旗標）。

## 3. 修改的 Route／JavaScript／Template

| 檔案 | 變更 |
|---|---|
| `core/practice_type_mastery.py` | `resolve_next_b1_practice_skill`、`build_skill_completion_payload` |
| `core/routes/practice.py` | `_emit_check_result` 回傳 `skill_just_completed`／下一 Skill／dashboard URL |
| `core/practice_student_payload.py` | 允許相關進度欄位 |
| `templates/index.html` | `#skillCompletionModal`、`showSkillCompletionModal`、`maybeShowB1SkillCompletion`；`handleCorrectAnswer(payload)` |
| 測試腳本／契約測試 | 字串斷言對齊 |

## 4. 完成狀態是否正確持久化

是。完成判定讀的是 DB 中 `student_problem_type_mastery` 聚合結果；`skill_just_completed` 僅在 commit 成功後計算。未持久化時即使記憶體看似完成也不慶祝。

## 5. 按鈕跳轉與停留

| 按鈕 | 行為 |
|---|---|
| 繼續挑戰下一個單元 | 有 `next_skill_url` 才導向下一 B1 Skill |
| （無下一單元時主按鈕改）返回學習儀表板 | 導向 `/dashboard` |
| 留在目前單元 | 關閉 Modal，保留 4/4 顯示，不跳轉、不自動換題 |

## 6. 桌面／iPad 顯示

- 沿用既有 `.modal-overlay`／`.modal-content`／`.modal-button` 樣式（非 `alert()`）。
- 未新增佔據手寫區的固定進度卡；Modal 為 overlay。
- 真人桌面／iPad 視覺仍需人工驗收。

## 7. 測試通過數量

| 套件 | 結果 |
|---|---|
| `scripts/test_b1_skill_completion_msgbox.py` | **16/16 PASS** |
| `tests/test_unified_correct_answer_flow.py` 等受影響契約測試 | 已對齊並通過本輪相關斷言 |

證據：`reports/gencode_closed_loop/b1_skill_completion_msgbox_latest.json`

## 8. 是否影響 B2～B4

否。僅 `progress_mode === 'problem_type_mastery'`（B1）走完成 MsgBox；非 B1 仍走原 `loadQuestion` 流程。

---

**核心原則已落地：完成所有題型 → 鼓勵 MsgBox → 學生主動選擇下一步。停止等待人工驗收。**
