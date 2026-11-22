# B2 第 1 章全 Skill 品質與 SOP 稽核報告

- stamp: `20261122_160007`
- sample_n: 30
- skills: 19
- status_counts: `{"INACTIVE_OK": 3, "PASS": 8, "NEEDS_DECISION": 8}`

## Skill 清單

| Skill | 名稱 | active | TE | Y | 掌握制 | status |
|---|---|---:|---:|---:|---|---|
| `vh_數學B2_DirectedAngle` | 有向角 | False | 0 | 0 | consecutive_correct_legacy | **INACTIVE_OK** |
| `vh_數學B2_RatioAndRatioValue` | 比與比值 | True | 2 | 1 | problem_type_mastery | **PASS** |
| `vh_數學B2_SubSection_1_3_1` | 標準位置角 | True | 3 | 1 | consecutive_correct_legacy | **NEEDS_DECISION** |
| `vh_數學B2_SubSection_1_4_1` | 正弦函數的圖形與其週期現象的表徵 | False | 0 | 0 | consecutive_correct_legacy | **INACTIVE_OK** |
| `vh_數學B2_SubSection_1_3_2` | 任意角的三角函數 | True | 3 | 1 | consecutive_correct_legacy | **NEEDS_DECISION** |
| `vh_數學B2_SubSection_1_4_2` | 餘弦函數的圖形與其週期現象的表徵 | False | 0 | 0 | consecutive_correct_legacy | **INACTIVE_OK** |
| `vh_數學B2_TrigonometricFunctionsOfAcuteAngles` | 銳角三角函數 | True | 11 | 4 | problem_type_mastery | **PASS** |
| `vh_數學B2_AngleMeasurementAndConversion` | 角的度量與換算 | True | 5 | 1 | problem_type_mastery | **PASS** |
| `vh_數學B2_SubSection_1_4_3` | 正切函數的圖形與其週期現象的表徵 | True | 8 | 3 | consecutive_correct_legacy | **NEEDS_DECISION** |
| `vh_數學B2_TrigonometricValuesOfSpecialAngles` | 30°、45°、60° 特別角的三角函數值 | True | 5 | 2 | problem_type_mastery | **PASS** |
| `vh_數學B2_ArcLengthAndAreaOfSector` | 扇形的弧長與面積 | True | 8 | 2 | problem_type_mastery | **PASS** |
| `vh_數學B2_CalculatingFunctionValuesUsingCalculator` | 使用計算機計算函數值 | True | 2 | 1 | problem_type_mastery | **PASS** |
| `vh_數學B2_SubSection_1_3_4` | 三角函數值在四個象限的正負情形 | True | 7 | 2 | consecutive_correct_legacy | **NEEDS_DECISION** |
| `vh_數學B2_SubSection_1_4_4` | 三角函數圖形的變化與週期 | True | 13 | 9 | consecutive_correct_legacy | **NEEDS_DECISION** |
| `vh_數學B2_FundamentalTrigonometricIdentities` | 三角函數的基本關係式 | True | 10 | 3 | problem_type_mastery | **PASS** |
| `vh_數學B2_SubSection_1_3_5` | 象限角的三角函數值 | True | 3 | 1 | consecutive_correct_legacy | **NEEDS_DECISION** |
| `vh_數學B2_CoterminalAngles` | 同界角 | True | 8 | 1 | problem_type_mastery | **PASS** |
| `vh_數學B2_SubSection_1_3_6` | 任意角三角函數求值 | True | 6 | 2 | consecutive_correct_legacy | **NEEDS_DECISION** |
| `vh_數學B2_SubSection_1_3_7` | 化任意角為銳角轉換關係式 | True | 7 | 4 | consecutive_correct_legacy | **NEEDS_DECISION** |

## 特別檢查

