# B4 Chapter 1 Runtime Closure Report

## 1. 本報告目的

說明：

- 本報告整理 B4 Chapter 1 自 Phase 4B 至 Phase 4E-16B 期間，deterministic int-answer 一般練習頁 runtime 的建置成果與凍結結論。
- 範圍僅限一般練習頁 runtime，不包含 adaptive route。
- 不包含 `future_ai_judged`、free-response 等非單一整數判分題型。
- 不代表 Chapter 1 所有教學型態或題型都已完備，而是代表「適合目前 deterministic int-answer runtime 的題型」已實質收尾；其餘題型改列 manual_review / excluded-like 或未來主線，避免與現行 runtime 混計。

## 2. 最終 coverage 狀態

依 `b4_ch1_runtime_coverage_matrix.csv` 與 `b4_ch1_runtime_coverage_matrix_summary.md` 之 Phase 4E-16B 收斂視角：

- **problem_type 總數**：28  
- **runtime_ready**：25  
- **planned_only**：0  
- **manual_review / excluded-like**（CSV 以 `excluded` 承載說明）：3  

| 類別 | 數量 | 說明 |
|---|---:|---|
| problem_type 總數 | 28 | Chapter 1 原始 coverage 分母（含已排除項） |
| runtime_ready | 25 | 已具 generator、question_router、skill wrapper，且 web smoke 通過之 int-answer 一般練習 runtime |
| planned_only | 0 | 一般 runtime 待辦已歸零（Phase 4E-15B／4E-16B 文件與矩陣一致） |
| manual_review / excluded-like | 3 | 不納入現行 deterministic int-answer runtime；改列未來 AI／視覺化／推導等路徑 |
| 補充 | — | `has_generator=yes` 為 26 係因 `binomial_expansion_basic` 有 generator 但非 runtime-ready，與「25 個接入」並行為真 |

## 3. runtime_ready 題型清單

以下 25 個 `runtime_ready` 之 `problem_type`，依主題分組（與 coverage matrix 及歷次 freeze／reconciliation 摘要一致）。

### Counting / Addition / Multiplication Principle

- `divisor_count_prime_factorization`
- `add_principle_mutually_exclusive_choice`
- `mult_principle_independent_choices`
- `mult_digits_no_repeat`

### Permutation

- `permutation_role_assignment`
- `permutation_formula_evaluation`
- `permutation_full_arrangement`
- `permutation_adjacent_block`
- `permutation_digit_parity`
- `repeated_permutation_digits`
- `repeated_permutation_assignment`
- `repeated_choice_basic`

### Combination

- `combination_definition_basic`
- `combination_basic_selection`
- `combination_group_selection`
- `combination_polygon_count`
- `combination_properties_simplification`
- `combination_required_excluded_person`
- `combination_restricted_selection`
- `combination_seat_assignment`

### Factorial

- `factorial_equation_solve_n`
- `factorial_evaluation`

### Binomial int-answer

- `binomial_coefficient_sum`
- `binomial_specific_term_coefficient`
- `binomial_equation_solve_n`

**注意：** Phase 4E-13F 之二項式 depth expansion 額外題型請見第 5 節；**不要**併入本節 25 項原始 `runtime_ready` 清單，以免與「28 題分母、25 題接入」之統計混淆。

## 4. manual_review / future_ai_judged 題型

以下 3 個題型目前為 **manual_review / excluded-like**（coverage 以 `excluded` 標示並於 notes 註記原因），不計入一般練習 deterministic runtime。

1. **`binomial_expansion_basic`**  
   - **原因**：答案為 `list[int]` 或完整多項式等多型態輸入，需 normalization、free-response 規格或 AI 判分，硬接現行 int-answer runtime 易產生非數學性誤判。  
   - **Future path**：handwriting AI checked、AI-judged free-response、係數列表／多項式 normalization。

