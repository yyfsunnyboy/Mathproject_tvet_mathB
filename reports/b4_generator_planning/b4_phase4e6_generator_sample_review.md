# B4 Phase 4E-6 Generator 樣題品質檢查報告

## 1. 本階段目的

本階段僅針對 Phase 4E-6 已完成之三個 generator，以固定 seed（1～5）實際各產生 5 題樣題，檢查題面、選項、答案、LaTeX、metadata、`parameter_tuple` 重複性與課本相似度之人工判讀。本報告不修改任何程式、不接 router、不建 wrapper、不接前端、不改測試與資料庫。

## 2. 檢查範圍

| generator_key | function | skill_id | subskill_id | multiple_choice |
|---|---|---|---|---|
| b4.counting.add_principle_mutually_exclusive_choice | add_principle_mutually_exclusive_choice | vh_數學B4_AdditionPrinciple | b4_ch1_add_principle_01 | True |
| b4.combination.combination_properties_simplification | combination_properties_simplification | vh_數學B4_CombinationProperties | b4_ch1_comb_properties_01 | True |
| b4.counting.repeated_choice_basic | repeated_choice_basic | vh_數學B4_PermutationWithRepetition | b4_ch1_repeated_choice_01 | True |

## 3. 總體檢查表

| generator_key | 樣題數 | unique_parameter_tuple 數 | choices_valid | answer_valid | latex_valid | metadata_complete | placeholder_free | 初步判斷 |
|---|---:|---:|---|---|---|---|---|---|
| b4.counting.add_principle_mutually_exclusive_choice | 5 | 5 | 是 | 是 | 是 | 是 | 是 | 通過 |
| b4.combination.combination_properties_simplification | 5 | 5 | 是 | 是 | 是 | 是 | 是 | 通過 |
| b4.counting.repeated_choice_basic | 5 | 5 | 是 | 是 | 是 | 是 | 是 | 通過 |

說明：`metadata_complete` 以題目交付所需欄位為準（含 `skill_id`、`subskill_id`、`problem_type_id`、`generator_key`、`difficulty`、`diagnosis_tags`、`remediation_candidates`、`source_style_refs` 與巢狀 `parameters`，且 `parameters.parameter_tuple` 存在）。`validate_problem_payload_contract` 之必填鍵集合不含 `parameters`，此點於第 7 節說明。

## 4. 樣題清單

### b4.counting.add_principle_mutually_exclusive_choice

#### seed = 1

- question_text: 某校社團活動可選擇4 種語文社團、2 種球類社團，若只選擇其中一種社團，共有多少種選法？
- choices: [6, 4, 3, 5]
- answer: 6
- explanation: 使用加法原理，互斥分類只選一類，總方法數為各類數量相加，例如：$4+2=6$。
- parameters: `category_names` 語文社團、球類社團；`counts` 4, 2；`parameter_tuple` 見第 5 節。
- 檢查結果:
  - choices_valid: 是（4 個互異，含答案）
  - answer_valid: 是（`addition_principle_count([4,2])=6`，型別 int）
  - latex_valid: 是（加法算式置於 `$4+2=6$`；題幹無裸指數或裸 `C(n,r)`）
  - metadata_complete: 是（合約鍵齊備，且含 `parameters` / `parameter_tuple`）
  - placeholder_free: 是（題幹與解析未含指定占位字元）
  - parameter_tuple_exists: 是
  - notes: 解析說明含「加法原理」與「互斥分類只選一類」；題幹為繁體中文。數字與「種」之間空格略不統一（`4 種` 與 `選擇4`），屬版式微瑕。

#### seed = 2

- question_text: 某校社團活動可選擇4 種球類社團、8 種舞蹈社團，若只選擇其中一種社團，共有多少種選法？
- choices: [12, 11, 10, 6]
- answer: 12
- explanation: 使用加法原理，互斥分類只選一類，總方法數為各類數量相加，例如：$4+8=12$。
- parameters: 球類社團／舞蹈社團；4, 8。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`addition_principle_count([4,8])=12`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 同上；版式空格微瑕。

