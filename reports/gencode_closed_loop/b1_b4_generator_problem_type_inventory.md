# 技高數學 B1～B4 Generator 題型靜態盤點

- 產生時間：`2026-11-21T23:31:24`
- 性質：**靜態分析**（不可視為動態出題或數學正確性已通過）
- 題型身分：`problem_type_id`（僅去除尾隨 `_數字` 變體；跨教材來源／隨機 seed 不去重膨脹）
- 可用題型：facade∩package `GENERATOR_KEYS` + 雙邊 `GENERATOR_SPECS` + `generate.py` 存在 + readiness 未封鎖
- 冊別「可用題型數」彙總＝**各 Skill 可用題型數加總**（非跨 Skill 去重）；跨 Skill 去重唯一可用題型數＝`376`

## 各冊彙總

| 冊別 | Skill 總數 | 可執行 Skill | Outline | Generator 實作數加總 | 可用題型數加總（逐 Skill） |
|---|---:|---:|---:|---:|---:|
| B1 | 45 | 35 | 10 | 314 | 95 |
| B2 | 59 | 48 | 11 | 316 | 152 |
| B3 | 50 | 38 | 12 | 373 | 131 |
| B4 | 40 | 40 | 0 | 56 | 26 |
| 合計 | 194 | 161 | 33 | 1059 | 404 |

## 異常清單摘要

- 沒有 Generator 的可執行 Skill：`41`
- 題型／Registry 異常（WARN/FAIL/UNKNOWN）：`23`
- 有 Generator 但未完全接入 Runtime：`8`
- 健康狀態分布：`{'PASS': 138, 'WARN': 23}`

### src_4584 / SlopeOfALine 靜態回歸

- src_4584 ∈ PointAndLine：`True`；∈ ParallelLines：`False`
- SlopeOfALine 可用題型數：`9` 實作數：`12` 健康：`PASS`

## Skill 明細

