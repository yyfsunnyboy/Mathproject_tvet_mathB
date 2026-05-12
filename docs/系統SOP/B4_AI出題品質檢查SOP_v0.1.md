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
### 5.1 題目不可重複性過高原則
1. 同一 `skill` 不可只用 2~3 個固定題幹輪替。
2. 同一題幹不可連續出現。
3. 不可只換數字就視為不同題型。
4. 不可只有 `question_text` 局部替換，但 `scenario_family` / `scenario_id` / `problem_type_id` 不變。
5. 若某 `skill` 因課本 fidelity 限制只能有單一 review shell，必須在 QA report 明確標註 `accepted_reason`，不可默認通過。

### 5.2 自動抽樣門檻（Release 前強制）
每個 `skill` 或 `family` 進入 release 前，必須自動抽樣檢查。

- 每個 `skill` 至少抽樣 20 題。
- `unique_question_text_count >= 6`（明確單一 review shell 可例外）。
- `unique_scenario_id_count >= 6`（明確單一 review shell 可例外）。
- `unique_question_pattern_hash_count >= 4`。
- `repeated_question_text_ratio <= 0.5`。
- `consecutive_duplicate_count = 0`。
- deterministic practice `skill` 至少應有 2 個以上 `scenario_family` 或 6 個以上 `scenario_id`。

未達門檻判定：
- deterministic skill：`MAJOR`，通常 `requires_repair=yes`。
- review / visibility shell：`MAJOR` 或 `accepted_with_reason`，需在 report 說明。
- 若連續兩題完全相同：`MAJOR`。
- 若學生端實測「下一題」仍一直相同：`BLOCKING` 或 `MAJOR`（依是否影響作答判定）。

### 5.3 Scenario Pool 規則
generator 必須有可檢查 scenario pool。每題 payload 應包含：

- `problem_type_id`
- `scenario_family`
- `scenario_id`
- `question_pattern_id` 或可由 `question_text hash` 推得
- `textbook_alignment_note` 或 `source_style_summary`

若沒有 `scenario_id`，QA gate 必須使用 `question_pattern_hash` 替代，但 report 應標示 metadata 不足。

### 5.4 Route 層避免連續同題
若 route / session 有最近題目紀錄，應避免：

- same `question_text`
- same `scenario_id`
- same `problem_type_id` + same `scenario_id`

若目前沒有 session history，也至少要在 generator 測試中保證隨機抽樣不會高度集中於同一題。

### 5.5 圖形 / 表格題 Diversity
除了文字多樣性，圖形題還要檢查：

- `visual_asset_hash`
- `chart_spec_hash`
- `table_spec_hash`
- `visual_asset_type`
- chart title / axis labels
- data pattern

要求：
1. 圖形不可完全相同。
2. 不可只是換標題但圖形資料結構完全相同。
3. 同一 visual family 至少要有 2 種 data pattern。
4. 若只有單一圖形模板，必須在 report 說明，並列為 `MAJOR` 或 `accepted_with_reason`。

### 5.6 Parameterized Diversity Gate（數字不可固定）
#### 題目不可固定數字原則
1. 題目不可只固定一組數字反覆出現。
2. 題目不可只是同一題幹、同一數字、同一答案重複輪播。
3. 在不違反 textbook fidelity 的前提下，數字參數、情境參數、選項順序、干擾選項應可控變化。
4. 參數化不是亂創新題型；題型骨架仍必須貼近課本例題。
5. 若課本例題本來數量少，仍需在同一課本骨架內變化：
   - 人數、抽樣數、間距、層別人數、樣本比例
   - 場景名稱、問法角度、選項順序、distractors

#### Textbook-bounded parameterization 原則（Chap3 SamplingMethods）
允許骨架：
- 簡單隨機抽樣：抽籤、摸彩券、編號後隨機抽
- 系統抽樣：每隔固定數量抽取、`k = 母體數 / 樣本數`
- 分層隨機抽樣：依性別/年級/收入/科別比例抽樣
- 部落抽樣：抽班級/社區/城市/部門等群組

