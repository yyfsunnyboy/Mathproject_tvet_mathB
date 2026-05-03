# B4 Phase 4D Runtime Wrapper / Router 成果凍結報告

## 1. 本階段目的
本階段目的為凍結 B4 Chapter 1 最小可用 runtime 成果。本階段不新增 generator，不新增 wrapper，不修改 route，亦不修改 frontend，僅整理目前已完成之 wrapper、router 與 web smoke test 成果。

## 2. 已完成 runtime 架構
前端 / route 傳入 skill_id
→ skills/{skill_id}.py wrapper
→ core/vocational_math_b4/services/question_router.py
→ core/vocational_math_b4/generators/*.py
→ core/vocational_math_b4/domain/*.py
→ 回傳舊 runtime 可接受 payload

## 3. 已完成 wrapper 清單

| skill_id | wrapper 檔案 | 可用 problem_type_id | generator_key | 測試狀態 |
|---|---|---|---|---|
| vh_數學B4_CombinationDefinition | skills/vh_數學B4_CombinationDefinition.py | combination_definition_basic | b4.combination.combination_definition_basic | 通過 |
| vh_數學B4_CombinationApplications | skills/vh_數學B4_CombinationApplications.py | combination_polygon_count<br>combination_required_excluded_person | b4.combination.combination_polygon_count<br>b4.combination.combination_required_excluded_person | 通過 |
| vh_數學B4_MultiplicationPrinciple | skills/vh_數學B4_MultiplicationPrinciple.py | divisor_count_prime_factorization | b4.counting.divisor_count_prime_factorization | 通過 |
| vh_數學B4_PermutationOfDistinctObjects | skills/vh_數學B4_PermutationOfDistinctObjects.py | permutation_role_assignment | b4.permutation.permutation_role_assignment | 通過 |
| vh_數學B4_RepeatedPermutation | skills/vh_數學B4_RepeatedPermutation.py | repeated_permutation_digits | b4.counting.repeated_permutation_digits | 通過 |

## 4. 已接入 generator 清單

| generator_key | problem_type_id | module | 對應 skill_id | 功能說明 |
|---|---|---|---|---|
| b4.combination.combination_definition_basic | combination_definition_basic | core.vocational_math_b4.generators.combination | vh_數學B4_CombinationDefinition | 組合定義基本計算 |
| b4.combination.combination_polygon_count | combination_polygon_count | core.vocational_math_b4.generators.combination | vh_數學B4_CombinationApplications | 多邊形對角線與三角形 / 正多邊形對角線與三角形計數 |
| b4.combination.combination_required_excluded_person | combination_required_excluded_person | core.vocational_math_b4.generators.combination | vh_數學B4_CombinationApplications | 指定人物必選或不可選 |
| b4.counting.divisor_count_prime_factorization | divisor_count_prime_factorization | core.vocational_math_b4.generators.counting | vh_數學B4_MultiplicationPrinciple | 正因數個數計算 |
| b4.permutation.permutation_role_assignment | permutation_role_assignment | core.vocational_math_b4.generators.permutation | vh_數學B4_PermutationOfDistinctObjects | 不同職務分配 |
| b4.counting.repeated_permutation_digits | repeated_permutation_digits | core.vocational_math_b4.generators.counting | vh_數學B4_RepeatedPermutation | 數字重複排列 |

## 5. question_router 最小版狀態
- **檔案位置**：`core/vocational_math_b4/services/question_router.py`
- **目前支援 skill_id**：`vh_數學B4_CombinationDefinition`, `vh_數學B4_CombinationApplications`, `vh_數學B4_MultiplicationPrinciple`, `vh_數學B4_PermutationOfDistinctObjects`, `vh_數學B4_RepeatedPermutation`
- **目前支援 problem_type_id**：`combination_definition_basic`, `combination_polygon_count`, `combination_required_excluded_person`, `divisor_count_prime_factorization`, `permutation_role_assignment`, `repeated_permutation_digits`
- **是否讀 CSV**：否
- **是否讀 database**：否
- **是否接 adaptive**：否
- **是否回傳 router_trace**：是
- **是否支援指定 problem_type_id**：是

## 6. 測試結果
目前已知測試結果如下（依本階段回報紀錄）：
- Phase 4B-1 domain functions / validators：通過
- Phase 4B-2 generators：通過
- Phase 4B-3 generators：通過
- Phase 4C single wrapper：26 passed
- Phase 4D-1 router：37 passed
- Phase 4D-2 wrappers：42 passed

## 7. Web Smoke Test 結果

| URL / skill_id | 測試結果 | 備註 |
|---|---|---|
| /practice/vh_數學B4_CombinationDefinition | 通過 | 可以產題，可以判斷答對錯，terminal 無 500 error |
| /practice/vh_數學B4_CombinationApplications | 通過 | 可以產題，可以判斷答對錯，terminal 無 500 error |
| /practice/vh_數學B4_MultiplicationPrinciple | 通過 | 可以產題，可以判斷答對錯，terminal 無 500 error，曾發現 LaTeX 顯示問題且已修正 |
| /practice/vh_數學B4_PermutationOfDistinctObjects | 通過 | 可以產題，可以判斷答對錯，terminal 無 500 error |
| /practice/vh_數學B4_RepeatedPermutation | 通過 | 可以產題，可以判斷答對錯，terminal 無 500 error |

## 8. 已知限制
- 目前只支援 Chapter 1 的部分 problem_type，不是全部 28 個。
- 目前只接 6 個 deterministic generators。
- 目前 question_router 使用內建最小 registry，尚未讀 CSV / database。
- 尚未接 adaptive route。
- 尚未處理所有 B4 Chapter 1 skill wrapper。
- 尚未處理 Chapter 2 機率與 Chapter 3 統計。
- 「No target nodes found」仍可能出現，但目前不影響一般練習主流程。
- 後續所有數學式必須使用 LaTeX 語法。

## 9. 後續建議
保守下一步規劃如下：
1. **Phase 4E-1**：將 router registry 從 hard-coded 轉為可維護設定檔或 Python registry。
2. **Phase 4E-2**：新增 registry integrity test。
3. **Phase 4E-3**：擴充第三批 high priority generators。
4. **Phase 4E-4**：批次建立更多 wrapper。
5. **Phase 4F**：再處理 adaptive route。
6. 最後才整理 Chapter 1 SOP 總結。

## 10. 結論
1. B4 Chapter 1 最小可用 runtime 已經完成。
2. 證明了 wrapper 結合 router 存取 generator 的架構具備高度可行性。
3. 該架構可作為後續擴充 B1～B3、高中、國中內容的穩固模板。
