# B4 Phase 4B-2 Generator ????????

## 1. ?????
?????? Phase 4B-2 ? 3 ? deterministic generators ????????????????????????????? route?

## 2. ????
- `b4.combination.combination_definition_basic` | module: `core/vocational_math_b4/generators/combination.py` | function: `generate`????? `combination_definition_basic`?
- `b4.permutation.permutation_role_assignment` | module: `core/vocational_math_b4/generators/permutation.py` | function: `generate`????? `permutation_role_assignment`?
- `b4.counting.repeated_permutation_digits` | module: `core/vocational_math_b4/generators/counting.py` | function: `generate`????? `repeated_permutation_digits`?

## 3. ??????
| generator_key | ??? | unique_parameter_tuple ? | choices_valid | answer_valid | metadata_complete | placeholder_free | ???? |
|---|---:|---:|---|---|---|---|---|
| b4.combination.combination_definition_basic | 5 | 4 | ? | ? | ? | ? | ??? |
| b4.permutation.permutation_role_assignment | 5 | 4 | ? | ? | ? | ? | ??? |
| b4.counting.repeated_permutation_digits | 5 | 3 | ? | ? | ? | ? | ??? |

## 4. ????

### b4.combination.combination_definition_basic

#### seed = 1
- question_text: 從 6 件不同作品中選出 2 件展示，共有多少種選法？
- choices: [14, 7, 15, 13]
- answer: 15
- explanation: 此題不計順序，使用 C(n,r)=n!/(r!(n-r)!)，所以 C(6,2)=15。
- parameters: {'n': 6, 'r': 2, 'parameter_tuple': ('combination_definition_basic', 6, 2)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

#### seed = 2
- question_text: 從 5 件不同作品中選出 2 件展示，共有多少種選法？
- choices: [8, 9, 5, 10]
- answer: 10
- explanation: 此題不計順序，使用 C(n,r)=n!/(r!(n-r)!)，所以 C(5,2)=10。
- parameters: {'n': 5, 'r': 2, 'parameter_tuple': ('combination_definition_basic', 5, 2)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

#### seed = 3
- question_text: 從 6 件不同作品中選出 2 件展示，共有多少種選法？
- choices: [15, 7, 14, 13]
- answer: 15
- explanation: 此題不計順序，使用 C(n,r)=n!/(r!(n-r)!)，所以 C(6,2)=15。
- parameters: {'n': 6, 'r': 2, 'parameter_tuple': ('combination_definition_basic', 6, 2)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

#### seed = 4
- question_text: 從 6 件不同作品中選出 3 件展示，共有多少種選法？
- choices: [18, 40, 10, 20]
- answer: 20
- explanation: 此題不計順序，使用 C(n,r)=n!/(r!(n-r)!)，所以 C(6,3)=20。
- parameters: {'n': 6, 'r': 3, 'parameter_tuple': ('combination_definition_basic', 6, 3)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

#### seed = 5
- question_text: 從 7 件不同作品中選出 3 件展示，共有多少種選法？
- choices: [34, 36, 33, 35]
- answer: 35
- explanation: 此題不計順序，使用 C(n,r)=n!/(r!(n-r)!)，所以 C(7,3)=35。
- parameters: {'n': 7, 'r': 3, 'parameter_tuple': ('combination_definition_basic', 7, 3)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

### b4.permutation.permutation_role_assignment

#### seed = 1
- question_text: 從 6 位同學中選出 2 位分別擔任不同職務，共有多少種安排方式？
- choices: [60, 32, 30, 33]
- answer: 30
- explanation: 職務不同且順序重要，使用 P(n,r)=n!/(n-r)!，所以 P(6,2)=30。
- parameters: {'n': 6, 'r': 2, 'parameter_tuple': ('permutation_role_assignment', 6, 2)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

#### seed = 2
- question_text: 從 5 位同學中選出 2 位分別擔任不同職務，共有多少種安排方式？
- choices: [10, 18, 40, 20]
- answer: 20
- explanation: 職務不同且順序重要，使用 P(n,r)=n!/(n-r)!，所以 P(5,2)=20。
- parameters: {'n': 5, 'r': 2, 'parameter_tuple': ('permutation_role_assignment', 5, 2)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

#### seed = 3
- question_text: 從 6 位同學中選出 2 位分別擔任不同職務，共有多少種安排方式？
- choices: [30, 32, 60, 33]
- answer: 30
- explanation: 職務不同且順序重要，使用 P(n,r)=n!/(n-r)!，所以 P(6,2)=30。
- parameters: {'n': 6, 'r': 2, 'parameter_tuple': ('permutation_role_assignment', 6, 2)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

#### seed = 4
- question_text: 從 6 位同學中選出 3 位分別擔任不同職務，共有多少種安排方式？
- choices: [119, 240, 118, 120]
- answer: 120
- explanation: 職務不同且順序重要，使用 P(n,r)=n!/(n-r)!，所以 P(6,3)=120。
- parameters: {'n': 6, 'r': 3, 'parameter_tuple': ('permutation_role_assignment', 6, 3)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

#### seed = 5
- question_text: 從 7 位同學中選出 3 位分別擔任不同職務，共有多少種安排方式？
- choices: [105, 208, 420, 210]
- answer: 210
- explanation: 職務不同且順序重要，使用 P(n,r)=n!/(n-r)!，所以 P(7,3)=210。
- parameters: {'n': 7, 'r': 3, 'parameter_tuple': ('permutation_role_assignment', 7, 3)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

### b4.counting.repeated_permutation_digits

#### seed = 1
- question_text: 有 3 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？
- choices: [8, 4, 9, 7]
- answer: 9
- explanation: 每一位都有 3 種選擇，使用 m^n 得 3^2=9。
- parameters: {'digit_count': 3, 'length': 2, 'parameter_tuple': ('repeated_permutation_digits', 3, 2)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

#### seed = 2
- question_text: 有 3 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？
- choices: [7, 8, 4, 9]
- answer: 9
- explanation: 每一位都有 3 種選擇，使用 m^n 得 3^2=9。
- parameters: {'digit_count': 3, 'length': 2, 'parameter_tuple': ('repeated_permutation_digits', 3, 2)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

#### seed = 3
- question_text: 有 3 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？
- choices: [9, 4, 8, 7]
- answer: 9
- explanation: 每一位都有 3 種選擇，使用 m^n 得 3^2=9。
- parameters: {'digit_count': 3, 'length': 2, 'parameter_tuple': ('repeated_permutation_digits', 3, 2)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

#### seed = 4
- question_text: 有 3 個可用數字，每個數字可重複使用，排成 3 位數，共有多少種排法？
- choices: [25, 13, 54, 27]
- answer: 27
- explanation: 每一位都有 3 種選擇，使用 m^n 得 3^3=27。
- parameters: {'digit_count': 3, 'length': 3, 'parameter_tuple': ('repeated_permutation_digits', 3, 3)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

#### seed = 5
- question_text: 有 5 個可用數字，每個數字可重複使用，排成 3 位數，共有多少種排法？
- choices: [128, 125, 250, 62]
- answer: 125
- explanation: 每一位都有 5 種選擇，使用 m^n 得 5^3=125。
- parameters: {'digit_count': 5, 'length': 3, 'parameter_tuple': ('repeated_permutation_digits', 5, 3)}
- ????:
  - choices_unique: True
  - answer_in_choices: True
  - metadata_complete: True
  - placeholder_free: True
  - formula_in_explanation: True
  - notes: answer_is_int=True, zh_tw_like=True

## 5. ????????????
| generator_key | ?????? | ????? | ?? |
|---|---|---|---|
| b4.combination.combination_definition_basic | ?????????tc_comb_definition_01? | ? | ????? Phase 2A/3 ?????????????? |
| b4.permutation.permutation_role_assignment | ?????????tc_perm_role_assignment_03? | ? | ????? Phase 2A/3 ?????????????? |
| b4.counting.repeated_permutation_digits | ???????tc_rep_perm_digits_01? | ? | ????? Phase 2A/3 ?????????????? |

## 6. ?????
- b4.combination.combination_definition_basic: [('combination_definition_basic', 6, 2), ('combination_definition_basic', 5, 2), ('combination_definition_basic', 6, 2), ('combination_definition_basic', 6, 3), ('combination_definition_basic', 7, 3)]
  - ??: ?
- b4.permutation.permutation_role_assignment: [('permutation_role_assignment', 6, 2), ('permutation_role_assignment', 5, 2), ('permutation_role_assignment', 6, 2), ('permutation_role_assignment', 6, 3), ('permutation_role_assignment', 7, 3)]
  - ??: ?
- b4.counting.repeated_permutation_digits: [('repeated_permutation_digits', 3, 2), ('repeated_permutation_digits', 3, 2), ('repeated_permutation_digits', 3, 2), ('repeated_permutation_digits', 3, 3), ('repeated_permutation_digits', 5, 3)]
  - ??: ?

## 7. ?????
- ?? 15 ?????????????????

## 8. ??
- ?? generator ? seed 1~5 ???????????????
- choices ???answer ? choices ??placeholder ??????
- ?????????????? generator ???????
- ????????????????????????
- ????????????? seed ??????