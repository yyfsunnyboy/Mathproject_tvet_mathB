# B4 Phase 4E Postcheck-D1 Router Distribution Sampling Audit

## 1. 本階段目的

本階段以 deterministic sampling 觀察 `question_router` 的 default selection 行為。

本階段不修改程式、不改 selection policy、不改 generator、不改前端、不改 route、不改 coverage matrix。目標是分辨使用者觀察到的單調感來自 router distribution、generator template enrichment 需求，或 skill 本身 narrow。

## 2. 抽樣方法

抽樣對象：

- `vh_數學B4_RepeatedPermutation`
- `vh_數學B4_CombinationDefinition`
- `vh_數學B4_BinomialTheorem`
- `vh_數學B4_BinomialCoefficientIdentities`
- `vh_數學B4_PermutationOfNonDistinctObjects`
- `vh_數學B4_PermutationOfDistinctObjects`

抽樣設定：

- 呼叫 `generate_for_skill(skill_id=..., level=1, seed=seed)`
- seed 範圍：1 到 30
- 不指定 `problem_type_id`
- 記錄欄位：seed、problem_type_id、generator_key、subskill_id、parameter_tuple、question_text 前 80 字、answer、router_trace
- 若單一 seed 產生錯誤，記錄 error 並繼續

補充：

- 本階段第一次抽樣命令因 PowerShell 到 Python 的非 ASCII 轉碼造成 `數學` 被轉為 `??`，該次結果全部為 `Unsupported skill_id`，已排除。
- 正式抽樣使用 Unicode code point 組出 `vh_數學B4_*` skill_id。

## 3. 總體統計表

| skill_id | samples | error_count | unique_problem_type_count | unique_parameter_tuple_count | dominant_problem_type | dominant_count | 初步分類 |
|---|---:|---:|---:|---:|---|---:|---|
| `vh_數學B4_RepeatedPermutation` | 30 | 0 | 1 | 6 | `repeated_permutation_digits` | 30 | single_problem_type |
| `vh_數學B4_CombinationDefinition` | 30 | 0 | 1 | 8 | `combination_definition_basic` | 30 | narrow_skill |
| `vh_數學B4_BinomialTheorem` | 30 | 0 | 3 | 25 | `binomial_specific_term_coefficient` / `binomial_specific_coefficient_with_negative_term` | 11 | ok_distribution |
| `vh_數學B4_BinomialCoefficientIdentities` | 30 | 0 | 3 | 22 | `binomial_coefficient_sum` / `binomial_odd_even_coefficient_sum` | 11 | ok_distribution |
| `vh_數學B4_PermutationOfNonDistinctObjects` | 30 | 0 | 1 | 6 | `repeated_permutation_digits` | 30 | mapping_surrogate |
| `vh_數學B4_PermutationOfDistinctObjects` | 30 | 0 | 5 | 20 | `permutation_formula_evaluation` | 10 | ok_distribution |

所有有效樣本之 `answer` 皆為 `int`。所有有效樣本之 `router_trace.selected_problem_type_id` 皆可對應 payload 的 `problem_type_id`。

## 4. 各 skill problem_type 分布

### 4.1 `vh_數學B4_RepeatedPermutation`

| problem_type_id | generator_key | count | percentage |
|---|---|---:|---:|
| `repeated_permutation_digits` | `b4.counting.repeated_permutation_digits` | 30 | 100.0% |

Seed 摘要：

