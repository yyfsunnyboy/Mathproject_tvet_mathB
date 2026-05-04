# B4 Phase 4E-10 Generator 樣題品質檢查報告

## 1. 本階段目的
本階段只檢查 Phase 4E-10 generator 樣題，不修改程式、不接 router、不建 wrapper、不接前端。

## 2. 檢查範圍

| generator_key | function | skill_id | subskill_id | multiple_choice |
|---|---|---|---|---|
| b4.counting.mult_principle_independent_choices | mult_principle_independent_choices | vh_數學B4_MultiplicationPrinciple | b4_ch1_mult_principle_independent_01 | True |
| b4.counting.mult_digits_no_repeat | mult_digits_no_repeat | vh_數學B4_MultiplicationPrinciple | b4_ch1_mult_digits_no_repeat_01 | True |
| b4.counting.repeated_permutation_assignment | repeated_permutation_assignment | vh_數學B4_PermutationWithRepetition | b4_ch1_rep_perm_assignment_01 | True |

## 3. 總體檢查表

| generator_key | 樣題數 | unique_parameter_tuple 數 | choices_valid | answer_valid | latex_valid | metadata_complete | placeholder_free | 初步判斷 |
|---|---:|---:|---|---|---|---|---|---|
| b4.counting.mult_principle_independent_choices | 5 | 5 | Yes | Yes | Yes | Yes | Yes | 通過 |
| b4.counting.mult_digits_no_repeat | 5 | 5 | Yes | Yes | Yes | Yes | Yes | 通過 |
| b4.counting.repeated_permutation_assignment | 5 | 5 | Yes | Yes | Yes | Yes | Yes | 通過 |

## 4. 樣題清單

### b4.counting.mult_principle_independent_choices

#### seed = 1
- question_text: 完成一件事分為 2 個獨立階段：搭公車有 3 種選法、轉捷運有 4 種選法，共有多少種方法？
- choices: [6, 10, 11, 12]
- answer: 12
- explanation: 使用乘法原理，獨立階段依序完成，總方法數為各階段數量相乘。例如：$3 \times 4=12$。
- parameters: {'stage_names': ['搭公車', '轉捷運'], 'counts': [3, 4], 'parameter_tuple': ['mult_principle_independent_choices', ['搭公車', '轉捷運'], [3, 4]]}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 2
- question_text: 完成一件事分為 3 個獨立階段：早餐有 2 種選法、午餐有 3 種選法、點心有 2 種選法，共有多少種方法？
- choices: [12, 6, 11, 10]
- answer: 12
- explanation: 使用乘法原理，獨立階段依序完成，總方法數為各階段數量相乘。例如：$2 \times 3 \times 2=12$。
- parameters: {'stage_names': ['早餐', '午餐', '點心'], 'counts': [2, 3, 2], 'parameter_tuple': ['mult_principle_independent_choices', ['早餐', '午餐', '點心'], [2, 3, 2]]}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 3
- question_text: 完成一件事分為 2 個獨立階段：選上衣有 5 種選法、選褲子有 6 種選法，共有多少種方法？
- choices: [32, 60, 33, 30]
- answer: 30
- explanation: 使用乘法原理，獨立階段依序完成，總方法數為各階段數量相乘。例如：$5 \times 6=30$。
- parameters: {'stage_names': ['選上衣', '選褲子'], 'counts': [5, 6], 'parameter_tuple': ['mult_principle_independent_choices', ['選上衣', '選褲子'], [5, 6]]}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 4
- question_text: 完成一件事分為 3 個獨立階段：填志願一有 4 種選法、填志願二有 3 種選法、填志願三有 2 種選法，共有多少種方法？
- choices: [24, 12, 22, 48]
- answer: 24
- explanation: 使用乘法原理，獨立階段依序完成，總方法數為各階段數量相乘。例如：$4 \times 3 \times 2=24$。
- parameters: {'stage_names': ['填志願一', '填志願二', '填志願三'], 'counts': [4, 3, 2], 'parameter_tuple': ['mult_principle_independent_choices', ['填志願一', '填志願二', '填志願三'], [4, 3, 2]]}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 5
- question_text: 完成一件事分為 3 個獨立階段：搭公車有 2 種選法、轉捷運有 2 種選法、步行路段有 3 種選法，共有多少種方法？
- choices: [12, 11, 10, 6]
- answer: 12
- explanation: 使用乘法原理，獨立階段依序完成，總方法數為各階段數量相乘。例如：$2 \times 2 \times 3=12$。
- parameters: {'stage_names': ['搭公車', '轉捷運', '步行路段'], 'counts': [2, 2, 3], 'parameter_tuple': ['mult_principle_independent_choices', ['搭公車', '轉捷運', '步行路段'], [2, 2, 3]]}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

