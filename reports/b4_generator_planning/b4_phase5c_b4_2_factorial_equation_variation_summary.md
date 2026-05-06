# Phase 5C-B4.2：階乘方程變形 enrichment

## 1. 依據 Phase 5C-B0-Followup（partially_supported）

`factorial_equation_solve_n` 原先僅涵蓋 \(\frac{n!}{(n-1)!}=k\)（即 \(n=k\)）之窄形；課本／統測常見的 **\(a!\cdot n=b!\)**、**\(b!+a!=n\cdot a!\)**、**\(b!=n\cdot a!\)** 等變形未覆蓋。本階段在 **同一 `problem_type_id`** 下以 **variant / template_context** 擴充，不改 Phase 4E matrix、不新增 manual_review／excluded 題型。

## 2. 修改／擴充的 generator

| 項目 | 說明 |
|------|------|
| 檔案 | `core/vocational_math_b4/generators/counting.py` |
| 函式 | `factorial_equation_solve_n`（擴充） |
| `problem_type_id` | **沿用** `factorial_equation_solve_n` |
| `generator_key` | **沿用** `b4.counting.factorial_equation_solve_n` |

## 3. 是否沿用 `factorial_equation_solve_n`

**是。** 未新增 `problem_type_id`；router 與 `vh_數學B4_FactorialNotation` wrapper **無需**變更。

## 4. variant／template_context 清單

| variant | 題意（摘要） | template_context |
|---------|----------------|------------------|
| `ratio_basic` | \(\frac{n!}{(n-1)!}=k\)，求 \(n\) | `ratio_equation` |
| `multiply_factorial_equation` | \(a!\times n=b!\)，求 \(n\) | `direct_equation` |
| `factorial_sum_linear_equation` | \(b!+a!=n\times a!\)，求 \(n\) | `sum_equation` |
| `factorial_product_ratio` | \(b!=n\times a!\)，求 \(n\) | `product_unknown` |

有號 `seed` 時：`variant = _FACTORIAL_EQ_VARIANTS_ORDER[seed % 4]`，使四類在短種子區間內輪替出現。  
`ratio_basic` 仍使用 **原參數 tuple** `(factorial_equation_solve_n, k)`，以相容 `seen_parameter_tuples` 與既有測試；其餘 variant 為 `(factorial_equation_solve_n, variant, a, b, template_context)`。

## 5. 階乘化簡公式

- **乘積型**（\(a!\times n=b!\) 或 \(b!=n\times a!\)）：  
  \(n=\dfrac{b!}{a!}=(a+1)(a+2)\cdots b\)
- **和線性型**（\(b!+a!=n\times a!\)）：  
  兩邊同除以 \(a!\) 得 \(n=\dfrac{b!}{a!}+1\)

參數：\(a\in[3,8]\)，\(b=a+d\)，\(d\) 依難度 1–2／2–3／3–4；\(b\le 12\)；\(\dfrac{b!}{a!}\) 與（和型）\(n\) 不超過 `_MAX_FACTORIAL_EQUATION_ANSWER`（100_000）。

## 6. Router 是否需要修改

**否。** `question_router` 仍指向同一 generator。

## 7. Validator／allowlist

- `vh_數學B4_FactorialNotation` 已在 allowlist。  
- `factorial_equation_solve_n` **未**加入 excluded set。

## 8. parameters（擴充欄位）

含：`variant`、`k`（僅 ratio_basic）、`a`／`b`／`gap`、`template_context`、`equation_latex`、`simplified_product_terms`、`factorial_ratio_value`、`formula_components`、`parameter_tuple`。

## 9. 測試與相容

- 新增：`tests/test_phase5c_b4_2_factorial_equation_variation.py`  
- 既有 `tests/test_vocational_math_b4_generators_phase4e3.py`：**僅**將 `test_raise_when_retries_exhausted` 中階乘案例之 `seed` 由 `1` 改為 `4`（使該例仍走 `ratio_basic`，以維持「擋滿 \((id,k)\) 後應拋錯」之意圖）。

## 10. QA 指令與結果（本機）

```text
python -m pytest -q tests/test_phase5c_b4_2_factorial_equation_variation.py
# 108 passed

python -m pytest -q tests/test_vocational_math_b4_generators_phase4e3.py
# 通過

python -m pytest -q tests/test_vocational_math_b4_question_router_registry_canonical.py
python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py
python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py
python -m pytest -q tests/test_phase5b_fix_e1_b4_remediation_bridge.py
python -m pytest -q tests/test_phase5c_b4_1_permutation_non_adjacent_generator.py
python -m pytest -q tests/test_phase5c_b3_grid_shortest_path_generator.py
python -m pytest -q tests/test_phase5c_b3_binomial_specific_coefficient_generators.py
# 合計 474 passed（含 SQLAlchemy DeprecationWarning）
```

## 11. 未處理項目（後續 phase）

- 組合遞移／錯列和  
- 純組合數和敘述 enrichment  
- 完整二項式展開仍保留 future AI-judged  
- 其他尚未納入的統測題型  
