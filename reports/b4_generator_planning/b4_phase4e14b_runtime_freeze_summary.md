# B4 Phase 4E-14B Runtime Freeze Summary

## 1. 本階段目的
本階段凍結 Phase 4E-14B 之限制排列題型 router 接入成果：更新 Chapter 1 原始 runtime coverage 狀態與文件紀錄。  
本階段不新增 generator、不改 route/frontend、不新增 wrapper、不修改程式碼。

## 2. 本階段新增接入項目

| skill_id | problem_type_id | generator_key | wrapper | web smoke test |
|---|---|---|---|---|
| vh_數學B4_PermutationOfDistinctObjects | permutation_adjacent_block | b4.permutation.permutation_adjacent_block | yes（`skills/vh_數學B4_PermutationOfDistinctObjects.py`） | yes（`/practice/vh_數學B4_PermutationOfDistinctObjects`） |
| vh_數學B4_PermutationOfDistinctObjects | permutation_digit_parity | b4.permutation.permutation_digit_parity | yes（`skills/vh_數學B4_PermutationOfDistinctObjects.py`） | yes（`/practice/vh_數學B4_PermutationOfDistinctObjects`） |

## 3. 測試結果
- pytest：348 passed
- 未新增 / 修改 wrapper
- 未修改 generator / domain / route / frontend / app.py
- 未重新引入 `vh_?詨飛B4_*` 亂碼 alias
- 未接入 `binomial_expansion_basic`
- 未實作不相鄰題型

## 4. Web Smoke Test 結果
頁面通過：
- `/practice/vh_數學B4_PermutationOfDistinctObjects`

說明：
- 可產題
- `permutation_adjacent_block` 可正常出題
- `permutation_digit_parity` 可正常出題
- 可判斷答對 / 答錯
- LaTeX 顯示正常
- terminal 無 500 error

## 5. Coverage 更新
依 `reports/b4_generator_planning/b4_ch1_runtime_coverage_matrix.csv` 逐列統計：
- problem_type 總數：28
- runtime_ready：25
- planned_only：2
- excluded：1

已完成 wrapper（以 `skills/` 內 `vh_數學B4_*.py` 實際檔案數統計）：**12**  
至少包含：
- `vh_數學B4_CombinationDefinition`
- `vh_數學B4_CombinationApplications`
- `vh_數學B4_MultiplicationPrinciple`
- `vh_數學B4_PermutationOfDistinctObjects`
- `vh_數學B4_RepeatedPermutation`
- `vh_數學B4_FactorialNotation`
- `vh_數學B4_AdditionPrinciple`
- `vh_數學B4_CombinationProperties`
- `vh_數學B4_PermutationWithRepetition`
- `vh_數學B4_Combination`
- `vh_數學B4_BinomialCoefficientIdentities`
- `vh_數學B4_BinomialTheorem`

補充：coverage matrix 的 `has_skill_wrapper=yes` 為 **25 / 28**（其餘 3 列為 `binomial_expansion_basic`、`tree_diagram_listing`、`pascal_triangle_derivation`），與「`skills/` 內 B4 wrapper 檔案數 = 12」屬不同維度統計口徑。

## 6. 尚未處理
- `binomial_expansion_basic` 已有 generator，但因 answer 為 `list[int]`，暫緩接入 wrapper。
- `tree_diagram_listing` 尚未處理。
- `pascal_triangle_derivation` 仍為 excluded / manual_review。
- 完整二項式展開 free-response 尚未設計。
- 不相鄰排列題尚未實作，未納入本階段。
- 尚未接 adaptive route。
- question_router 仍為最小 hard-coded registry。

## 7. 下一步建議
1. Phase 4E-15A：決定 `tree_diagram_listing` 是否暫緩、改為文字列舉題，或只做教學說明。
2. Phase 4E-15B：若 `tree_diagram_listing` 可文字化，實作 text-listing generator。
3. Phase 4E-16：重新確認 `binomial_expansion_basic` 是否仍暫緩，或規劃 free-response / normalization。
4. Phase 4F：等 Chapter 1 一般練習覆蓋穩定後，再接 adaptive。
5. 不要硬接 `list[int]` answer 題型。

## 8. 結論
Phase 4E-14B 已成功將 2 個限制排列題型以文件與 coverage 方式凍結為 `runtime_ready`。  
Chapter 1 `runtime_ready` 已提升到 **25 / 28**。  
原始 coverage 的 `planned_only` 已收斂為 **2**。  
目前仍非全 Chapter 1 完成（尚有 `planned_only` 與 `excluded` 項目）。