### TE 11583 / 11584
```json
{
  "11583": {
    "skill_id": "vh_數學B2_ArcLengthAndAreaOfSector",
    "expect_contains": "ArcLengthAndAreaOfSector",
    "pass": true,
    "has_image": true
  },
  "11584": {
    "skill_id": "vh_數學B2_TrigonometricFunctionsOfAcuteAngles",
    "expect_contains": "TrigonometricFunctionsOfAcuteAngles",
    "pass": true,
    "has_image": true
  }
}
```
### SubSection_1_3_2 labels
```json
{
  "types": [
    "compute_terminal_ray_trig_ratios"
  ],
  "humanize_raw_keys": [
    "$\\sin\\theta$",
    "$\\cos\\theta$",
    "$\\tan\\theta$"
  ],
  "humanize_ok": true,
  "samples": [
    {
      "stem": "設 P(−4,3) 為標準位置角 θ 終邊上的點，求 sinθ、cosθ、tanθ。",
      "parts": [
        {
          "key": "sin",
          "label": "$\\sin\\theta$",
          "display_label": "$\\sin\\theta$"
        },
        {
          "key": "cos",
          "label": "$\\cos\\theta$",
          "display_label": "$\\cos\\theta$"
        },
        {
          "key": "tan",
          "label": "$\\tan\\theta$",
          "display_label": "$\\tan\\theta$"
        }
      ],
      "answer_hash": "91a49dd9f6ca"
    },
    {
      "stem": "設 P(−√3,−1) 為標準位置角 θ 終邊上的點，求 sinθ、cosθ、tanθ。",
      "parts": [
        {
          "key": "sin",
          "label": "$\\sin\\theta$",
          "display_label": "$\\sin\\theta$"
        },
        {
          "key": "cos",
          "label": "$\\cos\\theta$",
          "display_label": "$\\cos\\theta$"
        },
        {
          "key": "tan",
          "label": "$\\tan\\theta$",
          "display_label": "$\\tan\\theta$"
        }
      ],
      "answer_hash": "f81e3e4a2dd1"
    },
    {
      "stem": "設 P(2,−1) 為 θ 終邊上一點，求 sinθ、cosθ、tanθ。",
      "parts": [
        {
          "key": "sin",
          "label": "$\\sin\\theta$",
          "display_label": "$\\sin\\theta$"
        },
        {
          "key": "cos",
          "label": "$\\cos\\theta$",
          "display_label": "$\\cos\\theta$"
        },
        {
          "key": "tan",
          "label": "$\\tan\\theta$",
          "display_label": "$\\tan\\theta$"
        }
      ],
      "answer_hash": "e2e7adaab009"
    },
    {
      "stem": "設 P(−4,3) 為標準位置角 θ 終邊上的點，求 sinθ、cosθ、tanθ。",
      "parts": [
        {
          "key": "sin",
          "label": "$\\sin\\theta$",
          "display_label": "$\\sin\\theta$"
        },
        {
          "key": "cos",
          "label": "$\\cos\\theta$",
          "display_label": "$\\cos\\theta$"
        },
        {
          "key": "tan",
          "label": "$\\tan\\theta$",
          "display_label": "$\\tan\\theta$"
        }
      ],
      "answer_hash": "91a49dd9f6ca"
    },
    {
      "stem": "設 P(−√3,−1) 為標準位置角 θ 終邊上的點，求 sinθ、cosθ、tanθ。",
      "parts": [
        {
          "key": "sin",
          "label": "$\\sin\\theta$",
          "display_label": "$\\sin\\theta$"
        },
        {
          "key": "cos",
          "label": "$\\cos\\theta$",
          "display_label": "$\\cos\\theta$"
        },
        {
          "key": "tan",
          "label": "$\\tan\\theta$",
          "display_label": "$\\tan\\theta$"
        }
      ],
      "answer_hash": "f81e3e4a2dd1"
    }
  ],
  "issues": [],
  "status": "PASS"
}
```

## 各 Skill 抽樣摘要

### `vh_數學B2_DirectedAngle` — INACTIVE_OK

### `vh_數學B2_RatioAndRatioValue` — PASS
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `solve_similar_triangle_proportion` | 30 | 2 | None | 2 | LIMITED_VARIATION |

### `vh_數學B2_SubSection_1_3_1` — NEEDS_DECISION
- NEEDS_DECISION: A類 SubSection：是否納入 B2 題型掌握制 allowlist（目前仍顯示舊連對／暫無門檻語意）
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `classify_standard_position_angle` | 30 | 3 | None | 3 | HAS_VARIATION |

### `vh_數學B2_SubSection_1_4_1` — INACTIVE_OK

### `vh_數學B2_SubSection_1_3_2` — NEEDS_DECISION
- NEEDS_DECISION: A類 SubSection：是否納入 B2 題型掌握制 allowlist（目前仍顯示舊連對／暫無門檻語意）
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `compute_terminal_ray_trig_ratios` | 30 | 3 | None | 3 | HAS_VARIATION |

### `vh_數學B2_SubSection_1_4_2` — INACTIVE_OK

### `vh_數學B2_TrigonometricFunctionsOfAcuteAngles` — PASS
- bugs: `[{"severity": "P2", "code": "LOW_PARAM_VARIATION", "detail": ["simplify_fundamental_trig_expression", "solve_right_triangle_projection"]}]`
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `compute_right_triangle_trig_ratios` | 30 | 3 | None | 3 | HAS_VARIATION |
| `simplify_fundamental_trig_expression` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |
| `solve_acute_trig_constraints` | 30 | 5 | None | 5 | HAS_VARIATION |
| `solve_right_triangle_projection` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |

### `vh_數學B2_AngleMeasurementAndConversion` — PASS
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `convert_angle_measure` | 30 | 25 | None | 25 | HAS_VARIATION |

### `vh_數學B2_SubSection_1_4_3` — NEEDS_DECISION
- NEEDS_DECISION: A類 SubSection：是否納入 B2 題型掌握制 allowlist（目前仍顯示舊連對／暫無門檻語意）
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `analyze_affine_transformed_trig_graph` | 30 | 4 | None | 4 | HAS_VARIATION |
| `compare_trig_values_by_monotonicity` | 30 | 2 | None | 2 | LIMITED_VARIATION |
| `solve_trig_value_quadratic_constraint` | 30 | 2 | None | 2 | LIMITED_VARIATION |

