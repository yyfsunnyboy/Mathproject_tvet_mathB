# Gencode 第三階段發布門檻報告

## 1. 摘要
- skill_id: vh_數學B1_MidpointCoordinates
- final_status: PUBLISH_BINDING_REQUIRED
- publish_ready: false

## 2. 整體判讀
- 狀態說明: candidate 驗證、binding 與 runtime coverage 綜合判讀結果。
- 是否可發布: 否
- 是否可進學生端 runtime: 否
- 是否需要人工處理: 否

## 3. 成功項目
- Phase 1 例題盤點: 完成
- Phase 2 candidate verification: 完成
- verified problem types: compute_centroid_coordinates, compute_midpoint_coordinates

## 4. 未完成 / 失敗項目
- registry binding: 未完成
- wrapper binding: 未完成
- runtime coverage: 通過
- missing runtime problem types: -
- blocking reasons: phase3_package_summary_stale_vs_phase2_generator_summary, registry_binding_missing, runtime_binding_missing, wrapper_binding_missing

## 5. 發布排除題型
- manual_review problem types: -
  說明：manual_review 題型不應列入 deterministic runtime coverage。
- future_ai_judged problem types: -

## 6. Runtime Coverage
- expected_problem_types: compute_centroid_coordinates, compute_midpoint_coordinates
- observed_problem_types: compute_centroid_coordinates, compute_midpoint_coordinates
- missing_problem_types: -
- coverage_status: pass

## 7. Registry / Wrapper / Runtime Binding 狀態
- registry_binding_status: NOT_BOUND
- wrapper_binding_status: NOT_BOUND
- runtime_binding_status: NOT_READY

## 8. 阻塞原因與說明
- phase3_package_summary_stale_vs_phase2_generator_summary: Phase 3 summary 早於 Phase 2 generator summary，需重跑 packaging
- registry_binding_missing: candidate 尚未 non-destructive merge 到 registry
- runtime_binding_missing: 學生 runtime 尚未能抽到 verified problem types
- wrapper_binding_missing: skill wrapper 尚未接上 verified candidates

## 9. 下一步建議
- next_action_type: repair_publish_binding
- command: python scripts\gencode_repair_build_gap.py --skill-id vh_數學B1_MidpointCoordinates --gap missing_runtime_binding
- reason: candidate 已驗證，但 registry / wrapper / runtime 尚未接線。
- should_publish: false
- requires_human_review: false
