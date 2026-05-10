# B4 Chapter 2 Phase 6O：Prerequisite Remediation Map Planning

## 1. Scope and Guardrails

本輪為 **planning-only**，目標是建立 Chap2 deterministic problem_type 的 prerequisite/remediation map 規劃稿，供後續實作 phase 使用。

明確限制：
- 不改 code
- 不改 tests
- 不改 DB
- 不改 mastery / APR / PPO / remediation
- 不新增題型
- 不啟動 implementation

輸出僅本報告：
- `reports/b4_generator_planning/b4_phase6o_chap2_prerequisite_remediation_map_plan.md`

## 2. Current Remediation Status

Chap2 v0.1 現況（已 closure，accepted with known limitations）：
- 補救為 session-local、rule-based
- 以 stage-based bridge 運作
- 已有 failed_stage lock + strict stage order guard（R/R2）
- 尚未正式接 APR / PPO / AKT routing
- 尚未做 problem_type-level prerequisite/remediation formal map

## 3. Stage Model

Chap2 四階段：
- Stage 1：集合與樣本空間
- Stage 2：基本機率與運算
- Stage 3：條件機率與獨立事件
- Stage 4：數學期望值

補救原則（規劃版）：
- 不得 forward-stage remediation
- 可 same-stage remediation
- 可 earlier-stage prerequisite fallback
- handwriting/free-response reserved 題型不進自動補救

## 4. Problem Type Remediation Map

| stage | skill_id | problem_type_id | direct_prerequisites | remediation_candidates | fallback_stage | scoring_signal_class | notes |
|---|---|---|---|---|---|---|---|
| stage_1_sets_and_sample_space | vh_數學B4_BasicConceptsOfSets | set_operation_count | [] | [set_operation_count, inclusion_exclusion_count] | same_stage | deterministic_checked | Stage1 基礎集合運算；作為 Stage2/3 的前置概念支持。 |
| stage_1_sets_and_sample_space | vh_數學B4_BasicConceptsOfSets | inclusion_exclusion_count | [set_operation_count] | [inclusion_exclusion_count, set_operation_count] | same_stage | deterministic_checked | Stage1 橋接重點題型；可回補集合計數觀念。 |
| stage_1_sets_and_sample_space | vh_數學B4_SampleSpaceAndEvents | sample_space_count_numeric | [set_operation_count] | [sample_space_count_numeric, set_operation_count] | same_stage | deterministic_checked | Stage1 樣本空間數量題；為 classical/conditional 共同前置。 |
| stage_2_basic_probability | vh_數學B4_ProbabilityDefinition | classical_probability_fraction | [sample_space_count_numeric] | [classical_probability_fraction, dice_coin_probability_count, sample_space_count_numeric] | previous_stage | deterministic_checked | Stage2 主幹；不得補到 Stage3/4。 |
| stage_2_basic_probability | vh_數學B4_ProbabilityDefinition | dice_coin_probability_count | [sample_space_count_numeric, classical_probability_fraction] | [dice_coin_probability_count, classical_probability_fraction, sample_space_count_numeric] | previous_stage | deterministic_checked | Stage2 同階補救優先；可回補 Stage1。 |
| stage_2_basic_probability | vh_數學B4_ProbabilityProperties | complement_probability | [classical_probability_fraction] | [complement_probability, classical_probability_fraction, dice_coin_probability_count] | same_stage | deterministic_checked | Stage2 機率補事件核心。 |
| stage_2_basic_probability | vh_數學B4_ProbabilityProperties | union_intersection_probability | [classical_probability_fraction, complement_probability] | [union_intersection_probability, complement_probability, classical_probability_fraction] | same_stage | deterministic_checked | Stage2 並交事件關係。 |
| stage_2_basic_probability | vh_數學B4_ProbabilityOperations | event_operation_probability | [classical_probability_fraction, union_intersection_probability] | [event_operation_probability, union_intersection_probability, complement_probability] | same_stage | deterministic_checked | Stage2 事件運算綜合。 |
| stage_2_basic_probability | vh_數學B4_ProbabilityOperations | probability_algebra_mixed | [complement_probability, union_intersection_probability, event_operation_probability] | [probability_algebra_mixed, event_operation_probability, union_intersection_probability, complement_probability] | same_stage | conservative | Stage2 代數混合題；同階分解補救為主。 |
| stage_3_conditional_independent | vh_數學B4_ConditionalProbability | conditional_probability_basic | [classical_probability_fraction, sample_space_count_numeric] | [conditional_probability_basic, without_replacement_conditional_probability, classical_probability_fraction, sample_space_count_numeric] | previous_stage | deterministic_checked | 符合期望方向；不得補到 Stage4。 |
| stage_3_conditional_independent | vh_數學B4_ConditionalProbability | without_replacement_conditional_probability | [conditional_probability_basic, classical_probability_fraction, sample_space_count_numeric] | [without_replacement_conditional_probability, conditional_probability_basic, classical_probability_fraction] | previous_stage | conservative | 符合期望方向；可退回 Stage2/1 基礎。 |
| stage_3_conditional_independent | vh_數學B4_IndependentEvents | independent_joint_probability | [classical_probability_fraction, probability_multiplication_concept] | [independent_joint_probability, conditional_probability_basic, classical_probability_fraction] | previous_stage | deterministic_checked | 若可用則接 multiplication principle；否則以 probability multiplication concept 替代。 |
| stage_3_conditional_independent | vh_數學B4_IndependentEvents | independent_at_least_one_probability | [complement_probability, independent_joint_probability] | [independent_at_least_one_probability, independent_joint_probability, complement_probability] | previous_stage | conservative | 符合期望方向；常見錯誤可先回補 complement。 |
| stage_4_expectation | vh_數學B4_MathematicalExpectationDefinition | expectation_discrete_basic | [classical_probability_fraction] | [expectation_discrete_basic, expectation_from_distribution, classical_probability_fraction] | previous_stage | deterministic_checked | Stage4 基礎期望值。 |
| stage_4_expectation | vh_數學B4_MathematicalExpectationDefinition | expectation_from_distribution | [expectation_discrete_basic, classical_probability_fraction] | [expectation_from_distribution, expectation_discrete_basic, classical_probability_fraction] | previous_stage | deterministic_checked | Stage4 表格分配題；可回補 Stage2 基礎機率。 |
| stage_4_expectation | vh_數學B4_ApplicationsOfExpectation | expectation_word_problem_profit_fairness | [expectation_discrete_basic, expectation_from_distribution, classical_probability_fraction] | [expectation_word_problem_profit_fairness, expectation_from_distribution, expectation_discrete_basic, classical_probability_fraction] | previous_stage | conservative | 符合期望方向；應保留 Stage4 同階回補再退 Stage2。 |
| stage_4_expectation | vh_數學B4_MathematicalExpectation | expectation_assessment_numeric | [expectation_discrete_basic, expectation_from_distribution] | [expectation_assessment_numeric, expectation_from_distribution, expectation_discrete_basic, classical_probability_fraction] | previous_stage | conservative | 符合期望方向；可回補 Stage4 基礎與 Stage2 機率底層。 |

