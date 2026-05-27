# Gencode / AgentSkillV2 Answer Contract and Closed Loop Gate v0.2

## 1. 文件目的與適用範圍

本文件是目前 Gencode / AgentSkillV2 自動出題閉環的 canonical SOP。

用途包含：

- problem_type answer_contract
- equivalence_type
- checker / verifier 選擇
- bootstrap from existing skill
- Phase 2 foundation preflight
- Phase 3 publish gate
- runtime quality audit
- web runtime audit
- source alignment audit
- reference case

目前部分舊 SOP 已污染，未清理前，本文件作為 Gencode closed-loop 的乾淨 source of truth。

## 2. answer_contract schema

每個 problem_type 必須有 answer_contract：

```yaml
answer_contract:
  answer_type:
  equivalence_type:
  checker_key:
  order_matters:
  accepted_format_notes:
  canonical_answer_schema:
```

說明每個欄位：

- answer_type
- equivalence_type
- checker_key
- order_matters
- accepted_format_notes
- canonical_answer_schema

若缺 answer_contract，該 problem_type 不得標為 runtime_ready，也不得讓 pipeline final status 為 PASS。

## 3. equivalence_type whitelist

列出並說明：

- exact_string
- numeric_exact
- rational_equivalent
- choice_label
- unordered_solution_set
- interval_set
- algebraic_equivalent
- manual_review_or_ai_judged

## 4. 禁止 raw string compare 的情境

以下不得 raw string compare：

- 解集合題
- 分數、小數、百分比等價題
- 選擇題
- 區間題
- 代數式等價題
- 證明、說明、畫圖、列舉題

## 5. 開放性答案處理策略

依序判斷：

A. 可結構化比對
B. 可不失真改寫為選擇題
C. 改寫會失真，標為 manual_review / future_ai_judged / handwriting_ai_checked

明確寫入：

不得為了自動判分而強行把證明、畫圖、完整列舉、解釋理由題改成選擇題。

## 6. Semantic Coverage Audit Gate

pipeline report 必須輸出：

```yaml
answer_contract_summary:
  observed_problem_type_answer_contracts:
  missing_answer_contract_problem_types:
  missing_checker_key_problem_types:
  equivalence_test_required_problem_types:
  convertible_to_choice_problem_types:
  manual_review_or_ai_judged_problem_types:
```

PASS 規則：

- 缺 answer_contract 不可 PASS
- 缺 checker_key 不可 PASS
- open-ended 若標 exact_string 不可 PASS
- manual_review_or_ai_judged 可以存在，但必須明確標記

## 7. Bootstrap From Existing Skill Gate

寫入：

當 DB examples 不足或語意不一致，但已有可信既有 skill.py，可 bootstrap。

條件：

- examples_total 過少或 misaligned
- 既有 skill.py 語意相近
- wrapper / adapter 可 py_compile
- 有 pytest 或 sample verification
- payload 必須改成目標 skill_id / problem_type_id / answer_contract

final_status 必須是：

PASS_BOOTSTRAP_ONLY

不得誤標為 PASS 或 FULL_OBSERVED_COVERAGE。

範例：

```yaml
vh_數學B1_NumberLine:
  source_coverage_status: INSUFFICIENT_OR_MISALIGNED_DB_EXAMPLES
  bootstrap_mode: true
  bootstrap_source_skill_id: jh_數學1上_NumberLine
  bootstrap_runtime_status: PASS
  final_status: PASS_BOOTSTRAP_ONLY
  full_observed_coverage: false
```

## 8. Phase 2 Build Planning / Foundation Preflight

規則：

- Phase 2 必須先做 dependency planning。
- 若缺 checker / verifier / domain function / generator，不應直接 BUILD_FAIL。
- 可修復缺口回傳 FOUNDATION_REPAIR_REQUIRED。
- 附上 repair_plan 與 next_action。
- foundation_ready = true 後才可進入 build。
- Phase 3 只可在 BUILD_PASS 或 BUILD_BOOTSTRAP_PASS 後執行。

支援 repair gap：

- missing_checker
- missing_verifier
- missing_domain_function
- missing_generator
- missing_runtime_binding
- missing_registry_binding

## 9. Phase 3 Publish Gate / Runtime Quality Gate

說明：

Phase 3 PASS 只代表技術發布門檻，不代表前台正常，也不代表課本語意完全貼合。

必須分層：

- Technical Closed Loop PASS
- Runtime Quality PASS
- Web Runtime PASS
- Source Alignment PASS / PARTIAL

### Technical Closed Loop PASS

條件：

- Phase 1 AUDIT_PASS 或可接受狀態
- Phase 2 BUILD_PASS
- Phase 3 PASS / publish_ready true
- registry binding / wrapper binding / runtime binding 完成
- deterministic runtime coverage 不缺 verified problem types

### Runtime Quality PASS

條件：

- choice quality audit PASS
- runtime distribution audit PASS
- manual_review 不外漏
- choice answer label 不固定單一選項
- wrapper 能抽到所有 expected verified problem types

### Web Runtime PASS

條件：

- web runtime audit PASS
- /get_next_question route_source = gencode_wrapper
- db_fallback_count = 0，除非 wrapper 明確失敗
- legacy_count = 0
- API observed problem types 涵蓋 verified problem types
- response payload 保留 problem_type_id / answer_contract / source / route_source

### Source Alignment PASS / PARTIAL

條件：

- source alignment audit 檢查 DB examples 題型形式是否被 runtime generator 語意覆蓋
- 若 missing_source_aligned_problem_types / possible_classifier_misclassifications / underrepresented_runtime_forms 存在，標 Source Alignment PARTIAL
- Source Alignment PARTIAL 可進技術發布審核，但必須列入 enhancement backlog，不得宣稱完整貼近課本例題