#### seed = 3

- question_text: 某校社團活動可選擇3 種語文社團、4 種舞蹈社團，若只選擇其中一種社團，共有多少種選法？
- choices: [3, 7, 5, 6]
- answer: 7
- explanation: 使用加法原理，互斥分類只選一類，總方法數為各類數量相加，例如：$3+4=7$。
- parameters: 語文社團／舞蹈社團；3, 4。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`addition_principle_count([3,4])=7`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 同上。

#### seed = 4

- question_text: 某校社團活動可選擇7 種美術社團、5 種球類社團，若只選擇其中一種社團，共有多少種選法？
- choices: [6, 10, 12, 11]
- answer: 12
- explanation: 使用加法原理，互斥分類只選一類，總方法數為各類數量相加，例如：$7+5=12$。
- parameters: 美術社團／球類社團；7, 5。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`addition_principle_count([7,5])=12`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 同上。

#### seed = 5

- question_text: 某校社團活動可選擇2 種志工社團、8 種美術社團、5 種語文社團，若只選擇其中一種社團，共有多少種選法？
- choices: [14, 15, 13, 7]
- answer: 15
- explanation: 使用加法原理，互斥分類只選一類，總方法數為各類數量相加，例如：$2+8+5=15$。
- parameters: 志工／美術／語文三類；2, 8, 5。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`addition_principle_count([2,8,5])=15`，int）
  - latex_valid: 是（三項和於單一 `$...$` 內）
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 三類互斥加法情境清楚；版式空格微瑕。

### b4.combination.combination_properties_simplification

#### seed = 1

- question_text: 計算 $C(6,1)$ 的值。
- choices: [5, 4, 3, 6]
- answer: 6
- explanation: 使用 $C(n,r)=\frac{n!}{r!(n-r)!}$ 計算，可得 $C(6,1)=6$。
- parameters: n=6, r=1, variant=direct。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(6,1)=6`，int）
  - latex_valid: 是（`$C(6,1)$`；解析中 `C(n,r)` 置於 `$...$` 內；指數以階乘語意表達，非裸 `2^2` 類文字）
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: direct 變體；解析為一般公式計算說明。

#### seed = 2

- question_text: 利用組合性質計算 $C(5,2)$ 的值。
- choices: [10, 9, 8, 5]
- answer: 10
- explanation: 使用 $C(n,r)=C(n,n-r)$，所以 $C(5,2)=C(5,3)=10$。
- parameters: n=5, r=2, variant=symmetry。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(5,2)=10`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: symmetry 變體；解析明確使用 $C(n,r)=C(n,n-r)$。

#### seed = 3

- question_text: 計算 $C(6,2)$ 的值。
- choices: [7, 15, 13, 14]
- answer: 15
- explanation: 使用 $C(n,r)=\frac{n!}{r!(n-r)!}$ 計算，可得 $C(6,2)=15$。
- parameters: n=6, r=2, variant=direct。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(6,2)=15`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: direct；與 seed 4 同 (n,r) 但 variant 不同，參數 tuple 仍相異。

#### seed = 4

- question_text: 利用組合性質計算 $C(6,2)$ 的值。
- choices: [7, 13, 15, 14]
- answer: 15
- explanation: 使用 $C(n,r)=C(n,n-r)$，所以 $C(6,2)=C(6,4)=15$。
- parameters: n=6, r=2, variant=symmetry。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(6,2)=15`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: symmetry；與 seed 3 題幹數字相同但命題用語與解析路徑不同。

#### seed = 5

