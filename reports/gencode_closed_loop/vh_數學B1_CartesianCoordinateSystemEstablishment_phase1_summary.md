# Gencode Phase1 Summary: vh_數學B1_CartesianCoordinateSystemEstablishment

## SOP Policy Reference

- **SOP Policy Version**: `v0.3`
- **Highest SOP**: `docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.3.md`
- **SOP Preflight Status**: `PASS`
- **SOP Gate Status**: `PASS`
- **Report Contract Status**: `PASS_WITH_WARNINGS`
- **Report Contract Warnings**: ['candidate_problem_type_count_synchronized']
- **Report Contract Violations**: []

- spec_mode: `induce_from_sources`

## Main skill anchor

- skill_ch_name: `直角坐標系的建立`
- expected_task_families: ['coordinate_system_family', 'function_concept_family']
- expected_subskill_candidates: ['evaluate_function_value', 'interpret_function_notation', 'judge_domain_range_basic', 'judge_function_from_mapping', 'judge_function_relation']
- skill_anchor_scope: `default`
- observed_source_family_distribution: {'classify_quadrant_family': 2, 'generic_numeric_family': 1, 'distance_between_two_points_family': 1}
- observed_target_task_distribution: {'classify_quadrant': 1, 'compute_numeric': 1, 'compute_distance_between_two_points': 1, 'choose_correct_statement': 1}
- same_family_subskill_mismatch_examples: 0
- examples_outside_expected_subskills: []
- suggested_action: ``

> 來源題多數與目前技能語意不一致，疑似 skill mapping 錯誤；請先檢查來源題歸屬，不建議進 Phase 2。

## Source alignment

- source_alignment_status: `warn`
- skill_problem_type_alignment_status: `warn`
- alignment_score: `0.0`
- alignment_blockers: []
- alignment_warnings: ['alignment_score_below_recommended_threshold', 'anchor_taxonomy_needs_refinement', 'candidate_family_span_outside_skill_scope', 'mixed_source_families', 'source_skill_scope_locked_demoted_blockers_to_warnings']

