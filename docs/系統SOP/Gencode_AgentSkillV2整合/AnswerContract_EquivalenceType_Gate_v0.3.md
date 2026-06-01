# AnswerContract EquivalenceType Gate v0.3

## 0. 文件目的
本文件定義答案型態、等價判定與批改（checker）的核心白名單與防線規則。所有 Gencode 生成題型的答案檢核、以及題庫原題批改，均須遵循本契約，嚴格防止使用生硬的 raw string compare 導致學生端判定出錯。

---

## 1. AnswerContract 結構 (Schema)
每個題型的 `answer_contract` 必須定義以下欄位：
```yaml
answer_contract:
  answer_type: numeric                    # 答案型態白名單值
  equivalence_type: numeric_exact         # 等價判定白名單值
  checker_key: numeric_checker            # 批改器識別碼
  order_matters: false                    # 多值答案時，順序是否會影響判定
  accepted_format_notes: "支援分數與帶負號整數"
  canonical_answer_schema:                # 結構化標準答案定義
    type: "number"
    format: "integer"
  auto_checkable: true                    # 是否支援系統自動批改
  manual_review_policy: null              # 若不能自動批改，對應的人工審核策略
```

---

## 2. 核心白名單定義

### 2.1 answer_type 白名單
- `numeric`：常規實數。
- `integer`：整數。
- `rational`：有理數（分數）。
- `decimal`：小數。
- `percentage`：百分比。
- `expression`：代數式（含有 x, y 等變數之多項式）。
- `equation`：等式或方程式。
- `interval`：區間。
- `set`：集合。
- `ordered_tuple`：有序對（點坐標等）。
- `unordered_tuple`：無序對。
- `matrix`：矩陣。
- `choice`：選擇題標籤。
- `boolean`：是非/二值判定。
- `text_short`：簡答文字。
- `free_response`：開放式詳答（不支援 auto_check）。
- `drawing`：作圖題（不支援 auto_check）。
- `handwriting`：手寫題（不支援 auto_check）。

### 2.2 equivalence_type 白名單
- `numeric_exact`：數值精確相等（整數等價）。
- `rational_equivalent`：分數等價（如 $\frac{2}{4}$ 等價於 $\frac{1}{2}$）。
- `decimal_tolerance`：帶容許誤差的小數比對。
- `percentage_equivalent`：百分比等價。
- `algebraic_equivalent`：代數多項式等價（利用 SymPy 展開化簡比對）。
- `equation_equivalent`：方程式等價。
- `interval_set`：數線區間等價。
- `unordered_solution_set`：無序解集合等價。
- `ordered_tuple_exact`：坐標點有序對精確比對。
- `unordered_tuple_equivalent`：無序多元組比對。
- `matrix_exact`：矩陣元素精確比對。
- `choice_label`：選擇題 A/B/C/D 標籤比對。
- `exact_string`：字串精確比對（不推薦用於數學題）。
- `case_insensitive_string`：不區分大小寫之字串比對。
- `manual_review_or_ai_judged`：非自動批改，標記後走人工或 AI 視覺判讀。

### 2.3 checker_key 白名單
必須與 equivalence_type 對應，包含：`numeric_checker`、`integer_checker`、`rational_checker`、`decimal_tolerance_checker`、`percentage_checker`、`expression_checker`、`equation_checker`、`interval_checker`、`set_checker`、`tuple_checker`、`matrix_checker`、`choice_label_checker`、`text_short_checker`、`manual_review_checker`、`ai_judged_checker`。

---

## 3. Legacy Canonical Mapping (舊欄位對應表)
舊代碼或 AI 產生的 legacy 欄位名稱必須在 Phase 2 被強制轉換（canonicalize）：
- `numeric_equivalence` $\rightarrow$ `numeric_exact`
- `numeric_equal` $\rightarrow$ `numeric_exact`
- `string_equivalence` $\rightarrow$ `exact_string`
- `exact_text` $\rightarrow$ `exact_string`
- `fraction_equal` $\rightarrow$ `rational_equivalent`
- `set_equal` $\rightarrow$ `unordered_solution_set`
- `interval_equivalence` $\rightarrow$ `interval_set`
- `inequality_solution_equivalence` $\rightarrow$ `interval_set`
- `expression_equivalence` $\rightarrow$ `algebraic_equivalent`

---

## 4. 嚴格防污染與比對防線

### 4.1 Equivalence 污染防線
1. **嚴禁 Self-Pollution**：若觀測到 `equivalence_type == problem_type_id`，此為嚴重污染，**必須立即清空並重新推論**。
2. **預設安全補齊**：
   - 當 `answer_type` 為 `numeric` 或 `integer` 且 `equivalence_type` 為空時，預設自動補齊為 `numeric_exact`。
   - 當 `answer_type` 為 `expression` 且 `equivalence_type` 為空時，預設自動補齊為 `algebraic_equivalent`。
3. **白名單守衛**：任何非白名單的自創 `equivalence_type` **絕對不可**寫入 registry。

