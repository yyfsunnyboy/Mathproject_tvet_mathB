# B4 Phase 2A 第一章排列組合與二項式成果凍結報告

## 1. 本階段目的

- 本階段只凍結 Phase 2A 成果。
- 本階段不建立 generator。
- 本階段不正式定義 problem_type。
- 本階段的 template_candidate 仍是候選模板，不是正式 generator。

## 2. 處理範圍

- 處理章節：1 排列組合
- 處理內容：加法原理、乘法原理、階乘、排列、重複排列、組合、二項式定理
- 讀取檔案：
  - `reports/b4_generator_planning/b4_phase2a_subskill_map_counting_binomial.csv`
  - `reports/b4_generator_planning/b4_phase2a_example_template_candidate_map_counting_binomial.csv`
  - `reports/b4_generator_planning/b4_data_quality_review.md`
- 輸出檔案：`reports/b4_generator_planning/b4_phase2a_counting_binomial_summary.md`

## 3. Phase 2A 成果統計

- subskill 總數：28
- example_template_map 總列數：68
- skill 總數：14
- template_candidate_id 總數：29
- variation_possible = yes 的數量：40
- variation_possible = partial 的數量：27
- variation_possible = no 的數量：False
- exclude_from_generator = yes 的數量：1
- review_required = yes 的數量：26
- adaptive_enabled = yes 的 subskill 數量：26

## 4. Subskill 清單摘要

### vh_數學B4_AdditionPrinciple - 加法原理

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_add_principle_01 | 互斥分類選擇加法原理 | yes | yes | 3618,3619,3668,3620 | 從多個互斥類別中選一個對象或方法，總數為各類方法數相加 |

### vh_數學B4_BinomialCoefficientIdentities - 二項式係數性質

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_binomial_id_01 | 二項式係數總和 | yes | yes | 3665,3666,3667 | 求組合數C(n,0)到C(n,n)之和 |

### vh_數學B4_BinomialTheorem - 二項式定理

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_binomial_expand_01 | 二項式完全展開 | yes | no | 3656,3659 | 展開 (x+a)^n |
| 2 | b4_ch1_binomial_coeff_02 | 二項式特定項係數 | yes | yes | 3657,3658,3660,3661,3690 | 求展開式中特定次方的係數 |
| 3 | b4_ch1_binomial_solve_n_03 | 已知組合數求參數 | yes | yes | 3691 | 已知組合數數值求n |

### vh_數學B4_Combination - 組合

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_comb_basic_01 | 組合基本計數 | yes | yes | 3683,3684,3686 | 顏色調配、數字和為偶數、套餐搭配 |
| 2 | b4_ch1_comb_restrict_02 | 組合限制條件選取 | yes | yes | 3685,3687,3688 | 特定男女數目、至少幾題或至少幾位女生的選法 |
| 3 | b4_ch1_comb_seat_03 | 組合與排列綜合應用 | yes | yes | 3689 | 不同身分者坐在指定編號座位的排法 |

### vh_數學B4_CombinationApplications - 組合的應用

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_comb_app_people_01 | 人員組合選取 | yes | no | 3648,3649,3651,3652 | 選出人員、特定人員必參加或不參加 |
| 2 | b4_ch1_comb_app_geom_02 | 幾何組合應用 | yes | no | 3650,3653 | 計算正多邊形的對角線條數與可構成的三角形個數 |
| 3 | b4_ch1_comb_app_item_03 | 物品組合搭配 | yes | no | 3654 | 甜品選配 |

### vh_數學B4_CombinationDefinition - 組合的定義與計算

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_comb_def_01 | 組合定義基本選取 | yes | no | 3643,3645 | 作答選題與電扇展示選取 |

### vh_數學B4_CombinationProperties - 組合的性質

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_comb_prop_01 | 巴斯卡組合性質 | yes | yes | 3646,3647 | 計算組合數相加的值 |

### vh_數學B4_FactorialNotation - 階乘記法

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_factorial_eval_01 | 階乘數值計算 | yes | yes | 3628,3630 | 計算 n! 或 n!/m! |
| 2 | b4_ch1_factorial_solve_02 | 階乘方程式求解 | yes | no | 3629,3631 | 求滿足 n!/(n-1)! = k 的 n 值 |

