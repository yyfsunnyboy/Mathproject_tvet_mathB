# B4 Phase 3 第一章 Problem Type 與 Generator Registry 成果凍結報告

## 1. 本階段目的

- 本階段只凍結 Phase 3 成果。
- 本階段不建立 generator。
- 本階段不建立 domain function。
- 本階段不修改前端或 route。
- Phase 3 的用途是將 template_candidate 正式整理為 canonical problem_type，並規劃 generator registry。

## 2. 處理範圍

- 處理章節：1 排列組合
- 處理內容：加法原理、乘法原理、階乘、排列、重複排列、組合、二項式定理
- 讀取檔案：
  - `reports/b4_generator_planning/b4_phase3_problem_type_map_counting_binomial.csv`
  - `reports/b4_generator_planning/b4_phase3_generator_registry_plan_counting_binomial.csv`
  - `reports/b4_generator_planning/b4_phase2a_counting_binomial_summary.md`
- 輸出檔案：`reports/b4_generator_planning/b4_phase3_counting_binomial_summary.md`

## 3. Phase 3 成果統計

- problem_type 總數：28
- generator_registry_plan 總數：28
- math_family 分布：counting: 9, combination: 8, binomial: 5, permutation: 5, tree_enumeration: 1
- priority 分布：medium: 14, high: 12, low: 2
- exclude_from_generator = yes 的數量：1
- review_required = yes 的數量：14
- requires_manual_review_before_runtime = yes 的數量：16
- supports_multiple_choice = yes 的數量：26
- supports_free_response = yes 的數量：28
- requires_ai_generation 分布：optional: 28
- requires_post_healer 分布：optional: 14, no: 14

## 4. Problem Type 清單摘要

### math_family: binomial

| problem_type_id | problem_type_name | priority | exclude_from_generator | answer_verification_method | domain_function_requirements | source_template_candidate_ids |
|---|---|---|---|---|---|---|
| binomial_coefficient_sum | 二項式係數和 | medium | no | binomial_coefficient | binomial_coefficient_sum | tc_binomial_coeff_sum_01 |
| binomial_expansion_basic | 二項式展開 | high | no | binomial_coefficient | binomial_expansion_coeffici... | tc_binomial_expand_basic_01 |
| binomial_equation_solve_n | 已知組合數求參數 | medium | no | combination | combination_equation_solve_n | tc_binomial_solve_n_03 |
| binomial_specific_term_coefficient | 指定項係數 | medium | no | binomial_term_coefficient | binomial_term_coefficient | tc_binomial_specific_term_02 |
| pascal_triangle_derivation | 巴斯卡三角形推導 | low | yes | manual_or_visual_check | pascal_triangle_row | tc_pascal_tri_derivation_01 |

### math_family: combination

| problem_type_id | problem_type_name | priority | exclude_from_generator | answer_verification_method | domain_function_requirements | source_template_candidate_ids |
|---|---|---|---|---|---|---|
| combination_basic_selection | 組合基本選取 | medium | no | combination | combination | tc_comb_basic_selection_01 |
| combination_definition_basic | 組合定義基本計算 | high | no | combination | combination | tc_comb_definition_01 |
| combination_polygon_count | 多邊形對角線與三角形 / 正多邊形對角線與三角形計數 | high | no | combination | polygon_diagonal_count,poly... | tc_comb_geometry_02,tc_comb_polygon_diagonal_triangle_02 |
| combination_group_selection | 分類組合乘法 | high | no | combination | combination | tc_comb_group_selection_03 |
| combination_properties_simplification | 組合性質化簡 | medium | no | combination | combination,pascal_identity | tc_comb_properties_01 |
| combination_required_excluded_person | 指定人物必選或不可選 | high | no | combination | combination | tc_comb_required_or_excluded_person_01 |
| combination_restricted_selection | 組合特定數量限制選取 | medium | no | combination | combination | tc_comb_restricted_selection_02 |
| combination_seat_assignment | 組合與排列混合排座 | medium | no | multiplication_principle | combination,permutation,mul... | tc_comb_seat_assignment_03 |

