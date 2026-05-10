# B4 Chapter 3 Phase 7E：Deterministic Coverage Postcheck / Remaining Decision

## 1. Scope and Guardrails

本階段 (Phase 7E) 僅負責執行 Postcheck 與制定決策報告。
為確保系統穩定與流程合規，本階段嚴格遵守以下限制：
- 不修改 production code
- 不修改 tests
- 不修改 DB
- 不撰寫 generator
- 不接 adaptive_practice
- 不新增 SOP

---

## 2. Completed Chap3 Deterministic Coverage

以下為目前已完成且進入 Runtime-Ready 狀態的 Chapter 3 技能清單（涵蓋 Phase 7B、7B-D 及 7D）：

| phase | skill_id | problem_type_id | scenario_diversity_status | runtime_status | notes |
|---|---|---|---|---|---|
| 7B-D | vh_數學B4_CentralTendencyMeasures | mean/median/mode basic numeric | Compliant | Runtime-Ready | 於 Phase 7B 完成，未發生多樣性風險 |
| 7B-D | vh_數學B4_WeightedMean | weighted_mean_basic | Compliant (Repaired) | Runtime-Ready | 已加入成績加權、混合物與單價情境 |
| 7B-D | vh_數學B4_VarianceAndStandardDeviation | variance/std_dev basic numeric | Compliant (Repaired) | Runtime-Ready | 已加入平時測驗、資料彙整計算情境 |
| 7B-D | vh_數學B4_LinearTransformationOfData | linear_transform_mean/std | Compliant (Repaired) | Runtime-Ready | 已涵蓋平移、伸縮、混和及反求原變數情境 |
| 7D | vh_數學B4_DispersionMeasures | range/percentile/quartile/iqr basic | Compliant | Runtime-Ready | 內建 3 種文本情境，通過 scenario tests 驗證 |

---

## 3. Scenario Diversity Compliance

依據 SOP v0.1.5，針對已完成之 Generator 進行審查：

- **是否有 scenario diversity tests**：是，在 `test_b4_chap3_phase7b_first_deterministic_batch.py` 與 `test_b4_chap3_phase7d_dispersion_measures_runtime_ready.py` 中皆包含 `test_generator_scenario_diversity`。
- **是否每個主要 generator 有 scenario_id / scenario_family 或等價判斷**：是，皆以 `scenario` 或 `scenario_id` 控制輸出情境。
- **是否仍有明顯單調風險**：否。經過 7B-D 修補與 7D 直接納入防護，目前隨機抽樣已可產出至少 3 種截然不同的應用語境。
- **是否需再修 7B-D / 7D**：否。

**結論**：`NO_IMMEDIATE_VARIETY_REPAIR_REQUIRED`

---

## 4. Remaining Chap3 Skill Decision Table

根據 Phase 7A 與 Phase 7C 盤點報告，Chapter 3 剩餘技能狀態如下：

| skill_id | skill_name | evidence_status | recommended_status | reason | next_action |
|---|---|---|---|---|---|
| vh_數學B4_SamplingMethods | 抽樣方法 | available | needs_textbook_alignment | 高度依賴選項語意與術語對齊 | 進行教材文本對齊後再決定 |
| vh_數學B4_NormalDistributionAndEmpiricalRule | 常態分配與經驗法則 | available | needs_textbook_alignment | 可轉為封閉數值，但需確認教材是否教 Z 分數或依賴圖表面積 | 確認課本題型結構 |
| vh_數學B4_OpinionPollInterpretation | 民意調查的解讀 | available | needs_textbook_alignment | 偏語意解讀，需固定結構轉為封閉型選項或信賴區間求值 | 確認教材出題模板 |
| vh_數學B4_SamplingSurvey | 抽樣調查 | insufficient | not_suitable_now | 缺乏具代表性題幹證據 | 暫緩實作 |
| vh_數學B4_StatisticalBasicConcepts | 統計的基本概念 | missing | not_suitable_now | 查無足夠之課本例題證據 | 暫緩實作 |
| vh_數學B4_StatisticalChartReading | 統計圖表判讀 | available | chart_table_image_reserved | 必須依賴前端 SVG 或圖檔 | 保留 |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與折線圖 | available | future_ai_judged | 高度依賴畫圖與填表 | 保留由 AI/Teacher 批改 |
| vh_數學B4_DataOrganizationAndCharts | 資料整理與圖表編製 | insufficient | future_ai_judged | 綜合性作圖 | 保留由 AI/Teacher 批改 |
| vh_數學B4_FrequencyDistributionTableConstruction | 次數分配表編製步驟 | available | future_ai_judged | 需完整填寫大型表格 | 保留由 AI/Teacher 批改 |
| vh_數學B4_HistogramsAndFrequencyPolygons | 直方圖與折線圖繪製 | available | future_ai_judged | 需坐標平面繪圖能力 | 保留由 AI/Teacher 批改 |

