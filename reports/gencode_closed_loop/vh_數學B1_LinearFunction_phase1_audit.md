# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B1_LinearFunction
- 階段狀態: AUDIT_PASS
- 建議下一步: phase2_build
- 題庫例題總數: 17
- 已分類例題數: 17
- 來源覆蓋判定: FULL_OBSERVED_COVERAGE_CANDIDATE

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |
| integer_numeric_evaluate_function_notation | deterministic_expression | 4424, 4425, 4426, 4430, 4431, 4433, 4434, 4441, 4442, 4444, 4445, 4446, 4448, 4449, 4500, 4515, 4516 | integer | numeric_exact | integer_checker | classified |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 4424 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 右圖為函數$y=f\left( x \right)=ax+b$的圖形。 (1) 試求直線的x截距與y截距。 (2) 試求$f\left( x \right)$。 |
| 4425 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 右圖是某電信公司的通話費計算方式：300秒以內只繳基本費，超過300秒之後的費用，與通話時間成線型函數關係，試問： (1) 手機基本費用為多少元？ (2) 本月小郁使用手機通話1500秒，需繳交多少元？ |
| 4426 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 設直角坐標平面上四點$A\left( -2,1 \right)$、$B\left( {{b}_{1}},{{b}_{2}} \right)$、$C\left( {{c}_{1}},{{c}_{2}} \right)... |
| 4430 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 伽利略（Galileo，1564−1642）研究自由落體運動發現自由落體公式：$S\left( t \right)=\frac{1}{2}g{{t}^{2}}$，$g=9.8$（公尺/秒2）為已知常數，當物體在空中... |
| 4431 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 英國科學家虎克（Robert Hooke，1635−1703）於1678年發現虎克定律：$F\left( x \right)=kx$，k為力常數，即在彈性限度內，彈簧所受的外力F與伸長量x有成正比的關係，所以外力F... |
| 4433 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 試在坐標平面上畫出$y=f\left( x \right)=-2$的圖形。 |
| 4434 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 試在坐標平面上畫出函數$y=f\left( x \right)=3x-6$的圖形。 |
| 4441 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 右圖為函數$y=f\left( x \right)=ax+b$的圖形。 (1) 試求直線的x截距與y截距。 (2) 試求$f\left( x \right)$。 |
| 4442 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 高老師搭乘某廉價航空，他的行李托運費用是850元，若行李托運費用與重量是成線型函數的關係，如圖所示，試求高老師托運的行李幾公斤？ |
| 4444 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 下圖為函數$y=f\left( x \right)=ax+b$的圖形。 (1)試求直線的x截距與y截距。 (2)試求$f\left( x \right)$。 |
| 4445 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 已知手機費包含月租基本費與超時通話費，某電信公司的手機月租基本費為m元，可以免費通話30分鐘。若通話時間超過30分鐘後，通話費與時間（分鐘）為線型函數的關係如圖所示。試問： (1)手機每個月基本費用m為多少元？ (... |
| 4446 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 公司給小虹最多50萬元的預算來採買$x$、$y$兩種貨品。但小虹一時疏忽，無法確定$x$貨品跟$y$貨品的單價哪一個是100元、哪一個是200元。下列數對($x$貨品購買數量 , $y$貨品購買數量)中，試問哪一組... |
| 4448 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 試在坐標平面上畫出$y=f\left( x \right)=3$的圖形。 |
| 4449 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 試在坐標平面上畫出函數$y=f\left( x \right)=-2x+4$的圖形。 |
| 4500 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 阿偉的汽車加滿油後開始行駛，其行駛距離x公里與剩餘油量y公升的關係為線型函數，其圖形如右圖所示，則x與y的關係式為 |
| 4515 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 設$f\left( x \right)=ax+b$為一線型函數，且圖形通過點$\left( -2,4 \right)$、$\left( 1,1 \right)$，則$f\left( x \right)=$ (A) ... |
| 4516 | integer_numeric_evaluate_function_notation | deterministic_expression | high |  | 利用截距定義，試問下列何者不可能是函數$y=f\left( x \right)=ax-3$的圖形？ |

## 4. 答案規格檢查
- 缺少 answer_contract 的題型: 無
- 缺少 checker_key 的題型: 無
- 需要等價答案測試的題型: 無

## 5. 人工審查與風險標記
- manual_review_problem_types: 無
- risk_flags: 無

## 6. Classifier Proposal 狀態
- classifier_proposal.enabled: False
- proposal_status: SKIPPED
- reason: 
- proposal_path: D:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_LinearFunction_classifier_proposal.json
- promote_ready: False
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_LinearFunction

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
python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B1_LinearFunction
