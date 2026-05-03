# B4 Phase 4A 第一章 Domain Function 規格設計

## 1. 本階段目的

- 本階段只設計 domain function 規格。
- 本階段不寫 Python 程式。
- 本階段不建立 generator。
- 本階段不修改 route。
- domain function 是 generator 共用的數學計算核心。
- generator 未來應呼叫 domain function 計算答案，不應自行硬算。

## 2. 讀取依據

- `reports/b4_generator_planning/b4_phase3_problem_type_map_counting_binomial.csv`：作為問題類型與 Domain Function 需求對應的依據。
- `reports/b4_generator_planning/b4_phase3_generator_registry_plan_counting_binomial.csv`：作為 Generator 與 Validator 對應的依據。
- `reports/b4_generator_planning/b4_phase3_counting_binomial_summary.md`：作為高階指引參考。
- `reports/b4_generator_planning/b4_phase2a_counting_binomial_summary.md`：作為過往統計參考。

## 3. Domain Function 模組規劃

### core/vocational_math_b4/domain/counting_domain_functions.py

負責：
- 加法原理
- 乘法原理
- 階乘
- 排列
- 組合
- 重複排列
- 數字排列
- 相鄰 / 不相鄰排列
- 正因數個數
- 正多邊形計數
- 列舉計數

### core/vocational_math_b4/domain/binomial_domain_functions.py

負責：
- 二項式展開
- 二項式係數
- 指定項係數
- 二項式係數和
- 巴斯卡三角形列

### core/vocational_math_b4/domain/b4_validators.py

負責：
- 正整數檢查
- n >= r 檢查
- answer 型別檢查
- choices 唯一性檢查
- answer 是否在 choices 中
- 未填空 placeholder 檢查
- 機率 / 統計後續擴充用驗證

## 4. Function 規格表

