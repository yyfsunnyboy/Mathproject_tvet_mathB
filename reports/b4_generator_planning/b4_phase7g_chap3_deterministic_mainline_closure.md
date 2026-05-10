# B4 Chapter 3 Phase 7G：Deterministic Mainline Closure

## 1. Scope and Guardrails

本階段 (Phase 7G) 專司 Chap3 Deterministic Mainline 收斂與總結。為確保系統一致性與安全，本輪作業嚴格遵循以下限制：
- 不改 code
- 不改 tests
- 不改 DB
- 不新增 generator
- 不接 adaptive
- 不新增 SOP

---

## 2. Completed Deterministic Runtime-ready Scope

經過 Phase 7B、7B-D 及 7D 的實作與修補，Chap3 已完成高確定性純數值統計量題型的涵蓋。以下為順利進入 Deterministic Runtime-ready 狀態之技能清單：

| phase | skill_id | completed problem_type | runtime status | scenario diversity status | notes |
|---|---|---|---|---|---|
| 7B-D | vh_數學B4_CentralTendencyMeasures | mean/median/mode basic numeric | Runtime-Ready | Compliant | 具備多情境之平均數、中位數、眾數 |
| 7B-D | vh_數學B4_WeightedMean | weighted_mean_basic | Runtime-Ready | Compliant (Repaired) | 已涵蓋成績學分、混和物、單價情境 |
| 7B-D | vh_數學B4_VarianceAndStandardDeviation | variance/std_dev basic numeric | Runtime-Ready | Compliant (Repaired) | 涵蓋純資料與情境資料變異數/標準差計算 |
| 7B-D | vh_數學B4_LinearTransformationOfData | linear_transform_mean/std | Runtime-Ready | Compliant (Repaired) | 涵蓋平移、伸縮及還原情境 |
| 7D | vh_數學B4_DispersionMeasures | range/percentile/quartile/iqr basic | Runtime-Ready | Compliant | 涵蓋全距、百分位數、四分位數及四分位距 |

---

## 3. Scenario Diversity and SOP v0.1.5 Compliance

針對 SOP v0.1.5 中關於多樣性與防呆機制之規範：
- **7B-D** 已針對 7B 遺留之情境單調風險進行修復，擴充題幹變異與隨機情境 `scenario`。
- **7D** 開發初期即導入 SOP v0.1.5 原則，不僅內建至少三個情境，並加入 `test_generator_scenario_diversity` 之自動化測試。
- 上述已完成的 generator 皆具備 `scenario_id` / `scenario` 或等價防護機制，不再需要人工進行大量的 manual smoke 來查驗變化度。

**結論**：`NO_IMMEDIATE_VARIETY_REPAIR_REQUIRED`

---

## 4. Remaining Skills Final Decision

經 Phase 7E Postcheck 審視，Chap3 尚餘 10 個不應硬做 deterministic 的技能，決議如下：

| skill_id | final decision | reason | future path |
|---|---|---|---|
| vh_數學B4_SamplingMethods | needs_textbook_alignment | 高度依賴選項語意及情境對齊 | 待文本清理後作為未來實作候選 |
| vh_數學B4_NormalDistributionAndEmpiricalRule | needs_textbook_alignment | 需確認課本題型是否為 Z 分數或圖形面積 | 待清理題型邊界後評估 |
| vh_數學B4_OpinionPollInterpretation | needs_textbook_alignment | 偏向語意解讀，需固定選項模板 | 固定結構後可轉換為選擇或信賴區間求值題 |
| vh_數學B4_SamplingSurvey | not_suitable_now | 教材練習來源證據不足 | 暫不處理 |
| vh_數學B4_StatisticalBasicConcepts | not_suitable_now | 完全無課本題庫來源證據 | 暫不處理 |
| vh_數學B4_StatisticalChartReading | chart_table_image_reserved | 必須依賴前端產生 SVG 或是看圖作答 | 保留給未來 AI 或前端圖表元件成熟後處理 |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | future_ai_judged | 需要完整大表填寫與畫圖 | 保留由 AI 或老師批改 |
| vh_數學B4_DataOrganizationAndCharts | future_ai_judged | 綜合性製表與圖表編製 | 保留由 AI 或老師批改 |
| vh_數學B4_FrequencyDistributionTableConstruction | future_ai_judged | 需要劃記並完整建立次數分配表 | 保留由 AI 或老師批改 |
| vh_數學B4_HistogramsAndFrequencyPolygons | future_ai_judged | 需要坐標繪圖（直方圖與折線圖） | 保留由 AI 或老師批改 |

