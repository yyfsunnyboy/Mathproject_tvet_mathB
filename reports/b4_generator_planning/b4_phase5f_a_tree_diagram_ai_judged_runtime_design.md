# Phase 5F-A：Tree Diagram AI-Judged Runtime Design

## 1. 設計目的

- `tree_diagram_listing` 是 B4 Chapter 1 排列組合的重要課本題型。
- 題目本身可以文字化，不一定需要圖片。
- 但學生答案不是單一整數，而是樹狀圖、分支圖或完整列舉。
- 因此不適合 deterministic int-answer runtime。
- 本階段目標是設計 AI-judged free-response / handwriting checked runtime。
- 本階段只做設計，不修改現有 deterministic runtime。

## 2. 為什麼不能用 int-answer

- 正確答案不只是總數。
- 題目要求「用樹狀圖描述」或「列出所有可能情形」。
- 學生只寫總數，例如 `6` 或 `8`，不能算完整正確。
- 系統需要判斷是否列舉完整、是否漏列、是否多列、是否重複、是否理解提前停止條件，以及是否符合樹狀圖或完整列舉要求。

`tree_diagram_listing` 應保留在 deterministic excluded set，不應直接接入 `check_answer` int path。

## 3. 第一批支援 variant

### 3.1 fixed_stage_binary_tree

代表題：

投擲一枚均勻硬幣連續三次，試用樹狀圖描述所有可能情形。

數學結構：

- 固定 3 階段
- 每階段 2 種結果：正、反
- 總數 8

`expected_paths`：

- 正正正
- 正正反
- 正反正
- 正反反
- 反正正
- 反正反
- 反反正
- 反反反

學生常見錯誤：

- 只寫 8 種，沒有列舉或畫圖
- 只列到兩次硬幣
- 漏列部分路徑
- 重複列舉
- 分支層數不足

### 3.2 early_stopping_game

代表題：

甲、乙兩隊比賽，每場沒有平手，先贏兩場者勝。試問共有多少種勝負情形？試以樹狀圖描述所有可能情形。

數學結構：

- 每場 2 種結果：甲勝、乙勝
- 先贏兩場即停止
- 可能 2 場結束，也可能 3 場結束
- 總數 6

`expected_paths`：

- 甲甲
- 甲乙甲
- 甲乙乙
- 乙甲甲
- 乙甲乙
- 乙乙

判斷重點：

- 若學生列出固定三場的 8 種，例如甲甲甲、甲甲乙等，代表沒有理解「先贏兩場即停止」，應判為 `partial` 或 `incorrect`。
- 若學生只列 4 種，例如甲甲、甲乙甲、乙乙、乙甲乙，則漏掉甲乙乙與乙甲甲，應判為 `partial`。

## 4. 題目資料 schema 設計

範例 schema：

```json
{
  "problem_type_id": "tree_diagram_listing",
  "grading_mode": "ai_judged_free_response",
  "variant": "fixed_stage_binary_tree | early_stopping_game",
  "question_text": "",
  "expected_count": 8,
  "expected_paths": [],
  "path_labels": [],
  "stopping_rule": null,
  "accept_text_listing": true,
  "accept_handwriting_tree": true,
  "requires_listing_or_tree": true
}
```

設計說明：

- `expected_count` 可用來輔助判斷，但不能作為唯一評分依據。
- `expected_paths` 是 AI judge 或 rule-based parser 的主要參考。
- `variant` 決定判斷規則。
- `grading_mode` 必須與 `deterministic_int_answer` 分開。

## 5. 學生答案格式

### 5.1 文字列舉

例如：

```text
甲甲、甲乙甲、甲乙乙、乙甲甲、乙甲乙、乙乙
```

或：

```text
正正正、正正反、正反正、正反反、反正正、反正反、反反正、反反反
```

### 5.2 簡單階層文字

例如：

```text
甲：
  甲
  乙：
    甲
    乙
乙：
  乙
  甲：
    甲
    乙
```

### 5.3 手寫樹狀圖 / 圖片

- 學生可用畫布或上傳圖片。
- 系統需先辨識路徑，再交給 AI judge 判斷。
- 若辨識不可靠，回傳 `needs_review`。

## 6. AI judging rubric

共同檢查項：

- 是否有列出或畫出所有終止路徑
- `detected_count` 是否與 `expected_count` 一致
- `missing_paths` 是否為空
- `extra_paths` 是否為空
- `duplicated_paths` 是否為空
- 是否符合題目要求：樹狀圖或完整列舉
- 是否只寫總數

`fixed_stage_binary_tree` 追加檢查：

- 是否有固定 3 層
- 是否每層皆有正／反兩種分支
- 是否列出 8 條長度 3 的路徑

`early_stopping_game` 追加檢查：