允許變化：
- `N` 母體數、`n` 樣本數、`k` 抽樣間距、起始編號
- 各層人數、總抽樣人數
- 場景文字、選項順序、干擾選項

禁止：
- 為了變化而加入課本外新奇情境
- 混入其他 skill 題型
- 把 `SamplingSurvey` 的母群體/樣本辨識混入 `SamplingMethods`
- 把 `OpinionPollInterpretation` 的民調偏誤評論混入 `SamplingMethods`
- 把統計量計算題混入抽樣方法

#### 參數化 metadata 要求
凡是參數化題型，payload 應包含：
- `parameter_signature`
- `parameters.template_id`
- `parameters.numeric_params`
- `parameters.context_params`

若無法直接加入 `parameters`，至少要可由 payload 或 QA script 推得：
- `numeric_tuple`
- `context_signature`
- `question_pattern_hash`

#### Parameterized diversity 抽樣門檻（Release 前）
每個參數化 family 至少抽樣 30 題，檢查：
- `unique_question_text_count`
- `unique_scenario_id_count`
- `unique_parameter_signature_count`
- `unique_numeric_tuple_count`
- `repeated_question_text_ratio`
- `repeated_parameter_signature_ratio`
- `consecutive_duplicate_count`
- `consecutive_same_numeric_tuple_count`

建議標準：
- `unique_parameter_signature_count >= 15 / 30`
- `unique_numeric_tuple_count >= 10 / 30`
- `repeated_parameter_signature_ratio <= 0.5`
- `consecutive_duplicate_count = 0`
- `consecutive_same_numeric_tuple_count = 0`

若題型本身較小，需在 report 標明：
- `textbook_limited_scope=true`
- `accepted_reason`
- 但仍不可連續同題或連續同數字。

#### 參數化答案一致性 Gate（SamplingMethods）
系統抽樣間距題：
- `N % n == 0`
- `k = N / n`
- `answer = k`
- `choices` 包含 `k`
- `explanation` 說明 `k = N / n`

分層比例分配題：
- `total = sum(layers)`
- `answer = sample_total × target_layer_count / total`
- `answer` 必須為整數，或題目需明確允許分數/小數
- `choices` 包含 `answer`
- `explanation` 說明比例計算

所有參數化選擇題：
- `choices` 不得重複
- `distractors` 不得等於 `answer`
- `answer` 必須對應 `choices`
- `/check_answer` 正答判對、錯答判錯

### 5.7 Level 1 Global Consecutive Duplicate Guard
#### Level 1 全域相鄰避重原則
1. Level 1 bare skill general practice 不得連續出現相同題目。
2. 不得只靠 generator 隨機；route/session 層也必須有相鄰避重機制。
3. 同一 skill 下一題應避免與上一題相同：
   - `question_text`
   - `scenario_id`
   - `parameter_signature`
   - `question_pattern_id`
   - `table_spec_hash`
   - `chart_spec_hash`
   - `visual_asset_hash`
4. 若新題與上一題任一核心識別完全相同，route 層應重抽。
5. 建議最多 retry 3 次。
6. 若 retry 後仍無法避開，才 fallback，且 report 必須記錄 fallback reason。
7. fallback 不得放出 open-ended review 題到 Level 1 default。

#### 適用範圍
適用於：
- `deterministic_choice`
- `deterministic_short_answer`
- `visual_reading_with_short_answer`
- mixed deterministic/review skill 的 Level 1 default path

至少涵蓋 Chap3：
- `StatisticalBasicConcepts`
- `SamplingSurvey`
- `SamplingMethods`
- `DataOrganizationAndCharts`
- `StatisticalChartReading`
- `CumulativeFrequencyTablesAndGraphs`
- `FrequencyDistributionTableConstruction`
- `HistogramsAndFrequencyPolygons`
- `CentralTendencyMeasures`
- `DispersionMeasures`
- `WeightedMean`
- `VarianceAndStandardDeviation`
- `LinearTransformationOfData`
- `NormalDistributionAndEmpiricalRule`

