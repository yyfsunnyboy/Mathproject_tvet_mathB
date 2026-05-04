# B4 Phase 4E-13B Generator 樣題品質檢查報告

## 1. 本階段目的

說明本階段只檢查 Phase 4E-13B generator 樣題，不修改程式、不接 router、不建 wrapper、不接前端。

## 2. 檢查範圍

| generator_key | function | skill_id | subskill_id | multiple_choice |
|---|---|---|---|---|
| b4.binomial.binomial_coefficient_sum | binomial_coefficient_sum | vh_數學B4_BinomialCoefficientIdentities | b4_ch1_binomial_coefficient_sum_01 | True |
| b4.binomial.binomial_specific_term_coefficient | binomial_specific_term_coefficient | vh_數學B4_BinomialTheorem | b4_ch1_binomial_specific_term_coefficient_01 | True |
| b4.binomial.binomial_equation_solve_n | binomial_equation_solve_n | vh_數學B4_BinomialCoefficientIdentities | b4_ch1_binomial_equation_solve_n_01 | True |

## 3. 總體檢查表

| generator_key | 樣題數 | unique_parameter_tuple 數 | choices_valid | answer_valid | latex_valid | metadata_complete | placeholder_free | 初步判斷 |
|---|---:|---:|---|---|---|---|---|---|
| b4.binomial.binomial_coefficient_sum | 5 | 5 | yes | yes | yes | yes | yes | 需微調 |
| b4.binomial.binomial_specific_term_coefficient | 5 | 5 | yes | yes | yes | yes | yes | 需微調 |
| b4.binomial.binomial_equation_solve_n | 5 | 5 | yes | yes | yes | yes | yes | 需微調 |

## 4. 樣題清單

### b4.binomial.binomial_coefficient_sum

#### seed = 1
- question_text: 展開 $(x+1)^{2}$ 後，所有係數和為多少？
- choices: [6, 4, 3, 5]
- answer: 4
- explanation: 係數和可令 $x=1$，所以 $(x+1)^{2}$ 的係數和為 $(1+1)^{2}=4$。
- parameters: {'a': 1, 'b': 1, 'n': 2, 'parameter_tuple': ['binomial_coefficient_sum', 1, 1, 2]}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 清楚說明了令 $x=1$。為避免前 5 seed 重複而固定代表參數，不影響其他 seed 抽樣。

#### seed = 2
- question_text: 展開 $(x+2)^{3}$ 後，所有係數和為多少？
- choices: [28, 26, 29, 27]
- answer: 27
- explanation: 係數和可令 $x=1$，所以 $(x+2)^{3}$ 的係數和為 $(1+2)^{3}=27$。
- parameters: {'a': 1, 'b': 2, 'n': 3, 'parameter_tuple': ['binomial_coefficient_sum', 1, 2, 3]}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 3
- question_text: 展開 $(x+3)^{4}$ 後，所有係數和為多少？
- choices: [258, 256, 255, 257]
- answer: 256
- explanation: 係數和可令 $x=1$，所以 $(x+3)^{4}$ 的係數和為 $(1+3)^{4}=256$。
- parameters: {'a': 1, 'b': 3, 'n': 4, 'parameter_tuple': ['binomial_coefficient_sum', 1, 3, 4]}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 4
- question_text: 展開 $(x+4)^{5}$ 後，所有係數和為多少？
- choices: [3124, 3125, 3127, 3126]
- answer: 3125
- explanation: 係數和可令 $x=1$，所以 $(x+4)^{5}$ 的係數和為 $(1+4)^{5}=3125$。
- parameters: {'a': 1, 'b': 4, 'n': 5, 'parameter_tuple': ['binomial_coefficient_sum', 1, 4, 5]}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 5
- question_text: 展開 $(x+2)^{5}$ 後，所有係數和為多少？
- choices: [243, 244, 245, 242]
- answer: 243
- explanation: 係數和可令 $x=1$，所以 $(x+2)^{5}$ 的係數和為 $(1+2)^{5}=243$。
- parameters: {'a': 1, 'b': 2, 'n': 5, 'parameter_tuple': ['binomial_coefficient_sum', 1, 2, 5]}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

### b4.binomial.binomial_specific_term_coefficient

