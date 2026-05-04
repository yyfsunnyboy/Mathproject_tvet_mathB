# B4 Phase 4E-11 Runtime Freeze Summary

## 1. 本階段目的
本階段凍結 Phase 4E-11 之 router 接入成果，不新增 generator、不改 route/frontend、不新增 wrapper。

## 2. 本階段新增接入項目

| skill_id | problem_type_id | generator_key | wrapper | web smoke test |
|---|---|---|---|---|
| vh_數學B4_MultiplicationPrinciple | mult_principle_independent_choices | b4.counting.mult_principle_independent_choices | yes | yes |
| vh_數學B4_MultiplicationPrinciple | mult_digits_no_repeat | b4.counting.mult_digits_no_repeat | yes | yes |
| vh_數學B4_PermutationWithRepetition | repeated_permutation_assignment | b4.counting.repeated_permutation_assignment | yes | yes |

## 3. 測試結果

- pytest：183 passed
- targeted cleanup pytest：15 passed
- 修正 router registry 技術債：
  - vh_數學B4_MultiplicationPrinciple 已改為 canonical key
  - 不再靠 vh_?詨飛B4_MultiplicationPrinciple alias
- 未修改 route / frontend / app.py / domain / generator / wrapper

## 4. Web Smoke Test 結果

兩個頁面均通過：
- /practice/vh_數學B4_MultiplicationPrinciple
- /practice/vh_數學B4_PermutationWithRepetition

說明：
- 可產題
- 可判斷答對 / 答錯
- LaTeX 顯示正常
- terminal 無 500 error

## 5. Coverage 更新

- problem_type 總數：28
- runtime_ready：17
- planned_only：10
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
- combination_restricted_selection、combination_seat_assignment 尚未處理。
- permutation_full_arrangement 尚未處理。
- binomial_coefficient_sum、binomial_equation_solve_n、binomial_specific_term_coefficient 尚未處理。
- 尚未接 adaptive route。
- question_router 仍為最小 hard-coded registry。
- router registry 中其他 skill 仍可能保留 vh_?詨飛B4_* 亂碼 alias，後續需另開 phase 清理。

## 7. 下一步建議

1. Phase 4E-12A：router registry canonical key cleanup，清理其餘亂碼 alias。
2. Phase 4E-12B：處理下一批最多 3 個 generator，建議：
   - permutation_full_arrangement
   - combination_restricted_selection
   - combination_seat_assignment
3. Phase 4E-13：決定 binomial_expansion_basic 的答案格式。
4. Phase 4F：等 Chapter 1 一般練習覆蓋更完整後，再接 adaptive。
5. 不要一次大量建立 wrapper。

## 8. 結論

- Phase 4E-11 成功將 3 個計數題型順利接入 router 並完成驗證。
- Chapter 1 runtime_ready 數量已提升到 17 / 28。
- 目前仍非全 Chapter 1 完成，將持續採批量穩定推進，並於後續清理 router 亂碼 alias 技術債。
