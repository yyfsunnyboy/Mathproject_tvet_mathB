# Manual Visual Induced Spec — Gap Analysis (Post-Extraction)

Skill: `vh_數學B4_CumulativeFrequencyTablesAndGraphs`  
Source: 4 張人工教材截圖（手工抽取，無 Gemini）  
Date: 2026-06-25

---

## 1. 題型 vs `statistics.frequency_distribution` 支援矩陣

| 題型 artifact | domain operation | 目前可直接支援 | 需補強 |
|---------------|------------------|----------------|--------|
| below_cumulative_graph_reading_01 | cumulative_frequency_graph_reading | △ 部分 | 固定 graph_points、threshold 推論、multi_part |
| bidirectional_cumulative_table_01 | cumulative_frequency_table_construction | △ 部分 | `cumulative_direction=both`、fill_table UI |
| above_cumulative_graph_reading_01 | greater_than_cumulative_frequency_reading | △ 部分 | above 方向 threshold 推論、multi_part |
| above_cumulative_mcq_fail_count_01 | greater_than_cumulative_frequency_reading | ✗ | MCQ + threshold_inference |
| above_cumulative_interval_difference_01 | class_frequency_from_cumulative_difference | ✓ 接近 | 需餵入固定 graph_points 與 bound 索引 |

---

## 2. Renderer gap

| 題型 | 需要 image_base64 | 可用 HTML table | 需要 server renderer |
|------|-------------------|-----------------|-------------------|
| 圖1 以下累積圖 | **是**（練習端顯示折線圖） | 否 | **是** — ogive PNG/SVG from `data_points` |
| 圖2 雙向表 | 否 | **是** | 建議 — blank cell 標記 |
| 圖3 以上累積圖 | **是** | 否 | **是** |
| 圖4 MCQ | **是** | 否 | **是** + choice 渲染 |
| 圖4 區間差 | **是** | 否 | **是** |

**現況：** `frequency_distribution_domain.build_cumulative_frequency_matrix()` 只輸出 `visual_spec.rows` / `graph_points` 結構，**無** matplotlib/renderer 產 `image_base64`。`table_chart_domain` 有 ogive 繪圖但未接到本 domain pipeline。

---

## 3. Generator gap

### 已具備（可擴充 constraints 即可）
- `build_less_than_cumulative_frequencies` / `build_greater_than_cumulative_frequencies`
- `read_interval_frequency_from_cumulative`（圖4中段：20−13=7）
- `cumulative_frequency_graph_points` 結構輸出

### 缺少
- **threshold_inference**：`fail_below_60 = below_cum(60)` 或 `total - above_cum(60)`
- **complement_inference**：`at_least_70 = total - below_cum(70)`
- **multi_part answer**：一題多子題 `[16, 21]`、`[15, 15]`
- **multiple_choice**：圖4上半需 4 選項 + `choice_label_checker`
- **cumulative_direction=both**：同表雙欄累積（圖2）
- **fill_table render_mode**：學生填寫累積欄（非只讀答案）
- **固定教材 graph_points 注入**：目前仍隨機 `class_bounds`

---

## 4. Capability 對照（第 7、8 點）

| Capability | 適用題型 |
|------------|----------|
| recover_class_frequency | 圖4中段（above 相鄰差） |
| threshold_inference | 圖1(1)、圖3(1)、圖4上半（不及格人數） |
| multi_part | 圖1、圖3 |
| multiple_choice | 圖4上半 |
| both_direction_table | 圖2 |

---

## 5. 下一輪本地實作優先順序（僅規劃）

### P0 — Renderer
1. **新增** `core/domain/statistics/cumulative_frequency_renderer.py`
   - `render_below_ogive_png(data_points, *, total=None) -> str` (base64)
   - `render_above_ogive_png(data_points) -> str`
   - `render_bidirectional_table_html(table_rows, blank_columns) -> visual_spec`

### P1 — Domain
2. **`core/domain/statistics/cumulative_frequency.py`**
   - `infer_fail_count_below_threshold(cumulative, threshold, direction, total)`
   - `infer_at_least_count(cumulative, threshold, direction, total)`

3. **`frequency_distribution_domain.py`**
   - 接受 `domain_constraints` from induced spec（graph_points, thresholds, sub_questions）
   - 支援 `cumulative_direction=both`

### P2 — Adapter / Runtime
4. **`core/gencode/domain_matrix_adapter.py`**
   - 讀 induced spec → constraints + `image_base64` / `visual_spec`
   - multi_part → `answers: [{part, value}]`
   - MCQ → `choices` + `semantic_answer`

5. **`core/routes/practice.py`**（或 visual 呈現層）
   - 支援 `visual_spec.type=cumulative_frequency_polygon` + `image_base64`
   - 支援 `fill_table` 互動（若圖2要可作答）

### P3 — Validator
6. **`core/gencode/validators/__init__.py`**
   - graph 題必須有 `image_base64` 或等價 `visual_spec` 且 points 與 induced spec 一致

---

## 6. 與 textbook example 的鬆耦合對照（非硬編碼）

| induced spec | 語意相近 DB 例題 | 備註 |
|--------------|------------------|------|
| below_cumulative_graph_reading_01 | 3830, 3833 | 以下累積折線圖 |
| bidirectional_cumulative_table_01 | 3831 | 完成累積表 |
| above_cumulative_graph_reading_01 | 3832 | 以上累積折線圖 |
| above_cumulative_interval_difference_01 | 3834 類型 | 表格/累積差反推 |

**production routing 仍依題面語意分類，不得寫死 example_id。**

---

## 7. 本輪產出

- `manual_sources/*.source.json` × 4（圖源結構）
- `induced_specs/*.json` × 5（題型規格）
- `_manual_extraction_manifest.json`
- 本 gap analysis

**Gemini 呼叫：0**  
**Production / tracker 變更：0**
