# Answer Contract / Equivalence Type Gate v0.1

本文件是 addendum SOP。

原因是既有兩份 SOP Markdown 在 repository HEAD 中已出現編碼污染，暫不直接修改原檔。
未來清理原 SOP 後，可將本 addendum 內容合併回主 SOP。

用途：
作為 Gencode / AgentSkillV2 自動出題閉環中，problem_type 答案型態、答案等價規則、checker 選擇與 semantic audit gate 的補充 SOP。

## 1. 目的與適用範圍

每個 `problem_type` 不只要有 `subskill_id`、`problem_type_id`、`runtime_category`，還必須有 `answer_contract`。

`answer_contract` 用來描述學生答案的基本型態、可接受格式、數學等價判斷方式、標準答案結構，以及 runtime 或 verifier 應使用的 checker。

若缺少 `answer_contract`，該 `problem_type` 不得標記為 `runtime_ready`，pipeline final status 也不得為 `PASS`。

## 2. answer_contract schema

```yaml
answer_contract:
  answer_type:
  equivalence_type:
  checker_key:
  order_matters:
  accepted_format_notes:
  canonical_answer_schema:
```

- `answer_type`：學生答案的基本型態，例如 `integer`、`rational`、`choice`、`solution_set`、`interval`、`expression`、`free_response`。
- `equivalence_type`：答案如何判斷等價，不可一律使用 raw string compare。
- `checker_key`：runtime 或 verifier 應使用的 checker 類別或 key。
- `order_matters`：答案順序是否影響正確性；解集合通常為 `false`。
- `accepted_format_notes`：記錄可接受輸入格式範例，供題型規格、UI 提示與測試案例對齊。
- `canonical_answer_schema`：記錄標準答案的結構化格式，例如 `set`、`fraction`、`interval`、`choice_label`。

## 3. equivalence_type whitelist

- `exact_string`：用於答案必須完全一致的少數情境。不得用於開放答案、解集合、分數等價或選擇題。
- `numeric_exact`：用於單一整數或單一精確數值，答案可被解析為同一個精確數值。
- `rational_equivalent`：用於分數、小數、百分比可互相等價的題型，例如 `1/2`、`0.5`、`50%`。
- `choice_label`：用於選擇題，支援 `A/B/C/D`、`1/2/3/4` 或完整選項文字。
- `unordered_solution_set`：用於解集合，順序不重要；例如 `x=-17 或 x=17` 可接受 `17,-17`。
- `interval_set`：用於不等式區間答案，例如 `x>3` 或 `(3,∞)`。
- `algebraic_equivalent`：用於代數式等價，例如 `2(x+1)` 與 `2x+2`。
- `manual_review_or_ai_judged`：用於證明、畫圖、列舉、完整過程、手寫題或開放式推論。

## 4. 禁止 raw string compare 的情境

若答案有多種數學等價表達，不得使用 `exact_string` / raw string compare。

以下情境不得直接使用 raw string compare：

- 解集合題。
- 分數、小數、百分比等價題。
- 選擇題。
- 區間題。
- 代數式等價題。
- 證明、說明、畫圖、列舉題。

## 5. 開放性答案處理策略

遇到開放性答案時，AI 題型分類不得直接標為 `exact_string`，必須依序判斷：

A. 可結構化比對：
指定 `equivalence_type` 與 `checker_key`。

```yaml
answer_type: solution_set
equivalence_type: unordered_solution_set
checker_key: solution_set_checker
```

B. 可不失真改寫為選擇題：
若學習目標可不失真地改寫為選擇題，標記如下。

```yaml
answer_type: choice
equivalence_type: choice_label
checker_key: choice_label_checker
convertible_to_choice: true
```

C. 改寫會失真：
若改寫為選擇題會破壞學習目標，標記為 `manual_review`、`future_ai_judged` 或 `handwriting_ai_checked`，並使用 `manual_review_or_ai_judged`。

```yaml
runtime_category: manual_review
equivalence_type: manual_review_or_ai_judged
```

不得為了自動判分而強行把證明、畫圖、完整列舉、解釋理由題改成選擇題。

## 6. Semantic Coverage Audit Gate

Semantic Coverage Audit 不只檢查 `problem_type` 覆蓋率，也必須檢查 `answer_contract`。

pipeline report 必須輸出：

```yaml
answer_contract_summary:
  observed_problem_type_answer_contracts:
  missing_answer_contract_problem_types:
  missing_checker_key_problem_types:
  equivalence_test_required_problem_types:
  convertible_to_choice_problem_types:
  manual_review_or_ai_judged_problem_types:
```

PASS / PARTIAL / FAIL 規則：

- 缺 `answer_contract`：不可 `PASS`。
- 缺 `checker_key`：不可 `PASS`。
- `equivalence_type` 非 `exact_string` / `numeric_exact` 時，需標示 equivalence verifier test。
- equivalence verifier 尚未實作時，final status 最多 `PARTIAL`。
- 開放答案若被標為 `exact_string`，應視為 audit risk，不可 `PASS`。
- `manual_review_or_ai_judged` 題型可以存在，但必須明確標記，不可偽裝成 deterministic runtime-ready。

每個 observed `problem_type` 至少必須列出：

