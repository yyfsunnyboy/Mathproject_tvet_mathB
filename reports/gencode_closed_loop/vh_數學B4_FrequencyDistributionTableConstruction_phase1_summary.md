# Gencode Phase1 Summary: vh_數學B4_FrequencyDistributionTableConstruction

## SOP Policy Reference

- **SOP Policy Version**: `v0.3`
- **Highest SOP**: `docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.3.md`
- **SOP Preflight Status**: `PASS`
- **SOP Gate Status**: `FAIL`
- **Report Contract Status**: `PASS_WITH_WARNINGS`
- **Report Contract Warnings**: ['candidate_problem_type_count_synchronized']
- **Report Contract Violations**: []

- spec_mode: `ai_first_induce_from_sources`

## Main skill anchor

- skill_ch_name: `統計資料的次數分配表編製步驟`
- expected_task_families: []
- expected_subskill_candidates: []
- skill_anchor_scope: `default`
- observed_source_family_distribution: {'generic_numeric_family': 4}
- observed_target_task_distribution: {'compute_numeric': 4}
- same_family_subskill_mismatch_examples: 0
- examples_outside_expected_subskills: []
- suggested_action: `Mixed groups were auto-split into distinct problem types.`

## Source alignment

- source_alignment_status: `warn`
- skill_problem_type_alignment_status: `warn`
- alignment_score: `0.8`
- alignment_blockers: []
- alignment_warnings: ['uniform_core_target_task_alignment_threshold_relaxed', 'disallowed_blocker_promoted_to_warning:mixed_source_families', 'disallowed_blocker_promoted_to_warning:requires_human_action']

| example_id | target_task | task_family | alignment_kind | subskill_match | included | exclude_reason | stem_preview |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3822 | compute_numeric | generic_numeric_family | unresolved_within_current_skill | False | True |  | 國貿科三年甲班40人英文模擬考成績資料如下：32、38、41、45、47、49、51、52、53、53、55、56、57 |
| 3823 | compute_numeric | generic_numeric_family | unresolved_within_current_skill | False | True |  | 會計科三年甲班45人數學模擬考成績資料如下（略），試將此班依分數分成5組，編製成次數分配表。（圖片待補） |
| 3824 | compute_numeric | generic_numeric_family | unresolved_within_current_skill | False | True |  | 有一組數值資料為60、64、66、68、73、75、76、85，試求這組數字的全距。 |
| 3825 | compute_numeric | generic_numeric_family | unresolved_within_current_skill | False | True |  | 某公司企劃部員工20人，年齡資料如下：25、26、27、28、28、30、31、31、32、35、36、36、37、37 |

## AI semantic classification

- ai_semantic_status: `ok`

| example_id | ai_task | ai_family | ai_conf | rule_task | rule_family | final_task | final_family | source | conflict | human |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3822 | compute_numeric | generic_numeric_family | 0.9 | compute_numeric | generic_numeric_family | compute_numeric | generic_numeric_family | ai_outsider_candidate |  | True |
| 3823 | compute_numeric | generic_numeric_family | 0.95 | compute_numeric | generic_numeric_family | compute_numeric | generic_numeric_family | ai |  | True |
| 3824 | compute_numeric | generic_numeric_family | 1.0 | compute_numeric | generic_numeric_family | compute_numeric | generic_numeric_family | ai |  | False |
| 3825 | compute_numeric | generic_numeric_family | 1.0 | compute_numeric | generic_numeric_family | compute_numeric | generic_numeric_family | ai |  | False |
## Classification diagnostics (per example)

| id | rule_task/family | AI task/family | conf | source | final task/family | align | excluded |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3822 | compute_numeric/generic_numeric_family | compute_numeric/generic_numeric_family | 0.9 | ai_outsider_candidate | compute_numeric/generic_numeric_family | unresolved_within_current_skill |  |
| 3823 | compute_numeric/generic_numeric_family | compute_numeric/generic_numeric_family | 0.95 | ai | compute_numeric/generic_numeric_family | unresolved_within_current_skill |  |
| 3824 | compute_numeric/generic_numeric_family | compute_numeric/generic_numeric_family | 1.0 | ai | compute_numeric/generic_numeric_family | unresolved_within_current_skill |  |
| 3825 | compute_numeric/generic_numeric_family | compute_numeric/generic_numeric_family | 1.0 | ai | compute_numeric/generic_numeric_family | unresolved_within_current_skill |  |


## Example / practice links

[{'practice_label': '隨堂練習1', 'linked_example': '例題1', 'example_id': 3823}]

## Same-section family distribution

{'generic_numeric_family': 4}

## Example features

| example_id | answer_type | target_task | has_choices | stem_embeds_choices | math_objects |
| --- | --- | --- | --- | --- | --- |
| 3822 | integer | compute_numeric | False | False |  |
| 3823 | integer | compute_numeric | False | False |  |
| 3824 | integer | compute_numeric | False | False |  |
| 3825 | integer | compute_numeric | False | False |  |

## Induction clusters

### Cluster 1
- answer_type: `numeric`
- source_example_ids: [3822, 3823, 3824, 3825]
- grouping_reason: single_signature_group
- feature_signature: `['numeric', 'compute_numeric', 'short_answer', ('numeric_computation',), (), 'default']`


## Candidate problem types

| problem_type_id | display_name | answer_type | source_examples | grouping_reason |
| --- | --- | --- | --- | --- |
| integer_compute_numeric | integer / compute_numeric | text_short | [3822, 3823, 3824] | single_signature_group |
| integer_compute_numeric | integer / compute_numeric | text_short | [3825] | single_signature_group |

