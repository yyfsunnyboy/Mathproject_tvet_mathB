# B4 AI出題品質檢查SOP v0.1

## 1. 定位與原則
- `coverage gate` 只代表 skill 有 runtime/review path。
- `quality gate` 才代表學生端題目可用。
- 發版前必須 coverage gate 通過後，再跑 quality gate。

Release 前最低 gate：
1. textbook fidelity gate
2. choice contract gate
3. visual/table payload gate
4. localization gate
5. diversity gate
6. runtime/check_mode consistency gate

## 2. Textbook Fidelity Gate（貼近課本）
規則：
1. 每題型需有 `textbook_alignment_note` 或 `source_style_summary`。
2. 不大量貼課本原文，只保留題型骨架。
3. 不可發明課本主體沒有的主要題型。
4. 課本選擇題優先 `deterministic_choice`。
5. 課本填充題優先 `deterministic_short_answer`。
6. 作圖/補表/推導/開放解釋題分流到：
   - `visual_or_handwriting_ai_checked`
   - `teacher_review`
   - `visibility_only`
7. 找不到 aligned source 時，不得為湊 coverage 硬做新 deterministic 題。

### Chap3 參考（3-1）
- `StatisticalBasicConcepts`：統計意義、流程、敘述/推論、普查/抽查
- `SamplingSurvey`：母群體、樣本、母群體數、樣本數
- `SamplingMethods`：簡單隨機、系統、分層隨機、部落抽樣

對齊重點：
- 具體情境判斷
- 明確選項或明確填答
- 不只問抽象名詞

## 3. Choice Contract Gate
觸發條件（任一成立即視為 choice 題）：
- `answer_input_type=choice`
- `answer_type=choice`
- `runtime_mode=deterministic_choice`
- `question_text` 含「請輸入選項代號」
- `question_text` 含「下列何者」

必須滿足：
1. `choices` 存在且非空
2. `choices` 至少 4 個（是非題除外）
3. 每個選項可前端顯示
4. `answer` 可對應 choices
5. `explanation` 有正解理由
6. `/get_next_question` 不得丟失 `choices`
7. frontend 必須渲染 choices
8. `/check_answer` 支援 alias：`1/2/3/4`、`A/B/C/D`、`a/b/c/d`

禁止：
- 要輸入選項代號但無 choices
- answer=2 但看不到選項
- 選項藏在題幹而 route 無 choices 欄位

## 4. Visual/Table Payload Gate
若題幹包含：
- 附圖、下圖、圖表、觀察圖、直方圖、折線圖、長條圖、圓形圖

payload 必須至少含一種：
- `image_base64`
- `visual_aids`
- `chart_spec`

若題幹包含：
- 下表、表格、補齊、次數分配表、累積次數

payload 必須至少含一種：
- `table`
- `visual_aids`
- `image_base64`

表格題必須有：
- `table_title`
- `headers`
- `rows`
- 中文欄位
- 補表欄位需以 `null/□/空白` 明示
- `expected_answer_schema` 或 `rubric`

禁止：
- 題幹說附圖但無圖
- 題幹說下表但無表
- `expected_answer` 空白且無 rubric（非 review/visibility 題）

## 5. Diversity Gate
每 skill/family 至少抽樣 10 題，統計：
- `unique problem_type_id`
- `unique scenario_family`
- `unique scenario_id`
- `question_pattern_hash`
- `visual_asset_hash`
- `table_spec_hash`

規則：
1. 一般 skill 至少 2 種 pattern
2. conceptual choice 至少 2-3 種情境
3. `SamplingMethods` 應覆蓋多種抽樣法
4. 圖形題 sample image/chart spec 不可高度重複
5. 單一 review shell 必須在 report 說明原因

門檻：
- `repeated_question_text_ratio > 0.7` → `MAJOR`
- `visual_asset_hash` 全相同 → `MAJOR`
- `scenario_family` 只有 1 且無理由 → `MAJOR`
- 下一題固定同句 → `BLOCKING`