### math_family: counting

| problem_type_id | problem_type_name | priority | exclude_from_generator | answer_verification_method | domain_function_requirements | source_template_candidate_ids |
|---|---|---|---|---|---|---|
| add_principle_mutually_exclusive_choice | 互斥分類選擇加法原理 | medium | no | addition_principle | addition_principle_count | tc_add_principle_mutually_exclusive_choice_01 |
| divisor_count_prime_factorization | 正因數個數計算 | high | no | multiplication_principle | divisor_count_from_prime_fa... | tc_divisor_count_prime_factorization_02 |
| factorial_evaluation | 階乘式求值 | medium | no | factorial | factorial | tc_factorial_eval_01 |
| factorial_equation_solve_n | 階乘方程求正整數 n | high | no | factorial | factorial_ratio_solve_n | tc_factorial_solve_n_02 |
| mult_digits_no_repeat | 數字排列無重複 | medium | no | multiplication_principle | digit_arrangement_count | tc_mult_digits_no_repeat_03 |
| mult_principle_independent_choices | 多階段選擇乘法原理 | medium | no | multiplication_principle | multiplication_principle_count | tc_mult_principle_independent_choices_01 |
| repeated_permutation_assignment | 重複排列分派計數 | high | no | repeated_permutation | repeated_assignment_count | tc_rep_perm_assign_02 |
| repeated_permutation_digits | 數字重複排列 | high | no | repeated_permutation | repeated_digit_arrangement_... | tc_rep_perm_digits_01 |
| repeated_choice_basic | 重複選擇基本計數 | medium | no | repeated_permutation | repeated_choice_count | tc_repeated_choice_basic_01 |

### math_family: permutation

| problem_type_id | problem_type_name | priority | exclude_from_generator | answer_verification_method | domain_function_requirements | source_template_candidate_ids |
|---|---|---|---|---|---|---|
| permutation_adjacent_block | 相鄰與不相鄰限制排列 | high | no | permutation | adjacent_arrangement_count,... | tc_perm_adjacent_block_05 |
| permutation_digit_parity | 數字排列含奇偶限制 | high | no | permutation | digit_arrangement_count | tc_perm_digit_parity_04 |
| permutation_formula_evaluation | 排列記號 P(n,r) 求值 | medium | no | permutation | permutation | tc_perm_formula_eval_02 |
| permutation_full_arrangement | 相異物全取排列 | medium | no | permutation | factorial | tc_perm_full_arrangement_01 |
| permutation_role_assignment | 不同職務分配 | high | no | permutation | permutation | tc_perm_role_assignment_03 |

### math_family: tree_enumeration

| problem_type_id | problem_type_name | priority | exclude_from_generator | answer_verification_method | domain_function_requirements | source_template_candidate_ids |
|---|---|---|---|---|---|---|
| tree_diagram_listing | 樹狀圖列舉 | low | no | enumeration_count | enumeration_count | tc_tree_diagram_listing_01 |


## 5. Generator Registry 清單摘要

### math_family: binomial

| generator_key | problem_type_id | recommended_module_path | required_domain_functions | required_validators | priority | requires_manual_review_before_runtime |
|---|---|---|---|---|---|---|
| b4.binomial.binomial_coefficient_sum | binomial_coefficient_sum | core/vocational_math_b4/generators/binomial.py | core/vocational_math_b4/domain/binomial_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |
| b4.binomial.binomial_expansion_basic | binomial_expansion_basic | core/vocational_math_b4/generators/binomial.py | core/vocational_math_b4/domain/binomial_domain_functions.py | core/vocational_math_b4/domain/b4_val... | high | no |
| b4.binomial.binomial_equation_solve_n | binomial_equation_solve_n | core/vocational_math_b4/generators/binomial.py | core/vocational_math_b4/domain/binomial_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |
| b4.binomial.binomial_specific_term_coefficient | binomial_specific_term_coefficient | core/vocational_math_b4/generators/binomial.py | core/vocational_math_b4/domain/binomial_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |
| b4.binomial.pascal_triangle_derivation | pascal_triangle_derivation | core/vocational_math_b4/generators/binomial.py | core/vocational_math_b4/domain/binomial_domain_functions.py | core/vocational_math_b4/domain/b4_val... | low | yes |

