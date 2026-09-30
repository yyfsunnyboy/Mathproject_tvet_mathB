# Practice Type Rotation B1-B4 Audit

generated_at: 2026-09-30 23:42:49  elapsed: 136.1s  generator_smoke: True

# Summary

| Volume | Curriculum rows | Sections (published) | READY | FALLBACK | BLOCKED | Coverage | Excluded |
|---|---:|---:|---:|---:|---:|---:|---|
| 數學B1 | 45 | 32 | 26 | 6 | 0 | 81.2% | outline_placeholder=10, runtime_missing=1, unpublished_inactive=2 |
| 數學B2 | 57 | 42 | 42 | 0 | 0 | 100.0% | outline_placeholder=10, runtime_missing=2, unpublished_inactive=3 |
| 數學B3 | 50 | 34 | 34 | 0 | 0 | 100.0% | outline_placeholder=12, unpublished_inactive=4 |
| 數學B4 | 40 | 24 | 11 | 13 | 0 | 45.8% | runtime_missing=14, unpublished_inactive=2 |

overall: published sections=132, rotation-ready sections=113, coverage=85.6%

# Exceptions

| skill_id | section | category | reason | severity | recommended action |
|---|---|---|---|---|---|
| vh_數學B1_QuadraticFunctionGraph,vh_數學B1_VertexFormOfQuadraticFunction,vh_數學B1_CompletingTheSquare,vh_數學B1_QuadraticFunctionExtremum,vh_數學B1_QuadraticInequalityAndFactoring,vh_數學B1_QuadraticInequalitySolution | 1 坐標系與函數圖形 | progression | 6 published non-READY section(s) are skipped by rotation; chapter_completed is reached without them | P1 | convert these wrappers to V3 component specs, or accept legacy practice for them |
| vh_數學B1_CompletingTheSquare | 1-3 二次函數 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 2); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B1_QuadraticFunctionExtremum | 1-3 二次函數 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 3); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B1_QuadraticFunctionGraph | 1-3 二次函數 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 3); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B1_QuadraticInequalityAndFactoring | 1-4 一元二次不等式 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 1); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B1_QuadraticInequalitySolution | 1-4 一元二次不等式 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 7); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B1_VertexFormOfQuadraticFunction | 1-3 二次函數 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 6); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B2_SubSection_2_1_2 | 2-1 正弦定理與餘弦定理 | content issue | src_11686 intermittent: 1 failed seed(s) before success (ValueError:invalid_vocational_multiple_choice:vocational_choice_semantic_duplicate,vocational_choice_duplicate) | P2 | route retry covers it; improve generator validity |
| vh_數學B2_SubSection_2_2_3 | 2-2 三角測量 | content issue | src_11728 intermittent: 3 failed seed(s) before success (ValueError:invalid_vocational_multiple_choice:vocational_choice_shape_mismatch) | P2 | route retry covers it; improve generator validity |
| vh_數學B4_AdditionPrinciple | 1-1 加法原理與乘法原理 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 0); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B4_AdditionPrinciple,vh_數學B4_MultiplicationPrinciple,vh_數學B4_FactorialNotation,vh_數學B4_PermutationOfNonDistinctObjects,vh_數學B4_PermutationOfDistinctObjects,vh_數學B4_RepeatedPermutation,vh_數學B4_PermutationWithRepetition,vh_數學B4_CombinationDefinition,vh_數學B4_CombinationApplications,vh_數學B4_Combination,vh_數學B4_CombinationProperties,vh_數學B4_BinomialTheorem,vh_數學B4_BinomialCoefficientIdentities | 1 排列組合 | progression | 13 published non-READY section(s) are skipped by rotation; chapter has no READY section (rotation never starts) | P2 | convert these wrappers to V3 component specs, or accept legacy practice for them |
| vh_數學B4_BinomialCoefficientIdentities | 1-5 二項式定理 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 0); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B4_BinomialTheorem | 1-5 二項式定理 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 0); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B4_Combination | 1-4 組合 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 0); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B4_CombinationApplications | 1-4 組合 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 0); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B4_CombinationDefinition | 1-4 組合 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 0); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B4_CombinationProperties | 1-4 組合 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 0); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B4_FactorialNotation | 1-1 加法原理與乘法原理 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 0); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B4_MultiplicationPrinciple | 1-1 加法原理與乘法原理 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 0); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B4_PermutationOfDistinctObjects | 1-2 直線排列 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 0); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B4_PermutationOfNonDistinctObjects | 1-2 直線排列 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 0); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B4_PermutationWithRepetition | 1-3 重複排列 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 0); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B4_RepeatedPermutation | 1-3 重複排列 | runtime metadata incomplete (legacy wrapper) | skill-level generator without component dispatch (specs with problem_type_id: 0); legacy practice OK | P2 | legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper |
| vh_數學B1_NumberLine | 1-1 數線與絕對值 | unpublished/dryrun | runtime module exists but skills_info.is_active=0 | info | stay hidden; must not be a next-section target |
| vh_數學B1_SubSection332 | 3-3 因式分解與分式 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B2_SubSection_1_4_1 | 1-4 正弦、餘弦函數的圖形 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B2_SubSection_1_4_2 | 1-4 正弦、餘弦函數的圖形 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_ApplicationsOfExpectation | 2-3 數學期望值 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_BasicConceptsOfSets | 2-1 樣本空間與事件 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_ConditionalProbability | 2-2 機率的運算 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_IndependentEvents | 2-2 機率的運算 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_MathematicalExpectation | 2-3 數學期望值 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_MathematicalExpectationDefinition | 2-3 數學期望值 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_PascalTriangle | 1-5 二項式定理 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_ProbabilityDefinition | 2-2 機率的運算 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_ProbabilityOperations | 2-2 機率的運算 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_ProbabilityProperties | 2-2 機率的運算 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_SampleSpaceAndEvents | 2-1 樣本空間與事件 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_SamplingMethods | 3-1 統計的基本概念 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_SamplingSurvey | 3-1 統計的基本概念 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |
| vh_數學B4_TreeDiagramCounting | 1-1 加法原理與乘法原理 | runtime_missing | active in curriculum but no runtime module (manifest=None) | info | not published yet; excluded from rotation |