- question_text: 計算 $C(9,3)$ 的值。
- choices: [42, 82, 168, 84]
- answer: 84
- explanation: 使用 $C(n,r)=\frac{n!}{r!(n-r)!}$ 計算，可得 $C(9,3)=84$。
- parameters: n=9, r=3, variant=direct。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(9,3)=84`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: direct。

### b4.counting.repeated_choice_basic

#### seed = 1

- question_text: 有 2 位同學，每人可從 2 種飲料中任選一種，且可重複選擇，共有多少種選法？
- choices: [5, 4, 3, 2]
- answer: 4
- explanation: 每個位置都有 $m$ 種選擇，共有 $n$ 個位置，所以總數為 $m^{n}$。例如：$2^{2}=4$。
- parameters: choices_per_position=2, positions=2。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`repeated_choice_count(2,2)=4`，int）
  - latex_valid: 是（一般式 `$m^{n}$`；數值例 `$2^{2}=4$` 使用 `^{...}`）
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 解析符合「每位置 m 種、n 位置、故 $m^n$」之要求；題幹為繁中敘述。

#### seed = 2

- question_text: 有 2 位同學，每人可從 3 種飲料中任選一種，且可重複選擇，共有多少種選法？
- choices: [4, 7, 8, 9]
- answer: 9
- explanation: 每個位置都有 $m$ 種選擇，共有 $n$ 個位置，所以總數為 $m^{n}$。例如：$3^{2}=9$。
- parameters: 3, 2。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`repeated_choice_count(3,2)=9`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 同上。

#### seed = 3

- question_text: 有 2 位同學，每人可從 4 種飲料中任選一種，且可重複選擇，共有多少種選法？
- choices: [14, 16, 8, 32]
- answer: 16
- explanation: 每個位置都有 $m$ 種選擇，共有 $n$ 個位置，所以總數為 $m^{n}$。例如：$4^{2}=16$。
- parameters: 4, 2。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`repeated_choice_count(4,2)=16`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 同上。

#### seed = 4

- question_text: 有 2 位同學，每人可從 5 種飲料中任選一種，且可重複選擇，共有多少種選法？
- choices: [50, 25, 23, 12]
- answer: 25
- explanation: 每個位置都有 $m$ 種選擇，共有 $n$ 個位置，所以總數為 $m^{n}$。例如：$5^{2}=25$。
- parameters: 5, 2。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`repeated_choice_count(5,2)=25`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 同上。

#### seed = 5

- question_text: 有 3 位同學，每人可從 2 種飲料中任選一種，且可重複選擇，共有多少種選法？
- choices: [8, 4, 7, 6]
- answer: 8
- explanation: 每個位置都有 $m$ 種選擇，共有 $n$ 個位置，所以總數為 $m^{n}$。例如：$2^{3}=8$。
- parameters: 2, 3。
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`repeated_choice_count(2,3)=8`，int）
  - latex_valid: 是（`$2^{3}=8$`）
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 同上；本題 `positions=3`，與 seed 1～4 之 2 位同學不同，參數 tuple 仍唯一。

## 5. parameter_tuple 重複性檢查

### b4.counting.add_principle_mutually_exclusive_choice

- seed 1: `('add_principle_mutually_exclusive_choice', ('語文社團', '球類社團'), (4, 2))`
- seed 2: `('add_principle_mutually_exclusive_choice', ('球類社團', '舞蹈社團'), (4, 8))`
- seed 3: `('add_principle_mutually_exclusive_choice', ('語文社團', '舞蹈社團'), (3, 4))`
- seed 4: `('add_principle_mutually_exclusive_choice', ('美術社團', '球類社團'), (7, 5))`
- seed 5: `('add_principle_mutually_exclusive_choice', ('志工社團', '美術社團', '語文社團'), (2, 8, 5))`

**無重複**：5 題 `parameter_tuple` 皆不同。

### b4.combination.combination_properties_simplification

- seed 1: `('combination_properties_simplification', 6, 1, 'direct')`
- seed 2: `('combination_properties_simplification', 5, 2, 'symmetry')`
- seed 3: `('combination_properties_simplification', 6, 2, 'direct')`
- seed 4: `('combination_properties_simplification', 6, 2, 'symmetry')`
- seed 5: `('combination_properties_simplification', 9, 3, 'direct')`

**無重複**：seed 3 與 seed 4 雖同為 $(n,r)=(6,2)$，但第四元 `variant` 不同，故 tuple 相異；5 題皆不同。

### b4.counting.repeated_choice_basic

- seed 1: `('repeated_choice_basic', 2, 2)`
- seed 2: `('repeated_choice_basic', 3, 2)`
- seed 3: `('repeated_choice_basic', 4, 2)`
- seed 4: `('repeated_choice_basic', 5, 2)`
- seed 5: `('repeated_choice_basic', 2, 3)`

**無重複**：5 題皆不同（seed 1 與 seed 5 之 `(2,2)` 與 `(2,3)` 亦不同）。

## 6. 與課本題型相似度人工檢查建議

| generator_key | 對應課本題型 | 相似度判斷 | 需要人工注意的點 |
|---|---|---|---|
| b4.counting.add_principle_mutually_exclusive_choice | 加法原理（互斥分類擇一） | 高 | 情境固定為「社團擇一」，敘述模板一致；數字與「種」之間空格可再統一。 |
| b4.combination.combination_properties_simplification | 組合數計算；對稱性 $C(n,r)=C(n,n-r)$ | 高 | 本批 5 題中 `direct` 3 題、`symmetry` 2 題；若課本強調對稱演練，比例宜人工斟酌。 |
| b4.counting.repeated_choice_basic | 重複選擇（乘法原理、$m^n$） | 中 | 與 `repeated_permutation_digits` 同為 $m^n$ 結構，但本題為飲料／同學敘事，與「數字排列」不同；教學上建議對照以免混淆。 |

## 7. 問題與建議

- **output_contract**：`core/vocational_math_b4/domain/b4_validators.py` 中 `validate_problem_payload_contract` 之 `_REQUIRED_PAYLOAD_KEYS` 未列入 `parameters`；實際 generator 仍輸出 `parameters` 且內含 `parameter_tuple`。若對外契約需明文納入 `parameters`，建議後續於規格文件或驗證層補列（本 QA 不修改程式）。
- **add_principle**：題幹皆為「某校社團活動可選擇…只選擇其中一種社團」，情境合理但重複性高；「選擇」與數字間空格略不一致，屬版式微調建議。
- **combination_properties**：本批 `direct` 略多於 `symmetry`；兩類題幹已用「計算」與「利用組合性質」區分，教學上可讀性尚可。
- **repeated_choice_basic**：解析已含 $m$、$n$、$m^{n}$ 與數值例，與 `repeated_permutation_digits` 之差異主要在情境物件，建議教材並列說明。
- **LaTeX**：本批未見題幹或解析出現裸 `2^2`、`C(n,r)`（未包於 `$...$`）之情形；組合記號以 `$C(n,r)$` 或具體 `$C(6,2)$` 呈現；重複選擇以 `$m^{n}$` 與 `$3^{2}=9$` 等形式呈現指數，符合檢核要點。

## 8. 結論

三個 generator 於 seed 1～5 各產 5 題，選項皆 4 個互異且含正解，答案皆為 int，並分別與 `addition_principle_count`、`combination`、`repeated_choice_count` 驗算一致。題面與解析未出現指定 placeholder；交付欄位齊備且含 `parameters.parameter_tuple`。LaTeX 於本批樣題檢視下判定合格。三者皆可進入後續整合討論；若嚴格以「contract 鍵集合」對齊，僅需在文件或契約層補述 `parameters` 是否為必填。接入 question_router／wrapper 前建議人工確認教學情境與題型比例。本 QA 未修改任何程式碼、測試、資料庫、前端、route 或 `app.py`。
