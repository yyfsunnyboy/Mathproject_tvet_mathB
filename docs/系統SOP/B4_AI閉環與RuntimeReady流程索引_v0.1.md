# B4 AI 閉環與 RuntimeReady 流程索引 v0.1

本文件是 B4（並可延伸到 B1–B3）的 SOP 索引總覽，提供「先後順序」與「對應文件」。

---

## 1. 核心 SOP 清單

1. [B4_AI出題品質檢查SOP_v0.1](./B4_AI出題品質檢查SOP_v0.1.md)
2. [B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1](./B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md)
3. [B1-B4教材匯入與AI出題流水線SOP_v0.1](./B1-B4教材匯入與AI出題流水線SOP_v0.1.md)
4. `B4_phase_prompt_templates_v0.1.md`（若存在，作為模板參考）

---

## 2. 建議使用順序

1. 先看「B1–B4 教材匯入與流水線 SOP」：決定 Phase 0–10 流程。
2. 進入 Runtime 實作時，依「Runtime Smoke Gate SOP」做路徑接通與冒煙檢查。
3. 進入 release 前檢查時，依「AI 出題品質檢查 SOP」跑 quality gates。
4. 修補完成後，更新 QA report 與 closure 記錄。

---

## 3. Phase Template A/B/C/D（索引）

- **Template A（Planning-only）**：盤點、審核、報告，不做 production 變更。  
- **Template B（Runtime-ready batch）**：小批量實作 generator/router/checker + 測試 + 報告。  
- **Template C（Closure）**：在 smoke/QA 收斂後做 closure 記錄。  
- **Template D（Small repair）**：針對明確問題做小修補，避免大改。

---

## 4. B4 FinalCoverage-Recount（索引）

參考報告：
- `reports/b4_generator_planning/b4_final_mode_aware_runtime_coverage_recount.md`

用途：
- 確認 mode-aware runtime coverage 基線。
- 確認 final coverage count 與 runtime category 分佈。

---

## 5. AI 出題品質檢查 SOP（索引摘要）

文件：
- [B4_AI出題品質檢查SOP_v0.1](./B4_AI出題品質檢查SOP_v0.1.md)

重點：
- `coverage gate` 只代表有路徑。
- `quality gate` 才代表學生端可用（可作答、可判分、可渲染、語言一致）。
- release 前應完成 quality gate 與 QA 報告一致性檢查。

---

## 6. Question Diversity Gate（索引摘要）

適用文件：
- `B4_AI出題品質檢查SOP_v0.1.md`
- `B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md`

重點：
- 不可只用 2–3 題輪替。
- 不可連續同題。
- 每 skill 至少抽樣 20 題。
- 需追蹤 `unique_question_text_count`、`repeated_question_text_ratio`、`consecutive_duplicate_count`。

---

## 7. Parameterized Diversity Gate（索引摘要）

適用文件：
- `B4_AI出題品質檢查SOP_v0.1.md`
- `B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md`

重點：
- 數字不可固定輪播。
- 題目需有 `parameter_signature` / `numeric_tuple` 等可追蹤資訊。
- 答案必須與參數一致（answer consistency）。

---

## 8. Level 1 Global Consecutive Duplicate Guard（索引摘要）

重點：
- Level 1 bare skill default 不得相鄰重複。
- route/session 層應做避重（建議 retry 最多 3 次）。
- fallback 不得落到 open-ended review 題。

---

## 9. Fake Diversity / Scenario Family Gate（索引摘要）

重點：
- 只換名稱不算真正多樣性。
- 同骨架（解題結構/作答行為相同）應歸同一 `scenario_family`。
- TreeDiagramCounting 案例：A/B、甲乙、紅藍先贏兩場皆屬 `best_of_three_binary_match`。

---

## 10. B1–B4 流水線 SOP（索引摘要）

文件：
- [B1-B4教材匯入與AI出題流水線SOP_v0.1](./B1-B4教材匯入與AI出題流水線SOP_v0.1.md)

定位：
- 用於 B1/B2/B3/B4 的 Phase 0–10 通用流程。
- 先完成每冊 Phase 1 RuntimeReady baseline，再做跨冊 adaptive。

B4 定位：
- **Phase 1**：RuntimeReady baseline（收斂）
- **Phase 2**：adaptive prerequisite graph（deferred，待 B1–B3 入庫）

B1 啟動原則：
- 先走流水線 SOP（import -> inventory -> fidelity -> mode matrix -> runtime），不直接跳到 generator 實作。

---

## 11. 相關報告位置（參考）

- `reports/b4_generator_planning/`：B4 各修補與 QA 總結。
- `reports/b_series_inventory/`：B 系列 skill inventory / runtime mode matrix。
- `reports/b_series_quality/`：每冊 fullbook QA audit。
