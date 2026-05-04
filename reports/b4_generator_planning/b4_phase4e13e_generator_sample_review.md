# B4 Phase 4E-13E Generator 樣題品質檢查報告

## 1. 本階段目的

本階段只檢查 Phase 4E-13E generator 樣題品質，不修改程式、不接 router、不建 wrapper、不接前端、不更新 coverage。

## 2. 檢查範圍

| generator_key | function | skill_id | subskill_id | multiple_choice |
|---|---|---|---|---|
| b4.binomial.binomial_middle_term_coefficient | binomial_middle_term_coefficient | vh_數學B4_BinomialTheorem | b4_ch1_binomial_middle_term_coefficient_01 | True |
| b4.binomial.binomial_odd_even_coefficient_sum | binomial_odd_even_coefficient_sum | vh_數學B4_BinomialCoefficientIdentities | b4_ch1_binomial_odd_even_coefficient_sum_01 | True |
| b4.binomial.binomial_specific_coefficient_with_negative_term | binomial_specific_coefficient_with_negative_term | vh_數學B4_BinomialTheorem | b4_ch1_binomial_specific_coefficient_negative_01 | True |

## 3. 總體檢查表

| generator_key | 樣題數 | unique_parameter_tuple 數 | choices_valid | answer_valid | latex_valid | metadata_complete | placeholder_free | 初步判斷 |
|---|---:|---:|---|---|---|---|---|---|
| b4.binomial.binomial_middle_term_coefficient | 5 | 5 | yes | yes | yes | yes | yes | 通過 |
| b4.binomial.binomial_odd_even_coefficient_sum | 5 | 5 | yes | yes | yes | yes | yes | 通過 |
| b4.binomial.binomial_specific_coefficient_with_negative_term | 5 | 5 | yes | yes | yes | yes | yes | 通過 |

## 4. 樣題清單

### b4.binomial.binomial_middle_term_coefficient

#### seed = 1
- question_text: 展開 $(x+1)^{2}$ 後，中間項，也就是 $x^{1}$ 項係數為多少？
- choices: [4, 2, 1, 3]
- answer: 2
- explanation: $n=2$ 為偶數，唯一中間項為 $x^{1}$ 項；由 $(x+1)^{2}$ 的展開係數可得其係數為 $2$。
- parameters: {'a': 1, 'b': 1, 'n': 2, 'middle_power': 1, 'parameter_tuple': ('binomial_middle_term_coefficient', 1, 1, 2)}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes（以 `binomial_expansion_coefficients(1,1,2)` 回算 middle_power=1 驗證）
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 題幹與 explanation 皆明示「偶數次唯一中間項」。

#### seed = 2
- question_text: 展開 $(x+2)^{4}$ 後，中間項，也就是 $x^{2}$ 項係數為多少？
- choices: [25, 23, 26, 24]
- answer: 24
- explanation: $n=4$ 為偶數，唯一中間項為 $x^{2}$ 項；由 $(x+2)^{4}$ 的展開係數可得其係數為 $24$。
- parameters: {'a': 1, 'b': 2, 'n': 4, 'middle_power': 2, 'parameter_tuple': ('binomial_middle_term_coefficient', 1, 2, 4)}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 3
- question_text: 展開 $(x+3)^{6}$ 後，中間項，也就是 $x^{3}$ 項係數為多少？
- choices: [542, 540, 539, 541]
- answer: 540
- explanation: $n=6$ 為偶數，唯一中間項為 $x^{3}$ 項；由 $(x+3)^{6}$ 的展開係數可得其係數為 $540$。
- parameters: {'a': 1, 'b': 3, 'n': 6, 'middle_power': 3, 'parameter_tuple': ('binomial_middle_term_coefficient', 1, 3, 6)}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 4
- question_text: 展開 $(x+4)^{2}$ 後，中間項，也就是 $x^{1}$ 項係數為多少？
- choices: [7, 8, 10, 9]
- answer: 8
- explanation: $n=2$ 為偶數，唯一中間項為 $x^{1}$ 項；由 $(x+4)^{2}$ 的展開係數可得其係數為 $8$。
- parameters: {'a': 1, 'b': 4, 'n': 2, 'middle_power': 1, 'parameter_tuple': ('binomial_middle_term_coefficient', 1, 4, 2)}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 5
- question_text: 展開 $(x+2)^{6}$ 後，中間項，也就是 $x^{3}$ 項係數為多少？
- choices: [160, 161, 162, 159]
- answer: 160
- explanation: $n=6$ 為偶數，唯一中間項為 $x^{3}$ 項；由 $(x+2)^{6}$ 的展開係數可得其係數為 $160$。
- parameters: {'a': 1, 'b': 2, 'n': 6, 'middle_power': 3, 'parameter_tuple': ('binomial_middle_term_coefficient', 1, 2, 6)}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 為避免前 5 seed 重複而固定代表參數，不影響其他 seed 抽樣。

