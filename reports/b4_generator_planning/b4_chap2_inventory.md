# B4 Chapter 2 Inventory Report

## 0. Scope and Guardrails
- 本輪為 `inventory phase`，僅讀取與盤點。
- 本輪不修改 production code / tests / routes / templates / generators / database。
- 本輪不修改 coverage matrix、allowlist、adaptive scoring、mastery、APR、remediation。
- 本輪不啟動任何 implementation phase。

## 1. Evidence Sources
- `E:\Python\Mathproject_tvet_mathB\instance\kumon_math.db`
  - 表：`skill_curriculum`, `skills_info`, `textbook_examples`
  - 用途：Chap2 skills、display_order、section、題數與 source_type/needs_review 盤點。
- `E:\Python\Mathproject_tvet_mathB\core\vocational_math_b4\services\question_router.py`
  - 用途：檢查 Chap2 skills 是否已接 deterministic generator router。
- `E:\Python\Mathproject_tvet_mathB\core\vocational_math_b4\adaptive\b4_chapter1_deterministic_allowlist.py`
  - 用途：檢查 deterministic allowlist、AI-judged candidate metadata 是否已有 Chap2 註冊。
- `E:\Python\Mathproject_tvet_mathB\core\adaptive\session_engine.py`
  - 用途：檢查 adaptive_audit 暴露目前是否限定在 Chapter 1 free-response checkpoints。
- `E:\Python\Mathproject_tvet_mathB\core\routes\practice.py`
  - 用途：檢查 B4 adaptive preflight 與 audit 輸出流程位置。
- `E:\Python\Mathproject_tvet_mathB\core\vocational_math_b4\domain\b4_validators.py`
  - 用途：檢查 Chap2 機率題型所需 checker/validator 現況。