---

## 5. Recommended Next Deterministic Batch

**分析**：
目前 Chap3 已無「可立即安全開發且無需依賴圖表或語意清理」的 Deterministic 候選技能。剩下的技能若非高度依賴圖表（Reserved），就是涉及語境校準（Needs Textbook Alignment）。強行進入 7F 可能會因證據不足而產生不符教學邏輯的風險。

**建議方案**：
**Option B：Chap3 deterministic mainline closure**
（對應下一階段的 `Phase 7G：Chap3 deterministic mainline closure`）
- 理由：純數值的統計核心（集中趨勢、離散趨勢、資料線性變換）已全數涵蓋，剩餘技能具備高風險，建議先進行 Chap3 收尾並凍結。
- 備案：若專案仍需推進剩餘的三個 needs_textbook_alignment 技能，應考慮專門開立一個獨立的 alignment 階段。

---

## 6. Reserved / Future AI-judged Confirmation

特此明確重申，以下類別之技能不應進入 Deterministic Allowlist：
- **chart reading** (看圖提取數據)
- **histogram / line chart drawing** (畫直方圖與折線圖)
- **full frequency table construction** (完整建構次數分配表)
- **sampling method explanation** (開放式抽樣方法說明)
- **opinion poll interpretation** (若為開放式解讀)
- **normal distribution empirical rule** (若依賴課本圖片解讀)
- **任何 image-dependent 或是 open-response 題型**

**處置政策**：
- 狀態列為 `reserved` 或 `future_ai_judged`
- 僅做為 `visibility-only`
- 嚴禁進入 `deterministic allowlist`
- 不得列入 mastery 或 APR 計算

---

## 7. Adaptive Practice Decision

目前 Chap3 **不會** 連接 adaptive_practice chapter mode。

**理由**：
1. Deterministic coverage 剛完成核心部分，剩餘技能狀態尚待 closure。
2. 尚未釐清 Reserved / Future AI-judged 在 adaptive 中的 fallback 處置方案。
3. 必須先完成 Chap3 deterministic mainline closure（確立邊界），方可安全地設計 adaptive practice 規則，以免系統遭遇無法批改的題型而崩潰。

---

## 8. Recommended Next Phase

**推薦下一階段：Phase 7G：Chap3 deterministic mainline closure**

**理由**：
Chap3 的「高價值、低風險」純數值運算技能（如平均、標準差、全距、百分位數）均已進入 Runtime-Ready 狀態。剩下 10 個技能全數帶有高風險（語意不精確、圖表依賴、手寫依賴）。此時強行推進 7F 將帶來極高的邊際成本與技術債，建議立即進入 Phase 7G 執行 Closure，凍結 Chap3 開發狀態，為進入 Chap4 或是 Adaptive 準備建立穩固的基準線。

---

## 9. Final Confirmation

- 是否只新增 postcheck report：**是**
- 是否修改 production code：**否**
- 是否修改 tests：**否**
- 是否修改 DB：**否**
- 是否新增 generator：**否**
- 是否修改 adaptive scoring / mastery / APR / PPO：**否**
- 是否接 adaptive_practice：**否**
- 是否啟動 implementation：**否**
- 是否新增 SOP：**否**
