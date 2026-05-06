# Phase 5D-A-Fix-1: BinomialCoefficientIdentities Pure Combination Sum Wording Calibration Summary

## 1. 教師 QA Observation
在 Phase 5D-A 手動 QA 期間，教師發現 B4 Chapter 1「排列組合」的單元練習中，系統抽到了 `binomial_coefficient_sum` 等題型，但題幹為：「展開 $(x+2)^2$ 後，所有係數和為多少？」。教師指出這類「展開後係數和」的 wording 較偏向多項式／二項式定理的展開章節，而 B4 Chapter 1 排列組合章節需要的應是「純組合數和式」的題型呈現。

## 2. 原題幹問題：數學正確但章節語境不符
原先 generator 產出的題目在數學邏輯上是正確的（的確是在考二項式係數），但其題幹設計以「多項式展開」為出發點。在技術型高中的課本脈絡中，B4 Chapter 1 的單元練習更適合出現純粹由 $C$ 組成的和式求值題。

## 3. 修正後題幹：純組合數和式
為符合章節語境，我們校準了 `binomial_coefficient_sum` 與 `binomial_odd_even_coefficient_sum` 的生成邏輯：
- **`binomial_coefficient_sum`**：改為純求值型式，例如：「求下列組合數和的值：$C^n_0 + C^n_1 + \dots + C^n_n$」，答案為 $2^n$。
- **`binomial_odd_even_coefficient_sum`**：改為純奇數／偶數項求值，例如：「求下列組合數和的值：$C^n_0 + C^n_2 + \dots$」或「$C^n_1 + C^n_3 + \dots$」，答案為 $2^{n-1}$。
- 說明（Explanation）也改為直接引用「二項式係數和性質」或「組合數奇偶項和性質」。

## 4. 保留的 problem_type
完全保留了原有的 `problem_type_id` 與 generator，並維持它們在 `vh_數學B4_BinomialCoefficientIdentities` 技能下的註冊。
保留的題型包含：
- `binomial_coefficient_sum`
- `binomial_odd_even_coefficient_sum`

（註：已撤銷了前一次在 router 層將 `binomial_coefficient_sum` 從 B4 Chapter 1 排出的設定，確保新版題幹可以直接在該單元練習中曝光給學生使用。）

## 5. QA Commands / Result
已撰寫全新測試 `tests/test_phase5d_a_fix1_binomial_coefficient_sum_wording.py` 來驗證題幹中不含「展開」與「係數和」，並確認生成答案與 $2^n$ 邏輯相符。
執行以下回歸測試：
```bash
python -m pytest -q tests/test_phase5d_a_fix1_binomial_coefficient_sum_wording.py
python -m pytest -q tests/test_phase5c_d1_fix_b4_router_sampling_exposure.py
python -m pytest -q tests/test_phase5c_d2_combination_hockey_stick_generator.py
python -m pytest -q tests/test_vocational_math_b4_question_router_registry_canonical.py
python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py
python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py
python -m pytest -q tests/test_phase5b_fix_e1_b4_remediation_bridge.py
```
**Result**: `159 passed, 28 warnings in 285.78s (0:04:45)`
測試全數通過。

## 6. 確認未放行 excluded 題型
已在測試中確保 `tree_diagram_listing`、`binomial_expansion_basic`、`pascal_triangle_derivation` 等題型仍保持 0 曝光，未被放行至 deterministic 流程中。
