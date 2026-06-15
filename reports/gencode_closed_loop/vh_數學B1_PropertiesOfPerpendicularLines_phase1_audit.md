# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B1_PropertiesOfPerpendicularLines
- 階段狀態: AUDIT_PASS
- 建議下一步: phase2_build
- 題庫例題總數: 8
- 已分類例題數: 8
- 來源覆蓋判定: FULL_OBSERVED_COVERAGE_CANDIDATE

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |
| perpendicular_lines_properties | deterministic_expression | 4526, 4527, 4531, 4532, 4536, 4537, 4538, 4539 | rational | rational_equivalent | rational_checker | classified |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 4526 | perpendicular_lines_properties | deterministic_expression | high |  | 已知直線${{L}_{1}}$的斜率為$-\frac{2}{3}$，試問： (1) 若直線${{L}_{2}}$平行${{L}_{1}}$，試求${{L}_{2}}$的斜率。 (2) 若直線${{L}_{3}}$垂... |
| 4527 | perpendicular_lines_properties | deterministic_expression | high |  | 已知坐標平面上三點$A\left( 2,1 \right)$、$B\left( 1,3 \right)$及$C\left( 4,2 \right)$，試問△ABC是否為直角三角形？. |
| 4531 | perpendicular_lines_properties | deterministic_expression | high |  | 設$A\left( -2,a \right)$、$B\left( 3,4 \right)$、$C\left( -2,8 \right)$、$D\left( 4,-2 \right)$，若$\overline{AB}... |
| 4532 | perpendicular_lines_properties | deterministic_expression | high |  | 已知直線${{L}_{1}}$的斜率為$\frac{3}{2}$，試問： (1)若直線${{L}_{2}}$平行${{L}_{1}}$，試求${{L}_{2}}$的斜率。 (2)若直線${{L}_{3}}$垂直${... |
| 4536 | perpendicular_lines_properties | deterministic_expression | high |  | 設$A\left( -3,4 \right)$、$B\left( a,1 \right)$、$C\left( -4,-2 \right)$、$D\left( 2,8 \right)$，若$\overline{AB}... |
| 4537 | perpendicular_lines_properties | deterministic_expression | high |  | 設直線${{L}_{1}}$通過$A\left( 3,k+1 \right)$、$B\left( -k,5 \right)$兩點，直線${{L}_{2}}$通過$C\left( 4,-3 \right)$、$D\l... |
| 4538 | perpendicular_lines_properties | deterministic_expression | high |  | 已知${{m}_{1}}$與${{m}_{2}}$分別為直線${{L}_{1}}$與直線${{L}_{2}}$的斜率，且${{m}_{1}}$、${{m}_{2}}$皆不為0。若直線${{L}_{1}}$通過第一、... |
| 4539 | perpendicular_lines_properties | deterministic_expression | high |  | 已知直線${{L}_{1}}$的斜率為$-\frac{1}{2}$，試問： (1) 若直線${{L}_{2}}$平行${{L}_{1}}$，試求${{L}_{2}}$的斜率。 (2) 若直線${{L}_{3}}$垂... |

## 4. 答案規格檢查
- 缺少 answer_contract 的題型: 無
- 缺少 checker_key 的題型: 無
- 需要等價答案測試的題型: perpendicular_lines_properties

## 5. 人工審查與風險標記
- manual_review_problem_types: 無
- risk_flags: 無

## 6. Classifier Proposal 狀態
- classifier_proposal.enabled: False
- proposal_status: SKIPPED
- reason: 
- proposal_path: D:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_PropertiesOfPerpendicularLines_classifier_proposal.json
- promote_ready: False
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_PropertiesOfPerpendicularLines

## 7. Auto Review Summary
- proposal_count: 0
- unknown_examples_total: 0
- auto_approve_safe_eligible: False
- split_or_merge_recommendation: 
- classifier_gate: {}
- generator_draft_gate: {}
- runtime_ready_gate: {}
- per_candidate_promote_gate: []
- next_action: 

## 8. 下一步建議
python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B1_PropertiesOfPerpendicularLines
