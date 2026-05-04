# B4 Phase 4E-12B Generator 樣題品質檢查報告

## 1. 本階段目的

本階段僅檢查 Phase 4E-12B 已完成之三個進階排列／組合 generator，以固定 seed（1～5）、`difficulty=1`、`multiple_choice=True` 實際各產生 5 題樣題，檢查 output 合約、答案、選項、LaTeX、`parameter_tuple` 重複性與課本相似度。不修改程式、不接 router、不建 wrapper、不接前端、不改測試與資料庫。

## 2. 檢查範圍

| generator_key | function | skill_id | subskill_id | multiple_choice |
|---|---|---|---|---|
| b4.permutation.permutation_full_arrangement | permutation_full_arrangement | vh_數學B4_PermutationOfDistinctObjects | b4_ch1_perm_full_arrangement_01 | True |
| b4.combination.combination_restricted_selection | combination_restricted_selection | vh_數學B4_Combination | b4_ch1_comb_restricted_selection_01 | True |
| b4.combination.combination_seat_assignment | combination_seat_assignment | vh_數學B4_Combination | b4_ch1_comb_seat_assignment_01 | True |

## 3. 總體檢查表

| generator_key | 樣題數 | unique_parameter_tuple 數 | choices_valid | answer_valid | latex_valid | metadata_complete | placeholder_free | 初步判斷 |
|---|---:|---:|---|---|---|---|---|---|
| b4.permutation.permutation_full_arrangement | 5 | 5 | 是 | 是 | 是 | 是 | 是 | 需微調 |
| b4.combination.combination_restricted_selection | 5 | 5 | 是 | 是 | 是 | 是 | 是 | 通過 |
| b4.combination.combination_seat_assignment | 5 | 5 | 是 | 是 | 是 | 是 | 是 | 通過 |

說明：`metadata_complete` 指實際 payload 含 `skill_id`、`subskill_id`、`problem_type_id`、`generator_key`、`difficulty`、`diagnosis_tags`、`remediation_candidates`、`source_style_refs` 與巢狀 `parameters`（含 `parameter_tuple`）。`validate_problem_payload_contract` 之必填鍵集合不含 `parameters`，與其他 B4 generator 相同，屬契約文件層級可再對齊（見第 7 節）。

## 4. 樣題清單

### b4.permutation.permutation_full_arrangement

#### seed = 1

- question_text: 3 位同學排成一列，共有多少種排法？
- choices: [5, 6, 4, 3]
- answer: 6
- explanation: $3$ 位相異對象全取排列，方法數為 $3!=6$。
- parameters: `n=3`, `context=students_line`, `parameter_tuple` 見第 5 節。
- 檢查結果:
  - choices_valid: 是（4 個互異，含答案）
  - answer_valid: 是（`factorial(3)=6`，int）
  - latex_valid: 是（階乘寫成 `$3!$`；數學式在 `$...$` 內）
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 解析說明「全取排列為 $n!$」符合要求；題幹為繁體。

#### seed = 2

- question_text: 4 本不同書排在書架上，共有多少種排法？
- choices: [12, 48, 22, 24]
- answer: 24
- explanation: $4$ 位相異對象全取排列，方法數為 $4!=24$。
- parameters: `n=4`, `context=books_shelf`
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`factorial(4)=24`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 解析仍寫「位相異對象」，與題幹「本書」量詞不一致，建議改為「本／張／件」等與 `context` 對應之用語（屬文字微調，非數學錯誤）。

#### seed = 3

- question_text: 5 張不同照片排成一排，共有多少種排法？
- choices: [119, 120, 118, 240]
- answer: 120
- explanation: $5$ 位相異對象全取排列，方法數為 $5!=120$。
- parameters: `n=5`, `context=photos_row`
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`factorial(5)=120`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 同上，「位」與「張」不一致。

#### seed = 4

