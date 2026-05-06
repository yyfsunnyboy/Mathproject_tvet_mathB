# Phase 5D-A-Fix-1: Remove Binomial Coefficient Sum Exposure from B4 Chapter 1 Unit Practice

## 1. 教師 QA Observation
在 Phase 5D-A 手動 QA 期間，教師發現 B4 Chapter 1「排列組合」的單元練習中，系統抽到了 `vh_數學B4_BinomialCoefficientIdentities` 技能下的題型 `binomial_coefficient_sum`（例如：「展開 $(x+2)^2$ 後，所有係數和為多少？」）。

## 2. 為什麼這不是數學錯誤，而是章節歸屬問題
這類「展開後所有係數和」題型在數學邏輯上是完全正確的，也是二項式定理的一種應用。然而，在目前技術型高中課綱與教材的教學脈絡中，這類題目更偏向於「多項式」或「二項式展開應用」章節的範疇。因此，教師認為它不適合出現在 B4 Chapter 1「排列組合」的單元練習中，這是一個章節歸屬（contextual fit）的問題，而非 Generator 本身的錯誤。

## 3. 修正方式
為達到最小化修正且不影響系統架構：
1. 修改 `core/vocational_math_b4/services/question_router.py`，讓 `generate_for_skill` 支援傳入 `excluded_problem_type_ids` 進行 router-level 過濾。
2. 修改 `skills/vh_數學B4_BinomialCoefficientIdentities.py` 的 wrapper，讓 `generate` 可將 `kwargs` 中的 `excluded_problem_type_ids` 向下傳遞。
3. 修改 `core/routes/practice.py` 中的 `get_adaptive_question`，在判斷為 B4 Chapter 1 單元練習的 Context 時，動態注入 `excluded_problem_type_ids = {"binomial_coefficient_sum"}`。
透過此修正，系統在 router 選題階段就會主動避開該題型，而不是產生後才被 validator 擋下導致不斷 retry。

## 4. 是否保留 Generator
**完全保留**。
我們沒有刪除 `binomial_coefficient_sum` 的 generator 程式碼，也沒有修改 Phase 4E 的 coverage matrix，確保該 generator 的單元測試不會中斷，且數學邏輯維持原樣。

## 5. B4 Chapter 1 Unit Practice Before/After Exposure
- **Before**: 在 B4 Chapter 1 單元練習中，抽到 `vh_數學B4_BinomialCoefficientIdentities` 時，有一定機率出現 `binomial_coefficient_sum`。
- **After**: 在 B4 Chapter 1 單元練習中，抽到該技能時**不再出現** `binomial_coefficient_sum`，而是集中在 `combination_hockey_stick_sum`、`binomial_equation_solve_n` 等其它合法題型。非章節模式（如單一技能測試）則不受任何影響，仍可正常產出 `binomial_coefficient_sum`。

## 6. QA Commands / Result
已執行以下回歸測試：
```bash
python -m pytest -q tests/test_phase5d_a_fix1_remove_binomial_coefficient_sum_exposure.py
python -m pytest -q tests/test_phase5c_d1_fix_b4_router_sampling_exposure.py
python -m pytest -q tests/test_phase5c_d2_combination_hockey_stick_generator.py
python -m pytest -q tests/test_vocational_math_b4_question_router_registry_canonical.py
python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py
python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py
python -m pytest -q tests/test_phase5b_fix_e1_b4_remediation_bridge.py
```
**Result**: `160 passed, 28 warnings in 290.64s (0:04:50)`
所有相關與新增的測試皆全數通過，包含 excluded 題型的隱藏以及 non-chapter context 的可見性驗證。

## 7. 後續使用建議
由於 generator 完好保留，未來若在「多項式」或專屬的「二項式定理」章節中需要使用該題型，只需直接將該技能或題型納入相應章節的 router 或 allowlist 即可，具備充分的擴展性。