| function_name | module | used_by_problem_type_ids | purpose | input_parameters | return_type | valid_input_constraints | error_handling_rule | example_usage_plain_text | notes |
|---|---|---|---|---|---|---|---|---|---|
| addition_principle_count | counting_domain_functions.py | add_principle_mutually_exclusive_choice | 計算 addition_principle_count | counts:list[int] | int | counts 不可空；所有元素皆為非負整數 | invalid input raise ValueError with clear message | addition_principle_count([3,4,5]) returns 12 | 無 |
| multiplication_principle_count | counting_domain_functions.py | combination_seat_assignment, mult_principle_independent_choices | 計算 multiplication_principle_count | counts:list[int] | int | counts 不可空；所有元素皆為非負整數 | invalid input raise ValueError with clear message | multiplication_principle_count([3,4,5]) returns 60 | 無 |
| factorial | counting_domain_functions.py | factorial_evaluation, permutation_full_arrangement | 計算 factorial | n:int | int | n >= 0 | invalid input raise ValueError with clear message | factorial(5) returns 120 | 無 |
| factorial_ratio_solve_n | counting_domain_functions.py | factorial_equation_solve_n | 計算 factorial_ratio_solve_n | numerator_offset:int, denominator_offset:int, target:int, search_min:int=1, search_max:int=20 | int | target > 0；search_min <= search_max；求 n 使 (n+numerator_offset)!/(n+denominator_offset)! = target | invalid input raise ValueError with clear message | factorial_ratio_solve_n(0,-1,6) returns 6 | 無 |
| permutation | counting_domain_functions.py | combination_seat_assignment, permutation_formula_evaluation, permutation_role_assignment | 計算 permutation | n:int, r:int | int | n >= 0；r >= 0；n >= r | invalid input raise ValueError with clear message | permutation(5,2) returns 20 | 無 |
| combination | counting_domain_functions.py | combination_basic_selection, combination_definition_basic, combination_group_selection, combination_properties_simplification, combination_required_excluded_person, combination_restricted_selection, combination_seat_assignment | 計算 combination | n:int, r:int | int | n >= 0；r >= 0；n >= r | invalid input raise ValueError with clear message | combination(5,2) returns 10 | 無 |
| repeated_choice_count | counting_domain_functions.py | repeated_choice_basic | 計算 repeated_choice_count | choices_per_position:int, positions:int | int | choices_per_position >= 0；positions >= 0 | invalid input raise ValueError with clear message | repeated_choice_count(3,4) returns 81 | 無 |
| repeated_digit_arrangement_count | counting_domain_functions.py | repeated_permutation_digits | 計算 repeated_digit_arrangement_count | digit_count:int, length:int, allow_leading_zero:bool=True, last_digit_filter:str|None=None | int | digit_count >= 0；length >= 0；last_digit_filter 可為 None/even/odd | invalid input raise ValueError with clear message | repeated_digit_arrangement_count(5,3,True,None) returns 125 | 無 |
| repeated_assignment_count | counting_domain_functions.py | repeated_permutation_assignment | 計算 repeated_assignment_count | item_count:int, recipient_count:int, allow_empty:bool=True | int | item_count >= 0；recipient_count >= 0 | invalid input raise ValueError with clear message | repeated_assignment_count(3,4,True) returns 64 | 無 |
| divisor_count_from_prime_factorization | counting_domain_functions.py | divisor_count_prime_factorization | 計算 divisor_count_from_prime_factorization | exponents:list[int] | int | exponents 不可空；所有 exponent >= 0 | invalid input raise ValueError with clear message | divisor_count_from_prime_factorization([2,1,3]) returns 24 | 無 |
| digit_arrangement_count | counting_domain_functions.py | mult_digits_no_repeat, permutation_digit_parity | 計算 digit_arrangement_count | digits:list[int], length:int, allow_repetition:bool=False, allow_leading_zero:bool=False, last_digit_filter:str|None=None | int | digits 不可空；length >= 0；若 allow_repetition=False 則 length <= len(digits)；last_digit_filter 可為 None/even/odd | invalid input raise ValueError with clear message | digit_arrangement_count([1,2,3,4,5],3,False,False,"odd") returns a nonnegative integer | 無 |
| adjacent_arrangement_count | counting_domain_functions.py | permutation_adjacent_block | 計算 adjacent_arrangement_count | total_items:int, block_size:int, distinct:bool=True | int | total_items >= block_size >= 2；目前僅支援 distinct=True | invalid input raise ValueError with clear message | adjacent_arrangement_count(5,2,True) returns 48 | 無 |
| non_adjacent_arrangement_count | counting_domain_functions.py | permutation_adjacent_block | 計算 non_adjacent_arrangement_count | total_items:int, separated_items:int, distinct:bool=True | int | total_items >= separated_items >= 2；目前僅支援 distinct=True | invalid input raise ValueError with clear message | non_adjacent_arrangement_count(5,2,True) returns 72 | 無 |
| polygon_diagonal_count | counting_domain_functions.py | combination_polygon_count | 計算 polygon_diagonal_count | n:int | int | n >= 4 | invalid input raise ValueError with clear message | polygon_diagonal_count(6) returns 9 | 無 |
| polygon_triangle_count | counting_domain_functions.py | combination_polygon_count | 計算 polygon_triangle_count | n:int | int | n >= 3 | invalid input raise ValueError with clear message | polygon_triangle_count(6) returns 20 | 無 |
| pascal_identity | binomial_domain_functions.py | combination_properties_simplification | 計算 pascal_identity | n:int, r:int | int | n >= 1；1 <= r <= n | invalid input raise ValueError with clear message | pascal_identity(5,2) returns combination(6,3) | 無 |
| binomial_coefficient_sum | binomial_domain_functions.py | binomial_coefficient_sum | 計算 binomial_coefficient_sum | n:int | int | n >= 0 | invalid input raise ValueError with clear message | binomial_coefficient_sum(5) returns 32 | 無 |
| binomial_expansion_coefficients | binomial_domain_functions.py | binomial_expansion_basic | 計算 binomial_expansion_coefficients | a:int, b:int, n:int | list[int] | n >= 0 | invalid input raise ValueError with clear message | binomial_expansion_coefficients(1,2,3) returns coefficients of (x+2)^3 | 無 |
| binomial_term_coefficient | binomial_domain_functions.py | binomial_specific_term_coefficient | 計算 binomial_term_coefficient | a:int, b:int, n:int, target_power:int | int | n >= 0；0 <= target_power <= n | invalid input raise ValueError with clear message | binomial_term_coefficient(1,2,3,2) returns coefficient of x^2 in (x+2)^3 | 無 |
| combination_equation_solve_n | counting_domain_functions.py | binomial_equation_solve_n | 計算 combination_equation_solve_n | r:int, target:int, search_min:int=0, search_max:int=50 | int | r >= 0；target > 0；search_min <= search_max；求 n 使 C(n,r)=target | invalid input raise ValueError with clear message | combination_equation_solve_n(2,10) returns 5 | 無 |
| enumeration_count | counting_domain_functions.py | tree_diagram_listing | 計算 enumeration_count | branches:list[int] | int | branches 不可空；所有元素皆為非負整數 | invalid input raise ValueError with clear message | enumeration_count([2,2,2]) returns 8 | 無 |
| pascal_triangle_row | binomial_domain_functions.py | pascal_triangle_derivation | 計算 pascal_triangle_row | n:int | list[int] | n >= 0 | invalid input raise ValueError with clear message | pascal_triangle_row(5) returns [1,5,10,10,5,1] | 無 |

