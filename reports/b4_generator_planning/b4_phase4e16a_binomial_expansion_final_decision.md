# B4 Phase 4E-16A Binomial Expansion Final Decision

## 1. 本階段目的

本階段針對 `binomial_expansion_basic` 做 Chapter 1 runtime 收尾的最終決策。

本階段只產出決策文件，不修改程式、不修改 tests、不修改 CSV、不修改既有 MD、不接 router、不新增 generator、不新增 wrapper、不改前端。

## 2. Chapter 1 runtime 收尾狀態

| 類別 | 數量 | 項目 |
|---|---:|---|
| runtime_ready | 25 / 28 | 已接入一般練習 runtime 的 25 個 problem_type |
| planned_only | 1 | `binomial_expansion_basic` |
| manual_review / excluded-like | 2 | `tree_diagram_listing`, `pascal_triangle_derivation` |

目前 Chapter 1 一般 runtime 的唯一待決策項目是 `binomial_expansion_basic`。

## 3. 已完成的二項式 runtime 能力

| problem_type_id | answer 型態 | runtime 狀態 | 說明 |
|---|---|---|---|
| `binomial_coefficient_sum` | `int` | runtime_ready | 二項式係數和 |
| `binomial_specific_term_coefficient` | `int` | runtime_ready | 指定項或指定次方的係數 |
| `binomial_equation_solve_n` | `int` | runtime_ready | 由組合式或係數條件反求 `n` |
| `binomial_middle_term_coefficient` | `int` | runtime_ready | 中間項係數 |
| `binomial_odd_even_coefficient_sum` | `int` | runtime_ready | 奇數項或偶數項係數和 |
| `binomial_specific_coefficient_with_negative_term` | `int` | runtime_ready | 含負項的指定係數 |

現在已有可用的二項式 runtime 練習，涵蓋係數和、指定係數、反求 `n`、中間項、奇偶項係數和、含負項係數等 int-answer 題型。

但完整展開題 `binomial_expansion_basic` 尚未上線。

## 4. binomial_expansion_basic 的核心問題

`binomial_expansion_basic` 目前的 generator answer 仍為 `list[int]`，例如 `[1, 6, 12, 8]`。題目 payload 沒有 choices，且標記為不支援 multiple choice。

現有一般 runtime wrapper 主要以 `int()` 做答案比對。學生在完整展開題可能輸入多種合理格式：

- `[1,6,12,8]`
- `1,6,12,8`
- `1 6 12 8`
- `x^3+6x^2+12x+8`
- `$x^{3}+6x^{2}+12x+8$`

若不改前端、`check_answer`、wrapper check 或 normalization，直接接入會造成大量非數學性誤判。

若改成多項式字串判分，需要 polynomial normalization 或 symbolic parser。若改成係數列表判分，需要明確輸入格式、列表 normalization、前端提示與錯誤訊息。若改成 choices，則會失去完整展開題本質。

## 5. 四種決策選項比較

| Option | 做法 | 優點 | 缺點 | 是否建議短期採用 |
|---|---|---|---|---|
| A：繼續維持 planned_only | 不接入，仍留在 planned_only | 保留未來 runtime 接入可能；不會錯誤標為完成 | Chapter 1 會持續看起來還差一題；不利於 runtime 收尾 | 不建議 |
| B：改為 manual_review / future_free_response | 不接一般 runtime；後續可從 planned_only 移出並標記 normalization_required | 誠實反映目前不適合 int-answer runtime；Chapter 1 一般 runtime 可視為實質收尾；與 `tree_diagram_listing` 的處理邏輯一致 | 原始 28 題 runtime_ready 不會達 26 或 28；完整展開題需另開未來模組 | 建議 |
| C：短期改成 coefficient-list structured-answer | 接入 `list[int]` answer，支援 `[1,6,12,8]`、`1,6,12,8`、`1 6 12 8` | 比完整多項式容易；可檢查完整係數序列 | 要改 wrapper check、normalization、前端提示；仍不能接受完整多項式輸入；擴大工程面 | 不建議 |
| D：短期改成 polynomial free-response | 學生輸入完整展開多項式，使用 SymPy 或 parser 判等價 | 教學完整度最高；最接近課本完整展開題 | 工程風險最高；牽動前端、route、wrapper、parser、安全性、格式提示 | 不建議 |

## 6. 最終建議

建議採用 **Option B**。

`binomial_expansion_basic` 應視為 `manual_review / future_free_response / normalization_required`，不建議現在接入一般 runtime。

不建議現在實作 `list[int]` normalization，也不建議現在實作 polynomial parser。

不建議現在改前端、route、`check_answer` 或二項式 wrapper。

在 `tree_diagram_listing` 已移出 planned_only 的前提下，若 `binomial_expansion_basic` 下一階段也移出 planned_only，Chapter 1 一般 runtime 可視為 **25 / 28 實質收尾**。

## 7. 對 coverage matrix 的建議

下一階段可將 `binomial_expansion_basic` 從 `planned_only` 移出。

建議標記為 excluded-style `manual_review / future_free_response / normalization_required`。

調整後：

- planned_only 將變成 0
- runtime_ready 仍維持 25 / 28
- manual_review / excluded-like 將變成 3：
  - `binomial_expansion_basic`
  - `tree_diagram_listing`
  - `pascal_triangle_derivation`

## 8. 未來完整展開題支援路線

Future Phase 1：answer format spec
- 決定支援係數列表、完整多項式，或兩者都支援。
- 明確定義 canonical answer，例如係數由高次到常數項排列。

Future Phase 2：normalizer
- `list[int]` parser
- polynomial string parser
- LaTeX to plain polynomial normalization
- SymPy equivalence check 或自訂 parser

Future Phase 3：frontend hint
- 題目頁提示學生可接受的輸入格式。
- 例如：「請輸入係數，格式：1,6,12,8」。
- 若支援多項式輸入，需提供明確範例與錯誤提示。

Future Phase 4：wrapper / check_answer extension
- 只對 `BinomialTheorem` free-response 題型啟用。
- 不影響其他 int-answer 題型。
- 避免把全站 `check_answer` 變成複雜通用 parser。

Future Phase 5：QA / smoke / teacher review
- 樣題檢查
- 錯誤輸入測試
- 等價多項式測試
- 學生試用
- 教師確認可接受格式與判分規則

## 9. 給非 coding 教師的說明

系統現在已能練二項式的係數和、指定係數、中間項、奇偶項係數和等。

但完整展開需要判斷一整串係數或多項式。

學生寫法很多種，目前系統若硬判會誤判。

所以完整展開題先放入 future free-response，不代表題目不重要，而是判分機制尚未完成。

## 10. 結論

`binomial_expansion_basic` 短期建議採 Option B。  
不建議立即接入一般 runtime。  
不建議現在改前端、route、wrapper 或 `check_answer`。  
下一階段可將其移出 `planned_only`，改列 manual_review / future_free_response。  
Chapter 1 一般 runtime 可在 25 / 28 視為實質收尾。  
