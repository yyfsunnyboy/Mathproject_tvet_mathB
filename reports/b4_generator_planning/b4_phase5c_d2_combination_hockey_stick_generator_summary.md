# Phase 5C-D2：Combination Identity / Hockey-Stick Deterministic Generator Summary

## 1. 依據 Phase 5C-C closure audit 的 remaining true gap

依 `b4_phase5c_c_b4_ch1_must_cover_closure_audit.md`，B4 Chapter 1 在 deterministic int-answer runtime 中仍屬 **true gap** 的 must-cover 題型為組合遞移和（hockey-stick 類）。

## 2. D1-Fix 後背景

Phase 5C-D1-Fix 已解決 B4 pure generator-first 路徑的 seed 耦合，讓新增題型可在 chapter unit practice 路徑被觀察到。D2 在此基礎上新增新題型，沿用 D1-Fix 的 inner seed 派生策略，不改 adaptive 核心策略。

## 3. 新增 generator / problem_type

- 檔案：`core/vocational_math_b4/generators/binomial.py`
- 新增：
  - `HOCKEY_STICK_SUM_PROBLEM_TYPE_ID = "combination_hockey_stick_sum"`
  - `HOCKEY_STICK_SUM_GENERATOR_KEY = "b4.binomial.combination_hockey_stick_sum"`
  - `combination_hockey_stick_sum(...)`
- 題型歸屬 skill：`vh_數學B4_BinomialCoefficientIdentities`
- Router 接入（`core/vocational_math_b4/services/question_router.py`）：
  - `subskill_id = "b4_ch1_combination_hockey_stick_sum_01"`
  - `problem_type_id = "combination_hockey_stick_sum"`
  - `generator_key = "b4.binomial.combination_hockey_stick_sum"`
  - `generator_fn = binomial_generators.combination_hockey_stick_sum`

## 4. 支援 variant

本版（安全版）僅支援：

- `variant = standard_hockey_stick`

尚未納入 shifted / staggered 類（見 §9）。

## 5. 數學公式與適用範圍

採用恆等式：

- $C(r,r)+C(r+1,r)+\cdots+C(n,r)=C(n+1,r+1)$

設計範圍（依 difficulty）：

- `r` 約在 `0..5`
- `n` 約在 `r+2 .. r+8`
- 僅保留 `answer <= 500000`
- 題目為 int-answer，無證明要求、無完整推導要求
- 題幹與解說均含 LaTeX 表示

## 6. Router 接入

`vh_數學B4_BinomialCoefficientIdentities` 在原有三題型（`binomial_coefficient_sum`、`binomial_equation_solve_n`、`binomial_odd_even_coefficient_sum`）上新增第四題型 `combination_hockey_stick_sum`，未變更 router 架構與其他技能行為。

## 7. Validator / allowlist 狀態

- `vh_數學B4_BinomialCoefficientIdentities` 已在 `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST`。
- `validate_b4_deterministic_adaptive_generator_payload` 不阻擋 `combination_hockey_stick_sum`。
- 未新增 excluded 項；下列仍維持阻擋：
  - `tree_diagram_listing`
  - `binomial_expansion_basic`
  - `pascal_triangle_derivation`

## 8. QA commands / result

新增與指定回歸皆通過：

- `python -m pytest -q tests/test_phase5c_d2_combination_hockey_stick_generator.py` → `105 passed`
- `python -m pytest -q tests/test_phase5c_d1_fix_b4_router_sampling_exposure.py` → `4 passed`
- `python -m pytest -q tests/test_vocational_math_b4_question_router_registry_canonical.py` → `24 passed`
- `python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py` → `8 passed`
- `python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py` → `13 passed`
- `python -m pytest -q tests/test_phase5b_fix_e1_b4_remediation_bridge.py` → `4 passed`
- （加跑）`python -m pytest -q tests/test_phase5c_b3_binomial_specific_coefficient_generators.py` → `104 passed`
- （加跑）`python -m pytest -q tests/test_phase5c_b3_grid_shortest_path_generator.py` → `107 passed`
- （加跑）`python -m pytest -q tests/test_phase5c_b4_1_permutation_non_adjacent_generator.py` → `106 passed`
- （加跑）`python -m pytest -q tests/test_phase5c_b4_2_factorial_equation_variation.py` → `108 passed`

補充曝光觀察（D1-Fix 派生 seed，seed 1–500）：

- `combination_hockey_stick_sum` 出現 `13` 次，`first_seen_seed = 14`（visible）

## 9. 未處理項目（保留後續）

- shifted / more complex staggered sums（例如 $C(s,0)+C(s,1)+C(s+1,2)+\cdots$ 的一般化）尚未加入；避免公式不穩定或誤導。
- 純組合數總和 wording enrichment 尚未擴充。
- 完整展開（`binomial_expansion_basic`）仍維持 future AI-judged / excluded policy。
- 樹狀圖 / 巴斯卡三角形仍維持 manual_review / future AI-judged policy。
