# B4 Phase 4E-8 Generator 樣題品質檢查報告

## 1. 本階段目的
本階段只檢查 Phase 4E-8 generator 樣題，不修改程式、不接 router、不建 wrapper、不接前端。

## 2. 檢查範圍

| generator_key | function | skill_id | subskill_id | multiple_choice |
|---|---|---|---|---|
| b4.combination.combination_basic_selection | combination_basic_selection | vh_數學B4_Combination | b4_ch1_comb_basic_selection_01 | True |
| b4.permutation.permutation_formula_evaluation | permutation_formula_evaluation | vh_數學B4_PermutationOfDistinctObjects | b4_ch1_perm_formula_eval_01 | True |
| b4.counting.factorial_evaluation | factorial_evaluation | vh_數學B4_FactorialNotation | b4_ch1_factorial_eval_01 | True |

## 3. 總體檢查表

| generator_key | 樣題數 | unique_parameter_tuple 數 | choices_valid | answer_valid | latex_valid | metadata_complete | placeholder_free | 初步判斷 |
|---|---:|---:|---|---|---|---|---|---|
| b4.combination.combination_basic_selection | 5 | 5 | Yes | Yes | Yes | Yes | Yes | 通過 |
| b4.permutation.permutation_formula_evaluation | 5 | 5 | Yes | Yes | Yes | Yes | Yes | 通過 |
| b4.counting.factorial_evaluation | 5 | 5 | Yes | Yes | Yes | Yes | Yes | 通過 |

## 4. 樣題清單

### b4.combination.combination_basic_selection