### vh_數學B4_MultiplicationPrinciple - 乘法原理

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_mult_principle_01 | 乘法原理基本應用 | yes | yes | 3621,3623,3669,3670,3625 | 依序選擇不同類別物品的搭配總數 |
| 2 | b4_ch1_mult_factors_02 | 正因數個數計算 | yes | no | 3622,3624 | 計算給定數字的正因數總數 |
| 3 | b4_ch1_mult_digits_03 | 數字排法乘法原理 | yes | yes | 3671 | 從區間內找出位數不重複的數字個數 |

### vh_數學B4_PascalTriangle - 巴斯卡三角形

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_pascal_tri_01 | 巴斯卡三角形推導 | no | no | 3655 | 推導第五列與第六列 |

### vh_數學B4_PermutationOfDistinctObjects - 相異物的排列

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_perm_linear_01 | 直線全排列 | yes | yes | 3599,3604 | n個人或字母排成一列 |
| 2 | b4_ch1_perm_formula_02 | 排列符號計算 | yes | yes | 3600,3605 | 計算P(n,r)的值 |
| 3 | b4_ch1_perm_select_03 | 選取排列 | yes | no | 3601,3606 | 選出r個事物擔任不同職位或安排順序 |
| 4 | b4_ch1_perm_digits_04 | 數字選取排列 | yes | no | 3602 | 排成不重複的奇偶數 |
| 5 | b4_ch1_perm_adjacent_05 | 相鄰與不相鄰排列 | yes | no | 3603 | 特定對象必須相鄰或不相鄰的排法 |

### vh_數學B4_PermutationWithRepetition - 重複排列

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_repeated_choice_01 | 重複選擇基本計數 | yes | yes | 3681,3682 | 每個人或每個位置都有相同選擇數，總數為 m^n |

### vh_數學B4_RepeatedPermutation - 重複排列

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_rep_perm_digits_01 | 數字重複排列 | yes | no | 3632,3635,3638 | 數字可重複選取排成多位數，含奇偶條件 |
| 2 | b4_ch1_rep_perm_assign_02 | 重複排列分派問題 | yes | no | 3633,3634,3636,3637,3639 | 泡湯選擇、分獎品、搭船、猜拳等分派 |

### vh_數學B4_TreeDiagramCounting - 樹狀圖

| teaching_order | subskill_id | subskill_name | adaptive_enabled | review_required | source_example_ids | evidence_summary |
|---|---|---|---|---|---|---|
| 1 | b4_ch1_tree_diagram_01 | 樹狀圖計數 | no | no | 3614,3615,3616,3617 | 比賽勝負、硬幣投擲、數字排列等情形列舉 |


## 5. Template Candidate 清單摘要

