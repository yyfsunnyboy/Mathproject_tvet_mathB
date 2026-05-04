# B4 Phase 4E-9 Runtime Freeze Summary

## 1. 本階段目的
本階段凍結 Phase 4E-9 之 router / wrapper 接入成果，不新增 generator、不改 route/frontend。

## 2. 本階段新增接入項目

| skill_id | problem_type_id | generator_key | wrapper | web smoke test |
|---|---|---|---|---|
| vh_數學B4_Combination | combination_basic_selection | b4.combination.combination_basic_selection | yes | yes |
| vh_數學B4_PermutationOfDistinctObjects | permutation_formula_evaluation | b4.permutation.permutation_formula_evaluation | yes | yes |
| vh_數學B4_FactorialNotation | factorial_evaluation | b4.counting.factorial_evaluation | yes | yes |

## 3. 測試結果

- pytest：140 passed
- 修正舊 generator LaTeX 格式債：
  - permutation_role_assignment explanation 已改為 $P^{n}_{r}$ 格式
- 未修改 route / frontend / app.py / domain / generator answer / choices / parameter_tuple

## 4. Web Smoke Test 結果

三個頁面均通過：
- /practice/vh_數學B4_Combination
- /practice/vh_數學B4_PermutationOfDistinctObjects
- /practice/vh_數學B4_FactorialNotation

說明：
- 可產題
- 可判斷答對 / 答錯
- LaTeX 顯示正常
- terminal 無 500 error

## 5. Coverage 更新

- problem_type 總數：28
- runtime_ready：14
- planned_only：13
- excluded：1

已完成 wrapper 總數包含：
- vh_數學B4_CombinationDefinition
- vh_數學B4_CombinationApplications
- vh_數學B4_MultiplicationPrinciple
- vh_數學B4_PermutationOfDistinctObjects
- vh_數學B4_RepeatedPermutation
- vh_數學B4_FactorialNotation
- vh_數學B4_AdditionPrinciple
- vh_數學B4_CombinationProperties
- vh_數學B4_PermutationWithRepetition
- vh_數學B4_Combination

## 6. 尚未處理

- binomial_expansion_basic 已有 generator，但因 answer 為 list[int]，暫緩接入 wrapper。
- vh_數學B4_BinomialTheorem 尚未建立 wrapper。
- vh_數學B4_TreeDiagramCounting 尚未處理。
- vh_數學B4_PascalTriangle 尚未處理。
- permutation_adjacent_block、permutation_digit_parity 等限制排列題尚未處理。
- 尚未接 adaptive route。
- question_router 仍為最小 hard-coded registry。

## 7. 下一步建議

1. Phase 4E-10：處理下一批最多 3 個 generator，建議：
   - mult_principle_independent_choices
   - mult_digits_no_repeat
   - repeated_permutation_assignment
2. Phase 4E-11：決定 binomial_expansion_basic 的答案格式。
3. Phase 4F：等 Chapter 1 一般練習覆蓋更完整後，再接 adaptive。
4. 不要一次大量建立 wrapper。

## 8. 結論

- Phase 4E-9 成功將 3 個基礎題型接入系統。
- Chapter 1 runtime_ready 數量已提升到 14 / 28。
- 目前仍非全 Chapter 1 完成，將持續採批量穩定推進。