- 是否理解先贏兩場即停止
- 是否列出長度 2 與長度 3 的終止路徑
- 是否沒有列出不該繼續的路徑
- 是否沒有把固定三場 8 種誤當成答案

## 7. AI judge output schema

範例 schema：

```json
{
  "status": "correct | partial | incorrect | needs_review",
  "score": 0.0,
  "expected_count": 6,
  "detected_count": 0,
  "expected_paths": [],
  "detected_paths": [],
  "missing_paths": [],
  "extra_paths": [],
  "duplicated_paths": [],
  "count_only_answer": false,
  "main_issue": "",
  "feedback": "",
  "teacher_review_needed": false,
  "confidence": 0.0
}
```

`status` 說明：

- `correct`：完整列出或畫出所有 `expected_paths`，無重大漏列或多列。
- `partial`：知道總數但未列舉；或列舉方向正確但漏少數項；或樹狀圖結構大致正確但不完整。
- `incorrect`：結構錯誤、規則理解錯誤、列出固定三場 8 種但題目是先贏兩場停止。
- `needs_review`：手寫圖辨識不清、AI 信心不足、答案格式無法可靠解析。

## 8. 評分案例

### fixed_stage_binary_tree

學生答案：「8 種」

- `status`: `partial`
- `main_issue`: 只寫總數，未用樹狀圖或完整列舉。

學生答案漏掉「反反反」

- `status`: `partial`
- `missing_paths`: `["反反反"]`

學生完整列出 8 種

- `status`: `correct`

### early_stopping_game

學生答案：「6 種」

- `status`: `partial`
- `main_issue`: 只寫總數，未列出所有勝負情形。

學生答案：

```text
甲甲、甲乙甲、乙乙、乙甲乙
```

- `status`: `partial`
- `missing_paths`: `["甲乙乙", "乙甲甲"]`

學生答案列出 8 種固定三場：

```text
甲甲甲、甲甲乙、甲乙甲、甲乙乙、乙甲甲、乙甲乙、乙乙甲、乙乙乙
```

- `status`: `incorrect` 或 `partial`
- `main_issue`: 未理解先贏兩場即停止，列出不該繼續的路徑。

學生答案：

```text
甲甲、甲乙甲、甲乙乙、乙甲甲、乙甲乙、乙乙
```

- `status`: `correct`

## 9. 前端需求

- 題目頁需支援 `grading_mode = ai_judged_free_response`。
- 不能只顯示普通數字輸入框。
- 第一版可先支援文字列舉輸入。
- 後續支援手寫畫布或圖片上傳。
- 送出後走 AI judge，而不是普通 `check_answer`。
- 顯示 AI feedback：`correct` / `partial` / `incorrect` / `needs_review`、`missing_paths`、`feedback`。
- `needs_review` 時提示教師檢查。

## 10. 後端需求

- 新增或規劃 `grading_mode = ai_judged_free_response`。
- `tree_diagram_listing` 仍不走 `deterministic_int_answer`。
- 新增 AI judge function：`judge_tree_diagram_response(...)`。
- 儲存 `original_text_answer`、`handwriting_image_path` 或 `image_id`、`ai_judge_result_json`、`teacher_override_status`。
- 需要支援 teacher review / audit log。
- 第一版可先只做文字列舉版，降低風險。

## 11. 與現有 deterministic runtime 的關係

- `tree_diagram_listing` 繼續保留在 excluded deterministic set。
- 不加入 `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST` 的 int-answer 路徑。
- 未來應建立 AI-judged allowlist 或 free-response runtime。
- 不影響 Phase 5C 已完成的 deterministic 題型。
- 不影響 Guided Progression 的 int-answer 題型。

## 12. Pilot 建議

第一階段：

- 教師端測試。
- 只接受文字列舉答案。
- 不先開放手寫圖像判斷。

第二階段：

- 加入手寫畫布或圖片上傳。
- AI 判斷結果由教師抽查。

第三階段：

- 小規模學生 pilot。
- 只在教師監看下使用。
- `needs_review` 的題目進入教師檢查清單。

不建議：

- 一開始直接無監督大量使用手寫 AI 判斷。

## 13. 後續實作階段

- Phase 5F-B：`tree_diagram_listing` text-answer generator / payload schema
- Phase 5F-C：rule-based parser + AI judge prompt 設計
- Phase 5F-D：front-end free-response text input path
- Phase 5F-E：handwriting / image upload support
- Phase 5F-F：teacher review / override / audit log
- Phase 5F-G：小規模 pilot

## 14. 停止線

- 本階段只做設計文件。
- 不改 deterministic runtime。
- 不接入 int-answer。
- 不處理完整二項式展開。
- 不處理巴斯卡推導。
- 不處理所有 free-response 題型。
- 只設計 `tree_diagram_listing` 的 AI-judged runtime。