### math_family: combination

| generator_key | problem_type_id | recommended_module_path | required_domain_functions | required_validators | priority | requires_manual_review_before_runtime |
|---|---|---|---|---|---|---|
| b4.combination.combination_basic_selection | combination_basic_selection | core/vocational_math_b4/generators/combination.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |
| b4.combination.combination_definition_basic | combination_definition_basic | core/vocational_math_b4/generators/combination.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | high | no |
| b4.combination.combination_polygon_count | combination_polygon_count | core/vocational_math_b4/generators/combination.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | high | no |
| b4.combination.combination_group_selection | combination_group_selection | core/vocational_math_b4/generators/combination.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | high | no |
| b4.combination.combination_properties_simplification | combination_properties_simplification | core/vocational_math_b4/generators/combination.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |
| b4.combination.combination_required_excluded_person | combination_required_excluded_person | core/vocational_math_b4/generators/combination.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | high | no |
| b4.combination.combination_restricted_selection | combination_restricted_selection | core/vocational_math_b4/generators/combination.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |
| b4.combination.combination_seat_assignment | combination_seat_assignment | core/vocational_math_b4/generators/combination.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |

### math_family: counting

| generator_key | problem_type_id | recommended_module_path | required_domain_functions | required_validators | priority | requires_manual_review_before_runtime |
|---|---|---|---|---|---|---|
| b4.counting.add_principle_mutually_exclusive_choice | add_principle_mutually_exclusive_choice | core/vocational_math_b4/generators/counting.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |
| b4.counting.divisor_count_prime_factorization | divisor_count_prime_factorization | core/vocational_math_b4/generators/counting.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | high | no |
| b4.counting.factorial_evaluation | factorial_evaluation | core/vocational_math_b4/generators/counting.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |
| b4.counting.factorial_equation_solve_n | factorial_equation_solve_n | core/vocational_math_b4/generators/counting.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | high | no |
| b4.counting.mult_digits_no_repeat | mult_digits_no_repeat | core/vocational_math_b4/generators/counting.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |
| b4.counting.mult_principle_independent_choices | mult_principle_independent_choices | core/vocational_math_b4/generators/counting.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |
| b4.counting.repeated_permutation_assignment | repeated_permutation_assignment | core/vocational_math_b4/generators/counting.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | high | no |
| b4.counting.repeated_permutation_digits | repeated_permutation_digits | core/vocational_math_b4/generators/counting.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | high | no |
| b4.counting.repeated_choice_basic | repeated_choice_basic | core/vocational_math_b4/generators/counting.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |

### math_family: permutation

| generator_key | problem_type_id | recommended_module_path | required_domain_functions | required_validators | priority | requires_manual_review_before_runtime |
|---|---|---|---|---|---|---|
| b4.permutation.permutation_adjacent_block | permutation_adjacent_block | core/vocational_math_b4/generators/permutation.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | high | no |
| b4.permutation.permutation_digit_parity | permutation_digit_parity | core/vocational_math_b4/generators/permutation.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | high | no |
| b4.permutation.permutation_formula_evaluation | permutation_formula_evaluation | core/vocational_math_b4/generators/permutation.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |
| b4.permutation.permutation_full_arrangement | permutation_full_arrangement | core/vocational_math_b4/generators/permutation.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | medium | yes |
| b4.permutation.permutation_role_assignment | permutation_role_assignment | core/vocational_math_b4/generators/permutation.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | high | no |

### math_family: tree_enumeration