後續 B1/B2/B3 也應沿用。

#### metadata 要求
為支援相鄰避重，payload 應盡量提供：
- `problem_type_id`
- `scenario_family`
- `scenario_id`
- `parameter_signature`
- `question_pattern_id`
- `table_spec_hash`
- `chart_spec_hash`
- `visual_asset_hash`

若無法提供上述 metadata，至少 QA/route 可使用 `question_text hash` 作為 fallback。

#### 不得破壞 Level 1 no-open-ended gate
相鄰避重時，不得因 retry/fallback 使 Level 1 default 主動出現開放式題：
- 請說明
- 請簡述
- 請討論
- 簡述理由
- 提出理由
- 可能有哪些偏誤
- 是否具有代表性
- 提出改善方式

除非明確指定：
- `teacher_review`
- `review_only`
- review 題 `problem_type_id`
- `handwriting_ai_checked`
- `visual_ai_checked`

#### QA 抽樣門檻（Level 1）
每個 Level 1 skill release/repair 後，至少抽樣 20 題，檢查：
- `consecutive_duplicate_question_text_count`
- `consecutive_duplicate_scenario_id_count`
- `consecutive_duplicate_parameter_signature_count`
- `consecutive_duplicate_table_spec_hash_count`
- `consecutive_duplicate_chart_spec_hash_count`
- `fallback_count`
- `retry_count`
- `open_ended_default_count`

建議通過門檻：
- `consecutive_duplicate_question_text_count = 0`
- `consecutive_duplicate_scenario_id_count = 0`（若 `scenario_id` 存在）
- `consecutive_duplicate_parameter_signature_count = 0`（若 `parameter_signature` 存在）
- deterministic Level 1 practice：`open_ended_default_count = 0`
- `fallback_count` 必須有 reason，且不得 fallback 到 open-ended review 題

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

diversity 欄位至少需包含：
- `sampled_count`
- `unique_question_text_count`
- `unique_scenario_id_count`
- `unique_question_pattern_hash_count`
- `repeated_question_text_ratio`
- `consecutive_duplicate_count`
- `diversity_status`
- `diversity_issue_severity`
- `accepted_reason`（若有）
- `requires_repair`
- `unique_parameter_signature_count`
- `unique_numeric_tuple_count`
- `repeated_parameter_signature_ratio`
- `consecutive_same_numeric_tuple_count`
- `parameterized_answer_consistency`
- `parameter_pool_size`
- `numeric_pool_size`
- `context_pool_size`
- `textbook_bounded_parameterization_status`

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
1. `StatisticalBasicConcepts`：曾出現連續抽題高度重複，常重複：
   - 「下列何者屬於敘述統計？」
   - 「若學校想了解全校學生通勤方式，直接詢問全校每一位學生，這屬於何者？」
   - 「統計研究通常包含蒐集、整理、陳示、分析、解釋。下列何者是正確的第一步？」
   處理原則：
   - 擴充 `scenario_id` 至至少 8~12 個
   - 連續抽 20 題時 `unique_question_text_count >= 6`
   - 不得連續兩題完全相同
   - 若不符合，QA 不可標 `QA_PASSED`
2. `SamplingMethods`：曾出現固定數字重複，常重複：
   - 「共有 600 名員工，想用系統抽樣抽出 60 人」
   - 「某校一年級 120 人、二年級 80 人、三年級 100 人，共 300 人，抽 30 人」
   - 「工廠品管從第 5 件開始每隔 20 件抽 1 件」
   處理原則：
   - 建立 `SYSTEMATIC_INTERVAL_NUMERIC_POOL`
   - 建立 `STRATIFIED_ALLOCATION_NUMERIC_POOL`
   - payload 補 `parameter_signature`
   - 連續抽 30 題檢查 `unique_parameter_signature_count`
   - 系統抽樣與分層抽樣答案必須由參數正確計算
