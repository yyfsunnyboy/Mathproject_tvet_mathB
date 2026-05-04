# B4 Phase 4E-13B-QA-Fix 教學文字覆核報告

## 1. 本次修正範圍

- 僅微調 `binomial_specific_term_coefficient` 的題幹與 explanation 文字。
- 僅微調 `binomial_equation_solve_n` 的 explanation 文字。
- 不修改 answer、choices、parameter_tuple、generator_key、problem_type_id、metadata。
- 以 seed 1～5 重新檢查輸出樣本。

## 2. 修正重點確認

- `binomial_specific_term_coefficient`：當 `k=0` 時，題幹已明示「常數項，即 $x^{0}$ 項」，explanation 也明示「常數項即 $x^{0}$ 項」。
- `binomial_equation_solve_n`：
  - `r=1`（或 `variant=r1`）已包含 $C^{n}_{1}=n$ 與題目給定值，並明確寫出因此 $n=...$。
  - `r=2`（或 `variant=r2`）已包含 $C^{n}_{2}=\frac{n(n-1)}{2}$、題目給定的 $m$、以及檢查 $C^{\text{answer}}_{2}=m$ 的步驟，並明確寫出因此 $n=...$。

## 3. seed 1～5 樣本（修正後）

### b4.binomial.binomial_specific_term_coefficient

- seed 1  
  - question_text: 展開 $(x+1)^{2}$ 後，$x^{1}$ 項係數為多少？  
  - explanation: 展開係數依 $x^{2}$ 到 $x^{0}$ 排列，$x^{1}$ 項係數為 $2$。
- seed 2  
  - question_text: 展開 $(x+2)^{3}$ 後，$x^{2}$ 項係數為多少？  
  - explanation: 展開係數依 $x^{3}$ 到 $x^{0}$ 排列，$x^{2}$ 項係數為 $6$。
- seed 3（`k=0`）  
  - question_text: 展開 $(x+3)^{4}$ 後，常數項，即 $x^{0}$ 項係數為多少？  
  - explanation: 展開係數依 $x^{4}$ 到 $x^{0}$ 排列，常數項即 $x^{0}$ 項，其係數為 $81$。
- seed 4  
  - question_text: 展開 $(x+4)^{5}$ 後，$x^{3}$ 項係數為多少？  
  - explanation: 展開係數依 $x^{5}$ 到 $x^{0}$ 排列，$x^{3}$ 項係數為 $160$。
- seed 5  
  - question_text: 展開 $(x+2)^{5}$ 後，$x^{5}$ 項係數為多少？  
  - explanation: 展開係數依 $x^{5}$ 到 $x^{0}$ 排列，$x^{5}$ 項係數為 $1$。

### b4.binomial.binomial_equation_solve_n

- seed 1（`r=1`）  
  - question_text: 若 $C^{n}_{1}=3$，求正整數 $n$。  
  - explanation: 因為 $C^{n}_{1}=n$，且題目給 $C^{n}_{1}=3$，所以 $n=3$。
- seed 2（`r=2`）  
  - question_text: 若 $C^{n}_{2}=6$，求正整數 $n$。  
  - explanation: 因為 $C^{n}_{2}=\frac{n(n-1)}{2}$，題目給 $C^{n}_{2}=6$。檢查 $C^{4}_{2}=6$，所以 $n=4$。
- seed 3（`r=1`）  
  - question_text: 若 $C^{n}_{1}=8$，求正整數 $n$。  
  - explanation: 因為 $C^{n}_{1}=n$，且題目給 $C^{n}_{1}=8$，所以 $n=8$。
- seed 4（`r=2`）  
  - question_text: 若 $C^{n}_{2}=21$，求正整數 $n$。  
  - explanation: 因為 $C^{n}_{2}=\frac{n(n-1)}{2}$，題目給 $C^{n}_{2}=21$。檢查 $C^{7}_{2}=21$，所以 $n=7$。
- seed 5（`r=1`）  
  - question_text: 若 $C^{n}_{1}=12$，求正整數 $n$。  
  - explanation: 因為 $C^{n}_{1}=n$，且題目給 $C^{n}_{1}=12$，所以 $n=12$。

## 4. 結論

- 常數項題目已明示 $x^{0}$。
- `binomial_equation_solve_n` explanation 已補上更明確推導語句（包含公式、題目給定值與檢查步驟）。
- 本次為教學文字微調，不涉及路由、前端、wrapper 或其他模組接線。
