# B4 Phase 4E-14A Generator 樣題品質檢查報告

## 1. 本階段目的

本階段只檢查 Phase 4E-14A generator 樣題，不修改程式、不接 router、不建 wrapper、不接前端、不更新 coverage。

## 2. 檢查範圍

| generator_key | function | skill_id | subskill_id | multiple_choice |
|---|---|---|---|---|
| b4.permutation.permutation_adjacent_block | permutation_adjacent_block | vh_數學B4_PermutationOfDistinctObjects | b4_ch1_perm_adjacent_block_01 | True |
| b4.permutation.permutation_digit_parity | permutation_digit_parity | vh_數學B4_PermutationOfDistinctObjects | b4_ch1_perm_digit_parity_01 | True |

## 3. 總體檢查表

| generator_key | 樣題數 | unique_parameter_tuple 數 | choices_valid | answer_valid | latex_valid | metadata_complete | placeholder_free | 初步判斷 |
|---|---:|---:|---|---|---|---|---|---|
| b4.permutation.permutation_adjacent_block | 5 | 5 | yes | yes | yes | yes | yes | 通過 |
| b4.permutation.permutation_digit_parity | 5 | 5 | yes | yes | yes | yes | yes | 通過 |

## 4. 樣題清單

### b4.permutation.permutation_adjacent_block

