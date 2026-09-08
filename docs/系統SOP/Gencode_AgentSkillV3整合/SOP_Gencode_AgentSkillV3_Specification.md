# Gencode × AgentSkillV3 核心規範說明書

> **文件版本**：v1.13  
> **文件定位**：本文件為 Gencode × AgentSkillV3 **唯一規範權威**（原則、契約、狀態、錯誤碼、Gate 定義、學生端作答契約與批改標準）。流程與時序見配套 [SOP_Gencode_AgentSkillV3_PipelineFlow.md](./SOP_Gencode_AgentSkillV3_PipelineFlow.md)（唯一流程權威）。

---

## 0. 錯誤快速索引

| 關鍵字／錯誤 | 查詢章節 |
| --- | --- |
| component_id | 2. 一題一最小生成單位 |
| 一題一 generator | 2. 一題一最小生成單位 |
| problem_type_id | 3. Skill-Fixed Domain |
| fixed_domain_key ≠ ready | 10.1 Exact Capability Readiness Gate |
| ready_to_rebuild | 10.1 Exact Capability Readiness Gate |
| placeholder / NotImplementedError | 10.2 Executable Workspace Gate |
| capability 狀態 | 10.3 Capability 狀態定義 |
| checker_key | 8. Answer Contract 與 Checker 規則 |
| equivalence_type | 8. Answer Contract 與 Checker 規則 |
| decimal_tolerance_checker | 8. Answer Contract 與 Checker 規則 |
| multi_part | 5. 五種套餐契約 |
| table_fill | 5. 五種套餐契約 |
| drawing | 5. 五種套餐契約 |
| ui_contract | 6. Presentation Mode 與 UI Contract |
| canonical_answer | 8. Answer Contract 與 Checker 規則 |
| verified blocker | 10. Gate 與錯誤碼責任分區 |
| source fidelity | 10.4 Textbook Source Fidelity Gate |
| answer oracle | 10.5 Answer Oracle Gate |
| oracle_source | 10.5 Answer Oracle Gate |
| missing_ground_truth | 10.4 / 10.5（Policy reason；非「學生版無答案」） |
| constraint | 9. 變數與約束分層 |
| AI 修改前／後回報 | 11. AI Implementation Contract |

---

## 1. AI / Agent 執行規則

1. 遇到錯誤先查 SOP 錯誤索引，再讀對應章節。
2. 流程、時序、狀態與分流以 PipelineFlow 為準。
3. 欄位、契約、checker、UI 與 Gate 以 Specification 為準。
4. 修改前先確認 production code 的真實行為。
5. SOP 的 `[Current]` 定義應有行為；production code 表示目前實作。
6. 若兩者不一致，先回報差異，再依 `[Current]` 規則最小修改。
7. `[Planned]` 不得宣稱已實作，也不得直接當成必填 contract。
8. `[Deprecated]` 不得用於產生或修改程式。
9. 一個任務只修改一個責任層，原則上限 1～2 個函式。
10. 缺乏直接證據時標記 `[Unknown]`，不得自行猜測。
11. 不得依 skill_id 或 example_id 新增個別數學補丁。
12. 修改後必須執行局部離線驗證並回報是否符合 SOP。
13. 修改程式前／後必須依 §11 AI Implementation Contract 完整回報；缺任一欄位即不得開始或宣稱完成修改。

---

## 2. 一題一最小生成單位 (Current)

本節為 **一題一 generator** 的唯一規範權威。流程文件僅引用本節，不得另立較弱或較寬鬆的定義。

### 2.1 一對一隔離關係

$$\text{textbook\_example\_row} \rightarrow \text{component\_id} \rightarrow \text{components/src\_<textbook\_example\_id>/} \rightarrow \text{generate.py}$$

教材中每一道原題都是獨立隨機生成的最小元件，`component_id` 恆等於 `src_{textbook_example_id}`。

### 2.2 最小生成單位必須同時滿足

每一筆 textbook example **必須**對應：

| 項目 | 要求 |
| --- | --- |
| `component_id` | 一筆 textbook example = 一個 `component_id` |
| 目錄 | 一個獨立 component 目錄（`components/src_<textbook_example_id>/`） |
| 原始碼 | 一個獨立 `generate.py`、`metadata.py`、`get_hint.py` |
| Tracker | 一筆獨立 tracker 紀錄 |
| Domain operation | 相同 capability **僅可共用 Domain operation**，**不得合併 generator** |

### 2.3 開發禁令

* 嚴禁將多道教材題目合併在同一個 component 資料夾中。
* 嚴禁因為共用 Domain Function／operation／capability 而合併 component 或合併 `generate.py`。
* 嚴禁在程式碼中依據 `skill_id`、`example_id` 或 `component_id` 寫死數學計算、數值或特例分支。
* 單一 component 失敗僅將其排除，絕不可使同單元其他 `verified` 組件無法發布。
* 建置、驗證、tracker 更新必須逐 component 獨立執行；不得以 capability 分組取代逐題 generator。

### 2.4 與 Capability 分組的邊界

* Capability 分組**只用於**：Exact Readiness 檢查、proposal 去重、Domain operation 共用。
* Capability 分組**不得用於**：合併 generator、合併 component 目錄、合併 tracker、以一題結果代表同組其他題。

流程層的 Recovery Orchestrator 與 rebuild 規則見 PipelineFlow §4.4、§4.5。

---

## 3. Skill-Fixed Domain (Current)