| generator_key | problem_type_id | recommended_module_path | required_domain_functions | required_validators | priority | requires_manual_review_before_runtime |
|---|---|---|---|---|---|---|
| b4.tree_enumeration.tree_diagram_listing | tree_diagram_listing | core/vocational_math_b4/generators/tree_enumeration.py | core/vocational_math_b4/domain/counting_domain_functions.py | core/vocational_math_b4/domain/b4_val... | low | yes |


## 6. High Priority 優先實作候選

| generator_key | problem_type_id | generator_name | recommended_module_path | required_domain_functions | difficulty_controls |
|---|---|---|---|---|---|
| b4.binomial.binomial_expansion_basic | binomial_expansion_basic | 二項式展開 | core/vocational_math_b4/generators/binomial.py | core/vocational_math_b4/domain/binomial_domain_functions.py | 係數 a, b, 次方 n |
| b4.combination.combination_definition_basic | combination_definition_basic | 組合定義基本計算 | core/vocational_math_b4/generators/combination.py | core/vocational_math_b4/domain/counting_domain_functions.py | n, r |
| b4.combination.combination_polygon_count | combination_polygon_count | 多邊形對角線與三角形 / 正多邊形對角線與三角形計數 | core/vocational_math_b4/generators/combination.py | core/vocational_math_b4/domain/counting_domain_functions.py | 多邊形邊數 n；正多邊形邊數 n |
| b4.combination.combination_group_selection | combination_group_selection | 分類組合乘法 | core/vocational_math_b4/generators/combination.py | core/vocational_math_b4/domain/counting_domain_functions.py | 各類別總數及選取數 |
| b4.combination.combination_required_excluded_person | combination_required_excluded_person | 指定人物必選或不可選 | core/vocational_math_b4/generators/combination.py | core/vocational_math_b4/domain/counting_domain_functions.py | 總人數, 選取數 |
| b4.counting.divisor_count_prime_factorization | divisor_count_prime_factorization | 正因數個數計算 | core/vocational_math_b4/generators/counting.py | core/vocational_math_b4/domain/counting_domain_functions.py | 給定的大數字 |
| b4.counting.factorial_equation_solve_n | factorial_equation_solve_n | 階乘方程求正整數 n | core/vocational_math_b4/generators/counting.py | core/vocational_math_b4/domain/counting_domain_functions.py | k值與常數C |
| b4.permutation.permutation_adjacent_block | permutation_adjacent_block | 相鄰與不相鄰限制排列 | core/vocational_math_b4/generators/permutation.py | core/vocational_math_b4/domain/counting_domain_functions.py | 各類別物件數量 |
| b4.permutation.permutation_digit_parity | permutation_digit_parity | 數字排列含奇偶限制 | core/vocational_math_b4/generators/permutation.py | core/vocational_math_b4/domain/counting_domain_functions.py | 數字集合, 排列位數 |
| b4.permutation.permutation_role_assignment | permutation_role_assignment | 不同職務分配 | core/vocational_math_b4/generators/permutation.py | core/vocational_math_b4/domain/counting_domain_functions.py | 總人數, 職務數 |
| b4.counting.repeated_permutation_assignment | repeated_permutation_assignment | 重複排列分派計數 | core/vocational_math_b4/generators/counting.py | core/vocational_math_b4/domain/counting_domain_functions.py | 物品數, 接收者數 |
| b4.counting.repeated_permutation_digits | repeated_permutation_digits | 數字重複排列 | core/vocational_math_b4/generators/counting.py | core/vocational_math_b4/domain/counting_domain_functions.py | 數字集合, 取出位數 |

## 7. 需人工審查或暫緩候選

