# B4 StatisticalChartReading Runtime Fidelity Repair Summary

## 1. 問題描述
`vh_數學B4_StatisticalChartReading` 修補前偏向 open-ended review，deterministic 可自動判分題不足；部分樣本曾出現「題幹提到附圖但 payload 缺圖」與 scenario 重複偏高問題。

## 2. Root Cause
1. Router 對 deterministic chart-reading 題型映射不足。
2. Generator 缺少穩定的 deterministic choice problem_type。
3. Review payload 的 visual/rubric 合約在部分樣本不完整。

## 3. 修正後 deterministic_choice problem_type
1. `chart_type_by_purpose`
2. `chart_interpretation_caution`
3. `chart_match_data_type`

這三類題型皆採 deterministic choice 路徑，提供可自動判分的選擇題練習。

## 4. review 題型條件
保留 `statistical_chart_reading_visibility_review`，並要求：
- payload 含 `visual_aids` 或 `chart_spec`
- 提供 `rubric`（或等價 review schema）
- `visual_backed=true`
- `check_mode=review_mode`

## 5. 是否已避免「附圖但無圖」
是。對應題型要求至少一種可視素材欄位（`visual_aids` / `chart_spec` / visual metadata），避免題幹與 payload 不一致。

## 6. 是否可產生不同 scenario / pattern
是。deterministic choice 三類 problem_type 具備多 scenario 與 pattern 變化，降低固定單題幹重播風險。

## 7. check_answer 是否正答判對 / 錯答判錯
是。deterministic choice 題型走 `deterministic_auto_checked`，正答判對、錯答判錯；review 題型維持 review guard，不走 deterministic 比對。

## 8. 修改檔案
1. `core/vocational_math_b4/generators/chap3_statistical_measures.py`
2. `core/vocational_math_b4/services/question_router.py`
3. `core/vocational_math_b4/adaptive/b4_chapter3_phase7b_allowlist.py`
4. `tests/test_b4_statistical_chart_reading_runtime_fidelity_repair.py`

## 9. 新增 tests
1. `tests/test_b4_statistical_chart_reading_runtime_fidelity_repair.py`

## 10. 測試結果
- `pytest -q tests/test_b4_statistical_chart_reading_runtime_fidelity_repair.py`：passed
- `pytest -q tests/test_b4_choice_payload_rendering_repair.py`：passed
- `pytest -q tests/test_b4_3_2_review_payload_repair.py`：passed
- `pytest -q tests/test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py`：passed
- `pytest -q tests/test_b4_final_mode_aware_runtime_coverage_recount.py`：passed
- `pytest -q tests/test_b4_data_organization_and_charts_runtime_fidelity_repair.py`：passed

## 11. 是否影響 B4 final coverage count
不影響。Final coverage recount 維持既有結果，`unknown_or_no_runtime_count = 0`。

## 12. Final Status
`READY_FOR_RECHECK`
