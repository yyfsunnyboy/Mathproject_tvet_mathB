# B4 Phase 4E-12C Runtime Freeze Summary

## 1. 本階段目的
說明本階段凍結 Phase 4E-12C 之 router 接入成果，不新增 generator、不改 route/frontend、不新增 wrapper。

## 2. 本階段新增接入項目

| skill_id | problem_type_id | generator_key | wrapper | web smoke test |
|---|---|---|---|---|
| vh_數學B4_PermutationOfDistinctObjects | permutation_full_arrangement | b4.permutation.permutation_full_arrangement | yes | yes |
| vh_數學B4_Combination | combination_restricted_selection | b4.combination.combination_restricted_selection | yes | yes |
| vh_數學B4_Combination | combination_seat_assignment | b4.combination.combination_seat_assignment | yes | yes |

## 3. 測試結果
- pytest：248 passed
- 未新增 wrapper
- 未修改 route / frontend / app.py / domain / generator
- 未接入 binomial_expansion_basic
- 未重新引入 vh_?詨飛B4_* 亂碼 alias

## 4. Web Smoke Test 結果
記錄兩個頁面均通過：
- /practice/vh_數學B4_PermutationOfDistinctObjects
- /practice/vh_數學B4_Combination

說明：
- 可產題
- 可判斷答對 / 答錯
- LaTeX 顯示正常
- terminal 無 500 error

## 5. Coverage 更新
- problem_type 總數：28
- runtime_ready：20
- planned_only：7
- excluded：1

目前已完成的 wrapper 包含：
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
- binomial_coefficient_sum、binomial_equation_solve_n、binomial_specific_term_coefficient 尚未處理。
- 尚未接 adaptive route。
- question_router 仍為最小 hard-coded registry。

## 7. 下一步建議
1. Phase 4E-13A：決定 binomial_expansion_basic 的答案格式。
2. Phase 4E-13B：若決定接入，建立 BinomialTheorem wrapper 與 router entry。
3. Phase 4E-14：處理限制排列題，建議：
   - permutation_adjacent_block
   - permutation_digit_parity
4. Phase 4E-15：處理二項式係數題，建議：
   - binomial_coefficient_sum
   - binomial_equation_solve_n
   - binomial_specific_term_coefficient
5. TreeDiagramCounting 與 PascalTriangle 繼續暫緩。
6. Phase 4F：等 Chapter 1 一般練習覆蓋更完整後，再接 adaptive。

## 8. 結論
Phase 4E-12C 已成功執行完畢並凍結狀態。Chapter 1 runtime_ready 數量順利提升到 20 / 28，進一步擴充了一般練習的覆蓋度。目前仍非全 Chapter 1 完成，尚有限制排列與二項式等進階題目待後續 Phase 補齊。
