# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B1_SlopeOfALine
- 階段狀態: AUDIT_PASS
- 建議下一步: phase2_build
- 題庫例題總數: 12
- 已分類例題數: 12
- 來源覆蓋判定: FULL_OBSERVED_COVERAGE_CANDIDATE

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |
| text_short_slope_of_line_problems | deterministic_expression | 4519, 4520, 4521, 4522, 4523, 4524, 4525, 4529, 4533, 4534, 4590, 4601 | rational | rational_equivalent | rational_checker | classified |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 4519 | text_short_slope_of_line_problems | deterministic_expression | high |  | 設、、$C\left( 5,2 \right)$、$D\left( 3,4 \right)$，試求下列直線的斜率並在坐標平面上畫出圖形。 (1)直線AB (2)直線BC (3)直線AC (4)直線BD。 |
| 4520 | text_short_slope_of_line_problems | deterministic_expression | high |  | (1) 請將m = 0、m不存在、m > 0、m < 0，填入下列各圖形的斜率。 ①②③④ (2) 設${{m}_{1}}$、${{m}_{2}}$分別為直線${{L}_{1}}$、${{L}_{2}}$的斜率，試... |
| 4521 | text_short_slope_of_line_problems | deterministic_expression | high |  | 試求過下列各組A、B兩點的直線斜率： (1)$A\left( 5,-2 \right)$、$B\left( -7,4 \right)$ (2)$A\left( 3,1 \right)$、$B\left( 3,5 \... |
| 4522 | text_short_slope_of_line_problems | deterministic_expression | high |  | 若直線通過點$\left( 2,a \right)$與$\left( 1-a,5 \right)$，且其斜率為2，試求a之值。 |
| 4523 | text_short_slope_of_line_problems | deterministic_expression | high |  | 若$A\left( -1,-1 \right)$、$B\left( 2,k \right)$、$C\left( 8,5 \right)$三點共線，試求k之值。 |
| 4524 | text_short_slope_of_line_problems | deterministic_expression | high |  | 在坐標平面上，設k為實數，若$P\left( 2,3 \right)$、$Q\left( 4,-5 \right)$、$R\left( k,-3 \right)$三點無法連結成一個三角形，試求k之值。 |
| 4525 | text_short_slope_of_line_problems | deterministic_expression | high |  | (1) 設$A\left( -3,4 \right)$、$B\left( a,1 \right)$、$C\left( -4,-2 \right)$、$D\left( 2,8 \right)$，若$\overline... |
| 4529 | text_short_slope_of_line_problems | deterministic_expression | high |  | 若$A\left( -2,0 \right)$、$B\left( -1,1 \right)$、$C\left( k,4 \right)$三點在同一直線上，試求k之值。 |
| 4533 | text_short_slope_of_line_problems | deterministic_expression | high |  | 如圖所示$A\left( -1,4 \right)$、$B\left( 2,-1 \right)$、 $$、$D\left( -3,-1 \right)$、$P\left( 2,2 \right)$， 試求下列直線... |
| 4534 | text_short_slope_of_line_problems | deterministic_expression | high |  | 若$A\left( -3,k \right)$、$$、$C\left( 3,-2 \right)$三點無法連結成一個三角形，試求k之值。 |
| 4590 | text_short_slope_of_line_problems | deterministic_expression | high |  | 在坐標平面上，若直線L通過兩點$A\left( 2,a \right)$、$B\left( a,8 \right)$，且直線L的斜率為2，則a = (A) −2 (B) 1 (C) 2 (D) 4。 |
| 4601 | text_short_slope_of_line_problems | deterministic_expression | high |  | 設$P\left( 4,2 \right)$、$Q\left( 0,a \right)$、$B\left( -1,0 \right)R\left( 8,-2 \right)$為共線之三點，則a = (A) 5 (B... |

## 4. 答案規格檢查
- 缺少 answer_contract 的題型: 無
- 缺少 checker_key 的題型: 無
- 需要等價答案測試的題型: text_short_slope_of_line_problems

## 5. 人工審查與風險標記
- manual_review_problem_types: 無
- risk_flags: 無

## 6. Classifier Proposal 狀態
- classifier_proposal.enabled: False
- proposal_status: SKIPPED
- reason: 
- proposal_path: E:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_SlopeOfALine_classifier_proposal.json
- promote_ready: False
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_SlopeOfALine

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
python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B1_SlopeOfALine
