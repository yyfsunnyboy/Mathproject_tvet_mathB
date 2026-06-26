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

### 1.5.6 防胖防禦線：Layer 6 獨立 Domain 隔離原則（Anti-Bloat Defense）

為了通吃 K7–K12 所有複雜數學題型，且防止全域調度器（`runtime_skill_wrapper.py`、`slot_generators.py`、`template_slot_resolver.py`）無限膨脹，本節剛性規定 **Layer 6 執行期** 的 Domain 職責隔離邊界：

#### 1.5.6.1 全域調度器職責上限

全域調度器**僅負責**：
1. YAML / ProblemTypeSpec 解析與 Contract Token 讀取。
2. `TASK_FAMILY_TO_SLOT` → `SLOT_REGISTRY` 函式分流與 payload 組裝委託。
3. `validate_generator_payload()` 與 Thin Facade 回傳封裝。

全域調度器**嚴禁**寫入任何實體數學公式、文字特例、情境池分支或 SymPy 運算邏輯。

#### 1.5.6.2 具名全域 Domain 模組（Domain Functions）

所有實體特殊邏輯**必須**依 Domain 職責完全抽離至下列具名全域模組；`SLOT_REGISTRY` 內的插槽處理函數僅能**委託**這些模組，不得內嵌實作：

| Domain | 模組範例 | 職責 |
|--------|---------|------|
| **核心算力域（Math Domain）** | `combinatorics_evaluator.py` | 排列組合計數、階乘、組合數等離散數學算力 |
| | `symbolic_expression_engine.py` | SymPy 符號運算、代數展開化簡、等價判定 |
| **插槽約束求解域（Constraint Domain）** | `random_slot_solver.py` | 解析 `variable_constraints`，自動求解合理參數，消除無解怪題 |
| **情境與文本樣板域（Template Domain）** | `scenario_pool_manager.py` | 情境多樣性文本管理、題幹組裝、靈魂 Token 黏貼與答案範例尾綴 |

#### 1.5.6.3 違規判定

下列情形視為 **Global Engine Bloat（全域引擎膨脹污染）**，Quality Gate 必須標記 `BLOCKED`：
1. 在 `slot_generators.py` 或 `runtime_skill_wrapper.py` 內直接撰寫超過 20 行之實體數學邏輯。
2. 以 `skill_id` 或 `problem_type_id` 為條件，在全域調度器內寫死 `if/elif` 特例分支。
3. 新建插槽處理函數卻未委託至上述 Domain 模組，而是將數學與文本邏輯堆疊於調度器本體。

### 1.7 Capability-First Domain 解析與 Automated Bootstrap 契約（v0.3.1 · **必要能力**）

> **產品定位**：本節為 **最終產品必要能力**，不是未來選配。與 [Gencode與AgentSkillV2整合總體設計_v0.3.md §14](Gencode與AgentSkillV2整合總體設計_v0.3.md)、[SOP_Gencode_AgentSkillV3_Specification.md §1.10](../Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_Specification.md) 互補：本文件定義 **ProblemTypeSpec 必須攜帶的欄位**；V3 SOP 定義 **bootstrap／healer 產物與 Gate**。

#### 1.7.1 ProblemTypeSpec 驅動的 resolution 順序

```text
Phase 1 induced spec（problem_type_id）
→ required_capabilities / matched_capabilities / missing_capabilities
→ capability-first domain matching（重用既有 verified provider）
→ 若 PARTIAL / UNRESOLVED → Domain Gap Report → Automated Domain Bootstrap
→ component scaffold（src_{example_id}）
→ 教師預覽 → verified → Publish Gate
```

`SKILL_TO_DOMAIN` 僅為 **confirmed binding** 加速路徑；**不得**作為「未註冊 skill 禁止生成」之門檻。

#### 1.7.2 Bootstrap 輸入（induced spec 必須可匯出）

| 欄位 | 來源 |
|------|------|
| `problem_type_id` | ProblemTypeSpec |
| `required_capabilities` | semantic / generator contract |
| `matched_capabilities` / `missing_capabilities` | resolver 輸出 |
| 教材例題集合 | `source_examples` + `examples_map` |
| `answer_contract` / `presentation_mode` | AnswerContract SOP |
| `source_hashes` | Layer 1 標準化 |
| 相近既有 domains | registry capability index |

