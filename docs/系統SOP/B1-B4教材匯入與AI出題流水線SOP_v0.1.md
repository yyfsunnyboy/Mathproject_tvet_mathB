# B1–B4 教材匯入與 AI 出題 RuntimeReady 流水線 SOP v0.1

## 一、SOP 目的
本 SOP 用於將 B1–B4 任一冊教材，從教材匯入、skill inventory、題型盤點、runtime mode 分流、generator/router/checker 建立、quality gate、自動 QA、少量人工 spot check，到 Phase 1 closure，形成可重複執行的流水線。

核心目標：
1. 減少人工逐題測試  
2. 避免 B4 曾發生的錯誤重演  
3. 確保題目貼近課本  
4. 確保 Level 1 題目適合高職學生  
5. 確保 runtime mode 與 check mode 一致  
6. 確保每冊先完成 Phase 1 RuntimeReady baseline，再談 Phase 2 adaptive prerequisite graph

## 二、總流程總覽
- Phase 0：入庫前準備  
- Phase 1：教材入庫  
- Phase 2：Skill Inventory  
- Phase 3：Textbook Fidelity Audit  
- Phase 4：Runtime Mode Matrix  
- Phase 5：Generator / Router / Checker 實作  
- Phase 6：Quality Gates  
- Phase 7：Fullbook QA Audit  
- Phase 8：Manual Spot Check  
- Phase 9：Phase 1 Closure  
- Phase 10：Adaptive Phase Deferred / Cross-volume prerequisite graph

## 三、Phase 0：入庫前準備
1. 確認冊別：B1 / B2 / B3 / B4  
2. 確認出版商與教材來源  
3. 確認章節與小節結構  
4. 確認 `source_type` 命名：`textbook_example` / `textbook_practice` / `self_assessment` / `review` / `other`  
5. 確認 `skill_id` 命名規則：`vh_數學B{volume}_{EnglishSkillName}`  
6. 確認圖表、手寫、公式、開放式題處理策略  
7. 確認 LaTeX 格式要求：
   - 數學式使用 `$...$`
   - 指數用 `^{...}`
   - 乘法用 `\times`
   - 不使用 plain text `2^2`, `C(n,r)`, `P(n,r)`

## 四、Phase 1：教材入庫
1. 匯入 `textbook_example / practice / self_assessment`  
2. 保留原始 `chapter / section / source_type`  
3. 入庫階段不急著 runtime  
4. 標記欄位：
   - `needs_review`
   - `formula_missing`
   - `visual_required`
   - `handwriting_candidate`
   - `teacher_review_candidate`
   - `deterministic_candidate`
5. 自我評量命名規則：
   - 不只叫「自我評量」
   - 應保留章節，如「第 X 章 自我評量」
6. 入庫後需產生 import summary report

## 五、Phase 2：Skill Inventory
每冊必須產生：`reports/b_series_inventory/B{volume}_skill_inventory.md`

每個 skill 欄位至少包含：
- `skill_id`
- 中文技能名稱
- `chapter`
- `section`
- source 題數
- `source_type` 分佈
- `problem_type / scenario family` 初步分類
- `deterministic_candidate` yes/no
- `visual/table` yes/no
- `handwriting_candidate` yes/no
- `teacher_review_candidate` yes/no
- `visibility_only_candidate` yes/no
- `formula_required` yes/no
- `needs_review` count
- `suitable_for_level1_practice` yes/no
- notes

明確規則：不能只看 skill 名稱，必須看實際課本題型內容。

## 六、Phase 3：Textbook Fidelity Audit
每個 skill 必須先回答：
1. 課本主題型是什麼？
2. 例題骨架是什麼？
3. 哪些題可以 deterministic？
4. 哪些題需要 visual / handwriting / teacher_review？
5. 哪些題不能硬做？
6. 有沒有 aligned source？
7. 若沒有 aligned source，不可為了 coverage 硬做 runtime

禁止：
- 課本是作圖題，硬改成 short-answer  
- 課本是選擇題，卻生 open-ended  
- 課本沒有的題型，AI 自行創新  
- 只為了 diversity 而偏離課本骨架  

B4 案例（警示）：
- `frequency_polygon_reading` 因課本主型偏作圖而 blocked  
- `cumulative_frequency_graph_reading` 不可硬轉 deterministic short-answer  
- `SamplingSurvey` 不應把民調偏誤開放題當 Level 1 主力

## 七、Phase 4：Runtime Mode Matrix
每個 skill 必須歸入 primary runtime category：
1. `deterministic_auto_checked`
2. `visual_or_handwriting_ai_checked`
3. `teacher_review`
4. `visibility_only`
5. `partial_runtime`
6. `blocked_by_fidelity`

每冊必須產生：`reports/b_series_inventory/B{volume}_runtime_mode_matrix.md`

欄位：
- `skill_id`
- `primary_runtime_category`
- `released_problem_type`
- `reserved_problem_type`
- `check_mode`
- `grading_mode`
- `reason`
- `known_limitations`

## 八、Phase 5：Generator / Router / Checker 實作原則
每個 runtime-ready skill 必須接通：
- `/practice`
- `/get_next_question`
- `/check_answer`
- encoded / decoded `skill_id`
- choice rendering
- visual/table rendering
- handwriting/upload/AI check path（若適用）
- friendly not-enabled / review guard
- regression tests