3. `SamplingSurvey`：choice 誤走 review 路徑 → 需明確分流 deterministic vs review
4. Choice payload：要求輸入代號但無 choices → 修 route payload + frontend rendering + alias checker
5. `CumulativeFrequencyTablesAndGraphs`：題幹有下表但 payload 無表 → 補 table/visual/image
6. `DataOrganizationAndCharts`：只出開放題且重複 → 增 `chart_type_selection_by_purpose`、`data_organization_first_step`
7. `StatisticalChartReading`：附圖無圖、answer 空、重複題幹 → 增 deterministic_choice + visual-backed review shell
8. `SamplingSurvey`：曾相鄰重複「2000 包餅乾抽 100 包」樣本題
   - 後續修補：補 `parameter_signature`，route 比對 `question_text/scenario_id/parameter_signature`，最多 retry 3 次
9. `DataOrganizationAndCharts`：曾相鄰重複「占比/圓形圖」題
   - 後續修補：Level 1 default 只出 deterministic_choice；補 `scenario_id/parameter_signature`；route 全域相鄰避重
10. `StatisticalBasicConcepts`：曾 3 個固定題幹輪播
   - 後續修補：scenario pool 擴充 + route/session 避開上一題 `scenario_id`
11. `SamplingMethods`：曾固定數字輪播
   - 後續修補：`parameter_signature` + `numeric_params/context_params` + parameterized diversity gate

## 11. 執行順序（Release）
1. Coverage gate 通過
2. Quality gate（本 SOP）通過
3. 回歸測試通過
4. 產出 QA report
5. 才能標記 release-ready

### Final Status 規則補強
若 diversity `MAJOR` 尚未釐清，不可標 `QA_PASSED`。

狀態規則：
- `consecutive_duplicate_count > 0` 且 skill 是 deterministic practice -> `NEEDS_REPAIR`
- `repeated_question_text_ratio > 0.5` 且無 `accepted_reason` -> `NEEDS_REPAIR`
- `unique_question_text_count < 6` 且非單一 review shell -> `NEEDS_REPAIR`
- deterministic generator 數字參數固定（無合理 accepted_reason）-> 不可 `QA_PASSED`
- `consecutive_same_numeric_tuple_count > 0` 且無 `accepted_reason` -> `NEEDS_REPAIR`
- `unique_parameter_signature_count` 過低且無 `accepted_reason` -> `NEEDS_REPAIR`
- `answer consistency fail` -> `BLOCKED`
- `choices` 未跟參數同步更新 -> `BLOCKED`
- 參數化超出課本骨架 -> `NEEDS_REPAIR` 或 `BLOCKED`
- Level 1 deterministic skill 出現相鄰完全相同題（無 `accepted_reason`）-> 不可 `QA_PASSED`
- `consecutive_duplicate_question_text_count > 0` 且無 `accepted_reason` -> `NEEDS_REPAIR`
- `consecutive_duplicate_parameter_signature_count > 0` 且無 `accepted_reason` -> `NEEDS_REPAIR`
- 避重 fallback 到 open-ended review 題 -> `BLOCKED`
- metadata 不足但可用 `question_text hash` 避重 -> `MINOR` 或 `MAJOR`（依影響程度）
- 所有 diversity major 都有 `accepted_reason` -> `QA_PASSED_WITH_MAJOR_NOTES`
- 無 active major/blocking -> `QA_PASSED`

## 12. 適用範圍
- B4 為本 SOP 首次完整落地。
- B1/B2/B3 與後續冊數應沿用同規則與同報告格式。

---

## 5.8 Fake Diversity / Scenario Family Gate（新增）

