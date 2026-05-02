# Agent Domain/Generator/Healer 盤點報告 (03_domain_generator_healer_inventory.md)

> ## 人工校正版註記
> 本報告為系統架構盤點文件，主要用途是記錄目前程式碼與目錄結構中「實際觀察到」的事實。涉及高職數學 B4 導入方向的內容，已依據目前 B4 原始教材資料校正：B4 主軸為排列組合、二項式、機率、統計與資料分析，不包含微積分、向量與圓錐曲線。因此本報告中的建議不得被視為最終 SOP，後續應以 B4 自動出題 SOP 為準。

## 1. Domain Logic / Function 清單

目前系統中已觀察到若干 Domain 領域函數切分，主要集中在 `core/` 與 `core/scaffold/` 目錄：
- **核心封裝介面 (Orchestrators)**：
  - `core/domain_functions.py` (RadicalSolver 高階封裝介面)
  - `core/integer_domain_functions.py`
  - `core/fraction_domain_functions.py`
  - `core/polynomial_domain_functions.py`
- **底層數學引擎 (Math Solvers)**：
  - `core/math_solvers/radical_solver.py` (負責具體根式化簡、同類項合併)
- **注入用工具庫 (Injected APIs / Scaffold)**：
  - `core/scaffold/domain_libs.py` 或 `core/prompts/domain_function_library.py` (包含 `IntegerOps`, `FractionOps`, `RadicalOps`, `PolynomialOps` 等，供模型在生成代碼中直接調用)

## 2. Generator / 出題流程清單

出題系統中觀察到包含生成流程與沙盒驗證的相關實作：
- **生成控制器**：
  - `core/code_generator.py`：主入口程式，負責構建 Prompt (`_build_prompt`)、呼叫模型 (`_call_ai`)，並協調後續的 Regex 與 AST 修復。
- **自動化技能庫**：
  - `skills/` 目錄存放大量已經由 AI 生成好的 Python 腳本 (例如 `jh_數學1上_*.py`, `gh_AreaUnderFunctionGraph.py`)，每個腳本都實作了 `generate()` 函數。
- **Prompt 構建**：
  - `core/prompts/prompt_builder.py` 負責將 SKILL.md、課本範例與特定 Ablation 層級 (Ab1/Ab2/Ab3) 組合。

## 3. Verifier / Answer Checker 清單

驗證與批改機制分為「生成時動態驗證」與「答題時判斷邏輯」：
- **生成時沙盒驗證**：
  - `core/code_generator.py` 中的 `_dynamic_sampling(final_code)`：啟動獨立的 subprocess (超時 5 秒) 來試跑生成的 `generate()`，確保回傳值為標準字典格式 (`question_text`, `answer` 等)，以防止死迴圈。
  - `core/validators/`：包含 `code_validator.py`, `syntax_validator.py`, `dynamic_sampler.py`。
- **用戶答題檢核 (Runtime Checker)**：
  - 每個在 `skills/` 中的技能腳本皆自帶 `check(user_answer, correct_answer)` 函數，通常實作了字串比對與基本浮點數等值比對。
- **特定單元輔助驗證**：
  - `tests/verify_factoring_quad.py`, `tests/verify_geometry_v12.py`, `tests/verify_visual.py` (輔助特定題型的視覺與邏輯驗證)。

## 4. Healer / Eval 清單

系統實作了多層次容錯修復管線 (Ab3 Full Healing)：
- **文字正則修復 (Regex Healer - `core/healers/regex_healer.py`)**：
  - `remove_trailing_artifacts` / `fix_mismatched_braces`：修復 C-style 結尾或缺失的字典括號 `}`。
  - `inject_domain_imports`：自動檢查並注入缺失的 API import。
  - `remove_duplicate_class_definitions`：刪除模型產生的重複類別宣告。
  - `fix_incorrect_class_method_calls` / `fix_latex_hallucinations_in_strings`：修復錯誤的方法調用與字串中幻覺的 LaTeX 標籤。