- question_text: 6 件不同任務安排順序，共有多少種排法？
- choices: [360, 720, 718, 1440]
- answer: 720
- explanation: $6$ 位相異對象全取排列，方法數為 $6!=720$。
- parameters: `n=6`, `context=tasks_order`
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`factorial(6)=720`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 同上，「位」與「件」不一致。

#### seed = 5

- question_text: 4 位同學排成一列，共有多少種排法？
- choices: [24, 12, 22, 48]
- answer: 24
- explanation: $4$ 位相異對象全取排列，方法數為 $4!=24$。
- parameters: `n=4`, `context=students_line`（與 seed 2 之 `n=4` 不同處在於 `context`，`parameter_tuple` 仍相異）
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`factorial(4)=24`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 題幹為同學，「位相異對象」尚可讀；與 seed 2 同階乘數值但參數 tuple 不同。

### b4.combination.combination_restricted_selection

#### seed = 1

- question_text: 甲組有 3 人、乙組有 4 人，今共選 2 人，且至少選 1 位甲組成員，共有多少種選法？
- choices: [14, 15, 13, 7]
- answer: 15
- explanation: 先算全部選法 $C^{7}_{2}$，扣掉沒有甲組成員的情形 $C^{4}_{2}$，所以 $C^{7}_{2}-C^{4}_{2}=15$。
- parameters: `a=3,b=4,r=2,k=1`, `variant=at_least_one_from_group`
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(7,2)-combination(4,2)=15`，int）
  - latex_valid: 是（組合數為 $C^{n}_{r}$ 形式；差式在 `$...$` 內）
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 反面扣除「沒有甲組成員」敘述清楚；題幹繁體。

#### seed = 2

- question_text: 甲組有 4 人、乙組有 5 人，今共選 3 人，且恰選 1 位甲組成員，共有多少種選法？
- choices: [38, 39, 41, 40]
- answer: 40
- explanation: 甲組選 $1$ 人、乙組選 $2$ 人，方法數為 $C^{4}_{1}\times C^{5}_{2}=40$。
- parameters: `variant=exactly_k_from_group`, `k=1`
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(4,1)*combination(5,2)=40`，int）
  - latex_valid: 是（兩組合之間使用 `\times`）
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 分組選取（甲 k、乙 r−k）說明清楚。

#### seed = 3

- question_text: 甲組有 5 人、乙組有 6 人，今共選 3 人，且至少選 1 位甲組成員，共有多少種選法？
- choices: [143, 145, 72, 290]
- answer: 145
- explanation: 先算全部選法 $C^{11}_{3}$，扣掉沒有甲組成員的情形 $C^{6}_{3}$，所以 $C^{11}_{3}-C^{6}_{3}=145$。
- parameters: `variant=at_least_one_from_group`
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(11,3)-combination(6,3)=145`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 反面扣除敘述清楚。

#### seed = 4

- question_text: 甲組有 6 人、乙組有 4 人，今共選 4 人，且恰選 2 位甲組成員，共有多少種選法？
- choices: [180, 90, 88, 45]
- answer: 90
- explanation: 甲組選 $2$ 人、乙組選 $2$ 人，方法數為 $C^{6}_{2}\times C^{4}_{2}=90$。
- parameters: `variant=exactly_k_from_group`, `k=2`
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(6,2)*combination(4,2)=90`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 分組選取說明清楚。

#### seed = 5

- question_text: 甲組有 3 人、乙組有 8 人，今共選 4 人，且至少選 1 位甲組成員，共有多少種選法？
- choices: [260, 258, 261, 259]
- answer: 260
- explanation: 先算全部選法 $C^{11}_{4}$，扣掉沒有甲組成員的情形 $C^{8}_{4}$，所以 $C^{11}_{4}-C^{8}_{4}=260$。
- parameters: `variant=at_least_one_from_group`
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(11,4)-combination(8,4)=260`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 反面扣除敘述清楚。

### b4.combination.combination_seat_assignment

#### seed = 1

- question_text: 從 5 位同學中選出 2 位，安排到 2 個不同座位，共有多少種安排方式？
- choices: [18, 20, 10, 40]
- answer: 20
- explanation: 先從 $5$ 人中選 $2$ 人，有 $C^{5}_{2}$ 種；再將 $2$ 人排列，有 $2!$ 種，所以 $C^{5}_{2}\times 2!=20$。
- parameters: `n=5,r=2`, `context=seats`
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(5,2)*permutation(2,2)=20`，int）
  - latex_valid: 是（組合 $C^{n}_{r}$、階乘 `$2!$`、乘號 `\times`）
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 「先選人再排列」兩步驟清楚；題幹點出不同座位。