# Type distribution

min=1 max=12 median=3 sections_with_1_type=26 sections_with_>=7_types=13 multi_candidate_sections=107

histogram (types -> sections): {1: 26, 2: 24, 3: 19, 4: 12, 5: 9, 6: 10, 7: 3, 9: 4, 10: 4, 11: 1, 12: 1}

| Volume | Chapter | Section | skill_id | status | components | unique types | candidates per type |
|---|---|---|---|---|---:|---:|---|
| 數學B1 | 1 坐標系與函數圖形 | 1-1 數線與絕對值 | vh_數學B1_AbsoluteValue | READY | 4 | 2 | 1, 3 |
| 數學B1 | 1 坐標系與函數圖形 | 1-1 數線與絕對值 | vh_數學B1_AbsoluteValueInequality | READY | 10 | 4 | 1, 4, 2, 3 |
| 數學B1 | 1 坐標系與函數圖形 | 1-1 數線與絕對值 | vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning | READY | 3 | 2 | 1, 2 |
| 數學B1 | 1 坐標系與函數圖形 | 1-2 平面坐標系與線型函數 | vh_數學B1_CartesianCoordinateSystemEstablishment | READY | 4 | 3 | 1, 2, 1 |
| 數學B1 | 1 坐標系與函數圖形 | 1-2 平面坐標系與線型函數 | vh_數學B1_DistanceBetweenTwoPointsInPlane | READY | 4 | 2 | 1, 3 |
| 數學B1 | 1 坐標系與函數圖形 | 1-2 平面坐標系與線型函數 | vh_數學B1_MidpointCoordinates | READY | 10 | 6 | 1, 1, 2, 2, 3, 1 |
| 數學B1 | 1 坐標系與函數圖形 | 1-2 平面坐標系與線型函數 | vh_數學B1_DivisionPointCoordinates | READY | 7 | 3 | 1, 5, 1 |
| 數學B1 | 1 坐標系與函數圖形 | 1-2 平面坐標系與線型函數 | vh_數學B1_LinearFunction | READY | 15 | 10 | 1, 2, 2, 1, 1, 2, 3, 1, 1, 1 |
| 數學B1 | 1 坐標系與函數圖形 | 1-3 二次函數 | vh_數學B1_QuadraticFunctionGraph | FALLBACK | 0 | 0 |  |
| 數學B1 | 1 坐標系與函數圖形 | 1-3 二次函數 | vh_數學B1_VertexFormOfQuadraticFunction | FALLBACK | 0 | 0 |  |
| 數學B1 | 1 坐標系與函數圖形 | 1-3 二次函數 | vh_數學B1_CompletingTheSquare | FALLBACK | 0 | 0 |  |
| 數學B1 | 1 坐標系與函數圖形 | 1-3 二次函數 | vh_數學B1_QuadraticFunctionExtremum | FALLBACK | 0 | 0 |  |
| 數學B1 | 1 坐標系與函數圖形 | 1-4 一元二次不等式 | vh_數學B1_QuadraticInequalityAndFactoring | FALLBACK | 0 | 0 |  |
| 數學B1 | 1 坐標系與函數圖形 | 1-4 一元二次不等式 | vh_數學B1_QuadraticInequalitySolution | FALLBACK | 0 | 0 |  |
| 數學B1 | 2 直線方程式 | 2-1 斜率 | vh_數學B1_SlopeOfALine | READY | 12 | 9 | 1, 2, 1, 2, 1, 1, 2, 1, 1 |
| 數學B1 | 2 直線方程式 | 2-1 斜率 | vh_數學B1_PropertiesOfParallelLines | READY | 4 | 3 | 2, 1, 1 |
| 數學B1 | 2 直線方程式 | 2-1 斜率 | vh_數學B1_PropertiesOfPerpendicularLines | READY | 8 | 5 | 3, 2, 1, 1, 1 |
| 數學B1 | 2 直線方程式 | 2-2 直線方程式 | vh_數學B1_PointSlopeForm | READY | 14 | 1 | 14 |
| 數學B1 | 2 直線方程式 | 2-2 直線方程式 | vh_數學B1_HorizontalAndVerticalLineEquations | READY | 4 | 1 | 4 |
| 數學B1 | 2 直線方程式 | 2-2 直線方程式 | vh_數學B1_SlopeInterceptForm | READY | 5 | 3 | 3, 1, 1 |
| 數學B1 | 2 直線方程式 | 2-2 直線方程式 | vh_數學B1_InterceptForm | READY | 7 | 5 | 3, 1, 1, 1, 1 |
| 數學B1 | 2 直線方程式 | 2-3 直線的一般式與點到直線的距離 | vh_數學B1_GeneralFormOfLinearEquation | READY | 17 | 11 | 1, 1, 3, 5, 1, 1, 1, 1, 1, 1, 1 |
| 數學B1 | 2 直線方程式 | 2-3 直線的一般式與點到直線的距離 | vh_數學B1_DistanceBetweenPointAndLine | READY | 7 | 4 | 2, 1, 3, 1 |
| 數學B1 | 2 直線方程式 | 2-3 直線的一般式與點到直線的距離 | vh_數學B1_DistanceBetweenTwoParallelLines | READY | 11 | 4 | 1, 5, 1, 4 |
| 數學B1 | 3 式的運算 | 3-1 多項式的基本概念與四則運算 | vh_數學B1_PolynomialBasicConcepts | READY | 7 | 4 | 1, 1, 3, 2 |
| 數學B1 | 3 式的運算 | 3-1 多項式的基本概念與四則運算 | vh_數學B1_PolynomialArithmeticOperations | READY | 22 | 7 | 3, 6, 2, 4, 3, 1, 3 |
| 數學B1 | 3 式的運算 | 3-1 多項式的基本概念與四則運算 | vh_數學B1_PolynomialEquality | READY | 4 | 1 | 4 |
| 數學B1 | 3 式的運算 | 3-2 除法原理與餘式定理 | vh_數學B1_RemainderTheorem | READY | 20 | 1 | 20 |
| 數學B1 | 3 式的運算 | 3-2 除法原理與餘式定理 | vh_數學B1_FactorTheorem | READY | 17 | 1 | 17 |
| 數學B1 | 3 式的運算 | 3-3 因式分解與分式 | vh_數學B1_PolynomialFactoring | READY | 18 | 1 | 18 |
| 數學B1 | 3 式的運算 | 3-3 因式分解與分式 | vh_數學B1_RationalExpressionArithmeticOperations | READY | 8 | 1 | 8 |
| 數學B1 | 3 式的運算 | 3-3 因式分解與分式 | vh_數學B1_RationalEquation | READY | 14 | 1 | 14 |
| 數學B2 | 第1章 三角函數 | 1-1 角度的基本性質 | vh_數學B2_AngleMeasurementAndConversion | READY | 5 | 1 | 5 |
| 數學B2 | 第1章 三角函數 | 1-1 角度的基本性質 | vh_數學B2_ArcLengthAndAreaOfSector | READY | 7 | 1 | 7 |
| 數學B2 | 第1章 三角函數 | 1-1 角度的基本性質 | vh_數學B2_CoterminalAngles | READY | 8 | 1 | 8 |
| 數學B2 | 第1章 三角函數 | 1-2 銳角三角函數 | vh_數學B2_RatioAndRatioValue | READY | 2 | 1 | 2 |
| 數學B2 | 第1章 三角函數 | 1-2 銳角三角函數 | vh_數學B2_TrigonometricFunctionsOfAcuteAngles | READY | 10 | 4 | 1, 3, 1, 5 |
| 數學B2 | 第1章 三角函數 | 1-2 銳角三角函數 | vh_數學B2_TrigonometricValuesOfSpecialAngles | READY | 6 | 2 | 3, 3 |
| 數學B2 | 第1章 三角函數 | 1-2 銳角三角函數 | vh_數學B2_CalculatingFunctionValuesUsingCalculator | READY | 2 | 1 | 2 |
| 數學B2 | 第1章 三角函數 | 1-2 銳角三角函數 | vh_數學B2_FundamentalTrigonometricIdentities | READY | 10 | 3 | 2, 5, 3 |
| 數學B2 | 第1章 三角函數 | 1-3 任意角的三角函數 | vh_數學B2_SubSection_1_3_1 | READY | 3 | 1 | 3 |
| 數學B2 | 第1章 三角函數 | 1-3 任意角的三角函數 | vh_數學B2_SubSection_1_3_2 | READY | 3 | 1 | 3 |
| 數學B2 | 第1章 三角函數 | 1-3 任意角的三角函數 | vh_數學B2_SubSection_1_3_4 | READY | 7 | 2 | 1, 6 |
| 數學B2 | 第1章 三角函數 | 1-3 任意角的三角函數 | vh_數學B2_SubSection_1_3_5 | READY | 3 | 1 | 3 |
| 數學B2 | 第1章 三角函數 | 1-3 任意角的三角函數 | vh_數學B2_SubSection_1_3_6 | READY | 6 | 2 | 5, 1 |
| 數學B2 | 第1章 三角函數 | 1-3 任意角的三角函數 | vh_數學B2_SubSection_1_3_7 | READY | 7 | 4 | 1, 1, 3, 2 |
| 數學B2 | 第1章 三角函數 | 1-4 正弦、餘弦函數的圖形 | vh_數學B2_SubSection_1_4_3 | READY | 8 | 3 | 4, 2, 2 |
| 數學B2 | 第1章 三角函數 | 1-4 正弦、餘弦函數的圖形 | vh_數學B2_SubSection_1_4_4 | READY | 13 | 9 | 3, 1, 3, 1, 1, 1, 1, 1, 1 |
| 數學B2 | 第2章 三角函數的應用 | 2-1 正弦定理與餘弦定理 | vh_數學B2_SubSection_2_1_1 | READY | 13 | 6 | 1, 3, 4, 3, 1, 1 |
| 數學B2 | 第2章 三角函數的應用 | 2-1 正弦定理與餘弦定理 | vh_數學B2_SubSection_2_1_2 | READY | 12 | 5 | 1, 4, 1, 1, 5 |
| 數學B2 | 第2章 三角函數的應用 | 2-2 三角測量 | vh_數學B2_SubSection_2_2_3 | READY | 14 | 10 | 2, 1, 1, 1, 1, 1, 1, 2, 2, 2 |
| 數學B2 | 第2章 三角函數的應用 | 2-2 三角測量 | vh_數學B2_SubSection_2_2_4 | READY | 8 | 2 | 4, 4 |
| 數學B2 | 第2章 三角函數的應用 | 2-2 三角測量 | vh_數學B2_SubSection_2_2_5 | READY | 3 | 3 | 1, 1, 1 |
| 數學B2 | 第3章 向 量 | 3-1 向量的作圖 | vh_數學B2_SubSection_3_1_1 | READY | 3 | 2 | 2, 1 |
| 數學B2 | 第3章 向 量 | 3-1 向量的作圖 | vh_數學B2_SubSection_3_1_2 | READY | 3 | 1 | 3 |
| 數學B2 | 第3章 向 量 | 3-1 向量的作圖 | vh_數學B2_SubSection_3_1_3 | READY | 7 | 1 | 7 |
| 數學B2 | 第3章 向 量 | 3-1 向量的作圖 | vh_數學B2_SubSection_3_1_4 | READY | 14 | 6 | 1, 1, 7, 1, 3, 1 |
| 數學B2 | 第3章 向 量 | 3-2 向量的坐標表示法 | vh_數學B2_SubSection_3_2_1 | READY | 11 | 6 | 3, 1, 1, 2, 2, 2 |
| 數學B2 | 第3章 向 量 | 3-2 向量的坐標表示法 | vh_數學B2_SubSection_3_2_2 | READY | 15 | 6 | 1, 3, 3, 2, 5, 1 |
| 數學B2 | 第3章 向 量 | 3-2 向量的坐標表示法 | vh_數學B2_SubSection_3_2_3 | READY | 2 | 2 | 1, 1 |
| 數學B2 | 第3章 向 量 | 3-2 向量的坐標表示法 | vh_數學B2_SubSection_3_2_4 | READY | 3 | 2 | 2, 1 |
| 數學B2 | 第3章 向 量 | 3-2 向量的坐標表示法 | vh_數學B2_SubSection_3_2_5 | READY | 4 | 2 | 1, 3 |
| 數學B2 | 第3章 向 量 | 3-2 向量的坐標表示法 | vh_數學B2_SubSection_3_2_6 | READY | 5 | 2 | 4, 1 |
| 數學B2 | 第3章 向 量 | 3-3 向量的內積 | vh_數學B2_SubSection_3_3_1 | READY | 4 | 3 | 1, 2, 1 |
| 數學B2 | 第3章 向 量 | 3-3 向量的內積 | vh_數學B2_SubSection_3_3_2 | READY | 5 | 3 | 1, 1, 3 |
| 數學B2 | 第3章 向 量 | 3-3 向量的內積 | vh_數學B2_SubSection_3_3_3 | READY | 9 | 5 | 2, 4, 1, 1, 1 |
| 數學B2 | 第3章 向 量 | 3-3 向量的內積 | vh_數學B2_SubSection_3_3_4 | READY | 4 | 2 | 1, 3 |
| 數學B2 | 第3章 向 量 | 3-3 向量的內積 | vh_數學B2_SubSection_3_3_5 | READY | 6 | 4 | 1, 3, 1, 1 |
| 數學B2 | 第4章 圓與直線 | 4-1 圓方程式 | vh_數學B2_SubSection_4_1_1 | READY | 16 | 9 | 1, 1, 4, 1, 1, 3, 1, 2, 2 |
| 數學B2 | 第4章 圓與直線 | 4-1 圓方程式 | vh_數學B2_SubSection_4_1_2 | READY | 19 | 10 | 1, 4, 1, 1, 1, 5, 1, 3, 1, 1 |
| 數學B2 | 第4章 圓與直線 | 4-2 圓與直線的關係 | vh_數學B2_SubSection_4_2_1 | READY | 5 | 3 | 3, 1, 1 |
| 數學B2 | 第4章 圓與直線 | 4-2 圓與直線的關係 | vh_數學B2_SubSection_4_2_2 | READY | 17 | 12 | 1, 2, 2, 3, 1, 1, 1, 1, 1, 1, 1, 2 |
| 數學B2 | 第4章 圓與直線 | 4-2 圓與直線的關係 | vh_數學B2_SubSection_4_2_3 | READY | 8 | 5 | 1, 3, 1, 2, 1 |
| 數學B2 | 第4章 圓與直線 | 4-2 圓與直線的關係 | vh_數學B2_SubSection_4_2_4 | READY | 5 | 3 | 1, 3, 1 |
| 數學B3 | 第1章 數列與級數 | 1-1 等差數列與等差級數 | vh_數學B3_SubSection_1_1_1 | READY | 3 | 1 | 3 |
| 數學B3 | 第1章 數列與級數 | 1-1 等差數列與等差級數 | vh_數學B3_SubSection_1_1_2 | READY | 13 | 5 | 1, 1, 3, 4, 4 |
| 數學B3 | 第1章 數列與級數 | 1-1 等差數列與等差級數 | vh_數學B3_SubSection_1_1_3 | READY | 2 | 1 | 2 |
| 數學B3 | 第1章 數列與級數 | 1-1 等差數列與等差級數 | vh_數學B3_SubSection_1_1_4 | READY | 5 | 1 | 5 |
| 數學B3 | 第1章 數列與級數 | 1-1 等差數列與等差級數 | vh_數學B3_SubSection_1_1_5 | READY | 14 | 6 | 1, 1, 2, 3, 6, 1 |
| 數學B3 | 第1章 數列與級數 | 1-2 等比數列與等比級數 | vh_數學B3_SubSection_1_2_1 | READY | 19 | 7 | 6, 1, 1, 6, 1, 1, 3 |
| 數學B3 | 第1章 數列與級數 | 1-2 等比數列與等比級數 | vh_數學B3_SubSection_1_2_2 | READY | 4 | 3 | 1, 1, 2 |
| 數學B3 | 第1章 數列與級數 | 1-2 等比數列與等比級數 | vh_數學B3_SubSection_1_2_3 | READY | 3 | 1 | 3 |
| 數學B3 | 第1章 數列與級數 | 1-2 等比數列與等比級數 | vh_數學B3_SubSection_1_2_4 | READY | 11 | 3 | 1, 3, 7 |
| 數學B3 | 第2章 方程式 | 2-1 一元一次方程式與一元一次不等式 | vh_數學B3_SubSection_2_1_1 | READY | 20 | 9 | 6, 3, 1, 2, 1, 1, 3, 1, 2 |
| 數學B3 | 第2章 方程式 | 2-1 一元一次方程式與一元一次不等式 | vh_數學B3_SubSection_2_1_2 | READY | 11 | 3 | 1, 6, 4 |
| 數學B3 | 第2章 方程式 | 2-2 一元二次方程式 | vh_數學B3_SubSection_2_2_1 | READY | 1 | 1 | 1 |
| 數學B3 | 第2章 方程式 | 2-2 一元二次方程式 | vh_數學B3_SubSection_2_2_2 | READY | 13 | 6 | 3, 5, 2, 1, 1, 1 |
| 數學B3 | 第2章 方程式 | 2-2 一元二次方程式 | vh_數學B3_SubSection_2_2_3 | READY | 9 | 4 | 2, 3, 1, 3 |
| 數學B3 | 第2章 方程式 | 2-2 一元二次方程式 | vh_數學B3_SubSection_2_2_4 | READY | 14 | 3 | 1, 7, 6 |
| 數學B3 | 第3章 二元一次不等式及其應用 | 3-1 二元一次聯立方程組 | vh_數學B3_SubSection_3_1_2 | READY | 18 | 7 | 1, 1, 1, 1, 1, 7, 6 |
| 數學B3 | 第3章 二元一次不等式及其應用 | 3-1 二元一次聯立方程組 | vh_數學B3_SubSection_3_1_3 | READY | 13 | 5 | 3, 3, 1, 1, 5 |
| 數學B3 | 第3章 二元一次不等式及其應用 | 3-2 二元一次不等式 | vh_數學B3_PlainHeading_3_2_2 | READY | 2 | 2 | 1, 1 |
| 數學B3 | 第3章 二元一次不等式及其應用 | 3-2 二元一次不等式 | vh_數學B3_PlainHeading_3_2_3 | READY | 14 | 2 | 11, 3 |
| 數學B3 | 第3章 二元一次不等式及其應用 | 3-2 二元一次不等式 | vh_數學B3_PlainHeading_3_2_4 | READY | 8 | 2 | 4, 4 |
| 數學B3 | 第3章 二元一次不等式及其應用 | 3-3 線性規劃 | vh_數學B3_SubSection_3_3_1 | READY | 15 | 5 | 2, 1, 1, 5, 6 |
| 數學B3 | 第3章 二元一次不等式及其應用 | 3-3 線性規劃 | vh_數學B3_SubSection_3_3_3 | READY | 6 | 1 | 6 |
| 數學B3 | 第3章 二元一次不等式及其應用 | 3-3 線性規劃 | vh_數學B3_SubSection_3_3_4 | READY | 9 | 2 | 2, 7 |
| 數學B3 | 第4章 指數與對數 | 4-1 指數 | vh_數學B3_SubSection_4_1_1 | READY | 5 | 3 | 3, 1, 1 |
| 數學B3 | 第4章 指數與對數 | 4-1 指數 | vh_數學B3_SubSection_4_1_2 | READY | 5 | 3 | 1, 3, 1 |
| 數學B3 | 第4章 指數與對數 | 4-1 指數 | vh_數學B3_SubSection_4_1_3 | READY | 14 | 5 | 1, 5, 3, 3, 2 |
| 數學B3 | 第4章 指數與對數 | 4-2 指數函數及其圖形 | vh_數學B3_SubSection_4_2_1 | READY | 14 | 4 | 4, 2, 3, 5 |
| 數學B3 | 第4章 指數與對數 | 4-2 指數函數及其圖形 | vh_數學B3_SubSection_4_2_2 | READY | 16 | 6 | 5, 1, 5, 3, 1, 1 |
| 數學B3 | 第4章 指數與對數 | 4-3 對數 | vh_數學B3_SubSection_4_3_1 | READY | 4 | 2 | 2, 2 |
| 數學B3 | 第4章 指數與對數 | 4-3 對數 | vh_數學B3_SubSection_4_3_2 | READY | 30 | 10 | 1, 3, 4, 4, 1, 5, 5, 3, 3, 1 |
| 數學B3 | 第4章 指數與對數 | 4-4 對數函數及其圖形 | vh_數學B3_SubSection_4_4_1 | READY | 14 | 4 | 2, 5, 5, 2 |
| 數學B3 | 第4章 指數與對數 | 4-4 對數函數及其圖形 | vh_數學B3_SubSection_4_4_2 | READY | 13 | 6 | 1, 4, 5, 1, 1, 1 |
| 數學B3 | 第4章 指數與對數 | 4-5 常用對數及其應用 | vh_數學B3_SubSection_4_5_1 | READY | 6 | 2 | 1, 5 |
| 數學B3 | 第4章 指數與對數 | 4-5 常用對數及其應用 | vh_數學B3_SubSection_4_5_3 | READY | 25 | 6 | 7, 1, 5, 5, 3, 4 |
| 數學B4 | 1 排列組合 | 1-1 加法原理與乘法原理 | vh_數學B4_AdditionPrinciple | FALLBACK | 0 | 0 |  |
| 數學B4 | 1 排列組合 | 1-1 加法原理與乘法原理 | vh_數學B4_MultiplicationPrinciple | FALLBACK | 0 | 0 |  |
| 數學B4 | 1 排列組合 | 1-1 加法原理與乘法原理 | vh_數學B4_FactorialNotation | FALLBACK | 0 | 0 |  |
| 數學B4 | 1 排列組合 | 1-2 直線排列 | vh_數學B4_PermutationOfNonDistinctObjects | FALLBACK | 0 | 0 |  |
| 數學B4 | 1 排列組合 | 1-2 直線排列 | vh_數學B4_PermutationOfDistinctObjects | FALLBACK | 0 | 0 |  |
| 數學B4 | 1 排列組合 | 1-3 重複排列 | vh_數學B4_RepeatedPermutation | FALLBACK | 0 | 0 |  |
| 數學B4 | 1 排列組合 | 1-3 重複排列 | vh_數學B4_PermutationWithRepetition | FALLBACK | 0 | 0 |  |
| 數學B4 | 1 排列組合 | 1-4 組合 | vh_數學B4_CombinationDefinition | FALLBACK | 0 | 0 |  |
| 數學B4 | 1 排列組合 | 1-4 組合 | vh_數學B4_CombinationApplications | FALLBACK | 0 | 0 |  |
| 數學B4 | 1 排列組合 | 1-4 組合 | vh_數學B4_Combination | FALLBACK | 0 | 0 |  |
| 數學B4 | 1 排列組合 | 1-4 組合 | vh_數學B4_CombinationProperties | FALLBACK | 0 | 0 |  |
| 數學B4 | 1 排列組合 | 1-5 二項式定理 | vh_數學B4_BinomialTheorem | FALLBACK | 0 | 0 |  |
| 數學B4 | 1 排列組合 | 1-5 二項式定理 | vh_數學B4_BinomialCoefficientIdentities | FALLBACK | 0 | 0 |  |
| 數學B4 | 3 統計 | 3-2 統計資料整理 | vh_數學B4_FrequencyDistributionTableConstruction | READY | 4 | 1 | 4 |
| 數學B4 | 3 統計 | 3-2 統計資料整理 | vh_數學B4_HistogramsAndFrequencyPolygons | READY | 4 | 2 | 3, 1 |
| 數學B4 | 3 統計 | 3-2 統計資料整理 | vh_數學B4_StatisticalChartReading | READY | 3 | 3 | 1, 1, 1 |
| 數學B4 | 3 統計 | 3-2 統計資料整理 | vh_數學B4_CumulativeFrequencyTablesAndGraphs | READY | 5 | 3 | 1, 3, 1 |
| 數學B4 | 3 統計 | 3-3 統計量分析 | vh_數學B4_CentralTendencyMeasures | READY | 11 | 4 | 7, 1, 1, 2 |
| 數學B4 | 3 統計 | 3-3 統計量分析 | vh_數學B4_WeightedMean | READY | 3 | 1 | 3 |
| 數學B4 | 3 統計 | 3-3 統計量分析 | vh_數學B4_DispersionMeasures | READY | 5 | 4 | 2, 1, 1, 1 |
| 數學B4 | 3 統計 | 3-3 統計量分析 | vh_數學B4_VarianceAndStandardDeviation | READY | 5 | 2 | 4, 1 |
| 數學B4 | 3 統計 | 3-3 統計量分析 | vh_數學B4_LinearTransformationOfData | READY | 7 | 2 | 1, 6 |
| 數學B4 | 3 統計 | 3-3 統計量分析 | vh_數學B4_NormalDistributionAndEmpiricalRule | READY | 6 | 2 | 1, 5 |
| 數學B4 | 3 統計 | 3-3 統計量分析 | vh_數學B4_OpinionPollInterpretation | READY | 2 | 2 | 1, 1 |

