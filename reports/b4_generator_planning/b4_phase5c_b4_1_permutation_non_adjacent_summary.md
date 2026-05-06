# Phase 5C-B4.1：排列「不相鄰／插空法」enrichment

## 1. 依據 Phase 5C-B0-Followup（partially_supported）

「排列中的相鄰／不相鄰」課本題型中，**必須相鄰**已有 `permutation_adjacent_block`；**不得相鄰（插空法）**先前在 generators 中未涵蓋。本階段補上 **deterministic、整數答案** 題型，與相鄰題型並列，供 B4 第 1 章單元練習使用。

**未**修改 Phase 4E coverage matrix；**未**改 `permutation_adjacent_block` 行為；**未**接入 excluded／manual_review 路徑。

## 2. 新增 generator／problem_type

| 項目 | 值 |
|------|-----|
| 函式 | `permutation_non_adjacent_arrangement` |
| 檔案 | `core/vocational_math_b4/generators/permutation.py` |
| `problem_type_id` | `permutation_non_adjacent_arrangement` |
| `generator_key` | `b4.permutation.permutation_non_adjacent_arrangement` |

## 3. 插空法數學公式

先將「多數群體」\(m\) 個相異對象排成一列：\(m!\)。  
形成 \(m+1\) 個空位；自其中選 \(k\) 個放入「少數群體」\(k\) 個相異對象：\(C(m+1,k)\)；再排列少數群體：\(k!\)。

**總數：**  
\[
m! \times C(m+1,k) \times k! = m! \times P(m+1,k)
\]

條件：\(k \in \{2,3\}\) 為主；\(m \ge k\)（敘述上多數／少數合理）；並以 `_MAX_NON_ADJACENT_ANSWER`（5_000_000）避免答案過大。

## 4. template_context 清單

| `template_context` | 語境摘要 |
|--------------------|----------|
| `boys_girls_lineup` | 男生 \(m\)、女生 \(k\)，女生不得相鄰 |
| `team_a_b_lineup` | 甲組 \(m\)、乙組 \(k\)，乙組不得相鄰 |
| `color_balls_arrangement` | 相異藍球 \(m\)、相異紅球 \(k\)，紅球不得相鄰 |
| `VIP_general_seating` | 一般成員 \(m\)、貴賓 \(k\)，貴賓不得相鄰 |

題干皆強調 **人／物互不相同**（球題另述「可辨識」），並註明 **只需方法數、不必列出所有排列**。

## 5. Router 接入

`core/vocational_math_b4/services/question_router.py` 中 **`vh_數學B4_PermutationOfDistinctObjects`** 新增：

- `subskill_id`: `b4_ch1_permutation_non_adjacent_01`
- `generator_fn`: `permutation_generators.permutation_non_adjacent_arrangement`

既有 `permutation_role_assignment`、`permutation_formula_evaluation`、`permutation_full_arrangement`、`permutation_adjacent_block`、`permutation_digit_parity` **均保留**。

`skills/vh_數學B4_PermutationOfDistinctObjects.py` 為通用 router wrapper，**無需**修改。

## 6. Validator／allowlist

- `vh_數學B4_PermutationOfDistinctObjects` 已在 `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST`。
- `permutation_non_adjacent_arrangement` **未**加入 `B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES`。

## 7. parameters（摘要）

含：`majority_group_label`、`minority_group_label`、`majority_count`（\(m\)）、`minority_count`（\(k\)）、`gap_count`（\(m+1\)）、`chosen_gap_count`（\(k\)）、`template_context`、`formula_components`（`majority_factorial`、`gap_choose`、`minority_factorial` 數值）、`answer`、`parameter_tuple`。

## 8. QA 指令與結果（本機）

```text
python -m pytest -q tests/test_phase5c_b4_1_permutation_non_adjacent_generator.py
# 106 passed

python -m pytest -q tests/test_vocational_math_b4_question_router_registry_canonical.py
python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py
python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py
python -m pytest -q tests/test_phase5b_fix_e1_b4_remediation_bridge.py
python -m pytest -q tests/test_phase5c_b3_grid_shortest_path_generator.py
python -m pytest -q tests/test_phase5c_b3_binomial_specific_coefficient_generators.py
# 260 passed（含 SQLAlchemy DeprecationWarning）
```

## 9. 未處理項目（後續 phase）

- 階乘方程變形
- 組合遞移／錯列和
- 純組合數和敘述 enrichment
- 完整二項式展開仍保留 future AI-judged
