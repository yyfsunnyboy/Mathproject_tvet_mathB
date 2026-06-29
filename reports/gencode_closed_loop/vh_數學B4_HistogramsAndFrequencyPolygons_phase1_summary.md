# Gencode Phase1 Summary: vh_數學B4_HistogramsAndFrequencyPolygons

## SOP Policy Reference

- **SOP Policy Version**: `v0.3`
- **Highest SOP**: `docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.3.md`
- **SOP Preflight Status**: `PASS`
- **SOP Gate Status**: `PASS`
- **Report Contract Status**: `PASS_WITH_WARNINGS`
- **Report Contract Warnings**: ['candidate_problem_type_count_synchronized']
- **Report Contract Violations**: []

- spec_mode: `ai_first_induce_from_sources`

## Main skill anchor

- skill_ch_name: `次數分配直方圖與次數分配折線圖的繪製`
- expected_task_families: []
- expected_subskill_candidates: []
- skill_anchor_scope: `default`
- observed_source_family_distribution: {'generic_numeric_family': 3, 'quadratic_inequality_family': 1}
- observed_target_task_distribution: {'compute_numeric': 3, 'applied_quadratic_inequality_problem': 1}
- same_family_subskill_mismatch_examples: 0
- examples_outside_expected_subskills: []
- suggested_action: ``

## Source alignment

- source_alignment_status: `warn`
- skill_problem_type_alignment_status: `warn`
- alignment_score: `0.0`
- alignment_blockers: []
- alignment_warnings: ['ai_first_mode_fell_back_to_rule_only', 'ai_partial_unavailable_relaxed_tolerance', 'ai_unavailable_fallback_to_same_as_main', 'alignment_score_below_recommended_threshold']

| example_id | target_task | task_family | alignment_kind | subskill_match | included | exclude_reason | stem_preview |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3826 | compute_numeric | generic_numeric_family | unresolved_within_current_skill | False | True |  | 國貿科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補） |
| 3827 | compute_numeric | generic_numeric_family | unresolved_within_current_skill | False | True |  | 會計科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補） |
| 3828 | compute_numeric | generic_numeric_family | unresolved_within_current_skill | False | True |  | 某女中二年八班同學的體重次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。體重(kg)：40~45(2人), 45~ |
| 3829 | applied_quadratic_inequality_problem | quadratic_inequality_family | unresolved_within_current_skill | False | True |  | 某幼兒園班上25位小朋友身高分布之直方圖如右。今班上轉出一位身高117公分之小朋友，轉入一位身高112公分之小朋友，則此 |

## AI semantic classification

- ai_semantic_status: `unavailable`

| example_id | ai_task | ai_family | ai_conf | rule_task | rule_family | final_task | final_family | source | conflict | human |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3826 |  |  | 0.0 | compute_numeric | generic_numeric_family | compute_numeric | generic_numeric_family | rule_fallback_ai_unavailable | ai_api_key_missing | True |
| 3827 |  |  | 0.0 | compute_numeric | generic_numeric_family | compute_numeric | generic_numeric_family | rule_fallback_ai_unavailable | ai_api_key_missing | True |
| 3828 |  |  | 0.0 | compute_numeric | generic_numeric_family | compute_numeric | generic_numeric_family | rule_fallback_ai_unavailable | ai_api_key_missing | True |
| 3829 |  |  | 0.0 | applied_quadratic_inequality_problem | quadratic_inequality_family | applied_quadratic_inequality_problem | quadratic_inequality_family | rule_fallback_ai_unavailable | ai_api_key_missing | True |

> AI 語意分類未執行：missing_api_key。已退回 rule fallback，請先設定 AI key 後重新執行 Phase 1。
## Classification diagnostics (per example)

| id | rule_task/family | AI task/family | conf | source | final task/family | align | excluded |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3826 | compute_numeric/generic_numeric_family | / | 0.0 | rule_fallback_ai_unavailable | compute_numeric/generic_numeric_family | unresolved_within_current_skill |  |
| 3827 | compute_numeric/generic_numeric_family | / | 0.0 | rule_fallback_ai_unavailable | compute_numeric/generic_numeric_family | unresolved_within_current_skill |  |
| 3828 | compute_numeric/generic_numeric_family | / | 0.0 | rule_fallback_ai_unavailable | compute_numeric/generic_numeric_family | unresolved_within_current_skill |  |
| 3829 | applied_quadratic_inequality_problem/quadratic_inequality_family | / | 0.0 | rule_fallback_ai_unavailable | applied_quadratic_inequality_problem/quadratic_inequality_family | unresolved_within_current_skill |  |


## Example / practice links

[{'practice_label': '隨堂練習2', 'linked_example': '例題2', 'example_id': 3827}]

## Same-section family distribution

{'generic_numeric_family': 3, 'quadratic_inequality_family': 1}

## Example features

| example_id | answer_type | target_task | has_choices | stem_embeds_choices | math_objects |
| --- | --- | --- | --- | --- | --- |
| 3826 | text_short | compute_numeric | False | False |  |
| 3827 | text_short | compute_numeric | False | False |  |
| 3828 | text_short | compute_numeric | False | False |  |
| 3829 | text_short | applied_quadratic_inequality_problem | False | False |  |

## Induction clusters

### Cluster 1
- answer_type: `short_answer`
- source_example_ids: [3826, 3827, 3828]
- grouping_reason: split_by_feature_signature
- feature_signature: `['short_answer', 'compute_numeric', 'short_answer', ('numeric_computation',), (), 'default']`

### Cluster 2
- answer_type: `short_answer`
- source_example_ids: [3829]
- grouping_reason: split_by_feature_signature
- feature_signature: `['short_answer', 'applied_quadratic_inequality_problem', 'short_answer', ('quadratic_factoring_reasoning',), (), 'default']`


## Candidate problem types

| problem_type_id | display_name | answer_type | source_examples | grouping_reason |
| --- | --- | --- | --- | --- |
| text_short_compute_numeric | text_short / compute_numeric | text_short | [3826, 3827, 3828] | split_by_feature_signature |
| unresolved_within_current_skill | text_short / applied_quadratic_inequality_problem | interval | [3829] | split_by_feature_signature |