#### 1.7.3 Bootstrap 產物（不得 skill／example 專用）

至少包括：`domain manifest`、純數學 `core`、`domain operations`、`capability declarations`、`matrix adapter`、`component scaffold contract`、`answer contract`、`validator`、`unit tests`、`property tests`、`integration fixtures`、題目預覽、成本與修補紀錄。**禁止**產生 skill-specific 或 example-specific domain。

#### 1.7.4 驗證三元分離（寫入 ValidatorContract）

```text
generator algorithm ≠ answer oracle ≠ integrity validator
```

ProblemTypeSpec 的 `validator_contract` **必須**分別聲明 oracle 來源與 integrity 檢查器；**禁止**用同一段生成邏輯自我證明正確。

#### 1.7.5 Domain 狀態與 registry 升格

| 狀態 | 規範 |
|------|------|
| `draft` | AI 初步產物；僅隔離區；正式 resolver／學生端 **不可用** |
| `candidate` | 通過基本品質閘門；可 dry-run 與教師預覽；**不可**正式發布 |
| `verified` | 完整驗證 + 教師／管理員核准；方可進入正式 provider 集合 |

AI 產物 **不得** 直接修改正式 registry 或立即發布。

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
diagnosis_tags: [concept_distance]      # 診斷用標記；排列組合單元須含四大經典 tag（見總體設計 §3.6）
related_problem_types:                  # 關聯題型列表
  - absolute_value_numeric_evaluation
runtime_status: runtime_ready           # runtime_ready | pending | disabled
```

**排列組合／機率單元 `diagnosis_tags` 強制範例**（見總體設計 §3.6；觸發條件：`skill_id` 含「排列」「組合」「機率」語意關鍵字）：

```yaml
subskill_id: permutation_combination_basic
skill_id: vh_數學B1_Permutations
display_name: 排列與組合
learning_goal: 區分排列與組合，正確計數並求機率
diagnosis_tags:                         # 四大經典錯誤標籤 — RAG 補救唯一特徵鍵
  - p_c_confusion
  - sample_space_error
  - double_counting
  - denominator_error
related_problem_types:
  - permutation_count_basic
  - combination_count_basic
  - probability_fraction_basic
runtime_status: runtime_ready
```

### 2.3 ProblemTypeSpec (problem_types.yaml)
題型規格，是 Gencode Pipeline 生成程式的唯一權威輸入。

**一般數值題範例**：
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
  required_concepts: [絕對值]
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

**排列組合／機率單元範例**（`skill_id` 含語意關鍵字時**必須**含 `hint_contract`）：
```yaml
problem_type_id: permutation_count_basic
skill_id: vh_數學B1_Combinatorics
subskill_id: permutation_combination_basic
display_name: 排列數計算
runtime_category: deterministic_numeric
answer_type: integer
stem_contract:
  require_latex: true
  keywords_required: [排列]
answer_contract:
  answer_type: integer
  equivalence_type: numeric_exact
  checker_key: integer_checker
semantic_contract:
  required_concepts: [排列, 組合, 階乘]
  variable_constraints:
    n: { type: integer, range: [3, 12] }
    r: { type: integer, range: [1, 5] }
hint_contract:                          # 語意判定屬排列/組合/機率時剛性必填
  hint_levels: 3
  forbid_final_answer: true
  concept_source: semantic_contract.required_concepts
generator_contract:
  generator_key: perm_count_v1
  function_name: generate
validator_contract:
  sample_count: 30
  correct_rate_threshold: 1.0
source_examples: [ex_201, ex_202]
readiness: runtime_ready
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

## 2.5 教學提示與核心概念三層階梯架構（Hint Scheme）

本節為 v0.3.2 增量法規。當單元經**語意關鍵字判定**（`skill_id` 含「排列」「組合」「機率」）屬於排列、組合、機率範疇時，規格包內 `problem_types.yaml` **必須剛性包含** `hint_contract`，落實「L1 概念喚醒 → L2 方法提示 → L3 結構提示」階梯，且強制標記 `forbid_final_answer: true`。