#### seed = 1
- question_text: 從 8 本不同的書中選出 4 本，共有多少種選法？
- choices: [68, 70, 35, 69]
- answer: 70
- explanation: 不考慮順序，使用 $C^{n}_{r}=\frac{n!}{r!(n-r)!}$，所以 $C^{8}_{4}=70$。
- parameters: {'n': 8, 'r': 4, 'context': 'books', 'parameter_tuple': ['combination_basic_selection', 8, 4, 'books']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 2
- question_text: 從 8 件不同禮物中選出 3 件，共有多少種選法？
- choices: [112, 56, 54, 55]
- answer: 56
- explanation: 不考慮順序，使用 $C^{n}_{r}=\frac{n!}{r!(n-r)!}$，所以 $C^{8}_{3}=56$。
- parameters: {'n': 8, 'r': 3, 'context': 'gifts', 'parameter_tuple': ['combination_basic_selection', 8, 3, 'gifts']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 3
- question_text: 從 9 位同學中選出 3 位，共有多少種選法？
- choices: [168, 82, 84, 42]
- answer: 84
- explanation: 不考慮順序，使用 $C^{n}_{r}=\frac{n!}{r!(n-r)!}$，所以 $C^{9}_{3}=84$。
- parameters: {'n': 9, 'r': 3, 'context': 'students', 'parameter_tuple': ['combination_basic_selection', 9, 3, 'students']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 4
- question_text: 從 6 題中選出 2 題作答，共有多少種選法？
- choices: [7, 14, 15, 13]
- answer: 15
- explanation: 不考慮順序，使用 $C^{n}_{r}=\frac{n!}{r!(n-r)!}$，所以 $C^{6}_{2}=15$。
- parameters: {'n': 6, 'r': 2, 'context': 'questions', 'parameter_tuple': ['combination_basic_selection', 6, 2, 'questions']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 5
- question_text: 從 8 位同學中選出 3 位，共有多少種選法？
- choices: [54, 55, 112, 56]
- answer: 56
- explanation: 不考慮順序，使用 $C^{n}_{r}=\frac{n!}{r!(n-r)!}$，所以 $C^{8}_{3}=56$。
- parameters: {'n': 8, 'r': 3, 'context': 'students', 'parameter_tuple': ['combination_basic_selection', 8, 3, 'students']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

### b4.permutation.permutation_formula_evaluation

#### seed = 1
- question_text: 從 5 個不同物件中取出 4 個排成一列，共有多少種排法？
- choices: [240, 120, 119, 118]
- answer: 120
- explanation: 使用 $P^{n}_{r}=\frac{n!}{(n-r)!}$，所以 $P^{5}_{4}=120$。
- parameters: {'n': 5, 'r': 4, 'variant': 'arrange', 'parameter_tuple': ['permutation_formula_evaluation', 5, 4, 'arrange']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 2
- question_text: 計算排列數 $P^{9}_{2}$ 的值。
- choices: [71, 70, 72, 36]
- answer: 72
- explanation: 使用 $P^{n}_{r}=\frac{n!}{(n-r)!}$，所以 $P^{9}_{2}=72$。
- parameters: {'n': 9, 'r': 2, 'variant': 'symbolic', 'parameter_tuple': ['permutation_formula_evaluation', 9, 2, 'symbolic']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 3
- question_text: 從 6 個不同物件中取出 3 個排成一列，共有多少種排法？
- choices: [120, 119, 240, 118]
- answer: 120
- explanation: 使用 $P^{n}_{r}=\frac{n!}{(n-r)!}$，所以 $P^{6}_{3}=120$。
- parameters: {'n': 6, 'r': 3, 'variant': 'arrange', 'parameter_tuple': ['permutation_formula_evaluation', 6, 3, 'arrange']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 4
- question_text: 從 8 個不同物件中取出 4 個排成一列，共有多少種排法？
- choices: [1678, 1680, 840, 3360]
- answer: 1680
- explanation: 使用 $P^{n}_{r}=\frac{n!}{(n-r)!}$，所以 $P^{8}_{4}=1680$。
- parameters: {'n': 8, 'r': 4, 'variant': 'arrange', 'parameter_tuple': ['permutation_formula_evaluation', 8, 4, 'arrange']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 5
- question_text: 從 9 個不同物件中取出 2 個排成一列，共有多少種排法？
- choices: [36, 71, 70, 72]
- answer: 72
- explanation: 使用 $P^{n}_{r}=\frac{n!}{(n-r)!}$，所以 $P^{9}_{2}=72$。
- parameters: {'n': 9, 'r': 2, 'variant': 'arrange', 'parameter_tuple': ['permutation_formula_evaluation', 9, 2, 'arrange']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

### b4.counting.factorial_evaluation

#### seed = 1
- question_text: 計算 $3!$ 的值。
- choices: [4, 5, 3, 6]
- answer: 6
- explanation: $3!=3 \times 2 \times 1=6$。
- parameters: {'n': 3, 'k': 0, 'variant': 'direct', 'parameter_tuple': ['factorial_evaluation', 3, 0, 'direct']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 2
- question_text: 計算 $\frac{5!}{3!}$ 的值。
- choices: [20, 10, 18, 40]
- answer: 20
- explanation: $\frac{5!}{3!}=5 \times 4=20$。
- parameters: {'n': 5, 'k': 2, 'variant': 'ratio', 'parameter_tuple': ['factorial_evaluation', 5, 2, 'ratio']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 3
- question_text: 計算 $6!$ 的值。
- choices: [360, 718, 1440, 720]
- answer: 720
- explanation: $6!=6 \times 5 \times 4 \times 3 \times 2 \times 1=720$。
- parameters: {'n': 6, 'k': 0, 'variant': 'direct', 'parameter_tuple': ['factorial_evaluation', 6, 0, 'direct']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 4
- question_text: 計算 $\frac{7!}{6!}$ 的值。
- choices: [5, 6, 7, 3]
- answer: 7
- explanation: $\frac{7!}{6!}=7=7$。
- parameters: {'n': 7, 'k': 1, 'variant': 'ratio', 'parameter_tuple': ['factorial_evaluation', 7, 1, 'ratio']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 5
- question_text: 計算 $4!$ 的值。
- choices: [24, 12, 22, 48]
- answer: 24
- explanation: $4!=4 \times 3 \times 2 \times 1=24$。
- parameters: {'n': 4, 'k': 0, 'variant': 'direct', 'parameter_tuple': ['factorial_evaluation', 4, 0, 'direct']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

## 5. parameter_tuple 重複性檢查

### b4.combination.combination_basic_selection
- seed 1: ['combination_basic_selection', 8, 4, 'books']
- seed 2: ['combination_basic_selection', 8, 3, 'gifts']
- seed 3: ['combination_basic_selection', 9, 3, 'students']
- seed 4: ['combination_basic_selection', 6, 2, 'questions']
- seed 5: ['combination_basic_selection', 8, 3, 'students']

### b4.permutation.permutation_formula_evaluation
- seed 1: ['permutation_formula_evaluation', 5, 4, 'arrange']
- seed 2: ['permutation_formula_evaluation', 9, 2, 'symbolic']
- seed 3: ['permutation_formula_evaluation', 6, 3, 'arrange']
- seed 4: ['permutation_formula_evaluation', 8, 4, 'arrange']
- seed 5: ['permutation_formula_evaluation', 9, 2, 'arrange']

### b4.counting.factorial_evaluation
- seed 1: ['factorial_evaluation', 3, 0, 'direct']
- seed 2: ['factorial_evaluation', 5, 2, 'ratio']
- seed 3: ['factorial_evaluation', 6, 0, 'direct']
- seed 4: ['factorial_evaluation', 7, 1, 'ratio']
- seed 5: ['factorial_evaluation', 4, 0, 'direct']

## 6. 與課本題型相似度人工檢查建議

| generator_key | 對應課本題型 | 相似度判斷 | 需要人工注意的點 |
|---|---|---|---|
| b4.combination.combination_basic_selection | 組合基本定義/單純選取 | 高 | 若與 combination_definition_basic 太相似，請註記 |
| b4.permutation.permutation_formula_evaluation | 排列公式代入求值 | 高 | 若只做公式代入，註記是否需要未來增加情境題 |
| b4.counting.factorial_evaluation | 階乘計算/化簡 | 高 | - |

## 7. 問題與建議

- b4.combination.combination_basic_selection：若與 combination_definition_basic 太相似，建議後續可由題幹情境作區分。
- b4.permutation.permutation_formula_evaluation：若只做公式代入，請註記是否需要未來增加情境題。
- b4.counting.factorial_evaluation：若 seed 1～5 使用固定代表參數，為避免前 5 seed 重複而固定代表參數，不影響其他 seed 抽樣。

## 8. 結論

- generators 皆能產出 5 題樣題。
- 品質通過自動檢查，可進下一階段，若需微調再針對性修改。
- 是否可接入 question_router / wrapper：是。
- 是否需要人工確認：是，特別是情境題與課本的相似度。