| template_candidate_id | template_candidate_name | 對應 example 數 | variation_possible 分布 | exclude_from_generator | answer_verification_need | 對應 skill |
|---|---|---|---|---|---|---|
| tc_add_principle_mutually_exclusive_choice_01 | 互斥分類選擇加法原理 | 4 | yes:4 | no | addition_principle | 加法原理 |
| tc_binomial_coeff_sum_01 | 二項式係數和 | 3 | partial:3 | no | binomial_coefficient | 二項式係數性質 |
| tc_binomial_expand_basic_01 | 二項式展開 | 2 | yes:2 | no | binomial_coefficient | 二項式定理 |
| tc_binomial_solve_n_03 | 已知組合數求參數 | 1 | partial:1 | no | combination | 二項式定理 |
| tc_binomial_specific_term_02 | 指定項係數 | 5 | yes:3, partial:2 | no | binomial_term_coefficient | 二項式定理 |
| tc_comb_basic_selection_01 | 組合基本選取 | 3 | partial:3 | no | combination | 組合 |
| tc_comb_definition_01 | 組合定義基本計算 | 2 | yes:2 | no | combination | 組合的定義與計算 |
| tc_comb_geometry_02 | 多邊形對角線與三角形 | 1 | yes:1 | no | combination | 組合的應用 |
| tc_comb_group_selection_03 | 分類組合乘法 | 1 | yes:1 | no | combination | 組合的應用 |
| tc_comb_polygon_diagonal_triangle_02 | 正多邊形對角線與三角形計數 | 1 | yes:1 | no | combination | 組合的應用 |
| tc_comb_properties_01 | 組合性質化簡 | 2 | partial:2 | no | combination | 組合的性質 |
| tc_comb_required_or_excluded_person_01 | 指定人物必選或不可選 | 4 | yes:4 | no | combination | 組合的應用 |
| tc_comb_restricted_selection_02 | 組合特定數量限制選取 | 3 | partial:3 | no | combination | 組合 |
| tc_comb_seat_assignment_03 | 組合與排列混合排座 | 1 | partial:1 | no | multiplication_principle | 組合 |
| tc_divisor_count_prime_factorization_02 | 正因數個數計算 | 2 | yes:2 | no | multiplication_principle | 乘法原理 |
| tc_factorial_eval_01 | 階乘式求值 | 2 | partial:2 | no | factorial | 階乘記法 |
| tc_factorial_solve_n_02 | 階乘方程求正整數 n | 2 | yes:2 | no | factorial | 階乘記法 |
| tc_mult_digits_no_repeat_03 | 數字排列無重複 | 1 | partial:1 | no | multiplication_principle | 乘法原理 |
| tc_mult_principle_independent_choices_01 | 多階段選擇乘法原理 | 5 | yes:3, partial:2 | no | multiplication_principle | 乘法原理 |
| tc_pascal_tri_derivation_01 | 巴斯卡三角形推導 | 1 | no:1 | yes | manual_or_visual_check | 巴斯卡三角形 |
| tc_perm_adjacent_block_05 | 相鄰與不相鄰限制排列 | 1 | yes:1 | no | permutation | 相異物的排列 |
| tc_perm_digit_parity_04 | 數字排列含奇偶限制 | 1 | yes:1 | no | permutation | 相異物的排列 |
| tc_perm_formula_eval_02 | 排列記號 P(n,r) 求值 | 2 | partial:2 | no | permutation | 相異物的排列 |
| tc_perm_full_arrangement_01 | 相異物全取排列 | 2 | yes:1, partial:1 | no | permutation | 相異物的排列 |
| tc_perm_role_assignment_03 | 不同職務分配 | 2 | yes:2 | no | permutation | 相異物的排列 |
| tc_rep_perm_assign_02 | 重複排列分派計數 | 5 | yes:5 | no | repeated_permutation | 重複排列 |
| tc_rep_perm_digits_01 | 數字重複排列 | 3 | yes:3 | no | repeated_permutation | 重複排列 |
| tc_repeated_choice_basic_01 | 重複選擇基本計數 | 2 | yes:2 | no | repeated_permutation | 重複排列 |
| tc_tree_diagram_listing_01 | 樹狀圖列舉 | 4 | partial:4 | no | enumeration_count | 樹狀圖 |

## 6. 可優先進 Phase 3 的模板候選

