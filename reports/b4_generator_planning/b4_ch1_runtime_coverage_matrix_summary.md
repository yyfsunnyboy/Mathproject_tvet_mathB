# B4 Chapter 1 Runtime Coverage Matrix Summary

## 1. 目的
本矩陣用於追蹤 B4 Chapter 1 目前從 problem_type 到 generator、router、wrapper 及 web smoke test 的端到端 runtime 覆蓋率狀態。
請注意，此覆蓋率僅反映當下支援自動生成與路由接入的進度，不代表全冊或全章的最終完成度。

## 2. 統計摘要
- **problem_type 總數**: 28
- **runtime_ready 數量**: 6
- **implemented_not_web_tested 數量**: 0
- **generator_ready_no_wrapper 數量**: 0
- **planned_only 數量**: 21
- **excluded 數量**: 1
- **has_generator=yes 數量**: 6
- **in_question_router=yes 數量**: 6
- **has_skill_wrapper=yes 數量**: 14
- **web_smoke_tested=yes 數量**: 6

## 3. runtime_ready 清單
以下 problem_type 已具備 generator、對應的 skill wrapper，且成功接入 question_router，並通過網頁一般練習流程測試：
1. `combination_definition_basic` (組合定義基本計算)
2. `combination_polygon_count` (多邊形對角線與三角形 / 正多邊形對角線與三角形計數)
3. `combination_required_excluded_person` (指定人物必選或不可選)
4. `divisor_count_prime_factorization` (正因數個數計算)
5. `permutation_role_assignment` (不同職務分配)
6. `repeated_permutation_digits` (數字重複排列)

## 4. planned_only 清單
尚未實作 generator 的 problem_type（共 21 個），依 priority（若已知）及題型分類排序：
1. `binomial_expansion_basic` (二項式展開) - high
2. `combination_group_selection` (分類組合乘法) - high
3. `factorial_equation_solve_n` (階乘方程求正整數 n) - high
4. `repeated_permutation_assignment` (重複排列分派計數) - high
5. `permutation_adjacent_block` (相鄰與不相鄰限制排列) - high
6. `permutation_digit_parity` (數字排列含奇偶限制) - high
7. `binomial_coefficient_sum` (二項式係數和) - medium
8. `binomial_equation_solve_n` (已知組合數求參數) - medium
9. `binomial_specific_term_coefficient` (指定項係數) - medium
10. `combination_basic_selection` (組合基本選取) - medium
11. `combination_properties_simplification` (組合性質化簡) - medium
12. `combination_restricted_selection` (組合特定數量限制選取) - medium
13. `combination_seat_assignment` (組合與排列混合排座) - medium
14. `add_principle_mutually_exclusive_choice` (互斥分類選擇加法原理) - medium
15. `factorial_evaluation` (階乘式求值) - medium
16. `mult_digits_no_repeat` (數字排列無重複) - medium
17. `mult_principle_independent_choices` (多階段選擇乘法原理) - medium
18. `repeated_choice_basic` (重複選擇基本計數) - medium
19. `permutation_formula_evaluation` (排列記號 P(n,r) 求值) - medium
20. `permutation_full_arrangement` (相異物全取排列) - medium
21. `tree_diagram_listing` (樹狀圖列舉) - low

## 5. 缺 wrapper 或缺 router 的項目
目前沒有 `has_generator=yes` 但尚未接入 wrapper/router/web test 的項目（數量為 0）。

## 6. 暫緩項目
以下 problem_type 因標示 `exclude_from_generator=yes` 而暫緩自動化：
- `pascal_triangle_derivation` (巴斯卡三角形推導) - manual_review

## 7. 下一步建議
基於保守擴充的原則，後續行動建議如下：
1. 優先補齊 high priority 且 domain function 已存在的 generator（例如 `binomial_expansion_basic`、`factorial_equation_solve_n` 等）。
2. 為確保系統與整合穩定性，每批最多只實作並接入 3 個 generator。
3. 每批 generator 完成後，必須嚴格產出對應的 sample QA 報告進行審查。
4. 審查通過後再接入 router 與對應 wrapper，並立即執行 web smoke test。
5. 不要直接跳 adaptive，必須確保單一 problem_type 在一般練習流程穩定運行後，再做 adaptive route 的考量。