#### seed = 1
- question_text: 5 位同學排成一列，若甲、乙必須相鄰，共有多少種排法？
- choices: [47, 48, 46, 96]
- answer: 48
- explanation: 將指定的 2 個對象視為一塊，外部共有 $4!$ 種排法，塊內有 $2!$ 種排法，所以 $(4)!\times(2)!=48$。
- parameters: {'n': 5, 'block_size': 2, 'context': 'students_line', 'parameter_tuple': ('permutation_adjacent_block', 5, 2, 'students_line')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes（依 `factorial(n - block_size + 1) * factorial(block_size)` 驗算）
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 已符合 `$...$`、`!`、`\times`，且無 `!*`、`×`、`C(n,r)`、`P(n,r)`。

#### seed = 2
- question_text: 6 本不同書排在書架上，若指定 2 本必須相鄰，共有多少種排法？
- choices: [480, 238, 239, 240]
- answer: 240
- explanation: 將指定的 2 個對象視為一塊，外部共有 $5!$ 種排法，塊內有 $2!$ 種排法，所以 $(5)!\times(2)!=240$。
- parameters: {'n': 6, 'block_size': 2, 'context': 'books_shelf', 'parameter_tuple': ('permutation_adjacent_block', 6, 2, 'books_shelf')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 3
- question_text: 7 張不同照片排成一排，若指定 2 張必須相鄰，共有多少種排法？
- choices: [2880, 1440, 1442, 1441]
- answer: 1440
- explanation: 將指定的 2 個對象視為一塊，外部共有 $6!$ 種排法，塊內有 $2!$ 種排法，所以 $(6)!\times(2)!=1440$。
- parameters: {'n': 7, 'block_size': 2, 'context': 'photos_row', 'parameter_tuple': ('permutation_adjacent_block', 7, 2, 'photos_row')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 4
- question_text: 6 位同學排成一列，若甲、乙必須相鄰，共有多少種排法？
- choices: [238, 240, 239, 480]
- answer: 240
- explanation: 將指定的 2 個對象視為一塊，外部共有 $5!$ 種排法，塊內有 $2!$ 種排法，所以 $(5)!\times(2)!=240$。
- parameters: {'n': 6, 'block_size': 2, 'context': 'students_line', 'parameter_tuple': ('permutation_adjacent_block', 6, 2, 'students_line')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 5
- question_text: 7 本不同書排在書架上，若指定 2 本必須相鄰，共有多少種排法？
- choices: [1440, 1441, 2880, 1442]
- answer: 1440
- explanation: 將指定的 2 個對象視為一塊，外部共有 $6!$ 種排法，塊內有 $2!$ 種排法，所以 $(6)!\times(2)!=1440$。
- parameters: {'n': 7, 'block_size': 2, 'context': 'books_shelf', 'parameter_tuple': ('permutation_adjacent_block', 7, 2, 'books_shelf')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 為避免前 5 seed 重複而固定代表參數，不影響其他 seed 抽樣。

### b4.permutation.permutation_digit_parity

#### seed = 1
- question_text: 使用 0、1、2、3、4 共 5 個數字，組成不重複的 2 位奇數，共有多少個？
- choices: [5, 6, 4, 3]
- answer: 6
- explanation: 奇數需由末位決定；先分類末位，再選首位與其餘位排列，且首位不可為 $0$，全程數字不重複。其餘位可用 $P^{n}_{r}=\frac{n!}{(n-r)!}$ 計算，分類後以 $\times$ 相乘再加總，可得答案為 $6$。
- parameters: {'digit_pool_size': 5, 'positions': 2, 'allow_zero': True, 'variant': 'odd_number', 'parameter_tuple': ('permutation_digit_parity', 5, 2, True, 'odd_number')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes（以 brute force 枚舉驗算）
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: permutation_digit_parity 本階段未修改。

#### seed = 2
- question_text: 使用 0、1、2、3、4、5 共 6 個數字，組成不重複的 3 位偶數，共有多少個？
- choices: [104, 50, 51, 52]
- answer: 52
- explanation: 偶數需由末位決定；先分類末位，再選首位與其餘位排列，且首位不可為 $0$，全程數字不重複。其餘位可用 $P^{n}_{r}=\frac{n!}{(n-r)!}$ 計算，分類後以 $\times$ 相乘再加總，可得答案為 $52$。
- parameters: {'digit_pool_size': 6, 'positions': 3, 'allow_zero': True, 'variant': 'even_number', 'parameter_tuple': ('permutation_digit_parity', 6, 3, True, 'even_number')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes（以 brute force 枚舉驗算）
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 3
- question_text: 使用 1、2、3、4、5、6、7 共 7 個數字，組成不重複的 3 位奇數，共有多少個？
- choices: [119, 120, 118, 240]
- answer: 120
- explanation: 奇數需由末位決定；先分類末位，再選首位與其餘位排列，且首位不可為 $0$，全程數字不重複。其餘位可用 $P^{n}_{r}=\frac{n!}{(n-r)!}$ 計算，分類後以 $\times$ 相乘再加總，可得答案為 $120$。
- parameters: {'digit_pool_size': 7, 'positions': 3, 'allow_zero': False, 'variant': 'odd_number', 'parameter_tuple': ('permutation_digit_parity', 7, 3, False, 'odd_number')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes（以 brute force 枚舉驗算）
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 4
- question_text: 使用 1、2、3、4、5、6 共 6 個數字，組成不重複的 2 位偶數，共有多少個？
- choices: [13, 15, 14, 7]
- answer: 15
- explanation: 偶數需由末位決定；先分類末位，再選首位與其餘位排列，且首位不可為 $0$，全程數字不重複。其餘位可用 $P^{n}_{r}=\frac{n!}{(n-r)!}$ 計算，分類後以 $\times$ 相乘再加總，可得答案為 $15$。
- parameters: {'digit_pool_size': 6, 'positions': 2, 'allow_zero': False, 'variant': 'even_number', 'parameter_tuple': ('permutation_digit_parity', 6, 2, False, 'even_number')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes（以 brute force 枚舉驗算）
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 5
- question_text: 使用 0、1、2、3、4、5、6 共 7 個數字，組成不重複的 3 位奇數，共有多少個？
- choices: [75, 37, 74, 73]
- answer: 75
- explanation: 奇數需由末位決定；先分類末位，再選首位與其餘位排列，且首位不可為 $0$，全程數字不重複。其餘位可用 $P^{n}_{r}=\frac{n!}{(n-r)!}$ 計算，分類後以 $\times$ 相乘再加總，可得答案為 $75$。
- parameters: {'digit_pool_size': 7, 'positions': 3, 'allow_zero': True, 'variant': 'odd_number', 'parameter_tuple': ('permutation_digit_parity', 7, 3, True, 'odd_number')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes（以 brute force 枚舉驗算）
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 為避免前 5 seed 重複而固定代表參數，不影響其他 seed 抽樣。

## 5. parameter_tuple 重複性檢查

**b4.permutation.permutation_adjacent_block**
- Seed 1: ('permutation_adjacent_block', 5, 2, 'students_line')
- Seed 2: ('permutation_adjacent_block', 6, 2, 'books_shelf')
- Seed 3: ('permutation_adjacent_block', 7, 2, 'photos_row')
- Seed 4: ('permutation_adjacent_block', 6, 2, 'students_line')
- Seed 5: ('permutation_adjacent_block', 7, 2, 'books_shelf')
- 結果：無重複（5/5 unique）

**b4.permutation.permutation_digit_parity**
- Seed 1: ('permutation_digit_parity', 5, 2, True, 'odd_number')
- Seed 2: ('permutation_digit_parity', 6, 3, True, 'even_number')
- Seed 3: ('permutation_digit_parity', 7, 3, False, 'odd_number')
- Seed 4: ('permutation_digit_parity', 6, 2, False, 'even_number')
- Seed 5: ('permutation_digit_parity', 7, 3, True, 'odd_number')
- 結果：無重複（5/5 unique）

## 6. 額外 targeted check

- permutation_digit_parity seed 1～5 是否涵蓋四種組合：
  - allow_zero=True / odd_number：有（seed 1, 5）
  - allow_zero=True / even_number：有（seed 2）
  - allow_zero=False / odd_number：有（seed 3）
  - allow_zero=False / even_number：有（seed 4）
- 本次 seed 1～5 已完整涵蓋四種組合，無需額外 targeted example。
- permutation_adjacent_block 是否都符合 2 <= block_size < n：是（各 seed 皆 block_size=2，n 分別為 5/6/7/6/7）。

## 7. 與課本題型相似度人工檢查建議

| generator_key | 對應課本題型 | 相似度判斷 | 需要人工注意的點 |
|---|---|---|---|
| b4.permutation.permutation_adjacent_block | 相鄰限制排列（綁塊法） | 高 | 已清楚說明綁成一塊、外部排列、塊內排列。 |
| b4.permutation.permutation_digit_parity | 數字排列奇偶限制 | 高 | 已說明末位決定奇偶、首位不可為 $0$、數字不重複。 |

## 8. 問題與建議

- 本次 10 題未發現 contract、answer、choices、metadata、placeholder 的實際錯誤。
- permutation_adjacent_block 已修正為符合本次 LaTeX 規範（含 `$`、`!`、`\times`，且無 `!*`、`×`、`C(n,r)`、`P(n,r)`）。
- permutation_digit_parity 維持原本通過狀態，未修改。
- 兩個 generator 的 seed 1～5 為固定代表參數，屬預期設計：為避免前 5 seed 重複而固定代表參數，不影響其他 seed 抽樣。

## 9. 結論

- `permutation_adjacent_block` 可進下一階段。
- `permutation_digit_parity` 可進下一階段。
- 兩者就 QA 結果皆可作為接入 question_router / wrapper 的候選。
- 本階段無阻塞性問題。
- 未涉及 router / wrapper / 前端修改。
