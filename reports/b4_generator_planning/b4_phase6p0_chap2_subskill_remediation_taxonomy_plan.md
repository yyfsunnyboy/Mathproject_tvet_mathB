# B4 Chapter 2 Phase 6P-0：Subskill and Remediation Taxonomy Planning

## 1. Scope and Guardrails

本輪為 **taxonomy planning-only**，目標是建立 Chap2 的 subskill / error-type / remediation taxonomy，作為後續 runtime 精準補救與 APR/mastety dry-run 的規劃基礎。

本輪明確限制：
- 不改 code
- 不改 tests
- 不改 DB
- 不改 mastery / APR / PPO / remediation
- 不新增題型
- 不啟動 implementation

輸出僅本報告：
- `reports/b4_generator_planning/b4_phase6p0_chap2_subskill_remediation_taxonomy_plan.md`

## 2. Why Problem-type Map Alone Is Not Enough

Phase 6O/6P 已把補救從 stage bridge 提升到 problem_type map-first，但仍可能出現補救文不對題，核心原因：
- skill 粒度太大（例如 `ProbabilityOperations` 內含多種不同能力）
- stage 粒度太粗（同 stage 內的錯誤機制差異很大）
- problem_type 只能描述題型，不足以描述「錯在哪裡」

補救應改為依 **subskill / diagnosis_tag / error_type** 決策。例如「基本機率錯」不等於要補條件機率，可能是：
- 樣本空間計數錯
- 有利結果分子分母對應錯
- 補事件規則誤用
- 聯集交集公式錯
- 分數約分或表示轉換錯

因此 v0.2 方向應採：
- problem_type -> subskill decomposition
- error_type -> remediation_subskill -> remediation_problem_type
- stage guard 僅作安全邊界，不作唯一選題依據

## 3. Proposed Subskill Taxonomy

Chap2 建議 subskill taxonomy（最小可行集合）：
- `set_cardinality`
- `inclusion_exclusion_counting`
- `sample_space_size`
- `favorable_outcome_count`
- `classical_probability_ratio`
- `fraction_simplification`
- `dice_coin_case_count`
- `complement_rule`
- `union_intersection_rule`
- `probability_event_algebra`
- `conditional_probability_denominator`
- `conditional_probability_numerator`
- `without_replacement_state_update`
- `independent_multiplication`
- `at_least_one_complement`
- `expectation_weighted_sum`
- `expectation_from_distribution_table`
- `net_gain_subtract_cost`
- `fair_game_fee`
- `negative_value_interpretation`

補充（建議增加，供診斷更穩定）：
- `event_translation_set_to_probability`（集合語句轉機率事件）
- `table_row_column_alignment`（分配表讀值對齊）

## 4. Problem Type → Subskill Map