| template_candidate_id | template_candidate_name | 建議原因 | answer_verification_need |
|---|---|---|---|
| tc_add_principle_mutually_exclusive_choice_01 | 互斥分類選擇加法原理 | 不須排除且有明確驗證方式 | addition_principle |
| tc_binomial_coeff_sum_01 | 二項式係數和 | 不須排除且有明確驗證方式 | binomial_coefficient |
| tc_binomial_expand_basic_01 | 二項式展開 | 不須排除且有明確驗證方式 | binomial_coefficient |
| tc_binomial_solve_n_03 | 已知組合數求參數 | 不須排除且有明確驗證方式 | combination |
| tc_binomial_specific_term_02 | 指定項係數 | 不須排除且有明確驗證方式 | binomial_term_coefficient |
| tc_comb_basic_selection_01 | 組合基本選取 | 不須排除且有明確驗證方式 | combination |
| tc_comb_definition_01 | 組合定義基本計算 | 不須排除且有明確驗證方式 | combination |
| tc_comb_geometry_02 | 多邊形對角線與三角形 | 不須排除且有明確驗證方式 | combination |
| tc_comb_group_selection_03 | 分類組合乘法 | 不須排除且有明確驗證方式 | combination |
| tc_comb_polygon_diagonal_triangle_02 | 正多邊形對角線與三角形計數 | 不須排除且有明確驗證方式 | combination |
| tc_comb_properties_01 | 組合性質化簡 | 不須排除且有明確驗證方式 | combination |
| tc_comb_required_or_excluded_person_01 | 指定人物必選或不可選 | 不須排除且有明確驗證方式 | combination |
| tc_comb_restricted_selection_02 | 組合特定數量限制選取 | 不須排除且有明確驗證方式 | combination |
| tc_comb_seat_assignment_03 | 組合與排列混合排座 | 不須排除且有明確驗證方式 | multiplication_principle |
| tc_divisor_count_prime_factorization_02 | 正因數個數計算 | 不須排除且有明確驗證方式 | multiplication_principle |
| tc_factorial_eval_01 | 階乘式求值 | 不須排除且有明確驗證方式 | factorial |
| tc_factorial_solve_n_02 | 階乘方程求正整數 n | 不須排除且有明確驗證方式 | factorial |
| tc_mult_digits_no_repeat_03 | 數字排列無重複 | 不須排除且有明確驗證方式 | multiplication_principle |
| tc_mult_principle_independent_choices_01 | 多階段選擇乘法原理 | 不須排除且有明確驗證方式 | multiplication_principle |
| tc_perm_adjacent_block_05 | 相鄰與不相鄰限制排列 | 不須排除且有明確驗證方式 | permutation |
| tc_perm_digit_parity_04 | 數字排列含奇偶限制 | 不須排除且有明確驗證方式 | permutation |
| tc_perm_formula_eval_02 | 排列記號 P(n,r) 求值 | 不須排除且有明確驗證方式 | permutation |
| tc_perm_full_arrangement_01 | 相異物全取排列 | 不須排除且有明確驗證方式 | permutation |
| tc_perm_role_assignment_03 | 不同職務分配 | 不須排除且有明確驗證方式 | permutation |
| tc_rep_perm_assign_02 | 重複排列分派計數 | 不須排除且有明確驗證方式 | repeated_permutation |
| tc_rep_perm_digits_01 | 數字重複排列 | 不須排除且有明確驗證方式 | repeated_permutation |
| tc_repeated_choice_basic_01 | 重複選擇基本計數 | 不須排除且有明確驗證方式 | repeated_permutation |
| tc_tree_diagram_listing_01 | 樹狀圖列舉 | 不須排除且有明確驗證方式 | enumeration_count |

## 7. 暫不進 Phase 3 的題目或模板

| example_id | skill_id | source_description | template_candidate_id | exclude_reason | notes |
|---|---|---|---|---|---|
| 3655 | vh_數學B4_PascalTriangle | 動動手 | tc_pascal_tri_derivation_01 | manual_review_required |  |

## 8. QA 修正紀錄

- 已補回 AdditionPrinciple。
- 已修正 PermutationWithRepetition 被誤判為不盡相異物排列。
- 已將 TreeDiagramCounting 由完全排除改為 partial 且不排除 generator。
- 已將正多邊形對角線與三角形計數 example_id 3650 改為可生成。
- 目前 exclude_from_generator = yes 僅剩 1 題。

## 9. 後續 Phase 3 建議方向

Phase 3 應將 template_candidate 正式整理成 canonical problem_type，並建立：
- `b4_phase3_problem_type_map_counting_binomial.csv`
- `b4_phase3_generator_registry_plan_counting_binomial.csv`

但本報告不建立上述檔案。

Phase 3 需要確認：
- 哪些 template_candidate 可合併為同一 problem_type
- 每個 problem_type 對應哪個 domain function
- 每個 problem_type 是否需要選項生成器
- 每個 problem_type 是否需要 verifier
- 是否能維持與課本例題同難度、相似結構、不同數據且不重複

## 10. 給非 coding 教師的操作說明

- 老師只需要看本報告確認題型是否合理。
- 若老師發現某題分類錯誤，可回報 example_id 與正確題型說明。
- 老師不需要看 Python 程式。
- 老師不需要手動補 generator。
- 後續若換教材版本，只需要重新做 example 到 template_candidate 對應，不一定要重寫 generator。
