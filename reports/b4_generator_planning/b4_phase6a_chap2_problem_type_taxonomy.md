# B4 Chapter 2 Phase 6A Problem Type Taxonomy Freeze

## 0. Scope and Guardrails

本輪為 **taxonomy freeze report only**。唯一允許新增/更新的檔案為本報告。

明確聲明：
- ❌ 未修改 production code
- ❌ 未修改 tests
- ❌ 未修改 routes
- ❌ 未修改 templates
- ❌ 未修改 generators
- ❌ 未修改 database
- ❌ 未修改 coverage matrix
- ❌ 未新增 allowlist
- ❌ 未修改 adaptive scoring / mastery / APR / remediation
- ❌ 未啟動 Phase 6B / 6C / implementation
- ✅ 僅新增本 taxonomy report

---

## 1. Evidence Sources

| 來源 | 路徑 | 用途 |
|---|---|---|
| Chap2 inventory | `reports/b4_generator_planning/b4_chap2_inventory.md` | 10 skills 盤點、題數、分流初稿、risk list |
| 教材匯入 SOP | `docs/系統SOP/教材匯入與技能生成SOP_v0.1.md` (v0.2) | deterministic / handwriting / future_ai_judged 分流規則 |
| AI 閉環 SOP | `docs/系統SOP/AI閉環開發與驗收SOP_v0.1.md` | agent 工作邊界、human approve 節點 |
| DB 查詢 | `instance/kumon_math.db` | 確認既有 `problem_type`、`source_description` 欄位語意 |

DB 查詢明細（最小 query，只讀）：
- table：`textbook_examples`
- query purpose 1：`SELECT skill_id, problem_type, source_description, COUNT(*)` — 盤點 Chap2 既有 problem_type 標籤實況
- query purpose 2：`PRAGMA table_info(textbook_examples)` — 確認欄位結構（無 source_type 獨立欄位；source_type 嵌入 source_description 字串）
- query purpose 3：`source_chapter != '2 機率'` filter — 確認異常掛載筆數

DB 查詢結論：
- 既有 problem_type 實際只有：`probability`、`in_class_practice`、`multiplication_principle`
- `source_type` 嵌在 `source_description` 字串中（如 `source_type=in_class_practice`），並非獨立欄位
- `in_class_practice` 同時出現在 problem_type 欄位（錯誤）與 source_description 字串（正確位置）
- 異常：`vh_數學B4_BasicConceptsOfSets` 有 1 筆 `source_chapter='3 統計'`

---

## 2. Taxonomy Principles

### 2.1 source_type 與 problem_type 分離

`source_type`（如 `textbook_example`、`in_class_practice`、`self_assessment`、`basic_exercise`、`exam_practice`）描述「題目來源」，屬於 metadata。

`problem_type` 必須描述「題型語意」，是 generator key 的基礎。兩者不可混用。

### 2.2 problem_type 命名原則

- 英文 snake_case
- 描述數學操作語意（不描述來源、難度、考試別）
- 可作為未來 generator 的 key
- 同類題型不過度切碎，也不過粗

### 2.3 分流先凍結，再寫 generator

本輪僅凍結分流分類與 problem_type 命名。不建議任何 runtime 接線。

### 2.4 listing 題不得硬轉 int-answer

樣本空間列舉、事件集合列舉、子集合列舉，答案非單一整數，不可強制成 deterministic int-answer。

---

## 3. Deprecated / Invalid Existing problem_type Labels

| existing label | issue | replacement strategy |
|---|---|---|
| `probability` | 過粗，涵蓋古典機率、補事件、聯集、條件、獨立、期望值等所有題型 | 拆成下方 Section 4 各細分 problem_type |
| `in_class_practice` | source_type 標籤，描述「來源」非「題型語意」；出現在 problem_type 欄位是錯誤存儲 | 保留於 source_description 字串，不得作為 problem_type |
| `multiplication_principle` | 描述解法策略，非題型語意；僅出現 1 筆 SampleSpaceAndEvents 且 source_type=exam_practice | 應重新分類為 `sample_space_count_numeric` 或 `event_relation_judgement` |
| `self_assessment` | source_type 標籤，不是題型語意 | 保留為 source metadata，不作 problem_type |
| `basic` / `advanced` / `exam` | difficulty-like 或 source 描述，非題型語意 | 保留為 metadata / difficulty 欄位 |