### `vh_數學B2_TrigonometricValuesOfSpecialAngles` — PASS
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `evaluate_exact_special_angle_expression` | 30 | 3 | None | 3 | HAS_VARIATION |
| `solve_right_triangle_projection` | 30 | 2 | None | 2 | LIMITED_VARIATION |

### `vh_數學B2_ArcLengthAndAreaOfSector` — PASS
- bugs: `[{"severity": "P2", "code": "LOW_PARAM_VARIATION", "detail": ["compute_chord_and_arc_length"]}]`
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `compute_chord_and_arc_length` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |
| `sector_arc_and_area` | 30 | 29 | None | 29 | HAS_VARIATION |

### `vh_數學B2_CalculatingFunctionValuesUsingCalculator` — PASS
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `evaluate_trig_decimal` | 30 | 2 | None | 2 | LIMITED_VARIATION |

### `vh_數學B2_SubSection_1_3_4` — NEEDS_DECISION
- NEEDS_DECISION: A類 SubSection：是否納入 B2 題型掌握制 allowlist（目前仍顯示舊連對／暫無門檻語意）
- bugs: `[{"severity": "P2", "code": "LOW_PARAM_VARIATION", "detail": ["classify_trig_derived_point_quadrant"]}]`
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `classify_trig_derived_point_quadrant` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |
| `solve_signed_trig_constraints` | 30 | 6 | None | 6 | HAS_VARIATION |

### `vh_數學B2_SubSection_1_4_4` — NEEDS_DECISION
- NEEDS_DECISION: A類 SubSection：是否納入 B2 題型掌握制 allowlist（目前仍顯示舊連對／暫無門檻語意）
- bugs: `[{"severity": "P2", "code": "LOW_PARAM_VARIATION", "detail": ["analyze_tangent_absolute_graph_period", "classify_trig_equation_feasibility", "classify_trig_expression_sign_change", "compare_trig_values_by_monotonicity", "count_sine_cosine_intersections", "evaluate_trig_decimal", "solve_trig_value_quadratic_constraint"]}]`
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `analyze_affine_transformed_trig_graph` | 30 | 3 | None | 2 | HAS_VARIATION |
| `analyze_tangent_absolute_graph_period` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |
| `calculate_trig_period_from_argument_scale` | 30 | 3 | None | 2 | HAS_VARIATION |
| `classify_trig_equation_feasibility` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |
| `classify_trig_expression_sign_change` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |
| `compare_trig_values_by_monotonicity` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |
| `count_sine_cosine_intersections` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |
| `evaluate_trig_decimal` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |
| `solve_trig_value_quadratic_constraint` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |

### `vh_數學B2_FundamentalTrigonometricIdentities` — PASS
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `complete_cofunction_identity` | 30 | 2 | None | 2 | LIMITED_VARIATION |
| `simplify_fundamental_trig_expression` | 30 | 5 | None | 4 | HAS_VARIATION |
| `solve_acute_trig_constraints` | 30 | 3 | None | 3 | HAS_VARIATION |

### `vh_數學B2_SubSection_1_3_5` — NEEDS_DECISION
- NEEDS_DECISION: A類 SubSection：是否納入 B2 題型掌握制 allowlist（目前仍顯示舊連對／暫無門檻語意）
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `evaluate_exact_arbitrary_angle_trig_expression` | 30 | 3 | None | 3 | HAS_VARIATION |

### `vh_數學B2_CoterminalAngles` — PASS
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `coterminal_angles` | 30 | 29 | None | 18 | HAS_VARIATION |

### `vh_數學B2_SubSection_1_3_6` — NEEDS_DECISION
- NEEDS_DECISION: A類 SubSection：是否納入 B2 題型掌握制 allowlist（目前仍顯示舊連對／暫無門檻語意）
- bugs: `[{"severity": "P2", "code": "LOW_PARAM_VARIATION", "detail": ["solve_arbitrary_angle_vertical_projection"]}]`
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `evaluate_exact_arbitrary_angle_trig_expression` | 30 | 5 | None | 5 | HAS_VARIATION |
| `solve_arbitrary_angle_vertical_projection` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |

### `vh_數學B2_SubSection_1_3_7` — NEEDS_DECISION
- NEEDS_DECISION: A類 SubSection：是否納入 B2 題型掌握制 allowlist（目前仍顯示舊連對／暫無門檻語意）
- bugs: `[{"severity": "P2", "code": "LOW_PARAM_VARIATION", "detail": ["classify_trig_derived_point_quadrant", "complete_reference_angle_conversion"]}]`
| problem_type | ok | unique_stems | unique_params | unique_answers | note |
|---|---:|---:|---:|---:|---|
| `classify_trig_derived_point_quadrant` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |
| `complete_reference_angle_conversion` | 30 | 1 | None | 1 | LOW_VARIATION_SUSPECT |
| `evaluate_exact_arbitrary_angle_trig_expression` | 30 | 3 | None | 3 | HAS_VARIATION |
| `simplify_fundamental_trig_expression` | 30 | 2 | None | 2 | LIMITED_VARIATION |

