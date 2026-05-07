# AI 閉環開發與驗收 SOP v0.1

## 1. SOP 目的

本 SOP 用於規範 AI / Codex / Antigravity 在 MathProject 技術型高中版本中協助章節開發的工作方式。

目標不是讓 AI 無限制自動改完整章，而是建立：

inventory → plan → small scoped implementation → tests → report → human approve → next loop

的 controlled development loop。

明確規範：
- AI 可以大量協助盤點、生成、測試與寫報告。
- adaptive scoring、mastery、APR、remediation policy、teacher review policy 仍需人工確認。
- 每輪工作必須可停止、可驗證、可回滾。

## 2. 閉環總原則

1. 小步快跑
2. 每輪只處理一個 phase
3. 每輪只處理少量 problem_type
4. 每輪先盤點再改 code
5. 每輪必須有測試
6. 每輪必須有 summary report
7. 每輪完成後停止，等待人工 approve
8. 不允許 AI 自己連續開下一個 phase
9. 不允許 AI 擴大 scope
10. 不允許 AI 為了通過測試而新增錯誤架構

## 3. 一輪 AI 開發循環標準流程

### Step 1：Read / Inventory

AI 只能讀取指定檔案與資料來源，產出 inventory。
此階段不改 code。

輸出：
- inventory report
- risk list
- candidate problem_type list
- deterministic / handwriting / future_ai_judged 分流表

### Step 2：Plan

AI 產生最小實作計畫。
計畫必須包含：
- 目標
- 修改檔案白名單
- 不可修改檔案
- 測試檔案
- rollback 方式
- closure 標準

### Step 3：Implement

AI 只依 plan 做小範圍修改。
每輪只做：
- 1–3 個 deterministic problem_type
或
- 1 個 handwriting AI-judged 題型
或
- 1 個 adaptive audit / metadata exposure
或
- 1 份 closure 文件

### Step 4：Test

AI 必須執行指定 pytest。
測試結果必須回報：
- command
- passed / failed
- warnings
- failure reason if any

### Step 5：Report

AI 必須產生 summary / closure report。
包含：
- 修改檔案
- 測試結果
- manual smoke 建議
- runtime boundary
- known limitations
- next step

### Step 6：Human Approve

AI 完成後必須停止。
等待人工確認：
- accept
- revise
- rollback
- next phase

## 4. Agent 可做的工作

- 讀 DB / Excel / Markdown / Python 檔案做 inventory
- 對照 skill_curriculum.display_order
- 對照已有 generator / wrapper / route
- 找出 missing problem_type
- 產生 deterministic generator
- 補 validator
- 補 router registry
- 補 isolated helper
- 建立 handwriting payload builder
- 撰寫 AI rubric
- 建立 pytest
- 執行 pytest
- 寫 phase summary / closure summary
- 產出 manual smoke checklist
- 檢查 runtime boundary

## 5. Agent 不可自動做的工作

- 不可無批准修改 adaptive scoring
- 不可無批准修改 mastery / APR
- 不可無批准修改 remediation trigger
- 不可無批准修改 return_to_mainline policy
- 不可把 handwriting 題型塞進 deterministic int-answer allowlist
- 不可把 free-response 題型硬改成 int-answer
- 不可新增假 skill generator 只為了避免 missing module
- 不可改 coverage matrix，除非 phase 明確要求
- 不可一次處理整章所有題型
- 不可大範圍重構 routes / templates / session_engine
- 不可刪除既有報告或 closure summary
- 不可把 expected_paths / expected_row / expected_expansion 顯示給正式學生端
- 不可在測試失敗時自行改 unrelated code

## 6. 標準 Phase 類型

### 6.1 Inventory Phase

目的：
只盤點，不改 code。

輸出：
- chapter inventory report
- skill list
- problem_type list
- deterministic / handwriting / future_ai_judged 分流
- risk list

### 6.2 Deterministic Generator Phase

目的：
補 int-answer / choice-answer 題型。

限制：
- 不改 adaptive scoring
- 不改 handwriting
- 不改 coverage matrix
- 每次只處理少量 problem_type

### 6.3 Handwriting AI-Judged Phase

目的：
處理完整列舉、展開式、推導、畫圖等非單一數字作答。

標準：
- 原 `/practice` 頁
- `answer_type = handwriting`
- `grading_mode = ai_judged_free_response`
- `/analyze_handwriting` rubric
- 不走 `/check_answer`
- 不進 deterministic allowlist

### 6.4 Adaptive Candidate Phase

目的：
註冊 deterministic 或 handwriting candidates。

限制：
- deterministic allowlist 與 handwriting candidate list 分開
- handwriting candidate 先 audit visibility
- 不直接 mastery scoring

### 6.5 Adaptive Audit Phase

目的：
在 adaptive_audit 中暴露候選資訊。

限制：
- visibility-only
- 不計分
- 不影響 fail_streak
- 不觸發 remediation

### 6.6 Closure Phase

