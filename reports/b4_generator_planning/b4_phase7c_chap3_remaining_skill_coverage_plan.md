# B4 Phase 7C: Chap3 Remaining Skill Coverage Planning

## 1. 任務目標 (Objective)
在 Phase 7B 確立了 `CentralTendencyMeasures`、`WeightedMean`、`VarianceAndStandardDeviation` 與 `LinearTransformationOfData` 的核心計算題型後，本階段 (Phase 7C) 針對 Chapter 3 (統計) 尚未實作的剩餘技能進行全面盤點。

本報告以 Textbook Evidence 為基礎，將剩餘技能與題型分為五大類，以明確未來的開發與保留策略。
此階段為 Planning-Only，不涉及 Generator 開發、不接 Adaptive、亦不要求 Manual Smoke。

---

## 2. Chap3 尚未完成技能盤點與分類

根據 `b4_phase7a_chap3_textbook_evidence_skill_inventory_plan.md` 與證據彙整，我們對 Chap3 剩餘技能進行以下分類：

### 2.1 Deterministic-ready (可確定性自動出題)
具備明確計算規則、可透過數值或簡單表單進行嚴謹自動批改的題型。

- **`vh_數學B4_DispersionMeasures` (離散趨勢量數)**
  - **題型候選**：全距 (Range)、四分位距 (IQR)、四分位數 (Quartiles)、百分位數 (Percentiles)。
  - **評估**：可以直接給定一組未排序或已排序的小型數據（或簡單次數分配表），要求計算特定的百分位數或四分位距。適合完全 deterministic 化，風險低。

### 2.2 Needs Textbook Alignment (需對齊教材語境)
具備出題潛力，但由於文字描述、名詞定義或選項設計高度依賴課本寫法，必須在開發前進行嚴謹的 `textbook evidence alignment`，以免偏離教學目標或引發語義爭議。

- **`vh_數學B4_SamplingMethods` (抽樣方法)**
  - **題型候選**：簡單隨機抽樣、系統抽樣、分層隨機抽樣、部落抽樣的判斷題。
  - **評估**：需要固定各抽樣方法的標準敘述與生活情境選項（如：抽查學校學生、產品檢驗），避免選項產生模糊地帶。
- **`vh_數學B4_NormalDistributionAndEmpiricalRule` (常態分配與經驗法則)**
  - **題型候選**：68-95-99.7 比例推估、求某區間內的人數。
  - **評估**：若限縮為純數值推估則可轉為 deterministic，但需確認教材是否有包含標準化 $Z$ 分數或是單純依賴圖形面積判讀。
- **`vh_數學B4_OpinionPollInterpretation` (民意調查的解讀)**
  - **題型候選**：在 95% 信心水準下給定抽樣誤差，求信賴區間或解讀結果。
  - **評估**：文字題為主，需要將問題結構化為封閉式的計算（例如求區間上下限）或固定的選擇題選項。
- **`vh_數學B4_SamplingSurvey` (抽樣調查) & `vh_數學B4_StatisticalBasicConcepts` (統計的基本概念)**
  - **題型候選**：名詞解釋、母體/樣本/參數/統計量的對應關係。
  - **評估**：這兩個技能在目前的 Evidence 數量為 0 或極少，實作前需要額外補齊教材題庫資料以確認教學範疇。

### 2.3 Chart/Table/Image-dependent Reserved (依賴圖表或圖片，暫予保留)
需要學生直接「看圖」或「看複雜表格」才能作答的題目。受限於現有 Deterministic 引擎對動態產圖的支援度，目前予以保留。

- **`vh_數學B4_StatisticalChartReading` (統計圖表判讀)**
  - **題型候選**：從圓餅圖、長條圖、直方圖、折線圖中提取資訊並進行後續計算。
  - **評估**：高度依賴前端 SVG 繪圖或圖片資源。在確定共用圖表渲染元件（如 Recharts/D3 等）之前，這類題目應先標示為 `reserved`。

### 2.4 Handwriting/Free-response Reserved (手寫或開放式作答保留)
統計學中偏向說明調查原因、解釋結果、或開放式設計抽樣機制的題型。

- **部分抽樣設計與民調解讀題**
  - **題型候選**：「請說明為何此抽樣方法有偏差？」或「請設計一個公平的抽樣方式」。
  - **評估**：無法進行 deterministic exact match，全面保留給未來的 Teacher Review 或是 AI-Judged Free Response 流程。

### 2.5 Future AI-judged (未來由 AI 批改或生成的複雜圖表操作題)
涉及學生需要「繪製」圖表或「完整填寫」大型資料表的題型。這類題目不僅出題複雜，批改時更需要容許一定的表現形式彈性。

- **`vh_數學B4_FrequencyDistributionTableConstruction` (統計資料的次數分配表編製步驟)**
  - **題型候選**：給定原始數據，要求劃記並完成分組次數分配表。
- **`vh_數學B4_HistogramsAndFrequencyPolygons` (次數分配直方圖與次數分配折線圖的繪製)**
  - **題型候選**：要求學生在坐標平面上畫出直方圖或折線圖。
- **`vh_數學B4_CumulativeFrequencyTablesAndGraphs` (累積次數分配表與累積折線圖)**
  - **題型候選**：繪製「以下/以上累積次數分配折線圖」。
- **`vh_數學B4_DataOrganizationAndCharts` (資料整理與圖表編製)**
  - **評估**：綜合性製圖題。這四個技能需要前端提供可互動的繪圖畫布 (canvas) 或是大型表格填寫元件，並搭配 AI 進行影像或結構化資料的寬鬆比對 (loose check)，因此將整體劃入 `Future AI-judged`。

---

## 3. 下一階段建議 (Recommendations)

基於上述盤點，建議在進入下一階段的 Implementation (Phase 7D) 時，採取以下策略：

1. **優先實作 Deterministic-Ready**：
   - 即刻針對 `vh_數學B4_DispersionMeasures` 進行開發，實作全距、百分位數、四分位距的純數值計算題型。
2. **開展 Needs Textbook Alignment 的語料清理**：
   - 針對抽樣方法、常態分配與民調解讀，整理出「固定語句模板」並確認封閉性檢核方式（例如：信賴區間求值、抽樣情境選擇題）。
3. **明確隔離 Reserved / AI-judged**：
   - 將圖表判讀、圖表繪製、次數分配表編製等技能在路由清單中標示為 `chart_dependent` 或 `ai_judged`，避免在未具備支援能力前誤入 Deterministic Runtime，並透過 8.3 SOP 規定回傳正確的 Not-Enabled 中性訊息。

## 4. Final Confirmation
- 是否修改了任何 production code/tests/DB？ **否**
- 是否開始寫 generator？ **否**
- 是否直接接上 adaptive？ **否**
- 是否要求人工 smoke？ **否**
- 是否達成 Planning-Only 要求？ **是**
