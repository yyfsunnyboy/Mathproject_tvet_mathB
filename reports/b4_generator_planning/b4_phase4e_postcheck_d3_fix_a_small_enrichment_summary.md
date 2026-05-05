# B4 Phase 4E Postcheck-D3-Fix-A Small Enrichment Summary

## 1. 目的與範圍

在 **Phase 4E-Final deterministic runtime closure** 已凍結、**不修改原始 coverage matrix**、不接 `binomial_expansion_basic`、不引入 free-response／AI-judged runtime 的前提下，針對：

1. **`vh_數學B4_RepeatedPermutation`**（`repeated_permutation_digits`）
2. **`vh_數學B4_BinomialTheorem`**（三個既有 int-answer generators）

進行 **小幅題幹／參數／說明 enrichment**，提升練習頁語境多樣性與說理清晰度，以利後續 Phase 4F adaptive 規劃。

## 2. 變更檔案

| 檔案 | 變更摘要 |
|---|---|
| `core/vocational_math_b4/generators/counting.py` | `generate`（`repeated_permutation_digits`）：情境模板、`parameters.template_context`、LaTeX 化 explanation，並註記與多重集合排列區隔 |
| `core/vocational_math_b4/generators/binomial.py` | `binomial_specific_term_coefficient`、`binomial_middle_term_coefficient`、`binomial_specific_coefficient_with_negative_term`：seed 預設組、bootstrap 抽樣分布、題幹／說明強化（一般項、第 $r+1$ 項、中間項項次、a≠1／b&lt;0 可見度） |
| `tests/test_vocational_math_b4_generators_phase4e13b.py` | `_exhausted_difficulty_one_tuples`：涵蓋 `a∈{1,2}` 與 `binomial_specific_term_coefficient` 全空間（配合新抽樣） |
| `tests/test_vocational_math_b4_generators_phase4e13e.py` | exhaustion 測試之 `seen` 集合擴充（middle／negative），與擴大後 difficulty 1 參數空間一致 |

**未修改：** `question_router.py`、任一 **wrapper**、`app.py`、routes、frontend、`b4_ch1_runtime_coverage_matrix.csv`、manual_review／future_ai_judged 相關設定。

## 3. 實際修改的 Generators／函式

| Generator（`problem_type_id`） | 說明 |
|---|---|
| `counting.generate`（`repeated_permutation_digits`） | 新增五種情境模板（密碼、車牌、座位／序號、染色序列、試驗序列）；數學仍為 `repeated_digit_arrangement_count` → $m^n$；`explanation` 改為 `$m^{n}$` LaTeX，並明示非多重集合排列 |
| `binomial_specific_term_coefficient` | difficulty 1 可抽 `a∈{1,2}`；seed 1～5 預設組改含 `a=2`、`a=3`；題幹標明指定次方；說明加入一般項 $\binom{n}{r}(ax)^{n-r}b^r$ 與求 $x^k$ 之 $r=n-k$ |
| `binomial_middle_term_coefficient` | difficulty 1 可抽 `a∈{1,2}`、`b` 可正可負；seed 預設含 $(2,1,4)$、$(1,-2,4)$ 等；題幹強調「$n$ 偶數時唯一中間項」；說明補上第幾項（$n$ 偶數時中間項位置） |
| `binomial_specific_coefficient_with_negative_term` | difficulty 1 可抽 `a∈{1,2}`；seed 預設含 `a>1`；題幹點出含負常數項；說明連結一般項與保留正負號 |

**未更動：** `binomial_expansion_basic`（仍不接入 BinomialTheorem runtime pool）、list／free-response 相關邏輯。

## 4. 測試與 QA 指令

**迴歸（執行結果：153 passed）：**

```text
python -m pytest tests/test_vocational_math_b4_generators_phase4e13b.py tests/test_vocational_math_b4_generators_phase4e13e.py tests/test_vocational_math_b4_generators_phase4b2.py tests/test_vocational_math_b4_generators_phase4e12b.py tests/test_vocational_math_b4_generators_phase4e14a.py tests/test_vocational_math_b4_generators_postcheck_d2_fix.py tests/test_vocational_math_b4_question_router_phase4e13c.py tests/test_vocational_math_b4_question_router_phase4e13f.py tests/test_vocational_math_b4_skill_wrappers_phase4e13c.py tests/test_vocational_math_b4_skill_wrappers_phase4e13f.py tests/test_vocational_math_b4_permutation_non_distinct_postcheck_d2_connect.py tests/test_vocational_math_b4_permutation_non_distinct_postcheck_c.py -q
```

**手工取樣 QA（`python -c`，種子 1～30）：**

- `question_router.generate_for_skill(skill_id="vh_數學B4_RepeatedPermutation", level=1, seed=s)`：`s=1..30`  
  - 核對：`problem_type_id==repeated_permutation_digits`、`answer==repeated_digit_arrangement_count(...)`、choices 四項唯一且含答案、`answer` 為 `int`、`parameters.template_context` 存在  
  - **五種 template_context 皆至少出現一次：** `password`、`license_plate`、`seat_serial`、`color_sequence`、`trial_sequence`
- `skill_id="vh_數學B4_BinomialTheorem"`，`problem_type_id` 各別指定為  
  `binomial_specific_term_coefficient`、`binomial_middle_term_coefficient`、`binomial_specific_coefficient_with_negative_term`，`seed=1..30`：逐題比對 `binomial_expansion_coefficients` 與 payload 答案；確認不含 `binomial_expansion_basic`
- 同上 **不指定** `problem_type_id`，`seed=1..30`：僅抽得上述三種 `problem_type_id`，三者皆有出現

## 5. 取樣結果摘要

- **RepeatedPermutation：** 30／30 無例外；情境模板覆蓋完整五類；說明維持 **重複選擇／$m^n$** 語義，並以文字與 **多重集合排列** 區隔。
- **BinomialTheorem（分题型各 30 seed + 混合 30 seed）：** 無 runtime 錯誤；答案皆為 int；choices 合法；說明含 LaTeX 與係數抽取邏輯加強；**未**出現 `binomial_expansion_basic`。
- **manual_review／future_ai_judged：** 本次未改 routing 與 coverage，deterministic pool 仍不包含 `binomial_expansion_basic` 等 excluded 題型。

## 6. Coverage matrix／架構層確認

- **原始 `b4_ch1_runtime_coverage_matrix.csv`（28／25 closure 口徑）：未修改。**
- **question_router／wrappers／frontend／app.py／routes：未修改**（本次僅 generators + 上述兩個測試檔之 exhaustion 集合同步）。

## 7. 結論與是否進入 Phase 4F

- **Postcheck-D3-Fix-A** 目標達成：在 **不更動 closure 統計與路由架構** 下，完成 **RepeatedPermutation** 與 **BinomialTheorem** 之 **小幅、可逆、語義一致** enrichment。
- **建議：** **可以進入 Phase 4F adaptive route 規劃**；但仍應遵守：adaptive **不指向** manual_review／不可用 skill；並可另開 **enrichment／adaptive 專用追蹤矩陣**，與 Phase 4E-Final **25／28** 口徑分帳。
- **剩餘非本次範圍：** `CombinationDefinition`、`BinomialCoefficientIdentities`、更深度參數域等，可留待 **Postcheck-D3** 後續批次或獨立 decision 文件。