| example_id | target_task | task_family | alignment_kind | subskill_match | included | exclude_reason | stem_preview |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4417 | classify_quadrant | classify_quadrant_family | unresolved_within_current_skill | False | True |  | 若點$P\left( a,b \right)$位在第一象限且a < b，則$Q\left( a-b,{{a}^{2}}b |
| 4435 | compute_numeric | generic_numeric_family | unresolved_within_current_skill | False | True |  | 設a、b為實數，且a < b < 0，則點$Q\left( ab,a+b \right)$在第幾象限？ |
| 4509 | compute_distance_between_two_points | distance_between_two_points_family | unresolved_within_current_skill | False | True |  | 設A點為坐標平面上一點，且A點到x軸及y軸之距離分別為3和4，則下列何者可能為A點之坐標？ 　(A)$\left( -4 |
| 4510 | choose_correct_statement | classify_quadrant_family | unresolved_within_current_skill | False | True |  | 已知點$P\left( a-b,ab \right)$在坐標平面的第四象限，則下列敘述何者正確？_x000D_
(A)$ |

## AI semantic classification

- ai_semantic_status: `not_used`

| example_id | ai_task | ai_family | ai_conf | rule_task | rule_family | final_task | final_family | source | conflict | human |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4417 |  |  | 0.0 | classify_quadrant | classify_quadrant_family | classify_quadrant | classify_quadrant_family | rule_first_mode |  | False |
| 4435 |  |  | 0.0 | compute_numeric | generic_numeric_family | compute_numeric | generic_numeric_family | rule_first_mode | rule_first_mode | True |
| 4509 |  |  | 0.0 | compute_distance_between_two_points | distance_between_two_points_family | compute_distance_between_two_points | distance_between_two_points_family | rule_first_mode |  | False |
| 4510 |  |  | 0.0 | choose_correct_statement | classify_quadrant_family | choose_correct_statement | classify_quadrant_family | rule_first_mode |  | False |
## Classification diagnostics (per example)

| id | rule_task/family | AI task/family | conf | source | final task/family | align | excluded |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4417 | classify_quadrant/classify_quadrant_family | / | 0.0 | rule_first_mode | classify_quadrant/classify_quadrant_family | unresolved_within_current_skill |  |
| 4435 | compute_numeric/generic_numeric_family | / | 0.0 | rule_first_mode | compute_numeric/generic_numeric_family | unresolved_within_current_skill |  |
| 4509 | compute_distance_between_two_points/distance_between_two_points_family | / | 0.0 | rule_first_mode | compute_distance_between_two_points/distance_between_two_points_family | unresolved_within_current_skill |  |
| 4510 | choose_correct_statement/classify_quadrant_family | / | 0.0 | rule_first_mode | choose_correct_statement/classify_quadrant_family | unresolved_within_current_skill |  |


## Same-section family distribution

{'classify_quadrant_family': 2, 'generic_numeric_family': 1, 'distance_between_two_points_family': 1}

## Example features

| example_id | answer_type | target_task | has_choices | stem_embeds_choices | math_objects |
| --- | --- | --- | --- | --- | --- |
| 4417 | text_short | classify_quadrant | False | False | coordinate_point, symbolic_condition, two_coordinate_points |
| 4435 | text_short | compute_numeric | False | False | coordinate_point, symbolic_condition |
| 4509 | choice | compute_distance_between_two_points | True | True | axis_distance, coordinate_point, distance_formula, segment_length, three_coordinate_points, triangle, two_coordinate_points |
| 4510 | choice | choose_correct_statement | True | True | coordinate_point, three_coordinate_points, triangle, two_coordinate_points |

## Induction clusters

### Cluster 1
- answer_type: `short_answer`
- source_example_ids: [4417]
- grouping_reason: split_by_feature_signature
- feature_signature: `['short_answer', 'classify_quadrant', 'short_answer', ('sign_reasoning',), ('symbolic_condition', 'coordinate_point'), 'default']`

### Cluster 2
- answer_type: `short_answer`
- source_example_ids: [4435]
- grouping_reason: split_by_feature_signature
- feature_signature: `['short_answer', 'compute_numeric', 'short_answer', ('sign_reasoning',), ('symbolic_condition', 'coordinate_point'), 'default']`

### Cluster 3
- answer_type: `single_choice`
- source_example_ids: [4509]
- grouping_reason: split_by_feature_signature
- feature_signature: `['single_choice', 'compute_distance_between_two_points', 'single_choice', ('axis_distance_reasoning', 'distance_formula_reasoning'), ('axis_distance', 'coordinate_point'), 'default']`

### Cluster 4
- answer_type: `single_choice`
- source_example_ids: [4510]
- grouping_reason: split_by_feature_signature
- feature_signature: `['single_choice', 'choose_correct_statement', 'single_choice', ('sign_reasoning',), ('coordinate_point', 'three_coordinate_points'), 'default']`


## Candidate problem types

| problem_type_id | display_name | answer_type | source_examples | grouping_reason |
| --- | --- | --- | --- | --- |
| evaluate_function_value_2 | evaluate_function_value / anchor bootstrap | expression | [] | anchor_subskill_bootstrap_zero_source |
| interpret_function_notation_2 | interpret_function_notation / anchor bootstrap | expression | [] | anchor_subskill_bootstrap_zero_source |

## phase1
```json
{
  "ok": true,
  "phase": "phase1",
  "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
  "skill_id_prefix_validated": true,
  "skill_id_prefix_validation_reason": "vocational_high_school_math_core_scope",
  "sop_reference": {
    "sop_policy_version": "v0.3",
    "highest_sop": "docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.3.md",
    "required_sop_files": [
      {
        "path": "docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.3.md",
        "exists": true,
        "readable": true,
        "mojibake_detected": false
      },
      {
        "path": "docs/系統SOP/Gencode_AgentSkillV2整合/AgentSkillV2_ProblemType規格包設計_v0.3.md",
        "exists": true,
        "readable": true,
        "mojibake_detected": false
      },
      {
        "path": "docs/系統SOP/Gencode_AgentSkillV2整合/AnswerContract_EquivalenceType_Gate_v0.3.md",
        "exists": true,
        "readable": true,
        "mojibake_detected": false
      }
    ],
    "sop_preflight_status": "PASS"
  },
  "sop_gate_status": "PASS",
  "sop_gate_violation": false,
  "invalid_skill_level_blockers": [],
  "main_skill_anchor": {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "skill_ch_name": "直角坐標系的建立",
    "skill_en_name": "CartesianCoordinateSystemEstablishment",
    "chapter": "1 坐標系與函數圖形",
    "section": "1-2 平面坐標系與線型函數",
    "normalized_skill_terms": [
      "1 坐標系與函數圖形",
      "2 平面坐標系與線型函數",
      "carte",
      "cartesian",
      "cartesiancoordinatesystemestablishment",
      "coordinate",
      "establishment",
      "hment",
      "iancoordinate",
      "solve_unknown_coordinate_from_two_point_distance",
      "system",
      "tabli",
      "teme",
      "vh",
      "vocational",
      "坐標系與函數圖形",
      "平面坐標系與線型函數",
      "數學b",
      "數學b1",
      "直角坐標系的建立",
      "線型函數"
    ],
    "expected_task_families": [
      "coordinate_system_family",
      "function_concept_family"
    ],
    "expected_math_objects": [],
    "expected_subskill_candidates": [
      "evaluate_function_value",
      "interpret_function_notation",
      "judge_domain_range_basic",
      "judge_function_from_mapping",
      "judge_function_relation"
    ],
    "skill_anchor_scope": "default",
    "fallback_subskill": {
      "subskill_id": "same_as_main_skill",
      "subskill_name": "直角坐標系的建立",
      "subskill_scope": "fallback",
      "display_note": "此子技能為 fallback，用於收納未細分或綜合題"
    },
    "source_belongs_to_current_skill_by_default": true,
    "source_skill_scope_locked": true,
    "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "classification_scope": "within_current_skill",
    "skill_mapping_authority": "textbook_examples.skill_id",
    "anchor_authority": "skill_id_derived_no_cross_family_pollution",
    "classification_mandate": "【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\n【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\nTrusted skill anchor (do not override):\n- skill_id: vh_數學B1_CartesianCoordinateSystemEstablishment\n- skill_ch_name: 直角坐標系的建立\n- skill_en_name: CartesianCoordinateSystemEstablishment\n- expected_task_families: ['coordinate_system_family', 'function_concept_family']\n- expected_subskill_candidates: ['evaluate_function_value', 'interpret_function_notation', 'judge_domain_range_basic', 'judge_function_from_mapping', 'judge_function_relation']\n- skill_anchor_scope: default\n- source_skill_scope_locked: True\n"
  },
  "source_example_count": 4,
  "source_alignment_status": "warn",
  "skill_problem_type_alignment_status": "warn",
  "alignment_score": 0.0,
  "alignment_warnings": [
    "alignment_score_below_recommended_threshold",
    "anchor_taxonomy_needs_refinement",
    "candidate_family_span_outside_skill_scope",
    "mixed_source_families",
    "source_skill_scope_locked_demoted_blockers_to_warnings"
  ],
  "alignment_blockers": [],
  "semantic_alignment": {
    "main_skill_anchor": {
      "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
      "skill_ch_name": "直角坐標系的建立",
      "skill_en_name": "CartesianCoordinateSystemEstablishment",
      "chapter": "1 坐標系與函數圖形",
      "section": "1-2 平面坐標系與線型函數",
      "normalized_skill_terms": [
        "1 坐標系與函數圖形",
        "2 平面坐標系與線型函數",
        "carte",
        "cartesian",
        "cartesiancoordinatesystemestablishment",
        "coordinate",
        "establishment",
        "hment",
        "iancoordinate",
        "solve_unknown_coordinate_from_two_point_distance",
        "system",
        "tabli",
        "teme",
        "vh",
        "vocational",
        "坐標系與函數圖形",
        "平面坐標系與線型函數",
        "數學b",
        "數學b1",
        "直角坐標系的建立",
        "線型函數"
      ],
      "expected_task_families": [
        "coordinate_system_family",
        "function_concept_family"
      ],
      "expected_math_objects": [],
      "expected_subskill_candidates": [
        "evaluate_function_value",
        "interpret_function_notation",
        "judge_domain_range_basic",
        "judge_function_from_mapping",
        "judge_function_relation"
      ],
      "skill_anchor_scope": "default",
      "fallback_subskill": {
        "subskill_id": "same_as_main_skill",
        "subskill_name": "直角坐標系的建立",
        "subskill_scope": "fallback",
        "display_note": "此子技能為 fallback，用於收納未細分或綜合題"
      },
      "source_belongs_to_current_skill_by_default": true,
      "source_skill_scope_locked": true,
      "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
      "classification_scope": "within_current_skill",
      "skill_mapping_authority": "textbook_examples.skill_id",
      "anchor_authority": "skill_id_derived_no_cross_family_pollution",
      "classification_mandate": "【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\n【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\nTrusted skill anchor (do not override):\n- skill_id: vh_數學B1_CartesianCoordinateSystemEstablishment\n- skill_ch_name: 直角坐標系的建立\n- skill_en_name: CartesianCoordinateSystemEstablishment\n- expected_task_families: ['coordinate_system_family', 'function_concept_family']\n- expected_subskill_candidates: ['evaluate_function_value', 'interpret_function_notation', 'judge_domain_range_basic', 'judge_function_from_mapping', 'judge_function_relation']\n- skill_anchor_scope: default\n- source_skill_scope_locked: True\n"
    },
    "ai_semantic_status": "not_used",
    "skill_terms": [
      "1 坐標系與函數圖形",
      "2 平面坐標系與線型函數",
      "carte",
      "cartesian",
      "cartesiancoordinatesystemestablishment",
      "coordinate",
      "establishment",
      "hment",
      "iancoordinate",
      "solve_unknown_coordinate_from_two_point_distance",
      "system",
      "tabli",
      "teme",
      "vh",
      "vocational",
      "坐標系與函數圖形",
      "平面坐標系與線型函數",
      "數學b",
      "數學b1",
      "直角坐標系的建立"
    ],
    "source_terms": [
      "ab",
      "axis_distance",
      "b為實數",
      "choose_correct_statement",
      "classify_quadrant",
      "compute_axis_distance",
      "compute_distance",
      "compute_distance_between_two_points",
      "compute_numeric",
      "coordinate_point",
      "distance_formula",
      "frac",
      "left",
      "right",
      "segment_length",
      "short_answer",
      "single_choice",
      "symbolic_condition",
      "three_coordinate_points",
      "triangle",
      "two_coordinate_points",
      "x000d",
      "且a",
      "且a點到x軸及y軸之距離分別為3和4",
      "位在第一象限且a",
      "位在第幾象限",
      "則下列何者可能為a點之坐標",
      "則下列敘述何者正確",
      "則點",
      "在坐標平面的第四象限",
      "在第一象限",
      "在第三象限",
      "在第二象限",
      "在第四象限",
      "在第幾象限",
      "已知點",
      "若點",
      "設a",
      "設a點為坐標平面上一點"
    ],
    "expected_subskill_candidates": [
      "evaluate_function_value",
      "interpret_function_notation",
      "judge_domain_range_basic",
      "judge_function_from_mapping",
      "judge_function_relation"
    ],
    "observed_target_task_distribution": {
      "classify_quadrant": 1,
      "compute_numeric": 1,
      "compute_distance_between_two_points": 1,
      "choose_correct_statement": 1
    },
    "same_family_subskill_mismatch_examples": [],
    "examples_outside_expected_subskills": [],
    "suggested_action": "",
    "examples_outside_expected_family": [],
    "problem_type_terms": [
      "evaluate",
      "evaluate_function_value",
      "evaluate_function_value / anchor bootstrap",
      "expression",
      "function",
      "function_value_numeric",
      "interpret",
      "interpret_function_notation",
      "interpret_function_notation / anchor bootstrap",
      "linear_function_two_point_choice",
      "notation",
      "value"
    ],
    "expected_task_candidates": [
      "evaluate_function_value",
      "interpret_function_notation",
      "judge_domain_range_basic",
      "judge_function_from_mapping",
      "judge_function_relation"
    ],
    "expected_skill_families": [
      "coordinate_system_family",
      "function_concept_family"
    ],
    "observed_source_family_distribution": {
      "classify_quadrant_family": 2,
      "generic_numeric_family": 1,
      "distance_between_two_points_family": 1
    },
    "source_family_distribution": {
      "classify_quadrant_family": 2,
      "generic_numeric_family": 1,
      "distance_between_two_points_family": 1
    },
    "candidate_problem_type_families": [
      "function_concept_family"
    ],
    "dominant_source_task": "classify_quadrant",
    "dominant_source_task_ratio": 0.25,
    "uniform_core_target_task": "classify_quadrant",
    "uniform_core_target_task_ratio": 0.25,
    "uniform_core_target_task_count": 4,
    "uniform_core_threshold_relaxed": false,
    "dominant_source_family": [
      "classify_quadrant_family"
    ],
    "dominant_source_family_ratio": 0.5,
    "skill_source_score": 0.0,
    "skill_problem_type_score": 0.0,
    "source_problem_type_score": 0.0,
    "per_problem_type_scores": [
      {
        "problem_type_id": "evaluate_function_value_2",
        "target_task": "evaluate_function_value",
        "task_family": "function_concept_family",
        "inferred_tasks": [
          "evaluate_function_value"
        ],
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0,
        "task_consistent_with_skill": true,
        "family_consistent_with_skill": true,
        "answer_contract_supported": true
      },
      {
        "problem_type_id": "interpret_function_notation_2",
        "target_task": "interpret_function_notation",
        "task_family": "function_concept_family",
        "inferred_tasks": [
          "interpret_function_notation"
        ],
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0,
        "task_consistent_with_skill": true,
        "family_consistent_with_skill": true,
        "answer_contract_supported": true
      }
    ],
    "decision": "warn",
    "blockers": [],
    "warnings": [
      "alignment_score_below_recommended_threshold",
      "anchor_taxonomy_needs_refinement",
      "candidate_family_span_outside_skill_scope",
      "mixed_source_families",
      "source_skill_scope_locked_demoted_blockers_to_warnings"
    ],
    "induction_core_example_count": 4,
    "induction_enrichment_example_count": 0,
    "source_skill_scope_locked": true,
    "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "classification_scope": "within_current_skill",
    "skill_mapping_authority": "textbook_examples.skill_id",
    "core_skill_concept": "function_concept",
    "supporting_math_objects": [
      "coordinate_point",
      "distance_formula",
      "segment_length",
      "three_coordinate_points",
      "triangle",
      "two_coordinate_points"
    ],
    "source_quality_reject_examples": []
  },
  "source_family_distribution": {
    "classify_quadrant_family": 2,
    "generic_numeric_family": 1,
    "distance_between_two_points_family": 1
  },
  "candidate_problem_type_families": [
    "function_concept_family"
  ],
  "expected_skill_families": [
    "coordinate_system_family",
    "function_concept_family"
  ],
  "expected_subskill_candidates": [
    "evaluate_function_value",
    "interpret_function_notation",
    "judge_domain_range_basic",
    "judge_function_from_mapping",
    "judge_function_relation"
  ],
  "observed_target_task_distribution": {
    "classify_quadrant": 1,
    "compute_numeric": 1,
    "compute_distance_between_two_points": 1,
    "choose_correct_statement": 1
  },
  "same_family_subskill_mismatch_examples": [],
  "examples_outside_expected_subskills": [],
  "suggested_action": "",
  "requires_human_action": true,
  "semantic_classifications": [
    {
      "example_id": 4417,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_evidence": [],
      "ai_negative_evidence": {},
      "ai_available": false,
      "ai_error": "rule_first_mode",
      "ai_unavailable_reason": "ai_wrapper_error",
      "rule_target_task": "classify_quadrant",
      "rule_task_family": "classify_quadrant_family",
      "rule_confidence": 0.7,
      "final_target_task": "classify_quadrant",
      "final_task_family": "classify_quadrant_family",
      "classifier_source": "rule_first_mode",
      "conflict_reason": "",
      "source_mapping_warning": "expected_family_mismatch",
      "requires_human_action": false,
      "ai_notes": "",
      "target_task": "classify_quadrant",
      "task_family": "classify_quadrant_family",
      "math_objects": [
        "coordinate_point",
        "symbolic_condition",
        "two_coordinate_points"
      ],
      "answer_type": "short_answer",
      "answer_shape": "text_short",
      "source_type": "unknown",
      "example_label": "",
      "practice_label": "",
      "linked_example": "",
      "linked_example_id": null,
      "linked_example_task_family": "",
      "structure_consistency": "not_applicable",
      "sequence_context_used": true,
      "structure_context_used": false,
      "confidence_adjustment_reason": "sequence_context_used",
      "possible_structure_mismatch": false,
      "possible_mixed_source_context": false
    },
    {
      "example_id": 4435,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_evidence": [],
      "ai_negative_evidence": {},
      "ai_available": false,
      "ai_error": "rule_first_mode",
      "ai_unavailable_reason": "ai_wrapper_error",
      "rule_target_task": "compute_numeric",
      "rule_task_family": "generic_numeric_family",
      "rule_confidence": 0.2,
      "final_target_task": "compute_numeric",
      "final_task_family": "generic_numeric_family",
      "classifier_source": "rule_first_mode",
      "conflict_reason": "rule_first_mode",
      "source_mapping_warning": "expected_family_mismatch",
      "requires_human_action": true,
      "ai_notes": "",
      "target_task": "compute_numeric",
      "task_family": "generic_numeric_family",
      "math_objects": [
        "coordinate_point",
        "symbolic_condition"
      ],
      "answer_type": "short_answer",
      "answer_shape": "text_short",
      "source_type": "in_class_practice",
      "example_label": "",
      "practice_label": "隨堂練習1",
      "linked_example": "",
      "linked_example_id": null,
      "linked_example_task_family": "",
      "structure_consistency": "unknown",
      "sequence_context_used": true,
      "structure_context_used": true,
      "confidence_adjustment_reason": "sequence_context_used",
      "possible_structure_mismatch": false,
      "possible_mixed_source_context": false
    },
    {
      "example_id": 4509,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_evidence": [],
      "ai_negative_evidence": {},
      "ai_available": false,
      "ai_error": "rule_first_mode",
      "ai_unavailable_reason": "ai_wrapper_error",
      "rule_target_task": "compute_distance_between_two_points",
      "rule_task_family": "distance_between_two_points_family",
      "rule_confidence": 0.55,
      "final_target_task": "compute_distance_between_two_points",
      "final_task_family": "distance_between_two_points_family",
      "classifier_source": "rule_first_mode",
      "conflict_reason": "",
      "source_mapping_warning": "expected_family_mismatch",
      "requires_human_action": false,
      "ai_notes": "",
      "target_task": "compute_distance_between_two_points",
      "task_family": "distance_between_two_points_family",
      "math_objects": [
        "axis_distance",
        "coordinate_point",
        "distance_formula",
        "segment_length",
        "three_coordinate_points",
        "triangle",
        "two_coordinate_points"
      ],
      "answer_type": "single_choice",
      "answer_shape": "single_choice",
      "source_type": "unknown",
      "example_label": "",
      "practice_label": "",
      "linked_example": "",
      "linked_example_id": null,
      "linked_example_task_family": "",
      "structure_consistency": "not_applicable",
      "sequence_context_used": true,
      "structure_context_used": false,
      "confidence_adjustment_reason": "sequence_context_used",
      "possible_structure_mismatch": false,
      "possible_mixed_source_context": false
    },
    {
      "example_id": 4510,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_evidence": [],
      "ai_negative_evidence": {},
      "ai_available": false,
      "ai_error": "rule_first_mode",
      "ai_unavailable_reason": "ai_wrapper_error",
      "rule_target_task": "choose_correct_statement",
      "rule_task_family": "classify_quadrant_family",
      "rule_confidence": 0.5,
      "final_target_task": "choose_correct_statement",
      "final_task_family": "classify_quadrant_family",
      "classifier_source": "rule_first_mode",
      "conflict_reason": "",
      "source_mapping_warning": "expected_family_mismatch",
      "requires_human_action": false,
      "ai_notes": "",
      "target_task": "choose_correct_statement",
      "task_family": "classify_quadrant_family",
      "math_objects": [
        "coordinate_point",
        "three_coordinate_points",
        "triangle",
        "two_coordinate_points"
      ],
      "answer_type": "single_choice",
      "answer_shape": "single_choice",
      "source_type": "unknown",
      "example_label": "",
      "practice_label": "",
      "linked_example": "",
      "linked_example_id": null,
      "linked_example_task_family": "",
      "structure_consistency": "not_applicable",
      "sequence_context_used": true,
      "structure_context_used": false,
      "confidence_adjustment_reason": "sequence_context_used",
      "possible_structure_mismatch": false,
      "possible_mixed_source_context": false
    }
  ],
  "ai_semantic_status": "not_used",
  "source_type_distribution": {
    "unknown": 3,
    "in_class_practice": 1
  },
  "example_practice_link_map": [],
  "structure_mismatch_examples": [],
  "same_section_family_distribution": {
    "classify_quadrant_family": 2,
    "generic_numeric_family": 1,
    "distance_between_two_points_family": 1
  },
  "source_structure_report": {
    "source_type_distribution": {
      "unknown": 3,
      "in_class_practice": 1
    },
    "example_practice_link_map": [],
    "structure_mismatch_examples": [],
    "same_section_family_distribution": {
      "classify_quadrant_family": 2,
      "generic_numeric_family": 1,
      "distance_between_two_points_family": 1
    }
  },
  "classification_diagnostics": [
    {
      "example_id": 4417,
      "rule_target_task": "classify_quadrant",
      "rule_task_family": "classify_quadrant_family",
      "rule_confidence": 0.7,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_semantic_status": "not_used",
      "ai_available": false,
      "ai_error": "rule_first_mode",
      "ai_unavailable_reason": "ai_wrapper_error",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "classifier_source": "rule_first_mode",
      "classification_decision": "",
      "final_target_task": "classify_quadrant",
      "final_task_family": "classify_quadrant_family",
      "expected_task_families": [
        "coordinate_system_family",
        "function_concept_family"
      ],
      "expected_subskill_candidates": [
        "evaluate_function_value",
        "interpret_function_notation",
        "judge_domain_range_basic",
        "judge_function_from_mapping",
        "judge_function_relation"
      ],
      "structure_context_used": false,
      "sequence_context_used": true,
      "alignment_kind": "unresolved_within_current_skill",
      "exclude_reason": "",
      "included_in_phase1": true,
      "conflict_reason": "",
      "source_mapping_warning": "expected_family_mismatch",
      "skill_anchor_scope": "default",
      "skill_scoped_candidates": [],
      "ai_best_candidate_id": "",
      "selected_subskill": "classify_quadrant",
      "selected_problem_type": "classify_quadrant",
      "candidate_source": "",
      "outsider_candidates": [],
      "selected_generator_contract": {},
      "parameter_schema": {},
      "variable_randomization_notes": []
    },
    {
      "example_id": 4435,
      "rule_target_task": "compute_numeric",
      "rule_task_family": "generic_numeric_family",
      "rule_confidence": 0.2,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_semantic_status": "not_used",
      "ai_available": false,
      "ai_error": "rule_first_mode",
      "ai_unavailable_reason": "ai_wrapper_error",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "classifier_source": "rule_first_mode",
      "classification_decision": "",
      "final_target_task": "compute_numeric",
      "final_task_family": "generic_numeric_family",
      "expected_task_families": [
        "coordinate_system_family",
        "function_concept_family"
      ],
      "expected_subskill_candidates": [
        "evaluate_function_value",
        "interpret_function_notation",
        "judge_domain_range_basic",
        "judge_function_from_mapping",
        "judge_function_relation"
      ],
      "structure_context_used": true,
      "sequence_context_used": true,
      "alignment_kind": "unresolved_within_current_skill",
      "exclude_reason": "",
      "included_in_phase1": true,
      "conflict_reason": "rule_first_mode",
      "source_mapping_warning": "expected_family_mismatch",
      "skill_anchor_scope": "default",
      "skill_scoped_candidates": [],
      "ai_best_candidate_id": "",
      "selected_subskill": "compute_numeric",
      "selected_problem_type": "compute_numeric",
      "candidate_source": "",
      "outsider_candidates": [],
      "selected_generator_contract": {},
      "parameter_schema": {},
      "variable_randomization_notes": []
    },
    {
      "example_id": 4509,
      "rule_target_task": "compute_distance_between_two_points",
      "rule_task_family": "distance_between_two_points_family",
      "rule_confidence": 0.55,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_semantic_status": "not_used",
      "ai_available": false,
      "ai_error": "rule_first_mode",
      "ai_unavailable_reason": "ai_wrapper_error",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "classifier_source": "rule_first_mode",
      "classification_decision": "",
      "final_target_task": "compute_distance_between_two_points",
      "final_task_family": "distance_between_two_points_family",
      "expected_task_families": [
        "coordinate_system_family",
        "function_concept_family"
      ],
      "expected_subskill_candidates": [
        "evaluate_function_value",
        "interpret_function_notation",
        "judge_domain_range_basic",
        "judge_function_from_mapping",
        "judge_function_relation"
      ],
      "structure_context_used": false,
      "sequence_context_used": true,
      "alignment_kind": "unresolved_within_current_skill",
      "exclude_reason": "",
      "included_in_phase1": true,
      "conflict_reason": "",
      "source_mapping_warning": "expected_family_mismatch",
      "skill_anchor_scope": "default",
      "skill_scoped_candidates": [],
      "ai_best_candidate_id": "",
      "selected_subskill": "compute_distance_between_two_points",
      "selected_problem_type": "compute_distance_between_two_points",
      "candidate_source": "",
      "outsider_candidates": [],
      "selected_generator_contract": {},
      "parameter_schema": {},
      "variable_randomization_notes": []
    },
    {
      "example_id": 4510,
      "rule_target_task": "choose_correct_statement",
      "rule_task_family": "classify_quadrant_family",
      "rule_confidence": 0.5,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_semantic_status": "not_used",
      "ai_available": false,
      "ai_error": "rule_first_mode",
      "ai_unavailable_reason": "ai_wrapper_error",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "classifier_source": "rule_first_mode",
      "classification_decision": "",
      "final_target_task": "choose_correct_statement",
      "final_task_family": "classify_quadrant_family",
      "expected_task_families": [
        "coordinate_system_family",
        "function_concept_family"
      ],
      "expected_subskill_candidates": [
        "evaluate_function_value",
        "interpret_function_notation",
        "judge_domain_range_basic",
        "judge_function_from_mapping",
        "judge_function_relation"
      ],
      "structure_context_used": false,
      "sequence_context_used": true,
      "alignment_kind": "unresolved_within_current_skill",
      "exclude_reason": "",
      "included_in_phase1": true,
      "conflict_reason": "",
      "source_mapping_warning": "expected_family_mismatch",
      "skill_anchor_scope": "default",
      "skill_scoped_candidates": [],
      "ai_best_candidate_id": "",
      "selected_subskill": "choose_correct_statement",
      "selected_problem_type": "choose_correct_statement",
      "candidate_source": "",
      "outsider_candidates": [],
      "selected_generator_contract": {},
      "parameter_schema": {},
      "variable_randomization_notes": []
    }
  ],
  "ai_semantic_unavailable_reason": "ai_wrapper_error",
  "excluded_source_examples": [],
  "induction_source_selection": {
    "core_example_count": 4,
    "enrichment_example_count": 0,
    "skipped_enrichment_examples": [],
    "future_ai_judged_candidates": [],
    "contextual_application_sources": [],
    "min_core_examples_for_induction": 2,
    "core_sufficient_for_induction": true
  },
  "skipped_enrichment_examples": [],
  "future_ai_judged_candidates": [],
  "contextual_application_sources": [],
  "clause45_escalation_applied": false,
  "clause45_rescued_example_ids": [],
  "clause45_observed_target_task_distribution": {},
  "clause45_proxy_problem_type_ids": [],
  "expected_family_relaxation_applied": false,
  "expected_family_relaxation_reason": "",
  "expected_family_relaxation_target_task": "",
  "core_example_count": 4,
  "enrichment_example_count": 0,
  "rejected_source_examples": [],
  "source_quality_issues": [],
  "semantic_mismatch_examples": [],
  "suspected_wrong_skill_examples": [],
  "same_family_extension_examples": [],
  "section_scope_subskill_extension_examples": [],
  "same_as_main_skill_examples": [],
  "inherited_from_previous_context_examples": [],
  "low_source_examples": [
    {
      "problem_type_id": "evaluate_function_value_2",
      "matched_example_count": 0
    },
    {
      "problem_type_id": "interpret_function_notation_2",
      "matched_example_count": 0
    }
  ],
  "candidate_only_problem_types": [
    {
      "example_id": 4435,
      "problem_type_id": "short_answer_compute_numeric_short_answer",
      "reason": "runtime_not_supported"
    }
  ],
  "candidate_only_count": 1,
  "same_as_main_skill_count": 0,
  "rule_only_classification_count": 0,
  "hybrid_resolved_count": 0,
  "subskills": [
    "choose_correct_statement",
    "classify_quadrant",
    "compute_distance_between_two_points",
    "compute_numeric",
    "same_as_main_skill"
  ],
  "fallback_subskill_used": true,
  "source_belongs_to_current_skill_by_default_count": 4,
  "source_example_alignment": [
    {
      "example_id": 4417,
      "target_task": "classify_quadrant",
      "task_family": "classify_quadrant_family",
      "alignment_score": 0.0,
      "aligned_with_skill": true,
      "included_in_phase1": true,
      "exclude_reason": "",
      "alignment_kind": "unresolved_within_current_skill",
      "skill_id_match": true,
      "task_family_match": false,
      "subskill_match": false,
      "pass_with_warning": false,
      "requires_human_action": true,
      "induction_tier": "core",
      "included_in_core_induction": true,
      "enrichment_reasons": [],
      "source_quality_issues": [],
      "source_quality_reject": false,
      "candidate_only": false,
      "classification_source": "rule_first_mode",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "induction_eligibility": "eligible",
      "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
      "title_stem_preview": "若點$P\\left( a,b \\right)$位在第一象限且a < b，則$Q\\left( a-b,{{a}^{2}}b \\right)$位在第幾象限？"
    },
    {
      "example_id": 4435,
      "target_task": "compute_numeric",
      "task_family": "generic_numeric_family",
      "alignment_score": 0.0,
      "aligned_with_skill": true,
      "included_in_phase1": true,
      "exclude_reason": "",
      "alignment_kind": "unresolved_within_current_skill",
      "skill_id_match": true,
      "task_family_match": false,
      "subskill_match": false,
      "pass_with_warning": false,
      "requires_human_action": true,
      "induction_tier": "core",
      "included_in_core_induction": true,
      "enrichment_reasons": [],
      "source_quality_issues": [],
      "source_quality_reject": false,
      "candidate_only": false,
      "classification_source": "rule_first_mode",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "induction_eligibility": "eligible",
      "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
      "title_stem_preview": "設a、b為實數，且a < b < 0，則點$Q\\left( ab,a+b \\right)$在第幾象限？"
    },
    {
      "example_id": 4509,
      "target_task": "compute_distance_between_two_points",
      "task_family": "distance_between_two_points_family",
      "alignment_score": 0.0,
      "aligned_with_skill": true,
      "included_in_phase1": true,
      "exclude_reason": "",
      "alignment_kind": "unresolved_within_current_skill",
      "skill_id_match": true,
      "task_family_match": false,
      "subskill_match": false,
      "pass_with_warning": false,
      "requires_human_action": true,
      "induction_tier": "core",
      "included_in_core_induction": true,
      "enrichment_reasons": [],
      "source_quality_issues": [],
      "source_quality_reject": false,
      "candidate_only": false,
      "classification_source": "rule_first_mode",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "induction_eligibility": "eligible",
      "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
      "title_stem_preview": "設A點為坐標平面上一點，且A點到x軸及y軸之距離分別為3和4，則下列何者可能為A點之坐標？ 　(A)$\\left( -4,-3 \\right)$　(B)$\\le"
    },
    {
      "example_id": 4510,
      "target_task": "choose_correct_statement",
      "task_family": "classify_quadrant_family",
      "alignment_score": 0.0,
      "aligned_with_skill": true,
      "included_in_phase1": true,
      "exclude_reason": "",
      "alignment_kind": "unresolved_within_current_skill",
      "skill_id_match": true,
      "task_family_match": false,
      "subskill_match": false,
      "pass_with_warning": false,
      "requires_human_action": true,
      "induction_tier": "core",
      "included_in_core_induction": true,
      "enrichment_reasons": [],
      "source_quality_issues": [],
      "source_quality_reject": false,
      "candidate_only": false,
      "classification_source": "rule_first_mode",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "induction_eligibility": "eligible",
      "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
      "title_stem_preview": "已知點$P\\left( a-b,ab \\right)$在坐標平面的第四象限，則下列敘述何者正確？_x000D_\n(A)$A\\left( -a,b \\right)"
    }
  ],
  "candidate_problem_types": [
    {
      "problem_type_id": "evaluate_function_value_2",
      "proposed_problem_type_id": "evaluate_function_value_2",
      "display_name": "evaluate_function_value / anchor bootstrap",
      "matched_example_ids": [],
      "matched_example_count": 0,
      "unmatched_example_ids": [],
      "representative_example_id": null,
      "structural_features": [
        "factored_expression"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "answer_equivalence": "algebraic_equivalent",
        "equivalence_type": "algebraic_equivalent",
        "checker": "expression_checker",
        "checker_key": "expression_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "expression_checker",
        "checker_selection_reason": "quadratic_factoring_expression",
        "accepted_formats": [
          "(x-5)(x+3)",
          "(2x-1)(x+5)",
          "2(x-1)(3x+2)"
        ],
        "answer_semantics": "algebraic_expression",
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
          ],
          "forbidden_patterns": [
            "\\(A\\)",
            "\\(B\\)",
            "\\(C\\)",
            "\\(D\\)"
          ]
        },
        "dependency_contract": {
          "givens_must_be_used": true,
          "target_answer_must_depend_on_givens": true,
          "variables_in_conditions_must_appear_in_target": false
        },
        "semantic_contract": {
          "reasoning_type": [
            "evaluate_function_value"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
          ]
        },
        "generator_contract": {
          "template_variants": [
            {
              "id": "default",
              "label": "default",
              "stem_pattern": "依題意求解：{stem_hint}。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "seed": {
              "type": "integer",
              "randomize": true
            },
            "difficulty_level": {
              "choices": [
                "level_1",
                "level_2",
                "level_3"
              ],
              "weights": [
                0.4,
                0.4,
                0.2
              ]
            }
          },
          "variation_dimensions": [
            "seed",
            "difficulty_level",
            "context_style"
          ],
          "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {}
          },
          "anti_repetition_rules": {
            "avoid_same_template_consecutive": true,
            "avoid_same_ratio_consecutive": true,
            "avoid_same_point_names_consecutive": true,
            "avoid_same_answer_consecutive": true,
            "recent_history_window": 5,
            "signature_fields": [
              "problem_type_id",
              "template_variant",
              "routing_track",
              "scenario_type",
              "ratio_form",
              "ratio_values",
              "coordinate_pattern",
              "answer"
            ]
          },
          "validity_constraints": [
            "answer derivable from givens"
          ],
          "answer_shape": "numeric",
          "explanation_variants": [
            "stepwise"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "evaluate_function_value"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "template_slots": {
            "stem": "function_value_numeric"
          },
          "problem_type_id": "evaluate_function_value_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "expression"
      },
      "checker_key_proposal": "expression_checker",
      "equivalence_type_proposal": "algebraic_equivalent",
      "answer_shape": "factored_expression",
      "answer_semantics": "algebraic_expression",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "expression_checker",
      "checker_selection_reason": "quadratic_factoring_expression",
      "confidence": "medium",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "alignment_score_below_recommended_threshold",
        "anchor_slot_bootstrap_zero_source",
        "anchor_taxonomy_needs_refinement",
        "candidate_family_span_outside_skill_scope",
        "mixed_source_families",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ],
      "checker_contract_warnings": [],
      "spec_source": "anchor_slot_bootstrap",
      "grouping_reason": "anchor_subskill_bootstrap_zero_source",
      "feature_signature": [
        "anchor_slot_bootstrap",
        "evaluate_function_value"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "evaluate_function_value_2",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "target_task": "evaluate_function_value",
        "task_family": "function_concept_family",
        "display_name": "evaluate_function_value / anchor bootstrap",
        "answer_format_hint": "expression",
        "source_example_ids": [],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "expression",
          "answer_shape": "factored_expression",
          "answer_equivalence": "algebraic_equivalent",
          "equivalence_type": "algebraic_equivalent",
          "checker": "expression_checker",
          "checker_key": "expression_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "expression_checker",
          "checker_selection_reason": "quadratic_factoring_expression",
          "accepted_formats": [
            "(x-5)(x+3)",
            "(2x-1)(x+5)",
            "2(x-1)(3x+2)"
          ],
          "answer_semantics": "algebraic_expression"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
          ],
          "forbidden_patterns": [
            "\\(A\\)",
            "\\(B\\)",
            "\\(C\\)",
            "\\(D\\)"
          ]
        },
        "dependency_contract": {
          "givens_must_be_used": true,
          "target_answer_must_depend_on_givens": true,
          "variables_in_conditions_must_appear_in_target": false
        },
        "semantic_contract": {
          "reasoning_type": [
            "evaluate_function_value"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
          ]
        },
        "generator_contract": {
          "template_variants": [
            {
              "id": "default",
              "label": "default",
              "stem_pattern": "依題意求解：{stem_hint}。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "seed": {
              "type": "integer",
              "randomize": true
            },
            "difficulty_level": {
              "choices": [
                "level_1",
                "level_2",
                "level_3"
              ],
              "weights": [
                0.4,
                0.4,
                0.2
              ]
            }
          },
          "variation_dimensions": [
            "seed",
            "difficulty_level",
            "context_style"
          ],
          "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {}
          },
          "anti_repetition_rules": {
            "avoid_same_template_consecutive": true,
            "avoid_same_ratio_consecutive": true,
            "avoid_same_point_names_consecutive": true,
            "avoid_same_answer_consecutive": true,
            "recent_history_window": 5,
            "signature_fields": [
              "problem_type_id",
              "template_variant",
              "routing_track",
              "scenario_type",
              "ratio_form",
              "ratio_values",
              "coordinate_pattern",
              "answer"
            ]
          },
          "validity_constraints": [
            "answer derivable from givens"
          ],
          "answer_shape": "numeric",
          "explanation_variants": [
            "stepwise"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "evaluate_function_value"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "template_slots": {
            "stem": "function_value_numeric"
          },
          "problem_type_id": "evaluate_function_value_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "anchor_slot_bootstrap",
        "grouping_reason": "anchor_subskill_bootstrap_zero_source",
        "feature_signature": [
          "anchor_slot_bootstrap",
          "evaluate_function_value"
        ],
        "canonical_base_problem_type_id": "evaluate_function_value_2",
        "value_type_prefix": "",
        "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
      },
      "generator_readiness": "runtime_ready",
      "usable_for_phase3": true,
      "template_slot": "function_value_numeric",
      "canonical_base_problem_type_id": "evaluate_function_value_2",
      "value_type_prefix": "",
      "subskill_id": "evaluate_function_value",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0,
        "task_consistent_with_skill": true
      },
      "answer_type": "expression"
    },
    {
      "problem_type_id": "interpret_function_notation_2",
      "proposed_problem_type_id": "interpret_function_notation_2",
      "display_name": "interpret_function_notation / anchor bootstrap",
      "matched_example_ids": [],
      "matched_example_count": 0,
      "unmatched_example_ids": [],
      "representative_example_id": null,
      "structural_features": [
        "factored_expression"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "answer_equivalence": "algebraic_equivalent",
        "equivalence_type": "algebraic_equivalent",
        "checker": "expression_checker",
        "checker_key": "expression_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "expression_checker",
        "checker_selection_reason": "quadratic_factoring_expression",
        "accepted_formats": [
          "(x-5)(x+3)",
          "(2x-1)(x+5)",
          "2(x-1)(3x+2)"
        ],
        "answer_semantics": "algebraic_expression",
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
          ],
          "forbidden_patterns": [
            "\\(A\\)",
            "\\(B\\)",
            "\\(C\\)",
            "\\(D\\)"
          ]
        },
        "dependency_contract": {
          "givens_must_be_used": true,
          "target_answer_must_depend_on_givens": true,
          "variables_in_conditions_must_appear_in_target": false
        },
        "semantic_contract": {
          "reasoning_type": [
            "interpret_function_notation"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
          ]
        },
        "generator_contract": {
          "template_variants": [
            {
              "id": "default",
              "label": "default",
              "stem_pattern": "依題意求解：{stem_hint}。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "seed": {
              "type": "integer",
              "randomize": true
            },
            "difficulty_level": {
              "choices": [
                "level_1",
                "level_2",
                "level_3"
              ],
              "weights": [
                0.4,
                0.4,
                0.2
              ]
            }
          },
          "variation_dimensions": [
            "seed",
            "difficulty_level",
            "context_style"
          ],
          "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {}
          },
          "anti_repetition_rules": {
            "avoid_same_template_consecutive": true,
            "avoid_same_ratio_consecutive": true,
            "avoid_same_point_names_consecutive": true,
            "avoid_same_answer_consecutive": true,
            "recent_history_window": 5,
            "signature_fields": [
              "problem_type_id",
              "template_variant",
              "routing_track",
              "scenario_type",
              "ratio_form",
              "ratio_values",
              "coordinate_pattern",
              "answer"
            ]
          },
          "validity_constraints": [
            "answer derivable from givens"
          ],
          "answer_shape": "numeric",
          "explanation_variants": [
            "stepwise"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "interpret_function_notation"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "template_slots": {
            "stem": "linear_function_two_point_choice"
          },
          "problem_type_id": "interpret_function_notation_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "expression"
      },
      "checker_key_proposal": "expression_checker",
      "equivalence_type_proposal": "algebraic_equivalent",
      "answer_shape": "factored_expression",
      "answer_semantics": "algebraic_expression",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "expression_checker",
      "checker_selection_reason": "quadratic_factoring_expression",
      "confidence": "medium",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "alignment_score_below_recommended_threshold",
        "anchor_slot_bootstrap_zero_source",
        "anchor_taxonomy_needs_refinement",
        "candidate_family_span_outside_skill_scope",
        "mixed_source_families",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ],
      "checker_contract_warnings": [],
      "spec_source": "anchor_slot_bootstrap",
      "grouping_reason": "anchor_subskill_bootstrap_zero_source",
      "feature_signature": [
        "anchor_slot_bootstrap",
        "interpret_function_notation"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "interpret_function_notation_2",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "target_task": "interpret_function_notation",
        "task_family": "function_concept_family",
        "display_name": "interpret_function_notation / anchor bootstrap",
        "answer_format_hint": "expression",
        "source_example_ids": [],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "expression",
          "answer_shape": "factored_expression",
          "answer_equivalence": "algebraic_equivalent",
          "equivalence_type": "algebraic_equivalent",
          "checker": "expression_checker",
          "checker_key": "expression_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "expression_checker",
          "checker_selection_reason": "quadratic_factoring_expression",
          "accepted_formats": [
            "(x-5)(x+3)",
            "(2x-1)(x+5)",
            "2(x-1)(3x+2)"
          ],
          "answer_semantics": "algebraic_expression"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
          ],
          "forbidden_patterns": [
            "\\(A\\)",
            "\\(B\\)",
            "\\(C\\)",
            "\\(D\\)"
          ]
        },
        "dependency_contract": {
          "givens_must_be_used": true,
          "target_answer_must_depend_on_givens": true,
          "variables_in_conditions_must_appear_in_target": false
        },
        "semantic_contract": {
          "reasoning_type": [
            "interpret_function_notation"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
          ]
        },
        "generator_contract": {
          "template_variants": [
            {
              "id": "default",
              "label": "default",
              "stem_pattern": "依題意求解：{stem_hint}。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "seed": {
              "type": "integer",
              "randomize": true
            },
            "difficulty_level": {
              "choices": [
                "level_1",
                "level_2",
                "level_3"
              ],
              "weights": [
                0.4,
                0.4,
                0.2
              ]
            }
          },
          "variation_dimensions": [
            "seed",
            "difficulty_level",
            "context_style"
          ],
          "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {}
          },
          "anti_repetition_rules": {
            "avoid_same_template_consecutive": true,
            "avoid_same_ratio_consecutive": true,
            "avoid_same_point_names_consecutive": true,
            "avoid_same_answer_consecutive": true,
            "recent_history_window": 5,
            "signature_fields": [
              "problem_type_id",
              "template_variant",
              "routing_track",
              "scenario_type",
              "ratio_form",
              "ratio_values",
              "coordinate_pattern",
              "answer"
            ]
          },
          "validity_constraints": [
            "answer derivable from givens"
          ],
          "answer_shape": "numeric",
          "explanation_variants": [
            "stepwise"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "interpret_function_notation"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "template_slots": {
            "stem": "linear_function_two_point_choice"
          },
          "problem_type_id": "interpret_function_notation_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "anchor_slot_bootstrap",
        "grouping_reason": "anchor_subskill_bootstrap_zero_source",
        "feature_signature": [
          "anchor_slot_bootstrap",
          "interpret_function_notation"
        ],
        "canonical_base_problem_type_id": "interpret_function_notation_2",
        "value_type_prefix": "",
        "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
      },
      "generator_readiness": "runtime_ready",
      "usable_for_phase3": true,
      "template_slot": "linear_function_two_point_choice",
      "canonical_base_problem_type_id": "interpret_function_notation_2",
      "value_type_prefix": "",
      "subskill_id": "interpret_function_notation",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0,
        "task_consistent_with_skill": true
      },
      "answer_type": "expression"
    }
  ],
  "answer_contract_summary": {
    "equivalence_type_whitelist": [
      "algebraic_equivalent",
      "choice_label",
      "exact_string",
      "interval_set",
      "linear_equation_equivalent",
      "manual_review_or_ai_judged",
      "multi_part_answer",
      "numeric_exact",
      "ordered_tuple_exact",
      "rational_equivalent",
      "unordered_solution_set",
      "unordered_tuple_equivalent"
    ],
    "observed_problem_type_answer_contracts": {
      "evaluate_function_value_2": {
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "equivalence_type": "algebraic_equivalent",
        "checker_key": "expression_checker",
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "expression"
      },
      "interpret_function_notation_2": {
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "equivalence_type": "algebraic_equivalent",
        "checker_key": "expression_checker",
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "expression"
      }
    },
    "missing_answer_contract_problem_types": [],
    "missing_checker_key_problem_types": [],
    "equivalence_test_required_problem_types": [
      "evaluate_function_value_2",
      "interpret_function_notation_2"
    ],
    "convertible_to_choice_problem_types": [
      "evaluate_function_value_2",
      "interpret_function_notation_2"
    ],
    "manual_review_or_ai_judged_problem_types": []
  },
  "invalid_equivalence_type_problem_types": [],
  "phase1_answer_contract_gate_status": "PASS",
  "per_example_classification": [
    {
      "example_id": 4417,
      "detected_problem_type_id": "short_answer_classify_quadrant_short_answer",
      "example_feature": {
        "source_example_id": 4417,
        "question_text": "若點$P\\left( a,b \\right)$位在第一象限且a < b，則$Q\\left( a-b,{{a}^{2}}b \\right)$位在第幾象限？",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition",
          "two_coordinate_points"
        ],
        "target_task": "classify_quadrant",
        "task_family": "classify_quadrant_family",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "P",
          "Q",
          "a",
          "b"
        ],
        "givens": [
          "P",
          "Q",
          "a",
          "b"
        ],
        "target": "classify_quadrant",
        "classifier_source": "rule_first_mode",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "classify_quadrant",
          "rule_task_family": "classify_quadrant_family",
          "rule_confidence": 0.7,
          "final_target_task": "classify_quadrant",
          "final_task_family": "classify_quadrant_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": false,
          "ai_notes": "",
          "target_task": "classify_quadrant",
          "task_family": "classify_quadrant_family",
          "math_objects": [
            "coordinate_point",
            "symbolic_condition",
            "two_coordinate_points"
          ],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": false,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4417,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 1"
            },
            {
              "example_id": 4435,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4509,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4510,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_first_mode",
      "risk_flags": [
        "expected_family_mismatch"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_evidence": [],
        "ai_negative_evidence": {},
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "rule_target_task": "classify_quadrant",
        "rule_task_family": "classify_quadrant_family",
        "rule_confidence": 0.7,
        "final_target_task": "classify_quadrant",
        "final_task_family": "classify_quadrant_family",
        "classifier_source": "rule_first_mode",
        "conflict_reason": "",
        "source_mapping_warning": "expected_family_mismatch",
        "requires_human_action": false,
        "ai_notes": "",
        "target_task": "classify_quadrant",
        "task_family": "classify_quadrant_family",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition",
          "two_coordinate_points"
        ],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": false,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "classify_quadrant",
      "classification_source": "rule_first_mode",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4435,
      "detected_problem_type_id": "short_answer_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 4435,
        "question_text": "設a、b為實數，且a < b < 0，則點$Q\\left( ab,a+b \\right)$在第幾象限？",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition"
        ],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "Q",
          "a",
          "b"
        ],
        "givens": [
          "Q",
          "a",
          "b"
        ],
        "target": "compute_numeric",
        "classifier_source": "rule_first_mode",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "rule_first_mode",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": true,
          "ai_notes": "",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "symbolic_condition"
          ],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習1",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "unknown",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習1",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": 1,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4417,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 1"
            },
            {
              "example_id": 4435,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4509,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4510,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_first_mode",
      "risk_flags": [
        "expected_family_mismatch",
        "requires_human_action",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_evidence": [],
        "ai_negative_evidence": {},
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "rule_first_mode",
        "conflict_reason": "rule_first_mode",
        "source_mapping_warning": "expected_family_mismatch",
        "requires_human_action": true,
        "ai_notes": "",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition"
        ],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "in_class_practice",
        "example_label": "",
        "practice_label": "隨堂練習1",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "unknown",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "compute_numeric",
      "classification_source": "rule_first_mode",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4509,
      "detected_problem_type_id": "single_choice_compute_distance_between_two_points_single_choice",
      "example_feature": {
        "source_example_id": 4509,
        "question_text": "設A點為坐標平面上一點，且A點到x軸及y軸之距離分別為3和4，則下列何者可能為A點之坐標？ 　(A)$\\left( -4,-3 \\right)$　(B)$\\left( -3,4 \\right)$　_x000D_\n(C)$\\left( -3,-4 \\right)$　(D)$\\left( 3,4 \\right)$。_x000D_",
        "answer": "A",
        "choices": [
          "$\\left( -4,-3 \\right)$",
          "$\\left( -3,4 \\right)$　_x000D_",
          "$\\left( -3,-4 \\right)$",
          "$\\left( 3,4 \\right)$。_x000D_"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "axis_distance",
          "coordinate_point",
          "distance_formula",
          "segment_length",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "reasoning_type": [
          "axis_distance_reasoning",
          "distance_formula_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B",
          "C",
          "D"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D"
        ],
        "target": "compute_distance_between_two_points",
        "classifier_source": "rule_first_mode",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "compute_distance_between_two_points",
          "rule_task_family": "distance_between_two_points_family",
          "rule_confidence": 0.55,
          "final_target_task": "compute_distance_between_two_points",
          "final_task_family": "distance_between_two_points_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": false,
          "ai_notes": "",
          "target_task": "compute_distance_between_two_points",
          "task_family": "distance_between_two_points_family",
          "math_objects": [
            "axis_distance",
            "coordinate_point",
            "distance_formula",
            "segment_length",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "single_choice",
          "answer_shape": "single_choice",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": false,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4417,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 1"
            },
            {
              "example_id": 4435,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4509,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4510,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            }
          ]
        },
        "correct_answer": "A",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker"
      },
      "answer_shape": "single_choice",
      "classification_confidence": "high",
      "classification_reason": "rule_first_mode",
      "risk_flags": [
        "stem_embeds_choices",
        "expected_family_mismatch"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_evidence": [],
        "ai_negative_evidence": {},
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "rule_target_task": "compute_distance_between_two_points",
        "rule_task_family": "distance_between_two_points_family",
        "rule_confidence": 0.55,
        "final_target_task": "compute_distance_between_two_points",
        "final_task_family": "distance_between_two_points_family",
        "classifier_source": "rule_first_mode",
        "conflict_reason": "",
        "source_mapping_warning": "expected_family_mismatch",
        "requires_human_action": false,
        "ai_notes": "",
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "math_objects": [
          "axis_distance",
          "coordinate_point",
          "distance_formula",
          "segment_length",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": false,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "compute_distance_between_two_points",
      "classification_source": "rule_first_mode",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4510,
      "detected_problem_type_id": "single_choice_choose_correct_statement_single_choice",
      "example_feature": {
        "source_example_id": 4510,
        "question_text": "已知點$P\\left( a-b,ab \\right)$在坐標平面的第四象限，則下列敘述何者正確？_x000D_\n(A)$A\\left( -a,b \\right)$在第一象限　(B)$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限_x000D_\n(C)$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限　(D)$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。_x000D_",
        "answer": "A",
        "choices": [
          "$A\\left( -a,b \\right)$在第一象限",
          "$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限_x000D_",
          "$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限",
          "$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。_x000D_"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "choose_correct_statement",
        "task_family": "classify_quadrant_family",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "a",
          "b"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "a",
          "b"
        ],
        "target": "choose_correct_statement",
        "classifier_source": "rule_first_mode",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "choose_correct_statement",
          "rule_task_family": "classify_quadrant_family",
          "rule_confidence": 0.5,
          "final_target_task": "choose_correct_statement",
          "final_task_family": "classify_quadrant_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": false,
          "ai_notes": "",
          "target_task": "choose_correct_statement",
          "task_family": "classify_quadrant_family",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "single_choice",
          "answer_shape": "single_choice",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": false,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4417,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 1"
            },
            {
              "example_id": 4435,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4509,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4510,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            }
          ]
        },
        "correct_answer": "A",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker"
      },
      "answer_shape": "single_choice",
      "classification_confidence": "high",
      "classification_reason": "rule_first_mode",
      "risk_flags": [
        "stem_embeds_choices",
        "expected_family_mismatch"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_evidence": [],
        "ai_negative_evidence": {},
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "rule_target_task": "choose_correct_statement",
        "rule_task_family": "classify_quadrant_family",
        "rule_confidence": 0.5,
        "final_target_task": "choose_correct_statement",
        "final_task_family": "classify_quadrant_family",
        "classifier_source": "rule_first_mode",
        "conflict_reason": "",
        "source_mapping_warning": "expected_family_mismatch",
        "requires_human_action": false,
        "ai_notes": "",
        "target_task": "choose_correct_statement",
        "task_family": "classify_quadrant_family",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": false,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "choose_correct_statement",
      "classification_source": "rule_first_mode",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker",
      "requires_human_action": false
    }
  ],
  "source_classifications": [
    {
      "example_id": 4417,
      "detected_problem_type_id": "short_answer_classify_quadrant_short_answer",
      "example_feature": {
        "source_example_id": 4417,
        "question_text": "若點$P\\left( a,b \\right)$位在第一象限且a < b，則$Q\\left( a-b,{{a}^{2}}b \\right)$位在第幾象限？",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition",
          "two_coordinate_points"
        ],
        "target_task": "classify_quadrant",
        "task_family": "classify_quadrant_family",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "P",
          "Q",
          "a",
          "b"
        ],
        "givens": [
          "P",
          "Q",
          "a",
          "b"
        ],
        "target": "classify_quadrant",
        "classifier_source": "rule_first_mode",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "classify_quadrant",
          "rule_task_family": "classify_quadrant_family",
          "rule_confidence": 0.7,
          "final_target_task": "classify_quadrant",
          "final_task_family": "classify_quadrant_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": false,
          "ai_notes": "",
          "target_task": "classify_quadrant",
          "task_family": "classify_quadrant_family",
          "math_objects": [
            "coordinate_point",
            "symbolic_condition",
            "two_coordinate_points"
          ],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": false,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4417,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 1"
            },
            {
              "example_id": 4435,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4509,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4510,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_first_mode",
      "risk_flags": [
        "expected_family_mismatch"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_evidence": [],
        "ai_negative_evidence": {},
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "rule_target_task": "classify_quadrant",
        "rule_task_family": "classify_quadrant_family",
        "rule_confidence": 0.7,
        "final_target_task": "classify_quadrant",
        "final_task_family": "classify_quadrant_family",
        "classifier_source": "rule_first_mode",
        "conflict_reason": "",
        "source_mapping_warning": "expected_family_mismatch",
        "requires_human_action": false,
        "ai_notes": "",
        "target_task": "classify_quadrant",
        "task_family": "classify_quadrant_family",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition",
          "two_coordinate_points"
        ],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": false,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "classify_quadrant",
      "classification_source": "rule_first_mode",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4435,
      "detected_problem_type_id": "short_answer_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 4435,
        "question_text": "設a、b為實數，且a < b < 0，則點$Q\\left( ab,a+b \\right)$在第幾象限？",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition"
        ],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "Q",
          "a",
          "b"
        ],
        "givens": [
          "Q",
          "a",
          "b"
        ],
        "target": "compute_numeric",
        "classifier_source": "rule_first_mode",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "rule_first_mode",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": true,
          "ai_notes": "",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "symbolic_condition"
          ],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習1",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "unknown",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習1",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": 1,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4417,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 1"
            },
            {
              "example_id": 4435,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4509,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4510,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_first_mode",
      "risk_flags": [
        "expected_family_mismatch",
        "requires_human_action",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_evidence": [],
        "ai_negative_evidence": {},
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "rule_first_mode",
        "conflict_reason": "rule_first_mode",
        "source_mapping_warning": "expected_family_mismatch",
        "requires_human_action": true,
        "ai_notes": "",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition"
        ],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "in_class_practice",
        "example_label": "",
        "practice_label": "隨堂練習1",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "unknown",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "compute_numeric",
      "classification_source": "rule_first_mode",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4509,
      "detected_problem_type_id": "single_choice_compute_distance_between_two_points_single_choice",
      "example_feature": {
        "source_example_id": 4509,
        "question_text": "設A點為坐標平面上一點，且A點到x軸及y軸之距離分別為3和4，則下列何者可能為A點之坐標？ 　(A)$\\left( -4,-3 \\right)$　(B)$\\left( -3,4 \\right)$　_x000D_\n(C)$\\left( -3,-4 \\right)$　(D)$\\left( 3,4 \\right)$。_x000D_",
        "answer": "A",
        "choices": [
          "$\\left( -4,-3 \\right)$",
          "$\\left( -3,4 \\right)$　_x000D_",
          "$\\left( -3,-4 \\right)$",
          "$\\left( 3,4 \\right)$。_x000D_"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "axis_distance",
          "coordinate_point",
          "distance_formula",
          "segment_length",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "reasoning_type": [
          "axis_distance_reasoning",
          "distance_formula_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B",
          "C",
          "D"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D"
        ],
        "target": "compute_distance_between_two_points",
        "classifier_source": "rule_first_mode",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "compute_distance_between_two_points",
          "rule_task_family": "distance_between_two_points_family",
          "rule_confidence": 0.55,
          "final_target_task": "compute_distance_between_two_points",
          "final_task_family": "distance_between_two_points_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": false,
          "ai_notes": "",
          "target_task": "compute_distance_between_two_points",
          "task_family": "distance_between_two_points_family",
          "math_objects": [
            "axis_distance",
            "coordinate_point",
            "distance_formula",
            "segment_length",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "single_choice",
          "answer_shape": "single_choice",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": false,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4417,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 1"
            },
            {
              "example_id": 4435,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4509,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4510,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            }
          ]
        },
        "correct_answer": "A",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker"
      },
      "answer_shape": "single_choice",
      "classification_confidence": "high",
      "classification_reason": "rule_first_mode",
      "risk_flags": [
        "stem_embeds_choices",
        "expected_family_mismatch"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_evidence": [],
        "ai_negative_evidence": {},
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "rule_target_task": "compute_distance_between_two_points",
        "rule_task_family": "distance_between_two_points_family",
        "rule_confidence": 0.55,
        "final_target_task": "compute_distance_between_two_points",
        "final_task_family": "distance_between_two_points_family",
        "classifier_source": "rule_first_mode",
        "conflict_reason": "",
        "source_mapping_warning": "expected_family_mismatch",
        "requires_human_action": false,
        "ai_notes": "",
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "math_objects": [
          "axis_distance",
          "coordinate_point",
          "distance_formula",
          "segment_length",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": false,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "compute_distance_between_two_points",
      "classification_source": "rule_first_mode",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4510,
      "detected_problem_type_id": "single_choice_choose_correct_statement_single_choice",
      "example_feature": {
        "source_example_id": 4510,
        "question_text": "已知點$P\\left( a-b,ab \\right)$在坐標平面的第四象限，則下列敘述何者正確？_x000D_\n(A)$A\\left( -a,b \\right)$在第一象限　(B)$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限_x000D_\n(C)$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限　(D)$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。_x000D_",
        "answer": "A",
        "choices": [
          "$A\\left( -a,b \\right)$在第一象限",
          "$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限_x000D_",
          "$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限",
          "$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。_x000D_"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "choose_correct_statement",
        "task_family": "classify_quadrant_family",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "a",
          "b"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "a",
          "b"
        ],
        "target": "choose_correct_statement",
        "classifier_source": "rule_first_mode",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "choose_correct_statement",
          "rule_task_family": "classify_quadrant_family",
          "rule_confidence": 0.5,
          "final_target_task": "choose_correct_statement",
          "final_task_family": "classify_quadrant_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": false,
          "ai_notes": "",
          "target_task": "choose_correct_statement",
          "task_family": "classify_quadrant_family",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "single_choice",
          "answer_shape": "single_choice",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": false,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4417,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 1"
            },
            {
              "example_id": 4435,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4509,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4510,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            }
          ]
        },
        "correct_answer": "A",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker"
      },
      "answer_shape": "single_choice",
      "classification_confidence": "high",
      "classification_reason": "rule_first_mode",
      "risk_flags": [
        "stem_embeds_choices",
        "expected_family_mismatch"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_evidence": [],
        "ai_negative_evidence": {},
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "rule_target_task": "choose_correct_statement",
        "rule_task_family": "classify_quadrant_family",
        "rule_confidence": 0.5,
        "final_target_task": "choose_correct_statement",
        "final_task_family": "classify_quadrant_family",
        "classifier_source": "rule_first_mode",
        "conflict_reason": "",
        "source_mapping_warning": "expected_family_mismatch",
        "requires_human_action": false,
        "ai_notes": "",
        "target_task": "choose_correct_statement",
        "task_family": "classify_quadrant_family",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": false,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "choose_correct_statement",
      "classification_source": "rule_first_mode",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker",
      "requires_human_action": false
    }
  ],
  "unclassified_examples": [],
  "risk_examples": [
    4417,
    4435,
    4509,
    4510
  ],
  "split_or_merge_recommendation": "induced_from_source_features",
  "classifier_gate": {
    "status": "classifier_auto_pending_promote_with_warning",
    "allowed": true,
    "warnings": [
      "insufficient_examples",
      "alignment_score_below_recommended_threshold",
      "anchor_slot_bootstrap_zero_source",
      "anchor_taxonomy_needs_refinement",
      "candidate_family_span_outside_skill_scope",
      "mixed_source_families",
      "source_skill_scope_locked_demoted_blockers_to_warnings"
    ]
  },
  "generator_draft_gate": {
    "status": "generator_draft_allowed_with_low_source_warning",
    "allowed": true,
    "warnings": [
      "low_source_examples",
      "alignment_score_below_recommended_threshold",
      "anchor_slot_bootstrap_zero_source",
      "anchor_taxonomy_needs_refinement",
      "candidate_family_span_outside_skill_scope",
      "mixed_source_families",
      "source_skill_scope_locked_demoted_blockers_to_warnings"
    ]
  },
  "runtime_ready_gate": {
    "status": "blocked_insufficient_examples",
    "allowed": false,
    "blockers": [
      "runtime_smoke_failed",
      "dynamic_sampling_failed"
    ],
    "warnings": [
      "alignment_score_below_recommended_threshold",
      "anchor_slot_bootstrap_zero_source",
      "anchor_taxonomy_needs_refinement",
      "candidate_family_span_outside_skill_scope",
      "mixed_source_families",
      "source_skill_scope_locked_demoted_blockers_to_warnings"
    ]
  },
  "exception_review_gate": {
    "required": false,
    "reasons": []
  },
  "reports": {
    "phase1_summary_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CartesianCoordinateSystemEstablishment_phase1_summary.json",
    "phase1_summary_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CartesianCoordinateSystemEstablishment_phase1_summary.md",
    "phase1_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CartesianCoordinateSystemEstablishment_phase1_summary.json",
    "phase1_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CartesianCoordinateSystemEstablishment_phase1_summary.md"
  },
  "next_action": "phase2_generate_from_induced_specs",
  "timestamp": "2026-06-29T03:15:14.719590+00:00",
  "dry_run": true,
  "auto_review_summary": {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "main_skill_anchor": {
      "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
      "skill_ch_name": "直角坐標系的建立",
      "skill_en_name": "CartesianCoordinateSystemEstablishment",
      "chapter": "1 坐標系與函數圖形",
      "section": "1-2 平面坐標系與線型函數",
      "normalized_skill_terms": [
        "1 坐標系與函數圖形",
        "2 平面坐標系與線型函數",
        "carte",
        "cartesian",
        "cartesiancoordinatesystemestablishment",
        "coordinate",
        "establishment",
        "hment",
        "iancoordinate",
        "solve_unknown_coordinate_from_two_point_distance",
        "system",
        "tabli",
        "teme",
        "vh",
        "vocational",
        "坐標系與函數圖形",
        "平面坐標系與線型函數",
        "數學b",
        "數學b1",
        "直角坐標系的建立",
        "線型函數"
      ],
      "expected_task_families": [
        "coordinate_system_family",
        "function_concept_family"
      ],
      "expected_math_objects": [],
      "expected_subskill_candidates": [
        "evaluate_function_value",
        "interpret_function_notation",
        "judge_domain_range_basic",
        "judge_function_from_mapping",
        "judge_function_relation"
      ],
      "skill_anchor_scope": "default",
      "fallback_subskill": {
        "subskill_id": "same_as_main_skill",
        "subskill_name": "直角坐標系的建立",
        "subskill_scope": "fallback",
        "display_note": "此子技能為 fallback，用於收納未細分或綜合題"
      },
      "source_belongs_to_current_skill_by_default": true,
      "source_skill_scope_locked": true,
      "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
      "classification_scope": "within_current_skill",
      "skill_mapping_authority": "textbook_examples.skill_id",
      "anchor_authority": "skill_id_derived_no_cross_family_pollution",
      "classification_mandate": "【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\n【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\nTrusted skill anchor (do not override):\n- skill_id: vh_數學B1_CartesianCoordinateSystemEstablishment\n- skill_ch_name: 直角坐標系的建立\n- skill_en_name: CartesianCoordinateSystemEstablishment\n- expected_task_families: ['coordinate_system_family', 'function_concept_family']\n- expected_subskill_candidates: ['evaluate_function_value', 'interpret_function_notation', 'judge_domain_range_basic', 'judge_function_from_mapping', 'judge_function_relation']\n- skill_anchor_scope: default\n- source_skill_scope_locked: True\n"
    },
    "spec_mode": "induce_from_sources",
    "semantic_classifications": [
      {
        "example_id": 4417,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_evidence": [],
        "ai_negative_evidence": {},
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "rule_target_task": "classify_quadrant",
        "rule_task_family": "classify_quadrant_family",
        "rule_confidence": 0.7,
        "final_target_task": "classify_quadrant",
        "final_task_family": "classify_quadrant_family",
        "classifier_source": "rule_first_mode",
        "conflict_reason": "",
        "source_mapping_warning": "expected_family_mismatch",
        "requires_human_action": false,
        "ai_notes": "",
        "target_task": "classify_quadrant",
        "task_family": "classify_quadrant_family",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition",
          "two_coordinate_points"
        ],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": false,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      {
        "example_id": 4435,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_evidence": [],
        "ai_negative_evidence": {},
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "rule_first_mode",
        "conflict_reason": "rule_first_mode",
        "source_mapping_warning": "expected_family_mismatch",
        "requires_human_action": true,
        "ai_notes": "",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition"
        ],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "in_class_practice",
        "example_label": "",
        "practice_label": "隨堂練習1",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "unknown",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      {
        "example_id": 4509,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_evidence": [],
        "ai_negative_evidence": {},
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "rule_target_task": "compute_distance_between_two_points",
        "rule_task_family": "distance_between_two_points_family",
        "rule_confidence": 0.55,
        "final_target_task": "compute_distance_between_two_points",
        "final_task_family": "distance_between_two_points_family",
        "classifier_source": "rule_first_mode",
        "conflict_reason": "",
        "source_mapping_warning": "expected_family_mismatch",
        "requires_human_action": false,
        "ai_notes": "",
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "math_objects": [
          "axis_distance",
          "coordinate_point",
          "distance_formula",
          "segment_length",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": false,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      {
        "example_id": 4510,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_evidence": [],
        "ai_negative_evidence": {},
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "rule_target_task": "choose_correct_statement",
        "rule_task_family": "classify_quadrant_family",
        "rule_confidence": 0.5,
        "final_target_task": "choose_correct_statement",
        "final_task_family": "classify_quadrant_family",
        "classifier_source": "rule_first_mode",
        "conflict_reason": "",
        "source_mapping_warning": "expected_family_mismatch",
        "requires_human_action": false,
        "ai_notes": "",
        "target_task": "choose_correct_statement",
        "task_family": "classify_quadrant_family",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": false,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      }
    ],
    "classification_diagnostics": [
      {
        "example_id": 4417,
        "rule_target_task": "classify_quadrant",
        "rule_task_family": "classify_quadrant_family",
        "rule_confidence": 0.7,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_semantic_status": "not_used",
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "classifier_source": "rule_first_mode",
        "classification_decision": "",
        "final_target_task": "classify_quadrant",
        "final_task_family": "classify_quadrant_family",
        "expected_task_families": [
          "coordinate_system_family",
          "function_concept_family"
        ],
        "expected_subskill_candidates": [
          "evaluate_function_value",
          "interpret_function_notation",
          "judge_domain_range_basic",
          "judge_function_from_mapping",
          "judge_function_relation"
        ],
        "structure_context_used": false,
        "sequence_context_used": true,
        "alignment_kind": "unresolved_within_current_skill",
        "exclude_reason": "",
        "included_in_phase1": true,
        "conflict_reason": "",
        "source_mapping_warning": "expected_family_mismatch",
        "skill_anchor_scope": "default",
        "skill_scoped_candidates": [],
        "ai_best_candidate_id": "",
        "selected_subskill": "classify_quadrant",
        "selected_problem_type": "classify_quadrant",
        "candidate_source": "",
        "outsider_candidates": [],
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": []
      },
      {
        "example_id": 4435,
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_semantic_status": "not_used",
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "classifier_source": "rule_first_mode",
        "classification_decision": "",
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "expected_task_families": [
          "coordinate_system_family",
          "function_concept_family"
        ],
        "expected_subskill_candidates": [
          "evaluate_function_value",
          "interpret_function_notation",
          "judge_domain_range_basic",
          "judge_function_from_mapping",
          "judge_function_relation"
        ],
        "structure_context_used": true,
        "sequence_context_used": true,
        "alignment_kind": "unresolved_within_current_skill",
        "exclude_reason": "",
        "included_in_phase1": true,
        "conflict_reason": "rule_first_mode",
        "source_mapping_warning": "expected_family_mismatch",
        "skill_anchor_scope": "default",
        "skill_scoped_candidates": [],
        "ai_best_candidate_id": "",
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "",
        "outsider_candidates": [],
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": []
      },
      {
        "example_id": 4509,
        "rule_target_task": "compute_distance_between_two_points",
        "rule_task_family": "distance_between_two_points_family",
        "rule_confidence": 0.55,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_semantic_status": "not_used",
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "classifier_source": "rule_first_mode",
        "classification_decision": "",
        "final_target_task": "compute_distance_between_two_points",
        "final_task_family": "distance_between_two_points_family",
        "expected_task_families": [
          "coordinate_system_family",
          "function_concept_family"
        ],
        "expected_subskill_candidates": [
          "evaluate_function_value",
          "interpret_function_notation",
          "judge_domain_range_basic",
          "judge_function_from_mapping",
          "judge_function_relation"
        ],
        "structure_context_used": false,
        "sequence_context_used": true,
        "alignment_kind": "unresolved_within_current_skill",
        "exclude_reason": "",
        "included_in_phase1": true,
        "conflict_reason": "",
        "source_mapping_warning": "expected_family_mismatch",
        "skill_anchor_scope": "default",
        "skill_scoped_candidates": [],
        "ai_best_candidate_id": "",
        "selected_subskill": "compute_distance_between_two_points",
        "selected_problem_type": "compute_distance_between_two_points",
        "candidate_source": "",
        "outsider_candidates": [],
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": []
      },
      {
        "example_id": 4510,
        "rule_target_task": "choose_correct_statement",
        "rule_task_family": "classify_quadrant_family",
        "rule_confidence": 0.5,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_semantic_status": "not_used",
        "ai_available": false,
        "ai_error": "rule_first_mode",
        "ai_unavailable_reason": "ai_wrapper_error",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "classifier_source": "rule_first_mode",
        "classification_decision": "",
        "final_target_task": "choose_correct_statement",
        "final_task_family": "classify_quadrant_family",
        "expected_task_families": [
          "coordinate_system_family",
          "function_concept_family"
        ],
        "expected_subskill_candidates": [
          "evaluate_function_value",
          "interpret_function_notation",
          "judge_domain_range_basic",
          "judge_function_from_mapping",
          "judge_function_relation"
        ],
        "structure_context_used": false,
        "sequence_context_used": true,
        "alignment_kind": "unresolved_within_current_skill",
        "exclude_reason": "",
        "included_in_phase1": true,
        "conflict_reason": "",
        "source_mapping_warning": "expected_family_mismatch",
        "skill_anchor_scope": "default",
        "skill_scoped_candidates": [],
        "ai_best_candidate_id": "",
        "selected_subskill": "choose_correct_statement",
        "selected_problem_type": "choose_correct_statement",
        "candidate_source": "",
        "outsider_candidates": [],
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": []
      }
    ],
    "ai_semantic_status": "not_used",
    "ai_semantic_unavailable_reason": "ai_wrapper_error",
    "ai_invalid_response_reason": "",
    "source_structure_report": {
      "source_type_distribution": {
        "unknown": 3,
        "in_class_practice": 1
      },
      "example_practice_link_map": [],
      "structure_mismatch_examples": [],
      "same_section_family_distribution": {
        "classify_quadrant_family": 2,
        "generic_numeric_family": 1,
        "distance_between_two_points_family": 1
      }
    },
    "source_type_distribution": {
      "unknown": 3,
      "in_class_practice": 1
    },
    "example_practice_link_map": [],
    "structure_mismatch_examples": [],
    "same_section_family_distribution": {
      "classify_quadrant_family": 2,
      "generic_numeric_family": 1,
      "distance_between_two_points_family": 1
    },
    "example_features": [
      {
        "source_example_id": 4417,
        "question_text": "若點$P\\left( a,b \\right)$位在第一象限且a < b，則$Q\\left( a-b,{{a}^{2}}b \\right)$位在第幾象限？",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition",
          "two_coordinate_points"
        ],
        "target_task": "classify_quadrant",
        "task_family": "classify_quadrant_family",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "P",
          "Q",
          "a",
          "b"
        ],
        "givens": [
          "P",
          "Q",
          "a",
          "b"
        ],
        "target": "classify_quadrant",
        "classifier_source": "rule_first_mode",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "classify_quadrant",
          "rule_task_family": "classify_quadrant_family",
          "rule_confidence": 0.7,
          "final_target_task": "classify_quadrant",
          "final_task_family": "classify_quadrant_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": false,
          "ai_notes": "",
          "target_task": "classify_quadrant",
          "task_family": "classify_quadrant_family",
          "math_objects": [
            "coordinate_point",
            "symbolic_condition",
            "two_coordinate_points"
          ],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": false,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4417,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 1"
            },
            {
              "example_id": 4435,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4509,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4510,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker"
      },
      {
        "source_example_id": 4435,
        "question_text": "設a、b為實數，且a < b < 0，則點$Q\\left( ab,a+b \\right)$在第幾象限？",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition"
        ],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "Q",
          "a",
          "b"
        ],
        "givens": [
          "Q",
          "a",
          "b"
        ],
        "target": "compute_numeric",
        "classifier_source": "rule_first_mode",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "rule_first_mode",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": true,
          "ai_notes": "",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "symbolic_condition"
          ],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習1",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "unknown",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習1",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": 1,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4417,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 1"
            },
            {
              "example_id": 4435,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4509,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4510,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker"
      },
      {
        "source_example_id": 4509,
        "question_text": "設A點為坐標平面上一點，且A點到x軸及y軸之距離分別為3和4，則下列何者可能為A點之坐標？ 　(A)$\\left( -4,-3 \\right)$　(B)$\\left( -3,4 \\right)$　_x000D_\n(C)$\\left( -3,-4 \\right)$　(D)$\\left( 3,4 \\right)$。_x000D_",
        "answer": "A",
        "choices": [
          "$\\left( -4,-3 \\right)$",
          "$\\left( -3,4 \\right)$　_x000D_",
          "$\\left( -3,-4 \\right)$",
          "$\\left( 3,4 \\right)$。_x000D_"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "axis_distance",
          "coordinate_point",
          "distance_formula",
          "segment_length",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "reasoning_type": [
          "axis_distance_reasoning",
          "distance_formula_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B",
          "C",
          "D"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D"
        ],
        "target": "compute_distance_between_two_points",
        "classifier_source": "rule_first_mode",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "compute_distance_between_two_points",
          "rule_task_family": "distance_between_two_points_family",
          "rule_confidence": 0.55,
          "final_target_task": "compute_distance_between_two_points",
          "final_task_family": "distance_between_two_points_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": false,
          "ai_notes": "",
          "target_task": "compute_distance_between_two_points",
          "task_family": "distance_between_two_points_family",
          "math_objects": [
            "axis_distance",
            "coordinate_point",
            "distance_formula",
            "segment_length",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "single_choice",
          "answer_shape": "single_choice",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": false,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4417,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 1"
            },
            {
              "example_id": 4435,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4509,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4510,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            }
          ]
        },
        "correct_answer": "A",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker"
      },
      {
        "source_example_id": 4510,
        "question_text": "已知點$P\\left( a-b,ab \\right)$在坐標平面的第四象限，則下列敘述何者正確？_x000D_\n(A)$A\\left( -a,b \\right)$在第一象限　(B)$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限_x000D_\n(C)$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限　(D)$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。_x000D_",
        "answer": "A",
        "choices": [
          "$A\\left( -a,b \\right)$在第一象限",
          "$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限_x000D_",
          "$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限",
          "$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。_x000D_"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "choose_correct_statement",
        "task_family": "classify_quadrant_family",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "a",
          "b"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "a",
          "b"
        ],
        "target": "choose_correct_statement",
        "classifier_source": "rule_first_mode",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "choose_correct_statement",
          "rule_task_family": "classify_quadrant_family",
          "rule_confidence": 0.5,
          "final_target_task": "choose_correct_statement",
          "final_task_family": "classify_quadrant_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": false,
          "ai_notes": "",
          "target_task": "choose_correct_statement",
          "task_family": "classify_quadrant_family",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "single_choice",
          "answer_shape": "single_choice",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": false,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4417,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 1"
            },
            {
              "example_id": 4435,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4509,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4510,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            }
          ]
        },
        "correct_answer": "A",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker"
      }
    ],
    "semantic_alignment": {
      "main_skill_anchor": {
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "skill_ch_name": "直角坐標系的建立",
        "skill_en_name": "CartesianCoordinateSystemEstablishment",
        "chapter": "1 坐標系與函數圖形",
        "section": "1-2 平面坐標系與線型函數",
        "normalized_skill_terms": [
          "1 坐標系與函數圖形",
          "2 平面坐標系與線型函數",
          "carte",
          "cartesian",
          "cartesiancoordinatesystemestablishment",
          "coordinate",
          "establishment",
          "hment",
          "iancoordinate",
          "solve_unknown_coordinate_from_two_point_distance",
          "system",
          "tabli",
          "teme",
          "vh",
          "vocational",
          "坐標系與函數圖形",
          "平面坐標系與線型函數",
          "數學b",
          "數學b1",
          "直角坐標系的建立",
          "線型函數"
        ],
        "expected_task_families": [
          "coordinate_system_family",
          "function_concept_family"
        ],
        "expected_math_objects": [],
        "expected_subskill_candidates": [
          "evaluate_function_value",
          "interpret_function_notation",
          "judge_domain_range_basic",
          "judge_function_from_mapping",
          "judge_function_relation"
        ],
        "skill_anchor_scope": "default",
        "fallback_subskill": {
          "subskill_id": "same_as_main_skill",
          "subskill_name": "直角坐標系的建立",
          "subskill_scope": "fallback",
          "display_note": "此子技能為 fallback，用於收納未細分或綜合題"
        },
        "source_belongs_to_current_skill_by_default": true,
        "source_skill_scope_locked": true,
        "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "classification_scope": "within_current_skill",
        "skill_mapping_authority": "textbook_examples.skill_id",
        "anchor_authority": "skill_id_derived_no_cross_family_pollution",
        "classification_mandate": "【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\n【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\nTrusted skill anchor (do not override):\n- skill_id: vh_數學B1_CartesianCoordinateSystemEstablishment\n- skill_ch_name: 直角坐標系的建立\n- skill_en_name: CartesianCoordinateSystemEstablishment\n- expected_task_families: ['coordinate_system_family', 'function_concept_family']\n- expected_subskill_candidates: ['evaluate_function_value', 'interpret_function_notation', 'judge_domain_range_basic', 'judge_function_from_mapping', 'judge_function_relation']\n- skill_anchor_scope: default\n- source_skill_scope_locked: True\n"
      },
      "ai_semantic_status": "not_used",
      "skill_terms": [
        "1 坐標系與函數圖形",
        "2 平面坐標系與線型函數",
        "carte",
        "cartesian",
        "cartesiancoordinatesystemestablishment",
        "coordinate",
        "establishment",
        "hment",
        "iancoordinate",
        "solve_unknown_coordinate_from_two_point_distance",
        "system",
        "tabli",
        "teme",
        "vh",
        "vocational",
        "坐標系與函數圖形",
        "平面坐標系與線型函數",
        "數學b",
        "數學b1",
        "直角坐標系的建立"
      ],
      "source_terms": [
        "ab",
        "axis_distance",
        "b為實數",
        "choose_correct_statement",
        "classify_quadrant",
        "compute_axis_distance",
        "compute_distance",
        "compute_distance_between_two_points",
        "compute_numeric",
        "coordinate_point",
        "distance_formula",
        "frac",
        "left",
        "right",
        "segment_length",
        "short_answer",
        "single_choice",
        "symbolic_condition",
        "three_coordinate_points",
        "triangle",
        "two_coordinate_points",
        "x000d",
        "且a",
        "且a點到x軸及y軸之距離分別為3和4",
        "位在第一象限且a",
        "位在第幾象限",
        "則下列何者可能為a點之坐標",
        "則下列敘述何者正確",
        "則點",
        "在坐標平面的第四象限",
        "在第一象限",
        "在第三象限",
        "在第二象限",
        "在第四象限",
        "在第幾象限",
        "已知點",
        "若點",
        "設a",
        "設a點為坐標平面上一點"
      ],
      "expected_subskill_candidates": [
        "evaluate_function_value",
        "interpret_function_notation",
        "judge_domain_range_basic",
        "judge_function_from_mapping",
        "judge_function_relation"
      ],
      "observed_target_task_distribution": {
        "classify_quadrant": 1,
        "compute_numeric": 1,
        "compute_distance_between_two_points": 1,
        "choose_correct_statement": 1
      },
      "same_family_subskill_mismatch_examples": [],
      "examples_outside_expected_subskills": [],
      "suggested_action": "",
      "examples_outside_expected_family": [],
      "problem_type_terms": [
        "evaluate",
        "evaluate_function_value",
        "evaluate_function_value / anchor bootstrap",
        "expression",
        "function",
        "function_value_numeric",
        "interpret",
        "interpret_function_notation",
        "interpret_function_notation / anchor bootstrap",
        "linear_function_two_point_choice",
        "notation",
        "value"
      ],
      "expected_task_candidates": [
        "evaluate_function_value",
        "interpret_function_notation",
        "judge_domain_range_basic",
        "judge_function_from_mapping",
        "judge_function_relation"
      ],
      "expected_skill_families": [
        "coordinate_system_family",
        "function_concept_family"
      ],
      "observed_source_family_distribution": {
        "classify_quadrant_family": 2,
        "generic_numeric_family": 1,
        "distance_between_two_points_family": 1
      },
      "source_family_distribution": {
        "classify_quadrant_family": 2,
        "generic_numeric_family": 1,
        "distance_between_two_points_family": 1
      },
      "candidate_problem_type_families": [
        "function_concept_family"
      ],
      "dominant_source_task": "classify_quadrant",
      "dominant_source_task_ratio": 0.25,
      "uniform_core_target_task": "classify_quadrant",
      "uniform_core_target_task_ratio": 0.25,
      "uniform_core_target_task_count": 4,
      "uniform_core_threshold_relaxed": false,
      "dominant_source_family": [
        "classify_quadrant_family"
      ],
      "dominant_source_family_ratio": 0.5,
      "skill_source_score": 0.0,
      "skill_problem_type_score": 0.0,
      "source_problem_type_score": 0.0,
      "per_problem_type_scores": [
        {
          "problem_type_id": "evaluate_function_value_2",
          "target_task": "evaluate_function_value",
          "task_family": "function_concept_family",
          "inferred_tasks": [
            "evaluate_function_value"
          ],
          "skill_problem_type_score": 0.0,
          "source_problem_type_score": 0.0,
          "task_consistent_with_skill": true,
          "family_consistent_with_skill": true,
          "answer_contract_supported": true
        },
        {
          "problem_type_id": "interpret_function_notation_2",
          "target_task": "interpret_function_notation",
          "task_family": "function_concept_family",
          "inferred_tasks": [
            "interpret_function_notation"
          ],
          "skill_problem_type_score": 0.0,
          "source_problem_type_score": 0.0,
          "task_consistent_with_skill": true,
          "family_consistent_with_skill": true,
          "answer_contract_supported": true
        }
      ],
      "decision": "warn",
      "blockers": [],
      "warnings": [
        "alignment_score_below_recommended_threshold",
        "anchor_taxonomy_needs_refinement",
        "candidate_family_span_outside_skill_scope",
        "mixed_source_families",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ],
      "induction_core_example_count": 4,
      "induction_enrichment_example_count": 0,
      "source_skill_scope_locked": true,
      "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
      "classification_scope": "within_current_skill",
      "skill_mapping_authority": "textbook_examples.skill_id",
      "core_skill_concept": "function_concept",
      "supporting_math_objects": [
        "coordinate_point",
        "distance_formula",
        "segment_length",
        "three_coordinate_points",
        "triangle",
        "two_coordinate_points"
      ],
      "source_quality_reject_examples": []
    },
    "source_alignment_status": "warn",
    "skill_problem_type_alignment_status": "warn",
    "alignment_score": 0.0,
    "alignment_warnings": [
      "alignment_score_below_recommended_threshold",
      "anchor_taxonomy_needs_refinement",
      "candidate_family_span_outside_skill_scope",
      "mixed_source_families",
      "source_skill_scope_locked_demoted_blockers_to_warnings"
    ],
    "alignment_blockers": [],
    "source_family_distribution": {
      "classify_quadrant_family": 2,
      "generic_numeric_family": 1,
      "distance_between_two_points_family": 1
    },
    "candidate_problem_type_families": [
      "function_concept_family"
    ],
    "expected_skill_families": [
      "coordinate_system_family",
      "function_concept_family"
    ],
    "expected_subskill_candidates": [
      "evaluate_function_value",
      "interpret_function_notation",
      "judge_domain_range_basic",
      "judge_function_from_mapping",
      "judge_function_relation"
    ],
    "observed_target_task_distribution": {
      "classify_quadrant": 1,
      "compute_numeric": 1,
      "compute_distance_between_two_points": 1,
      "choose_correct_statement": 1
    },
    "same_family_subskill_mismatch_examples": [],
    "examples_outside_expected_subskills": [],
    "suggested_action": "",
    "requires_human_action": true,
    "excluded_source_examples": [],
    "rejected_source_examples": [],
    "source_quality_issues": [],
    "semantic_mismatch_examples": [],
    "suspected_wrong_skill_examples": [],
    "same_family_extension_examples": [],
    "section_scope_subskill_extension_examples": [],
    "same_as_main_skill_examples": [],
    "inherited_from_previous_context_examples": [],
    "low_source_examples": [
      {
        "problem_type_id": "evaluate_function_value_2",
        "matched_example_count": 0
      },
      {
        "problem_type_id": "interpret_function_notation_2",
        "matched_example_count": 0
      }
    ],
    "coverage_floor_suggestions": [],
    "anchor_subskill_bootstrap": {
      "bootstrapped_tasks": [
        "evaluate_function_value",
        "interpret_function_notation"
      ],
      "bootstrapped_count": 2,
      "skipped_tasks": [
        {
          "task": "judge_domain_range_basic",
          "reason": "no_registered_slot_generator"
        },
        {
          "task": "judge_function_from_mapping",
          "reason": "no_registered_slot_generator"
        },
        {
          "task": "judge_function_relation",
          "reason": "no_registered_slot_generator"
        }
      ]
    },
    "candidate_only_problem_types": [
      {
        "example_id": 4435,
        "problem_type_id": "short_answer_compute_numeric_short_answer",
        "reason": "runtime_not_supported"
      }
    ],
    "candidate_only_count": 1,
    "same_as_main_skill_count": 0,
    "rule_only_classification_count": 0,
    "hybrid_resolved_count": 0,
    "subskills": [
      "choose_correct_statement",
      "classify_quadrant",
      "compute_distance_between_two_points",
      "compute_numeric",
      "same_as_main_skill"
    ],
    "fallback_subskill_used": true,
    "source_belongs_to_current_skill_by_default_count": 4,
    "induction_source_selection": {
      "core_example_count": 4,
      "enrichment_example_count": 0,
      "skipped_enrichment_examples": [],
      "future_ai_judged_candidates": [],
      "contextual_application_sources": [],
      "min_core_examples_for_induction": 2,
      "core_sufficient_for_induction": true
    },
    "skipped_enrichment_examples": [],
    "future_ai_judged_candidates": [],
    "contextual_application_sources": [],
    "core_example_count": 4,
    "enrichment_example_count": 0,
    "source_example_alignment": [
      {
        "example_id": 4417,
        "target_task": "classify_quadrant",
        "task_family": "classify_quadrant_family",
        "alignment_score": 0.0,
        "aligned_with_skill": true,
        "included_in_phase1": true,
        "exclude_reason": "",
        "alignment_kind": "unresolved_within_current_skill",
        "skill_id_match": true,
        "task_family_match": false,
        "subskill_match": false,
        "pass_with_warning": false,
        "requires_human_action": true,
        "induction_tier": "core",
        "included_in_core_induction": true,
        "enrichment_reasons": [],
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "classification_source": "rule_first_mode",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "induction_eligibility": "eligible",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "title_stem_preview": "若點$P\\left( a,b \\right)$位在第一象限且a < b，則$Q\\left( a-b,{{a}^{2}}b \\right)$位在第幾象限？"
      },
      {
        "example_id": 4435,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "alignment_score": 0.0,
        "aligned_with_skill": true,
        "included_in_phase1": true,
        "exclude_reason": "",
        "alignment_kind": "unresolved_within_current_skill",
        "skill_id_match": true,
        "task_family_match": false,
        "subskill_match": false,
        "pass_with_warning": false,
        "requires_human_action": true,
        "induction_tier": "core",
        "included_in_core_induction": true,
        "enrichment_reasons": [],
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "classification_source": "rule_first_mode",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "induction_eligibility": "eligible",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "title_stem_preview": "設a、b為實數，且a < b < 0，則點$Q\\left( ab,a+b \\right)$在第幾象限？"
      },
      {
        "example_id": 4509,
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "alignment_score": 0.0,
        "aligned_with_skill": true,
        "included_in_phase1": true,
        "exclude_reason": "",
        "alignment_kind": "unresolved_within_current_skill",
        "skill_id_match": true,
        "task_family_match": false,
        "subskill_match": false,
        "pass_with_warning": false,
        "requires_human_action": true,
        "induction_tier": "core",
        "included_in_core_induction": true,
        "enrichment_reasons": [],
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "classification_source": "rule_first_mode",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "induction_eligibility": "eligible",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "title_stem_preview": "設A點為坐標平面上一點，且A點到x軸及y軸之距離分別為3和4，則下列何者可能為A點之坐標？ 　(A)$\\left( -4,-3 \\right)$　(B)$\\le"
      },
      {
        "example_id": 4510,
        "target_task": "choose_correct_statement",
        "task_family": "classify_quadrant_family",
        "alignment_score": 0.0,
        "aligned_with_skill": true,
        "included_in_phase1": true,
        "exclude_reason": "",
        "alignment_kind": "unresolved_within_current_skill",
        "skill_id_match": true,
        "task_family_match": false,
        "subskill_match": false,
        "pass_with_warning": false,
        "requires_human_action": true,
        "induction_tier": "core",
        "included_in_core_induction": true,
        "enrichment_reasons": [],
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "classification_source": "rule_first_mode",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "induction_eligibility": "eligible",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "title_stem_preview": "已知點$P\\left( a-b,ab \\right)$在坐標平面的第四象限，則下列敘述何者正確？_x000D_\n(A)$A\\left( -a,b \\right)"
      }
    ],
    "induction_clusters": [
      {
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "short_answer",
          "classify_quadrant",
          "short_answer",
          [
            "sign_reasoning"
          ],
          [
            "symbolic_condition",
            "coordinate_point"
          ],
          "default"
        ],
        "source_example_ids": [
          4417
        ],
        "answer_type": "short_answer",
        "presentation_mode": "short_answer",
        "source_has_choices": false
      },
      {
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "short_answer",
          "compute_numeric",
          "short_answer",
          [
            "sign_reasoning"
          ],
          [
            "symbolic_condition",
            "coordinate_point"
          ],
          "default"
        ],
        "source_example_ids": [
          4435
        ],
        "answer_type": "short_answer",
        "presentation_mode": "short_answer",
        "source_has_choices": false
      },
      {
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "single_choice",
          "compute_distance_between_two_points",
          "single_choice",
          [
            "axis_distance_reasoning",
            "distance_formula_reasoning"
          ],
          [
            "axis_distance",
            "coordinate_point"
          ],
          "default"
        ],
        "source_example_ids": [
          4509
        ],
        "answer_type": "single_choice",
        "presentation_mode": "single_choice",
        "source_has_choices": true
      },
      {
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "single_choice",
          "choose_correct_statement",
          "single_choice",
          [
            "sign_reasoning"
          ],
          [
            "coordinate_point",
            "three_coordinate_points"
          ],
          "default"
        ],
        "source_example_ids": [
          4510
        ],
        "answer_type": "single_choice",
        "presentation_mode": "single_choice",
        "source_has_choices": true
      }
    ],
    "induced_problem_type_specs": [
      {
        "problem_type_id": "evaluate_function_value_2",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "target_task": "evaluate_function_value",
        "task_family": "function_concept_family",
        "display_name": "evaluate_function_value / anchor bootstrap",
        "answer_format_hint": "expression",
        "source_example_ids": [],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "expression",
          "answer_shape": "factored_expression",
          "answer_equivalence": "algebraic_equivalent",
          "equivalence_type": "algebraic_equivalent",
          "checker": "expression_checker",
          "checker_key": "expression_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "expression_checker",
          "checker_selection_reason": "quadratic_factoring_expression",
          "accepted_formats": [
            "(x-5)(x+3)",
            "(2x-1)(x+5)",
            "2(x-1)(3x+2)"
          ],
          "answer_semantics": "algebraic_expression"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
          ],
          "forbidden_patterns": [
            "\\(A\\)",
            "\\(B\\)",
            "\\(C\\)",
            "\\(D\\)"
          ]
        },
        "dependency_contract": {
          "givens_must_be_used": true,
          "target_answer_must_depend_on_givens": true,
          "variables_in_conditions_must_appear_in_target": false
        },
        "semantic_contract": {
          "reasoning_type": [
            "evaluate_function_value"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
          ]
        },
        "generator_contract": {
          "template_variants": [
            {
              "id": "default",
              "label": "default",
              "stem_pattern": "依題意求解：{stem_hint}。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "seed": {
              "type": "integer",
              "randomize": true
            },
            "difficulty_level": {
              "choices": [
                "level_1",
                "level_2",
                "level_3"
              ],
              "weights": [
                0.4,
                0.4,
                0.2
              ]
            }
          },
          "variation_dimensions": [
            "seed",
            "difficulty_level",
            "context_style"
          ],
          "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {}
          },
          "anti_repetition_rules": {
            "avoid_same_template_consecutive": true,
            "avoid_same_ratio_consecutive": true,
            "avoid_same_point_names_consecutive": true,
            "avoid_same_answer_consecutive": true,
            "recent_history_window": 5,
            "signature_fields": [
              "problem_type_id",
              "template_variant",
              "routing_track",
              "scenario_type",
              "ratio_form",
              "ratio_values",
              "coordinate_pattern",
              "answer"
            ]
          },
          "validity_constraints": [
            "answer derivable from givens"
          ],
          "answer_shape": "numeric",
          "explanation_variants": [
            "stepwise"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "evaluate_function_value"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "template_slots": {
            "stem": "function_value_numeric"
          },
          "problem_type_id": "evaluate_function_value_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "anchor_slot_bootstrap",
        "grouping_reason": "anchor_subskill_bootstrap_zero_source",
        "feature_signature": [
          "anchor_slot_bootstrap",
          "evaluate_function_value"
        ],
        "canonical_base_problem_type_id": "evaluate_function_value_2",
        "value_type_prefix": "",
        "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
      },
      {
        "problem_type_id": "interpret_function_notation_2",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "target_task": "interpret_function_notation",
        "task_family": "function_concept_family",
        "display_name": "interpret_function_notation / anchor bootstrap",
        "answer_format_hint": "expression",
        "source_example_ids": [],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "expression",
          "answer_shape": "factored_expression",
          "answer_equivalence": "algebraic_equivalent",
          "equivalence_type": "algebraic_equivalent",
          "checker": "expression_checker",
          "checker_key": "expression_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "expression_checker",
          "checker_selection_reason": "quadratic_factoring_expression",
          "accepted_formats": [
            "(x-5)(x+3)",
            "(2x-1)(x+5)",
            "2(x-1)(3x+2)"
          ],
          "answer_semantics": "algebraic_expression"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
          ],
          "forbidden_patterns": [
            "\\(A\\)",
            "\\(B\\)",
            "\\(C\\)",
            "\\(D\\)"
          ]
        },
        "dependency_contract": {
          "givens_must_be_used": true,
          "target_answer_must_depend_on_givens": true,
          "variables_in_conditions_must_appear_in_target": false
        },
        "semantic_contract": {
          "reasoning_type": [
            "interpret_function_notation"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
          ]
        },
        "generator_contract": {
          "template_variants": [
            {
              "id": "default",
              "label": "default",
              "stem_pattern": "依題意求解：{stem_hint}。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "seed": {
              "type": "integer",
              "randomize": true
            },
            "difficulty_level": {
              "choices": [
                "level_1",
                "level_2",
                "level_3"
              ],
              "weights": [
                0.4,
                0.4,
                0.2
              ]
            }
          },
          "variation_dimensions": [
            "seed",
            "difficulty_level",
            "context_style"
          ],
          "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {}
          },
          "anti_repetition_rules": {
            "avoid_same_template_consecutive": true,
            "avoid_same_ratio_consecutive": true,
            "avoid_same_point_names_consecutive": true,
            "avoid_same_answer_consecutive": true,
            "recent_history_window": 5,
            "signature_fields": [
              "problem_type_id",
              "template_variant",
              "routing_track",
              "scenario_type",
              "ratio_form",
              "ratio_values",
              "coordinate_pattern",
              "answer"
            ]
          },
          "validity_constraints": [
            "answer derivable from givens"
          ],
          "answer_shape": "numeric",
          "explanation_variants": [
            "stepwise"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "interpret_function_notation"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "template_slots": {
            "stem": "linear_function_two_point_choice"
          },
          "problem_type_id": "interpret_function_notation_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "anchor_slot_bootstrap",
        "grouping_reason": "anchor_subskill_bootstrap_zero_source",
        "feature_signature": [
          "anchor_slot_bootstrap",
          "interpret_function_notation"
        ],
        "canonical_base_problem_type_id": "interpret_function_notation_2",
        "value_type_prefix": "",
        "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
      }
    ],
    "candidate_problem_types": [
      {
        "problem_type_id": "evaluate_function_value_2",
        "proposed_problem_type_id": "evaluate_function_value_2",
        "display_name": "evaluate_function_value / anchor bootstrap",
        "matched_example_ids": [],
        "matched_example_count": 0,
        "unmatched_example_ids": [],
        "representative_example_id": null,
        "structural_features": [
          "factored_expression"
        ],
        "answer_contract_proposal": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "expression",
          "answer_shape": "factored_expression",
          "answer_equivalence": "algebraic_equivalent",
          "equivalence_type": "algebraic_equivalent",
          "checker": "expression_checker",
          "checker_key": "expression_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "expression_checker",
          "checker_selection_reason": "quadratic_factoring_expression",
          "accepted_formats": [
            "(x-5)(x+3)",
            "(2x-1)(x+5)",
            "2(x-1)(3x+2)"
          ],
          "answer_semantics": "algebraic_expression",
          "checker_capability_status": "ok",
          "checker_contract_blockers": [],
          "checker_contract_warnings": [],
          "stem_contract": {
            "stem_must_not_embed_choices": true,
            "allowed_math_objects": [
              "quadratic_inequality"
            ],
            "required_math_objects": [
              "quadratic_inequality"
            ],
            "forbidden_patterns": [
              "\\(A\\)",
              "\\(B\\)",
              "\\(C\\)",
              "\\(D\\)"
            ]
          },
          "dependency_contract": {
            "givens_must_be_used": true,
            "target_answer_must_depend_on_givens": true,
            "variables_in_conditions_must_appear_in_target": false
          },
          "semantic_contract": {
            "reasoning_type": [
              "evaluate_function_value"
            ],
            "reject_if": [
              "unused_condition",
              "ambiguous_answer",
              "answer_not_derivable"
            ]
          },
          "generator_contract": {
            "template_variants": [
              {
                "id": "default",
                "label": "default",
                "stem_pattern": "依題意求解：{stem_hint}。",
                "weight": 1.0,
                "enabled": true
              }
            ],
            "parameter_schema": {
              "seed": {
                "type": "integer",
                "randomize": true
              },
              "difficulty_level": {
                "choices": [
                  "level_1",
                  "level_2",
                  "level_3"
                ],
                "weights": [
                  0.4,
                  0.4,
                  0.2
                ]
              }
            },
            "variation_dimensions": [
              "seed",
              "difficulty_level",
              "context_style"
            ],
            "difficulty_controls": {
              "level_1": {},
              "level_2": {},
              "level_3": {}
            },
            "anti_repetition_rules": {
              "avoid_same_template_consecutive": true,
              "avoid_same_ratio_consecutive": true,
              "avoid_same_point_names_consecutive": true,
              "avoid_same_answer_consecutive": true,
              "recent_history_window": 5,
              "signature_fields": [
                "problem_type_id",
                "template_variant",
                "routing_track",
                "scenario_type",
                "ratio_form",
                "ratio_values",
                "coordinate_pattern",
                "answer"
              ]
            },
            "validity_constraints": [
              "answer derivable from givens"
            ],
            "answer_shape": "numeric",
            "explanation_variants": [
              "stepwise"
            ],
            "sampling_strategy": "weighted_random",
            "template_families": [
              "evaluate_function_value"
            ],
            "parameter_slots": {
              "seed": "integer",
              "difficulty": "easy"
            },
            "randomization_rules": {
              "shuffle_choices": false
            },
            "avoid_llm_freeform_math": true,
            "use_domain_functions": true,
            "derivation_steps_required": true,
            "template_slots": {
              "stem": "function_value_numeric"
            },
            "problem_type_id": "evaluate_function_value_2",
            "contract_validation_blockers": [],
            "contract_validation_warnings": [
              "single_template_variant_only",
              "variation_dimensions_below_recommended_minimum"
            ]
          },
          "validator_contract": {
            "static_checks": [
              "answer_contract_checks"
            ],
            "semantic_checks": [
              "givens_to_target_dependency"
            ],
            "runtime_smoke_count": 30
          },
          "order_matters": true,
          "accepted_format_notes": [],
          "canonical_answer_schema": "expression"
        },
        "checker_key_proposal": "expression_checker",
        "equivalence_type_proposal": "algebraic_equivalent",
        "answer_shape": "factored_expression",
        "answer_semantics": "algebraic_expression",
        "presentation_mode": "short_answer",
        "source_has_choices": false,
        "selected_checker": "expression_checker",
        "checker_selection_reason": "quadratic_factoring_expression",
        "confidence": "medium",
        "promote_recommendation": "recommend_promote_for_that_candidate",
        "promote_blockers": [],
        "risk_flags": [
          "alignment_score_below_recommended_threshold",
          "anchor_slot_bootstrap_zero_source",
          "anchor_taxonomy_needs_refinement",
          "candidate_family_span_outside_skill_scope",
          "mixed_source_families",
          "source_skill_scope_locked_demoted_blockers_to_warnings"
        ],
        "checker_contract_warnings": [],
        "spec_source": "anchor_slot_bootstrap",
        "grouping_reason": "anchor_subskill_bootstrap_zero_source",
        "feature_signature": [
          "anchor_slot_bootstrap",
          "evaluate_function_value"
        ],
        "problem_type_spec_draft": {
          "problem_type_id": "evaluate_function_value_2",
          "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
          "target_task": "evaluate_function_value",
          "task_family": "function_concept_family",
          "display_name": "evaluate_function_value / anchor bootstrap",
          "answer_format_hint": "expression",
          "source_example_ids": [],
          "answer_contract": {
            "choices_required": false,
            "choice_count": null,
            "correct_choice_count": null,
            "frontend_render_choices": false,
            "answer_type": "expression",
            "answer_shape": "factored_expression",
            "answer_equivalence": "algebraic_equivalent",
            "equivalence_type": "algebraic_equivalent",
            "checker": "expression_checker",
            "checker_key": "expression_checker",
            "presentation_mode": "short_answer",
            "selected_checker": "expression_checker",
            "checker_selection_reason": "quadratic_factoring_expression",
            "accepted_formats": [
              "(x-5)(x+3)",
              "(2x-1)(x+5)",
              "2(x-1)(3x+2)"
            ],
            "answer_semantics": "algebraic_expression"
          },
          "stem_contract": {
            "stem_must_not_embed_choices": true,
            "allowed_math_objects": [
              "quadratic_inequality"
            ],
            "required_math_objects": [
              "quadratic_inequality"
            ],
            "forbidden_patterns": [
              "\\(A\\)",
              "\\(B\\)",
              "\\(C\\)",
              "\\(D\\)"
            ]
          },
          "dependency_contract": {
            "givens_must_be_used": true,
            "target_answer_must_depend_on_givens": true,
            "variables_in_conditions_must_appear_in_target": false
          },
          "semantic_contract": {
            "reasoning_type": [
              "evaluate_function_value"
            ],
            "reject_if": [
              "unused_condition",
              "ambiguous_answer",
              "answer_not_derivable"
            ]
          },
          "generator_contract": {
            "template_variants": [
              {
                "id": "default",
                "label": "default",
                "stem_pattern": "依題意求解：{stem_hint}。",
                "weight": 1.0,
                "enabled": true
              }
            ],
            "parameter_schema": {
              "seed": {
                "type": "integer",
                "randomize": true
              },
              "difficulty_level": {
                "choices": [
                  "level_1",
                  "level_2",
                  "level_3"
                ],
                "weights": [
                  0.4,
                  0.4,
                  0.2
                ]
              }
            },
            "variation_dimensions": [
              "seed",
              "difficulty_level",
              "context_style"
            ],
            "difficulty_controls": {
              "level_1": {},
              "level_2": {},
              "level_3": {}
            },
            "anti_repetition_rules": {
              "avoid_same_template_consecutive": true,
              "avoid_same_ratio_consecutive": true,
              "avoid_same_point_names_consecutive": true,
              "avoid_same_answer_consecutive": true,
              "recent_history_window": 5,
              "signature_fields": [
                "problem_type_id",
                "template_variant",
                "routing_track",
                "scenario_type",
                "ratio_form",
                "ratio_values",
                "coordinate_pattern",
                "answer"
              ]
            },
            "validity_constraints": [
              "answer derivable from givens"
            ],
            "answer_shape": "numeric",
            "explanation_variants": [
              "stepwise"
            ],
            "sampling_strategy": "weighted_random",
            "template_families": [
              "evaluate_function_value"
            ],
            "parameter_slots": {
              "seed": "integer",
              "difficulty": "easy"
            },
            "randomization_rules": {
              "shuffle_choices": false
            },
            "avoid_llm_freeform_math": true,
            "use_domain_functions": true,
            "derivation_steps_required": true,
            "template_slots": {
              "stem": "function_value_numeric"
            },
            "problem_type_id": "evaluate_function_value_2",
            "contract_validation_blockers": [],
            "contract_validation_warnings": [
              "single_template_variant_only",
              "variation_dimensions_below_recommended_minimum"
            ]
          },
          "validator_contract": {
            "static_checks": [
              "answer_contract_checks"
            ],
            "semantic_checks": [
              "givens_to_target_dependency"
            ],
            "runtime_smoke_count": 30
          },
          "spec_source": "anchor_slot_bootstrap",
          "grouping_reason": "anchor_subskill_bootstrap_zero_source",
          "feature_signature": [
            "anchor_slot_bootstrap",
            "evaluate_function_value"
          ],
          "canonical_base_problem_type_id": "evaluate_function_value_2",
          "value_type_prefix": "",
          "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
        },
        "generator_readiness": "runtime_ready",
        "usable_for_phase3": true,
        "template_slot": "function_value_numeric",
        "canonical_base_problem_type_id": "evaluate_function_value_2",
        "value_type_prefix": "",
        "subskill_id": "evaluate_function_value",
        "runtime_status": "runtime_ready_candidate",
        "next_action": "phase2_foundation_preflight",
        "semantic_alignment": {
          "skill_problem_type_score": 0.0,
          "source_problem_type_score": 0.0,
          "task_consistent_with_skill": true
        }
      },
      {
        "problem_type_id": "interpret_function_notation_2",
        "proposed_problem_type_id": "interpret_function_notation_2",
        "display_name": "interpret_function_notation / anchor bootstrap",
        "matched_example_ids": [],
        "matched_example_count": 0,
        "unmatched_example_ids": [],
        "representative_example_id": null,
        "structural_features": [
          "factored_expression"
        ],
        "answer_contract_proposal": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "expression",
          "answer_shape": "factored_expression",
          "answer_equivalence": "algebraic_equivalent",
          "equivalence_type": "algebraic_equivalent",
          "checker": "expression_checker",
          "checker_key": "expression_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "expression_checker",
          "checker_selection_reason": "quadratic_factoring_expression",
          "accepted_formats": [
            "(x-5)(x+3)",
            "(2x-1)(x+5)",
            "2(x-1)(3x+2)"
          ],
          "answer_semantics": "algebraic_expression",
          "checker_capability_status": "ok",
          "checker_contract_blockers": [],
          "checker_contract_warnings": [],
          "stem_contract": {
            "stem_must_not_embed_choices": true,
            "allowed_math_objects": [
              "quadratic_inequality"
            ],
            "required_math_objects": [
              "quadratic_inequality"
            ],
            "forbidden_patterns": [
              "\\(A\\)",
              "\\(B\\)",
              "\\(C\\)",
              "\\(D\\)"
            ]
          },
          "dependency_contract": {
            "givens_must_be_used": true,
            "target_answer_must_depend_on_givens": true,
            "variables_in_conditions_must_appear_in_target": false
          },
          "semantic_contract": {
            "reasoning_type": [
              "interpret_function_notation"
            ],
            "reject_if": [
              "unused_condition",
              "ambiguous_answer",
              "answer_not_derivable"
            ]
          },
          "generator_contract": {
            "template_variants": [
              {
                "id": "default",
                "label": "default",
                "stem_pattern": "依題意求解：{stem_hint}。",
                "weight": 1.0,
                "enabled": true
              }
            ],
            "parameter_schema": {
              "seed": {
                "type": "integer",
                "randomize": true
              },
              "difficulty_level": {
                "choices": [
                  "level_1",
                  "level_2",
                  "level_3"
                ],
                "weights": [
                  0.4,
                  0.4,
                  0.2
                ]
              }
            },
            "variation_dimensions": [
              "seed",
              "difficulty_level",
              "context_style"
            ],
            "difficulty_controls": {
              "level_1": {},
              "level_2": {},
              "level_3": {}
            },
            "anti_repetition_rules": {
              "avoid_same_template_consecutive": true,
              "avoid_same_ratio_consecutive": true,
              "avoid_same_point_names_consecutive": true,
              "avoid_same_answer_consecutive": true,
              "recent_history_window": 5,
              "signature_fields": [
                "problem_type_id",
                "template_variant",
                "routing_track",
                "scenario_type",
                "ratio_form",
                "ratio_values",
                "coordinate_pattern",
                "answer"
              ]
            },
            "validity_constraints": [
              "answer derivable from givens"
            ],
            "answer_shape": "numeric",
            "explanation_variants": [
              "stepwise"
            ],
            "sampling_strategy": "weighted_random",
            "template_families": [
              "interpret_function_notation"
            ],
            "parameter_slots": {
              "seed": "integer",
              "difficulty": "easy"
            },
            "randomization_rules": {
              "shuffle_choices": false
            },
            "avoid_llm_freeform_math": true,
            "use_domain_functions": true,
            "derivation_steps_required": true,
            "template_slots": {
              "stem": "linear_function_two_point_choice"
            },
            "problem_type_id": "interpret_function_notation_2",
            "contract_validation_blockers": [],
            "contract_validation_warnings": [
              "single_template_variant_only",
              "variation_dimensions_below_recommended_minimum"
            ]
          },
          "validator_contract": {
            "static_checks": [
              "answer_contract_checks"
            ],
            "semantic_checks": [
              "givens_to_target_dependency"
            ],
            "runtime_smoke_count": 30
          },
          "order_matters": true,
          "accepted_format_notes": [],
          "canonical_answer_schema": "expression"
        },
        "checker_key_proposal": "expression_checker",
        "equivalence_type_proposal": "algebraic_equivalent",
        "answer_shape": "factored_expression",
        "answer_semantics": "algebraic_expression",
        "presentation_mode": "short_answer",
        "source_has_choices": false,
        "selected_checker": "expression_checker",
        "checker_selection_reason": "quadratic_factoring_expression",
        "confidence": "medium",
        "promote_recommendation": "recommend_promote_for_that_candidate",
        "promote_blockers": [],
        "risk_flags": [
          "alignment_score_below_recommended_threshold",
          "anchor_slot_bootstrap_zero_source",
          "anchor_taxonomy_needs_refinement",
          "candidate_family_span_outside_skill_scope",
          "mixed_source_families",
          "source_skill_scope_locked_demoted_blockers_to_warnings"
        ],
        "checker_contract_warnings": [],
        "spec_source": "anchor_slot_bootstrap",
        "grouping_reason": "anchor_subskill_bootstrap_zero_source",
        "feature_signature": [
          "anchor_slot_bootstrap",
          "interpret_function_notation"
        ],
        "problem_type_spec_draft": {
          "problem_type_id": "interpret_function_notation_2",
          "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
          "target_task": "interpret_function_notation",
          "task_family": "function_concept_family",
          "display_name": "interpret_function_notation / anchor bootstrap",
          "answer_format_hint": "expression",
          "source_example_ids": [],
          "answer_contract": {
            "choices_required": false,
            "choice_count": null,
            "correct_choice_count": null,
            "frontend_render_choices": false,
            "answer_type": "expression",
            "answer_shape": "factored_expression",
            "answer_equivalence": "algebraic_equivalent",
            "equivalence_type": "algebraic_equivalent",
            "checker": "expression_checker",
            "checker_key": "expression_checker",
            "presentation_mode": "short_answer",
            "selected_checker": "expression_checker",
            "checker_selection_reason": "quadratic_factoring_expression",
            "accepted_formats": [
              "(x-5)(x+3)",
              "(2x-1)(x+5)",
              "2(x-1)(3x+2)"
            ],
            "answer_semantics": "algebraic_expression"
          },
          "stem_contract": {
            "stem_must_not_embed_choices": true,
            "allowed_math_objects": [
              "quadratic_inequality"
            ],
            "required_math_objects": [
              "quadratic_inequality"
            ],
            "forbidden_patterns": [
              "\\(A\\)",
              "\\(B\\)",
              "\\(C\\)",
              "\\(D\\)"
            ]
          },
          "dependency_contract": {
            "givens_must_be_used": true,
            "target_answer_must_depend_on_givens": true,
            "variables_in_conditions_must_appear_in_target": false
          },
          "semantic_contract": {
            "reasoning_type": [
              "interpret_function_notation"
            ],
            "reject_if": [
              "unused_condition",
              "ambiguous_answer",
              "answer_not_derivable"
            ]
          },
          "generator_contract": {
            "template_variants": [
              {
                "id": "default",
                "label": "default",
                "stem_pattern": "依題意求解：{stem_hint}。",
                "weight": 1.0,
                "enabled": true
              }
            ],
            "parameter_schema": {
              "seed": {
                "type": "integer",
                "randomize": true
              },
              "difficulty_level": {
                "choices": [
                  "level_1",
                  "level_2",
                  "level_3"
                ],
                "weights": [
                  0.4,
                  0.4,
                  0.2
                ]
              }
            },
            "variation_dimensions": [
              "seed",
              "difficulty_level",
              "context_style"
            ],
            "difficulty_controls": {
              "level_1": {},
              "level_2": {},
              "level_3": {}
            },
            "anti_repetition_rules": {
              "avoid_same_template_consecutive": true,
              "avoid_same_ratio_consecutive": true,
              "avoid_same_point_names_consecutive": true,
              "avoid_same_answer_consecutive": true,
              "recent_history_window": 5,
              "signature_fields": [
                "problem_type_id",
                "template_variant",
                "routing_track",
                "scenario_type",
                "ratio_form",
                "ratio_values",
                "coordinate_pattern",
                "answer"
              ]
            },
            "validity_constraints": [
              "answer derivable from givens"
            ],
            "answer_shape": "numeric",
            "explanation_variants": [
              "stepwise"
            ],
            "sampling_strategy": "weighted_random",
            "template_families": [
              "interpret_function_notation"
            ],
            "parameter_slots": {
              "seed": "integer",
              "difficulty": "easy"
            },
            "randomization_rules": {
              "shuffle_choices": false
            },
            "avoid_llm_freeform_math": true,
            "use_domain_functions": true,
            "derivation_steps_required": true,
            "template_slots": {
              "stem": "linear_function_two_point_choice"
            },
            "problem_type_id": "interpret_function_notation_2",
            "contract_validation_blockers": [],
            "contract_validation_warnings": [
              "single_template_variant_only",
              "variation_dimensions_below_recommended_minimum"
            ]
          },
          "validator_contract": {
            "static_checks": [
              "answer_contract_checks"
            ],
            "semantic_checks": [
              "givens_to_target_dependency"
            ],
            "runtime_smoke_count": 30
          },
          "spec_source": "anchor_slot_bootstrap",
          "grouping_reason": "anchor_subskill_bootstrap_zero_source",
          "feature_signature": [
            "anchor_slot_bootstrap",
            "interpret_function_notation"
          ],
          "canonical_base_problem_type_id": "interpret_function_notation_2",
          "value_type_prefix": "",
          "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
        },
        "generator_readiness": "runtime_ready",
        "usable_for_phase3": true,
        "template_slot": "linear_function_two_point_choice",
        "canonical_base_problem_type_id": "interpret_function_notation_2",
        "value_type_prefix": "",
        "subskill_id": "interpret_function_notation",
        "runtime_status": "runtime_ready_candidate",
        "next_action": "phase2_foundation_preflight",
        "semantic_alignment": {
          "skill_problem_type_score": 0.0,
          "source_problem_type_score": 0.0,
          "task_consistent_with_skill": true
        }
      }
    ],
    "per_example_classification": [
      {
        "example_id": 4417,
        "detected_problem_type_id": "short_answer_classify_quadrant_short_answer",
        "example_feature": {
          "source_example_id": 4417,
          "question_text": "若點$P\\left( a,b \\right)$位在第一象限且a < b，則$Q\\left( a-b,{{a}^{2}}b \\right)$位在第幾象限？",
          "answer": "",
          "choices": [],
          "has_choices": false,
          "stem_embeds_choices": false,
          "answer_type": "text_short",
          "answer_shape": "text_short",
          "checker": "text_short_checker",
          "equivalence": "exact_string",
          "math_objects": [
            "coordinate_point",
            "symbolic_condition",
            "two_coordinate_points"
          ],
          "target_task": "classify_quadrant",
          "task_family": "classify_quadrant_family",
          "reasoning_type": [
            "sign_reasoning"
          ],
          "required_derivation": true,
          "source_quality_issues": [],
          "source_quality_reject": false,
          "candidate_only": false,
          "variables": [
            "P",
            "Q",
            "a",
            "b"
          ],
          "givens": [
            "P",
            "Q",
            "a",
            "b"
          ],
          "target": "classify_quadrant",
          "classifier_source": "rule_first_mode",
          "math_meta_tags": [],
          "forced_target_task": "",
          "meta_answer_format_hint": "",
          "semantic_classification": {
            "ai_target_task": "",
            "ai_task_family": "",
            "ai_confidence": 0.0,
            "ai_evidence": [],
            "ai_negative_evidence": {},
            "ai_available": false,
            "ai_error": "rule_first_mode",
            "ai_unavailable_reason": "ai_wrapper_error",
            "rule_target_task": "classify_quadrant",
            "rule_task_family": "classify_quadrant_family",
            "rule_confidence": 0.7,
            "final_target_task": "classify_quadrant",
            "final_task_family": "classify_quadrant_family",
            "classifier_source": "rule_first_mode",
            "conflict_reason": "",
            "source_mapping_warning": "expected_family_mismatch",
            "requires_human_action": false,
            "ai_notes": "",
            "target_task": "classify_quadrant",
            "task_family": "classify_quadrant_family",
            "math_objects": [
              "coordinate_point",
              "symbolic_condition",
              "two_coordinate_points"
            ],
            "answer_type": "short_answer",
            "answer_shape": "text_short",
            "source_type": "unknown",
            "example_label": "",
            "practice_label": "",
            "linked_example": "",
            "linked_example_id": null,
            "linked_example_task_family": "",
            "structure_consistency": "not_applicable",
            "sequence_context_used": true,
            "structure_context_used": false,
            "confidence_adjustment_reason": "sequence_context_used",
            "possible_structure_mismatch": false,
            "possible_mixed_source_context": false
          },
          "source_structure_context": {
            "source_type": "unknown",
            "example_label": "",
            "practice_label": "",
            "linked_example": "",
            "section_order": 0,
            "example_number": null,
            "practice_number": null,
            "nearby_worked_examples": [],
            "linked_worked_example": null,
            "linked_practices": [],
            "same_section_sequence": [
              {
                "example_id": 4417,
                "source_type": "unknown",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "1-2習題 基礎題 1"
              },
              {
                "example_id": 4435,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習1",
                "section_order": 0,
                "title_head": "隨堂練習1"
              },
              {
                "example_id": 4509,
                "source_type": "unknown",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "CH1自我評量 題2"
              },
              {
                "example_id": 4510,
                "source_type": "unknown",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "CH1自我評量 題3"
              }
            ]
          },
          "induction_tier": "core",
          "enrichment_reasons": [],
          "included_in_core_induction": true,
          "source_skill_scope_locked": true,
          "skill_mapping_authority": "textbook_examples.skill_id",
          "classification_scope": "within_current_skill",
          "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
          "unresolved_within_current_skill": true,
          "pending_problem_type_induction": true,
          "requires_human_rule_pack": true,
          "requires_human_action": false,
          "unresolved_reason": "semantic_score_zero_within_current_skill",
          "generator_readiness": "pending_problem_type_induction",
          "usable_for_phase3": false,
          "equivalence_type": "exact_string",
          "checker_key": "text_short_checker"
        },
        "answer_shape": "text_short",
        "classification_confidence": "high",
        "classification_reason": "rule_first_mode",
        "risk_flags": [
          "expected_family_mismatch"
        ],
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "classify_quadrant",
          "rule_task_family": "classify_quadrant_family",
          "rule_confidence": 0.7,
          "final_target_task": "classify_quadrant",
          "final_task_family": "classify_quadrant_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": false,
          "ai_notes": "",
          "target_task": "classify_quadrant",
          "task_family": "classify_quadrant_family",
          "math_objects": [
            "coordinate_point",
            "symbolic_condition",
            "two_coordinate_points"
          ],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": false,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "subskill_id": "classify_quadrant",
        "classification_source": "rule_first_mode",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "requires_human_rule_pack": true,
        "induction_eligibility": "eligible"
      },
      {
        "example_id": 4435,
        "detected_problem_type_id": "short_answer_compute_numeric_short_answer",
        "example_feature": {
          "source_example_id": 4435,
          "question_text": "設a、b為實數，且a < b < 0，則點$Q\\left( ab,a+b \\right)$在第幾象限？",
          "answer": "",
          "choices": [],
          "has_choices": false,
          "stem_embeds_choices": false,
          "answer_type": "text_short",
          "answer_shape": "text_short",
          "checker": "text_short_checker",
          "equivalence": "exact_string",
          "math_objects": [
            "coordinate_point",
            "symbolic_condition"
          ],
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "reasoning_type": [
            "sign_reasoning"
          ],
          "required_derivation": true,
          "source_quality_issues": [],
          "source_quality_reject": false,
          "candidate_only": false,
          "variables": [
            "Q",
            "a",
            "b"
          ],
          "givens": [
            "Q",
            "a",
            "b"
          ],
          "target": "compute_numeric",
          "classifier_source": "rule_first_mode",
          "math_meta_tags": [],
          "forced_target_task": "",
          "meta_answer_format_hint": "",
          "semantic_classification": {
            "ai_target_task": "",
            "ai_task_family": "",
            "ai_confidence": 0.0,
            "ai_evidence": [],
            "ai_negative_evidence": {},
            "ai_available": false,
            "ai_error": "rule_first_mode",
            "ai_unavailable_reason": "ai_wrapper_error",
            "rule_target_task": "compute_numeric",
            "rule_task_family": "generic_numeric_family",
            "rule_confidence": 0.2,
            "final_target_task": "compute_numeric",
            "final_task_family": "generic_numeric_family",
            "classifier_source": "rule_first_mode",
            "conflict_reason": "rule_first_mode",
            "source_mapping_warning": "expected_family_mismatch",
            "requires_human_action": true,
            "ai_notes": "",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "math_objects": [
              "coordinate_point",
              "symbolic_condition"
            ],
            "answer_type": "short_answer",
            "answer_shape": "text_short",
            "source_type": "in_class_practice",
            "example_label": "",
            "practice_label": "隨堂練習1",
            "linked_example": "",
            "linked_example_id": null,
            "linked_example_task_family": "",
            "structure_consistency": "unknown",
            "sequence_context_used": true,
            "structure_context_used": true,
            "confidence_adjustment_reason": "sequence_context_used",
            "possible_structure_mismatch": false,
            "possible_mixed_source_context": false
          },
          "source_structure_context": {
            "source_type": "in_class_practice",
            "example_label": "",
            "practice_label": "隨堂練習1",
            "linked_example": "",
            "section_order": 0,
            "example_number": null,
            "practice_number": 1,
            "nearby_worked_examples": [],
            "linked_worked_example": null,
            "linked_practices": [],
            "same_section_sequence": [
              {
                "example_id": 4417,
                "source_type": "unknown",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "1-2習題 基礎題 1"
              },
              {
                "example_id": 4435,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習1",
                "section_order": 0,
                "title_head": "隨堂練習1"
              },
              {
                "example_id": 4509,
                "source_type": "unknown",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "CH1自我評量 題2"
              },
              {
                "example_id": 4510,
                "source_type": "unknown",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "CH1自我評量 題3"
              }
            ]
          },
          "induction_tier": "core",
          "enrichment_reasons": [],
          "included_in_core_induction": true,
          "source_skill_scope_locked": true,
          "skill_mapping_authority": "textbook_examples.skill_id",
          "classification_scope": "within_current_skill",
          "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
          "unresolved_within_current_skill": true,
          "pending_problem_type_induction": true,
          "requires_human_rule_pack": true,
          "requires_human_action": false,
          "unresolved_reason": "semantic_score_zero_within_current_skill",
          "generator_readiness": "pending_problem_type_induction",
          "usable_for_phase3": false,
          "equivalence_type": "exact_string",
          "checker_key": "text_short_checker"
        },
        "answer_shape": "text_short",
        "classification_confidence": "high",
        "classification_reason": "rule_first_mode",
        "risk_flags": [
          "expected_family_mismatch",
          "requires_human_action",
          "candidate_only_problem_type"
        ],
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "rule_first_mode",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": true,
          "ai_notes": "",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "symbolic_condition"
          ],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習1",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "unknown",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "subskill_id": "compute_numeric",
        "classification_source": "rule_first_mode",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "requires_human_rule_pack": true,
        "induction_eligibility": "eligible"
      },
      {
        "example_id": 4509,
        "detected_problem_type_id": "single_choice_compute_distance_between_two_points_single_choice",
        "example_feature": {
          "source_example_id": 4509,
          "question_text": "設A點為坐標平面上一點，且A點到x軸及y軸之距離分別為3和4，則下列何者可能為A點之坐標？ 　(A)$\\left( -4,-3 \\right)$　(B)$\\left( -3,4 \\right)$　_x000D_\n(C)$\\left( -3,-4 \\right)$　(D)$\\left( 3,4 \\right)$。_x000D_",
          "answer": "A",
          "choices": [
            "$\\left( -4,-3 \\right)$",
            "$\\left( -3,4 \\right)$　_x000D_",
            "$\\left( -3,-4 \\right)$",
            "$\\left( 3,4 \\right)$。_x000D_"
          ],
          "has_choices": true,
          "stem_embeds_choices": true,
          "answer_type": "choice",
          "answer_shape": "single_choice",
          "checker": "choice_label_checker",
          "equivalence": "choice_label",
          "math_objects": [
            "axis_distance",
            "coordinate_point",
            "distance_formula",
            "segment_length",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "target_task": "compute_distance_between_two_points",
          "task_family": "distance_between_two_points_family",
          "reasoning_type": [
            "axis_distance_reasoning",
            "distance_formula_reasoning"
          ],
          "required_derivation": true,
          "source_quality_issues": [],
          "source_quality_reject": false,
          "candidate_only": false,
          "variables": [
            "A",
            "B",
            "C",
            "D"
          ],
          "givens": [
            "A",
            "B",
            "C",
            "D"
          ],
          "target": "compute_distance_between_two_points",
          "classifier_source": "rule_first_mode",
          "math_meta_tags": [],
          "forced_target_task": "",
          "meta_answer_format_hint": "",
          "semantic_classification": {
            "ai_target_task": "",
            "ai_task_family": "",
            "ai_confidence": 0.0,
            "ai_evidence": [],
            "ai_negative_evidence": {},
            "ai_available": false,
            "ai_error": "rule_first_mode",
            "ai_unavailable_reason": "ai_wrapper_error",
            "rule_target_task": "compute_distance_between_two_points",
            "rule_task_family": "distance_between_two_points_family",
            "rule_confidence": 0.55,
            "final_target_task": "compute_distance_between_two_points",
            "final_task_family": "distance_between_two_points_family",
            "classifier_source": "rule_first_mode",
            "conflict_reason": "",
            "source_mapping_warning": "expected_family_mismatch",
            "requires_human_action": false,
            "ai_notes": "",
            "target_task": "compute_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "math_objects": [
              "axis_distance",
              "coordinate_point",
              "distance_formula",
              "segment_length",
              "three_coordinate_points",
              "triangle",
              "two_coordinate_points"
            ],
            "answer_type": "single_choice",
            "answer_shape": "single_choice",
            "source_type": "unknown",
            "example_label": "",
            "practice_label": "",
            "linked_example": "",
            "linked_example_id": null,
            "linked_example_task_family": "",
            "structure_consistency": "not_applicable",
            "sequence_context_used": true,
            "structure_context_used": false,
            "confidence_adjustment_reason": "sequence_context_used",
            "possible_structure_mismatch": false,
            "possible_mixed_source_context": false,
            "source_quality_reject": false,
            "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
          },
          "source_structure_context": {
            "source_type": "unknown",
            "example_label": "",
            "practice_label": "",
            "linked_example": "",
            "section_order": 0,
            "example_number": null,
            "practice_number": null,
            "nearby_worked_examples": [],
            "linked_worked_example": null,
            "linked_practices": [],
            "same_section_sequence": [
              {
                "example_id": 4417,
                "source_type": "unknown",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "1-2習題 基礎題 1"
              },
              {
                "example_id": 4435,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習1",
                "section_order": 0,
                "title_head": "隨堂練習1"
              },
              {
                "example_id": 4509,
                "source_type": "unknown",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "CH1自我評量 題2"
              },
              {
                "example_id": 4510,
                "source_type": "unknown",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "CH1自我評量 題3"
              }
            ]
          },
          "correct_answer": "A",
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
          "induction_tier": "core",
          "enrichment_reasons": [],
          "included_in_core_induction": true,
          "source_skill_scope_locked": true,
          "skill_mapping_authority": "textbook_examples.skill_id",
          "classification_scope": "within_current_skill",
          "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
          "unresolved_within_current_skill": true,
          "pending_problem_type_induction": true,
          "requires_human_rule_pack": true,
          "requires_human_action": false,
          "unresolved_reason": "semantic_score_zero_within_current_skill",
          "generator_readiness": "pending_problem_type_induction",
          "usable_for_phase3": false,
          "equivalence_type": "choice_label",
          "checker_key": "choice_label_checker"
        },
        "answer_shape": "single_choice",
        "classification_confidence": "high",
        "classification_reason": "rule_first_mode",
        "risk_flags": [
          "stem_embeds_choices",
          "expected_family_mismatch"
        ],
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "compute_distance_between_two_points",
          "rule_task_family": "distance_between_two_points_family",
          "rule_confidence": 0.55,
          "final_target_task": "compute_distance_between_two_points",
          "final_task_family": "distance_between_two_points_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": false,
          "ai_notes": "",
          "target_task": "compute_distance_between_two_points",
          "task_family": "distance_between_two_points_family",
          "math_objects": [
            "axis_distance",
            "coordinate_point",
            "distance_formula",
            "segment_length",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "single_choice",
          "answer_shape": "single_choice",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": false,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
        },
        "subskill_id": "compute_distance_between_two_points",
        "classification_source": "rule_first_mode",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "requires_human_rule_pack": true,
        "induction_eligibility": "eligible"
      },
      {
        "example_id": 4510,
        "detected_problem_type_id": "single_choice_choose_correct_statement_single_choice",
        "example_feature": {
          "source_example_id": 4510,
          "question_text": "已知點$P\\left( a-b,ab \\right)$在坐標平面的第四象限，則下列敘述何者正確？_x000D_\n(A)$A\\left( -a,b \\right)$在第一象限　(B)$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限_x000D_\n(C)$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限　(D)$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。_x000D_",
          "answer": "A",
          "choices": [
            "$A\\left( -a,b \\right)$在第一象限",
            "$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限_x000D_",
            "$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限",
            "$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。_x000D_"
          ],
          "has_choices": true,
          "stem_embeds_choices": true,
          "answer_type": "choice",
          "answer_shape": "single_choice",
          "checker": "choice_label_checker",
          "equivalence": "choice_label",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "target_task": "choose_correct_statement",
          "task_family": "classify_quadrant_family",
          "reasoning_type": [
            "sign_reasoning"
          ],
          "required_derivation": true,
          "source_quality_issues": [],
          "source_quality_reject": false,
          "candidate_only": false,
          "variables": [
            "A",
            "B",
            "C",
            "D",
            "P",
            "a",
            "b"
          ],
          "givens": [
            "A",
            "B",
            "C",
            "D",
            "P",
            "a",
            "b"
          ],
          "target": "choose_correct_statement",
          "classifier_source": "rule_first_mode",
          "math_meta_tags": [],
          "forced_target_task": "",
          "meta_answer_format_hint": "",
          "semantic_classification": {
            "ai_target_task": "",
            "ai_task_family": "",
            "ai_confidence": 0.0,
            "ai_evidence": [],
            "ai_negative_evidence": {},
            "ai_available": false,
            "ai_error": "rule_first_mode",
            "ai_unavailable_reason": "ai_wrapper_error",
            "rule_target_task": "choose_correct_statement",
            "rule_task_family": "classify_quadrant_family",
            "rule_confidence": 0.5,
            "final_target_task": "choose_correct_statement",
            "final_task_family": "classify_quadrant_family",
            "classifier_source": "rule_first_mode",
            "conflict_reason": "",
            "source_mapping_warning": "expected_family_mismatch",
            "requires_human_action": false,
            "ai_notes": "",
            "target_task": "choose_correct_statement",
            "task_family": "classify_quadrant_family",
            "math_objects": [
              "coordinate_point",
              "three_coordinate_points",
              "triangle",
              "two_coordinate_points"
            ],
            "answer_type": "single_choice",
            "answer_shape": "single_choice",
            "source_type": "unknown",
            "example_label": "",
            "practice_label": "",
            "linked_example": "",
            "linked_example_id": null,
            "linked_example_task_family": "",
            "structure_consistency": "not_applicable",
            "sequence_context_used": true,
            "structure_context_used": false,
            "confidence_adjustment_reason": "sequence_context_used",
            "possible_structure_mismatch": false,
            "possible_mixed_source_context": false,
            "source_quality_reject": false,
            "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
          },
          "source_structure_context": {
            "source_type": "unknown",
            "example_label": "",
            "practice_label": "",
            "linked_example": "",
            "section_order": 0,
            "example_number": null,
            "practice_number": null,
            "nearby_worked_examples": [],
            "linked_worked_example": null,
            "linked_practices": [],
            "same_section_sequence": [
              {
                "example_id": 4417,
                "source_type": "unknown",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "1-2習題 基礎題 1"
              },
              {
                "example_id": 4435,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習1",
                "section_order": 0,
                "title_head": "隨堂練習1"
              },
              {
                "example_id": 4509,
                "source_type": "unknown",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "CH1自我評量 題2"
              },
              {
                "example_id": 4510,
                "source_type": "unknown",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "CH1自我評量 題3"
              }
            ]
          },
          "correct_answer": "A",
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
          "induction_tier": "core",
          "enrichment_reasons": [],
          "included_in_core_induction": true,
          "source_skill_scope_locked": true,
          "skill_mapping_authority": "textbook_examples.skill_id",
          "classification_scope": "within_current_skill",
          "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
          "unresolved_within_current_skill": true,
          "pending_problem_type_induction": true,
          "requires_human_rule_pack": true,
          "requires_human_action": false,
          "unresolved_reason": "semantic_score_zero_within_current_skill",
          "generator_readiness": "pending_problem_type_induction",
          "usable_for_phase3": false,
          "equivalence_type": "choice_label",
          "checker_key": "choice_label_checker"
        },
        "answer_shape": "single_choice",
        "classification_confidence": "high",
        "classification_reason": "rule_first_mode",
        "risk_flags": [
          "stem_embeds_choices",
          "expected_family_mismatch"
        ],
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_evidence": [],
          "ai_negative_evidence": {},
          "ai_available": false,
          "ai_error": "rule_first_mode",
          "ai_unavailable_reason": "ai_wrapper_error",
          "rule_target_task": "choose_correct_statement",
          "rule_task_family": "classify_quadrant_family",
          "rule_confidence": 0.5,
          "final_target_task": "choose_correct_statement",
          "final_task_family": "classify_quadrant_family",
          "classifier_source": "rule_first_mode",
          "conflict_reason": "",
          "source_mapping_warning": "expected_family_mismatch",
          "requires_human_action": false,
          "ai_notes": "",
          "target_task": "choose_correct_statement",
          "task_family": "classify_quadrant_family",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "single_choice",
          "answer_shape": "single_choice",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": false,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
        },
        "subskill_id": "choose_correct_statement",
        "classification_source": "rule_first_mode",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "requires_human_rule_pack": true,
        "induction_eligibility": "eligible"
      }
    ],
    "split_or_merge_recommendation": "induced_from_source_features",
    "problem_type_spec_first": true,
    "spec_defined_problem_type_ids": [
      "evaluate_function_value_2",
      "interpret_function_notation_2"
    ],
    "classifier_gate": {
      "status": "classifier_auto_pending_promote_with_warning",
      "allowed": true,
      "warnings": [
        "insufficient_examples",
        "alignment_score_below_recommended_threshold",
        "anchor_slot_bootstrap_zero_source",
        "anchor_taxonomy_needs_refinement",
        "candidate_family_span_outside_skill_scope",
        "mixed_source_families",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ]
    },
    "generator_draft_gate": {
      "status": "generator_draft_allowed_with_low_source_warning",
      "allowed": true,
      "warnings": [
        "low_source_examples",
        "alignment_score_below_recommended_threshold",
        "anchor_slot_bootstrap_zero_source",
        "anchor_taxonomy_needs_refinement",
        "candidate_family_span_outside_skill_scope",
        "mixed_source_families",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ]
    },
    "runtime_ready_gate": {
      "status": "blocked_insufficient_examples",
      "allowed": false,
      "blockers": [
        "runtime_smoke_failed",
        "dynamic_sampling_failed"
      ],
      "warnings": [
        "alignment_score_below_recommended_threshold",
        "anchor_slot_bootstrap_zero_source",
        "anchor_taxonomy_needs_refinement",
        "candidate_family_span_outside_skill_scope",
        "mixed_source_families",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ]
    },
    "exception_review_gate": {
      "required": false,
      "reasons": []
    },
    "next_action": "phase2_generate_from_induced_specs",
    "source_skill_scope_locked": true,
    "source_skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "classification_scope": "within_current_skill",
    "skill_mapping_authority": "textbook_examples.skill_id",
    "human_confirmed_rule_pack_applied": false,
    "matched_registered_yaml_rule_pack": "",
    "ai_classification_overridden_by_human_confirmed_rule_pack": false,
    "curated_specs_available": true
  },
  "classifier_source": "rule_pack+phase1_induction",
  "ai_bootstrap_used": false,
  "ai_bootstrap_status": "not_used",
  "ai_bootstrap_confidence_summary": {},
  "inspect_report_note": "",
  "ai_bootstrap_error": "",
  "ai_bootstrap_raw_response_preview": "",
  "ai_bootstrap_validation_errors": [],
  "ai_bootstrap_prompt_version": "",
  "ai_bootstrap_model": "",
  "ai_bootstrap_provider": "",
  "ai_bootstrap_config_source": "",
  "default_problem_type_used": false,
  "problem_type_spec_first": true,
  "spec_defined_problem_type_ids": [
    "evaluate_function_value_2",
    "interpret_function_notation_2"
  ],
  "spec_mode": "induce_from_sources",
  "induced_problem_type_specs": [
    {
      "problem_type_id": "evaluate_function_value_2",
      "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
      "target_task": "evaluate_function_value",
      "task_family": "function_concept_family",
      "display_name": "evaluate_function_value / anchor bootstrap",
      "answer_format_hint": "expression",
      "source_example_ids": [],
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "answer_equivalence": "algebraic_equivalent",
        "equivalence_type": "algebraic_equivalent",
        "checker": "expression_checker",
        "checker_key": "expression_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "expression_checker",
        "checker_selection_reason": "quadratic_factoring_expression",
        "accepted_formats": [
          "(x-5)(x+3)",
          "(2x-1)(x+5)",
          "2(x-1)(3x+2)"
        ],
        "answer_semantics": "algebraic_expression"
      },
      "stem_contract": {
        "stem_must_not_embed_choices": true,
        "allowed_math_objects": [
          "quadratic_inequality"
        ],
        "required_math_objects": [
          "quadratic_inequality"
        ],
        "forbidden_patterns": [
          "\\(A\\)",
          "\\(B\\)",
          "\\(C\\)",
          "\\(D\\)"
        ]
      },
      "dependency_contract": {
        "givens_must_be_used": true,
        "target_answer_must_depend_on_givens": true,
        "variables_in_conditions_must_appear_in_target": false
      },
      "semantic_contract": {
        "reasoning_type": [
          "evaluate_function_value"
        ],
        "reject_if": [
          "unused_condition",
          "ambiguous_answer",
          "answer_not_derivable"
        ]
      },
      "generator_contract": {
        "template_variants": [
          {
            "id": "default",
            "label": "default",
            "stem_pattern": "依題意求解：{stem_hint}。",
            "weight": 1.0,
            "enabled": true
          }
        ],
        "parameter_schema": {
          "seed": {
            "type": "integer",
            "randomize": true
          },
          "difficulty_level": {
            "choices": [
              "level_1",
              "level_2",
              "level_3"
            ],
            "weights": [
              0.4,
              0.4,
              0.2
            ]
          }
        },
        "variation_dimensions": [
          "seed",
          "difficulty_level",
          "context_style"
        ],
        "difficulty_controls": {
          "level_1": {},
          "level_2": {},
          "level_3": {}
        },
        "anti_repetition_rules": {
          "avoid_same_template_consecutive": true,
          "avoid_same_ratio_consecutive": true,
          "avoid_same_point_names_consecutive": true,
          "avoid_same_answer_consecutive": true,
          "recent_history_window": 5,
          "signature_fields": [
            "problem_type_id",
            "template_variant",
            "routing_track",
            "scenario_type",
            "ratio_form",
            "ratio_values",
            "coordinate_pattern",
            "answer"
          ]
        },
        "validity_constraints": [
          "answer derivable from givens"
        ],
        "answer_shape": "numeric",
        "explanation_variants": [
          "stepwise"
        ],
        "sampling_strategy": "weighted_random",
        "template_families": [
          "evaluate_function_value"
        ],
        "parameter_slots": {
          "seed": "integer",
          "difficulty": "easy"
        },
        "randomization_rules": {
          "shuffle_choices": false
        },
        "avoid_llm_freeform_math": true,
        "use_domain_functions": true,
        "derivation_steps_required": true,
        "template_slots": {
          "stem": "function_value_numeric"
        },
        "problem_type_id": "evaluate_function_value_2",
        "contract_validation_blockers": [],
        "contract_validation_warnings": [
          "single_template_variant_only",
          "variation_dimensions_below_recommended_minimum"
        ]
      },
      "validator_contract": {
        "static_checks": [
          "answer_contract_checks"
        ],
        "semantic_checks": [
          "givens_to_target_dependency"
        ],
        "runtime_smoke_count": 30
      },
      "spec_source": "anchor_slot_bootstrap",
      "grouping_reason": "anchor_subskill_bootstrap_zero_source",
      "feature_signature": [
        "anchor_slot_bootstrap",
        "evaluate_function_value"
      ],
      "canonical_base_problem_type_id": "evaluate_function_value_2",
      "value_type_prefix": "",
      "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
    },
    {
      "problem_type_id": "interpret_function_notation_2",
      "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
      "target_task": "interpret_function_notation",
      "task_family": "function_concept_family",
      "display_name": "interpret_function_notation / anchor bootstrap",
      "answer_format_hint": "expression",
      "source_example_ids": [],
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "answer_equivalence": "algebraic_equivalent",
        "equivalence_type": "algebraic_equivalent",
        "checker": "expression_checker",
        "checker_key": "expression_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "expression_checker",
        "checker_selection_reason": "quadratic_factoring_expression",
        "accepted_formats": [
          "(x-5)(x+3)",
          "(2x-1)(x+5)",
          "2(x-1)(3x+2)"
        ],
        "answer_semantics": "algebraic_expression"
      },
      "stem_contract": {
        "stem_must_not_embed_choices": true,
        "allowed_math_objects": [
          "quadratic_inequality"
        ],
        "required_math_objects": [
          "quadratic_inequality"
        ],
        "forbidden_patterns": [
          "\\(A\\)",
          "\\(B\\)",
          "\\(C\\)",
          "\\(D\\)"
        ]
      },
      "dependency_contract": {
        "givens_must_be_used": true,
        "target_answer_must_depend_on_givens": true,
        "variables_in_conditions_must_appear_in_target": false
      },
      "semantic_contract": {
        "reasoning_type": [
          "interpret_function_notation"
        ],
        "reject_if": [
          "unused_condition",
          "ambiguous_answer",
          "answer_not_derivable"
        ]
      },
      "generator_contract": {
        "template_variants": [
          {
            "id": "default",
            "label": "default",
            "stem_pattern": "依題意求解：{stem_hint}。",
            "weight": 1.0,
            "enabled": true
          }
        ],
        "parameter_schema": {
          "seed": {
            "type": "integer",
            "randomize": true
          },
          "difficulty_level": {
            "choices": [
              "level_1",
              "level_2",
              "level_3"
            ],
            "weights": [
              0.4,
              0.4,
              0.2
            ]
          }
        },
        "variation_dimensions": [
          "seed",
          "difficulty_level",
          "context_style"
        ],
        "difficulty_controls": {
          "level_1": {},
          "level_2": {},
          "level_3": {}
        },
        "anti_repetition_rules": {
          "avoid_same_template_consecutive": true,
          "avoid_same_ratio_consecutive": true,
          "avoid_same_point_names_consecutive": true,
          "avoid_same_answer_consecutive": true,
          "recent_history_window": 5,
          "signature_fields": [
            "problem_type_id",
            "template_variant",
            "routing_track",
            "scenario_type",
            "ratio_form",
            "ratio_values",
            "coordinate_pattern",
            "answer"
          ]
        },
        "validity_constraints": [
          "answer derivable from givens"
        ],
        "answer_shape": "numeric",
        "explanation_variants": [
          "stepwise"
        ],
        "sampling_strategy": "weighted_random",
        "template_families": [
          "interpret_function_notation"
        ],
        "parameter_slots": {
          "seed": "integer",
          "difficulty": "easy"
        },
        "randomization_rules": {
          "shuffle_choices": false
        },
        "avoid_llm_freeform_math": true,
        "use_domain_functions": true,
        "derivation_steps_required": true,
        "template_slots": {
          "stem": "linear_function_two_point_choice"
        },
        "problem_type_id": "interpret_function_notation_2",
        "contract_validation_blockers": [],
        "contract_validation_warnings": [
          "single_template_variant_only",
          "variation_dimensions_below_recommended_minimum"
        ]
      },
      "validator_contract": {
        "static_checks": [
          "answer_contract_checks"
        ],
        "semantic_checks": [
          "givens_to_target_dependency"
        ],
        "runtime_smoke_count": 30
      },
      "spec_source": "anchor_slot_bootstrap",
      "grouping_reason": "anchor_subskill_bootstrap_zero_source",
      "feature_signature": [
        "anchor_slot_bootstrap",
        "interpret_function_notation"
      ],
      "canonical_base_problem_type_id": "interpret_function_notation_2",
      "value_type_prefix": "",
      "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
    }
  ],
  "induction_clusters": [
    {
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "short_answer",
        "classify_quadrant",
        "short_answer",
        [
          "sign_reasoning"
        ],
        [
          "symbolic_condition",
          "coordinate_point"
        ],
        "default"
      ],
      "source_example_ids": [
        4417
      ],
      "answer_type": "short_answer",
      "presentation_mode": "short_answer",
      "source_has_choices": false
    },
    {
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "short_answer",
        "compute_numeric",
        "short_answer",
        [
          "sign_reasoning"
        ],
        [
          "symbolic_condition",
          "coordinate_point"
        ],
        "default"
      ],
      "source_example_ids": [
        4435
      ],
      "answer_type": "short_answer",
      "presentation_mode": "short_answer",
      "source_has_choices": false
    },
    {
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "single_choice",
        "compute_distance_between_two_points",
        "single_choice",
        [
          "axis_distance_reasoning",
          "distance_formula_reasoning"
        ],
        [
          "axis_distance",
          "coordinate_point"
        ],
        "default"
      ],
      "source_example_ids": [
        4509
      ],
      "answer_type": "single_choice",
      "presentation_mode": "single_choice",
      "source_has_choices": true
    },
    {
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "single_choice",
        "choose_correct_statement",
        "single_choice",
        [
          "sign_reasoning"
        ],
        [
          "coordinate_point",
          "three_coordinate_points"
        ],
        "default"
      ],
      "source_example_ids": [
        4510
      ],
      "answer_type": "single_choice",
      "presentation_mode": "single_choice",
      "source_has_choices": true
    }
  ],
  "human_review_items": [],
  "source_quality_reject_examples": [],
  "proposal_items": [
    {
      "problem_type_id": "evaluate_function_value_2",
      "proposed_problem_type_id": "evaluate_function_value_2",
      "display_name": "evaluate_function_value / anchor bootstrap",
      "matched_example_ids": [],
      "matched_example_count": 0,
      "unmatched_example_ids": [],
      "representative_example_id": null,
      "structural_features": [
        "factored_expression"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "answer_equivalence": "algebraic_equivalent",
        "equivalence_type": "algebraic_equivalent",
        "checker": "expression_checker",
        "checker_key": "expression_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "expression_checker",
        "checker_selection_reason": "quadratic_factoring_expression",
        "accepted_formats": [
          "(x-5)(x+3)",
          "(2x-1)(x+5)",
          "2(x-1)(3x+2)"
        ],
        "answer_semantics": "algebraic_expression",
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
          ],
          "forbidden_patterns": [
            "\\(A\\)",
            "\\(B\\)",
            "\\(C\\)",
            "\\(D\\)"
          ]
        },
        "dependency_contract": {
          "givens_must_be_used": true,
          "target_answer_must_depend_on_givens": true,
          "variables_in_conditions_must_appear_in_target": false
        },
        "semantic_contract": {
          "reasoning_type": [
            "evaluate_function_value"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
          ]
        },
        "generator_contract": {
          "template_variants": [
            {
              "id": "default",
              "label": "default",
              "stem_pattern": "依題意求解：{stem_hint}。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "seed": {
              "type": "integer",
              "randomize": true
            },
            "difficulty_level": {
              "choices": [
                "level_1",
                "level_2",
                "level_3"
              ],
              "weights": [
                0.4,
                0.4,
                0.2
              ]
            }
          },
          "variation_dimensions": [
            "seed",
            "difficulty_level",
            "context_style"
          ],
          "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {}
          },
          "anti_repetition_rules": {
            "avoid_same_template_consecutive": true,
            "avoid_same_ratio_consecutive": true,
            "avoid_same_point_names_consecutive": true,
            "avoid_same_answer_consecutive": true,
            "recent_history_window": 5,
            "signature_fields": [
              "problem_type_id",
              "template_variant",
              "routing_track",
              "scenario_type",
              "ratio_form",
              "ratio_values",
              "coordinate_pattern",
              "answer"
            ]
          },
          "validity_constraints": [
            "answer derivable from givens"
          ],
          "answer_shape": "numeric",
          "explanation_variants": [
            "stepwise"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "evaluate_function_value"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "template_slots": {
            "stem": "function_value_numeric"
          },
          "problem_type_id": "evaluate_function_value_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "expression"
      },
      "checker_key_proposal": "expression_checker",
      "equivalence_type_proposal": "algebraic_equivalent",
      "answer_shape": "factored_expression",
      "answer_semantics": "algebraic_expression",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "expression_checker",
      "checker_selection_reason": "quadratic_factoring_expression",
      "confidence": "medium",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "alignment_score_below_recommended_threshold",
        "anchor_slot_bootstrap_zero_source",
        "anchor_taxonomy_needs_refinement",
        "candidate_family_span_outside_skill_scope",
        "mixed_source_families",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ],
      "checker_contract_warnings": [],
      "spec_source": "anchor_slot_bootstrap",
      "grouping_reason": "anchor_subskill_bootstrap_zero_source",
      "feature_signature": [
        "anchor_slot_bootstrap",
        "evaluate_function_value"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "evaluate_function_value_2",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "target_task": "evaluate_function_value",
        "task_family": "function_concept_family",
        "display_name": "evaluate_function_value / anchor bootstrap",
        "answer_format_hint": "expression",
        "source_example_ids": [],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "expression",
          "answer_shape": "factored_expression",
          "answer_equivalence": "algebraic_equivalent",
          "equivalence_type": "algebraic_equivalent",
          "checker": "expression_checker",
          "checker_key": "expression_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "expression_checker",
          "checker_selection_reason": "quadratic_factoring_expression",
          "accepted_formats": [
            "(x-5)(x+3)",
            "(2x-1)(x+5)",
            "2(x-1)(3x+2)"
          ],
          "answer_semantics": "algebraic_expression"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
          ],
          "forbidden_patterns": [
            "\\(A\\)",
            "\\(B\\)",
            "\\(C\\)",
            "\\(D\\)"
          ]
        },
        "dependency_contract": {
          "givens_must_be_used": true,
          "target_answer_must_depend_on_givens": true,
          "variables_in_conditions_must_appear_in_target": false
        },
        "semantic_contract": {
          "reasoning_type": [
            "evaluate_function_value"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
          ]
        },
        "generator_contract": {
          "template_variants": [
            {
              "id": "default",
              "label": "default",
              "stem_pattern": "依題意求解：{stem_hint}。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "seed": {
              "type": "integer",
              "randomize": true
            },
            "difficulty_level": {
              "choices": [
                "level_1",
                "level_2",
                "level_3"
              ],
              "weights": [
                0.4,
                0.4,
                0.2
              ]
            }
          },
          "variation_dimensions": [
            "seed",
            "difficulty_level",
            "context_style"
          ],
          "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {}
          },
          "anti_repetition_rules": {
            "avoid_same_template_consecutive": true,
            "avoid_same_ratio_consecutive": true,
            "avoid_same_point_names_consecutive": true,
            "avoid_same_answer_consecutive": true,
            "recent_history_window": 5,
            "signature_fields": [
              "problem_type_id",
              "template_variant",
              "routing_track",
              "scenario_type",
              "ratio_form",
              "ratio_values",
              "coordinate_pattern",
              "answer"
            ]
          },
          "validity_constraints": [
            "answer derivable from givens"
          ],
          "answer_shape": "numeric",
          "explanation_variants": [
            "stepwise"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "evaluate_function_value"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "template_slots": {
            "stem": "function_value_numeric"
          },
          "problem_type_id": "evaluate_function_value_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "anchor_slot_bootstrap",
        "grouping_reason": "anchor_subskill_bootstrap_zero_source",
        "feature_signature": [
          "anchor_slot_bootstrap",
          "evaluate_function_value"
        ],
        "canonical_base_problem_type_id": "evaluate_function_value_2",
        "value_type_prefix": "",
        "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
      },
      "generator_readiness": "runtime_ready",
      "usable_for_phase3": true,
      "template_slot": "function_value_numeric",
      "canonical_base_problem_type_id": "evaluate_function_value_2",
      "value_type_prefix": "",
      "subskill_id": "evaluate_function_value",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0,
        "task_consistent_with_skill": true
      },
      "answer_type": "expression"
    },
    {
      "problem_type_id": "interpret_function_notation_2",
      "proposed_problem_type_id": "interpret_function_notation_2",
      "display_name": "interpret_function_notation / anchor bootstrap",
      "matched_example_ids": [],
      "matched_example_count": 0,
      "unmatched_example_ids": [],
      "representative_example_id": null,
      "structural_features": [
        "factored_expression"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "answer_equivalence": "algebraic_equivalent",
        "equivalence_type": "algebraic_equivalent",
        "checker": "expression_checker",
        "checker_key": "expression_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "expression_checker",
        "checker_selection_reason": "quadratic_factoring_expression",
        "accepted_formats": [
          "(x-5)(x+3)",
          "(2x-1)(x+5)",
          "2(x-1)(3x+2)"
        ],
        "answer_semantics": "algebraic_expression",
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
          ],
          "forbidden_patterns": [
            "\\(A\\)",
            "\\(B\\)",
            "\\(C\\)",
            "\\(D\\)"
          ]
        },
        "dependency_contract": {
          "givens_must_be_used": true,
          "target_answer_must_depend_on_givens": true,
          "variables_in_conditions_must_appear_in_target": false
        },
        "semantic_contract": {
          "reasoning_type": [
            "interpret_function_notation"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
          ]
        },
        "generator_contract": {
          "template_variants": [
            {
              "id": "default",
              "label": "default",
              "stem_pattern": "依題意求解：{stem_hint}。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "seed": {
              "type": "integer",
              "randomize": true
            },
            "difficulty_level": {
              "choices": [
                "level_1",
                "level_2",
                "level_3"
              ],
              "weights": [
                0.4,
                0.4,
                0.2
              ]
            }
          },
          "variation_dimensions": [
            "seed",
            "difficulty_level",
            "context_style"
          ],
          "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {}
          },
          "anti_repetition_rules": {
            "avoid_same_template_consecutive": true,
            "avoid_same_ratio_consecutive": true,
            "avoid_same_point_names_consecutive": true,
            "avoid_same_answer_consecutive": true,
            "recent_history_window": 5,
            "signature_fields": [
              "problem_type_id",
              "template_variant",
              "routing_track",
              "scenario_type",
              "ratio_form",
              "ratio_values",
              "coordinate_pattern",
              "answer"
            ]
          },
          "validity_constraints": [
            "answer derivable from givens"
          ],
          "answer_shape": "numeric",
          "explanation_variants": [
            "stepwise"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "interpret_function_notation"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "template_slots": {
            "stem": "linear_function_two_point_choice"
          },
          "problem_type_id": "interpret_function_notation_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "expression"
      },
      "checker_key_proposal": "expression_checker",
      "equivalence_type_proposal": "algebraic_equivalent",
      "answer_shape": "factored_expression",
      "answer_semantics": "algebraic_expression",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "expression_checker",
      "checker_selection_reason": "quadratic_factoring_expression",
      "confidence": "medium",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "alignment_score_below_recommended_threshold",
        "anchor_slot_bootstrap_zero_source",
        "anchor_taxonomy_needs_refinement",
        "candidate_family_span_outside_skill_scope",
        "mixed_source_families",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ],
      "checker_contract_warnings": [],
      "spec_source": "anchor_slot_bootstrap",
      "grouping_reason": "anchor_subskill_bootstrap_zero_source",
      "feature_signature": [
        "anchor_slot_bootstrap",
        "interpret_function_notation"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "interpret_function_notation_2",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "target_task": "interpret_function_notation",
        "task_family": "function_concept_family",
        "display_name": "interpret_function_notation / anchor bootstrap",
        "answer_format_hint": "expression",
        "source_example_ids": [],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "expression",
          "answer_shape": "factored_expression",
          "answer_equivalence": "algebraic_equivalent",
          "equivalence_type": "algebraic_equivalent",
          "checker": "expression_checker",
          "checker_key": "expression_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "expression_checker",
          "checker_selection_reason": "quadratic_factoring_expression",
          "accepted_formats": [
            "(x-5)(x+3)",
            "(2x-1)(x+5)",
            "2(x-1)(3x+2)"
          ],
          "answer_semantics": "algebraic_expression"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
          ],
          "forbidden_patterns": [
            "\\(A\\)",
            "\\(B\\)",
            "\\(C\\)",
            "\\(D\\)"
          ]
        },
        "dependency_contract": {
          "givens_must_be_used": true,
          "target_answer_must_depend_on_givens": true,
          "variables_in_conditions_must_appear_in_target": false
        },
        "semantic_contract": {
          "reasoning_type": [
            "interpret_function_notation"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
          ]
        },
        "generator_contract": {
          "template_variants": [
            {
              "id": "default",
              "label": "default",
              "stem_pattern": "依題意求解：{stem_hint}。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "seed": {
              "type": "integer",
              "randomize": true
            },
            "difficulty_level": {
              "choices": [
                "level_1",
                "level_2",
                "level_3"
              ],
              "weights": [
                0.4,
                0.4,
                0.2
              ]
            }
          },
          "variation_dimensions": [
            "seed",
            "difficulty_level",
            "context_style"
          ],
          "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {}
          },
          "anti_repetition_rules": {
            "avoid_same_template_consecutive": true,
            "avoid_same_ratio_consecutive": true,
            "avoid_same_point_names_consecutive": true,
            "avoid_same_answer_consecutive": true,
            "recent_history_window": 5,
            "signature_fields": [
              "problem_type_id",
              "template_variant",
              "routing_track",
              "scenario_type",
              "ratio_form",
              "ratio_values",
              "coordinate_pattern",
              "answer"
            ]
          },
          "validity_constraints": [
            "answer derivable from givens"
          ],
          "answer_shape": "numeric",
          "explanation_variants": [
            "stepwise"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "interpret_function_notation"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "template_slots": {
            "stem": "linear_function_two_point_choice"
          },
          "problem_type_id": "interpret_function_notation_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "anchor_slot_bootstrap",
        "grouping_reason": "anchor_subskill_bootstrap_zero_source",
        "feature_signature": [
          "anchor_slot_bootstrap",
          "interpret_function_notation"
        ],
        "canonical_base_problem_type_id": "interpret_function_notation_2",
        "value_type_prefix": "",
        "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
      },
      "generator_readiness": "runtime_ready",
      "usable_for_phase3": true,
      "template_slot": "linear_function_two_point_choice",
      "canonical_base_problem_type_id": "interpret_function_notation_2",
      "value_type_prefix": "",
      "subskill_id": "interpret_function_notation",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0,
        "task_consistent_with_skill": true
      },
      "answer_type": "expression"
    }
  ],
  "candidate_problem_type_count": 2,
  "source_skill_scope_locked": true,
  "classification_scope": "within_current_skill",
  "skill_mapping_authority": "textbook_examples.skill_id",
  "human_confirmed_rule_pack_applied": false,
  "ai_classification_overridden_by_human_confirmed_rule_pack": false,
  "supporting_math_objects": [],
  "report_contract_status": "PASS_WITH_WARNINGS",
  "report_contract_warnings": [
    "candidate_problem_type_count_synchronized"
  ],
  "report_contract_violations": [],
  "problem_type_grouping_contract_status": "PASS",
  "problem_type_grouping_contract_warnings": [],
  "problem_type_grouping_contract_violations": []
}
```