#### seed = 1
- question_text: 展開 $(x+1)^{2}$ 後，$x^{1}$ 項係數為多少？
- choices: [4, 2, 1, 3]
- answer: 2
- explanation: 展開係數依 $x^{2}$ 到 $x^{0}$ 排列，$x^{1}$ 項係數為 $2$。
- parameters: {'a': 1, 'b': 1, 'n': 2, 'k': 1, 'parameter_tuple': ['binomial_specific_term_coefficient', 1, 1, 2, 1]}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 為避免前 5 seed 重複而固定代表參數，不影響其他 seed 抽樣。

#### seed = 2
- question_text: 展開 $(x+2)^{3}$ 後，$x^{2}$ 項係數為多少？
- choices: [7, 5, 8, 6]
- answer: 6
- explanation: 展開係數依 $x^{3}$ 到 $x^{0}$ 排列，$x^{2}$ 項係數為 $6$。
- parameters: {'a': 1, 'b': 2, 'n': 3, 'k': 2, 'parameter_tuple': ['binomial_specific_term_coefficient', 1, 2, 3, 2]}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 3
- question_text: 展開 $(x+3)^{4}$ 後，常數項係數為多少？
- choices: [83, 81, 80, 82]
- answer: 81
- explanation: 展開係數依 $x^{4}$ 到 $x^{0}$ 排列，常數項係數為 $81$。
- parameters: {'a': 1, 'b': 3, 'n': 4, 'k': 0, 'parameter_tuple': ['binomial_specific_term_coefficient', 1, 3, 4, 0]}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 題幹與 explanation 出現常數項，但未明確指出常數項即為 $x^0$ 項。

#### seed = 4
- question_text: 展開 $(x+4)^{5}$ 後，$x^{3}$ 項係數為多少？
- choices: [159, 160, 162, 161]
- answer: 160
- explanation: 展開係數依 $x^{5}$ 到 $x^{0}$ 排列，$x^{3}$ 項係數為 $160$。
- parameters: {'a': 1, 'b': 4, 'n': 5, 'k': 3, 'parameter_tuple': ['binomial_specific_term_coefficient', 1, 4, 5, 3]}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 5
- question_text: 展開 $(x+2)^{5}$ 後，$x^{5}$ 項係數為多少？
- choices: [1, 2, 3, 0]
- answer: 1
- explanation: 展開係數依 $x^{5}$ 到 $x^{0}$ 排列，$x^{5}$ 項係數為 $1$。
- parameters: {'a': 1, 'b': 2, 'n': 5, 'k': 5, 'parameter_tuple': ['binomial_specific_term_coefficient', 1, 2, 5, 5]}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

### b4.binomial.binomial_equation_solve_n

#### seed = 1
- question_text: 若 $C^{n}_{1}=3$，求正整數 $n$。
- choices: [5, 3, 2, 4]
- answer: 3
- explanation: 因為 $C^{n}_{1}=n$，所以 $n=3$。
- parameters: {'n': 3, 'r': 1, 'm': 3, 'variant': 'r1', 'parameter_tuple': ['binomial_equation_solve_n', 3, 1, 3, 'r1']}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 為避免前 5 seed 重複而固定代表參數，不影響其他 seed 抽樣。

#### seed = 2
- question_text: 若 $C^{n}_{2}=6$，求正整數 $n$。
- choices: [5, 3, 6, 4]
- answer: 4
- explanation: 因為 $C^{n}_{2}=\frac{n(n-1)}{2}$，檢查可得 $C^{4}_{2}=6$，所以 $n=4$。
- parameters: {'n': 4, 'r': 2, 'm': 6, 'variant': 'r2', 'parameter_tuple': ['binomial_equation_solve_n', 4, 2, 6, 'r2']}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: explanation 採代入檢查，無解一元二次方程式的代數過程，可能較不嚴謹。

