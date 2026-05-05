# B4 Phase 4E Postcheck-D Router Distribution / Enrichment Review

## 1. 本階段目的

本階段針對 Phase 4E 後使用者實測觀察到的「題型偏單調、預設抽題分布不明、depth 題型不易看見」進行靜態 review。

本報告只分析 router distribution、generator/template richness 與 skill/problem_type mapping，不修改程式、不修改 route/frontend/app.py、不新增 generator、不新增 wrapper、不修改 question_router、不修改 coverage matrix。

本階段讀取之參考文件均存在，未發現缺少文件。

## 2. 使用者觀察摘要

| skill_id | 可用性 | 使用者觀察 | 初步問題類型 |
|---|---|---|---|
| `vh_數學B4_RepeatedPermutation` | 可正常出題 | 常見「有 4 個可用數字，每個數字可重複使用，排成 3 位數」類題目，題型偏單調 | 單一 router entry + 單一題幹模板 |
| `vh_數學B4_CombinationDefinition` | 可正常出題 | 常見「從 6 件不同作品中選出 3 件展示」類題目，題型偏單調 | 窄技能 + 單一 router entry + 單一題幹模板 |
| `vh_數學B4_BinomialTheorem` | 可正常出題 | depth 題型已接入，但分數 / depth 題型沒有明顯進來，分布不明 | 多 entry 抽樣不可見 + 題幹相近 + template/parameter enrichment 需求 |
| `vh_數學B4_BinomialCoefficientIdentities` | 可正常出題 | 缺少部分題型或預設抽題覆蓋不足 | 多 entry 抽樣可觀測性不足 + visibility/sampling review |
| `vh_數學B4_PermutationOfNonDistinctObjects` | Postcheck-C 後可正常出題 | 目前重用 `repeated_permutation_digits`，可能仍偏單調 | skill mapping 暫用 alias-like mapping + 單一 problem_type |

## 3. Router registry 靜態盤點

| skill_id | router entries 數 | problem_type_id 清單 | generator_key 清單 | 初步判斷 |
|---|---:|---|---|---|
| `vh_數學B4_RepeatedPermutation` | 1 | `repeated_permutation_digits` | `b4.counting.repeated_permutation_digits` | 只有一個 entry；default 必定 single_entry，不是抽樣分布問題 |
| `vh_數學B4_CombinationDefinition` | 1 | `combination_definition_basic` | `b4.combination.combination_definition_basic` | 只有一個 entry；符合「組合定義」窄技能定位，但體感會單調 |
| `vh_數學B4_BinomialTheorem` | 3 | `binomial_specific_term_coefficient`, `binomial_middle_term_coefficient`, `binomial_specific_coefficient_with_negative_term` | `b4.binomial.binomial_specific_term_coefficient`, `b4.binomial.binomial_middle_term_coefficient`, `b4.binomial.binomial_specific_coefficient_with_negative_term` | 多 entry；未指定 `problem_type_id` 時由 seed-based selection 抽樣，但 UI 不易看見選到哪個題型 |
| `vh_數學B4_BinomialCoefficientIdentities` | 3 | `binomial_coefficient_sum`, `binomial_equation_solve_n`, `binomial_odd_even_coefficient_sum` | `b4.binomial.binomial_coefficient_sum`, `b4.binomial.binomial_equation_solve_n`, `b4.binomial.binomial_odd_even_coefficient_sum` | 多 entry；需確認實際 seed/前端行為是否平均覆蓋 |
| `vh_數學B4_PermutationOfNonDistinctObjects` | 1 | `repeated_permutation_digits` | `b4.counting.repeated_permutation_digits` | Postcheck-C 暫以最貼近題型接入；目前仍只有一個 problem_type |

Router selection 靜態結論：

- `_select_entry` 在 `problem_type_id` 指定時會直接選指定題型。
- 未指定 `problem_type_id` 且 skill 只有一筆 entry 時，selection_reason 為 `single_entry`。
- 未指定 `problem_type_id` 且 skill 有多筆 entry 時，使用 `random.Random(seed).choice(entries)`，selection_reason 為 `seed_based_selection`。
- 因此單調可能來自兩類原因：skill 只有一筆 entry，或多筆 entry 但實際 seed/抽樣與 UI 可觀測性不足。