共同 error_handling_rule：
invalid input raise ValueError with clear message
不可回傳 None。
不可靜默修正錯誤輸入。

## 5. Validator 規格表

| validator_name | purpose | input_parameters | return_type | used_by_problem_type_ids | validation_rule | error_message_rule | notes |
|---|---|---|---|---|---|---|---|
| validate_positive_integer | 驗證 positive_integer | value:any, name:str="value" | bool | add_principle_mutually_exclusive_choice, binomial_coefficient_sum, binomial_expansion_basic, binomial_equation_solve_n, binomial_specific_term_coefficient, combination_basic_selection, combination_definition_basic, combination_polygon_count, combination_group_selection, combination_properties_simplification, combination_required_excluded_person, combination_restricted_selection, combination_seat_assignment, divisor_count_prime_factorization, factorial_evaluation, factorial_equation_solve_n, mult_digits_no_repeat, mult_principle_independent_choices, pascal_triangle_derivation, permutation_adjacent_block, permutation_digit_parity, permutation_formula_evaluation, permutation_full_arrangement, permutation_role_assignment, repeated_permutation_assignment, repeated_permutation_digits, repeated_choice_basic, tree_diagram_listing | value 必須是 int 且 value > 0 | 失敗時 raise ValueError，訊息包含 validator_name 與不合法欄位名稱。 | 無 |
| validate_nonnegative_integer | 驗證 nonnegative_integer | value:any, name:str="value" | bool | 依題意 | value 必須是 int 且 value >= 0 | 失敗時 raise ValueError，訊息包含 validator_name 與不合法欄位名稱。 | 無 |
| validate_n_ge_r | 驗證 n_ge_r | n:int, r:int | bool | add_principle_mutually_exclusive_choice, binomial_coefficient_sum, binomial_expansion_basic, binomial_equation_solve_n, binomial_specific_term_coefficient, combination_basic_selection, combination_definition_basic, combination_polygon_count, combination_group_selection, combination_properties_simplification, combination_required_excluded_person, combination_restricted_selection, combination_seat_assignment, divisor_count_prime_factorization, factorial_evaluation, factorial_equation_solve_n, mult_digits_no_repeat, mult_principle_independent_choices, pascal_triangle_derivation, permutation_adjacent_block, permutation_digit_parity, permutation_formula_evaluation, permutation_full_arrangement, permutation_role_assignment, repeated_permutation_assignment, repeated_permutation_digits, repeated_choice_basic, tree_diagram_listing | n >= r 且 n,r 皆為非負整數 | 失敗時 raise ValueError，訊息包含 validator_name 與不合法欄位名稱。 | 無 |
| validate_choices_unique | 驗證 choices_unique | choices:list | bool | add_principle_mutually_exclusive_choice, binomial_coefficient_sum, binomial_expansion_basic, binomial_equation_solve_n, binomial_specific_term_coefficient, combination_basic_selection, combination_definition_basic, combination_polygon_count, combination_group_selection, combination_properties_simplification, combination_required_excluded_person, combination_restricted_selection, combination_seat_assignment, divisor_count_prime_factorization, factorial_evaluation, factorial_equation_solve_n, mult_digits_no_repeat, mult_principle_independent_choices, pascal_triangle_derivation, permutation_adjacent_block, permutation_digit_parity, permutation_formula_evaluation, permutation_full_arrangement, permutation_role_assignment, repeated_permutation_assignment, repeated_permutation_digits, repeated_choice_basic, tree_diagram_listing | choices 轉成字串後不可重複 | 失敗時 raise ValueError，訊息包含 validator_name 與不合法欄位名稱。 | 無 |
| validate_answer_in_choices | 驗證 answer_in_choices | answer:any, choices:list | bool | add_principle_mutually_exclusive_choice, binomial_coefficient_sum, binomial_expansion_basic, binomial_equation_solve_n, binomial_specific_term_coefficient, combination_basic_selection, combination_definition_basic, combination_polygon_count, combination_group_selection, combination_properties_simplification, combination_required_excluded_person, combination_restricted_selection, combination_seat_assignment, divisor_count_prime_factorization, factorial_evaluation, factorial_equation_solve_n, mult_digits_no_repeat, mult_principle_independent_choices, pascal_triangle_derivation, permutation_adjacent_block, permutation_digit_parity, permutation_formula_evaluation, permutation_full_arrangement, permutation_role_assignment, repeated_permutation_assignment, repeated_permutation_digits, repeated_choice_basic, tree_diagram_listing | answer 的標準化字串必須出現在 choices 的標準化字串中 | 失敗時 raise ValueError，訊息包含 validator_name 與不合法欄位名稱。 | 無 |
| validate_no_unfilled_placeholder | 驗證 no_unfilled_placeholder | text:str | bool | add_principle_mutually_exclusive_choice, binomial_coefficient_sum, binomial_expansion_basic, binomial_equation_solve_n, binomial_specific_term_coefficient, combination_basic_selection, combination_definition_basic, combination_polygon_count, combination_group_selection, combination_properties_simplification, combination_required_excluded_person, combination_restricted_selection, combination_seat_assignment, divisor_count_prime_factorization, factorial_evaluation, factorial_equation_solve_n, mult_digits_no_repeat, mult_principle_independent_choices, pascal_triangle_derivation, permutation_adjacent_block, permutation_digit_parity, permutation_formula_evaluation, permutation_full_arrangement, permutation_role_assignment, repeated_permutation_assignment, repeated_permutation_digits, repeated_choice_basic, tree_diagram_listing | text 不可含 [BLANK]、[FORMULA_MISSING]、[FORMULA_IMAGE]、[WORD_EQUATION_UNPARSED]、□、＿＿ | 失敗時 raise ValueError，訊息包含 validator_name 與不合法欄位名稱。 | 無 |
| validate_integer_answer | 驗證 integer_answer | answer:any | bool | 全部或依題意 | answer 必須可解析為整數 | 失敗時 raise ValueError，訊息包含 validator_name 與不合法欄位名稱。 | 無 |
| validate_expression_answer | 驗證 expression_answer | answer:any | bool | 全部或依題意 | answer 必須是非空字串或可序列化表達式 | 失敗時 raise ValueError，訊息包含 validator_name 與不合法欄位名稱。 | 無 |
| validate_polynomial_answer | 驗證 polynomial_answer | answer:any | bool | 全部或依題意 | answer 必須可表示為多項式字串或係數列表 | 失敗時 raise ValueError，訊息包含 validator_name 與不合法欄位名稱。 | 無 |
| validate_parameter_tuple_not_seen | 驗證 parameter_tuple_not_seen | parameter_tuple:tuple, seen:set | bool | 依題意 | parameter_tuple 不在 seen 中 | 失敗時 raise ValueError，訊息包含 validator_name 與不合法欄位名稱。 | 無 |
| validate_problem_payload_contract | 驗證 problem_payload_contract | payload:dict | bool | 全部或依題意 | payload 必須包含 question_text, choices, answer, explanation, skill_id, subskill_id, problem_type_id, generator_key, difficulty, diagnosis_tags, remediation_candidates, source_style_refs | 失敗時 raise ValueError，訊息包含 validator_name 與不合法欄位名稱。 | 無 |

