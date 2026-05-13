# B4 既有 Generator Registry 匯出稽核報告 v0.1

## 1. 任務目的
本任務旨在執行 Phase 1：B4-Registry-A，將 Mathproject_tvet_mathB 專案中已完成的 B4 Generator 現況匯出為標準化 Registry。本輪僅進行規格化盤點，不重新生成任何 B4 Generator，亦不修改正式生產代碼。

## 2. 輸出檔案
- [b4_generator_registry.v0.1.yaml](file:///d:/Python/Mathproject_tvet_mathB/configs/b4_generator_registry.v0.1.yaml)
- [b4_existing_generator_registry_audit.md](file:///d:/Python/Mathproject_tvet_mathB/reports/gencode_integration/b4_existing_generator_registry_audit.md)

## 3. 盤點來源
實際閱讀並分析以下檔案：
- `core/vocational_math_b4/services/question_router.py`：核心路由註冊表。
- `core/vocational_math_b4/generators/`：Generator 實作代碼。
- `core/vocational_math_b4/domain/b4_validators.py`：Payload 與答案驗證器。
- `core/vocational_math_b4/adaptive/`：Ch1-Ch3 自適應練習白名單。
- `core/routes/practice.py`：手動審閱清單與 Runtime 閘口。
- `reports/b4_generator_planning/`：歷史開發進度與矩陣報告。

## 4. Router Registry 匯出摘要

| router_registry_source | chapter | skill_count | problem_type_count | 備註 |
|---|---|---|---|---|
| `_REGISTRY` | 1 | 13 | 27 | 涵蓋排列組合與二項式定理。 |
| `_ENRICHMENT_REGISTRY` | 1 | 1 | 1 | 不盡相異物排列的補強路由。 |
| `_CHAP2_PHASE6C1_REGISTRY` | 2 | 10 | 17 | 涵蓋機率運算、期望值與集合。 |
| `_CHAP3_PHASE7B_REGISTRY` | 3 | 15 | 31 | 涵蓋統計量數、圖表讀取與抽樣。 |

## 5. Generator Registry 欄位摘要
- `skill_id`: 課程技能識別碼 (例如 `vh_數學B4_Combination`)。
- `problem_type_id`: 最小題型單位識別碼。
- `generator_key`: 內部 Generator 定位點。
- `answer_type`: 答案類型 (numeric, rational, choice, handwriting)。
- `checker_type`: Runtime 判分函數類型 (例如 `check_integer_answer`)。
- `status`: 整合狀態。
- `adaptive_allowlisted`: 是否已進入自適應練習池。

## 6. Status 判斷規則
- **`runtime_ready`**: 已註冊於 Router，不在 `MANUAL_REVIEW_SKILLS` 中，且已出現在 `adaptive_allowlist` 中。
- **`manual_review`**: 顯式標記於 `practice.py` 或因題型限制（如巴斯卡三角形）需人工介入。
- **`future_ai_judged`**: 涉及手寫、繪圖或複雜列舉，目前標記為 Free Response。
- **`experimental` / `unknown`**: 路由已註冊但未進入自適應白名單，或無法確認其端到端驗證狀態。

## 7. Adaptive Allowlist 對照

| chapter | allowlist_source | allowlisted_skill_count | 備註 |
|---|---|---|---|
| 1 | `b4_chapter1_deterministic_allowlist.py` | 13 | 已對齊 Phase 4E-Final 矩陣。 |
| 2 | `b4_chapter2_phase6c1_allowlist.py` | 10 | 包含機率性質與期待值。 |
| 3 | `b4_chapter3_phase7b_allowlist.py` | 10 | 部分圖表讀取題型排除。 |

## 8. Checker / Validator 對照

| answer_type | checker_type | validator_file | 適用題型 | 備註 |
|---|---|---|---|---|
| numeric | `check_integer_answer` | `b4_validators.py` | 排列組合、集合計數 | 最常用的判分器。 |
| rational | `check_rational_answer` | `b4_validators.py` | 基礎機率運算 | 支援 LaTeX 分式與小數。 |
| rational | `check_expected_value_answer` | `b4_validators.py` | 期望值 | 排除百分比輸入。 |
| choice | null | N/A | 統計圖表讀取 | 由前端 Choice Handler 處理。 |

## 9. 無法確認或需人工確認項目
1.  **`vh_??B4_StatisticalChartReading`**: `question_router.py` 第 938 行存在問號 typo，Registry 已根據 context 修正。
2.  **`tree_diagram_counting_runtime_shell`**: 雖然已註冊，但其邏輯涉及 Free Response，目前標記為 `future_ai_judged`。
3.  **`weighted_mean_basic`**: 已註冊且 Allowlisted，但其難度分級 (Level 1 vs Level 2) 在 Registry 中設為 `unknown` 待測。

## 10. 風險
- **狀態來源碎片化**：Registry 匯出時需比對 Router、Allowlist、Practice 三處，未來若不統一，容易發生「代碼已就緒但路由未開啟」的現象。
- **Typos 潛在威脅**：Router 中的技能 ID 拼寫錯誤（如 `vh_??B4_...`）可能導致學生端呼叫失敗。
- **Registry 同步性**：本 YAML 檔案目前僅為盤點文件 (Documentation Registry)，**並非**系統 Runtime 的真相來源 (Truth)，若不建立 Consistency Checker，兩者將會產生 Drift。

## 11. 下一步建議
建議下一步執行 **Phase 1B：B4 Registry Consistency Checker**。
開發一個測試腳本，自動比對 `configs/b4_generator_registry.v0.1.yaml` 與 `question_router.py` 以及 `allowlist.py` 的內容，確保盤點資訊與生產代碼 100% 同步，並能自動偵測 ID 拼寫錯誤。

---
*報告完成日期: 2026-05-13*
*盤點人員: Antigravity AI*