### A. Fake Diversity 禁止原則
1. 只換名稱不算真正多樣性。
2. 若題型骨架相同，只是把 A/B 改成甲/乙、紅/藍，應視為同一 `scenario_family`。
3. 若只是把「學校」改成「社區」、「商店」改成「公司」，但數學結構、作答行為、答案生成邏輯完全相同，不得直接算作不同 `scenario_family`。
4. 表面文字不同，不代表題型多樣。
5. QA gate 必須能區分：
   - `surface wording variation`
   - `context name variation`
   - `numeric parameter variation`
   - `true scenario family variation`

### B. scenario_family 定義
`scenario_family` 應代表「題型骨架 / 解題結構 / 作答行為」相同的一群題。

TreeDiagramCounting 範例：
以下都屬同一 `scenario_family=best_of_three_binary_match`：
- A、B 兩隊比賽，每場沒有平手，先贏兩場者勝。
- 甲、乙兩隊比賽，每場沒有平手，先贏兩場者勝。
- 紅、藍兩隊比賽，每場沒有平手，先贏兩場者勝。

原因：其數學結構同為二元勝負、每場無平手、先贏兩場結束、以樹狀圖/完整列舉作答。

### C. 有效多樣性判斷標準
有效多樣性至少改變其一：
1. 解題結構不同（例：硬幣三次、主餐飲料搭配、兩段路線、先贏兩場）。
2. `tree_depth` / `branch_counts` 不同。
3. `outcome_set` 結構不同。
4. 作答要求不同（列舉全部、補樹狀圖、求總數、檢查遺漏）。
5. 有效參數化不同（分支數、次數、集合大小、table/chart data pattern）。

僅替換：
- A/B -> 甲/乙
- 紅/藍 -> 黑/白
- 學校 -> 社區
- 商店 -> 公司

只算 `context_label variation`，不算新 `scenario_family`。

### D. Metadata 要求（Fake Diversity 檢查）
generator payload 應盡量提供：
- `scenario_family`
- `scenario_id`
- `parameter_signature`
- `context_signature`
- `outcome_set_signature`
- `structure_signature`
- `question_pattern_id`

TreeDiagramCounting 建議額外提供：
- `tree_depth`
- `branch_counts`
- `outcome_set_signature`
- `stopping_rule`（若有）
- `listing_expected_count`（若可得）

### E. QA 抽樣門檻補強
Diversity QA 新增欄位：
- `unique_scenario_family_count`
- `fake_name_only_variation_count`
- `unique_structure_signature_count`
- `unique_outcome_set_signature_count`

判定規則：
1. `fake_name_only_variation_count > 0` 且被拿來充當 diversity -> `MAJOR`，`requires_repair=yes`。
2. `unique_question_text_count` 達標但 `unique_scenario_family_count` 不達標 -> `MAJOR`，不可 `QA_PASSED`。
3. 若課本 scope 有限，可標 `textbook_limited_scope=true`，但不得以換名字假裝多樣。

### F. 已發生案例（TreeDiagramCounting）
曾出現表面不同但骨架相同：
- A、B 兩隊先贏兩場
- 甲、乙兩隊先贏兩場
- 紅、藍兩隊先贏兩場

處理原則：
- 三者皆歸 `best_of_three_binary_match`
- 不得計為三個 `scenario_family`
- 應擴充真正不同骨架（硬幣連投、主餐飲料搭配、兩段路線、多階段選擇、不同分支數列舉）

### G. 與既有 Gate 關係
- Fake Diversity Gate 是 Question Diversity Gate 子規則。
- 與 Parameterized Diversity Gate 並行：
  - Question Diversity Gate：檢查題幹/scenario/pattern 多樣性
  - Parameterized Diversity Gate：檢查數字與參數多樣性
  - Fake Diversity Gate：檢查表面換名是否被誤當 scenario diversity
  - Level 1 Global Consecutive Duplicate Guard：檢查相鄰重複
