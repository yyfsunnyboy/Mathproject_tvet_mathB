# B4 Phase 4E-13F Binomial Depth Runtime Freeze Summary

## 1. 本階段目的

本階段凍結 Phase 4E-13F 之二項式 depth int-answer 題型接入成果。  
本階段不更新原始 28 題 coverage matrix 統計，因為這 3 題屬於二項式深度補強題型，主要用來增加教學厚度，而非原始 matrix 的 problem_type 收尾項。

## 2. 本階段新增接入項目

| skill_id | problem_type_id | generator_key | wrapper | web smoke test |
|---|---|---|---|---|
| vh_數學B4_BinomialTheorem | binomial_middle_term_coefficient | b4.binomial.binomial_middle_term_coefficient | yes | yes |
| vh_數學B4_BinomialTheorem | binomial_specific_coefficient_with_negative_term | b4.binomial.binomial_specific_coefficient_with_negative_term | yes | yes |
| vh_數學B4_BinomialCoefficientIdentities | binomial_odd_even_coefficient_sum | b4.binomial.binomial_odd_even_coefficient_sum | yes | yes |

## 3. 測試結果

- pytest：322 passed
- 未新增 / 修改 wrapper
- 未接入 binomial_expansion_basic
- runtime 不會產出 list[int] answer
- 未修改 generator / domain / route / frontend / app.py
- 未重新引入 vh_?詨飛B4_* 亂碼 alias

## 4. Web Smoke Test 結果

記錄兩個頁面均通過：
- /practice/vh_數學B4_BinomialTheorem
- /practice/vh_數學B4_BinomialCoefficientIdentities

說明：
- 可產題
- 可判斷答對 / 答錯
- LaTeX 顯示正常
- answer 為 int，不是 list[int]
- terminal 無 500 error

## 5. 目前觀察到的限制

雖然本階段接入成功，但目前仍觀察到：
- 題型仍偏單調。
- 參數偏簡單。
- 二項式 depth 題型已比 Phase 4E-13C 豐富，但還不是完整二項式定理題庫。
- 仍不支援完整展開 free-response。
- 仍不接入 `binomial_expansion_basic`，因為該題型 answer 為 `list[int]`。

## 6. 與 coverage matrix 的關係

- 原始 Chapter 1 coverage matrix 仍維持 Phase 4E-13C 的統計：
  - problem_type 總數：28
  - runtime_ready：23
  - planned_only：4
  - excluded：1
- 本階段新增的 3 個 depth 題型是補強題型，暫不納入原始 28 題分母統計。
- 若未來要納入 coverage，需另開「expanded problem_type coverage matrix」或新增 depth coverage 欄位。

## 7. 尚未處理

- `binomial_expansion_basic` 尚未接入。
- 完整二項式展開 free-response 尚未設計。
- polynomial normalization / symbolic parser 尚未設計。
- 二項式題型模板仍需後續擴充。
- 二項式 difficulty=2 / 3 的參數與模板仍可再強化。
- 原始 matrix 中仍有：
  - permutation_adjacent_block
  - permutation_digit_parity
  - tree_diagram_listing
  - binomial_expansion_basic
- pascal_triangle_derivation 仍為 excluded / manual_review。
- 尚未接 adaptive route。

## 8. 下一步建議

1. Phase 4E-13G：binomial depth parameter / template enrichment
   - 增加 difficulty=2 / 3 參數變化
   - 增加題幹模板
   - 增加 a != 1、b < 0、n 較大時的出現比例
   - 保持 answer 為 int
   - 不接 `binomial_expansion_basic`
2. Phase 4E-14：處理原始 matrix 剩餘限制排列題：
   - permutation_adjacent_block
   - permutation_digit_parity
3. Phase 4E-15：處理 tree_diagram_listing 是否暫緩或轉成文字列舉題。
4. Phase 4F：等 Chapter 1 一般練習覆蓋更完整後，再接 adaptive。

## 9. 結論

- Phase 4E-13F 凍結已完成。  
- 二項式 depth 三個 int-answer 題型已安全接入。  
- 目前題型仍偏單調、參數仍偏簡單。  
- 本階段不更新原始 coverage matrix（仍為 28 / 23 / 4 / 1）。  
- 後續應以模板與參數 enrichment 為優先。  
