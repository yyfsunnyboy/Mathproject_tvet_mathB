# B4 Phase 4E-13A Binomial Answer Format Decision

## 1. 本階段目的

本階段目的，是決定 `binomial_expansion_basic` 若要接入一般練習頁時，答案格式與判分策略應如何設計。

目前此題型已可由 generator 產題，但答案是係數列表，例如 `[1, 6, 12, 8]`。這種答案格式適合程式驗證，卻不適合直接交給學生在一般文字輸入框作答。因此本階段只做決策，不修改程式、不接 router、不新增 wrapper、不調整前端。

## 2. 目前問題

`binomial_expansion_basic` 題幹目前類似：「展開 $(x+2)^3$，請寫出由高次到低次的係數。」

主要問題是學生輸入格式沒有明確標準。可能答案包括：

- `1,6,12,8`
- `[1,6,12,8]`
- `1 6 12 8`
- `$x^3+6x^2+12x+8$`
- `x^3+6x^2+12x+8`

這些答案在數學上可能都合理，但對一般 runtime 而言不是同一種資料格式。若 wrapper 的 `check()` 只做整數或字串比對，`list[int]` 無法穩定判分。

此外，前端若直接顯示 `[1, 6, 12, 8]` 作為正確答案，學生不一定理解這代表「由高次到低次的係數」。題目文字雖然有說明，但作答介面沒有格式約束時，仍容易造成非數學錯誤的判錯。

## 3. 現有 binomial_expansion_basic 狀態

- generator 是否已存在：已存在，位於 `core/vocational_math_b4/generators/binomial.py`。
- answer 型態：`list[int]`，例如 `[1, 4, 6, 4, 1]`。
- choices 狀態：`choices == []`，並且 payload 內標示 `supports_multiple_choice: False`。
- 是否已接 router：未接入一般 runtime router。
- 是否已建 wrapper：未建立 `BinomialTheorem` wrapper。
- 為何暫緩：目前答案格式、學生輸入格式、wrapper 判分策略、前端顯示方式都尚未定義；直接接入會提高誤判與使用困惑風險。

目前練習頁判分流程會呼叫 skill wrapper 的 `check(user_answer, current["answer"])`。既有 B4 wrapper 多以整數或字串比對為主，不是針對 `list[int]` 作答設計。因此 `binomial_expansion_basic` 若維持 `list[int]`，需要額外 normalization 與明確前端提示。

## 4. 三種方案比較

| 方案 | answer 型態 | 是否相容現有 runtime | 教學直覺性 | 判分難度 | 修改範圍 | 風險 |
|---|---|---|---|---|---|---|
| 方案 A：維持係數列表 | `list[int]` | 低 | 中 | 中到高 | wrapper check、輸入提示、答案 normalization | 學生格式不一致導致誤判 |
| 方案 B：改成多項式字串 | `str` | 中 | 高 | 高 | generator、wrapper check、可能需要 symbolic parser | 等價式與格式差異容易誤判 |
| 方案 C：改問單一係數或常數項 | `int` | 高 | 中到高 | 低 | 新增或改造 int-answer 題型 | 不是完整展開題 |

## 5. 建議方案

建議短期採用方案 C：將完整的 `binomial_expansion_basic` 暫緩接入一般練習頁，另建立或優先接入 answer 為 `int` 的二項式係數題型。

短期可將題目改為：

- 「展開 $(x+2)^3$ 後，$x^2$ 項係數為多少？」
- 「展開 $(x+2)^3$ 後，常數項為多少？」
- 「展開 $(ax+b)^n$ 後，指定項係數為多少？」

這樣 answer 維持整數，能直接相容現有 runtime、choices、wrapper check 與一般練習頁。完整展開題則保留為後續 free-response 題型，等答案 normalization 或 symbolic parser 設計完成後再接入。

## 6. 建議後續拆法

建議後續將二項式相關題型拆成下列方向：

- `binomial_coefficient_sum`：問係數和，answer 為 `int`。
- `binomial_specific_term_coefficient`：問指定次方項係數，answer 為 `int`。
- `binomial_equation_solve_n`：由組合或二項式係數條件反求 `n`，answer 為 `int`。
- `binomial_constant_term`：問常數項，answer 為 `int`。
- `binomial_middle_term`：問中間項或中間項係數，answer 可先限制為 `int`。
- `binomial_expansion_full_free_response_future`：完整展開，保留為未來 free-response，需定義多項式 normalization。

## 7. 對 coverage matrix 的影響

`binomial_expansion_basic` 短期仍不建議列入 `runtime_ready`。雖然 generator 已存在並通過 sample QA，但因 answer 是 `list[int]`，缺少一般練習頁可用的判分策略與 wrapper 支援，因此應繼續暫緩接入。

若 coverage matrix 需要更精確分類，可標註為 generator 已存在但 runtime 接入暫緩；在目前矩陣語境下，仍可維持在 `planned_only` 或等價的「generator_ready_no_wrapper」狀態。短期不接入時，`runtime_ready` 不會增加。

若下一批改做 int-answer 的二項式係數題型，應作為獨立 problem_type 納入 generator 與 router/wrapper 接入流程，而不是把 `binomial_expansion_basic` 直接推上一般練習頁。

## 8. 給非 coding 教師的說明

二項式展開不能直接上線，原因不是題目不能算，而是系統還不知道學生會用什麼格式回答。

例如正確展開可以寫成一串係數，也可以寫成完整多項式。學生寫 `1,6,12,8`、`[1,6,12,8]` 或 `x^3+6x^2+12x+8`，數學意思可能都對，但系統如果只做簡單比對，可能會判錯。

短期先改成問單一係數，例如「$x^2$ 項係數是多少」，答案就是一個整數。這比較適合目前的練習頁，也比較容易讓學生理解與系統判分。

完整展開題可以保留到未來，等系統能可靠判斷多項式答案格式後再上線。

## 9. 結論

短期建議採用方案 C。

不建議立即接入現有 `binomial_expansion_basic`。

`list[int]` answer 對一般練習頁判分與顯示都不夠穩定。

完整展開題應保留為 future free-response。

下一步宜優先做 int-answer 的二項式係數類題型。