### b4.counting.mult_digits_no_repeat

#### seed = 1
- question_text: 使用 1、2、3、4、5 共 5 個數字，組成不重複的 3 位數，共有多少個？
- choices: [30, 60, 120, 58]
- answer: 60
- explanation: 數字不可重複，使用 $P^{n}_{r}$ 得 $P^{5}_{3}=60$。
- parameters: {'digit_pool_size': 5, 'positions': 3, 'allow_zero': False, 'parameter_tuple': ['mult_digits_no_repeat', 5, 3, False]}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 2
- question_text: 使用 0、1、2、3、4、5 共 6 個數字，組成不重複的 2 位數，且首位不可為 $0$，共有多少個？
- choices: [25, 12, 50, 23]
- answer: 25
- explanation: 第一位不能為 $0$，有 $5$ 種選法；其餘 $1$ 位有 $P^{5}_{1}$ 種，所以 $5\times P^{5}_{1}=25$。
- parameters: {'digit_pool_size': 6, 'positions': 2, 'allow_zero': True, 'parameter_tuple': ['mult_digits_no_repeat', 6, 2, True]}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 3
- question_text: 使用 0、1、2、3、4、5、6 共 7 個數字，組成不重複的 3 位數，且首位不可為 $0$，共有多少個？
- choices: [178, 179, 360, 180]
- answer: 180
- explanation: 第一位不能為 $0$，有 $6$ 種選法；其餘 $2$ 位有 $P^{6}_{2}$ 種，所以 $6\times P^{6}_{2}=180$。
- parameters: {'digit_pool_size': 7, 'positions': 3, 'allow_zero': True, 'parameter_tuple': ['mult_digits_no_repeat', 7, 3, True]}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 4
- question_text: 使用 1、2、3、4、5 共 5 個數字，組成不重複的 2 位數，共有多少個？
- choices: [40, 20, 10, 18]
- answer: 20
- explanation: 數字不可重複，使用 $P^{n}_{r}$ 得 $P^{5}_{2}=20$。
- parameters: {'digit_pool_size': 5, 'positions': 2, 'allow_zero': False, 'parameter_tuple': ['mult_digits_no_repeat', 5, 2, False]}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 5
- question_text: 使用 1、2、3、4、5、6 共 6 個數字，組成不重複的 3 位數，共有多少個？
- choices: [120, 119, 118, 240]
- answer: 120
- explanation: 數字不可重複，使用 $P^{n}_{r}$ 得 $P^{6}_{3}=120$。
- parameters: {'digit_pool_size': 6, 'positions': 3, 'allow_zero': False, 'parameter_tuple': ['mult_digits_no_repeat', 6, 3, False]}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

### b4.counting.repeated_permutation_assignment