## 5. Example Map Expectations

本規劃已對齊下列方向：
- `conditional_probability_basic` prerequisites：`classical_probability_fraction`, `sample_space_count_numeric`
- `without_replacement_conditional_probability` prerequisites：`conditional_probability_basic`, `classical_probability_fraction`, `sample_space_count_numeric`
- `independent_joint_probability` prerequisites：`classical_probability_fraction`, `probability_multiplication_concept`（若有 multiplication principle 可接，否則用機率乘法概念）
- `independent_at_least_one_probability` prerequisites：`complement_probability`, `independent_joint_probability`
- `expectation_word_problem_profit_fairness` prerequisites：`expectation_discrete_basic`, `expectation_from_distribution`, `classical_probability_fraction`
- `expectation_assessment_numeric` prerequisites：`expectation_discrete_basic`, `expectation_from_distribution`
- `probability_algebra_mixed` prerequisites：`complement_probability`, `union_intersection_probability`, `event_operation_probability`

Stage 邊界約束：
- Stage2 題型不得補到 Stage3/4
- Stage3 題型不得補到 Stage4
- Stage4 可回補 Stage2 基本機率與 Stage4 期望值基礎

## 6. Reserved / Future AI-judged Items

下列保留題型仍不進 deterministic remediation：
- `sample_space_listing`
- `event_set_listing`
- `subset_listing`
- `tree_diagram_listing`

政策（維持 v0.1）：
- visibility-only
- 不進 mastery
- 不進 APR
- 不進 fail_streak
- 不做自動扣分
- 未來若 AI-judged 成熟，須以 `scoring_policy_version v0.2` additive signal 接入

## 7. Relation to APR / Scoring Policy

對齊 Phase 6L 規劃：
- `scoring_policy_version = chap2_v0.1_deterministic_only`
- v0.1 只使用 deterministic_checked events
- 本 map 可作為 APR low-skill -> remediation candidate lookup
- 本 map 不直接寫 mastery
- 預計 Phase 6P / 6Q 再做 dry-run / APR-assisted routing
- future handwriting signal 必須採 v0.2 additive，不覆蓋 v0.1

## 8. Automated Test Implications

未來測試規劃應覆蓋：
- no forward-stage remediation
- every problem_type has at least one remediation candidate
- reserved problem_type never selected
- stage_2 never remediates to stage_3 / stage_4
- stage_3 never remediates to stage_4
- stage_4 may fallback to probability basics
- map entries match allowlist problem_type IDs

本輪不新增 tests，只規劃。

## 9. Recommended Next Phase

Option A：
- Phase 6P：Chap2 Remediation Map Runtime Integration
- 把 map 接進 session-local remediation
- 不接正式 APR
- automated tests first

Option B：
- Phase 7A：Next Chapter Planning Package
- 沿用 Chap2 流程擴到下一章

建議：
- 若目標是降低 Chap2 補救文不對題，先做 **6P**
- 若目標是擴教材，做 **7A**

## 10. Final Confirmation

- 是否只新增 planning report：是
- 是否修改 production code：否
- 是否修改 tests：否
- 是否修改 DB：否
- 是否修改 adaptive scoring / mastery / APR / PPO / remediation：否
- 是否新增題型：否
- 是否啟動 implementation：否
- 是否保留 reserved handwriting/free-response：是