---

## 4. Skill-by-Skill Proposed Taxonomy

### 2-1 樣本空間與事件

| skill_id | section | proposed_problem_type | description | triage_class | checker_requirement | source_alignment | notes |
|---|---|---|---|---|---|---|---|
| `vh_數學B4_BasicConceptsOfSets` | 2-1 | `set_membership_judgement` | 判斷元素是否屬於集合、集合相等判斷、正確/錯誤敘述選擇 | B: deterministic_choice | `choice_answer` | textbook_example, basic_exercise | 選擇題；選項為集合敘述 |
| `vh_數學B4_BasicConceptsOfSets` | 2-1 | `subset_listing` | 列出所有子集合、真子集 | C: ai_judged_handwriting_free_response | `not_ready` | textbook_example | 答案為集合列舉，不適合 int-answer |
| `vh_數學B4_BasicConceptsOfSets` | 2-1 | `set_operation_count` | 計算聯集/交集/差集的元素個數（容斥原理數值題） | A: deterministic_numeric | `integer` / `set_count` | textbook_example, basic_exercise | 答案為整數個數 |
| `vh_數學B4_BasicConceptsOfSets` | 2-1 | `inclusion_exclusion_count` | 容斥原理計數（兩事件或三事件） | A: deterministic_numeric | `integer` | basic_exercise | 可與 set_operation_count 合併為同一 generator |
| `vh_數學B4_SampleSpaceAndEvents` | 2-1 | `sample_space_listing` | 完整列出樣本空間（擲幣、擲骰、抽籤等） | C: ai_judged_handwriting_free_response | `not_ready` | textbook_example, self_assessment | 不適合 int-answer |
| `vh_數學B4_SampleSpaceAndEvents` | 2-1 | `event_set_listing` | 列出事件子集合（A、B、A∩B、A∪B、A'） | C: ai_judged_handwriting_free_response | `not_ready` | textbook_example | 集合表示，不適合 int-answer |
| `vh_數學B4_SampleSpaceAndEvents` | 2-1 | `event_relation_judgement` | 判斷事件關係（互斥、包含、對立等），選擇題形式 | B: deterministic_choice | `choice_answer` | basic_exercise | 選項為文字敘述或集合表示 |
| `vh_數學B4_SampleSpaceAndEvents` | 2-1 | `sample_space_count_numeric` | 計算樣本空間元素個數 n(S)，答案唯一整數 | A: deterministic_numeric | `integer` | exam_practice | 適合 deterministic；ex: 擲兩骰 n(S)=36 |

### 2-2 機率的運算

