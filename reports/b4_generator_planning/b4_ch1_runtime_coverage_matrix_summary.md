# B4 Chapter 1 Runtime Coverage Matrix Summary

## 1. 目的
本矩陣用於追蹤 B4 Chapter 1 目前從 problem_type 到 generator、router、wrapper 及 web smoke test 的端到端 runtime 覆蓋率狀態。  
此覆蓋率僅反映當下支援自動生成與路由接入的進度，不代表全章最終完成度。

## 2. 統計摘要
- **problem_type 總數**: 28
- **runtime_ready 數量**: 25
- **implemented_not_web_tested 數量**: 0
- **generator_ready_no_wrapper 數量**: 0
- **planned_only 數量**: 2
- **excluded 數量**: 1
- **has_generator=yes 數量**: 25
- **in_question_router=yes 數量**: 25
- **has_skill_wrapper=yes 數量**: 25
- **web_smoke_tested=yes 數量**: 25

### Reconciliation notes（Phase 4E-7B, 4E-9, 4E-11, 4E-12C, 4E-13C, 4E-14B）
- **Phase 4E-7** 初次 freeze 僅將當批 **3** 個 `problem_type` 升級為 `runtime_ready`，矩陣逐列一度為 **runtime_ready 9**、**planned_only 18**（excluded 1）。
- 本次 **Phase 4E-7B** 為 **coverage reconciliation**：補回 **Phase 4E-4A** 已接入 `question_router`、具 **skill wrapper**，且具專案 web smoke 紀錄之 **2** 題（`combination_group_selection`、`factorial_equation_solve_n`），**不修改程式**。
- **Phase 4E-9** 新增 3 個 problem_type 接入 router / wrapper：
  - pytest 140 passed
  - web smoke test 三頁通過：
    `/practice/vh_數學B4_Combination`
    `/practice/vh_數學B4_PermutationOfDistinctObjects`
    `/practice/vh_數學B4_FactorialNotation`
  - 因此 coverage 統計更新為 14 / 13 / 1
- **Phase 4E-11** 新增 3 個 problem_type 接入 router：
  - pytest 183 passed
  - targeted cleanup pytest 15 passed
  - web smoke test 兩頁通過：
    `/practice/vh_數學B4_MultiplicationPrinciple`
    `/practice/vh_數學B4_PermutationWithRepetition`
  - 因此 coverage 統計更新為 17 / 10 / 1
- **Phase 4E-12C** 新增 3 個 problem_type 接入 router：
  - pytest 248 passed
  - web smoke test 兩頁通過：
    `/practice/vh_數學B4_PermutationOfDistinctObjects`
    `/practice/vh_數學B4_Combination`
  - 未重新引入亂碼 alias
  - 因此 coverage 統計更新為 20 / 7 / 1
- **Phase 4E-13C** 新增 3 個 binomial int-answer problem_type 接入 router / wrapper：
  - `binomial_coefficient_sum`
  - `binomial_specific_term_coefficient`
  - `binomial_equation_solve_n`
  - pytest 288 passed
  - web smoke test 兩頁通過：
    `/practice/vh_數學B4_BinomialCoefficientIdentities`
    `/practice/vh_數學B4_BinomialTheorem`
  - runtime path 不會產出 `list[int]` answer
  - 未接入 `binomial_expansion_basic`
  - 二項式題型目前為 int-answer 最小可用接入，不代表完整二項式展開能力
  - 因此 coverage 統計更新為 23 / 4 / 1
- **Phase 4E-14B** 新增 2 個限制排列 problem_type 接入 router：
  - pytest 348 passed
  - web smoke test 一頁通過：
    `/practice/vh_數學B4_PermutationOfDistinctObjects`
  - 未重新引入亂碼 alias
  - 因此 coverage 統計更新為 25 / 2 / 1
- **Web smoke 文件依據**：`combination_group_selection` 所屬 skill 之 `/practice/vh_數學B4_CombinationApplications` 通過，見 `b4_phase4d_runtime_wrapper_router_summary.md` §7；`factorial_equation_solve_n` 所屬 `/practice/vh_數學B4_FactorialNotation` 依任務書定之 Phase 4E-4A／後續紀錄。

## 3. runtime_ready 清單
以下 problem_type 已具備 generator、對應的 skill wrapper，且成功接入 question_router，並通過網頁一般練習流程測試：
1. `combination_definition_basic` (組合定義基本計算)
2. `combination_polygon_count` (多邊形對角線與三角形 / 正多邊形對角線與三角形計數)
3. `combination_group_selection` (分類組合乘法) — Phase 4E-7B reconciliation（Phase 4E-4A 已接入）
4. `combination_properties_simplification` (組合性質化簡) — Phase 4E-7
5. `combination_required_excluded_person` (指定人物必選或不可選)
6. `add_principle_mutually_exclusive_choice` (互斥分類選擇加法原理) — Phase 4E-7
7. `divisor_count_prime_factorization` (正因數個數計算)
8. `factorial_equation_solve_n` (階乘方程求正整數 n) — Phase 4E-7B reconciliation（Phase 4E-4A 已接入）
9. `repeated_permutation_digits` (數字重複排列)
10. `repeated_choice_basic` (重複選擇基本計數) — Phase 4E-7
11. `permutation_role_assignment` (不同職務分配)
12. `combination_basic_selection` (組合基本選取) — Phase 4E-9
13. `permutation_formula_evaluation` (排列記號 P(n,r) 求值) — Phase 4E-9
14. `factorial_evaluation` (階乘式求值) — Phase 4E-9
15. `mult_principle_independent_choices` (多階段選擇乘法原理) — Phase 4E-11
16. `mult_digits_no_repeat` (數字排列無重複) — Phase 4E-11
17. `repeated_permutation_assignment` (重複排列分派計數) — Phase 4E-11
18. `permutation_full_arrangement` (相異物全取排列) — Phase 4E-12C
19. `permutation_adjacent_block` (相鄰與不相鄰限制排列) — Phase 4E-14B
20. `permutation_digit_parity` (數字排列含奇偶限制) — Phase 4E-14B
21. `combination_restricted_selection` (組合特定數量限制選取) — Phase 4E-12C
22. `combination_seat_assignment` (組合與排列混合排座) — Phase 4E-12C
23. `binomial_coefficient_sum` (二項式係數和) — Phase 4E-13C
24. `binomial_specific_term_coefficient` (指定項係數) — Phase 4E-13C
25. `binomial_equation_solve_n` (已知組合數求參數) — Phase 4E-13C

## 4. planned_only 清單
尚未達成端到端 `runtime_ready` 的 problem_type（共 2 個）：
1. `binomial_expansion_basic` (二項式展開)
2. `tree_diagram_listing` (樹狀圖列舉)

## 5. 暫緩項目
以下 problem_type 因標示 `excluded` 而暫緩自動化：
- `pascal_triangle_derivation` (巴斯卡三角形推導) - manual_review

## 6. 下一步建議
- 持續維持 Phase 4E-13C 的 3 個 binomial int-answer 題型於 runtime_ready。
- `binomial_expansion_basic` 暫不接入 wrapper：其 answer 仍為 `list[int]`，需先完成輸入格式與 normalization 策略。
- 評估 `tree_diagram_listing` 是否改為文字列舉題、只做教學說明，或維持暫緩。
- 維持每批小量接入、sample QA 審查、router/wrapper/web smoke 全鏈路驗證後再更新 coverage matrix。
