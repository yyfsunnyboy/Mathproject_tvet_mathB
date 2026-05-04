# B4 Phase 4E-13C Runtime Freeze Summary

## 1. 本階段目的
說明本階段凍結 Phase 4E-13C 之二項式 int-answer 題型接入成果，不新增 generator、不改 route/frontend。

## 2. 本階段新增接入項目

| skill_id | problem_type_id | generator_key | wrapper | web smoke test |
|---|---|---|---|---|
| vh_數學B4_BinomialCoefficientIdentities | binomial_coefficient_sum | b4.binomial.binomial_coefficient_sum | yes | yes |
| vh_數學B4_BinomialTheorem | binomial_specific_term_coefficient | b4.binomial.binomial_specific_term_coefficient | yes | yes |
| vh_數學B4_BinomialCoefficientIdentities | binomial_equation_solve_n | b4.binomial.binomial_equation_solve_n | yes | yes |

## 3. 測試結果
- pytest：288 passed
- 已建立 2 個 wrapper：
  - skills/vh_數學B4_BinomialCoefficientIdentities.py
  - skills/vh_數學B4_BinomialTheorem.py
- 未接入 binomial_expansion_basic
- runtime 不會產出 list[int] answer
- 未修改 generator / domain / route / frontend / app.py
- 未重新引入 vh_?詨飛B4_* 亂碼 alias

## 4. Web Smoke Test 結果
記錄兩個頁面均通過：
- /practice/vh_數學B4_BinomialCoefficientIdentities
- /practice/vh_數學B4_BinomialTheorem

說明：
- 可產題
- 可判斷答對 / 答錯
- LaTeX 顯示正常
- answer 為 int，不是 list[int]
- terminal 無 500 error

## 5. 二項式題型限制聲明
本階段的二項式接入屬於「int-answer 最小可用版本」。
它可以支援：
- 係數和
- 指定項係數
- 由組合數條件求 n

但目前尚不能代表完整二項式定理教學。  
完整展開題 `binomial_expansion_basic` 仍暫緩，原因是 answer 為 `list[int]`，一般練習頁尚未定義學生輸入格式與判分 normalization。

## 6. Coverage 更新
- problem_type 總數：28
- runtime_ready：23
- planned_only：4
- excluded：1
- 已完成 wrapper 總數：12

目前已完成的 wrapper 至少包含：
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
- vh_數學B4_BinomialCoefficientIdentities
- vh_數學B4_BinomialTheorem

## 7. 尚未處理
- binomial_expansion_basic 已有 generator，但因 answer 為 list[int]，暫緩接入 wrapper。
- permutation_adjacent_block、permutation_digit_parity 等限制排列題尚未處理。
- tree_diagram_listing 尚未處理。
- pascal_triangle_derivation 仍為 excluded / manual_review。
- 完整二項式展開 free-response 尚未設計。
- 尚未接 adaptive route。
- question_router 仍為最小 hard-coded registry。

## 8. 下一步建議
1. Phase 4E-13D：binomial theorem depth expansion plan，規劃二項式題型厚度。
2. Phase 4E-14：處理限制排列題，建議：
   - permutation_adjacent_block
   - permutation_digit_parity
3. Phase 4E-15：處理 tree_diagram_listing 是否暫緩或改成文字列舉題。
4. Phase 4F：等 Chapter 1 一般練習覆蓋更完整後，再接 adaptive。
5. 不要直接接入 binomial_expansion_basic，除非先完成答案 normalization 策略。

## 9. 結論
- Phase 4E-13C 接入已成功凍結。  
- Chapter 1 runtime_ready 已提升至 23 / 28。  
- 二項式題型目前屬於 int-answer 最小可用版本。  
- `binomial_expansion_basic` 仍暫緩，尚待答案 normalization。  
- 目前仍非全 Chapter 1 完成。  
