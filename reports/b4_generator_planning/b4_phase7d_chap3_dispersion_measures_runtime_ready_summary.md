# B4 Phase 7D: Chap3 Dispersion Measures Runtime-ready Summary

## 1. 任務與目標
本階段旨在實作 Chap3 的 `vh_數學B4_DispersionMeasures`（離散趨勢量數），嚴格遵守 Phase 7C 盤點報告與 Runtime Smoke Gate SOP v0.1.5，只實作高確定性的封閉數值題型。

### 涵蓋題型 (Problem Types)
1. `range_basic_numeric`: 全距計算
2. `percentile_basic_numeric`: 百分位數計算
3. `quartile_basic_numeric`: 四分位數計算 (Q1, Q2, Q3)
4. `interquartile_range_basic`: 四分位距 (IQR) 計算

---

## 2. 實作細節與 SOP 遵守狀況

### 2.1 Skill-level Textbook Coverage
根據教科書對離散趨勢量數的定義，我們涵蓋了未分組資料的以下核心觀念：
- **全距 (Range)**：最大值減最小值。
- **百分位數 (Percentile)**：利用指標值 $i = \frac{n \times k}{100}$ 判斷是否為整數，若是整數則取第 $i$ 筆與 $i+1$ 筆平均，若否則無條件進位。此計算規則符合教科書標準定義。
- **四分位數 (Quartiles) 與 四分位距 (IQR)**：分別對應第 25、50、75 百分位數的計算。

### 2.2 Automated Scenario Diversity Check
為了避免題幹單調，四個 generator 皆內建了三個不同的生活/數學情境 (`scenario`)：
- **Scenario 0**：純數學未排序資料。
- **Scenario 1**：班級學生的測驗分數。
- **Scenario 2**：手搖飲店的每日銷售杯數或連續日期的氣溫。
多樣性已在自動化測試 `test_generator_scenario_diversity` 中驗證，確保 50 次亂數生成下，每種題型都能涵蓋至少 3 種情境，符合 SOP 的多樣性防護要求。

### 2.3 Router & Allowlist Integration
- 將四個 problem_types 註冊至 `core/vocational_math_b4/services/question_router.py` 的 `_CHAP3_PHASE7B_REGISTRY` 中。
- 在 `core/vocational_math_b4/adaptive/b4_chapter3_phase7b_allowlist.py` 內將 `vh_數學B4_DispersionMeasures` 加入開放清單，確保 `/practice` 等 API 可正確路由與出題。

### 2.4 Checker 檢核機制
- 全距 (`range_basic_numeric`)：屬於整數作答，由 `check_integer_answer` 嚴格把關。
- 百分位數系列：依據計算結果可能產生非整數的 `.5` 值，因此使用 Fraction 保留精確度，並透過 `check_rational_answer` 寬鬆檢查，容許學生輸入分數或等值小數。

---

## 3. 測試與驗證 (Regression & Unit Tests)
新增了 `tests/test_b4_chap3_phase7d_dispersion_measures_runtime_ready.py`，並進行了全系統的回歸測試，共 226 項測試全數通過。

### 包含的測試面向：
- **Generator 穩定度**：無佔位符、無空字串、確保運算皆能正確解出答案。
- **Payload 契約與 Checker**：答案格式與 `answer_type` 吻合，並且能正確被對應的 checker 判定為 True。
- **Scenario Diversity**：驗證 `scenario` 變數產出多樣化的情境。
- **API Integration**：`/practice`, `/get_next_question`, `/check_answer` 流程完整走通。
- **Not-enabled Friendly Error**：驗證尚未開放的 Chap3 技能（如圖表判讀）會正確回傳不支援的友善錯誤，而非 internal server error。

---

## 4. Final Status
本階段所涵蓋的 `vh_數學B4_DispersionMeasures` 已經穩定且合乎教材規範。
所有更改均不涉及 PPO、DB Schema 或 Adaptive 核心邏輯。

**系統目前狀態：`READY_FOR_MANUAL_SMOKE`**
