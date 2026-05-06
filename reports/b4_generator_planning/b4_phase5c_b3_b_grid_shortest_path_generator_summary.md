# Phase 5C-B3-B：棋盤格最短路徑（僅向右／向上）deterministic generator

## 1. 依據 Phase 5C-B0-Followup 的缺口

「棋盤格最短路徑」在 follow-up 盤點中為 **missing_generator**。本階段補上 **整數答案、文字敘述、LaTeX 解說** 的 deterministic 題型，對應課本／統測常見「任意走、必經指定點、不經指定點」三種問法。

**未**修改 Phase 4E coverage matrix；**未**接入 `tree_diagram_listing`、`binomial_expansion_basic`、`pascal_triangle_derivation` 或 manual_review／future_ai_judged 路徑。

## 2. 新增 generator／problem_type

| 項目 | 值 |
|------|-----|
| 函式 | `grid_shortest_path_count` |
| 檔案 | `core/vocational_math_b4/generators/combination.py` |
| `problem_type_id` | `grid_shortest_path_count` |
| `generator_key` | `b4.combination.grid_shortest_path_count` |

## 3. 三個 variant

| variant | 題意 | 答案 |
|---------|------|------|
| `basic` | 甲→乙，僅能向右或向上各走滿給定段數 | \(C(a+b,a)\)，此處 \(a=\) `width`，\(b=\) `height` |
| `via_point` | 必須經過丙（兩段路程的右段／上段數於題干給定） | \(\text{甲→丙} \times \text{丙→乙}\) |
| `avoid_point` | 不得經過丙 | 全部最短路徑數減去必經丙者（並保證 **answer > 0**） |

中繼點座標以「從甲出發已走的右段、上段數」表示：\(1 \le \texttt{mid\_x} \le \texttt{width}-1\)、\(1 \le \texttt{mid\_y} \le \texttt{height}-1\)，不與甲（0,0）、乙（`width`,`height`）重合。

## 4. 數學公式

- 水平段數 \(a\)、鉛直段數 \(b\)：最短路徑數 **\(C(a+b,a)\)**。
- 必經丙：**\(C(a_1+b_1,a_1)\times C(a_2+b_2,a_2)\)**（甲→丙、丙→乙）。
- 不經丙：**\(C(a+b,a) - C(a_1+b_1,a_1)\times C(a_2+b_2,a_2)\)**。

`seed % 3` 決定 variant（並輔以難度與 `seen_parameter_tuples` 抽樣）；`difficulty==1` 且 `seed` 為 1–6 時有固定 preset 以利穩定 smoke。

## 5. Router 接入

`core/vocational_math_b4/services/question_router.py` 中 **`vh_數學B4_CombinationApplications`** 新增一筆 entry：

- `subskill_id`: `b4_ch1_grid_shortest_path_01`
- `generator_fn`: `combination_generators.grid_shortest_path_count`

`skills/vh_數學B4_CombinationApplications.py` 已為通用 `generate_for_skill` wrapper，**無需**修改。

## 6. Validator／allowlist

- `vh_數學B4_CombinationApplications` 已在 `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST`。
- `grid_shortest_path_count` **未**加入 `B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES`；`validate_b4_deterministic_adaptive_generator_payload` 可正常通過。

## 7. parameters 欄位（摘要）

含：`variant`、`width`／`height`（並附 `a`／`b` 同值）、`mid_x`／`mid_y`（`basic` 為 `None`）、`total_paths`、`via_paths`（`basic` 為 0）、`answer`、`template_context`、`parameter_tuple`。

`template_context`：`chessboard_roads`／`campus_grid`／`street_grid`／`generic_ab`（語境變化，無圖片）。

## 8. QA 指令與結果（本機）

```text
python -m pytest -q tests/test_phase5c_b3_grid_shortest_path_generator.py
# 107 passed

python -m pytest -q tests/test_vocational_math_b4_question_router_registry_canonical.py
python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py
python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py
python -m pytest -q tests/test_phase5b_fix_e1_b4_remediation_bridge.py
python -m pytest -q tests/test_phase5c_b3_binomial_specific_coefficient_generators.py
# 153 passed（含 SQLAlchemy DeprecationWarning）
```

## 9. 未處理項目（後續 phase）

- 不相鄰排列
- 階乘方程變形
- 組合遞移／錯列和
- 純組合數和敘述 enrichment
- 完整二項式展開仍保留 future AI-judged