| seed | problem_type_id | parameter_tuple | question_preview |
|---:|---|---|---|
| 1 | `repeated_permutation_digits` | `('repeated_permutation_digits', 3, 2)` | 有 3 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？ |
| 2 | `repeated_permutation_digits` | `('repeated_permutation_digits', 3, 2)` | 有 3 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？ |
| 3 | `repeated_permutation_digits` | `('repeated_permutation_digits', 3, 2)` | 有 3 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？ |
| 4 | `repeated_permutation_digits` | `('repeated_permutation_digits', 3, 3)` | 有 3 個可用數字，每個數字可重複使用，排成 3 位數，共有多少種排法？ |
| 5 | `repeated_permutation_digits` | `('repeated_permutation_digits', 5, 3)` | 有 5 個可用數字，每個數字可重複使用，排成 3 位數，共有多少種排法？ |
| 6 | `repeated_permutation_digits` | `('repeated_permutation_digits', 5, 2)` | 有 5 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？ |
| 7 | `repeated_permutation_digits` | `('repeated_permutation_digits', 4, 2)` | 有 4 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？ |
| 8 | `repeated_permutation_digits` | `('repeated_permutation_digits', 3, 3)` | 有 3 個可用數字，每個數字可重複使用，排成 3 位數，共有多少種排法？ |
| 9 | `repeated_permutation_digits` | `('repeated_permutation_digits', 4, 3)` | 有 4 個可用數字，每個數字可重複使用，排成 3 位數，共有多少種排法？ |
| 10 | `repeated_permutation_digits` | `('repeated_permutation_digits', 5, 2)` | 有 5 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？ |

完整 30 seeds 統計均為 `repeated_permutation_digits`。

### 4.2 `vh_數學B4_CombinationDefinition`

| problem_type_id | generator_key | count | percentage |
|---|---|---:|---:|
| `combination_definition_basic` | `b4.combination.combination_definition_basic` | 30 | 100.0% |

Seed 摘要：

| seed | problem_type_id | parameter_tuple | question_preview |
|---:|---|---|---|
| 1 | `combination_definition_basic` | `('combination_definition_basic', 6, 2)` | 從 6 件不同作品中選出 2 件展示，共有多少種選法？ |
| 2 | `combination_definition_basic` | `('combination_definition_basic', 5, 2)` | 從 5 件不同作品中選出 2 件展示，共有多少種選法？ |
| 3 | `combination_definition_basic` | `('combination_definition_basic', 6, 2)` | 從 6 件不同作品中選出 2 件展示，共有多少種選法？ |
| 4 | `combination_definition_basic` | `('combination_definition_basic', 6, 3)` | 從 6 件不同作品中選出 3 件展示，共有多少種選法？ |
| 5 | `combination_definition_basic` | `('combination_definition_basic', 7, 3)` | 從 7 件不同作品中選出 3 件展示，共有多少種選法？ |
| 6 | `combination_definition_basic` | `('combination_definition_basic', 5, 3)` | 從 5 件不同作品中選出 3 件展示，共有多少種選法？ |
| 7 | `combination_definition_basic` | `('combination_definition_basic', 7, 2)` | 從 7 件不同作品中選出 2 件展示，共有多少種選法？ |
| 8 | `combination_definition_basic` | `('combination_definition_basic', 6, 3)` | 從 6 件不同作品中選出 3 件展示，共有多少種選法？ |
| 9 | `combination_definition_basic` | `('combination_definition_basic', 8, 3)` | 從 8 件不同作品中選出 3 件展示，共有多少種選法？ |
| 10 | `combination_definition_basic` | `('combination_definition_basic', 5, 3)` | 從 5 件不同作品中選出 3 件展示，共有多少種選法？ |

完整 30 seeds 統計均為 `combination_definition_basic`。

### 4.3 `vh_數學B4_BinomialTheorem`

| problem_type_id | generator_key | count | percentage |
|---|---|---:|---:|
| `binomial_specific_term_coefficient` | `b4.binomial.binomial_specific_term_coefficient` | 11 | 36.7% |
| `binomial_specific_coefficient_with_negative_term` | `b4.binomial.binomial_specific_coefficient_with_negative_term` | 11 | 36.7% |
| `binomial_middle_term_coefficient` | `b4.binomial.binomial_middle_term_coefficient` | 8 | 26.7% |

Seed 摘要：

