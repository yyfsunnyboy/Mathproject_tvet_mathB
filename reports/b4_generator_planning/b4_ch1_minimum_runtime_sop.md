# B4 Chapter 1 最小閉環 SOP 小結

## 1. SOP 目的
本文件旨在固定 B4 Chapter 1 從教材資料整理到網頁可出題的「最小閉環」流程。
請注意，這並非代表 Chapter 1 的所有題型已全部完成，而是展示一個完整的「最小可用 runtime 模板」，供後續擴充其他題型或教材時作為標準作業程序 (SOP) 的參考。

## 2. 最小閉環定義
本次建立的最小閉環包含以下完整流向：

教材例題
→ subskill / template_candidate
→ problem_type / generator_registry_plan
→ domain functions
→ deterministic generators
→ skill wrapper
→ question_router
→ 舊 runtime / 網頁一般練習頁

## 3. 已完成成果摘要
目前已順利凍結的成果數量如下（數據基於各階段 Freeze 報告）：
- Chapter 1 subskill：28 個
- Chapter 1 problem_type：28 個
- 已實作 deterministic generators：6 個
- 已完成 wrappers：5 個
- question_router 最小版：完成
- web smoke test：5 個頁面通過

## 4. Phase 流程與產出檔
| Phase | 目的 | 主要產出 | 狀態 |
|---|---|---|---|
| Phase 1 | 教材來源盤點 | 第一版技能草案 | 完成 |
| Phase 1.5 | 資料品質檢查 | b4_data_quality_review.md | 完成 |
| Phase 2A | subskill / template_candidate | b4_phase2a_subskill_map_... 等 CSV | 完成 |
| Phase 2A-Freeze | 凍結 2A 成果 | b4_phase2a_counting_binomial_summary.md | 完成 |
| Phase 3 | problem_type / generator registry plan | b4_phase3_problem_type_map_... 等 CSV | 完成 |
| Phase 3-Freeze | 凍結 3 成果 | b4_phase3_counting_binomial_summary.md | 完成 |
| Phase 4A | domain function spec | b4_phase4a_domain_function_spec_... | 完成 |
| Phase 4B-1 | domain functions / validators | domain/*.py, validators | 完成 |
| Phase 4B-2 | 第一批 generators | generators/*.py | 完成 |
| Phase 4B-3 | 第二批 generators | generators/*.py | 完成 |
| Phase 4C | single wrapper trial | b4_phase4c_wrapper_trial_summary.md | 完成 |
| Phase 4D | question_router + wrapper runtime | b4_phase4d_runtime_wrapper_router_summary.md | 完成 |

## 5. 目前 runtime 架構
前端 / route 傳 skill_id
→ skills/{skill_id}.py wrapper
→ question_router.generate_for_skill()
→ generator
→ domain function
→ payload
→ 舊 runtime check_answer

## 6. 各層責任分工
| 層級 | 位置 | 責任 | 不應該做的事 |
|---|---|---|---|
| skills/ | `skills/*.py` | 只放主 skill wrapper，負責承接前端路由。 | 不應該把 subskill 寫成獨立 Python 檔，也不要讓 wrapper 自己寫題型邏輯與選題。 |
| question_router | `services/question_router.py` | 管理題庫派發、隨機選擇對應的 generator。 | 不處理題幹文字與學生狀態。 |
| generators/ | `generators/*.py` | 組織題幹文字、呼叫 domain function、產生選項與解答結構。 | 不直接讀資料庫，不自己硬算答案。 |
| domain/ | `domain/*.py` | 核心數學邏輯計算、無狀態的純函數。 | 不處理題幹文字與學生狀態。 |
| validators/ | `domain/b4_validators.py` | 驗證 payload 合法性與參數合規。 | 不處理題幹文字與學生狀態。 |
| tests/ | `tests/` | 單元測試與契約測試。 | 不能跳過不寫。 |
| reports/ | `reports/` | 紀錄 SOP、QA 結果與架構證據。 | 不修改既有 reports。 |

**特別強調：**
- skills/ 只放主 skill wrapper。
- subskill / problem_type 不建立獨立 Python 檔。
- generator 不直接讀資料庫。
- domain function 不處理題幹文字與學生狀態。
- route/frontend 目前不直接修改。

## 7. 已完成的 5 個 wrapper
| skill_id | wrapper | 對應 problem_type | generator_key |
|---|---|---|---|
| vh_數學B4_CombinationDefinition | skills/vh_數學B4_CombinationDefinition.py | combination_definition_basic | b4.combination.combination_definition_basic |
| vh_數學B4_CombinationApplications | skills/vh_數學B4_CombinationApplications.py | combination_polygon_count<br>combination_required_excluded_person | b4.combination.combination_polygon_count<br>b4.combination.combination_required_excluded_person |
| vh_數學B4_MultiplicationPrinciple | skills/vh_數學B4_MultiplicationPrinciple.py | divisor_count_prime_factorization | b4.counting.divisor_count_prime_factorization |
| vh_數學B4_PermutationOfDistinctObjects | skills/vh_數學B4_PermutationOfDistinctObjects.py | permutation_role_assignment | b4.permutation.permutation_role_assignment |
| vh_數學B4_RepeatedPermutation | skills/vh_數學B4_RepeatedPermutation.py | repeated_permutation_digits | b4.counting.repeated_permutation_digits |

## 8. 已完成的 6 個 generator
| generator_key | problem_type_id | module | 題型 |
|---|---|---|---|
| b4.combination.combination_definition_basic | combination_definition_basic | core/vocational_math_b4/generators/combination.py | 組合定義基本計算 |
| b4.combination.combination_polygon_count | combination_polygon_count | core/vocational_math_b4/generators/combination.py | 多邊形對角線與三角形計數 |
| b4.combination.combination_required_excluded_person | combination_required_excluded_person | core/vocational_math_b4/generators/combination.py | 指定人物必選或不可選組合 |
| b4.counting.divisor_count_prime_factorization | divisor_count_prime_factorization | core/vocational_math_b4/generators/counting.py | 正因數個數計算 |
| b4.permutation.permutation_role_assignment | permutation_role_assignment | core/vocational_math_b4/generators/permutation.py | 不同職務分配排列 |
| b4.counting.repeated_permutation_digits | repeated_permutation_digits | core/vocational_math_b4/generators/counting.py | 數字重複排列 |

## 9. 新增下一個 generator 的標準步驟
1. 從 Phase 3 problem_type_map 選一個 problem_type。
2. 確認 domain function 已存在。
3. 若不存在，先補 domain function 與測試。
4. 在對應 math_family generator module 新增 generator function。
5. 補 generator pytest。
6. 產生樣題 QA 報告。
7. 通過後才接入 question_router。
8. 接入 wrapper。
9. 做 web smoke test。
10. 更新 freeze / SOP 文件。

## 10. 新增下一個 wrapper 的標準步驟
1. 確認 question_router 已支援該 skill_id。
2. 建立 skills/{skill_id}.py。
3. wrapper 只呼叫 generate_for_skill。
4. wrapper 不寫題型邏輯。
5. 建立 pytest。
6. 網頁 smoke test。
7. 更新 runtime freeze 報告。

## 11. LaTeX 題幹規則
- 所有數學式用 LaTeX。
- 行內數學用 `$...$`。
- 指數用 `^{...}`。
- 乘號用 `\times`。
- 不輸出純文字 `2^2`、`C(n,r)`、`P(n,r)`。
- 組合可用 `$C(n,r)$` 或 `$\binom{n}{r}$`。
- 排列可用 `$P(n,r)$` 或 `$P^{n}_{r}$`。
- generator 測試應檢查常見數學式格式。

## 12. 不要做的事
- 不要把 subskill 寫成 skills/*.py。
- 不要一個 subskill 一個 Python 檔。
- 不要讓 wrapper 自己選題型。
- 不要讓 generator 自己硬算答案，必須呼叫 domain function。
- 不要直接改 route/frontend 來配合單一 generator。
- 不要跳過 pytest。
- 不要留下 tmp_* 臨時檔。
- 不要一次擴充太多 generator。

## 13. 已知限制
- Chapter 1 尚未全 problem_type generator 化。
- 目前只有 6 個 generator。
- question_router 仍是最小 hard-coded registry。
- 尚未接 adaptive route。
- 尚未處理 Chapter 2 / Chapter 3。
- 「No target nodes found」目前不影響一般練習，但後續需處理知識圖或 prerequisite node mapping。

## 14. 下一步建議
1. Phase 4E-1：registry integrity test。
2. Phase 4E-2：把 router registry 從 hard-coded 拆成可維護 Python registry。
3. Phase 4E-3：第三批 high priority generator。
4. Phase 4E-4：更多 wrapper。
5. Phase 4F：adaptive route。
6. Chapter 2 機率依此 SOP 開始 Phase 2 / Phase 3。

## 15. 給非 coding 教師的操作說明
- 老師只要確認題型像不像課本。
- 老師不需要寫 Python。
- 若題目不像課本，回報 skill_id、problem_type_id、題目截圖。
- 若答案錯，回報 generator_key 與 parameter_tuple。
- 若畫面不能出題，回報 skill_id 與 terminal log。