| 冊別 | Skill ID | 中文名稱 | 實作數 | 可用題型數 | Family 數 | 教材題數 | Eligible | V3 | Runtime published | 健康 | 異常 |
|---|---|---|---:|---:|---:|---:|---:|---|---:|---|---|
| B2 | `outline_vocational_數學B2_13` | 1-3 任意角的三角函數 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B2 | `vh_數學B2_SubSection_1_3_3` | 同界角的三角函數 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B1 | `vh_數學B1_AbsoluteValue` | 絕對值 | 4 | 2 | 2 | 4 | 4 | 已上線 | 4 | PASS |  |
| B1 | `vh_數學B1_CartesianCoordinateSystemEstablishment` | 直角坐標系的建立 | 4 | 3 | 3 | 4 | 4 | 已上線 | 4 | WARN | facade_generator_specs_not_literal_using_package |
| B1 | `vh_數學B1_GeneralFormOfLinearEquation` | 直線的一般式 | 17 | 11 | 11 | 17 | 17 | 已上線 | 17 | PASS |  |
| B1 | `vh_數學B1_PointSlopeForm` | 點斜式 | 14 | 1 | 1 | 14 | 14 | 全部上線 | 14 | PASS |  |
| B1 | `vh_數學B1_PolynomialBasicConcepts` | 多項式的基本概念 | 7 | 4 | 4 | 9 | 9 | 驗證失敗 | 7 | PASS |  |
| B1 | `vh_數學B1_PolynomialFactoring` | 因式分解 | 18 | 1 | 1 | 18 | 18 | 已上線 | 18 | PASS |  |
| B1 | `vh_數學B1_QuadraticFunctionGraph` | 二次函數的圖形 | 4 | 0 | 0 | 4 | 4 | 全部上線 | 4 | WARN | generators_exist_but_not_runtime_selectable; unregistered_generate_py:src_4450,src_4460,src_4466,src_4503; registered_without_generate_py:vh_數學B1_QuadraticFunctionGraph:integer_quadratic_graph_properties_choice:draft_v1,vh_數學B1_QuadraticFunctionGraph:integer_quadratic_graph_translation_fill_blank:draft_v1,vh_數學B1_QuadraticFunctionGraph:rational_quadratic_graph_translation_fill_blank:draft_v1 |
| B1 | `vh_數學B1_QuadraticInequalityAndFactoring` | 一元二次不等式的基本概念與十字交乘法 | 3 | 0 | 0 | 3 | 3 | 全部上線 | 3 | WARN | generators_exist_but_not_runtime_selectable; unregistered_generate_py:src_4473,src_4480,src_4490; registered_without_generate_py:vh_數學B1_QuadraticInequalityAndFactoring:integer_factor_quadratic_by_cross_multiplication:draft_v1 |
| B1 | `vh_數學B1_RemainderTheorem` | 餘式定理 | 20 | 1 | 1 | 24 | 24 | 驗證失敗 | 20 | PASS |  |
| B1 | `vh_數學B1_SlopeOfALine` | 直線的斜率 | 12 | 9 | 9 | 12 | 12 | 已上線 | 12 | PASS |  |
| B1 | `vh_數學B1_AbsoluteValueInequality` | 絕對值不等式 | 10 | 4 | 4 | 10 | 10 | 已上線 | 10 | PASS |  |
| B1 | `vh_數學B1_DistanceBetweenPointAndLine` | 點到直線的距離 | 8 | 5 | 5 | 8 | 8 | 已上線 | 7 | PASS |  |
| B1 | `vh_數學B1_FactorTheorem` | 因式定理 | 17 | 1 | 1 | 17 | 17 | 已上線 | 17 | PASS |  |
| B1 | `vh_數學B1_FunctionConcept` | 函數的概念 | 2 | 0 | 0 | 2 | 2 | 全部上線 | 2 | WARN | facade_missing_package_only_not_runtime; generators_exist_but_not_runtime_selectable; unregistered_generate_py:src_4430,src_4431 |
| B1 | `vh_數學B1_HorizontalAndVerticalLineEquations` | 水平線與鉛直線的直線方程式 | 4 | 1 | 2 | 4 | 4 | 全部上線 | 4 | PASS |  |
| B1 | `vh_數學B1_PolynomialArithmeticOperations` | 多項式的四則運算 | 22 | 7 | 7 | 22 | 22 | 已上線 | 22 | PASS |  |
| B1 | `vh_數學B1_PropertiesOfParallelLines` | 兩平行線的性質 | 4 | 3 | 3 | 4 | 4 | 已上線 | 4 | PASS |  |
| B1 | `vh_數學B1_QuadraticInequalitySolution` | 一元二次不等式的解 | 29 | 0 | 0 | 29 | 29 | 全部上線 | 29 | WARN | generators_exist_but_not_runtime_selectable; unregistered_generate_py:src_4474,src_4475,src_4476,src_4477,src_4478,src_4479,src_4481,src_4482; registered_without_generate_py:vh_數學B1_QuadraticInequalitySolution:integer_applied_quadratic_inequality_problem:draft_v1,vh_數學B1_QuadraticInequalitySolution:integer_reverse_quadratic_inequality_coefficients:draft_v1,vh_數學B1_QuadraticInequalitySolution:integer_solve_quadratic_inequality:draft_v1,vh_數學B1_QuadraticInequalitySolution:integer_solve_quadratic_inequality_parameter_range:draft_v1,vh_數學B1_QuadraticInequalitySolution:rational_solve_quadratic_inequality:draft_v1,vh_數學B1_QuadraticInequalitySolution:rational_solve_quadratic_inequality_special_cases:draft_v1,vh_數學B1_QuadraticInequalitySolution:text_short_factor_quadratic_by_cross_multiplication:draft_v1 |
| B1 | `vh_數學B1_RationalExpressionArithmeticOperations` | 分式的四則運算 | 8 | 1 | 1 | 8 | 8 | 已上線 | 8 | PASS |  |
| B1 | `vh_數學B1_VertexFormOfQuadraticFunction` | 頂點式 | 5 | 0 | 0 | 5 | 5 | 全部上線 | 5 | WARN | generators_exist_but_not_runtime_selectable; unregistered_generate_py:src_4451,src_4452,src_4453,src_4456,src_4504; registered_without_generate_py:vh_數學B1_VertexFormOfQuadraticFunction:numeric_quadratic_vertex_or_parameter_computation_short_answer:spec_v1,vh_數學B1_VertexFormOfQuadraticFunction:numeric_quadratic_vertex_or_parameter_computation_single_choice:spec_v1,vh_數學B1_VertexFormOfQuadraticFunction:quadratic_standard_to_vertex_properties:spec_v1,vh_數學B1_VertexFormOfQuadraticFunction:single_choice_quadratic_vertex_form_properties_single_choice:spec_v1,vh_數學B1_VertexFormOfQuadraticFunction:text_quadratic_graph_translation_fill_blank_short_answer:spec_v1,vh_數學B1_VertexFormOfQuadraticFunction:text_quadratic_vertex_form_translation_to_new_function_short_answer:spec_v1 |
| B1 | `outline_vocational_數學B1_14` | 1-4 一元二次不等式 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B1 | `outline_vocational_數學B1_32` | 3-2 除法原理與餘式定理 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B1 | `vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning` | 絕對值不等式的展開與幾何意義 | 3 | 2 | 2 | 3 | 3 | 已上線 | 3 | PASS |  |
| B1 | `vh_數學B1_CompletingTheSquare` | 配方法 | 2 | 0 | 0 | 2 | 2 | 全部上線 | 2 | WARN | generators_exist_but_not_runtime_selectable; unregistered_generate_py:src_4468,src_4501; registered_without_generate_py:vh_數學B1_CompletingTheSquare:integer_quadratic_graph_vertex_axis_choice:draft_v1,vh_數學B1_CompletingTheSquare:integer_quadratic_vertex_or_parameter_computation:draft_v1 |
| B1 | `vh_數學B1_DistanceBetweenTwoParallelLines` | 兩條平行線間的距離 | 10 | 3 | 3 | 10 | 10 | 已上線 | 10 | PASS |  |
| B1 | `vh_數學B1_DistanceBetweenTwoPointsInPlane` | 平面上兩點間的距離 | 4 | 2 | 2 | 4 | 4 | 已上線 | 4 | PASS |  |
| B1 | `vh_數學B1_PolynomialEquality` | 多項式的相等 | 4 | 1 | 1 | 4 | 4 | 已上線 | 4 | PASS |  |
| B1 | `vh_數學B1_PropertiesOfPerpendicularLines` | 兩垂直線的性質 | 8 | 5 | 5 | 8 | 8 | 已上線 | 8 | PASS |  |
| B1 | `vh_數學B1_RationalEquation` | 分式方程式 | 14 | 1 | 1 | 14 | 14 | 已上線 | 14 | PASS |  |
| B1 | `vh_數學B1_SlopeInterceptForm` | 斜截式 | 5 | 3 | 3 | 5 | 5 | 全部上線 | 5 | PASS |  |
| B1 | `outline_vocational_數學B1_21` | 2-1 斜率 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B1 | `outline_vocational_數學B1_23` | 2-3 直線的一般式與點到直線的距離 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B1 | `outline_vocational_數學B1_31` | 3-1 多項式的基本概念與四則運算 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B1 | `outline_vocational_數學B1_33` | 3-3 因式分解與分式 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B1 | `vh_數學B1_InterceptForm` | 截距式 | 7 | 5 | 5 | 7 | 7 | 已上線 | 7 | PASS |  |
| B1 | `vh_數學B1_MidpointCoordinates` | 中點坐標 | 10 | 6 | 6 | 10 | 10 | 已上線 | 10 | PASS |  |
| B1 | `vh_數學B1_NumberLine` | 數線 | 0 | 0 | 0 | 1 | 1 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B1 | `vh_數學B1_QuadraticFunctionExtremum` | 二次函數 $y = ax^{2} + bx + c$ 的最大（小）值 | 13 | 0 | 0 | 13 | 13 | 全部上線 | 13 | WARN | generators_exist_but_not_runtime_selectable; unregistered_generate_py:src_4454,src_4455,src_4457,src_4458,src_4459,src_4463,src_4464,src_4465; registered_without_generate_py:vh_數學B1_QuadraticFunctionExtremum:integer_compute_quadratic_vertex:draft_v1,vh_數學B1_QuadraticFunctionExtremum:integer_quadratic_vertex_or_parameter_computation:draft_v1,vh_數學B1_QuadraticFunctionExtremum:text_short_quadratic_vertex_or_parameter_computation:draft_v1 |
| B1 | `outline_vocational_數學B1_11` | 1-1 數線與絕對值 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B1 | `outline_vocational_數學B1_13` | 1-3 二次函數 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B1 | `outline_vocational_數學B1_22` | 2-2 直線方程式 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B1 | `vh_數學B1_DivisionPointCoordinates` | 分點坐標 | 7 | 3 | 0 | 7 | 7 | 已上線 | 7 | PASS |  |
| B1 | `vh_數學B1_SubSection332` | 分式 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B1 | `vh_數學B1_LinearFunction` | 線型函數 | 15 | 10 | 10 | 15 | 15 | 已上線 | 15 | PASS |  |
| B1 | `outline_vocational_數學B1_12` | 1-2 平面坐標系與線型函數 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B2 | `vh_數學B2_DirectedAngle` | 有向角 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B2 | `vh_數學B2_RatioAndRatioValue` | 比與比值 | 2 | 1 | 1 | 2 | 2 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_1_3_1` | 標準位置角 | 3 | 1 | 1 | 3 | 3 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_1_4_1` | 正弦函數的圖形與其週期現象的表徵 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B2 | `vh_數學B2_SubSection_2_2_1` | 測量的名詞與術語 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B2 | `vh_數學B2_SubSection_3_1_1` | 向量定義 | 3 | 2 | 2 | 3 | 3 | 驗證失敗 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_3_2_1` | 向量的坐標表示法 | 11 | 6 | 6 | 11 | 11 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_3_3_1` | 向量的夾角 | 4 | 3 | 3 | 4 | 4 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_4_2_1` | 點與圓的關係 | 5 | 3 | 3 | 5 | 5 | 已上線 | 5 | PASS |  |
| B2 | `vh_數學B2_SubSection_1_3_2` | 任意角的三角函數 | 3 | 1 | 1 | 3 | 3 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_1_4_2` | 餘弦函數的圖形與其週期現象的表徵 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B2 | `vh_數學B2_SubSection_2_1_1` | 正弦定理 | 13 | 6 | 6 | 13 | 13 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_2_2_2` | 求解平面三角測量問題的原則 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B2 | `vh_數學B2_SubSection_3_1_2` | 向量的加法作圖 | 3 | 1 | 1 | 3 | 3 | 驗證失敗 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_3_3_2` | 向量內積的定義 | 5 | 3 | 3 | 5 | 5 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_4_1_1` | 圓的標準式 | 16 | 9 | 9 | 16 | 16 | 已上線 | 16 | PASS |  |
| B2 | `vh_數學B2_SubSection_4_2_2` | 圓與直線的關係 | 17 | 12 | 12 | 17 | 17 | 已上線 | 17 | PASS |  |
| B2 | `vh_數學B2_TrigonometricFunctionsOfAcuteAngles` | 銳角三角函數 | 11 | 4 | 4 | 11 | 11 | 已部署，待重新驗證 (11/11) | 0 | WARN | unregistered_generate_py:src_11575 |
| B2 | `vh_數學B2_AngleMeasurementAndConversion` | 角的度量與換算 | 5 | 1 | 1 | 5 | 5 | 已上線 | 5 | PASS |  |
| B2 | `vh_數學B2_SubSection_1_4_3` | 正切函數的圖形與其週期現象的表徵 | 8 | 3 | 3 | 8 | 8 | 已上線 | 8 | PASS |  |
| B2 | `vh_數學B2_SubSection_2_2_3` | 直角三角形的測量 | 14 | 10 | 10 | 15 | 15 | 已部署，待重新驗證 (15/15) | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_3_1_3` | 向量的減法作圖 | 7 | 1 | 1 | 7 | 7 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_3_2_2` | 向量加減的坐標表示法 | 15 | 6 | 6 | 15 | 15 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_3_3_3` | 向量內積的坐標表示法 | 9 | 5 | 5 | 9 | 9 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_4_1_2` | 圓的一般式 | 19 | 10 | 10 | 19 | 19 | 已上線 | 19 | PASS |  |
| B2 | `vh_數學B2_SubSection_4_2_3` | 圓的切線方程式 | 8 | 5 | 5 | 8 | 8 | 已上線 | 8 | PASS |  |
| B2 | `vh_數學B2_TrigonometricValuesOfSpecialAngles` | 30°、45°、60° 特別角的三角函數值 | 6 | 2 | 2 | 6 | 6 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_ArcLengthAndAreaOfSector` | 扇形的弧長與面積 | 7 | 1 | 1 | 7 | 7 | 已上線 | 7 | PASS |  |
| B2 | `vh_數學B2_CalculatingFunctionValuesUsingCalculator` | 使用計算機計算函數值 | 2 | 1 | 1 | 2 | 2 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_1_3_4` | 三角函數值在四個象限的正負情形 | 7 | 2 | 2 | 7 | 7 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_1_4_4` | 三角函數圖形的變化與週期 | 13 | 9 | 9 | 13 | 13 | 已上線 | 13 | PASS |  |
| B2 | `vh_數學B2_SubSection_2_1_2` | 餘弦定理 | 12 | 5 | 5 | 14 | 14 | 已部署，待重新驗證 (14/14) | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_2_2_4` | 非直角三角形測量 | 8 | 2 | 2 | 9 | 9 | 已部署，待重新驗證 (9/9) | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_3_1_4` | 向量的實數積作圖 | 14 | 6 | 6 | 14 | 14 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_3_2_3` | 向量實數積的坐標表示法 | 2 | 2 | 2 | 2 | 2 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_3_3_4` | 兩向量的垂直 | 4 | 2 | 2 | 4 | 4 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_FundamentalTrigonometricIdentities` | 三角函數的基本關係式 | 10 | 3 | 3 | 10 | 10 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_1_3_5` | 象限角的三角函數值 | 3 | 1 | 1 | 3 | 3 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_2_2_5` | 簡單的立體測量 | 3 | 3 | 3 | 4 | 4 | 已部署，待重新驗證 (4/4) | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_3_3_5` | 向量內積的性質 | 6 | 4 | 4 | 6 | 6 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_4_2_4` | 切線段長 | 5 | 3 | 3 | 5 | 5 | 已上線 | 5 | PASS |  |
| B2 | `vh_數學B2_CoterminalAngles` | 同界角 | 8 | 1 | 1 | 8 | 8 | 已上線 | 8 | PASS |  |
| B2 | `vh_數學B2_SubSection_1_3_6` | 任意角三角函數求值 | 6 | 2 | 2 | 6 | 6 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_3_2_4` | 向量實數積的基本性質 | 3 | 2 | 2 | 3 | 3 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_1_3_7` | 化任意角為銳角轉換關係式 | 7 | 4 | 4 | 7 | 7 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_3_2_5` | 向量的平行 | 4 | 2 | 2 | 4 | 4 | 已上線 | 0 | PASS |  |
| B2 | `vh_數學B2_SubSection_3_2_6` | 單位向量 | 5 | 2 | 2 | 5 | 5 | 已上線 | 0 | PASS |  |
| B2 | `outline_vocational_數學B2_11` | 1-1 角度的基本性質 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B2 | `outline_vocational_數學B2_12` | 1-2 銳角三角函數 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B2 | `outline_vocational_數學B2_14` | 1-4 正弦、餘弦函數的圖形 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B2 | `outline_vocational_數學B2_21` | 2-1 正弦定理與餘弦定理 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B2 | `outline_vocational_數學B2_22` | 2-2 三角測量 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B2 | `outline_vocational_數學B2_31` | 3-1 向量的作圖 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B2 | `outline_vocational_數學B2_32` | 3-2 向量的坐標表示法 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B2 | `outline_vocational_數學B2_33` | 3-3 向量的內積 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B2 | `outline_vocational_數學B2_41` | 4-1 圓方程式 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B2 | `outline_vocational_數學B2_42` | 4-2 圓與直線的關係 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B3 | `vh_數學B3_PlainHeading_3_2_1` | 二元一次不等式的定義 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B3 | `vh_數學B3_SubSection_1_1_1` | 數列與級數 | 3 | 1 | 1 | 3 | 3 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_1_2_1` | 等比數列 | 19 | 7 | 7 | 19 | 19 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_2_1_1` | 一元一次方程式 | 20 | 9 | 9 | 20 | 20 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_2_2_1` | 一元二次方程式的基礎概念 | 1 | 1 | 1 | 1 | 1 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_3_1_1` | 二元一次方程組的基本概念 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B3 | `vh_數學B3_SubSection_3_3_1` | 二元一次聯立不等式 | 15 | 5 | 5 | 15 | 15 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_4_1_1` | 正整數指數與指數律 | 5 | 3 | 3 | 5 | 5 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_4_2_1` | 指數函數的圖形 | 14 | 4 | 4 | 14 | 14 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_4_3_1` | 對數的意義 | 4 | 2 | 2 | 4 | 4 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_4_4_1` | 對數函數的圖形 | 14 | 4 | 4 | 14 | 14 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_4_5_1` | 常用對數表的使用 | 6 | 2 | 2 | 6 | 6 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_PlainHeading_3_2_2` | 二元一次不等式的解 | 2 | 2 | 2 | 2 | 2 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_2_1_2` | 一元一次不等式 | 11 | 3 | 3 | 11 | 11 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_2_2_2` | 一元二次方程式的解法 | 13 | 6 | 6 | 13 | 13 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_3_1_2` | 二元一次聯立方程組的解法 | 18 | 7 | 7 | 18 | 18 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_3_3_2` | 線性規劃 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B3 | `vh_數學B3_SubSection_4_1_2` | 零指數與負整數指數 | 5 | 3 | 3 | 5 | 5 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_4_2_2` | 指數方程式 | 16 | 6 | 6 | 16 | 16 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_4_3_2` | 對數的性質 | 30 | 10 | 10 | 30 | 30 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_4_4_2` | 對數方程式 | 13 | 6 | 6 | 13 | 13 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_4_5_2` | 使用計算機鍵 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B3 | `vh_數學B3_PlainHeading_3_2_3` | 邊界、半平面 | 14 | 2 | 2 | 14 | 14 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_1_1_2` | 等差數列 | 13 | 5 | 5 | 13 | 13 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_1_2_2` | 等比中項 | 4 | 3 | 3 | 4 | 4 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_2_2_3` | 根的性質與判別式 | 9 | 4 | 4 | 9 | 9 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_3_1_3` | 二元一次方程組的幾何圖形 | 13 | 5 | 5 | 13 | 13 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_3_3_3` | 求目標函數的最佳值 | 6 | 1 | 1 | 6 | 6 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_4_1_3` | 有理數指數 | 14 | 5 | 5 | 14 | 14 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_4_5_3` | 首數、尾數及其應用 | 25 | 6 | 6 | 25 | 25 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_PlainHeading_3_2_4` | 相異兩點在直線的同側、異側 | 8 | 2 | 2 | 8 | 8 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_1_2_3` | 等比數列的遞迴關係式 | 3 | 1 | 1 | 3 | 3 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_2_2_4` | 根與係數的關係 | 14 | 3 | 3 | 14 | 14 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_3_3_4` | 線性規劃的應用 | 9 | 2 | 2 | 9 | 9 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_1_1_3` | 等差中項 | 2 | 1 | 1 | 2 | 2 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_1_2_4` | 等比級數 | 11 | 3 | 3 | 11 | 11 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_1_1_4` | 等差數列的遞迴關係式 | 5 | 1 | 1 | 5 | 5 | 已上線 | 0 | PASS |  |
| B3 | `vh_數學B3_SubSection_1_1_5` | 等差級數 | 14 | 6 | 6 | 14 | 14 | 已上線 | 0 | PASS |  |
| B3 | `outline_vocational_數學B3_11` | 1-1 等差數列與等差級數 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B3 | `outline_vocational_數學B3_12` | 1-2 等比數列與等比級數 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B3 | `outline_vocational_數學B3_21` | 2-1 一元一次方程式與一元一次不等式 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B3 | `outline_vocational_數學B3_22` | 2-2 一元二次方程式 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B3 | `outline_vocational_數學B3_31` | 3-1 二元一次聯立方程組 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B3 | `outline_vocational_數學B3_32` | 3-2 二元一次不等式 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B3 | `outline_vocational_數學B3_33` | 3-3 線性規劃 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B3 | `outline_vocational_數學B3_41` | 4-1 指數 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B3 | `outline_vocational_數學B3_42` | 4-2 指數函數及其圖形 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B3 | `outline_vocational_數學B3_43` | 4-3 對數 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B3 | `outline_vocational_數學B3_44` | 4-4 對數函數及其圖形 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B3 | `outline_vocational_數學B3_45` | 4-5 常用對數及其應用 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | outline_skill_excluded_from_executable_types |
| B4 | `vh_數學B4_AdditionPrinciple` | 加法原理 | 0 | 0 | 0 | 4 | 4 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B4 | `vh_數學B4_BinomialTheorem` | 二項式定理 | 0 | 0 | 0 | 12 | 12 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B4 | `vh_數學B4_CentralTendencyMeasures` | 集中趨勢量數 | 11 | 4 | 4 | 11 | 11 | 已上線 | 7 | PASS |  |
| B4 | `vh_數學B4_CombinationDefinition` | 組合的定義與計算 | 0 | 0 | 0 | 2 | 2 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B4 | `vh_數學B4_FrequencyDistributionTableConstruction` | 統計資料的次數分配表編製步驟 | 4 | 1 | 1 | 4 | 4 | 已上線 | 0 | PASS |  |
| B4 | `vh_數學B4_MathematicalExpectation` | 數學期望值 | 0 | 0 | 0 | 5 | 5 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_PermutationOfNonDistinctObjects` | 不盡相異物的排列 | 0 | 0 | 0 | 6 | 6 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B4 | `vh_數學B4_ProbabilityDefinition` | 機率的定義 | 0 | 0 | 0 | 15 | 15 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_RepeatedPermutation` | 重複排列 | 0 | 0 | 0 | 10 | 10 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B4 | `vh_數學B4_SampleSpaceAndEvents` | 樣本空間與事件 | 0 | 0 | 0 | 13 | 13 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_SamplingSurvey` | 抽樣調查 | 0 | 0 | 0 | 2 | 2 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_BasicConceptsOfSets` | 集合的基本概念 | 0 | 0 | 0 | 10 | 10 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_CombinationApplications` | 組合的應用 | 0 | 0 | 0 | 7 | 7 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B4 | `vh_數學B4_HistogramsAndFrequencyPolygons` | 次數分配直方圖與次數分配折線圖的繪製 | 4 | 2 | 2 | 4 | 4 | 已上線 | 4 | PASS |  |
| B4 | `vh_數學B4_MathematicalExpectationDefinition` | 數學期望值的定義與計算 | 0 | 0 | 0 | 9 | 9 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_MultiplicationPrinciple` | 乘法原理 | 0 | 0 | 0 | 10 | 10 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B4 | `vh_數學B4_PascalTriangle` | 巴斯卡三角形 | 0 | 0 | 0 | 1 | 1 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_PermutationOfDistinctObjects` | 相異物的排列 | 0 | 0 | 0 | 18 | 18 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B4 | `vh_數學B4_PermutationWithRepetition` | 重複排列 | 0 | 0 | 0 | 2 | 2 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B4 | `vh_數學B4_ProbabilityOperations` | 機率的運算 | 0 | 0 | 0 | 9 | 9 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_SamplingMethods` | 抽樣方法 | 0 | 0 | 0 | 15 | 15 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_WeightedMean` | 加權平均數 | 3 | 1 | 1 | 3 | 3 | 已上線 | 3 | PASS |  |
| B4 | `vh_數學B4_ApplicationsOfExpectation` | 數學期望值的應用 | 0 | 0 | 0 | 10 | 10 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_BinomialCoefficientIdentities` | 二項式係數性質 | 0 | 0 | 0 | 3 | 3 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B4 | `vh_數學B4_Combination` | 組合 | 0 | 0 | 0 | 7 | 7 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B4 | `vh_數學B4_ConditionalProbability` | 條件機率 | 0 | 0 | 0 | 5 | 5 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_DispersionMeasures` | 離散趨勢量數 | 5 | 4 | 4 | 5 | 5 | 已上線 | 5 | PASS |  |
| B4 | `vh_數學B4_StatisticalBasicConcepts` | 統計的基本概念 | 0 | 0 | 0 | 0 | 0 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_StatisticalChartReading` | 統計圖表判讀 | 3 | 3 | 3 | 3 | 3 | 已上線 | 3 | PASS |  |
| B4 | `vh_數學B4_TreeDiagramCounting` | 樹狀圖 | 0 | 0 | 0 | 4 | 4 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_CombinationProperties` | 組合的性質 | 0 | 0 | 0 | 2 | 2 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B4 | `vh_數學B4_CumulativeFrequencyTablesAndGraphs` | 累積次數分配表與累積次數分配折線圖 | 5 | 3 | 3 | 5 | 5 | 已上線 | 4 | PASS |  |
| B4 | `vh_數學B4_FactorialNotation` | 階乘記法 | 0 | 0 | 0 | 4 | 4 | 尚待驗證或尚未生成 | 0 | WARN | package_missing_facade_only |
| B4 | `vh_數學B4_IndependentEvents` | 獨立事件 | 0 | 0 | 0 | 4 | 4 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_VarianceAndStandardDeviation` | 變異數與標準差 | 5 | 2 | 2 | 5 | 5 | 已上線 | 4 | PASS |  |
| B4 | `vh_數學B4_DataOrganizationAndCharts` | 資料整理與圖表編製 | 0 | 0 | 0 | 1 | 1 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_LinearTransformationOfData` | 資料的線性變換 | 8 | 2 | 3 | 8 | 8 | 已上線 | 4 | PASS |  |
| B4 | `vh_數學B4_ProbabilityProperties` | 機率的性質 | 0 | 0 | 0 | 7 | 7 | 尚待驗證或尚未生成 | 0 | PASS | no_generator_artifacts |
| B4 | `vh_數學B4_NormalDistributionAndEmpiricalRule` | 常態分配與經驗法則 | 6 | 2 | 2 | 6 | 6 | 已上線 | 6 | PASS |  |
| B4 | `vh_數學B4_OpinionPollInterpretation` | 民意調查的解讀 | 2 | 2 | 2 | 2 | 2 | 驗證失敗 | 0 | PASS |  |

## 題型識別清單（逐 Skill）

### `vh_數學B2_SubSection_1_3_3` — 同界角的三角函數
- 可用：（無）

### `vh_數學B1_AbsoluteValue` — 絕對值
- 可用：number_line_distance_between_two_points, solve_basic_absolute_value_equation
- Family/line_type：number_line_distance_between_two_points, solve_basic_absolute_value_equation

### `vh_數學B1_CartesianCoordinateSystemEstablishment` — 直角坐標系的建立
- 可用：axis_distance_coordinate_point_numerical_choice, cartesian_coordinate_quadrant_symbol_reasoning, quadrant_statement_reasoning_choice
- Family/line_type：axis_distance_coordinate_point_numerical_choice, cartesian_coordinate_quadrant_symbol_reasoning, quadrant_statement_reasoning_choice

### `vh_數學B1_GeneralFormOfLinearEquation` — 直線的一般式
- 可用：compare_line_slopes, line_through_intersection_parallel_to_line, line_through_point_parallel_to_line, line_through_point_perpendicular_to_line, parallel_line_slope, perpendicular_bisector_application, perpendicular_condition_parameter, perpendicular_line_slope, slope_from_general_form, slope_from_general_or_intercept_form, slope_of_horizontal_or_vertical_line
- Family/line_type：compare_line_slopes, line_through_intersection_parallel_to_line, line_through_point_parallel_to_line, line_through_point_perpendicular_to_line, parallel_line_slope, perpendicular_bisector_application, perpendicular_condition_parameter, perpendicular_line_slope, slope_from_general_form, slope_from_general_or_intercept_form, slope_of_horizontal_or_vertical_line

### `vh_數學B1_PointSlopeForm` — 點斜式
- 可用：write_line_equation_from_point_slope
- Family/line_type：point_slope

### `vh_數學B1_PolynomialBasicConcepts` — 多項式的基本概念
- 可用：polynomial_degree_product_sum, polynomial_descending_power_properties, polynomial_param_degree_constraint, zero_polynomial_find_coeffs
- Family/line_type：polynomial_degree_product_sum, polynomial_descending_power_properties, polynomial_param_degree_constraint, zero_polynomial_find_coeffs

### `vh_數學B1_PolynomialFactoring` — 因式分解
- 可用：polynomial_factoring
- Family/line_type：polynomial_factoring

### `vh_數學B1_QuadraticFunctionGraph` — 二次函數的圖形
- 可用：（無）
- 已定義但未接入 Runtime：integer_quadratic_graph_properties_choice, integer_quadratic_graph_translation_fill_blank, rational_quadratic_graph_translation_fill_blank

### `vh_數學B1_QuadraticInequalityAndFactoring` — 一元二次不等式的基本概念與十字交乘法
- 可用：（無）
- 已定義但未接入 Runtime：integer_factor_quadratic_by_cross_multiplication

### `vh_數學B1_RemainderTheorem` — 餘式定理
- 可用：remainder_theorem_evaluate
- Family/line_type：remainder_theorem_evaluate

### `vh_數學B1_SlopeOfALine` — 直線的斜率
- 可用：classify_and_compare_figure_slopes, collinear_three_points_parameter, collinear_three_points_parameter_choice, non_triangle_collinear_parameter, parallel_segments_parameter, slope_from_two_points, slopes_of_named_segments, solve_parameter_from_known_slope, solve_parameter_from_known_slope_choice
- Family/line_type：classify_and_compare_figure_slopes, collinear_three_points_parameter, collinear_three_points_parameter_choice, non_triangle_collinear_parameter, parallel_segments_parameter, slope_from_two_points, slopes_of_named_segments, solve_parameter_from_known_slope, solve_parameter_from_known_slope_choice

### `vh_數學B1_AbsoluteValueInequality` — 絕對值不等式
- 可用：absolute_value_inequality_integer_solution_count_choice, absolute_value_inequality_linear_expression_basic, absolute_value_inequality_shifted_basic, absolute_value_inequality_zero_center_basic
- Family/line_type：absolute_value_inequality_integer_solution_count_choice, absolute_value_inequality_linear_expression_basic, absolute_value_inequality_shifted_basic, absolute_value_inequality_zero_center_basic

### `vh_數學B1_DistanceBetweenPointAndLine` — 點到直線的距離
- 可用：compare_point_to_line_distances, distance_from_point_to_line, distance_from_point_to_line_parameter, distance_from_point_to_line_parameter_single_choice_scalar, slope_and_point_line_distance_parameter_choice
- Family/line_type：compare_point_to_line_distances, distance_from_point_to_line, distance_from_point_to_line_parameter, distance_from_point_to_line_parameter_single_choice_scalar, slope_and_point_line_distance_parameter_choice

### `vh_數學B1_FactorTheorem` — 因式定理
- 可用：factor_theorem_root_factor
- Family/line_type：factor_theorem_root_factor

### `vh_數學B1_FunctionConcept` — 函數的概念
- 可用：（無）

### `vh_數學B1_HorizontalAndVerticalLineEquations` — 水平線與鉛直線的直線方程式
- 可用：write_line_equation_from_point_slope
- Family/line_type：horizontal_line, vertical_line

### `vh_數學B1_PolynomialArithmeticOperations` — 多項式的四則運算
- 可用：polynomial_add_sub, polynomial_long_division, polynomial_multiply, polynomial_product_term_coefficient, polynomial_remainder_param_solve, polynomial_shifted_basis_eval, polynomial_synthetic_division
- Family/line_type：polynomial_add_sub, polynomial_long_division, polynomial_multiply, polynomial_product_term_coefficient, polynomial_remainder_param_solve, polynomial_shifted_basis_eval, polynomial_synthetic_division

### `vh_數學B1_PropertiesOfParallelLines` — 兩平行線的性質
- 可用：parallel_segments_parameter, parallel_segments_parameter_choice, parallel_two_point_lines_parameter_choice
- Family/line_type：parallel_segments_parameter, parallel_segments_parameter_choice, parallel_two_point_lines_parameter_choice

### `vh_數學B1_QuadraticInequalitySolution` — 一元二次不等式的解
- 可用：（無）
- 已定義但未接入 Runtime：integer_applied_quadratic_inequality_problem, integer_reverse_quadratic_inequality_coefficients, integer_solve_quadratic_inequality, integer_solve_quadratic_inequality_parameter_range, rational_solve_quadratic_inequality, rational_solve_quadratic_inequality_special_cases, text_short_factor_quadratic_by_cross_multiplication

### `vh_數學B1_RationalExpressionArithmeticOperations` — 分式的四則運算
- 可用：rational_expression_arithmetic
- Family/line_type：rational_expression_arithmetic

### `vh_數學B1_VertexFormOfQuadraticFunction` — 頂點式
- 可用：（無）
- 已定義但未接入 Runtime：numeric_quadratic_vertex_or_parameter_computation_short_answer, numeric_quadratic_vertex_or_parameter_computation_single_choice, quadratic_standard_to_vertex_properties, single_choice_quadratic_vertex_form_properties_single_choice, text_quadratic_graph_translation_fill_blank_short_answer, text_quadratic_vertex_form_translation_to_new_function_short_answer

### `vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning` — 絕對值不等式的展開與幾何意義
- 可用：absolute_value_inequality_interval_interpretation, absolute_value_inequality_linear_expression_basic
- Family/line_type：absolute_value_inequality_interval_interpretation, absolute_value_inequality_linear_expression_basic

### `vh_數學B1_CompletingTheSquare` — 配方法
- 可用：（無）
- 已定義但未接入 Runtime：integer_quadratic_graph_vertex_axis_choice, quadratic_vertex_or_parameter_computation

### `vh_數學B1_DistanceBetweenTwoParallelLines` — 兩條平行線間的距離
- 可用：area_using_parallel_distance, distance_between_parallel_lines, solve_parameter_from_parallel_distance
- Family/line_type：area_using_parallel_distance, distance_between_parallel_lines, solve_parameter_from_parallel_distance

### `vh_數學B1_DistanceBetweenTwoPointsInPlane` — 平面上兩點間的距離
- 可用：compute_distance_between_two_points, solve_unknown_coordinate_from_two_point_distance
- Family/line_type：compute_distance_between_two_points, solve_unknown_coordinate_from_two_point_distance

### `vh_數學B1_PolynomialEquality` — 多項式的相等
- 可用：polynomial_equality_identity
- Family/line_type：polynomial_equality_identity

### `vh_數學B1_PropertiesOfPerpendicularLines` — 兩垂直線的性質
- 可用：parallel_and_perpendicular_slopes_from_reference, perpendicular_segments_parameter, perpendicular_slope_quadrant_choice, perpendicular_two_point_lines_parameter, triangle_right_angle_verification
- Family/line_type：parallel_and_perpendicular_slopes_from_reference, perpendicular_segments_parameter, perpendicular_slope_quadrant_choice, perpendicular_two_point_lines_parameter, triangle_right_angle_verification

### `vh_數學B1_RationalEquation` — 分式方程式
- 可用：rational_equation_solve
- Family/line_type：rational_equation_solve

### `vh_數學B1_SlopeInterceptForm` — 斜截式
- 可用：slope_intercept_equation, slope_intercept_find_x_intercept, slope_intercept_read_slope_and_intercept
- Family/line_type：slope_intercept_equation, slope_intercept_find_x_intercept, slope_intercept_read_slope_and_intercept

### `vh_數學B1_InterceptForm` — 截距式
- 可用：intercept_form_equation_and_triangle_area, intercept_form_from_intercept_sum_and_slope, intercept_form_triangle_area, parabola_secant_parallel_line_choice, triangle_area_bisector_line_equation
- Family/line_type：intercept_form_equation_and_triangle_area, intercept_form_from_intercept_sum_and_slope, intercept_form_triangle_area, parabola_secant_parallel_line_choice, triangle_area_bisector_line_equation

### `vh_數學B1_MidpointCoordinates` — 中點坐標
- 可用：centroid_coordinate, inverse_centroid_vertex, midpoint_distance_from_origin, multi_part_midpoint_application, parallelogram_fourth_vertex, triangle_median_length
- Family/line_type：centroid_coordinate, inverse_centroid_vertex, midpoint_distance_from_origin, multi_part_midpoint_application, parallelogram_fourth_vertex, triangle_median_length

### `vh_數學B1_NumberLine` — 數線
- 可用：（無）

### `vh_數學B1_QuadraticFunctionExtremum` — 二次函數 $y = ax^{2} + bx + c$ 的最大（小）值
- 可用：（無）
- 已定義但未接入 Runtime：integer_compute_quadratic_vertex, integer_quadratic_vertex_or_parameter_computation, text_short_quadratic_vertex_or_parameter_computation

### `vh_數學B1_DivisionPointCoordinates` — 分點坐標
- 可用：compute_centroid_coordinates, compute_internal_division_point_coordinates, compute_section_point_distance_from_origin

### `vh_數學B1_SubSection332` — 分式
- 可用：（無）

### `vh_數學B1_LinearFunction` — 線型函數
- 可用：collinear_trisection_coordinate, draw_constant_function_graph, draw_linear_function_graph, graph_based_linear_application_inverse, graph_based_linear_model_equation, graph_based_tiered_linear_application_multi_part, graph_intercepts_and_linear_equation, linear_equation_from_two_points_choice, linear_graph_feasibility_choice, robust_budget_feasibility_choice
- Family/line_type：collinear_trisection_coordinate, draw_constant_function_graph, draw_linear_function_graph, graph_based_linear_application_inverse, graph_based_linear_model_equation, graph_based_tiered_linear_application_multi_part, graph_intercepts_and_linear_equation, linear_equation_from_two_points_choice, linear_graph_feasibility_choice, robust_budget_feasibility_choice

### `vh_數學B2_DirectedAngle` — 有向角
- 可用：（無）

### `vh_數學B2_RatioAndRatioValue` — 比與比值
- 可用：solve_similar_triangle_proportion
- Family/line_type：solve_similar_triangle_proportion

### `vh_數學B2_SubSection_1_3_1` — 標準位置角
- 可用：classify_standard_position_angle
- Family/line_type：classify_standard_position_angle

### `vh_數學B2_SubSection_1_4_1` — 正弦函數的圖形與其週期現象的表徵
- 可用：（無）

### `vh_數學B2_SubSection_2_2_1` — 測量的名詞與術語
- 可用：（無）

### `vh_數學B2_SubSection_3_1_1` — 向量定義
- 可用：express_named_vectors_in_given_basis, identify_equal_vector_mcq
- Family/line_type：express_named_vectors_in_given_basis, identify_equal_vector_mcq

### `vh_數學B2_SubSection_3_2_1` — 向量的坐標表示法
- 可用：compute_directed_segment_and_magnitude, compute_directed_segment_mixed_multipart, compute_triangle_perimeter_from_two_vectors, compute_vector_components_and_magnitude, solve_equal_vector_coordinates, solve_parallelogram_fourth_vertex
- Family/line_type：compute_directed_segment_and_magnitude, compute_directed_segment_mixed_multipart, compute_triangle_perimeter_from_two_vectors, compute_vector_components_and_magnitude, solve_equal_vector_coordinates, solve_parallelogram_fourth_vertex

### `vh_數學B2_SubSection_3_3_1` — 向量的夾角
- 可用：classify_angle_quality_from_dot_mcq, compute_cosine_of_angle_from_dot, solve_navigation_heading_correction
- Family/line_type：classify_angle_quality_from_dot_mcq, compute_cosine_of_angle_from_dot, solve_navigation_heading_correction

### `vh_數學B2_SubSection_4_2_1` — 點與圓的關係
- 可用：classify_point_vs_circles_multipart, identify_point_on_circle_mcq, solve_point_circle_parameter_range
- Family/line_type：classify_point_vs_circles_multipart, identify_point_on_circle_mcq, solve_point_circle_parameter_range

### `vh_數學B2_SubSection_1_3_2` — 任意角的三角函數
- 可用：compute_terminal_ray_trig_ratios
- Family/line_type：compute_terminal_ray_trig_ratios

### `vh_數學B2_SubSection_1_4_2` — 餘弦函數的圖形與其週期現象的表徵
- 可用：（無）

### `vh_數學B2_SubSection_2_1_1` — 正弦定理
- 可用：compute_sin_from_side_and_circumradius, compute_triangle_area_sas, solve_angle_by_law_of_sines, solve_side_and_circumradius_by_sines, solve_side_by_law_of_sines, solve_side_ratio_by_law_of_sines
- Family/line_type：compute_sin_from_side_and_circumradius, compute_triangle_area_sas, solve_angle_by_law_of_sines, solve_side_and_circumradius_by_sines, solve_side_by_law_of_sines, solve_side_ratio_by_law_of_sines

### `vh_數學B2_SubSection_2_2_2` — 求解平面三角測量問題的原則
- 可用：（無）

### `vh_數學B2_SubSection_3_1_2` — 向量的加法作圖
- 可用：simplify_vector_path_expression
- Family/line_type：simplify_vector_path_expression

### `vh_數學B2_SubSection_3_3_2` — 向量內積的定義
- 可用：compute_dot_identity_multipart, compute_dot_product_from_magnitudes_angle, compute_regular_polygon_edge_dot
- Family/line_type：compute_dot_identity_multipart, compute_dot_product_from_magnitudes_angle, compute_regular_polygon_edge_dot

### `vh_數學B2_SubSection_4_1_1` — 圓的標準式
- 可用：circle_center_tangent_to_line, circle_equal_radius_at_origin, circle_from_diameter_endpoints, circle_origin_through_lines_intersection, circle_same_center_scaled_area, identify_center_radius_from_standard, interpret_circular_locus_equation, translate_and_scale_circle, write_circle_equations_from_conditions
- Family/line_type：circle_center_tangent_to_line, circle_equal_radius_at_origin, circle_from_diameter_endpoints, circle_origin_through_lines_intersection, circle_same_center_scaled_area, identify_center_radius_from_standard, interpret_circular_locus_equation, translate_and_scale_circle, write_circle_equations_from_conditions

### `vh_數學B2_SubSection_4_2_2` — 圓與直線的關係
- 可用：classify_line_circle_relation, classify_line_circle_relation_mcq, classify_lines_vs_circle_multipart, compute_chord_length, compute_storm_path_length_in_circle, compute_triangle_center_chord_area, count_line_circle_intersections, solve_axis_tangent_parameter, solve_diameter_chord_parameter_mcq, solve_line_circle_parameter_range, solve_line_circle_relation_ranges_multipart, solve_line_circle_tangent_parameter
- Family/line_type：classify_line_circle_relation, classify_line_circle_relation_mcq, classify_lines_vs_circle_multipart, compute_chord_length, compute_storm_path_length_in_circle, compute_triangle_center_chord_area, count_line_circle_intersections, solve_axis_tangent_parameter, solve_diameter_chord_parameter_mcq, solve_line_circle_parameter_range, solve_line_circle_relation_ranges_multipart, solve_line_circle_tangent_parameter

### `vh_數學B2_TrigonometricFunctionsOfAcuteAngles` — 銳角三角函數
- 可用：compute_chord_and_arc_length, compute_right_triangle_trig_ratios, simplify_fundamental_trig_expression, solve_acute_trig_constraints
- Family/line_type：compute_chord_and_arc_length, compute_right_triangle_trig_ratios, simplify_fundamental_trig_expression, solve_acute_trig_constraints

### `vh_數學B2_AngleMeasurementAndConversion` — 角的度量與換算
- 可用：convert_angle_measure
- Family/line_type：convert_angle_measure

### `vh_數學B2_SubSection_1_4_3` — 正切函數的圖形與其週期現象的表徵
- 可用：analyze_affine_transformed_trig_graph, compare_trig_values_by_monotonicity, solve_trig_value_quadratic_constraint
- Family/line_type：analyze_affine_transformed_trig_graph, compare_trig_values_by_monotonicity, solve_trig_value_quadratic_constraint

### `vh_數學B2_SubSection_2_2_3` — 直角三角形的測量
- 可用：solve_adjacent_from_hypotenuse_ground_angle, solve_broken_tree_original_height, solve_building_height_with_flagpole_elevations, solve_height_decimal_from_sight_line_elevation, solve_height_from_sight_line_elevation, solve_horizontal_from_height_depression, solve_horizontal_from_height_elevation, solve_opposite_from_adjacent_elevation, solve_two_elevation_horizontal_shift, solve_two_elevation_unknown_height
- Family/line_type：solve_adjacent_from_hypotenuse_ground_angle, solve_broken_tree_original_height, solve_building_height_with_flagpole_elevations, solve_height_decimal_from_sight_line_elevation, solve_height_from_sight_line_elevation, solve_horizontal_from_height_depression, solve_horizontal_from_height_elevation, solve_opposite_from_adjacent_elevation, solve_two_elevation_horizontal_shift, solve_two_elevation_unknown_height

### `vh_數學B2_SubSection_3_1_3` — 向量的減法作圖
- 可用：simplify_vector_path_expression
- Family/line_type：simplify_vector_path_expression

### `vh_數學B2_SubSection_3_2_2` — 向量加減的坐標表示法
- 可用：compute_chain_closure_vector_mcq, compute_point_vectors_linear_combination, compute_triangle_chain_and_perimeter, compute_vector_linear_combination, compute_vector_sum_difference, solve_parallelogram_fourth_vertex
- Family/line_type：compute_chain_closure_vector_mcq, compute_point_vectors_linear_combination, compute_triangle_chain_and_perimeter, compute_vector_linear_combination, compute_vector_sum_difference, solve_parallelogram_fourth_vertex

### `vh_數學B2_SubSection_3_3_3` — 向量內積的坐標表示法
- 可用：compute_cosine_of_angle_from_dot, compute_dot_product_coordinates, compute_midpoint_dot_product, plot_navigation_points_coordinates, solve_dot_product_parameter_mcq
- Family/line_type：compute_cosine_of_angle_from_dot, compute_dot_product_coordinates, compute_midpoint_dot_product, plot_navigation_points_coordinates, solve_dot_product_parameter_mcq

### `vh_數學B2_SubSection_4_1_2` — 圓的一般式
- 可用：circle_center_on_axis_area, circle_through_three_points, classify_general_circle_graph, compute_circle_area_from_general, evaluate_center_radius_expression, identify_center_radius_from_general, identify_circle_from_product_form, solve_circle_parameter_range, solve_circle_parameter_range_mcq, translate_and_scale_circle
- Family/line_type：circle_center_on_axis_area, circle_through_three_points, classify_general_circle_graph, compute_circle_area_from_general, evaluate_center_radius_expression, identify_center_radius_from_general, identify_circle_from_product_form, solve_circle_parameter_range, solve_circle_parameter_range_mcq, translate_and_scale_circle

### `vh_數學B2_SubSection_4_2_3` — 圓的切線方程式
- 可用：compute_tangents_from_point_quad_area, tangent_at_point_on_circle, tangent_at_point_on_circle_mcq, tangents_parallel_to_line, tangents_perpendicular_to_line
- Family/line_type：compute_tangents_from_point_quad_area, tangent_at_point_on_circle, tangent_at_point_on_circle_mcq, tangents_parallel_to_line, tangents_perpendicular_to_line

### `vh_數學B2_TrigonometricValuesOfSpecialAngles` — 30°、45°、60° 特別角的三角函數值
- 可用：evaluate_exact_special_angle_expression, solve_right_triangle_projection
- Family/line_type：evaluate_exact_special_angle_expression, solve_right_triangle_projection

### `vh_數學B2_ArcLengthAndAreaOfSector` — 扇形的弧長與面積
- 可用：sector_arc_and_area
- Family/line_type：sector_arc_and_area

### `vh_數學B2_CalculatingFunctionValuesUsingCalculator` — 使用計算機計算函數值
- 可用：evaluate_trig_decimal
- Family/line_type：evaluate_trig_decimal

### `vh_數學B2_SubSection_1_3_4` — 三角函數值在四個象限的正負情形
- 可用：classify_trig_derived_point_quadrant, solve_signed_trig_constraints
- Family/line_type：classify_trig_derived_point_quadrant, solve_signed_trig_constraints

### `vh_數學B2_SubSection_1_4_4` — 三角函數圖形的變化與週期
- 可用：analyze_affine_transformed_trig_graph, analyze_tangent_absolute_graph_period, calculate_trig_period_from_argument_scale, classify_trig_equation_feasibility, classify_trig_expression_sign_change, compare_trig_values_by_monotonicity, count_sine_cosine_intersections, evaluate_trig_decimal, solve_trig_value_quadratic_constraint
- Family/line_type：analyze_affine_transformed_trig_graph, analyze_tangent_absolute_graph_period, calculate_trig_period_from_argument_scale, classify_trig_equation_feasibility, classify_trig_expression_sign_change, compare_trig_values_by_monotonicity, count_sine_cosine_intersections, evaluate_trig_decimal, solve_trig_value_quadratic_constraint

### `vh_數學B2_SubSection_2_1_2` — 餘弦定理
- 可用：compute_circumradius_from_three_sides, solve_angle_by_law_of_cosines, solve_cosine_identity_angle, solve_detour_extra_distance_by_cosines, solve_side_by_law_of_cosines
- Family/line_type：compute_circumradius_from_three_sides, solve_angle_by_law_of_cosines, solve_cosine_identity_angle, solve_detour_extra_distance_by_cosines, solve_side_by_law_of_cosines

### `vh_數學B2_SubSection_2_2_4` — 非直角三角形測量
- 可用：solve_side_by_law_of_cosines, solve_side_by_law_of_sines
- Family/line_type：solve_side_by_law_of_cosines, solve_side_by_law_of_sines

### `vh_數學B2_SubSection_3_1_4` — 向量的實數積作圖
- 可用：construct_linear_combination_choice, express_linear_combination_from_givens, express_section_point_vector, identify_resultant_path_mcq, solve_scalar_multiple_relation_fill, solve_section_coefficient_pair
- Family/line_type：construct_linear_combination_choice, express_linear_combination_from_givens, express_section_point_vector, identify_resultant_path_mcq, solve_scalar_multiple_relation_fill, solve_section_coefficient_pair

### `vh_數學B2_SubSection_3_2_3` — 向量實數積的坐標表示法
- 可用：solve_collinear_ratio_mcq, solve_point_from_vector_combination
- Family/line_type：solve_collinear_ratio_mcq, solve_point_from_vector_combination

### `vh_數學B2_SubSection_3_3_4` — 兩向量的垂直
- 可用：solve_perpendicular_composite_parameter, solve_perpendicular_vector_parameter
- Family/line_type：solve_perpendicular_composite_parameter, solve_perpendicular_vector_parameter

### `vh_數學B2_FundamentalTrigonometricIdentities` — 三角函數的基本關係式
- 可用：complete_cofunction_identity, simplify_fundamental_trig_expression, solve_acute_trig_constraints
- Family/line_type：complete_cofunction_identity, simplify_fundamental_trig_expression, solve_acute_trig_constraints

### `vh_數學B2_SubSection_1_3_5` — 象限角的三角函數值
- 可用：evaluate_exact_arbitrary_angle_trig_expression
- Family/line_type：evaluate_exact_arbitrary_angle_trig_expression

### `vh_數學B2_SubSection_2_2_5` — 簡單的立體測量
- 可用：solve_height_from_isosceles_bearing_walk_elevation, solve_height_from_two_elevation_tan_ratios, solve_tower_two_elevation_path_and_river_width
- Family/line_type：solve_height_from_isosceles_bearing_walk_elevation, solve_height_from_two_elevation_tan_ratios, solve_tower_two_elevation_path_and_river_width

### `vh_數學B2_SubSection_3_3_5` — 向量內積的性質
- 可用：classify_dot_sign_from_diagram_mcq, compute_dot_product_from_magnitudes_angle, expand_perpendicular_dot_product, solve_angle_from_magnitude_identity
- Family/line_type：classify_dot_sign_from_diagram_mcq, compute_dot_product_from_magnitudes_angle, expand_perpendicular_dot_product, solve_angle_from_magnitude_identity

### `vh_數學B2_SubSection_4_2_4` — 切線段長
- 可用：compute_tangent_segment_length_mcq, compute_tangent_segment_lengths, count_line_vs_two_circles_intersections
- Family/line_type：compute_tangent_segment_length_mcq, compute_tangent_segment_lengths, count_line_vs_two_circles_intersections

### `vh_數學B2_CoterminalAngles` — 同界角
- 可用：coterminal_angles
- Family/line_type：coterminal_angles

### `vh_數學B2_SubSection_1_3_6` — 任意角三角函數求值
- 可用：evaluate_exact_arbitrary_angle_trig_expression, solve_arbitrary_angle_vertical_projection
- Family/line_type：evaluate_exact_arbitrary_angle_trig_expression, solve_arbitrary_angle_vertical_projection

### `vh_數學B2_SubSection_3_2_4` — 向量實數積的基本性質
- 可用：compute_vector_linear_combination, solve_unknown_vector_linear_equation
- Family/line_type：compute_vector_linear_combination, solve_unknown_vector_linear_equation

### `vh_數學B2_SubSection_1_3_7` — 化任意角為銳角轉換關係式
- 可用：classify_trig_derived_point_quadrant, complete_reference_angle_conversion, evaluate_exact_arbitrary_angle_trig_expression, simplify_fundamental_trig_expression
- Family/line_type：classify_trig_derived_point_quadrant, complete_reference_angle_conversion, evaluate_exact_arbitrary_angle_trig_expression, simplify_fundamental_trig_expression

### `vh_數學B2_SubSection_3_2_5` — 向量的平行
- 可用：solve_parallel_then_magnitude_mcq, solve_parallel_vector_parameter
- Family/line_type：solve_parallel_then_magnitude_mcq, solve_parallel_vector_parameter

### `vh_數學B2_SubSection_3_2_6` — 單位向量
- 可用：compute_scaled_direction_vector, identify_unit_vector_mcq
- Family/line_type：compute_scaled_direction_vector, identify_unit_vector_mcq

### `vh_數學B3_PlainHeading_3_2_1` — 二元一次不等式的定義
- 可用：（無）

### `vh_數學B3_SubSection_1_1_1` — 數列與級數
- 可用：expand_general_term_first_n
- Family/line_type：expand_general_term_first_n

### `vh_數學B3_SubSection_1_2_1` — 等比數列
- 可用：geometric_from_two_terms, geometric_growth_table_cells, geometric_insert_terms, geometric_nth_from_a1_r, geometric_r_from_a1_an, geometric_ratio_from_product_quotient, geometric_ratio_from_shifted_pair_sums
- Family/line_type：geometric_from_two_terms, geometric_growth_table_cells, geometric_insert_terms, geometric_nth_from_a1_r, geometric_r_from_a1_an, geometric_ratio_from_product_quotient, geometric_ratio_from_shifted_pair_sums

### `vh_數學B3_SubSection_2_1_1` — 一元一次方程式
- 可用：linear_solve_general, linear_solve_isolated, linear_word_class_share, linear_word_markup, linear_word_ratio_sum, linear_word_three_shares, linear_word_two_conditions, linear_word_two_plans, linear_word_unit_total
- Family/line_type：linear_solve_general, linear_solve_isolated, linear_word_class_share, linear_word_markup, linear_word_ratio_sum, linear_word_three_shares, linear_word_two_conditions, linear_word_two_plans, linear_word_unit_total

### `vh_數學B3_SubSection_2_2_1` — 一元二次方程式的基礎概念
- 可用：quadratic_factor_identity
- Family/line_type：quadratic_factor_identity

### `vh_數學B3_SubSection_3_1_1` — 二元一次方程組的基本概念
- 可用：（無）

### `vh_數學B3_SubSection_3_3_1` — 二元一次聯立不等式
- 可用：feasible_area, integer_points_count, labeled_region_choice, shade_to_system, system_region_corner
- Family/line_type：feasible_area, integer_points_count, labeled_region_choice, shade_to_system, system_region_corner

### `vh_數學B3_SubSection_4_1_1` — 正整數指數與指數律
- 可用：exp_integer_power_eval, exp_law_product_choice, exp_prime_factor_exponent
- Family/line_type：exp_integer_power_eval, exp_law_product_choice, exp_prime_factor_exponent

### `vh_數學B3_SubSection_4_2_1` — 指數函數的圖形
- 可用：exp_compare_same_base, exp_model_from_graph, graph_property_choice, graph_sketch_table
- Family/line_type：exp_compare_same_base, exp_model_from_graph, graph_property_choice, graph_sketch_table

### `vh_數學B3_SubSection_4_3_1` — 對數的意義
- 可用：log_definition_eval, log_domain_validity_choice
- Family/line_type：log_definition_eval, log_domain_validity_choice

### `vh_數學B3_SubSection_4_4_1` — 對數函數的圖形
- 可用：graph_property_choice, graph_sketch_table, log_compare_values, log_decibel_application
- Family/line_type：graph_property_choice, graph_sketch_table, log_compare_values, log_decibel_application

### `vh_數學B3_SubSection_4_5_1` — 常用對數表的使用
- 可用：common_log_given_approx_eval, common_log_table_lookup
- Family/line_type：common_log_given_approx_eval, common_log_table_lookup

### `vh_數學B3_PlainHeading_3_2_2` — 二元一次不等式的解
- 可用：integer_feasible_choice, integer_feasible_count
- Family/line_type：integer_feasible_choice, integer_feasible_count

### `vh_數學B3_SubSection_2_1_2` — 一元一次不等式
- 可用：inequality_bmi_bound, inequality_solve, inequality_word_minimum
- Family/line_type：inequality_bmi_bound, inequality_solve, inequality_word_minimum

### `vh_數學B3_SubSection_2_2_2` — 一元二次方程式的解法
- 可用：quadratic_formula_exact, quadratic_integer_roots, quadratic_projectile_time, quadratic_right_triangle_side_relation, quadratic_word_pair_count, quadratic_word_pythagoras
- Family/line_type：quadratic_formula_exact, quadratic_integer_roots, quadratic_projectile_time, quadratic_right_triangle_side_relation, quadratic_word_pair_count, quadratic_word_pythagoras

### `vh_數學B3_SubSection_3_1_2` — 二元一次聯立方程組的解法
- 可用：system_abs_pair, system_continued_ratio, system_dependent_value, system_known_solution, system_linear_combo, system_ordered_pair, system_word_two
- Family/line_type：system_abs_pair, system_continued_ratio, system_dependent_value, system_known_solution, system_linear_combo, system_ordered_pair, system_word_two

### `vh_數學B3_SubSection_3_3_2` — 線性規劃
- 可用：（無）

### `vh_數學B3_SubSection_4_1_2` — 零指數與負整數指數
- 可用：exp_fill_integer_exponent, exp_integer_exponent_simplify, exp_zero_negative_eval
- Family/line_type：exp_fill_integer_exponent, exp_integer_exponent_simplify, exp_zero_negative_eval

### `vh_數學B3_SubSection_4_2_2` — 指數方程式
- 可用：exp_equation_convert_base, exp_equation_factor_common, exp_equation_quadratic_sub, exp_equation_same_base, exp_graph_identify_choice, exp_power_substitution_value
- Family/line_type：exp_equation_convert_base, exp_equation_factor_common, exp_equation_quadratic_sub, exp_equation_same_base, exp_graph_identify_choice, exp_power_substitution_value

### `vh_數學B3_SubSection_4_3_2` — 對數的性質
- 可用：log_application_statement_choice, log_basic_property_eval, log_change_base_chain_eval, log_change_base_product_eval, log_definition_inverse_eval, log_express_in_ab, log_linear_combination_eval, log_product_quotient_eval, log_rational_value_eval, log_reciprocal_sum_param
- Family/line_type：log_application_statement_choice, log_basic_property_eval, log_change_base_chain_eval, log_change_base_product_eval, log_definition_inverse_eval, log_express_in_ab, log_linear_combination_eval, log_product_quotient_eval, log_rational_value_eval, log_reciprocal_sum_param

### `vh_數學B3_SubSection_4_4_2` — 對數方程式
- 可用：log_curve_through_points, log_equation_linear_arg, log_equation_product_quadratic, log_equation_quadratic_arg, log_equation_solve_base, log_threshold_application_choice
- Family/line_type：log_curve_through_points, log_equation_linear_arg, log_equation_product_quadratic, log_equation_quadratic_arg, log_equation_solve_base, log_threshold_application_choice

### `vh_數學B3_SubSection_4_5_2` — 使用計算機鍵
- 可用：（無）

### `vh_數學B3_PlainHeading_3_2_3` — 邊界、半平面
- 可用：halfplane_region, shade_to_inequality
- Family/line_type：halfplane_region, shade_to_inequality

### `vh_數學B3_SubSection_1_1_2` — 等差數列
- 可用：arithmetic_d_from_a1_an, arithmetic_first_threshold_crossing, arithmetic_from_two_terms, arithmetic_insert_terms, arithmetic_nth_from_a1_d
- Family/line_type：arithmetic_d_from_a1_an, arithmetic_first_threshold_crossing, arithmetic_from_two_terms, arithmetic_insert_terms, arithmetic_nth_from_a1_d

### `vh_數學B3_SubSection_1_2_2` — 等比中項
- 可用：ap_gp_mixed_mean_middle, geometric_mean_solve_x, geometric_mean_value
- Family/line_type：ap_gp_mixed_mean_middle, geometric_mean_solve_x, geometric_mean_value

### `vh_數學B3_SubSection_2_2_3` — 根的性質與判別式
- 可用：quadratic_parameter_equal_roots, quadratic_parameter_no_real, quadratic_parameter_two_distinct, quadratic_root_count
- Family/line_type：quadratic_parameter_equal_roots, quadratic_parameter_no_real, quadratic_parameter_two_distinct, quadratic_root_count

### `vh_數學B3_SubSection_3_1_3` — 二元一次方程組的幾何圖形
- 可用：line_pair_relation, line_slope_pair, system_dependent_value, system_parameter_cases, system_parameter_unique
- Family/line_type：line_pair_relation, line_slope_pair, system_dependent_value, system_parameter_cases, system_parameter_unique

### `vh_數學B3_SubSection_3_3_3` — 求目標函數的最佳值
- 可用：lp_extrema
- Family/line_type：lp_extrema

### `vh_數學B3_SubSection_4_1_3` — 有理數指數
- 可用：exp_growth_decay_model_choice, exp_rational_exponent_simplify, exp_rational_power_combo, exp_rational_power_eval, exp_solve_exponent_radical
- Family/line_type：exp_growth_decay_model_choice, exp_rational_exponent_simplify, exp_rational_power_combo, exp_rational_power_eval, exp_solve_exponent_radical

### `vh_數學B3_SubSection_4_5_3` — 首數、尾數及其應用
- 可用：log_characteristic_mantissa, log_characteristic_rule, log_growth_years, log_power_digit_count, log_power_first_nonzero, log_scientific_shift
- Family/line_type：log_characteristic_mantissa, log_characteristic_rule, log_growth_years, log_power_digit_count, log_power_first_nonzero, log_scientific_shift

### `vh_數學B3_PlainHeading_3_2_4` — 相異兩點在直線的同側、異側
- 可用：same_side_parameter, same_side_test
- Family/line_type：same_side_parameter, same_side_test

### `vh_數學B3_SubSection_1_2_3` — 等比數列的遞迴關係式
- 可用：geometric_recurrence_general
- Family/line_type：geometric_recurrence_general

### `vh_數學B3_SubSection_2_2_4` — 根與係數的關係
- 可用：quadratic_build_from_symmetric, quadratic_vieta_expressions, quadratic_vieta_parameter
- Family/line_type：quadratic_build_from_symmetric, quadratic_vieta_expressions, quadratic_vieta_parameter

### `vh_數學B3_SubSection_3_3_4` — 線性規劃的應用
- 可用：constraint_system_choice, lp_application
- Family/line_type：constraint_system_choice, lp_application

### `vh_數學B3_SubSection_1_1_3` — 等差中項
- 可用：arithmetic_mean_solve
- Family/line_type：arithmetic_mean_solve

### `vh_數學B3_SubSection_1_2_4` — 等比級數
- 可用：geometric_first_threshold_crossing, geometric_series_recover_param, geometric_series_sum_given
- Family/line_type：geometric_first_threshold_crossing, geometric_series_recover_param, geometric_series_sum_given

### `vh_數學B3_SubSection_1_1_4` — 等差數列的遞迴關係式
- 可用：arithmetic_recurrence_general
- Family/line_type：arithmetic_recurrence_general

### `vh_數學B3_SubSection_1_1_5` — 等差級數
- 可用：arithmetic_index_and_total_sum, arithmetic_odd_count_mid_total, arithmetic_series_from_two_terms, arithmetic_series_recover_param, arithmetic_series_sum_given, arithmetic_sum_multiples_range
- Family/line_type：arithmetic_index_and_total_sum, arithmetic_odd_count_mid_total, arithmetic_series_from_two_terms, arithmetic_series_recover_param, arithmetic_series_sum_given, arithmetic_sum_multiples_range

### `vh_數學B4_AdditionPrinciple` — 加法原理
- 可用：（無）

### `vh_數學B4_BinomialTheorem` — 二項式定理
- 可用：（無）

### `vh_數學B4_CentralTendencyMeasures` — 集中趨勢量數
- 可用：compute_arithmetic_mean_from_raw_values, compute_median_from_raw_values, compute_mode_from_raw_values, compute_weighted_mean
- Family/line_type：compute_arithmetic_mean_from_raw_values, compute_median_from_raw_values, compute_mode_from_raw_values, compute_weighted_mean

### `vh_數學B4_CombinationDefinition` — 組合的定義與計算
- 可用：（無）

### `vh_數學B4_FrequencyDistributionTableConstruction` — 統計資料的次數分配表編製步驟
- 可用：frequency_table_construction_review
- Family/line_type：frequency_table_construction_review

### `vh_數學B4_MathematicalExpectation` — 數學期望值
- 可用：（無）

### `vh_數學B4_PermutationOfNonDistinctObjects` — 不盡相異物的排列
- 可用：（無）

### `vh_數學B4_ProbabilityDefinition` — 機率的定義
- 可用：（無）

### `vh_數學B4_RepeatedPermutation` — 重複排列
- 可用：（無）

### `vh_數學B4_SampleSpaceAndEvents` — 樣本空間與事件
- 可用：（無）

### `vh_數學B4_SamplingSurvey` — 抽樣調查
- 可用：（無）

### `vh_數學B4_BasicConceptsOfSets` — 集合的基本概念
- 可用：（無）

### `vh_數學B4_CombinationApplications` — 組合的應用
- 可用：（無）

### `vh_數學B4_HistogramsAndFrequencyPolygons` — 次數分配直方圖與次數分配折線圖的繪製
- 可用：frequency_distribution_chart_construction, histogram_distribution_update
- Family/line_type：frequency_distribution_chart_construction, histogram_distribution_update

### `vh_數學B4_MathematicalExpectationDefinition` — 數學期望值的定義與計算
- 可用：（無）

### `vh_數學B4_MultiplicationPrinciple` — 乘法原理
- 可用：（無）

### `vh_數學B4_PascalTriangle` — 巴斯卡三角形
- 可用：（無）

### `vh_數學B4_PermutationOfDistinctObjects` — 相異物的排列
- 可用：（無）

### `vh_數學B4_PermutationWithRepetition` — 重複排列
- 可用：（無）

### `vh_數學B4_ProbabilityOperations` — 機率的運算
- 可用：（無）

### `vh_數學B4_SamplingMethods` — 抽樣方法
- 可用：（無）

### `vh_數學B4_WeightedMean` — 加權平均數
- 可用：compute_weighted_mean
- Family/line_type：compute_weighted_mean

### `vh_數學B4_ApplicationsOfExpectation` — 數學期望值的應用
- 可用：（無）

### `vh_數學B4_BinomialCoefficientIdentities` — 二項式係數性質
- 可用：（無）

### `vh_數學B4_Combination` — 組合
- 可用：（無）

### `vh_數學B4_ConditionalProbability` — 條件機率
- 可用：（無）

### `vh_數學B4_DispersionMeasures` — 離散趨勢量數
- 可用：compare_dispersion, compute_population_standard_deviation, compute_quartiles_and_iqr, conceptual_dispersion_judgment
- Family/line_type：compare_dispersion, compute_population_standard_deviation, compute_quartiles_and_iqr, conceptual_dispersion_judgment

### `vh_數學B4_StatisticalBasicConcepts` — 統計的基本概念
- 可用：（無）

### `vh_數學B4_StatisticalChartReading` — 統計圖表判讀
- 可用：cumulative_above_fail_count, cumulative_above_interval_count, cumulative_below_interval_count
- Family/line_type：cumulative_above_fail_count, cumulative_above_interval_count, cumulative_below_interval_count

### `vh_數學B4_TreeDiagramCounting` — 樹狀圖
- 可用：（無）

### `vh_數學B4_CombinationProperties` — 組合的性質
- 可用：（無）

### `vh_數學B4_CumulativeFrequencyTablesAndGraphs` — 累積次數分配表與累積次數分配折線圖
- 可用：class_frequency_from_cumulative_difference, cumulative_frequency_graph_reading, cumulative_frequency_table_construction
- Family/line_type：class_frequency_from_cumulative_difference, cumulative_frequency_graph_reading, cumulative_frequency_table_construction

### `vh_數學B4_FactorialNotation` — 階乘記法
- 可用：（無）

### `vh_數學B4_IndependentEvents` — 獨立事件
- 可用：（無）

### `vh_數學B4_VarianceAndStandardDeviation` — 變異數與標準差
- 可用：compute_population_standard_deviation, compute_sample_standard_deviation
- Family/line_type：compute_population_standard_deviation, compute_sample_standard_deviation

### `vh_數學B4_DataOrganizationAndCharts` — 資料整理與圖表編製
- 可用：（無）

### `vh_數學B4_LinearTransformationOfData` — 資料的線性變換
- 可用：compute_arithmetic_mean_from_raw_values, compute_population_standard_deviation
- 已定義但未接入 Runtime：compute_linear_transform_median_and_range
- Family/line_type：compute_arithmetic_mean_from_raw_values, compute_linear_transform_median_and_range, compute_population_standard_deviation

### `vh_數學B4_ProbabilityProperties` — 機率的性質
- 可用：（無）

### `vh_數學B4_NormalDistributionAndEmpiricalRule` — 常態分配與經驗法則
- 可用：compare_distribution_spread, empirical_rule_population_count
- Family/line_type：compare_distribution_spread, empirical_rule_population_count

### `vh_數學B4_OpinionPollInterpretation` — 民意調查的解讀
- 可用：poll_interval_from_support_and_margin, poll_support_from_interval
- Family/line_type：poll_interval_from_support_and_margin, poll_support_from_interval