| seed | problem_type_id | parameter_tuple | question_preview |
|---:|---|---|---|
| 1 | `binomial_specific_term_coefficient` | `('binomial_specific_term_coefficient', 1, 1, 2, 1)` | 展開 $(x+1)^{2}$ 後，$x^{1}$ 項係數為多少？ |
| 2 | `binomial_specific_term_coefficient` | `('binomial_specific_term_coefficient', 1, 2, 3, 2)` | 展開 $(x+2)^{3}$ 後，$x^{2}$ 項係數為多少？ |
| 3 | `binomial_specific_term_coefficient` | `('binomial_specific_term_coefficient', 1, 3, 4, 0)` | 展開 $(x+3)^{4}$ 後，常數項係數為多少？ |
| 4 | `binomial_specific_term_coefficient` | `('binomial_specific_term_coefficient', 1, 4, 5, 3)` | 展開 $(x+4)^{5}$ 後，$x^{3}$ 項係數為多少？ |
| 5 | `binomial_specific_coefficient_with_negative_term` | `('binomial_specific_coefficient_with_negative_term', 1, -2, 5, 5)` | 展開 $(x-2)^{5}$ 後，$x^{5}$ 項係數為多少？ |
| 6 | `binomial_specific_coefficient_with_negative_term` | `('binomial_specific_coefficient_with_negative_term', 1, -4, 5, 2)` | 展開 $(x-4)^{5}$ 後，$x^{2}$ 項係數為多少？ |
| 7 | `binomial_middle_term_coefficient` | `('binomial_middle_term_coefficient', 1, 3, 2)` | 展開 $(x+3)^{2}$ 後，中間項係數為多少？ |
| 8 | `binomial_specific_term_coefficient` | `('binomial_specific_term_coefficient', 1, 2, 4, 3)` | 展開 $(x+2)^{4}$ 後，$x^{3}$ 項係數為多少？ |
| 9 | `binomial_middle_term_coefficient` | `('binomial_middle_term_coefficient', 1, 4, 6)` | 展開 $(x+4)^{6}$ 後，中間項係數為多少？ |
| 10 | `binomial_specific_coefficient_with_negative_term` | `('binomial_specific_coefficient_with_negative_term', 1, -4, 5, 3)` | 展開 $(x-4)^{5}$ 後，$x^{3}$ 項係數為多少？ |

完整 30 seeds 均成功，三種 problem_type 均有出現。

### 4.4 `vh_數學B4_BinomialCoefficientIdentities`

| problem_type_id | generator_key | count | percentage |
|---|---|---:|---:|
| `binomial_coefficient_sum` | `b4.binomial.binomial_coefficient_sum` | 11 | 36.7% |
| `binomial_odd_even_coefficient_sum` | `b4.binomial.binomial_odd_even_coefficient_sum` | 11 | 36.7% |
| `binomial_equation_solve_n` | `b4.binomial.binomial_equation_solve_n` | 8 | 26.7% |

Seed 摘要：

| seed | problem_type_id | parameter_tuple | question_preview |
|---:|---|---|---|
| 1 | `binomial_coefficient_sum` | `('binomial_coefficient_sum', 1, 1, 2)` | 展開 $(x+1)^{2}$ 後，所有係數和為多少？ |
| 2 | `binomial_coefficient_sum` | `('binomial_coefficient_sum', 1, 2, 3)` | 展開 $(x+2)^{3}$ 後，所有係數和為多少？ |
| 3 | `binomial_coefficient_sum` | `('binomial_coefficient_sum', 1, 3, 4)` | 展開 $(x+3)^{4}$ 後，所有係數和為多少？ |
| 4 | `binomial_coefficient_sum` | `('binomial_coefficient_sum', 1, 4, 5)` | 展開 $(x+4)^{5}$ 後，所有係數和為多少？ |
| 5 | `binomial_odd_even_coefficient_sum` | `('binomial_odd_even_coefficient_sum', 1, 2, 5, 'odd')` | 展開 $(x+2)^{5}$ 後，奇數次項係數和為多少？ |
| 6 | `binomial_odd_even_coefficient_sum` | `('binomial_odd_even_coefficient_sum', 1, 1, 5, 'even')` | 展開 $(x+1)^{5}$ 後，偶數次項係數和為多少？ |
| 7 | `binomial_equation_solve_n` | `('binomial_equation_solve_n', 5, 2, 10, 'r2')` | 若 $C^{n}_{2}=10$，求正整數 $n$。 |
| 8 | `binomial_coefficient_sum` | `('binomial_coefficient_sum', 1, 2, 4)` | 展開 $(x+2)^{4}$ 後，所有係數和為多少？ |
| 9 | `binomial_equation_solve_n` | `('binomial_equation_solve_n', 8, 2, 28, 'r2')` | 若 $C^{n}_{2}=28$，求正整數 $n$。 |
| 10 | `binomial_odd_even_coefficient_sum` | `('binomial_odd_even_coefficient_sum', 1, 1, 5, 'even')` | 展開 $(x+1)^{5}$ 後，偶數次項係數和為多少？ |