每個 generator payload 應盡量包含：
- `skill_id`
- `problem_type_id`
- `scenario_family`
- `scenario_id`
- `question_pattern_id`
- `parameter_signature`
- `numeric_params`
- `context_params`
- `table_spec_hash`
- `chart_spec_hash`
- `visual_asset_hash`
- `runtime_mode`
- `check_mode`
- `grading_mode`
- `answer_input_type`
- `choices`（若 choice）
- `answer / expected_answer_schema / rubric`
- `explanation`
- `textbook_alignment_note`

## 九、Phase 6：Quality Gates（硬性）
1. Choice Contract Gate  
2. Level 1 No-open-ended Gate  
3. Question Diversity Gate  
4. Parameterized Diversity Gate  
5. Fake Diversity / Scenario Family Gate  
6. Level 1 Global Consecutive Duplicate Guard  
7. Visual/Table Payload Gate  
8. Localization Gate  
9. Runtime/check_mode Consistency Gate

關鍵要求（摘要）：
- 「請輸入選項代號」必須有 choices，且 answer 對應 choices  
- Level 1 bare skill default 不得主動出 open-ended  
- 每 skill 抽樣至少 20 題  
- 數字不可固定，答案必須跟參數一致  
- 只換名字不算 diversity（A/B、甲乙、紅藍先贏兩場同 family）  
- route/session 避重最多 retry 3 次，不得 fallback 到 open-ended review 題  
- 題幹提及下表/附圖，必須有對應 payload  
- 學生端全中文，禁止英文模板殘留  
- deterministic 與 review/checker 路徑不可錯配

## 十、Phase 7：Fullbook QA Audit
每冊 release 前必須產生：  
`reports/b_series_quality/B{volume}_fullbook_level1_quality_gate_audit_summary.md`

抽樣規則：
- 每個 skill Level 1 default route 至少 20 題
- visual/handwriting/review 題檢查 metadata 與 contract
- 不可用 deterministic 標準誤判 review 題

report 必須包含：
- total skills sampled
- total sampled questions
- `active_blocking / active_major / active_minor`
- failed items table
- each skill QA status：
  - `QA_PASSED`
  - `QA_PASSED_WITH_MAJOR_NOTES`
  - `NEEDS_REPAIR`
  - `BLOCKED`
  - `TEST_NOT_RUN_ENV_BLOCKED`
- `expected_by_design` 清單
- `requires_repair` 清單
- `TEST_NOT_RUN` 不可標 passed

## 十一、Phase 8：Manual Spot Check
人工不再逐 skill 大量測試；只測：
1. 每章代表性 2–3 個 skill  
2. 剛修過的 bug  
3. report 標 active major 的 skill  
4. visual/table/handwriting 題  
5. mixed deterministic/review skill  

記錄格式：
- `skill_id`
- sample count
- 是否有 choices
- 是否可判分
- 是否有圖表 payload
- 是否相鄰重複
- 是否 open-ended 混入 Level 1
- result：`PASS / FAIL / NOTE`

## 十二、Phase 9：Phase 1 Closure
每冊完成 Phase 1 時，只能宣告：  
`B{volume} Phase 1 RuntimeReady baseline complete`

不可宣告完整 adaptive complete。

Phase 1 closure 必備：
1. skill inventory 完成  
2. runtime mode matrix 完成  
3. runtime path 已接通  
4. quality gates 已跑  
5. `active_blocking = 0`  
6. `active_major` 已處理或有 `accepted_reason`  
7. manual spot check passed  
8. final coverage count 明確

## 十三、Phase 10：Adaptive Phase Deferred
明確規則：  
B4 第二階段 adaptive prerequisite graph / mastery / remediation linkage，應待 B1–B3 入庫後再處理。

原因：B4 許多前置技能來自 B1–B3；若 B1–B3 未入庫，B4 adaptive graph 只能 session-local，無法形成完整補救路徑。

B1–B4 全部完成 Phase 1 後，再做：
- Cross-volume Skill Graph v0.1
- `main_skill / prerequisite_skill / remediation_skill`
- adaptive chapter mode v2
- mastery write-back
- teacher-facing skill graph

## 十四、B1 匯入時建議流程
1. B1 import  
2. B1 import summary  
3. B1 skill inventory  
4. B1 textbook fidelity audit  
5. B1 runtime mode matrix  
6. B1 first deterministic batch  
7. B1 visual/handwriting/review path  
8. B1 quality gate  
9. B1 fullbook QA audit  
10. B1 manual spot check  
11. B1 Phase 1 closure

## 十五、B4 經驗案例索引（供 B1–B3 警示）
- choices missing  
- Level 1 open-ended 混入  
- SamplingSurvey checker legacy module error  
- DataOrganization open-ended 題混入 default  
- StatisticalBasicConcepts 3 題輪播  
- SamplingMethods 固定數字  
- TreeDiagramCounting 只換名稱 fake diversity  
- graph/table 題 missing payload  
- English localization residues  
- QA report stale / major count mismatch  
- `TEST_NOT_RUN` 卻被標 passed

## 十六、與既有 SOP 的關係
本 SOP 為 B 系列總流水線，與既有 B4 gate SOP 並行使用：
- `B4_AI出題品質檢查SOP_v0.1.md`
- `B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md`
- `B4_AI閉環與RuntimeReady流程索引_v0.1.md`

執行順序建議：先走本流水線完成 Phase 0–5，再套用 Phase 6 gate，最後進入 Phase 7–9。