## 6. Localization Gate（全中文）
必須中文化欄位：
- `question_text`、`choices`、`explanation`、`message`
- `table_title`、`headers`
- `visual_aids.title/caption/alt_text`
- chart title / axis labels / rubric

禁止英文模板殘留：
- Read the
- Frequency Table
- Histogram
- Frequency
- Value
- interval
- count
- total frequency
- Cumulative Frequency
- chart type by purpose
- review shell

## 7. Runtime / Check-Mode Consistency Gate
1. `deterministic_choice` / `deterministic_short_answer`
- `check_mode=deterministic_auto_checked`
- `grading_mode=deterministic`
- `answer` 不得空
- 正答判對、錯答判錯

2. `visual_or_handwriting_ai_checked`
- `check_mode=visual_ai_checked` 或 `handwriting_ai_checked`
- `grading_mode=ai_assisted_review`
- `requires_handwriting` / `visual_backed` 要存在
- `/check_answer` 必須 guard 到 AI

3. `teacher_review`
- `check_mode=review_mode`
- `grading_mode=teacher_review`
- 必須有 rubric 或 `expected_answer_schema`
- `/check_answer` 不得 deterministic 比對

4. `visibility_only`
- `check_mode=review_mode`
- `grading_mode=visibility_only`
- 必須有 friendly message
- 不得回生硬 not-enabled error

禁止：
- choice 題誤走 review
- review 題被 deterministic 比對
- 顯示 `...not enabled in current deterministic runtime` 給學生

## 8. AI Judge QA（第二層）
- AI judge 不取代 rule-based gate。
- 用於判斷：課本貼合、題意清楚、可作答性、題型分類、難度、是否過度開放、是否僅換數字。

Input：
- `skill_id`、`problem_type_id`、`scenario_family`
- `question_text`、`choices`、`answer`、`explanation`
- `runtime_mode`、`check_mode`、`grading_mode`
- visual/table metadata summary
- `textbook_alignment_note`

Output JSON：
```json
{
  "is_answerable": true,
  "textbook_fidelity_score": 4,
  "student_clarity_score": 4,
  "runtime_mode_correct": true,
  "missing_choices": false,
  "missing_visual_or_table": false,
  "too_open_ended_for_deterministic": false,
  "too_repetitive": false,
  "suggested_fix": ""
}
```

建議門檻：
- `textbook_fidelity_score >= 4`
- `student_clarity_score >= 4`
- `is_answerable=true`
- `runtime_mode_correct=true`

## 9. QA Report 標準
每次題型修補後必須輸出 report，包含：
- sampled skills
- sample count
- rule-based QA result
- diversity QA result
- localization result
- AI judge result（若執行）
- visual/table sample artifact paths
- failed items table
- repair decision

failed items table 欄位：
- `skill_id`
- `problem_type_id`
- `issue_type`
- `severity` (`BLOCKING/MAJOR/MINOR`)
- `sample_question_text`
- `reason`
- `suggested_fix`
- `fixed_in_this_phase`

## 10. B4 Chap3 已發生案例（警示）
1. `StatisticalBasicConcepts`：抽象問法過多 → 改為流程/普查抽查/敘述推論情境題
2. `SamplingSurvey`：choice 誤走 review 路徑 → 需明確分流 deterministic vs review
3. Choice payload：要求輸入代號但無 choices → 修 route payload + frontend rendering + alias checker
4. `CumulativeFrequencyTablesAndGraphs`：題幹有下表但 payload 無表 → 補 table/visual/image
5. `DataOrganizationAndCharts`：只出開放題且重複 → 增 `chart_type_selection_by_purpose`、`data_organization_first_step`
6. `StatisticalChartReading`：附圖無圖、answer 空、重複題幹 → 增 deterministic_choice + visual-backed review shell

## 11. 執行順序（Release）
1. Coverage gate 通過
2. Quality gate（本 SOP）通過
3. 回歸測試通過
4. 產出 QA report
5. 才能標記 release-ready

## 12. 適用範圍
- B4 為本 SOP 首次完整落地。
- B1/B2/B3 與後續冊數應沿用同規則與同報告格式。