* **行政歸屬**：`textbook_examples.skill_id` 是單題唯一行政歸屬權威，AI 不得手動修改或重新決定。
* **Registry 決定路由**：由 [taxonomy_registry.py](file:///e:/Python/Mathproject_tvet_mathB/core/registry/taxonomy_registry.py) 解析的 `fixed_domain_key` 決定唯一物理 Domain Module，AI 嚴禁修改 `skill_id`、改派 `fixed_domain_key` 或跨 Domain 借菜。
* **共享算子**：共享數學算子 (Shared Mathematical Primitive) 允許跨 Domain 調用，但不改變上層 routing domain。
* **型別驗證**：若發現 operation 不符時回報為 `operation_contract_mismatch`，禁止以更換 Domain 逃避。
* **Readiness 邊界**：`fixed_domain_key` 存在**不等於** capability ready。完整就緒條件見 §10.1 Exact Capability Readiness Gate。

---

## 4. 西堤選餐法：題型、呈現、作答與輸入元件

### 4.1 四層分離 (Current)
任何出題規格皆需嚴格遵循以下四層獨立定義與解耦，四層不得混用：
$$\text{數學內容層} \rightarrow \text{Data Presentation (呈現維度)} \rightarrow \text{Answer Type (作答維度)} \rightarrow \text{Presentation Mode / UI Contract (元件外觀)}$$

### 4.2 Data Presentation 正式選項 (Current)
* `text` (純文字題幹)
* `image` (靜態圖片呈現)
* `graph` (動態幾何或函數圖形)
* `readonly_table` (唯讀表格數據呈現)
* `canvas` (作圖專用空白繪圖區)

*注意：Data Presentation 僅用來描述題幹資料如何呈現，與學生如何作答無關。*

### 4.3 五種正式 Answer Type (Current)
* `short_answer` (簡答題)
* `single_choice` (單選題)
* `multi_part` (多小題題型)
* `table_fill` (表格填空題)
* `drawing` (作圖題)

### 4.4 Answer Type 判定順序 (Current)
對教材原題進行作答套餐分類時，**必須**依教材原始作答拓撲，依以下優先級順序進行，不得僅依 Domain、答案數量或題面是否有圖表推斷：
1. **答案是否必須直接填入表格指定 cell？** $\rightarrow$ `table_fill` (優先級最高，優先於 `multi_part` 判定)
2. **是否有兩個以上獨立小題？** $\rightarrow$ `multi_part`
3. **是否要求學生作圖，且作圖為主要答案？** $\rightarrow$ `drawing` (即使有 expected_answer 字串，亦不得降級為 `short_answer`)
4. **是否提供選項且只有一個正解？** $\rightarrow$ `single_choice`
5. **其餘** $\rightarrow$ `short_answer`

*分類決策成立後，才得依據答案格式選擇對應的 `presentation_mode` 與 `checker`。*

### 4.5 Presentation Mode / Input Widget 正式選項 (Current)
`presentation_mode` 是輸入元件的外觀，與 `answer_type` 分開：
* `integer` (整數輸入框)
* `rational` (分數輸入框)
* `equation` (方程式輸入框)
* `text_short` (普通短文字框)
* `single_choice` (單選 ABCD 按鈕)
* `multiple_inputs` (多重輸入框)
* `inline_table_input` (表格內儲存格輸入框)
* `canvas` (畫布交互元件)

### 4.6 西堤選餐法對照表與口訣 (Current)

| 概念 | 比喻 | 正式責任 |
| --- | --- | --- |
| **Skill** | 餐廳 | 教材行政歸屬。 |
| **Routing Domain** | 菜系/菜單 | Registry 的 `fixed_domain_key` 與 `allowed_operations`。 |
| **Operation** | 菜色 | AI 只能在白名單內選取所需數學操作。 |
| **Data Presentation** | 盤飾 | 題幹資料呈現模式，不影響作答方式。 |
| **Answer Type** | 作答套餐 | 教材原始作答拓撲，五選一。 |
| **Presentation Mode** | 餐具 | 輸入元件外觀 (`presentation_mode` 與 `ui_contract`)。 |
| **Checker** | 驗收標準 | `Answer Contract` 與 `checker_registry`。 |

> **西堤核心口訣**：  
> *Skill 決定餐廳。Registry 決定菜單。AI 只能在菜單內選菜。*  
> *教材原始作答拓撲決定套餐。答案格式決定餐具。Checker 決定如何驗收。*

### 4.7 必須保留的組合規則 (Current)
* `graph + single_choice` (呈現圖形，單選作答)
* `graph + multi_part` (呈現圖形，多小題填答)
* `readonly_table + short_answer` (唯讀表格數據，單一簡答)
* `readonly_table + single_choice` (唯讀表格數據，單選作答)
* `readonly_table + multi_part` (唯讀表格數據，多小題填答)
* `table_fill` (表格填空作答)
* `graph/canvas + drawing` (在 Canvas/Graph 上進行作圖作答)

*核心提示：有表格不一定是 table_fill (唯讀表可搭配 short_answer)；有圖不一定是 drawing (可為圖形搭配單選)；有多個答案不一定是 multi_part (表格內填空為 table_fill 優先)。*

---

## 5. 五種套餐契約 (Current)

本節為前台作答元件與驗證的剛性邊界。

### 5.1 `short_answer` (單一簡答)
* **限制**：一個輸入框，不得承載兩個或以上小題的輸入。

### 5.2 `single_choice` (單選題)
* **限制**：選項內容不得重複，必須有且僅有唯一正解。批改時必須比對實體 semantic answer，不得僅依選項的 ABCD 位置進行匹配。

### 5.3 `multi_part` (多小題)
* **核心 UI**：每小題擁有獨立的 `field_key` 輸入框與對應 `answer_order`。
* **限制**：評分必須支援 per-part grading，嚴禁將小題串聯成逗號分隔的單一簡答字串。

### 5.4 `table_fill` (表格填空)
* **正式契約欄位**：`table_question` (表格題幹)、`blank_cells` (儲存格陣列，包含 `row`, `col`, `field_key`, `answer_order`, `show_blank_labels` 等核心屬性)。
* **限制**：
  * 輸入框必須精確渲染於表格 Cell 內。
  * `blank_cells` 的 row 與 col 坐標不得重複。
  * `field_key` 屬內部隨機標記，嚴禁顯示給學生。
  * `show_blank_labels` 預設為 `False`，若為 `False` 時題幹嚴禁要求學生「求解 a、b、c、d」。
  * 嚴禁退化為表格下方的一排輸入框。

### 5.5 `drawing` (作圖題)
* **正式契約屬性**：
  ```python
  drawing_required = True
  ai_check_required = True
  text_answer_enabled = False
  submit_button_enabled = False
  success_dialog_required = True
  ```
* **正常成功流程**：前台禁用文字輸入與一般 submit $\rightarrow$ 學生於 Canvas 作圖 $\rightarrow$ 點擊評分觸發 AI Check $\rightarrow$ AI 批改通過後，鎖定 Canvas 與評分按鈕 $\rightarrow$ 記錄答對事實，顯示 `success_dialog` $\rightarrow$ 學生確認後點擊下一題。
* **批改錯誤或 API 失敗流程**：不得記錄答對，前台不得跳題，必須完整保留學生在 Canvas 上的作圖，恢復評分按鈕，並於介面上顯示可操作的錯誤提示。

---

## 6. Presentation Mode 與 UI Contract (Current)

本節決定 Phase 3 封裝中 `GENERATOR_SPECS` 規格陣列項目的欄位定義。

### 6.1 規格欄位對照表

| 欄位名 | 類型 | 預設值/格式 | 狀態 | 證據來源 |
| --- | --- | --- | --- | --- |
| `problem_type_id` | `str` | `"point_slope"` 等 | `[Current]` | [phase3_skill_codegen.py](file:///e:/Python/Mathproject_tvet_mathB/core/gencode/phase3_skill_codegen.py#L204) |
| `base_problem_type_id` | `str` | 基礎題型 ID | `[Current]` | [phase3_skill_codegen.py](file:///e:/Python/Mathproject_tvet_mathB/core/gencode/phase3_skill_codegen.py#L216) |
| `checker_key` | `str` | `"integer_checker"` 等 | `[Current]` | [phase3_skill_codegen.py](file:///e:/Python/Mathproject_tvet_mathB/core/gencode/phase3_skill_codegen.py#L205) |
| `equivalence_type` | `str` | `"numeric_exact"` 等 | `[Current]` | [phase3_skill_codegen.py](file:///e:/Python/Mathproject_tvet_mathB/core/gencode/phase3_skill_codegen.py#L206) |
| `generator_readiness` | `str` | `"runtime_ready"` | `[Current]` | [phase3_skill_codegen.py](file:///e:/Python/Mathproject_tvet_mathB/core/gencode/phase3_skill_codegen.py#L207) |
| `answer_type` | `str` | `"short_answer"、"single_choice" 等` | `[Current]` | [phase3_skill_codegen.py](file:///e:/Python/Mathproject_tvet_mathB/core/gencode/phase3_skill_codegen.py#L210) |
| `template_slot` | `str` | 模板位置標記 | `[Current]` | [phase3_skill_codegen.py](file:///e:/Python/Mathproject_tvet_mathB/core/gencode/phase3_skill_codegen.py#L212) |
| `value_type_prefix` | `str` | `"integer"` 等前綴 | `[Current]` | [phase3_skill_codegen.py](file:///e:/Python/Mathproject_tvet_mathB/core/gencode/phase3_skill_codegen.py#L214) |
| `target_task` | `str` | 目標任務標記 | `[Current]` | [phase3_skill_codegen.py](file:///e:/Python/Mathproject_tvet_mathB/core/gencode/phase3_skill_codegen.py#L219) |
| `presentation_mode` | `str` | `"integer"、"rational" 等` | `[Current]` | [phase3_skill_codegen.py](file:///e:/Python/Mathproject_tvet_mathB/core/gencode/phase3_skill_codegen.py#L223) |
| `answer_shape` | `str` | 答案外觀 | `[Current]` | [phase3_skill_codegen.py](file:///e:/Python/Mathproject_tvet_mathB/core/gencode/phase3_skill_codegen.py#L225) |
| `schema_version` | `str` | 契約版本 | `[Planned]` | 待 M1 實施後啟用 |
| `skill_id` | `str` | 大綱 ID | `[Planned]` | 待 M1 實施後啟用 |
| `example_id` | `int` | 例題 ID | `[Planned]` | 待 M1 實施後啟用 |
| `component_id` | `str` | 元件 ID | `[Planned]` | 待 M1 實施後啟用 |
| `classification_status`| `str`| 分類狀態 | `[Planned]` | 待 M1 實施後啟用 |
| `capabilities` | `list` | 能力列表 | `[Planned]` | 待 M1 實施後啟用 |
| `answer_contract` | `dict` | 答案完整合約 | `[Current]` | 學生作答與批改的正式權威；外層 legacy 僅供相容 fallback，衝突時以 nested contract 為準，由 validator／Gate 阻擋不一致合約 |

---

## 7. 禁止降級 Blocker 矩陣 (Current)

若違反以下任何一條規約，該組件在驗證 Gate 將直接判定為失敗，不得進入 `verified` 與 `published` 狀態：

| 違規項目 (Violation) | 處理後果 |
| --- | --- |
| 將 `multi_part` 多小題合併並壓入單一簡答輸入框中 | 不得 verified / published |
| 將 `table_fill` 表格填空改寫為表格外部輸入框 | 不得 verified / published |
| 表格填空顯示了內部 `field_key` 供學生識別 | 不得 verified / published |
| `drawing` 作圖題允許使用文字輸入或啟用了通用 submit 提交按鈕 | 不得 verified / published |
| `drawing` 未強制啟用 `ai_check_required` 流程 | 不得 verified / published |
| `drawing` 在 API 失敗或批改不通過時，靜默記為答對或允許學生跳題 | 不得 verified / published |
| `single_choice` 單選題選項內容重複或無唯一正解 | 不得 verified / published |
| metadata / config 中的 `answer_type` 與實際前台渲染的 UI 套餐不一致 | 不得 verified / published |
| 組件 schema、adapter 或 wrapper 遺失了必要 `ui_contract` 或 `answer_contract` | 不得 verified / published |
| 將多道 textbook example 合併為單一 generator／component | 不得 verified / published |
| 在 Exact Readiness Gate 未通過時標記 `ready_to_rebuild` 或重建 generator | 不得 verified / published |
| 以 placeholder／`pass`／`NotImplementedError`／固定空回傳通過 Executable Workspace Gate | 不得 verified / published |
| 以 AI／LLM 解題、generator 自算或 component-local formula 充當 Answer Oracle | 不得 verified / published |

---

## 8. Answer Contract 與 Checker 規則

本節決定答案表示、正規化與批改分發。

### 8.1 Answer Contract 權威
目前以 `answer_contract` 作為學生作答與批改的正式權威。外層 legacy 欄位（如 `checker_key`、`equivalence_type` 等）僅保留相容讀取用途。任何新 component 或 generator spec 均不得以 legacy 欄位取代 `answer_contract`。
若發生合約衝突，以 nested `answer_contract` 為準，並由 validator／Gate 阻擋不一致之合約。

批改資料權威順序為：
1. nested `answer_contract`
2. 題型專用正式結構：
   * `multi_part`：parts
   * `table_fill`：blank_cells
   * `drawing`：expected_drawing_spec
   * `single_choice`：choices／semantic mapping
3. canonical_answer (或 expected_drawing_spec 的 spec 設定)
4. legacy root 欄位（僅作相容 fallback）

### 8.2 五種 grading 規則
* **short_answer**：單一答案，由 checker_key 進行 dispatch（如 `integer_checker`, `rational_checker`, `decimal_tolerance_checker`, `linear_equation_equivalent_checker`, `text_short_checker` 等）。
* **single_choice**：選項語意批改 (semantic option grading)。經 `choice_value_to_label` 將學生答案與正確答案對齊，不依賴脆弱的 ABCD 絕對位置。
* **multi_part**：多欄位 (per-part grading)，且必須 all-parts-correct (所有 parts 皆答對) 才能判定 overall correct。
* **table_fill**：表格逐格批改 (per-cell grading)，且必須 all-cells-correct (所有 cells 皆答對) 才能判定 overall correct。
* **drawing**：AI 視覺評分 (AI grading)。必須經 AI 判定通過且信心值高於設定門檻才算 correct。

### 8.3 錯誤分流與批改語意原則
* **數學語意比對**：數值、分數、小數應依數學語意比對，不得退化為字串相等對比；方程式應依等價性進行比較。
* **錯誤分流機制**：評分與執行期必須嚴密分開以下狀態：
  * **未作答**：由前端攔截，不得發送請求。
  * **parse failure**：如輸入格式非法，返回格式錯誤提示引導學生修正，不計為學生答錯。
  * **contract mismatch**：合約不匹配，判定答錯或觸發系統錯誤。
  * **checker execution failure / system error**：評分器或系統執行異常，記錄日誌並返回系統錯誤，**絕不得**被靜默當成學生答錯。
  * **一般答錯**：比對結果不符，返回 incorrect。

### 8.4 數學答案檢核原則

所有數學答案類 checker 必須採：

```text
safe parse → normalize → mathematical equivalence → optional required-form validation
```

不得只做 `strip()` / `lower()` / `string == string`。

規則：

1. **數值**依數學值比較，不做純文字比對。例如 canonical `2` 應接受 `2`、`+2`、`2.0`（若 contract 允許 numeric equivalence）。
2. **分數**允許等價分數。例如 `1/2` = `2/4` = `3/6`。是否接受小數由 `answer_contract` / `equivalence_type` 決定。
3. **代數式**支援隱含乘法與代數等價。例如 `(x-1)(x-2)` = `(x-2)(x-1)` = `(x - 1) (x - 2)`；亦應接受 `2x`、`2(x+1)`、`x(x+3)`。
4. **方程式**依等價性判斷，不比對左右兩邊字串。例如 `x=3` = `3=x` = `2x=6` = `x-3=0`。
5. **multi_part** 必須逐 part 依該 part 自己的 checker 做數學等價，禁止把整個 dict stringify 後字串比對。
6. **single_choice** 使用 semantic answer mapping：學生選到的 label 先對應選項語意值，再與正解語意比較；shuffle 後 mapping 必須同步。
7. **text_short** 只用於真正文字答案（如「第一象限」「無解」），不得把數學式誤派去 text checker。
8. parse failure → `ANSWER_PARSE_FAILED`（不算學生答錯）。
9. checker exception → `CHECKER_EXECUTION_FAILED`（不得靜默當成答錯）。
10. **因式分解等題型**：先驗證代數等價，再驗證 required form。

代表案例：

| canonical | 學生輸入 | 結果 |
| --- | --- | --- |
| `(x-1)(x-2)` | `(x-2)(x-1)` | PASS（代數等價） |
| `1/2` | `2/4` | PASS（分數等價） |
| `x=3` | `3=x`、`2x=6` | PASS（方程等價） |
| `(x-1)(x-2)` 且 contract 要求 factorized form | `x^2-3x+2` | FAIL required-form（雖代數等價，但未完成因式分解） |

等價與形式不得混為一談：未要求 factorized form 時，展開式可依代數等價通過；一旦 `answer_contract` 要求 `required_form=factorized`（或 `answer_shape=factored_expression`），展開式必須 FAIL。

---

## 9. 變數與約束分層 (Current)

* **參數約束**：在組件執行期調用 `generate()` 時，由各 component 或 Domain 執行自身已實作的變數範圍抽樣與局部防禦性檢查。
* **學生端輸入驗證**：如 `分母 != 0` 屬於作答批改期 Answer Parser 與 Checker 職責，嚴禁混入出題期的變數約束。
* **[Planned] 宣告式變數與約束**：支援 `ConstraintPolicy` 引擎（變數 `variables`、`hard_constraints`（支援二元比較如 `>=`, `>`, `<=`, `<`, `==`, `!=`）、`quality_constraints` 與 `sampling_policy`）。

---

## 10. Gate 與錯誤碼責任分區

所有錯誤碼按層級嚴格分類：

| 錯誤碼 | 責任層 | 影響範圍 | 正確處置 | 狀態 |
| --- | --- | --- | --- | --- |
| `SKILL_ONBOARDING_NEEDS_REVIEW` | Phase 1 / Onboarding | 整 Skill | 記錄於 needs_human_review，掛起待人工處理 | `[Current]` |
| `DOMAIN_FUNCTION_MISSING` | Phase 2 / Component | 單題 | 進入 Capability 自動生長閉環（見 PipelineFlow §4.3） | `[Current]` |
| `DOMAIN_CAPABILITY_UNRESOLVED` | Phase 1 / Capability | 單 capability | 建立 proposal，進入自動生長閉環；不得阻斷其他 capability | `[Current]` |
| `CAPABILITY_NOT_READY` | Capability Gate | 單 capability | Exact Readiness Gate 未通過，禁止 `ready_to_rebuild` | `[Current]` |
| `EXECUTABLE_WORKSPACE_INCOMPLETE` | Capability Gate | 單 capability | Executable Workspace Gate 未通過，不得標記完成 | `[Current]` |
| `GENERATOR_SPEC_MISSING_FIELD` | Spec Contract | 單題 | 排除該組件，不阻斷其他題 | `[Planned]` |
| `GENERATOR_SPEC_ANSWER_CONTRACT_CONFLICT` | Spec Contract | 單題 | 排除該組件，不阻斷其他題 | `[Planned]` |
| `GENERATOR_SPEC_UNSUPPORTED_VERSION` | Spec Contract | 單題 | 排除該組件 | `[Planned]` |
| `ANSWER_PARSE_FAILED` | Answer Runtime | 單題 (作答) | 提示格式錯誤，引導重新輸入 | `[Current]` |
| `ANSWER_CONTRACT_MISMATCH` | Answer Runtime | 單題 (作答) | 判定答錯 | `[Current]` |
| `CHECKER_EXECUTION_FAILED` | Answer Runtime | 單題 (作答) | 評分器內部執行錯誤，記錄日誌 | `[Current]` |
| `CONSTRAINT_SCHEMA_INVALID` | Sampling Runtime | 單題 (出題) | 約束結構有誤，阻斷發布 | `[Planned]` |
| `CONSTRAINT_UNSATISFIED` | Sampling Runtime | 單題 (出題) | 重新出題抽樣 | `[Planned]` |
| `SAMPLING_EXHAUSTED` | Sampling Runtime | 單題 (出題) | 超限拋出異常，拋棄該 seed | `[Planned]` |
| `CAPABILITY_IMMUTABILITY_VIOLATION` | Capability | 單題 | 自動管線寫入 production 唯讀區，Gate 安全攔截 | `[Current]` |
| `source_incomplete` [Policy] | Source Fidelity | 單題 | 題幹／圖表／公式等來源資產不完整；verified/package/publish = NO。不是 tracker enum。[Gap: production alignment required] | `[Current]` Policy |
| `source_corrupt` [Policy] | Source Fidelity | 單題 | 來源解析損毀；verified/package/publish = NO。不是 tracker enum。[Gap: production alignment required] | `[Current]` Policy |
| `oracle_unavailable` [Policy] | Answer Oracle | 單題 | 無 source-provided oracle，且尚無可解析之 shared Domain operation；進 capability growth。不是 tracker enum。[Gap: production alignment required] | `[Current]` Policy |
| `oracle_not_ready` [Policy] | Answer Oracle | 單題 | Domain operation 已識別但 Exact Readiness / Executable Workspace 未過；禁止以該 oracle 標記 VERIFIED。不是 tracker enum。[Gap: production alignment required] | `[Current]` Policy |
| `oracle_validation_failed` [Policy] | Answer Oracle | 單題 | Oracle 輸出未通過 per-component validator / checker / 20-seed consistency。不是 tracker enum。[Gap: production alignment required] | `[Current]` Policy |
| `missing_ground_truth` [Policy] | Answer Oracle | 單題 | **僅**當系統明確要求 source-provided answer evidence，且該來源本應存在卻遺失。不得用於「學生版課本本來就沒有答案」。不是 tracker enum。[Gap: production alignment required] | `[Current]` Policy |

### 10.1 Exact Capability Readiness Gate (Current)

本節為 **capability 是否可 `ready_to_rebuild`** 的唯一規範權威。

**明定**：`fixed_domain_key` 存在 **不等於** capability ready。僅有 Domain 路由鍵不足以重建任何 generator。

只有以下條件**全部**存在且一致時，才可標記 `ready_to_rebuild`：

| # | 必要條件 | 說明 |
| --- | --- | --- |
| 1 | capability declaration | capability 已正式宣告，可被解析與追蹤 |
| 2 | operation registry spec | operation 已登錄於 registry，規格完整 |
| 3 | executable implementation | 可執行實作存在，且通過 §10.2 Executable Workspace Gate |
| 4 | adapter route | adapter 路由存在，可將 domain 結果轉為 component payload |
| 5 | presentation／answer contract | presentation 與 answer contract 完整且一致 |
| 6 | checker | 對應 checker 已登錄且可執行 |
| 7 | component validator | 每個 source example 具備獨立 validator |
| 8 | selected operation ≡ required operation | 選定 operation 與 required operation 一致 |

**Gate 失敗處置**：

* 不得標記 `ready_to_rebuild`。
* 不得重建任何 generator。
* `partial_capability`（僅部分條件滿足）**不得**重建 generator。
* 失敗 capability 必須隔離並記錄 `failure_stage`，不得阻斷其他 capability 或其他 component。

### 10.2 Executable Workspace Gate (Current)

本節為 **workspace／implementation 是否可判定完成** 的唯一規範權威。

#### 10.2.1 不得判定為完成的情形

以下任一成立，即判定 **未完成**（`implementation_incomplete` 或 `validation_failed`），不得進入 promotion：

| 禁止通過項 | 說明 |
| --- | --- |
| `pass` | 空實作或僅 `pass` 語句 |
| `NotImplementedError` | 明確未實作 |
| placeholder | 佔位字串、TODO、stub 註記充當完成 |
| 固定空回傳 | 固定回傳 `{}`、`None`、空字串等無數學內容結果 |
| 無 assertion 測試 | 測試檔存在但無有效 assertion |
| 僅編譯通過 | 語法／import 通過不足以證明正確性 |
| 僅 payload schema 通過 | schema 形狀正確不足以證明數學與批改正確 |

#### 10.2.2 必須實際驗證的項目

必須**實際執行並通過**以下驗證，缺一不得判定完成：

| # | 驗證項 | 要求 |
| --- | --- | --- |
| 1 | mathematical invariants | 數學不變量成立（非字串形狀檢查） |
| 2 | adapter conversion | adapter 轉換結果正確且可被 component 消費 |
| 3 | answer contract | answer contract 與產出答案一致 |
| 4 | checker 正解／錯解 | checker 對正解通過、對錯解拒絕 |
| 5 | fixed seeds | 固定 seed 可重現且結果穩定 |
| 6 | 每題獨立 validator | 每個 source example 有獨立 validator，不得以同 capability 一題結果代表其他題 |

### 10.3 Capability 狀態定義 (Current)

本節為 capability lifecycle **狀態名稱**的唯一規範權威。狀態轉移時序見 PipelineFlow §4.3、§7.3。

| 狀態 | 含義 |
| --- | --- |
| `proposed` | capability 缺口已建立 proposal（含去重後的正式提案） |
| `approved` | proposal 通過 auto triage／規則審核，允許進入 draft |
| `draft_scaffold_ready` | 隔離 workspace 的 scaffold（規格、測試骨架、registry／adapter patch 草稿）已就緒 |
| `implementation_incomplete` | 實作存在但未通過 Executable Workspace Gate |
| `validation_failed` | 已執行完整驗證但未通過 |
| `ready_for_human_review` | 隔離實作與 full validation 皆通過，等待 production promotion 前人工審核 |
| `promoted` | 已原子性寫入 production（registry、implementation、adapter 等） |
| `verified` | promotion 後經逐題 rebuild／validator 確認可用 |

**狀態使用禁令**：

* 不得跳過 `ready_for_human_review` 直接 `promoted`（人工審核位置見 PipelineFlow §4.6）。
* 不得在 `implementation_incomplete`、`validation_failed` 或未通過 Exact Readiness Gate 時標記 `ready_to_rebuild`。
* `promoted` 後仍須逐 component 獨立 rebuild 與 tracker 更新，才得進入 component 層 `verified`。

### 10.4 Textbook Source Fidelity Gate (Current)

本節為 **教材來源是否足以建立 component 並進入後續 Oracle / 驗證** 的唯一規範權威。

#### 10.4.1 根本假設

本系統 `textbook_examples` 主要來源為 **學生版教科書**。學生版教材在正常情況下可能沒有：

* `correct_answer`
* `detailed_solution`
* 官方答案頁

**「教材沒有答案」本身不是 component failure，也不得自動導致不能 VERIFIED。**  
本 Gate **不要求**學生版課本必須提供答案。

#### 10.4.2 本 Gate 證明什麼

Source Fidelity PASS 代表來源足以證明：

1. 題幹完整
2. 數學條件完整
3. 圖片 / 表格 / 公式資產完整（題面若依賴該資產）
4. 題目作答拓撲可判定
5. `skill_id` 來源可信
6. 無 parse corruption
7. 無關鍵 source loss

完整學生版隨堂練習 + 無 `correct_answer` + 無 `detailed_solution` **仍可** `source_fidelity = PASS`。

#### 10.4.3 FAIL 條件

| 情境 | Policy reason | 處置 |
| --- | --- | --- |
| 題幹破損、關鍵條件缺失 | `source_incomplete` | component 仍須建立；verified/package/publish = NO |
| 題目依賴配圖／表格但缺少資產 | `source_incomplete` | 同上 |
| 公式／題幹 parse 損毀 | `source_corrupt` | 同上 |

以上為 **Policy eligibility condition / reason**，不是 Current production tracker enum。不得擅自新增 production enum；不得固定映射 `needs_human_review`。標示：`[Gap: production alignment required]`。

**不得**因為沒有答案自動標記 `missing_ground_truth` / failed / blocked。

### 10.5 Answer Oracle Gate (Current)

本節為 **canonical answer 之可信權威來源** 的唯一規範權威。

正式 canonical answer 必須有可信 Answer Oracle。Generator implementation **不等於** mathematical oracle authority。

#### 10.5.1 合法 Oracle 兩類

**A. Source-provided Oracle**（記錄 `oracle_source=source`）

* `textbook_examples.correct_answer`
* 教材 `detailed_solution` 中明確存在的正式解答
* 教師手冊 / 官方答案
* 有 provenance 的正式 answer artifact

**B. Verified Mathematical Oracle**（記錄 `oracle_source=domain_operation`）

當學生版教材沒有答案時，可使用已通過 Capability / Domain 驗證的 shared mathematical oracle。必須**全部**滿足：

1. `fixed_domain_key` 正確
2. required operation 已登錄
3. Exact Capability Readiness Gate PASS（§10.1）
4. shared Domain operation 是獨立、可重用的 production implementation
5. operation 已通過 mathematical invariant tests
6. operation 已通過獨立 unit tests
7. component generator 只呼叫 oracle，不自行重寫相同數學公式
8. per-component validator 獨立驗證題目與 oracle output
9. shared checker 正解通過 / 錯解拒絕
10. 20-seed / fixed-seed validation PASS（**implementation consistency**，不是 Oracle 本身）

此情況即使教材沒有正式答案，Answer Oracle Gate 仍可 PASS。  
**不得**因 `oracle_source=domain_operation` 而降低其他 Gate。

#### 10.5.2 嚴格禁止的 Oracle

以下不得作為 Answer Oracle：

* AI / LLM 現場解題結果
* Agent 看題目後自己寫死答案
* component-local ad-hoc formula
* generator 內自己重寫的 domain math
* checker 反推答案
* 20-seed PASS 本身
* 「程式跑得過所以答案應該對」

**20 seeds 驗證 implementation consistency，不是 Answer Oracle 本身。**

#### 10.5.3 Generator / Oracle 分離

```text
generator implementation  ≠  mathematical oracle authority
```

Generator 可以：sample parameters、build question、call shared Domain operation、construct payload、construct answer_contract。

Generator 不可：自己定義該 capability 的核心數學演算法；自己產生答案後再自己當驗證權威。

同一 shared Domain operation 可供多個 components 共用。仍維持 `textbook_example : component = 1 : 1`。

#### 10.5.4 Oracle 未就緒時的 Policy reason

| 情境 | Policy reason |
| --- | --- |
| 無 source oracle，且尚無可解析之 shared Domain operation | `oracle_unavailable`（進 Capability Growth） |
| operation 已識別但 Exact Readiness / Executable Workspace 未過 | `oracle_not_ready` |
| oracle 輸出未通過 validator / checker / 20-seed consistency | `oracle_validation_failed` |
| 系統明確要求 source-provided evidence，且該來源本應存在卻遺失 | `missing_ground_truth` |

`missing_ground_truth` **不再**代表「學生版教材沒有答案」。一般學生版無答案不是錯誤。

以上同樣不是 production tracker enum；`[Gap: production alignment required]`。

### 10.6 VERIFIED 充要條件 (Current)

元件標記 `verified` 必須同時滿足：

```text
VERIFIED =
  Textbook Source Fidelity PASS
  AND Answer Oracle Gate PASS
  AND Exact Capability Readiness PASS
  AND Executable Component PASS
  AND Per-component Validator PASS
  AND Valid Answer Contract PASS
  AND Shared Checker Validation PASS
```

Source-provided Oracle → `oracle_source=source`。  
Verified Mathematical Oracle → `oracle_source=domain_operation`。

有 `correct_answer` / `detailed_solution` **不得**直接寫成 VERIFIED；仍須通過其餘 Gate。

#### 10.6.1 Source Fidelity & Answer Oracle 資格矩陣 (Current)

本表為 **可否進入 VERIFIED 資格判斷** 的唯一矩陣權威。Master SOP 必須與本表一致。

| 情境 | Source Fidelity | Oracle | 可否驗證 |
| --- | --- | --- | --- |
| 完整學生版題目，無答案，已有 verified domain oracle | PASS | domain oracle | YES |
| 完整題目 + 官方答案 | PASS | source oracle | YES |
| 題幹破損 | FAIL | 不論 | NO |
| 缺關鍵圖片 | FAIL | 不論 | NO |
| 題目完整但 operation 不存在 | PASS | unavailable | NO，進 capability growth |
| AI 自算答案 | PASS | INVALID | NO |

---

## 11. AI Implementation Contract (AI 程式修改規範)

本節為 AI／Agent **修改 production 或管線程式前／後回報格式**的唯一規範權威。缺欄不得開始修改；缺欄不得宣稱完成。

### 11.1 修改前必須回報

```text
錯誤責任層：[Phase 1 / Phase 2 / Spec Contract / Answer Runtime / Sampling Runtime / Capability / Recovery Orchestrator]
對應 SOP 章節：[Specification §x / PipelineFlow §y]
production code 現況：[1-3 句說明現行程式碼行為]
直接根因：[說明為何出錯]
預計修改範圍：[檔案與函式；點擊 file 連結]
不修改範圍：[明示不影響的組件、capability、其他題]
局部測試：[說明測試指令與預期]
停止條件：[說明何時算完成，以及何時必須停止不得擴大範圍]
```

### 11.2 實作約束

在撰寫與實作程式碼時，AI 必須遵守：

* 一個 Prompt 只處理一個微小任務，限改 1～2 個函式，優先 no-LLM。
* 禁止修改已發布的 `verified` 既有組件（除非根因代碼就在該組件內）。
* 同類工具或 shell 失敗最多重試 2 次，超過即停止，禁止反覆切換腳本或重寫排版。
* 不得依 skill_id、example_id、component_id 新增個別數學補丁。
* 不得合併多題 generator；相同 capability 僅可共用 Domain operation。
* 不得在 Exact Readiness Gate 未通過時重建 generator。
* 不得以 placeholder／僅編譯通過／僅 schema 通過宣稱 capability 完成。

### 11.3 修改後必須回報

```text
違反的 SOP 規則：[無／有 (說明理由)]
修改檔案與函式：[點擊 file 連結]
測試結果：[說明局部測試輸出]
是否新增特例：[必須為否]
是否呼叫 LLM：[必須為否]
是否影響其他 component：[必須為否]
SOP 與 production 是否已對齊：[是／否]
```

---

## 11.5 M2 Production Verification Summary

* **五套餐全面驗收**：五種 Answer Type（短答、單選、多小題、表格填空、作圖題）的前後端交互、契約與批改均已通過 production 唯讀驗收。
* **作圖題閉環完成**：drawing 題型已特別修復成功轉題期間的鎖定時間窗，確保在下一題渲染前持續鎖定防刷，且判錯與 system error 均能保留 canvas 並允許重試。
* **橫向一致性對齊**：UI renderer 互斥與題型切換時的狀態重設（canvas 清除、紅綠反饋與 styles 抹除）全數通過，無題型交界衝突與 silent fallback。
* **獨立性與安全**：所有題型均無特例補丁，驗收過程完全離線，未依賴外部 LLM，M2 已正式封板。

---

## 12. Planned Roadmap

| 里程碑 | 目標 | 狀態 |
| --- | --- | --- |
| M1 | Phase 3 Integrity Gate 邊界與最小相容檢查，不預設新增 Pydantic/schema_version | Planned |
| M2 | Answer Contract／Checker 一致化，五種 Answer Type 完成 UI、runtime grading、錯誤分流與橫向一致性驗收 | Completed |
| M3 | Runtime Variables／Constraints 變數取樣引擎，引進 `ConstraintPolicy` | Planned |
| M4 | Capability Extension 寫入保護與隔離；Exact Readiness／Executable Workspace Gate 與自動生長閉環對齊 production | Investigation |
| M5 | Phase 1 通用 Onboarding 分流器 | Planned |

---

## 13. Deprecated
* **全域 Nearest Template Fallback**：已廢除，禁止跨 Domain 相似度匹配。
* **V2 Handwriting 舊批改路由**：已廢除，全面由 V3 `drawing` 元件與評分器取代。
* **以 `fixed_domain_key` 存在推斷 capability ready**：已廢除，必須通過 Exact Capability Readiness Gate。
* **多題合併單一 generator**：已廢除，必須遵守 §2 一題一最小生成單位。
* **以 placeholder／僅編譯／僅 schema 通過判定 implementation 完成**：已廢除，必須通過 Executable Workspace Gate。
* **以「學生版教材沒有 `correct_answer` / `detailed_solution`」自動禁止 VERIFIED**：已廢除；Source Fidelity 與 Answer Oracle 為彼此獨立 Gate。
* **一律禁止 shared Domain operation 作為 Answer Oracle**：已廢除；僅允許通過 Exact Readiness 且獨立驗證之 Verified Mathematical Oracle。

---

## 14. Change Log

| 版本 | 核心變更 |
| --- | --- |
| v1.13 | 拆分 Textbook Source Fidelity Gate 與 Answer Oracle Gate；學生版無答案不得自動禁止 VERIFIED；允許 Exact-Ready 之 shared Domain operation 作為 Verified Mathematical Oracle；`missing_ground_truth` 限縮為 source answer 本應存在卻遺失 |
| v1.12.1 | Answer Runtime：數學答案類 checker 改為 safe parse → normalize → mathematical equivalence → optional required-form；parse failure / checker exception 不得靜默當成學生答錯 |
| v1.12 | 確立一題一最小生成單位完整契約；新增 Exact Capability Readiness Gate、Executable Workspace Gate、Capability 狀態定義；強化 AI Implementation Contract 修改前／後回報欄位；禁止降級矩陣納入 readiness／workspace 違規 |
| v1.11 | M2 正式封板：answer_contract 升格為 Current 權威；五種 Answer Type 完成 UI、grading、error handling 與橫向一致性驗收；修正 answer_type／presentation_mode 舊範例 |
| v1.10 | 定義 Bootstrap 與 Healer 狀態及升格 Gate，確定 generator/oracle/validator 三元分離 |
| v1.9 | 新增資料呈現/學生作答三層分離，正式確立五種作答套餐及禁止降級原則 |
| v1.8 | 移除全域 fallback，確立一題一 component_id 實體隔離與 practice.py 相容規範 |

---

## 15. Known Issues / Technical Debt

### 15.1 CartesianCoordinateSystem skill-local `check()` 仍為字串比對

`skills/vh_數學B1_CartesianCoordinateSystemEstablishment.py` 的 skill-local `check()` 仍存在字串比對，未走共用數學等價 checker。

本輪不處理：該問題不屬於共用 checker 層，也與 B1 Chapter 3 無關。runtime wrapper `check_answer` 在 contract 指向象限 checker 時仍走共用路徑；未對齊的是 skill 本體 `check()`。

狀態：deferred。禁止順手修改。
