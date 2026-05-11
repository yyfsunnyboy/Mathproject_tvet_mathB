# B4 Full Skill Runtime Coverage Audit + Graph Closure (Small Repair v2)

## Repair Scope
- 本次僅修正 audit report 的分類一致性與技能歸類。
- 未修改 production code、未新增 runtime family、未修改 router/generator/tests。

## Primary/Secondary Classification Rule
1. **Primary runtime status（互斥）**
   - `RUNTIME_RELEASED`
   - `PARTIAL_RUNTIME`
   - `NO_RUNTIME_GENERATOR`
2. **Secondary reason tags（可重疊）**
   - `blocked_by_fidelity`
   - `future_ai_checked`
   - `teacher_review`
   - `visibility_only`
   - `handwriting_candidate`

---

## Count Summary (Mutually Exclusive)

| metric | count |
|---|---:|
| total_b4_skills | 40 |
| RUNTIME_RELEASED | 28 |
| PARTIAL_RUNTIME | 1 |
| NO_RUNTIME_GENERATOR | 11 |
| sum_status_counts | 40 |

Check: `RUNTIME_RELEASED + PARTIAL_RUNTIME + NO_RUNTIME_GENERATOR = 40` -> **True**

## Secondary Reason Tag Counts (May Overlap)

| secondary_reason_tag | count |
|---|---:|
| blocked_by_fidelity | 3 |
| future_ai_checked | 3 |
| teacher_review | 4 |
| visibility_only | 2 |
| handwriting_candidate | 2 |

> 註：secondary tags 可重疊，不可與 primary counts 直接相加。

---

## Repair Decisions Applied

### 1) `vh_數學B4_HistogramsAndFrequencyPolygons`
- 已確認 Graph-3 released `histogram_reading`。
- 主要狀態改為 `PARTIAL_RUNTIME`（保留）。
- 從 `no_runtime_generator_skills` 清單移除（已移除）。
- `released_family_or_problem_type`: `histogram_reading`
- `secondary_reason_tags`: `blocked_by_fidelity, handwriting_candidate`（frequency_polygon_reading 仍受 Graph-4 fidelity gate BLOCKED）

### 2) `vh_數學B4_ProbabilityBasicConcepts` 查證
- 在以下來源查無此 `skill_id` 實體：
  - `core/vocational_math_b4/**`
  - `tests/test_b4_*.py`
  - `reports/b4_generator_planning/*.md`
  - `reports/b4_generator_planning/b4_skill_source_summary.csv`
- Chap2 使用的是拆分後技能（如 `vh_數學B4_ProbabilityDefinition`、`vh_數學B4_ProbabilityOperations`、`vh_數學B4_ConditionalProbability` 等），並已有 released runtime coverage。
- 結論：`vh_數學B4_ProbabilityBasicConcepts` **不在本次 40-skill canonical 清單中**，不列入 `NO_RUNTIME_GENERATOR`。

---

## PARTIAL_RUNTIME Skill List

| skill_id | released_family_or_problem_type | secondary_reason_tags | notes |
|---|---|---|---|
| vh_數學B4_HistogramsAndFrequencyPolygons | histogram_reading | blocked_by_fidelity,handwriting_candidate | Graph-3 released；Graph-4 frequency_polygon_reading blocked by textbook fidelity gate |

---

## no_runtime_generator_skills List (Must Equal NO_RUNTIME_GENERATOR Count)

| skill_id | primary_runtime_status | secondary_reason_tags | recommended_future_path |
|---|---|---|---|
| vh_數學B4_TreeDiagramCounting | NO_RUNTIME_GENERATOR | future_ai_checked,handwriting_candidate | visual_or_handwriting_ai_checked |
| vh_數學B4_PascalTriangle | NO_RUNTIME_GENERATOR | future_ai_checked,handwriting_candidate | visual_or_handwriting_ai_checked |
| vh_數學B4_SamplingMethods | NO_RUNTIME_GENERATOR | teacher_review | teacher_review |
| vh_數學B4_SamplingSurvey | NO_RUNTIME_GENERATOR | teacher_review | teacher_review |
| vh_數學B4_StatisticalBasicConcepts | NO_RUNTIME_GENERATOR | visibility_only | visibility_only |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | NO_RUNTIME_GENERATOR | blocked_by_fidelity,future_ai_checked | keep_blocked_until_textbook_aligned_source_found |
| vh_數學B4_DataOrganizationAndCharts | NO_RUNTIME_GENERATOR | teacher_review | teacher_review |
| vh_數學B4_FrequencyDistributionTableConstruction | NO_RUNTIME_GENERATOR | future_ai_checked | future_ai_checked |
| vh_數學B4_StatisticalChartReading | NO_RUNTIME_GENERATOR | blocked_by_fidelity,teacher_review | keep_blocked_until_textbook_aligned_source_found |
| vh_數學B4_NormalDistributionAndEmpiricalRule | NO_RUNTIME_GENERATOR | teacher_review | teacher_review |
| vh_數學B4_OpinionPollInterpretation | NO_RUNTIME_GENERATOR | visibility_only | visibility_only |

Count check:
- `no_runtime_generator_skills = 11`
- 與 `NO_RUNTIME_GENERATOR count = 11` 一致。
- `PARTIAL_RUNTIME` skill 未出現在本清單中（已確認）。

---

## Full B4 Skill Coverage Table (Primary/Secondary Schema)

> 本次 small repair 僅修正衝突列與計數邏輯；其餘 skill 列維持前版 audit 結論。  
> 欄位 schema 統一為：`primary_runtime_status`、`secondary_reason_tags`、`released_family_or_problem_type`、`evidence_source`、`notes`。

關鍵修正列：

| skill_id | primary_runtime_status | secondary_reason_tags | released_family_or_problem_type | evidence_source | notes |
|---|---|---|---|---|---|
| vh_數學B4_HistogramsAndFrequencyPolygons | PARTIAL_RUNTIME | blocked_by_fidelity,handwriting_candidate | histogram_reading | Graph-3/Graph-4 reports + tests | histogram released; frequency_polygon blocked |
| vh_數學B4_ProbabilityBasicConcepts | N/A (not in canonical 40 skills) | N/A | N/A | core/tests/reports/skill_source_summary lookup | treated as non-canonical alias; Chap2 coverage exists on split skills |

---

## Graph Closure Decision
1. Chap3 visual/table deterministic short-answer path：**建議暫時 closure**  
2. **不建議硬挖 Graph-6**  
3. 未放行技能改走：
   - `future_ai_checked`
   - `teacher_review`
   - `visibility_only`
   - 或另開 AI-judged/handwriting phase

## Next Phase Recommendation (No Implementation This Round)
1. `B4-AI-Checked-1`
2. `B4-Chap3-TeacherReview-1`
3. `B4-Fullbook-Runtime-Index`