### b4.binomial.binomial_odd_even_coefficient_sum

#### seed = 1
- question_text: 展開 $(x+1)^{2}$ 後，奇數次項係數和為多少？
- choices: [4, 2, 1, 3]
- answer: 2
- explanation: 依 $x^{2}$ 到 $x^{0}$ 的係數，取出 奇數次項 對應項後相加；因此係數和為 $2$。
- parameters: {'a': 1, 'b': 1, 'n': 2, 'target_parity': 'odd', 'parameter_tuple': ('binomial_odd_even_coefficient_sum', 1, 1, 2, 'odd')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes（以 `binomial_expansion_coefficients` 依次方奇偶加總驗證）
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 題幹已清楚區分奇數次項。

#### seed = 2
- question_text: 展開 $(x+2)^{3}$ 後，偶數次項係數和為多少？
- choices: [15, 13, 16, 14]
- answer: 14
- explanation: 依 $x^{3}$ 到 $x^{0}$ 的係數，取出 偶數次項 對應項後相加；因此係數和為 $14$。
- parameters: {'a': 1, 'b': 2, 'n': 3, 'target_parity': 'even', 'parameter_tuple': ('binomial_odd_even_coefficient_sum', 1, 2, 3, 'even')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 題幹已清楚區分偶數次項。

#### seed = 3
- question_text: 展開 $(x+3)^{4}$ 後，奇數次項係數和為多少？
- choices: [122, 120, 119, 121]
- answer: 120
- explanation: 依 $x^{4}$ 到 $x^{0}$ 的係數，取出 奇數次項 對應項後相加；因此係數和為 $120$。
- parameters: {'a': 1, 'b': 3, 'n': 4, 'target_parity': 'odd', 'parameter_tuple': ('binomial_odd_even_coefficient_sum', 1, 3, 4, 'odd')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 4
- question_text: 展開 $(x+4)^{5}$ 後，偶數次項係數和為多少？
- choices: [1683, 1684, 1686, 1685]
- answer: 1684
- explanation: 依 $x^{5}$ 到 $x^{0}$ 的係數，取出 偶數次項 對應項後相加；因此係數和為 $1684$。
- parameters: {'a': 1, 'b': 4, 'n': 5, 'target_parity': 'even', 'parameter_tuple': ('binomial_odd_even_coefficient_sum', 1, 4, 5, 'even')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 5
- question_text: 展開 $(x+2)^{5}$ 後，奇數次項係數和為多少？
- choices: [121, 122, 123, 120]
- answer: 121
- explanation: 依 $x^{5}$ 到 $x^{0}$ 的係數，取出 奇數次項 對應項後相加；因此係數和為 $121$。
- parameters: {'a': 1, 'b': 2, 'n': 5, 'target_parity': 'odd', 'parameter_tuple': ('binomial_odd_even_coefficient_sum', 1, 2, 5, 'odd')}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 為避免前 5 seed 重複而固定代表參數，不影響其他 seed 抽樣。

### b4.binomial.binomial_specific_coefficient_with_negative_term

#### seed = 1
- question_text: 展開 $(x-1)^{2}$ 後，$x^{1}$ 項係數為多少？
- choices: [3, -2, 1, 0]
- answer: -2
- explanation: 因為二項式中含負項，係數符號需保留；展開後 $x^{1}$ 項 的係數為 $-2$。
- parameters: {'a': 1, 'b': -1, 'n': 2, 'k': 1, 'parameter_tuple': ('binomial_specific_coefficient_with_negative_term', 1, -1, 2, 1)}
- 檢查結果:
  - choices_valid: yes（含負數選項且唯一，answer 在 choices 內）
  - answer_valid: yes（以 `binomial_expansion_coefficients(1,-1,2)` 驗證）
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 本題即為負答案 case。

#### seed = 2
- question_text: 展開 $(x-2)^{3}$ 後，$x^{2}$ 項係數為多少？
- choices: [-6, 21, 12, 11]
- answer: -6
- explanation: 因為二項式中含負項，係數符號需保留；展開後 $x^{2}$ 項 的係數為 $-6$。
- parameters: {'a': 1, 'b': -2, 'n': 3, 'k': 2, 'parameter_tuple': ('binomial_specific_coefficient_with_negative_term', 1, -2, 3, 2)}
- 檢查結果:
  - choices_valid: yes（含負數選項且唯一，answer 在 choices 內）
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 負項造成係數負號，敘述合理。

#### seed = 3
- question_text: 展開 $(x-3)^{4}$ 後，常數項，也就是 $x^{0}$ 項係數為多少？
- choices: [83, 81, 80, 82]
- answer: 81
- explanation: 因為二項式中含負項，係數符號需保留；展開後 常數項，也就是 $x^{0}$ 項 的係數為 $81$。
- parameters: {'a': 1, 'b': -3, 'n': 4, 'k': 0, 'parameter_tuple': ('binomial_specific_coefficient_with_negative_term', 1, -3, 4, 0)}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: `k=0` 時已明示「常數項，即 $x^{0}$ 項」。

#### seed = 4
- question_text: 展開 $(x-4)^{5}$ 後，$x^{3}$ 項係數為多少？
- choices: [159, 160, 162, 161]
- answer: 160
- explanation: 因為二項式中含負項，係數符號需保留；展開後 $x^{3}$ 項 的係數為 $160$。
- parameters: {'a': 1, 'b': -4, 'n': 5, 'k': 3, 'parameter_tuple': ('binomial_specific_coefficient_with_negative_term', 1, -4, 5, 3)}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 同上。

#### seed = 5
- question_text: 展開 $(x-2)^{5}$ 後，$x^{5}$ 項係數為多少？
- choices: [1, 2, 3, 0]
- answer: 1
- explanation: 因為二項式中含負項，係數符號需保留；展開後 $x^{5}$ 項 的係數為 $1$。
- parameters: {'a': 1, 'b': -2, 'n': 5, 'k': 5, 'parameter_tuple': ('binomial_specific_coefficient_with_negative_term', 1, -2, 5, 5)}
- 檢查結果:
  - choices_valid: yes
  - answer_valid: yes
  - latex_valid: yes
  - metadata_complete: yes
  - placeholder_free: yes
  - parameter_tuple_exists: yes
  - notes: 為避免前 5 seed 重複而固定代表參數，不影響其他 seed 抽樣。

## 5. parameter_tuple 重複性檢查

**b4.binomial.binomial_middle_term_coefficient**
- Seed 1: ('binomial_middle_term_coefficient', 1, 1, 2)
- Seed 2: ('binomial_middle_term_coefficient', 1, 2, 4)
- Seed 3: ('binomial_middle_term_coefficient', 1, 3, 6)
- Seed 4: ('binomial_middle_term_coefficient', 1, 4, 2)
- Seed 5: ('binomial_middle_term_coefficient', 1, 2, 6)
- 結果：無重複（5/5 unique）

**b4.binomial.binomial_odd_even_coefficient_sum**
- Seed 1: ('binomial_odd_even_coefficient_sum', 1, 1, 2, 'odd')
- Seed 2: ('binomial_odd_even_coefficient_sum', 1, 2, 3, 'even')
- Seed 3: ('binomial_odd_even_coefficient_sum', 1, 3, 4, 'odd')
- Seed 4: ('binomial_odd_even_coefficient_sum', 1, 4, 5, 'even')
- Seed 5: ('binomial_odd_even_coefficient_sum', 1, 2, 5, 'odd')
- 結果：無重複（5/5 unique）

**b4.binomial.binomial_specific_coefficient_with_negative_term**
- Seed 1: ('binomial_specific_coefficient_with_negative_term', 1, -1, 2, 1)
- Seed 2: ('binomial_specific_coefficient_with_negative_term', 1, -2, 3, 2)
- Seed 3: ('binomial_specific_coefficient_with_negative_term', 1, -3, 4, 0)
- Seed 4: ('binomial_specific_coefficient_with_negative_term', 1, -4, 5, 3)
- Seed 5: ('binomial_specific_coefficient_with_negative_term', 1, -2, 5, 5)
- 結果：無重複（5/5 unique）

## 6. 額外 targeted check

- negative term 題型是否驗證到負答案 case：**是**。seed 1（answer=-2）與 seed 2（answer=-6）即為負答案案例，choices 仍唯一且包含答案。  
- middle term 題型是否全部 n 為偶數：**是**。seed 1~5 的 n 分別為 2, 4, 6, 2, 6。  
- odd/even coefficient sum 是否同時出現 odd / even：**是**。seed 1,3,5 為 odd；seed 2,4 為 even。

## 7. 與課本題型相似度人工檢查建議

| generator_key | 對應課本題型 | 相似度判斷 | 需要人工注意的點 |
|---|---|---|---|
| b4.binomial.binomial_middle_term_coefficient | 二項式中間項係數 | 高 | 說明已有「偶數次唯一中間項」，可再評估是否補一行公式化推導。 |
| b4.binomial.binomial_odd_even_coefficient_sum | 奇/偶次項係數和 | 中 | 建議後續可補上以 $x^k$ 的 k 奇偶判斷示例，降低語意跳躍。 |
| b4.binomial.binomial_specific_coefficient_with_negative_term | 含負項二項式指定項係數 | 高 | 已提醒負項影響符號；可再補一題較高次數以強化符號規律。 |

## 8. 問題與建議

- 本次 15 題未發現 contract、answer、choices、metadata、placeholder 的實際錯誤。  
- LaTeX 檢查通過；未出現 `2^2`、`C(n,r)`、`P(n,r)` 等不合格字樣。  
- 額外說明：本批題目未出現需要顯式乘號的位置，因此無 `\times` 使用場景，不構成違規。  
- `binomial_odd_even_coefficient_sum` 的 explanation 目前寫「取出奇/偶數次項後相加」，可於後續微調時補更明確的「依 $x^k$ 的 k 奇偶判斷」句型。  
- 三個 generator 的 seed 1~5 皆為固定代表參數，屬預期設計：為避免前 5 seed 重複而固定代表參數，不影響其他 seed 抽樣。

## 9. 結論

- `binomial_middle_term_coefficient`：可進下一階段。  
- `binomial_odd_even_coefficient_sum`：可進下一階段（建議後續微調 explanation 清晰度）。  
- `binomial_specific_coefficient_with_negative_term`：可進下一階段，且已驗證負答案情境。  
- 就 QA 觀察，三者皆可作為接入 question_router / wrapper 的候選。  
- 無阻塞性問題，僅有教學敘述可讀性微調建議。  
