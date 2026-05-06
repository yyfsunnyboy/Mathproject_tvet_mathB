# Phase 5C-B3-A：二項式「指定項／指定次方」係數 deterministic generators

## 依據 Phase 5C-B0.1 之缺口

唯讀驗證（`b4_phase5c_b0_1_binomial_must_cover_verification.md`）指出：

- **二變數二項式指定項係數**：`missing_generator`
- **Laurent 型二項式指定次方係數**：`missing_generator`

本階段僅補上上述兩類 **整數答案、deterministic** 題型；**完整二項式展開**仍維持 excluded／future AI-judged，**未**接入 `binomial_expansion_basic`。

## 新增 generator／problem_type

| problem_type_id | generator 函式 | generator_key |
|-----------------|----------------|---------------|
| `binomial_two_variable_specific_coefficient` | `binomial_two_variable_specific_coefficient` | `b4.binomial.binomial_two_variable_specific_coefficient` |
| `binomial_laurent_specific_power_coefficient` | `binomial_laurent_specific_power_coefficient` | `b4.binomial.binomial_laurent_specific_power_coefficient` |

實作檔案：`core/vocational_math_b4/generators/binomial.py`

## 數學公式（題幹僅求係數，不要求完整展開）

### A. 二變數 \((ax \pm by)^n\)，求 \(x^p y^q\) 之係數（\(p+q=n\)）

一般項（對應 \(y\) 的次方為 \(q\)）：

\[
\binom{n}{q}(ax)^p(\pm by)^q
\]

係數：

\[
\binom{n}{q}\,a^p\,(\pm b)^q
\]

（負號在 \(y\) 項時，以 \((-b)^q\) 保留正負。）

### B. Laurent 型 \(\left(ax \pm \dfrac{b}{x}\right)^n\)，求 \(x^k\) 之係數

一般項（以 \(r\) 表取 \(\dfrac{b}{x}\) 的次數）：

\[
\binom{n}{r}(ax)^{n-r}\left(\frac{\pm b}{x}\right)^r
\]

\(x\) 的次方為 \((n-r)-r=n-2r\)。若指定 \(k\)，則 \(n-2r=k\)，即 \(r=\dfrac{n-k}{2}\)（需為整數且 \(0\le r\le n\)）。

係數：

\[
\binom{n}{r}\,a^{n-r}\,(\pm b)^r
\]

## Variant 覆蓋

- **二變數**：\(n\) 約 3–7；\(a,b\) 約 1–5；\(q\in[0,n]\)、\(p=n-q\)；\(+\)／\(-\) 在 \(y\) 項；難度較高時係數範圍略放大。答案絕對值超過 `_MAX_BINOMIAL_SPECIFIC_ANSWER`（500_000）時重新抽樣。
- **Laurent**：\(n\) 約 4–8；\(r\in[0,n]\)、\(k=n-2r\)；\(ax \pm \dfrac{b}{x}\) 兩種符號；同樣受答案上界保護。

## Router 接入

`core/vocational_math_b4/services/question_router.py` 中 **`vh_數學B4_BinomialTheorem`** 已新增兩筆 registry entry（薄 wrapper，直接呼叫上述 generator）。

`skills/vh_數學B4_BinomialTheorem.py` 仍為通用 `generate_for_skill`，**無需**修改即可經 `problem_type_id` 或 seed 抽樣取得新題型。

## Allowlist／validator

- `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST` 已含 `vh_數學B4_BinomialTheorem`（未改集合）。
- 新 `problem_type_id` **未**列入 `B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES`；`binomial_expansion_basic` 等仍排除。

## 測試

新增：`tests/test_phase5c_b3_binomial_specific_coefficient_generators.py`

- 二變數：\(p+q=n\)、係數公式、seed 1–50 抽樣、validator gate。
- Laurent：\(k=n-2r\)、係數公式、解說含 \(n-2r\) 推導、seed 1–50、validator gate。
- Router：明確指定 `problem_type_id` 與長程 seed 抽樣須涵蓋兩種新題型。

## QA 指令與結果（本機）

```text
python -m pytest -q tests/test_phase5c_b3_binomial_specific_coefficient_generators.py
# 104 passed

python -m pytest -q tests/test_vocational_math_b4_question_router_registry_canonical.py
python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py
python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py
python -m pytest -q tests/test_phase5b_fix_e1_b4_remediation_bridge.py
# 49 passed（含既有 SQLAlchemy DeprecationWarning）
```

## 未處理項目（後續 phase）

- **組合遞移／錯列和**：仍缺 generator。
- **純組合數總和**之敘述 enrichment：仍僅 partial。
- **奇偶項係數和**：仍僅 partial。
- **完整二項式展開**：仍保留 future AI-judged／不硬接 int-only。
- **棋盤路徑**等應用題：列為後續 phase。
