# Phase 5D-A Fix-2：Hockey-stick LaTeX 與 Shifted Textbook Variant 校準

## 1) 教師 QA observation

- **LaTeX 排版不符規範**：`combination_hockey_stick_sum` 題幹出現 `C(1,1)+C(2,1)+...` 之類的 plain text / function notation，與本專案及課本排版（`$C^{n}_{r}$`）不一致。
- **課本常見 shifted / staggered 題型缺失**：目前僅支援 standard hockey-stick，未支援以對稱性錯列呈現的常見形式（例如 \(C^{m}_{m-r}\) 的外觀）。

## 2) 修正方式（Fix-2）

### (A) LaTeX formatter

- 新增 `format_combination_latex(n, r)` 產生 **課本標準** \(C^{n}_{r}\) 形式（不再產生 `C(n,r)`）。

### (B) standard hockey-stick 題幹與解說改為 LaTeX

- 題幹與 identity 一律使用：
  - \(C^{n}_{r}\) 形式
  - 題幹整段以 `$...$` 包住（確保畫面渲染為 LaTeX）
- 不再出現任何 `C(` 字樣。

### (C) 新增 shifted_textbook 安全變體（不新增 problem_type_id）

- **沿用** `problem_type_id = combination_hockey_stick_sum`。
- 以對稱性 \(C^{m}_{m-r}=C^{m}_{r}\) 產生錯列外觀：
  - 題幹以 \(C^{m}_{m-r}\) 呈現（staggered）
  - 解說先用對稱性正規化為同一下標 \(r\) 的標準和，再套用 hockey-stick identity
- **不要求證明**、不做完整推導，維持 **int-answer**。

## 3) 數學公式（本輪採用的安全構造）

### standard hockey-stick identity

\[
C^{r}_{r}+C^{r+1}_{r}+\cdots+C^{n}_{r}=C^{n+1}_{r+1}.
\]

### shifted_textbook（以對稱性顯示錯列）

\[
C^{r}_{0}+C^{r+1}_{1}+C^{r+2}_{2}+\cdots+C^{n}_{n-r}
=
C^{r}_{r}+C^{r+1}_{r}+\cdots+C^{n}_{r}
=
C^{n+1}_{r+1}.
\]

## 4) 未處理（future micro-variant）

- 更貼近某些課本例題的更複雜錯列，例如：
  - \(C^{3}_{0}+C^{3}_{1}+C^{4}_{2}+C^{5}_{3}+\cdots\)
- 本輪先以 **可程式化驗證**、不易寫錯的 shifted_textbook 版本落地；上述更複雜外觀可在後續另立 micro-variant 擴充（仍須維持同一 `problem_type_id` 與 validator 通過）。

## 5) QA commands / result

建議回歸指令（Fix-2 任務要求）：

- `python -m pytest -q tests/test_phase5d_a_fix2_hockey_stick_latex_shifted_variant.py`
- `python -m pytest -q tests/test_phase5c_d2_combination_hockey_stick_generator.py`
- `python -m pytest -q tests/test_phase5d_a_fix1_binomial_coefficient_sum_wording.py`
- `python -m pytest -q tests/test_phase5c_d1_fix_b4_router_sampling_exposure.py`
- `python -m pytest -q tests/test_vocational_math_b4_question_router_registry_canonical.py`
- `python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py`

