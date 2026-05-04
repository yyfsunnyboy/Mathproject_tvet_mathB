# B4 Phase 4E-7B Coverage Reconciliation Summary

## 1. 本階段目的
本階段僅**校正** B4 Chapter 1 **coverage 矩陣與摘要文件**，使 `problem_type` 列與 `question_router`、skill wrapper、專案 web smoke 紀錄一致；**不修改任何程式**、資料庫、route、前端或測試。

## 2. 校正項目

| problem_type_id | skill_id | generator_key | generator_exists | in_router | wrapper_exists | web_smoke_tested | final_status |
|---|---|---|---|---|---|---|---|
| combination_group_selection | vh_數學B4_CombinationApplications | b4.combination.combination_group_selection | yes | yes | yes（`skills/vh_數學B4_CombinationApplications.py`） | yes（`/practice/vh_數學B4_CombinationApplications`，見 Phase4D §7） | runtime_ready |
| factorial_equation_solve_n | vh_數學B4_FactorialNotation | b4.counting.factorial_equation_solve_n | yes | yes | yes（`skills/vh_數學B4_FactorialNotation.py`） | yes（依 Phase4E-4A／後續專案紀錄；Phase4D §7 尚未單列該 URL） | runtime_ready |

## 3. 校正前後統計

| 指標 | 校正前 | 校正後 |
|---|---:|---:|
| runtime_ready | 9 | 11 |
| planned_only | 18 | 16 |
| excluded | 1 | 1 |

## 4. 為什麼要校正
- **Phase 4E-7-Freeze** 依範圍**只升級當批 3 題**，矩陣逐列暫時停在 **9 / 18**，屬預期流程。
- **Phase 4E-4A** 已完成之 **2 題**（`combination_group_selection`、`factorial_equation_solve_n`）早已具 **generator**、登錄於 **`question_router`**，並有對應 **wrapper** 與 **web smoke** 依據，但矩陣未同步為 `runtime_ready`。
- 本次 **Phase 4E-7B** 僅讓**文件**與實際系統狀態一致，避免進度判讀偏低。

## 5. 下一步
- 之後每次 **router／wrapper** 接入後，**必須立即**更新 `b4_ch1_runtime_coverage_matrix.csv` 與摘要。
- 下一批 **generator** 規劃前，先以 **matrix 為唯一進度來源** 對齊現況。
- **暫緩** `binomial_expansion_basic` 相關 wrapper 決策，直到 **答案格式**與判分契約確定。

## 6. 結論
Phase 4E-7B 已成功將 **2** 個延遲登記之 `problem_type` 調整為 **`runtime_ready`**，coverage 收斂為 **11 / 16 / 1**。此舉不改變 runtime 行為，只消除文件落後。後續應在每次接入當下更新矩陣，並在擴充下一批 generator 前以矩陣為準做缺口盤點。