- `problem_type_id`
- `subskill_id`
- `runtime_category`
- `answer_contract.answer_type`
- `answer_contract.equivalence_type`
- `answer_contract.checker_key`
- `answer_contract.order_matters`

## 7. AbsoluteValue 範例

```yaml
absolute_value_numeric_evaluation:
  answer_contract:
    answer_type: integer
    equivalence_type: numeric_exact
    checker_key: integer_checker
    order_matters: false
    canonical_answer_schema:
      type: integer

absolute_value_distance_from_zero:
  answer_contract:
    answer_type: choice
    equivalence_type: choice_label
    checker_key: choice_label_checker
    order_matters: false
    accepted_format_notes:
      - A/B/C/D
      - 1/2/3/4
      - 完整選項文字

absolute_value_distance_between_two_points:
  answer_contract:
    answer_type: integer
    equivalence_type: numeric_exact
    checker_key: integer_checker
    order_matters: false
    canonical_answer_schema:
      type: integer

absolute_value_equation_basic:
  answer_contract:
    answer_type: solution_set
    equivalence_type: unordered_solution_set
    checker_key: solution_set_checker
    order_matters: false
    accepted_format_notes:
      - "17,-17"
      - "-17,17"
      - "x=17 或 x=-17"
      - "x=-17 或 x=17"
      - "±17"
    canonical_answer_schema:
      type: integer_set
      values_example:
        - -17
        - 17
```

`absolute_value_equation_basic` 不能 raw string compare，因為學生可能用不同格式表示同一組解。

## 8. 後續實作階段

- Phase A：Addendum SOP 建立。
- Phase B：pipeline report 顯示 `answer_contract`。
- Phase C：checker unit tests，例如 `solution_set_checker`。
- Phase D：student runtime 接線。
- Phase E：第二個 skill 泛化驗證。
- Phase F：後台 Gencode Lab 頁面化。

## Bootstrap From Existing Skill Gate

### 目的

當目標 skill 的 DB textbook examples 不足，或 examples 與技能語意明顯不一致，但專案中已有可信、可測試、語意相近的 `skill.py` 時，允許使用既有 `skill.py` 作為 bootstrap source。

此模式用於建立暫時可用的 runtime generator，不代表教材題庫 coverage 已完整完成。

### 適用條件

必須同時符合：

1. 目標 skill 的 DB examples 數量不足，例如 `examples_total < 3`。
2. 或 DB examples 與目標 skill 語意不一致。
3. 存在可信的既有 `skill.py` 可沿用。
4. 既有 `skill.py` 的題型與目標 skill 學習目標高度相容。
5. 新 wrapper / adapter 可通過 `py_compile`。
6. 新 wrapper / adapter 有 pytest 或 sample verification。
7. 產出 payload 必須改成目標 `skill_id`、目標 `problem_type_id`、目標 `answer_contract`。
8. 不得把舊 `skill_id` 混入新 skill runtime payload。

### 禁止事項

1. 不得把 bootstrap-only 誤標為 `FULL_OBSERVED_COVERAGE`。
2. 不得把 bootstrap-only 誤標為一般 `PASS`。
3. 不得跳過 `answer_contract`。
4. 不得破壞原始舊 `skill.py`。
5. 不得直接把舊 `skill_id` 暴露在學生端 payload。
6. 不得用 bootstrap mode 掩蓋 DB 題庫缺口。

### final_status 規則

bootstrap mode 的 `final_status` 應使用：

```text
PASS_BOOTSTRAP_ONLY
```

而不是 `PASS`。

report 必須包含：

```yaml
bootstrap_summary:
  bootstrap_mode: true
  bootstrap_source_skill_id:
  bootstrap_runtime_status:
  source_coverage_status:
  full_observed_coverage: false
  warning:
```

`source_coverage_status` 可使用：

```text
INSUFFICIENT_SOURCE_EXAMPLES
INSUFFICIENT_OR_MISALIGNED_DB_EXAMPLES
```

### NumberLine 範例

```yaml
vh_數學B1_NumberLine:
  source_coverage_status: INSUFFICIENT_OR_MISALIGNED_DB_EXAMPLES
  bootstrap_mode: true
  bootstrap_source_skill_id: jh_數學1上_NumberLine
  bootstrap_runtime_status: PASS
  final_status: PASS_BOOTSTRAP_ONLY
  full_observed_coverage: false
  warning: "Bootstrap-only runtime ready; not full DB observed textbook coverage."
```

此 skill 的 B1 DB examples 只有 1 筆，且不代表完整數線技能，因此允許使用國一數線 generator 作為 bootstrap source。
但此狀態不得宣稱為完整 gencode closed-loop `PASS`。

## Phase 2 Build Planning / Foundation Preflight

1. Phase 2 必須先做 dependency planning，再決定是否執行 build。  
2. 若缺 checker / verifier / domain function / generator foundation，不應直接 `BUILD_FAIL`。  
3. 此類可修復缺口應回傳 `FOUNDATION_REPAIR_REQUIRED`，並附上 `repair_plan`。  
4. 只有 `foundation_ready = true` 時，才可進入 generator build。  
5. Phase 3 僅可在 `BUILD_PASS` 或 `BUILD_BOOTSTRAP_PASS` 後執行。  
6. `repair_plan` 是後台頁面與自動修復 script 的接口。  