完整 30 seeds 均成功，三種 problem_type 均有出現。

### 4.5 `vh_數學B4_PermutationOfNonDistinctObjects`

| problem_type_id | generator_key | count | percentage |
|---|---|---:|---:|
| `repeated_permutation_digits` | `b4.counting.repeated_permutation_digits` | 30 | 100.0% |

Seed 摘要：

| seed | problem_type_id | parameter_tuple | question_preview |
|---:|---|---|---|
| 1 | `repeated_permutation_digits` | `('repeated_permutation_digits', 3, 2)` | 有 3 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？ |
| 2 | `repeated_permutation_digits` | `('repeated_permutation_digits', 3, 2)` | 有 3 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？ |
| 3 | `repeated_permutation_digits` | `('repeated_permutation_digits', 3, 2)` | 有 3 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？ |
| 4 | `repeated_permutation_digits` | `('repeated_permutation_digits', 3, 3)` | 有 3 個可用數字，每個數字可重複使用，排成 3 位數，共有多少種排法？ |
| 5 | `repeated_permutation_digits` | `('repeated_permutation_digits', 5, 3)` | 有 5 個可用數字，每個數字可重複使用，排成 3 位數，共有多少種排法？ |
| 6 | `repeated_permutation_digits` | `('repeated_permutation_digits', 5, 2)` | 有 5 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？ |
| 7 | `repeated_permutation_digits` | `('repeated_permutation_digits', 4, 2)` | 有 4 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？ |
| 8 | `repeated_permutation_digits` | `('repeated_permutation_digits', 3, 3)` | 有 3 個可用數字，每個數字可重複使用，排成 3 位數，共有多少種排法？ |
| 9 | `repeated_permutation_digits` | `('repeated_permutation_digits', 4, 3)` | 有 4 個可用數字，每個數字可重複使用，排成 3 位數，共有多少種排法？ |
| 10 | `repeated_permutation_digits` | `('repeated_permutation_digits', 5, 2)` | 有 5 個可用數字，每個數字可重複使用，排成 2 位數，共有多少種排法？ |

完整 30 seeds 統計均為 `repeated_permutation_digits`。

### 4.6 `vh_數學B4_PermutationOfDistinctObjects`

| problem_type_id | generator_key | count | percentage |
|---|---|---:|---:|
| `permutation_formula_evaluation` | `b4.permutation.permutation_formula_evaluation` | 10 | 33.3% |
| `permutation_digit_parity` | `b4.permutation.permutation_digit_parity` | 6 | 20.0% |
| `permutation_adjacent_block` | `b4.permutation.permutation_adjacent_block` | 6 | 20.0% |
| `permutation_role_assignment` | `b4.permutation.permutation_role_assignment` | 4 | 13.3% |
| `permutation_full_arrangement` | `b4.permutation.permutation_full_arrangement` | 4 | 13.3% |

Seed 摘要：

