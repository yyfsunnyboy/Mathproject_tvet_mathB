# AgentSkillV2 ProblemType 規格包設計 v0.2

## 0. 文件目的
本文件定義 AgentSkillV2 規格包（Specification Package）的資料結構與 YAML Schema，作為課本題型拆解、AI 生成、驗證與註冊的共同標準。文件採用 Schema 方式描述，以便於機器自動檢查與人類審核。

---

## 1. 規格包目錄結構
每個 `skill` 的規格包以目錄為單位進行封閉管理，結構如下：
```text
agent_skills_v2/{skill_id}/
  skill.json              # 技能基本描述與 meta
  subskills.yaml          # 子技能清單與依賴
  problem_types.yaml      # 題型規格與 Contract 定義
  examples_map.yaml       # 教材例題與題型分類映射
  prerequisites.yaml      # 子技能層級的先備與補救候選
  evals.yaml              # 驗證抽樣與品質閾值
```

---

## 2. 核心 YAML Schema 設計

### 2.1 SkillSpec (YAML / JSON)
描述單一技能（Skill）的總體屬性。
```yaml
skill_id: vh_數學B1_AbsoluteValue        # 技能唯一識別碼
volume: 數學B1                         # 冊別
chapter: 1 坐標系與函數圖形             # 章
section: 1-1 數線與絕對值              # 節
display_name: 絕對值                    # 前台顯示名稱
curriculum: vocational_high_school_math # 課綱標籤
status: active                         # active | draft | deprecated
source_scope:
  db_examples_count: 24                 # DB 中觀測到的例題總數
  source_types: [textbook_example, textbook_practice]
subskills: [absolute_value_basic, absolute_value_equations]
problem_types: [absolute_value_numeric_evaluation]
```

### 2.2 SubSkillSpec (subskills.yaml)
用於學習追蹤與補救路徑，定義 SubSkill 層級。
```yaml
subskill_id: absolute_value_basic       # 子技能唯一識別碼
skill_id: vh_數學B1_AbsoluteValue       # 所屬主技能 ID
display_name: 絕對值幾何意義            # 前台子技能顯示名稱
learning_goal: 理解絕對值為數線上點到原點的距離
prerequisite_subskills: []              # 前置子技能 ID 列表
diagnosis_tags: [concept_distance]      # 診斷用標記
related_problem_types:                  # 關聯題型列表
  - absolute_value_numeric_evaluation
runtime_status: runtime_ready           # runtime_ready | pending | disabled
```

### 2.3 ProblemTypeSpec (problem_types.yaml)
題型規格，是 Gencode Pipeline 生成程式的唯一權威輸入。
```yaml
problem_type_id: absolute_value_numeric_evaluation
skill_id: vh_數學B1_AbsoluteValue
subskill_id: absolute_value_basic
display_name: 絕對值數值求值
runtime_category: deterministic_numeric  # 參閱 runtime_category 枚舉
answer_type: numeric                    # 參閱 answer_type 白名單
stem_contract:                          # 題幹契約
  require_latex: true
  keywords_required: [絕對值, "|"]
answer_contract:                        # 答案判定契約，參閱 AnswerContract SOP
  answer_type: numeric
  equivalence_type: numeric_exact
  checker_key: numeric_checker
semantic_contract:                      # 語意與變數約束契約
  variable_constraints:
    x: { type: integer, range: [-50, 50], exclude: [0] }
generator_contract:                     # 生成器調用契約
  generator_key: abs_val_eval_v1
  function_name: generate
validator_contract:                     # 驗證器要求
  sample_count: 30
  correct_rate_threshold: 1.0
source_examples: [ex_101, ex_102]       # 支撐的教材 core example IDs
source_bank_refs: [ex_103]              # 僅進題庫原題的 example IDs
readiness: runtime_ready                # runtime_ready | pending_template | blocked
status: active
```

### 2.4 examples_map.yaml Schema
記錄每一筆教材例題到題型的精確映射。**included_in_core_induction 與 included_in_source_bank 必須分開獨立判定**。
```yaml
example_id: ex_101                       # 教材/DB 題目唯一識別碼
source_type: textbook_example            # textbook_example | textbook_practice | self_assessment
source_section: 1-1 例題 1
problem_preview: "求 $|-7|$ 的值。"
skill_id: vh_數學B1_AbsoluteValue
subskill_id: absolute_value_basic
problem_type_id: absolute_value_numeric_evaluation
runtime_category: deterministic_numeric
source_item_status: core_induction      # 參閱 source_item_status 枚舉
source_quality_status: usable            # usable | warning | rejected
classification_source: ai               # ai | registry_rule | parser_rule | manual_override
classification_confidence: 0.95
final_target_task: absolute_value_numeric_evaluation
final_task_family: absolute_value_basic
included_in_core_induction: true        # 是否參與 core induction 形成 ProblemTypeSpec
included_in_source_bank: true           # 是否可進題庫抽題 pool
exclude_reason: null
review_required: false
review_reason: null
answer_contract_ref:                     # 關聯的答案判定細節
  answer_type: numeric
  equivalence_type: numeric_exact
  checker_key: numeric_checker
auto_checkable: true
```

