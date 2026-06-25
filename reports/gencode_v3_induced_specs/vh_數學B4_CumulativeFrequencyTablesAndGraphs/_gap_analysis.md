# B4 Cumulative Frequency — Visual Induced Spec Gap Analysis

Skill: `vh_數學B4_CumulativeFrequencyTablesAndGraphs`  
Examples: 3830–3834  
Generated: 2026-06-25 (extraction preflight + domain audit)

## Extraction run summary

| example_id | Gemini eligible | Gemini calls | Status |
|------------|-----------------|--------------|--------|
| 3830 | No | 0 | blocked — graph image missing |
| 3831 | No | 0 | blocked — stem data omitted, answer 略 |
| 3832 | No | 0 | blocked — graph image missing, answer 略 |
| 3833 | No | 0 | blocked — graph image missing, answer not verifiable |
| 3834 | Yes (text-only) | 1 attempted | failed — `gemini_api_key_missing` |

**Total Gemini calls this run: 1** (3834 only; API key not configured in environment)

---

## A. Per-example source completeness

| ID | 題幹 | 答案 | 解析 | 圖片附件 | 表格資料 | 可抽取 |
|----|------|------|------|----------|----------|--------|
| 3830 | ✓ 原文 | ✓ (1)16人 (2)21人 | ✓ 含累積讀值 | ✗ `missing_docx_image_asset` | ✗ 僅圖 | ✗ |
| 3831 | ✓ 但「數據略」 | ✗ 略 | ✓ 方法說明 | ✗ 無 | ✗ 缺表 | ✗ |
| 3832 | ✓ 原文 | ✗ 略 | ✓ 方法 | ✗ 缺圖 | ✗ | ✗ |
| 3833 | ✓ 原文 | ✗ 需視圖表而定 | ✓ 方法 | ✗ 缺圖 | ✗ | ✗ |
| 3834 | ✓ 含完整列資料 | ✓ a=8,b=22,c=6,d=40 | ✓ | ✗ 缺圖（表在題幹） | ✓ 內嵌 | △ 需 Gemini text-only |

**結論：** 4 題因缺原始圖檔或缺表資料，依規則不得呼叫 Gemini。3834 題幹已含完整表格，可 text-only 抽取（待 API key + 重跑）。

---

## B. Induced spec 摘要（預期語意，待 Gemini 確認）

### 3830 — 以下累積折線圖讀值（圖形題）
- visual_type: `cumulative_frequency_graph`
- cumulative_direction: `less_than`
- question_target: `read_graph` + `compare_intervals`（不及格人數、至少70分人數）
- 需從圖讀：60以下累積=16、70以下累積=29、總數50（解析有寫，但**不可在無圖時自動採信為 generator 約束**）

### 3831 — 完成累積次數分配表（表格題）
- visual_type: `cumulative_frequency_table` 或 `mixed`（以下+以上）
- cumulative_direction: `both`
- question_target: `construct_cumulative_table`
- **阻塞：** 題幹「數據略」、linked 例題 3 不在 DB

### 3832 — 以上累積折線圖（圖形題）
- cumulative_direction: `greater_than`
- question_target: `read_graph`
- **阻塞：** 缺圖、答案略

### 3833 — 以下累積折線圖（圖形題）
- cumulative_direction: `less_than`
- question_target: `read_graph`
- **阻塞：** 缺圖、答案不固定

### 3834 — 次數表 + 以下累積表求 a,b,c,d（混合表格）
- visual_type: `frequency_table_with_cumulative_fields`
- cumulative_direction: `less_than`
- question_target: `recover_class_frequency`
- blank_fields: `a`, `b`, `c`, `d`
- known: 0~20→4人, 40~60→10人, 60~80→12人, 累積12/34, 總人數40

---

## C. `build_cumulative_frequency_matrix()` 現有能力 vs spec gap

### 已可直接支援（3834 類）
- `class_frequency_from_cumulative_difference` — 相鄰累積差反推區間次數
- `cumulative_frequency_table_construction` — 由 class_frequencies 建以下/以上累積
- `build_less_than_cumulative_frequencies` / `recover_class_frequencies_from_cumulative`
- constraints: `class_bounds`, `class_frequencies`, `cumulative_direction`, `total_students`

### 部分支援（需 induced spec 餵 constraints）
- 固定列舉 `a,b,c,d` 空格拓撲 — domain 可算值，但**不讀取 induced spec 的 blank_cells**
- 多欄表（次數 + 以下累積同表）— `visual_spec.type=cumulative_frequency_table` 有三欄 headers，但未綁定 `table_spec.blank_cells`

