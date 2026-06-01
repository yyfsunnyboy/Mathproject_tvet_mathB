# AgentSkillV2 ProblemType 規格包設計 v0.3

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

## 1.5 薄入口外殼方案（Thin Facade Entrance Scheme）

本節為 v0.3 增量法規，**不修改** v0.2 已定案的 YAML Schema 與 Registry 欄位，僅在執行期封裝層補充「技能檔案職責邊界」。

### 1.5.1 法規定位

管線在 Phase 3 編譯期組裝產出的 `skills/{skill_id}.py`，其職責**有且僅能**作為前台 Web 請求的 **Thin Facade（薄入口外殼路由）**。所有實體數學運算、多模板隨機化、題幹組裝與 SymPy 驗證，必須在全域執行期引擎（`core/gencode/runtime_skill_wrapper.py`、`slot_generators.py`、`template_slot_resolver.py`）中完成，**不得**下沉至技能檔。

### 1.5.2 鋼鐵禁止事項

在 `skills/{skill_id}.py` 內部，**嚴禁**：

1. 堆疊、封裝或實作任何實體數學公式（斜率截距、距離公式、分點公式等）。
2. 撰寫多模板隨機化字串、情境池分支或 `seed` 路徑專屬題幹邏輯。
3. 內嵌 LLM 提示詞、Codegen 骨架或 Phase 3 生成計畫註解。
4. 以 skill_id 為條件的 `if/elif` 特例路由（違反去特例化原則）。

違反上述任一條，視為 **Facade Pollution（外殼污染）**，Quality Gate 必須標記 `BLOCKED`，不得發布至學生端。

### 1.5.3 外殼標準定義（允許宣告項）

薄入口外殼**只能**宣告並維護下列執行期白名單資料，作為 `generate_for_skill()` 與 `check_answer()` 的索引矩陣：

| 宣告項 | 職責 |
|--------|------|
| `SKILL_ID` | 與目錄、Registry、RAG 身份鍵一致的技能識別碼 |
| `GENERATOR_KEYS` | Phase 2 通過 Spec Gate 之 generator 複合鍵清單（唯讀鏡像） |
| `GENERATOR_SPECS` | 每個 active problem_type 的 `problem_type_id`、`checker_key`、`equivalence_type`、`generator_readiness` 白名單列 |

所有 `generate(level, seed, …)` 與 `check(user_answer, correct_answer, question_payload)` 請求，必須 **100% 動態委託** 給：

- `generate_for_skill(SKILL_ID, GENERATOR_SPECS, …)` — 由全域調度器依 `problem_type_id` 與 `template_slot` 分流至 `SLOT_REGISTRY`。
- `check_answer(…)` — 由 `answer_contract` 驅動的 checker 鏈執行確定性批改。

外殼**不得**自行選擇 checker、不得覆寫 `answer_contract`、不得在記憶體中改寫 `question_payload` 的數學語意。

### 1.5.4 標準外殼結構骨架範本（中文註解版）

下列為**結構骨架**（非可執行完整程式），Codex 組裝 Phase 3 產物時必須對齊此形狀：

```text
# ── 模組宣告區（僅 import 全域調度器）──
from core.gencode.runtime_skill_wrapper import generate_for_skill, check_answer

# ── 技能身份與白名單矩陣（由 Phase 3 自動寫入，禁止手改數學邏輯）──
SKILL_ID = "<skill_id>"
GENERATOR_KEYS = [ "<skill_id>:<problem_type_id>:draft_v1>", ... ]
GENERATOR_SPECS = [
  {
    "problem_type_id": "<canonical_problem_type_id>",
    "checker_key": "<checker_key>",
    "equivalence_type": "<equivalence_type>",
    "generator_readiness": "runtime_ready",
  },
  ...
]

# ── 前台唯一入口：生成（零實體數學）──
def generate(level=1, seed=None, difficulty=None, **kwargs):
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty, **kwargs)

# ── 前台唯一入口：批改（零自訂比對）──
def check(user_answer, correct_answer, question_payload=None):
    return check_answer(user_answer, correct_answer, payload=question_payload)
```

### 1.5.5 與規格包的關係

- **ProblemTypeSpec**（`problem_types.yaml` / induced JSON）仍是數學語意與 Contract 的唯一權威來源。
- **skills/{skill_id}.py** 僅為 Runtime 索引外殼；規格變更必須先走 Phase 1/2/2.5，再經 Phase 3 重新序列化外殼，禁止直接編輯外殼以「修題」。

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
| 2026-06-01 | v0.3 | 增量新增 §1.5 薄入口外殼方案；完整保留 v0.2 Schema；焊入 Thin Facade 與全域調度器委託法規 | 首席系統架構師 |

*本文件職責：定義 AgentSkillV2 所有核心規格檔（YAML）與 Registry Entry 的 Schema 結構，以及 Phase 3 技能薄外殼之職責邊界。*
*不負責事項：不定義具體的運行流程（Phase）與等價判定 checker 的比對邏輯。*
*應參考的其他 SOP：[Gencode與AgentSkillV2整合總體設計_v0.3.md](Gencode與AgentSkillV2整合總體設計_v0.3.md)、[AnswerContract_EquivalenceType_Gate_v0.3.md](AnswerContract_EquivalenceType_Gate_v0.3.md)。*