# Progression

- 數學B1 1 坐標系與函數圖形: 數學B1_AbsoluteValue -> 數學B1_AbsoluteValueInequality -> 數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning -> 數學B1_CartesianCoordinateSystemEstablishment -> 數學B1_DistanceBetweenTwoPointsInPlane -> 數學B1_MidpointCoordinates -> 數學B1_DivisionPointCoordinates -> 數學B1_LinearFunction -> chapter_completed  | skipped: vh_數學B1_NumberLine(not_ready), outline_vocational_數學B1_11(no_runtime), vh_數學B1_FunctionConcept(no_runtime)
- 數學B1 2 直線方程式: 數學B1_SlopeOfALine -> 數學B1_PropertiesOfParallelLines -> 數學B1_PropertiesOfPerpendicularLines -> 數學B1_PointSlopeForm -> 數學B1_HorizontalAndVerticalLineEquations -> 數學B1_SlopeInterceptForm -> 數學B1_InterceptForm -> 數學B1_GeneralFormOfLinearEquation -> 數學B1_DistanceBetweenPointAndLine -> 數學B1_DistanceBetweenTwoParallelLines -> chapter_completed  | skipped: outline_vocational_數學B1_21(no_runtime), outline_vocational_數學B1_22(no_runtime)
- 數學B1 3 式的運算: 數學B1_PolynomialBasicConcepts -> 數學B1_PolynomialArithmeticOperations -> 數學B1_PolynomialEquality -> 數學B1_RemainderTheorem -> 數學B1_FactorTheorem -> 數學B1_PolynomialFactoring -> 數學B1_RationalExpressionArithmeticOperations -> 數學B1_RationalEquation -> chapter_completed  | skipped: outline_vocational_數學B1_31(no_runtime), outline_vocational_數學B1_32(no_runtime)
- 數學B2 第1章 三角函數: 數學B2_AngleMeasurementAndConversion -> 數學B2_ArcLengthAndAreaOfSector -> 數學B2_CoterminalAngles -> 數學B2_RatioAndRatioValue -> 數學B2_TrigonometricFunctionsOfAcuteAngles -> 數學B2_TrigonometricValuesOfSpecialAngles -> 數學B2_CalculatingFunctionValuesUsingCalculator -> 數學B2_FundamentalTrigonometricIdentities -> 數學B2_SubSection_1_3_1 -> 數學B2_SubSection_1_3_2 -> 數學B2_SubSection_1_3_4 -> 數學B2_SubSection_1_3_5 -> 數學B2_SubSection_1_3_6 -> 數學B2_SubSection_1_3_7 -> 數學B2_SubSection_1_4_3 -> 數學B2_SubSection_1_4_4 -> chapter_completed  | skipped: outline_vocational_數學B2_11(no_runtime), outline_vocational_數學B2_12(no_runtime), vh_數學B2_SubSection_1_4_1(no_runtime), vh_數學B2_SubSection_1_4_2(no_runtime)
- 數學B2 第2章 三角函數的應用: 數學B2_SubSection_2_1_1 -> 數學B2_SubSection_2_1_2 -> 數學B2_SubSection_2_2_3 -> 數學B2_SubSection_2_2_4 -> 數學B2_SubSection_2_2_5 -> chapter_completed  | skipped: outline_vocational_數學B2_21(no_runtime), vh_數學B2_SubSection_2_2_1(no_runtime), vh_數學B2_SubSection_2_2_2(no_runtime)
- 數學B2 第3章 向 量: 數學B2_SubSection_3_1_1 -> 數學B2_SubSection_3_1_2 -> 數學B2_SubSection_3_1_3 -> 數學B2_SubSection_3_1_4 -> 數學B2_SubSection_3_2_1 -> 數學B2_SubSection_3_2_2 -> 數學B2_SubSection_3_2_3 -> 數學B2_SubSection_3_2_4 -> 數學B2_SubSection_3_2_5 -> 數學B2_SubSection_3_2_6 -> 數學B2_SubSection_3_3_1 -> 數學B2_SubSection_3_3_2 -> 數學B2_SubSection_3_3_3 -> 數學B2_SubSection_3_3_4 -> 數學B2_SubSection_3_3_5 -> chapter_completed  | skipped: outline_vocational_數學B2_31(no_runtime), outline_vocational_數學B2_32(no_runtime)
- 數學B2 第4章 圓與直線: 數學B2_SubSection_4_1_1 -> 數學B2_SubSection_4_1_2 -> 數學B2_SubSection_4_2_1 -> 數學B2_SubSection_4_2_2 -> 數學B2_SubSection_4_2_3 -> 數學B2_SubSection_4_2_4 -> chapter_completed  | skipped: outline_vocational_數學B2_41(no_runtime)
- 數學B3 第1章 數列與級數: 數學B3_SubSection_1_1_1 -> 數學B3_SubSection_1_1_2 -> 數學B3_SubSection_1_1_3 -> 數學B3_SubSection_1_1_4 -> 數學B3_SubSection_1_1_5 -> 數學B3_SubSection_1_2_1 -> 數學B3_SubSection_1_2_2 -> 數學B3_SubSection_1_2_3 -> 數學B3_SubSection_1_2_4 -> chapter_completed  | skipped: outline_vocational_數學B3_11(no_runtime)
- 數學B3 第2章 方程式: 數學B3_SubSection_2_1_1 -> 數學B3_SubSection_2_1_2 -> 數學B3_SubSection_2_2_1 -> 數學B3_SubSection_2_2_2 -> 數學B3_SubSection_2_2_3 -> 數學B3_SubSection_2_2_4 -> chapter_completed  | skipped: outline_vocational_數學B3_21(no_runtime)
- 數學B3 第3章 二元一次不等式及其應用: 數學B3_SubSection_3_1_2 -> 數學B3_SubSection_3_1_3 -> 數學B3_PlainHeading_3_2_2 -> 數學B3_PlainHeading_3_2_3 -> 數學B3_PlainHeading_3_2_4 -> 數學B3_SubSection_3_3_1 -> 數學B3_SubSection_3_3_3 -> 數學B3_SubSection_3_3_4 -> chapter_completed  | skipped: outline_vocational_數學B3_31(no_runtime), vh_數學B3_PlainHeading_3_2_1(no_runtime), outline_vocational_數學B3_32(no_runtime), vh_數學B3_SubSection_3_3_2(no_runtime)
- 數學B3 第4章 指數與對數: 數學B3_SubSection_4_1_1 -> 數學B3_SubSection_4_1_2 -> 數學B3_SubSection_4_1_3 -> 數學B3_SubSection_4_2_1 -> 數學B3_SubSection_4_2_2 -> 數學B3_SubSection_4_3_1 -> 數學B3_SubSection_4_3_2 -> 數學B3_SubSection_4_4_1 -> 數學B3_SubSection_4_4_2 -> 數學B3_SubSection_4_5_1 -> 數學B3_SubSection_4_5_3 -> chapter_completed  | skipped: outline_vocational_數學B3_41(no_runtime), outline_vocational_數學B3_42(no_runtime), outline_vocational_數學B3_43(no_runtime), outline_vocational_數學B3_44(no_runtime), vh_數學B3_SubSection_4_5_2(no_runtime)
- 數學B4 1 排列組合: (no READY section) -> chapter_completed
- 數學B4 2 機率: (no READY section) -> chapter_completed
- 數學B4 3 統計: 數學B4_FrequencyDistributionTableConstruction -> 數學B4_HistogramsAndFrequencyPolygons -> 數學B4_StatisticalChartReading -> 數學B4_CumulativeFrequencyTablesAndGraphs -> 數學B4_CentralTendencyMeasures -> 數學B4_WeightedMean -> 數學B4_DispersionMeasures -> 數學B4_VarianceAndStandardDeviation -> 數學B4_LinearTransformationOfData -> 數學B4_NormalDistributionAndEmpiricalRule -> 數學B4_OpinionPollInterpretation -> chapter_completed  | skipped: vh_數學B4_DataOrganizationAndCharts(no_runtime)

# Automated validation

READY sections checked: 113  type pools built: 113  scheduler failures: 0  generated: 1003  generator failures: 0  undeliverable types: 0  self-grade failures: 0  unanswerable types: 0  legacy checked: 19  legacy failures: 0

Generator smoke mirrors get_next_question: up to 5 seeds per candidate, session normalization, delivery gate, then the payload's own correct answer is graded by the formal grader.
