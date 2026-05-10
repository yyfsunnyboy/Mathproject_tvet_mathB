# Phase 7B-D: Chap3 Textbook Variety Small Repair Summary

## 1. Manual Smoke Issue
在完成 Phase 7B 後的手動驗收 (Manual Smoke) 過程中，發現三個技能的題型語境過於單調：
- `vh_數學B4_WeightedMean`：幾乎只出學生科目學分加權平均。
- `vh_數學B4_VarianceAndStandardDeviation`：幾乎只出固定格式小數列求母體變異數/標準差。
- `vh_數學B4_LinearTransformationOfData`：幾乎只出 $y_i = ax_i + b$ 後求平均數/標準差/變異數。

為提升題型多樣性且不破壞已穩定的 Phase 7B 架構，啟動了本次 Small Repair (Phase 7B-D)，在原有的 `chap3_statistical_measures.py` generator 內最小化地新增出題 scenario，以符合課本語境多樣性的要求。

## 2. Files Changed
- **`core/vocational_math_b4/generators/chap3_statistical_measures.py`**：擴充三種技能的 generator，加入 `scenario` 控制變數，實作至少三種情境。
- **`tests/test_b4_chap3_phase7b_first_deterministic_batch.py`**：新增 `test_generator_scenario_diversity`，驗證各 generator 在多組 seed 情況下，確實能產生至少 3 種不同的 scenario。

## 3. WeightedMean Variety Repair
保留原本的學生學分加權題，並新增以下 scenario：
- **Scenario 0**：科目學分加權平均 (既有)
- **Scenario 1**：平時/段考比例加權 (以百分比計算學期成績)
- **Scenario 2**：分組平均合併 (已知兩組人數與各自平均數，求全班總平均)
- **Scenario 3**：商品價格與數量加權 (兩項商品的購買單價與數量加權)

## 4. Variance / SD Variety Repair
將變異數與標準差共用 `_generate_variance_std_scenario` 邏輯，並設計以下情境：
- **Scenario 0**：原始小資料組求變異數/標準差 (既有，使用完美平方數構造)。
- **Scenario 1**：給定母體大小 $N$、算術平均數 $\mu$ 以及所有數據的平方和 $\sum x_i^2$，利用快速公式求變異數/標準差。
- **Scenario 2**：給定母體大小 $N$ 與離均差平方和 $\sum (x_i - \mu)^2$，利用定義式求變異數/標準差。

## 5. LinearTransformation Variety Repair
針對平均數 (`linear_transform_mean`) 設計情境：
- **Scenario 0**：給定 $y_i = ax_i + b$，求新平均數 (既有)。
- **Scenario 1**：給定 $y_i = x_i \pm b$ (純平移)，求新平均數。
- **Scenario 2**：給定新舊平均數，反求平移量 $b$ 或縮放倍數 $a$。

針對變異數與標準差 (`linear_transform_std_variance`) 設計情境：
- **Scenario 0**：給定 $y_i = ax_i + b$，求新標準差/變異數 (既有)。
- **Scenario 1**：給定 $y_i = x_i \pm b$ (純平移)，觀察出標準差/變異數不變。
- **Scenario 2**：給定 $y_i = ax_i$ (純縮放)，求新標準差/變異數。

## 6. Scenario Diversity Tests
已於 `tests/test_b4_chap3_phase7b_first_deterministic_batch.py` 中新增 `test_generator_scenario_diversity` 函數，針對上述五支生成器函數，以 50 個不同的隨機種子執行，並透過 `payload["parameters"]["scenario"]` 檢查產生的集合。測試結果確認每支生成器皆能產生至少 3 種以上的情境。

## 7. Regression Result
執行了完整的迴歸測試涵蓋範圍：
- Phase 7B Chap3 原有測試
- Chap2 Phase 6K 及 Phase 6C-2R
- Chap1 Adaptive Allowlist
- Router Canonical Tests

共 324 個項目測試皆成功通過 (100%)。

## 8. Known Limitations
- 目前的 `VarianceAndStandardDeviation` 中未放入比較離散程度之單純 choice 題，由於 choice checker 尚未完全穩定，已依據規定先保留 numeric 題型。
- 加權平均數之數值設計依然強制產出有理數 (Rational Fraction) 以確保 checker 能夠穩定對接。

## 9. Final Confirmation
- 是否只修三個 Chap3 skill 題型變化：**是**
- 是否修改 adaptive scoring / mastery / APR：**否**
- 是否新增 handwriting / free-response / chart / table scoring：**否**
- 是否修改 DB schema：**否**
- 是否破壞 Chap1 / Chap2：**否**
- 是否啟動下一 phase：**否** (目前停留在 `READY_FOR_MANUAL_SMOKE`)