| problem_type_id | primary_subskills | secondary_subskills | common_error_types | diagnosis_tags_to_emit | notes |
|---|---|---|---|---|---|
| set_operation_count | [set_cardinality] | [event_translation_set_to_probability] | [sample_space_count_error, formula_selection_error] | [stage1, set_cardinality, counting] | 集合基礎計數。 |
| inclusion_exclusion_count | [inclusion_exclusion_counting] | [set_cardinality] | [union_intersection_formula_error, arithmetic_sign_error] | [stage1, inclusion_exclusion, counting] | 常見為 n(A∪B) 與 n(A∩B)關係混淆。 |
| sample_space_count_numeric | [sample_space_size] | [set_cardinality, favorable_outcome_count] | [sample_space_count_error, denominator_scope_error] | [stage1, sample_space, counting] | Stage2/3 的關鍵前置。 |
| classical_probability_fraction | [classical_probability_ratio, favorable_outcome_count] | [sample_space_size, fraction_simplification] | [wrong_denominator, wrong_numerator, fraction_simplification_error] | [stage2, classical_ratio, fraction] | 最常見是分子分母顛倒或未約分。 |
| dice_coin_probability_count | [dice_coin_case_count, classical_probability_ratio] | [sample_space_size, fraction_simplification] | [sample_space_count_error, wrong_numerator, fraction_simplification_error] | [stage2, dice_coin, counting_to_ratio] | 先計數再轉比例。 |
| complement_probability | [complement_rule] | [classical_probability_ratio, fraction_simplification] | [complement_misuse, arithmetic_sign_error] | [stage2, complement, rule] | 1-P(A) 運算與表示錯誤常見。 |
| union_intersection_probability | [union_intersection_rule] | [complement_rule, classical_probability_ratio] | [union_intersection_formula_error, overlap_double_count_error] | [stage2, union_intersection, rule] | P(A∪B)=P(A)+P(B)-P(A∩B)。 |
| event_operation_probability | [probability_event_algebra] | [union_intersection_rule, complement_rule] | [event_algebra_mapping_error, union_intersection_formula_error] | [stage2, event_algebra, transformation] | 事件語句轉換錯會造成文不對題補救。 |
| probability_algebra_mixed | [probability_event_algebra, union_intersection_rule] | [complement_rule, fraction_simplification] | [event_algebra_mapping_error, complement_misuse, fraction_simplification_error] | [stage2, algebra_mixed, multi_step] | 多步驟錯誤來源需拆解診斷。 |
| conditional_probability_basic | [conditional_probability_denominator, conditional_probability_numerator] | [classical_probability_ratio, sample_space_size] | [conditional_denominator_error, wrong_numerator] | [stage3, conditional_basic, numerator_denominator] | 尤其分母 P(B) 定義錯。 |
| without_replacement_conditional_probability | [without_replacement_state_update, conditional_probability_denominator] | [conditional_probability_numerator, sample_space_size] | [without_replacement_state_error, conditional_denominator_error] | [stage3, without_replacement, state_update] | 狀態更新（母體減1）錯誤高頻。 |
| independent_joint_probability | [independent_multiplication] | [classical_probability_ratio, fraction_simplification] | [independence_multiplication_error, independence_assumption_error] | [stage3, independence, multiplication] | P(A∩B)=P(A)P(B) 條件判定錯。 |
| independent_at_least_one_probability | [at_least_one_complement] | [independent_multiplication, complement_rule] | [at_least_one_without_complement, independence_multiplication_error] | [stage3, at_least_one, complement_strategy] | 常誤用直接加法。 |
| expectation_discrete_basic | [expectation_weighted_sum] | [classical_probability_ratio, fraction_simplification] | [expectation_weighted_sum_error, fraction_simplification_error] | [stage4, expectation_basic, weighted_sum] | ΣxP(x) 結構錯最常見。 |
| expectation_from_distribution | [expectation_from_distribution_table, expectation_weighted_sum] | [table_row_column_alignment, fraction_simplification] | [table_probability_reading_error, expectation_weighted_sum_error] | [stage4, distribution_table, weighted_sum] | 讀表錯與乘加順序錯需要分開補救。 |
| expectation_word_problem_profit_fairness | [net_gain_subtract_cost, fair_game_fee] | [expectation_weighted_sum, negative_value_interpretation] | [net_gain_cost_not_subtracted, negative_value_sign_error, expectation_weighted_sum_error] | [stage4, expectation_word, fairness] | 淨收益概念錯比計算錯更常見。 |
| expectation_assessment_numeric | [expectation_weighted_sum] | [expectation_from_distribution_table, negative_value_interpretation] | [expectation_weighted_sum_error, negative_value_sign_error] | [stage4, expectation_numeric, mixed] | 綜合題，需先判別是表讀值錯還是符號錯。 |

## 5. Subskill Prerequisite Graph