| seed | problem_type_id | parameter_tuple | question_preview |
|---:|---|---|---|
| 1 | `permutation_formula_evaluation` | `('permutation_formula_evaluation', 5, 4, 'arrange')` | 從 5 個不同物件中取出 4 個排成一列，共有多少種排法？ |
| 2 | `permutation_role_assignment` | `('permutation_role_assignment', 5, 2)` | 從 5 位同學中選出 2 位分別擔任不同職務，共有多少種安排方式？ |
| 3 | `permutation_formula_evaluation` | `('permutation_formula_evaluation', 6, 3, 'arrange')` | 從 6 個不同物件中取出 3 個排成一列，共有多少種排法？ |
| 4 | `permutation_formula_evaluation` | `('permutation_formula_evaluation', 8, 4, 'arrange')` | 從 8 個不同物件中取出 4 個排成一列，共有多少種排法？ |
| 5 | `permutation_digit_parity` | `('permutation_digit_parity', 7, 3, True, 'odd_number')` | 使用 0、1、2、3、4、5、6 共 7 個數字，組成不重複的 3 位奇數 |
| 6 | `permutation_digit_parity` | `('permutation_digit_parity', 7, 2, False, 'even_number')` | 使用 1、2、3、4、5、6、7 共 7 個數字，組成不重複的 2 位偶數 |
| 7 | `permutation_full_arrangement` | `('permutation_full_arrangement', 5, 'books_shelf')` | 5 本不同書排在書架上，共有多少種排法？ |
| 8 | `permutation_formula_evaluation` | `('permutation_formula_evaluation', 7, 3, 'arrange')` | 從 7 個不同物件中取出 3 個排成一列，共有多少種排法？ |
| 9 | `permutation_adjacent_block` | `('permutation_adjacent_block', 6, 2, 'photos_row')` | 6 張不同照片排成一排，若指定 2 張必須相鄰，共有多少種排法？ |
| 10 | `permutation_digit_parity` | `('permutation_digit_parity', 7, 2, False, 'even_number')` | 使用 1、2、3、4、5、6、7 共 7 個數字，組成不重複的 2 位偶數 |

完整 30 seeds 均成功，五種 problem_type 均有出現。

## 5. 特別判斷

### `vh_數學B4_RepeatedPermutation`

- Router distribution 問題：否。此 skill 只有一筆 router entry。
- Generator template 問題：是。30 seeds 都是同一個 problem_type，且題幹語境固定為可用數字重複排列。
- Skill narrow：是，至少目前 router 定義上是窄技能。
- 下一階段修正：D3 template enrichment，不一定要改 router。

### `vh_數學B4_CombinationDefinition`

- Router distribution 問題：否。此 skill 只有一筆 router entry。
- Generator template 問題：是，題幹固定為作品選展示語境。
- Skill narrow：是。`combination_definition_basic` 可接受為基礎技能頁。
- 下一階段修正：若要改善體感，做 D3 template enrichment；不一定要擴 router。

### `vh_數學B4_BinomialTheorem`

- Router distribution 問題：未發現硬性問題。30 seeds 內三個 problem_type 都有出現。
- 出現分布：11 / 11 / 8，沒有缺漏。
- Generator template 問題：可能。三類題都以「展開後某項係數」呈現，使用者可能感覺相近。
- 下一階段修正：若仍覺體感不足，優先做 template enrichment 或 debug visibility；不得以接入 `binomial_expansion_basic` 作為解法。

### `vh_數學B4_BinomialCoefficientIdentities`

- Router distribution 問題：未發現硬性問題。30 seeds 內三個 problem_type 都有出現。
- 出現分布：11 / 11 / 8，沒有缺漏。
- Generator template 問題：可能，尤其 UI 不顯示 problem_type 時，使用者不易感知題型覆蓋。
- 下一階段修正：可改善 problem_type visibility 或做 template enrichment；目前不需要立即改 router selection policy。

### `vh_數學B4_PermutationOfNonDistinctObjects`

- Router distribution 問題：否。此 skill 目前只有一筆 router entry。
- Mapping surrogate：是。Postcheck-C 目前重用 `repeated_permutation_digits`。
- Generator template 問題：是，與 `RepeatedPermutation` 同樣固定為可用數字重複排列。
- 下一階段修正：D2 決定是否新增真正「不盡相異物排列」word problem generator，或文件化保留為 repeated-permutation surrogate page。