2. **`tree_diagram_listing`**  
   - **原因**：樹狀圖著重視覺化與完整列舉能力，與現行「整數答案＋選項」runtime 目標不一致；不宜改作假計數題取代教學意圖。  
   - **Future path**：視覺化元件、structured-answer 列舉、AI 判分手寫或圖形作答。

3. **`pascal_triangle_derivation`**  
   - **原因**：推導型內容，不適合單一 deterministic int-answer 自動判分。  
   - **Future path**：教師審阅、AI-judged derivation、structured proof／推導流程。

## 5. 二項式 depth expansion 補強成果

Phase 4E-13F 額外接入 **3** 個二項式 depth 題型，用於教學厚度與能力補強；依專案決策，**不計入**原始 Chapter 1「28 題」coverage 分母與 `runtime_ready` 的 25 項統計。

| problem_type_id |
|---|
| `binomial_middle_term_coefficient` |
| `binomial_odd_even_coefficient_sum` |
| `binomial_specific_coefficient_with_negative_term` |

說明（與 Phase 4E-13F freeze 摘要一致）：

- 已接入 **question_router** 與對應 **skill wrapper** 路徑。  
- **pytest**：322 passed（該階段紀錄）。  
- **Web smoke**：`/practice/vh_數學B4_BinomialTheorem`、`/practice/vh_數學B4_BinomialCoefficientIdentities` 等頁面通過。  
- **answer** 仍為 **int**，非 `list[int]`。  
- **未**接入 `binomial_expansion_basic`。  
- 題幹模板與參數空間仍偏保守，後續可做 template／parameter enrichment（維持 int-answer 合約）。

## 6. 已完成的 runtime 架構

綜合 `b4_ch1_minimum_runtime_sop.md`、`b4_phase4d_runtime_wrapper_router_summary.md` 與 Phase 4E-7～4E-16 各次 freeze／reconciliation 文件所描述之實作型態：

1. **Deterministic generators**  
   - 使用 **seed** 控制可重現性。  
   - 支援 **seen_parameter_tuples**（或等價去重機制）以降低重題。  
   - **Output contract** 穩定（題幹、選項、答案型別一致）。  
   - **answer** 以 **int** 為主（一般練習判分路徑）。  
   - **choices** 合法、與答案一致。

2. **question_router**  
   - **Hard-coded registry** 明確對應 `generator_key` 與題型。  
   - **Canonical `skill_id`** 已清理並與教材／練習頁對齊。  
   - **不再使用** `vh_?詨飛B4_*` 等亂碼 alias（凍結與 reconciliation 文件多次確認）。

3. **Skill wrappers**  
   - Wrapper **呼叫** `generate_for_skill`（或專案約定之統一產題入口），不複寫題型核心邏輯。  
   - **`check()`** 以 **int／string** 比對為主，符合一般練習頁合約。  
   - **不**在 wrapper 內直接實作完整題型演算法。

4. **QA 流程**（Phase 4B～4E 累積之標準節奏）  
   - Generator 層 **pytest**。  
   - **Sample QA report**（抽樣品質）。  
   - Router／wrapper **pytest**。  
   - **Web smoke test**（可產題、可判對錯、LaTeX、無 500）。  
   - **Freeze summary**（階段凍結宣告）。  
   - **Coverage matrix reconciliation**（與程式接入狀態對齊，矩陣為進度唯一來源之一）。

## 7. 重要設計決策

1. **不把** `list[int]`／`list[str]` 等答案型別 **硬接入** 現行 deterministic general-practice runtime。  
2. **`binomial_expansion_basic`** **不**接入目前一般練習 runtime；改列 future_ai_judged／normalization 主線。  
3. **`tree_diagram_listing`** **不**改成假計數題以「凑」int-answer；保留列舉／視覺化教學意義。  
4. **`pascal_triangle_derivation`** **維持** manual_review／excluded-like，不強制 int-answer。  
5. **`future_ai_judged`／handwriting checked** 類 runtime **另開主線**，不與 deterministic int-answer 混為同一套完成度指標。  
6. **Adaptive route** **不在** Phase 4E 範圍內接入；本報告僅為 4F 規劃提供依據。  
7. **Coverage matrix** 為文件化進度之 **權威來源**；router／wrapper 接入後應 **立即** 以 freeze／summary 固化，避免口頭狀態與矩陣漂移。