共同 error_message_rule：
失敗時 raise ValueError，訊息包含 validator_name 與不合法欄位名稱。

## 6. Output Contract 規格

未來所有 generator 應輸出的標準 dict 欄位：
- **question_text**: 題幹字串
- **choices**: 選擇題選項清單（如不支援或非選擇題可為空）
- **answer**: 標準答案（依照 expected_answer_type 決定型別）
- **explanation**: 詳細詳解字串
- **skill_id**: 對應原始 skill_id
- **subskill_id**: 對應分類的 subskill_id
- **problem_type_id**: 對應本階段規劃的題型
- **generator_key**: 註冊的 generator 識別碼
- **difficulty**: 題目難度層級
- **diagnosis_tags**: 學習診斷標籤清單
- **remediation_candidates**: 需要補救的相關項目
- **source_style_refs**: 參考原始題型來源的 ID 或指紋

## 7. 與 Phase 3 Problem Type 的對應表

| problem_type_id | generator_key | required_domain_functions | required_validators | expected_answer_type | supports_multiple_choice | supports_free_response | priority |
|---|---|---|---|---|---|---|---|
| add_principle_mutually_exclusive_choice | b4.counting.add_principle_mutually_exclusive_choice | addition_principle_count | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| binomial_coefficient_sum | b4.binomial.binomial_coefficient_sum | binomial_coefficient_sum | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| binomial_expansion_basic | b4.binomial.binomial_expansion_basic | binomial_expansion_coefficients | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | high |
| binomial_equation_solve_n | b4.binomial.binomial_equation_solve_n | combination_equation_solve_n | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| binomial_specific_term_coefficient | b4.binomial.binomial_specific_term_coefficient | binomial_term_coefficient | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| combination_basic_selection | b4.combination.combination_basic_selection | combination | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| combination_definition_basic | b4.combination.combination_definition_basic | combination | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | high |
| combination_polygon_count | b4.combination.combination_polygon_count | polygon_diagonal_count,polygon_triangle_count | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | high |
| combination_group_selection | b4.combination.combination_group_selection | combination | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | high |
| combination_properties_simplification | b4.combination.combination_properties_simplification | combination,pascal_identity | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| combination_required_excluded_person | b4.combination.combination_required_excluded_person | combination | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | high |
| combination_restricted_selection | b4.combination.combination_restricted_selection | combination | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| combination_seat_assignment | b4.combination.combination_seat_assignment | combination,permutation,multiplication_principle_count | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| divisor_count_prime_factorization | b4.counting.divisor_count_prime_factorization | divisor_count_from_prime_factorization | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | high |
| factorial_evaluation | b4.counting.factorial_evaluation | factorial | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| factorial_equation_solve_n | b4.counting.factorial_equation_solve_n | factorial_ratio_solve_n | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | high |
| mult_digits_no_repeat | b4.counting.mult_digits_no_repeat | digit_arrangement_count | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| mult_principle_independent_choices | b4.counting.mult_principle_independent_choices | multiplication_principle_count | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| pascal_triangle_derivation | b4.binomial.pascal_triangle_derivation | pascal_triangle_row | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | list | no | yes | low |
| permutation_adjacent_block | b4.permutation.permutation_adjacent_block | adjacent_arrangement_count,non_adjacent_arrangement_count | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | high |
| permutation_digit_parity | b4.permutation.permutation_digit_parity | digit_arrangement_count | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | high |
| permutation_formula_evaluation | b4.permutation.permutation_formula_evaluation | permutation | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| permutation_full_arrangement | b4.permutation.permutation_full_arrangement | factorial | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| permutation_role_assignment | b4.permutation.permutation_role_assignment | permutation | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | high |
| repeated_permutation_assignment | b4.counting.repeated_permutation_assignment | repeated_assignment_count | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | high |
| repeated_permutation_digits | b4.counting.repeated_permutation_digits | repeated_digit_arrangement_count | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | high |
| repeated_choice_basic | b4.counting.repeated_choice_basic | repeated_choice_count | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | integer | yes | yes | medium |
| tree_diagram_listing | b4.tree_enumeration.tree_diagram_listing | enumeration_count | core/vocational_math_b4/domain/b4_validators.py; validate_positive_integer, validate_n_ge_r, validate_choices_unique, validate_answer_in_choices, validate_no_unfilled_placeholder | list | no | yes | low |