| problem_type_id | generator_key | 原因 | notes |
|---|---|---|---|
| add_principle_mutually_exclusive_choice | b4.counting.add_principle_mutually_exclusive_choice | requires_manual_review_before_runtime = yes |  |
| binomial_coefficient_sum | b4.binomial.binomial_coefficient_sum | requires_manual_review_before_runtime = yes |  |
| binomial_equation_solve_n | b4.binomial.binomial_equation_solve_n | requires_manual_review_before_runtime = yes |  |
| binomial_specific_term_coefficient | b4.binomial.binomial_specific_term_coefficient | requires_manual_review_before_runtime = yes |  |
| combination_basic_selection | b4.combination.combination_basic_selection | requires_manual_review_before_runtime = yes |  |
| combination_properties_simplification | b4.combination.combination_properties_simplification | requires_manual_review_before_runtime = yes |  |
| combination_restricted_selection | b4.combination.combination_restricted_selection | requires_manual_review_before_runtime = yes |  |
| combination_seat_assignment | b4.combination.combination_seat_assignment | requires_manual_review_before_runtime = yes |  |
| factorial_evaluation | b4.counting.factorial_evaluation | requires_manual_review_before_runtime = yes |  |
| mult_digits_no_repeat | b4.counting.mult_digits_no_repeat | requires_manual_review_before_runtime = yes |  |
| mult_principle_independent_choices | b4.counting.mult_principle_independent_choices | requires_manual_review_before_runtime = yes |  |
| pascal_triangle_derivation | b4.binomial.pascal_triangle_derivation | exclude_from_generator = yes, requires_manual_review_before_runtime = yes, priority = low, answer_verification_method = manual_or_visual_check |  |
| permutation_formula_evaluation | b4.permutation.permutation_formula_evaluation | requires_manual_review_before_runtime = yes |  |
| permutation_full_arrangement | b4.permutation.permutation_full_arrangement | requires_manual_review_before_runtime = yes |  |
| repeated_choice_basic | b4.counting.repeated_choice_basic | requires_manual_review_before_runtime = yes |  |
| tree_diagram_listing | b4.tree_enumeration.tree_diagram_listing | requires_manual_review_before_runtime = yes, priority = low |  |

## 8. Phase 3-QA 修正紀錄

- 已將 add_principle_mutually_exclusive_choice 歸入 counting。
- 已將 mult_principle_independent_choices 歸入 counting。
- 已將 repeated_choice_basic 歸入 counting。
- 已將 repeated_permutation_assignment 歸入 counting。
- 已將 repeated_permutation_digits 歸入 counting。
- 已將上述題型 generator_key 修正為 b4.counting.*。
- 已移除 domain_function_requirements 中 eval_ 開頭的錯誤命名。
- problem_type 總數仍為 28。
- generator_registry_plan 總數仍為 28。
- exclude_from_generator = yes 仍為 1。

## 9. 與前端 / router 的銜接原則

- 前端仍維持以主技能 skill_id 作為入口。
- 前端不直接呼叫 subskill_id.py。
- 前端不直接呼叫 problem_type_id.py。
- 後端應新增 generator_router 或 question_router。
- router 根據 skill_id 選擇 subskill_id，再選 problem_type_id，再查 generator_key。
- 回傳題目時應包含 skill_id、subskill_id、problem_type_id、generator_key 等 metadata。
- 舊 skill_id.py 流程可作 fallback，不應直接破壞既有 route。

## 10. 後續 Phase 4 建議方向

Phase 4A：整理 B4 domain function 規格，不寫 generator。
Phase 4B：先實作 high priority deterministic generators。
Phase 4C：新增 generator_router，但前端仍維持 skill_id 呼叫。
Phase 4D：加入 duplicate avoidance 與 session fingerprint。
Phase 4E：接入 adaptive metadata。

## 11. 給非 coding 教師的操作說明

- 老師只需要看本報告確認題型名稱是否合理。
- 若老師發現題型歸類錯誤，可回報 problem_type_id 或 example_id。
- 老師不需要看 Python 程式。
- 老師不需要手動建立 generator。
- 後續若換教材版本，優先重新做 example 到 problem_type 的對應，不一定要重寫 generator。