## phase1
```json
{
  "ok": true,
  "phase": "phase1",
  "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
    "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
    "skill_ch_name": "次數分配直方圖與次數分配折線圖的繪製",
    "skill_en_name": "HistogramsAndFrequencyPolygons",
    "chapter": "3 統計",
    "section": "3-2 統計資料整理",
    "normalized_skill_terms": [
      "2 統計資料整理",
      "3 統計",
      "and",
      "andfrequencypolygon",
      "frequency",
      "hi",
      "histograms",
      "histogramsandfrequencypolygons",
      "polygons",
      "togram",
      "vh",
      "vocational",
      "數學b",
      "數學b4",
      "次數分配直方圖與次數分配折線圖的繪製",
      "統計",
      "統計資料整理"
    ],
    "expected_task_families": [],
    "expected_math_objects": [],
    "expected_subskill_candidates": [],
    "skill_anchor_scope": "default",
    "fallback_subskill": {
      "subskill_id": "same_as_main_skill",
      "subskill_name": "次數分配直方圖與次數分配折線圖的繪製",
      "subskill_scope": "fallback",
      "display_note": "此子技能為 fallback，用於收納未細分或綜合題"
    },
    "source_belongs_to_current_skill_by_default": true,
    "source_skill_scope_locked": true,
    "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
    "classification_scope": "within_current_skill",
    "skill_mapping_authority": "textbook_examples.skill_id",
    "anchor_authority": "skill_id_derived_no_cross_family_pollution",
    "classification_mandate": "【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\n【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\nTrusted skill anchor (do not override):\n- skill_id: vh_數學B4_HistogramsAndFrequencyPolygons\n- skill_ch_name: 次數分配直方圖與次數分配折線圖的繪製\n- skill_en_name: HistogramsAndFrequencyPolygons\n- expected_task_families: []\n- expected_subskill_candidates: []\n- skill_anchor_scope: default\n- source_skill_scope_locked: True\n"
  },
  "source_example_count": 4,
  "source_alignment_status": "warn",
  "skill_problem_type_alignment_status": "warn",
  "alignment_score": 0.0,
  "alignment_warnings": [
    "ai_first_mode_fell_back_to_rule_only",
    "ai_partial_unavailable_relaxed_tolerance",
    "ai_unavailable_fallback_to_same_as_main",
    "alignment_score_below_recommended_threshold"
  ],
  "alignment_blockers": [],
  "semantic_alignment": {
    "main_skill_anchor": {
      "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
      "skill_ch_name": "次數分配直方圖與次數分配折線圖的繪製",
      "skill_en_name": "HistogramsAndFrequencyPolygons",
      "chapter": "3 統計",
      "section": "3-2 統計資料整理",
      "normalized_skill_terms": [
        "2 統計資料整理",
        "3 統計",
        "and",
        "andfrequencypolygon",
        "frequency",
        "hi",
        "histograms",
        "histogramsandfrequencypolygons",
        "polygons",
        "togram",
        "vh",
        "vocational",
        "數學b",
        "數學b4",
        "次數分配直方圖與次數分配折線圖的繪製",
        "統計",
        "統計資料整理"
      ],
      "expected_task_families": [],
      "expected_math_objects": [],
      "expected_subskill_candidates": [],
      "skill_anchor_scope": "default",
      "fallback_subskill": {
        "subskill_id": "same_as_main_skill",
        "subskill_name": "次數分配直方圖與次數分配折線圖的繪製",
        "subskill_scope": "fallback",
        "display_note": "此子技能為 fallback，用於收納未細分或綜合題"
      },
      "source_belongs_to_current_skill_by_default": true,
      "source_skill_scope_locked": true,
      "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
      "classification_scope": "within_current_skill",
      "skill_mapping_authority": "textbook_examples.skill_id",
      "anchor_authority": "skill_id_derived_no_cross_family_pollution",
      "classification_mandate": "【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\n【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\nTrusted skill anchor (do not override):\n- skill_id: vh_數學B4_HistogramsAndFrequencyPolygons\n- skill_ch_name: 次數分配直方圖與次數分配折線圖的繪製\n- skill_en_name: HistogramsAndFrequencyPolygons\n- expected_task_families: []\n- expected_subskill_candidates: []\n- skill_anchor_scope: default\n- source_skill_scope_locked: True\n"
    },
    "ai_semantic_status": "unavailable",
    "skill_terms": [
      "2 統計資料整理",
      "3 統計",
      "and",
      "andfrequencypolygon",
      "frequency",
      "hi",
      "histograms",
      "histogramsandfrequencypolygons",
      "polygons",
      "togram",
      "vh",
      "vocational",
      "數學b",
      "數學b4",
      "次數分配直方圖與次數分配折線圖的繪製",
      "統計",
      "統計資料整理"
    ],
    "source_terms": [
      "10人",
      "11人",
      "2人",
      "3人",
      "40",
      "45",
      "50",
      "55",
      "5人",
      "60",
      "65",
      "70",
      "75",
      "7人",
      "applied_quadratic_inequality_problem",
      "compute_numeric",
      "kg",
      "short_answer",
      "今班上轉出一位身高117公分之小朋友",
      "則此時班上小朋友身高分布之直方圖為何",
      "國貿科三年甲班模擬考某科成績的次數分配表如下",
      "圖片待補",
      "會計科三年甲班模擬考某科成績的次數分配表如下",
      "某女中二年八班同學的體重次數分配表如下",
      "某幼兒園班上25位小朋友身高分布之直方圖如右",
      "試畫出其對應的直方圖與次數分配折線圖",
      "轉入一位身高112公分之小朋友",
      "體重"
    ],
    "expected_subskill_candidates": [],
    "observed_target_task_distribution": {
      "compute_numeric": 3,
      "applied_quadratic_inequality_problem": 1
    },
    "same_family_subskill_mismatch_examples": [],
    "examples_outside_expected_subskills": [],
    "suggested_action": "",
    "examples_outside_expected_family": [],
    "problem_type_terms": [
      "an",
      "answer",
      "applied",
      "applied_quadratic_inequality_problem",
      "compute",
      "compute_numeric",
      "hort",
      "inequality",
      "interval",
      "numeric",
      "numeric_computation",
      "point_quadrant",
      "problem",
      "quadratic",
      "quadratic_factoring_reasoning",
      "short",
      "short_answer / applied_quadratic_inequality_problem",
      "short_answer / compute_numeric",
      "solve_absolute_value_inequality",
      "text_short",
      "wer"
    ],
    "expected_task_candidates": [],
    "expected_skill_families": [],
    "observed_source_family_distribution": {
      "generic_numeric_family": 3,
      "quadratic_inequality_family": 1
    },
    "source_family_distribution": {
      "generic_numeric_family": 3,
      "quadratic_inequality_family": 1
    },
    "candidate_problem_type_families": [
      "generic_numeric_family",
      "quadratic_inequality_family"
    ],
    "dominant_source_task": "compute_numeric",
    "dominant_source_task_ratio": 0.75,
    "uniform_core_target_task": "compute_numeric",
    "uniform_core_target_task_ratio": 0.75,
    "uniform_core_target_task_count": 4,
    "uniform_core_threshold_relaxed": false,
    "dominant_source_family": [
      "generic_numeric_family"
    ],
    "dominant_source_family_ratio": 0.75,
    "skill_source_score": 0.0,
    "skill_problem_type_score": 0.0,
    "source_problem_type_score": 0.0256,
    "per_problem_type_scores": [
      {
        "problem_type_id": "short_answer_compute_numeric_short_answer",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "inferred_tasks": [
          "compute_numeric"
        ],
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0256,
        "task_consistent_with_skill": true,
        "family_consistent_with_skill": true,
        "answer_contract_supported": true
      },
      {
        "problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "inferred_tasks": [
          "applied_quadratic_inequality_problem"
        ],
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0244,
        "task_consistent_with_skill": true,
        "family_consistent_with_skill": true,
        "answer_contract_supported": true
      }
    ],
    "decision": "warn",
    "blockers": [],
    "warnings": [
      "ai_first_mode_fell_back_to_rule_only",
      "ai_partial_unavailable_relaxed_tolerance",
      "ai_unavailable_fallback_to_same_as_main",
      "alignment_score_below_recommended_threshold"
    ],
    "induction_core_example_count": 4,
    "induction_enrichment_example_count": 0,
    "source_skill_scope_locked": true,
    "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
    "classification_scope": "within_current_skill",
    "skill_mapping_authority": "textbook_examples.skill_id",
    "core_skill_concept": "histogramsandfrequencypolygons",
    "supporting_math_objects": [],
    "source_quality_reject_examples": []
  },
  "source_family_distribution": {
    "generic_numeric_family": 3,
    "quadratic_inequality_family": 1
  },
  "candidate_problem_type_families": [
    "generic_numeric_family",
    "quadratic_inequality_family"
  ],
  "expected_skill_families": [],
  "expected_subskill_candidates": [],
  "observed_target_task_distribution": {
    "compute_numeric": 3,
    "applied_quadratic_inequality_problem": 1
  },
  "same_family_subskill_mismatch_examples": [],
  "examples_outside_expected_subskills": [],
  "suggested_action": "",
  "requires_human_action": true,
  "semantic_classifications": [
    {
      "example_id": 3826,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_best_candidate_id": "needs_review",
      "ai_evidence": [],
      "ai_rejected_candidates": {},
      "ai_available": false,
      "ai_error": "ai_api_key_missing",
      "ai_unavailable_reason": "missing_api_key",
      "ai_semantic_status": "unavailable",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "rule_target_task": "compute_numeric",
      "rule_task_family": "generic_numeric_family",
      "rule_confidence": 0.2,
      "final_target_task": "compute_numeric",
      "final_task_family": "generic_numeric_family",
      "classifier_source": "rule_fallback_ai_unavailable",
      "classification_decision": "",
      "conflict_reason": "ai_api_key_missing",
      "source_mapping_warning": "",
      "requires_human_action": true,
      "ai_notes": "",
      "skill_scoped_candidates": [
        {
          "candidate_id": "C1",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "problem_type_id": "compute_numeric",
          "label": "compute_numeric",
          "candidate_source": "outsider",
          "in_anchor_scope": false,
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "math_objects": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
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
              "compute_numeric"
            ]
          },
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
          }
        },
        {
          "candidate_id": "needs_review",
          "target_task": "",
          "task_family": "",
          "problem_type_id": "needs_review",
          "label": "needs_review",
          "candidate_source": "needs_review",
          "in_anchor_scope": false,
          "answer_type": "",
          "answer_shape": "",
          "math_objects": [],
          "checker_key": "manual_review_checker",
          "equivalence_type": "manual_review_or_ai_judged",
          "generator_contract": {},
          "parameter_schema": {}
        }
      ],
      "outsider_candidates": [
        "C1"
      ],
      "selected_subskill": "compute_numeric",
      "selected_problem_type": "compute_numeric",
      "candidate_source": "needs_review",
      "selected_generator_contract": {},
      "parameter_schema": {},
      "variable_randomization_notes": [],
      "checker_key": "",
      "equivalence_type": "",
      "skill_scope_trusted": true,
      "target_task": "compute_numeric",
      "task_family": "generic_numeric_family",
      "math_objects": [],
      "answer_type": "short_answer",
      "answer_shape": "text_short",
      "source_type": "worked_example",
      "example_label": "例題2",
      "practice_label": "",
      "linked_example": "",
      "linked_example_id": null,
      "linked_example_task_family": "",
      "structure_consistency": "not_applicable",
      "sequence_context_used": true,
      "structure_context_used": true,
      "confidence_adjustment_reason": "sequence_context_used",
      "possible_structure_mismatch": false,
      "possible_mixed_source_context": false
    },
    {
      "example_id": 3827,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_best_candidate_id": "needs_review",
      "ai_evidence": [],
      "ai_rejected_candidates": {},
      "ai_available": false,
      "ai_error": "ai_api_key_missing",
      "ai_unavailable_reason": "missing_api_key",
      "ai_semantic_status": "unavailable",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "rule_target_task": "compute_numeric",
      "rule_task_family": "generic_numeric_family",
      "rule_confidence": 0.2,
      "final_target_task": "compute_numeric",
      "final_task_family": "generic_numeric_family",
      "classifier_source": "rule_fallback_ai_unavailable",
      "classification_decision": "",
      "conflict_reason": "ai_api_key_missing",
      "source_mapping_warning": "",
      "requires_human_action": true,
      "ai_notes": "",
      "skill_scoped_candidates": [
        {
          "candidate_id": "C1",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "problem_type_id": "compute_numeric",
          "label": "compute_numeric",
          "candidate_source": "structure",
          "in_anchor_scope": false,
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "math_objects": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
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
              "compute_numeric"
            ]
          },
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
          }
        },
        {
          "candidate_id": "needs_review",
          "target_task": "",
          "task_family": "",
          "problem_type_id": "needs_review",
          "label": "needs_review",
          "candidate_source": "needs_review",
          "in_anchor_scope": false,
          "answer_type": "",
          "answer_shape": "",
          "math_objects": [],
          "checker_key": "manual_review_checker",
          "equivalence_type": "manual_review_or_ai_judged",
          "generator_contract": {},
          "parameter_schema": {}
        }
      ],
      "outsider_candidates": [],
      "selected_subskill": "compute_numeric",
      "selected_problem_type": "compute_numeric",
      "candidate_source": "needs_review",
      "selected_generator_contract": {},
      "parameter_schema": {},
      "variable_randomization_notes": [],
      "checker_key": "",
      "equivalence_type": "",
      "skill_scope_trusted": true,
      "target_task": "compute_numeric",
      "task_family": "generic_numeric_family",
      "math_objects": [],
      "answer_type": "short_answer",
      "answer_shape": "text_short",
      "source_type": "in_class_practice",
      "example_label": "",
      "practice_label": "隨堂練習2",
      "linked_example": "例題2",
      "linked_example_id": 3826,
      "linked_example_task_family": "generic_numeric_family",
      "structure_consistency": "consistent",
      "sequence_context_used": true,
      "structure_context_used": true,
      "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
      "possible_structure_mismatch": false,
      "possible_mixed_source_context": false
    },
    {
      "example_id": 3828,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_best_candidate_id": "needs_review",
      "ai_evidence": [],
      "ai_rejected_candidates": {},
      "ai_available": false,
      "ai_error": "ai_api_key_missing",
      "ai_unavailable_reason": "missing_api_key",
      "ai_semantic_status": "unavailable",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "rule_target_task": "compute_numeric",
      "rule_task_family": "generic_numeric_family",
      "rule_confidence": 0.2,
      "final_target_task": "compute_numeric",
      "final_task_family": "generic_numeric_family",
      "classifier_source": "rule_fallback_ai_unavailable",
      "classification_decision": "",
      "conflict_reason": "ai_api_key_missing",
      "source_mapping_warning": "",
      "requires_human_action": true,
      "ai_notes": "",
      "skill_scoped_candidates": [
        {
          "candidate_id": "C1",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "problem_type_id": "compute_numeric",
          "label": "compute_numeric",
          "candidate_source": "structure",
          "in_anchor_scope": false,
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "math_objects": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
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
              "compute_numeric"
            ]
          },
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
          }
        },
        {
          "candidate_id": "needs_review",
          "target_task": "",
          "task_family": "",
          "problem_type_id": "needs_review",
          "label": "needs_review",
          "candidate_source": "needs_review",
          "in_anchor_scope": false,
          "answer_type": "",
          "answer_shape": "",
          "math_objects": [],
          "checker_key": "manual_review_checker",
          "equivalence_type": "manual_review_or_ai_judged",
          "generator_contract": {},
          "parameter_schema": {}
        }
      ],
      "outsider_candidates": [],
      "selected_subskill": "compute_numeric",
      "selected_problem_type": "compute_numeric",
      "candidate_source": "needs_review",
      "selected_generator_contract": {},
      "parameter_schema": {},
      "variable_randomization_notes": [],
      "checker_key": "",
      "equivalence_type": "",
      "skill_scope_trusted": true,
      "target_task": "compute_numeric",
      "task_family": "generic_numeric_family",
      "math_objects": [],
      "answer_type": "short_answer",
      "answer_shape": "text_short",
      "source_type": "basic_exercise",
      "example_label": "",
      "practice_label": "",
      "linked_example": "",
      "linked_example_id": null,
      "linked_example_task_family": "",
      "structure_consistency": "not_applicable",
      "sequence_context_used": true,
      "structure_context_used": true,
      "confidence_adjustment_reason": "sequence_context_used",
      "possible_structure_mismatch": false,
      "possible_mixed_source_context": false
    },
    {
      "example_id": 3829,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_best_candidate_id": "needs_review",
      "ai_evidence": [],
      "ai_rejected_candidates": {},
      "ai_available": false,
      "ai_error": "ai_api_key_missing",
      "ai_unavailable_reason": "missing_api_key",
      "ai_semantic_status": "unavailable",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "rule_target_task": "applied_quadratic_inequality_problem",
      "rule_task_family": "quadratic_inequality_family",
      "rule_confidence": 0.5,
      "final_target_task": "applied_quadratic_inequality_problem",
      "final_task_family": "quadratic_inequality_family",
      "classifier_source": "rule_fallback_ai_unavailable",
      "classification_decision": "",
      "conflict_reason": "ai_api_key_missing",
      "source_mapping_warning": "",
      "requires_human_action": true,
      "ai_notes": "",
      "skill_scoped_candidates": [
        {
          "candidate_id": "C1",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "problem_type_id": "compute_numeric",
          "label": "compute_numeric",
          "candidate_source": "structure",
          "in_anchor_scope": false,
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "math_objects": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
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
              "compute_numeric"
            ]
          },
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
          }
        },
        {
          "candidate_id": "C2",
          "target_task": "applied_quadratic_inequality_problem",
          "task_family": "quadratic_inequality_family",
          "problem_type_id": "applied_quadratic_inequality_problem",
          "label": "applied_quadratic_inequality_problem",
          "candidate_source": "outsider",
          "in_anchor_scope": false,
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "math_objects": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
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
              "applied_quadratic_inequality_problem"
            ]
          },
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
          }
        },
        {
          "candidate_id": "needs_review",
          "target_task": "",
          "task_family": "",
          "problem_type_id": "needs_review",
          "label": "needs_review",
          "candidate_source": "needs_review",
          "in_anchor_scope": false,
          "answer_type": "",
          "answer_shape": "",
          "math_objects": [],
          "checker_key": "manual_review_checker",
          "equivalence_type": "manual_review_or_ai_judged",
          "generator_contract": {},
          "parameter_schema": {}
        }
      ],
      "outsider_candidates": [
        "C2"
      ],
      "selected_subskill": "applied_quadratic_inequality_problem",
      "selected_problem_type": "applied_quadratic_inequality_problem",
      "candidate_source": "needs_review",
      "selected_generator_contract": {},
      "parameter_schema": {},
      "variable_randomization_notes": [],
      "checker_key": "",
      "equivalence_type": "",
      "skill_scope_trusted": true,
      "target_task": "applied_quadratic_inequality_problem",
      "task_family": "quadratic_inequality_family",
      "math_objects": [],
      "answer_type": "short_answer",
      "answer_shape": "text_short",
      "source_type": "advanced_exercise",
      "example_label": "",
      "practice_label": "",
      "linked_example": "",
      "linked_example_id": null,
      "linked_example_task_family": "",
      "structure_consistency": "not_applicable",
      "sequence_context_used": true,
      "structure_context_used": true,
      "confidence_adjustment_reason": "possible_structure_mismatch_penalty; sequence_context_used",
      "possible_structure_mismatch": true,
      "possible_mixed_source_context": true
    }
  ],
  "ai_semantic_status": "unavailable",
  "source_type_distribution": {
    "worked_example": 1,
    "in_class_practice": 1,
    "basic_exercise": 1,
    "advanced_exercise": 1
  },
  "example_practice_link_map": [
    {
      "practice_label": "隨堂練習2",
      "linked_example": "例題2",
      "example_id": 3827
    }
  ],
  "structure_mismatch_examples": [],
  "same_section_family_distribution": {
    "generic_numeric_family": 3,
    "quadratic_inequality_family": 1
  },
  "source_structure_report": {
    "source_type_distribution": {
      "worked_example": 1,
      "in_class_practice": 1,
      "basic_exercise": 1,
      "advanced_exercise": 1
    },
    "example_practice_link_map": [
      {
        "practice_label": "隨堂練習2",
        "linked_example": "例題2",
        "example_id": 3827
      }
    ],
    "structure_mismatch_examples": [],
    "same_section_family_distribution": {
      "generic_numeric_family": 3,
      "quadratic_inequality_family": 1
    }
  },
  "classification_diagnostics": [
    {
      "example_id": 3826,
      "rule_target_task": "compute_numeric",
      "rule_task_family": "generic_numeric_family",
      "rule_confidence": 0.2,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_semantic_status": "unavailable",
      "ai_available": false,
      "ai_error": "ai_api_key_missing",
      "ai_unavailable_reason": "missing_api_key",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "classifier_source": "rule_fallback_ai_unavailable",
      "classification_decision": "",
      "final_target_task": "compute_numeric",
      "final_task_family": "generic_numeric_family",
      "expected_task_families": [],
      "expected_subskill_candidates": [],
      "structure_context_used": true,
      "sequence_context_used": true,
      "alignment_kind": "unresolved_within_current_skill",
      "exclude_reason": "",
      "included_in_phase1": true,
      "conflict_reason": "ai_api_key_missing",
      "source_mapping_warning": "",
      "skill_anchor_scope": "default",
      "skill_scoped_candidates": [
        {
          "candidate_id": "C1",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "problem_type_id": "compute_numeric",
          "label": "compute_numeric",
          "candidate_source": "outsider",
          "in_anchor_scope": false,
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "math_objects": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
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
              "compute_numeric"
            ]
          },
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
          }
        },
        {
          "candidate_id": "needs_review",
          "target_task": "",
          "task_family": "",
          "problem_type_id": "needs_review",
          "label": "needs_review",
          "candidate_source": "needs_review",
          "in_anchor_scope": false,
          "answer_type": "",
          "answer_shape": "",
          "math_objects": [],
          "checker_key": "manual_review_checker",
          "equivalence_type": "manual_review_or_ai_judged",
          "generator_contract": {},
          "parameter_schema": {}
        }
      ],
      "ai_best_candidate_id": "needs_review",
      "selected_subskill": "compute_numeric",
      "selected_problem_type": "compute_numeric",
      "candidate_source": "needs_review",
      "outsider_candidates": [
        "C1"
      ],
      "selected_generator_contract": {},
      "parameter_schema": {},
      "variable_randomization_notes": []
    },
    {
      "example_id": 3827,
      "rule_target_task": "compute_numeric",
      "rule_task_family": "generic_numeric_family",
      "rule_confidence": 0.2,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_semantic_status": "unavailable",
      "ai_available": false,
      "ai_error": "ai_api_key_missing",
      "ai_unavailable_reason": "missing_api_key",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "classifier_source": "rule_fallback_ai_unavailable",
      "classification_decision": "",
      "final_target_task": "compute_numeric",
      "final_task_family": "generic_numeric_family",
      "expected_task_families": [],
      "expected_subskill_candidates": [],
      "structure_context_used": true,
      "sequence_context_used": true,
      "alignment_kind": "unresolved_within_current_skill",
      "exclude_reason": "",
      "included_in_phase1": true,
      "conflict_reason": "ai_api_key_missing",
      "source_mapping_warning": "",
      "skill_anchor_scope": "default",
      "skill_scoped_candidates": [
        {
          "candidate_id": "C1",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "problem_type_id": "compute_numeric",
          "label": "compute_numeric",
          "candidate_source": "structure",
          "in_anchor_scope": false,
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "math_objects": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
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
              "compute_numeric"
            ]
          },
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
          }
        },
        {
          "candidate_id": "needs_review",
          "target_task": "",
          "task_family": "",
          "problem_type_id": "needs_review",
          "label": "needs_review",
          "candidate_source": "needs_review",
          "in_anchor_scope": false,
          "answer_type": "",
          "answer_shape": "",
          "math_objects": [],
          "checker_key": "manual_review_checker",
          "equivalence_type": "manual_review_or_ai_judged",
          "generator_contract": {},
          "parameter_schema": {}
        }
      ],
      "ai_best_candidate_id": "needs_review",
      "selected_subskill": "compute_numeric",
      "selected_problem_type": "compute_numeric",
      "candidate_source": "needs_review",
      "outsider_candidates": [],
      "selected_generator_contract": {},
      "parameter_schema": {},
      "variable_randomization_notes": []
    },
    {
      "example_id": 3828,
      "rule_target_task": "compute_numeric",
      "rule_task_family": "generic_numeric_family",
      "rule_confidence": 0.2,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_semantic_status": "unavailable",
      "ai_available": false,
      "ai_error": "ai_api_key_missing",
      "ai_unavailable_reason": "missing_api_key",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "classifier_source": "rule_fallback_ai_unavailable",
      "classification_decision": "",
      "final_target_task": "compute_numeric",
      "final_task_family": "generic_numeric_family",
      "expected_task_families": [],
      "expected_subskill_candidates": [],
      "structure_context_used": true,
      "sequence_context_used": true,
      "alignment_kind": "unresolved_within_current_skill",
      "exclude_reason": "",
      "included_in_phase1": true,
      "conflict_reason": "ai_api_key_missing",
      "source_mapping_warning": "",
      "skill_anchor_scope": "default",
      "skill_scoped_candidates": [
        {
          "candidate_id": "C1",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "problem_type_id": "compute_numeric",
          "label": "compute_numeric",
          "candidate_source": "structure",
          "in_anchor_scope": false,
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "math_objects": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
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
              "compute_numeric"
            ]
          },
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
          }
        },
        {
          "candidate_id": "needs_review",
          "target_task": "",
          "task_family": "",
          "problem_type_id": "needs_review",
          "label": "needs_review",
          "candidate_source": "needs_review",
          "in_anchor_scope": false,
          "answer_type": "",
          "answer_shape": "",
          "math_objects": [],
          "checker_key": "manual_review_checker",
          "equivalence_type": "manual_review_or_ai_judged",
          "generator_contract": {},
          "parameter_schema": {}
        }
      ],
      "ai_best_candidate_id": "needs_review",
      "selected_subskill": "compute_numeric",
      "selected_problem_type": "compute_numeric",
      "candidate_source": "needs_review",
      "outsider_candidates": [],
      "selected_generator_contract": {},
      "parameter_schema": {},
      "variable_randomization_notes": []
    },
    {
      "example_id": 3829,
      "rule_target_task": "applied_quadratic_inequality_problem",
      "rule_task_family": "quadratic_inequality_family",
      "rule_confidence": 0.5,
      "ai_target_task": "",
      "ai_task_family": "",
      "ai_confidence": 0.0,
      "ai_semantic_status": "unavailable",
      "ai_available": false,
      "ai_error": "ai_api_key_missing",
      "ai_unavailable_reason": "missing_api_key",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "classifier_source": "rule_fallback_ai_unavailable",
      "classification_decision": "",
      "final_target_task": "applied_quadratic_inequality_problem",
      "final_task_family": "quadratic_inequality_family",
      "expected_task_families": [],
      "expected_subskill_candidates": [],
      "structure_context_used": true,
      "sequence_context_used": true,
      "alignment_kind": "unresolved_within_current_skill",
      "exclude_reason": "",
      "included_in_phase1": true,
      "conflict_reason": "ai_api_key_missing",
      "source_mapping_warning": "",
      "skill_anchor_scope": "default",
      "skill_scoped_candidates": [
        {
          "candidate_id": "C1",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "problem_type_id": "compute_numeric",
          "label": "compute_numeric",
          "candidate_source": "structure",
          "in_anchor_scope": false,
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "math_objects": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
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
              "compute_numeric"
            ]
          },
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
          }
        },
        {
          "candidate_id": "C2",
          "target_task": "applied_quadratic_inequality_problem",
          "task_family": "quadratic_inequality_family",
          "problem_type_id": "applied_quadratic_inequality_problem",
          "label": "applied_quadratic_inequality_problem",
          "candidate_source": "outsider",
          "in_anchor_scope": false,
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "math_objects": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
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
              "applied_quadratic_inequality_problem"
            ]
          },
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
          }
        },
        {
          "candidate_id": "needs_review",
          "target_task": "",
          "task_family": "",
          "problem_type_id": "needs_review",
          "label": "needs_review",
          "candidate_source": "needs_review",
          "in_anchor_scope": false,
          "answer_type": "",
          "answer_shape": "",
          "math_objects": [],
          "checker_key": "manual_review_checker",
          "equivalence_type": "manual_review_or_ai_judged",
          "generator_contract": {},
          "parameter_schema": {}
        }
      ],
      "ai_best_candidate_id": "needs_review",
      "selected_subskill": "applied_quadratic_inequality_problem",
      "selected_problem_type": "applied_quadratic_inequality_problem",
      "candidate_source": "needs_review",
      "outsider_candidates": [
        "C2"
      ],
      "selected_generator_contract": {},
      "parameter_schema": {},
      "variable_randomization_notes": []
    }
  ],
  "ai_semantic_unavailable_reason": "missing_api_key",
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
      "problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
      "matched_example_count": 1
    }
  ],
  "candidate_only_problem_types": [
    {
      "example_id": 3826,
      "problem_type_id": "short_answer_compute_numeric_short_answer",
      "reason": "runtime_not_supported"
    },
    {
      "example_id": 3827,
      "problem_type_id": "short_answer_compute_numeric_short_answer",
      "reason": "runtime_not_supported"
    },
    {
      "example_id": 3828,
      "problem_type_id": "short_answer_compute_numeric_short_answer",
      "reason": "runtime_not_supported"
    }
  ],
  "candidate_only_count": 3,
  "same_as_main_skill_count": 0,
  "rule_only_classification_count": 0,
  "hybrid_resolved_count": 0,
  "subskills": [
    "applied_quadratic_inequality_problem",
    "compute_numeric",
    "same_as_main_skill"
  ],
  "fallback_subskill_used": true,
  "source_belongs_to_current_skill_by_default_count": 4,
  "source_example_alignment": [
    {
      "example_id": 3826,
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
      "classification_source": "rule_fallback_ai_unavailable",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "induction_eligibility": "eligible",
      "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
      "title_stem_preview": "國貿科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補）"
    },
    {
      "example_id": 3827,
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
      "classification_source": "rule_fallback_ai_unavailable",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "induction_eligibility": "eligible",
      "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
      "title_stem_preview": "會計科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補）"
    },
    {
      "example_id": 3828,
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
      "classification_source": "rule_fallback_ai_unavailable",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "induction_eligibility": "eligible",
      "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
      "title_stem_preview": "某女中二年八班同學的體重次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。體重(kg)：40~45(2人), 45~50(7人), 50~55(11人), "
    },
    {
      "example_id": 3829,
      "target_task": "applied_quadratic_inequality_problem",
      "task_family": "quadratic_inequality_family",
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
      "classification_source": "rule_fallback_ai_unavailable",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "induction_eligibility": "eligible",
      "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
      "title_stem_preview": "某幼兒園班上25位小朋友身高分布之直方圖如右。今班上轉出一位身高117公分之小朋友，轉入一位身高112公分之小朋友，則此時班上小朋友身高分布之直方圖為何？（圖片"
    }
  ],
  "candidate_problem_types": [
    {
      "problem_type_id": "text_short_compute_numeric",
      "proposed_problem_type_id": "text_short_compute_numeric",
      "display_name": "text_short / compute_numeric",
      "matched_example_ids": [
        3826,
        3827,
        3828
      ],
      "matched_example_count": 3,
      "unmatched_example_ids": [],
      "representative_example_id": 3826,
      "structural_features": [
        "text_short"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "answer_equivalence": "exact_string",
        "checker": "text_short_checker",
        "accepted_formats": [
          "5",
          "5.0",
          "-3"
        ],
        "source_has_choices": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "presentation_mode": "",
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "text_short"
      },
      "checker_key_proposal": "text_short_checker",
      "equivalence_type_proposal": "exact_string",
      "answer_shape": "text_short",
      "answer_semantics": "text_short",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "text_short_checker",
      "checker_selection_reason": "task_family_default",
      "coordinate_pair_presentation_note": "",
      "confidence": "high",
      "promote_recommendation": "hold_pending_problem_type_induction",
      "promote_blockers": [
        "generic_fallback_blocked_by_source_skill_binding"
      ],
      "risk_flags": [
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance",
        "ai_unavailable_fallback_to_same_as_main",
        "alignment_score_below_recommended_threshold",
        "generic_fallback_blocked_by_source_skill_binding"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "short_answer",
        "compute_numeric",
        "short_answer",
        [
          "numeric_computation"
        ],
        [],
        "default"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "expression_compute_text_short_expression",
        "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "display_name": "short_answer / compute_numeric",
        "answer_format_hint": "text_short",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          3826,
          3827,
          3828
        ],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "text_short",
          "answer_shape": "text_short",
          "answer_equivalence": "exact_string",
          "checker": "text_short_checker",
          "accepted_formats": [
            "5",
            "5.0",
            "-3"
          ],
          "source_has_choices": false,
          "equivalence_type": "exact_string",
          "checker_key": "text_short_checker",
          "presentation_mode": "short_answer"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [],
          "required_math_objects": [],
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
            "numeric_computation"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable",
            "duplicated_choices",
            "no_correct_choice",
            "multiple_correct_choices_when_single_choice"
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
            "compute_numeric"
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
            "stem": "point_quadrant"
          },
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "short_answer_compute_numeric_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks",
            "choices_policy"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "short_answer",
          "compute_numeric",
          "short_answer",
          [
            "numeric_computation"
          ],
          [],
          "default"
        ],
        "canonical_base_problem_type_id": "short_answer_compute_numeric_short_answer",
        "value_type_prefix": "",
        "_resolved_template_slot": "point_quadrant"
      },
      "generator_readiness": "pending_problem_type_induction",
      "usable_for_phase3": false,
      "template_slot": "point_quadrant",
      "canonical_base_problem_type_id": "short_answer_compute_numeric_short_answer",
      "value_type_prefix": "",
      "subskill_id": "compute_numeric",
      "requires_human_action": true,
      "requires_human_rule_pack": true,
      "pending_problem_type_induction": true,
      "answer_type": "text_short",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0256,
        "task_consistent_with_skill": true
      }
    },
    {
      "problem_type_id": "unresolved_within_current_skill",
      "proposed_problem_type_id": "unresolved_within_current_skill",
      "display_name": "text_short / applied_quadratic_inequality_problem",
      "matched_example_ids": [
        3829
      ],
      "matched_example_count": 1,
      "unmatched_example_ids": [],
      "representative_example_id": 3829,
      "structural_features": [
        "interval_or_union"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "source_has_choices": false,
        "answer_type": "text_short",
        "answer_shape": "interval_or_union",
        "answer_semantics": "interval_union",
        "answer_equivalence": "exact_string",
        "equivalence_type": "exact_string",
        "checker": "text_short_checker",
        "checker_key": "text_short_checker",
        "presentation_mode": "",
        "selected_checker": "interval_checker",
        "checker_selection_reason": "quadratic_inequality_interval_solution",
        "accepted_formats": [
          "-5 <= x <= 1",
          "(-5, 1]",
          "x in [-5,1]",
          "x<-2 or x>5",
          "-2<x<5",
          "x<=-2 or x>=5"
        ],
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "interval"
      },
      "checker_key_proposal": "text_short_checker",
      "equivalence_type_proposal": "exact_string",
      "answer_shape": "interval_or_union",
      "answer_semantics": "interval_union",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "interval_checker",
      "checker_selection_reason": "quadratic_inequality_interval_solution",
      "coordinate_pair_presentation_note": "",
      "confidence": "high",
      "promote_recommendation": "hold_pending_problem_type_induction",
      "promote_blockers": [
        "unregistered_current_skill_problem_type"
      ],
      "risk_flags": [
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance",
        "ai_unavailable_fallback_to_same_as_main",
        "alignment_score_below_recommended_threshold",
        "unregistered_current_skill_problem_type"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "short_answer",
        "applied_quadratic_inequality_problem",
        "short_answer",
        [
          "quadratic_factoring_reasoning"
        ],
        [],
        "default"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "unresolved_within_current_skill",
        "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "display_name": "short_answer / applied_quadratic_inequality_problem",
        "answer_format_hint": "interval",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          3829
        ],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "source_has_choices": false,
          "answer_type": "interval",
          "answer_shape": "interval_or_union",
          "answer_semantics": "interval_union",
          "answer_equivalence": "interval_set",
          "equivalence_type": "interval_set",
          "checker": "interval_checker",
          "checker_key": "interval_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "interval_checker",
          "checker_selection_reason": "quadratic_inequality_interval_solution",
          "accepted_formats": [
            "-5 <= x <= 1",
            "(-5, 1]",
            "x in [-5,1]",
            "x<-2 or x>5",
            "-2<x<5",
            "x<=-2 or x>=5"
          ]
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [],
          "required_math_objects": [],
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
            "quadratic_factoring_reasoning"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable",
            "duplicated_choices",
            "no_correct_choice",
            "multiple_correct_choices_when_single_choice"
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
            "applied_quadratic_inequality_problem"
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
            "stem": "applied_quadratic_inequality_problem"
          },
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks",
            "choices_policy"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "short_answer",
          "applied_quadratic_inequality_problem",
          "short_answer",
          [
            "quadratic_factoring_reasoning"
          ],
          [],
          "default"
        ],
        "canonical_base_problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
        "value_type_prefix": "",
        "_resolved_template_slot": "applied_quadratic_inequality_problem"
      },
      "generator_readiness": "pending_problem_type_induction",
      "usable_for_phase3": false,
      "template_slot": "applied_quadratic_inequality_problem",
      "canonical_base_problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
      "value_type_prefix": "",
      "subskill_id": "applied_quadratic_inequality_problem",
      "answer_type": "interval",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0244,
        "task_consistent_with_skill": true
      },
      "detected_weak_problem_type_id": "text_short_applied_quadratic_inequality_problem",
      "detected_weak_target_task": "applied_quadratic_inequality_problem",
      "requires_human_action": true,
      "requires_human_rule_pack": true,
      "pending_problem_type_induction": true,
      "unresolved_reason": "unregistered_current_skill_problem_type"
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
      "short_answer_compute_numeric_short_answer": {
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "text_short"
      },
      "unresolved_within_current_skill": {
        "answer_type": "interval",
        "answer_shape": "interval_or_union",
        "equivalence_type": "interval_set",
        "checker_key": "interval_checker",
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "interval"
      }
    },
    "missing_answer_contract_problem_types": [],
    "missing_checker_key_problem_types": [],
    "equivalence_test_required_problem_types": [
      "unresolved_within_current_skill"
    ],
    "convertible_to_choice_problem_types": [],
    "manual_review_or_ai_judged_problem_types": []
  },
  "invalid_equivalence_type_problem_types": [],
  "phase1_answer_contract_gate_status": "PASS",
  "per_example_classification": [
    {
      "example_id": 3826,
      "detected_problem_type_id": "short_answer_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3826,
        "question_text": "國貿科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補）",
        "answer": "直方圖與折線圖",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "compute_numeric",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "outsider",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [
            "C1"
          ],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "worked_example",
          "example_label": "例題2",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "worked_example",
          "example_label": "例題2",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": 2,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            }
          ],
          "same_section_sequence": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            },
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            },
            {
              "example_id": 3828,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題3"
            },
            {
              "example_id": 3829,
              "source_type": "advanced_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 進階題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "requires_human_action",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "outsider",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [
          "C1"
        ],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "worked_example",
        "example_label": "例題2",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "compute_numeric",
      "classification_source": "rule_fallback_ai_unavailable",
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
      "example_id": 3827,
      "detected_problem_type_id": "short_answer_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3827,
        "question_text": "會計科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補）",
        "answer": "略",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "compute_numeric",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習2",
          "linked_example": "例題2",
          "linked_example_id": 3826,
          "linked_example_task_family": "generic_numeric_family",
          "structure_consistency": "consistent",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習2",
          "linked_example": "例題2",
          "section_order": 0,
          "example_number": null,
          "practice_number": 2,
          "nearby_worked_examples": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            }
          ],
          "linked_worked_example": {
            "example_id": 3826,
            "source_type": "worked_example",
            "example_label": "例題2",
            "practice_label": "",
            "section_order": 0,
            "title_head": "例題 2"
          },
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            },
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            },
            {
              "example_id": 3828,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題3"
            },
            {
              "example_id": 3829,
              "source_type": "advanced_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 進階題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "requires_human_action",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "in_class_practice",
        "example_label": "",
        "practice_label": "隨堂練習2",
        "linked_example": "例題2",
        "linked_example_id": 3826,
        "linked_example_task_family": "generic_numeric_family",
        "structure_consistency": "consistent",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "compute_numeric",
      "classification_source": "rule_fallback_ai_unavailable",
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
      "example_id": 3828,
      "detected_problem_type_id": "short_answer_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3828,
        "question_text": "某女中二年八班同學的體重次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。體重(kg)：40~45(2人), 45~50(7人), 50~55(11人), 55~60(10人), 60~65(5人), 65~70(3人), 70~75(2人)。（圖片待補）",
        "answer": "略",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "compute_numeric",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "basic_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "basic_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            },
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            },
            {
              "example_id": 3828,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題3"
            },
            {
              "example_id": 3829,
              "source_type": "advanced_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 進階題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "requires_human_action",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "basic_exercise",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "compute_numeric",
      "classification_source": "rule_fallback_ai_unavailable",
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
      "example_id": 3829,
      "detected_problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
      "example_feature": {
        "source_example_id": 3829,
        "question_text": "某幼兒園班上25位小朋友身高分布之直方圖如右。今班上轉出一位身高117公分之小朋友，轉入一位身高112公分之小朋友，則此時班上小朋友身高分布之直方圖為何？（圖片待補）",
        "answer": "115~120組次數減1，110~115組次數加1",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "reasoning_type": [
          "quadratic_factoring_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "applied_quadratic_inequality_problem",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [
          "[Task: Applied_Context]"
        ],
        "forced_target_task": "applied_quadratic_inequality_problem",
        "meta_answer_format_hint": "interval",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "applied_quadratic_inequality_problem",
          "rule_task_family": "quadratic_inequality_family",
          "rule_confidence": 0.5,
          "final_target_task": "applied_quadratic_inequality_problem",
          "final_task_family": "quadratic_inequality_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "C2",
              "target_task": "applied_quadratic_inequality_problem",
              "task_family": "quadratic_inequality_family",
              "problem_type_id": "applied_quadratic_inequality_problem",
              "label": "applied_quadratic_inequality_problem",
              "candidate_source": "outsider",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "applied_quadratic_inequality_problem"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [
            "C2"
          ],
          "selected_subskill": "applied_quadratic_inequality_problem",
          "selected_problem_type": "applied_quadratic_inequality_problem",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "applied_quadratic_inequality_problem",
          "task_family": "quadratic_inequality_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "advanced_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "possible_structure_mismatch_penalty; sequence_context_used",
          "possible_structure_mismatch": true,
          "possible_mixed_source_context": true
        },
        "source_structure_context": {
          "source_type": "advanced_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            },
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            },
            {
              "example_id": 3828,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題3"
            },
            {
              "example_id": 3829,
              "source_type": "advanced_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 進階題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "requires_human_action"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "applied_quadratic_inequality_problem",
        "rule_task_family": "quadratic_inequality_family",
        "rule_confidence": 0.5,
        "final_target_task": "applied_quadratic_inequality_problem",
        "final_task_family": "quadratic_inequality_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "C2",
            "target_task": "applied_quadratic_inequality_problem",
            "task_family": "quadratic_inequality_family",
            "problem_type_id": "applied_quadratic_inequality_problem",
            "label": "applied_quadratic_inequality_problem",
            "candidate_source": "outsider",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "applied_quadratic_inequality_problem"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [
          "C2"
        ],
        "selected_subskill": "applied_quadratic_inequality_problem",
        "selected_problem_type": "applied_quadratic_inequality_problem",
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "math_objects": [],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "advanced_exercise",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "possible_structure_mismatch_penalty; sequence_context_used",
        "possible_structure_mismatch": true,
        "possible_mixed_source_context": true
      },
      "subskill_id": "applied_quadratic_inequality_problem",
      "classification_source": "rule_fallback_ai_unavailable",
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
    }
  ],
  "source_classifications": [
    {
      "example_id": 3826,
      "detected_problem_type_id": "short_answer_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3826,
        "question_text": "國貿科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補）",
        "answer": "直方圖與折線圖",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "compute_numeric",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "outsider",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [
            "C1"
          ],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "worked_example",
          "example_label": "例題2",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "worked_example",
          "example_label": "例題2",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": 2,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            }
          ],
          "same_section_sequence": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            },
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            },
            {
              "example_id": 3828,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題3"
            },
            {
              "example_id": 3829,
              "source_type": "advanced_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 進階題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "requires_human_action",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "outsider",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [
          "C1"
        ],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "worked_example",
        "example_label": "例題2",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "compute_numeric",
      "classification_source": "rule_fallback_ai_unavailable",
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
      "example_id": 3827,
      "detected_problem_type_id": "short_answer_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3827,
        "question_text": "會計科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補）",
        "answer": "略",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "compute_numeric",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習2",
          "linked_example": "例題2",
          "linked_example_id": 3826,
          "linked_example_task_family": "generic_numeric_family",
          "structure_consistency": "consistent",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習2",
          "linked_example": "例題2",
          "section_order": 0,
          "example_number": null,
          "practice_number": 2,
          "nearby_worked_examples": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            }
          ],
          "linked_worked_example": {
            "example_id": 3826,
            "source_type": "worked_example",
            "example_label": "例題2",
            "practice_label": "",
            "section_order": 0,
            "title_head": "例題 2"
          },
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            },
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            },
            {
              "example_id": 3828,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題3"
            },
            {
              "example_id": 3829,
              "source_type": "advanced_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 進階題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "requires_human_action",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "in_class_practice",
        "example_label": "",
        "practice_label": "隨堂練習2",
        "linked_example": "例題2",
        "linked_example_id": 3826,
        "linked_example_task_family": "generic_numeric_family",
        "structure_consistency": "consistent",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "compute_numeric",
      "classification_source": "rule_fallback_ai_unavailable",
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
      "example_id": 3828,
      "detected_problem_type_id": "short_answer_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3828,
        "question_text": "某女中二年八班同學的體重次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。體重(kg)：40~45(2人), 45~50(7人), 50~55(11人), 55~60(10人), 60~65(5人), 65~70(3人), 70~75(2人)。（圖片待補）",
        "answer": "略",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "compute_numeric",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "basic_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "basic_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            },
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            },
            {
              "example_id": 3828,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題3"
            },
            {
              "example_id": 3829,
              "source_type": "advanced_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 進階題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "requires_human_action",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "basic_exercise",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "compute_numeric",
      "classification_source": "rule_fallback_ai_unavailable",
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
      "example_id": 3829,
      "detected_problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
      "example_feature": {
        "source_example_id": 3829,
        "question_text": "某幼兒園班上25位小朋友身高分布之直方圖如右。今班上轉出一位身高117公分之小朋友，轉入一位身高112公分之小朋友，則此時班上小朋友身高分布之直方圖為何？（圖片待補）",
        "answer": "115~120組次數減1，110~115組次數加1",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "reasoning_type": [
          "quadratic_factoring_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "applied_quadratic_inequality_problem",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [
          "[Task: Applied_Context]"
        ],
        "forced_target_task": "applied_quadratic_inequality_problem",
        "meta_answer_format_hint": "interval",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "applied_quadratic_inequality_problem",
          "rule_task_family": "quadratic_inequality_family",
          "rule_confidence": 0.5,
          "final_target_task": "applied_quadratic_inequality_problem",
          "final_task_family": "quadratic_inequality_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "C2",
              "target_task": "applied_quadratic_inequality_problem",
              "task_family": "quadratic_inequality_family",
              "problem_type_id": "applied_quadratic_inequality_problem",
              "label": "applied_quadratic_inequality_problem",
              "candidate_source": "outsider",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "applied_quadratic_inequality_problem"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [
            "C2"
          ],
          "selected_subskill": "applied_quadratic_inequality_problem",
          "selected_problem_type": "applied_quadratic_inequality_problem",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "applied_quadratic_inequality_problem",
          "task_family": "quadratic_inequality_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "advanced_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "possible_structure_mismatch_penalty; sequence_context_used",
          "possible_structure_mismatch": true,
          "possible_mixed_source_context": true
        },
        "source_structure_context": {
          "source_type": "advanced_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            },
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            },
            {
              "example_id": 3828,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題3"
            },
            {
              "example_id": 3829,
              "source_type": "advanced_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 進階題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "requires_human_action"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "applied_quadratic_inequality_problem",
        "rule_task_family": "quadratic_inequality_family",
        "rule_confidence": 0.5,
        "final_target_task": "applied_quadratic_inequality_problem",
        "final_task_family": "quadratic_inequality_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "C2",
            "target_task": "applied_quadratic_inequality_problem",
            "task_family": "quadratic_inequality_family",
            "problem_type_id": "applied_quadratic_inequality_problem",
            "label": "applied_quadratic_inequality_problem",
            "candidate_source": "outsider",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "applied_quadratic_inequality_problem"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [
          "C2"
        ],
        "selected_subskill": "applied_quadratic_inequality_problem",
        "selected_problem_type": "applied_quadratic_inequality_problem",
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "math_objects": [],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "advanced_exercise",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "possible_structure_mismatch_penalty; sequence_context_used",
        "possible_structure_mismatch": true,
        "possible_mixed_source_context": true
      },
      "subskill_id": "applied_quadratic_inequality_problem",
      "classification_source": "rule_fallback_ai_unavailable",
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
    }
  ],
  "unclassified_examples": [],
  "risk_examples": [
    3826,
    3827,
    3828,
    3829
  ],
  "split_or_merge_recommendation": "induced_from_source_features",
  "classifier_gate": {
    "status": "classifier_auto_pending_promote_with_warning",
    "allowed": true,
    "warnings": [
      "insufficient_examples",
      "ai_first_mode_fell_back_to_rule_only",
      "ai_partial_unavailable_relaxed_tolerance",
      "ai_unavailable_fallback_to_same_as_main",
      "alignment_score_below_recommended_threshold",
      "generic_fallback_blocked_by_source_skill_binding"
    ]
  },
  "generator_draft_gate": {
    "status": "generator_draft_allowed_with_low_source_warning",
    "allowed": true,
    "warnings": [
      "low_source_examples",
      "ai_first_mode_fell_back_to_rule_only",
      "ai_partial_unavailable_relaxed_tolerance",
      "ai_unavailable_fallback_to_same_as_main",
      "alignment_score_below_recommended_threshold",
      "generic_fallback_blocked_by_source_skill_binding"
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
      "ai_first_mode_fell_back_to_rule_only",
      "ai_partial_unavailable_relaxed_tolerance",
      "ai_unavailable_fallback_to_same_as_main",
      "alignment_score_below_recommended_threshold",
      "generic_fallback_blocked_by_source_skill_binding"
    ]
  },
  "exception_review_gate": {
    "required": false,
    "reasons": []
  },
  "reports": {
    "phase1_summary_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B4_HistogramsAndFrequencyPolygons_phase1_summary.json",
    "phase1_summary_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B4_HistogramsAndFrequencyPolygons_phase1_summary.md",
    "phase1_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B4_HistogramsAndFrequencyPolygons_phase1_summary.json",
    "phase1_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B4_HistogramsAndFrequencyPolygons_phase1_summary.md"
  },
  "next_action": "phase2_generate_from_induced_specs",
  "timestamp": "2026-06-29T02:55:09.383926+00:00",
  "dry_run": true,
  "auto_review_summary": {
    "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
    "main_skill_anchor": {
      "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
      "skill_ch_name": "次數分配直方圖與次數分配折線圖的繪製",
      "skill_en_name": "HistogramsAndFrequencyPolygons",
      "chapter": "3 統計",
      "section": "3-2 統計資料整理",
      "normalized_skill_terms": [
        "2 統計資料整理",
        "3 統計",
        "and",
        "andfrequencypolygon",
        "frequency",
        "hi",
        "histograms",
        "histogramsandfrequencypolygons",
        "polygons",
        "togram",
        "vh",
        "vocational",
        "數學b",
        "數學b4",
        "次數分配直方圖與次數分配折線圖的繪製",
        "統計",
        "統計資料整理"
      ],
      "expected_task_families": [],
      "expected_math_objects": [],
      "expected_subskill_candidates": [],
      "skill_anchor_scope": "default",
      "fallback_subskill": {
        "subskill_id": "same_as_main_skill",
        "subskill_name": "次數分配直方圖與次數分配折線圖的繪製",
        "subskill_scope": "fallback",
        "display_note": "此子技能為 fallback，用於收納未細分或綜合題"
      },
      "source_belongs_to_current_skill_by_default": true,
      "source_skill_scope_locked": true,
      "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
      "classification_scope": "within_current_skill",
      "skill_mapping_authority": "textbook_examples.skill_id",
      "anchor_authority": "skill_id_derived_no_cross_family_pollution",
      "classification_mandate": "【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\n【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\nTrusted skill anchor (do not override):\n- skill_id: vh_數學B4_HistogramsAndFrequencyPolygons\n- skill_ch_name: 次數分配直方圖與次數分配折線圖的繪製\n- skill_en_name: HistogramsAndFrequencyPolygons\n- expected_task_families: []\n- expected_subskill_candidates: []\n- skill_anchor_scope: default\n- source_skill_scope_locked: True\n"
    },
    "spec_mode": "ai_first_induce_from_sources",
    "semantic_classifications": [
      {
        "example_id": 3826,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "outsider",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [
          "C1"
        ],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "worked_example",
        "example_label": "例題2",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      {
        "example_id": 3827,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "in_class_practice",
        "example_label": "",
        "practice_label": "隨堂練習2",
        "linked_example": "例題2",
        "linked_example_id": 3826,
        "linked_example_task_family": "generic_numeric_family",
        "structure_consistency": "consistent",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      {
        "example_id": 3828,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "basic_exercise",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      {
        "example_id": 3829,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "applied_quadratic_inequality_problem",
        "rule_task_family": "quadratic_inequality_family",
        "rule_confidence": 0.5,
        "final_target_task": "applied_quadratic_inequality_problem",
        "final_task_family": "quadratic_inequality_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "C2",
            "target_task": "applied_quadratic_inequality_problem",
            "task_family": "quadratic_inequality_family",
            "problem_type_id": "applied_quadratic_inequality_problem",
            "label": "applied_quadratic_inequality_problem",
            "candidate_source": "outsider",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "applied_quadratic_inequality_problem"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [
          "C2"
        ],
        "selected_subskill": "applied_quadratic_inequality_problem",
        "selected_problem_type": "applied_quadratic_inequality_problem",
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "math_objects": [],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "advanced_exercise",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "possible_structure_mismatch_penalty; sequence_context_used",
        "possible_structure_mismatch": true,
        "possible_mixed_source_context": true
      }
    ],
    "classification_diagnostics": [
      {
        "example_id": 3826,
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_semantic_status": "unavailable",
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "expected_task_families": [],
        "expected_subskill_candidates": [],
        "structure_context_used": true,
        "sequence_context_used": true,
        "alignment_kind": "unresolved_within_current_skill",
        "exclude_reason": "",
        "included_in_phase1": true,
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "skill_anchor_scope": "default",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "outsider",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "ai_best_candidate_id": "needs_review",
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "needs_review",
        "outsider_candidates": [
          "C1"
        ],
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": []
      },
      {
        "example_id": 3827,
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_semantic_status": "unavailable",
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "expected_task_families": [],
        "expected_subskill_candidates": [],
        "structure_context_used": true,
        "sequence_context_used": true,
        "alignment_kind": "unresolved_within_current_skill",
        "exclude_reason": "",
        "included_in_phase1": true,
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "skill_anchor_scope": "default",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "ai_best_candidate_id": "needs_review",
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "needs_review",
        "outsider_candidates": [],
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": []
      },
      {
        "example_id": 3828,
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_semantic_status": "unavailable",
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "expected_task_families": [],
        "expected_subskill_candidates": [],
        "structure_context_used": true,
        "sequence_context_used": true,
        "alignment_kind": "unresolved_within_current_skill",
        "exclude_reason": "",
        "included_in_phase1": true,
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "skill_anchor_scope": "default",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "ai_best_candidate_id": "needs_review",
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "needs_review",
        "outsider_candidates": [],
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": []
      },
      {
        "example_id": 3829,
        "rule_target_task": "applied_quadratic_inequality_problem",
        "rule_task_family": "quadratic_inequality_family",
        "rule_confidence": 0.5,
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_semantic_status": "unavailable",
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "final_target_task": "applied_quadratic_inequality_problem",
        "final_task_family": "quadratic_inequality_family",
        "expected_task_families": [],
        "expected_subskill_candidates": [],
        "structure_context_used": true,
        "sequence_context_used": true,
        "alignment_kind": "unresolved_within_current_skill",
        "exclude_reason": "",
        "included_in_phase1": true,
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "skill_anchor_scope": "default",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "C2",
            "target_task": "applied_quadratic_inequality_problem",
            "task_family": "quadratic_inequality_family",
            "problem_type_id": "applied_quadratic_inequality_problem",
            "label": "applied_quadratic_inequality_problem",
            "candidate_source": "outsider",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                "applied_quadratic_inequality_problem"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "ai_best_candidate_id": "needs_review",
        "selected_subskill": "applied_quadratic_inequality_problem",
        "selected_problem_type": "applied_quadratic_inequality_problem",
        "candidate_source": "needs_review",
        "outsider_candidates": [
          "C2"
        ],
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": []
      }
    ],
    "ai_semantic_status": "unavailable",
    "ai_semantic_unavailable_reason": "missing_api_key",
    "ai_invalid_response_reason": "",
    "source_structure_report": {
      "source_type_distribution": {
        "worked_example": 1,
        "in_class_practice": 1,
        "basic_exercise": 1,
        "advanced_exercise": 1
      },
      "example_practice_link_map": [
        {
          "practice_label": "隨堂練習2",
          "linked_example": "例題2",
          "example_id": 3827
        }
      ],
      "structure_mismatch_examples": [],
      "same_section_family_distribution": {
        "generic_numeric_family": 3,
        "quadratic_inequality_family": 1
      }
    },
    "source_type_distribution": {
      "worked_example": 1,
      "in_class_practice": 1,
      "basic_exercise": 1,
      "advanced_exercise": 1
    },
    "example_practice_link_map": [
      {
        "practice_label": "隨堂練習2",
        "linked_example": "例題2",
        "example_id": 3827
      }
    ],
    "structure_mismatch_examples": [],
    "same_section_family_distribution": {
      "generic_numeric_family": 3,
      "quadratic_inequality_family": 1
    },
    "example_features": [
      {
        "source_example_id": 3826,
        "question_text": "國貿科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補）",
        "answer": "直方圖與折線圖",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "compute_numeric",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "outsider",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [
            "C1"
          ],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "worked_example",
          "example_label": "例題2",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "worked_example",
          "example_label": "例題2",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": 2,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            }
          ],
          "same_section_sequence": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            },
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            },
            {
              "example_id": 3828,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題3"
            },
            {
              "example_id": 3829,
              "source_type": "advanced_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 進階題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
        "source_example_id": 3827,
        "question_text": "會計科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補）",
        "answer": "略",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "compute_numeric",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習2",
          "linked_example": "例題2",
          "linked_example_id": 3826,
          "linked_example_task_family": "generic_numeric_family",
          "structure_consistency": "consistent",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習2",
          "linked_example": "例題2",
          "section_order": 0,
          "example_number": null,
          "practice_number": 2,
          "nearby_worked_examples": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            }
          ],
          "linked_worked_example": {
            "example_id": 3826,
            "source_type": "worked_example",
            "example_label": "例題2",
            "practice_label": "",
            "section_order": 0,
            "title_head": "例題 2"
          },
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            },
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            },
            {
              "example_id": 3828,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題3"
            },
            {
              "example_id": 3829,
              "source_type": "advanced_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 進階題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
        "source_example_id": 3828,
        "question_text": "某女中二年八班同學的體重次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。體重(kg)：40~45(2人), 45~50(7人), 50~55(11人), 55~60(10人), 60~65(5人), 65~70(3人), 70~75(2人)。（圖片待補）",
        "answer": "略",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "compute_numeric",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "basic_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "basic_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            },
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            },
            {
              "example_id": 3828,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題3"
            },
            {
              "example_id": 3829,
              "source_type": "advanced_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 進階題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
        "source_example_id": 3829,
        "question_text": "某幼兒園班上25位小朋友身高分布之直方圖如右。今班上轉出一位身高117公分之小朋友，轉入一位身高112公分之小朋友，則此時班上小朋友身高分布之直方圖為何？（圖片待補）",
        "answer": "115~120組次數減1，110~115組次數加1",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "reasoning_type": [
          "quadratic_factoring_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "applied_quadratic_inequality_problem",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [
          "[Task: Applied_Context]"
        ],
        "forced_target_task": "applied_quadratic_inequality_problem",
        "meta_answer_format_hint": "interval",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "applied_quadratic_inequality_problem",
          "rule_task_family": "quadratic_inequality_family",
          "rule_confidence": 0.5,
          "final_target_task": "applied_quadratic_inequality_problem",
          "final_task_family": "quadratic_inequality_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "C2",
              "target_task": "applied_quadratic_inequality_problem",
              "task_family": "quadratic_inequality_family",
              "problem_type_id": "applied_quadratic_inequality_problem",
              "label": "applied_quadratic_inequality_problem",
              "candidate_source": "outsider",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "applied_quadratic_inequality_problem"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [
            "C2"
          ],
          "selected_subskill": "applied_quadratic_inequality_problem",
          "selected_problem_type": "applied_quadratic_inequality_problem",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "applied_quadratic_inequality_problem",
          "task_family": "quadratic_inequality_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "advanced_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "possible_structure_mismatch_penalty; sequence_context_used",
          "possible_structure_mismatch": true,
          "possible_mixed_source_context": true
        },
        "source_structure_context": {
          "source_type": "advanced_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            },
            {
              "example_id": 3827,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習 2"
            },
            {
              "example_id": 3828,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題3"
            },
            {
              "example_id": 3829,
              "source_type": "advanced_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 進階題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker"
      }
    ],
    "semantic_alignment": {
      "main_skill_anchor": {
        "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "skill_ch_name": "次數分配直方圖與次數分配折線圖的繪製",
        "skill_en_name": "HistogramsAndFrequencyPolygons",
        "chapter": "3 統計",
        "section": "3-2 統計資料整理",
        "normalized_skill_terms": [
          "2 統計資料整理",
          "3 統計",
          "and",
          "andfrequencypolygon",
          "frequency",
          "hi",
          "histograms",
          "histogramsandfrequencypolygons",
          "polygons",
          "togram",
          "vh",
          "vocational",
          "數學b",
          "數學b4",
          "次數分配直方圖與次數分配折線圖的繪製",
          "統計",
          "統計資料整理"
        ],
        "expected_task_families": [],
        "expected_math_objects": [],
        "expected_subskill_candidates": [],
        "skill_anchor_scope": "default",
        "fallback_subskill": {
          "subskill_id": "same_as_main_skill",
          "subskill_name": "次數分配直方圖與次數分配折線圖的繪製",
          "subskill_scope": "fallback",
          "display_note": "此子技能為 fallback，用於收納未細分或綜合題"
        },
        "source_belongs_to_current_skill_by_default": true,
        "source_skill_scope_locked": true,
        "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "classification_scope": "within_current_skill",
        "skill_mapping_authority": "textbook_examples.skill_id",
        "anchor_authority": "skill_id_derived_no_cross_family_pollution",
        "classification_mandate": "【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\n【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\nTrusted skill anchor (do not override):\n- skill_id: vh_數學B4_HistogramsAndFrequencyPolygons\n- skill_ch_name: 次數分配直方圖與次數分配折線圖的繪製\n- skill_en_name: HistogramsAndFrequencyPolygons\n- expected_task_families: []\n- expected_subskill_candidates: []\n- skill_anchor_scope: default\n- source_skill_scope_locked: True\n"
      },
      "ai_semantic_status": "unavailable",
      "skill_terms": [
        "2 統計資料整理",
        "3 統計",
        "and",
        "andfrequencypolygon",
        "frequency",
        "hi",
        "histograms",
        "histogramsandfrequencypolygons",
        "polygons",
        "togram",
        "vh",
        "vocational",
        "數學b",
        "數學b4",
        "次數分配直方圖與次數分配折線圖的繪製",
        "統計",
        "統計資料整理"
      ],
      "source_terms": [
        "10人",
        "11人",
        "2人",
        "3人",
        "40",
        "45",
        "50",
        "55",
        "5人",
        "60",
        "65",
        "70",
        "75",
        "7人",
        "applied_quadratic_inequality_problem",
        "compute_numeric",
        "kg",
        "short_answer",
        "今班上轉出一位身高117公分之小朋友",
        "則此時班上小朋友身高分布之直方圖為何",
        "國貿科三年甲班模擬考某科成績的次數分配表如下",
        "圖片待補",
        "會計科三年甲班模擬考某科成績的次數分配表如下",
        "某女中二年八班同學的體重次數分配表如下",
        "某幼兒園班上25位小朋友身高分布之直方圖如右",
        "試畫出其對應的直方圖與次數分配折線圖",
        "轉入一位身高112公分之小朋友",
        "體重"
      ],
      "expected_subskill_candidates": [],
      "observed_target_task_distribution": {
        "compute_numeric": 3,
        "applied_quadratic_inequality_problem": 1
      },
      "same_family_subskill_mismatch_examples": [],
      "examples_outside_expected_subskills": [],
      "suggested_action": "",
      "examples_outside_expected_family": [],
      "problem_type_terms": [
        "an",
        "answer",
        "applied",
        "applied_quadratic_inequality_problem",
        "compute",
        "compute_numeric",
        "hort",
        "inequality",
        "interval",
        "numeric",
        "numeric_computation",
        "point_quadrant",
        "problem",
        "quadratic",
        "quadratic_factoring_reasoning",
        "short",
        "short_answer / applied_quadratic_inequality_problem",
        "short_answer / compute_numeric",
        "solve_absolute_value_inequality",
        "text_short",
        "wer"
      ],
      "expected_task_candidates": [],
      "expected_skill_families": [],
      "observed_source_family_distribution": {
        "generic_numeric_family": 3,
        "quadratic_inequality_family": 1
      },
      "source_family_distribution": {
        "generic_numeric_family": 3,
        "quadratic_inequality_family": 1
      },
      "candidate_problem_type_families": [
        "generic_numeric_family",
        "quadratic_inequality_family"
      ],
      "dominant_source_task": "compute_numeric",
      "dominant_source_task_ratio": 0.75,
      "uniform_core_target_task": "compute_numeric",
      "uniform_core_target_task_ratio": 0.75,
      "uniform_core_target_task_count": 4,
      "uniform_core_threshold_relaxed": false,
      "dominant_source_family": [
        "generic_numeric_family"
      ],
      "dominant_source_family_ratio": 0.75,
      "skill_source_score": 0.0,
      "skill_problem_type_score": 0.0,
      "source_problem_type_score": 0.0256,
      "per_problem_type_scores": [
        {
          "problem_type_id": "short_answer_compute_numeric_short_answer",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "inferred_tasks": [
            "compute_numeric"
          ],
          "skill_problem_type_score": 0.0,
          "source_problem_type_score": 0.0256,
          "task_consistent_with_skill": true,
          "family_consistent_with_skill": true,
          "answer_contract_supported": true
        },
        {
          "problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
          "target_task": "applied_quadratic_inequality_problem",
          "task_family": "quadratic_inequality_family",
          "inferred_tasks": [
            "applied_quadratic_inequality_problem"
          ],
          "skill_problem_type_score": 0.0,
          "source_problem_type_score": 0.0244,
          "task_consistent_with_skill": true,
          "family_consistent_with_skill": true,
          "answer_contract_supported": true
        }
      ],
      "decision": "warn",
      "blockers": [],
      "warnings": [
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance",
        "ai_unavailable_fallback_to_same_as_main",
        "alignment_score_below_recommended_threshold"
      ],
      "induction_core_example_count": 4,
      "induction_enrichment_example_count": 0,
      "source_skill_scope_locked": true,
      "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
      "classification_scope": "within_current_skill",
      "skill_mapping_authority": "textbook_examples.skill_id",
      "core_skill_concept": "histogramsandfrequencypolygons",
      "supporting_math_objects": [],
      "source_quality_reject_examples": []
    },
    "source_alignment_status": "warn",
    "skill_problem_type_alignment_status": "warn",
    "alignment_score": 0.0,
    "alignment_warnings": [
      "ai_first_mode_fell_back_to_rule_only",
      "ai_partial_unavailable_relaxed_tolerance",
      "ai_unavailable_fallback_to_same_as_main",
      "alignment_score_below_recommended_threshold"
    ],
    "alignment_blockers": [],
    "source_family_distribution": {
      "generic_numeric_family": 3,
      "quadratic_inequality_family": 1
    },
    "candidate_problem_type_families": [
      "generic_numeric_family",
      "quadratic_inequality_family"
    ],
    "expected_skill_families": [],
    "expected_subskill_candidates": [],
    "observed_target_task_distribution": {
      "compute_numeric": 3,
      "applied_quadratic_inequality_problem": 1
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
        "problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
        "matched_example_count": 1
      }
    ],
    "coverage_floor_suggestions": [],
    "anchor_subskill_bootstrap": {
      "bootstrapped_tasks": [],
      "bootstrapped_count": 0,
      "skipped_tasks": []
    },
    "candidate_only_problem_types": [
      {
        "example_id": 3826,
        "problem_type_id": "short_answer_compute_numeric_short_answer",
        "reason": "runtime_not_supported"
      },
      {
        "example_id": 3827,
        "problem_type_id": "short_answer_compute_numeric_short_answer",
        "reason": "runtime_not_supported"
      },
      {
        "example_id": 3828,
        "problem_type_id": "short_answer_compute_numeric_short_answer",
        "reason": "runtime_not_supported"
      }
    ],
    "candidate_only_count": 3,
    "same_as_main_skill_count": 0,
    "rule_only_classification_count": 0,
    "hybrid_resolved_count": 0,
    "subskills": [
      "applied_quadratic_inequality_problem",
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
        "example_id": 3826,
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
        "classification_source": "rule_fallback_ai_unavailable",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "induction_eligibility": "eligible",
        "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "title_stem_preview": "國貿科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補）"
      },
      {
        "example_id": 3827,
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
        "classification_source": "rule_fallback_ai_unavailable",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "induction_eligibility": "eligible",
        "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "title_stem_preview": "會計科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補）"
      },
      {
        "example_id": 3828,
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
        "classification_source": "rule_fallback_ai_unavailable",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "induction_eligibility": "eligible",
        "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "title_stem_preview": "某女中二年八班同學的體重次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。體重(kg)：40~45(2人), 45~50(7人), 50~55(11人), "
      },
      {
        "example_id": 3829,
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
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
        "classification_source": "rule_fallback_ai_unavailable",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "induction_eligibility": "eligible",
        "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "title_stem_preview": "某幼兒園班上25位小朋友身高分布之直方圖如右。今班上轉出一位身高117公分之小朋友，轉入一位身高112公分之小朋友，則此時班上小朋友身高分布之直方圖為何？（圖片"
      }
    ],
    "induction_clusters": [
      {
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "short_answer",
          "compute_numeric",
          "short_answer",
          [
            "numeric_computation"
          ],
          [],
          "default"
        ],
        "source_example_ids": [
          3826,
          3827,
          3828
        ],
        "answer_type": "short_answer",
        "presentation_mode": "short_answer",
        "source_has_choices": false
      },
      {
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "short_answer",
          "applied_quadratic_inequality_problem",
          "short_answer",
          [
            "quadratic_factoring_reasoning"
          ],
          [],
          "default"
        ],
        "source_example_ids": [
          3829
        ],
        "answer_type": "short_answer",
        "presentation_mode": "short_answer",
        "source_has_choices": false
      }
    ],
    "induced_problem_type_specs": [
      {
        "problem_type_id": "short_answer_compute_numeric_short_answer",
        "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "display_name": "short_answer / compute_numeric",
        "answer_format_hint": "text_short",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          3826,
          3827,
          3828
        ],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "text_short",
          "answer_shape": "text_short",
          "answer_equivalence": "exact_string",
          "checker": "text_short_checker",
          "accepted_formats": [
            "5",
            "5.0",
            "-3"
          ],
          "source_has_choices": false,
          "equivalence_type": "exact_string",
          "checker_key": "text_short_checker",
          "presentation_mode": "short_answer"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [],
          "required_math_objects": [],
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
            "numeric_computation"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable",
            "duplicated_choices",
            "no_correct_choice",
            "multiple_correct_choices_when_single_choice"
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
            "compute_numeric"
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
            "stem": "point_quadrant"
          },
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "short_answer_compute_numeric_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks",
            "choices_policy"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "short_answer",
          "compute_numeric",
          "short_answer",
          [
            "numeric_computation"
          ],
          [],
          "default"
        ],
        "canonical_base_problem_type_id": "short_answer_compute_numeric_short_answer",
        "value_type_prefix": "",
        "_resolved_template_slot": "point_quadrant"
      },
      {
        "problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
        "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "display_name": "short_answer / applied_quadratic_inequality_problem",
        "answer_format_hint": "interval",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          3829
        ],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "source_has_choices": false,
          "answer_type": "interval",
          "answer_shape": "interval_or_union",
          "answer_semantics": "interval_union",
          "answer_equivalence": "interval_equivalence",
          "equivalence_type": "interval_equivalence",
          "checker": "interval_checker",
          "checker_key": "interval_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "interval_checker",
          "checker_selection_reason": "quadratic_inequality_interval_solution",
          "accepted_formats": [
            "-5 <= x <= 1",
            "(-5, 1]",
            "x in [-5,1]",
            "x<-2 or x>5",
            "-2<x<5",
            "x<=-2 or x>=5"
          ]
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [],
          "required_math_objects": [],
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
            "quadratic_factoring_reasoning"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable",
            "duplicated_choices",
            "no_correct_choice",
            "multiple_correct_choices_when_single_choice"
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
            "applied_quadratic_inequality_problem"
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
            "stem": "applied_quadratic_inequality_problem"
          },
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks",
            "choices_policy"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "short_answer",
          "applied_quadratic_inequality_problem",
          "short_answer",
          [
            "quadratic_factoring_reasoning"
          ],
          [],
          "default"
        ],
        "canonical_base_problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
        "value_type_prefix": "",
        "_resolved_template_slot": "applied_quadratic_inequality_problem"
      }
    ],
    "candidate_problem_types": [
      {
        "problem_type_id": "short_answer_compute_numeric_short_answer",
        "proposed_problem_type_id": "short_answer_compute_numeric_short_answer",
        "display_name": "short_answer / compute_numeric",
        "matched_example_ids": [
          3826,
          3827,
          3828
        ],
        "matched_example_count": 3,
        "unmatched_example_ids": [],
        "representative_example_id": 3826,
        "structural_features": [
          "text_short"
        ],
        "answer_contract_proposal": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "text_short",
          "answer_shape": "text_short",
          "answer_equivalence": "exact_string",
          "checker": "text_short_checker",
          "accepted_formats": [
            "5",
            "5.0",
            "-3"
          ],
          "source_has_choices": false,
          "equivalence_type": "exact_string",
          "checker_key": "text_short_checker",
          "presentation_mode": "short_answer",
          "order_matters": true,
          "accepted_format_notes": [],
          "canonical_answer_schema": "text_short"
        },
        "checker_key_proposal": "text_short_checker",
        "equivalence_type_proposal": "exact_string",
        "answer_shape": "text_short",
        "answer_semantics": "text_short",
        "presentation_mode": "short_answer",
        "source_has_choices": false,
        "selected_checker": "text_short_checker",
        "checker_selection_reason": "task_family_default",
        "coordinate_pair_presentation_note": "",
        "confidence": "high",
        "promote_recommendation": "hold_pending_problem_type_induction",
        "promote_blockers": [
          "generic_fallback_blocked_by_source_skill_binding"
        ],
        "risk_flags": [
          "ai_first_mode_fell_back_to_rule_only",
          "ai_partial_unavailable_relaxed_tolerance",
          "ai_unavailable_fallback_to_same_as_main",
          "alignment_score_below_recommended_threshold",
          "generic_fallback_blocked_by_source_skill_binding"
        ],
        "checker_contract_warnings": [],
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "short_answer",
          "compute_numeric",
          "short_answer",
          [
            "numeric_computation"
          ],
          [],
          "default"
        ],
        "problem_type_spec_draft": {
          "problem_type_id": "short_answer_compute_numeric_short_answer",
          "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "display_name": "short_answer / compute_numeric",
          "answer_format_hint": "text_short",
          "answer_fields": null,
          "answer_separator": null,
          "source_example_ids": [
            3826,
            3827,
            3828
          ],
          "answer_contract": {
            "choices_required": false,
            "choice_count": null,
            "correct_choice_count": null,
            "frontend_render_choices": false,
            "answer_type": "text_short",
            "answer_shape": "text_short",
            "answer_equivalence": "exact_string",
            "checker": "text_short_checker",
            "accepted_formats": [
              "5",
              "5.0",
              "-3"
            ],
            "source_has_choices": false,
            "equivalence_type": "exact_string",
            "checker_key": "text_short_checker",
            "presentation_mode": "short_answer"
          },
          "stem_contract": {
            "stem_must_not_embed_choices": true,
            "allowed_math_objects": [],
            "required_math_objects": [],
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
              "numeric_computation"
            ],
            "reject_if": [
              "unused_condition",
              "ambiguous_answer",
              "answer_not_derivable",
              "duplicated_choices",
              "no_correct_choice",
              "multiple_correct_choices_when_single_choice"
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
              "compute_numeric"
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
              "stem": "point_quadrant"
            },
            "templates": [
              "template_scalar_unknown",
              "template_feature_value"
            ],
            "problem_type_id": "short_answer_compute_numeric_short_answer",
            "contract_validation_blockers": [],
            "contract_validation_warnings": [
              "single_template_variant_only",
              "variation_dimensions_below_recommended_minimum"
            ]
          },
          "validator_contract": {
            "static_checks": [
              "answer_contract_checks",
              "choices_policy"
            ],
            "semantic_checks": [
              "givens_to_target_dependency"
            ],
            "runtime_smoke_count": 30
          },
          "spec_source": "phase1_induced_draft",
          "grouping_reason": "split_by_feature_signature",
          "feature_signature": [
            "short_answer",
            "compute_numeric",
            "short_answer",
            [
              "numeric_computation"
            ],
            [],
            "default"
          ],
          "canonical_base_problem_type_id": "short_answer_compute_numeric_short_answer",
          "value_type_prefix": "",
          "_resolved_template_slot": "point_quadrant"
        },
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "template_slot": "point_quadrant",
        "canonical_base_problem_type_id": "short_answer_compute_numeric_short_answer",
        "value_type_prefix": "",
        "subskill_id": "compute_numeric",
        "requires_human_action": true,
        "requires_human_rule_pack": true,
        "pending_problem_type_induction": true,
        "answer_type": "text_short",
        "runtime_status": "runtime_ready_candidate",
        "next_action": "phase2_foundation_preflight",
        "semantic_alignment": {
          "skill_problem_type_score": 0.0,
          "source_problem_type_score": 0.0256,
          "task_consistent_with_skill": true
        }
      },
      {
        "problem_type_id": "unresolved_within_current_skill",
        "proposed_problem_type_id": "unresolved_within_current_skill",
        "display_name": "short_answer / applied_quadratic_inequality_problem",
        "matched_example_ids": [
          3829
        ],
        "matched_example_count": 1,
        "unmatched_example_ids": [],
        "representative_example_id": 3829,
        "structural_features": [
          "interval_or_union"
        ],
        "answer_contract_proposal": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "source_has_choices": false,
          "answer_type": "interval",
          "answer_shape": "interval_or_union",
          "answer_semantics": "interval_union",
          "answer_equivalence": "interval_equivalence",
          "equivalence_type": "interval_set",
          "checker": "interval_checker",
          "checker_key": "interval_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "interval_checker",
          "checker_selection_reason": "quadratic_inequality_interval_solution",
          "accepted_formats": [
            "-5 <= x <= 1",
            "(-5, 1]",
            "x in [-5,1]",
            "x<-2 or x>5",
            "-2<x<5",
            "x<=-2 or x>=5"
          ],
          "order_matters": true,
          "accepted_format_notes": [],
          "canonical_answer_schema": "interval"
        },
        "checker_key_proposal": "interval_checker",
        "equivalence_type_proposal": "interval_set",
        "answer_shape": "interval_or_union",
        "answer_semantics": "interval_union",
        "presentation_mode": "short_answer",
        "source_has_choices": false,
        "selected_checker": "interval_checker",
        "checker_selection_reason": "quadratic_inequality_interval_solution",
        "coordinate_pair_presentation_note": "",
        "confidence": "high",
        "promote_recommendation": "hold_pending_problem_type_induction",
        "promote_blockers": [
          "unregistered_current_skill_problem_type"
        ],
        "risk_flags": [
          "ai_first_mode_fell_back_to_rule_only",
          "ai_partial_unavailable_relaxed_tolerance",
          "ai_unavailable_fallback_to_same_as_main",
          "alignment_score_below_recommended_threshold",
          "unregistered_current_skill_problem_type"
        ],
        "checker_contract_warnings": [],
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "short_answer",
          "applied_quadratic_inequality_problem",
          "short_answer",
          [
            "quadratic_factoring_reasoning"
          ],
          [],
          "default"
        ],
        "problem_type_spec_draft": {
          "problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
          "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
          "target_task": "applied_quadratic_inequality_problem",
          "task_family": "quadratic_inequality_family",
          "display_name": "short_answer / applied_quadratic_inequality_problem",
          "answer_format_hint": "interval",
          "answer_fields": null,
          "answer_separator": null,
          "source_example_ids": [
            3829
          ],
          "answer_contract": {
            "choices_required": false,
            "choice_count": null,
            "correct_choice_count": null,
            "frontend_render_choices": false,
            "source_has_choices": false,
            "answer_type": "interval",
            "answer_shape": "interval_or_union",
            "answer_semantics": "interval_union",
            "answer_equivalence": "interval_equivalence",
            "equivalence_type": "interval_equivalence",
            "checker": "interval_checker",
            "checker_key": "interval_checker",
            "presentation_mode": "short_answer",
            "selected_checker": "interval_checker",
            "checker_selection_reason": "quadratic_inequality_interval_solution",
            "accepted_formats": [
              "-5 <= x <= 1",
              "(-5, 1]",
              "x in [-5,1]",
              "x<-2 or x>5",
              "-2<x<5",
              "x<=-2 or x>=5"
            ]
          },
          "stem_contract": {
            "stem_must_not_embed_choices": true,
            "allowed_math_objects": [],
            "required_math_objects": [],
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
              "quadratic_factoring_reasoning"
            ],
            "reject_if": [
              "unused_condition",
              "ambiguous_answer",
              "answer_not_derivable",
              "duplicated_choices",
              "no_correct_choice",
              "multiple_correct_choices_when_single_choice"
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
              "applied_quadratic_inequality_problem"
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
              "stem": "applied_quadratic_inequality_problem"
            },
            "templates": [
              "template_scalar_unknown",
              "template_feature_value"
            ],
            "problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
            "contract_validation_blockers": [],
            "contract_validation_warnings": [
              "single_template_variant_only",
              "variation_dimensions_below_recommended_minimum"
            ]
          },
          "validator_contract": {
            "static_checks": [
              "answer_contract_checks",
              "choices_policy"
            ],
            "semantic_checks": [
              "givens_to_target_dependency"
            ],
            "runtime_smoke_count": 30
          },
          "spec_source": "phase1_induced_draft",
          "grouping_reason": "split_by_feature_signature",
          "feature_signature": [
            "short_answer",
            "applied_quadratic_inequality_problem",
            "short_answer",
            [
              "quadratic_factoring_reasoning"
            ],
            [],
            "default"
          ],
          "canonical_base_problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
          "value_type_prefix": "",
          "_resolved_template_slot": "applied_quadratic_inequality_problem"
        },
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "template_slot": "applied_quadratic_inequality_problem",
        "canonical_base_problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
        "value_type_prefix": "",
        "subskill_id": "applied_quadratic_inequality_problem",
        "answer_type": "interval",
        "runtime_status": "runtime_ready_candidate",
        "next_action": "phase2_foundation_preflight",
        "semantic_alignment": {
          "skill_problem_type_score": 0.0,
          "source_problem_type_score": 0.0244,
          "task_consistent_with_skill": true
        },
        "detected_weak_problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
        "detected_weak_target_task": "applied_quadratic_inequality_problem",
        "requires_human_action": true,
        "requires_human_rule_pack": true,
        "pending_problem_type_induction": true,
        "unresolved_reason": "unregistered_current_skill_problem_type"
      }
    ],
    "per_example_classification": [
      {
        "example_id": 3826,
        "detected_problem_type_id": "short_answer_compute_numeric_short_answer",
        "example_feature": {
          "source_example_id": 3826,
          "question_text": "國貿科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補）",
          "answer": "直方圖與折線圖",
          "choices": [],
          "has_choices": false,
          "stem_embeds_choices": false,
          "answer_type": "text_short",
          "answer_shape": "text_short",
          "checker": "text_short_checker",
          "equivalence": "exact_string",
          "math_objects": [],
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "reasoning_type": [
            "numeric_computation"
          ],
          "required_derivation": true,
          "source_quality_issues": [],
          "source_quality_reject": false,
          "candidate_only": false,
          "variables": [],
          "givens": [],
          "target": "compute_numeric",
          "classifier_source": "rule_fallback_ai_unavailable",
          "math_meta_tags": [],
          "forced_target_task": "",
          "meta_answer_format_hint": "",
          "semantic_classification": {
            "ai_target_task": "",
            "ai_task_family": "",
            "ai_confidence": 0.0,
            "ai_best_candidate_id": "needs_review",
            "ai_evidence": [],
            "ai_rejected_candidates": {},
            "ai_available": false,
            "ai_error": "ai_api_key_missing",
            "ai_unavailable_reason": "missing_api_key",
            "ai_semantic_status": "unavailable",
            "ai_invalid_response_reason": "",
            "parser_error": "",
            "raw_response_preview": "",
            "sanitized_response_preview": "",
            "failed_stage": "",
            "rule_target_task": "compute_numeric",
            "rule_task_family": "generic_numeric_family",
            "rule_confidence": 0.2,
            "final_target_task": "compute_numeric",
            "final_task_family": "generic_numeric_family",
            "classifier_source": "rule_fallback_ai_unavailable",
            "classification_decision": "",
            "conflict_reason": "ai_api_key_missing",
            "source_mapping_warning": "",
            "requires_human_action": true,
            "ai_notes": "",
            "skill_scoped_candidates": [
              {
                "candidate_id": "C1",
                "target_task": "compute_numeric",
                "task_family": "generic_numeric_family",
                "problem_type_id": "compute_numeric",
                "label": "compute_numeric",
                "candidate_source": "outsider",
                "in_anchor_scope": false,
                "answer_type": "numeric",
                "answer_shape": "numeric",
                "math_objects": [],
                "checker_key": "numeric_checker",
                "equivalence_type": "numeric_equivalence",
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
                    "compute_numeric"
                  ]
                },
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
                }
              },
              {
                "candidate_id": "needs_review",
                "target_task": "",
                "task_family": "",
                "problem_type_id": "needs_review",
                "label": "needs_review",
                "candidate_source": "needs_review",
                "in_anchor_scope": false,
                "answer_type": "",
                "answer_shape": "",
                "math_objects": [],
                "checker_key": "manual_review_checker",
                "equivalence_type": "manual_review_or_ai_judged",
                "generator_contract": {},
                "parameter_schema": {}
              }
            ],
            "outsider_candidates": [
              "C1"
            ],
            "selected_subskill": "compute_numeric",
            "selected_problem_type": "compute_numeric",
            "candidate_source": "needs_review",
            "selected_generator_contract": {},
            "parameter_schema": {},
            "variable_randomization_notes": [],
            "checker_key": "",
            "equivalence_type": "",
            "skill_scope_trusted": true,
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "math_objects": [],
            "answer_type": "short_answer",
            "answer_shape": "text_short",
            "source_type": "worked_example",
            "example_label": "例題2",
            "practice_label": "",
            "linked_example": "",
            "linked_example_id": null,
            "linked_example_task_family": "",
            "structure_consistency": "not_applicable",
            "sequence_context_used": true,
            "structure_context_used": true,
            "confidence_adjustment_reason": "sequence_context_used",
            "possible_structure_mismatch": false,
            "possible_mixed_source_context": false
          },
          "source_structure_context": {
            "source_type": "worked_example",
            "example_label": "例題2",
            "practice_label": "",
            "linked_example": "",
            "section_order": 0,
            "example_number": 2,
            "practice_number": null,
            "nearby_worked_examples": [],
            "linked_worked_example": null,
            "linked_practices": [
              {
                "example_id": 3827,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習2",
                "section_order": 0,
                "title_head": "隨堂練習 2"
              }
            ],
            "same_section_sequence": [
              {
                "example_id": 3826,
                "source_type": "worked_example",
                "example_label": "例題2",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 2"
              },
              {
                "example_id": 3827,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習2",
                "section_order": 0,
                "title_head": "隨堂練習 2"
              },
              {
                "example_id": 3828,
                "source_type": "basic_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 基礎題3"
              },
              {
                "example_id": 3829,
                "source_type": "advanced_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 進階題9"
              }
            ]
          },
          "induction_tier": "core",
          "enrichment_reasons": [],
          "included_in_core_induction": true,
          "source_skill_scope_locked": true,
          "skill_mapping_authority": "textbook_examples.skill_id",
          "classification_scope": "within_current_skill",
          "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
        "classification_reason": "rule_fallback_ai_unavailable",
        "risk_flags": [
          "requires_human_action",
          "candidate_only_problem_type"
        ],
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "outsider",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [
            "C1"
          ],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "worked_example",
          "example_label": "例題2",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "subskill_id": "compute_numeric",
        "classification_source": "rule_fallback_ai_unavailable",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "requires_human_rule_pack": true,
        "induction_eligibility": "eligible"
      },
      {
        "example_id": 3827,
        "detected_problem_type_id": "short_answer_compute_numeric_short_answer",
        "example_feature": {
          "source_example_id": 3827,
          "question_text": "會計科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。（圖片待補）",
          "answer": "略",
          "choices": [],
          "has_choices": false,
          "stem_embeds_choices": false,
          "answer_type": "text_short",
          "answer_shape": "text_short",
          "checker": "text_short_checker",
          "equivalence": "exact_string",
          "math_objects": [],
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "reasoning_type": [
            "numeric_computation"
          ],
          "required_derivation": true,
          "source_quality_issues": [],
          "source_quality_reject": false,
          "candidate_only": false,
          "variables": [],
          "givens": [],
          "target": "compute_numeric",
          "classifier_source": "rule_fallback_ai_unavailable",
          "math_meta_tags": [],
          "forced_target_task": "",
          "meta_answer_format_hint": "",
          "semantic_classification": {
            "ai_target_task": "",
            "ai_task_family": "",
            "ai_confidence": 0.0,
            "ai_best_candidate_id": "needs_review",
            "ai_evidence": [],
            "ai_rejected_candidates": {},
            "ai_available": false,
            "ai_error": "ai_api_key_missing",
            "ai_unavailable_reason": "missing_api_key",
            "ai_semantic_status": "unavailable",
            "ai_invalid_response_reason": "",
            "parser_error": "",
            "raw_response_preview": "",
            "sanitized_response_preview": "",
            "failed_stage": "",
            "rule_target_task": "compute_numeric",
            "rule_task_family": "generic_numeric_family",
            "rule_confidence": 0.2,
            "final_target_task": "compute_numeric",
            "final_task_family": "generic_numeric_family",
            "classifier_source": "rule_fallback_ai_unavailable",
            "classification_decision": "",
            "conflict_reason": "ai_api_key_missing",
            "source_mapping_warning": "",
            "requires_human_action": true,
            "ai_notes": "",
            "skill_scoped_candidates": [
              {
                "candidate_id": "C1",
                "target_task": "compute_numeric",
                "task_family": "generic_numeric_family",
                "problem_type_id": "compute_numeric",
                "label": "compute_numeric",
                "candidate_source": "structure",
                "in_anchor_scope": false,
                "answer_type": "numeric",
                "answer_shape": "numeric",
                "math_objects": [],
                "checker_key": "numeric_checker",
                "equivalence_type": "numeric_equivalence",
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
                    "compute_numeric"
                  ]
                },
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
                }
              },
              {
                "candidate_id": "needs_review",
                "target_task": "",
                "task_family": "",
                "problem_type_id": "needs_review",
                "label": "needs_review",
                "candidate_source": "needs_review",
                "in_anchor_scope": false,
                "answer_type": "",
                "answer_shape": "",
                "math_objects": [],
                "checker_key": "manual_review_checker",
                "equivalence_type": "manual_review_or_ai_judged",
                "generator_contract": {},
                "parameter_schema": {}
              }
            ],
            "outsider_candidates": [],
            "selected_subskill": "compute_numeric",
            "selected_problem_type": "compute_numeric",
            "candidate_source": "needs_review",
            "selected_generator_contract": {},
            "parameter_schema": {},
            "variable_randomization_notes": [],
            "checker_key": "",
            "equivalence_type": "",
            "skill_scope_trusted": true,
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "math_objects": [],
            "answer_type": "short_answer",
            "answer_shape": "text_short",
            "source_type": "in_class_practice",
            "example_label": "",
            "practice_label": "隨堂練習2",
            "linked_example": "例題2",
            "linked_example_id": 3826,
            "linked_example_task_family": "generic_numeric_family",
            "structure_consistency": "consistent",
            "sequence_context_used": true,
            "structure_context_used": true,
            "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
            "possible_structure_mismatch": false,
            "possible_mixed_source_context": false
          },
          "source_structure_context": {
            "source_type": "in_class_practice",
            "example_label": "",
            "practice_label": "隨堂練習2",
            "linked_example": "例題2",
            "section_order": 0,
            "example_number": null,
            "practice_number": 2,
            "nearby_worked_examples": [
              {
                "example_id": 3826,
                "source_type": "worked_example",
                "example_label": "例題2",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 2"
              }
            ],
            "linked_worked_example": {
              "example_id": 3826,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 2"
            },
            "linked_practices": [],
            "same_section_sequence": [
              {
                "example_id": 3826,
                "source_type": "worked_example",
                "example_label": "例題2",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 2"
              },
              {
                "example_id": 3827,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習2",
                "section_order": 0,
                "title_head": "隨堂練習 2"
              },
              {
                "example_id": 3828,
                "source_type": "basic_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 基礎題3"
              },
              {
                "example_id": 3829,
                "source_type": "advanced_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 進階題9"
              }
            ]
          },
          "induction_tier": "core",
          "enrichment_reasons": [],
          "included_in_core_induction": true,
          "source_skill_scope_locked": true,
          "skill_mapping_authority": "textbook_examples.skill_id",
          "classification_scope": "within_current_skill",
          "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
        "classification_reason": "rule_fallback_ai_unavailable",
        "risk_flags": [
          "requires_human_action",
          "candidate_only_problem_type"
        ],
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習2",
          "linked_example": "例題2",
          "linked_example_id": 3826,
          "linked_example_task_family": "generic_numeric_family",
          "structure_consistency": "consistent",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "subskill_id": "compute_numeric",
        "classification_source": "rule_fallback_ai_unavailable",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "requires_human_rule_pack": true,
        "induction_eligibility": "eligible"
      },
      {
        "example_id": 3828,
        "detected_problem_type_id": "short_answer_compute_numeric_short_answer",
        "example_feature": {
          "source_example_id": 3828,
          "question_text": "某女中二年八班同學的體重次數分配表如下，試畫出其對應的直方圖與次數分配折線圖。體重(kg)：40~45(2人), 45~50(7人), 50~55(11人), 55~60(10人), 60~65(5人), 65~70(3人), 70~75(2人)。（圖片待補）",
          "answer": "略",
          "choices": [],
          "has_choices": false,
          "stem_embeds_choices": false,
          "answer_type": "text_short",
          "answer_shape": "text_short",
          "checker": "text_short_checker",
          "equivalence": "exact_string",
          "math_objects": [],
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "reasoning_type": [
            "numeric_computation"
          ],
          "required_derivation": true,
          "source_quality_issues": [],
          "source_quality_reject": false,
          "candidate_only": false,
          "variables": [],
          "givens": [],
          "target": "compute_numeric",
          "classifier_source": "rule_fallback_ai_unavailable",
          "math_meta_tags": [],
          "forced_target_task": "",
          "meta_answer_format_hint": "",
          "semantic_classification": {
            "ai_target_task": "",
            "ai_task_family": "",
            "ai_confidence": 0.0,
            "ai_best_candidate_id": "needs_review",
            "ai_evidence": [],
            "ai_rejected_candidates": {},
            "ai_available": false,
            "ai_error": "ai_api_key_missing",
            "ai_unavailable_reason": "missing_api_key",
            "ai_semantic_status": "unavailable",
            "ai_invalid_response_reason": "",
            "parser_error": "",
            "raw_response_preview": "",
            "sanitized_response_preview": "",
            "failed_stage": "",
            "rule_target_task": "compute_numeric",
            "rule_task_family": "generic_numeric_family",
            "rule_confidence": 0.2,
            "final_target_task": "compute_numeric",
            "final_task_family": "generic_numeric_family",
            "classifier_source": "rule_fallback_ai_unavailable",
            "classification_decision": "",
            "conflict_reason": "ai_api_key_missing",
            "source_mapping_warning": "",
            "requires_human_action": true,
            "ai_notes": "",
            "skill_scoped_candidates": [
              {
                "candidate_id": "C1",
                "target_task": "compute_numeric",
                "task_family": "generic_numeric_family",
                "problem_type_id": "compute_numeric",
                "label": "compute_numeric",
                "candidate_source": "structure",
                "in_anchor_scope": false,
                "answer_type": "numeric",
                "answer_shape": "numeric",
                "math_objects": [],
                "checker_key": "numeric_checker",
                "equivalence_type": "numeric_equivalence",
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
                    "compute_numeric"
                  ]
                },
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
                }
              },
              {
                "candidate_id": "needs_review",
                "target_task": "",
                "task_family": "",
                "problem_type_id": "needs_review",
                "label": "needs_review",
                "candidate_source": "needs_review",
                "in_anchor_scope": false,
                "answer_type": "",
                "answer_shape": "",
                "math_objects": [],
                "checker_key": "manual_review_checker",
                "equivalence_type": "manual_review_or_ai_judged",
                "generator_contract": {},
                "parameter_schema": {}
              }
            ],
            "outsider_candidates": [],
            "selected_subskill": "compute_numeric",
            "selected_problem_type": "compute_numeric",
            "candidate_source": "needs_review",
            "selected_generator_contract": {},
            "parameter_schema": {},
            "variable_randomization_notes": [],
            "checker_key": "",
            "equivalence_type": "",
            "skill_scope_trusted": true,
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "math_objects": [],
            "answer_type": "short_answer",
            "answer_shape": "text_short",
            "source_type": "basic_exercise",
            "example_label": "",
            "practice_label": "",
            "linked_example": "",
            "linked_example_id": null,
            "linked_example_task_family": "",
            "structure_consistency": "not_applicable",
            "sequence_context_used": true,
            "structure_context_used": true,
            "confidence_adjustment_reason": "sequence_context_used",
            "possible_structure_mismatch": false,
            "possible_mixed_source_context": false
          },
          "source_structure_context": {
            "source_type": "basic_exercise",
            "example_label": "",
            "practice_label": "",
            "linked_example": "",
            "section_order": 0,
            "example_number": null,
            "practice_number": null,
            "nearby_worked_examples": [
              {
                "example_id": 3826,
                "source_type": "worked_example",
                "example_label": "例題2",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 2"
              }
            ],
            "linked_worked_example": null,
            "linked_practices": [],
            "same_section_sequence": [
              {
                "example_id": 3826,
                "source_type": "worked_example",
                "example_label": "例題2",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 2"
              },
              {
                "example_id": 3827,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習2",
                "section_order": 0,
                "title_head": "隨堂練習 2"
              },
              {
                "example_id": 3828,
                "source_type": "basic_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 基礎題3"
              },
              {
                "example_id": 3829,
                "source_type": "advanced_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 進階題9"
              }
            ]
          },
          "induction_tier": "core",
          "enrichment_reasons": [],
          "included_in_core_induction": true,
          "source_skill_scope_locked": true,
          "skill_mapping_authority": "textbook_examples.skill_id",
          "classification_scope": "within_current_skill",
          "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
        "classification_reason": "rule_fallback_ai_unavailable",
        "risk_flags": [
          "requires_human_action",
          "candidate_only_problem_type"
        ],
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "basic_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "subskill_id": "compute_numeric",
        "classification_source": "rule_fallback_ai_unavailable",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "requires_human_rule_pack": true,
        "induction_eligibility": "eligible"
      },
      {
        "example_id": 3829,
        "detected_problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
        "example_feature": {
          "source_example_id": 3829,
          "question_text": "某幼兒園班上25位小朋友身高分布之直方圖如右。今班上轉出一位身高117公分之小朋友，轉入一位身高112公分之小朋友，則此時班上小朋友身高分布之直方圖為何？（圖片待補）",
          "answer": "115~120組次數減1，110~115組次數加1",
          "choices": [],
          "has_choices": false,
          "stem_embeds_choices": false,
          "answer_type": "text_short",
          "answer_shape": "text_short",
          "checker": "text_short_checker",
          "equivalence": "exact_string",
          "math_objects": [],
          "target_task": "applied_quadratic_inequality_problem",
          "task_family": "quadratic_inequality_family",
          "reasoning_type": [
            "quadratic_factoring_reasoning"
          ],
          "required_derivation": true,
          "source_quality_issues": [],
          "source_quality_reject": false,
          "candidate_only": false,
          "variables": [],
          "givens": [],
          "target": "applied_quadratic_inequality_problem",
          "classifier_source": "rule_fallback_ai_unavailable",
          "math_meta_tags": [
            "[Task: Applied_Context]"
          ],
          "forced_target_task": "applied_quadratic_inequality_problem",
          "meta_answer_format_hint": "interval",
          "semantic_classification": {
            "ai_target_task": "",
            "ai_task_family": "",
            "ai_confidence": 0.0,
            "ai_best_candidate_id": "needs_review",
            "ai_evidence": [],
            "ai_rejected_candidates": {},
            "ai_available": false,
            "ai_error": "ai_api_key_missing",
            "ai_unavailable_reason": "missing_api_key",
            "ai_semantic_status": "unavailable",
            "ai_invalid_response_reason": "",
            "parser_error": "",
            "raw_response_preview": "",
            "sanitized_response_preview": "",
            "failed_stage": "",
            "rule_target_task": "applied_quadratic_inequality_problem",
            "rule_task_family": "quadratic_inequality_family",
            "rule_confidence": 0.5,
            "final_target_task": "applied_quadratic_inequality_problem",
            "final_task_family": "quadratic_inequality_family",
            "classifier_source": "rule_fallback_ai_unavailable",
            "classification_decision": "",
            "conflict_reason": "ai_api_key_missing",
            "source_mapping_warning": "",
            "requires_human_action": true,
            "ai_notes": "",
            "skill_scoped_candidates": [
              {
                "candidate_id": "C1",
                "target_task": "compute_numeric",
                "task_family": "generic_numeric_family",
                "problem_type_id": "compute_numeric",
                "label": "compute_numeric",
                "candidate_source": "structure",
                "in_anchor_scope": false,
                "answer_type": "numeric",
                "answer_shape": "numeric",
                "math_objects": [],
                "checker_key": "numeric_checker",
                "equivalence_type": "numeric_equivalence",
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
                    "compute_numeric"
                  ]
                },
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
                }
              },
              {
                "candidate_id": "C2",
                "target_task": "applied_quadratic_inequality_problem",
                "task_family": "quadratic_inequality_family",
                "problem_type_id": "applied_quadratic_inequality_problem",
                "label": "applied_quadratic_inequality_problem",
                "candidate_source": "outsider",
                "in_anchor_scope": false,
                "answer_type": "numeric",
                "answer_shape": "numeric",
                "math_objects": [],
                "checker_key": "numeric_checker",
                "equivalence_type": "numeric_equivalence",
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
                    "applied_quadratic_inequality_problem"
                  ]
                },
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
                }
              },
              {
                "candidate_id": "needs_review",
                "target_task": "",
                "task_family": "",
                "problem_type_id": "needs_review",
                "label": "needs_review",
                "candidate_source": "needs_review",
                "in_anchor_scope": false,
                "answer_type": "",
                "answer_shape": "",
                "math_objects": [],
                "checker_key": "manual_review_checker",
                "equivalence_type": "manual_review_or_ai_judged",
                "generator_contract": {},
                "parameter_schema": {}
              }
            ],
            "outsider_candidates": [
              "C2"
            ],
            "selected_subskill": "applied_quadratic_inequality_problem",
            "selected_problem_type": "applied_quadratic_inequality_problem",
            "candidate_source": "needs_review",
            "selected_generator_contract": {},
            "parameter_schema": {},
            "variable_randomization_notes": [],
            "checker_key": "",
            "equivalence_type": "",
            "skill_scope_trusted": true,
            "target_task": "applied_quadratic_inequality_problem",
            "task_family": "quadratic_inequality_family",
            "math_objects": [],
            "answer_type": "short_answer",
            "answer_shape": "text_short",
            "source_type": "advanced_exercise",
            "example_label": "",
            "practice_label": "",
            "linked_example": "",
            "linked_example_id": null,
            "linked_example_task_family": "",
            "structure_consistency": "not_applicable",
            "sequence_context_used": true,
            "structure_context_used": true,
            "confidence_adjustment_reason": "possible_structure_mismatch_penalty; sequence_context_used",
            "possible_structure_mismatch": true,
            "possible_mixed_source_context": true
          },
          "source_structure_context": {
            "source_type": "advanced_exercise",
            "example_label": "",
            "practice_label": "",
            "linked_example": "",
            "section_order": 0,
            "example_number": null,
            "practice_number": null,
            "nearby_worked_examples": [
              {
                "example_id": 3826,
                "source_type": "worked_example",
                "example_label": "例題2",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 2"
              }
            ],
            "linked_worked_example": null,
            "linked_practices": [],
            "same_section_sequence": [
              {
                "example_id": 3826,
                "source_type": "worked_example",
                "example_label": "例題2",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 2"
              },
              {
                "example_id": 3827,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習2",
                "section_order": 0,
                "title_head": "隨堂練習 2"
              },
              {
                "example_id": 3828,
                "source_type": "basic_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 基礎題3"
              },
              {
                "example_id": 3829,
                "source_type": "advanced_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 進階題9"
              }
            ]
          },
          "induction_tier": "core",
          "enrichment_reasons": [],
          "included_in_core_induction": true,
          "source_skill_scope_locked": true,
          "skill_mapping_authority": "textbook_examples.skill_id",
          "classification_scope": "within_current_skill",
          "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
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
        "classification_reason": "rule_fallback_ai_unavailable",
        "risk_flags": [
          "requires_human_action"
        ],
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "applied_quadratic_inequality_problem",
          "rule_task_family": "quadratic_inequality_family",
          "rule_confidence": 0.5,
          "final_target_task": "applied_quadratic_inequality_problem",
          "final_task_family": "quadratic_inequality_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "C2",
              "target_task": "applied_quadratic_inequality_problem",
              "task_family": "quadratic_inequality_family",
              "problem_type_id": "applied_quadratic_inequality_problem",
              "label": "applied_quadratic_inequality_problem",
              "candidate_source": "outsider",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                  "applied_quadratic_inequality_problem"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [
            "C2"
          ],
          "selected_subskill": "applied_quadratic_inequality_problem",
          "selected_problem_type": "applied_quadratic_inequality_problem",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "applied_quadratic_inequality_problem",
          "task_family": "quadratic_inequality_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "advanced_exercise",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "possible_structure_mismatch_penalty; sequence_context_used",
          "possible_structure_mismatch": true,
          "possible_mixed_source_context": true
        },
        "subskill_id": "applied_quadratic_inequality_problem",
        "classification_source": "rule_fallback_ai_unavailable",
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
      "short_answer_compute_numeric_short_answer",
      "short_answer_applied_quadratic_inequality_problem_short_answer"
    ],
    "classifier_gate": {
      "status": "classifier_auto_pending_promote_with_warning",
      "allowed": true,
      "warnings": [
        "insufficient_examples",
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance",
        "ai_unavailable_fallback_to_same_as_main",
        "alignment_score_below_recommended_threshold",
        "generic_fallback_blocked_by_source_skill_binding"
      ]
    },
    "generator_draft_gate": {
      "status": "generator_draft_allowed_with_low_source_warning",
      "allowed": true,
      "warnings": [
        "low_source_examples",
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance",
        "ai_unavailable_fallback_to_same_as_main",
        "alignment_score_below_recommended_threshold",
        "generic_fallback_blocked_by_source_skill_binding"
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
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance",
        "ai_unavailable_fallback_to_same_as_main",
        "alignment_score_below_recommended_threshold",
        "generic_fallback_blocked_by_source_skill_binding"
      ]
    },
    "exception_review_gate": {
      "required": false,
      "reasons": []
    },
    "next_action": "phase2_generate_from_induced_specs",
    "source_skill_scope_locked": true,
    "source_skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
    "classification_scope": "within_current_skill",
    "skill_mapping_authority": "textbook_examples.skill_id",
    "human_confirmed_rule_pack_applied": false,
    "matched_registered_yaml_rule_pack": "",
    "ai_classification_overridden_by_human_confirmed_rule_pack": false,
    "curated_specs_available": true
  },
  "classifier_source": "neutral_fallback+phase1_induction",
  "ai_bootstrap_used": true,
  "ai_bootstrap_status": "failed",
  "ai_bootstrap_confidence_summary": {
    "count": 4,
    "avg": 0.0,
    "low_confidence_count": 4
  },
  "inspect_report_note": "Missing classifier/rule pack, AI bootstrap attempted.",
  "ai_bootstrap_error": "resolved_google_but_fell_back_to_local",
  "ai_bootstrap_raw_response_preview": "",
  "ai_bootstrap_validation_errors": [],
  "ai_bootstrap_prompt_version": "gencode_phase1_ai_bootstrap_v2",
  "ai_bootstrap_model": "",
  "ai_bootstrap_provider": "",
  "ai_bootstrap_config_source": "",
  "default_problem_type_used": false,
  "problem_type_spec_first": true,
  "spec_defined_problem_type_ids": [
    "short_answer_compute_numeric_short_answer",
    "short_answer_applied_quadratic_inequality_problem_short_answer"
  ],
  "spec_mode": "ai_first_induce_from_sources",
  "induced_problem_type_specs": [
    {
      "problem_type_id": "short_answer_compute_numeric_short_answer",
      "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
      "target_task": "compute_numeric",
      "task_family": "generic_numeric_family",
      "display_name": "short_answer / compute_numeric",
      "answer_format_hint": "text_short",
      "answer_fields": null,
      "answer_separator": null,
      "source_example_ids": [
        3826,
        3827,
        3828
      ],
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "answer_equivalence": "exact_string",
        "checker": "text_short_checker",
        "accepted_formats": [
          "5",
          "5.0",
          "-3"
        ],
        "source_has_choices": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "presentation_mode": "short_answer"
      },
      "stem_contract": {
        "stem_must_not_embed_choices": true,
        "allowed_math_objects": [],
        "required_math_objects": [],
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
          "numeric_computation"
        ],
        "reject_if": [
          "unused_condition",
          "ambiguous_answer",
          "answer_not_derivable",
          "duplicated_choices",
          "no_correct_choice",
          "multiple_correct_choices_when_single_choice"
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
          "compute_numeric"
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
          "stem": "point_quadrant"
        },
        "templates": [
          "template_scalar_unknown",
          "template_feature_value"
        ],
        "problem_type_id": "short_answer_compute_numeric_short_answer",
        "contract_validation_blockers": [],
        "contract_validation_warnings": [
          "single_template_variant_only",
          "variation_dimensions_below_recommended_minimum"
        ]
      },
      "validator_contract": {
        "static_checks": [
          "answer_contract_checks",
          "choices_policy"
        ],
        "semantic_checks": [
          "givens_to_target_dependency"
        ],
        "runtime_smoke_count": 30
      },
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "short_answer",
        "compute_numeric",
        "short_answer",
        [
          "numeric_computation"
        ],
        [],
        "default"
      ],
      "canonical_base_problem_type_id": "short_answer_compute_numeric_short_answer",
      "value_type_prefix": "",
      "_resolved_template_slot": "point_quadrant"
    },
    {
      "problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
      "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
      "target_task": "applied_quadratic_inequality_problem",
      "task_family": "quadratic_inequality_family",
      "display_name": "short_answer / applied_quadratic_inequality_problem",
      "answer_format_hint": "interval",
      "answer_fields": null,
      "answer_separator": null,
      "source_example_ids": [
        3829
      ],
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "source_has_choices": false,
        "answer_type": "interval",
        "answer_shape": "interval_or_union",
        "answer_semantics": "interval_union",
        "answer_equivalence": "interval_equivalence",
        "equivalence_type": "interval_equivalence",
        "checker": "interval_checker",
        "checker_key": "interval_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "interval_checker",
        "checker_selection_reason": "quadratic_inequality_interval_solution",
        "accepted_formats": [
          "-5 <= x <= 1",
          "(-5, 1]",
          "x in [-5,1]",
          "x<-2 or x>5",
          "-2<x<5",
          "x<=-2 or x>=5"
        ]
      },
      "stem_contract": {
        "stem_must_not_embed_choices": true,
        "allowed_math_objects": [],
        "required_math_objects": [],
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
          "quadratic_factoring_reasoning"
        ],
        "reject_if": [
          "unused_condition",
          "ambiguous_answer",
          "answer_not_derivable",
          "duplicated_choices",
          "no_correct_choice",
          "multiple_correct_choices_when_single_choice"
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
          "applied_quadratic_inequality_problem"
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
          "stem": "applied_quadratic_inequality_problem"
        },
        "templates": [
          "template_scalar_unknown",
          "template_feature_value"
        ],
        "problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
        "contract_validation_blockers": [],
        "contract_validation_warnings": [
          "single_template_variant_only",
          "variation_dimensions_below_recommended_minimum"
        ]
      },
      "validator_contract": {
        "static_checks": [
          "answer_contract_checks",
          "choices_policy"
        ],
        "semantic_checks": [
          "givens_to_target_dependency"
        ],
        "runtime_smoke_count": 30
      },
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "short_answer",
        "applied_quadratic_inequality_problem",
        "short_answer",
        [
          "quadratic_factoring_reasoning"
        ],
        [],
        "default"
      ],
      "canonical_base_problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
      "value_type_prefix": "",
      "_resolved_template_slot": "applied_quadratic_inequality_problem"
    }
  ],
  "induction_clusters": [
    {
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "short_answer",
        "compute_numeric",
        "short_answer",
        [
          "numeric_computation"
        ],
        [],
        "default"
      ],
      "source_example_ids": [
        3826,
        3827,
        3828
      ],
      "answer_type": "short_answer",
      "presentation_mode": "short_answer",
      "source_has_choices": false
    },
    {
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "short_answer",
        "applied_quadratic_inequality_problem",
        "short_answer",
        [
          "quadratic_factoring_reasoning"
        ],
        [],
        "default"
      ],
      "source_example_ids": [
        3829
      ],
      "answer_type": "short_answer",
      "presentation_mode": "short_answer",
      "source_has_choices": false
    }
  ],
  "human_review_items": [],
  "source_quality_reject_examples": [],
  "proposal_items": [
    {
      "problem_type_id": "text_short_compute_numeric",
      "proposed_problem_type_id": "text_short_compute_numeric",
      "display_name": "text_short / compute_numeric",
      "matched_example_ids": [
        3826,
        3827,
        3828
      ],
      "matched_example_count": 3,
      "unmatched_example_ids": [],
      "representative_example_id": 3826,
      "structural_features": [
        "text_short"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "answer_equivalence": "exact_string",
        "checker": "text_short_checker",
        "accepted_formats": [
          "5",
          "5.0",
          "-3"
        ],
        "source_has_choices": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "presentation_mode": "",
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "text_short"
      },
      "checker_key_proposal": "text_short_checker",
      "equivalence_type_proposal": "exact_string",
      "answer_shape": "text_short",
      "answer_semantics": "text_short",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "text_short_checker",
      "checker_selection_reason": "task_family_default",
      "coordinate_pair_presentation_note": "",
      "confidence": "high",
      "promote_recommendation": "hold_pending_problem_type_induction",
      "promote_blockers": [
        "generic_fallback_blocked_by_source_skill_binding"
      ],
      "risk_flags": [
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance",
        "ai_unavailable_fallback_to_same_as_main",
        "alignment_score_below_recommended_threshold",
        "generic_fallback_blocked_by_source_skill_binding"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "short_answer",
        "compute_numeric",
        "short_answer",
        [
          "numeric_computation"
        ],
        [],
        "default"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "expression_compute_text_short_expression",
        "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "display_name": "short_answer / compute_numeric",
        "answer_format_hint": "text_short",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          3826,
          3827,
          3828
        ],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "text_short",
          "answer_shape": "text_short",
          "answer_equivalence": "exact_string",
          "checker": "text_short_checker",
          "accepted_formats": [
            "5",
            "5.0",
            "-3"
          ],
          "source_has_choices": false,
          "equivalence_type": "exact_string",
          "checker_key": "text_short_checker",
          "presentation_mode": "short_answer"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [],
          "required_math_objects": [],
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
            "numeric_computation"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable",
            "duplicated_choices",
            "no_correct_choice",
            "multiple_correct_choices_when_single_choice"
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
            "compute_numeric"
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
            "stem": "point_quadrant"
          },
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "short_answer_compute_numeric_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks",
            "choices_policy"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "short_answer",
          "compute_numeric",
          "short_answer",
          [
            "numeric_computation"
          ],
          [],
          "default"
        ],
        "canonical_base_problem_type_id": "short_answer_compute_numeric_short_answer",
        "value_type_prefix": "",
        "_resolved_template_slot": "point_quadrant"
      },
      "generator_readiness": "pending_problem_type_induction",
      "usable_for_phase3": false,
      "template_slot": "point_quadrant",
      "canonical_base_problem_type_id": "short_answer_compute_numeric_short_answer",
      "value_type_prefix": "",
      "subskill_id": "compute_numeric",
      "requires_human_action": true,
      "requires_human_rule_pack": true,
      "pending_problem_type_induction": true,
      "answer_type": "text_short",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0256,
        "task_consistent_with_skill": true
      }
    },
    {
      "problem_type_id": "text_short_applied_quadratic_inequality_problem",
      "proposed_problem_type_id": "text_short_applied_quadratic_inequality_problem",
      "display_name": "text_short / applied_quadratic_inequality_problem",
      "matched_example_ids": [
        3829
      ],
      "matched_example_count": 1,
      "unmatched_example_ids": [],
      "representative_example_id": 3829,
      "structural_features": [
        "interval_or_union"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "source_has_choices": false,
        "answer_type": "text_short",
        "answer_shape": "interval_or_union",
        "answer_semantics": "interval_union",
        "answer_equivalence": "exact_string",
        "equivalence_type": "exact_string",
        "checker": "text_short_checker",
        "checker_key": "text_short_checker",
        "presentation_mode": "",
        "selected_checker": "interval_checker",
        "checker_selection_reason": "quadratic_inequality_interval_solution",
        "accepted_formats": [
          "-5 <= x <= 1",
          "(-5, 1]",
          "x in [-5,1]",
          "x<-2 or x>5",
          "-2<x<5",
          "x<=-2 or x>=5"
        ],
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "interval"
      },
      "checker_key_proposal": "text_short_checker",
      "equivalence_type_proposal": "exact_string",
      "answer_shape": "interval_or_union",
      "answer_semantics": "interval_union",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "interval_checker",
      "checker_selection_reason": "quadratic_inequality_interval_solution",
      "coordinate_pair_presentation_note": "",
      "confidence": "high",
      "promote_recommendation": "hold_pending_problem_type_induction",
      "promote_blockers": [
        "unregistered_current_skill_problem_type"
      ],
      "risk_flags": [
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance",
        "ai_unavailable_fallback_to_same_as_main",
        "alignment_score_below_recommended_threshold",
        "unregistered_current_skill_problem_type"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "short_answer",
        "applied_quadratic_inequality_problem",
        "short_answer",
        [
          "quadratic_factoring_reasoning"
        ],
        [],
        "default"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "unresolved_within_current_skill",
        "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "display_name": "short_answer / applied_quadratic_inequality_problem",
        "answer_format_hint": "interval",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          3829
        ],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "source_has_choices": false,
          "answer_type": "interval",
          "answer_shape": "interval_or_union",
          "answer_semantics": "interval_union",
          "answer_equivalence": "interval_set",
          "equivalence_type": "interval_set",
          "checker": "interval_checker",
          "checker_key": "interval_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "interval_checker",
          "checker_selection_reason": "quadratic_inequality_interval_solution",
          "accepted_formats": [
            "-5 <= x <= 1",
            "(-5, 1]",
            "x in [-5,1]",
            "x<-2 or x>5",
            "-2<x<5",
            "x<=-2 or x>=5"
          ]
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [],
          "required_math_objects": [],
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
            "quadratic_factoring_reasoning"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable",
            "duplicated_choices",
            "no_correct_choice",
            "multiple_correct_choices_when_single_choice"
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
            "applied_quadratic_inequality_problem"
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
            "stem": "applied_quadratic_inequality_problem"
          },
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks",
            "choices_policy"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "short_answer",
          "applied_quadratic_inequality_problem",
          "short_answer",
          [
            "quadratic_factoring_reasoning"
          ],
          [],
          "default"
        ],
        "canonical_base_problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
        "value_type_prefix": "",
        "_resolved_template_slot": "applied_quadratic_inequality_problem"
      },
      "generator_readiness": "pending_problem_type_induction",
      "usable_for_phase3": false,
      "template_slot": "applied_quadratic_inequality_problem",
      "canonical_base_problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
      "value_type_prefix": "",
      "subskill_id": "applied_quadratic_inequality_problem",
      "answer_type": "interval",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0244,
        "task_consistent_with_skill": true
      },
      "detected_weak_problem_type_id": "short_answer_applied_quadratic_inequality_problem_short_answer",
      "detected_weak_target_task": "applied_quadratic_inequality_problem",
      "requires_human_action": true,
      "requires_human_rule_pack": true,
      "pending_problem_type_induction": true,
      "unresolved_reason": "unregistered_current_skill_problem_type"
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