目的：
收斂該階段，產生 closure summary。
不改 code。

## 7. 檔案修改白名單規則

每一輪 prompt 必須明確列：
- allowed files
- forbidden files
- tests to run
- report path

若 AI 需要修改白名單外檔案，必須停止並回報，不可自行擴權。

範例：

Allowed:
- `core/vocational_math_b4/generators/<target>.py`
- `core/vocational_math_b4/services/question_router.py`
- `tests/test_<phase>.py`
- `reports/b4_generator_planning/<phase>_summary.md`

Forbidden:
- `/check_answer`
- `/api/adaptive/submit_and_get_next`
- coverage matrix
- unrelated templates
- unrelated routes

## 8. 測試門檻

每輪完成前必須至少跑：

- 新增測試檔
- 相關回歸測試
- allowlist boundary tests
- router canonical tests if generator changed
- handwriting flow tests if handwriting changed
- adaptive audit tests if audit changed

測試回報格式：

修改檔案：
...

測試指令：
`python -m pytest -q ...`

測試結果：
... passed
warnings: ...
failures: none / details

Manual smoke：
...

若測試失敗：
- 不可直接擴大修改
- 先回報 root cause
- 提出最小修正 plan
- 等人工確認或只做與失敗直接相關的修正

## 9. Manual Smoke 標準

每個功能完成後都要有 manual smoke checklist。

deterministic 題型：
- 題幹正確
- 選項唯一
- 答案正確
- explanation 正確
- 下一題正常
- 不出 excluded 題型

handwriting 題型：
- 進原 `/practice` 頁
- 顯示手寫作答區
- 不顯示一般數字輸入框
- `/analyze_handwriting` 被呼叫
- correct / partial / incorrect / needs_review 合理
- 下一題正常
- 題目可參數化變化
- 不暴露 expected answer data

adaptive audit：
- Network response 有 `adaptive_audit` 欄位
- scoring_policy 明確
- 不更新 mastery
- 不更新 APR
- 不觸發 remediation

## 10. Closure 標準

每個 phase closure summary 必須包含：

1. Phase 目的
2. 完成範圍
3. 修改檔案
4. 支援題型 / variants
5. 測試結果
6. manual smoke 結果
7. runtime boundary
8. known limitations
9. Go / No-Go
10. next phase 建議
11. final closure statement

closure 完成後：
- 不再繼續修改該 phase
- 後續需求另開 phase
- 不把 closure phase 跟新功能混在一起

## 11. Rollback 原則

AI 每輪修改前應盡量小範圍。

若失敗：
1. 優先回復本輪修改檔案。
2. 不動上一輪已 closure 的成果。
3. 不用新增 fake generator 掩蓋錯誤。
4. 不用刪測試換取通過。
5. 若需要回復，必須回報：
- 回復哪些檔案
- 為什麼回復
- 哪些成果保留
- 哪些測試重新通過

## 12. Token 節省規則

- prompt 要短
- 每輪只給必要背景
- 優先引用 SOP / report，而不是重貼長歷史
- 指定檔案與測試
- 最後只要求回報修改檔案與測試結果
- 不要求 AI 輸出完整 diff
- 不要求 AI 解釋所有歷史
- 讓 AI 先 inventory，再決定是否改 code
- 大型架構問題才使用高階模型
- 小修與測試優先使用較省 token 的模型

## 13. Human Approval 節點

每一輪結束時，AI 必須停在以下狀態之一：
- READY_FOR_REVIEW
- TEST_FAILED_NEEDS_DECISION
- BLOCKED_NEEDS_HUMAN_INPUT
- CLOSED

AI 不可自行從 READY_FOR_REVIEW 進入下一 phase。

## 14. Chap2 建議啟動流程

請定義 Chap2 第一步：

Prompt 範例：

依照 `docs/系統SOP/教材匯入與技能生成SOP_v0.1.md` 以及 `docs/系統SOP/AI閉環開發與驗收SOP_v0.1.md`，
執行 B4 Chapter 2 inventory phase。
只讀取，不改 code。
請盤點：
- skill_curriculum
- display_order
- textbook_examples / in_class_practice / self_assessment
- existing generators / wrappers / routes
- deterministic / handwriting / future_ai_judged 分流
- risk list
- suggested phases
輸出：
`reports/b4_generator_planning/b4_chap2_inventory.md`

## 15. 與既有 SOP 的關係

本 SOP 不取代：
`docs/系統SOP/教材匯入與技能生成SOP_v0.1.md`

而是補充它：
- 該 SOP 定義 B4 章節開發方法
- 本 SOP 定義 AI agent 如何安全執行該方法
- 兩者需一起使用

## 16. Changelog

v0.1：
- 建立 AI controlled development loop
- 定義 inventory / implement / test / report / approve 循環
- 定義 agent 可做與不可做事項
- 定義 phase 類型
- 定義測試、manual smoke、closure、rollback、token 節省規則
- 定義 Chap2 啟動方式