- **語法樹修復 (AST Healer - `core/healers/ast_healer.py`)**：
  - `visit_Call`：攔截危險函式 (`eval`, `exec` 換為 `safe_eval`)，強制切除 `input()` 避免阻塞。
  - `visit_While`：將無窮迴圈 `while True` 強制改為 `for _ in range(1000)` 的熔斷機制。
  - 幻覺函數防護：將不存在的多項式排版函數改寫，或是補上兜底的 `generate()` 函數。
  - `semantic_heal`：Hybrid Healer，在靜態修復失效時呼叫 AI 進行自我修正。
- **Eval 評分維度 (從 `agent_tools/analyze_results.py` 得知)**：
  - 評分採計五大維度：L1 (語法與運行時 15分)、L2 (函數契約 15分)、L3 (邏輯正確性 15分)、L4 (數學與視覺質量/MQI 20分)、L5 (架構設計 20分)。
  - Ablation 實驗驗證了 Prompt 工程 (Ab2) 與 Full Healing (Ab3) 帶來的顯著提分效果。

## 5. 可沿用到高職 B4 的部分

- **Generator 流程與沙盒隔離**：`code_generator.py` 中的 `_dynamic_sampling` 超時與沙盒執行設計可作為參考。
- **Regex & AST Healer 核心管線**：拔除 Markdown、括號配對、危險函數替換、無窮迴圈熔斷機制等防護網部分可沿用至 B4。
- **Eval 與 Ablation 框架**：L1 ~ L5 的五維度評分體系與實驗日誌 (`ExperimentLog`) 可作為 B4 測量參考。
- **Prompt 架構設計**：結合課本例題動態產生 Prompt 的邏輯部分可沿用。

## 6. 需要新增的部分

### B4 專屬 Domain Functions 建議
應新增或規劃：

- counting_domain_functions.py
  - factorial
  - permutation
  - combination
  - multiset_permutation
  - repeated_permutation
  - digit_arrangement_count
  - adjacent_arrangement_count
  - non_adjacent_arrangement_count

- binomial_domain_functions.py
  - binomial_coefficient
  - pascal_value
  - binomial_expansion_coefficients
  - binomial_term_coefficient

- probability_domain_functions.py
  - classic_probability
  - complement_probability
  - union_probability
  - conditional_probability
  - independent_joint_probability
  - expectation

- statistics_domain_functions.py
  - mean
  - median
  - mode
  - weighted_mean
  - data_range
  - quartiles
  - interquartile_range
  - variance
  - standard_deviation
  - linear_transform_stats
  - empirical_rule_interval

- table_chart_domain_functions.py
  - build_frequency_table
  - build_cumulative_frequency_table
  - relative_frequency
  - histogram_data
  - frequency_polygon_points
  - cumulative_frequency_points

- b4_validators.py
  - validate_choices_unique
  - validate_answer_in_choices
  - validate_numeric_answer
  - validate_probability_range
  - validate_statistics_dataset
  - validate_no_unfilled_placeholder
  - validate_latex_safety

### B4 Generator 方向
- generator 不應以 skill 為單位，而應以 problem_type 為單位。
- 同一個 generator 可以支援多個相近 problem_type。
- generator 應呼叫 domain function 計算答案，而不是自行硬算。
- generator 輸出應包含：
  skill_id
  subskill_id
  problem_type_id
  generator_key
  question_text
  choices
  answer
  explanation
  difficulty
  diagnosis_tags
  remediation_candidates
  source_style_refs

## 7. 初步缺口與風險

### B4 Healer 風險
- AST / Regex Healer 核心機制可作為參考，但 AST Healer 的白名單若寫死國中多項式或根式函式，B4 新 domain function 可能被誤砍。
- 需要為 B4 domain functions 建立 allowlist。
- B4 的 verifier 不應只靠字串與 float 比對。
- 機率與統計答案需要支援分數、小數、百分比、區間、集合式答案。
- 統計資料題需要驗證資料集是否合理、選項是否唯一、答案是否一致。