| skill_id | section | proposed_problem_type | description | triage_class | checker_requirement | source_alignment | notes |
|---|---|---|---|---|---|---|---|
| `vh_數學B4_ProbabilityDefinition` | 2-2 | `classical_probability_fraction` | 古典機率：P(A)=n(A)/n(S)，答案為最簡分數 | A: deterministic_numeric | `rational` | textbook_example, in_class_practice | 需分數化簡政策 |
| `vh_數學B4_ProbabilityDefinition` | 2-2 | `sample_space_count_numeric` | 計算 n(S) 或 n(A)（純計數，無需求機率值） | A: deterministic_numeric | `integer` | textbook_example | 可共用 SampleSpace generator |
| `vh_數學B4_ProbabilityDefinition` | 2-2 | `dice_coin_probability_count` | 擲幣/擲骰情境下的古典機率（常見參數化情境） | A: deterministic_numeric | `rational` / `probability_range` | textbook_example, in_class_practice | image-related 題(2筆)需排除首批 |
| `vh_數學B4_ProbabilityProperties` | 2-2 | `complement_probability` | 補事件/餘事件：P(A')=1-P(A) | A: deterministic_numeric | `rational` / `decimal_tolerance` | textbook_example | 高優先，結構簡單 |
| `vh_數學B4_ProbabilityProperties` | 2-2 | `union_intersection_probability` | P(A∪B)=P(A)+P(B)-P(A∩B) | A: deterministic_numeric | `rational` | textbook_example, in_class_practice | 已知條件給 P(A)、P(B)、P(A∩B) |
| `vh_數學B4_ProbabilityProperties` | 2-2 | `set_probability_word_problem` | 文字描述集合關係後計算機率（含題幹事件映射） | A: deterministic_numeric | `rational` | basic_exercise | 注意題幹事件一致性 |
| `vh_數學B4_ConditionalProbability` | 2-2 | `conditional_probability_basic` | P(B|A)=P(A∩B)/P(A)，直接代入計算 | A: deterministic_numeric | `rational` | textbook_example, in_class_practice | 需條件事件一致性驗證 |
| `vh_數學B4_ConditionalProbability` | 2-2 | `without_replacement_conditional_probability` | 不放回抽樣條件機率（逐步縮小樣本空間） | A: deterministic_numeric | `rational` | textbook_example | 常見情境：袋中取球 |
| `vh_數學B4_IndependentEvents` | 2-2 | `independent_joint_probability` | 獨立事件乘法定理：P(A∩B)=P(A)×P(B) | A: deterministic_numeric | `rational` / `decimal_tolerance` | textbook_example, in_class_practice | 需驗證獨立性假設在題幹中明確給定 |
| `vh_數學B4_IndependentEvents` | 2-2 | `independent_at_least_one_probability` | 至少一次成功（補事件技巧）：1-(1-p)^n | A: deterministic_numeric | `rational` / `decimal_tolerance` | textbook_example | 常見情境：命中率、多次試驗 |
| `vh_數學B4_IndependentEvents` | 2-2 | `independent_event_judgement` | 判斷兩事件是否獨立（選擇題形式）或比較命中率 | B: deterministic_choice | `choice_answer` | in_class_practice | 表格題可能需 manual review |
| `vh_數學B4_ProbabilityOperations` | 2-2 | `probability_algebra_mixed` | 綜合機率運算（補事件 + 聯集 + 條件混合） | A: deterministic_numeric | `rational` | self_assessment (9筆全 needs_review) | 需人工確認題幹品質後才可進 deterministic |
| `vh_數學B4_ProbabilityOperations` | 2-2 | `event_operation_probability` | 事件集合運算後求機率（A∩B、A'∩B 等） | A: deterministic_numeric | `rational` | self_assessment | 同上，needs_review 全部 |

### 2-3 數學期望值

| skill_id | section | proposed_problem_type | description | triage_class | checker_requirement | source_alignment | notes |
|---|---|---|---|---|---|---|---|
| `vh_數學B4_MathematicalExpectationDefinition` | 2-3 | `expectation_discrete_basic` | 離散隨機變數期望值 E(X)=Σx·P(X=x) | A: deterministic_numeric | `expected_value` / `rational` | textbook_example, in_class_practice | 入門計算，結構規則 |
| `vh_數學B4_MathematicalExpectationDefinition` | 2-3 | `expectation_from_distribution` | 給定機率分佈表，計算 E(X) | A: deterministic_numeric | `expected_value` / `rational` | textbook_example, in_class_practice | 需確認分佈表格式可解析 |
| `vh_數學B4_ApplicationsOfExpectation` | 2-3 | `expectation_word_problem_profit_fairness` | 期望值應用：抽獎/保險/獲利/公平遊戲判斷 | A: deterministic_numeric (主體) + D: future_ai_judged (複雜情境) | `expected_value` / `rational` | textbook_example, in_class_practice | 情境長，解析風險高；複雜敘述先 D 類 |
| `vh_數學B4_MathematicalExpectation` | 2-3 | `expectation_assessment_numeric` | 期望值綜合計算（自評題集中，答案格式需統一） | A: deterministic_numeric | `expected_value` / `rational` / `decimal_tolerance` | self_assessment (5筆全 needs_review) | 需人工確認品質後才可進 deterministic |

---

## 5. Final Chap2 Problem Type Registry Draft

| proposed_problem_type | primary_skill_id | secondary_skill_ids | triage_class | checker_requirement | generator_priority | phase_recommendation | notes |
|---|---|---|---|---|---|---|---|
| `classical_probability_fraction` | `ProbabilityDefinition` | — | A | `rational`, `probability_range` | P0 | Phase 6C | 首批核心 |
| `complement_probability` | `ProbabilityProperties` | `ProbabilityDefinition` | A | `rational`, `decimal_tolerance` | P0 | Phase 6C | 結構簡單，高優先 |
| `union_intersection_probability` | `ProbabilityProperties` | — | A | `rational` | P0 | Phase 6C | P(A∪B) 公式 |
| `sample_space_count_numeric` | `SampleSpaceAndEvents` | `ProbabilityDefinition` | A | `integer` | P0 | Phase 6C | 純計數，整數答案 |
| `dice_coin_probability_count` | `ProbabilityDefinition` | — | A | `rational`, `probability_range` | P0 | Phase 6C | 排除 image-related 題 |
| `set_operation_count` | `BasicConceptsOfSets` | — | A | `integer`, `set_count` | P0 | Phase 6C | 容斥計數 |
| `inclusion_exclusion_count` | `BasicConceptsOfSets` | — | A | `integer` | P0 | Phase 6C | 可與 set_operation_count 合併 |
| `conditional_probability_basic` | `ConditionalProbability` | — | A | `rational` | P1 | Phase 6D | 需條件一致性驗證 |
| `without_replacement_conditional_probability` | `ConditionalProbability` | — | A | `rational` | P1 | Phase 6D | 不放回情境 |
| `independent_joint_probability` | `IndependentEvents` | — | A | `rational`, `decimal_tolerance` | P1 | Phase 6D | 獨立假設需題幹明確 |
| `independent_at_least_one_probability` | `IndependentEvents` | — | A | `rational`, `decimal_tolerance` | P1 | Phase 6D | 1-(1-p)^n |
| `set_probability_word_problem` | `ProbabilityProperties` | — | A | `rational` | P1 | Phase 6D | 題幹事件映射風險 |
| `expectation_discrete_basic` | `MathematicalExpectationDefinition` | — | A | `expected_value`, `rational` | P1 | Phase 6E | 入門計算 |
| `expectation_from_distribution` | `MathematicalExpectationDefinition` | — | A | `expected_value`, `rational` | P1 | Phase 6E | 分佈表格式需確認 |
| `expectation_word_problem_profit_fairness` | `ApplicationsOfExpectation` | — | A (簡單) / D (複雜) | `expected_value`, `rational` | P1 / HOLD | Phase 6E / 6F | 複雜情境先 HOLD |
| `probability_algebra_mixed` | `ProbabilityOperations` | — | A | `rational` | P1 | Phase 6E | 需人工確認 needs_review 題品質 |
| `expectation_assessment_numeric` | `MathematicalExpectation` | — | A | `expected_value`, `rational`, `decimal_tolerance` | P1 | Phase 6E | 需人工確認品質 |
| `event_operation_probability` | `ProbabilityOperations` | — | A | `rational` | P1 | Phase 6E | 同上 |
| `set_membership_judgement` | `BasicConceptsOfSets` | — | B | `choice_answer` | P1 | Phase 6D | 選擇題形式 |
| `event_relation_judgement` | `SampleSpaceAndEvents` | — | B | `choice_answer` | P1 | Phase 6D | 事件關係判斷 |
| `independent_event_judgement` | `IndependentEvents` | — | B | `choice_answer` | P1 | Phase 6D | 表格題部分需 D 類 |
| `sample_space_listing` | `SampleSpaceAndEvents` | — | C | `not_ready` | P2 | Phase 6F | 不進 deterministic allowlist |
| `event_set_listing` | `SampleSpaceAndEvents` | `BasicConceptsOfSets` | C | `not_ready` | P2 | Phase 6F | 不進 deterministic allowlist |
| `subset_listing` | `BasicConceptsOfSets` | — | C | `not_ready` | P2 | Phase 6F | 不進 deterministic allowlist |

---

## 6. Handwriting / Free-response Reserved Types

以下題型**不得加入 deterministic allowlist**：

| problem_type | skill_id | 原因 | scoring_policy |
|---|---|---|---|
| `sample_space_listing` | `SampleSpaceAndEvents` | 答案為集合列舉，非單一整數；樣本空間可能含數十個元素 | `deferred_teacher_review` / visibility-only |
| `event_set_listing` | `SampleSpaceAndEvents`, `BasicConceptsOfSets` | 答案為事件子集合集合表示（如 A={HH, HT}），非整數 | `deferred_teacher_review` / visibility-only |
| `subset_listing` | `BasicConceptsOfSets` | 子集合列舉，答案為集合之集合，非整數 | `deferred_teacher_review` / visibility-only |

政策聲明：
- 上述題型不加入 `b4_chapter1_deterministic_allowlist.py` 或任何未來的 Chap2 deterministic allowlist
- 不更新 mastery / APR / fail_streak / remediation
- 只能做 `visibility-only` / `deferred_teacher_review`
- 除非未來另開 phase 並人工 approve handwriting AI-judged 流程（參照 TreeDiagram / Pascal SOP）

---

## 7. Deterministic Candidate Freeze

### Phase 6C Candidates（首批，高優先）

| problem_type | skill | checker | 特點 |
|---|---|---|---|
| `classical_probability_fraction` | ProbabilityDefinition | rational | 古典機率核心 |
| `complement_probability` | ProbabilityProperties | rational | 結構簡單，1-P(A) |
| `union_intersection_probability` | ProbabilityProperties | rational | 加法定理 |
| `sample_space_count_numeric` | SampleSpaceAndEvents, ProbabilityDefinition | integer | 純整數計數 |
| `dice_coin_probability_count` | ProbabilityDefinition | rational, probability_range | 排除 image-related 2 筆 |
| `set_operation_count` + `inclusion_exclusion_count` | BasicConceptsOfSets | integer, set_count | 容斥計數，可合一 generator |

### Phase 6D Candidates

| problem_type | skill | checker |
|---|---|---|
| `conditional_probability_basic` | ConditionalProbability | rational |
| `without_replacement_conditional_probability` | ConditionalProbability | rational |
| `independent_joint_probability` | IndependentEvents | rational, decimal_tolerance |
| `independent_at_least_one_probability` | IndependentEvents | rational, decimal_tolerance |
| `set_membership_judgement` | BasicConceptsOfSets | choice_answer |
| `event_relation_judgement` | SampleSpaceAndEvents | choice_answer |
| `independent_event_judgement` | IndependentEvents | choice_answer |
| `set_probability_word_problem` | ProbabilityProperties | rational |

### Phase 6E Candidates

| problem_type | skill | checker | 前置條件 |
|---|---|---|---|
| `expectation_discrete_basic` | MathematicalExpectationDefinition | expected_value, rational | 需 expected_value checker |
| `expectation_from_distribution` | MathematicalExpectationDefinition | expected_value, rational | 分佈表格式須確認 |
| `expectation_word_problem_profit_fairness` | ApplicationsOfExpectation | expected_value, rational | 先限縮簡單情境 |
| `probability_algebra_mixed` | ProbabilityOperations | rational | 需人工確認 needs_review 品質 |
| `expectation_assessment_numeric` | MathematicalExpectation | expected_value, rational, decimal_tolerance | 需人工確認品質 |
| `event_operation_probability` | ProbabilityOperations | rational | 同上 |

---

## 8. Risks and Open Questions

| # | 風險 / Open Question | 說明 | 建議處置 |
|---|---|---|---|
| R1 | display_order tie | 20001 有 4 筆、20002 有 4 筆；非唯一 | 需以 section 字母序 + skill_id 做 tie-break，確認 DB-first 規則 |
| R2 | source_chapter 異常 | `BasicConceptsOfSets` 有 1 筆 `source_chapter='3 統計'` | 建議人工確認是否誤掛；先保留，首批 generator 排除此筆 |
| R3 | needs_review 全為 87 | 整章 87 題全部 `needs_review=true`，代表尚無任何人工確認 | 首批 deterministic 應優先選 needs_review 風險較低的 textbook_example + in_class_practice |
| R4 | image-related 題 | `ProbabilityDefinition` 有 2 筆（has_image/needs_image_review）| 明確排除於 Phase 6C 首批；未來另處理 |
| R5 | 答案格式不一致 | 分數/小數/百分比混用；期望值可能為分數或有限小數 | Phase 6B 需定義 checker contract（rational / decimal_tolerance / percentage 統一政策）|
| R6 | 分數化簡政策 | 古典機率答案是否要求最簡分數？ | 建議：要求最簡分數，checker 比較化簡後的值 |
| R7 | 條件機率一致性 | 條件描述與答案事件可能錯配 | Phase 6D 前需設計條件一致性 validator |
| R8 | 期望值應用題情境複雜 | `ApplicationsOfExpectation` 文字長；OCR / 公式解析不穩定 | 先限縮「單一期望值計算」情境；複雜情境標 D 類（future_ai_judged）|
| R9 | ProbabilityOperations / MathematicalExpectation 全 needs_review | 9+5 筆自評題無任何確認 | Phase 6E 前需人工批次確認至少部分題目品質 |
| R10 | checker 等值接受範圍 | 答案 1/2、0.5、50% 是否視為等值？ | Phase 6B 需定義 normalization 政策 |
| R11 | `multiplication_principle` 標籤 | 僅 1 筆，出現在 SampleSpaceAndEvents；描述解法策略非題型語意 | 廢棄；該題重分類為 `sample_space_count_numeric` |

---

## 9. Recommended Next Phase

### Phase 6B：probability domain functions / validators planning（本輪不執行）

Phase 6B scope（規劃文件只，不改 runtime code）：

- probability answer checker contract 定義
- `rational` checker：分子/分母格式、化簡政策
- `decimal_tolerance` checker：容差範圍（建議 ±0.001）
- `percentage` checker：百分比輸入正規化（60% → 0.6）
- `expected_value` checker contract：可接受分數 / 有限小數；需 domain 範圍驗證
- `probability_range` validator：確保 0 ≤ P ≤ 1
- `set_count` checker：非負整數
- fraction simplification policy（最簡分數要求）
- ⚠️ 本 phase 不實作 generator；不改 `b4_validators.py`；只產出規劃文件

預期 report：`reports/b4_generator_planning/b4_phase6b_probability_validator_plan.md`

---

## 10. Final Confirmation

| 項目 | 狀態 |
|---|---|
| 是否只新增 / 更新 taxonomy report | ✅ 是 |
| 是否修改 production code | ✅ 否 |
| 是否修改 tests | ✅ 否 |
| 是否修改 routes | ✅ 否 |
| 是否修改 templates | ✅ 否 |
| 是否修改 generators | ✅ 否 |
| 是否修改 database | ✅ 否 |
| 是否修改 coverage matrix | ✅ 否 |
| 是否新增 allowlist | ✅ 否 |
| 是否修改 adaptive scoring / mastery / APR / remediation | ✅ 否 |
| 是否啟動 Phase 6B / 6C | ✅ 否 |

---

*Phase 6A taxonomy freeze 完成。停在此處，等待人工 approve。*  
*狀態：READY_FOR_REVIEW*
