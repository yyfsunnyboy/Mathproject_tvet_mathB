# B4 Phase 7B: Chapter 3 First Deterministic Runtime-ready Batch Summary

## 1. 任務目標與範圍
本階段（Phase 7B）的目標為完成 B4 Chapter 3 第一批純數值高確定性題型的 generator 實作，並完成與現有 adaptive/practice 系統的路由整合。
範圍涵蓋四項核心技能，所有實作均需滿足「無手寫、無圖表依賴、LaTeX 格式相容」的 Deterministic Runtime-ready 條件。

**涵蓋技能與題型**：
- `vh_數學B4_CentralTendencyMeasures`
  - `mean_basic_numeric`: 算術平均數
  - `median_basic_numeric`: 中位數
  - `mode_basic_numeric`: 眾數
- `vh_數學B4_WeightedMean`
  - `weighted_mean_basic`: 加權平均數
- `vh_數學B4_VarianceAndStandardDeviation`
  - `variance_basic_numeric`: 變異數（整數保證演算法）
  - `standard_deviation_basic_numeric`: 標準差（整數保證演算法）
- `vh_數學B4_LinearTransformationOfData`
  - `linear_transform_mean`: 線性變換對平均數的影響
  - `linear_transform_std_variance`: 線性變換對標準差/變異數的影響

---

## 2. 實作細節

### 2.1 Generators (`core/vocational_math_b4/generators/chap3_statistical_measures.py`)
- **完全隔離**：新建專屬檔案，避免與 Chap1 / Chap2 混合。
- **rng 隨機種子**：實作 `rng` 以確保 `gen_seed` 注入時的產出穩定性（Seed deterministic）。
- **整數題型演算法**：針對變異數與標準差，實作了 `_generate_perfect_square_variance_dataset` 演算法，確保隨機產生的數據群其平均數與變異數必定為整數，避免出現無理數根號答案。
- **Payload 契約**：每題均回傳標準字典格式，確保 `skill_id`, `subskill_id`, `problem_type_id`, `question_text`, `answer`, `explanation` 等必備欄位完整。

### 2.2 Allowlist 與 Validator (`core/vocational_math_b4/adaptive/b4_chapter3_phase7b_allowlist.py`)
- **獨立白名單**：定義 `B4_CHAPTER3_PHASE7B_ALLOWLIST`。
- **閘道防護**：`is_b4_chapter3_skill_not_enabled` 可阻擋剩餘尚未實作的 Chap3 技能，確保不會引發內部 Crash。
- **Payload 驗證**：透過 `validate_b4_chap3_phase7b_generator_payload` 防止格式錯誤的產出流向前端。

### 2.3 Router 與 Practice 整合
- 在 `core/vocational_math_b4/services/question_router.py` 建立 `_CHAP3_PHASE7B_REGISTRY` 註冊表。
- 修改 `core/routes/practice.py`：
  - 於 `get_next_question` 加入 Chap3 白名單判斷，直接橋接 router 產生題目。
  - 於 `check_answer` 內加入 Chap3 獨立批改路徑（共用 `check_integer_answer` 與 `check_rational_answer`，針對機率外題型設定 `validate_probability_range=False` 以避免 0~1 的區間限制）。
  - 對於尚未開放的 Chap3 技能，回傳友善錯誤訊息 `B4_CHAP3_SKILL_NOT_ENABLED_PUBLIC_ERROR`。

---

## 3. 回歸與整合測試

已建立 `tests/test_b4_chap3_phase7b_first_deterministic_batch.py`，並執行涵蓋 Chap1, Chap2 的綜合測試。

**測試項目**：
1. **Generator 穩定性**：多 Seed 測試無報錯、無 `[FORMULA_MISSING]` / `[BLANK]` 等佔位符。
2. **Checker 共用**：成功複用 Chap2 的 rational/integer 批改器且通過測試。
3. **HTTP Route 整合**：`/practice`, `/get_next_question`, `/check_answer` API 層成功對接。
4. **Url Encoding**：URL encoded 與 decoded `skill_id` (含中文字元) 均能正確解析。
5. **Regression**：
   - 323 items passed.
   - 涵蓋 `test_b4_chap2_phase6k_remaining_skill_coverage.py`
   - 涵蓋 `test_b4_chap2_phase6c2r_practice_smoke_regression.py`
   - 涵蓋 `test_b4_chapter1_adaptive_allowlist.py`
   - 涵蓋 `test_vocational_math_b4_question_router_registry_canonical.py`

無破壞既有架構，完全向下相容。

---

## 4. Manual Smoke 驗收準備

系統已達到 **READY_FOR_MANUAL_SMOKE** 狀態。
請依據 `B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md` 進行以下驗證：

1. 開啟前端介面，進入單元練習模式，測試以下技能 URL：
   - `vh_數學B4_CentralTendencyMeasures`
   - `vh_數學B4_WeightedMean`
   - `vh_數學B4_VarianceAndStandardDeviation`
   - `vh_數學B4_LinearTransformationOfData`
2. 驗證題幹與解析之 LaTeX 渲染正常。
3. 送出整數、小數與分數（若適用）的答案，確認 AI 批改與分數判斷正確。
4. 測試一個被阻擋的技能（例如 `vh_數學B4_SamplingMethods`），確認出現友善錯誤提示而非系統 500。