#### seed = 2

- question_text: 從 6 人中選出 3 人擔任 3 個不同職務，共有多少種安排方式？
- choices: [240, 118, 119, 120]
- answer: 120
- explanation: 先從 $6$ 人中選 $3$ 人，有 $C^{6}_{3}$ 種；再將 $3$ 人排列，有 $3!$ 種，所以 $C^{6}_{3}\times 3!=120$。
- parameters: `context=officers`
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(6,3)*permutation(3,3)=120`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 對應不同職務之「選後排列」清楚。

#### seed = 3

- question_text: 從 7 人中選出 2 人依序上台報告，共有多少種安排方式？
- choices: [43, 42, 41, 40]
- answer: 42
- explanation: 先從 $7$ 人中選 $2$ 人，有 $C^{7}_{2}$ 種；再將 $2$ 人排列，有 $2!$ 種，所以 $C^{7}_{2}\times 2!=42$。
- parameters: `context=presentation_order`
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(7,2)*2=42`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 「依序上台」與解析之先選后排一致。

#### seed = 4

- question_text: 從 8 位同學中選出 3 位，安排到 3 個不同座位，共有多少種安排方式？
- choices: [168, 336, 334, 672]
- answer: 336
- explanation: 先從 $8$ 人中選 $3$ 人，有 $C^{8}_{3}$ 種；再將 $3$ 人排列，有 $3!$ 種，所以 $C^{8}_{3}\times 3!=336$。
- parameters: `n=8,r=3`, `context=seats`
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(8,3)*permutation(3,3)=336`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 同上。

#### seed = 5

- question_text: 從 6 人中選出 2 人擔任 2 個不同職務，共有多少種安排方式？
- choices: [30, 32, 60, 33]
- answer: 30
- explanation: 先從 $6$ 人中選 $2$ 人，有 $C^{6}_{2}$ 種；再將 $2$ 人排列，有 $2!$ 種，所以 $C^{6}_{2}\times 2!=30$。
- parameters: `context=officers`
- 檢查結果:
  - choices_valid: 是
  - answer_valid: 是（`combination(6,2)*2=30`，int）
  - latex_valid: 是
  - metadata_complete: 是
  - placeholder_free: 是
  - parameter_tuple_exists: 是
  - notes: 同上。

## 5. parameter_tuple 重複性檢查

### b4.permutation.permutation_full_arrangement

- seed 1: `('permutation_full_arrangement', 3, 'students_line')`
- seed 2: `('permutation_full_arrangement', 4, 'books_shelf')`
- seed 3: `('permutation_full_arrangement', 5, 'photos_row')`
- seed 4: `('permutation_full_arrangement', 6, 'tasks_order')`
- seed 5: `('permutation_full_arrangement', 4, 'students_line')`

**無重複**：5 題 `parameter_tuple` 皆不同（seed 2 與 seed 5 雖皆為 `n=4`，但 `context` 不同）。

### b4.combination.combination_restricted_selection

- seed 1: `('combination_restricted_selection', 3, 4, 2, 1, 'at_least_one_from_group')`
- seed 2: `('combination_restricted_selection', 4, 5, 3, 1, 'exactly_k_from_group')`
- seed 3: `('combination_restricted_selection', 5, 6, 3, 2, 'at_least_one_from_group')`
- seed 4: `('combination_restricted_selection', 6, 4, 4, 2, 'exactly_k_from_group')`
- seed 5: `('combination_restricted_selection', 3, 8, 4, 1, 'at_least_one_from_group')`

**無重複**：5 題皆不同。

### b4.combination.combination_seat_assignment

- seed 1: `('combination_seat_assignment', 5, 2, 'seats')`
- seed 2: `('combination_seat_assignment', 6, 3, 'officers')`
- seed 3: `('combination_seat_assignment', 7, 2, 'presentation_order')`
- seed 4: `('combination_seat_assignment', 8, 3, 'seats')`
- seed 5: `('combination_seat_assignment', 6, 2, 'officers')`

**無重複**：5 題皆不同（`(6,3,officers)` 與 `(6,2,officers)` 相異）。

**固定代表參數**：此三個函式在 `difficulty==1` 且 `seed` 為 1～5 時，原始碼皆使用預設 `(n, context)` 或 `(a,b,r,k,variant)` 之固定列表，以避免前幾個 seed 與隨機抽樣碰撞；**不影響**其他 `difficulty` 或更大 `seed` 之隨機抽樣行為。

## 6. 與課本題型相似度人工檢查建議

| generator_key | 對應課本題型 | 相似度判斷 | 需要人工注意的點 |
|---|---|---|---|
| b4.permutation.permutation_full_arrangement | 相異物全取排列、$n!$ | 高 | 與 `permutation_formula_evaluation`（一般 $P^{n}_{r}$／取 r 個排一列）數學上不同：本題為全取 $n!$；題型可區分。解析用語宜與題幹物件一致。 |
| b4.combination.combination_restricted_selection | 限制條件組合（至少／恰幾名來自某組） | 高 | 兩變體題意與解析路徑清楚；參數為 seed 1～5 固定代表值，題庫多樣性仍賴其他 seed／難度。 |
| b4.combination.combination_seat_assignment | 選後排列（座位／職務／順序） | 高 | 與課本「先組合再階乘／排列」典型敘述一致；`context` 三種情境利於教學對照。 |

## 7. 問題與建議

- **permutation_full_arrangement**：解析固定寫「$n$ 位相異對象」，當 `context` 為書本、照片、任務時，量詞「位」與題幹「本／張／件」不一致，建議依 `context` 調整用語（屬敘事微調，**非**數學或 LaTeX 錯誤）。與 `permutation_formula_evaluation` 相比：前者為全排列 $n!$，後者為選排 $P^{n}_{r}$，**差異足夠**；若 symbolic 子題僅寫符號、本題偏情境，重複感低。
- **combination_restricted_selection**：`at_least_one_from_group` 解析已明列「全部選法」與「扣掉沒有甲組成員」；`exactly_k_from_group` 已明列甲組 $k$ 人、乙組 $r-k$ 人與 $C\times C$ 乘積式。LaTeX 使用 $C^{n}_{r}$ 與 `\times`，未見裸 `C(n,r)` 或題幹裸指數。
- **combination_seat_assignment**：解析已分「先選 $C^{n}_{r}$」與「再排 $r!$」，並以 `\times` 連接，符合「先選再排」之教學敘述。
- **output_contract**：`b4_validators.validate_problem_payload_contract` 未強制 `parameters` 鍵；實際輸出仍含完整 `parameters` 與 `parameter_tuple`。
- **固定 seed 1～5 參數**：三個 generator 於 `difficulty=1` 時對 seed 1～5 使用預設代表參數，**目的為避免前 5 seed 重複**；其他 seed 仍走隨機抽樣邏輯，不影響長題庫覆蓋。

## 8. 結論

`combination_restricted_selection` 與 `combination_seat_assignment` 樣題在答案、選項、LaTeX、metadata 與解析完整性上均可進下一階段；`permutation_full_arrangement` 數學與格式正確，但解析量詞建議微調後再大量上架。三者均可作為後續接入 question_router／wrapper 之候選，建議接入前由教學編輯確認情境用語與契約是否需明文納入 `parameters`。本 QA 未修改任何程式碼、測試、資料庫、前端、route、`app.py` 或 `question_router`。
