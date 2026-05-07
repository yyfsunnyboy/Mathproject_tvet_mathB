# Phase 5F-C：Tree Diagram Free-Response Integration Design

## 1. 設計目的

- Phase 5F-B 已有 isolated text-answer judge。
- 目前缺的是「如何安全接入學生作答流程」。
- `tree_diagram_listing` 不適合 deterministic int-answer。
- 本階段目標是設計 free-response route / UI / grading / teacher review 的整合方式。
- 本階段不實作，只做設計。

## 2. 現有能力摘要

Phase 5F-B 已完成：

- `build_tree_diagram_listing_payload(...)`
- `parse_tree_diagram_text_answer(...)`
- `judge_tree_diagram_text_answer(...)`
- 支援 `fixed_stage_binary_tree`
- 支援 `early_stopping_game`
- 可判斷 `correct` / `partial` / `incorrect` / `needs_review`
- 可偵測 count-only answer
- 可列出 `missing_paths` / `extra_paths` / `duplicated_paths`
- 可辨識 `early_stopping_game` 的固定三場錯誤

目前未完成：

- 尚未接前端 UI
- 尚未接 API route
- 尚未接 adaptive flow
- 尚未接 handwriting / image
- 尚未接 teacher review dashboard

## 3. Integration 原則

- `tree_diagram_listing` 不走 `/check_answer` int-answer。
- `tree_diagram_listing` 不加入 `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST` 的 deterministic path。
- `tree_diagram_listing` 應走新的 `grading_mode = ai_judged_free_response`。
- 第一版只支援文字列舉 `textarea`。
- 手寫圖像延後到後續 Phase。
- `partial` / `needs_review` 不應直接視為普通答錯；應有 teacher review / learning feedback 的處理。
- 此 runtime 是 deterministic B4 unit practice 的旁支，不取代已完成的 int-answer runtime。

## 4. 建議入口設計

### Option A：獨立 Tree Diagram Practice Page

例如：

```text
/free_response_practice?curriculum=vocational&volume=數學B4&chapter_id=1&problem_type=tree_diagram_listing
```

優點：

- 最安全，不污染 `adaptive_practice_v2`。
- 可先只讓教師測。
- UI 可專門設計 `textarea` / feedback。

缺點：

- 與現有單元練習分離。
- 暫時不參與 adaptive sequencing。

### Option B：在 adaptive_practice_v2 中支援 grading_mode

當題目 payload 的 `grading_mode = ai_judged_free_response` 時，前端改顯示 `textarea`。

優點：

- 學生體驗整合。
- 未來可混入 guided progression。

缺點：

- 需要改前端和 submit flow。
- `partial` / `needs_review` 對 adaptive scoring 會複雜。
- 較容易破壞現有 int-answer flow。

### Option C：Teacher QA only / Admin Preview

只在教師後台或測試頁面顯示 tree diagram 題型。

優點：

- 最低風險。
- 適合先驗證 judge 品質。

缺點：

- 學生無法使用。

建議：

- 第一階段採 Option A 或 C，不建議直接採 Option B。
- Phase 5F-D 先做獨立 `free_response_practice` route 或 teacher preview route。

## 5. 前端 UI 設計

第一版 UI 只支援文字列舉。

頁面需要顯示：

- 題幹
- 提示：「請用樹狀圖或完整列舉方式寫出所有可能情形。本版本請先用文字列舉，例如：甲甲、甲乙甲、...」
- `textarea`
- 送出按鈕
- AI judge result 區塊

`textarea` placeholder 範例：

`early_stopping_game`：

```text
甲甲、甲乙甲、甲乙乙、乙甲甲、乙甲乙、乙乙
```

`fixed_stage_binary_tree`：

```text
正正正、正正反、正反正、正反反、反正正、反正反、反反正、反反反
```

結果顯示：

- `status`
- `score`
- `missing_paths`
- `extra_paths`
- `duplicated_paths`
- `feedback`
- `teacher_review_needed`

註記：

- 目前不顯示手寫畫布。
- 不要要求學生只輸入總數。

## 6. 後端 Route 設計

本段僅為建議 API，不在本階段實作。

### 6.1 取得 free-response 題目

```text
GET /api/free_response/tree_diagram/question?variant=early_stopping_game
```

Response:

```json
{
  "problem_type_id": "tree_diagram_listing",
  "grading_mode": "ai_judged_free_response",
  "variant": "early_stopping_game",
  "question_text": "...",
  "expected_count": 6,
  "accept_text_listing": true,
  "accept_handwriting_tree": false,
  "requires_listing_or_tree": true
}
```

