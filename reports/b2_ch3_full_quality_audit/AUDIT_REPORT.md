# B2 第 3 章全 Skill 品質稽核報告

- stamp: `20261123_134714`
- gate: **PASS_ENGINEERING**
- skills: 15；Y 合計（非去重）=47；全章去重 problem_type=42
- status: `{"PASS": 15}`
- UI/Canvas/AI Tutor: NOT_TESTED

## Skill 清單

| Skill | 名稱 | TE | Y | 掌握 | status |
|---|---|---:|---:|---|---|
| `vh_數學B2_SubSection_3_1_1` | 向量定義 | 3 | 2 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_1_2` | 向量的加法作圖 | 3 | 1 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_1_3` | 向量的減法作圖 | 7 | 1 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_1_4` | 向量的實數積作圖 | 14 | 6 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_2_1` | 向量的坐標表示法 | 11 | 6 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_2_2` | 向量加減的坐標表示法 | 15 | 6 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_2_3` | 向量實數積的坐標表示法 | 2 | 2 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_2_4` | 向量實數積的基本性質 | 3 | 2 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_2_5` | 向量的平行 | 4 | 2 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_2_6` | 單位向量 | 5 | 2 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_3_1` | 向量的夾角 | 4 | 3 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_3_2` | 向量內積的定義 | 5 | 3 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_3_3` | 向量內積的坐標表示法 | 9 | 5 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_3_4` | 兩向量的垂直 | 4 | 2 | X/Y | **PASS** |
| `vh_數學B2_SubSection_3_3_5` | 向量內積的性質 | 6 | 4 | X/Y | **PASS** |

## Shared problem_type_id

```json
{
  "compute_cosine_of_angle_from_dot": [
    "vh_數學B2_SubSection_3_3_1",
    "vh_數學B2_SubSection_3_3_3"
  ],
  "compute_dot_product_from_magnitudes_angle": [
    "vh_數學B2_SubSection_3_3_2",
    "vh_數學B2_SubSection_3_3_5"
  ],
  "compute_vector_linear_combination": [
    "vh_數學B2_SubSection_3_2_2",
    "vh_數學B2_SubSection_3_2_4"
  ],
  "simplify_vector_path_expression": [
    "vh_數學B2_SubSection_3_1_2",
    "vh_數學B2_SubSection_3_1_3"
  ],
  "solve_parallelogram_fourth_vertex": [
    "vh_數學B2_SubSection_3_2_1",
    "vh_數學B2_SubSection_3_2_2"
  ]
}
```

## 抽樣摘要

### `vh_數學B2_SubSection_3_1_1` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `express_named_vectors_in_given_basis` | 10 | 4 | 6 | 4 | HAS_VARIATION | PASS | 0 | True |
| `identify_equal_vector_mcq` | 30 | 1 | 4 | 4 | LIMITED_VARIATION | PASS | 0 | True |

### `vh_數學B2_SubSection_3_1_2` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `simplify_vector_path_expression` | 10 | 6 | 9 | 5 | HAS_VARIATION | PASS | 0 | True |

### `vh_數學B2_SubSection_3_1_3` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `simplify_vector_path_expression` | 10 | 4 | 7 | 3 | HAS_VARIATION | PASS | 0 | True |

### `vh_數學B2_SubSection_3_1_4` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `construct_linear_combination_choice` | 10 | 10 | 4 | 4 | HAS_VARIATION | PASS | 0 | True |
| `express_linear_combination_from_givens` | 10 | 9 | 9 | 9 | HAS_VARIATION | PASS | 0 | False |
| `express_section_point_vector` | 10 | 3 | 10 | 3 | HAS_VARIATION | PASS | 0 | True |
| `identify_resultant_path_mcq` | 30 | 1 | 4 | 4 | LIMITED_VARIATION | PASS | 0 | True |
| `solve_scalar_multiple_relation_fill` | 10 | 3 | 9 | 7 | HAS_VARIATION | PASS | 0 | True |
| `solve_section_coefficient_pair` | 30 | 1 | 14 | 14 | LIMITED_VARIATION | PASS | 0 | True |

### `vh_數學B2_SubSection_3_2_1` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `compute_directed_segment_and_magnitude` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |
| `compute_directed_segment_mixed_multipart` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |
| `compute_triangle_perimeter_from_two_vectors` | 30 | 1 | 4 | 4 | LIMITED_VARIATION | PASS | 0 | False |
| `compute_vector_components_and_magnitude` | 10 | 9 | 9 | 9 | HAS_VARIATION | PASS | 0 | False |
| `solve_equal_vector_coordinates` | 30 | 2 | 4 | 2 | LIMITED_VARIATION | PASS | 0 | False |
| `solve_parallelogram_fourth_vertex` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |

### `vh_數學B2_SubSection_3_2_2` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `compute_chain_closure_vector_mcq` | 10 | 10 | 3 | 3 | HAS_VARIATION | PASS | 0 | False |
| `compute_point_vectors_linear_combination` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |
| `compute_triangle_chain_and_perimeter` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |
| `compute_vector_linear_combination` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |
| `compute_vector_sum_difference` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |
| `solve_parallelogram_fourth_vertex` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |

### `vh_數學B2_SubSection_3_2_3` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `solve_collinear_ratio_mcq` | 30 | 1 | 4 | 4 | LIMITED_VARIATION | PASS | 0 | False |
| `solve_point_from_vector_combination` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |

### `vh_數學B2_SubSection_3_2_4` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `compute_vector_linear_combination` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |
| `solve_unknown_vector_linear_equation` | 30 | 1 | 4 | 4 | LIMITED_VARIATION | PASS | 0 | False |

### `vh_數學B2_SubSection_3_2_5` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `solve_parallel_then_magnitude_mcq` | 10 | 4 | 3 | 3 | HAS_VARIATION | PASS | 0 | False |
| `solve_parallel_vector_parameter` | 10 | 10 | 10 | 9 | HAS_VARIATION | PASS | 0 | False |

### `vh_數學B2_SubSection_3_2_6` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `compute_scaled_direction_vector` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |
| `identify_unit_vector_mcq` | 30 | 1 | 4 | 4 | LIMITED_VARIATION | PASS | 0 | False |

### `vh_數學B2_SubSection_3_3_1` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `classify_angle_quality_from_dot_mcq` | 30 | 1 | 4 | 4 | LIMITED_VARIATION | PASS | 0 | False |
| `compute_cosine_of_angle_from_dot` | 10 | 10 | 8 | 8 | HAS_VARIATION | PASS | 0 | False |
| `solve_navigation_heading_correction` | 10 | 9 | 9 | 9 | HAS_VARIATION | PASS | 0 | True |

### `vh_數學B2_SubSection_3_3_2` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `compute_dot_identity_multipart` | 10 | 9 | 9 | 9 | HAS_VARIATION | PASS | 0 | False |
| `compute_dot_product_from_magnitudes_angle` | 10 | 9 | 9 | 9 | HAS_VARIATION | PASS | 0 | False |
| `compute_regular_polygon_edge_dot` | 10 | 8 | 9 | 5 | HAS_VARIATION | PASS | 0 | True |

### `vh_數學B2_SubSection_3_3_3` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `compute_cosine_of_angle_from_dot` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |
| `compute_dot_product_coordinates` | 10 | 10 | 10 | 8 | HAS_VARIATION | PASS | 0 | False |
| `compute_midpoint_dot_product` | 30 | 1 | 4 | 4 | LIMITED_VARIATION | PASS | 0 | False |
| `plot_navigation_points_coordinates` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | True |
| `solve_dot_product_parameter_mcq` | 30 | 1 | 4 | 4 | LIMITED_VARIATION | PASS | 0 | False |

### `vh_數學B2_SubSection_3_3_4` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `solve_perpendicular_composite_parameter` | 10 | 10 | 9 | 9 | HAS_VARIATION | PASS | 0 | False |
| `solve_perpendicular_vector_parameter` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |

### `vh_數學B2_SubSection_3_3_5` — PASS
| pt | ok | stems | params | answers | note | checker | labels | visual |
|---|---:|---:|---:|---:|---|---|---:|---|
| `classify_dot_sign_from_diagram_mcq` | 30 | 1 | 4 | 4 | LIMITED_VARIATION | PASS | 0 | True |
| `compute_dot_product_from_magnitudes_angle` | 10 | 9 | 7 | 6 | HAS_VARIATION | PASS | 0 | False |
| `expand_perpendicular_dot_product` | 10 | 10 | 10 | 10 | HAS_VARIATION | PASS | 0 | False |
| `solve_angle_from_magnitude_identity` | 10 | 7 | 7 | 7 | HAS_VARIATION | PASS | 0 | False |