### 不支援（3830/3832/3833 圖形題）
- 由 `graph_spec.points` 還原真實教材折線 anchor
- 閾值讀值（60分不及格、70/80分區間）需 `threshold` + `total_students` constraints
- 「至少 N 分」= 總數 − 以下累積 的雙步推論 — 無專用 operation payload
- `cumulative_frequency_graph_reading` 目前用隨機 class_bounds，**未消費 axis_spec / graph_spec**

### 3831 雙向表（以下+以上）
- 無 `both` direction 單次 matrix 輸出
- 無「空白待填」表格 construction 模式

---

## D. Renderer capability gap

| 能力 | 現況 | Gap |
|------|------|-----|
| HTML/JSON table | `visual_spec.rows` + headers | 缺 `blank_cells` 渲染、合併儲存格 |
| 累積折線圖 PNG/SVG | `table_chart_domain._build_cumulative_frequency_polygon_matrix` 在 **table_chart** domain | frequency_distribution 僅 `graph_points` 結構，**無 server renderer → image_base64** |
| cumulative ogive 軸標籤 | 無 | 需 `axis_spec.x_axis_semantics=upper_class_boundary` |
| 組界 vs 組中點 | 未區分 | graph x 軸必須用組界（累積圖），非組中點（次數折線圖） |
| image_base64 輸出 | histogram 有 matplotlib 路徑 | cumulative 在 frequency_distribution **無 matplotlib 繪圖** |
| 前端 visual_spec | `cumulative_frequency_polygon` type | 練習端是否支援需對照 UI；目前 validator 要求 visual asset |

---

## E. 建議下一輪本地修改（不硬編碼 example_id）

1. **`core/domain/statistics/frequency_distribution_domain.py`**
   - 接受 induced spec constraints：`threshold`, `asked_subquestions`, `blank_fields`, `graph_points`（非隨機）
   - 支援 `cumulative_direction=both` 輸出雙欄累積表

2. **`core/domain/statistics/cumulative_frequency.py`**
   - `read_fail_count_from_below_cumulative(threshold)`
   - `read_at_least_count_from_below_cumulative(threshold, total)`

3. **新增 renderer（建議 `core/domain/statistics/cumulative_frequency_renderer.py`）**
   - `render_cumulative_frequency_polygon_png(graph_spec, axis_spec) -> image_base64`
   - `render_frequency_table_with_blanks_html(table_spec) -> visual_spec`

4. **`core/gencode/domain_matrix_adapter.py`**
   - 將 induced `table_spec` / `graph_spec` 注入 `constraints` 與 `visual_spec`
   - cumulative graph 題輸出 `image_base64` 或結構化 `visual_spec` 供前端

5. **`scripts/extract_visual_induced_specs_b4_cumulative.py`**
   - 配置 Gemini API 後重跑 3834（及將來補圖後的 3830–3833）

6. **教材資產補齊（非 code）**
   - 自 DOCX/PDF 補 `image_assets` 至 `textbook_examples.notes`
   - 補 3831 linked 例題 3 原始表格

---

## F. Component 交付物建議

| Component | 類型 | image_base64 | HTML table | visual_spec + renderer |
|-----------|------|--------------|------------|----------------------|
| 3830 | 圖 | **必須** | — | 必須 |
| 3831 | 表 | 可選 | 可 | 建議 |
| 3832 | 圖 | **必須** | — | 必須 |
| 3833 | 圖 | **必須** | — | 必須 |
| 3834 | 混合表 | 可選 | **可直接** | 建議（含 blank 標記） |

---

## G. 本輪未執行項目（依指示）

- ✗ 發布 / 更新 tracker verified
- ✗ 覆蓋 production component
- ✗ 完整 regenerate
- ✗ 以 Gemini 生成 Python

## H. 產出 artifact 路徑

- `reports/gencode_v3_induced_specs/_source_audit_3830_3834.json`
- `reports/gencode_v3_induced_specs/vh_數學B4_CumulativeFrequencyTablesAndGraphs/src_383*_visual_induced_spec.json`
- `reports/gencode_v3_induced_specs/vh_數學B4_CumulativeFrequencyTablesAndGraphs/_extraction_run_summary.json`
- `scripts/extract_visual_induced_specs_b4_cumulative.py`