## 8. Web Smoke Test 總結

以下主要 **practice** 頁面已於專案 smoke 流程中通過（可產題、可判對錯、LaTeX 正常、terminal 無 500），與 25 個 `runtime_ready` 及二項式 depth 補強所涵蓋之技能頁一致：

- `/practice/vh_數學B4_CombinationDefinition`  
- `/practice/vh_數學B4_CombinationApplications`  
- `/practice/vh_數學B4_MultiplicationPrinciple`  
- `/practice/vh_數學B4_PermutationOfDistinctObjects`  
- `/practice/vh_數學B4_RepeatedPermutation`  
- `/practice/vh_數學B4_FactorialNotation`  
- `/practice/vh_數學B4_AdditionPrinciple`  
- `/practice/vh_數學B4_CombinationProperties`  
- `/practice/vh_數學B4_PermutationWithRepetition`  
- `/practice/vh_數學B4_Combination`  
- `/practice/vh_數學B4_BinomialCoefficientIdentities`  
- `/practice/vh_數學B4_BinomialTheorem`  

## 9. 尚未做與不應誤解之處

請勿將本 closure 解讀為「Chapter 1 已全部完成」：

- **尚未**接 **adaptive route**（診斷式／適性路徑）。  
- **尚未**建立完整 **`future_ai_judged`** general-practice runtime 產品線。  
- **尚未**支援完整二項式展開之 **free-response** 與多型態輸入 **normalization**。  
- **尚未**支援樹狀圖 **繪圖與列舉** 之自動結構化判分。  
- **尚未**支援巴斯卡三角形 **推導** 之 deterministic 判分。  
- **Chapter 1 deterministic runtime 收尾**，**不等於** Chapter 1 所有教學型態或評量型態完成。  
- **二項式 depth expansion** 雖已接入並可再強化模板與 **difficulty**，但仍應維持 **int-answer** 合約；與「28 題主矩陣」分開追蹤。

## 10. 下一階段建議

1. **Phase 4F-1：adaptive route 接入策略**  
   - 不要一次全接。  
   - 先挑 **3～5** 個行為穩定、測試與 smoke 覆蓋完整之 **skill**。  
   - 釐清 remediation routing、target node、prerequisite mapping 與現有 deterministic 層之分界。

2. **Phase 4F-2：adaptive coverage matrix**  
   - 獨立追蹤哪些 skill／節點已支援 adaptive。  
   - **不**與 Chapter 1 deterministic `runtime_ready` 覆蓋率混為同一張表或同一分母。

3. **`future_ai_judged` runtime 主線**  
   - 優先對應：`binomial_expansion_basic`、`tree_diagram_listing`、`pascal_triangle_derivation` 及同類列舉／推導題。

4. **Binomial depth enrichment**  
   - 增加題幹模板與情境變化。  
   - 強化 **difficulty = 2／3** 之參數設計。  
   - 全程維持 **answer 為 int**，並與 `binomial_expansion_basic` 路徑分離。

## 11. 結論

B4 Chapter 1 在 Phase 4B 至 Phase 4E-16B 的迭代後，**deterministic int-answer 一般練習 runtime** 已達 **實質收尾**：**25／28** 題型為 **`runtime_ready`**，**`planned_only` 已歸零**，其餘 **3** 題明確標示為 **manual_review／excluded-like** 並具 **future path**，不擠入現行 runtime 完成度。Phase 4E-13F 的 **3** 個二項式 depth 題型為**補強接入**，**不**改寫「28 題」主統計口徑。後續主戰場應轉向 **Phase 4F adaptive route** 與 **future_ai_judged** 平行主線，而非在 deterministic 層硬補已裁定不適合的題型；本報告可作為 4F 規劃之**凍結基線文件**。