---

## 3. 重要枚舉值定義

### 3.1 source_item_status (來源狀態枚舉)
- `core_induction`：品質良好，參與核心題型歸納，且可進入學生抽題。
- `source_bank_only`：不參與自動生成歸納，但因語意明確，可直接做為教材原題抽題。
- `enrichment_source`：具備素養或延伸語意，不進生成，可作為原題展示。
- `candidate_only`：候選題型，待進一步確認。
- `runtime_ready_candidate`：具備自動生成潛力，但尚未正式綁定。
- `manual_review`：需人工審核，不可強行自動批改。
- `future_ai_judged`：需 AI-vision 或 LLM 判分，暫不進 deterministic 批改。
- `future_graph_renderer`：需要前端動態繪圖支援，目前暫不啟用自動批改。
- `should_remap`：歸類錯誤或超綱，需改派正確單元，**改派前絕對不可抽給學生**。
- `source_quality_reject`：嚴重破損、少答案或 OCR 亂碼，**絕對不可進入 core induction 亦不可抽給學生**。

### 3.2 runtime_category (運行分類枚舉)
- `deterministic_numeric`：純數值答案（整數、小數、分數），支援精確判定。
- `deterministic_expression`：代數式或方程式，需通過符號運算等價判定。
- `deterministic_choice`：單選或多選題，比對 A/B/C/D 標籤。
- `deterministic_short_answer`：簡答題，支援常規字串清理後比對。
- `visual_or_handwriting_ai_checked`：圖形或手寫辨識題，需 AI 輔助稽核。
- `teacher_review`：需教師人工閱卷，不進行自動比對。
- `visibility_only`：僅供前台展示，無須比對答案。
- `manual_review` / `future_ai_judged` / `future_graph_renderer`：對應上述狀態之外流限制。
- `partial_runtime`：僅部分步驟可自動批改。

---

## 4. Registry 註冊表規範與 Non-Destructive Merge

### Registry Entry Schema (gencode_registry.yaml)
```yaml
registry:
  vh_數學B1_AbsoluteValue:
    - problem_type_id: absolute_value_numeric_evaluation
      subskill_id: absolute_value_basic
      generator_key: abs_val_eval_v1
      candidate_path: generated_candidates/abs_val_eval_v1.py
      function_name: generate
      answer_type: numeric
      equivalence_type: numeric_exact
      checker_key: numeric_checker
      status: verified                  # candidate | verified | runtime_ready | failed
      verified_at: "2026-05-31T23:16:00+08:00"
      verifier_report_path: reports/vh_AbsoluteValue/verify_report.json
      runtime_smoke_report_path: reports/vh_AbsoluteValue/runtime_smoke.json
```

### Non-Destructive Merge 規則
1. **嚴禁覆蓋**：Failed candidate 絕對不可覆蓋已驗證通過（verified / runtime_ready）的 candidate。
2. **新增即 Append**：新 entry 必須通過 verifier 驗證後，以 append 方式併入對應 skill 下的註冊表，不得重建（rebuild）整個 registry。
3. **隔離性**：registry 寫入必須精確鎖定在當前 skill_id，嚴禁破壞或修改其他無關單元的註冊資訊。

---

## 5. 版本紀錄
| 日期 | 版本 | 職責與變更內容 | 紀錄人 |
|---|---|---|---|
| 2026-05-25 | v0.1 | 首版規格包 schema 定義 | Codex |
| 2026-05-31 | v0.2 | 重整 v0.2，將流程性內容（Phase 3、Web Runtime、Quality Gate）移至總體設計，精簡 Schema 欄位，增加 source_item_status 與 non-destructive merge 細則，確保 100% 乾淨 UTF-8 | Antigravity |

*本文件職責：定義 AgentSkillV2 所有核心規格檔（YAML）與 Registry Entry 的 Schema 結構。*
*不負責事項：不定義具體的運行流程（Phase）與等價判定 checker 的比對邏輯。*
*應參考的其他 SOP：[Gencode與AgentSkillV2整合總體設計_v0.2.md](file:///e:/Python/Mathproject_tvet_mathB/docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.2.md)、[AnswerContract_EquivalenceType_Gate_v0.2.md](file:///e:/Python/Mathproject_tvet_mathB/docs/系統SOP/Gencode_AgentSkillV2整合/AnswerContract_EquivalenceType_Gate_v0.2.md)。*