## 4. 題型單調原因分析

| skill_id | 是否只有單一 problem_type | 是否模板偏少 | 是否 difficulty=1 限制 | 是否 router 分布問題 | 結論 |
|---|---|---|---|---|---|
| `vh_數學B4_RepeatedPermutation` | 是 | 是，`repeated_permutation_digits` 題幹固定為可用數字重複排列語境 | 是，difficulty=1 參數範圍較小 | 否；單 entry 沒有 distribution 可言 | 主要是 mapping/template enrichment 問題 |
| `vh_數學B4_CombinationDefinition` | 是 | 是，題幹固定為作品選展示語境 | 是，difficulty=1 只抽較小 n/r | 否；單 entry 沒有 distribution 可言 | 本質為窄技能，可接受但可做 template enrichment |
| `vh_數學B4_BinomialTheorem` | 否 | 中等偏少；三個 problem_type 題幹皆為「展開後某係數」 | 是，seed 1-5 與 difficulty=1 preset 較保守 | 可能；需要抽樣 audit 才能確認 | 優先做 router distribution instrumentation / sampling audit |
| `vh_數學B4_BinomialCoefficientIdentities` | 否 | 中等；係數和、求 n、奇偶係數和語義不同，但 UI 未顯示題型 | 是，difficulty=1 preset 較保守 | 可能；需確認實際抽題覆蓋 | 優先做 problem_type visibility / sampling review |
| `vh_數學B4_PermutationOfNonDistinctObjects` | 是 | 是，目前完全重用 `repeated_permutation_digits` | 是 | 否；單 entry 沒有 distribution 可言 | 目前是 runtime mapping 修補，不是真正豐富的非相異物排列題庫 |

## 5. 各 skill 詳細分析

### 5.1 RepeatedPermutation

現況：

- Wrapper 存在，router entry 存在。
- 目前只掛 `repeated_permutation_digits`。
- generator_key 為 `b4.counting.repeated_permutation_digits`。
- default 不指定 `problem_type_id` 時，router 必定選這一筆，selection_reason 為 `single_entry`。

問題原因：

- 不是 router 隨機分布失敗，因為沒有第二個 problem_type 可抽。
- generator 靜態內容顯示題幹固定為「有 n 個可用數字，每個數字可重複使用，排成 k 位數」。
- difficulty=1 參數範圍較小，會讓題目更像同一題。
- `repeated_permutation_assignment` 雖已存在，但掛在 `vh_數學B4_PermutationWithRepetition`，不是此 skill。

是否需要立即修：

- 不影響 runtime 可用性，不需急修。
- 若目標是改善使用者體感，後續可做小批 template enrichment。

建議修法：

- 同一 problem_type 增加更多情境模板，例如密碼、座位代碼、產品編號、車牌局部格式。
- 或重新檢討 `RepeatedPermutation` 與 `PermutationWithRepetition` 的 skill 分工，決定是否合併部分 assignment 題型。
- 不建議為了單調問題修改 route/frontend。

### 5.2 CombinationDefinition

現況：

- Wrapper 存在，router entry 存在。
- 目前只掛 `combination_definition_basic`。
- generator_key 為 `b4.combination.combination_definition_basic`。
- default 不指定 `problem_type_id` 時，router 必定選這一筆。

問題原因：

- 此 skill 本質上是「組合定義」窄技能，不是應用題集合。
- generator 題幹固定為「從 n 件不同作品中選出 r 件展示」。
- difficulty=1 參數範圍為較小的 n/r，符合入門題，但體感會單調。

是否需要立即修：

- 不需要立即修。這是可接受的窄技能頁。
- 若教師希望同頁更豐富，應定位為 template enrichment，而不是 router bug。

建議修法：

- 增加同一概念下的安全模板，例如選作品、選學生、選書籍、選零件、選代表。
- 若要更多應用面，應導向 `vh_數學B4_Combination` 或 `vh_數學B4_CombinationApplications`，不要把 definition 頁混成應用綜合頁。

### 5.3 BinomialTheorem

現況：

- Wrapper 存在，router entry 存在。
- 目前掛三個 int-answer problem_type：
  - `binomial_specific_term_coefficient`
  - `binomial_middle_term_coefficient`
  - `binomial_specific_coefficient_with_negative_term`