## phase1
```json
{
  "ok": true,
  "phase": "phase1",
  "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
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
  "sop_gate_status": "FAIL",
  "sop_gate_violation": true,
  "invalid_skill_level_blockers": [
    "mixed_source_families",
    "requires_human_action"
  ],
  "main_skill_anchor": {
    "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
    "skill_ch_name": "統計資料的次數分配表編製步驟",
    "skill_en_name": "FrequencyDistributionTableConstruction",
    "chapter": "3 統計",
    "section": "3-2 統計資料整理",
    "normalized_skill_terms": [
      "2 統計資料整理",
      "3 統計",
      "construction",
      "distribution",
      "frequency",
      "frequencydi",
      "frequencydistributiontableconstruction",
      "table",
      "tributiontablecon",
      "truction",
      "vh",
      "vocational",
      "數學b",
      "數學b4",
      "統計",
      "統計資料整理",
      "統計資料的次數分配表編製步驟"
    ],
    "expected_task_families": [],
    "expected_math_objects": [],
    "expected_subskill_candidates": [],
    "skill_anchor_scope": "default",
    "fallback_subskill": {
      "subskill_id": "same_as_main_skill",
      "subskill_name": "統計資料的次數分配表編製步驟",
      "subskill_scope": "fallback",
      "display_note": "此子技能為 fallback，用於收納未細分或綜合題"
    },
    "source_belongs_to_current_skill_by_default": true,
    "source_skill_scope_locked": true,
    "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
    "classification_scope": "within_current_skill",
    "skill_mapping_authority": "textbook_examples.skill_id",
    "anchor_authority": "skill_id_derived_no_cross_family_pollution",
    "classification_mandate": "【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\n【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\nTrusted skill anchor (do not override):\n- skill_id: vh_數學B4_FrequencyDistributionTableConstruction\n- skill_ch_name: 統計資料的次數分配表編製步驟\n- skill_en_name: FrequencyDistributionTableConstruction\n- expected_task_families: []\n- expected_subskill_candidates: []\n- skill_anchor_scope: default\n- source_skill_scope_locked: True\n"
  },
  "source_example_count": 4,
  "source_alignment_status": "warn",
  "skill_problem_type_alignment_status": "warn",
  "alignment_score": 0.8,
  "alignment_warnings": [
    "uniform_core_target_task_alignment_threshold_relaxed",
    "disallowed_blocker_promoted_to_warning:mixed_source_families",
    "disallowed_blocker_promoted_to_warning:requires_human_action"
  ],
  "alignment_blockers": [],
  "semantic_alignment": {
    "main_skill_anchor": {
      "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
      "skill_ch_name": "統計資料的次數分配表編製步驟",
      "skill_en_name": "FrequencyDistributionTableConstruction",
      "chapter": "3 統計",
      "section": "3-2 統計資料整理",
      "normalized_skill_terms": [
        "2 統計資料整理",
        "3 統計",
        "construction",
        "distribution",
        "frequency",
        "frequencydi",
        "frequencydistributiontableconstruction",
        "table",
        "tributiontablecon",
        "truction",
        "vh",
        "vocational",
        "數學b",
        "數學b4",
        "統計",
        "統計資料整理",
        "統計資料的次數分配表編製步驟"
      ],
      "expected_task_families": [],
      "expected_math_objects": [],
      "expected_subskill_candidates": [],
      "skill_anchor_scope": "default",
      "fallback_subskill": {
        "subskill_id": "same_as_main_skill",
        "subskill_name": "統計資料的次數分配表編製步驟",
        "subskill_scope": "fallback",
        "display_note": "此子技能為 fallback，用於收納未細分或綜合題"
      },
      "source_belongs_to_current_skill_by_default": true,
      "source_skill_scope_locked": true,
      "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
      "classification_scope": "within_current_skill",
      "skill_mapping_authority": "textbook_examples.skill_id",
      "anchor_authority": "skill_id_derived_no_cross_family_pollution",
      "classification_mandate": "【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\n【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\nTrusted skill anchor (do not override):\n- skill_id: vh_數學B4_FrequencyDistributionTableConstruction\n- skill_ch_name: 統計資料的次數分配表編製步驟\n- skill_en_name: FrequencyDistributionTableConstruction\n- expected_task_families: []\n- expected_subskill_candidates: []\n- skill_anchor_scope: default\n- source_skill_scope_locked: True\n"
    },
    "ai_semantic_status": "ok",
    "skill_terms": [
      "2 統計資料整理",
      "3 統計",
      "construction",
      "distribution",
      "frequency",
      "frequencydi",
      "frequencydistributiontableconstruction",
      "table",
      "tributiontablecon",
      "truction",
      "vh",
      "vocational",
      "數學b",
      "數學b4",
      "統計",
      "統計資料整理",
      "統計資料的次數分配表編製步驟"
    ],
    "source_terms": [
      "25",
      "26",
      "27",
      "28",
      "30",
      "31",
      "32",
      "35",
      "36",
      "37",
      "38",
      "39",
      "40",
      "41",
      "42",
      "44",
      "45",
      "47",
      "49",
      "51",
      "52",
      "53",
      "55",
      "56",
      "57",
      "58",
      "61",
      "62",
      "63",
      "64",
      "65",
      "66",
      "67",
      "68",
      "69",
      "70",
      "71",
      "73",
      "75",
      "76",
      "77",
      "78",
      "79",
      "80",
      "85",
      "87",
      "89",
      "92",
      "96",
      "compute_numeric",
      "numeric",
      "依年齡分成4組",
      "國貿科三年甲班40人英文模擬考成績資料如下",
      "圖片待補",
      "定組距為5",
      "年齡資料如下",
      "最小一組為25",
      "會計科三年甲班45人數學模擬考成績資料如下",
      "有一組數值資料為60",
      "某公司企劃部員工20人",
      "編製成次數分配表",
      "試將此班依分數分成5組",
      "試將此班依分數分成7組",
      "試將此組資料分組",
      "試求這組數字的全距"
    ],
    "expected_subskill_candidates": [],
    "observed_target_task_distribution": {
      "compute_numeric": 4
    },
    "same_family_subskill_mismatch_examples": [],
    "examples_outside_expected_subskills": [],
    "suggested_action": "",
    "examples_outside_expected_family": [
      3822
    ],
    "problem_type_terms": [
      "an",
      "answer",
      "compute",
      "compute_numeric",
      "hort",
      "numeric",
      "numeric / compute_numeric",
      "numeric_computation",
      "point_quadrant",
      "short",
      "text_short",
      "wer"
    ],
    "expected_task_candidates": [],
    "expected_skill_families": [],
    "observed_source_family_distribution": {
      "generic_numeric_family": 4
    },
    "source_family_distribution": {
      "generic_numeric_family": 4
    },
    "candidate_problem_type_families": [
      "generic_numeric_family"
    ],
    "dominant_source_task": "compute_numeric",
    "dominant_source_task_ratio": 1.0,
    "uniform_core_target_task": "compute_numeric",
    "uniform_core_target_task_ratio": 1.0,
    "uniform_core_target_task_count": 4,
    "uniform_core_threshold_relaxed": true,
    "dominant_source_family": [
      "generic_numeric_family"
    ],
    "dominant_source_family_ratio": 1.0,
    "skill_source_score": 0.8,
    "skill_problem_type_score": 0.8,
    "source_problem_type_score": 0.8,
    "per_problem_type_scores": [
      {
        "problem_type_id": "numeric_compute_numeric_short_answer",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "inferred_tasks": [
          "compute_numeric"
        ],
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0267,
        "task_consistent_with_skill": true,
        "family_consistent_with_skill": true,
        "answer_contract_supported": true
      }
    ],
    "decision": "warn",
    "blockers": [],
    "warnings": [
      "uniform_core_target_task_alignment_threshold_relaxed"
    ],
    "induction_core_example_count": 4,
    "induction_enrichment_example_count": 0,
    "source_skill_scope_locked": true,
    "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
    "classification_scope": "within_current_skill",
    "skill_mapping_authority": "textbook_examples.skill_id",
    "core_skill_concept": "frequencydistributiontableconstruction",
    "supporting_math_objects": [],
    "source_quality_reject_examples": []
  },
  "source_family_distribution": {
    "generic_numeric_family": 4
  },
  "candidate_problem_type_families": [
    "generic_numeric_family"
  ],
  "expected_skill_families": [],
  "expected_subskill_candidates": [],
  "observed_target_task_distribution": {
    "compute_numeric": 4
  },
  "same_family_subskill_mismatch_examples": [],
  "examples_outside_expected_subskills": [],
  "suggested_action": "Mixed groups were auto-split into distinct problem types.",
  "requires_human_action": true,
  "semantic_classifications": [
    {
      "example_id": 3822,
      "ai_target_task": "compute_numeric",
      "ai_task_family": "generic_numeric_family",
      "ai_confidence": 0.9,
      "ai_best_candidate_id": "C1",
      "ai_evidence": [
        "題目要求將40人的英文模擬考成績分成7組並編製成次數分配表",
        "根據強制合約，此題目與技能 vh_數學B4_FrequencyDistributionTableConstruction 100% 對齊",
        "在候選清單中，除了 needs_review 之外，僅有 C1 (compute_numeric) 可供選擇",
        "依據規則，禁止選擇 needs_review，因此選擇 C1"
      ],
      "ai_rejected_candidates": {
        "needs_review": "題目清晰可讀，且規則禁止在非無法閱讀的情況下選擇 needs_review"
      },
      "ai_available": true,
      "ai_error": "",
      "ai_unavailable_reason": "",
      "ai_semantic_status": "ok",
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
      "classifier_source": "ai_outsider_candidate",
      "classification_decision": "",
      "conflict_reason": "",
      "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
      "requires_human_action": true,
      "ai_notes": "此題目為編製次數分配表的標準題型，因候選清單中無更具體的子技能，且禁止選擇 needs_review，故選擇 C1。",
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
      "candidate_source": "outsider",
      "selected_generator_contract": {
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
      },
      "variable_randomization_notes": [],
      "checker_key": "numeric_checker",
      "equivalence_type": "numeric_equivalence",
      "skill_scope_trusted": true,
      "target_task": "compute_numeric",
      "task_family": "generic_numeric_family",
      "math_objects": [],
      "answer_type": "numeric",
      "answer_shape": "numeric",
      "source_type": "worked_example",
      "example_label": "例題1",
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
      "example_id": 3823,
      "ai_target_task": "compute_numeric",
      "ai_task_family": "generic_numeric_family",
      "ai_confidence": 0.95,
      "ai_best_candidate_id": "C1",
      "ai_evidence": [
        "題目明確要求將45人的成績依分數分成5組，並編製成次數分配表",
        "此題型完全符合統計資料的次數分配表編製步驟之技能範疇"
      ],
      "ai_rejected_candidates": {
        "needs_review": "雖然題目中含有「資料如下（略）」與「圖片待補」，但其數學任務與題意極為清晰，並非無法辨識之文本，因此不選擇 needs_review"
      },
      "ai_available": true,
      "ai_error": "",
      "ai_unavailable_reason": "",
      "ai_semantic_status": "ok",
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
      "classifier_source": "ai",
      "classification_decision": "",
      "conflict_reason": "",
      "source_mapping_warning": "",
      "requires_human_action": true,
      "ai_notes": "本題題目文字清晰且題型明確，但因含有「圖片待補」與「資料如下（略）」，後續需要人工補齊具體的成績數據或圖表以供學生作答。",
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
      "candidate_source": "structure",
      "selected_generator_contract": {
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
      },
      "variable_randomization_notes": [],
      "checker_key": "numeric_checker",
      "equivalence_type": "numeric_equivalence",
      "skill_scope_trusted": true,
      "target_task": "compute_numeric",
      "task_family": "generic_numeric_family",
      "math_objects": [],
      "answer_type": "numeric",
      "answer_shape": "numeric",
      "source_type": "in_class_practice",
      "example_label": "",
      "practice_label": "隨堂練習1",
      "linked_example": "例題1",
      "linked_example_id": 3822,
      "linked_example_task_family": "generic_numeric_family",
      "structure_consistency": "consistent",
      "sequence_context_used": true,
      "structure_context_used": true,
      "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
      "possible_structure_mismatch": false,
      "possible_mixed_source_context": false
    },
    {
      "example_id": 3824,
      "ai_target_task": "compute_numeric",
      "ai_task_family": "generic_numeric_family",
      "ai_confidence": 1.0,
      "ai_best_candidate_id": "C1",
      "ai_evidence": [
        "The problem asks for the range of a given set of numbers, which is 85 minus 60 equals 25.",
        "Calculating the range is the initial step in constructing a frequency distribution table to determine class intervals.",
        "Since needs_review is forbidden for readable stems, C1 is the correct choice."
      ],
      "ai_rejected_candidates": {
        "needs_review": "The question is clear and directly related to the steps of constructing a frequency distribution table."
      },
      "ai_available": true,
      "ai_error": "",
      "ai_unavailable_reason": "",
      "ai_semantic_status": "ok",
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
      "classifier_source": "ai",
      "classification_decision": "",
      "conflict_reason": "",
      "source_mapping_warning": "",
      "requires_human_action": false,
      "ai_notes": "The calculation of the range (全距) is a standard numeric computation step within the frequency distribution table construction process.",
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
      "candidate_source": "structure",
      "selected_generator_contract": {
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
      },
      "variable_randomization_notes": [],
      "checker_key": "numeric_checker",
      "equivalence_type": "numeric_equivalence",
      "skill_scope_trusted": true,
      "target_task": "compute_numeric",
      "task_family": "generic_numeric_family",
      "math_objects": [],
      "answer_type": "numeric",
      "answer_shape": "numeric",
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
      "example_id": 3825,
      "ai_target_task": "compute_numeric",
      "ai_task_family": "generic_numeric_family",
      "ai_confidence": 1.0,
      "ai_best_candidate_id": "C1",
      "ai_evidence": [
        "題目要求將20位員工的年齡資料，以組距為5、最小一組為25至30歲，編製成次數分配表。",
        "此題完全符合當前技能「統計資料的次數分配表編製步驟」的定義。",
        "依據強制合約，在題目清晰可讀的情況下，禁止選擇 needs_review，因此選擇唯一的候選者 C1。"
      ],
      "ai_rejected_candidates": {
        "needs_review": "題目語意完整且清晰，無須進行人工審查。"
      },
      "ai_available": true,
      "ai_error": "",
      "ai_unavailable_reason": "",
      "ai_semantic_status": "ok",
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
      "classifier_source": "ai",
      "classification_decision": "",
      "conflict_reason": "",
      "source_mapping_warning": "",
      "requires_human_action": false,
      "ai_notes": "本題為標準的次數分配表編製題目，對應到 C1 (compute_numeric) 進行次數的計算與歸類。",
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
      "candidate_source": "structure",
      "selected_generator_contract": {
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
      },
      "variable_randomization_notes": [],
      "checker_key": "numeric_checker",
      "equivalence_type": "numeric_equivalence",
      "skill_scope_trusted": true,
      "target_task": "compute_numeric",
      "task_family": "generic_numeric_family",
      "math_objects": [],
      "answer_type": "numeric",
      "answer_shape": "numeric",
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
    }
  ],
  "ai_semantic_status": "ok",
  "source_type_distribution": {
    "worked_example": 1,
    "in_class_practice": 1,
    "basic_exercise": 2
  },
  "example_practice_link_map": [
    {
      "practice_label": "隨堂練習1",
      "linked_example": "例題1",
      "example_id": 3823
    }
  ],
  "structure_mismatch_examples": [],
  "same_section_family_distribution": {
    "generic_numeric_family": 4
  },
  "source_structure_report": {
    "source_type_distribution": {
      "worked_example": 1,
      "in_class_practice": 1,
      "basic_exercise": 2
    },
    "example_practice_link_map": [
      {
        "practice_label": "隨堂練習1",
        "linked_example": "例題1",
        "example_id": 3823
      }
    ],
    "structure_mismatch_examples": [],
    "same_section_family_distribution": {
      "generic_numeric_family": 4
    }
  },
  "classification_diagnostics": [
    {
      "example_id": 3822,
      "rule_target_task": "compute_numeric",
      "rule_task_family": "generic_numeric_family",
      "rule_confidence": 0.2,
      "ai_target_task": "compute_numeric",
      "ai_task_family": "generic_numeric_family",
      "ai_confidence": 0.9,
      "ai_semantic_status": "ok",
      "ai_available": true,
      "ai_error": "",
      "ai_unavailable_reason": "",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "classifier_source": "ai_outsider_candidate",
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
      "conflict_reason": "",
      "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
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
      "ai_best_candidate_id": "C1",
      "selected_subskill": "compute_numeric",
      "selected_problem_type": "compute_numeric",
      "candidate_source": "outsider",
      "outsider_candidates": [
        "C1"
      ],
      "selected_generator_contract": {
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
      },
      "variable_randomization_notes": []
    },
    {
      "example_id": 3823,
      "rule_target_task": "compute_numeric",
      "rule_task_family": "generic_numeric_family",
      "rule_confidence": 0.2,
      "ai_target_task": "compute_numeric",
      "ai_task_family": "generic_numeric_family",
      "ai_confidence": 0.95,
      "ai_semantic_status": "ok",
      "ai_available": true,
      "ai_error": "",
      "ai_unavailable_reason": "",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "classifier_source": "ai",
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
      "conflict_reason": "",
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
      "ai_best_candidate_id": "C1",
      "selected_subskill": "compute_numeric",
      "selected_problem_type": "compute_numeric",
      "candidate_source": "structure",
      "outsider_candidates": [],
      "selected_generator_contract": {
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
      },
      "variable_randomization_notes": []
    },
    {
      "example_id": 3824,
      "rule_target_task": "compute_numeric",
      "rule_task_family": "generic_numeric_family",
      "rule_confidence": 0.2,
      "ai_target_task": "compute_numeric",
      "ai_task_family": "generic_numeric_family",
      "ai_confidence": 1.0,
      "ai_semantic_status": "ok",
      "ai_available": true,
      "ai_error": "",
      "ai_unavailable_reason": "",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "classifier_source": "ai",
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
      "conflict_reason": "",
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
      "ai_best_candidate_id": "C1",
      "selected_subskill": "compute_numeric",
      "selected_problem_type": "compute_numeric",
      "candidate_source": "structure",
      "outsider_candidates": [],
      "selected_generator_contract": {
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
      },
      "variable_randomization_notes": []
    },
    {
      "example_id": 3825,
      "rule_target_task": "compute_numeric",
      "rule_task_family": "generic_numeric_family",
      "rule_confidence": 0.2,
      "ai_target_task": "compute_numeric",
      "ai_task_family": "generic_numeric_family",
      "ai_confidence": 1.0,
      "ai_semantic_status": "ok",
      "ai_available": true,
      "ai_error": "",
      "ai_unavailable_reason": "",
      "ai_invalid_response_reason": "",
      "parser_error": "",
      "raw_response_preview": "",
      "sanitized_response_preview": "",
      "failed_stage": "",
      "classifier_source": "ai",
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
      "conflict_reason": "",
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
      "ai_best_candidate_id": "C1",
      "selected_subskill": "compute_numeric",
      "selected_problem_type": "compute_numeric",
      "candidate_source": "structure",
      "outsider_candidates": [],
      "selected_generator_contract": {
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
      },
      "variable_randomization_notes": []
    }
  ],
  "ai_semantic_unavailable_reason": "",
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
  "suspected_wrong_skill_examples": [
    3822
  ],
  "same_family_extension_examples": [],
  "section_scope_subskill_extension_examples": [],
  "same_as_main_skill_examples": [],
  "inherited_from_previous_context_examples": [],
  "low_source_examples": [],
  "candidate_only_problem_types": [
    {
      "example_id": 3822,
      "problem_type_id": "numeric_compute_numeric_short_answer",
      "reason": "runtime_not_supported"
    },
    {
      "example_id": 3823,
      "problem_type_id": "numeric_compute_numeric_short_answer",
      "reason": "runtime_not_supported"
    },
    {
      "example_id": 3824,
      "problem_type_id": "numeric_compute_numeric_short_answer",
      "reason": "runtime_not_supported"
    },
    {
      "example_id": 3825,
      "problem_type_id": "numeric_compute_numeric_short_answer",
      "reason": "runtime_not_supported"
    }
  ],
  "candidate_only_count": 4,
  "same_as_main_skill_count": 0,
  "rule_only_classification_count": 0,
  "hybrid_resolved_count": 0,
  "subskills": [
    "compute_numeric",
    "same_as_main_skill"
  ],
  "fallback_subskill_used": true,
  "source_belongs_to_current_skill_by_default_count": 4,
  "source_example_alignment": [
    {
      "example_id": 3822,
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
      "pass_with_warning": true,
      "requires_human_action": true,
      "induction_tier": "core",
      "included_in_core_induction": true,
      "enrichment_reasons": [],
      "source_quality_issues": [],
      "source_quality_reject": false,
      "candidate_only": false,
      "classification_source": "ai_outsider_candidate",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "induction_eligibility": "eligible",
      "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
      "title_stem_preview": "國貿科三年甲班40人英文模擬考成績資料如下：32、38、41、45、47、49、51、52、53、53、55、56、57、58、61、61、62、63、64、6"
    },
    {
      "example_id": 3823,
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
      "classification_source": "ai",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "induction_eligibility": "eligible",
      "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
      "title_stem_preview": "會計科三年甲班45人數學模擬考成績資料如下（略），試將此班依分數分成5組，編製成次數分配表。（圖片待補）"
    },
    {
      "example_id": 3824,
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
      "classification_source": "ai",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "induction_eligibility": "eligible",
      "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
      "title_stem_preview": "有一組數值資料為60、64、66、68、73、75、76、85，試求這組數字的全距。"
    },
    {
      "example_id": 3825,
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
      "classification_source": "ai",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "induction_eligibility": "eligible",
      "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
      "title_stem_preview": "某公司企劃部員工20人，年齡資料如下：25、26、27、28、28、30、31、31、32、35、36、36、37、37、38、39、39、40、42、44。試"
    }
  ],
  "candidate_problem_types": [
    {
      "problem_type_id": "integer_compute_numeric",
      "proposed_problem_type_id": "integer_compute_numeric",
      "display_name": "integer / compute_numeric",
      "matched_example_ids": [
        3822,
        3823,
        3824
      ],
      "matched_example_count": 3,
      "unmatched_example_ids": [],
      "representative_example_id": 3822,
      "structural_features": [
        "text_short"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "integer",
        "answer_shape": "text_short",
        "answer_equivalence": "numeric_exact",
        "checker": "integer_checker",
        "accepted_formats": [
          "5",
          "5.0",
          "-3"
        ],
        "source_has_choices": false,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "presentation_mode": "",
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "text_short"
      },
      "checker_key_proposal": "integer_checker",
      "equivalence_type_proposal": "numeric_exact",
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
        "generic_fallback_blocked_by_source_skill_binding",
        "uniform_core_target_task_alignment_threshold_relaxed"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "numeric",
        "compute_numeric",
        "short_answer",
        [
          "numeric_computation"
        ],
        [],
        "default"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "text_short_compute_text_short_expression",
        "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "display_name": "numeric / compute_numeric",
        "answer_format_hint": "text_short",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          3822,
          3823,
          3824,
          3825
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
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "numeric_compute_numeric_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ],
          "template_slots": {
            "stem": "point_quadrant"
          }
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
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "numeric",
          "compute_numeric",
          "short_answer",
          [
            "numeric_computation"
          ],
          [],
          "default"
        ],
        "canonical_base_problem_type_id": "compute_numeric_short_answer",
        "value_type_prefix": "numeric",
        "_resolved_template_slot": "point_quadrant",
        "naming_warning": "naming_warning:numeric_prefix_but_hint_is_text_short"
      },
      "generator_readiness": "pending_problem_type_induction",
      "usable_for_phase3": false,
      "template_slot": "point_quadrant",
      "canonical_base_problem_type_id": "compute_numeric_short_answer",
      "value_type_prefix": "numeric",
      "subskill_id": "compute_numeric",
      "requires_human_action": true,
      "requires_human_rule_pack": true,
      "pending_problem_type_induction": true,
      "answer_type": "text_short",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0267,
        "task_consistent_with_skill": true
      }
    },
    {
      "problem_type_id": "integer_compute_numeric",
      "proposed_problem_type_id": "integer_compute_numeric",
      "display_name": "integer / compute_numeric",
      "matched_example_ids": [
        3825
      ],
      "matched_example_count": 1,
      "unmatched_example_ids": [],
      "representative_example_id": 3825,
      "structural_features": [
        "text_short"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "integer",
        "answer_shape": "text_short",
        "answer_equivalence": "unordered_solution_set",
        "checker": "integer_checker",
        "accepted_formats": [
          "5",
          "5.0",
          "-3"
        ],
        "source_has_choices": false,
        "equivalence_type": "unordered_solution_set",
        "checker_key": "integer_checker",
        "presentation_mode": "",
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "text_short"
      },
      "checker_key_proposal": "integer_checker",
      "equivalence_type_proposal": "unordered_solution_set",
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
        "generic_fallback_blocked_by_source_skill_binding",
        "uniform_core_target_task_alignment_threshold_relaxed"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "numeric",
        "compute_numeric",
        "short_answer",
        [
          "numeric_computation"
        ],
        [],
        "default"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "text_short_compute_text_short_expression",
        "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "display_name": "numeric / compute_numeric",
        "answer_format_hint": "text_short",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          3822,
          3823,
          3824,
          3825
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
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "numeric_compute_numeric_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ],
          "template_slots": {
            "stem": "point_quadrant"
          }
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
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "numeric",
          "compute_numeric",
          "short_answer",
          [
            "numeric_computation"
          ],
          [],
          "default"
        ],
        "canonical_base_problem_type_id": "compute_numeric_short_answer",
        "value_type_prefix": "numeric",
        "_resolved_template_slot": "point_quadrant",
        "naming_warning": "naming_warning:numeric_prefix_but_hint_is_text_short"
      },
      "generator_readiness": "pending_problem_type_induction",
      "usable_for_phase3": false,
      "template_slot": "point_quadrant",
      "canonical_base_problem_type_id": "compute_numeric_short_answer",
      "value_type_prefix": "numeric",
      "subskill_id": "compute_numeric",
      "requires_human_action": true,
      "requires_human_rule_pack": true,
      "pending_problem_type_induction": true,
      "answer_type": "text_short",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0267,
        "task_consistent_with_skill": true
      }
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
      "numeric_compute_numeric_short_answer": {
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "text_short"
      }
    },
    "missing_answer_contract_problem_types": [],
    "missing_checker_key_problem_types": [],
    "equivalence_test_required_problem_types": [],
    "convertible_to_choice_problem_types": [],
    "manual_review_or_ai_judged_problem_types": []
  },
  "invalid_equivalence_type_problem_types": [],
  "phase1_answer_contract_gate_status": "PASS",
  "per_example_classification": [
    {
      "example_id": 3822,
      "detected_problem_type_id": "numeric_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3822,
        "question_text": "國貿科三年甲班40人英文模擬考成績資料如下：32、38、41、45、47、49、51、52、53、53、55、56、57、58、61、61、62、63、64、64、65、65、65、66、67、69、70、70、71、75、77、77、78、79、80、85、87、89、92、96。試將此班依分數分成7組，編製成次數分配表。（圖片待補）",
        "answer": "次數分配表（組距10，從30開始）",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
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
        "classifier_source": "ai_outsider_candidate",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 0.9,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目要求將40人的英文模擬考成績分成7組並編製成次數分配表",
            "根據強制合約，此題目與技能 vh_數學B4_FrequencyDistributionTableConstruction 100% 對齊",
            "在候選清單中，除了 needs_review 之外，僅有 C1 (compute_numeric) 可供選擇",
            "依據規則，禁止選擇 needs_review，因此選擇 C1"
          ],
          "ai_rejected_candidates": {
            "needs_review": "題目清晰可讀，且規則禁止在非無法閱讀的情況下選擇 needs_review"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai_outsider_candidate",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
          "requires_human_action": true,
          "ai_notes": "此題目為編製次數分配表的標準題型，因候選清單中無更具體的子技能，且禁止選擇 needs_review，故選擇 C1。",
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
          "candidate_source": "outsider",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "worked_example",
          "example_label": "例題1",
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
          "example_label": "例題1",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": 1,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            }
          ],
          "same_section_sequence": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            },
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            },
            {
              "example_id": 3824,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題1"
            },
            {
              "example_id": 3825,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題2"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": true,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai_outsider_candidate",
      "risk_flags": [
        "outsider_candidate_within_confirmed_skill",
        "requires_human_action",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 0.9,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目要求將40人的英文模擬考成績分成7組並編製成次數分配表",
          "根據強制合約，此題目與技能 vh_數學B4_FrequencyDistributionTableConstruction 100% 對齊",
          "在候選清單中，除了 needs_review 之外，僅有 C1 (compute_numeric) 可供選擇",
          "依據規則，禁止選擇 needs_review，因此選擇 C1"
        ],
        "ai_rejected_candidates": {
          "needs_review": "題目清晰可讀，且規則禁止在非無法閱讀的情況下選擇 needs_review"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
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
        "classifier_source": "ai_outsider_candidate",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
        "requires_human_action": true,
        "ai_notes": "此題目為編製次數分配表的標準題型，因候選清單中無更具體的子技能，且禁止選擇 needs_review，故選擇 C1。",
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
        "candidate_source": "outsider",
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "worked_example",
        "example_label": "例題1",
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
      "classification_source": "ai_outsider_candidate",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 3823,
      "detected_problem_type_id": "numeric_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3823,
        "question_text": "會計科三年甲班45人數學模擬考成績資料如下（略），試將此班依分數分成5組，編製成次數分配表。（圖片待補）",
        "answer": "略",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
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
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 0.95,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目明確要求將45人的成績依分數分成5組，並編製成次數分配表",
            "此題型完全符合統計資料的次數分配表編製步驟之技能範疇"
          ],
          "ai_rejected_candidates": {
            "needs_review": "雖然題目中含有「資料如下（略）」與「圖片待補」，但其數學任務與題意極為清晰，並非無法辨識之文本，因此不選擇 needs_review"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "本題題目文字清晰且題型明確，但因含有「圖片待補」與「資料如下（略）」，後續需要人工補齊具體的成績數據或圖表以供學生作答。",
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
          "candidate_source": "structure",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習1",
          "linked_example": "例題1",
          "linked_example_id": 3822,
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
          "practice_label": "隨堂練習1",
          "linked_example": "例題1",
          "section_order": 0,
          "example_number": null,
          "practice_number": 1,
          "nearby_worked_examples": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            }
          ],
          "linked_worked_example": {
            "example_id": 3822,
            "source_type": "worked_example",
            "example_label": "例題1",
            "practice_label": "",
            "section_order": 0,
            "title_head": "例題 1"
          },
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            },
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            },
            {
              "example_id": 3824,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題1"
            },
            {
              "example_id": 3825,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題2"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": true,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "requires_human_action",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 0.95,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目明確要求將45人的成績依分數分成5組，並編製成次數分配表",
          "此題型完全符合統計資料的次數分配表編製步驟之技能範疇"
        ],
        "ai_rejected_candidates": {
          "needs_review": "雖然題目中含有「資料如下（略）」與「圖片待補」，但其數學任務與題意極為清晰，並非無法辨識之文本，因此不選擇 needs_review"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
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
        "classifier_source": "ai",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "本題題目文字清晰且題型明確，但因含有「圖片待補」與「資料如下（略）」，後續需要人工補齊具體的成績數據或圖表以供學生作答。",
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
        "candidate_source": "structure",
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "in_class_practice",
        "example_label": "",
        "practice_label": "隨堂練習1",
        "linked_example": "例題1",
        "linked_example_id": 3822,
        "linked_example_task_family": "generic_numeric_family",
        "structure_consistency": "consistent",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "compute_numeric",
      "classification_source": "ai",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 3824,
      "detected_problem_type_id": "numeric_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3824,
        "question_text": "有一組數值資料為60、64、66、68、73、75、76、85，試求這組數字的全距。",
        "answer": "25",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
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
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "The problem asks for the range of a given set of numbers, which is 85 minus 60 equals 25.",
            "Calculating the range is the initial step in constructing a frequency distribution table to determine class intervals.",
            "Since needs_review is forbidden for readable stems, C1 is the correct choice."
          ],
          "ai_rejected_candidates": {
            "needs_review": "The question is clear and directly related to the steps of constructing a frequency distribution table."
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "The calculation of the range (全距) is a standard numeric computation step within the frequency distribution table construction process.",
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
          "candidate_source": "structure",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
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
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            },
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            },
            {
              "example_id": 3824,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題1"
            },
            {
              "example_id": 3825,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題2"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": true,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "The problem asks for the range of a given set of numbers, which is 85 minus 60 equals 25.",
          "Calculating the range is the initial step in constructing a frequency distribution table to determine class intervals.",
          "Since needs_review is forbidden for readable stems, C1 is the correct choice."
        ],
        "ai_rejected_candidates": {
          "needs_review": "The question is clear and directly related to the steps of constructing a frequency distribution table."
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
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
        "classifier_source": "ai",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "The calculation of the range (全距) is a standard numeric computation step within the frequency distribution table construction process.",
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
        "candidate_source": "structure",
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "numeric",
        "answer_shape": "numeric",
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
      "classification_source": "ai",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 3825,
      "detected_problem_type_id": "numeric_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3825,
        "question_text": "某公司企劃部員工20人，年齡資料如下：25、26、27、28、28、30、31、31、32、35、36、36、37、37、38、39、39、40、42、44。試將此組資料分組，定組距為5，依年齡分成4組，最小一組為25～30，編製成次數分配表。（圖片待補）",
        "answer": "次數：25~30(5人), 30~35(4人), 35~40(8人), 40~45(3人)",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "unordered_solution_set",
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
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目要求將20位員工的年齡資料，以組距為5、最小一組為25至30歲，編製成次數分配表。",
            "此題完全符合當前技能「統計資料的次數分配表編製步驟」的定義。",
            "依據強制合約，在題目清晰可讀的情況下，禁止選擇 needs_review，因此選擇唯一的候選者 C1。"
          ],
          "ai_rejected_candidates": {
            "needs_review": "題目語意完整且清晰，無須進行人工審查。"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "本題為標準的次數分配表編製題目，對應到 C1 (compute_numeric) 進行次數的計算與歸類。",
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
          "candidate_source": "structure",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
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
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            },
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            },
            {
              "example_id": 3824,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題1"
            },
            {
              "example_id": 3825,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題2"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": true,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "unordered_solution_set",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目要求將20位員工的年齡資料，以組距為5、最小一組為25至30歲，編製成次數分配表。",
          "此題完全符合當前技能「統計資料的次數分配表編製步驟」的定義。",
          "依據強制合約，在題目清晰可讀的情況下，禁止選擇 needs_review，因此選擇唯一的候選者 C1。"
        ],
        "ai_rejected_candidates": {
          "needs_review": "題目語意完整且清晰，無須進行人工審查。"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
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
        "classifier_source": "ai",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "本題為標準的次數分配表編製題目，對應到 C1 (compute_numeric) 進行次數的計算與歸類。",
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
        "candidate_source": "structure",
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "numeric",
        "answer_shape": "numeric",
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
      "classification_source": "ai",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "unordered_solution_set",
      "checker_key": "integer_checker"
    }
  ],
  "source_classifications": [
    {
      "example_id": 3822,
      "detected_problem_type_id": "numeric_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3822,
        "question_text": "國貿科三年甲班40人英文模擬考成績資料如下：32、38、41、45、47、49、51、52、53、53、55、56、57、58、61、61、62、63、64、64、65、65、65、66、67、69、70、70、71、75、77、77、78、79、80、85、87、89、92、96。試將此班依分數分成7組，編製成次數分配表。（圖片待補）",
        "answer": "次數分配表（組距10，從30開始）",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
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
        "classifier_source": "ai_outsider_candidate",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 0.9,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目要求將40人的英文模擬考成績分成7組並編製成次數分配表",
            "根據強制合約，此題目與技能 vh_數學B4_FrequencyDistributionTableConstruction 100% 對齊",
            "在候選清單中，除了 needs_review 之外，僅有 C1 (compute_numeric) 可供選擇",
            "依據規則，禁止選擇 needs_review，因此選擇 C1"
          ],
          "ai_rejected_candidates": {
            "needs_review": "題目清晰可讀，且規則禁止在非無法閱讀的情況下選擇 needs_review"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai_outsider_candidate",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
          "requires_human_action": true,
          "ai_notes": "此題目為編製次數分配表的標準題型，因候選清單中無更具體的子技能，且禁止選擇 needs_review，故選擇 C1。",
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
          "candidate_source": "outsider",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "worked_example",
          "example_label": "例題1",
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
          "example_label": "例題1",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": 1,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            }
          ],
          "same_section_sequence": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            },
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            },
            {
              "example_id": 3824,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題1"
            },
            {
              "example_id": 3825,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題2"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": true,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai_outsider_candidate",
      "risk_flags": [
        "outsider_candidate_within_confirmed_skill",
        "requires_human_action",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 0.9,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目要求將40人的英文模擬考成績分成7組並編製成次數分配表",
          "根據強制合約，此題目與技能 vh_數學B4_FrequencyDistributionTableConstruction 100% 對齊",
          "在候選清單中，除了 needs_review 之外，僅有 C1 (compute_numeric) 可供選擇",
          "依據規則，禁止選擇 needs_review，因此選擇 C1"
        ],
        "ai_rejected_candidates": {
          "needs_review": "題目清晰可讀，且規則禁止在非無法閱讀的情況下選擇 needs_review"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
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
        "classifier_source": "ai_outsider_candidate",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
        "requires_human_action": true,
        "ai_notes": "此題目為編製次數分配表的標準題型，因候選清單中無更具體的子技能，且禁止選擇 needs_review，故選擇 C1。",
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
        "candidate_source": "outsider",
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "worked_example",
        "example_label": "例題1",
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
      "classification_source": "ai_outsider_candidate",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 3823,
      "detected_problem_type_id": "numeric_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3823,
        "question_text": "會計科三年甲班45人數學模擬考成績資料如下（略），試將此班依分數分成5組，編製成次數分配表。（圖片待補）",
        "answer": "略",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
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
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 0.95,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目明確要求將45人的成績依分數分成5組，並編製成次數分配表",
            "此題型完全符合統計資料的次數分配表編製步驟之技能範疇"
          ],
          "ai_rejected_candidates": {
            "needs_review": "雖然題目中含有「資料如下（略）」與「圖片待補」，但其數學任務與題意極為清晰，並非無法辨識之文本，因此不選擇 needs_review"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "本題題目文字清晰且題型明確，但因含有「圖片待補」與「資料如下（略）」，後續需要人工補齊具體的成績數據或圖表以供學生作答。",
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
          "candidate_source": "structure",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習1",
          "linked_example": "例題1",
          "linked_example_id": 3822,
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
          "practice_label": "隨堂練習1",
          "linked_example": "例題1",
          "section_order": 0,
          "example_number": null,
          "practice_number": 1,
          "nearby_worked_examples": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            }
          ],
          "linked_worked_example": {
            "example_id": 3822,
            "source_type": "worked_example",
            "example_label": "例題1",
            "practice_label": "",
            "section_order": 0,
            "title_head": "例題 1"
          },
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            },
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            },
            {
              "example_id": 3824,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題1"
            },
            {
              "example_id": 3825,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題2"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": true,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "requires_human_action",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 0.95,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目明確要求將45人的成績依分數分成5組，並編製成次數分配表",
          "此題型完全符合統計資料的次數分配表編製步驟之技能範疇"
        ],
        "ai_rejected_candidates": {
          "needs_review": "雖然題目中含有「資料如下（略）」與「圖片待補」，但其數學任務與題意極為清晰，並非無法辨識之文本，因此不選擇 needs_review"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
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
        "classifier_source": "ai",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "本題題目文字清晰且題型明確，但因含有「圖片待補」與「資料如下（略）」，後續需要人工補齊具體的成績數據或圖表以供學生作答。",
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
        "candidate_source": "structure",
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "in_class_practice",
        "example_label": "",
        "practice_label": "隨堂練習1",
        "linked_example": "例題1",
        "linked_example_id": 3822,
        "linked_example_task_family": "generic_numeric_family",
        "structure_consistency": "consistent",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "compute_numeric",
      "classification_source": "ai",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 3824,
      "detected_problem_type_id": "numeric_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3824,
        "question_text": "有一組數值資料為60、64、66、68、73、75、76、85，試求這組數字的全距。",
        "answer": "25",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
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
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "The problem asks for the range of a given set of numbers, which is 85 minus 60 equals 25.",
            "Calculating the range is the initial step in constructing a frequency distribution table to determine class intervals.",
            "Since needs_review is forbidden for readable stems, C1 is the correct choice."
          ],
          "ai_rejected_candidates": {
            "needs_review": "The question is clear and directly related to the steps of constructing a frequency distribution table."
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "The calculation of the range (全距) is a standard numeric computation step within the frequency distribution table construction process.",
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
          "candidate_source": "structure",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
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
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            },
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            },
            {
              "example_id": 3824,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題1"
            },
            {
              "example_id": 3825,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題2"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": true,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "The problem asks for the range of a given set of numbers, which is 85 minus 60 equals 25.",
          "Calculating the range is the initial step in constructing a frequency distribution table to determine class intervals.",
          "Since needs_review is forbidden for readable stems, C1 is the correct choice."
        ],
        "ai_rejected_candidates": {
          "needs_review": "The question is clear and directly related to the steps of constructing a frequency distribution table."
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
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
        "classifier_source": "ai",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "The calculation of the range (全距) is a standard numeric computation step within the frequency distribution table construction process.",
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
        "candidate_source": "structure",
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "numeric",
        "answer_shape": "numeric",
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
      "classification_source": "ai",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 3825,
      "detected_problem_type_id": "numeric_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 3825,
        "question_text": "某公司企劃部員工20人，年齡資料如下：25、26、27、28、28、30、31、31、32、35、36、36、37、37、38、39、39、40、42、44。試將此組資料分組，定組距為5，依年齡分成4組，最小一組為25～30，編製成次數分配表。（圖片待補）",
        "answer": "次數：25~30(5人), 30~35(4人), 35~40(8人), 40~45(3人)",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "unordered_solution_set",
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
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目要求將20位員工的年齡資料，以組距為5、最小一組為25至30歲，編製成次數分配表。",
            "此題完全符合當前技能「統計資料的次數分配表編製步驟」的定義。",
            "依據強制合約，在題目清晰可讀的情況下，禁止選擇 needs_review，因此選擇唯一的候選者 C1。"
          ],
          "ai_rejected_candidates": {
            "needs_review": "題目語意完整且清晰，無須進行人工審查。"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "本題為標準的次數分配表編製題目，對應到 C1 (compute_numeric) 進行次數的計算與歸類。",
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
          "candidate_source": "structure",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
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
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            },
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            },
            {
              "example_id": 3824,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題1"
            },
            {
              "example_id": 3825,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題2"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": true,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "unordered_solution_set",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目要求將20位員工的年齡資料，以組距為5、最小一組為25至30歲，編製成次數分配表。",
          "此題完全符合當前技能「統計資料的次數分配表編製步驟」的定義。",
          "依據強制合約，在題目清晰可讀的情況下，禁止選擇 needs_review，因此選擇唯一的候選者 C1。"
        ],
        "ai_rejected_candidates": {
          "needs_review": "題目語意完整且清晰，無須進行人工審查。"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
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
        "classifier_source": "ai",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "本題為標準的次數分配表編製題目，對應到 C1 (compute_numeric) 進行次數的計算與歸類。",
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
        "candidate_source": "structure",
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "numeric",
        "answer_shape": "numeric",
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
      "classification_source": "ai",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "unordered_solution_set",
      "checker_key": "integer_checker"
    }
  ],
  "unclassified_examples": [],
  "risk_examples": [
    3822,
    3823,
    3824,
    3825
  ],
  "split_or_merge_recommendation": "induced_from_source_features",
  "classifier_gate": {
    "status": "classifier_auto_pending_promote",
    "allowed": true,
    "warnings": [
      "generic_fallback_blocked_by_source_skill_binding",
      "uniform_core_target_task_alignment_threshold_relaxed"
    ]
  },
  "generator_draft_gate": {
    "status": "generator_draft_allowed",
    "allowed": true,
    "warnings": [
      "generic_fallback_blocked_by_source_skill_binding",
      "uniform_core_target_task_alignment_threshold_relaxed"
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
      "generic_fallback_blocked_by_source_skill_binding",
      "uniform_core_target_task_alignment_threshold_relaxed"
    ]
  },
  "exception_review_gate": {
    "required": false,
    "reasons": []
  },
  "reports": {
    "phase1_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B4_FrequencyDistributionTableConstruction_phase1_summary.json",
    "phase1_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B4_FrequencyDistributionTableConstruction_phase1_summary.md",
    "phase1_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B4_FrequencyDistributionTableConstruction_phase1_summary.json",
    "phase1_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B4_FrequencyDistributionTableConstruction_phase1_summary.md"
  },
  "next_action": "phase2_generate_from_induced_specs",
  "timestamp": "2026-06-23T14:47:42.218779+00:00",
  "dry_run": true,
  "auto_review_summary": {
    "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
    "main_skill_anchor": {
      "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
      "skill_ch_name": "統計資料的次數分配表編製步驟",
      "skill_en_name": "FrequencyDistributionTableConstruction",
      "chapter": "3 統計",
      "section": "3-2 統計資料整理",
      "normalized_skill_terms": [
        "2 統計資料整理",
        "3 統計",
        "construction",
        "distribution",
        "frequency",
        "frequencydi",
        "frequencydistributiontableconstruction",
        "table",
        "tributiontablecon",
        "truction",
        "vh",
        "vocational",
        "數學b",
        "數學b4",
        "統計",
        "統計資料整理",
        "統計資料的次數分配表編製步驟"
      ],
      "expected_task_families": [],
      "expected_math_objects": [],
      "expected_subskill_candidates": [],
      "skill_anchor_scope": "default",
      "fallback_subskill": {
        "subskill_id": "same_as_main_skill",
        "subskill_name": "統計資料的次數分配表編製步驟",
        "subskill_scope": "fallback",
        "display_note": "此子技能為 fallback，用於收納未細分或綜合題"
      },
      "source_belongs_to_current_skill_by_default": true,
      "source_skill_scope_locked": true,
      "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
      "classification_scope": "within_current_skill",
      "skill_mapping_authority": "textbook_examples.skill_id",
      "anchor_authority": "skill_id_derived_no_cross_family_pollution",
      "classification_mandate": "【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\n【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\nTrusted skill anchor (do not override):\n- skill_id: vh_數學B4_FrequencyDistributionTableConstruction\n- skill_ch_name: 統計資料的次數分配表編製步驟\n- skill_en_name: FrequencyDistributionTableConstruction\n- expected_task_families: []\n- expected_subskill_candidates: []\n- skill_anchor_scope: default\n- source_skill_scope_locked: True\n"
    },
    "spec_mode": "ai_first_induce_from_sources",
    "semantic_classifications": [
      {
        "example_id": 3822,
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 0.9,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目要求將40人的英文模擬考成績分成7組並編製成次數分配表",
          "根據強制合約，此題目與技能 vh_數學B4_FrequencyDistributionTableConstruction 100% 對齊",
          "在候選清單中，除了 needs_review 之外，僅有 C1 (compute_numeric) 可供選擇",
          "依據規則，禁止選擇 needs_review，因此選擇 C1"
        ],
        "ai_rejected_candidates": {
          "needs_review": "題目清晰可讀，且規則禁止在非無法閱讀的情況下選擇 needs_review"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
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
        "classifier_source": "ai_outsider_candidate",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
        "requires_human_action": true,
        "ai_notes": "此題目為編製次數分配表的標準題型，因候選清單中無更具體的子技能，且禁止選擇 needs_review，故選擇 C1。",
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
        "candidate_source": "outsider",
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "worked_example",
        "example_label": "例題1",
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
        "example_id": 3823,
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 0.95,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目明確要求將45人的成績依分數分成5組，並編製成次數分配表",
          "此題型完全符合統計資料的次數分配表編製步驟之技能範疇"
        ],
        "ai_rejected_candidates": {
          "needs_review": "雖然題目中含有「資料如下（略）」與「圖片待補」，但其數學任務與題意極為清晰，並非無法辨識之文本，因此不選擇 needs_review"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
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
        "classifier_source": "ai",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "本題題目文字清晰且題型明確，但因含有「圖片待補」與「資料如下（略）」，後續需要人工補齊具體的成績數據或圖表以供學生作答。",
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
        "candidate_source": "structure",
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "in_class_practice",
        "example_label": "",
        "practice_label": "隨堂練習1",
        "linked_example": "例題1",
        "linked_example_id": 3822,
        "linked_example_task_family": "generic_numeric_family",
        "structure_consistency": "consistent",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      {
        "example_id": 3824,
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "The problem asks for the range of a given set of numbers, which is 85 minus 60 equals 25.",
          "Calculating the range is the initial step in constructing a frequency distribution table to determine class intervals.",
          "Since needs_review is forbidden for readable stems, C1 is the correct choice."
        ],
        "ai_rejected_candidates": {
          "needs_review": "The question is clear and directly related to the steps of constructing a frequency distribution table."
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
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
        "classifier_source": "ai",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "The calculation of the range (全距) is a standard numeric computation step within the frequency distribution table construction process.",
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
        "candidate_source": "structure",
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "numeric",
        "answer_shape": "numeric",
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
        "example_id": 3825,
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目要求將20位員工的年齡資料，以組距為5、最小一組為25至30歲，編製成次數分配表。",
          "此題完全符合當前技能「統計資料的次數分配表編製步驟」的定義。",
          "依據強制合約，在題目清晰可讀的情況下，禁止選擇 needs_review，因此選擇唯一的候選者 C1。"
        ],
        "ai_rejected_candidates": {
          "needs_review": "題目語意完整且清晰，無須進行人工審查。"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
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
        "classifier_source": "ai",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "本題為標準的次數分配表編製題目，對應到 C1 (compute_numeric) 進行次數的計算與歸類。",
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
        "candidate_source": "structure",
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "numeric",
        "answer_shape": "numeric",
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
      }
    ],
    "classification_diagnostics": [
      {
        "example_id": 3822,
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 0.9,
        "ai_semantic_status": "ok",
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "classifier_source": "ai_outsider_candidate",
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
        "conflict_reason": "",
        "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
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
        "ai_best_candidate_id": "C1",
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "outsider",
        "outsider_candidates": [
          "C1"
        ],
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": []
      },
      {
        "example_id": 3823,
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 0.95,
        "ai_semantic_status": "ok",
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "classifier_source": "ai",
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
        "conflict_reason": "",
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
        "ai_best_candidate_id": "C1",
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "structure",
        "outsider_candidates": [],
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": []
      },
      {
        "example_id": 3824,
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_semantic_status": "ok",
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "classifier_source": "ai",
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
        "conflict_reason": "",
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
        "ai_best_candidate_id": "C1",
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "structure",
        "outsider_candidates": [],
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": []
      },
      {
        "example_id": 3825,
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_semantic_status": "ok",
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "classifier_source": "ai",
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
        "conflict_reason": "",
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
        "ai_best_candidate_id": "C1",
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "structure",
        "outsider_candidates": [],
        "selected_generator_contract": {
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
        },
        "variable_randomization_notes": []
      }
    ],
    "ai_semantic_status": "ok",
    "ai_semantic_unavailable_reason": "",
    "ai_invalid_response_reason": "",
    "source_structure_report": {
      "source_type_distribution": {
        "worked_example": 1,
        "in_class_practice": 1,
        "basic_exercise": 2
      },
      "example_practice_link_map": [
        {
          "practice_label": "隨堂練習1",
          "linked_example": "例題1",
          "example_id": 3823
        }
      ],
      "structure_mismatch_examples": [],
      "same_section_family_distribution": {
        "generic_numeric_family": 4
      }
    },
    "source_type_distribution": {
      "worked_example": 1,
      "in_class_practice": 1,
      "basic_exercise": 2
    },
    "example_practice_link_map": [
      {
        "practice_label": "隨堂練習1",
        "linked_example": "例題1",
        "example_id": 3823
      }
    ],
    "structure_mismatch_examples": [],
    "same_section_family_distribution": {
      "generic_numeric_family": 4
    },
    "example_features": [
      {
        "source_example_id": 3822,
        "question_text": "國貿科三年甲班40人英文模擬考成績資料如下：32、38、41、45、47、49、51、52、53、53、55、56、57、58、61、61、62、63、64、64、65、65、65、66、67、69、70、70、71、75、77、77、78、79、80、85、87、89、92、96。試將此班依分數分成7組，編製成次數分配表。（圖片待補）",
        "answer": "次數分配表（組距10，從30開始）",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
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
        "classifier_source": "ai_outsider_candidate",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 0.9,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目要求將40人的英文模擬考成績分成7組並編製成次數分配表",
            "根據強制合約，此題目與技能 vh_數學B4_FrequencyDistributionTableConstruction 100% 對齊",
            "在候選清單中，除了 needs_review 之外，僅有 C1 (compute_numeric) 可供選擇",
            "依據規則，禁止選擇 needs_review，因此選擇 C1"
          ],
          "ai_rejected_candidates": {
            "needs_review": "題目清晰可讀，且規則禁止在非無法閱讀的情況下選擇 needs_review"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai_outsider_candidate",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
          "requires_human_action": true,
          "ai_notes": "此題目為編製次數分配表的標準題型，因候選清單中無更具體的子技能，且禁止選擇 needs_review，故選擇 C1。",
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
          "candidate_source": "outsider",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "worked_example",
          "example_label": "例題1",
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
          "example_label": "例題1",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": 1,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            }
          ],
          "same_section_sequence": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            },
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            },
            {
              "example_id": 3824,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題1"
            },
            {
              "example_id": 3825,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題2"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": true,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      {
        "source_example_id": 3823,
        "question_text": "會計科三年甲班45人數學模擬考成績資料如下（略），試將此班依分數分成5組，編製成次數分配表。（圖片待補）",
        "answer": "略",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
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
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 0.95,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目明確要求將45人的成績依分數分成5組，並編製成次數分配表",
            "此題型完全符合統計資料的次數分配表編製步驟之技能範疇"
          ],
          "ai_rejected_candidates": {
            "needs_review": "雖然題目中含有「資料如下（略）」與「圖片待補」，但其數學任務與題意極為清晰，並非無法辨識之文本，因此不選擇 needs_review"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "本題題目文字清晰且題型明確，但因含有「圖片待補」與「資料如下（略）」，後續需要人工補齊具體的成績數據或圖表以供學生作答。",
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
          "candidate_source": "structure",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習1",
          "linked_example": "例題1",
          "linked_example_id": 3822,
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
          "practice_label": "隨堂練習1",
          "linked_example": "例題1",
          "section_order": 0,
          "example_number": null,
          "practice_number": 1,
          "nearby_worked_examples": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            }
          ],
          "linked_worked_example": {
            "example_id": 3822,
            "source_type": "worked_example",
            "example_label": "例題1",
            "practice_label": "",
            "section_order": 0,
            "title_head": "例題 1"
          },
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            },
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            },
            {
              "example_id": 3824,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題1"
            },
            {
              "example_id": 3825,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題2"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": true,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      {
        "source_example_id": 3824,
        "question_text": "有一組數值資料為60、64、66、68、73、75、76、85，試求這組數字的全距。",
        "answer": "25",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
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
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "The problem asks for the range of a given set of numbers, which is 85 minus 60 equals 25.",
            "Calculating the range is the initial step in constructing a frequency distribution table to determine class intervals.",
            "Since needs_review is forbidden for readable stems, C1 is the correct choice."
          ],
          "ai_rejected_candidates": {
            "needs_review": "The question is clear and directly related to the steps of constructing a frequency distribution table."
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "The calculation of the range (全距) is a standard numeric computation step within the frequency distribution table construction process.",
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
          "candidate_source": "structure",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
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
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            },
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            },
            {
              "example_id": 3824,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題1"
            },
            {
              "example_id": 3825,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題2"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": true,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      {
        "source_example_id": 3825,
        "question_text": "某公司企劃部員工20人，年齡資料如下：25、26、27、28、28、30、31、31、32、35、36、36、37、37、38、39、39、40、42、44。試將此組資料分組，定組距為5，依年齡分成4組，最小一組為25～30，編製成次數分配表。（圖片待補）",
        "answer": "次數：25~30(5人), 30~35(4人), 35~40(8人), 40~45(3人)",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "unordered_solution_set",
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
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目要求將20位員工的年齡資料，以組距為5、最小一組為25至30歲，編製成次數分配表。",
            "此題完全符合當前技能「統計資料的次數分配表編製步驟」的定義。",
            "依據強制合約，在題目清晰可讀的情況下，禁止選擇 needs_review，因此選擇唯一的候選者 C1。"
          ],
          "ai_rejected_candidates": {
            "needs_review": "題目語意完整且清晰，無須進行人工審查。"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "本題為標準的次數分配表編製題目，對應到 C1 (compute_numeric) 進行次數的計算與歸類。",
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
          "candidate_source": "structure",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
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
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            },
            {
              "example_id": 3823,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習 1"
            },
            {
              "example_id": 3824,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題1"
            },
            {
              "example_id": 3825,
              "source_type": "basic_exercise",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "3-2習題 基礎題2"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": true,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "unordered_solution_set",
        "checker_key": "integer_checker"
      }
    ],
    "semantic_alignment": {
      "main_skill_anchor": {
        "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "skill_ch_name": "統計資料的次數分配表編製步驟",
        "skill_en_name": "FrequencyDistributionTableConstruction",
        "chapter": "3 統計",
        "section": "3-2 統計資料整理",
        "normalized_skill_terms": [
          "2 統計資料整理",
          "3 統計",
          "construction",
          "distribution",
          "frequency",
          "frequencydi",
          "frequencydistributiontableconstruction",
          "table",
          "tributiontablecon",
          "truction",
          "vh",
          "vocational",
          "數學b",
          "數學b4",
          "統計",
          "統計資料整理",
          "統計資料的次數分配表編製步驟"
        ],
        "expected_task_families": [],
        "expected_math_objects": [],
        "expected_subskill_candidates": [],
        "skill_anchor_scope": "default",
        "fallback_subskill": {
          "subskill_id": "same_as_main_skill",
          "subskill_name": "統計資料的次數分配表編製步驟",
          "subskill_scope": "fallback",
          "display_note": "此子技能為 fallback，用於收納未細分或綜合題"
        },
        "source_belongs_to_current_skill_by_default": true,
        "source_skill_scope_locked": true,
        "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "classification_scope": "within_current_skill",
        "skill_mapping_authority": "textbook_examples.skill_id",
        "anchor_authority": "skill_id_derived_no_cross_family_pollution",
        "classification_mandate": "【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\n【強制合約｜最高優先級】\n目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，並直接在此 anchor 範圍內切分子技能（subskills）。\n禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；若規則分類已在 anchor 子技能清單內，必須接受。\n\nTrusted skill anchor (do not override):\n- skill_id: vh_數學B4_FrequencyDistributionTableConstruction\n- skill_ch_name: 統計資料的次數分配表編製步驟\n- skill_en_name: FrequencyDistributionTableConstruction\n- expected_task_families: []\n- expected_subskill_candidates: []\n- skill_anchor_scope: default\n- source_skill_scope_locked: True\n"
      },
      "ai_semantic_status": "ok",
      "skill_terms": [
        "2 統計資料整理",
        "3 統計",
        "construction",
        "distribution",
        "frequency",
        "frequencydi",
        "frequencydistributiontableconstruction",
        "table",
        "tributiontablecon",
        "truction",
        "vh",
        "vocational",
        "數學b",
        "數學b4",
        "統計",
        "統計資料整理",
        "統計資料的次數分配表編製步驟"
      ],
      "source_terms": [
        "25",
        "26",
        "27",
        "28",
        "30",
        "31",
        "32",
        "35",
        "36",
        "37",
        "38",
        "39",
        "40",
        "41",
        "42",
        "44",
        "45",
        "47",
        "49",
        "51",
        "52",
        "53",
        "55",
        "56",
        "57",
        "58",
        "61",
        "62",
        "63",
        "64",
        "65",
        "66",
        "67",
        "68",
        "69",
        "70",
        "71",
        "73",
        "75",
        "76",
        "77",
        "78",
        "79",
        "80",
        "85",
        "87",
        "89",
        "92",
        "96",
        "compute_numeric",
        "numeric",
        "依年齡分成4組",
        "國貿科三年甲班40人英文模擬考成績資料如下",
        "圖片待補",
        "定組距為5",
        "年齡資料如下",
        "最小一組為25",
        "會計科三年甲班45人數學模擬考成績資料如下",
        "有一組數值資料為60",
        "某公司企劃部員工20人",
        "編製成次數分配表",
        "試將此班依分數分成5組",
        "試將此班依分數分成7組",
        "試將此組資料分組",
        "試求這組數字的全距"
      ],
      "expected_subskill_candidates": [],
      "observed_target_task_distribution": {
        "compute_numeric": 4
      },
      "same_family_subskill_mismatch_examples": [],
      "examples_outside_expected_subskills": [],
      "suggested_action": "",
      "examples_outside_expected_family": [
        3822
      ],
      "problem_type_terms": [
        "an",
        "answer",
        "compute",
        "compute_numeric",
        "hort",
        "numeric",
        "numeric / compute_numeric",
        "numeric_computation",
        "point_quadrant",
        "short",
        "text_short",
        "wer"
      ],
      "expected_task_candidates": [],
      "expected_skill_families": [],
      "observed_source_family_distribution": {
        "generic_numeric_family": 4
      },
      "source_family_distribution": {
        "generic_numeric_family": 4
      },
      "candidate_problem_type_families": [
        "generic_numeric_family"
      ],
      "dominant_source_task": "compute_numeric",
      "dominant_source_task_ratio": 1.0,
      "uniform_core_target_task": "compute_numeric",
      "uniform_core_target_task_ratio": 1.0,
      "uniform_core_target_task_count": 4,
      "uniform_core_threshold_relaxed": true,
      "dominant_source_family": [
        "generic_numeric_family"
      ],
      "dominant_source_family_ratio": 1.0,
      "skill_source_score": 0.8,
      "skill_problem_type_score": 0.8,
      "source_problem_type_score": 0.8,
      "per_problem_type_scores": [
        {
          "problem_type_id": "numeric_compute_numeric_short_answer",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "inferred_tasks": [
            "compute_numeric"
          ],
          "skill_problem_type_score": 0.0,
          "source_problem_type_score": 0.0267,
          "task_consistent_with_skill": true,
          "family_consistent_with_skill": true,
          "answer_contract_supported": true
        }
      ],
      "decision": "warn",
      "blockers": [],
      "warnings": [
        "uniform_core_target_task_alignment_threshold_relaxed"
      ],
      "induction_core_example_count": 4,
      "induction_enrichment_example_count": 0,
      "source_skill_scope_locked": true,
      "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
      "classification_scope": "within_current_skill",
      "skill_mapping_authority": "textbook_examples.skill_id",
      "core_skill_concept": "frequencydistributiontableconstruction",
      "supporting_math_objects": [],
      "source_quality_reject_examples": []
    },
    "source_alignment_status": "warn",
    "skill_problem_type_alignment_status": "warn",
    "alignment_score": 0.8,
    "alignment_warnings": [
      "uniform_core_target_task_alignment_threshold_relaxed",
      "disallowed_blocker_promoted_to_warning:mixed_source_families",
      "disallowed_blocker_promoted_to_warning:requires_human_action"
    ],
    "alignment_blockers": [],
    "source_family_distribution": {
      "generic_numeric_family": 4
    },
    "candidate_problem_type_families": [
      "generic_numeric_family"
    ],
    "expected_skill_families": [],
    "expected_subskill_candidates": [],
    "observed_target_task_distribution": {
      "compute_numeric": 4
    },
    "same_family_subskill_mismatch_examples": [],
    "examples_outside_expected_subskills": [],
    "suggested_action": "",
    "requires_human_action": true,
    "excluded_source_examples": [],
    "rejected_source_examples": [],
    "source_quality_issues": [],
    "semantic_mismatch_examples": [],
    "suspected_wrong_skill_examples": [
      3822
    ],
    "same_family_extension_examples": [],
    "section_scope_subskill_extension_examples": [],
    "same_as_main_skill_examples": [],
    "inherited_from_previous_context_examples": [],
    "low_source_examples": [],
    "coverage_floor_suggestions": [],
    "anchor_subskill_bootstrap": {
      "bootstrapped_tasks": [],
      "bootstrapped_count": 0,
      "skipped_tasks": []
    },
    "candidate_only_problem_types": [
      {
        "example_id": 3822,
        "problem_type_id": "numeric_compute_numeric_short_answer",
        "reason": "runtime_not_supported"
      },
      {
        "example_id": 3823,
        "problem_type_id": "numeric_compute_numeric_short_answer",
        "reason": "runtime_not_supported"
      },
      {
        "example_id": 3824,
        "problem_type_id": "numeric_compute_numeric_short_answer",
        "reason": "runtime_not_supported"
      },
      {
        "example_id": 3825,
        "problem_type_id": "numeric_compute_numeric_short_answer",
        "reason": "runtime_not_supported"
      }
    ],
    "candidate_only_count": 4,
    "same_as_main_skill_count": 0,
    "rule_only_classification_count": 0,
    "hybrid_resolved_count": 0,
    "subskills": [
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
        "example_id": 3822,
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
        "pass_with_warning": true,
        "requires_human_action": true,
        "induction_tier": "core",
        "included_in_core_induction": true,
        "enrichment_reasons": [],
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "classification_source": "ai_outsider_candidate",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "induction_eligibility": "eligible",
        "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "title_stem_preview": "國貿科三年甲班40人英文模擬考成績資料如下：32、38、41、45、47、49、51、52、53、53、55、56、57、58、61、61、62、63、64、6"
      },
      {
        "example_id": 3823,
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
        "classification_source": "ai",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "induction_eligibility": "eligible",
        "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "title_stem_preview": "會計科三年甲班45人數學模擬考成績資料如下（略），試將此班依分數分成5組，編製成次數分配表。（圖片待補）"
      },
      {
        "example_id": 3824,
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
        "classification_source": "ai",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "induction_eligibility": "eligible",
        "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "title_stem_preview": "有一組數值資料為60、64、66、68、73、75、76、85，試求這組數字的全距。"
      },
      {
        "example_id": 3825,
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
        "classification_source": "ai",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "induction_eligibility": "eligible",
        "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "title_stem_preview": "某公司企劃部員工20人，年齡資料如下：25、26、27、28、28、30、31、31、32、35、36、36、37、37、38、39、39、40、42、44。試"
      }
    ],
    "induction_clusters": [
      {
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "numeric",
          "compute_numeric",
          "short_answer",
          [
            "numeric_computation"
          ],
          [],
          "default"
        ],
        "source_example_ids": [
          3822,
          3823,
          3824,
          3825
        ],
        "answer_type": "numeric",
        "presentation_mode": "short_answer",
        "source_has_choices": false
      }
    ],
    "induced_problem_type_specs": [
      {
        "problem_type_id": "numeric_compute_numeric_short_answer",
        "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "display_name": "numeric / compute_numeric",
        "answer_format_hint": "text_short",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          3822,
          3823,
          3824,
          3825
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
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "numeric_compute_numeric_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ],
          "template_slots": {
            "stem": "point_quadrant"
          }
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
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "numeric",
          "compute_numeric",
          "short_answer",
          [
            "numeric_computation"
          ],
          [],
          "default"
        ],
        "canonical_base_problem_type_id": "compute_numeric_short_answer",
        "value_type_prefix": "numeric",
        "_resolved_template_slot": "point_quadrant",
        "naming_warning": "naming_warning:numeric_prefix_but_hint_is_text_short"
      }
    ],
    "candidate_problem_types": [
      {
        "problem_type_id": "numeric_compute_numeric_short_answer",
        "proposed_problem_type_id": "numeric_compute_numeric_short_answer",
        "display_name": "numeric / compute_numeric",
        "matched_example_ids": [
          3822,
          3823,
          3824,
          3825
        ],
        "matched_example_count": 4,
        "unmatched_example_ids": [],
        "representative_example_id": 3822,
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
          "generic_fallback_blocked_by_source_skill_binding",
          "uniform_core_target_task_alignment_threshold_relaxed"
        ],
        "checker_contract_warnings": [],
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "numeric",
          "compute_numeric",
          "short_answer",
          [
            "numeric_computation"
          ],
          [],
          "default"
        ],
        "problem_type_spec_draft": {
          "problem_type_id": "numeric_compute_numeric_short_answer",
          "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "display_name": "numeric / compute_numeric",
          "answer_format_hint": "text_short",
          "answer_fields": null,
          "answer_separator": null,
          "source_example_ids": [
            3822,
            3823,
            3824,
            3825
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
            "templates": [
              "template_scalar_unknown",
              "template_feature_value"
            ],
            "problem_type_id": "numeric_compute_numeric_short_answer",
            "contract_validation_blockers": [],
            "contract_validation_warnings": [
              "single_template_variant_only",
              "variation_dimensions_below_recommended_minimum"
            ],
            "template_slots": {
              "stem": "point_quadrant"
            }
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
          "grouping_reason": "single_signature_group",
          "feature_signature": [
            "numeric",
            "compute_numeric",
            "short_answer",
            [
              "numeric_computation"
            ],
            [],
            "default"
          ],
          "canonical_base_problem_type_id": "compute_numeric_short_answer",
          "value_type_prefix": "numeric",
          "_resolved_template_slot": "point_quadrant",
          "naming_warning": "naming_warning:numeric_prefix_but_hint_is_text_short"
        },
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "template_slot": "point_quadrant",
        "canonical_base_problem_type_id": "compute_numeric_short_answer",
        "value_type_prefix": "numeric",
        "subskill_id": "compute_numeric",
        "requires_human_action": true,
        "requires_human_rule_pack": true,
        "pending_problem_type_induction": true,
        "answer_type": "text_short",
        "runtime_status": "runtime_ready_candidate",
        "next_action": "phase2_foundation_preflight",
        "semantic_alignment": {
          "skill_problem_type_score": 0.0,
          "source_problem_type_score": 0.0267,
          "task_consistent_with_skill": true
        }
      }
    ],
    "per_example_classification": [
      {
        "example_id": 3822,
        "detected_problem_type_id": "numeric_compute_numeric_short_answer",
        "example_feature": {
          "source_example_id": 3822,
          "question_text": "國貿科三年甲班40人英文模擬考成績資料如下：32、38、41、45、47、49、51、52、53、53、55、56、57、58、61、61、62、63、64、64、65、65、65、66、67、69、70、70、71、75、77、77、78、79、80、85、87、89、92、96。試將此班依分數分成7組，編製成次數分配表。（圖片待補）",
          "answer": "次數分配表（組距10，從30開始）",
          "choices": [],
          "has_choices": false,
          "stem_embeds_choices": false,
          "answer_type": "integer",
          "answer_shape": "numeric",
          "checker": "integer_checker",
          "equivalence": "numeric_exact",
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
          "classifier_source": "ai_outsider_candidate",
          "math_meta_tags": [],
          "forced_target_task": "",
          "meta_answer_format_hint": "",
          "semantic_classification": {
            "ai_target_task": "compute_numeric",
            "ai_task_family": "generic_numeric_family",
            "ai_confidence": 0.9,
            "ai_best_candidate_id": "C1",
            "ai_evidence": [
              "題目要求將40人的英文模擬考成績分成7組並編製成次數分配表",
              "根據強制合約，此題目與技能 vh_數學B4_FrequencyDistributionTableConstruction 100% 對齊",
              "在候選清單中，除了 needs_review 之外，僅有 C1 (compute_numeric) 可供選擇",
              "依據規則，禁止選擇 needs_review，因此選擇 C1"
            ],
            "ai_rejected_candidates": {
              "needs_review": "題目清晰可讀，且規則禁止在非無法閱讀的情況下選擇 needs_review"
            },
            "ai_available": true,
            "ai_error": "",
            "ai_unavailable_reason": "",
            "ai_semantic_status": "ok",
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
            "classifier_source": "ai_outsider_candidate",
            "classification_decision": "",
            "conflict_reason": "",
            "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
            "requires_human_action": true,
            "ai_notes": "此題目為編製次數分配表的標準題型，因候選清單中無更具體的子技能，且禁止選擇 needs_review，故選擇 C1。",
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
            "candidate_source": "outsider",
            "selected_generator_contract": {
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
            },
            "variable_randomization_notes": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
            "skill_scope_trusted": true,
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "math_objects": [],
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "source_type": "worked_example",
            "example_label": "例題1",
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
            "example_label": "例題1",
            "practice_label": "",
            "linked_example": "",
            "section_order": 0,
            "example_number": 1,
            "practice_number": null,
            "nearby_worked_examples": [],
            "linked_worked_example": null,
            "linked_practices": [
              {
                "example_id": 3823,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習1",
                "section_order": 0,
                "title_head": "隨堂練習 1"
              }
            ],
            "same_section_sequence": [
              {
                "example_id": 3822,
                "source_type": "worked_example",
                "example_label": "例題1",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 1"
              },
              {
                "example_id": 3823,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習1",
                "section_order": 0,
                "title_head": "隨堂練習 1"
              },
              {
                "example_id": 3824,
                "source_type": "basic_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 基礎題1"
              },
              {
                "example_id": 3825,
                "source_type": "basic_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 基礎題2"
              }
            ]
          },
          "induction_tier": "core",
          "enrichment_reasons": [],
          "included_in_core_induction": true,
          "source_skill_scope_locked": true,
          "skill_mapping_authority": "textbook_examples.skill_id",
          "classification_scope": "within_current_skill",
          "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
          "unresolved_within_current_skill": true,
          "pending_problem_type_induction": true,
          "requires_human_rule_pack": true,
          "requires_human_action": true,
          "unresolved_reason": "semantic_score_zero_within_current_skill",
          "generator_readiness": "pending_problem_type_induction",
          "usable_for_phase3": false,
          "equivalence_type": "numeric_exact",
          "checker_key": "integer_checker"
        },
        "answer_shape": "numeric",
        "classification_confidence": "high",
        "classification_reason": "ai_outsider_candidate",
        "risk_flags": [
          "outsider_candidate_within_confirmed_skill",
          "requires_human_action",
          "candidate_only_problem_type"
        ],
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 0.9,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目要求將40人的英文模擬考成績分成7組並編製成次數分配表",
            "根據強制合約，此題目與技能 vh_數學B4_FrequencyDistributionTableConstruction 100% 對齊",
            "在候選清單中，除了 needs_review 之外，僅有 C1 (compute_numeric) 可供選擇",
            "依據規則，禁止選擇 needs_review，因此選擇 C1"
          ],
          "ai_rejected_candidates": {
            "needs_review": "題目清晰可讀，且規則禁止在非無法閱讀的情況下選擇 needs_review"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai_outsider_candidate",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
          "requires_human_action": true,
          "ai_notes": "此題目為編製次數分配表的標準題型，因候選清單中無更具體的子技能，且禁止選擇 needs_review，故選擇 C1。",
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
          "candidate_source": "outsider",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "worked_example",
          "example_label": "例題1",
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
        "classification_source": "ai_outsider_candidate",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "requires_human_rule_pack": true,
        "induction_eligibility": "eligible"
      },
      {
        "example_id": 3823,
        "detected_problem_type_id": "numeric_compute_numeric_short_answer",
        "example_feature": {
          "source_example_id": 3823,
          "question_text": "會計科三年甲班45人數學模擬考成績資料如下（略），試將此班依分數分成5組，編製成次數分配表。（圖片待補）",
          "answer": "略",
          "choices": [],
          "has_choices": false,
          "stem_embeds_choices": false,
          "answer_type": "integer",
          "answer_shape": "numeric",
          "checker": "integer_checker",
          "equivalence": "numeric_exact",
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
          "classifier_source": "ai",
          "math_meta_tags": [],
          "forced_target_task": "",
          "meta_answer_format_hint": "",
          "semantic_classification": {
            "ai_target_task": "compute_numeric",
            "ai_task_family": "generic_numeric_family",
            "ai_confidence": 0.95,
            "ai_best_candidate_id": "C1",
            "ai_evidence": [
              "題目明確要求將45人的成績依分數分成5組，並編製成次數分配表",
              "此題型完全符合統計資料的次數分配表編製步驟之技能範疇"
            ],
            "ai_rejected_candidates": {
              "needs_review": "雖然題目中含有「資料如下（略）」與「圖片待補」，但其數學任務與題意極為清晰，並非無法辨識之文本，因此不選擇 needs_review"
            },
            "ai_available": true,
            "ai_error": "",
            "ai_unavailable_reason": "",
            "ai_semantic_status": "ok",
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
            "classifier_source": "ai",
            "classification_decision": "",
            "conflict_reason": "",
            "source_mapping_warning": "",
            "requires_human_action": true,
            "ai_notes": "本題題目文字清晰且題型明確，但因含有「圖片待補」與「資料如下（略）」，後續需要人工補齊具體的成績數據或圖表以供學生作答。",
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
            "candidate_source": "structure",
            "selected_generator_contract": {
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
            },
            "variable_randomization_notes": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
            "skill_scope_trusted": true,
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "math_objects": [],
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "source_type": "in_class_practice",
            "example_label": "",
            "practice_label": "隨堂練習1",
            "linked_example": "例題1",
            "linked_example_id": 3822,
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
            "practice_label": "隨堂練習1",
            "linked_example": "例題1",
            "section_order": 0,
            "example_number": null,
            "practice_number": 1,
            "nearby_worked_examples": [
              {
                "example_id": 3822,
                "source_type": "worked_example",
                "example_label": "例題1",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 1"
              }
            ],
            "linked_worked_example": {
              "example_id": 3822,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例題 1"
            },
            "linked_practices": [],
            "same_section_sequence": [
              {
                "example_id": 3822,
                "source_type": "worked_example",
                "example_label": "例題1",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 1"
              },
              {
                "example_id": 3823,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習1",
                "section_order": 0,
                "title_head": "隨堂練習 1"
              },
              {
                "example_id": 3824,
                "source_type": "basic_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 基礎題1"
              },
              {
                "example_id": 3825,
                "source_type": "basic_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 基礎題2"
              }
            ]
          },
          "induction_tier": "core",
          "enrichment_reasons": [],
          "included_in_core_induction": true,
          "source_skill_scope_locked": true,
          "skill_mapping_authority": "textbook_examples.skill_id",
          "classification_scope": "within_current_skill",
          "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
          "unresolved_within_current_skill": true,
          "pending_problem_type_induction": true,
          "requires_human_rule_pack": true,
          "requires_human_action": true,
          "unresolved_reason": "semantic_score_zero_within_current_skill",
          "generator_readiness": "pending_problem_type_induction",
          "usable_for_phase3": false,
          "equivalence_type": "numeric_exact",
          "checker_key": "integer_checker"
        },
        "answer_shape": "numeric",
        "classification_confidence": "high",
        "classification_reason": "ai",
        "risk_flags": [
          "requires_human_action",
          "candidate_only_problem_type"
        ],
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 0.95,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目明確要求將45人的成績依分數分成5組，並編製成次數分配表",
            "此題型完全符合統計資料的次數分配表編製步驟之技能範疇"
          ],
          "ai_rejected_candidates": {
            "needs_review": "雖然題目中含有「資料如下（略）」與「圖片待補」，但其數學任務與題意極為清晰，並非無法辨識之文本，因此不選擇 needs_review"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "本題題目文字清晰且題型明確，但因含有「圖片待補」與「資料如下（略）」，後續需要人工補齊具體的成績數據或圖表以供學生作答。",
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
          "candidate_source": "structure",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習1",
          "linked_example": "例題1",
          "linked_example_id": 3822,
          "linked_example_task_family": "generic_numeric_family",
          "structure_consistency": "consistent",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "linked_example_consistent_boost; structure_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "subskill_id": "compute_numeric",
        "classification_source": "ai",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "requires_human_rule_pack": true,
        "induction_eligibility": "eligible"
      },
      {
        "example_id": 3824,
        "detected_problem_type_id": "numeric_compute_numeric_short_answer",
        "example_feature": {
          "source_example_id": 3824,
          "question_text": "有一組數值資料為60、64、66、68、73、75、76、85，試求這組數字的全距。",
          "answer": "25",
          "choices": [],
          "has_choices": false,
          "stem_embeds_choices": false,
          "answer_type": "integer",
          "answer_shape": "numeric",
          "checker": "integer_checker",
          "equivalence": "numeric_exact",
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
          "classifier_source": "ai",
          "math_meta_tags": [],
          "forced_target_task": "",
          "meta_answer_format_hint": "",
          "semantic_classification": {
            "ai_target_task": "compute_numeric",
            "ai_task_family": "generic_numeric_family",
            "ai_confidence": 1.0,
            "ai_best_candidate_id": "C1",
            "ai_evidence": [
              "The problem asks for the range of a given set of numbers, which is 85 minus 60 equals 25.",
              "Calculating the range is the initial step in constructing a frequency distribution table to determine class intervals.",
              "Since needs_review is forbidden for readable stems, C1 is the correct choice."
            ],
            "ai_rejected_candidates": {
              "needs_review": "The question is clear and directly related to the steps of constructing a frequency distribution table."
            },
            "ai_available": true,
            "ai_error": "",
            "ai_unavailable_reason": "",
            "ai_semantic_status": "ok",
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
            "classifier_source": "ai",
            "classification_decision": "",
            "conflict_reason": "",
            "source_mapping_warning": "",
            "requires_human_action": false,
            "ai_notes": "The calculation of the range (全距) is a standard numeric computation step within the frequency distribution table construction process.",
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
            "candidate_source": "structure",
            "selected_generator_contract": {
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
            },
            "variable_randomization_notes": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
            "skill_scope_trusted": true,
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "math_objects": [],
            "answer_type": "numeric",
            "answer_shape": "numeric",
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
                "example_id": 3822,
                "source_type": "worked_example",
                "example_label": "例題1",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 1"
              }
            ],
            "linked_worked_example": null,
            "linked_practices": [],
            "same_section_sequence": [
              {
                "example_id": 3822,
                "source_type": "worked_example",
                "example_label": "例題1",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 1"
              },
              {
                "example_id": 3823,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習1",
                "section_order": 0,
                "title_head": "隨堂練習 1"
              },
              {
                "example_id": 3824,
                "source_type": "basic_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 基礎題1"
              },
              {
                "example_id": 3825,
                "source_type": "basic_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 基礎題2"
              }
            ]
          },
          "induction_tier": "core",
          "enrichment_reasons": [],
          "included_in_core_induction": true,
          "source_skill_scope_locked": true,
          "skill_mapping_authority": "textbook_examples.skill_id",
          "classification_scope": "within_current_skill",
          "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
          "unresolved_within_current_skill": true,
          "pending_problem_type_induction": true,
          "requires_human_rule_pack": true,
          "requires_human_action": true,
          "unresolved_reason": "semantic_score_zero_within_current_skill",
          "generator_readiness": "pending_problem_type_induction",
          "usable_for_phase3": false,
          "equivalence_type": "numeric_exact",
          "checker_key": "integer_checker"
        },
        "answer_shape": "numeric",
        "classification_confidence": "high",
        "classification_reason": "ai",
        "risk_flags": [
          "candidate_only_problem_type"
        ],
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "The problem asks for the range of a given set of numbers, which is 85 minus 60 equals 25.",
            "Calculating the range is the initial step in constructing a frequency distribution table to determine class intervals.",
            "Since needs_review is forbidden for readable stems, C1 is the correct choice."
          ],
          "ai_rejected_candidates": {
            "needs_review": "The question is clear and directly related to the steps of constructing a frequency distribution table."
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "The calculation of the range (全距) is a standard numeric computation step within the frequency distribution table construction process.",
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
          "candidate_source": "structure",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
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
        "classification_source": "ai",
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "requires_human_rule_pack": true,
        "induction_eligibility": "eligible"
      },
      {
        "example_id": 3825,
        "detected_problem_type_id": "numeric_compute_numeric_short_answer",
        "example_feature": {
          "source_example_id": 3825,
          "question_text": "某公司企劃部員工20人，年齡資料如下：25、26、27、28、28、30、31、31、32、35、36、36、37、37、38、39、39、40、42、44。試將此組資料分組，定組距為5，依年齡分成4組，最小一組為25～30，編製成次數分配表。（圖片待補）",
          "answer": "次數：25~30(5人), 30~35(4人), 35~40(8人), 40~45(3人)",
          "choices": [],
          "has_choices": false,
          "stem_embeds_choices": false,
          "answer_type": "integer",
          "answer_shape": "numeric",
          "checker": "integer_checker",
          "equivalence": "unordered_solution_set",
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
          "classifier_source": "ai",
          "math_meta_tags": [],
          "forced_target_task": "",
          "meta_answer_format_hint": "",
          "semantic_classification": {
            "ai_target_task": "compute_numeric",
            "ai_task_family": "generic_numeric_family",
            "ai_confidence": 1.0,
            "ai_best_candidate_id": "C1",
            "ai_evidence": [
              "題目要求將20位員工的年齡資料，以組距為5、最小一組為25至30歲，編製成次數分配表。",
              "此題完全符合當前技能「統計資料的次數分配表編製步驟」的定義。",
              "依據強制合約，在題目清晰可讀的情況下，禁止選擇 needs_review，因此選擇唯一的候選者 C1。"
            ],
            "ai_rejected_candidates": {
              "needs_review": "題目語意完整且清晰，無須進行人工審查。"
            },
            "ai_available": true,
            "ai_error": "",
            "ai_unavailable_reason": "",
            "ai_semantic_status": "ok",
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
            "classifier_source": "ai",
            "classification_decision": "",
            "conflict_reason": "",
            "source_mapping_warning": "",
            "requires_human_action": false,
            "ai_notes": "本題為標準的次數分配表編製題目，對應到 C1 (compute_numeric) 進行次數的計算與歸類。",
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
            "candidate_source": "structure",
            "selected_generator_contract": {
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
            },
            "variable_randomization_notes": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
            "skill_scope_trusted": true,
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "math_objects": [],
            "answer_type": "numeric",
            "answer_shape": "numeric",
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
                "example_id": 3822,
                "source_type": "worked_example",
                "example_label": "例題1",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 1"
              }
            ],
            "linked_worked_example": null,
            "linked_practices": [],
            "same_section_sequence": [
              {
                "example_id": 3822,
                "source_type": "worked_example",
                "example_label": "例題1",
                "practice_label": "",
                "section_order": 0,
                "title_head": "例題 1"
              },
              {
                "example_id": 3823,
                "source_type": "in_class_practice",
                "example_label": "",
                "practice_label": "隨堂練習1",
                "section_order": 0,
                "title_head": "隨堂練習 1"
              },
              {
                "example_id": 3824,
                "source_type": "basic_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 基礎題1"
              },
              {
                "example_id": 3825,
                "source_type": "basic_exercise",
                "example_label": "",
                "practice_label": "",
                "section_order": 0,
                "title_head": "3-2習題 基礎題2"
              }
            ]
          },
          "induction_tier": "core",
          "enrichment_reasons": [],
          "included_in_core_induction": true,
          "source_skill_scope_locked": true,
          "skill_mapping_authority": "textbook_examples.skill_id",
          "classification_scope": "within_current_skill",
          "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
          "unresolved_within_current_skill": true,
          "pending_problem_type_induction": true,
          "requires_human_rule_pack": true,
          "requires_human_action": true,
          "unresolved_reason": "semantic_score_zero_within_current_skill",
          "generator_readiness": "pending_problem_type_induction",
          "usable_for_phase3": false,
          "equivalence_type": "unordered_solution_set",
          "checker_key": "integer_checker"
        },
        "answer_shape": "numeric",
        "classification_confidence": "high",
        "classification_reason": "ai",
        "risk_flags": [
          "candidate_only_problem_type"
        ],
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目要求將20位員工的年齡資料，以組距為5、最小一組為25至30歲，編製成次數分配表。",
            "此題完全符合當前技能「統計資料的次數分配表編製步驟」的定義。",
            "依據強制合約，在題目清晰可讀的情況下，禁止選擇 needs_review，因此選擇唯一的候選者 C1。"
          ],
          "ai_rejected_candidates": {
            "needs_review": "題目語意完整且清晰，無須進行人工審查。"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
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
          "classifier_source": "ai",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "本題為標準的次數分配表編製題目，對應到 C1 (compute_numeric) 進行次數的計算與歸類。",
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
          "candidate_source": "structure",
          "selected_generator_contract": {
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
          },
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
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
        "classification_source": "ai",
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
      "numeric_compute_numeric_short_answer"
    ],
    "classifier_gate": {
      "status": "classifier_auto_pending_promote",
      "allowed": true,
      "warnings": [
        "generic_fallback_blocked_by_source_skill_binding",
        "uniform_core_target_task_alignment_threshold_relaxed"
      ]
    },
    "generator_draft_gate": {
      "status": "generator_draft_allowed",
      "allowed": true,
      "warnings": [
        "generic_fallback_blocked_by_source_skill_binding",
        "uniform_core_target_task_alignment_threshold_relaxed"
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
        "generic_fallback_blocked_by_source_skill_binding",
        "uniform_core_target_task_alignment_threshold_relaxed"
      ]
    },
    "exception_review_gate": {
      "required": false,
      "reasons": []
    },
    "next_action": "phase2_generate_from_induced_specs",
    "source_skill_scope_locked": true,
    "source_skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
    "classification_scope": "within_current_skill",
    "skill_mapping_authority": "textbook_examples.skill_id",
    "human_confirmed_rule_pack_applied": false,
    "matched_registered_yaml_rule_pack": "",
    "ai_classification_overridden_by_human_confirmed_rule_pack": false,
    "curated_specs_available": false
  },
  "classifier_source": "ai_bootstrap_with_default_fallback+phase1_induction",
  "ai_bootstrap_used": true,
  "ai_bootstrap_status": "success",
  "ai_bootstrap_confidence_summary": {
    "count": 4,
    "avg": 1.0,
    "low_confidence_count": 0
  },
  "inspect_report_note": "Missing classifier/rule pack, AI bootstrap attempted.",
  "ai_bootstrap_error": "",
  "ai_bootstrap_raw_response_preview": "```json\n{\n  \"skill_id\": \"vh_數學B4_FrequencyDistributionTableConstruction\",\n  \"skill_ch_name\": \"統計資料的次數分配表編製步驟\",\n  \"classifier_source\": \"llm_bootstrap\",\n  \"problem_types\": [\n    {\n      \"problem_type_id\": \"calculate_range_of_data\",\n      \"problem_type_ch_name\": \"求數值資料的全距\",\n      \"description\": \"給定一組數值資料，找出最大值與最小值並計算其差值（全距）。\",\n      \"answer_contract\": {\n        \"checker\": \"numeric_checker\",\n        \"equivalence\": \"numeric_equivalence\",\n        \"requires_human_action\": false\n      }\n    },\n    {\n      \"problem_type_id\": \"construct_frequency_distribution_table\",\n      \"problem_type_ch_name\": \"編製次數分配表\",\n      \"description\": \"給定一組原始數據，依據指定的組數或組距，將數據進行分組整理並編製成次數分配表。\",\n      \"answer_contract\": {\n        \"checker\": \"manual_review_checker\",\n        \"equivalence\": \"manual_review_or_ai_judged\",\n        \"requires_human_action\": true\n      }\n    }\n  ],\n  \"source_classifications\": [\n    {\n      \"source_index\": 1,\n      \"problem_type_id\": \"construct_frequency_distribution_table\",\n      \"confidence\": 1.",
  "ai_bootstrap_validation_errors": [
    "source_index=1: invalid_problem_type_id=",
    "source_index=1: invalid_checker=",
    "source_index=1: invalid_equivalence=",
    "source_index=1: unrelated_problem_type=",
    "source_index=1: invalid_problem_type_id_style=",
    "source_index=2: invalid_problem_type_id=",
    "source_index=2: invalid_checker=",
    "source_index=2: invalid_equivalence=",
    "source_index=2: unrelated_problem_type=",
    "source_index=2: invalid_problem_type_id_style=",
    "source_index=3: invalid_problem_type_id=",
    "source_index=3: invalid_checker=",
    "source_index=3: invalid_equivalence=",
    "source_index=3: unrelated_problem_type=",
    "source_index=3: invalid_problem_type_id_style=",
    "source_index=4: invalid_problem_type_id=",
    "source_index=4: invalid_checker=",
    "source_index=4: invalid_equivalence=",
    "source_index=4: unrelated_problem_type=",
    "source_index=4: invalid_problem_type_id_style=",
    "ai_bootstrap_all_unclassified_promoted_to_default_problem_type"
  ],
  "ai_bootstrap_prompt_version": "gencode_phase1_ai_bootstrap_v2",
  "ai_bootstrap_model": "gemini-3.5-flash",
  "ai_bootstrap_provider": "google",
  "ai_bootstrap_config_source": "db_global_selected_model",
  "default_problem_type_used": true,
  "problem_type_spec_first": true,
  "spec_defined_problem_type_ids": [
    "numeric_compute_numeric_short_answer"
  ],
  "spec_mode": "ai_first_induce_from_sources",
  "induced_problem_type_specs": [
    {
      "problem_type_id": "numeric_compute_numeric_short_answer",
      "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
      "target_task": "compute_numeric",
      "task_family": "generic_numeric_family",
      "display_name": "numeric / compute_numeric",
      "answer_format_hint": "text_short",
      "answer_fields": null,
      "answer_separator": null,
      "source_example_ids": [
        3822,
        3823,
        3824,
        3825
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
        "templates": [
          "template_scalar_unknown",
          "template_feature_value"
        ],
        "problem_type_id": "numeric_compute_numeric_short_answer",
        "contract_validation_blockers": [],
        "contract_validation_warnings": [
          "single_template_variant_only",
          "variation_dimensions_below_recommended_minimum"
        ],
        "template_slots": {
          "stem": "point_quadrant"
        }
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
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "numeric",
        "compute_numeric",
        "short_answer",
        [
          "numeric_computation"
        ],
        [],
        "default"
      ],
      "canonical_base_problem_type_id": "compute_numeric_short_answer",
      "value_type_prefix": "numeric",
      "_resolved_template_slot": "point_quadrant",
      "naming_warning": "naming_warning:numeric_prefix_but_hint_is_text_short"
    }
  ],
  "induction_clusters": [
    {
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "numeric",
        "compute_numeric",
        "short_answer",
        [
          "numeric_computation"
        ],
        [],
        "default"
      ],
      "source_example_ids": [
        3822,
        3823,
        3824,
        3825
      ],
      "answer_type": "numeric",
      "presentation_mode": "short_answer",
      "source_has_choices": false
    }
  ],
  "human_review_items": [],
  "source_quality_reject_examples": [],
  "proposal_items": [
    {
      "problem_type_id": "integer_compute_numeric",
      "proposed_problem_type_id": "integer_compute_numeric",
      "display_name": "integer / compute_numeric",
      "matched_example_ids": [
        3822,
        3823,
        3824
      ],
      "matched_example_count": 3,
      "unmatched_example_ids": [],
      "representative_example_id": 3822,
      "structural_features": [
        "text_short"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "integer",
        "answer_shape": "text_short",
        "answer_equivalence": "numeric_exact",
        "checker": "integer_checker",
        "accepted_formats": [
          "5",
          "5.0",
          "-3"
        ],
        "source_has_choices": false,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "presentation_mode": "",
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "text_short"
      },
      "checker_key_proposal": "integer_checker",
      "equivalence_type_proposal": "numeric_exact",
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
        "generic_fallback_blocked_by_source_skill_binding",
        "uniform_core_target_task_alignment_threshold_relaxed"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "numeric",
        "compute_numeric",
        "short_answer",
        [
          "numeric_computation"
        ],
        [],
        "default"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "text_short_compute_text_short_expression",
        "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "display_name": "numeric / compute_numeric",
        "answer_format_hint": "text_short",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          3822,
          3823,
          3824,
          3825
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
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "numeric_compute_numeric_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ],
          "template_slots": {
            "stem": "point_quadrant"
          }
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
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "numeric",
          "compute_numeric",
          "short_answer",
          [
            "numeric_computation"
          ],
          [],
          "default"
        ],
        "canonical_base_problem_type_id": "compute_numeric_short_answer",
        "value_type_prefix": "numeric",
        "_resolved_template_slot": "point_quadrant",
        "naming_warning": "naming_warning:numeric_prefix_but_hint_is_text_short"
      },
      "generator_readiness": "pending_problem_type_induction",
      "usable_for_phase3": false,
      "template_slot": "point_quadrant",
      "canonical_base_problem_type_id": "compute_numeric_short_answer",
      "value_type_prefix": "numeric",
      "subskill_id": "compute_numeric",
      "requires_human_action": true,
      "requires_human_rule_pack": true,
      "pending_problem_type_induction": true,
      "answer_type": "text_short",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0267,
        "task_consistent_with_skill": true
      }
    },
    {
      "problem_type_id": "integer_compute_numeric",
      "proposed_problem_type_id": "integer_compute_numeric",
      "display_name": "integer / compute_numeric",
      "matched_example_ids": [
        3825
      ],
      "matched_example_count": 1,
      "unmatched_example_ids": [],
      "representative_example_id": 3825,
      "structural_features": [
        "text_short"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "integer",
        "answer_shape": "text_short",
        "answer_equivalence": "unordered_solution_set",
        "checker": "integer_checker",
        "accepted_formats": [
          "5",
          "5.0",
          "-3"
        ],
        "source_has_choices": false,
        "equivalence_type": "unordered_solution_set",
        "checker_key": "integer_checker",
        "presentation_mode": "",
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "text_short"
      },
      "checker_key_proposal": "integer_checker",
      "equivalence_type_proposal": "unordered_solution_set",
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
        "generic_fallback_blocked_by_source_skill_binding",
        "uniform_core_target_task_alignment_threshold_relaxed"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "numeric",
        "compute_numeric",
        "short_answer",
        [
          "numeric_computation"
        ],
        [],
        "default"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "text_short_compute_text_short_expression",
        "skill_id": "vh_數學B4_FrequencyDistributionTableConstruction",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "display_name": "numeric / compute_numeric",
        "answer_format_hint": "text_short",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          3822,
          3823,
          3824,
          3825
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
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "numeric_compute_numeric_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ],
          "template_slots": {
            "stem": "point_quadrant"
          }
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
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "numeric",
          "compute_numeric",
          "short_answer",
          [
            "numeric_computation"
          ],
          [],
          "default"
        ],
        "canonical_base_problem_type_id": "compute_numeric_short_answer",
        "value_type_prefix": "numeric",
        "_resolved_template_slot": "point_quadrant",
        "naming_warning": "naming_warning:numeric_prefix_but_hint_is_text_short"
      },
      "generator_readiness": "pending_problem_type_induction",
      "usable_for_phase3": false,
      "template_slot": "point_quadrant",
      "canonical_base_problem_type_id": "compute_numeric_short_answer",
      "value_type_prefix": "numeric",
      "subskill_id": "compute_numeric",
      "requires_human_action": true,
      "requires_human_rule_pack": true,
      "pending_problem_type_induction": true,
      "answer_type": "text_short",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0267,
        "task_consistent_with_skill": true
      }
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
  "problem_type_grouping_contract_status": "PASS_WITH_WARNINGS",
  "problem_type_grouping_contract_warnings": [
    "mixed_group_split_required:text_short_compute_text_short_expression"
  ],
  "problem_type_grouping_contract_violations": []
}
```