- `E:\Python\Mathproject_tvet_mathB\skills\`
  - 用途：檢查 Chap2 是否已有對應 skill file。
- `E:\Python\Mathproject_tvet_mathB\core\textbook_processor.py`（`infer_mathb4_ch2_self_assessment_skill` 區段）
  - 用途：觀察自評題 skill/problem_type 推斷規則與語意粒度。

## 2. Chapter Identification
- Chapter 名稱：`2 機率`
- Chapter 欄位實際值：`skill_curriculum.chapter = '2 機率'`
- Chapter id（運營辨識）：`2`（由 chapter 字串前綴判定；DB 無獨立 numeric chapter_id 欄位）
- sections（來自 `skill_curriculum.section`）：
  - `2-1 樣本空間與事件`
  - `2-2 機率的運算`
  - `2-3 數學期望值`

## 3. skill_curriculum Inventory
| display_order | skill_id | skill_name | display_name | chapter | section | source_type | notes |
|---|---|---|---|---|---|---|---|
| 20001 | vh_數學B4_BasicConceptsOfSets | BasicConceptsOfSets | 集合的基本概念 | 2 機率 | 2-1 樣本空間與事件 | DB table未設獨立欄位 | 與機率章交界技能 |
| 20001 | vh_數學B4_ProbabilityDefinition | ProbabilityDefinition | 機率的定義 | 2 機率 | 2-2 機率的運算 | DB table未設獨立欄位 | 章內核心起點 |
| 20001 | vh_數學B4_MathematicalExpectationDefinition | MathematicalExpectationDefinition | 數學期望值的定義與計算 | 2 機率 | 2-3 數學期望值 | DB table未設獨立欄位 | 與 2-3 同層起點 |
| 20001 | vh_數學B4_ProbabilityOperations | ProbabilityOperations | 機率的運算 | 2 機率 | 2-2 機率的運算 | DB table未設獨立欄位 | 自評題較多 |
| 20002 | vh_數學B4_SampleSpaceAndEvents | SampleSpaceAndEvents | 樣本空間與事件 | 2 機率 | 2-1 樣本空間與事件 | DB table未設獨立欄位 | 含 listing 類風險 |
| 20002 | vh_數學B4_ProbabilityProperties | ProbabilityProperties | 機率的性質 | 2 機率 | 2-2 機率的運算 | DB table未設獨立欄位 | 含補事件/聯集交集 |
| 20002 | vh_數學B4_ApplicationsOfExpectation | ApplicationsOfExpectation | 數學期望值的應用 | 2 機率 | 2-3 數學期望值 | DB table未設獨立欄位 | 多情境文字題 |
| 20002 | vh_數學B4_MathematicalExpectation | MathematicalExpectation | 數學期望值 | 2 機率 | 2-3 數學期望值 | DB table未設獨立欄位 | 自評題集中 |
| 20003 | vh_數學B4_ConditionalProbability | ConditionalProbability | 條件機率 | 2 機率 | 2-2 機率的運算 | DB table未設獨立欄位 | 需條件事件一致性檢查 |
| 20004 | vh_數學B4_IndependentEvents | IndependentEvents | 獨立事件 | 2 機率 | 2-2 機率的運算 | DB table未設獨立欄位 | 含表格/命中率題風險 |

檢查結論：
- duplicated skill rows：0
- missing display_order：0
- suspicious：`display_order` 非唯一（20001 有 4 筆，20002 有 4 筆）；需以 DB order + section/skill 序列規則做 tie-break。
- 章節一致性異常：`textbook_examples` 有 1 筆掛在 `source_chapter='3 統計'` 且 skill_id 為 Chap2（見第 8 節風險）。

## 4. Question Count Summary
| skill_id | section | textbook_examples count | in_class_practice count | self_assessment count | total count | needs_review count | image-related count | notes |
|---|---|---:|---:|---:|---:|---:|---:|---|
| vh_數學B4_BasicConceptsOfSets | 2-1 樣本空間與事件 | 4 | 2 | 1 | 10 | 5 | 0 | 含集合列舉/集合運算 |
| vh_數學B4_SampleSpaceAndEvents | 2-1 樣本空間與事件 | 2 | 2 | 6 | 13 | 7 | 0 | 含樣本空間 listing 需求 |
| vh_數學B4_ProbabilityDefinition | 2-2 機率的運算 | 6 | 5 | 0 | 15 | 4 | 2 | `needs_formula_review=1`, `needs_image_review=1` |
| vh_數學B4_ProbabilityProperties | 2-2 機率的運算 | 3 | 3 | 0 | 7 | 5 | 0 | 聯集/交集/補事件混合 |
| vh_數學B4_ConditionalProbability | 2-2 機率的運算 | 2 | 2 | 0 | 5 | 3 | 0 | 條件敘述一致性風險 |
| vh_數學B4_IndependentEvents | 2-2 機率的運算 | 1 | 1 | 0 | 4 | 3 | 0 | 含命中率比較題 |
| vh_數學B4_ProbabilityOperations | 2-2 機率的運算 | 0 | 0 | 9 | 9 | 9 | 0 | 自評題全 needs_review |
| vh_數學B4_MathematicalExpectationDefinition | 2-3 數學期望值 | 2 | 2 | 0 | 9 | 1 | 0 | 期望值入門計算 |
| vh_數學B4_ApplicationsOfExpectation | 2-3 數學期望值 | 2 | 2 | 0 | 10 | 2 | 0 | 抽獎/保險/獲利題 |
| vh_數學B4_MathematicalExpectation | 2-3 數學期望值 | 0 | 0 | 5 | 5 | 5 | 0 | 自評題為主 |

章節總量：
- textbook_examples：22
- in_class_practice：17
- self_assessment：26
- 其他 source_type（basic/advanced/exam 等）：22
- total：87
- needs_review：87
- needs_formula_review：1
- image-related（has_image / needs_image_review / image_dependency 任一）：2
- `source_page` / `page_index` 欄位訊號：0（在 source_description/notes 未觀察到）

## 5. Runtime / File Existence Audit
| skill_id | skill file exists? | generator exists? | route / wrapper exists? | checker exists? | in deterministic allowlist? | adaptive metadata exists? | notes |
|---|---|---|---|---|---|---|---|
| vh_數學B4_BasicConceptsOfSets | No | No | No (skill-specific) | No (skill-specific) | No | No | 僅見於教材處理/修復腳本與DB |
| vh_數學B4_SampleSpaceAndEvents | No | No | No | No | No | No | 同上 |
| vh_數學B4_ProbabilityDefinition | No | No | No | No | No | No | 同上 |
| vh_數學B4_ProbabilityProperties | No | No | No | No | No | No | 同上 |
| vh_數學B4_ConditionalProbability | No | No | No | No | No | No | 同上 |
| vh_數學B4_IndependentEvents | No | No | No | No | No | No | 同上 |
| vh_數學B4_ProbabilityOperations | No | No | No | No | No | No | 同上 |
| vh_數學B4_MathematicalExpectationDefinition | No | No | No | No | No | No | 同上 |
| vh_數學B4_ApplicationsOfExpectation | No | No | No | No | No | No | 同上 |
| vh_數學B4_MathematicalExpectation | No | No | No | No | No | No | 同上 |

補充觀察：
- 現有 `question_router.py` 與 `b4_chapter1_deterministic_allowlist.py` 僅 Chapter 1 runtime。
- `adaptive_audit` 與 `ai_judged_free_response` metadata 目前僅 Chapter 1（TreeDiagram/Pascal）候選。

## 6. Existing and Missing problem_type
| skill_id | existing problem_type | issue | proposed semantic problem_type | deterministic / choice / handwriting / manual_review | notes |
|---|---|---|---|---|---|
| vh_數學B4_BasicConceptsOfSets | mixed_counting, addition_principle, in_class_practice, set_concepts | 混入來源型標籤 `in_class_practice`；語意過粗 | set_membership_judgement, subset_listing, set_operation_result, inclusion_exclusion_count | deterministic + handwriting + choice | `subset_listing` 可能需 handwriting/free-response |
| vh_數學B4_SampleSpaceAndEvents | probability, in_class_practice, multiplication_principle | `in_class_practice` 不是 problem_type；`probability`過粗 | sample_space_listing, event_set_listing, event_relation_judgement, sample_space_count_numeric | handwriting + deterministic + choice | listing/集合表示不宜硬塞 int-answer |
| vh_數學B4_ProbabilityDefinition | probability, in_class_practice | 過粗 | classical_probability_fraction, complement_probability, dice_coin_probability_count | deterministic numeric | 需分數/小數/百分比 checker |
| vh_數學B4_ProbabilityProperties | probability, in_class_practice | 過粗 | union_intersection_probability, complement_rule_probability, set_probability_word_problem | deterministic numeric + choice | 注意事件記號一致性 |
| vh_數學B4_ConditionalProbability | probability, in_class_practice | 過粗 | conditional_probability_basic, without_replacement_conditional | deterministic numeric | 需條件敘述一致性檢查 |
| vh_數學B4_IndependentEvents | probability, in_class_practice | 過粗 | independent_joint_probability, independent_at_least_one_probability | deterministic numeric + choice | 表格題可能 manual_review |
| vh_數學B4_ProbabilityOperations | probability | 過粗 | probability_algebra_mixed, event_operation_probability | deterministic numeric + choice | 自評題大量 needs_review |
| vh_數學B4_MathematicalExpectationDefinition | probability, in_class_practice | 過粗；混入來源型標籤 | expectation_discrete_basic, expectation_from_distribution | deterministic numeric | 需 expected-value domain verifier |
| vh_數學B4_ApplicationsOfExpectation | probability, in_class_practice | 過粗；混入來源型標籤 | expectation_word_problem_profit_fairness | deterministic numeric + manual_review | 情境敘述長，解析風險高 |
| vh_數學B4_MathematicalExpectation | probability | 過粗 | expectation_assessment_numeric | deterministic numeric | 答案格式需統一（分數/小數） |

## 7. Triage Summary
### deterministic numeric candidates
- vh_數學B4_ProbabilityDefinition
- vh_數學B4_ProbabilityProperties
- vh_數學B4_ConditionalProbability
- vh_數學B4_IndependentEvents
- vh_數學B4_ProbabilityOperations
- vh_數學B4_MathematicalExpectationDefinition
- vh_數學B4_ApplicationsOfExpectation
- vh_數學B4_MathematicalExpectation
- vh_數學B4_BasicConceptsOfSets（僅計數/容斥數值子題）
- vh_數學B4_SampleSpaceAndEvents（僅 `n(S)` 或可唯一數值子題）

建議 checker 類型標記：
- integer：樣本數、計數題
- rational：古典機率/條件機率主體
- decimal_tolerance：小數機率題
- percentage：百分比機率題
- probability_range：範圍合法性（0~1）
- expected_value：期望值專用規則（可接受分數/有限小數）

### deterministic choice candidates
- 集合觀念判斷題（錯誤敘述、正確敘述）
- 機率比較/判斷題（含命中率比較題）
- 事件關係判斷（互斥/獨立）

### AI-judged handwriting / free-response candidates
- 樣本空間完整列舉（例如連續擲幣/擲骰）
- 事件集合列出（A, B, A∩B, A∪B, A'）
- 子集合完整列舉題

政策（inventory建議，未實作）：
- 不加入 deterministic allowlist
- scoring_policy 維持 `deferred_teacher_review` / visibility-only
- 不更新 mastery / APR / fail_streak / remediation

### future_ai_judged / manual review candidates
- 需圖表/表格解讀題（例如統測命中率比較題）
- OCR/公式疑慮題（`needs_formula_review` 或 parse_warning 明顯）
- 長文本多步驟推導題（題幹與答案映射不穩定）

## 8. Risk List
1. 答案格式風險：分數/小數/百分比/集合表示混用，若無統一 checker 規格易誤判。
2. 古典機率約分風險：需明確規範是否要求最簡分數。
3. 條件機率與獨立事件題幹一致性風險：條件描述與答案事件可能錯配。
4. 樣本空間 listing 風險：不適合 int-answer，需 handwriting/free-response 路徑。
5. 期望值應用題 verifier 風險：須有 domain-level expected value checker，避免僅字串比對。
6. image/table dependency 風險：ProbabilityDefinition 已見 image/needs_image_review 訊號。
7. 資料品質風險：Chapter 2 skill 出現 1 筆 `source_chapter='3 統計'` 異常掛載。
8. 題型 taxonomy 風險：`problem_type` 混入 `in_class_practice`（來源型態誤當題型）。
9. 排序風險：display_order 非唯一（20001/20002 各4筆），需明確 tie-break。
10. adaptive policy 風險：若直接接入 scoring 會誤觸 mastery/APR/remediation。
11. fake generator 風險：Chap2 目前無 runtime 接線，後續實作需避免「補假 skill file」解 missing module。

## 9. Recommended Next Phases
### Phase 6A：Chap2 semantic problem_type taxonomy freeze
- scope：整理 Chap2 semantic problem_type 命名與分流對照，不做 runtime 接線。
- allowed files in future phase：
  - `reports/b4_generator_planning/b4_phase6a_chap2_problem_type_taxonomy.md`
  - （若需）`reports/b4_generator_planning/*.csv`
- forbidden changes：production code / routes / generators / allowlist / scoring policy。
- required tests / manual smoke：N/A（文件盤點相位）；人工檢核命名一致性。
- expected report path：`reports/b4_generator_planning/b4_phase6a_chap2_problem_type_taxonomy.md`

### Phase 6B：probability domain functions / validators planning
- scope：僅規劃 checker contract（integer/rational/decimal/percentage/probability_range/expected_value）。
- allowed files in future phase：report 文件。
- forbidden changes：不改 runtime validator 程式。
- required tests / manual smoke：N/A（規劃文件）。
- expected report path：`reports/b4_generator_planning/b4_phase6b_probability_validator_plan.md`

### Phase 6C：first deterministic probability generator batch
- scope：1–3 個 problem_type（優先 ProbabilityDefinition/Properties 基礎題）。
- allowed files in future phase：
  - `core/vocational_math_b4/generators/<target>.py`
  - `core/vocational_math_b4/services/question_router.py`
  - `core/vocational_math_b4/domain/b4_validators.py`
  - `tests/test_b4_chap2_phase6c_*.py`
  - `reports/b4_generator_planning/b4_phase6c_*.md`
- forbidden changes：adaptive scoring/mastery/APR/remediation、coverage matrix、unrelated routes/templates。
- required tests / manual smoke：generator + router + checker + allowlist boundary + `/practice` smoke。
- expected report path：`reports/b4_generator_planning/b4_phase6c_deterministic_batch1_summary.md`

### Phase 6D：conditional probability / independent events generator batch
- scope：條件機率與獨立事件（小批次）。
- allowed files in future phase：同 6C（限相干檔案）。
- forbidden changes：同 6C。
- required tests / manual smoke：條件事件一致性測試、分數化簡與範圍檢查。
- expected report path：`reports/b4_generator_planning/b4_phase6d_conditional_independent_summary.md`

### Phase 6E：expected value generator batch
- scope：期望值定義與應用（小批次）。
- allowed files in future phase：同 6C（含 expected_value validator）。
- forbidden changes：同 6C。
- required tests / manual smoke：expected value domain tests、答案格式容忍策略測試。
- expected report path：`reports/b4_generator_planning/b4_phase6e_expectation_summary.md`

### Phase 6F：AI-judged listing / sample space handwriting candidate planning
- scope：僅規劃 SampleSpace/Set listing handwriting candidates，不直接上 deterministic。
- allowed files in future phase：規劃文件、候選設計文件。
- forbidden changes：不改 allowlist/scoring。
- required tests / manual smoke：N/A（規劃）。
- expected report path：`reports/b4_generator_planning/b4_phase6f_handwriting_candidate_plan.md`

### Phase 6G：adaptive audit visibility planning
- scope：僅規劃 audit exposure schema（visibility-only）。
- allowed files in future phase：規劃文件。
- forbidden changes：不更新 mastery/APR/fail_streak/remediation。
- required tests / manual smoke：N/A（規劃）。
- expected report path：`reports/b4_generator_planning/b4_phase6g_adaptive_audit_visibility_plan.md`

### Phase 6H：closure / postcheck
- scope：本章分階段收斂與 closure gate。
- allowed files in future phase：closure reports。
- forbidden changes：不混入新功能。
- required tests / manual smoke：彙整各 phase 測試與 smoke 結果。
- expected report path：`reports/b4_generator_planning/b4_phase6h_chap2_closure_summary.md`

## 10. Final Confirmation
- 是否只新增 / 更新 inventory report：是
- 是否修改 production code：否
- 是否修改 tests：否
- 是否修改 routes：否
- 是否修改 templates：否
- 是否修改 generators：否
- 是否修改 database：否
- 是否修改 coverage matrix：否
- 是否新增 allowlist：否
- 是否修改 adaptive scoring / mastery / APR / remediation：否