- depth 題型 `binomial_middle_term_coefficient` 與 `binomial_specific_coefficient_with_negative_term` 已接入。
- 未接入 `binomial_expansion_basic`，符合 Phase 4E-16A/16B 決策。

問題原因：

- router 有三筆 entry，理論上 default 會 seed-based selection。
- 但使用者在頁面上通常看不到 `router_trace.selected_problem_type_id`，因此很難判斷是否真的抽到 depth 題型。
- 三個 problem_type 的題幹都圍繞「展開後某項係數」，視覺上相近。
- generator 靜態內容顯示 difficulty=1 preset 偏保守，且多數模板仍為單句係數題。

是否需要立即修：

- 不屬於 runtime failure，但值得優先 review。
- 對二項式頁面而言，使用者對 depth 題型可見度的期待較高。

建議修法：

- 先做 Postcheck-D1：deterministic sampling audit，列出 seed 1-30 對應選到的 problem_type。
- 確認前端是否固定 seed 或是否造成同一 problem_type 反覆出現。
- 在報告或 debug 模式顯示 router_trace，不一定先改 UI。
- 後續再做 binomial template enrichment，保持 answer 為 int，不接 `binomial_expansion_basic`。

### 5.4 BinomialCoefficientIdentities

現況：

- Wrapper 存在，router entry 存在。
- 目前掛三個 problem_type：
  - `binomial_coefficient_sum`
  - `binomial_equation_solve_n`
  - `binomial_odd_even_coefficient_sum`
- `binomial_odd_even_coefficient_sum` 為 Phase 4E-13F depth 補強題型。

問題原因：

- router 有多筆 entry，但抽題結果不顯示 problem_type，導致使用者不易確認覆蓋。
- 部分題型可能在短時間或特定 seed 序列下不常出現。
- 若使用者期待更多恆等式題型，需區分「目前 runtime 已承諾的三題」與「尚未設計的 expanded 題庫」。

是否需要立即修：

- 不屬於 runtime failure。
- 但與 BinomialTheorem 一樣，適合優先做 sampling audit。

建議修法：

- 先輸出 deterministic sampling audit，確認 default seed 下三個 problem_type 的出現比例。
- 若比例合理但仍體感不足，改做 template enrichment。
- 若比例不合理，再討論 router selection policy，例如 seed 輪替或均勻抽樣。

### 5.5 PermutationOfNonDistinctObjects

現況：

- Postcheck-C 已新增 wrapper 與 router skill_id entry。
- 目前重用 `repeated_permutation_digits`。
- generator_key 為 `b4.counting.repeated_permutation_digits`。
- default 不指定 `problem_type_id` 時，router 必定 single_entry。

問題原因：

- 這是 mapping 修正，不是完整「不盡相異物排列」題庫建置。
- 現在的語境仍是「可重複使用數字排位」，較接近 repeated digit arrangement。
- 真正「不盡相異物排列」通常包含相同物件排列，例如 letters with duplicates 或物件有重複類別，語義不完全相同。

是否需要立即修：

- No module named 已由 Postcheck-C 解決。
- 題型豐富度可列下一階段決策，不應在本階段新增 generator。

建議修法：

- Postcheck-D2 先做 enrichment decision：
  - 若保留目前路線，需在文件中標註此 skill 是 `repeated_permutation_digits` 的 wrapper page。
  - 若追求教學語義準確，未來可新增 `non_distinct_objects_word_problem` generator。
  - 不建議長期只用 repeated digits 代表完整不盡相異物排列。

## 6. 修正方向分類

### Router selection policy

可能措施：

- 對同一 skill 下多個 problem_type 做明確均勻抽樣。
- 根據 seed 輪替 problem_type，避免短時間體感集中。
- 根據 level / difficulty 決定 problem_type pool。
- 在 QA 報告中列出 router_trace 的 selected problem_type。
- 增加 debug log 或 report 顯示 `selected_problem_type_id`、`selected_generator_key`、`selection_reason`。
- 先做 sampling audit，再決定是否真的要改 policy。

### Generator template enrichment

可能措施：