## 8. 實作順序建議

Phase 4B 第一批可實作的候選：

| priority_order | problem_type_id | generator_key | required_domain_functions | 理由 |
|---|---|---|---|---|
| 1 | binomial_expansion_basic | b4.binomial.binomial_expansion_basic | binomial_expansion_coefficients | 高優先級且無須人工審查 |
| 2 | combination_definition_basic | b4.combination.combination_definition_basic | combination | 高優先級且無須人工審查 |
| 3 | combination_polygon_count | b4.combination.combination_polygon_count | polygon_diagonal_count,polygon_triangle_count | 高優先級且無須人工審查 |
| 4 | combination_group_selection | b4.combination.combination_group_selection | combination | 高優先級且無須人工審查 |
| 5 | combination_required_excluded_person | b4.combination.combination_required_excluded_person | combination | 高優先級且無須人工審查 |
| 6 | divisor_count_prime_factorization | b4.counting.divisor_count_prime_factorization | divisor_count_from_prime_factorization | 高優先級且無須人工審查 |
| 7 | factorial_equation_solve_n | b4.counting.factorial_equation_solve_n | factorial_ratio_solve_n | 高優先級且無須人工審查 |
| 8 | permutation_adjacent_block | b4.permutation.permutation_adjacent_block | adjacent_arrangement_count,non_adjacent_arrangement_count | 高優先級且無須人工審查 |
| 9 | permutation_digit_parity | b4.permutation.permutation_digit_parity | digit_arrangement_count | 高優先級且無須人工審查 |
| 10 | permutation_role_assignment | b4.permutation.permutation_role_assignment | permutation | 高優先級且無須人工審查 |
| 11 | repeated_permutation_assignment | b4.counting.repeated_permutation_assignment | repeated_assignment_count | 高優先級且無須人工審查 |
| 12 | repeated_permutation_digits | b4.counting.repeated_permutation_digits | repeated_digit_arrangement_count | 高優先級且無須人工審查 |

## 9. 風險與注意事項

- domain function 必須純函式，不依賴 session / database / frontend。
- generator 不應自行計算答案，必須呼叫 domain function。
- 同一 domain function 可能被多個 generator 共用。
- 不要把文字題語意判斷放進 domain function。
- 不要把 choice 生成混進 domain function。
- 不要把 adaptive 狀態混進 domain function。
- B4 後續 Chapter 2 機率、Chapter 3 統計會新增 probability_domain_functions.py 與 statistics_domain_functions.py，目前不要規劃太細。

domain function 不得包含：
- 題幹自然語言生成
- 選項干擾項生成
- 學生狀態判斷
- skill/subskill/problem_type 路由
- session duplicate history 查詢
- 資料庫查詢
- AI prompt 或 healer 呼叫

## 10. 給非 coding 教師的說明

- domain function 是「計算答案的標準工具」。
- 老師不需要寫程式，只需要確認題型和答案規則是否合理。
- 未來若題目數字改變，domain function 會重新計算答案。
- 這能避免 AI 自己亂算答案。
