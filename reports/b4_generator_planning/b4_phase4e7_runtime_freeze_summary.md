# B4 Phase 4E-7 Runtime Freeze Summary

## 1. 本階段目的
本階段凍結 Phase 4E-7 將指定基礎 generator 經 **skill wrapper** 與 **`question_router` 最小 hard-coded registry** 接入後之 **runtime** 成果紀錄；**不新增 generator**、**不修改 route／前端／測試程式**，僅更新本報告與 coverage 矩陣文件。

## 2. 本階段新增接入項目

| skill_id | problem_type_id | generator_key | wrapper | web smoke test |
|---|---|---|---|---|
| vh_數學B4_AdditionPrinciple | add_principle_mutually_exclusive_choice | b4.counting.add_principle_mutually_exclusive_choice | yes | yes |
| vh_數學B4_CombinationProperties | combination_properties_simplification | b4.combination.combination_properties_simplification | yes | yes |
| vh_數學B4_PermutationWithRepetition | repeated_choice_basic | b4.counting.repeated_choice_basic | yes | yes |

## 3. Web Smoke Test 結果
以下三個一般練習頁面均通過 smoke：
- `/practice/vh_數學B4_AdditionPrinciple`
- `/practice/vh_數學B4_CombinationProperties`
- `/practice/vh_數學B4_PermutationWithRepetition`

驗證重點：
- 可產題
- 可判斷答對／答錯
- LaTeX 顯示正常
- 執行期 terminal 無 500 error

## 4. Coverage 更新
- **依本次更新後之 CSV 逐列統計**：**runtime_ready 9 / 28**、**planned_only 18**、**excluded 1**。
- 任務敘述中曾出現之口徑 **runtime_ready 11 / 28**、**planned_only 16**：與「**僅升級指定三題**」後之矩陣相差 **2**；`question_router.py` 已登錄 **`combination_group_selection`**、**`factorial_equation_solve_n`** 等項，惟**本次 CSV 未變更**該兩列之狀態，故逐列計數尚未達 11 / 16。
- **已完成 wrapper 總數（skill 層級）**：**9 個**

已完成 wrapper 清單：
- vh_數學B4_CombinationDefinition
- vh_數學B4_CombinationApplications
- vh_數學B4_MultiplicationPrinciple
- vh_數學B4_PermutationOfDistinctObjects
- vh_數學B4_RepeatedPermutation
- vh_數學B4_FactorialNotation
- vh_數學B4_AdditionPrinciple
- vh_數學B4_CombinationProperties
- vh_數學B4_PermutationWithRepetition

## 5. 尚未處理
- `binomial_expansion_basic` 已有 generator，但因 **answer 為 `list[int]`**，暫緩接入 wrapper（需先決定輸入與判分格式）。
- `vh_數學B4_BinomialTheorem` 尚未建立 wrapper。
- `vh_數學B4_TreeDiagramCounting` 尚未處理。
- `vh_數學B4_PascalTriangle` 尚未處理。
- 尚未接 adaptive route。
- `question_router` 仍為最小 hard-coded registry；與矩陣逐列狀態可能尚未完全一致（例如已登錄但未標為 `runtime_ready` 之列）。

## 6. 下一步建議
1. **Phase 4E-8**：下一批可處理 3 個 generator（接入與 smoke 仍採小批量）：`combination_basic_selection`、`permutation_formula_evaluation`、`factorial_evaluation`。
2. **Phase 4E-9**：決定 `binomial_expansion_basic` 的答案格式與判分契約。
3. **Phase 4F**：待 Chapter 1 一般練習覆蓋更完整後，再接 adaptive。
4. **不要**一次大量建立 wrapper。

## 7. 結論
Phase 4E-7 已成功將 **3** 個指定 `problem_type` 標示為端到端 **runtime_ready**，並完成對應三個 practice 路徑之 web smoke 紀錄。Chapter 1 之最小 runtime 覆蓋相較升級前（6 題）已提升至 **9 / 28**，但仍**非**全章完成。`question_router` 與矩陣之逐列狀態仍有待下一小步對齊，以避免統計口徑落差。