| subskill | prerequisites | remediation_subskills | notes |
|---|---|---|---|
| set_cardinality | [] | [set_cardinality, inclusion_exclusion_counting] | Stage1 基礎節點。 |
| inclusion_exclusion_counting | [set_cardinality] | [set_cardinality, inclusion_exclusion_counting] | 與 union/intersection 規則可對映。 |
| sample_space_size | [set_cardinality] | [sample_space_size, set_cardinality] | 後續 ratio/conditional 重要前置。 |
| favorable_outcome_count | [sample_space_size] | [favorable_outcome_count, sample_space_size] | classical ratio 子能力。 |
| classical_probability_ratio | [sample_space_size, favorable_outcome_count] | [classical_probability_ratio, fraction_simplification] | Stage2 主幹。 |
| fraction_simplification | [classical_probability_ratio] | [fraction_simplification, classical_probability_ratio] | 跨 Stage2~4 通用。 |
| dice_coin_case_count | [sample_space_size] | [dice_coin_case_count, classical_probability_ratio] | 計數到比例轉換。 |
| complement_rule | [classical_probability_ratio] | [complement_rule, classical_probability_ratio] | at_least_one 與 event algebra 依賴。 |
| union_intersection_rule | [classical_probability_ratio, complement_rule] | [union_intersection_rule, complement_rule] | Stage2 規則核心。 |
| probability_event_algebra | [union_intersection_rule, complement_rule] | [probability_event_algebra, union_intersection_rule] | 語義轉換與公式映射。 |
| conditional_probability_denominator | [sample_space_size, classical_probability_ratio] | [conditional_probability_denominator, classical_probability_ratio] | P(B) 定義與條件範圍。 |
| conditional_probability_numerator | [favorable_outcome_count, classical_probability_ratio] | [conditional_probability_numerator, favorable_outcome_count] | P(A∩B) 計數/比例。 |
| without_replacement_state_update | [conditional_probability_denominator, sample_space_size] | [without_replacement_state_update, conditional_probability_denominator] | 有放回/無放回切換。 |
| independent_multiplication | [classical_probability_ratio] | [independent_multiplication, classical_probability_ratio] | Stage3 獨立事件主幹。 |
| at_least_one_complement | [complement_rule, independent_multiplication] | [at_least_one_complement, complement_rule] | 1-P(none) 策略。 |
| expectation_weighted_sum | [classical_probability_ratio, fraction_simplification] | [expectation_weighted_sum, classical_probability_ratio] | Stage4 主幹。 |
| expectation_from_distribution_table | [expectation_weighted_sum] | [expectation_from_distribution_table, expectation_weighted_sum] | 讀表與乘加順序。 |
| net_gain_subtract_cost | [expectation_weighted_sum, negative_value_interpretation] | [net_gain_subtract_cost, expectation_weighted_sum] | 文字題轉式子核心。 |
| fair_game_fee | [net_gain_subtract_cost] | [fair_game_fee, net_gain_subtract_cost] | 公平價格判斷。 |
| negative_value_interpretation | [expectation_weighted_sum] | [negative_value_interpretation, net_gain_subtract_cost] | 損失/成本符號。 |
| event_translation_set_to_probability | [set_cardinality, sample_space_size] | [event_translation_set_to_probability, probability_event_algebra] | 集合語句轉機率事件。 |
| table_row_column_alignment | [expectation_from_distribution_table] | [table_row_column_alignment, expectation_from_distribution_table] | 表格讀值軸對齊。 |

## 6. Error Type → Remediation Routing

| error_type | likely_cause_subskill | remediation_subskill | remediation_problem_type_candidates | notes |
|---|---|---|---|---|
| wrong_denominator | classical_probability_ratio / conditional_probability_denominator | sample_space_size -> classical_probability_ratio | [sample_space_count_numeric, classical_probability_fraction, dice_coin_probability_count] | 先回補母體定義。 |
| wrong_numerator | favorable_outcome_count / conditional_probability_numerator | favorable_outcome_count | [classical_probability_fraction, conditional_probability_basic] | 先補有利事件識別。 |
| sample_space_count_error | sample_space_size | sample_space_size | [sample_space_count_numeric, set_operation_count] | Stage1 優先回補。 |
| complement_misuse | complement_rule | complement_rule | [complement_probability, independent_at_least_one_probability] | 避免直接加法錯誤。 |
| union_intersection_formula_error | union_intersection_rule | union_intersection_rule | [union_intersection_probability, event_operation_probability] | 先修公式再做代數混合。 |
| conditional_denominator_error | conditional_probability_denominator | conditional_probability_denominator | [conditional_probability_basic, classical_probability_fraction, sample_space_count_numeric] | P(B) 錯先退 Stage2/1。 |
| without_replacement_state_error | without_replacement_state_update | without_replacement_state_update | [without_replacement_conditional_probability, conditional_probability_basic] | 狀態更新單獨補救。 |
| independence_multiplication_error | independent_multiplication | independent_multiplication | [independent_joint_probability, classical_probability_fraction] | 先確認可乘條件。 |
| at_least_one_without_complement | at_least_one_complement | at_least_one_complement | [independent_at_least_one_probability, complement_probability, independent_joint_probability] | 強制回到 1-P(none)。 |
| expectation_weighted_sum_error | expectation_weighted_sum | expectation_weighted_sum | [expectation_discrete_basic, expectation_from_distribution] | 乘加結構為主。 |
| table_probability_reading_error | expectation_from_distribution_table / table_row_column_alignment | expectation_from_distribution_table | [expectation_from_distribution, expectation_discrete_basic] | 讀表錯先不進文字題。 |
| net_gain_cost_not_subtracted | net_gain_subtract_cost | net_gain_subtract_cost | [expectation_word_problem_profit_fairness, expectation_discrete_basic] | 先分離收益與成本。 |
| negative_value_sign_error | negative_value_interpretation | negative_value_interpretation | [expectation_word_problem_profit_fairness, expectation_assessment_numeric] | 符號意義優先修正。 |
| fraction_simplification_error | fraction_simplification | fraction_simplification | [classical_probability_fraction, dice_coin_probability_count, expectation_discrete_basic] | 跨題型共用錯誤。 |