#### seed = 1
- question_text: 將 3 個不同工作分別指派給 4 位人員，每個工作可指派給任一人，且同一人可負責多個工作，共有多少種指派方式？
- choices: [65, 64, 66, 128]
- answer: 64
- explanation: 每個位置都有 $m$ 種選擇，共有 $n$ 個位置，允許重複，所以共有 $m^{n}$ 種。例如：$4^{3}=64$。
- parameters: {'choices_per_position': 4, 'positions': 3, 'context': 'tasks_to_people', 'parameter_tuple': ['repeated_permutation_assignment', 4, 3, 'tasks_to_people']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 2
- question_text: 將 4 封不同信件分別投入 3 個信箱，每封信可投入任一信箱，且同一信箱可收到多封信，共有多少種投法？
- choices: [40, 81, 162, 79]
- answer: 81
- explanation: 每個位置都有 $m$ 種選擇，共有 $n$ 個位置，允許重複，所以共有 $m^{n}$ 種。例如：$3^{4}=81$。
- parameters: {'choices_per_position': 3, 'positions': 4, 'context': 'letters_to_mailboxes', 'parameter_tuple': ['repeated_permutation_assignment', 3, 4, 'letters_to_mailboxes']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 3
- question_text: 將 2 件不同物品分別放入 5 個盒子，每件物品可放入任一盒子，且同一盒子可放多件物品，共有多少種放法？
- choices: [50, 12, 23, 25]
- answer: 25
- explanation: 每個位置都有 $m$ 種選擇，共有 $n$ 個位置，允許重複，所以共有 $m^{n}$ 種。例如：$5^{2}=25$。
- parameters: {'choices_per_position': 5, 'positions': 2, 'context': 'items_to_boxes', 'parameter_tuple': ['repeated_permutation_assignment', 5, 2, 'items_to_boxes']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 4
- question_text: 將 4 個不同工作分別指派給 4 位人員，每個工作可指派給任一人，且同一人可負責多個工作，共有多少種指派方式？
- choices: [257, 256, 258, 512]
- answer: 256
- explanation: 每個位置都有 $m$ 種選擇，共有 $n$ 個位置，允許重複，所以共有 $m^{n}$ 種。例如：$4^{4}=256$。
- parameters: {'choices_per_position': 4, 'positions': 4, 'context': 'tasks_to_people', 'parameter_tuple': ['repeated_permutation_assignment', 4, 4, 'tasks_to_people']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

#### seed = 5
- question_text: 將 3 封不同信件分別投入 3 個信箱，每封信可投入任一信箱，且同一信箱可收到多封信，共有多少種投法？
- choices: [13, 27, 25, 54]
- answer: 27
- explanation: 每個位置都有 $m$ 種選擇，共有 $n$ 個位置，允許重複，所以共有 $m^{n}$ 種。例如：$3^{3}=27$。
- parameters: {'choices_per_position': 3, 'positions': 3, 'context': 'letters_to_mailboxes', 'parameter_tuple': ['repeated_permutation_assignment', 3, 3, 'letters_to_mailboxes']}
- 檢查結果:
  - choices_valid: Yes
  - answer_valid: Yes
  - latex_valid: Yes
  - metadata_complete: Yes
  - placeholder_free: Yes
  - parameter_tuple_exists: Yes
  - notes:

## 5. parameter_tuple 重複性檢查

### b4.counting.mult_principle_independent_choices
- seed 1: ['mult_principle_independent_choices', ['搭公車', '轉捷運'], [3, 4]]
- seed 2: ['mult_principle_independent_choices', ['早餐', '午餐', '點心'], [2, 3, 2]]
- seed 3: ['mult_principle_independent_choices', ['選上衣', '選褲子'], [5, 6]]
- seed 4: ['mult_principle_independent_choices', ['填志願一', '填志願二', '填志願三'], [4, 3, 2]]
- seed 5: ['mult_principle_independent_choices', ['搭公車', '轉捷運', '步行路段'], [2, 2, 3]]

### b4.counting.mult_digits_no_repeat
- seed 1: ['mult_digits_no_repeat', 5, 3, False]
- seed 2: ['mult_digits_no_repeat', 6, 2, True]
- seed 3: ['mult_digits_no_repeat', 7, 3, True]
- seed 4: ['mult_digits_no_repeat', 5, 2, False]
- seed 5: ['mult_digits_no_repeat', 6, 3, False]

### b4.counting.repeated_permutation_assignment
- seed 1: ['repeated_permutation_assignment', 4, 3, 'tasks_to_people']
- seed 2: ['repeated_permutation_assignment', 3, 4, 'letters_to_mailboxes']
- seed 3: ['repeated_permutation_assignment', 5, 2, 'items_to_boxes']
- seed 4: ['repeated_permutation_assignment', 4, 4, 'tasks_to_people']
- seed 5: ['repeated_permutation_assignment', 3, 3, 'letters_to_mailboxes']

## 6. 與課本題型相似度人工檢查建議

| generator_key | 對應課本題型 | 相似度判斷 | 需要人工注意的點 |
|---|---|---|---|
| b4.counting.mult_principle_independent_choices | 乘法原理（服裝搭配/路線等） | 高 | 檢查情境是否太抽象 |
| b4.counting.mult_digits_no_repeat | 數字排列（無重複） | 高 | 含 0 題型需確認是否有說明首位不可為 0 |
| b4.counting.repeated_permutation_assignment | 重複排列（分派問題） | 高 | 檢查是否與 repeated_choice_basic 太相似 |

## 7. 問題與建議

- **b4.counting.mult_principle_independent_choices**: 題意通常為連續動作（如搭配服裝或選餐），需人工檢視情境是否直觀，且符合課本。
- **b4.counting.mult_digits_no_repeat**: 若含 0 題目沒有清楚說明首位不可為 0，或排列時未考慮此條件，可能需微調 explanation。
- **b4.counting.repeated_permutation_assignment**: 請注意題幹是否能清楚區分「物品」與「可選對象」，避免與 repeated_choice_basic 混淆。

## 8. 結論

- 三個 generator 皆能順利產出 5 題樣題。
- 各項基礎驗證（答案、選擇題選項、LaTeX 格式、Metadata）皆通過。
- 可接入 question_router / wrapper，並推進到下一階段。
- 建議人工確認各 generator 題目的情境語氣與課本的相似程度。