### 2.5.1 法規定位

- `hint_contract` 與 `answer_contract` **分離**：Hint 僅引導思考方向，**不得**洩漏最終答案或可直接代入求解之完整算式。
- Hint 文本**必須**由 `semantic_contract.required_concepts` 驅動，限制產出引導方向之文本，**嚴禁** AI 直接給解答（❌ 直接給最終答案）。
- 非排列/組合/機率單元：`hint_contract` 為選配；排列/組合/機率單元：**剛性必填**。

### 2.5.2 三層階梯定義

| 層級 | 欄位鍵 | 職責 | 允許內容 | 禁止內容 |
|------|--------|------|---------|---------|
| L1 | `concept_nudge` | 概念喚醒 | 點出本題核心概念（如「此題涉及排列還是組合？」） | 最終數值、完整公式、逐步代入 |
| L2 | `method_hint` | 方法提示 | 建議解題策略（如「先定義樣本空間，再計數」） | 最終答案、可直接抄寫之算式 |
| L3 | `structure_hint` | 結構提示 | 提示算式骨架（如「使用 $P^n_r$ 或 $C^n_r$」） | 代入後可直接得出之結果 |

### 2.5.3 hint_contract Schema

```yaml
hint_contract:
  hint_levels: 3
  forbid_final_answer: true              # 剛性：任何層級均不得含最終答案
  concept_source: semantic_contract.required_concepts
  level_1_concept_nudge:
    max_chars: 80
    must_reference_concepts: true
  level_2_method_hint:
    max_chars: 120
    must_reference_concepts: true
  level_3_structure_hint:
    max_chars: 150
    allow_formula_skeleton: true         # 允許符號骨架，禁止代入求值
  runtime_delegate: runtime_skill_wrapper  # Hint 請求由全域調度器委託產出
```

### 2.5.4 執行期委託規則

1. 學生請求 Hint 時，`runtime_skill_wrapper.py` 讀取 `hint_contract` 與當前 `required_concepts`，依已請求層級遞進產出 L1→L2→L3。
2. AI 僅可於 Template Domain（`scenario_pool_manager.py`）建議引導用語；最終 Hint 須經 `forbid_final_answer` 守衛過濾後方可回傳前台。
3. 違反 `forbid_final_answer` 之 Hint 視為 **Hint Leakage（提示洩題）**，Quality Gate 標記 `BLOCKED`。

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
| 2026-05-31 | v0.2 | 重整 v0.2，將流程性內容移至總體設計，精簡 Schema 欄位，增加 source_item_status 與 non-destructive merge 細則 | Antigravity |
| 2026-06-01 | v0.3 | 增量新增 §1.5 薄入口外殼方案；焊入 Thin Facade 與全域調度器委託法規 | 首席系統架構師 |
| 2026-06-13 | v0.3.1 | 增量新增 §1.5.6 防胖防禦線（Layer 6 Domain 隔離原則） | 首席系統架構師 |
| 2026-06-13 | v0.3.2 | 洗淨版：清除佔位符；YAML 範例改為 vh_數學B1 實例 | 首席系統架構師 |
| 2026-06-26 | v0.3.3 | 新增 §1.7 Capability-First Bootstrap 契約；對齊 V3 §1.10 最終產品流程 | 首席系統架構師 |

*本文件職責：定義 AgentSkillV2 所有核心規格檔（YAML）與 Registry Entry 的 Schema 結構，以及 Phase 3 技能薄外殼之職責邊界。*
*不負責事項：不定義具體的運行流程（Phase）與等價判定 checker 的比對邏輯。*
*應參考的其他 SOP：[Gencode與AgentSkillV2整合總體設計_v0.3.md](Gencode與AgentSkillV2整合總體設計_v0.3.md)、[AnswerContract_EquivalenceType_Gate_v0.3.md](AnswerContract_EquivalenceType_Gate_v0.3.md)、[SOP_Gencode_AgentSkillV3_Specification.md §1.10](../Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_Specification.md)。*