---

## 5. Reserved / Future AI-judged Policy

為了防範系統運行錯誤與減輕邊際開發成本，明訂以下題型**絕不進入 Deterministic Allowlist**：
- chart reading (圖表判讀提取資料)
- histogram / line chart drawing (繪製長條圖/直方圖/折線圖)
- full frequency table construction (編製完整次數分配表)
- sampling method explanation (抽樣方法開放式解釋)
- opinion poll interpretation (若為開放式的民調解讀)
- 任何 image-dependent / chart-dependent / table-heavy 題型

**既定政策**：
- 前端維持 `visibility-only`
- 不進 `mastery` 與 `APR`
- 不進 deterministic checker 路由
- 留待 future AI-judged 或 teacher review 後再另開專屬 phase 處理

---

## 6. Adaptive Practice Decision

Chap3 本輪**不接** adaptive_practice chapter mode。

**理由**：
- 目前 deterministic mainline 僅完成了最高價值且低風險的純數值核心計算。
- 章節內仍有大量技能屬於 reserved 或 future_ai_judged 狀態。
- 若強行在此階段開放 adaptive_practice chapter mode，極易遇到「coverage 不完整」或演算法推送了「尚未支援批改/需依賴外部圖表」的題目而導致崩潰。
- 此決策應推遲至未來 Chap3 Reserved Policy 有明確 fallback 機制，或下一章節流程穩定後再綜合考慮。

---

## 7. Closure Status

**Chap3 deterministic mainline = ACCEPTED WITH RESERVED SCOPE**

**說明**：
Chap3 已穩健完成最具實用性、低風險且高確定性的純數值統計計算核心技能（集中趨勢、離散趨勢、資料線性變換）。
剩餘未完成之技能並非 Bug，而是因為牽涉到「圖表互動」、「完整表格」與「語意不確定性」等客觀因素，我們選擇主動性暫緩與保留 (Deferred/Reserved)。此決策不僅有效限縮風險，亦確保了已上線功能的高穩定性。

---

## 8. Recommended Next Phase

考量到 Chap3 已收尾，且繼續開發高風險 Reserved 題型的技術投資報酬率較低，建議下一步直接邁向新單元：

- **Option A (推薦優先)**：
  **Phase 8A：B4 Chap4 Textbook Evidence and Skill Inventory Planning**
  *理由*：最符合推進主線進度的邏輯，能讓 Deterministic coverage 向前拓展。

- **Option B**：
  B1-B3 / 國中 prerequisite content planning
  *理由*：若欲強化先備知識與 Remediation 演算法，可著手建立更低年級的知識節點。

- **Option C**：
  Chap3 reserved / future AI-judged planning
  *理由*：僅當專案短期內「極度強烈要求」具備畫圖與表格能力時才選擇，不建議作為首選。

---

## 9. Final Confirmation

- 是否只新增 closure report：**是**
- 是否修改 production code：**否**
- 是否修改 tests：**否**
- 是否修改 DB：**否**
- 是否新增 generator：**否**
- 是否修改 adaptive scoring / mastery / APR / PPO：**否**
- 是否接 adaptive_practice：**否**
- 是否新增題型：**否**
- 是否啟動下一 phase：**否**
- 是否新增 SOP：**否**