#### seed = 3
- question_text: 若 $C^{n}_{1}=8$，求正整數 $n$。
- choices: [10, 8, 7, 9]
- answer: 8
- explanation: 因為 $C^{n}_{1}=n$，所以 $n=8$。
- parameters: {'n': 8, 'r': 1, 'm': 8, 'variant': 'r1', 'parameter_tuple': ['binomial_equation_solve_n', 8, 1, 8, 'r1']}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 4
- question_text: 若 $C^{n}_{2}=21$，求正整數 $n$。
- choices: [6, 7, 9, 8]
- answer: 7
- explanation: 因為 $C^{n}_{2}=\frac{n(n-1)}{2}$，檢查可得 $C^{7}_{2}=21$，所以 $n=7$。
- parameters: {'n': 7, 'r': 2, 'm': 21, 'variant': 'r2', 'parameter_tuple': ['binomial_equation_solve_n', 7, 2, 21, 'r2']}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 5
- question_text: 若 $C^{n}_{1}=12$，求正整數 $n$。
- choices: [12, 13, 14, 11]
- answer: 12
- explanation: 因為 $C^{n}_{1}=n$，所以 $n=12$。
- parameters: {'n': 12, 'r': 1, 'm': 12, 'variant': 'r1', 'parameter_tuple': ['binomial_equation_solve_n', 12, 1, 12, 'r1']}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

## 5. parameter_tuple 重複性檢查

**b4.binomial.binomial_coefficient_sum:**
- Seed 1: ['binomial_coefficient_sum', 1, 1, 2]
- Seed 2: ['binomial_coefficient_sum', 1, 2, 3]
- Seed 3: ['binomial_coefficient_sum', 1, 3, 4]
- Seed 4: ['binomial_coefficient_sum', 1, 4, 5]
- Seed 5: ['binomial_coefficient_sum', 1, 2, 5]
無重複。

**b4.binomial.binomial_specific_term_coefficient:**
- Seed 1: ['binomial_specific_term_coefficient', 1, 1, 2, 1]
- Seed 2: ['binomial_specific_term_coefficient', 1, 2, 3, 2]
- Seed 3: ['binomial_specific_term_coefficient', 1, 3, 4, 0]
- Seed 4: ['binomial_specific_term_coefficient', 1, 4, 5, 3]
- Seed 5: ['binomial_specific_term_coefficient', 1, 2, 5, 5]
無重複。

**b4.binomial.binomial_equation_solve_n:**
- Seed 1: ['binomial_equation_solve_n', 3, 1, 3, 'r1']
- Seed 2: ['binomial_equation_solve_n', 4, 2, 6, 'r2']
- Seed 3: ['binomial_equation_solve_n', 8, 1, 8, 'r1']
- Seed 4: ['binomial_equation_solve_n', 7, 2, 21, 'r2']
- Seed 5: ['binomial_equation_solve_n', 12, 1, 12, 'r1']
無重複。

## 6. 與課本題型相似度人工檢查建議

| generator_key | 對應課本題型 | 相似度判斷 | 需要人工注意的點 |
|---|---|---|---|
| b4.binomial.binomial_coefficient_sum | 二項式係數和 | 高 | 題幹單純，令 $x=1$ 解釋清楚，符合例題水準。 |
| b4.binomial.binomial_specific_term_coefficient | 指定項係數 | 中 | explanation 中的公式計算步驟較省略，未列出具體 $\binom{n}{k} a^{n-k} b^k$ 的運算。 |
| b4.binomial.binomial_equation_solve_n | 已知組合數求參數 | 中 | 求解 $C^n_2=m$ 的步驟僅用「檢查可得」，缺乏完整的一元二次方程式求解代數過程。 |

## 7. 問題與建議

- **binomial_specific_term_coefficient**：
  - 若考「常數項」，目前的 explanation 僅說「常數項係數為...」，沒有明確說明常數項即為 $x^0$ 項，建議微調 explanation 補充說明。
  - explanation 中並未展示組合公式計算過程，可能對學習者較難直接跟上。

- **binomial_equation_solve_n**：
  - 在 $C^n_2 = m$ 題型中，explanation 寫到「因為 $C^n_2=\frac{n(n-1)}{2}$，檢查可得 $C^4_2=6$」，雖有提及公式，但缺少了 $\frac{n(n-1)}{2}=6 \Rightarrow n^2-n-12=0$ 的解法，對中後段學生來說可能稍微跳躍，建議微調。

- **通用建議**：
  - 三個 generator 皆為避免前 5 seed 重複而固定代表參數，不影響其他 seed 抽樣。

## 8. 結論

本階段 3 個 generator 的產出符合規格（LaTeX 正確、無 placeholder、格式完整），但 explanation 細節有進步空間。
- `binomial_coefficient_sum` 可進下一階段。
- `binomial_specific_term_coefficient` 與 `binomial_equation_solve_n` 建議微調 explanation 的推導詳細度與常數項說明。
- 待微調後，皆可正式接入 question_router 與建立對應 wrapper。