注意：

- 開發模式可回傳 `expected_paths` 以供 debug。
- 正式學生模式不應直接回傳 `expected_paths`。

### 6.2 送出 free-response 文字答案

```text
POST /api/free_response/tree_diagram/submit
```

Request:

```json
{
  "variant": "early_stopping_game",
  "answer_text": "甲甲、甲乙甲、甲乙乙、乙甲甲、乙甲乙、乙乙",
  "student_id": "...",
  "session_id": "...",
  "question_id": "..."
}
```

Response:

```json
{
  "status": "correct",
  "score": 1.0,
  "expected_count": 6,
  "detected_count": 6,
  "missing_paths": [],
  "extra_paths": [],
  "duplicated_paths": [],
  "feedback": "列舉完整，且符合題目規則。",
  "teacher_review_needed": false
}
```

## 7. Grading 與 adaptive scoring 邊界

第一階段不要直接影響 adaptive mastery。

建議只記錄：

- `correct` / `partial` / `incorrect` / `needs_review`
- `score`
- `teacher_review_needed`

若未來要接 adaptive：

- `correct` 可視為通過。
- `partial` 可視為半對或需補救。
- `needs_review` 不應自動扣 mastery，應等待教師確認。
- count-only answer 應為 `partial`，不應 full correct。

在 Phase 5F-D 之前，不要把此結果寫入既有 int-answer grading pipeline。

## 8. Teacher review / audit log 設計

需要保存：

- `problem_type_id`
- `variant`
- `question_text`
- `expected_count`
- `expected_paths` hash 或 debug-only snapshot
- `student_answer_text`
- `judge_result_json`
- `status`
- `score`
- `teacher_review_needed`
- `teacher_override_status`
- `teacher_override_comment`
- `created_at`

teacher override 狀態：

- `accepted`
- `corrected_to_partial`
- `corrected_to_incorrect`
- `needs_followup`

teacher override 是後續 Phase，不在本階段實作。

## 9. 安全與品質邊界

- 不處理學生個資之外洩。
- 不把 `expected_paths` 暴露給正式學生端。
- `needs_review` 時避免給過度肯定回饋。
- AI / parser 信心低時應保守。
- 手寫辨識未接入前，不接受 image-only 作答為 automatic correct。
- free-response judge 的 feedback 應簡短、針對漏列或規則誤解，不要長篇教學。

## 10. 與現有 Phase 5E learning path 的關係

- Phase 5E-A guided progression 已處理 int-answer 題型的課本順序。
- `tree_diagram_listing` 暫不混入 guided progression。
- 未來可在 AdditionPrinciple / MultiplicationPrinciple 之後，作為 optional free-response activity。
- 不應在現有 `adaptive_practice_v2` 中突然插入，除非前端與 `grading_mode` 已準備完成。
- 若要納入學習路徑，建議作為 teacher-assigned activity 或 optional checkpoint。

## 11. Pilot 策略

### Stage 1：Teacher-only QA

- 使用獨立 route 或 admin preview。
- 教師輸入標準答案、錯誤答案、漏列答案，檢查 judge result。

### Stage 2：Small supervised student trial

- 學生使用文字列舉作答。
- 教師抽查 `partial` / `needs_review`。
- 不接 handwriting。

### Stage 3：Handwriting / image support

- 加入畫布或圖片上傳。
- 先辨識 `detected_paths`，再交給 judge。
- 教師審核低信心答案。

## 12. 後續實作拆分

- Phase 5F-D：`free_response_practice` route + `textarea` UI
- Phase 5F-E：free-response submit API using `judge_tree_diagram_text_answer`
- Phase 5F-F：teacher review log / override schema
- Phase 5F-G：optional integration into B4 Chapter 1 learning path
- Phase 5F-H：handwriting / image recognition support

## 13. Go / No-Go 準則

### 可進 Phase 5F-D 若：

- judge prototype 測試通過。
- integration design 已決定先採 Option A 或 C。
- 不會影響 int-answer runtime。
- 教師接受先用文字列舉版。

### 不可直接進 adaptive integration 若：

- `partial` / `needs_review` 的 scoring 還沒定義。
- 前端仍只有數字輸入框。
- `expected_paths` 會暴露給學生。
- teacher review 沒有紀錄方案。
- handwriting 辨識尚未測試。

## 14. 停止線

- 本階段只做 integration design。
- 不改前端。
- 不改 route。
- 不接 API。
- 不接 adaptive。
- 不接 handwriting。
- 不接 teacher review DB。
- 不把 `tree_diagram_listing` 放入 deterministic allowlist。