## 10. Runtime Quality Audit Gate

### Choice Quality Gate

所有 choice 題必須符合：

- answer / correct_answer 必須是 A/B/C/D label
- 不得把完整選項文字塞進 answer / correct_answer
- correct_text 可放 metadata / explanation
- choices 不可重複
- correct answer 必須存在於 choices
- choices shuffle 後，answer label 必須重新計算
- choice_question_count >= 20 且所有正確答案都是同一 label 時必須 FAIL
- checker 支援 A/B/C/D、a/b/c/d、(A)、1/2/3/4、完整選項文字 normalize

指令：

```powershell
python scripts\gencode_choice_quality_audit.py --skill-id <skill_id> --samples 100
```

修復：

```powershell
python scripts\gencode_repair_choice_quality.py --skill-id <skill_id> --samples 100
```

### Runtime Distribution Audit

指令：

```powershell
python scripts\gencode_runtime_distribution_audit.py --skill-id <skill_id> --samples 200
```

PASS 條件：

- observed problem types 涵蓋 expected verified problem types
- missing_problem_types 為空
- manual_review 不外漏
- choice answer label 不固定

### Web Runtime Audit

指令：

```powershell
python scripts\gencode_web_runtime_audit.py --skill-id <skill_id> --samples 50
```

PASS 條件：

- route_source = gencode_wrapper
- wrapper_loaded_count = samples
- db_fallback_count = 0 或僅 wrapper 失敗時 fallback
- legacy_count = 0
- observed problem types 涵蓋 verified problem types
- response 保留 problem_type_id / answer_contract

重要教訓：

若 route 每次 importlib.reload wrapper module，可能重置 wrapper _STATE，導致前台每次都抽到同一個 problem_type。Web Runtime Audit 必須能抓出這類問題。

## 11. Source Alignment Audit Gate

指令：

```powershell
python scripts\gencode_source_alignment_audit.py --skill-id <skill_id>
```

每筆 example 至少檢查：

- example_id
- source_preview
- classifier_problem_type_id
- runtime_category
- source_form_category
- verified_generator_exists
- alignment_status

判定：

- PASS：source form 與 problem_type 合理對應，且有 verified generator
- PARTIAL：有 generator，但 runtime 題型形式未完全貼近 source form
- FAIL：source form 明確，但無對應 generator，或被誤判為 manual_review / malformed
- MANUAL_REVIEW：來源真的缺字、破損、無法判斷

## 12. Gencode Closed Loop 標準執行順序

### Phase 1

```powershell
python scripts\gencode_pipeline_phase1_audit.py --skill-id <skill_id>
```

### Phase 2

```powershell
python scripts\gencode_pipeline_phase2_build.py --skill-id <skill_id>
```

若 next_action 指向 repair gap：

```powershell
python scripts\gencode_repair_build_gap.py --skill-id <skill_id> --gap missing_checker
python scripts\gencode_repair_build_gap.py --skill-id <skill_id> --gap missing_verifier
python scripts\gencode_repair_build_gap.py --skill-id <skill_id> --gap missing_domain_function
python scripts\gencode_repair_build_gap.py --skill-id <skill_id> --gap missing_generator
python scripts\gencode_repair_build_gap.py --skill-id <skill_id> --gap missing_runtime_binding
python scripts\gencode_repair_build_gap.py --skill-id <skill_id> --gap missing_registry_binding
```

每次 repair 後重跑 Phase 2。

### Phase 3

```powershell
python scripts\gencode_pipeline_phase3_publish_gate.py --skill-id <skill_id>
```

### Phase 3 後品質稽核

即使 Phase 3 PASS，仍必須執行：

```powershell
python scripts\gencode_choice_quality_audit.py --skill-id <skill_id> --samples 100
python scripts\gencode_runtime_distribution_audit.py --skill-id <skill_id> --samples 200
python scripts\gencode_web_runtime_audit.py --skill-id <skill_id> --samples 50
python scripts\gencode_source_alignment_audit.py --skill-id <skill_id>
```

## 13. Reference Case: vh_數學B1_AbsoluteValueInequality

本案例是第一個完整跑通三階段 closed loop、repair framework、publish gate、runtime quality audit、web runtime audit 的複雜 skill。

最終狀態：

| Gate | Status | Notes |
|---|---|---|
| Phase 1 | AUDIT_PASS | 10/10 examples covered |
| Phase 2 | BUILD_PASS | 4 verified problem types |
| Phase 3 | PASS | publish_ready true |
| Choice Quality | PASS | answer label not fixed |
| Runtime Distribution | PASS | 4 problem types observed |
| Web Runtime | PASS | route_source = gencode_wrapper |
| Source Alignment | PARTIAL | multi_part_abs_ineq_solving underrepresented |

教訓：

- Phase 3 PASS 不等於前台正常，必須跑 Web Runtime Audit。
- wrapper direct audit PASS 不代表 /get_next_question API 一定走 wrapper。
- choice 題不能只檢查正確答案可判對，還必須檢查答案 label 分布。
- manual_review_exclusions 是正常機制，但來源題修正後應重跑 Phase 1。
- 技術閉環與課本語意貼合必須分開判讀。
- Source Alignment PARTIAL 可以進入技術發布，但必須列為 enhancement backlog。

## 14. Backlog

- 補 multi_part_abs_ineq_solving source-aligned generator。
- 建立 legacy_skill_generate_signature_compatibility_audit，處理舊 skill generate(level/seed/difficulty) 介面不相容。
- 將 Phase 1/2/3 + repair + quality audit 串成 auto-run-until-human-review orchestrator。
- 未來建立 /admin/gencode_lab 後台頁面。