- 同一 problem_type 增加多個 context。
- 增加題幹模板，但保持 answer / output contract 不變。
- difficulty=1 增加安全但不同的變化，不提高計算負擔。
- RepeatedPermutation 可增加密碼、編號、代碼、車牌片段等語境。
- CombinationDefinition 可增加作品、學生、書籍、零件、代表等同構模板。
- Binomial 題型可增加問法變體與參數分布，但仍維持 int-answer。

### Skill mapping

可能措施：

- `PermutationOfNonDistinctObjects` 不應長期只重用 `repeated_permutation_digits`，除非明確標註為 alias-like wrapper page。
- 若要符合「不盡相異物排列」語義，未來可新增 `non_distinct_objects_word_problem` generator。
- `RepeatedPermutation` 與 `PermutationWithRepetition` 的分工需文件化，避免 dashboard skill 名稱造成使用者期待落差。
- 不應把 manual_review 題型或 `binomial_expansion_basic` 混入 deterministic runtime 來增加豐富度。

### UI / debug visibility

可能措施：

- 在 debug 模式或教師 QA 模式顯示目前 problem_type。
- 顯示 generator_key / router_trace，有助於判斷是否真的抽到 depth 題。
- 對 narrow skill 顯示「基礎技能」說明，降低使用者對大題庫的期待落差。
- 不建議為了單調問題直接改 route/frontend；若要做，應另開 UI 改善階段。

## 7. 建議優先順序

Priority 1：router distribution instrumentation / audit

- 先確認是否真的沒抽到，還是抽到但看不出來。
- 對 `BinomialTheorem` / `BinomialCoefficientIdentities` 最重要。
- 建議輸出 seed 1-30 或 1-50 的 `router_trace.selected_problem_type_id` 分布。
- 先做 report 或測試，不急著改 router policy。

Priority 2：PermutationOfNonDistinctObjects enrichment

- 因為目前剛修 mapping，只有一類題。
- 可決定是否新增真正「不盡相異物排列」word problem generator。
- 或明確保留為 `repeated_permutation_digits` wrapper page。
- 不在本階段實作。

Priority 3：RepeatedPermutation / CombinationDefinition template enrichment

- 兩者可用但單調。
- 不是 runtime failure，可後續小批 enrichment。
- 優先採同 problem_type 多模板，不先改 route/frontend。

Priority 4：dashboard/debug display

- 讓教師知道目前題目來自哪個 problem_type。
- 對 QA 與 classroom feedback 有幫助。
- 但屬 UI/debug 可見性改善，應排在 distribution audit 之後。

## 8. 下一階段建議

1. Postcheck-D1：router distribution instrumentation / deterministic sampling audit
   - 不改題型。
   - 增加或檢查 router_trace / log / report。
   - 針對 `BinomialTheorem`、`BinomialCoefficientIdentities`、`PermutationOfDistinctObjects`。
   - 目標是確認 seed 序列下各 problem_type 是否有合理覆蓋。

2. Postcheck-D2：PermutationOfNonDistinctObjects enrichment decision
   - 決定是否新增 `non_distinct_objects_word_problem` generator。
   - 或保留為 `repeated_permutation_digits` wrapper page。
   - 若新增 generator，需另開階段並走 Phase 4E SOP：generator pytest、sample QA、router/wrapper test、web smoke、freeze。

3. Postcheck-D3：small template enrichment
   - `RepeatedPermutation`：增加 repeated digit 類題幹情境。
   - `CombinationDefinition`：增加同構選取模板。
   - Binomial templates：增加問法與安全參數變體。
   - 全程保持 deterministic int-answer contract。

## 9. 結論

- 目前問題屬於題型豐富度、抽題分布可觀測性與 skill mapping 設計問題，不是 runtime 可用性失敗。
- `RepeatedPermutation`、`CombinationDefinition` 可接受暫時維持，因為它們目前都是可出題的窄技能或單 entry skill。
- `BinomialTheorem` 與 `BinomialCoefficientIdentities` 應優先做 distribution audit，確認 depth 題型是否真的被抽到。
- `PermutationOfNonDistinctObjects` 已可用，但目前只是重用 `repeated_permutation_digits`，後續需決定是否做真正非相異物排列題庫。
- 不建議為了體感豐富度立即改 route/frontend 或硬接 free-response/manual_review 題型。
- 下一步建議先做 Postcheck-D1：router distribution instrumentation / deterministic sampling audit。