## 7. Remediation Selection Policy v0.2 Proposal

未來 runtime selection（提案）應改為：
1. `failed_problem_type_id`
2. `diagnosis_tags` / `error_type`
3. `primary_subskill`
4. `prerequisite_subskill`
5. `remediation_problem_type_candidates`
6. `stage-order guard`
7. `stage bridge fallback`（最後手段）

關鍵原則：
- 補救 routing 不應直接用「大 skill 名稱」決策
- 同一 skill 內必須先做 error-type/subskill 分流
- stage guard 是 safety constraint，不是主選題器

## 8. Relation to APR / Mastery

APR/mastety 層次建議：
- APR 應累積到 **subskill / problem_type family**，不是僅 skill
- scoring_policy_version 規劃：
  - `chap2_v0.1_deterministic_only`（現行）
  - `chap2_v0.2_subskill_remediation`（未來）
- v0.2 可新增 `subskill_mastery_preview`（preview-only）
- v0.2 仍不直接寫正式 mastery（先 dry-run）
- handwriting/free-response 未成熟前維持 visibility-only

## 9. Reserved / Future AI-judged Items

以下仍不進 v0.1 / v0.2 deterministic remediation：
- `sample_space_listing`
- `event_set_listing`
- `subset_listing`
- `tree_diagram_listing`

政策維持：
- visibility-only
- 不進 mastery
- 不進 APR
- 不進 fail_streak
- 不做自動扣分
- 待 AI-judged 成熟後，僅可 additive signal 方式接入

## 10. Automated Test Implications

未來 tests 規劃應覆蓋：
- every problem_type has primary_subskills
- every error_type maps to remediation_subskill
- no forward-stage remediation
- Stage2 error never routes to ConditionalProbability / IndependentEvents / Expectation unless diagnosis explicitly belongs to later stage
- reserved problem_type never selected
- subskill map entries match allowed problem_type IDs
- fallback only after map/subskill lookup fails

本輪不新增 tests，只規劃。

## 11. Recommended Next Phase

Option A：
- **Phase 6P-1：Chap2 Subskill Taxonomy Runtime Data Structure**
- 將 taxonomy 落地成 runtime constant/helper
- 不改 APR/mastery
- tests first

Option B：
- **Phase 7A：Next Chapter Planning Package**
- 沿用 Chap2 流程擴到下一章

建議：
- 若優先修補「補救文不對題」，先做 **6P-1**
- 若優先擴教材，做 **7A**

## 12. Final Confirmation

- 是否只新增 planning report：是
- 是否修改 production code：否
- 是否修改 tests：否
- 是否修改 DB：否
- 是否修改 adaptive scoring / mastery / APR / PPO / remediation：否
- 是否新增題型：否
- 是否啟動 implementation：否
- 是否保留 reserved handwriting/free-response：是