### 4.2 絕對禁止 raw string compare 的情境
- **分數、小數、百分比**：嚴禁以字串直接對比（例如 `1/2` 與 `2/4`、`0.5` 與 `0.50`、`50%` 與 `0.5`），必須使用專屬有理數或小數 checker。
- **解集合、區間與集合**：元素順序不同或 LaTeX 格式不同（例如 `{1, 2}` 與 `{2, 1}`、`x > 2` 與 `(2, \infty)`），嚴禁 raw string 對比，必須解析為 set / interval 結構比對。
- **代數多項式**：嚴禁直接對比 LaTeX 字串（例如 `x^2 - 1` 與 `(x-1)(x+1)`），必須使用 SymPy 進行 `algebraic_equivalent` 展開化簡驗證。
- **選擇題標籤**：前台輸入與正確答案均必須 normalize 為 `A`, `B`, `C`, `D` 單一字元，嚴禁包含括號或完整選項內容（如 `(A)` 或 `A. 5`）直接與 raw string 比對。
- **畫圖、證明與開放說明**：**絕對不可**使用 `exact_string` 企圖矇混自動批改，此類題型之 `auto_checkable` 必須標記為 `false`，且將 `equivalence_type` 設為 `manual_review_or_ai_judged`。

### 4.3 執行期展現型態強制作戰原則（Runtime Presentation Mode Coercion）

本節為 v0.3 增量法規，**不刪除、不更名** v0.2 之 `answer_contract` 欄位；在 Phase 3 序列化封裝層以記憶體覆寫方式校正「展現型態」，防止歷史幽靈快取造成前台題型錯位。

#### 4.3.1 觸發時機與讀取來源

在 Phase 3 啟動序列化封裝的**第一毫秒**，全域管線（`pipeline_orchestrator` / `phase3_skill_codegen`）必須同步讀取：

1. 當前題型之 **canonical `problem_type_id` 前綴**（如 `expression_`、`integer_`、`single_choice_`）。
2. `answer_contract.answer_type` 與 `answer_contract` 內之選項特徵旗標（`choices_required`、`source_has_choices`、`choice_count` 等 Contract Token）。

上述 Token **僅作資料驅動判定**，禁止以 skill_id 或章節名稱寫死分支。

#### 4.3.2 選擇題型強制作戰（Single Choice Coercion）

若 Contract Token 顯示該題型屬於選擇題契約，或具備可辨識之選項特徵，管線必須在記憶體中**強制覆寫**下列執行期配置（寫回 induced spec 與 generator payload 前均須一致）：

| 欄位 | 強制值 |
|------|--------|
| `presentation_mode` | `"single_choice"` |
| `answer_type` | `"single_choice"`（或與前台相容之 choice 家族） |
| `checker` / `checker_key` | `"choice_label_checker"` |
| `answer_equivalence` / `equivalence_type` | `"choice_label"` |
| `choices_required` | `true` |
| `frontend_render_choices` | `true` |

並**實體隔離**隨機選項池：四選項須由確定性數學干擾項演算法產生，經 shuffle 後綁定 A/B/C/D 標籤；`question_text` 內不得嵌入 `(A)(B)(C)(D)` 字面，與 §4.2 一致。

**禁止**：在選擇題路徑殘留 `expression_checker` 或 `numeric_checker` 作為最終批改器（除非 Spec Gate 明確標記 `blocked` 並停止發布）。

#### 4.3.3 簡答題型強制作戰（Short Answer / Expression Coercion）

若 Contract Token 顯示該題型屬於代數式、整數或數值計算應用（非選擇題家族），管線必須在**編譯前夕**自動校正為 `presentation_mode: "short_answer"`，並依 `problem_type_id` 前綴對齊 checker 鏈：

| 前綴 Token | `answer_type` 校正 | `checker_key` 剛性綁定 |
|------------|-------------------|------------------------|
| `expression_` | `expression` | `expression_checker` + `algebraic_equivalent` |
| `integer_` | `integer` | `integer_checker` + `numeric_exact` |
| `numeric_` | `numeric` | `integer_checker` 或 `numeric_checker` + `numeric_exact` |

**洗淨義務**：凡從歷史 induced cache、draft spec 或 Phase 1 幽靈列繼承之 `choice_label`、`source_has_choices`、`choices_required: true` 等 Choice 殘留合約，必須在 `_sync_phase3_runtime_specs_from_draft` 與 `_reinforce_canonical_answer_contract` 階段清除或降級為 `source_bank_only`，不得帶入 Runtime Generation。

#### 4.3.4 與 LLM 的邊界

展現型態強制作戰屬**確定性管線責任**；LLM 僅可於 Phase 3 Codegen 建議題幹，**不得**於 runtime 判斷「這題是不是選擇題」。最終 checker 以本節覆寫後之 `answer_contract` 為準。

---

## 5. 版本紀錄
| 日期 | 版本 | 職責與變更內容 | 紀錄人 |
|---|---|---|---|
| 2026-05-25 | v0.1 | 首版答案契約定義，內含過多流程性描述 | Codex |
| 2026-05-31 | v0.2 | 重整 v0.2，將 Phase 1/2 流程與品質稽核工具移出，專注於 answer_type、equivalence_type 白名單、legacy 對應表、污染防線與結構化比對防護，確保 100% 乾淨 UTF-8 | Antigravity |
| 2026-06-01 | v0.3 | 增量新增 §4.3 執行期展現型態強制作戰；完整保留 v0.2 白名單與 Schema | 首席系統架構師 |

*本文件職責：定義答案判定契約、比對 whitelist、legacy canonical mapping、精確批改防禦規則，以及 Phase 3 展現型態強制校正。*
*不負責事項：不定義 ProblemType 規格包與資料結構、亦不定義 pipeline 各階段流程。*
*應參考的其他 SOP：[Gencode與AgentSkillV2整合總體設計_v0.3.md](Gencode與AgentSkillV2整合總體設計_v0.3.md)、[AgentSkillV2_ProblemType規格包設計_v0.3.md](AgentSkillV2_ProblemType規格包設計_v0.3.md)。*