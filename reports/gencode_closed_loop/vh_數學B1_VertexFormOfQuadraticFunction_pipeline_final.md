# Gencode 第三階段發布門檻報告

## 1. 摘要
- skill_id: vh_數學B1_VertexFormOfQuadraticFunction
- final_status: FAIL
- publish_ready: false

## 2. 整體判讀
- 狀態說明: 
- 是否可發布: 否
- 是否可進學生端 runtime: 否
- 是否需要人工處理: 是

## 3. 成功項目
- Phase 1 例題盤點: 未完成
- Phase 2 candidate verification: 未完成
- verified problem types: -

## 4. 未完成 / 失敗項目
- registry binding: 未完成
- wrapper binding: 未完成
- runtime coverage: 未通過
- missing runtime problem types: -
- blocking reasons: missing_phase_reports

## 5. 發布排除題型
- manual_review problem types: -
  說明：manual_review 題型不應列入 deterministic runtime coverage。
- future_ai_judged problem types: -

## 6. Runtime Coverage
- expected_problem_types: -
- observed_problem_types: -
- missing_problem_types: -
- coverage_status: 

## 7. Registry / Wrapper / Runtime Binding 狀態
- registry_binding_status: UNKNOWN
- wrapper_binding_status: UNKNOWN
- runtime_binding_status: UNKNOWN

## 8. 阻塞原因與說明
- missing_phase_reports: 缺少 Phase 1/Phase 2 報告

## 9. 下一步建議
- next_action_type: rerun_or_fix_phase2
- command: python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B1_VertexFormOfQuadraticFunction
- reason: Phase 報告不足，請先完成 Phase 1/2。
- should_publish: false
- requires_human_review: true