### `vh_數學B4_PermutationOfDistinctObjects`

- Router distribution 問題：未發現硬性問題。30 seeds 內五個 problem_type 都有出現。
- 出現分布：10 / 6 / 6 / 4 / 4，`permutation_formula_evaluation` 較高，但 30 samples 下仍屬可接受觀察，不宜直接判定為 failure。
- Generator template 問題：部分題型仍可 enrichment，但不是優先項。
- 下一階段修正：不優先處理；若未來要求嚴格均勻，可再檢討 seed-based rotation。

## 6. 主要發現

1. `RepeatedPermutation` 30 seeds 全部為 `repeated_permutation_digits`，原因是 single router entry。
2. `CombinationDefinition` 30 seeds 全部為 `combination_definition_basic`，原因是 narrow skill / single router entry。
3. `PermutationOfNonDistinctObjects` 30 seeds 全部為 `repeated_permutation_digits`，符合 Postcheck-C 的 mapping surrogate 設計。
4. `BinomialTheorem` 三個 problem_type 在 30 seeds 內全數出現，分布為 11 / 11 / 8。
5. `BinomialCoefficientIdentities` 三個 problem_type 在 30 seeds 內全數出現，分布為 11 / 11 / 8。
6. `PermutationOfDistinctObjects` 五個 problem_type 在 30 seeds 內全數出現，沒有缺漏。
7. 本次沒有任何有效 skill / seed 產生 runtime error。
8. 所有有效樣本的 answer 都是 int，符合 deterministic int-answer runtime。
9. `router_trace` 已能看出 chosen problem_type，但前端/一般頁面不一定顯示，造成使用者不易感知 depth 題型。
10. 目前單調問題主要不是 closure failure，也不是 generator 無法產題，而是 single entry、mapping surrogate、template similarity 與 debug visibility 問題。

## 7. 下一步建議

1. 若 BinomialTheorem / BinomialCoefficientIdentities 分布不足：
   - 本次 sampling 未顯示明顯不足；三種 problem_type 都有出現。
   - 暫不建議立即做 Phase 4E-Postcheck-D1-Fix。
   - 若未來要求嚴格平均，可再開 router default selection review，考慮 seed-based rotation 或 uniform problem_type selection。

2. 若 RepeatedPermutation / CombinationDefinition 只有單一 problem_type：
   - 建議 Phase 4E-Postcheck-D3：template enrichment。
   - 不一定要改 router。
   - `CombinationDefinition` 可接受為基礎技能頁，但可增加題幹語境。

3. 若 PermutationOfNonDistinctObjects 只有 `repeated_permutation_digits`：
   - 建議 Phase 4E-Postcheck-D2：non-distinct permutation enrichment decision。
   - 決定是否新增真正「不盡相異物排列」word problem generator。
   - 或明確保留為 repeated_permutation_digits wrapper page。

4. 若 PermutationOfDistinctObjects 分布正常：
   - 本次五類 problem_type 均有出現，不優先處理。
   - 若後續教師 QA 要求可觀測性，可考慮 debug 顯示 router_trace。

## 8. 結論

- 本次 sampling 確認單調問題來源大多可定位。
- `RepeatedPermutation` 是 single_problem_type 與 template enrichment 問題。
- `CombinationDefinition` 是 narrow skill 與 template enrichment 問題。
- `PermutationOfNonDistinctObjects` 是 mapping_surrogate，後續需 D2 決策是否建立真正不盡相異物排列題型。
- `BinomialTheorem`、`BinomialCoefficientIdentities`、`PermutationOfDistinctObjects` 在 seed 1-30 內都有抽到所有已掛 problem_type，未見硬性 router distribution failure。
- 下一步建議優先 D2 處理 `PermutationOfNonDistinctObjects` 語義決策，並以 D3 做小批 template enrichment。
